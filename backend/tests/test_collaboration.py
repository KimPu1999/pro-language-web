from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.models import DeveloperTeam, DeveloperTeamMember, User

def verified_student(client, email="team@example.com"):
    response=client.post("/api/v1/auth/register",json={"full_name":"Team Student","email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True}); assert response.status_code==201
    with client.session_factory() as db:
        user=db.scalar(select(User).where(User.email==email)); user.email_verified_at=datetime.now(timezone.utc); db.commit()
    client.post("/api/v1/auth/login",json={"email":email,"password":"strong-pwd12"}); return client.cookies.get("cm_csrf")

def test_team_creation_assigns_owner_and_isolation(client):
    csrf=verified_student(client); created=client.post("/api/v1/teams",json={"name":"Builders","description":"Shared work"},headers={"X-CSRF-Token":csrf}); assert created.status_code==201
    team_id=created.json()["id"]; detail=client.get(f"/api/v1/teams/{team_id}"); assert detail.status_code==200; assert detail.json()["role"]=="owner"; assert detail.json()["members"][0]["role"]=="owner"

def test_anonymous_team_and_competition_mutations_are_blocked(client):
    assert client.post("/api/v1/teams",json={"name":"Nope"}).status_code==401
    assert client.post("/api/v1/competitions/00000000-0000-0000-0000-000000000000/register").status_code==401

def test_collaboration_realtime_is_truthfully_unavailable_for_admin(client):
    assert client.get("/api/v1/platform/collaboration/status").status_code==401
