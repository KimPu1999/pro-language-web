
from test_organizations import student


def owner_with_org(client, email: str, slug: str):
    csrf = student(client, email)
    created = client.post("/api/v1/organizations", json={"name": "Automation Org", "slug": slug}, headers={"X-CSRF-Token": csrf})
    assert created.status_code == 201
    return csrf


def valid_graph():
    return {"nodes": [{"node_key": "start", "node_type": "trigger", "config": {}}, {"node_key": "notify", "node_type": "action", "config": {"action": "notify"}}, {"node_key": "end", "node_type": "end", "config": {}}], "edges": [{"source_key": "start", "target_key": "notify"}, {"source_key": "notify", "target_key": "end"}]}


def test_workflow_graph_validation_and_idempotent_run(client):
    csrf = owner_with_org(client, "automation-owner@test", "automation-org")
    created = client.post("/api/v1/organizations/automation-org/automation/workflows", json={"name": "Reminder", "slug": "reminder"}, headers={"X-CSRF-Token": csrf})
    assert created.status_code == 201
    workflow_id = created.json()["id"]
    cycle = {"nodes": [{"node_key": "a", "node_type": "trigger"}, {"node_key": "b", "node_type": "end"}], "edges": [{"source_key": "a", "target_key": "b"}, {"source_key": "b", "target_key": "a"}]}
    checked = client.post(f"/api/v1/organizations/automation-org/automation/workflows/{workflow_id}/validate", json=cycle)
    assert checked.status_code == 200 and checked.json()["valid"] is False
    version = client.post(f"/api/v1/organizations/automation-org/automation/workflows/{workflow_id}/versions", json=valid_graph(), headers={"X-CSRF-Token": csrf})
    assert version.status_code == 201
    published = client.post(f"/api/v1/organizations/automation-org/automation/workflows/{workflow_id}/versions/{version.json()['id']}/publish", headers={"X-CSRF-Token": csrf})
    assert published.status_code == 200
    first = client.post(f"/api/v1/organizations/automation-org/automation/workflows/{workflow_id}/runs", json={"idempotency_key": "same-request-001"}, headers={"X-CSRF-Token": csrf})
    second = client.post(f"/api/v1/organizations/automation-org/automation/workflows/{workflow_id}/runs", json={"idempotency_key": "same-request-001"}, headers={"X-CSRF-Token": csrf})
    assert first.status_code == 202 and second.status_code == 202
    assert first.json()["id"] == second.json()["id"] and first.json()["execution"] == "worker_not_configured"


def test_automation_isolation_and_truthful_provider_state(client):
    csrf = owner_with_org(client, "automation-owner-two@test", "automation-org-two")
    client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf})
    student(client, "automation-outsider@test")
    assert client.get("/api/v1/organizations/automation-org-two/automation").status_code == 403
    assert client.get("/api/v1/platform/automation").status_code == 403
