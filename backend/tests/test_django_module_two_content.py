import ast

from app.django_module_two_content import LESSONS, _module_assessment, _render_en, _render_mm


def test_module_two_has_six_bilingual_substantive_lessons():
    assert len(LESSONS) == 6
    for item in LESSONS:
        english = _render_en(item)
        burmese = _render_mm(item)
        assert len(english) > 5000
        assert len(burmese) > 5000
        assert "Detailed theory" in english
        assert "အိမ်စာ" in burmese
        assert len(item["examples"]) == 5
        assert len(item["quiz"]) == 8
        for example in item["examples"]:
            ast.parse(example["code"])


def test_module_assessment_has_private_answer_keys_and_eighteen_questions():
    questions = _module_assessment()
    assert len(questions) == 18
    assert all(question["correct_answer"] for question in questions)
    assert all(question["explanation"] for question in questions)
