"""Authored draft content for Django Module 04: templates and frontend.

The seeder in this module is intentionally scoped to the canonical fourth
module of the ``django`` course.  It preserves existing lesson identities and
published versions, while making the existing incomplete draft rows useful.
"""

from __future__ import annotations

import json
from textwrap import dedent

from sqlalchemy import select

from .models import (
    CodeExample,
    CodingExercise,
    CourseModule,
    Lesson,
    LessonContentDraft,
    LessonQuiz,
    LessonSyntaxReference,
    ModuleQuizDraft,
    ProjectCourseLink,
    ProjectMilestone,
    ProjectRequirement,
    ProjectRubricCriterion,
    ProjectTemplate,
    QuizQuestion,
    SyntaxExampleTranslation,
    SyntaxReference,
    SyntaxReferenceExample,
    SyntaxReferenceTranslation,
)


MODULE_TITLE = "Django Templates, Static Files and Frontend Integration"
MODULE_TITLE_MM = "Django Template၊ Static File နှင့် Frontend ပေါင်းစပ်မှု"
MODULE_DESCRIPTION = (
    "Learn how Django renders dynamic HTML, passes context into templates, uses template tags "
    "and filters, composes layouts, manages static assets, and builds reusable responsive interfaces."
)
MODULE_DESCRIPTION_MM = (
    "Django သည် dynamic HTML ကို render လုပ်ပုံ၊ context ပေးပုံ၊ template tag/filter သုံးပုံ၊ "
    "layout ပေါင်းစပ်ပုံ၊ static asset စီမံပုံနှင့် responsive interface တည်ဆောက်ပုံကို လေ့လာရန် module ဖြစ်သည်။"
)
OBJECTIVES = [
    "Explain Django's template engine and configure project- and app-level templates.",
    "Pass dictionaries, lists, and safe context values from views to templates.",
    "Use tags, filters, inheritance, includes, and registered custom filters without moving business logic into HTML.",
    "Load CSS, JavaScript, and images through the staticfiles system and distinguish static from media files.",
    "Build semantic, responsive, keyboard-friendly frontend layouts with safe form and asset handling.",
    "Test rendered HTML, route behavior, empty states, and the responsive Student Portal project.",
]
OBJECTIVES_MM = [
    "Django template engine နှင့် project/app-level template configuration ကို ရှင်းပြနိုင်ရန်။",
    "View မှ dictionary၊ list နှင့် safe context value များကို template သို့ ပေးနိုင်ရန်။",
    "Business logic ကို HTML ထဲမရွှေ့ဘဲ tag၊ filter၊ inheritance၊ include နှင့် registered custom filter သုံးနိုင်ရန်။",
    "Staticfiles ဖြင့် CSS၊ JavaScript နှင့် image များ load လုပ်ပြီး static နှင့် media ကို ခွဲခြားနိုင်ရန်။",
    "Semantic၊ responsive၊ keyboard-friendly frontend layout နှင့် safe form/asset handling တည်ဆောက်နိုင်ရန်။",
    "Rendered HTML၊ route behavior၊ empty state နှင့် responsive Student Portal project ကို test လုပ်နိုင်ရန်။",
]


def _example(title, files, input_text, output, steps, steps_mm):
    return {"title": title, "files": files, "input": input_text, "output": output, "steps": steps, "steps_mm": steps_mm}


def _q(prompt, options, answer, explanation, difficulty="beginner", lesson=1):
    return {"prompt": prompt, "options": options, "correct_answer": answer, "explanation": explanation, "difficulty": difficulty, "points": 2 if difficulty == "intermediate" else 1, "lesson_position": lesson}


