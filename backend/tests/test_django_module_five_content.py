import ast
import json

from app.django_module_five_content import LESSONS, SYNTAX_REFERENCES, _module_assessment, _render_en, _render_mm, _project_source_files


def test_module_five_has_eight_bilingual_substantive_lessons():
    assert len(LESSONS) == 8
    for item in LESSONS:
        english = _render_en(item)
        burmese = _render_mm(item)
        assert len(english) > 5000
        assert len(burmese) > 5000
        assert "Detailed theory" in english
        assert "အိမ်စာ" in burmese
        assert 4 <= len(item["examples"]) <= 5
        assert len(item["quiz"]) == 8
        for example in item["examples"]:
            for filename, source in example["files"].items():
                if filename.endswith(".py"):
                    ast.parse(source)


def test_module_assessment_has_private_answered_questions():
    questions = _module_assessment()
    assert len(questions) == 24
    assert all(question["correct_answer"] for question in questions)
    assert all(question["explanation"] for question in questions)
    assert all(question["lesson_position"] in range(1, 9) for question in questions)


def test_syntax_references_cover_models_orm_postgresql_surface():
    slugs = {item["slug"] for item in SYNTAX_REFERENCES}
    assert {
        "django-models-model",
        "django-models-fields",
        "django-models-constraints",
        "django-databases-setting",
        "django-postgres-backend",
        "django-makemigrations",
        "django-migrate",
        "django-showmigrations",
        "django-sqlmigrate",
        "django-objects-create",
        "django-objects-get-filter",
        "django-objects-update",
        "django-get-or-create",
        "django-select-related",
        "django-prefetch-related",
        "django-q-f-expressions",
        "django-annotate-aggregate",
        "django-queryset-explain",
        "django-transaction-atomic",
        "django-transaction-on-commit",
        "django-select-for-update",
    } <= slugs


def test_project_source_files_are_parseable_and_have_required_boundaries():
    files = _project_source_files()
    assert {"students/models.py", "students/services.py", "courses/services.py", "students/tests/test_models.py"} <= files.keys()
    for filename, source in files.items():
        if filename.endswith(".py"):
            ast.parse(source)
    assert "school_portal_dev" not in files["school_site/settings.py"]
    assert "transaction.atomic" in files["students/services.py"]
    assert "UniqueConstraint" in files["students/models.py"]
