from datetime import datetime, timezone
from sqlalchemy import select
from app.models import ProjectMilestone, ProjectTemplate, StudentProject, User
def verified_client(client,email="project@example.com"):
    response=client.post("/api/v1/auth/register",json={"full_name":"Project Student","email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True});assert response.status_code==201
    with client.session_factory() as db:
        user=db.scalar(select(User).where(User.email==email));user.email_verified_at=datetime.now(timezone.utc);db.commit()
    return client.cookies.get("cm_csrf")
def seed_project(client):
    with client.session_factory() as db:
        row=ProjectTemplate(title="Portfolio API",slug="portfolio-api",description_en="Build an API.",difficulty="intermediate",estimated_hours=20,status="published",published=True);db.add(row);db.flush();db.add(ProjectMilestone(project_id=row.id,title="Design",description_en="Design the API",position=0));db.commit();return row.id
def test_published_project_start_and_duplicate_prevention(client):
    project_id=seed_project(client);assert client.get("/api/v1/projects").json()["total"]==1;csrf=verified_client(client);response=client.post("/api/v1/me/projects/portfolio-api",headers={"X-CSRF-Token":csrf});assert response.status_code==201;assert client.post("/api/v1/me/projects/portfolio-api",headers={"X-CSRF-Token":csrf}).status_code==409;assert project_id
def test_github_submission_rejects_non_github_url(client):
    seed_project(client);csrf=verified_client(client,"project-url@example.com");start=client.post("/api/v1/me/projects/portfolio-api",headers={"X-CSRF-Token":csrf}).json();response=client.post(f"/api/v1/me/projects/{start['id']}/submissions",json={"repository_url":"https://example.com/repo","branch_or_sha":"main"},headers={"X-CSRF-Token":csrf});assert response.status_code==422