LESSONS = [
    {
        "title": "Django Template Engine and HTML Rendering",
        "slug": "04-django-template-engine-and-html-rendering",
        "topic": "DjangoTemplates backend, template directories, render(), context, loading errors, and separation of concerns",
        "description": "Configure Django template discovery and render a first dynamic education page from a view.",
        "description_mm": "Django template discovery ကို configure လုပ်ပြီး view မှ dynamic education page ပထမဆုံး render လုပ်ပါ။",
        "syntax": "return render(request, \"pages/home.html\", {\"title\": \"Education Portal\"})",
        "theory": "A template engine combines a presentation file with trusted context data to produce an HTTP response. Django's DjangoTemplates backend searches directories in TEMPLATES[0][\"DIRS\"] and, when APP_DIRS is true, templates inside installed applications. A project-level templates directory is useful for shared layouts; app-level templates should be namespaced to avoid collisions. The render() shortcut loads a template, creates a context, and returns an HttpResponse. TemplateDoesNotExist and TemplateSyntaxError are configuration or authoring failures, not reasons to hide every exception. Keep queries and policy decisions in Python services/views and keep templates focused on presentation.",
        "theory_mm": "Template engine သည် presentation file နှင့် ယုံကြည်စိတ်ချရသော context data ကို ပေါင်းပြီး HTTP response ထုတ်ပေးသည်။ DjangoTemplates backend သည် TEMPLATES[0][\"DIRS\"] ထဲက directory များကို ရှာပြီး APP_DIRS true ဖြစ်လျှင် installed app အတွင်း template များကို ရှာသည်။ Shared layout အတွက် project-level templates နှင့် app-level template များကို collision မဖြစ်စေရန် namespace လုပ်သုံးပါ။ render() shortcut သည် template load၊ context တည်ဆောက်ပြီး HttpResponse ပြန်သည်။ Template မတွေ့ခြင်းနှင့် syntax error သည် configuration/authoring error ဖြစ်ပြီး exception အားလုံးကို ဖုံးကွယ်ရန် အကြောင်းမဟုတ်ပါ။ Query နှင့် policy ကို Python view/service တွင်ထားပြီး template ကို presentation အတွက်သာထားပါ။",
        "concepts": "DjangoTemplates backend, DIRS, APP_DIRS, project templates, app templates, render(), context, TemplateDoesNotExist, TemplateSyntaxError, and separation of concerns.",
        "concepts_mm": "DjangoTemplates backend၊ DIRS၊ APP_DIRS၊ project/app template၊ render()၊ context၊ TemplateDoesNotExist၊ TemplateSyntaxError နှင့် separation of concerns တို့ကို လေ့လာရမည်။",
        "mistakes": ["Putting templates in a directory that is not in DIRS and not inside an installed app.", "Forgetting APP_DIRS when relying on app templates.", "Calling database code from a template.", "Using a broad exception handler that converts a missing template into a fake success page."],
        "mistakes_mm": ["DIRS ထဲမပါသော directory သို့မဟုတ် installed app အတွင်းမဟုတ်သောနေရာတွင် template ထားခြင်း။", "App template သုံးသော်လည်း APP_DIRS မစစ်ခြင်း။", "Template ထဲမှ database code ခေါ်ခြင်း။", "Template error ကို fake success page အဖြစ် ပြောင်းရန် broad exception သုံးခြင်း။"],
        "best_practices": "Use a stable template root, namespace app templates, pass a small explicit context, include a useful 404/error path, and test both the response and the rendered text.",
        "best_practices_mm": "Template root တည်ငြိမ်စွာထားပါ၊ app template ကို namespace လုပ်ပါ၊ context ကို သေးငယ်ရှင်းလင်းစွာပေးပါ၊ 404/error path ရှိစေပြီး response နှင့် rendered text နှစ်ခုလုံးကို test လုပ်ပါ။",
        "examples": [
            _example("Render basic HTML", {"school_site/settings.py": "from pathlib import Path\nBASE_DIR = Path(__file__).resolve().parent.parent\nTEMPLATES = [{\"BACKEND\": \"django.template.backends.django.DjangoTemplates\", \"DIRS\": [BASE_DIR / \"templates\"], \"APP_DIRS\": True}]", "templates/pages/home.html": "<!doctype html>\n<html lang=\"en\"><body><h1>{{ title }}</h1></body></html>", "pages/views.py": "from django.shortcuts import render\n\ndef home(request):\n    return render(request, \"pages/home.html\", {\"title\": \"Education Portal\"})", "school_site/urls.py": "from django.urls import path\nfrom pages.views import home\nurlpatterns = [path(\"\", home, name=\"home\")]"}, "GET /", "Browser shows Education Portal", "Set the directory, create the template, return render(), and connect a named URL.", "Directory သတ်မှတ်ပြီး template ပြုလုပ်ပါ။ render() ပြန်ပြီး named URL နှင့် ချိတ်ပါ။"),
            _example("Create a home page template", {"templates/pages/home.html": "{% extends \"base.html\" %}\n{% block title %}Home | Education Portal{% endblock %}\n{% block content %}<main><h1>Learn with confidence</h1></main>{% endblock %}", "templates/base.html": "<!doctype html>\n<html lang=\"en\"><head><title>{% block title %}Education Portal{% endblock %}</title></head><body>{% block content %}{% endblock %}</body></html>"}, "A template request for pages/home.html", "The child page supplies title and content blocks", "Create base.html first, then let the child extend it and override named blocks.", "အရင် base.html ပြုလုပ်ပြီး child က extends လုပ်ကာ block များ override လုပ်ပါ။"),
            _example("Pass context from a view", {"pages/views.py": "from django.shortcuts import render\n\ndef home(request):\n    context = {\"title\": \"Student Portal\", \"notice\": \"Demo data only\"}\n    return render(request, \"pages/home.html\", context)", "templates/pages/home.html": "<h1>{{ title }}</h1>\n<p class=\"notice\">{{ notice }}</p>"}, "The context dictionary contains title and notice", "Student Portal and Demo data only render as text", "Keep context keys predictable and let the template decide markup, not business policy.", "Context key များကို တည်ငြိမ်စွာထားပြီး markup ကို template က ဆုံးဖြတ်ပါစေ။"),
            _example("Diagnose template loading", {"pages/views.py": "from django.shortcuts import render\n\ndef home(request):\n    return render(request, \"pages/missing.html\")", "school_site/settings.py": "TEMPLATES = [{\"BACKEND\": \"django.template.backends.django.DjangoTemplates\", \"DIRS\": [BASE_DIR / \"templates\"], \"APP_DIRS\": True}]"}, "GET / with no pages/missing.html", "Development logs show TemplateDoesNotExist; the fix is to create the file or correct its path", "Check spelling, relative template name, DIRS, APP_DIRS, and INSTALLED_APPS before changing code.", "စာလုံးပေါင်း၊ relative template name၊ DIRS၊ APP_DIRS နှင့် INSTALLED_APPS ကို အရင်စစ်ပါ။"),
        ],
        "exercises": "Create a project-level templates directory, configure DIRS and APP_DIRS, build home.html, connect a view and URL, then deliberately break the template path and fix the observed TemplateDoesNotExist error.",
        "exercises_mm": "Project-level templates directory ပြုလုပ်ပြီး DIRS/APP_DIRS configure လုပ်ပါ။ home.html၊ view နှင့် URL ချိတ်ပါ။ Template path ကို တမင်မှားစေပြီး TemplateDoesNotExist error ကို ပြန်ပြင်ပါ။",
        "homework": "Build a Django Education Portal homepage with a title, navigation placeholder, welcome message, demo-data notice, and a test that asserts the rendered HTML contains the heading.",
        "homework_mm": "Title၊ navigation placeholder၊ welcome message နှင့် demo-data notice ပါသော Django Education Portal homepage တည်ဆောက်ပါ။ Rendered HTML တွင် heading ပါကြောင်း test ရေးပါ။",
        "summary": "Django templates are discovered through explicit settings, rendered from views, and kept responsible for presentation rather than business decisions.",
        "summary_mm": "Django template များကို settings ဖြင့်ရှာဖွေပြီး view မှ render လုပ်ကာ business decision မဟုတ်ဘဲ presentation အတွက်သာ အသုံးပြုရသည်။",
        "quiz": [
            _q("Which setting key lists project-level template directories?", ["DIRS", "STATIC_URL", "ALLOWED_HOSTS", "ROOT_URLCONF"], "DIRS", "DIRS tells Django where project templates can be found.", lesson=1),
            _q("What does APP_DIRS=True enable?", ["Searching installed apps for templates", "Loading user uploads as code", "Disabling autoescape", "Creating database tables"], "Searching installed apps for templates", "App directories become part of template discovery.", lesson=1),
            _q("What does render() return?", ["An HttpResponse rendered from a template", "A database migration", "A CSS file", "A URL pattern"], "An HttpResponse rendered from a template", "The shortcut loads the template and returns the response.", lesson=1),
            _q("Which error means Django cannot find the named template?", ["TemplateDoesNotExist", "IntegrityError", "KeyError only", "PermissionDenied always"], "TemplateDoesNotExist", "The loader did not find a matching template.", lesson=1),
            _q("True or false: templates should own complex business rules.", ["True", "False"], "False", "Keep policy and data operations in Python boundaries.", lesson=1),
            _q("Where is a shared base template commonly kept?", ["A project-level templates directory", "Inside a password field", "Only in static/js", "In a database migration"], "A project-level templates directory", "Shared layouts are often project-level assets.", lesson=1),
            _q("What is the purpose of context?", ["Values made available to a template", "A CSS selector", "A URL converter", "A password store"], "Values made available to a template", "The context is the view-to-template data boundary.", lesson=1),
            _q("Which fix should be checked first for a missing template?", ["Path, DIRS, APP_DIRS, and installed app configuration", "Disable all exceptions", "Publish the page", "Delete the URL"], "Path, DIRS, APP_DIRS, and installed app configuration", "Loader configuration and path are the usual causes.", "intermediate", 1),
        ],
    },
    {
        "title": "Template Variables and Context",
        "slug": "04-template-variables-and-context",
        "topic": "context dictionaries, variable lookup, nested data, missing values, autoescaping, and safe presentation",
        "description": "Pass student and course data into templates while preserving safe, readable presentation boundaries.",
        "description_mm": "Student နှင့် course data များကို safe presentation boundary ထိန်းထားပြီး template သို့ ပေးပါ။",
        "syntax": "{{ student.name }}\n{{ student.courses.0 }}\n{{ profile.email|default:\"Not provided\" }}",
        "theory": "A context is a mapping from names to values. Django's template variable lookup can traverse dictionary keys, object attributes, and list indexes using dot notation, but it is not Python expression evaluation. A dictionary key such as student['name'] is accessed in a template as student.name; Django applies its lookup rules in a defined order. Missing variables render as an empty string by default, so a view should validate important data and a template should use default or if guards for optional display values. Autoescaping protects HTML output by escaping characters from untrusted strings. Do not disable autoescape or mark untrusted HTML safe.",
        "theory_mm": "Context သည် name နှင့် value များကို ချိတ်ထားသော mapping ဖြစ်သည်။ Django template variable lookup သည် dictionary key၊ object attribute နှင့် list index များကို dot notation ဖြင့် ရှာနိုင်သော်လည်း Python expression ကို တိုက်ရိုက်မတွက်ပါ။ Python တွင် student['name'] ဖြစ်သောအရာကို template တွင် student.name ဟု ရေးသည်။ Missing variable သည် ပုံမှန်အားဖြင့် empty string ဖြစ်နိုင်သောကြောင့် အရေးကြီး data ကို view တွင် validate လုပ်ပြီး optional display အတွက် default/if guard သုံးပါ။ Autoescaping သည် untrusted string ထဲက HTML special character များကို escape လုပ်ပြီး ကာကွယ်သည်။ Autoescape ပိတ်ခြင်း သို့မဟုတ် untrusted HTML ကို safe သတ်မှတ်ခြင်း မလုပ်ပါနှင့်။",
        "concepts": "Context dictionaries, dot lookup, dictionary versus template access, object attributes, list indexes, nested values, missing variables, default values, autoescaping, and XSS prevention.",
        "concepts_mm": "Context dictionary၊ dot lookup၊ dictionary နှင့် template access ခြားနားမှု၊ object attribute၊ list index၊ nested value၊ missing variable၊ default value၊ autoescaping နှင့် XSS ကာကွယ်မှုတို့ကို လေ့လာရမည်။",
        "mistakes": ["Writing Python indexing or method calls as if templates were Python.", "Assuming an empty rendered value proves the data was correct.", "Using |safe on user-provided HTML.", "Passing a huge unrelated object graph when a small context would do."],
        "mistakes_mm": ["Template ကို Python ကဲ့သို့ index/method call ရေးခြင်း။", "Rendered value empty ဖြစ်ခြင်းကို data မှန်ကြောင်း ယူဆခြင်း။", "User-provided HTML ကို |safe သုံးခြင်း။", "Context သေးသေးလေးဖြင့် ရသော်လည်း မသက်ဆိုင်သော object graph ကြီး ပေးခြင်း။"],
        "best_practices": "Prepare display-ready values in Python, use descriptive context keys, guard optional values, keep context small, and rely on autoescaping for untrusted text.",
        "best_practices_mm": "Python တွင် display-ready value ပြင်ဆင်ပါ၊ context key ရှင်းလင်းစွာပေးပါ၊ optional value ကို guard လုပ်ပါ၊ context ကိုသေးငယ်စွာထားပြီး untrusted text အတွက် autoescaping ကို ယုံကြည်ပါ။",
        "examples": [
            _example("Display student name", {"students/views.py": "from django.shortcuts import render\n\nSTUDENTS = [{\"id\": 1, \"name\": \"John\", \"course\": \"Python\"}, {\"id\": 2, \"name\": \"Mary\", \"course\": \"Django\"}]\n\ndef list_students(request):\n    return render(request, \"students/list.html\", {\"students\": STUDENTS})", "students/templates/students/list.html": "<h1>Students</h1>\n<p>{{ students.0.name }}</p>"}, "students contains two dictionaries", "The page shows John", "The view provides the list; dot lookup reads the first dictionary's name.", "View က list ပေးပြီး dot lookup ဖြင့် ပထမ dictionary ၏ name ကို ဖတ်သည်။"),
            _example("Display a profile", {"students/views.py": "def profile(request):\n    student = {\"name\": \"Mary\", \"course\": \"Django\", \"contact\": {\"email\": \"mary@example.test\"}}\n    return render(request, \"students/profile.html\", {\"student\": student})", "students/templates/students/profile.html": "<h1>{{ student.name }}</h1>\n<p>{{ student.course }}</p>\n<a href=\"mailto:{{ student.contact.email }}\">Email</a>"}, "A nested student dictionary", "Mary, Django, and the email link render", "Nested dictionary keys are accessed with dots, but the output still passes through template escaping.", "Nested dictionary key များကို dot ဖြင့် ဖတ်ပြီး output သည် escaping ဖြင့် ဖြတ်သန်းသည်။"),
            _example("Render a student list", {"students/templates/students/list.html": "<ul>\n{% for student in students %}<li>{{ student.id }} — {{ student.name }} — {{ student.course }}</li>{% empty %}<li>No students yet.</li>{% endfor %}\n</ul>", "students/views.py": "def list_students(request):\n    students = [{\"id\": 1, \"name\": \"John\", \"course\": \"Python\"}, {\"id\": 2, \"name\": \"Mary\", \"course\": \"Django\"}]\n    return render(request, \"students/list.html\", {\"students\": students})"}, "Two student dictionaries", "A two-row unordered list is rendered", "The loop uses each dictionary as student and the empty branch handles no records.", "Loop သည် dictionary တစ်ခုစီကို student အဖြစ်သုံးပြီး empty branch ဖြင့် record မရှိမှုကို ကိုင်တွယ်သည်။"),
            _example("Handle missing values safely", {"students/templates/students/profile.html": "<p>Email: {{ student.email|default:\"Not provided\" }}</p>\n{% if student.bio %}<p>{{ student.bio }}</p>{% else %}<p>No biography yet.</p>{% endif %}", "students/views.py": "def profile(request):\n    return render(request, \"students/profile.html\", {\"student\": {\"name\": \"John\"}})"}, "student has no email or bio", "The page shows Not provided and No biography yet", "Default is for a display fallback; critical validation belongs in Python.", "Default သည် display fallback အတွက်ဖြစ်ပြီး အရေးကြီး validation ကို Python တွင်လုပ်ရသည်။"),
        ],
        "exercises": "Use the given John and Mary dictionaries. Render names, courses, nested profile data, a missing email fallback, and an empty list state. Add a test showing that a value containing <script> is escaped in the response.",
        "exercises_mm": "ပေးထားသော John/Mary dictionary များကိုသုံးပါ။ Name၊ course၊ nested profile၊ missing email fallback နှင့် empty list state ကို render လုပ်ပါ။ <script> ပါသော value ကို response တွင် escape လုပ်ကြောင်း test ရေးပါ။",
        "homework": "Build a dynamic Student Profile Page with a safe summary, course label, optional biography, contact fallback, and tests for both complete and incomplete demo records.",
        "homework_mm": "Safe summary၊ course label၊ optional biography နှင့် contact fallback ပါသော dynamic Student Profile Page တည်ဆောက်ပါ။ Complete/incomplete demo record နှစ်မျိုးအတွက် test ရေးပါ။",
        "summary": "Template lookup is presentation-oriented, missing values need explicit display decisions, and autoescaping is a security boundary.",
        "summary_mm": "Template lookup သည် presentation-oriented ဖြစ်ပြီး missing value ကို display decision ဖြင့် ကိုင်တွယ်ရသည်။ Autoescaping သည် security boundary ဖြစ်သည်။",
        "quiz": [
            _q("How is a dictionary key commonly accessed in a template?", ["{{ student.name }}", "{{ student['name'] }} only", "{{ student->name }}", "{{ student::name }}"], "{{ student.name }}", "Django template dot lookup handles dictionary keys.", lesson=2),
            _q("What does |default provide?", ["A fallback for an empty or missing display value", "A database default migration", "A CSS class", "A URL namespace"], "A fallback for an empty or missing display value", "It is useful for optional presentation values.", lesson=2),
            _q("Which list index is written as students.0?", ["The first item", "The second item", "The last item", "No item"], "The first item", "Indexes are zero-based.", lesson=2),
            _q("True or false: template variables are full Python expressions.", ["True", "False"], "False", "The template language intentionally limits expression evaluation.", lesson=2),
            _q("What does autoescaping help prevent?", ["HTML injection and XSS from untrusted text", "Missing migrations", "Slow URLs", "Duplicate apps"], "HTML injection and XSS from untrusted text", "Special characters are escaped for HTML output.", "intermediate", 2),
            _q("Which tag handles an empty loop safely?", ["{% empty %}", "{% missing %}", "{% fallback_loop %}", "{% none %}"], "{% empty %}", "The for tag supports an empty branch.", lesson=2),
            _q("Where should critical data validation happen?", ["A Python boundary such as a view or service", "Only in CSS", "After HTML is published", "In a URL name"], "A Python boundary such as a view or service", "Templates should not be the only validation layer.", "intermediate", 2),
            _q("What is unsafe as a default?", ["Applying |safe to user-provided HTML", "Using autoescape", "Using default", "Passing a small context"], "Applying |safe to user-provided HTML", "It can turn untrusted content into executable markup.", "intermediate", 2),
        ],
    },
    {
        "title": "Django Template Tags and Filters",
        "slug": "04-django-template-tags-and-filters",
        "topic": "if, for, empty, url, with, comment, built-in filters, and registered custom filters",
        "description": "Use Django's presentation language to format and branch on prepared data without moving business logic into templates.",
        "description_mm": "ပြင်ဆင်ထားသော data ကို template တွင် format/branch လုပ်ပြီး business logic မရွှေ့ဘဲ Django tag/filter သုံးပါ။",
        "syntax": "{% if student.active %}...{% endif %}\n{% for course in courses %}...{% empty %}...{% endfor %}\n{{ name|title|truncatechars:24 }}",
        "theory": "Template tags control structure and template filters transform a value for display. if/elif/else handles presentation branches, for iterates over prepared collections, and empty gives a useful no-data state. url reverses a named route instead of hard-coding a path. with binds a temporary value and comment hides documentation from output. Filters such as default, length, upper, lower, title, date, and truncatechars should remain small and readable. A custom filter is a registered Python function in a templatetags package; it should format a value, not perform authorization or a large query. The backend remains responsible for business rules.",
        "theory_mm": "Template tag သည် structure ကိုထိန်းပြီး filter သည် value ကို display အတွက် ပြောင်းလဲသည်။ if/elif/else သည် presentation branch၊ for သည် prepared collection loop နှင့် empty သည် data မရှိမှုကို ပြသည်။ url သည် path hard-code မလုပ်ဘဲ named route reverse လုပ်သည်။ with သည် temporary value bind လုပ်ပြီး comment သည် output မထွက်သော မှတ်ချက်ဖြစ်သည်။ default၊ length၊ upper၊ lower၊ title၊ date နှင့် truncatechars filter များကို သေးငယ်ရှင်းလင်းစွာ သုံးပါ။ Custom filter သည် templatetags package ထဲက register လုပ်ထားသော Python function ဖြစ်ပြီး value format အတွက်သာသုံးသင့်သည်။ Authorization နှင့် query ကို backend တွင်ထားပါ။",
        "concepts": "Block tags, filter arguments, chained filters, named URL generation, empty states, custom filter registration, and avoiding business logic in templates.",
        "concepts_mm": "Block tag၊ filter argument၊ chained filter၊ named URL၊ empty state၊ custom filter registration နှင့် template ထဲ business logic မထည့်ခြင်းတို့ကို လေ့လာရမည်။",
        "mistakes": ["Forgetting closing tags such as endif or endfor.", "Using a filter chain that hides a business decision.", "Calling a database query from a custom filter.", "Using a literal URL where {% url %} would survive route changes."],
        "mistakes_mm": ["endif/endfor ကဲ့သို့ closing tag မပိတ်ခြင်း။", "Business decision ကို filter chain ထဲ ဖုံးကွယ်ခြင်း။", "Custom filter မှ database query ခေါ်ခြင်း။", "Route ပြောင်းလဲနိုင်သော်လည်း {% url %} အစား literal URL သုံးခြင်း။"],
        "best_practices": "Prepare booleans and collections in Python, keep template branches obvious, use named URLs, register custom filters explicitly, and test empty as well as populated states.",
        "best_practices_mm": "Boolean နှင့် collection ကို Python တွင်ပြင်ဆင်ပါ၊ template branch ကို ရှင်းလင်းစွာထားပါ၊ named URL သုံးပါ၊ custom filter ကို explicit register လုပ်ပြီး populated/empty state နှစ်ခုလုံး test လုပ်ပါ။",
        "examples": [
            _example("Conditional student status", {"students/templates/students/card.html": "<article>{% if student.active %}<span class=\"status\">Active</span>{% elif student.graduated %}<span>Graduate</span>{% else %}<span>On hold</span>{% endif %}</article>", "students/views.py": "context = {\"student\": {\"active\": True, \"graduated\": False}}"}, "active=True", "The card shows Active", "The view supplies booleans and the template chooses only presentation text.", "View က boolean များပေးပြီး template က presentation text ကိုသာ ရွေးသည်။"),
            _example("Loop and empty state", {"templates/courses/list.html": "<ul>{% for course in courses %}<li>{{ course.name|title }}</li>{% empty %}<li class=\"empty\">No courses yet.</li>{% endfor %}</ul>", "courses/views.py": "def list_courses(request):\n    return render(request, \"courses/list.html\", {\"courses\": []})"}, "courses=[]", "No courses yet. is rendered", "The empty branch makes the UI intentional rather than blank.", "Empty branch သည် blank UI မဖြစ်စေဘဲ ရည်ရွယ်ချက်ရှိသော state ပြသည်။"),
            _example("Format course data", {"templates/courses/detail.html": "<h1>{{ course.name|title }}</h1>\n<p>{{ course.summary|truncatechars:80 }}</p>\n<p>{{ course.updated_at|date:\"Y-m-d\" }}</p>", "courses/views.py": "course = {\"name\": \"django templates\", \"summary\": \"Learn safe, reusable frontend rendering.\", \"updated_at\": now()}"}, "A course dictionary with name, summary, and date", "Title case, truncated summary, and YYYY-MM-DD date render", "Filters format values without changing the source object.", "Filter များသည် source object မပြောင်းဘဲ display value ကို format လုပ်သည်။"),
            _example("Register a custom filter", {"students/templatetags/student_extras.py": "from django import template\n\nregister = template.Library()\n\n@register.filter\ndef initials(value):\n    return \"\".join(part[0].upper() for part in str(value).split() if part)[:2]", "students/templates/students/card.html": "{% load student_extras %}<span aria-label=\"Initials\">{{ student.name|initials }}</span>", "students/views.py": "context = {\"student\": {\"name\": \"Mary Aung\"}}"}, "student name Mary Aung", "MA is rendered", "Create templatetags/__init__.py, register the filter, load the library, and keep it a pure formatter.", "templatetags/__init__.py ပြုလုပ်ပြီး filter register/load လုပ်ပါ။ Pure formatter အဖြစ်ထားပါ။"),
        ],
        "exercises": "Build a course listing with if/elif/else status, for/empty rendering, title and truncatechars filters, named {% url %} links, and one registered initials filter. Test populated and empty data.",
        "exercises_mm": "if/elif/else status၊ for/empty၊ title/truncatechars၊ named {% url %} link နှင့် initials custom filter ပါသော course listing တည်ဆောက်ပါ။ Populated/empty data test လုပ်ပါ။",
        "homework": "Build a Course Listing UI where all display formatting is in the template, while availability and enrollment decisions are computed in Python before rendering.",
        "homework_mm": "Display formatting ကို template တွင်ထားပြီး availability/enrollment decision ကို render မလုပ်မီ Python တွင်တွက်ထားသော Course Listing UI တည်ဆောက်ပါ။",
        "summary": "Tags control presentation structure, filters format values, and custom filters should remain registered, small, and free from business side effects.",
        "summary_mm": "Tag များသည် presentation structure ကို ထိန်းပြီး filter များသည် value format လုပ်သည်။ Custom filter သည် register လုပ်ထားသော သေးငယ်ပြီး side effect မရှိသော formatter ဖြစ်သင့်သည်။",
        "quiz": [
            _q("Which tag iterates over a collection?", ["{% for %}", "{% loop_now %}", "{% each_python %}", "{% list %}"], "{% for %}", "The for tag iterates over template context data.", lesson=3),
            _q("Which branch handles no items in a for loop?", ["{% empty %}", "{% none %}", "{% elsefor %}", "{% noitems %}"], "{% empty %}", "The for tag supports an empty branch.", lesson=3),
            _q("What does {% url %} use?", ["A named URL pattern", "A CSS file", "A database password", "A template variable only"], "A named URL pattern", "It reverses a route name.", lesson=3),
            _q("What does |truncatechars:80 do?", ["Limits displayed characters to 80", "Creates 80 database rows", "Escapes a URL", "Loads static files"], "Limits displayed characters to 80", "It is a presentation filter.", lesson=3),
            _q("True or false: a custom filter should perform authorization queries.", ["True", "False"], "False", "Authorization belongs in a backend policy boundary.", "intermediate", 3),
            _q("What must a custom filter library call?", ["register = template.Library()", "settings.register_filter_only", "urls.register", "static.register"], "register = template.Library()", "Django uses the template Library registry.", lesson=3),
            _q("Which filter changes text to title case?", ["title", "length", "date", "default"], "title", "title formats words for display.", lesson=3),
            _q("Why test an empty list?", ["To ensure the UI explains no data instead of rendering a blank region", "To disable autoescape", "To create a model", "To publish a quiz"], "To ensure the UI explains no data instead of rendering a blank region", "Empty states are part of the user experience.", "intermediate", 3),
        ],
    },
    {
        "title": "Template Inheritance and Shared Layouts",
        "slug": "04-template-inheritance-and-shared-layouts",
        "topic": "base.html, extends, block, block.super, nested layouts, shared navigation, and accessible structure",
        "description": "Create a reusable layout so education pages share navigation, title, CSS, and footer without duplicated HTML.",
        "description_mm": "Education page များတွင် navigation၊ title၊ CSS နှင့် footer ကို HTML မထပ်ဘဲ reusable layout ဖြင့် မျှဝေပါ။",
        "syntax": "{% extends \"base.html\" %}\n{% block title %}Students{% endblock %}\n{% block content %}...{% endblock %}",
        "theory": "Template inheritance lets a base template define the document skeleton and child templates fill named blocks. {% extends \"base.html\" %} must be the first template tag in a child. {% block %} and {% endblock %} define replacement regions; block.super preserves the parent content when a child wants to add rather than replace. A base layout should provide semantic landmarks, a page title block, a main content block, navigation, and a footer. Keep the layout hierarchy predictable and name templates by app or page area to avoid collisions. Shared CSS and JavaScript can be loaded once by the base template.",
        "theory_mm": "Template inheritance သည် base template တွင် document skeleton သတ်မှတ်ပြီး child template က named block များဖြည့်စေသည်။ {% extends \"base.html\" %} သည် child template ၏ ပထမဆုံး template tag ဖြစ်ရမည်။ {% block %}/{% endblock %} သည် replacement region သတ်မှတ်ပြီး child က parent content ကို ဆက်ထားလိုလျှင် block.super သုံးနိုင်သည်။ Base layout တွင် semantic landmark၊ page title block၊ main content၊ navigation နှင့် footer ပါသင့်သည်။ Layout hierarchy ကို တည်ငြိမ်စွာထားပြီး collision မဖြစ်စေရန် app/page area အလိုက် template name ပေးပါ။ Shared CSS/JavaScript ကို base template မှ တစ်ကြိမ် load လုပ်နိုင်သည်။",
        "concepts": "Parent and child templates, extends ordering, named blocks, block.super, nested inheritance, shared navigation/footer, and semantic landmarks.",
        "concepts_mm": "Parent/child template၊ extends order၊ named block၊ block.super၊ nested inheritance၊ shared navigation/footer နှင့် semantic landmark များကို လေ့လာရမည်။",
        "mistakes": ["Putting markup before extends in a child template.", "Using the same block name for unrelated page regions.", "Duplicating navigation in every page.", "Removing focus-visible styles from shared navigation."],
        "mistakes_mm": ["Child template တွင် extends မတိုင်မီ markup ထည့်ခြင်း။", "မသက်ဆိုင်သော page region များတွင် block name တူသုံးခြင်း။", "Page တိုင်းတွင် navigation ပြန်ရေးခြင်း။", "Shared navigation မှ focus-visible style ဖယ်ခြင်း။"],
        "best_practices": "Keep base.html small and semantic, define stable blocks, use block.super intentionally, load shared assets centrally, and test each child page through its real route.",
        "best_practices_mm": "base.html ကို သေးငယ် semantic ထားပါ၊ stable block သတ်မှတ်ပါ၊ block.super ကို ရည်ရွယ်ချက်ရှိမှသုံးပါ၊ shared asset ကို central load လုပ်ပြီး child page တစ်ခုစီကို real route ဖြင့် test လုပ်ပါ။",
        "examples": [
            _example("Create base.html", {"templates/base.html": "{% load static %}\n<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>{% block title %}Education Portal{% endblock %}</title><link rel=\"stylesheet\" href=\"{% static 'css/main.css' %}\"></head><body><header>{% block header %}{% endblock %}</header><main id=\"main-content\">{% block content %}{% endblock %}</main><footer>{% block footer %}{% endblock %}</footer></body></html>"}, "No child template yet", "A valid document skeleton with title/header/content/footer blocks", "Place extends-compatible blocks in one base document and include viewport metadata.", "Base document တစ်ခုတွင် extends-compatible block များနှင့် viewport metadata ထည့်ပါ။"),
            _example("Extend the base", {"templates/pages/home.html": "{% extends \"base.html\" %}\n{% block title %}Home | Education Portal{% endblock %}\n{% block content %}<h1>Welcome</h1><p>Learn by building.</p>{% endblock %}"}, "The home route renders pages/home.html", "The browser keeps base markup and replaces title/content", "The extends tag is first, and only declared blocks are overridden.", "extends tag ကို ပထမဆုံးထားပြီး သတ်မှတ်ထားသော block များကိုသာ override လုပ်ပါ။"),
            _example("Add navigation with block.super", {"templates/base.html": "{% block header %}<nav aria-label=\"Primary\"><a href=\"{% url 'home' %}\">Home</a></nav>{% endblock %}", "templates/pages/about.html": "{% extends \"base.html\" %}\n{% block header %}{{ block.super }}<span class=\"section-label\">About</span>{% endblock %}\n{% block content %}<h1>About</h1>{% endblock %}"}, "About page extends the shared header", "The Home link remains and the About label is added", "block.super preserves parent content before adding a child-specific fragment.", "block.super သည် parent content ကို ထိန်းပြီး child fragment ထပ်ထည့်စေသည်။"),
            _example("Build a multi-page layout", {"templates/students/list.html": "{% extends \"base.html\" %}\n{% block title %}Students{% endblock %}\n{% block content %}<section aria-labelledby=\"students-title\"><h1 id=\"students-title\">Students</h1>{% include \"components/empty_state.html\" with message=\"No students yet.\" %}</section>{% endblock %}", "templates/courses/list.html": "{% extends \"base.html\" %}\n{% block title %}Courses{% endblock %}\n{% block content %}<section><h1>Courses</h1><p>Explore the catalog.</p></section>{% endblock %}"}, "Two child pages use one base", "Both pages share header/footer/CSS and have unique title/content", "Add one child at a time, navigate to it, and inspect the rendered landmarks.", "Child page တစ်ခုစီတိုးပြီး navigate လုပ်ကာ rendered landmark များကို စစ်ပါ။"),
        ],
        "exercises": "Create base.html with a skip link, navigation, main, and footer blocks. Extend it from home, students, and courses pages. Use block.super once and test that all pages contain one main landmark.",
        "exercises_mm": "Skip link၊ navigation၊ main နှင့် footer block ပါသော base.html ပြုလုပ်ပါ။ Home/students/courses page များက extends လုပ်ပါ။ block.super တစ်ကြိမ်သုံးပြီး page တိုင်း main landmark တစ်ခုပါကြောင်း test လုပ်ပါ။",
        "homework": "Build a reusable Education Website layout with Home, Students, Courses, and About pages. Keep navigation in one partial/base boundary and add active-page styling without duplicating markup.",
        "homework_mm": "Home၊ Students၊ Courses နှင့် About page ပါသော reusable Education Website layout တည်ဆောက်ပါ။ Navigation ကို boundary တစ်ခုတွင်သာထားပြီး markup မထပ်ဘဲ active-page style ထည့်ပါ။",
        "summary": "Inheritance gives every page a shared semantic skeleton while named blocks let each page supply its own content.",
        "summary_mm": "Inheritance သည် page တိုင်းကို semantic skeleton တစ်ခုမျှဝေစေပြီး named block များက page-specific content ဖြည့်စေသည်။",
        "quiz": [
            _q("Which tag makes a child use a parent template?", ["{% extends %}", "{% inherits_now %}", "{% parent %}", "{% layout %}"], "{% extends %}", "extends selects the parent template.", lesson=4),
            _q("Where should extends appear?", ["As the first template tag", "After arbitrary HTML", "Only in CSS", "Inside a Python loop"], "As the first template tag", "Django requires the inheritance declaration first.", lesson=4),
            _q("What does block define?", ["A replaceable template region", "A database table", "A URL converter", "A JavaScript event"], "A replaceable template region", "Child templates override named blocks.", lesson=4),
            _q("What does block.super preserve?", ["Parent block content", "A database transaction", "A static file cache", "A quiz answer"], "Parent block content", "It lets a child extend rather than replace the parent.", lesson=4),
            _q("True or false: copying the navbar to every page is the best reuse pattern.", ["True", "False"], "False", "Put shared navigation in a base or component boundary.", lesson=4),
            _q("Which element is an accessible main landmark?", ["<main>", "<span>", "<b>", "<i>"], "<main>", "Semantic landmarks help structure and assistive technology.", lesson=4),
            _q("Where should shared CSS commonly load?", ["The base template", "Every duplicated page only", "A quiz answer", "A URL name"], "The base template", "The shared shell can load common assets once.", lesson=4),
            _q("What is a useful inheritance test?", ["Each real route contains expected title and one main landmark", "Only check file size", "Disable autoescape", "Delete the base"], "Each real route contains expected title and one main landmark", "Rendered behavior is more valuable than file presence.", "intermediate", 4),
        ],
    },
    {
        "title": "Static Files, CSS, JavaScript and Images",
        "slug": "04-static-files-css-javascript-and-images",
        "topic": "staticfiles, STATIC_URL, STATICFILES_DIRS, STATIC_ROOT, load static, static, asset namespacing, and media",
        "description": "Load and organize frontend assets correctly in development while preparing a safe production collection step.",
        "description_mm": "Development တွင် frontend asset များကို မှန်ကန်စွာ load/organize လုပ်ပြီး production collection အတွက် ပြင်ဆင်ပါ။",
        "syntax": "{% load static %}\n<link rel=\"stylesheet\" href=\"{% static 'students/css/students.css' %}\">\nSTATIC_URL = \"static/\"",
        "theory": "Static files are application-owned assets such as CSS, JavaScript, and bundled images. django.contrib.staticfiles discovers them during development and collectstatic gathers them into STATIC_ROOT for a deployment storage backend. STATIC_URL is the URL prefix used in templates; STATICFILES_DIRS adds project-level directories; app assets are conventionally namespaced under app_name/static/app_name/. User-uploaded content is media, not static application code, and must use a separate MEDIA_ROOT/storage policy. {% load static %} loads the tag library and {% static %} builds the correct URL. runserver is convenient for development but is not a production static hosting solution.",
        "theory_mm": "Static file သည် application ပိုင် CSS၊ JavaScript နှင့် bundled image asset များဖြစ်သည်။ django.contrib.staticfiles သည် development တွင် ရှာဖွေပြီး collectstatic သည် deployment storage အတွက် STATIC_ROOT ထဲ စုစည်းသည်။ STATIC_URL သည် template တွင်သုံးသော URL prefix ဖြစ်ပြီး STATICFILES_DIRS သည် project-level directory ထပ်ထည့်သည်။ App asset ကို app_name/static/app_name/ အောက်တွင် namespace လုပ်ထားလေ့ရှိသည်။ User-uploaded content သည် media ဖြစ်ပြီး static application code မဟုတ်သဖြင့် MEDIA_ROOT/storage policy သီးခြားထားရသည်။ {% load static %} သည် tag library load လုပ်ပြီး {% static %} သည် မှန်ကန်သော URL တည်ဆောက်သည်။ runserver သည် development အတွက်သာဖြစ်ပြီး production static hosting မဟုတ်ပါ။",
        "concepts": "STATIC_URL, STATICFILES_DIRS, STATIC_ROOT, staticfiles app, app namespacing, collectstatic, cache strategy, media separation, and missing asset debugging.",
        "concepts_mm": "STATIC_URL၊ STATICFILES_DIRS၊ STATIC_ROOT၊ staticfiles app၊ app namespace၊ collectstatic၊ cache strategy၊ media ခွဲခြားမှုနှင့် missing asset debug တို့ကို လေ့လာရမည်။",
        "mistakes": ["Confusing STATIC_ROOT with MEDIA_ROOT.", "Hard-coding /static/ paths instead of using {% static %}.", "Putting user uploads in trusted application static directories.", "Treating runserver's static serving as production deployment."],
        "mistakes_mm": ["STATIC_ROOT နှင့် MEDIA_ROOT ကို ရောထွေးခြင်း။", "{% static %} အစား /static/ path hard-code လုပ်ခြင်း။", "User upload ကို trusted application static directory ထဲထည့်ခြင်း။", "runserver static serving ကို production deployment ဟုယူဆခြင်း။"],
        "best_practices": "Namespace app assets, use the static tag, collect assets in deployment, set cache policy deliberately, and keep uploaded media on a separate controlled storage boundary.",
        "best_practices_mm": "App asset ကို namespace လုပ်ပါ၊ static tag သုံးပါ၊ deployment တွင် collect လုပ်ပါ၊ cache policy ရည်ရွယ်ချက်ရှိစွာထားပြီး uploaded media ကို storage boundary သီးခြားတွင် ထားပါ။",
        "examples": [
            _example("Load external CSS", {"school_site/settings.py": "INSTALLED_APPS = [\"django.contrib.staticfiles\"]\nSTATIC_URL = \"static/\"\nSTATICFILES_DIRS = [BASE_DIR / \"static\"]", "templates/base.html": "{% load static %}<link rel=\"stylesheet\" href=\"{% static 'css/main.css' %}\">", "static/css/main.css": "body { font-family: system-ui; color: #172033; }"}, "Request base.html", "The response links /static/css/main.css in development", "Register staticfiles, define STATIC_URL, load the tag, and inspect the stylesheet request.", "staticfiles register လုပ်၊ STATIC_URL သတ်မှတ်၊ tag load လုပ်ပြီး stylesheet request ကို စစ်ပါ။"),
            _example("Load a static image", {"students/static/students/images/student.svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 160 100\" role=\"img\" aria-labelledby=\"title\"><title id=\"title\">Student illustration</title><rect width=\"160\" height=\"100\" rx=\"16\" fill=\"#e8e5ff\"/><circle cx=\"80\" cy=\"38\" r=\"18\" fill=\"#7658ff\"/><path d=\"M40 88c6-24 22-34 40-34s34 10 40 34\" fill=\"#7658ff\"/></svg>", "students/templates/students/profile.html": "{% load static %}<img src=\"{% static 'students/images/student.svg' %}\" alt=\"Student profile illustration\">"}, "The namespaced image exists under app static", "The browser requests /static/students/images/student.svg with useful alt text", "Keep the app namespace in both the path and the static tag.", "App namespace ကို path နှင့် static tag နှစ်ခုလုံးတွင် ထိန်းထားပါ။"),
            _example("Add JavaScript", {"templates/base.html": "{% load static %}<script src=\"{% static 'js/main.js' %}\" defer></script>", "static/js/main.js": "document.addEventListener('DOMContentLoaded', () => {\n  const button = document.querySelector('[data-menu-toggle]');\n  const menu = document.querySelector('[data-menu]');\n  if (!button || !menu) return;\n  button.addEventListener('click', () => {\n    const expanded = button.getAttribute('aria-expanded') === 'true';\n    button.setAttribute('aria-expanded', String(!expanded));\n    menu.hidden = expanded;\n  });\n});"}, "A button with data-menu-toggle and a hidden menu", "Clicking the button updates aria-expanded and visibility", "Use defer, guard missing elements, update accessible state, and keep behavior progressive.", "defer သုံး၊ element မရှိပါက guard လုပ်၊ accessible state update လုပ်ပြီး progressive behavior ထားပါ။"),
            _example("Prepare files for deployment", {"school_site/settings.py": "STATIC_URL = \"/static/\"\nSTATIC_ROOT = BASE_DIR / \"collected-static\"", "deployment/commands.txt": "python manage.py collectstatic --noinput"}, "A configured production settings environment", "collectstatic copies versioned assets into STATIC_ROOT for the configured storage", "Run collectstatic in an isolated deployment step and serve the collected directory through a proper web server/storage backend.", "collectstatic ကို deployment step သီးခြားတွင် run ပြီး proper web server/storage ဖြင့် serve လုပ်ပါ။"),
        ],
        "exercises": "Create app-namespaced CSS, a static image with alt text, and a JavaScript menu toggle. Configure STATIC_URL and STATICFILES_DIRS, confirm asset URLs, then diagnose one missing asset without moving it into MEDIA_ROOT.",
        "exercises_mm": "App-namespaced CSS၊ alt text ပါသော static image နှင့် JavaScript menu toggle တည်ဆောက်ပါ။ STATIC_URL/STATICFILES_DIRS configure လုပ်ပြီး asset URL စစ်ပါ။ Missing asset တစ်ခုကို MEDIA_ROOT သို့မရွှေ့ဘဲ debug လုပ်ပါ။",
        "homework": "Style the Student Portal using external CSS, a namespaced illustration, and a keyboard-friendly mobile menu. Document why STATIC_ROOT and MEDIA_ROOT are different.",
        "homework_mm": "External CSS၊ namespaced illustration နှင့် keyboard-friendly mobile menu ဖြင့် Student Portal ကို style လုပ်ပါ။ STATIC_ROOT နှင့် MEDIA_ROOT မတူကြောင်း မှတ်တမ်းတင်ပါ။",
        "summary": "Staticfiles provides a disciplined asset path from source directories to deployment storage, while uploaded media needs a separate trust boundary.",
        "summary_mm": "Staticfiles သည် source directory မှ deployment storage အထိ asset လမ်းကြောင်းကို စည်းကမ်းရှိစွာ စီမံပြီး uploaded media သည် trust boundary သီးခြားလိုအပ်သည်။",
        "quiz": [
            _q("What does STATIC_URL represent?", ["The URL prefix for static assets", "The upload directory", "The database URL", "The template context"], "The URL prefix for static assets", "Templates use it through the static tag.", lesson=5),
            _q("What is STATIC_ROOT for?", ["Collected static files for deployment", "User-uploaded originals only", "A URL namespace", "A quiz answer store"], "Collected static files for deployment", "collectstatic gathers assets there for serving.", lesson=5),
            _q("Which tag builds a static asset URL?", ["{% static %}", "{% asset_url_now %}", "{% media_only %}", "{% css %}"], "{% static %}", "The static tag uses the configured static URL/storage.", lesson=5),
            _q("What should user uploads use?", ["A separate media storage policy", "The trusted static source directory", "STATIC_ROOT as code", "The template loader"], "A separate media storage policy", "Uploads are different from versioned application assets.", "intermediate", 5),
            _q("True or false: runserver is a production static hosting solution.", ["True", "False"], "False", "Use a production web server or storage backend.", lesson=5),
            _q("Why namespace app assets?", ["To avoid filename collisions", "To disable CSS", "To publish secrets", "To create migrations"], "To avoid filename collisions", "App namespaces keep asset paths predictable.", lesson=5),
            _q("Which command gathers static assets?", ["python manage.py collectstatic", "python manage.py collectmediaonly", "python manage.py staticapp", "python manage.py gathercss"], "python manage.py collectstatic", "collectstatic prepares the deployment collection.", lesson=5),
            _q("What belongs on an image tag for accessibility?", ["Meaningful alt text when the image conveys information", "A password", "A database ID only", "No attributes ever"], "Meaningful alt text when the image conveys information", "Alternative text communicates image purpose.", "intermediate", 5),
        ],
    },
    {
        "title": "Reusable Templates, Partials and Components",
        "slug": "04-reusable-templates-partials-and-components",
        "topic": "include, with, only, shared navigation, cards, empty states, context isolation, and component accessibility",
        "description": "Extract repeated UI into focused template partials that remain predictable and accessible.",
        "description_mm": "ထပ်ခါထပ်ခါသုံးရသော UI ကို ခန့်မှန်းရလွယ်ပြီး accessible ဖြစ်သော template partial များအဖြစ် ခွဲထုတ်ပါ။",
        "syntax": "{% include \"components/card.html\" with item=item only %}",
        "theory": "The include tag composes a page from reusable template fragments. Passing explicit context with include makes a partial's contract visible; include ... only prevents accidental access to unrelated parent context. Traditional includes work across supported Django versions and are a dependable starting point for navigation, footer, cards, alerts, and empty states. A partial should have a narrow input contract, semantic markup, accessible labels, and no hidden database query. Reuse reduces drift, but over-generalizing every visual detail can make templates harder to read. Prefer a small number of purposeful components.",
        "theory_mm": "include tag သည် page ကို reusable template fragment များဖြင့် ပေါင်းစပ်သည်။ include နှင့် explicit context ပေးခြင်းက partial contract ကို ရှင်းလင်းစေပြီး include ... only သည် မသက်ဆိုင်သော parent context ကို မမြင်စေပါ။ Traditional include သည် Django version များအကြား သုံးနိုင်ပြီး navigation၊ footer၊ card၊ alert နှင့် empty state အတွက် သင့်တော်သည်။ Partial တစ်ခုတွင် input contract သေးငယ်၊ semantic markup၊ accessible label ရှိရမည်။ Hidden database query မလုပ်ပါနှင့်။ Reuse သည် drift လျော့စေသော်လည်း visual detail အားလုံးကို generalize လုပ်လွန်းလျှင် ဖတ်ရခက်နိုင်သည်။ ရည်ရွယ်ချက်ရှိသော component အနည်းငယ်ကိုသာ သုံးပါ။",
        "concepts": "include, explicit context, only context isolation, component contracts, card partials, navigation, empty state, accessibility, and rendered-fragment tests.",
        "concepts_mm": "include၊ explicit context၊ only ဖြင့် context isolation၊ component contract၊ card partial၊ navigation၊ empty state၊ accessibility နှင့် fragment test တို့ကို လေ့လာရမည်။",
        "mistakes": ["Including a partial without documenting required variables.", "Relying on accidental parent context.", "Putting a full page title or main landmark inside a card partial.", "Creating a component that hides a query or permission check."],
        "mistakes_mm": ["Partial လိုအပ်သော variable များကို မသတ်မှတ်ဘဲ include လုပ်ခြင်း။", "Parent context ကို မရည်ရွယ်ဘဲ မှီခိုခြင်း။", "Card partial ထဲ full page title/main landmark ထည့်ခြင်း။", "Query/permission check ကို component အတွင်းဖုံးကွယ်ခြင်း။"],
        "best_practices": "Give every partial a small contract, use include ... with ... only when isolation matters, keep cards composable, and test rendered fragments with realistic context.",
        "best_practices_mm": "Partial တစ်ခုစီတွင် contract သေးငယ်ထားပါ၊ isolation လိုလျှင် include ... with ... only သုံးပါ၊ card ကို composable ထားပြီး realistic context ဖြင့် rendered fragment test လုပ်ပါ။",
        "examples": [
            _example("Shared header partial", {"templates/components/navbar.html": "<nav aria-label=\"Primary navigation\"><a href=\"{% url 'home' %}\">Home</a><a href=\"{% url 'students:list' %}\">Students</a><a href=\"{% url 'courses:list' %}\">Courses</a></nav>", "templates/base.html": "{% include \"components/navbar.html\" %}"}, "The base template renders all routes", "One accessible nav is shared by every page", "Keep only navigation markup in the partial and place route ownership in named URLs.", "Partial ထဲတွင် navigation markup သာထားပြီး route ကို named URL ဖြင့် ချိတ်ပါ။"),
            _example("Reusable footer", {"templates/components/footer.html": "<footer><p>&copy; {{ year }} Learn-Coding</p></footer>", "templates/base.html": "{% include \"components/footer.html\" with year=current_year only %}"}, "current_year=2026 in base context", "Footer displays the current year without reading unrelated context", "Explicit with plus only documents and isolates the partial contract.", "with နှင့် only သည် partial contract ကို ရှင်းလင်းပြီး context isolate လုပ်သည်။"),
            _example("Student card partial", {"templates/components/student_card.html": "<article class=\"student-card\"><h2>{{ student.name }}</h2><p>{{ student.course }}</p><a href=\"{% url 'students:detail' student.id %}\">View profile<span class=\"sr-only\"> for {{ student.name }}</span></a></article>", "templates/students/list.html": "{% for student in students %}{% include \"components/student_card.html\" with student=student only %}{% empty %}{% include \"components/empty_state.html\" with message=\"No students yet.\" only %}{% endfor %}"}, "A student dictionary per loop", "Each card has a heading, course, and accessible detail link", "The list owns iteration; the card owns one student's presentation.", "List က loop ကိုပိုင်ပြီး card က student တစ်ယောက်၏ presentation ကိုပိုင်သည်။"),
            _example("Course card and empty state", {"templates/components/course_card.html": "<article class=\"course-card\"><h2>{{ course.title }}</h2><p>{{ course.summary }}</p><a href=\"{% url 'courses:detail' course.slug %}\">Open course</a></article>", "templates/components/empty_state.html": "<div class=\"empty-state\" role=\"status\"><p>{{ message }}</p></div>", "templates/courses/list.html": "{% for course in courses %}{% include \"components/course_card.html\" with course=course only %}{% empty %}{% include \"components/empty_state.html\" with message=\"No courses yet.\" only %}{% endfor %}"}, "courses is populated or empty", "Cards render for data and a status message renders for no data", "Keep empty state wording explicit and treat it as a tested UI state.", "Empty state စာသားကို ရှင်းလင်းစွာထားပြီး test လုပ်ရမည့် UI state အဖြစ် သတ်မှတ်ပါ။"),
        ],
        "exercises": "Extract a navbar, footer, student card, course card, and empty state from a duplicated page. Make each include pass explicit context and add tests for populated and empty lists.",
        "exercises_mm": "ထပ်နေသော page markup မှ navbar၊ footer၊ student card၊ course card နှင့် empty state ခွဲထုတ်ပါ။ Include တစ်ခုစီကို explicit context ပေးပြီး populated/empty list test ရေးပါ။",
        "homework": "Refactor the Student Portal into reusable components. For each component document required variables, semantic role, keyboard behavior, and one failure/empty state.",
        "homework_mm": "Student Portal ကို reusable component များအဖြစ် refactor လုပ်ပါ။ Component တစ်ခုစီ၏ required variable၊ semantic role၊ keyboard behavior နှင့် failure/empty state တစ်ခုစီ မှတ်တမ်းတင်ပါ။",
        "summary": "Partials are small presentation components with explicit context contracts; include ... only helps prevent accidental coupling.",
        "summary_mm": "Partial သည် explicit context contract ပါသော presentation component သေးငယ်တစ်ခုဖြစ်ပြီး include ... only သည် မရည်ရွယ်သော coupling ကို ကာကွယ်သည်။",
        "quiz": [
            _q("What does include do?", ["Composes a template from a reusable fragment", "Runs a migration", "Creates a CSS file", "Authorizes a user"], "Composes a template from a reusable fragment", "It renders another template at that point.", lesson=6),
            _q("Why use include ... only?", ["To isolate a partial from unrelated parent context", "To disable escaping", "To create a route", "To load a database"], "To isolate a partial from unrelated parent context", "Only makes the input contract more explicit.", "intermediate", 6),
            _q("What should a card partial receive?", ["A small explicit item contract", "The entire database", "A password", "Every request header"], "A small explicit item contract", "Small contracts keep components predictable.", lesson=6),
            _q("True or false: a partial should hide a permission query.", ["True", "False"], "False", "Permission decisions belong in backend policy boundaries.", "intermediate", 6),
            _q("What should an empty state communicate?", ["Why there is no content and what the user can do next", "A secret token", "A fake success", "Only whitespace"], "Why there is no content and what the user can do next", "An empty list is a real UI state.", lesson=6),
            _q("Which component should own loop iteration?", ["The parent list template", "Every card's hidden query", "CSS only", "The footer"], "The parent list template", "The card renders one item; the parent controls the collection.", lesson=6),
            _q("Why use semantic headings in cards?", ["They provide a useful document hierarchy", "They disable JavaScript", "They create migrations", "They hide links"], "They provide a useful document hierarchy", "Headings help scanning and assistive technologies.", "intermediate", 6),
            _q("What is a useful partial test?", ["Render it through a real page with realistic context", "Check only its filename", "Disable autoescape", "Skip empty data"], "Render it through a real page with realistic context", "Rendered behavior validates the contract.", lesson=6),
        ],
    },
    {
        "title": "HTML, CSS, JavaScript and Responsive Django UI",
        "slug": "04-html-css-javascript-and-responsive-django-ui",
        "topic": "semantic HTML, CSS Grid/Flexbox, mobile-first design, media queries, focus states, forms, CSRF, and UI testing",
        "description": "Assemble a semantic, responsive Student Portal interface with safe Django forms and accessible interactions.",
        "description_mm": "Safe Django form နှင့် accessible interaction များပါသော semantic responsive Student Portal interface တည်ဆောက်ပါ။",
        "syntax": "<form method=\"post\">{% csrf_token %}... </form>\n.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }",
        "theory": "Frontend integration begins with semantic HTML and a clear content hierarchy. Flexbox is useful for one-dimensional alignment such as a navbar; CSS Grid is useful for two-dimensional card layouts. Mobile-first CSS starts with a readable single-column layout and adds media queries for wider screens. Controls need visible focus states, labels, keyboard operation, sufficient color contrast, and touch-friendly sizes. A POST form that changes server state must include CSRF protection; validation still happens server-side even when JavaScript adds client-side feedback. JavaScript should enhance navigation and feedback without making content inaccessible when it is unavailable. Never render untrusted HTML as trusted markup.",
        "theory_mm": "Frontend integration သည် semantic HTML နှင့် content hierarchy ရှင်းလင်းမှုမှ စတင်သည်။ Flexbox သည် navbar ကဲ့သို့ one-dimensional alignment အတွက်ကောင်းပြီး CSS Grid သည် card layout ကဲ့သို့ two-dimensional layout အတွက်ကောင်းသည်။ Mobile-first CSS သည် single-column readable layout မှစပြီး screen ကျယ်လာလျှင် media query ထည့်သည်။ Control များတွင် မြင်သာသော focus state၊ label၊ keyboard operation၊ လုံလောက်သော contrast နှင့် touch-friendly size ရှိရမည်။ Server state ပြောင်းသော POST form တွင် CSRF ကာကွယ်မှု ပါရမည်။ JavaScript က feedback ထည့်ပေးသော်လည်း JavaScript မရှိချိန် content မသုံးမရ မဖြစ်စေပါနှင့်။ Untrusted HTML ကို trusted markup အဖြစ် မrender လုပ်ပါနှင့်။",
        "concepts": "Semantic landmarks, mobile-first CSS, Flexbox, Grid, media queries, responsive cards, accessible navigation, CSRF, server validation, progressive enhancement, and keyboard testing.",
        "concepts_mm": "Semantic landmark၊ mobile-first CSS၊ Flexbox၊ Grid၊ media query၊ responsive card၊ accessible navigation၊ CSRF၊ server validation၊ progressive enhancement နှင့် keyboard test တို့ကို လေ့လာရမည်။",
        "mistakes": ["Using divs for every control without semantics.", "Removing outline without adding a visible focus replacement.", "Disabling CSRF to make a form submit.", "Assuming a desktop grid will fit a 320px viewport."],
        "mistakes_mm": ["Control အားလုံးကို semantic မပါဘဲ div သုံးခြင်း။", "Visible focus အစားထိုးမထည့်ဘဲ outline ဖယ်ခြင်း။", "Form submit အောင်ရန် CSRF ပိတ်ခြင်း။", "Desktop grid သည် 320px viewport တွင် အလိုအလျောက် fit ဖြစ်မည်ဟု ယူဆခြင်း။"],
        "best_practices": "Start mobile-first, use Grid and Flexbox for their strengths, preserve keyboard focus, label controls, keep server validation authoritative, and test at representative widths.",
        "best_practices_mm": "Mobile-first စပါ၊ Grid/Flexbox ကို သင့်တော်သလိုသုံးပါ၊ keyboard focus ထိန်းပါ၊ control label ပေးပါ၊ server validation ကို အဓိကထားပြီး width အမျိုးမျိုးတွင် test လုပ်ပါ။",
        "examples": [
            _example("Responsive header", {"templates/components/navbar.html": "<header class=\"site-header\"><a class=\"brand\" href=\"{% url 'home' %}\">Learn-Coding</a><button type=\"button\" data-menu-toggle aria-expanded=\"false\" aria-controls=\"primary-menu\">Menu</button><nav id=\"primary-menu\" data-menu aria-label=\"Primary\" hidden><a href=\"{% url 'students:list' %}\">Students</a><a href=\"{% url 'courses:list' %}\">Courses</a></nav></header>", "static/css/main.css": ".site-header { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }\n.site-header nav { display: flex; gap: 1rem; }\n@media (min-width: 48rem) { .site-header button { display: none; } .site-header nav { display: flex !important; } }", "static/js/main.js": "document.addEventListener('DOMContentLoaded', () => {\n  const button = document.querySelector('[data-menu-toggle]');\n  const menu = document.querySelector('[data-menu]');\n  if (!button || !menu) return;\n  button.addEventListener('click', () => {\n    const isOpen = button.getAttribute('aria-expanded') === 'true';\n    button.setAttribute('aria-expanded', String(!isOpen));\n    menu.hidden = isOpen;\n  });\n});"}, "320px to 1440px viewport", "A keyboard-accessible menu works on narrow screens and the nav is visible on wider screens", "Use a real button, aria-expanded, hidden, focus styles, and a media query that progressively shows the desktop nav.", "Real button၊ aria-expanded၊ hidden၊ focus style နှင့် media query သုံးပါ။"),
            _example("Student card grid", {"templates/students/list.html": "<section class=\"card-grid\" aria-labelledby=\"students-title\"><h1 id=\"students-title\">Students</h1>{% for student in students %}<article class=\"student-card\"><h2>{{ student.name }}</h2><p>{{ student.course }}</p></article>{% empty %}<p role=\"status\">No students yet.</p>{% endfor %}</section>", "static/css/main.css": ".card-grid { display: grid; gap: 1rem; grid-template-columns: 1fr; }\n@media (min-width: 40rem) { .card-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }\n@media (min-width: 64rem) { .card-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }"}, "Students list with 0 or more records", "One column at mobile, two at tablet, three at desktop without horizontal overflow", "Start with one column, use minmax(0, 1fr), and verify long names wrap.", "One column ဖြင့်စပြီး minmax(0, 1fr) သုံးကာ long name wrap ဖြစ်ကြောင်း စစ်ပါ။"),
            _example("Course listing layout", {"templates/courses/list.html": "<main><h1>Courses</h1><div class=\"course-grid\">{% for course in courses %}<article class=\"course-card\"><h2>{{ course.title }}</h2><p>{{ course.summary }}</p><a class=\"button\" href=\"{% url 'courses:detail' course.slug %}\">Open course</a></article>{% empty %}<p role=\"status\">No courses are available.</p>{% endfor %}</div></main>", "static/css/main.css": ".course-grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr)); }\n.button:focus-visible, a:focus-visible, button:focus-visible { outline: 3px solid #7c5cff; outline-offset: 3px; }"}, "Course records with long descriptions", "Cards fit their container and links have a visible keyboard outline", "Use a flexible minimum, avoid fixed widths, and keep focus-visible styles visible.", "Flexible minimum သုံးပြီး fixed width ရှောင်ကာ focus-visible style ကို ထိန်းပါ။"),
            _example("Safe POST form", {"templates/students/form.html": "<form method=\"post\" novalidate>{% csrf_token %}<label for=\"student-name\">Name</label><input id=\"student-name\" name=\"name\" required maxlength=\"120\"><button type=\"submit\">Save student</button></form>", "students/views.py": "from django.shortcuts import render\n\ndef create_student(request):\n    if request.method == \"POST\":\n        name = request.POST.get(\"name\", \"\").strip()\n        if not name:\n            return render(request, \"students/form.html\", {\"error\": \"Name is required.\"}, status=400)\n        return redirect(\"students:list\")\n    return render(request, \"students/form.html\")"}, "POST with a missing or valid name", "Missing input returns a 400 form with an error; valid input redirects", "Keep CSRF, validate on the server, use labels, and never trust client-only required attributes.", "CSRF မပိတ်ဘဲ server တွင် validate လုပ်ပြီး label သုံးပါ။ Client-only required ကို မယုံပါနှင့်။"),
        ],
        "exercises": "Build a responsive header, student card grid, course grid, and CSRF-protected form. Test at 320, 375, 430, 768, 1024, and 1440px; keyboard through every control and record overflow/focus findings.",
        "exercises_mm": "Responsive header၊ student card grid၊ course grid နှင့် CSRF-protected form တည်ဆောက်ပါ။ 320၊ 375၊ 430၊ 768၊ 1024 နှင့် 1440px တွင် test လုပ်ပြီး control အားလုံးကို keyboard ဖြင့်စမ်းကာ overflow/focus finding မှတ်ပါ။",
        "homework": "Build the complete responsive Student Portal frontend with shared navigation/footer, home, students list/detail, courses list/detail, CSS, JavaScript menu, empty states, named routes, 404 handling, and an accessibility checklist.",
        "homework_mm": "Shared navigation/footer၊ home၊ students list/detail၊ courses list/detail၊ CSS၊ JavaScript menu၊ empty state၊ named route၊ 404 handling နှင့် accessibility checklist ပါသော responsive Student Portal frontend ပြီးစီးအောင် တည်ဆောက်ပါ။",
        "summary": "A professional Django frontend combines semantic HTML, mobile-first CSS, progressive JavaScript, safe forms, and honest responsive testing.",
        "summary_mm": "Professional Django frontend သည် semantic HTML၊ mobile-first CSS၊ progressive JavaScript၊ safe form နှင့် အမှန်တကယ် responsive testing ကို ပေါင်းစပ်ထားသည်။",
        "quiz": [
            _q("Which layout tool is well suited to a two-dimensional card grid?", ["CSS Grid", "Only inline text", "A migration", "Http404"], "CSS Grid", "Grid handles rows and columns effectively.", lesson=7),
            _q("What does mobile-first mean?", ["Start with a usable narrow layout, then enhance wider screens", "Build desktop only", "Hide all mobile content", "Disable media queries"], "Start with a usable narrow layout, then enhance wider screens", "The base styles serve small screens first.", lesson=7),
            _q("What must a state-changing browser form include?", ["CSRF protection and server-side validation", "Only JavaScript", "A hidden password in the URL", "No method"], "CSRF protection and server-side validation", "Browser forms need CSRF and the server remains authoritative.", "intermediate", 7),
            _q("Which selector state helps keyboard users see focus?", [":focus-visible", ":secret", ":database", ":hidden-focus"], ":focus-visible", "A visible focus indicator is essential for keyboard navigation.", lesson=7),
            _q("True or false: client-side required attributes replace server validation.", ["True", "False"], "False", "Client checks improve feedback but are not a trust boundary.", "intermediate", 7),
            _q("What should a responsive grid avoid?", ["Fixed widths that cause horizontal overflow", "Wrapping text", "minmax", "Media queries"], "Fixed widths that cause horizontal overflow", "Flexible columns adapt to the viewport.", lesson=7),
            _q("What is progressive enhancement?", ["Core content works before optional JavaScript enhancements", "Only JavaScript can render content", "Disable semantic HTML", "Put queries in CSS"], "Core content works before optional JavaScript enhancements", "Enhancement should not make the page unusable.", "intermediate", 7),
            _q("What should untrusted HTML be?", ["Escaped or safely handled, not blindly marked safe", "Always marked safe", "Placed in CSS", "Used as a script"], "Escaped or safely handled, not blindly marked safe", "Unsafe HTML can create XSS.", "intermediate", 7),
        ],
    },
]


