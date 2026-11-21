from datetime import datetime, timezone
from io import BytesIO
from zipfile import ZipFile
from sqlalchemy import select
from app.auth import password_hasher
from app.config import settings
from app.models import ProjectCategory, ProjectMilestone, ProjectTemplate, ProjectRubricCriterion, User
def verified_client(client,email="project@example.com"):
    response=client.post("/api/v1/auth/register",json={"full_name":"Project Student","email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True});assert response.status_code==201
    with client.session_factory() as db:
        user=db.scalar(select(User).where(User.email==email));user.email_verified_at=datetime.now(timezone.utc);db.commit()
    return client.cookies.get("cm_csrf")
def admin_client(client,email="project-admin@example.com"):
    with client.session_factory() as db:
        db.add(User(email=email,email_normalized=email,password_hash=password_hasher.hash("admin-pass-123"),display_name="Project Admin",role="platform_admin",account_status="active",email_verified_at=datetime.now(timezone.utc)));db.commit()
    response=client.post("/api/v1/admin/auth/login",json={"email":email,"password":"admin-pass-123"});assert response.status_code==200
    return client.cookies.get("cm_csrf")
def seed_project(client):
    with client.session_factory() as db:
        category=ProjectCategory(name="Backend Development",slug="backend-development",status="active");db.add(category);db.flush();row=ProjectTemplate(title="Portfolio API",slug="portfolio-api",description_en="Build an API.",difficulty="intermediate",estimated_hours=20,technology_stack="Python, FastAPI",category_id=category.id,status="published",published=True);db.add(row);db.flush();db.add(ProjectMilestone(project_id=row.id,title="Design",slug="design",description_en="Design the API",content_en="Design theory",position=0));db.commit();return row.id
def test_published_project_start_and_duplicate_prevention(client):
    project_id=seed_project(client);assert client.get("/api/v1/projects").json()["total"]==1;csrf=verified_client(client);response=client.post("/api/v1/me/projects/portfolio-api",headers={"X-CSRF-Token":csrf});assert response.status_code==201;assert client.post("/api/v1/me/projects/portfolio-api",headers={"X-CSRF-Token":csrf}).status_code==409;assert project_id
def test_github_submission_rejects_non_github_url(client):
    seed_project(client);csrf=verified_client(client,"project-url@example.com");start=client.post("/api/v1/me/projects/portfolio-api",headers={"X-CSRF-Token":csrf}).json();response=client.post(f"/api/v1/me/projects/{start['id']}/submissions",json={"repository_url":"https://example.com/repo","branch_or_sha":"main"},headers={"X-CSRF-Token":csrf});assert response.status_code==422

def test_project_catalog_filters_and_step_reader(client):
    seed_project(client)
    assert client.get("/api/v1/project-categories").json()[0]["slug"] == "backend-development"
    assert client.get("/api/v1/projects?technology=FastAPI").json()["total"] == 1
    detail=client.get("/api/v1/projects/portfolio-api"); assert detail.status_code == 200; assert detail.json()["milestones"][0]["slug"] == "design"
    assert client.get("/api/v1/projects/portfolio-api/steps").json()[0]["content_en"] == "Design theory"

def test_project_bookmark_requires_owned_authenticated_session(client):
    project_id=seed_project(client)
    assert client.post(f"/api/v1/projects/{project_id}/bookmark").status_code in {401, 403}
    csrf=verified_client(client,"project-bookmark@example.com")
    assert client.post(f"/api/v1/projects/{project_id}/bookmark",headers={"X-CSRF-Token":csrf}).status_code == 200

def test_admin_project_draft_builder_and_publish_workflow(client):
    csrf=admin_client(client)
    created=client.post("/api/v1/admin/projects",json={"title":"Draft API Lab","slug":"draft-api-lab"},headers={"X-CSRF-Token":csrf})
    assert created.status_code==201
    project_id=created.json()["id"]
    assert client.get(f"/api/v1/admin/projects/{project_id}").status_code==200
    assert client.get(f"/api/v1/admin/projects/{project_id}/requirements").status_code==200
    assert client.post(f"/api/v1/admin/projects/{project_id}/publish",json={"published":True},headers={"X-CSRF-Token":csrf}).status_code==422
    assert client.patch(f"/api/v1/admin/projects/{project_id}",json={"description_en":"Build an API","learning_outcomes":"Learn APIs","technology_stack":"FastAPI","testing_guide":"Run tests"},headers={"X-CSRF-Token":csrf}).status_code==200
    milestone=client.post(f"/api/v1/admin/projects/{project_id}/milestones",json={"title":"Build","content_en":"Build the service","position":0},headers={"X-CSRF-Token":csrf});assert milestone.status_code==201
    requirement=client.post(f"/api/v1/admin/projects/{project_id}/requirements",json={"title":"Working endpoint","position":0},headers={"X-CSRF-Token":csrf});assert requirement.status_code==201
    rubric=client.post(f"/api/v1/admin/projects/{project_id}/rubric",json={"name":"Implementation","weight":100,"position":0},headers={"X-CSRF-Token":csrf});assert rubric.status_code==201
    assert client.patch(f"/api/v1/admin/projects/{project_id}/milestones/{milestone.json()['id']}",json={"content_en":"Updated content"},headers={"X-CSRF-Token":csrf}).status_code==200
    published=client.post(f"/api/v1/admin/projects/{project_id}/publish",json={"published":True},headers={"X-CSRF-Token":csrf});assert published.status_code==200, published.text
    assert client.get("/api/v1/projects/draft-api-lab").status_code==200

def test_project_management_permissions_and_private_resources(client):
    project_id=seed_project(client)
    assert client.get(f"/api/v1/admin/projects/{project_id}").status_code in {401,403}
    csrf=admin_client(client,"project-admin-private@example.com")
    resource=client.post(f"/api/v1/admin/projects/{project_id}/resources",json={"title":"Private starter","resource_type":"link","url":"https://example.com/starter","is_public":False},headers={"X-CSRF-Token":csrf});assert resource.status_code==201, resource.text
    assert all(item["title"]!="Private starter" for item in client.get("/api/v1/projects/portfolio-api").json()["resources"])
    assert client.get("/api/v1/admin/project-metrics").status_code==200

def test_project_cover_upload_uses_shared_media_storage(client):
    csrf=admin_client(client,"project-cover-admin@example.com")
    created=client.post("/api/v1/admin/projects",json={"title":"Cover Project","slug":"cover-project"},headers={"X-CSRF-Token":csrf});assert created.status_code==201
    png=b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0dIDAT\x08\xd7c\xf8\xcf\xc0\xf0\x1f\x00\x05\x00\x01\xff\x89\x99=\x1d\x00\x00\x00\x00IEND\xaeB`\x82"
    response=client.post(f"/api/v1/admin/projects/{created.json()['id']}/cover-image",files={"image":("cover.png",png,"image/png")},headers={"X-CSRF-Token":csrf})
    assert response.status_code==200,response.text
    assert response.json()["url"].startswith("/media/projects/")

def test_project_zip_submission_is_private_and_downloadable_by_owner_or_admin(client, monkeypatch, tmp_path):
    project_id=seed_project(client)
    csrf=verified_client(client,"project-zip@example.com")
    started=client.post("/api/v1/me/projects/portfolio-api",headers={"X-CSRF-Token":csrf}).json()
    with client.session_factory() as db:
        milestone=db.scalar(select(ProjectMilestone).where(ProjectMilestone.project_id==project_id))
    completed=client.post(f"/api/v1/me/projects/{started['id']}/milestones/{milestone.id}",json={"completed":True,"notes":"Done"},headers={"X-CSRF-Token":csrf})
    assert completed.status_code==200
    archive=BytesIO()
    with ZipFile(archive,"w") as zipped:
        zipped.writestr("README.md","safe archive")
    monkeypatch.setattr(settings,"media_root",str(tmp_path/"media"))
    response=client.post(f"/api/v1/me/projects/{started['id']}/submissions/upload",data={"branch_or_sha":"main","project_description":"Archive submission"},files={"archive":("submission.zip",archive.getvalue(),"application/zip")},headers={"X-CSRF-Token":csrf})
    assert response.status_code==201,response.text
    submission_id=response.json()["id"]
    assert client.get(f"/api/v1/me/project-submissions/{submission_id}/download").status_code==200
    admin_csrf=admin_client(client,"project-zip-admin@example.com")
    detail=client.get(f"/api/v1/instructor/projects/reviews/{submission_id}")
    assert detail.status_code==200 and detail.json()["has_attachment"] is True
    downloaded=client.get(f"/api/v1/admin/project-submissions/{submission_id}/download")
    assert downloaded.status_code==200 and downloaded.content.startswith(b"PK")
    assert admin_csrf
