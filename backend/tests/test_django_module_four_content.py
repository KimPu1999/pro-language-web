import ast

from app.django_module_four_content import LESSONS, SYNTAX_REFERENCES, _module_assessment, _render_en, _render_mm


def test_module_four_has_seven_bilingual_substantive_lessons():
    assert len(LESSONS) == 7
    for item in LESSONS:
        english = _render_en(item)
        burmese = _render_mm(item)
        assert len(english) > 5000
        assert len(burmese) > 5000
        assert "Detailed theory" in english
        assert "အိမ်စာ" in burmese
        assert 3 <= len(item["examples"]) <= 5
        assert len(item["quiz"]) == 8
        for example in item["examples"]:
            for filename, source in example["files"].items():
                if filename.endswith(".py"):
                    ast.parse(source)


def test_module_assessment_has_eighteen_private_answered_questions():
    questions = _module_assessment()
    assert len(questions) == 18
    assert all(question["correct_answer"] for question in questions)
    assert all(question["explanation"] for question in questions)
    assert all(question["lesson_position"] in range(1, 8) for question in questions)


def test_syntax_references_cover_template_and_static_api_surface():
    slugs = {item["slug"] for item in SYNTAX_REFERENCES}
    assert {
        "django-render",
        "django-template-variable",
        "django-if-elif-else",
        "django-for-empty-endfor",
        "django-url-tag",
        "django-extends",
        "django-block-endblock",
        "django-block-super",
        "django-include",
        "django-load-static",
        "django-static-tag",
        "django-default-filter",
        "django-length-filter",
        "django-case-filters",
        "django-date-filter",
        "django-truncatechars-filter",
    } <= slugs