def _render_en(item: dict) -> str:
    examples = []
    for index, example in enumerate(item["examples"], 1):
        files = []
        for filename, source in example["files"].items():
            language = "html" if filename.endswith(".html") else "css" if filename.endswith(".css") else "javascript" if filename.endswith(".js") else "text" if filename.endswith(".txt") or filename.endswith(".png") else "python"
            files.append(f"File: {filename}\n```{language}\n{source}\n```")
        examples.append(f"Example {index}: {example['title']}\nSetup/input: {example['input']}\n" + "\n\n".join(files) + f"\nExpected browser behavior: {example['output']}\nStep-by-step explanation: {example['steps']}\nVerify the route, rendered HTML, asset request, and keyboard behavior where relevant.")
    mistakes = "\n".join(f"- {value}" for value in item["mistakes"])
    quiz = "\n".join(f"{i}. {q['prompt']} Options: {', '.join(q['options'])}" for i, q in enumerate(item["quiz"], 1))
    example_text = "\n\n".join(examples)
    return dedent(f"""
        # {item['title']}

        ## Introduction
        {item['description']}

        ## Prerequisites
        Complete Django Modules 01–03, know Python functions and dictionaries, and be able to run a project in an isolated virtual environment. Use the supported Django version for every framework example.

        ## Learning objectives
        1. Explain {item['topic']}.
        2. Identify the file, context, route, or asset boundary involved.
        3. Implement the pattern with complete Django/Python/frontend code.
        4. Test normal, empty, missing, unsafe-input, and responsive behavior.

        ## Detailed theory
        {item['theory']}

        ## Concept explanations
        {item['concepts']}

        ## Syntax/API references
        ```django
        {item['syntax']}
        ```
        Treat every template variable, tag, filter, setting, and asset path as a contract. The view prepares data; the template presents it; the browser enhances it; the server remains the security authority.

        ## Complete guided examples
        {example_text}

        ## Common mistakes
        {mistakes}

        ## Best practices
        {item['best_practices']}

        ## Guided exercises
        {item['exercises']}

        ## Independent exercises
        Rebuild the exercise from an empty app without copying the example. Add one populated case, one empty/missing case, one invalid-input case where applicable, and one focused test. Record the actual command and output.

        ## Homework
        {item['homework']}

        ## Lesson quiz
        {quiz}
        Answer first, then verify with a focused test or browser inspection. Review answer keys are stored privately and are not part of student payloads.

        ## Summary
        {item['summary']}

        ## Further reading
        Read the official Django template language, built-in tags and filters, and static files documentation. Compare the documented behavior with your rendered HTML and tests.
    """).strip()


