from datetime import datetime, timezone
from sqlalchemy import select
from app.auth import password_hasher
from app.models import Course, CourseCategory, ProgrammingLanguage, User
def admin_login(client):
    with client.session_factory() as db:
        user=User(email="admin@example.com",email_normalized="admin@example.com",password_hash=password_hasher.hash("admin-pass-123"),display_name="Admin",role="admin",account_status="active",email_verified_at=datetime.now(timezone.utc)); db.add(user); db.commit()
    assert client.post("/api/v1/auth/login",json={"email":"admin@example.com","password":"admin-pass-123"}).status_code==200
    return client.cookies.get("cm_csrf")
def test_students_cannot_access_admin_apis(client):
    assert client.get("/api/v1/admin/dashboard").status_code==401
def test_admin_course_create_and_publish_validation(client):
    csrf=admin_login(client); lang=client.get("/api/v1/languages").json()[0]; category=client.get("/api/v1/categories").json()[0]
    payload={"title":"Admin Course","slug":"admin-course","short_description":"Short","description":"Long","language_id":lang["id"],"category_id":category["id"],"level":"beginner","estimated_duration":90,"outcomes":[],"requirements":[]}
    response=client.post("/api/v1/admin/courses",json=payload,headers={"X-CSRF-Token":csrf}); assert response.status_code==201; course_id=response.json()["id"]
    assert client.post(f"/api/v1/admin/courses/{course_id}/publish",json={"decision":"publish"},headers={"X-CSRF-Token":csrf}).status_code==422
def test_admin_duplicate_language_slug_is_rejected(client):
    csrf=admin_login(client); language=client.get("/api/v1/languages").json()[0]; response=client.post("/api/v1/admin/languages",json={"name":"Duplicate","slug":language["slug"]},headers={"X-CSRF-Token":csrf}); assert response.status_code==409
