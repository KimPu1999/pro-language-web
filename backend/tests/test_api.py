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
        assert all(not any(character in lesson.slug for character in "?&#/") for lesson in db.query(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).all())
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

def test_cpp_curriculum_is_separate_complete_and_idempotent(client):
    from app.cpp_course_content import seed_cpp_course
    from app.models import CodeExample, Course, CourseCategory, CourseModule, Lesson, LessonQuiz, ProgrammingLanguage, QuizQuestion
    import json

    with client.session_factory() as db:
        language = ProgrammingLanguage(name="C++", slug="cpp", color="#00599C")
        category = db.query(CourseCategory).filter_by(slug="fundamentals").one()
        db.add(language); db.flush()
        course = Course(language_id=language.id, category_id=category.id, title="C++", slug="cpp-programming", description="C++20", level="beginner", duration_minutes=0, published=True, status="draft")
        db.add(course); db.flush(); seed_cpp_course(db, course); db.commit()
        seed_cpp_course(db, course); db.commit()
        modules = db.query(CourseModule).filter_by(course_id=course.id).order_by(CourseModule.order_index).all()
        lessons = db.query(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).all()
        assert len(modules) == 24
        assert len(lessons) == 63
        assert all(lesson.content_en and "Complete C++20 example" in lesson.content_en for lesson in lessons)
        assert all(lesson.content_mm for lesson in lessons)
        assert db.query(LessonQuiz).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).count() == 63
        for question in db.query(QuizQuestion).join(LessonQuiz).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).all():
            assert question.correct_answer in json.loads(question.options_json)
        assert db.query(CodeExample).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id, CodeExample.language == "cpp").count() == 63
        response = client.get("/api/v1/courses/cpp-programming")
        assert response.status_code == 200
        assert response.json()["title"] == "C++ Programming — From Zero to Modern C++"
        assert len(response.json()["modules"]) == 24

def test_html_curriculum_is_published_and_idempotent(client):
    from app.html_course_content import MODULES, MODULE_ONE, seed_html_course
    from app.models import CodeExample, Course, CourseCategory, CourseModule, Lesson, LessonQuiz, ProgrammingLanguage, QuizQuestion
    import json

    with client.session_factory() as db:
        language = ProgrammingLanguage(name="HTML", slug="html", color="#E34F26")
        category = db.query(CourseCategory).filter_by(slug="fundamentals").one()
        db.add(language); db.flush()
        course = Course(language_id=language.id, category_id=category.id, title="HTML", slug="html", description="HTML", level="beginner", duration_minutes=0, published=True, status="draft")
        db.add(course); db.flush(); seed_html_course(db, course); db.commit()
        seed_html_course(db, course); db.commit()
        modules = db.query(CourseModule).filter_by(course_id=course.id).order_by(CourseModule.order_index).all()
        lessons = db.query(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).order_by(CourseModule.order_index, Lesson.order_index).all()
        assert [module.title for module in modules] == MODULES
        assert len(modules) == 20
        assert len([lesson for lesson in lessons if lesson.module.order_index == 1]) == len(MODULE_ONE)
        assert len(lessons) == 53
        assert all(lesson.published and "Browser preview" in lesson.content_en and "Accessibility guidance" in lesson.content_en for lesson in lessons)
        assert all(lesson.content_mm for lesson in lessons)
        assert db.query(LessonQuiz).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).count() == len(lessons)
        assert db.query(CodeExample).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id, CodeExample.language == "html").count() == len(lessons)
        for question in db.query(QuizQuestion).join(LessonQuiz).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).all():
            assert question.correct_answer in json.loads(question.options_json)
        assert course.title == "HTML — From Zero to Web Development Foundations"

    response = client.get("/api/v1/courses/html")
    assert response.status_code == 200
    assert response.json()["title"] == "HTML — From Zero to Web Development Foundations"
    assert len(response.json()["modules"]) == 20

def test_css_curriculum_is_published_and_idempotent(client):
    from app.css_course_content import MODULES, MODULE_ONE, seed_css_course
    from app.models import CodeExample, Course, CourseCategory, CourseModule, Lesson, LessonQuiz, ProgrammingLanguage, QuizQuestion
    import json

    with client.session_factory() as db:
        language = ProgrammingLanguage(name="CSS", slug="css", color="#264DE4")
        category = db.query(CourseCategory).filter_by(slug="fundamentals").one()
        db.add(language); db.flush()
        course = Course(language_id=language.id, category_id=category.id, title="CSS", slug="css", description="CSS", level="beginner", duration_minutes=0, published=True, status="draft")
        db.add(course); db.flush(); seed_css_course(db, course); db.commit()
        seed_css_course(db, course); db.commit()
        modules = db.query(CourseModule).filter_by(course_id=course.id).order_by(CourseModule.order_index).all()
        lessons = db.query(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).order_by(CourseModule.order_index, Lesson.order_index).all()
        assert [module.title for module in modules] == MODULES
        assert len(modules) == 24
        assert len([lesson for lesson in lessons if lesson.module.order_index == 1]) == len(MODULE_ONE)
        assert len(lessons) == 44
        assert all(lesson.published and "Browser preview" in lesson.content_en and "Visual explanation" in lesson.content_en for lesson in lessons)
        assert all(lesson.content_mm for lesson in lessons)
        assert db.query(LessonQuiz).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).count() == len(lessons)
        assert db.query(CodeExample).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id, CodeExample.language == "html").count() == len(lessons)
        assert db.query(CodeExample).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id, CodeExample.language == "css").count() == len(lessons)
        for question in db.query(QuizQuestion).join(LessonQuiz).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).all():
            assert question.correct_answer in json.loads(question.options_json)
        assert course.title == "CSS — From Zero to Professional Web Design"

    response = client.get("/api/v1/courses/css")
    assert response.status_code == 200
    assert response.json()["title"] == "CSS — From Zero to Professional Web Design"
    assert len(response.json()["modules"]) == 24