def _render_mm(item: dict) -> str:
    examples = []
    for index, example in enumerate(item["examples"], 1):
        files = []
        for filename, source in example["files"].items():
            language = "html" if filename.endswith(".html") else "css" if filename.endswith(".css") else "javascript" if filename.endswith(".js") else "text" if filename.endswith(".txt") or filename.endswith(".png") else "python"
            files.append(f"File: {filename}\n```{language}\n{source}\n```")
        examples.append(f"နမူနာ {index}: {example['title']}\nSetup/Input: {example['input']}\n" + "\n\n".join(files) + f"\nမျှော်မှန်း browser behavior: {example['output']}\nအဆင့်လိုက်ရှင်းလင်းချက်: {example['steps_mm']}\nသက်ဆိုင်ရာ route၊ rendered HTML၊ asset request နှင့် keyboard behavior ကို စစ်ပါ။")
    mistakes = "\n".join(f"- {value}" for value in item["mistakes_mm"])
    quiz = "\n".join(f"{i}. {q['prompt']} Options: {', '.join(q['options'])}" for i, q in enumerate(item["quiz"], 1))
    example_text = "\n\n".join(examples)
    return dedent(f"""
        # {item['title']}

        ## မိတ်ဆက်
        {item['description_mm']}

        ## ကြိုတင်လိုအပ်ချက်
        Django Module 01–03 ပြီးထားရမည်။ Python function/dictionary ကို သိပြီး isolated virtual environment တွင် project run နိုင်ရမည်။ Framework example အားလုံးကို supported Django version ဖြင့် run ပါ။

        ## သင်ယူရမည့်ရည်မှန်းချက်
        ၁။ {item['topic']} ကို ရှင်းပြနိုင်ရန်။
        ၂။ ပါဝင်သော file၊ context၊ route သို့မဟုတ် asset boundary ကို ခွဲခြားနိုင်ရန်။
        ၃။ Complete Django/Python/frontend code ဖြင့် pattern ကို တည်ဆောက်နိုင်ရန်။
        ၄။ Normal၊ empty၊ missing၊ unsafe-input နှင့် responsive behavior ကို test လုပ်နိုင်ရန်။

        ## အသေးစိတ်သီအိုရီ
        {item['theory_mm']}

        ## Concept ရှင်းလင်းချက်
        {item['concepts_mm']}

        ## Syntax/API reference
        ```django
        {item['syntax']}
        ```
        Template variable၊ tag၊ filter၊ setting နှင့် asset path တစ်ခုစီကို contract အဖြစ် စဉ်းစားပါ။ View က data ပြင်ဆင်၊ template က presentation လုပ်၊ browser က enhancement လုပ်သော်လည်း security authority သည် server ဖြစ်သည်။

        ## လမ်းညွှန်နမူနာများ
        {example_text}

        ## အများဆုံးမှားတတ်သောအချက်များ
        {mistakes}

        ## အကောင်းဆုံးနည်းလမ်းများ
        {item['best_practices_mm']}

        ## လမ်းညွှန်လေ့ကျင့်ခန်း
        {item['exercises_mm']}

        ## ကိုယ်တိုင်လေ့ကျင့်ရန်
        Empty app မှ exercise ကို ကိုယ်တိုင်ပြန်တည်ဆောက်ပါ။ Populated case၊ empty/missing case၊ လိုအပ်လျှင် invalid-input case နှင့် focused test တစ်ခုစီ ထည့်ပါ။ Run command နှင့် အမှန်တကယ် output ကို မှတ်တမ်းတင်ပါ။

        ## အိမ်စာ
        {item['homework_mm']}

        ## Lesson quiz
        {quiz}
        အရင်ကိုယ်တိုင်ဖြေပြီး focused test သို့မဟုတ် browser inspection ဖြင့် စစ်ဆေးပါ။ Answer key သည် private review data ထဲတွင်သာရှိပြီး student payload ထဲမပါပါ။

        ## အနှစ်ချုပ်
        {item['summary_mm']}

        ## ဆက်လက်ဖတ်ရှုရန်
        Django template language၊ built-in tag/filter နှင့် static files official documentation ကို ဖတ်ပါ။ Document behavior ကို rendered HTML နှင့် test ရလဒ်နှင့် နှိုင်းယှဉ်ပါ။
    """).strip()


