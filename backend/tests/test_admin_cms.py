from datetime import datetime, timezone
from sqlalchemy import select
from app.auth import password_hasher
from app.models import User
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

def test_admin_can_edit_lesson_examples_and_quiz(client):
    from app.models import Course, CourseModule, Lesson
    csrf=admin_login(client)
    with client.session_factory() as db:
        course=db.scalar(select(Course).where(Course.slug=="python-foundations"))
        module=db.scalar(select(CourseModule).where(CourseModule.course_id==course.id))
        lesson=db.scalar(select(Lesson).where(Lesson.module_id==module.id))
        course_id, lesson_id = str(course.id), str(lesson.id)
    curriculum=client.get(f"/api/v1/admin/courses/{course_id}/curriculum"); assert curriculum.status_code==200
    lesson_payload={"title":"Hello updated","slug":"hello","description":"Updated description","content_en":"Introduction\nUpdated content","content_mm":"မြန်မာ","position":1,"duration_minutes":25,"status":"published"}
    updated=client.patch(f"/api/v1/admin/lessons/{lesson_id}",json=lesson_payload,headers={"X-CSRF-Token":csrf}); assert updated.status_code==200; assert updated.json()["title"]=="Hello updated"
    example_payload={"title":"Hello example","language":"c","filename":"hello.c","source_code":"#include <stdio.h>\n\nint main(void) { return 0; }\n","description":"Expected output:\n","position":1}
    created=client.post(f"/api/v1/admin/lessons/{lesson_id}/examples",json=example_payload,headers={"X-CSRF-Token":csrf}); assert created.status_code==201; example_id=created.json()["id"]
    examples=client.get(f"/api/v1/admin/lessons/{lesson_id}/examples"); assert examples.status_code==200; assert examples.json()[0]["filename"]=="hello.c"
    example_payload["title"]="Hello example updated"; assert client.patch(f"/api/v1/admin/examples/{example_id}",json=example_payload,headers={"X-CSRF-Token":csrf}).status_code==200
    question_payload={"prompt":"What does printf return?","options":["A number","A string"],"correct_answer":"A number","explanation":"printf returns the number of printed characters.","question_type":"multiple_choice","position":1}
    question=client.post(f"/api/v1/admin/lessons/{lesson_id}/quiz/questions",json=question_payload,headers={"X-CSRF-Token":csrf}); assert question.status_code==201; question_id=question.json()["id"]
    question_payload["prompt"]="What does printf write to?"; question_payload["position"]=1
    assert client.patch(f"/api/v1/admin/quiz/questions/{question_id}",json=question_payload,headers={"X-CSRF-Token":csrf}).status_code==200
    invalid={**question_payload,"correct_answer":"Not an option"}; assert client.patch(f"/api/v1/admin/quiz/questions/{question_id}",json=invalid,headers={"X-CSRF-Token":csrf}).status_code==422
    quiz=client.get(f"/api/v1/admin/lessons/{lesson_id}/quiz"); assert quiz.status_code==200; assert quiz.json()["questions"][0]["prompt"]=="What does printf write to?"

def test_student_cannot_use_admin_lesson_editing(client):
    from app.models import Lesson
    client.post("/api/v1/auth/register",json={"full_name":"Student Editor","email":"editor@example.com","password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True})
    csrf=client.cookies.get("cm_csrf")
    with client.session_factory() as db: lesson_id=str(db.scalar(select(Lesson)))
    assert client.get(f"/api/v1/admin/lessons/{lesson_id}/examples").status_code==403
    assert client.patch(f"/api/v1/admin/lessons/{lesson_id}",json={"title":"Nope","slug":"nope","description":"","content_en":"","content_mm":None,"position":1,"duration_minutes":10,"status":"draft"},headers={"X-CSRF-Token":csrf}).status_code==403
