from datetime import datetime, timezone, timedelta
from app.auth import password_hasher
from app.models import CommunityEvent, DeveloperPublicProfile, User

def user(client,email,name="Community User"):
    r=client.post("/api/v1/auth/register",json={"full_name":name,"email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True});assert r.status_code==201
    with client.session_factory() as db:
        row=db.query(User).filter(User.email_normalized==email).one();row.email_verified_at=datetime.now(timezone.utc);db.commit()
    client.post("/api/v1/auth/login",json={"email":email,"password":"strong-pwd12"});return client.cookies.get("cm_csrf")
def admin(client,email="community-network-admin@example.com"):
    with client.session_factory() as db:db.add(User(email=email,email_normalized=email,password_hash=password_hasher.hash("Admin-pass12"),display_name="Community Admin",role="platform_admin",account_status="active",email_verified_at=datetime.now(timezone.utc)));db.commit()
    client.post("/api/v1/auth/login",json={"email":email,"password":"Admin-pass12"});return client.cookies.get("cm_csrf")
def test_developer_discovery_is_public_profile_only(client):
    csrf=user(client,"community-public@example.com","Public Developer")
    with client.session_factory() as db:
        row=db.query(User).filter(User.email_normalized=="community-public@example.com").one();db.add(DeveloperPublicProfile(user_id=row.id,username="public-developer",headline="Python builder",visibility="public"));db.commit()
    result=client.get("/api/v1/community-network/developers");assert result.status_code==200 and result.json()[0]["username"]=="public-developer" and "email" not in result.text
def test_event_capacity_and_admin_publish(client):
    csrf=user(client,"community-event-owner@example.com","Event Owner")
    start=datetime.now(timezone.utc)+timedelta(days=1);body={"title":"Python Study Session","description":"A real session","event_type":"study_group","starts_at":start.isoformat(),"ends_at":(start+timedelta(hours=1)).isoformat(),"capacity":1}
    created=client.post("/api/v1/community-network/events",json=body,headers={"X-CSRF-Token":csrf});assert created.status_code==201
    assert client.get("/api/v1/community-network/events").json()==[]
    admin_csrf=admin(client);assert client.post(f"/api/v1/community-network/events/{created.json()['id']}/publish",headers={"X-CSRF-Token":admin_csrf}).status_code==200
    client.post("/api/v1/auth/logout");first=user(client,"community-attendee1@example.com","Attendee One");assert client.post(f"/api/v1/community-network/events/{created.json()['id']}/register",headers={"X-CSRF-Token":first}).json()["status"]=="registered"
    client.post("/api/v1/auth/logout");second=user(client,"community-attendee2@example.com","Attendee Two");assert client.post(f"/api/v1/community-network/events/{created.json()['id']}/register",headers={"X-CSRF-Token":second}).json()["status"]=="waitlisted"
def test_platform_analytics_requires_admin(client):
    user(client,"community-analytics-student@example.com");assert client.get("/api/v1/community-network/analytics").status_code==403
