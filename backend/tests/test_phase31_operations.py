from datetime import datetime, timezone

from app.auth import password_hasher
from app.models import PlatformAlertEvent, User


def verified_student(client, email="phase31-student@example.com"):
    response = client.post("/api/v1/auth/register", json={"full_name": "Phase 31 Student", "email": email, "password": "strong-pwd12", "confirm_password": "strong-pwd12", "accept_terms": True})
    assert response.status_code == 201
    with client.session_factory() as db:
        user = db.query(User).filter(User.email_normalized == email).one(); user.email_verified_at = datetime.now(timezone.utc); db.commit()
    client.post("/api/v1/auth/login", json={"email": email, "password": "strong-pwd12"})
    return client.cookies.get("cm_csrf")


def admin(client, email="phase31-admin@example.com"):
    with client.session_factory() as db:
        db.add(User(email=email, email_normalized=email, password_hash=password_hasher.hash("Admin123"), display_name="Admin", role="platform_admin", account_status="active", email_verified_at=datetime.now(timezone.utc))); db.commit()
    client.post("/api/v1/auth/login", json={"email": email, "password": "Admin123"})
    return client.cookies.get("cm_csrf")


def test_public_status_does_not_require_platform_access(client):
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    assert "services" in response.json()


def test_feedback_is_owned_and_rate_limited_endpoint_is_authenticated(client):
    csrf = verified_student(client)
    created = client.post("/api/v1/feedback", json={"category": "course", "title": "Helpful lesson", "body": "The examples helped me understand the topic."}, headers={"X-CSRF-Token": csrf})
    assert created.status_code == 201
    assert client.get("/api/v1/feedback/my").status_code == 200
    assert client.get("/api/v1/feedback").status_code == 403


def test_monitoring_and_alert_deduplication_are_platform_only(client):
    csrf = admin(client)
    assert client.get("/api/v1/platform/monitoring").status_code == 200
    health = client.post("/api/v1/platform/monitoring/checks", json={"service": "api", "status": "healthy", "latency_ms": 12}, headers={"X-CSRF-Token": csrf})
    assert health.status_code == 201
    payload = {"service": "api", "severity": "warning", "message": "Slow request", "dedupe_key": "api-slow-1"}
    first = client.post("/api/v1/platform/alerts", json=payload, headers={"X-CSRF-Token": csrf})
    second = client.post("/api/v1/platform/alerts", json=payload, headers={"X-CSRF-Token": csrf})
    assert first.status_code == 201
    assert second.status_code == 201 and second.json()["deduplicated"] is True
    with client.session_factory() as db:
        assert db.query(PlatformAlertEvent).count() == 1


def test_system_quality_endpoint_is_platform_only_and_truthful(client):
    assert client.get("/api/v1/platform/quality").status_code == 401
    admin(client, "phase31-quality-admin@example.com")
    response = client.get("/api/v1/platform/quality")
    assert response.status_code == 200
    payload = response.json()
    assert {check["name"] for check in payload["checks"]} >= {"api", "database", "secure_runner", "ai_provider"}
    assert payload["checks"][-1]["name"] == "observability"


def test_bug_attachment_scope_and_feature_flag_evaluation(client):
    csrf = verified_student(client, "phase31-bug@example.com")
    bug = client.post("/api/v1/support/report-bug", json={"title": "Broken button", "description": "The button does not submit.", "affected_page": "/feedback"}, headers={"X-CSRF-Token": csrf})
    assert bug.status_code == 201
    bug_id = bug.json()["id"]
    bad = client.post(f"/api/v1/support/report-bug/{bug_id}/attachments?storage_key=x&content_type=application%2Fx-sh&size_bytes=10", headers={"X-CSRF-Token": csrf})
    assert bad.status_code == 422
    admin_csrf = admin(client, "phase31-flag-admin@example.com")
    flag = client.post("/api/v1/platform/feature-flags", json={"key": "phase31.test", "enabled": True, "rollout_percent": 100}, headers={"X-CSRF-Token": admin_csrf})
    assert flag.status_code == 201
    assert client.get("/api/v1/feature-flags/phase31.test").json()["enabled"] is True
