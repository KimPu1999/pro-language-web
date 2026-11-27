from datetime import datetime, timezone
from app.auth import password_hasher
from app.models import Enrollment, LessonProgress, User

def admin_login(client):
    with client.session_factory() as db:
        db.add(User(email="analytics-admin@example.com", email_normalized="analytics-admin@example.com", password_hash=password_hasher.hash("admin-pass-123"), display_name="Analytics Admin", role="admin", account_status="active", email_verified_at=datetime.now(timezone.utc)))
        db.commit()
    response = client.post("/api/v1/auth/login", json={"email":"analytics-admin@example.com", "password":"admin-pass-123"})
    assert response.status_code == 200
    return client.cookies.get("cm_csrf")

def test_analytics_requires_platform_admin(client):
    assert client.get("/api/v1/platform/analytics/overview").status_code == 401

def test_analytics_overview_uses_real_empty_dataset(client):
    admin_login(client)
    response = client.get("/api/v1/platform/analytics/overview")
    assert response.status_code == 200
    body = response.json()
    assert body["kpis"]["published_courses"] == 1
    assert body["kpis"]["total_students"] == 0
    assert "definitions" in body

def test_invalid_analytics_date_range_is_rejected(client):
    admin_login(client)
    response = client.get("/api/v1/platform/analytics/overview?start_date=2026-02-01&end_date=2026-01-01")
    assert response.status_code == 422

def test_project_analytics_is_admin_only_and_uses_empty_real_dataset(client):
    assert client.get("/api/v1/platform/analytics/projects").status_code == 401
    admin_login(client)
    response = client.get("/api/v1/platform/analytics/projects")
    assert response.status_code == 200
    body = response.json()
    assert body["submitted"] == 0
    assert body["pending_reviews"] == 0
    assert body["definitions"]["submitted"]

def test_report_export_requires_csrf_and_admin(client):
    assert client.post("/api/v1/platform/reports/export").status_code == 401
    csrf = admin_login(client)
    response = client.post("/api/v1/platform/reports/export", headers={"X-CSRF-Token": csrf})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")


def instructor_login(client):
    with client.session_factory() as db:
        instructor = User(email="instructor-analytics@example.com", email_normalized="instructor-analytics@example.com", password_hash=password_hasher.hash("instructor-pass-123"), display_name="Analytics Instructor", role="instructor", account_status="active", email_verified_at=datetime(2026, 1, 1, tzinfo=timezone.utc), created_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
        student = User(email="analytics-learner@example.com", email_normalized="analytics-learner@example.com", password_hash=password_hasher.hash("student-pass-123"), display_name="Analytics Learner", role="student", account_status="active", email_verified_at=datetime(2026, 1, 1, tzinfo=timezone.utc), created_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
        db.add_all([instructor, student]); db.flush()
        course = db.query(__import__("app.models", fromlist=["Course"]).Course).filter_by(slug="python-foundations").one()
        course.created_by = instructor.id
        lesson = db.query(__import__("app.models", fromlist=["Lesson"]).Lesson).filter_by(slug="hello").one()
        enrollment = Enrollment(user_id=student.id, course_id=course.id, created_at=datetime(2026, 1, 5, tzinfo=timezone.utc), updated_at=datetime(2026, 1, 5, tzinfo=timezone.utc))
        progress = LessonProgress(user_id=student.id, lesson_id=lesson.id, completed=True, last_visited_at=datetime(2026, 1, 6, tzinfo=timezone.utc), created_at=datetime(2026, 1, 6, tzinfo=timezone.utc), updated_at=datetime(2026, 1, 6, tzinfo=timezone.utc))
        db.add_all([enrollment, progress]); db.commit()
    response = client.post("/api/v1/auth/login", json={"email": "instructor-analytics@example.com", "password": "instructor-pass-123"})
    assert response.status_code == 200


def test_instructor_analytics_uses_utc_boundaries_and_real_associations(client):
    instructor_login(client)
    params = "start_utc=2026-01-01T00:00:00%2B00:00&end_utc=2026-01-10T00:00:00%2B00:00"
    overview = client.get(f"/api/v1/platform/analytics/instructors/overview?{params}")
    assert overview.status_code == 200, overview.text
    body = overview.json()
    assert body["kpis"]["total_instructors"] == 1
    assert body["kpis"]["new_enrollments"] == 1
    assert body["kpis"]["active_learners"] == 1
    assert body["kpis"]["course_completions"] == 1
    assert body["range"]["start"].startswith("2026-01-01T00:00:00")

    listing = client.get(f"/api/v1/platform/analytics/instructors/list?{params}&page=1&page_size=10")
    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    instructor_id = listing.json()["items"][0]["id"]
    detail = client.get(f"/api/v1/platform/analytics/instructors/{instructor_id}?{params}")
    assert detail.status_code == 200
    assert detail.json()["instructor"]["associated_courses"] == 1
    trends = client.get(f"/api/v1/platform/analytics/instructors/trends?{params}&bucket=daily")
    assert trends.status_code == 200
    assert any(item["new_enrollments"] == 1 for item in trends.json()["items"])
    courses = client.get(f"/api/v1/platform/analytics/instructors/courses?{params}")
    assert courses.status_code == 200
    assert courses.json()["items"][0]["new_enrollments"] == 1


def test_instructor_analytics_rejects_students_and_invalid_utc(client):
    with client.session_factory() as db:
        student = User(email="analytics-student@example.com", email_normalized="analytics-student@example.com", password_hash=password_hasher.hash("student-pass-123"), display_name="Student", role="student", account_status="active", email_verified_at=datetime.now(timezone.utc))
        db.add(student); db.commit()
    assert client.post("/api/v1/auth/login", json={"email": "analytics-student@example.com", "password": "student-pass-123"}).status_code == 200
    assert client.get("/api/v1/platform/analytics/instructors/overview").status_code == 403
    client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": client.cookies.get("cm_csrf")})
    instructor_login(client)
    invalid = client.get("/api/v1/platform/analytics/instructors/overview?start_utc=2026-01-01T00:00:00&end_utc=2026-01-02T00:00:00")
    assert invalid.status_code == 422


def test_instructor_export_is_platform_admin_only_and_formula_safe(client):
    instructor_login(client)
    assert client.get("/api/v1/platform/analytics/instructors/export").status_code == 403
    client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": client.cookies.get("cm_csrf")})
    admin_login(client)
    response = client.get("/api/v1/platform/analytics/instructors/export?start_date=2026-01-01&end_date=2026-01-10")
    assert response.status_code == 200
    assert "instructor,associated_courses" in response.text
