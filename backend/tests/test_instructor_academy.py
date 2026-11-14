from datetime import datetime, timezone

from app.auth import password_hasher
from app.models import User


def login(client, email, role="student"):
    with client.session_factory() as db:
        db.add(User(email=email, email_normalized=email, password_hash=password_hasher.hash("Academy-pass"), display_name=email.split("@")[0], role=role, account_status="active", email_verified_at=datetime.now(timezone.utc)))
        db.commit()
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "Academy-pass"})
    assert response.status_code == 200
    return client.cookies.get("cm_csrf")


def test_onboarding_requires_guidelines_and_does_not_self_assign(client):
    csrf = login(client, "academy-student@example.com")
    denied = client.post("/api/v1/instructor-academy/onboarding", json={"guidelines_agreed": False}, headers={"X-CSRF-Token": csrf})
    assert denied.status_code == 422
    submitted = client.post("/api/v1/instructor-academy/onboarding", json={"guidelines_agreed": True, "expertise": ["Python"], "sample_lesson": "Validation"}, headers={"X-CSRF-Token": csrf})
    assert submitted.status_code == 202
    assert client.get("/api/v1/auth/me").json()["role"] == "student"


def test_student_cannot_approve_application(client):
    csrf = login(client, "academy-student-two@example.com")
    response = client.post("/api/v1/instructor-academy/platform/applications/00000000-0000-0000-0000-000000000000", json={"decision": "approved"}, headers={"X-CSRF-Token": csrf})
    assert response.status_code == 403


def test_instructor_analytics_suppresses_private_student_data(client):
    login(client, "academy-instructor@example.com", "instructor")
    response = client.get("/api/v1/instructor-academy/analytics")
    assert response.status_code == 200
    assert response.json()["student_data"] == "suppressed_without_verified_aggregate"


def test_peer_review_rejects_self_review(client):
    csrf = login(client, "academy-instructor-two@example.com", "instructor")
    response = client.post("/api/v1/instructor-academy/peer-reviews", json={"course_id": "00000000-0000-0000-0000-000000000000", "reviewer_id": "00000000-0000-0000-0000-000000000000"}, headers={"X-CSRF-Token": csrf})
    assert response.status_code == 403


def test_ai_coach_is_draft_only(client):
    login(client, "academy-instructor-three@example.com", "instructor")
    response = client.get("/api/v1/instructor-academy/ai-coach")
    assert response.status_code == 200
    assert response.json()["status"] == "draft_only"
