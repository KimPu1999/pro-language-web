from test_organizations import student


def owner_org(client, email="content-owner@test", slug="content-org"):
    csrf = student(client, email)
    created = client.post("/api/v1/organizations", json={"name": "Content Org", "slug": slug}, headers={"X-CSRF-Token": csrf})
    assert created.status_code == 201
    return csrf


def test_content_drafts_are_tenant_scoped_and_ai_unavailable_is_truthful(client):
    csrf = owner_org(client)
    project = client.post("/api/v1/organizations/content-org/content-studio/projects", json={"title": "Python course", "content_type": "course"}, headers={"X-CSRF-Token": csrf})
    assert project.status_code == 201
    project_id = project.json()["id"]
    job = client.post(f"/api/v1/organizations/content-org/content-studio/projects/{project_id}/generate", json={"job_type": "lesson", "inputs": {"topic": "loops"}, "idempotency_key": "content-job-001"}, headers={"X-CSRF-Token": csrf})
    assert job.status_code == 202 and job.json()["status"] == "provider_unavailable"
    duplicate = client.post(f"/api/v1/organizations/content-org/content-studio/projects/{project_id}/generate", json={"job_type": "lesson", "inputs": {}, "idempotency_key": "content-job-001"}, headers={"X-CSRF-Token": csrf})
    assert duplicate.json()["id"] == job.json()["id"]
    client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf})
    student(client, "content-outsider@test")
    assert client.get("/api/v1/organizations/content-org/content-studio").status_code == 403


def test_unapproved_revision_cannot_be_published(client):
    csrf = owner_org(client, "publisher@test", "publisher-org")
    project = client.post("/api/v1/organizations/publisher-org/content-studio/projects", json={"title": "Lesson draft", "content_type": "lesson"}, headers={"X-CSRF-Token": csrf}).json()
    revision = client.post(f"/api/v1/organizations/publisher-org/content-studio/projects/{project['id']}/revisions", json={"content_type": "lesson", "snapshot": {"title": "Draft"}}, headers={"X-CSRF-Token": csrf}).json()
    response = client.post(f"/api/v1/organizations/publisher-org/content-studio/projects/{project['id']}/publish?revision_id={revision['id']}", headers={"X-CSRF-Token": csrf})
    assert response.status_code == 409