def _example_code(example):
    return "\n\n".join(f"# --- {filename} ---\n{source}" for filename, source in example["files"].items())


def _ensure_examples(db, lesson, item):
    rows = db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all()
    for position, example in enumerate(item["examples"], 1):
        values = {"title": example["title"], "language": "django", "filename": next(iter(example["files"])), "code": _example_code(example), "description": f"Setup/input: {example['input']}\nExpected behavior: {example['output']}\n\n{example['steps']}", "position": position}
        if position <= len(rows):
            for key, value in values.items():
                setattr(rows[position - 1], key, value)
        else:
            db.add(CodeExample(lesson_id=lesson.id, **values))


def _ensure_quiz(db, lesson, item):
    quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
    if not quiz:
        quiz = LessonQuiz(lesson_id=lesson.id, title=f"{item['title']} knowledge check", explanation="Review the rendered behavior and explain the boundary behind each answer.", status="draft")
        db.add(quiz)
        db.flush()
    quiz.title = f"{item['title']} knowledge check"
    quiz.explanation = "Review the rendered behavior and explain the boundary behind each answer."
    if quiz.status not in {"published", "approved", "in_review"}:
        quiz.status = "draft"
    questions = db.scalars(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id).order_by(QuizQuestion.position)).all()
    for position, data in enumerate(item["quiz"], 1):
        values = {"prompt": data["prompt"], "question_type": "true_false" if data["options"] == ["True", "False"] else "multiple_choice", "options_json": json.dumps(data["options"], ensure_ascii=False), "correct_answer": data["correct_answer"], "explanation": data["explanation"]}
        if position <= len(questions):
            for key, value in values.items():
                setattr(questions[position - 1], key, value)
        else:
            db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))


