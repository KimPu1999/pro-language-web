import re


def test_python_ai_batch_is_idempotent_and_preserves_module_one(client):
    from app.models import CodingExercise, Course, CourseCategory, CourseModule, Lesson, LessonQuiz, ProgrammingLanguage
    from app.python_ai_complete_curriculum import LESSONS, MODULES
    from app.python_ai_course_content import seed_python_ai_course

    with client.session_factory() as db:
        language = ProgrammingLanguage(name="Python for AI", slug="python-for-ai")
        category = CourseCategory(name="Artificial Intelligence", slug="artificial-intelligence-python")
        db.add_all([language, category])
        db.flush()
        course = Course(language_id=language.id, category_id=category.id, title="Python for Artificial Intelligence", slug="python-for-ai", description="Python AI course", level="beginner", duration_minutes=60, published=True)
        db.add(course)
        db.flush()
        seed_python_ai_course(db, course)
        db.commit()

        modules = db.query(CourseModule).filter_by(course_id=course.id).order_by(CourseModule.order_index).all()
        module_one_lessons = db.query(Lesson).filter_by(module_id=modules[0].id).order_by(Lesson.order_index).all()
        module_one_ids = [lesson.id for lesson in module_one_lessons]
        lessons = db.query(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).order_by(CourseModule.order_index, Lesson.order_index).all()
        expected_new = sum(len(items) for items in LESSONS.values())

        assert [module.order_index for module in modules] == [1, *MODULES.keys()]
        assert len(module_one_lessons) == 8
        assert len(lessons) == 8 + expected_new
        assert all(lesson.published and lesson.status == "published" for lesson in module_one_lessons)
        new_lessons = lessons[8:]
        assert all(not lesson.published and lesson.status == "draft" for lesson in new_lessons)
        assert all("## Detailed theory" in lesson.content_en for lesson in new_lessons)
        assert all("## Practical exercises" in lesson.content_en for lesson in new_lessons)
        assert all("## Quiz" in lesson.content_en for lesson in new_lessons)
        assert all(len(re.findall(r"[\u1000-\u109f]", lesson.content_mm or "")) >= 50 for lesson in new_lessons)
        assert "## Detailed theory" in module_one_lessons[0].content_en
        assert "## အသေးစိတ်သီအိုရီ" in (module_one_lessons[0].content_mm or "")
        assert db.query(LessonQuiz).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).count() == len(lessons)
        assert db.query(CodingExercise).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).count() == len(lessons)

        seed_python_ai_course(db, course)
        db.commit()
        modules_again = db.query(CourseModule).filter_by(course_id=course.id).order_by(CourseModule.order_index).all()
        lessons_again = db.query(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).order_by(CourseModule.order_index, Lesson.order_index).all()
        assert len(modules_again) == 12
        assert len(lessons_again) == len(lessons)
        assert [lesson.id for lesson in lessons_again[:8]] == module_one_ids
