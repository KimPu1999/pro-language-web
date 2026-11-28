"""Seed reviewed-only achievement drafts; no awards or public definitions are created."""

import json
import uuid

from alembic import op
import sqlalchemy as sa


revision = "0071_initial_achievement_drafts"
down_revision = "0070_verified_achievements"
branch_labels = None
depends_on = None


def upgrade():
    definitions = [
        ("first-step", "First Step", "ပထမခြေလှမ်း", "Complete your first verified lesson.", "အတည်ပြုထားသော သင်ခန်းစာတစ်ခုကို ပြီးမြောက်ပါ။", "Complete 1 published lesson.", "ထုတ်ဝေထားသော သင်ခန်းစာ ၁ ခု ပြီးမြောက်ပါ။", "learning", "lesson_completion_count", {"count": 1}),
        ("knowledge-builder", "Knowledge Builder", "အသိပညာ တည်ဆောက်သူ", "Complete ten distinct verified lessons.", "အတည်ပြုထားသော သီးခြားသင်ခန်းစာ ၁၀ ခုကို ပြီးမြောက်ပါ။", "Complete 10 distinct published lessons.", "သီးခြားထုတ်ဝေထားသော သင်ခန်းစာ ၁၀ ခု ပြီးမြောက်ပါ။", "learning", "lesson_completion_count", {"count": 10}),
        ("dedicated-learner", "Dedicated Learner", "ကြိုးစားသင်ယူသူ", "Complete fifty distinct verified lessons.", "အတည်ပြုထားသော သီးခြားသင်ခန်းစာ ၅၀ ခုကို ပြီးမြောက်ပါ။", "Complete 50 distinct published lessons.", "သီးခြားထုတ်ဝေထားသော သင်ခန်းစာ ၅၀ ခု ပြီးမြောက်ပါ။", "learning", "lesson_completion_count", {"count": 50}),
        ("learning-expert", "Learning Expert", "သင်ယူမှု ကျွမ်းကျင်သူ", "Complete one hundred distinct verified lessons.", "အတည်ပြုထားသော သီးခြားသင်ခန်းစာ ၁၀၀ ခုကို ပြီးမြောက်ပါ။", "Complete 100 distinct published lessons.", "သီးခြားထုတ်ဝေထားသော သင်ခန်းစာ ၁၀၀ ခု ပြီးမြောက်ပါ။", "learning", "lesson_completion_count", {"count": 100}),
        ("quiz-champion", "Quiz Champion", "Quiz ချန်ပီယံ", "Pass a qualifying quiz using the recorded assessment result.", "မှတ်တမ်းတင်ထားသော assessment ရလဒ်ဖြင့် သတ်မှတ်ချက်ပြည့်မီသော quiz ကို အောင်မြင်ပါ။", "Pass a published quiz with at least 70%.", "ထုတ်ဝေထားသော quiz ကို အနည်းဆုံး ၇၀% ဖြင့် အောင်မြင်ပါ။", "quiz", "quiz_passed", {"minimum_score": 70}),
        ("project-creator", "Project Creator", "Project ဖန်တီးသူ", "Receive approval for your first project submission.", "ပထမဆုံး project submission အတွက် အတည်ပြုချက်ရယူပါ။", "Have 1 approved project.", "အတည်ပြုထားသော project ၁ ခု ရှိပါ။", "project", "approved_project_count", {"count": 1}),
        ("course-graduate", "Course Graduate", "သင်တန်းဘွဲ့ရ", "Complete a course through the verified certificate workflow.", "အတည်ပြုထားသော certificate workflow ဖြင့် သင်တန်းကို ပြီးမြောက်ပါ။", "Earn 1 valid course completion certificate.", "မှန်ကန်သော course completion certificate ၁ ခု ရရှိပါ။", "course", "course_verified_completion", {}),
        ("path-master", "Path Master", "Learning Path ကျွမ်းကျင်သူ", "Complete every required step in a published Learning Path.", "ထုတ်ဝေထားသော Learning Path တစ်ခု၏ လိုအပ်သောအဆင့်အားလုံးကို ပြီးမြောက်ပါ။", "Configure a published Learning Path reference and complete every required step.", "ထုတ်ဝေထားသော Learning Path ကို ချိတ်ဆက်ပြီး လိုအပ်သောအဆင့်အားလုံး ပြီးမြောက်ပါ။", "path", "learning_path_completion", {}),
        ("capstone-builder", "Capstone Builder", "Capstone တည်ဆောက်သူ", "Receive approval for a configured capstone project.", "သတ်မှတ်ထားသော capstone project အတွက် အတည်ပြုချက်ရယူပါ။", "Configure a capstone project reference and receive approval.", "Capstone project ကို ချိတ်ဆက်ပြီး အတည်ပြုချက်ရယူပါ။", "capstone", "capstone_approved", {}),
    ]
    bind = op.get_bind()
    for code, title, title_mm, description, description_mm, criteria, criteria_mm, category, rule_type, rule in definitions:
        bind.execute(sa.text("""
            INSERT INTO achievement_definitions
                (id, slug, title, title_mm, description, description_mm, criteria_description, criteria_description_mm,
                 category, threshold, rule_type, rule_json, rule_version, icon_name, tier, repeatable, visibility,
                 status, display_order, created_by)
            VALUES (:id, :slug, :title, :title_mm, :description, :description_mm, :criteria, :criteria_mm,
                    :category, 1, :rule_type, :rule_json, 1, 'Award', 'standard', false, 'public', 'draft', :display_order, NULL)
            ON CONFLICT (slug) DO NOTHING
        """), {
            "id": str(uuid.uuid4()), "slug": code, "title": title, "title_mm": title_mm,
            "description": description, "description_mm": description_mm, "criteria": criteria,
            "criteria_mm": criteria_mm, "category": category, "rule_type": rule_type,
            "rule_json": json.dumps(rule, separators=(",", ":"), ensure_ascii=False),
            "display_order": definitions.index((code, title, title_mm, description, description_mm, criteria, criteria_mm, category, rule_type, rule)),
        })


def downgrade():
    bind = op.get_bind()
    bind.execute(sa.text("DELETE FROM achievement_definitions WHERE slug IN ('first-step','knowledge-builder','dedicated-learner','learning-expert','quiz-champion','project-creator','course-graduate','path-master','capstone-builder') AND status = 'draft'"))
