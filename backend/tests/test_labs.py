from test_organizations import student


def instructor(client, email="lab-instructor@test"):
    csrf = student(client, email)
    with client.session_factory() as db:
        from app.models import User
        db.scalar(__import__("sqlalchemy", fromlist=["select"]).select(User).where(User.email_normalized == email)).role = "instructor"
        db.commit()
    return csrf


def test_lab_workspace_ownership_path_safety_and_runner_status(client):
    csrf = instructor(client)
    created = client.post("/api/v1/instructor/labs", json={"title":"Python Lab","slug":"python-lab","description_en":"Practice"}, headers={"X-CSRF-Token":csrf})
    assert created.status_code == 201
    lab_id = created.json()["id"]
    assert client.post(f"/api/v1/instructor/labs/{lab_id}/publish", headers={"X-CSRF-Token":csrf}).status_code == 200
    workspace = client.post(f"/api/v1/labs/{lab_id}/workspace", headers={"X-CSRF-Token":csrf})
    assert workspace.status_code == 201
    workspace_id = workspace.json()["id"]
    unsafe = client.put(f"/api/v1/lab-workspaces/{workspace_id}/files", json={"path":"../secret.py","source_code":"x","language":"python"}, headers={"X-CSRF-Token":csrf})
    assert unsafe.status_code == 422
    run = client.post(f"/api/v1/lab-workspaces/{workspace_id}/run", json={"idempotency_key":"lab-run-001"}, headers={"X-CSRF-Token":csrf})
    assert run.status_code == 202 and run.json()["status"] == "runner_unavailable"


def test_lab_workspace_isolation(client):
    csrf = instructor(client, "lab-owner-two@test")
    created = client.post("/api/v1/instructor/labs", json={"title":"Private Lab","slug":"private-lab","description_en":"Practice"}, headers={"X-CSRF-Token":csrf}).json()
    client.post(f"/api/v1/instructor/labs/{created['id']}/publish", headers={"X-CSRF-Token":csrf})
    workspace = client.post(f"/api/v1/labs/{created['id']}/workspace", headers={"X-CSRF-Token":csrf}).json()
    client.post("/api/v1/auth/logout", headers={"X-CSRF-Token":csrf})
    student(client, "lab-outsider@test")
    assert client.get(f"/api/v1/lab-workspaces/{workspace['id']}").status_code == 404
