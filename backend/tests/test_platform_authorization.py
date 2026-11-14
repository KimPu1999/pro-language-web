from datetime import datetime, timezone

from app.auth import password_hasher
from app.models import User


def add_user(client, email, role, *, verified=True, status="active"):
    with client.session_factory() as db:
        user = User(
            email=email,
            email_normalized=email,
            password_hash=password_hasher.hash("Admin123"),
            display_name=role,
            role=role,
            account_status=status,
            email_verified_at=datetime.now(timezone.utc) if verified else None,
        )
        db.add(user)
        db.commit()


def login_and_check_platform(client, email, expected_status):
    response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "Admin123"}
    )
    assert response.status_code == 200
    assert client.get("/api/v1/platform/quality").status_code == expected_status


def test_platform_roles_are_server_enforced(client):
    add_user(client, "platform@example.com", "platform_admin")
    add_user(client, "legacy-admin@example.com", "admin")
    add_user(client, "super@example.com", "super_admin")
    add_user(client, "instructor@example.com", "instructor")
    add_user(client, "moderator@example.com", "moderator")
    add_user(client, "student@example.com", "student")

    login_and_check_platform(client, "platform@example.com", 200)
    login_and_check_platform(client, "legacy-admin@example.com", 200)
    login_and_check_platform(client, "super@example.com", 200)
    login_and_check_platform(client, "instructor@example.com", 403)
    login_and_check_platform(client, "moderator@example.com", 403)
    login_and_check_platform(client, "student@example.com", 403)


def test_platform_requires_verified_email_and_inactive_login_is_rejected(client):
    add_user(client, "unverified@example.com", "platform_admin", verified=False)
    add_user(client, "inactive@example.com", "platform_admin", status="disabled")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "unverified@example.com", "password": "Admin123"},
    )
    assert response.status_code == 200
    assert client.get("/api/v1/platform/quality").status_code == 403

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@example.com", "password": "Admin123"},
    )
    assert response.status_code == 401


def test_platform_permission_change_is_seen_without_reissuing_session(client):
    add_user(client, "role-change@example.com", "student", verified=False)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "role-change@example.com", "password": "Admin123"},
    )
    assert response.status_code == 200
    assert client.get("/api/v1/platform/quality").status_code == 403

    with client.session_factory() as db:
        user = db.query(User).filter(User.email_normalized == "role-change@example.com").one()
        user.role = "platform_admin"
        db.commit()

    assert client.get("/api/v1/platform/quality").status_code == 403

    with client.session_factory() as db:
        user = db.query(User).filter(User.email_normalized == "role-change@example.com").one()
        user.email_verified_at = datetime.now(timezone.utc)
        db.commit()

    assert client.get("/api/v1/platform/quality").status_code == 200
