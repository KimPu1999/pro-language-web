from datetime import datetime, timezone
from sqlalchemy import select
from app.auth import password_hasher
from app.models import CareerRoadmap, Course, RoadmapStage, RoadmapStep, User

def verified_client(client,email="roadmap@example.com"):
    response=client.post("/api/v1/auth/register",json={"full_name":"Roadmap Student","email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True}); assert response.status_code==201
    with client.session_factory() as db:
        user=db.scalar(select(User).where(User.email==email)); user.email_verified_at=datetime.now(timezone.utc); db.commit()
    return client.cookies.get("cm_csrf")
def seed_roadmap(client):
    with client.session_factory() as db:
        roadmap=CareerRoadmap(title="Backend Developer",slug="backend-developer",career_category="Backend",description_en="Build services.",outcomes_en="Ship APIs",estimated_hours=20,status="published",published=True); db.add(roadmap);db.flush();stage=RoadmapStage(roadmap_id=roadmap.id,title="Foundations",description_en="Start here",level="beginner",position=0);db.add(stage);db.flush();db.add(RoadmapStep(stage_id=stage.id,title="HTTP basics",instructions_en="Learn HTTP",position=0));db.commit();return roadmap.id
def test_published_roadmap_detail_and_student_enrollment(client):
    roadmap_id=seed_roadmap(client); assert client.get("/api/v1/roadmaps").json()["total"]==1; assert client.get("/api/v1/roadmaps/backend-developer").status_code==200
    csrf=verified_client(client); response=client.post("/api/v1/me/roadmaps/backend-developer",headers={"X-CSRF-Token":csrf}); assert response.status_code==201; assert client.post("/api/v1/me/roadmaps/backend-developer",headers={"X-CSRF-Token":csrf}).status_code==409; assert roadmap_id
def test_roadmap_goal_is_owned_by_current_student(client):
    csrf=verified_client(client,"goal@example.com"); response=client.put("/api/v1/me/goals",json={"career_goal":"Python Developer","current_level":"beginner","interests":["python"],"weekly_hours":5,"pace":"steady","timezone":"Asia/Yangon"},headers={"X-CSRF-Token":csrf}); assert response.status_code==200; assert client.get("/api/v1/me/goals").json()["career_goal"]=="Python Developer"

def admin_client(client):
    with client.session_factory() as db:
        db.add(User(email="career-admin@example.com",email_normalized="career-admin@example.com",password_hash=password_hasher.hash("Admin-pass12"),display_name="Career Admin",role="platform_admin",account_status="active",email_verified_at=datetime.now(timezone.utc)));db.commit()
    response=client.post("/api/v1/auth/login",json={"email":"career-admin@example.com","password":"Admin-pass12"}); assert response.status_code==200
    return client.cookies.get("cm_csrf")

def test_admin_career_path_draft_builder_and_publish(client):
    csrf=admin_client(client)
    created=client.post("/api/v1/admin/roadmaps",json={"title":"","slug":"career-builder-draft","description_en":"","career_category":""},headers={"X-CSRF-Token":csrf}); assert created.status_code==201
    roadmap_id=created.json()["id"]
    assert client.get(f"/api/v1/admin/roadmaps/{roadmap_id}").status_code==200
    assert client.get(f"/api/v1/admin/roadmaps/{roadmap_id}/preview").status_code==200
    updated=client.patch(f"/api/v1/admin/roadmaps/{roadmap_id}",json={"title":"Frontend Engineer Path","description_en":"Build production interfaces.","goals":["Ship accessible interfaces"],"skills":["React"]},headers={"X-CSRF-Token":csrf}); assert updated.status_code==200
    stage=client.post(f"/api/v1/admin/roadmaps/{roadmap_id}/stages",json={"title":"Foundations","level":"beginner","position":0,"objectives":["Understand the web"],"skills":["HTML"]},headers={"X-CSRF-Token":csrf}); assert stage.status_code==201
    stage_id=stage.json()["id"]
    step=client.post(f"/api/v1/admin/stages/{stage_id}/steps",json={"title":"HTML basics","instructions_en":"Read the lesson","position":0},headers={"X-CSRF-Token":csrf}); assert step.status_code==201
    step_id=step.json()["id"]
    with client.session_factory() as db: course_id=db.scalar(select(Course.id))
    linked=client.post(f"/api/v1/admin/steps/{step_id}/resources",json={"resource_type":"course","resource_id":str(course_id)},headers={"X-CSRF-Token":csrf}); assert linked.status_code==200
    assert client.post(f"/api/v1/admin/roadmaps/{roadmap_id}/publish",json={},headers={"X-CSRF-Token":csrf}).status_code==200
    detail=client.get(f"/api/v1/admin/roadmaps/{roadmap_id}").json(); assert detail["published"] is True; assert detail["goals"]==["Ship accessible interfaces"]

def test_admin_career_path_requires_auth_and_preserves_drafts(client):
    created=client.post("/api/v1/admin/roadmaps",json={"title":"No access","slug":"no-access"}); assert created.status_code in {401,403}
    csrf=admin_client(client); draft=client.post("/api/v1/admin/roadmaps",json={"title":"Private draft","slug":"private-draft"},headers={"X-CSRF-Token":csrf}); assert draft.status_code==201
    detail=client.get(f"/api/v1/roadmaps/private-draft"); assert detail.status_code==404

def test_admin_management_capability_endpoints_are_protected_and_live(client):
    assert client.get("/api/v1/admin/audit-logs").status_code in {401,403}
    csrf=admin_client(client)
    for path in ("/api/v1/admin/audit-logs", "/api/v1/admin/media", "/api/v1/admin/settings/overview", "/api/v1/admin/settings/seo", "/api/v1/admin/security/overview"):
        response=client.get(path)
        assert response.status_code==200, (path, response.text)
    assert csrf
