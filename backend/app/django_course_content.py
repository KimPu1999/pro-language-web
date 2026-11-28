"""Authored Django vertical slice for the catalog seed.

The seed is deliberately idempotent and only publishes lessons that contain
reviewed content. Future modules are kept in the planning list below, but are
not published until their lessons are authored.
"""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion
from .django_complete_curriculum import _ensure_exercise, seed_django_additional_curriculum


PLANNED_MODULES = [
    "Introduction to Django", "Python for Django Developers", "Web Development Fundamentals",
    "Django Installation & Project Setup", "Django Project Structure", "URLs & Routing",
    "Views & Request Handling", "Django Templates", "Static Files & Media", "Django Models & ORM",
    "Database Migrations", "PostgreSQL with Django", "Django Forms", "Django Admin Customization",
    "Authentication Fundamentals", "Users, Groups & Permissions", "Class-Based Views",
    "Advanced ORM & Query Optimization", "Django Security", "Sessions, Cookies & Middleware",
    "Signals & Application Events", "File Uploads & Storage", "REST API Fundamentals",
    "Django REST Framework", "API Authentication & Authorization", "Advanced DRF APIs",
    "React & Django Integration", "API Documentation & Versioning", "Django Testing Fundamentals",
    "Advanced Testing & Quality", "Caching & Performance", "Background Tasks & Scheduling",
    "WebSockets & Real-Time Django", "Docker & Containerization", "Production Deployment",
    "CI/CD for Django", "Monitoring, Logging & Maintenance", "Multi-Tenant & SaaS Fundamentals",
    "Professional Django Projects", "Final Django Capstone & Assessment",
]