def _ensure_exercise(db, lesson, item):
    exercise = db.scalar(select(CodingExercise).where(CodingExercise.lesson_id == lesson.id).order_by(CodingExercise.created_at, CodingExercise.id))
    values = {"title": f"{item['title']} practice", "description_en": item["exercises"], "description_mm": item["exercises_mm"], "difficulty": "intermediate", "language": "django", "starter_code": "# Build the exercise in the isolated Student Portal project.\n", "status": "draft"}
    if exercise:
        for key, value in values.items():
            setattr(exercise, key, value)
    else:
        db.add(CodingExercise(lesson_id=lesson.id, slug=f"django-templates-{lesson.order_index}-practice", **values))


def _module_assessment(lesson_ids=None):
    questions = [
        _q("Which setting key helps Django find project-level templates?", ["DIRS", "STATIC_ROOT", "MEDIA_URL", "ALLOWED_HOSTS"], "DIRS", "DIRS lists template search directories.", lesson=1),
        _q("What does render() produce?", ["An HttpResponse from a template and context", "A CSS bundle", "A migration", "A password"], "An HttpResponse from a template and context", "render connects the view, template, and context.", lesson=1),
        _q("Which notation reads a dictionary value in a template?", ["{{ student.name }}", "{{ student['name'] }} only", "{{ student->name }}", "{{ student::name }}"], "{{ student.name }}", "Django template lookup uses dot notation.", lesson=2),
        _q("What security boundary does autoescaping support?", ["XSS prevention for untrusted text", "Database indexing", "URL ordering", "Static collection"], "XSS prevention for untrusted text", "Escaping prevents text from becoming markup.", "intermediate", 2),
        _q("Which tag handles a no-items loop state?", ["{% empty %}", "{% noitems %}", "{% fallback %}", "{% zero %}"], "{% empty %}", "empty provides intentional no-data output.", lesson=3),
        _q("What should a custom filter avoid?", ["Hidden queries and authorization decisions", "Formatting a string", "A registered function", "A small pure transformation"], "Hidden queries and authorization decisions", "Business rules belong in Python boundaries.", "intermediate", 3),
        _q("What must a child template do first?", ["Use {% extends %} as its first template tag", "Load a database", "Disable autoescape", "Call collectstatic"], "Use {% extends %} as its first template tag", "Django inheritance follows this syntax contract.", lesson=4),
        _q("What does block.super preserve?", ["Parent block content", "A URL parameter", "A CSS cache", "A quiz answer"], "Parent block content", "It lets a child add to the parent block.", lesson=4),
        _q("Which tag creates a static asset URL?", ["{% static %}", "{% asset %}", "{% media_static %}", "{% css %}"], "{% static %}", "The static tag uses configured static storage/URL.", lesson=5),
        _q("What is the difference between static and media?", ["Static is versioned app assets; media is user-uploaded content", "They are always the same", "Media is CSS only", "Static is passwords"], "Static is versioned app assets; media is user-uploaded content", "They need separate storage and trust policies.", "intermediate", 5),
        _q("Why use include ... only?", ["To isolate a partial's context", "To disable escaping", "To create a model", "To publish a page"], "To isolate a partial's context", "It makes component input explicit.", "intermediate", 6),
        _q("What should an empty state do?", ["Explain that no data exists and guide the user", "Render blank space only", "Expose a secret", "Disable routes"], "Explain that no data exists and guide the user", "Empty data is a real UI state.", lesson=6),
        _q("Which tool fits a responsive two-dimensional card layout?", ["CSS Grid", "Only a database", "Http404", "A template quiz"], "CSS Grid", "Grid handles rows and columns.", lesson=7),
        _q("Which form protection belongs on a state-changing POST?", ["CSRF token plus server validation", "Only client JavaScript", "A URL password", "No method"], "CSRF token plus server validation", "The server is the trust boundary.", "intermediate", 7),
        _q("True or false: runserver is production static hosting.", ["True", "False"], "False", "Production needs a proper web server or storage backend.", lesson=5),
        _q("What is a visible keyboard focus state for?", ["Helping keyboard users locate the active control", "Making a migration", "Hiding links", "Loading media"], "Helping keyboard users locate the active control", "Focus visibility is an accessibility requirement.", lesson=7),
        _q("What should happen to user-provided HTML by default?", ["Escape or safely sanitize it; do not blindly mark it safe", "Always use |safe", "Put it in JavaScript", "Treat it as a template"], "Escape or safely sanitize it; do not blindly mark it safe", "Untrusted markup can cause XSS.", "intermediate", 2),
        _q("Which test best covers a responsive template feature?", ["Render real routes, inspect text/assets, and check representative viewport behavior", "Check only a filename", "Skip empty state", "Disable CSRF"], "Render real routes, inspect text/assets, and check representative viewport behavior", "The feature is observable in routes, HTML, assets, and widths.", "intermediate", 7),
    ]
    if lesson_ids:
        for question in questions:
            question["lesson_id"] = str(lesson_ids[question["lesson_position"]])
    return questions


