from datetime import datetime, timezone

from app.auth import password_hasher
from app.models import User


def add_user(client, email: str, role: str):
    with client.session_factory() as db:
        row = User(
            email=email,
            email_normalized=email,
            password_hash=password_hasher.hash("Admin123"),
            display_name=role,
            role=role,
            account_status="active",
            email_verified_at=datetime.now(timezone.utc),
        )
        db.add(row)
        db.commit()
        return row.id


def login(client, email: str):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "Admin123"})
    assert response.status_code == 200
    return client.cookies.get("cm_csrf")


def test_security_center_is_server_authorized(client):
    add_user(client, "security-student@example.com", "student")
    login(client, "security-student@example.com")
    assert client.get("/api/v1/platform/security/overview").status_code == 403

    client.cookies.clear()
    add_user(client, "security-admin@example.com", "platform_admin")
    login(client, "security-admin@example.com")
    response = client.get("/api/v1/platform/security/overview")
    assert response.status_code == 200
    assert response.json()["data_source"] == "database security and authentication records"
    assert client.get("/api/v1/platform/security/roles").status_code == 200
    assert client.get("/api/v1/platform/security/audit-logs").status_code == 200
    assert client.post(
        "/api/v1/platform/security/assignments",
        json={"user_id": str(add_user(client, "cannot-escalate@example.com", "student")), "role": "super_admin"},
        headers={"X-CSRF-Token": client.cookies.get("cm_csrf")},
    ).status_code == 403


def test_super_admin_role_changes_are_persisted_and_audited(client):
    super_id = add_user(client, "security-super@example.com", "super_admin")
    target_id = add_user(client, "security-target@example.com", "student")
    csrf = login(client, "security-super@example.com")

    response = client.post(
        "/api/v1/platform/security/assignments",
        json={"user_id": str(target_id), "role": "platform_admin"},
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 201
    assert response.json()["assignment"]["role"] == "platform_admin"

    with client.session_factory() as db:
        assert db.get(User, target_id).role == "platform_admin"

    logs = client.get("/api/v1/platform/security/audit-logs").json()["items"]
    assert any(item["action"] == "platform_role_assigned" for item in logs)

    response = client.delete(
        f"/api/v1/platform/security/assignments/{target_id}",
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 200
    with client.session_factory() as db:
        assert db.get(User, target_id).role == "student"

    assert client.delete(
        f"/api/v1/platform/security/assignments/{super_id}",
        headers={"X-CSRF-Token": csrf},
    ).status_code == 409


def test_failed_login_is_recorded_as_a_security_event(client):
    add_user(client, "security-events-super@example.com", "super_admin")
    response = client.post("/api/v1/auth/login", json={"email": "security-events-super@example.com", "password": "Wrong123"})
    assert response.status_code == 401
    login(client, "security-events-super@example.com")
    events = client.get("/api/v1/platform/security/events?event=login_failed").json()
    assert events["total"] == 1
    assert events["items"][0]["event"] == "login_failed"
