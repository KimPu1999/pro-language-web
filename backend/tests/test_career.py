from datetime import datetime, timezone
from sqlalchemy import select
from app.models import User

def student(client, email="career@example.com"):
    response=client.post("/api/v1/auth/register",json={"full_name":"Career Student","email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True}); assert response.status_code==201
    with client.session_factory() as db:
        user=db.scalar(select(User).where(User.email==email)); user.email_verified_at=datetime.now(timezone.utc); db.commit()
    client.post("/api/v1/auth/login",json={"email":email,"password":"strong-pwd12"}); return client.cookies.get("cm_csrf")

def test_career_dashboard_does_not_fabricate_readiness(client):
    student(client); response=client.get("/api/v1/career/dashboard"); assert response.status_code==200; assert response.json()["readiness"]["status"]=="not_yet_assessed"

def test_private_application_records_are_owned(client):
    csrf=student(client,"applications@example.com"); created=client.post("/api/v1/career/applications",json={"company_name":"Example","job_title":"Junior Developer"},headers={"X-CSRF-Token":csrf}); assert created.status_code==201; assert client.get("/api/v1/career/applications").json()[0]["company_name"]=="Example"

def test_career_private_endpoints_reject_anonymous(client):
    assert client.get("/api/v1/career/dashboard").status_code==401
    assert client.get("/api/v1/career/applications").status_code==401
