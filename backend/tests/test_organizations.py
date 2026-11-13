from datetime import datetime, timezone

def student(client,email):
    result=client.post("/api/v1/auth/register",json={"full_name":"Org Student","email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True})
    assert result.status_code==201
    user_id=result.json()["id"]
    with client.session_factory() as db:
        from app.models import User
        db.get(User,user_id).email_verified_at=datetime.now(timezone.utc);db.commit()
    client.post("/api/v1/auth/login",json={"email":email,"password":"strong-pwd12"})
    return client.cookies.get("cm_csrf")

def test_organization_creation_and_duplicate_slug(client):
    csrf=student(client,"owner@organization.test")
    payload={"name":"Acme Learning","slug":"acme-learning","description":"Private training"}
    created=client.post("/api/v1/organizations",json=payload,headers={"X-CSRF-Token":csrf})
    assert created.status_code==201
    assert client.post("/api/v1/organizations",json=payload,headers={"X-CSRF-Token":csrf}).status_code==409
    dashboard=client.get("/api/v1/organizations/acme-learning/dashboard")
    assert dashboard.status_code==200 and dashboard.json()["metrics"]["active_members"]==1

def test_organization_membership_isolation(client):
    csrf=student(client,"first@organization.test")
    assert client.post("/api/v1/organizations",json={"name":"First Org","slug":"first-org"},headers={"X-CSRF-Token":csrf}).status_code==201
    client.post("/api/v1/auth/logout",headers={"X-CSRF-Token":csrf})
    student(client,"second@organization.test")
    assert client.get("/api/v1/organizations/first-org/dashboard").status_code==403

def test_public_course_is_not_implicitly_private_org_course(client):
    assert client.get("/api/v1/organizations/unknown/courses").status_code==401
