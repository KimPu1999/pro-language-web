from datetime import datetime, timezone

from app.auth import password_hasher
from app.models import LearningLab, LearningLabVersion, User


def user(client, email: str):
    with client.session_factory() as db:
        row = User(
            email=email,
            email_normalized=email,
            password_hash=password_hasher.hash("Cloud123"),
            display_name="Cloud learner",
            role="student",
            account_status="active",
            email_verified_at=datetime.now(timezone.utc),
        )
        db.add(row)
        db.commit()
        return row.id


def lab(client, creator):
    with client.session_factory() as db:
        row = LearningLab(
            title="Git workspace",
            slug="git-workspace",
            description_en="Practice safe Git operations.",
            category="git",
            language="git",
            published=True,
            status="published",
        )
        db.add(row)
        db.flush()
        db.add(LearningLabVersion(lab_id=row.id, version_number=1, status="published", created_by=creator, snapshot_json="{}"))
        db.commit()
        return row.id


def login(client, email: str):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "Cloud123"})
    assert response.status_code == 200
    return client.cookies.get("cm_csrf")


def test_cloud_modes_are_truthful_and_safe(client):
    response = client.get("/api/v1/cloud-labs/modes")
    assert response.status_code == 200
    body = response.json()
    assert body["docker"]["host_socket_exposed"] is False
    assert body["kubernetes"]["cluster_admin_exposed"] is False
    assert body["deployment"]["public_previews"] is False


def test_cloud_workspace_creation_and_file_path_protection(client):
    learner = user(client, "cloud-one@example.com")
    lab_id = lab(client, learner)
    csrf = login(client, "cloud-one@example.com")

    response = client.post(f"/api/v1/cloud-labs/{lab_id}/workspaces", headers={"X-CSRF-Token": csrf})
    assert response.status_code == 201
    workspace_id = response.json()["id"]
    assert client.get(f"/api/v1/cloud-labs/workspaces/{workspace_id}").status_code == 200

    unsafe = client.put(
        f"/api/v1/cloud-labs/workspaces/{workspace_id}/files",
        json={"path": "../escape.py", "source_code": "x", "language": "python"},
        headers={"X-CSRF-Token": csrf},
    )
    assert unsafe.status_code == 422


def test_cloud_workspace_isolation(client):
    owner = user(client, "cloud-owner@example.com")
    other = user(client, "cloud-other@example.com")
    lab_id = lab(client, owner)
    csrf = login(client, "cloud-owner@example.com")
    created = client.post(f"/api/v1/cloud-labs/{lab_id}/workspaces", headers={"X-CSRF-Token": csrf})
    workspace_id = created.json()["id"]

    login(client, "cloud-other@example.com")
    assert client.get(f"/api/v1/cloud-labs/workspaces/{workspace_id}").status_code == 404
