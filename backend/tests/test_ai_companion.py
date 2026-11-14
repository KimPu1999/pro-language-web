from datetime import datetime, timezone

from sqlalchemy import select

from app.auth import password_hasher
from app.models import AICompanionRevisionItem, User


def login(client, email="companion@example.com", role="student"):
    with client.session_factory() as db:
        db.add(User(email=email, email_normalized=email, password_hash=password_hasher.hash("companion-pass"), display_name="Companion", role=role, account_status="active", email_verified_at=datetime.now(timezone.utc)))
        db.commit()
    assert client.post("/api/v1/auth/login", json={"email": email, "password": "companion-pass"}).status_code == 200
    return client.cookies.get("cm_csrf")


def test_companion_profile_sessions_and_authorized_dashboard(client):
    assert client.get("/api/v1/ai-companion/dashboard").status_code == 401
    csrf = login(client)
    profile = client.put("/api/v1/ai-companion/profile", json={"language": "mm", "difficulty": "beginner", "study_minutes": 45}, headers={"X-CSRF-Token": csrf})
    assert profile.status_code == 200 and profile.json()["language"] == "mm"
    session = client.post("/api/v1/ai-companion/study-sessions", json={"session_type": "mixed"}, headers={"X-CSRF-Token": csrf})
    assert session.status_code == 201 and session.json()["verified"] is False
    dashboard = client.get("/api/v1/ai-companion/dashboard")
    assert dashboard.status_code == 200 and dashboard.json()["verified_data_only"] is True


def test_revision_algorithm_is_deterministic_and_user_scoped(client):
    csrf = login(client, "revision@example.com")
    client.post("/api/v1/ai-companion/study-sessions", json={"session_type": "revision"}, headers={"X-CSRF-Token": csrf})
    with client.session_factory() as db:
        item = db.scalar(select(AICompanionRevisionItem).where(AICompanionRevisionItem.user_id == select(User.id).where(User.email == "revision@example.com").scalar_subquery()))
        item_id = str(item.id)
    reviewed = client.post(f"/api/v1/ai-companion/revision/{item_id}/review", json={"confidence": 5, "correct": True}, headers={"X-CSRF-Token": csrf})
    assert reviewed.status_code == 200 and reviewed.json()["algorithm_version"] == "v1"
    client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf})
    other_csrf = login(client, "revision-other@example.com")
    assert client.post(f"/api/v1/ai-companion/revision/{item_id}/review", json={"confidence": 1, "correct": False}, headers={"X-CSRF-Token": other_csrf}).status_code == 404


def test_provider_voice_and_platform_status_are_truthful(client):
    csrf = login(client, "status@example.com")
    assert client.get("/api/v1/ai-companion/voice/status").json()["status"] == "not_configured"
    assert client.get("/api/v1/ai-companion/platform/operations").status_code == 403
    client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf})
    login(client, "status-admin@example.com", role="platform_admin")
    operations = client.get("/api/v1/ai-companion/platform/operations")
    assert operations.status_code == 200 and operations.json()["voice"] == "not_configured"


def test_privacy_delete_soft_deletes_existing_ai_conversations(client):
    csrf = login(client, "privacy@example.com")
    created = client.post("/api/v1/ai/conversations", json={"title": "Private study"}, headers={"X-CSRF-Token": csrf})
    assert created.status_code == 201
    deleted = client.delete("/api/v1/ai-companion/privacy", headers={"X-CSRF-Token": csrf})
    assert deleted.status_code == 200 and deleted.json()["status"] == "deleted"
    assert client.get("/api/v1/ai/conversations").json()["total"] == 0
