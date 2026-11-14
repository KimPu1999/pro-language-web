from datetime import datetime, timezone

from app.auth import password_hasher
from app.models import StudentLearningSignal, StudentLearningSignalEvidence, StudentSuccessPrivacyPreference, User


def student(client, email):
    response = client.post("/api/v1/auth/register", json={"full_name": "Support Student", "email": email, "password": "strong-pwd12", "confirm_password": "strong-pwd12", "accept_terms": True})
    assert response.status_code == 201
    with client.session_factory() as db:
        user = db.query(User).filter(User.email_normalized == email).one(); user.email_verified_at = datetime.now(timezone.utc); db.commit()
    client.post("/api/v1/auth/login", json={"email": email, "password": "strong-pwd12"})
    return client.cookies.get("cm_csrf")


def staff(client, email):
    with client.session_factory() as db:
        db.add(User(email=email, email_normalized=email, password_hash=password_hasher.hash("Staff-pass12"), display_name="Support Staff", role="support_staff", account_status="active", email_verified_at=datetime.now(timezone.utc))); db.commit()
    client.post("/api/v1/auth/login", json={"email": email, "password": "Staff-pass12"})
    return client.cookies.get("cm_csrf")


def test_ticket_ownership_and_authorized_workflow(client):
    csrf = student(client, "success-owner@example.com")
    created = client.post("/api/v1/student-success/tickets", json={"category": "course", "subject": "Need help", "description": "I need help with this lesson."}, headers={"X-CSRF-Token": csrf})
    assert created.status_code == 201
    ticket_id = created.json()["id"]
    assert client.get(f"/api/v1/student-success/tickets/{ticket_id}").status_code == 200
    assert client.post(f"/api/v1/student-success/tickets/{ticket_id}/transition", json={"status": "triaged"}, headers={"X-CSRF-Token": csrf}).status_code == 403
    staff_csrf = staff(client, "success-staff@example.com")
    assert client.post(f"/api/v1/student-success/tickets/{ticket_id}/transition", json={"status": "triaged"}, headers={"X-CSRF-Token": staff_csrf}).status_code == 200


def test_learning_signals_respect_student_visibility(client):
    student(client, "success-signals@example.com")
    with client.session_factory() as db:
        user = db.query(User).filter(User.email_normalized == "success-signals@example.com").one()
        signal = StudentLearningSignal(user_id=user.id, signal_code="stalled_progress", explanation="No completed lesson in the observed period.", confidence_limit="This is an activity signal, not a diagnosis.")
        db.add(signal); db.flush(); db.add(StudentLearningSignalEvidence(signal_id=signal.id, source_type="lesson_progress", summary="Persisted lesson progress record.")); db.add(StudentSuccessPrivacyPreference(user_id=user.id, show_signals=False)); db.commit()
    response = client.get("/api/v1/student-success/learning-signals")
    assert response.status_code == 200 and response.json()["visible"] is False
    assert client.get("/api/v1/student-success/platform/overview").status_code == 403


def test_mentor_escalation_requires_explicit_consent(client):
    csrf = student(client, "success-mentor@example.com")
    denied = client.post("/api/v1/student-success/mentorship/escalations", json={"topic": "Planning", "description": "I need help planning study time.", "consented": False}, headers={"X-CSRF-Token": csrf})
    assert denied.status_code == 403