def _project_source_files():
    return {
        "manage.py": dedent('''
            #!/usr/bin/env python
            import os
            import sys
            if __name__ == "__main__":
                os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_site.settings")
                from django.core.management import execute_from_command_line
                execute_from_command_line(sys.argv)
        ''').strip() + "\n",
        "school_site/__init__.py": "",
        "school_site/settings.py": dedent('''
            from pathlib import Path
            BASE_DIR = Path(__file__).resolve().parent.parent
            SECRET_KEY = "development-only-change-me"
            DEBUG = True
            ALLOWED_HOSTS = []
            ROOT_URLCONF = "school_site.urls"
            MIDDLEWARE = ["django.middleware.csrf.CsrfViewMiddleware"]
            INSTALLED_APPS = ["django.contrib.staticfiles", "students", "courses"]
            TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True, "OPTIONS": {"context_processors": []}}]
            STATIC_URL = "/static/"
            STATICFILES_DIRS = [BASE_DIR / "static"]
            STATIC_ROOT = BASE_DIR / "collected-static"
            DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
        ''').strip() + "\n",
        "school_site/urls.py": dedent('''
            from django.urls import include, path
            from django.views.generic import TemplateView
            urlpatterns = [
                path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
                path("students/", include("students.urls")),
                path("courses/", include("courses.urls")),
            ]
        ''').strip() + "\n",
        "school_site/asgi.py": "import os\nos.environ.setdefault(\"DJANGO_SETTINGS_MODULE\", \"school_site.settings\")\nfrom django.core.asgi import get_asgi_application\napplication = get_asgi_application()\n",
        "school_site/wsgi.py": "import os\nos.environ.setdefault(\"DJANGO_SETTINGS_MODULE\", \"school_site.settings\")\nfrom django.core.wsgi import get_wsgi_application\napplication = get_wsgi_application()\n",
        "students/__init__.py": "",
        "students/apps.py": "from django.apps import AppConfig\n\nclass StudentsConfig(AppConfig):\n    default_auto_field = \"django.db.models.BigAutoField\"\n    name = \"students\"\n",
        "students/urls.py": dedent('''
            from django.urls import path
            from . import views
            app_name = "students"
            urlpatterns = [
                path("", views.list_students, name="list"),
                path("<int:student_id>/", views.detail, name="detail"),
            ]
        ''').strip() + "\n",
        "students/views.py": dedent('''
            from django.http import Http404
            from django.shortcuts import render
            STUDENTS = [
                {"id": 1, "name": "John", "course": "Python", "bio": "Learning functions."},
                {"id": 2, "name": "Mary", "course": "Django", "bio": "Building web pages."},
            ]
            def list_students(request):
                return render(request, "students/list.html", {"students": STUDENTS})
            def detail(request, student_id):
                student = next((item for item in STUDENTS if item["id"] == student_id), None)
                if student is None:
                    raise Http404("Student not found")
                return render(request, "students/detail.html", {"student": student})
        ''').strip() + "\n",
        "students/templates/students/list.html": "{% extends \"base.html\" %}\n{% block title %}Students{% endblock %}\n{% block content %}<main><h1>Students</h1><div class=\"card-grid\">{% for student in students %}{% include \"components/student_card.html\" with student=student only %}{% empty %}{% include \"components/empty_state.html\" with message=\"No students yet.\" only %}{% endfor %}</div></main>{% endblock %}\n",
        "students/templates/students/detail.html": "{% extends \"base.html\" %}\n{% block title %}{{ student.name }}{% endblock %}\n{% block content %}<main><article><h1>{{ student.name }}</h1><p>{{ student.course }}</p><p>{{ student.bio|default:\"No biography yet.\" }}</p></article></main>{% endblock %}\n",
        "courses/__init__.py": "",
        "courses/apps.py": "from django.apps import AppConfig\n\nclass CoursesConfig(AppConfig):\n    default_auto_field = \"django.db.models.BigAutoField\"\n    name = \"courses\"\n",
        "courses/urls.py": "from django.urls import path\nfrom . import views\napp_name = \"courses\"\nurlpatterns = [path(\"\", views.list_courses, name=\"list\"), path(\"<slug:slug>/\", views.detail, name=\"detail\")]\n",
        "courses/views.py": dedent('''
            from django.http import Http404
            from django.shortcuts import render
            COURSES = [
                {"slug": "python", "title": "Python", "summary": "Build useful programs."},
                {"slug": "django", "title": "Django", "summary": "Build maintainable web apps."},
            ]
            def list_courses(request):
                return render(request, "courses/list.html", {"courses": COURSES})
            def detail(request, slug):
                course = next((item for item in COURSES if item["slug"] == slug), None)
                if course is None:
                    raise Http404("Course not found")
                return render(request, "courses/detail.html", {"course": course})
        ''').strip() + "\n",
        "courses/templates/courses/list.html": "{% extends \"base.html\" %}\n{% block title %}Courses{% endblock %}\n{% block content %}<main><h1>Courses</h1><div class=\"card-grid\">{% for course in courses %}{% include \"components/course_card.html\" with course=course only %}{% empty %}{% include \"components/empty_state.html\" with message=\"No courses available.\" only %}{% endfor %}</div></main>{% endblock %}\n",
        "courses/templates/courses/detail.html": "{% extends \"base.html\" %}\n{% block title %}{{ course.title }}{% endblock %}\n{% block content %}<main><article><h1>{{ course.title }}</h1><p>{{ course.summary }}</p></article></main>{% endblock %}\n",
        "templates/base.html": "{% load static %}\n<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>{% block title %}Student Portal{% endblock %}</title><link rel=\"stylesheet\" href=\"{% static 'css/main.css' %}\"></head><body>{% include \"components/navbar.html\" %}<main id=\"main-content\">{% block content %}{% endblock %}</main>{% include \"components/footer.html\" %}<script src=\"{% static 'js/main.js' %}\" defer></script></body></html>\n",
        "templates/pages/home.html": "{% extends \"base.html\" %}\n{% block title %}Home | Student Portal{% endblock %}\n{% block content %}<section class=\"hero\"><p class=\"eyebrow\">Demo data only</p><h1>Responsive Django Student Portal</h1><p>Explore students and courses through reusable templates.</p></section>{% endblock %}\n",
        "templates/components/navbar.html": "<header class=\"site-header\"><a class=\"brand\" href=\"{% url 'home' %}\">Learn-Coding</a><button type=\"button\" data-menu-toggle aria-expanded=\"false\" aria-controls=\"primary-menu\">Menu</button><nav id=\"primary-menu\" data-menu aria-label=\"Primary navigation\" hidden><a href=\"{% url 'students:list' %}\">Students</a><a href=\"{% url 'courses:list' %}\">Courses</a></nav></header>\n",
        "templates/components/footer.html": "<footer><p>Demo project — sample records are stored in memory.</p></footer>\n",
        "templates/components/student_card.html": "<article class=\"card\"><h2>{{ student.name }}</h2><p>{{ student.course }}</p><a href=\"{% url 'students:detail' student.id %}\">View profile</a></article>\n",
        "templates/components/course_card.html": "<article class=\"card\"><h2>{{ course.title }}</h2><p>{{ course.summary }}</p><a href=\"{% url 'courses:detail' course.slug %}\">Open course</a></article>\n",
        "templates/components/empty_state.html": "<p class=\"empty-state\" role=\"status\">{{ message }}</p>\n",
        "students/static/students/images/student.svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 160 100\" role=\"img\" aria-labelledby=\"title\"><title id=\"title\">Student illustration</title><rect width=\"160\" height=\"100\" rx=\"16\" fill=\"#e8e5ff\"/><circle cx=\"80\" cy=\"38\" r=\"18\" fill=\"#7658ff\"/><path d=\"M40 88c6-24 22-34 40-34s34 10 40 34\" fill=\"#7658ff\"/></svg>\n",
        "static/css/main.css": ":root { font-family: system-ui, sans-serif; color: #172033; background: #f7f8fc; }\nbody { margin: 0; line-height: 1.5; }\n.site-header, main, footer { max-width: 72rem; margin-inline: auto; padding: 1rem; }\n.site-header { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }\n.site-header nav { display: flex; gap: 1rem; }\n.card-grid { display: grid; grid-template-columns: 1fr; gap: 1rem; }\n.card { padding: 1rem; background: white; border: 1px solid #dfe3ee; border-radius: .75rem; }\n:focus-visible { outline: 3px solid #7658ff; outline-offset: 3px; }\n@media (min-width: 40rem) { .card-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }\n@media (min-width: 64rem) { .card-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } .site-header button { display: none; } .site-header nav { display: flex !important; } }\n",
        "static/js/main.js": "document.addEventListener('DOMContentLoaded', () => {\n  const button = document.querySelector('[data-menu-toggle]');\n  const menu = document.querySelector('[data-menu]');\n  if (!button || !menu) return;\n  button.addEventListener('click', () => {\n    const isOpen = button.getAttribute('aria-expanded') === 'true';\n    button.setAttribute('aria-expanded', String(!isOpen));\n    menu.hidden = isOpen;\n  });\n});\n",
        "students/tests.py": "from django.test import SimpleTestCase\nfrom django.urls import reverse\n\nclass StudentPortalTests(SimpleTestCase):\n    def test_student_list_and_detail(self):\n        self.assertContains(self.client.get(reverse('students:list')), 'John')\n        self.assertEqual(self.client.get(reverse('students:detail', args=[1])).status_code, 200)\n        self.assertEqual(self.client.get(reverse('students:detail', args=[99])).status_code, 404)\n\n    def test_course_routes(self):\n        self.assertEqual(self.client.get(reverse('courses:list')).status_code, 200)\n        self.assertEqual(self.client.get(reverse('courses:detail', kwargs={'slug': 'django'})).status_code, 200)\n",
    }


def _ensure_project(db, course, module):
    slug = "django-responsive-student-portal"
    source_files = _project_source_files()
    brief = {
        "goal": "Build a multi-page responsive Django Student Portal using templates, reusable components, CSS, JavaScript, and in-memory sample records.",
        "scope": "Module 04 only. Demo records are in memory; persistent ORM/database models are intentionally deferred to the later ORM module.",
        "setup_commands": ["python -m venv .venv", "pip install Django", "python manage.py check", "python manage.py test", "python manage.py runserver"],
        "routes": ["/", "/students/", "/students/1/", "/courses/", "/courses/django/"],
        "responsive_viewports": [320, 360, 375, 390, 430, 768, 1024, 1440],
        "source_files": source_files,
        "expected_behavior": ["Shared base/navbar/footer render", "Students and courses list/detail pages render", "Missing IDs/slugs return 404", "Cards are one/two/three columns at mobile/tablet/desktop", "Menu button updates aria-expanded and hidden"],
        "troubleshooting": ["Run from the directory containing manage.py.", "Confirm templates/base.html is in TEMPLATES DIRS and app templates are namespaced.", "Use {% load static %} and inspect the asset request before changing STATIC_URL.", "The records are deliberately in memory and reset when the process restarts.", "Do not add PostgreSQL models in this module."],
        "review_checklist": ["No draft content is published automatically.", "Run route and template tests.", "Check keyboard focus and widths.", "Keep CSRF enabled for future POST forms.", "Do not mark untrusted HTML safe."],
    }
    project = db.scalar(select(ProjectTemplate).where(ProjectTemplate.slug == slug))
    values = {"title": "Responsive Django Student Portal", "description_en": "A multi-page Django frontend project with templates, inheritance, reusable components, static CSS/JavaScript, in-memory students/courses, responsive cards, accessible navigation, and tests.", "description_mm": "Template၊ inheritance၊ reusable component၊ static CSS/JavaScript၊ in-memory student/course၊ responsive card၊ accessible navigation နှင့် test ပါသော Django frontend project ဖြစ်သည်။", "difficulty": "intermediate", "estimated_hours": 14, "requirements": "Python 3, isolated environment, supported Django version, HTML/CSS basics, and Module 04 lessons.", "learning_outcomes": "Render pages, share layouts, use components, load assets, implement responsive CSS/JS, handle 404, and test HTML behavior.", "technology_stack": "Python | Django | Django Templates | HTML | CSS Grid | Flexbox | JavaScript", "prerequisites": "Complete Django Modules 01–03.", "architecture_overview": "school_site owns settings and root URLs; students and courses own views/routes/templates; project templates hold shared layout/components; static owns CSS and JS; sample records remain in memory.", "folder_structure": "\n".join(source_files.keys()), "testing_guide": "Run python manage.py check and python manage.py test, then inspect each route at the listed viewport widths with keyboard navigation.", "deployment_guide": "This is a learning frontend project. Do not deploy with DEBUG enabled and do not treat in-memory records as production persistence.", "tags_json": json.dumps(["django", "templates", "static-files", "responsive", "frontend", "student-portal"], ensure_ascii=False), "languages_json": json.dumps(["Python", "HTML", "CSS", "JavaScript"], ensure_ascii=False), "brief_json": json.dumps(brief, ensure_ascii=False), "status": "draft", "published": False}
    if not project:
        project = ProjectTemplate(slug=slug, **values)
        db.add(project)
        db.flush()
    elif not project.published and project.status not in {"published", "approved", "in_review"}:
        for key, value in values.items():
            setattr(project, key, value)
    link = db.scalar(select(ProjectCourseLink).where(ProjectCourseLink.project_id == project.id, ProjectCourseLink.course_id == course.id, ProjectCourseLink.module_id == module.id))
    if not link:
        db.add(ProjectCourseLink(project_id=project.id, course_id=course.id, module_id=module.id, position=1))
    milestones = [
        ("Template shell", "Configure templates, base.html, inheritance, and shared navigation.", "templates/base.html", "Home and child pages render one shared document shell."),
        ("Data and components", "Pass sample students/courses, create cards, empty states, and detail pages.", "students/views.py and templates/components/", "List, detail, and empty states render safely."),
        ("Assets and responsive UI", "Load CSS/JS/images, implement mobile-first Grid/Flexbox, and add menu behavior.", "static/css/main.css and static/js/main.js", "Widths 320–1440px have no intentional horizontal overflow."),
        ("Tests and accessibility review", "Run Django tests, inspect focus states, check 404 routes, and record viewport results.", "students/tests.py", "Tests pass and the review checklist is complete."),
    ]
    for position, (title, description, filename, output) in enumerate(milestones, 1):
        row = db.scalar(select(ProjectMilestone).where(ProjectMilestone.project_id == project.id, ProjectMilestone.position == position))
        data = {"title": title, "slug": f"responsive-portal-{position}", "description_en": description, "description_mm": description + " ကို လက်တွေ့တည်ဆောက်ပါ။", "content_en": f"Required boundary: {filename}\n\n{description}\n\nSample data is explicitly in memory for this module.", "content_mm": "ဤ milestone တွင် sample data ကို in-memory အဖြစ်သာထားပြီး frontend behavior ကို တည်ဆောက်ပါ။", "code": source_files.get(filename, "") if filename in source_files else "", "filename": filename, "expected_output": output, "line_explanation": "Read settings and URL ownership first, then template composition, then CSS/JS behavior, and finally the test that proves the route.", "completion_criteria": "The learner runs the command, records actual output, checks keyboard behavior, and documents one remaining limitation.", "resources_json": json.dumps([{"title": "Django templates", "url": "https://docs.djangoproject.com/en/stable/topics/templates/"}, {"title": "Django static files", "url": "https://docs.djangoproject.com/en/stable/howto/static-files/"}], ensure_ascii=False), "required": True}
        if not row:
            db.add(ProjectMilestone(project_id=project.id, position=position, **data))
        else:
            for key, value in data.items():
                setattr(row, key, value)
    requirement = db.scalar(select(ProjectRequirement).where(ProjectRequirement.project_id == project.id, ProjectRequirement.position == 1))
    req = {"title": "Complete responsive Student Portal frontend", "description": "Implement all routes, shared templates, components, static assets, responsive behavior, safe empty/404 states, and tests using in-memory demo records.", "acceptance_criteria": "All source files exist; check and tests pass; home/students/courses routes render; missing detail returns 404; static references use the static tag; no horizontal overflow is found at the required widths; keyboard focus remains visible; data is labeled as demo/in-memory.", "required": True}
    if not requirement:
        db.add(ProjectRequirement(project_id=project.id, position=1, **req))
    else:
        for key, value in req.items():
            setattr(requirement, key, value)
    rubric = [("Template architecture", "Inheritance, context, includes, and named routes are clear and reusable.", 25), ("Frontend behavior", "CSS, JavaScript, semantic HTML, responsive layout, and focus states work.", 25), ("Django behavior", "List/detail routes, safe context, 404, static references, and no database claim are correct.", 20), ("Tests", "Route, template, empty, 404, and accessibility-oriented checks are meaningful.", 20), ("Documentation", "Setup, outputs, troubleshooting, responsive widths, and scope are recorded.", 10)]
    for position, (name, description, weight) in enumerate(rubric, 1):
        criterion = db.scalar(select(ProjectRubricCriterion).where(ProjectRubricCriterion.project_id == project.id, ProjectRubricCriterion.position == position))
        if not criterion:
            db.add(ProjectRubricCriterion(project_id=project.id, position=position, name=name, description=description, weight=weight))
        else:
            criterion.name, criterion.description, criterion.weight = name, description, weight
    return project


