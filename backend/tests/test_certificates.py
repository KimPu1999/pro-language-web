from datetime import datetime, timezone

from app.auth import password_hasher
from app.models import Course, Enrollment, Lesson, LessonProgress, LessonQuiz, QuizQuestion, User


def login_student(client, email, name):
    result = client.post("/api/v1/auth/register", json={"full_name": name, "email": email, "password": "strong-pwd12", "confirm_password": "strong-pwd12", "accept_terms": True})
    assert result.status_code == 201
    with client.session_factory() as db:
        user = db.query(User).filter(User.email_normalized == email).one()
        user.email_verified_at = datetime.now(timezone.utc)
        db.commit()
    assert client.post("/api/v1/auth/login", json={"email": email, "password": "strong-pwd12"}).status_code == 200
    return client.cookies.get("cm_csrf")


def login_admin(client):
    email = "certificate-admin@example.com"
    with client.session_factory() as db:
        db.add(User(email=email, email_normalized=email, password_hash=password_hasher.hash("Admin-pass12"), display_name="Certificate Admin", role="platform_admin", account_status="active", email_verified_at=datetime.now(timezone.utc)))
        db.commit()
    assert client.post("/api/v1/auth/login", json={"email": email, "password": "Admin-pass12"}).status_code == 200
    return client.cookies.get("cm_csrf")


def test_certificate_is_issued_only_after_verified_course_completion(client):
    csrf = login_student(client, "certificate-student@example.com", "Certificate Student")
    with client.session_factory() as db:
        course = db.query(Course).filter(Course.slug == "python-foundations").one()
        lesson = db.query(Lesson).one()
    assert client.post(f"/api/v1/me/enrollments/{course.slug}", headers={"X-CSRF-Token": csrf}).status_code == 201
    assert client.get("/api/v1/me/certificates").json()["items"] == []
    completed = client.post(f"/api/v1/me/lessons/{lesson.id}/progress", json={"completed": True}, headers={"X-CSRF-Token": csrf})
    assert completed.status_code == 200
    assert completed.json()["certificate_earned"]["status"] == "valid"
    library = client.get("/api/v1/me/certificates")
    assert library.status_code == 200 and len(library.json()["items"]) == 1
    certificate = library.json()["items"][0]
    assert client.get(f"/api/v1/certificates/verify/{certificate['certificate_id']}").json()["status"] == "valid"
    pdf = client.get(f"/api/v1/me/certificates/{certificate['certificate_id']}/download")
    assert pdf.status_code == 200 and pdf.headers["content-type"] == "application/pdf" and pdf.content.startswith(b"%PDF")
    assert client.post(f"/api/v1/me/lessons/{lesson.id}/progress", json={"completed": True}, headers={"X-CSRF-Token": csrf}).json()["certificate_earned"]["certificate_id"] == certificate["certificate_id"]


def test_certificate_ownership_and_revocation_are_enforced(client):
    csrf = login_student(client, "certificate-owner@example.com", "Owner")
    with client.session_factory() as db:
        course = db.query(Course).filter(Course.slug == "python-foundations").one(); course_slug = course.slug; lesson = db.query(Lesson).one(); lesson_id = str(lesson.id)
    client.post(f"/api/v1/me/enrollments/{course_slug}", headers={"X-CSRF-Token": csrf})
    client.post(f"/api/v1/me/lessons/{lesson_id}/progress", json={"completed": True}, headers={"X-CSRF-Token": csrf})
    certificate = client.get("/api/v1/me/certificates").json()["items"][0]
    client.post("/api/v1/auth/logout")
    other_csrf = login_student(client, "certificate-other@example.com", "Other")
    assert client.get(f"/api/v1/me/certificates/{certificate['certificate_id']}").status_code == 404
    client.post("/api/v1/auth/logout")
    admin_csrf = login_admin(client)
    revoked = client.post(f"/api/v1/admin/certificates/{certificate['certificate_id']}/revoke?reason=Evidence%20review", headers={"X-CSRF-Token": admin_csrf})
    assert revoked.status_code == 200 and revoked.json()["status"] == "revoked"
    assert client.get(f"/api/v1/certificates/verify/{certificate['certificate_id']}").json()["status"] == "revoked"


def test_published_quiz_is_a_real_certificate_requirement(client):
    csrf = login_student(client, "certificate-quiz@example.com", "Quiz Learner")
    with client.session_factory() as db:
        course = db.query(Course).filter(Course.slug == "python-foundations").one(); course_slug = course.slug; lesson = db.query(Lesson).one(); lesson_id = str(lesson.id)
        quiz = LessonQuiz(lesson_id=lesson.id, title="Completion check", status="published"); db.add(quiz); db.flush()
        question = QuizQuestion(quiz_id=quiz.id, prompt="What is 2 + 2?", options_json='["4", "5"]', correct_answer="4", position=1); db.add(question); db.commit()
        question_id = str(question.id)
    client.post(f"/api/v1/me/enrollments/{course_slug}", headers={"X-CSRF-Token": csrf})
    client.post(f"/api/v1/me/lessons/{lesson_id}/progress", json={"completed": True}, headers={"X-CSRF-Token": csrf})
    assert client.get("/api/v1/me/certificates").json()["items"] == []
    result = client.post(f"/api/v1/me/lessons/{lesson_id}/quiz", json={"answers": {question_id: "4"}}, headers={"X-CSRF-Token": csrf})
    assert result.status_code == 200 and result.json()["passed"] is True and result.json()["certificate_earned"]["status"] == "valid"
