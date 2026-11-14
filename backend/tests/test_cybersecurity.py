from datetime import datetime, timezone

from sqlalchemy import select

from app.auth import password_hasher
from app.models import CybersecurityLabDefinition, LearningLabWorkspace, User


def login_user(client, email, role="student", verified=True):
    with client.session_factory() as db:
        user = User(
            email=email,
            email_normalized=email,
            password_hash=password_hasher.hash("cyber-test-password"),
            display_name=email.split("@")[0],
            role=role,
            account_status="active",
            email_verified_at=datetime.now(timezone.utc) if verified else None,
        )
        db.add(user)
        db.commit()
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "cyber-test-password"})
    assert response.status_code == 200
    return client.cookies.get("cm_csrf")


def seed_published_lab(client):
    with client.session_factory() as db:
        lab = CybersecurityLabDefinition(
            title="Secure Input Validation",
            slug="secure-input-validation",
            category="secure_coding",
            difficulty="beginner",
            language="python",
            description_en="Practice safe input validation.",
            objectives_json='["Validate untrusted input"]',
            status="published",
            published=True,
        )
        db.add(lab)
        db.commit()
        return str(lab.id)


def test_public_catalog_and_authenticated_dashboard_are_truthful(client):
    lab_id = seed_published_lab(client)
    catalog = client.get("/api/v1/cybersecurity/labs")
    assert catalog.status_code == 200
    assert catalog.json()["total"] == 1
    assert client.get("/api/v1/cybersecurity/labs/" + lab_id).json()["evaluation"]["score_source"] == "server_only"
    assert client.get("/api/v1/cybersecurity/dashboard").status_code == 401


def test_verified_student_can_start_but_cannot_evaluate_without_owned_workspace(client):
    csrf = login_user(client, "cyber-student@example.com")
    lab_id = seed_published_lab(client)
    started = client.post(f"/api/v1/cybersecurity/labs/{lab_id}/attempts", json={}, headers={"X-CSRF-Token": csrf})
    assert started.status_code == 201, started.text
    attempt_id = started.json()["id"]
    evaluated = client.post(
        f"/api/v1/cybersecurity/attempts/{attempt_id}/evaluate",
        json={"workspace_id": "00000000-0000-0000-0000-000000000001", "evidence": ""},
        headers={"X-CSRF-Token": csrf},
    )
    assert evaluated.status_code == 422


def test_assessment_rejects_workspace_owned_by_another_user(client):
    first_csrf = login_user(client, "assessment-owner@example.com")
    with client.session_factory() as db:
        owner = db.scalar(select(User).where(User.email == "assessment-owner@example.com"))
        workspace = LearningLabWorkspace(user_id=owner.id, lab_id=owner.id, version_id=owner.id)
        db.add(workspace)
        db.commit()
        workspace_id = str(workspace.id)
    client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": first_csrf})
    csrf = login_user(client, "assessment-outsider@example.com")
    response = client.post(
        "/api/v1/cybersecurity/assessment/targets",
        json={"workspace_id": workspace_id, "evidence": ""},
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 403


def test_threat_models_are_owner_scoped_and_platform_operations_are_rbac_protected(client):
    csrf = login_user(client, "cyber-student-two@example.com")
    created = client.post(
        "/api/v1/cybersecurity/threat-models",
        json={"title": "Checkout trust boundaries", "content": {"assets": ["orders"]}},
        headers={"X-CSRF-Token": csrf},
    )
    assert created.status_code == 201
    assert client.get("/api/v1/cybersecurity/platform/operations").status_code == 403
    client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf})
    admin_csrf = login_user(client, "cyber-admin@example.com", role="platform_admin")
    operations = client.get("/api/v1/cybersecurity/platform/operations")
    assert operations.status_code == 200
    assert operations.json()["external_scanning"] is False
    assert admin_csrf