SYNTAX_REFERENCES = [
    {"slug": "django-render", "title": "render()", "lesson": 1, "syntax": "render(request, template_name, context=None, content_type=None, status=None, using=None)", "description": "Loads a template with context and returns an HttpResponse.", "example": "return render(request, \"pages/home.html\", {\"title\": \"Home\"})", "output": "A rendered HTTP response", "mm": "Template နှင့် context ကို load လုပ်ပြီး HttpResponse ပြန်သည်။"},
    {"slug": "django-template-backend", "title": "DjangoTemplates backend", "lesson": 1, "syntax": "{\"BACKEND\": \"django.template.backends.django.DjangoTemplates\", \"DIRS\": [...], \"APP_DIRS\": True}", "description": "Configures Django template loading.", "example": "TEMPLATES = [{\"BACKEND\": \"django.template.backends.django.DjangoTemplates\", \"DIRS\": [BASE_DIR / \"templates\"], \"APP_DIRS\": True}]", "output": "Project and app templates can be discovered", "mm": "Django template loading ကို configure လုပ်သည်။"},
    {"slug": "django-template-context", "title": "Template context", "lesson": 1, "syntax": "{\"name\": value}", "description": "Maps names to values available during rendering.", "example": "context = {\"title\": \"Student Portal\"}", "output": "{{ title }} renders Student Portal", "mm": "Render အချိန်အသုံးပြုနိုင်သော name/value mapping ဖြစ်သည်။"},
    {"slug": "django-template-variable", "title": "Template variable lookup", "lesson": 2, "syntax": "{{ student.name }}", "description": "Displays dictionary keys, object attributes, and list indexes through dot lookup.", "example": "{{ student.contact.email }}", "output": "The nested email value is displayed", "mm": "Dot lookup ဖြင့် dictionary/object/list value ကို ပြသည်။"},
    {"slug": "django-if-elif-else", "title": "if, elif, else, endif", "lesson": 3, "syntax": "{% if condition %}...{% elif other %}...{% else %}...{% endif %}", "description": "Branches presentation based on prepared context values.", "example": "{% if student.active %}Active{% else %}On hold{% endif %}", "output": "The matching status is displayed", "mm": "Prepared context အပေါ်မူတည်၍ presentation branch လုပ်သည်။"},
    {"slug": "django-for-empty-endfor", "title": "for, empty, endfor", "lesson": 3, "syntax": "{% for item in items %}...{% empty %}...{% endfor %}", "description": "Loops over a collection and renders an explicit empty state.", "example": "{% for course in courses %}{{ course.title }}{% empty %}No courses{% endfor %}", "output": "Items or No courses", "mm": "Collection ကို loop လုပ်ပြီး empty state ပြသည်။"},
    {"slug": "django-url-tag", "title": "url tag", "lesson": 3, "syntax": "{% url 'namespace:name' arg %}", "description": "Reverses a named URL inside a template.", "example": "{% url 'students:detail' student.id %}", "output": "/students/1/", "mm": "Template ထဲတွင် named URL ကို reverse လုပ်သည်။"},
    {"slug": "django-with-tag", "title": "with tag", "lesson": 3, "syntax": "{% with total=students|length %}...{% endwith %}", "description": "Binds a temporary display value.", "example": "{% with count=courses|length %}{{ count }}{% endwith %}", "output": "The count is displayed", "mm": "ယာယီ display value bind လုပ်သည်။"},
    {"slug": "django-comment-tag", "title": "comment tag", "lesson": 3, "syntax": "{% comment \"reason\" %}...{% endcomment %}", "description": "Adds a template-only comment that is not rendered.", "example": "{% comment \"explain card\" %}internal note{% endcomment %}", "output": "The note is absent from HTML", "mm": "HTML ထဲမထွက်သော template comment ထည့်သည်။"},
    {"slug": "django-extends", "title": "extends tag", "lesson": 4, "syntax": "{% extends 'base.html' %}", "description": "Selects a parent template for inheritance.", "example": "{% extends \"base.html\" %}", "output": "Child uses the base skeleton", "mm": "Inheritance အတွက် parent template ရွေးသည်။"},
    {"slug": "django-block-endblock", "title": "block and endblock", "lesson": 4, "syntax": "{% block content %}...{% endblock %}", "description": "Defines a named replacement region.", "example": "{% block title %}Students{% endblock %}", "output": "The page title becomes Students", "mm": "Named replacement region သတ်မှတ်သည်။"},
    {"slug": "django-block-super", "title": "block.super", "lesson": 4, "syntax": "{{ block.super }}", "description": "Includes parent block content in a child override.", "example": "{% block header %}{{ block.super }}<span>Section</span>{% endblock %}", "output": "Parent header plus Section", "mm": "Child block ထဲ parent content ထည့်သည်။"},
    {"slug": "django-include", "title": "include tag", "lesson": 6, "syntax": "{% include 'components/card.html' with item=item only %}", "description": "Renders a reusable template fragment with explicit context.", "example": "{% include \"components/student_card.html\" with student=student only %}", "output": "One student card", "mm": "Reusable fragment ကို explicit context ဖြင့် render လုပ်သည်။"},
    {"slug": "django-load-static", "title": "load static", "lesson": 5, "syntax": "{% load static %}", "description": "Loads the static template tag library.", "example": "{% load static %}", "output": "static tag becomes available", "mm": "Static template tag library ကို load လုပ်သည်။"},
    {"slug": "django-static-tag", "title": "static tag", "lesson": 5, "syntax": "{% static 'path/to/asset.css' %}", "description": "Builds a configured URL for a static asset.", "example": "<link rel=\"stylesheet\" href=\"{% static 'css/main.css' %}\">", "output": "The stylesheet URL is generated", "mm": "Static asset အတွက် configure လုပ်ထားသော URL တည်ဆောက်သည်။"},
    {"slug": "django-default-filter", "title": "default filter", "lesson": 2, "syntax": "{{ value|default:'Fallback' }}", "description": "Displays a fallback for an empty value.", "example": "{{ student.bio|default:\"No biography yet.\" }}", "output": "A safe display fallback", "mm": "Empty value အတွက် fallback ပြသည်။"},
    {"slug": "django-length-filter", "title": "length filter", "lesson": 3, "syntax": "{{ value|length }}", "description": "Returns the length of a string or collection for display.", "example": "{{ students|length }}", "output": "The number of students", "mm": "String သို့မဟုတ် collection အရှည်ကို ပြသည်။"},
    {"slug": "django-case-filters", "title": "upper, lower and title filters", "lesson": 3, "syntax": "{{ value|upper }} {{ value|lower }} {{ value|title }}", "description": "Formats text case for presentation.", "example": "{{ course.name|title }}", "output": "Django Templates", "mm": "Presentation အတွက် စာလုံးအကြီး/အသေး format လုပ်သည်။"},
    {"slug": "django-date-filter", "title": "date filter", "lesson": 3, "syntax": "{{ value|date:'Y-m-d' }}", "description": "Formats a date or datetime value.", "example": "{{ course.updated_at|date:\"Y-m-d\" }}", "output": "2026-11-28", "mm": "Date/datetime value ကို format လုပ်သည်။"},
    {"slug": "django-truncatechars-filter", "title": "truncatechars filter", "lesson": 3, "syntax": "{{ value|truncatechars:80 }}", "description": "Shortens long display text to a character limit.", "example": "{{ course.summary|truncatechars:80 }}", "output": "A shortened summary", "mm": "ရှည်လျားသော display text ကို character limit ဖြင့် ချုံ့သည်။"},
    {"slug": "django-static-settings", "title": "STATIC_URL, STATICFILES_DIRS and STATIC_ROOT", "lesson": 5, "syntax": "STATIC_URL = '/static/'\nSTATICFILES_DIRS = [BASE_DIR / 'static']\nSTATIC_ROOT = BASE_DIR / 'collected-static'", "description": "Configures source discovery, asset URL generation, and deployment collection.", "example": "python manage.py collectstatic --noinput", "output": "Assets are collected for deployment", "mm": "Static source၊ URL နှင့် deployment collection ကို configure လုပ်သည်။"},
]


def _ensure_syntax_references(db, course, lessons_by_position):
    created = 0
    for order, item in enumerate(SYNTAX_REFERENCES, 1):
        ref = db.scalar(select(SyntaxReference).where(SyntaxReference.course_id == course.id, SyntaxReference.slug == item["slug"]))
        values = {"title": item["title"], "category": "Django Templates and Frontend", "description": item["description"], "basic_syntax": item["syntax"], "when_to_use": "Use this reference when implementing the matching Module 04 lesson boundary.", "important_notes": "Keep autoescaping and CSRF protections enabled; verify against the supported Django version.", "reference_type": "framework_api", "difficulty": "intermediate", "purpose": item["description"], "syntax_format": item["syntax"], "parameters": "See the official Django documentation for the documented arguments.", "return_value": "Rendered output, formatted value, URL, or configured asset behavior as documented.", "version_compatibility": "Validate against the course-supported Django version.", "input_output": f"Input: {item['example']}\nOutput: {item['output']}", "common_mistakes": "Do not hard-code route/static paths, disable autoescape/CSRF, or move authorization into templates.", "best_practices": "Keep context explicit, use named routes, namespaced assets, safe escaping, and focused tests.", "practice_exercises": "Implement the linked lesson exercise and add populated, empty, and failure cases where relevant.", "further_reading": "https://docs.djangoproject.com/en/stable/", "minimum_examples": 1, "review_notes": "Phase 06 Module 04 draft; publication remains review-only.", "status": "draft", "display_order": order}
        if not ref:
            ref = SyntaxReference(course_id=course.id, slug=item["slug"], **values)
            db.add(ref)
            db.flush()
            created += 1
        elif ref.status not in {"published", "approved", "in_review"}:
            for key, value in values.items():
                setattr(ref, key, value)
        if not db.scalar(select(SyntaxReferenceTranslation).where(SyntaxReferenceTranslation.reference_id == ref.id, SyntaxReferenceTranslation.locale == "my")):
            db.add(SyntaxReferenceTranslation(reference_id=ref.id, locale="my", title=item["title"], description=item["mm"], purpose=item["mm"], syntax_format=item["syntax"], parameters="Supported Django version official documentation နှင့် တိုက်ဆိုင်စစ်ဆေးပါ။", return_value="Documentation တွင် ဖော်ပြထားသော result ဖြစ်သည်။", version_compatibility="Course-supported Django version နှင့် စစ်ဆေးပါ။", input_output=f"Input: {item['example']}\nOutput: {item['output']}", common_mistakes="Route/static path ကို hard-code မလုပ်ပါနှင့်။ Autoescape/CSRF မပိတ်ပါနှင့်။", best_practices="Context explicit၊ named route၊ namespace asset၊ safe escaping နှင့် focused test သုံးပါ။", practice_exercises="သက်ဆိုင်ရာ lesson exercise နှင့် failure case ရေးပါ။", further_reading="https://docs.djangoproject.com/en/stable/", status="draft"))
        example = db.scalar(select(SyntaxReferenceExample).where(SyntaxReferenceExample.reference_id == ref.id, SyntaxReferenceExample.example_number == 1))
        example_values = {"title": item["title"], "code": item["example"], "language": "django", "difficulty": "intermediate", "description": item["description"], "setup": "Use the supported Django project environment.", "sample_input": item["syntax"], "expected_output": item["output"], "explanation": "Read the syntax, render or run the example, and compare the result with the expected behavior.", "common_mistakes": "Use the exact tag delimiters and keep the security boundary enabled.", "verification_steps": "Run a focused route/template/static check and record the actual output."}
        if not example:
            example = SyntaxReferenceExample(reference_id=ref.id, example_number=1, **example_values)
            db.add(example)
            db.flush()
        else:
            for key, value in example_values.items():
                setattr(example, key, value)
        if not db.scalar(select(SyntaxExampleTranslation).where(SyntaxExampleTranslation.example_id == example.id, SyntaxExampleTranslation.locale == "my")):
            db.add(SyntaxExampleTranslation(example_id=example.id, locale="my", title=item["title"], description=item["mm"], setup="Supported Django project တွင် run ပါ။", sample_input=item["syntax"], expected_output=item["output"], explanation="Code/template ကို run ပြီး expected behavior နှင့် နှိုင်းယှဉ်ပါ။", common_mistakes="Tag delimiter နှင့် security boundary ကို မလွတ်ပါစေနှင့်။", verification_steps="Focused check/test ကို run ပြီး actual output မှတ်တမ်းတင်ပါ။", status="draft"))
        lesson = lessons_by_position[item["lesson"]]
        if not db.scalar(select(LessonSyntaxReference).where(LessonSyntaxReference.lesson_id == lesson.id, LessonSyntaxReference.reference_id == ref.id)):
            db.add(LessonSyntaxReference(lesson_id=lesson.id, reference_id=ref.id, position=order))
    return created


def seed_django_module_four(db, course):
    """Populate only canonical Django Module 04 as reviewable draft content."""
    module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == 4))
    if not module:
        module = CourseModule(course_id=course.id, title=MODULE_TITLE, order_index=4)
        db.add(module)
        db.flush()
    module.title = MODULE_TITLE
    module.title_mm = MODULE_TITLE_MM
    module.description = MODULE_DESCRIPTION
    module.description_mm = MODULE_DESCRIPTION_MM
    module.learning_objectives = "\n".join(f"{i}. {value}" for i, value in enumerate(OBJECTIVES, 1))
    module.learning_objectives_mm = "\n".join(f"{i}. {value}" for i, value in enumerate(OBJECTIVES_MM, 1))
    created_lessons = 0
    lessons_by_position = {}
    for position, item in enumerate(LESSONS, 1):
        lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == position))
        if not lesson:
            lesson = Lesson(module_id=module.id, title=item["title"], slug=item["slug"], description=item["description"], content_en="", content_mm="", order_index=position, duration_minutes=80, status="draft", published=False)
            db.add(lesson)
            db.flush()
            created_lessons += 1
        content_en, content_mm = _render_en(item), _render_mm(item)
        if lesson.published or lesson.status in {"published", "approved", "in_review"}:
            draft = db.scalar(select(LessonContentDraft).where(LessonContentDraft.lesson_id == lesson.id))
            if not draft:
                db.add(LessonContentDraft(lesson_id=lesson.id, base_content_version=lesson.content_version, draft_version=1, title=item["title"], slug=lesson.slug, description=item["description"], content_en=content_en, content_mm=content_mm, duration_minutes=80, status="draft", change_summary="Phase 06 Module 04 authoring"))
            elif draft.status == "draft":
                draft.title, draft.description, draft.content_en, draft.content_mm, draft.duration_minutes = item["title"], item["description"], content_en, content_mm, 80
        else:
            lesson.title = item["title"]
            lesson.description = item["description"]
            lesson.content_en = content_en
            lesson.content_mm = content_mm
            lesson.duration_minutes = 80
            lesson.status = "draft"
            lesson.published = False
            _ensure_examples(db, lesson, item)
            _ensure_quiz(db, lesson, item)
            _ensure_exercise(db, lesson, item)
        lessons_by_position[position] = lesson
    lesson_ids = {position: lesson.id for position, lesson in lessons_by_position.items()}
    questions = _module_assessment(lesson_ids)
    payload = [{"position": i, **question} for i, question in enumerate(questions, 1)]
    assessment = db.scalar(select(ModuleQuizDraft).where(ModuleQuizDraft.module_id == module.id))
    if not assessment:
        db.add(ModuleQuizDraft(module_id=module.id, title_en="Django Templates and Frontend Module Assessment", title_mm="Django Template နှင့် Frontend Module စစ်ဆေးမှု", questions_json=json.dumps(payload, ensure_ascii=False), pass_percent=70, status="draft"))
    elif assessment.status not in {"published", "approved", "in_review"}:
        assessment.title_en = "Django Templates and Frontend Module Assessment"
        assessment.title_mm = "Django Template နှင့် Frontend Module စစ်ဆေးမှု"
        assessment.questions_json = json.dumps(payload, ensure_ascii=False)
        assessment.pass_percent = 70
        assessment.status = "draft"
    project = _ensure_project(db, course, module)
    syntax_created = _ensure_syntax_references(db, course, lessons_by_position)
    db.flush()
    return {"module": module, "created_lessons": created_lessons, "lesson_count": len(LESSONS), "assessment_questions": len(questions), "project": project, "syntax_created": syntax_created}

