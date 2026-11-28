import ast
import json

from app.django_module_three_content import LESSONS, SYNTAX_REFERENCES, _module_assessment, _render_en, _render_mm


def test_module_three_has_seven_bilingual_substantive_lessons():
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
            ast.parse(example["code"])


def test_module_assessment_has_private_answer_keys_and_eighteen_questions():
    questions = _module_assessment()
    assert len(questions) == 18
    assert all(question["correct_answer"] for question in questions)
    assert all(question["explanation"] for question in questions)


def test_syntax_reference_catalog_covers_requested_module_three_apis():
    slugs = {item["slug"] for item in SYNTAX_REFERENCES}
    assert {
        "django-admin-startproject",
        "django-manage-py-commands",
        "django-path",
        "django-include",
        "django-urlpatterns",
        "django-url-app-name",
        "django-reverse",
        "django-reverse-lazy",
        "django-httprequest",
        "django-httpresponse",
        "django-jsonresponse",
        "django-http404",
        "django-request-get-post-method",
        "django-settings-debug",
        "django-settings-allowed-hosts",
        "django-settings-installed-apps",
    } <= slugs

