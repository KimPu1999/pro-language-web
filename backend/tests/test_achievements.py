from datetime import datetime, timezone

from app.auth import password_hasher
from app.models import Course, Lesson, User


def login_student(client, email, name):
    result = client.post("/api/v1/auth/register", json={"full_name": name, "email": email, "password": "strong-pwd12", "confirm_password": "strong-pwd12", "accept_terms": True})
    assert result.status_code == 201
    with client.session_factory() as db:
        user = db.query(User).filter(User.email_normalized == email).one()
        user.email_verified_at = datetime.now(timezone.utc)
        db.commit()
    assert client.post("/api/v1/auth/login", json={"email": email, "password": "strong-pwd12"}).status_code == 200
    return client.cookies.get("cm_csrf")


def login_admin(client, email="achievement-admin@example.com"):
    with client.session_factory() as db:
        db.add(User(email=email, email_normalized=email, password_hash=password_hasher.hash("Admin-pass12"), display_name="Achievement Admin", role="platform_admin", account_status="active", email_verified_at=datetime.now(timezone.utc)))
        db.commit()
    assert client.post("/api/v1/auth/login", json={"email": email, "password": "Admin-pass12"}).status_code == 200
    return client.cookies.get("cm_csrf")


def test_draft_definition_is_private_then_awarded_from_verified_lesson(client):
    admin_csrf = login_admin(client)
    payload = {"code": "first-step", "title": "First Step", "description": "Complete one verified lesson.", "criteria": "Complete one published lesson.", "category": "learning", "rule_type": "lesson_completion_count", "rule": {"count": 1}}
    created = client.post("/api/v1/admin/achievements", json=payload, headers={"X-CSRF-Token": admin_csrf})
    assert created.status_code == 201
    definition_id = created.json()["id"]
    assert client.get("/api/v1/achievements").json()["items"] == []
    assert client.post(f"/api/v1/admin/achievements/{definition_id}/submit-review", headers={"X-CSRF-Token": admin_csrf}).status_code == 200
    assert client.post(f"/api/v1/admin/achievements/{definition_id}/approve", headers={"X-CSRF-Token": admin_csrf}).status_code == 200
    assert client.post(f"/api/v1/admin/achievements/{definition_id}/publish", headers={"X-CSRF-Token": admin_csrf}).status_code == 200
    assert len(client.get("/api/v1/achievements").json()["items"]) == 1

    client.post("/api/v1/auth/logout")
    csrf = login_student(client, "achievement-student@example.com", "Achievement Student")
    with client.session_factory() as db:
        course = db.query(Course).filter(Course.slug == "python-foundations").one()
        lesson = db.query(Lesson).one()
    assert client.post(f"/api/v1/me/enrollments/{course.slug}", headers={"X-CSRF-Token": csrf}).status_code == 201
    completed = client.post(f"/api/v1/me/lessons/{lesson.id}/progress", json={"completed": True}, headers={"X-CSRF-Token": csrf})
    assert completed.status_code == 200
    assert len(completed.json()["achievements_earned"]) == 1
    library = client.get("/api/v1/me/achievements")
    assert library.status_code == 200 and library.json()["metrics"]["earned_badges"] == 1
    award_id = library.json()["items"][0]["award"]["award_id"]
    verification = client.get(f"/api/v1/achievements/verify/{award_id}")
    assert verification.status_code == 200 and verification.json()["status"] == "valid" and "email" not in verification.json()
    repeated = client.post(f"/api/v1/me/lessons/{lesson.id}/progress", json={"completed": True}, headers={"X-CSRF-Token": csrf})
    assert repeated.status_code == 200 and repeated.json()["achievements_earned"] == []
