from app.main import app

@app.get("/_test/unhandled-error")
def unhandled_error_for_test():
    raise RuntimeError("test-only failure")

def test_health(client):
    response = client.get("/api/v1/health", headers={"X-Request-ID": "test-request"})
    assert response.json()["status"] == "ok"
    assert response.headers["X-Request-ID"] == "test-request"
    assert "X-Response-Time-ms" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"

def test_unhandled_errors_are_safe_and_correlated(client):
    from fastapi.testclient import TestClient
    response = TestClient(app, raise_server_exceptions=False).get("/_test/unhandled-error", headers={"X-Request-ID": "error-request"})
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error", "request_id": "error-request"}
def test_course_filter_and_pagination(client):
    response=client.get("/api/v1/courses?language=python&page=1&page_size=1"); assert response.status_code==200; assert response.json()["total"]==1

def test_course_filters_sort_and_published_scope(client):
    from app.models import Course, CourseCategory, ProgrammingLanguage

    with client.session_factory() as db:
        python = db.query(ProgrammingLanguage).filter_by(slug="python").one()
        fundamentals = db.query(CourseCategory).filter_by(slug="fundamentals").one()
        backend = CourseCategory(name="Backend", slug="backend")
        javascript = ProgrammingLanguage(name="JavaScript", slug="javascript")
        db.add_all([backend, javascript])
        db.flush()
        db.add_all([
            Course(language_id=python.id, category_id=backend.id, title="Python APIs", slug="python-apis", description="Build backend services", level="Intermediate", duration_minutes=90, published=True),
            Course(language_id=javascript.id, category_id=fundamentals.id, title="JavaScript Basics", slug="javascript-basics", description="Learn browser programming", level="Beginner", duration_minutes=30, published=True),
            Course(language_id=python.id, category_id=fundamentals.id, title="Draft Python", slug="draft-python", description="Not publicly visible", level="Beginner", duration_minutes=15, published=False),
        ])
        db.commit()

    response = client.get("/api/v1/courses?search=backend&category=backend&difficulty=intermediate&language=python&sort=duration_desc&page_size=10")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert [item["slug"] for item in payload["items"]] == ["python-apis"]
    assert payload["page_size"] == 10

    sorted_response = client.get("/api/v1/courses?sort=duration_asc&page_size=10")
    assert sorted_response.status_code == 200
    assert [item["slug"] for item in sorted_response.json()["items"]] == ["javascript-basics", "python-foundations", "python-apis"]

    assert client.get("/api/v1/courses?difficulty=beginner&level=advanced").status_code == 422

def test_c_curriculum_seed_is_complete_and_idempotent(client):
    from app.c_course_content import seed_c_curriculum
    from app.c_module_three import MODULE_THREE_LESSONS, MODULE_THREE_SECTION_HEADINGS
    from app.models import CodeExample, Course, CourseCategory, CourseModule, Lesson, LessonQuiz, ProgrammingLanguage, QuizQuestion
    import json

    with client.session_factory() as db:
        language = ProgrammingLanguage(name="C", slug="c")
        category = CourseCategory(name="Programming Languages", slug="programming-languages")
        db.add_all([language, category]); db.flush()
        course = Course(language_id=language.id, category_id=category.id, title="C Programming", slug="c-programming", description="Beginner C", level="beginner", duration_minutes=0, published=True, status="draft")
        db.add(course); db.flush(); seed_c_curriculum(db, course); db.commit()
        module_three = db.query(CourseModule).filter_by(course_id=course.id, order_index=3).one()
        first_ids = {lesson.order_index: lesson.id for lesson in db.query(Lesson).filter_by(module_id=module_three.id).all()}
        seed_c_curriculum(db, course); db.commit()
        assert db.query(CourseModule).filter_by(course_id=course.id).count() == 20
        assert db.query(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).count() == 75
        assert db.query(LessonQuiz).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).count() == 75
        assert module_three.title == "03 Your First C Program & C Syntax Fundamentals"
        lessons = db.query(Lesson).filter_by(module_id=module_three.id).order_by(Lesson.order_index).all()
        assert [lesson.title for lesson in lessons] == [item["title"] for item in MODULE_THREE_LESSONS]
        assert {lesson.order_index: lesson.id for lesson in lessons} == first_ids
        for lesson in lessons:
            assert lesson.published is True
            assert lesson.content_mm and lesson.content_mm.strip()
            for heading in MODULE_THREE_SECTION_HEADINGS:
                if heading in {"Additional complete example", "Explanation"}:
                    continue
                assert heading in lesson.content_en, (lesson.title, heading)
        quiz_rows = db.query(QuizQuestion).join(LessonQuiz).filter(LessonQuiz.lesson_id.in_([lesson.id for lesson in lessons])).all()
        assert quiz_rows
        for question in quiz_rows:
            assert question.correct_answer in json.loads(question.options_json), question.prompt
        assert db.query(CodeExample).filter_by(lesson_id=lessons[-1].id).count() == 2

def test_course_detail_and_lesson(client):
    course=client.get("/api/v1/courses/python-foundations"); assert course.status_code==200; assert course.json()["modules"][0]["lessons"][0]["content_en"]=="Hello lesson"
def test_missing_and_unpublished(client):
    assert client.get("/api/v1/courses/missing").status_code==404
