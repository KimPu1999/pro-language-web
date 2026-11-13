from datetime import datetime, timezone
from sqlalchemy import select
from app.models import CareerRoadmap, RoadmapStage, RoadmapStep, User

def verified_client(client,email="roadmap@example.com"):
    response=client.post("/api/v1/auth/register",json={"full_name":"Roadmap Student","email":email,"password":"strong-pass-123","confirm_password":"strong-pass-123","accept_terms":True}); assert response.status_code==201
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
