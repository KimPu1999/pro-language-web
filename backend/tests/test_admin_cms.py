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

def test_homepage_draft_publish_is_database_backed_and_public(client):
    from app.models import Course, CourseModule, Lesson
    csrf=admin_login(client)
    with client.session_factory() as db:
        course=db.scalar(select(Course).where(Course.slug=="python-foundations")); module=db.scalar(select(CourseModule).where(CourseModule.course_id==course.id)); lesson=db.scalar(select(Lesson).where(Lesson.module_id==module.id)); course_id,lesson_id=str(course.id),str(lesson.id)
    initial=client.get("/api/v1/admin/settings/homepage"); assert initial.status_code==200; assert "settings" in initial.json(); assert initial.json()["settings"]["status"] in {"draft","published"}; assert initial.json()["lessons"][0]["course_slug"]==course.slug
    draft={"status":"draft","hero_title":"Managed homepage","hero_description":"Persisted homepage content","hero_cta_label":"Start learning","hero_cta_href":"/courses","announcement":"New content","featured_course_ids":[course_id],"featured_lesson_ids":[lesson_id],"sections":[{"key":"featured-courses","label":"Featured courses","visible":True,"display_order":0},{"key":"featured-lessons","label":"Featured lessons","visible":True,"display_order":1}]}
    saved=client.patch("/api/v1/admin/settings/homepage",json=draft,headers={"X-CSRF-Token":csrf}); assert saved.status_code==200; assert saved.json()["status"]=="draft"
    assert client.get("/api/v1/site/homepage").json()["hero_title"] != "Managed homepage"
    published=client.post("/api/v1/admin/settings/homepage/publish",headers={"X-CSRF-Token":csrf}); assert published.status_code==200; assert published.json()["status"]=="published"
    public=client.get("/api/v1/site/homepage"); assert public.status_code==200; assert public.json()["hero_title"]=="Managed homepage"; assert public.json()["featured_courses"][0]["id"]==course_id; assert public.json()["featured_lessons"][0]["id"]==lesson_id; assert public.json()["featured_lessons"][0]["course_slug"]==course.slug
    preview=client.get("/api/v1/admin/settings/homepage/preview"); assert preview.status_code==200; assert preview.json()["preview"] is True; assert preview.json()["hero_title"]=="Managed homepage"
    revisions=client.get("/api/v1/admin/settings/homepage/revisions"); assert revisions.status_code==200; assert revisions.json()
    restored=client.post(f"/api/v1/admin/settings/homepage/revisions/{revisions.json()[0]['id']}/restore",headers={"X-CSRF-Token":csrf}); assert restored.status_code==200; assert restored.json()["status"]=="draft"; assert client.get("/api/v1/site/homepage").json()["hero_title"]=="Managed homepage"

def test_admin_lesson_read_route_is_get_and_returns_editor_metadata(client):
    from app.models import Course, CourseModule, Lesson
    assert client.get("/api/v1/admin/lessons/00000000-0000-0000-0000-000000000000").status_code==401
    csrf=admin_login(client)
    with client.session_factory() as db:
        course=db.scalar(select(Course).where(Course.slug=="python-foundations")); module=db.scalar(select(CourseModule).where(CourseModule.course_id==course.id)); lesson=db.scalar(select(Lesson).where(Lesson.module_id==module.id)); lesson_id=str(lesson.id)
    response=client.get(f"/api/v1/admin/lessons/{lesson_id}")
    assert response.status_code==200
    body=response.json(); assert body["id"]==lesson_id; assert body["module_id"]==str(module.id); assert body["course_id"]==str(course.id); assert body["course_slug"]==course.slug; assert body["language_name"]=="Python"; assert body["content_en"]=="Hello lesson"; assert "published" in body
    assert client.get("/api/v1/admin/lessons/00000000-0000-0000-0000-000000000000").status_code==404
    assert csrf

def test_course_publish_route_accepts_post_only_and_handles_cors_preflight(client):
    path="/api/v1/admin/courses/00000000-0000-0000-0000-000000000000/publish"
    for method in ("get", "patch", "put"):
        response=getattr(client,method)(path)
        assert response.status_code==405
        assert response.headers["allow"]=="POST"
        assert response.json()=={"detail":"Method Not Allowed"}
    preflight=client.options(path,headers={"Origin":"http://localhost:3001","Access-Control-Request-Method":"POST","Access-Control-Request-Headers":"content-type,x-csrf-token"})
    assert preflight.status_code==200
    assert "POST" in preflight.headers["access-control-allow-methods"]

def test_admin_course_create_and_publish_validation(client):
    csrf=admin_login(client); lang=client.get("/api/v1/languages").json()[0]; category=client.get("/api/v1/categories").json()[0]
    payload={"title":"Admin Course","slug":"admin-course","short_description":"Short","description":"Long","language_id":lang["id"],"category_id":category["id"],"level":"beginner","estimated_duration":90,"outcomes":[],"requirements":[]}
    response=client.post("/api/v1/admin/courses",json=payload,headers={"X-CSRF-Token":csrf}); assert response.status_code==201; course_id=response.json()["id"]
    assert client.post(f"/api/v1/admin/courses/{course_id}/publish",json={"decision":"publish"},headers={"X-CSRF-Token":csrf}).status_code==422

def test_admin_course_builder_publish_workflow_and_public_visibility(client):
    csrf=admin_login(client); lang=client.get("/api/v1/languages").json()[0]; category=client.get("/api/v1/categories").json()[0]
    payload={"title":"Publish Workflow Course","slug":"publish-workflow-course","short_description":"Short","description":"Long","language_id":lang["id"],"category_id":category["id"],"level":"beginner","estimated_duration":90,"outcomes":[],"requirements":[]}
    course=client.post("/api/v1/admin/courses",json=payload,headers={"X-CSRF-Token":csrf}); assert course.status_code==201; course_id=course.json()["id"]
    module=client.post(f"/api/v1/admin/courses/{course_id}/modules",json={"title":"Module 1","position":0},headers={"X-CSRF-Token":csrf}); assert module.status_code==201; module_id=module.json()["id"]
    lesson=client.post(f"/api/v1/admin/modules/{module_id}/lessons",json={"title":"English Lesson","slug":"english-lesson","description":"Lesson","content_en":"Published content","content_mm":None,"position":0,"duration_minutes":10,"status":"draft"},headers={"X-CSRF-Token":csrf}); assert lesson.status_code==201; lesson_id=lesson.json()["id"]
    ready=client.patch(f"/api/v1/admin/lessons/{lesson_id}",json={"title":"English Lesson","slug":"english-lesson","description":"Lesson","content_en":"Published content","content_mm":None,"position":0,"duration_minutes":10,"status":"published","expected_version":lesson.json()["content_version"]},headers={"X-CSRF-Token":csrf}); assert ready.status_code==200; assert ready.json()["published"] is True
    published=client.post(f"/api/v1/admin/courses/{course_id}/publish",json={"decision":"publish","note":"Ready"},headers={"X-CSRF-Token":csrf}); assert published.status_code==200; assert published.json()["published"] is True
    public=client.get("/api/v1/courses/publish-workflow-course"); assert public.status_code==200; assert public.json()["slug"]=="publish-workflow-course"
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
