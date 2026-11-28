import re

def test_spring_boot_batch_is_idempotent_and_preserves_module_one(client):
    from app.models import CodingExercise, Course, CourseCategory, CourseModule, Lesson, LessonQuiz, ProgrammingLanguage
    from app.spring_boot_complete_curriculum import LESSONS, MODULES
    from app.spring_boot_course_content import seed_spring_boot_course
    with client.session_factory() as db:
        language = ProgrammingLanguage(name="Spring Boot", slug="spring-boot")
        category = CourseCategory(name="Java Backend", slug="java-backend")
        db.add_all([language, category]); db.flush()
        course = Course(language_id=language.id, category_id=category.id, title="Spring Boot", slug="spring-boot", description="Spring course", level="beginner", duration_minutes=60, published=True)
        db.add(course); db.flush(); seed_spring_boot_course(db, course); db.commit()
        modules = db.query(CourseModule).filter_by(course_id=course.id).order_by(CourseModule.order_index).all()
        module_one_lessons = db.query(Lesson).filter_by(module_id=modules[0].id).order_by(Lesson.order_index).all()
        module_one_ids = [lesson.id for lesson in module_one_lessons]
        lessons = db.query(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).order_by(CourseModule.order_index, Lesson.order_index).all()
        assert [module.order_index for module in modules] == [1, *MODULES.keys()]
        assert len(lessons) == 8 + sum(len(items) for items in LESSONS.values())
        assert all(lesson.published and lesson.status == "published" for lesson in module_one_lessons)
        new_lessons = lessons[8:]
        assert all(not lesson.published and lesson.status == "draft" for lesson in new_lessons)
        assert all("## Detailed theory" in lesson.content_en and "## Practical exercises" in lesson.content_en and "## Quiz" in lesson.content_en for lesson in new_lessons)
        assert all(len(re.findall(r"[\u1000-\u109f]", lesson.content_mm or "")) >= 50 for lesson in new_lessons)
        assert "## Detailed theory" in module_one_lessons[0].content_en
        assert db.query(LessonQuiz).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).count() == len(lessons)
        assert db.query(CodingExercise).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).count() == len(lessons)
        seed_spring_boot_course(db, course); db.commit()
        assert db.query(CourseModule).filter_by(course_id=course.id).count() == 9
        lessons_again = db.query(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).order_by(CourseModule.order_index, Lesson.order_index).all()
        assert len(lessons_again) == len(lessons)
        assert [lesson.id for lesson in lessons_again[:8]] == module_one_ids
