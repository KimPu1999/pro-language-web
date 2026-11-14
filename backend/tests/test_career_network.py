from datetime import datetime, timezone
from app.auth import password_hasher
from app.models import CareerRoleDefinition, DeveloperTalentProfile, User

def student(client,email="career-network@example.com"):
    r=client.post("/api/v1/auth/register",json={"full_name":"Career Student","email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True}); assert r.status_code==201
    with client.session_factory() as db:
        u=db.query(User).filter(User.email_normalized==email).one();u.email_verified_at=datetime.now(timezone.utc);db.commit()
    client.post("/api/v1/auth/login",json={"email":email,"password":"strong-pwd12"});return client.cookies.get("cm_csrf")
def admin(client,email="career-network-admin@example.com"):
    with client.session_factory() as db: db.add(User(email=email,email_normalized=email,password_hash=password_hasher.hash("Admin-pass12"),display_name="Career Admin",role="platform_admin",account_status="active",email_verified_at=datetime.now(timezone.utc)));db.commit()
    client.post("/api/v1/auth/login",json={"email":email,"password":"Admin-pass12"});return client.cookies.get("cm_csrf")
def test_talent_is_private_until_explicit_visibility(client):
    csrf=student(client); assert client.get("/api/v1/career-network/dashboard").status_code==200
    assert client.get("/api/v1/career-network/profiles/Career Student").status_code==404
    assert client.put("/api/v1/career-network/visibility",json={"profile_public":True,"employer_discoverable":True,"contact_allowed":True},headers={"X-CSRF-Token":csrf}).status_code==200
    public=client.get("/api/v1/career-network/profiles/Career Student");assert public.status_code==200 and "email" not in public.text
def test_employer_and_job_require_platform_review(client):
    csrf=student(client,"employer-owner@example.com")
    created=client.post("/api/v1/career-network/employer/organizations",json={"name":"Example Labs","website":"https://example.org"},headers={"X-CSRF-Token":csrf});assert created.status_code==201
    assert client.post("/api/v1/career-network/employer/jobs",json={"title":"Python Developer","description":"Build APIs","external_url":"https://example.org/jobs/1"},headers={"X-CSRF-Token":csrf}).status_code==403
    admin_csrf=admin(client); assert client.post(f"/api/v1/career-network/platform/employers/{created.json()['id']}/decision",json={"decision":"approve"},headers={"X-CSRF-Token":admin_csrf}).status_code==200
def test_skill_gap_uses_published_roles_only(client):
    csrf=student(client,"skill-gap@example.com")
    with client.session_factory() as db: db.add(CareerRoleDefinition(slug="backend",title="Backend Developer",status="published"));db.commit()
    result=client.get("/api/v1/career-network/skill-gap?role_slug=backend");assert result.status_code==200 and result.json()["evidence_based"] is True
