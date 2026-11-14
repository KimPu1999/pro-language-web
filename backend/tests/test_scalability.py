from datetime import datetime, timezone

from app.auth import password_hasher
from app.models import User


def login(client, email: str, role: str = "student"):
    with client.session_factory() as db:
        db.add(
            User(
                email=email,
                email_normalized=email,
                password_hash=password_hasher.hash("Scale-test-pass"),
                display_name="Scale Test",
                role=role,
                account_status="active",
                email_verified_at=datetime.now(timezone.utc),
            )
        )
        db.commit()
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Scale-test-pass"},
    )
    assert response.status_code == 200
    return client.cookies.get("cm_csrf")


def test_scalability_requires_platform_admin(client):
    login(client, "scale-student@example.com")
    response = client.get("/api/v1/platform/scalability")
    assert response.status_code == 403


def test_scalability_dashboard_is_truthful_when_telemetry_is_absent(client):
    login(client, "scale-admin@example.com", "platform_admin")
    response = client.get("/api/v1/platform/scalability")
    assert response.status_code == 200
    body = response.json()
    assert body["telemetry"] == "not_configured"
    assert body["api"]["instances"] == "not_tested"
    assert body["database"]["read_replicas"] == "not_configured"


def test_scaling_policy_is_safe_and_never_enabled_by_request(client):
    csrf = login(client, "scale-policy@example.com", "platform_admin")
    invalid = client.post(
        "/api/v1/platform/scalability/policies",
        headers={"X-CSRF-Token": csrf},
        json={
            "service": "api",
            "min_capacity": 4,
            "max_capacity": 2,
            "scale_out_threshold": 0.8,
            "scale_in_threshold": 0.2,
            "cooldown_seconds": 60,
            "enabled": True,
            "approval_required": False,
        },
    )
    assert invalid.status_code == 422

    created = client.post(
        "/api/v1/platform/scalability/policies",
        headers={"X-CSRF-Token": csrf},
        json={
            "service": "api",
            "min_capacity": 1,
            "max_capacity": 2,
            "scale_out_threshold": 0.8,
            "scale_in_threshold": 0.2,
            "cooldown_seconds": 60,
            "enabled": True,
            "approval_required": False,
        },
    )
    assert created.status_code == 201
    assert created.json()["enabled"] is False
    assert created.json()["approval_required"] is True


def test_scaling_event_only_records_a_plan(client):
    csrf = login(client, "scale-event@example.com", "platform_admin")
    response = client.post(
        "/api/v1/platform/scalability/events",
        headers={"X-CSRF-Token": csrf},
        json={
            "service": "runner",
            "action": "scale_out",
            "requested_capacity": 2,
            "reason": "Controlled capacity test",
        },
    )
    assert response.status_code == 202
    assert response.json()["status"] == "planned"
    assert "no infrastructure was changed" in response.json()["message"]
