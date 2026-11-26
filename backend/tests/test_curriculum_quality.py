from datetime import datetime, timezone

from app.auth import password_hasher
from app.models import User


def admin_login(client, email="quality-admin@example.com"):
    with client.session_factory() as db:
        db.add(User(email=email, email_normalized=email, password_hash=password_hasher.hash("quality-pass"), display_name="Quality Admin", role="platform_admin", account_status="active", email_verified_at=datetime.now(timezone.utc)))
        db.commit()
    response = client.post("/api/v1/admin/auth/login", json={"email": email, "password": "quality-pass"})
    assert response.status_code == 200, response.text
    return response.cookies.get("cm_csrf") or client.cookies.get("cm_csrf")


def test_quality_center_reports_live_evidence_and_supports_filters(client):
    assert client.get("/api/v1/admin/curriculum-quality/courses").status_code == 401
    admin_login(client)
    response = client.get("/api/v1/admin/curriculum-quality/courses")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["data_source"] == "live database records"
    assert body["total"] == 1
    item = body["items"][0]
    assert item["slug"] == "python-foundations"
    assert "missing_modules" in item
    assert "missing_lesson_sections" in item
    assert "missing_quizzes" in item
    assert "gaps" in item
    assert client.get("/api/v1/admin/curriculum-quality/courses?technology=python").json()["total"] == 1
    assert client.get("/api/v1/admin/curriculum-quality/courses?technology=javascript").json()["total"] == 0


def test_quality_detail_and_review_submission_are_additive(client):
    csrf = admin_login(client, "quality-review@example.com")
    item = client.get("/api/v1/admin/curriculum-quality/courses").json()["items"][0]
    detail = client.get(f"/api/v1/admin/curriculum-quality/courses/{item['id']}")
    assert detail.status_code == 200
    assert detail.json()["lessons"][0]["missing_sections"]
    submitted = client.post(f"/api/v1/admin/curriculum-quality/courses/{item['id']}/submit-review", headers={"X-CSRF-Token": csrf})
    assert submitted.status_code == 201, submitted.text
    assert submitted.json()["status"] == "submitted"
    repeated = client.post(f"/api/v1/admin/curriculum-quality/courses/{item['id']}/submit-review", headers={"X-CSRF-Token": csrf})
    assert repeated.status_code == 201
    assert repeated.json()["created"] is False
