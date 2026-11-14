from datetime import datetime, timezone

from app.auth import password_hasher
from app.models import CompetencyDefinition, StudentCompetencyRecord, User


def student(client, email="assessment-student@example.com"):
    result = client.post("/api/v1/auth/register", json={"full_name": "Assessment Student", "email": email, "password": "strong-pwd12", "confirm_password": "strong-pwd12", "accept_terms": True})
    assert result.status_code == 201
    with client.session_factory() as db:
        user = db.query(User).filter(User.email_normalized == email).one(); user.email_verified_at = datetime.now(timezone.utc); db.commit()
    client.post("/api/v1/auth/login", json={"email": email, "password": "strong-pwd12"})
    return client.cookies.get("cm_csrf")


def admin(client, email="assessment-admin@example.com"):
    with client.session_factory() as db:
        db.add(User(email=email, email_normalized=email, password_hash=password_hasher.hash("Admin-pass12"), display_name="Assessment Admin", role="platform_admin", account_status="active", email_verified_at=datetime.now(timezone.utc))); db.commit()
    client.post("/api/v1/auth/login", json={"email": email, "password": "Admin-pass12"})
    return client.cookies.get("cm_csrf")


def test_published_attempt_is_versioned_and_submission_is_idempotent(client):
    csrf = admin(client)
    created = client.post("/api/v1/assessments", json={"title": "Python Check", "slug": "python-check", "assessment_type": "multiple_choice"}, headers={"X-CSRF-Token": csrf})
    assert created.status_code == 201
    assessment_id = created.json()["id"]
    assert client.post(f"/api/v1/assessments/{assessment_id}/versions", json={"instructions": "Answer carefully."}, headers={"X-CSRF-Token": csrf}).status_code == 201
    question = client.post(f"/api/v1/assessments/{assessment_id}/questions", json={"question_type": "multiple_choice", "prompt": "Two plus two?", "options": ["3", "4"], "correct_answer": "4"}, headers={"X-CSRF-Token": csrf})
    assert question.status_code == 201
    assert client.post(f"/api/v1/assessments/{assessment_id}/publish", headers={"X-CSRF-Token": csrf}).status_code == 200
    client.post("/api/v1/auth/logout")
    student_csrf = student(client)
    started = client.post(f"/api/v1/assessments/{assessment_id}/attempts", headers={"X-CSRF-Token": student_csrf})
    assert started.status_code == 201
    attempt_id = started.json()["id"]; question_id = question.json()["id"]
    detail = client.get(f"/api/v1/assessments/{assessment_id}").json()
    assert "answer_hash" not in str(detail) and "hidden_tests_ref" not in str(detail)
    assert client.put(f"/api/v1/assessments/attempts/{attempt_id}/answers", json={"question_id": question_id, "answer": "4"}, headers={"X-CSRF-Token": student_csrf}).status_code == 200
    first = client.post(f"/api/v1/assessments/attempts/{attempt_id}/submit", json={"idempotency_key": "assessment-submit-001"}, headers={"X-CSRF-Token": student_csrf})
    second = client.post(f"/api/v1/assessments/attempts/{attempt_id}/submit", json={"idempotency_key": "assessment-submit-001"}, headers={"X-CSRF-Token": student_csrf})
    assert first.status_code == 200 and first.json()["passed"] is True
    assert second.status_code == 200 and second.json()["idempotent"] is True


def test_credentials_require_verified_competency_and_platform_role(client):
    csrf = student(client, "credential-student@example.com")
    with client.session_factory() as db:
        user = db.query(User).filter(User.email_normalized == "credential-student@example.com").one(); user_id = user.id; competency = CompetencyDefinition(slug="python-syntax", title="Python syntax", description="Verified syntax competency"); db.add(competency); db.flush(); record = StudentCompetencyRecord(user_id=user.id, competency_id=competency.id, level="proficient", verified=True); db.add(record); db.commit(); record_id = record.id
    assert client.get("/api/v1/assessments/platform/credentials").status_code == 403
    client.post("/api/v1/auth/logout"); admin_csrf = admin(client, "credential-admin@example.com")
    issued = client.post("/api/v1/assessments/platform/credentials", json={"user_id": str(user_id), "credential_type": "competency", "title": "Python Syntax", "source_id": str(record_id), "public": True}, headers={"X-CSRF-Token": admin_csrf})
    assert issued.status_code == 201
    verification = client.get(f"/api/v1/assessments/credentials/verify/{issued.json()['verification_id']}")
    assert verification.status_code == 200 and verification.json()["status"] == "active"