def test_javascript_curriculum_is_published_and_idempotent(client):
    from app.javascript_course_content import MODULES, MODULE_ONE, seed_javascript_course
    from app.models import CodeExample, Course, CourseCategory, CourseModule, Lesson, LessonQuiz, ProgrammingLanguage, QuizQuestion
    import json

    with client.session_factory() as db:
        language = ProgrammingLanguage(name="JavaScript", slug="javascript", color="#F7DF1E")
        category = db.query(CourseCategory).filter_by(slug="fundamentals").one()
        db.add(language); db.flush()
        course = Course(language_id=language.id, category_id=category.id, title="JavaScript", slug="javascript", description="JavaScript", level="beginner", duration_minutes=0, published=True, status="draft")
        db.add(course); db.flush(); seed_javascript_course(db, course); db.commit()
        seed_javascript_course(db, course); db.commit()
        modules = db.query(CourseModule).filter_by(course_id=course.id).order_by(CourseModule.order_index).all()
        lessons = db.query(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).order_by(CourseModule.order_index, Lesson.order_index).all()
        assert [module.title for module in modules] == MODULES
        assert len(modules) == 30
        assert len([lesson for lesson in lessons if lesson.module.order_index == 1]) == len(MODULE_ONE)
        assert len(lessons) == 78
        assert all(lesson.published and "Expected output" in lesson.content_en and "Best practices" in lesson.content_en for lesson in lessons)
        assert all(lesson.content_mm for lesson in lessons)
        assert db.query(LessonQuiz).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).count() == len(lessons)
        assert db.query(CodeExample).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id, CodeExample.language == "javascript").count() == len(lessons)
        for question in db.query(QuizQuestion).join(LessonQuiz).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).all():
            assert question.correct_answer in json.loads(question.options_json)
        assert course.title == "JavaScript Programming — From Zero to Advanced"

    response = client.get("/api/v1/courses/javascript")
    assert response.status_code == 200
    assert response.json()["title"] == "JavaScript Programming — From Zero to Advanced"
    assert len(response.json()["modules"]) == 30

def test_python_curriculum_is_published_and_idempotent(client):
    from app.python_course_content import MODULES, MODULE_ONE, seed_python_course
    from app.models import CodeExample, Course, CourseCategory, CourseModule, Lesson, LessonQuiz, ProgrammingLanguage, QuizQuestion
    import json

    with client.session_factory() as db:
        language = db.query(ProgrammingLanguage).filter_by(slug="python").one()
        category = db.query(CourseCategory).filter_by(slug="fundamentals").one()
        db.flush()
        course = Course(language_id=language.id, category_id=category.id, title="Python", slug="python", description="Python", level="beginner", duration_minutes=0, published=True, status="draft")
        db.add(course); db.flush(); seed_python_course(db, course); db.commit()
        seed_python_course(db, course); db.commit()
        modules = db.query(CourseModule).filter_by(course_id=course.id).order_by(CourseModule.order_index).all()
        lessons = db.query(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).order_by(CourseModule.order_index, Lesson.order_index).all()
        assert [module.title for module in modules] == MODULES
        assert len(modules) == 32
        assert len([lesson for lesson in lessons if lesson.module.order_index == 1]) == len(MODULE_ONE)
        assert len(lessons) == 87
        assert all(lesson.published and "Expected output" in lesson.content_en and "Best practices" in lesson.content_en for lesson in lessons)
        assert all(lesson.content_mm for lesson in lessons)
        assert db.query(LessonQuiz).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).count() == len(lessons)
        assert db.query(CodeExample).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id, CodeExample.language == "python").count() == len(lessons)
        for question in db.query(QuizQuestion).join(LessonQuiz).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).all():
            assert question.correct_answer in json.loads(question.options_json)
        assert course.title == "Python Programming — From Zero to Advanced"

    response = client.get("/api/v1/courses/python")
    assert response.status_code == 200
    assert response.json()["title"] == "Python Programming — From Zero to Advanced"
    assert len(response.json()["modules"]) == 32

def test_course_detail_and_lesson(client):
    course=client.get("/api/v1/courses/python-foundations"); assert course.status_code==200; assert course.json()["modules"][0]["lessons"][0]["content_en"]=="Hello lesson"
    learning=client.get("/api/v1/courses/python-foundations/learning"); assert learning.status_code==200
    assert learning.json()["modules"][0]["lessons"][0]["title"] == "Hello"
    assert "content_en" not in learning.json()["modules"][0]["lessons"][0]
    lesson=client.get("/api/v1/courses/python-foundations/lessons/hello"); assert lesson.status_code==200
    assert lesson.json()["content_en"] == "Hello lesson"
    assert client.get("/api/v1/courses/python-foundations/lessons/hello%3F").status_code==200
    assert client.get("/api/v1/courses/python-foundations/lessons/missing").status_code==404
def test_missing_and_unpublished(client):
    assert client.get("/api/v1/courses/missing").status_code==404
