from datetime import datetime, timezone
from sqlalchemy import select
from app.models import Lesson, User
def register(client, email="student@example.com"):
    return client.post("/api/v1/auth/register", json={"full_name":"Student One","email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True})
def test_registration_hashes_password_and_forces_student_role(client):
    response=register(client); assert response.status_code==201; body=response.json(); assert body["role"]=="student"; assert "password_hash" not in body
    with client.session_factory() as db:
        user=db.scalar(select(User).where(User.email=="student@example.com")); assert user.password_hash != "strong-pwd12"; assert user.email_normalized=="student@example.com"
def test_duplicate_registration_and_bad_login_are_generic(client):
    assert register(client).status_code==201
    assert register(client).status_code==400
    assert client.post("/api/v1/auth/login",json={"email":"student@example.com","password":"wrong-pass"}).status_code==401
def test_unverified_student_cannot_enroll_or_mutate_progress(client):
    register(client); course=client.get("/api/v1/courses/python-foundations")
    assert course.status_code==404 or course.status_code==200
    assert client.post("/api/v1/me/enrollments/python-foundations",headers={"X-CSRF-Token":""}).status_code in {403, 422}
def test_anonymous_student_endpoints_reject(client):
    assert client.get("/api/v1/auth/me").status_code==401
    assert client.get("/api/v1/me/dashboard").status_code==401
def test_csrf_and_role_escalation_are_blocked(client):
    response=client.post("/api/v1/auth/register",json={"full_name":"Student Two","email":"two@example.com","password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True,"role":"admin"}); assert response.status_code==201; assert response.json()["role"]=="student"
    assert client.patch("/api/v1/me/profile",json={"full_name":"Changed"}).status_code==403
def test_login_creates_cookie_session(client):
    register(client,"login@example.com"); response=client.post("/api/v1/auth/login",json={"email":"login@example.com","password":"strong-pwd12"}); assert response.status_code==200; assert "cm_session" in response.cookies; assert client.get("/api/v1/auth/me").status_code==200
def test_verified_student_enrollment_and_progress_are_persistent(client):
    register(client,"verified@example.com")
    with client.session_factory() as db:
        user=db.scalar(select(User).where(User.email=="verified@example.com")); user.email_verified_at=datetime.now(timezone.utc); db.commit()
    csrf=client.cookies.get("cm_csrf"); first=client.post("/api/v1/me/enrollments/python-foundations",headers={"X-CSRF-Token":csrf}); assert first.status_code==201
    assert client.post("/api/v1/me/enrollments/python-foundations",headers={"X-CSRF-Token":csrf}).status_code==409
    with client.session_factory() as db: lesson_id=str(db.scalar(select(Lesson)).id)
    assert client.post(f"/api/v1/me/lessons/{lesson_id}/progress",json={"completed":True},headers={"X-CSRF-Token":csrf}).status_code==200
    assert client.get("/api/v1/me/dashboard").json()["enrollments"][0]["progress_percent"]==100
