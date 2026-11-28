import ast

from app.django_module_six_content import LESSONS, SYNTAX_REFERENCES, _module_assessment, _project_source_files, _render_en, _render_mm


def test_module_six_has_seven_bilingual_substantive_lessons():
    assert len(LESSONS) == 7
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
    assert all(question["lesson_position"] in range(1, 8) for question in questions)


def test_syntax_references_cover_forms_validation_formsets_and_uploads():
    slugs = {item["slug"] for item in SYNTAX_REFERENCES}
    assert {
        "django-forms-form",
        "django-forms-modelform",
        "django-form-charfield",
        "django-form-emailfield",
        "django-form-integerfield",
        "django-form-choicefield",
        "django-form-modelchoicefield",
        "django-form-filefield",
        "django-form-imagefield",
        "django-form-widgets",
        "django-form-is-valid",
        "django-form-cleaned-data",
        "django-form-errors",
        "django-form-clean",
        "django-form-clean-field",
        "django-form-validation-error",
        "django-form-add-error",
        "django-form-non-field-errors",
        "django-form-save",
        "django-form-save-commit-false",
        "django-formset-factory",
        "django-modelformset-factory",
        "django-inlineformset-factory",
        "django-request-post-files",
        "django-csrf-token",
        "django-media-root-url",
        "django-upload-to",
        "django-uploaded-file-chunks",
    } <= slugs


def test_project_source_files_are_parseable_and_secure_boundaries_are_present():
    files = _project_source_files()
    assert {"students/forms.py", "students/validators.py", "students/services.py", "students/tests/test_uploads.py"} <= files.keys()
    for filename, source in files.items():
        if filename.endswith(".py"):
            ast.parse(source)
    assert "CsrfViewMiddleware" in files["school_site/settings.py"]
    assert "request.FILES" in files["students/views.py"]
    assert 'enctype="multipart/form-data"' in files["templates/students/edit.html"]
    assert "transaction.atomic" in files["students/services.py"]
    assert "validate_profile_image" in files["students/forms.py"]