MODULE_ONE = [
    {
        "title": "What Django Is and Why It Exists",
        "topic": "Django's purpose, batteries-included design, and request-driven web applications",
        "code": "from django.http import HttpResponse\n\ndef home(request):\n    return HttpResponse(\"CodeMaster Academy\")",
        "filename": "learning/views.py",
        "output": "A browser request to / returns: CodeMaster Academy",
        "theory": "Django is a Python web framework for building maintainable server-rendered sites and APIs. It provides conventions for URLs, views, templates, models, forms, authentication, security middleware, and administration. The framework does not remove design decisions: a production application still needs clear boundaries, validation, tests, observability, and safe deployment.",
        "mm": "Django သည် Python ဖြင့် maintainable website နှင့် API များတည်ဆောက်ရန် အသုံးပြုသော web framework ဖြစ်သည်။ URL၊ view၊ template၊ model၊ form၊ authentication နှင့် security middleware များအတွက် အဆင်သင့်စနစ်များ ပေးထားသော်လည်း validation၊ testing နှင့် secure deployment ကို developer က စီမံရမည်။",
        "exercise": "In your notes, compare a Django view with a normal Python function. Identify its input, response, and the URL that should call it.",
        "questions": [
            ("What problem does Django primarily solve?", ["Building maintainable web applications", "Compiling C programs", "Editing images"], "Building maintainable web applications", "Django supplies conventions and reusable web components around Python."),
            ("True or false: Django removes the need for input validation.", ["True", "False"], "False", "Applications still need explicit validation at every trust boundary."),
            ("Which object commonly receives an HTTP request in a Django view?", ["request", "database_password", "package-lock"], "request", "A view receives the request and returns an HTTP response."),
        ],
    },
    {
        "title": "Django's MVT Architecture",
        "topic": "the Model-View-Template separation used by Django",
        "code": "# models.py\nclass Course(models.Model):\n    title = models.CharField(max_length=180)\n\n# views.py\ndef course_list(request):\n    courses = Course.objects.order_by(\"title\")\n    return render(request, \"courses/list.html\", {\"courses\": courses})",
        "filename": "courses/models.py + courses/views.py",
        "output": "The view queries Course records and renders courses/list.html.",
        "theory": "Django's MVT vocabulary maps a browser request to a URL, a view, optional model queries, and a template response. Models describe persisted data and relationships. Views coordinate application behavior and choose a response. Templates present trusted context without becoming a second business-logic layer. URL configuration connects public paths to views.",
        "mm": "MVT architecture တွင် Model က database data ကို ကိုယ်စားပြုသည်။ View က request ကို လက်ခံပြီး logic နှင့် data query ကို စီမံသည်။ Template က context data ကို user မြင်ရမည့် HTML အဖြစ် ပြသသည်။ URL configuration က request path ကို view နှင့် ချိတ်ဆက်ပေးသည်။",
        "exercise": "Draw the flow request → URLconf → view → model query → template → response, then label which layer owns each responsibility.",
        "questions": [
            ("Which MVT part represents persisted data?", ["Model", "Template", "URL pattern"], "Model", "Models define data and relationships stored through Django's ORM."),
            ("Which layer should primarily present HTML?", ["Template", "Migration", "Password hasher"], "Template", "Templates render the context selected by a view."),
            ("What connects a path such as /courses/ to a view?", ["URLconf", "CSS file", "Database index"], "URLconf", "URL patterns map paths to view callables."),
        ],
    },
    {
        "title": "Install Python and Django Safely",
        "topic": "supported Python versions, virtual environments, and dependency isolation",
        "code": "python3 -m venv .venv\nsource .venv/bin/activate  # Windows: .venv\\Scripts\\activate\npython -m pip install --upgrade pip\npip install \"Django>=5.0,<6.0\"\npython -m django --version",
        "filename": "terminal",
        "output": "A Django 5.x version is printed from the isolated environment.",
        "theory": "Use a supported Python 3 release and one virtual environment per project. Installing dependencies into the system interpreter makes unrelated projects interfere with one another. Pin a compatible major/minor range, record the exact resolved dependencies for deployment, and never put credentials in requirements files or source code.",
        "mm": "Project တစ်ခုစီအတွက် Python virtual environment သီးခြားသုံးပါ။ System interpreter ထဲသို့ package များ အားလုံးထည့်ခြင်းသည် project များအကြား conflict ဖြစ်စေနိုင်သည်။ Django version range ကို သတ်မှတ်ပြီး deployment အတွက် resolved dependency များကို မှတ်တမ်းတင်ပါ။",
        "exercise": "Create a folder named django-learning, create and activate .venv, install Django, and record the output of python -m django --version.",
        "questions": [
            ("Why use a virtual environment?", ["To isolate project dependencies", "To make passwords public", "To replace PostgreSQL"], "To isolate project dependencies", "Isolation prevents dependency changes in one project from breaking another."),
            ("Which command creates a virtual environment?", ["python3 -m venv .venv", "django-admin delete-env", "pip remove python"], "python3 -m venv .venv", "The venv module creates an isolated Python environment."),
            ("True or false: Secrets belong in source control.", ["True", "False"], "False", "Use environment variables or a secret manager and keep credentials out of commits."),
        ],
    },
    {
        "title": "Create Your First Django Project",
        "topic": "project scaffolding and the first development server",
        "code": "django-admin startproject config .\npython manage.py migrate\npython manage.py runserver",
        "filename": "terminal",
        "output": "Starting development server at http://127.0.0.1:8000/",
        "theory": "A Django project is the configuration boundary for one web application deployment. startproject creates settings, the root URLconf, ASGI/WSGI entry points, and manage.py. The initial migration creates Django's built-in tables. The development server is for local work only; production needs a hardened server, trusted hosts, secure settings, and a real database configuration.",
        "mm": "Django project သည် application တစ်ခုလုံး၏ configuration boundary ဖြစ်သည်။ startproject သည် settings၊ root URLconf၊ ASGI/WSGI entry point နှင့် manage.py ကို ဖန်တီးသည်။ Development server ကို local development အတွက်သာ သုံးပြီး production တွင် secure deployment စနစ်ကို အသုံးပြုရမည်။",
        "exercise": "Create a project named config inside a new folder, run migrate, open the local welcome page, and stop the server with Ctrl+C.",
        "questions": [
            ("What does manage.py provide?", ["Project management commands", "A password database", "A browser engine"], "Project management commands", "manage.py is the project-local command entry point."),
            ("Which command applies pending migrations?", ["python manage.py migrate", "python manage.py render", "python manage.py serve-static"], "python manage.py migrate", "migrate creates or updates database tables from migration files."),
            ("True or false: runserver is a production server.", ["True", "False"], "False", "Django's development server is not hardened for production traffic."),
        ],
    },
    {
        "title": "Create Your First Django App",
        "topic": "application boundaries and reusable Django components",
        "code": "python manage.py startapp learning\n\n# config/settings.py\nINSTALLED_APPS = [\n    # ...\n    \"learning\",\n]",
        "filename": "terminal + config/settings.py",
        "output": "The learning app is importable and ready for models, views, tests, and migrations.",
        "theory": "A project can contain multiple Django apps, each focused on a domain such as learning, accounts, or billing. An app is reusable code; the project settings decide how it is installed and configured. Keep app responsibilities cohesive and avoid putting every feature into one oversized module.",
        "mm": "Project တစ်ခုတွင် learning၊ accounts၊ billing စသည့် domain အလိုက် Django app များစွာ ပါနိုင်သည်။ App တစ်ခုသည် reusable code boundary ဖြစ်ပြီး settings ထဲတွင် install လုပ်မှ project က အသုံးပြုနိုင်မည်။",
        "exercise": "Create a learning app, add it to INSTALLED_APPS, and inspect the generated files. Write one sentence describing the responsibility of each file.",
        "questions": [
            ("What is a useful reason to split a project into apps?", ["Keep domain responsibilities cohesive", "Duplicate every database row", "Disable migrations"], "Keep domain responsibilities cohesive", "Focused apps are easier to test and reuse."),
            ("Where is an app registered for a project?", ["INSTALLED_APPS", "ALLOWED_PASSWORDS", "STATIC_OUTPUT_ONLY"], "INSTALLED_APPS", "Django loads installed apps from settings."),
            ("True or false: every feature must live in one app file.", ["True", "False"], "False", "A feature can use models, views, URLs, forms, tests, and templates in a focused app."),
        ],
    },
    {
        "title": "Runserver and the Development Workflow",
        "topic": "the edit-check-request loop and safe development settings",
        "code": "python manage.py check\npython manage.py runserver 8000\n# In another terminal:\ncurl http://127.0.0.1:8000/",
        "filename": "terminal",
        "output": "System check identified no issues. The local server returns an HTTP response.",
        "theory": "A reliable Django workflow is small and repeatable: make one change, run manage.py check, run focused tests, request the page, inspect logs, and commit a coherent change. DEBUG may be useful locally but must not be enabled in production. Keep allowed hosts, secret keys, cookies, CSRF origins, and database settings environment-specific.",
        "mm": "Django development workflow သည် change တစ်ခုလုပ်၊ manage.py check run၊ test run၊ browser/curl ဖြင့် request လုပ်၊ log စစ်ပြီးမှ commit လုပ်သော loop ဖြစ်သည်။ DEBUG နှင့် secret settings များကို production တွင် မဖွင့်ထားရပါ။",
        "exercise": "Run manage.py check, start the server on port 8000, request / with curl, and change one setting only after reading its documentation.",
        "questions": [
            ("What is manage.py check useful for?", ["Finding configuration and model issues", "Publishing secrets", "Deleting users"], "Finding configuration and model issues", "The system check framework catches many setup problems early."),
            ("Which setting should not expose detailed errors in production?", ["DEBUG", "LANGUAGE_CODE", "TIME_ZONE"], "DEBUG", "Production error pages must not disclose internals."),
            ("True or false: focused tests should run before a broad deployment.", ["True", "False"], "True", "Small feedback loops reduce regressions and make failures easier to diagnose."),
        ],
    },
    {
        "title": "URL Routing and Request Flow",
        "topic": "URL patterns, named routes, and request dispatch",
        "code": "# config/urls.py\nfrom django.urls import path\nfrom learning import views\n\nurlpatterns = [\n    path(\"\", views.home, name=\"home\"),\n]\n\n# learning/views.py\nfrom django.http import HttpResponse\n\ndef home(request):\n    return HttpResponse(\"Welcome to Django\")",
        "filename": "config/urls.py + learning/views.py",
        "output": "GET / is dispatched to home and returns Welcome to Django.",
        "theory": "Django resolves an incoming path against URL patterns in order. A pattern selects a view and may capture typed parameters. Name routes so templates and redirects do not hardcode URLs. Include app URLconfs under a project prefix when the project grows. Return a deliberate 404 when a resource is absent rather than leaking internal details.",
        "mm": "Django သည် incoming path ကို URL patterns အစဉ်လိုက် စစ်ပြီး သင့်တော်သော view သို့ dispatch လုပ်သည်။ URL များကို name ပေးထားပါက template နှင့် redirect တွင် hardcode မလုပ်ဘဲ reverse လုပ်နိုင်သည်။ Resource မရှိပါက အတွင်းပိုင်းအချက်အလက် မဖော်ပြဘဲ 404 ပြန်ပေးပါ။",
        "exercise": "Add /about/ with a named route, request it from the browser, then add an app-level urls.py and include it from the project URLconf.",
        "questions": [
            ("Why name a URL pattern?", ["To reverse it without hardcoding paths", "To store a password", "To run SQL automatically"], "To reverse it without hardcoding paths", "Named routes keep links and redirects resilient to path changes."),
            ("In what order are URL patterns checked?", ["Top to bottom", "Randomly", "Alphabetically by view name"], "Top to bottom", "Django uses the first matching pattern."),
            ("What is an appropriate response for a missing resource?", ["A deliberate 404", "A database password", "A 500 with secrets"], "A deliberate 404", "404 communicates absence without exposing internal details."),
        ],
    },
    {
        "title": "Build a First View and Template",
        "topic": "rendering templates with explicit context",
        "code": "# learning/views.py\nfrom django.shortcuts import render\n\ndef home(request):\n    context = {\"course_name\": \"Django Web Development\"}\n    return render(request, \"learning/home.html\", context)\n\n# learning/templates/learning/home.html\n<h1>{{ course_name }}</h1>",
        "filename": "learning/views.py + learning/templates/learning/home.html",
        "output": "The page displays Django Web Development as an h1 heading.",
        "theory": "The render shortcut combines a request, a template name, and a context dictionary into an HTTP response. Keep business rules in Python and use templates for presentation. Use Django's auto-escaping for untrusted text, avoid marking user input safe, and add tests for both the status code and important page content.",
        "mm": "render shortcut သည် request၊ template name နှင့် context dictionary ကို ပေါင်းပြီး HTTP response ပြန်ပေးသည်။ Business logic ကို Python တွင်ထားပြီး template ကို presentation အတွက် အသုံးပြုပါ။ User input ကို safe ဟု မမှတ်ဘဲ Django auto-escaping ကို ထိန်းသိမ်းပါ။",
        "exercise": "Create the learning/home.html template, render a course_name value, add a second context value, and write a test that checks a 200 response and the heading text.",
        "questions": [
            ("What does the context dictionary provide?", ["Values available to the template", "Database credentials", "A compiled CSS bundle"], "Values available to the template", "Template variables are supplied through context."),
            ("What is the safe default for untrusted template text?", ["Auto-escaping", "Mark everything safe", "String concatenation into HTML"], "Auto-escaping", "Auto-escaping reduces HTML injection risk when outputting untrusted values."),
            ("Which response should a healthy view commonly return?", ["An HttpResponse", "A raw database connection", "A shell command"], "An HttpResponse", "Django views return an HTTP response object or a response-producing shortcut."),
        ],
    },
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(index: int, item: dict) -> str:
    previous = "No Django experience is required; basic Python and terminal familiarity are helpful." if index == 1 else f"Complete Module 1 lesson {index - 1} first."
    next_step = "Continue to the next Module 1 lesson." if index < len(MODULE_ONE) else "Next: complete the Module 1 project lab and review assessment."
    return f"""Introduction
{item['title']} introduces {item['topic']} and places it in a production-minded Django workflow.

Learning objectives
- Explain {item['topic']} in your own words.
- Build and inspect the smallest useful Django example.
- Identify the security and operational boundary involved.

Prerequisites
{previous}

Django architecture explanation
{item['theory']}

Step-by-step example
1. Activate the project virtual environment.
2. Create or open the file shown below.
3. Run the command or request described in Expected output.
4. Change one small value and observe the result.

File path and code
```text
{item['filename']}
```
```python
{item['code']}
```

Commands
Use the project environment and run `python manage.py check` before starting the development server. Never paste real credentials into examples.

Expected output
{item['output']}

Code explanation
The example keeps one responsibility per step: inputs enter through a framework boundary, application code makes an explicit decision, and Django returns a response. Read errors from the first traceback line that points to your code.

Common errors
- Running a command outside the activated virtual environment.
- Using the wrong project folder or forgetting to add an app to settings.
- Hardcoding secrets, disabling validation, or trusting browser-supplied values.

Troubleshooting
Run `python manage.py check`, read the complete traceback, verify the current working directory, and compare the URL, view, template, and settings names character by character. Fix one cause at a time.

Best practices
- Keep configuration environment-specific and use named URLs.
- Add focused tests for status codes, permissions, and important output.
- Prefer small cohesive apps and explicit service boundaries.

Security considerations
Use CSRF protection for state-changing browser forms, Django's auto-escaping for template output, secure session/cookie settings in production, and server-side authorization for every protected record.

Hands-on exercise
{item['exercise']}

Mini project
Extend the example into a tiny Course Welcome page with a named URL, a view, a template, one deterministic test, and a short README explaining the request flow. Do not add login or external integrations until the basics are verified.

Summary
You can now explain {item['topic']} and verify it with a small repeatable example.

Next lesson
{next_step}
"""


def _repair_module_one_sections(lesson, item):
    """Append missing review sections without replacing authored Module 1 text."""
    if "## Detailed theory" not in lesson.content_en:
        lesson.content_en += f"""

## Detailed theory
{item['theory']}

## Core concepts
The request boundary, explicit validation, and server-side authorization are the core concepts for this lesson.

## Syntax and usage
```python
{item['code']}
```

## Expected output
{item['output']}

## Line-by-line explanation
Read the imports and declarations first, then trace the request or command into the application call, and finally compare the returned response with the expected output. Change one value at a time and rerun the focused check.

## Common mistakes
- Skipping the virtual environment or using the wrong project directory.
- Trusting client input or putting secrets in a tutorial example.

## Best practices
- Use named routes, focused tests, explicit validation, and secure defaults.
- Keep the example small and record the expected behavior before changing it.

## Practical exercises
{item['exercise']}

## Homework
Extend the example with one focused test and document the input, output, and security boundary.

## Related references
- Django documentation: https://docs.djangoproject.com/
- Django security topics: https://docs.djangoproject.com/en/stable/topics/security/

## Key takeaways
The example is a starting point for a production-minded Django workflow; verify behavior with tests before adding complexity.
"""
    if "## အသေးစိတ်သီအိုရီ" not in (lesson.content_mm or ""):
        lesson.content_mm = (lesson.content_mm or "") + f"""

## အသေးစိတ်သီအိုရီ
{item['mm']}

## လက်တွေ့လေ့ကျင့်ခန်း
{item['exercise']}

## အိမ်စာ
ဥပမာကို focused test တစ်ခုဖြင့် စစ်ပြီး input၊ output နှင့် security boundary ကို မှတ်တမ်းတင်ပါ။

## ဆက်စပ်ရည်ညွှန်းချက်
Django documentation နှင့် Django security topics ကို project version နှင့် ကိုက်ညီအောင် ပြန်လည်ဖတ်ပါ။
"""


def seed_django_course(db, course):
    """Preserve Module 1 and add the reviewable Django curriculum batch."""
    course.title = "Django Web Development — From Zero to Professional"
    course.short_description = "A free, practical Django path from Python web foundations to secure production applications."
    course.description = "Learn Django from first principles through MVT architecture, project setup, URL routing, views, templates, databases, APIs, testing, security, and professional deployment patterns."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 35
    course.outcomes = "Explain Django MVT and request flow|Create maintainable Django projects and apps|Build secure views, templates, and data-backed features|Test and deploy Django applications responsibly"
    course.requirements = "Basic Python syntax, a terminal, and a text editor; no previous Django experience is required."

    module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == 1))
    if not module:
        module = CourseModule(course_id=course.id, title=PLANNED_MODULES[0], order_index=1)
        db.add(module)
        db.flush()
    module.title = PLANNED_MODULES[0]

    for position, item in enumerate(MODULE_ONE, 1):
        slug = f"01-{_slug(item['title'])}"
        lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == position))
        if not lesson:
            lesson = Lesson(module_id=module.id, title=item["title"], slug=slug, order_index=position, content_en="", content_mm="")
            db.add(lesson)
            db.flush()
        if not lesson.content_en or not lesson.content_en.strip():
            lesson.title = item["title"]
            lesson.slug = lesson.slug or slug
            lesson.description = item["topic"]
            lesson.content_en = _content(position, item)
            lesson.content_mm = f"{item['title']}\n\n{item['mm']}\n\nလေ့ကျင့်ခန်း\n{item['exercise']}"
            lesson.duration_minutes = 35
            lesson.status = "published"
            lesson.published = True
        _repair_module_one_sections(lesson, item)

        example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        values = {
            "title": f"{item['title']} example", "language": "python", "filename": item["filename"],
            "code": item["code"], "description": f"Expected output: {item['output']}\n\nRead-only example. Run it in your local, isolated Django project.", "position": 1,
        }
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)

        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{item['title']} knowledge check", explanation="Review the lesson, then retry to reinforce the request flow and security boundaries.", status="published")
            db.add(quiz)
            db.flush()
        for q_position, (prompt, options, answer, explanation) in enumerate(item["questions"], 1):
            question = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
            values = {"prompt": prompt, "question_type": "true_false" if options == ["True", "False"] else "multiple_choice", "options_json": json.dumps(options), "correct_answer": answer, "explanation": explanation}
            if not question:
                db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
            else:
                for key, value in values.items():
                    setattr(question, key, value)
        _ensure_exercise(db, lesson, item["title"], item["exercise"], f"{item['mm']} ကို isolated Django project ထဲတွင် လက်တွေ့လေ့ကျင့်ပါ။")
    db.flush()
    additional_report = seed_django_additional_curriculum(db, course)
    db.flush()
    course.duration_minutes = sum(
        lesson.duration_minutes or 35
        for module in db.scalars(select(CourseModule).where(CourseModule.course_id == course.id)).all()
        for lesson in db.scalars(select(Lesson).where(Lesson.module_id == module.id)).all()
    )
    db.flush()
    return additional_report

