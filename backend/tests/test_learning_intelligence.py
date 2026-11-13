from datetime import datetime, timezone
from sqlalchemy import select
from app.models import LessonProgress, SkillDefinition, StudentSkillEvidence, User

def login_student(client, email="intelligence@example.com", verified=False):
    response = client.post("/api/v1/auth/register", json={"full_name":"Intelligence Student","email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True})
    assert response.status_code == 201
    with client.session_factory() as db:
        user = db.scalar(select(User).where(User.email == email))
        if verified:
            user.email_verified_at = datetime.now(timezone.utc)
        db.commit()
    client.post("/api/v1/auth/login", json={"email":email,"password":"strong-pwd12"})
    return client.cookies.get("cm_csrf")

def test_intelligence_marks_insufficient_evidence(client):
    login_student(client)
    with client.session_factory() as db:
        db.add(SkillDefinition(name="Python", slug="python-skill", category="language")); db.commit()
    response = client.get("/api/v1/learning/intelligence")
    assert response.status_code == 200
    assert response.json()["skills"][0]["confidence"] == "not_yet_assessed"
    assert response.json()["skills"][0]["score"] is None

def test_study_plan_requires_verified_student_and_is_owned(client):
    csrf = login_student(client, "plan@example.com", verified=True)
    response = client.post("/api/v1/learning/study-plans", json={"title":"Week one"}, headers={"X-CSRF-Token":csrf})
    assert response.status_code == 201
    plan = client.get("/api/v1/learning/study-plans")
    assert plan.status_code == 200 and plan.json()["items"][0]["title"] == "Week one"

def test_learning_endpoints_reject_anonymous_access(client):
    assert client.get("/api/v1/learning/intelligence").status_code == 401
    assert client.get("/api/v1/learning/recommendations").status_code == 401
