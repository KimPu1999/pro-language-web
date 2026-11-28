import re


def test_django_batch_adds_reviewable_modules_idempotently_and_preserves_module_one(client):
    from app.django_course_content import seed_django_course
    from app.models import CodingExercise, Course, CourseCategory, CourseModule, Lesson, LessonQuiz, ProgrammingLanguage

    with client.session_factory() as db:
        language = ProgrammingLanguage(name="Django", slug="django")
        category = CourseCategory(name="Django Backend", slug="django-backend")
        db.add_all([language, category])
        db.flush()
        course = Course(
            language_id=language.id,
            category_id=category.id,
            title="Django Web Development",
            slug="django",
            description="Django course",
            level="beginner",
            duration_minutes=60,
            published=True,
        )
        db.add(course)
        db.flush()
        seed_django_course(db, course)
        db.commit()

        modules = db.query(CourseModule).filter_by(course_id=course.id).order_by(CourseModule.order_index).all()
        module_one_lessons = db.query(Lesson).filter_by(module_id=modules[0].id).order_by(Lesson.order_index).all()
        module_one_ids = [lesson.id for lesson in module_one_lessons]
        lessons = db.query(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).order_by(CourseModule.order_index, Lesson.order_index).all()
        assert [module.order_index for module in modules] == list(range(1, 11))
        assert [module.title for module in modules[1:]] == [
            "Django Fundamentals",
            "Templates and Frontend",
            "Database and Models",
            "Forms and Validation",
            "Authentication",
            "Advanced Django",
            "Django REST APIs",
            "Security and Testing",
            "Production Engineering",
        ]
        assert len(module_one_lessons) == 8
        assert len(lessons) == 56
        assert all(lesson.published and lesson.status == "published" for lesson in module_one_lessons)

        new_lessons = lessons[len(module_one_lessons):]
        assert len(new_lessons) == 48
        assert all(not lesson.published and lesson.status == "draft" for lesson in new_lessons)
        assert all("## Learning objectives" in lesson.content_en for lesson in new_lessons)
        assert all("## Detailed theory" in lesson.content_en for lesson in new_lessons)
        assert all("## Practical exercises" in lesson.content_en for lesson in new_lessons)
        assert all("## Knowledge quiz" in lesson.content_en for lesson in new_lessons)
        assert all(len(re.findall(r"[\u1000-\u109f]", lesson.content_mm or "")) >= 50 for lesson in new_lessons)
        assert "## Detailed theory" in module_one_lessons[0].content_en
        assert "## အသေးစိတ်သီအိုရီ" in (module_one_lessons[0].content_mm or "")
        assert db.query(LessonQuiz).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).count() == 56
        assert db.query(CodingExercise).join(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).count() == 56

        seed_django_course(db, course)
        db.commit()
        modules_again = db.query(CourseModule).filter_by(course_id=course.id).order_by(CourseModule.order_index).all()
        lessons_again = db.query(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).order_by(CourseModule.order_index, Lesson.order_index).all()
        assert len(modules_again) == 10
        assert len(lessons_again) == 56
        assert [lesson.id for lesson in lessons_again[:8]] == module_one_ids
