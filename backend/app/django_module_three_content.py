"""Authored, reviewable content for Django Module 03.

This module deliberately targets only the canonical third module of the
``django`` course.  It is additive and idempotent: existing lesson IDs and
slugs are retained, published lesson rows are never overwritten, and all new
curriculum assets remain drafts until an authorized reviewer publishes them.
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


MODULE_TITLE = "Django Fundamentals — Projects, Apps, URLs and Views"
MODULE_TITLE_MM = "Django အခြေခံများ — Project၊ App၊ URL နှင့် View များ"
MODULE_DESCRIPTION = (
    "Build a clear mental model of Django projects, applications, URL routing, "
    "function-based views, HTTP requests and responses, dynamic routes, and safe settings."
)
MODULE_DESCRIPTION_MM = (
    "Django project၊ application၊ URL routing၊ function-based view၊ HTTP request/response၊ "
    "dynamic route နှင့် လုံခြုံသော settings များကို လက်တွေ့နားလည်စေရန် တည်ဆောက်ထားသော module ဖြစ်သည်။"
)
OBJECTIVES = [
    "Trace a request through Django's URL resolver, view, response, and middleware boundaries.",
    "Create a project and multiple focused applications with explicit ownership.",
    "Write named URL patterns and function-based views that return useful responses.",
    "Read GET/POST request data safely and choose appropriate response types and status codes.",
    "Use converters and route parameters without confusing untrusted input with authorization.",
    "Configure development and production settings without leaking secrets.",
    "Build and test a small in-memory Student Portal using the Django fundamentals learned here.",
]
OBJECTIVES_MM = [
    "Django URL resolver၊ view၊ response နှင့် middleware boundary များအတွင်း request သွားလာပုံကို ခြေရာခံနိုင်ရန်။",
    "တာဝန်ခွဲဝေမှု ရှင်းလင်းသော project နှင့် application များကို တည်ဆောက်နိုင်ရန်။",
    "Named URL pattern နှင့် function-based view များရေးပြီး အသုံးဝင်သော response ပြန်နိုင်ရန်။",
    "GET/POST request data ကို လုံခြုံစွာဖတ်ပြီး response type နှင့် status code မှန်ကန်စွာ ရွေးနိုင်ရန်။",
    "Converter နှင့် route parameter များသုံးပြီး untrusted input ကို authorization နှင့် မရောထွေးစေရန်။",
    "Secret မပေါက်ကြားစေဘဲ development နှင့် production settings များကို စီမံနိုင်ရန်။",
    "ဤ module တွင် သင်ယူသော Django အခြေခံများဖြင့် in-memory Student Portal သေးငယ်တစ်ခု တည်ဆောက်ပြီး test လုပ်နိုင်ရန်။",
]


def _example(title, code, output, input_text, explanation, explanation_mm):
    return {
        "title": title,
        "code": dedent(code).strip(),
        "output": output,
        "input": input_text,
        "explanation": explanation,
        "explanation_mm": explanation_mm,
    }


def _q(prompt, options, answer, explanation, difficulty="beginner"):
    return {
        "prompt": prompt,
        "options": options,
        "correct_answer": answer,
        "explanation": explanation,
        "difficulty": difficulty,
        "points": 2 if difficulty == "intermediate" else 1,
    }


LESSONS = [
    {
        "title": "Django Architecture and Request Lifecycle",
        "slug": "03-django-architecture-and-request-lifecycle",
        "topic": "project architecture, URL resolution, middleware, views, and response lifecycle",
        "description": "Follow a browser request through Django's main boundaries before writing a view.",
        "description_mm": "View မရေးမီ browser request သည် Django ၏ boundary များကို ဖြတ်သန်းပုံကို လေ့လာပါ။",
        "syntax": "browser → ASGI/WSGI → middleware → URL resolver → view → response middleware → browser",
        "syntax_mm": "browser → ASGI/WSGI → middleware → URL resolver → view → response middleware → browser",
        "theory": "Django is a request/response framework. A server adapter receives an HTTP request and creates an HttpRequest object. Middleware can inspect or short-circuit it, the URL resolver selects a view, and the view returns an HttpResponse (or a response-producing shortcut). Response middleware then runs on the way out. Templates, models, and forms are useful collaborators, but they do not replace this lifecycle. A clean design keeps routing declarative, views focused on orchestration, and domain rules testable outside the request boundary.",
        "theory_mm": "Django သည် request/response framework ဖြစ်သည်။ Server adapter က HTTP request ကို လက်ခံပြီး HttpRequest object ပြုလုပ်သည်။ Middleware သည် request ကို စစ်ဆေးနိုင်သလို အစောပိုင်း response ပြန်နိုင်သည်။ URL resolver က view ကိုရွေးပြီး view က HttpResponse (သို့) response ထုတ်ပေးသော shortcut ကို ပြန်သည်။ ပြန်ထွက်ရာတွင် response middleware များက လုပ်ဆောင်သည်။ Routing ကို declarative ထားပြီး view ကို orchestration အတွက်သာ အသုံးပြုကာ business rule ကို request boundary ပြင်ပတွင် testable ထားသင့်သည်။",
        "concepts": "Key concepts: server adapter, middleware chain, URL resolver, view callable, HttpRequest, HttpResponse, status code, template rendering, exception handling, and the difference between a route match and authorization.",
        "concepts_mm": "အဓိက concept များမှာ server adapter၊ middleware chain၊ URL resolver၊ view callable၊ HttpRequest၊ HttpResponse၊ status code၊ template rendering၊ exception handling နှင့် route match သည် authorization မဟုတ်ကြောင်းတို့ ဖြစ်သည်။",
        "mistakes": ["Putting database queries in URL configuration.", "Assuming a URL match proves that a user is allowed to see the object.", "Returning a string instead of an HttpResponse from a view.", "Hiding all exceptions so operational failures look like empty pages."],
        "mistakes_mm": ["URL configuration ထဲတွင် database query ထည့်ခြင်း။", "URL match ဖြစ်သည်နှင့် object ကိုကြည့်ခွင့်ရှိပြီဟု ယူဆခြင်း။", "View မှ HttpResponse အစား string တိုက်ရိုက်ပြန်ခြင်း။", "Exception အားလုံးကိုဖုံးကွယ်ပြီး system failure ကို empty page အဖြစ် ပြခြင်း။"],
        "best_practices": "Keep each boundary observable, return explicit status codes, use named routes, keep middleware small, and test the view with RequestFactory or the Django test client.",
        "best_practices_mm": "Boundary တစ်ခုချင်းစီကို စောင့်ကြည့်နိုင်အောင်ထားပါ၊ status code ကို ရှင်းလင်းစွာပြန်ပါ၊ named route သုံးပါ၊ middleware ကိုသေးငယ်စွာထားပြီး RequestFactory သို့မဟုတ် Django test client ဖြင့် view ကို test လုပ်ပါ။",
        "examples": [
            _example("A minimal response boundary", "from django.http import HttpResponse\n\ndef health(request):\n    return HttpResponse(\"ok\", content_type=\"text/plain\")", "HTTP 200 with body ok", "GET /health/", "The callable receives request and returns an HttpResponse.", "Callable သည် request ကိုလက်ခံပြီး HttpResponse ပြန်ပေးသည်။"),
            _example("A named request lifecycle trace", "def trace(request):\n    print(request.method, request.path)\n    return HttpResponse(\"request recorded\")", "GET /trace/ is printed on the server", "GET /trace/", "Server-side logging is different from data shown to the student; never log secrets.", "Server log သည် student ကိုပြသော data မဟုတ်ပါ။ Secret များကို log မလုပ်ပါနှင့်။"),
            _example("A small middleware boundary", "class AddRequestId:\n    def __init__(self, get_response):\n        self.get_response = get_response\n\n    def __call__(self, request):\n        response = self.get_response(request)\n        response[\"X-Request-Id\"] = \"demo\"\n        return response", "Response includes X-Request-Id: demo", "The middleware wraps the next callable.", "Django constructs middleware around the next callable and adds a response header.", "Middleware သည် နောက် callable ကို wrap လုပ်ပြီး response header ထည့်ပြသည်။"),
            _example("Explicit not found behavior", "from django.http import Http404, HttpResponse\n\ndef only_demo(request):\n    if request.path != \"/demo/\":\n        raise Http404(\"Demo page not found\")\n    return HttpResponse(\"demo\")", "GET /other/ produces 404", "GET /other/ is the input.", "The path is intentionally not a data lookup; a non-matching path raises 404.", "Path မကိုက်ပါက 404 ပြန်ပြီး ကိုက်ပါက demo response ပြန်သည်။"),
        ],
        "exercises": "Draw the request lifecycle for /students/42/. Then create a health view, add one logging middleware, and write tests for a 200 response and a 404 response. Explain which layer owns each assertion.",
        "exercises_mm": " /students/42/ request lifecycle ကို ပုံဆွဲပါ။ ထို့နောက် health view၊ logging middleware တစ်ခုနှင့် 200/404 response test များရေးပါ။ Assertion တစ်ခုချင်းစီကို ဘယ် layer က တာဝန်ယူသလဲ ရှင်းပြပါ။",
        "homework": "Request Lifecycle Notebook: make a table of each boundary, its input/output, and one failure mode. Add a test proving that the view—not the URL file—decides the response body.",
        "homework_mm": "Request Lifecycle Notebook ပြုလုပ်ပါ။ Boundary တစ်ခုချင်းစီ၏ input/output နှင့် failure mode တစ်ခုစီရေးပါ။ Response body ကို URL file မဟုတ်ဘဲ view ကဆုံးဖြတ်ကြောင်း test ထည့်ပါ။",
        "summary": "Django turns an incoming HTTP request into a response through explicit, testable boundaries.",
        "summary_mm": "Django သည် incoming HTTP request ကို ရှင်းလင်းပြီး test လုပ်နိုင်သော boundary များမှတစ်ဆင့် response အဖြစ် ပြောင်းလဲသည်။",
        "quiz": [
            _q("Which component selects a view from a path?", ["URL resolver", "Template engine", "Database", "Static file finder"], "URL resolver", "URL patterns are resolved before the view is called."),
            _q("What should a view return?", ["An HttpResponse or response-producing result", "A database password", "A CSS selector", "A migration file"], "An HttpResponse or response-producing result", "Django's request handler needs a response object."),
            _q("True or false: matching a URL automatically authorizes a user.", ["True", "False"], "False", "Authorization is a separate policy decision."),
            _q("Where can a short-circuit response be produced?", ["Middleware", "A URL name", "A model field", "A CSS rule"], "Middleware", "Middleware can return before the view runs."),
            _q("What is HttpRequest?", ["The request data object passed to a view", "A database table", "A template", "A command-line flag"], "The request data object passed to a view", "It contains method, path, headers, query data, and more."),
            _q("What is a useful reason to keep domain rules out of a view?", ["They can be reused and tested independently", "Django forbids functions", "It makes URLs dynamic", "It disables middleware"], "They can be reused and tested independently", "Thin views make behavior easier to verify.", "intermediate"),
            _q("Which response signals that a resource was not found?", ["404", "200", "201", "302"], "404", "404 communicates that the requested resource is absent."),
            _q("What should not be written to request logs?", ["Passwords and secret tokens", "A safe request method", "A route name", "A correlation ID"], "Passwords and secret tokens", "Logs are operational data and must not leak credentials.", "intermediate"),
        ],
    },
    {
        "title": "Django Projects and Applications",
        "slug": "03-django-projects-and-applications",
        "topic": "django-admin startproject, manage.py, startapp, app boundaries, and installed apps",
        "description": "Create a Django project shell and organize features into reusable applications.",
        "description_mm": "Django project shell တည်ဆောက်ပြီး feature များကို reusable application များအဖြစ် ခွဲပါ။",
        "syntax": "django-admin startproject school_site .\npython manage.py startapp students\nINSTALLED_APPS = [\"students\"]",
        "syntax_mm": "django-admin startproject school_site .\npython manage.py startapp students\nINSTALLED_APPS = [\"students\"]",
        "theory": "A Django project is the configuration and deployment container; an application is a focused feature package. One project can contain students, courses, and accounts applications. manage.py delegates commands to the project's settings module. startproject creates the project package and manage.py; startapp creates an application package. Adding an app to INSTALLED_APPS makes Django discover its configuration and, later, migrations, templates, and static assets. The folder name, Python package name, app label, and URL namespace are related but not interchangeable.",
        "theory_mm": "Django project သည် configuration နှင့် deployment container ဖြစ်ပြီး application သည် feature တစ်ခုကို အာရုံစိုက်ထားသော package ဖြစ်သည်။ Project တစ်ခုအတွင်း students၊ courses၊ accounts app များပါနိုင်သည်။ manage.py သည် project settings module သို့ command များကို လွှဲပို့သည်။ startproject က project package နှင့် manage.py ပြုလုပ်ပြီး startapp က application package ပြုလုပ်သည်။ INSTALLED_APPS ထဲထည့်လျှင် Django က app configuration၊ နောက်ပိုင်း migration/template/static asset များကို ရှာဖွေနိုင်သည်။ Folder name၊ Python package name၊ app label နှင့် URL namespace တို့ကို တူသည်ဟု မယူဆပါနှင့်။",
        "concepts": "Project versus app, manage.py, settings module, root URL configuration, app configuration, INSTALLED_APPS, import paths, and feature ownership.",
        "concepts_mm": "Project နှင့် app ခွဲခြားမှု၊ manage.py၊ settings module၊ root URL configuration၊ app configuration၊ INSTALLED_APPS၊ import path နှင့် feature ownership တို့ကို နားလည်ရမည်။",
        "mistakes": ["Running startapp from an unexpected directory.", "Adding a filesystem path instead of an installed Python app.", "Putting every feature into one views.py file.", "Committing a generated secret key or local database file."],
        "mistakes_mm": ["မမျှော်လင့်သော directory မှ startapp run ခြင်း။", "Installed Python app အစား filesystem path ထည့်ခြင်း။", "Feature အားလုံးကို views.py တစ်ခုထဲ ထည့်ခြင်း။", "Generated secret key သို့မဟုတ် local database file ကို commit လုပ်ခြင်း။"],
        "best_practices": "Keep settings explicit, use one app for one coherent capability, name packages consistently, and keep secrets outside version control.",
        "best_practices_mm": "Settings ကို ရှင်းလင်းစွာထားပါ၊ app တစ်ခုကို capability တစ်ခုအတွက် သုံးပါ၊ package name များ တစ်သမတ်တည်းထားပြီး secret များကို version control ပြင်ပတွင်ထားပါ။",
        "examples": [
            _example("Create a project in the current directory", "command = \"django-admin startproject school_site .\"\nprint(command)", "manage.py and school_site/ are created", "Run from an empty project directory.", "Run the printed command in the terminal; the dot prevents an unnecessary nested directory.", "Terminal တွင် ပြထားသော command ကို run ပါ။ dot သုံးခြင်းဖြင့် မလိုအပ်သော nested directory မဖြစ်စေပါ။"),
            _example("Create two feature apps", "commands = [\"python manage.py startapp students\", \"python manage.py startapp courses\"]\nfor command in commands:\n    print(command)", "students/ and courses/ packages are created", "Run the printed commands from the directory containing manage.py.", "Each command owns a focused domain boundary.", "Command တစ်ခုစီသည် သီးခြား domain boundary ကို တာဝန်ယူသည်။"),
            _example("Register apps", "INSTALLED_APPS = [\n    \"django.contrib.contenttypes\",\n    \"students\",\n    \"courses\",\n]", "Django discovers both feature apps", "The modules are importable from the project path.", "Installed app registration is configuration, not a database migration by itself.", "Installed app registration သည် configuration ဖြစ်ပြီး တစ်ခုတည်းဖြင့် database migration မဟုတ်ပါ။"),
            _example("Expose a project URL module", "from django.urls import include, path\n\nurlpatterns = [\n    path(\"students/\", include(\"students.urls\")),\n]", "students routes own the students/ prefix", "The students.urls module defines child routes.", "include() delegates a URL prefix to an app.", "include() သည် URL prefix ကို app တစ်ခုသို့ လွှဲပေးသည်။"),
        ],
        "exercises": "Create school_site with students and courses apps. Register both apps, create a urls.py in each, and write a README that identifies the owner of settings, root URLs, student routes, and course routes.",
        "exercises_mm": "school_site project ထဲတွင် students နှင့် courses app တည်ဆောက်ပါ။ App နှစ်ခုကို register လုပ်ပြီး app တစ်ခုစီတွင် urls.py ပြုလုပ်ပါ။ Settings၊ root URL၊ student route နှင့် course route တို့၏ owner ကို README တွင် ရေးပါ။",
        "homework": "Project Boundary Audit: start from an empty folder, reproduce the commands, inspect every generated file, and record which generated values must be replaced or kept secret before production.",
        "homework_mm": "Project Boundary Audit ပြုလုပ်ပါ။ Empty folder မှ command များကို ပြန် run ပြီး generated file တစ်ခုစီ စစ်ဆေးပါ။ Production မတင်မီ ပြောင်းရမည့် value နှင့် secret ထားရမည့် value များကို မှတ်တမ်းတင်ပါ။",
        "summary": "Projects hold configuration; applications hold focused features and can own their URLs, tests, templates, and models.",
        "summary_mm": "Project သည် configuration ကို ကိုင်ထားပြီး application သည် focused feature၊ URL၊ test၊ template နှင့် model တို့ကို တာဝန်ယူနိုင်သည်။",
        "quiz": [
            _q("Which command creates manage.py and a project package?", ["startproject", "startapp", "runserver", "check"], "startproject", "startproject creates the project shell."),
            _q("Which command creates an application package?", ["python manage.py startapp students", "python manage.py startproject students", "python manage.py migrateapp students", "python manage.py install students"], "python manage.py startapp students", "startapp creates a focused application."),
            _q("What does INSTALLED_APPS control?", ["Django app discovery and configuration", "The browser viewport", "The database password only", "The URL port"], "Django app discovery and configuration", "It tells Django which apps participate in the project."),
            _q("True or false: a project and an app are identical concepts.", ["True", "False"], "False", "The project is the container; apps are feature packages."),
            _q("Why use multiple apps?", ["To keep feature ownership and dependencies clearer", "To hide every URL", "To avoid settings", "To remove tests"], "To keep feature ownership and dependencies clearer", "Cohesive apps are easier to evolve."),
            _q("Which file normally contains root URL patterns?", ["project urls.py", "README.md", "requirements.txt", "models.py only"], "project urls.py", "The root URL module delegates to app URL modules."),
            _q("What should happen to a production SECRET_KEY?", ["Keep it outside source control", "Print it in logs", "Put it in a public README", "Use it as a URL"], "Keep it outside source control", "Secrets must be injected through a safe configuration boundary.", "intermediate"),
            _q("What does the dot in startproject school_site . mean?", ["Use the current directory as the destination", "Enable debug mode", "Create a database", "Install an app"], "Use the current directory as the destination", "It avoids an extra nested directory."),
        ],
    },
    {
        "title": "Django URL Routing and URL Configuration",
        "slug": "03-django-url-routing-and-url-configuration",
        "topic": "path, include, urlpatterns, app_name, names, reverse, and reverse_lazy",
        "description": "Design readable, named URL contracts from the project root down to each app.",
        "description_mm": "Project root မှ app အထိ ဖတ်ရလွယ်ပြီး named URL contract များကို ဒီဇိုင်းလုပ်ပါ။",
        "syntax": "from django.urls import include, path\napp_name = \"students\"\nurlpatterns = [path(\"\", views.list_students, name=\"list\")]\nreverse(\"students:list\")",
        "syntax_mm": "from django.urls import include, path\napp_name = \"students\"\nurlpatterns = [path(\"\", views.list_students, name=\"list\")]\nreverse(\"students:list\")",
        "theory": "URL configuration is a Python declaration of public route contracts. path() connects a route to a callable or include(); include() lets an app own a prefix. urlpatterns must be a sequence of URL patterns. A name makes code independent of literal paths, while app_name creates a namespace for included routes. reverse() builds a URL at runtime; reverse_lazy() postpones URL resolution for import-time contexts such as class attributes. A route should describe the resource, while authorization and validation remain in the view or service layer.",
        "theory_mm": "URL configuration သည် public route contract များကို Python declaration အဖြစ် ဖော်ပြသည်။ path() သည် route ကို callable သို့မဟုတ် include() နှင့် ချိတ်သည်။ include() သည် app တစ်ခုအား prefix တစ်ခုကို ပိုင်ဆိုင်စေသည်။ urlpatterns သည် URL pattern များ၏ sequence ဖြစ်ရမည်။ name သည် literal path မလိုဘဲ code ရေးနိုင်စေပြီး app_name သည် namespace ပြုလုပ်သည်။ reverse() သည် runtime တွင် URL တည်ဆောက်ပြီး reverse_lazy() သည် import-time context တွင် resolution ကို နောက်ဆုတ်ထားသည်။ Route သည် resource ကိုဖော်ပြပြီး authorization နှင့် validation ကို view/service layer တွင်ထားရမည်။",
        "concepts": "Literal paths versus names, namespaces, include delegation, route ordering, trailing slashes, URL reversing, and route contract tests.",
        "concepts_mm": "Literal path နှင့် name ခြားနားမှု၊ namespace၊ include delegation၊ route order၊ trailing slash၊ URL reversing နှင့် route contract test များကို လေ့လာရမည်။",
        "mistakes": ["Defining a broad route before a specific route.", "Using duplicate URL names across included apps.", "Hard-coding links throughout templates.", "Calling reverse() too early during module import."],
        "mistakes_mm": ["Specific route မတိုင်မီ broad route ထားခြင်း။", "Included app များတွင် URL name ထပ်ခြင်း။", "Template အားလုံးတွင် link ကို hard-code လုပ်ခြင်း။", "Module import အချိန်တွင် reverse() ကို စောစောခေါ်ခြင်း။"],
        "best_practices": "Name every navigable route, namespace app routes, keep patterns ordered from specific to general, and test reverse/resolve behavior.",
        "best_practices_mm": "သွားလာနိုင်သော route တိုင်းကို name ပေးပါ၊ app route များကို namespace လုပ်ပါ၊ specific မှ general အစီအစဉ်ထားပြီး reverse/resolve behavior ကို test လုပ်ပါ။",
        "examples": [
            _example("Project delegates to an app", "path(\"students/\", include(\"students.urls\"))", "students.urls receives the remaining path", "GET /students/", "The project owns the prefix and the app owns child patterns.", "Project က prefix ကိုပိုင်ပြီး app က child pattern များကို ပိုင်သည်။"),
            _example("Named app route", "app_name = \"students\"\nurlpatterns = [\n    path(\"\", views.list_students, name=\"list\"),\n]", "students:list resolves to /students/", "The root include supplies the students/ prefix.", "The namespace prevents collisions with another app's list route.", "Namespace သည် အခြား app ၏ list route နှင့် name မထပ်စေရန် ကာကွယ်သည်။"),
            _example("Reverse a parameterized route", "path(\"<int:student_id>/\", views.detail, name=\"detail\")\nreverse(\"students:detail\", kwargs={\"student_id\": 7})", "'/students/7/'", "student_id=7", "reverse uses the route name and converter keyword.", "reverse သည် route name နှင့် converter keyword ကို သုံးသည်။"),
            _example("Lazy reverse for a class attribute", "from django.urls import reverse_lazy\n\nclass StudentCreate:  # example policy object\n    success_url = reverse_lazy(\"students:list\")", "URL resolution is deferred", "The URL namespace is loaded later.", "reverse_lazy avoids import-time resolution errors.", "reverse_lazy သည် import-time resolution error မဖြစ်စေရန် resolution ကို နောက်ဆုတ်သည်။"),
        ],
        "exercises": "Build project and app URL files with names and namespaces. Add tests that reverse list/detail URLs and resolve them back to the expected view names. Deliberately place a broad route first, observe the bug, then fix the order.",
        "exercises_mm": "Project နှင့် app URL file များကို name/namespace ဖြင့် တည်ဆောက်ပါ။ List/detail URL များကို reverse လုပ်ပြီး မှန်ကန်သော view name သို့ resolve ဖြစ်ကြောင်း test လုပ်ပါ။ Broad route ကို အရင်ထားပြီး bug ကို လေ့လာကာ ပြန်ပြင်ပါ။",
        "homework": "URL Contract Review: create a route table containing method, path, name, parameters, owner, and authorization rule for the Student Portal.",
        "homework_mm": "URL Contract Review ပြုလုပ်ပါ။ Student Portal အတွက် method၊ path၊ name၊ parameter၊ owner နှင့် authorization rule ပါသော route table ပြုလုပ်ပါ။",
        "summary": "Named, namespaced URL patterns form a stable contract between navigation, views, and tests.",
        "summary_mm": "Named နှင့် namespaced URL pattern များသည် navigation၊ view နှင့် test တို့အကြား တည်ငြိမ်သော contract ဖြစ်သည်။",
        "quiz": [
            _q("What does include() provide?", ["Delegation to another URL module", "A database connection", "A template variable", "A response body"], "Delegation to another URL module", "It lets an app own child routes."),
            _q("Why name a URL pattern?", ["To reverse it without hard-coding its path", "To hide it from all users", "To create a model", "To enable CSS"], "To reverse it without hard-coding its path", "Names are stable code-facing identifiers."),
            _q("What does app_name define?", ["A URL namespace", "A database schema", "A password", "A static file"], "A URL namespace", "The namespace prefixes route names."),
            _q("Which function is lazy?", ["reverse_lazy", "reverse_now", "path_lazy", "include_later"], "reverse_lazy", "It postpones URL resolution."),
            _q("True or false: route order can affect matching.", ["True", "False"], "True", "Django checks patterns in order."),
            _q("Where should authorization normally be enforced?", ["View or service policy boundary", "The route name only", "A CSS class", "A browser bookmark"], "View or service policy boundary", "A route match is not permission checking.", "intermediate"),
            _q("What does reverse need for a dynamic route?", ["The route name and required arguments", "A screenshot", "A database reset", "A media asset"], "The route name and required arguments", "All converter parameters must be supplied."),
            _q("What should app URL names avoid?", ["Unclear collisions across namespaces", "Meaningful names", "Tests", "Converters"], "Unclear collisions across namespaces", "Namespaces make names predictable.", "intermediate"),
        ],
    },
    {
        "title": "Django Function-Based Views",
        "slug": "03-django-function-based-views",
        "topic": "function-based views, render, redirect, get_object_or_404, and view boundaries",
        "description": "Write small function-based views that validate input and return intentional responses.",
        "description_mm": "Input ကို validate လုပ်ပြီး ရည်ရွယ်ချက်ရှိသော response ပြန်ပေးသည့် function-based view များရေးပါ။",
        "syntax": "def list_students(request):\n    return render(request, \"students/list.html\", {\"students\": rows})",
        "syntax_mm": "def list_students(request):\n    return render(request, \"students/list.html\", {\"students\": rows})",
        "theory": "A function-based view is an ordinary Python callable with a Django request contract. It can branch on request.method, validate input, call a service or ORM query, and return render(), redirect(), JsonResponse, or an error response. render() combines a request, template name, and context. redirect() communicates a new location after a successful mutation. get_object_or_404() turns a missing object into a correct 404. Keep the view short: parse the boundary, call a focused operation, choose a response, and leave reusable rules in a service or model method.",
        "theory_mm": "Function-based view သည် Django request contract ကိုလိုက်နာသော ရိုးရိုး Python callable ဖြစ်သည်။ request.method အပေါ် မူတည်၍ branch လုပ်နိုင်ပြီး input validate လုပ်ကာ service/ORM query ခေါ်ပြီး render(), redirect(), JsonResponse သို့မဟုတ် error response ပြန်နိုင်သည်။ render() သည် request၊ template name နှင့် context ကို ပေါင်းစပ်သည်။ Mutation အောင်မြင်ပြီးနောက် redirect() သည် location အသစ်ကို ပြသည်။ get_object_or_404() သည် object မရှိလျှင် မှန်ကန်သော 404 ပြန်သည်။ View ကိုတိုအောင်ထားပြီး reusable rule ကို service/model method တွင် ထားပါ။",
        "concepts": "View callable, render context, redirect-after-POST, 404 semantics, service boundary, template safety, and response selection.",
        "concepts_mm": "View callable၊ render context၊ POST ပြီး redirect၊ 404 semantics၊ service boundary၊ template safety နှင့် response ရွေးချယ်မှုတို့ကို လေ့လာရမည်။",
        "mistakes": ["Accepting POST data without validation.", "Returning a redirect before a failed operation is handled.", "Using a broad except around the complete view.", "Passing secret or untrusted internal data into a template context."],
        "mistakes_mm": ["POST data ကို validate မလုပ်ဘဲ လက်ခံခြင်း။", "Operation မအောင်မြင်မှုကို မကိုင်တွယ်မီ redirect လုပ်ခြင်း။", "View အားလုံးကို broad except ဖြင့် ဖုံးခြင်း။", "Secret သို့မဟုတ် untrusted internal data ကို template context ထဲထည့်ခြင်း။"],
        "best_practices": "Use one responsibility per view, validate at the boundary, redirect after successful POST, use 404 for missing resources, and test status, context, and side effects.",
        "best_practices_mm": "View တစ်ခုတွင် တာဝန်တစ်ခုသာထားပါ၊ boundary တွင် validate လုပ်ပါ၊ POST အောင်မြင်လျှင် redirect လုပ်ပါ၊ resource မရှိလျှင် 404 ပြန်ပြီး status/context/side effect များကို test လုပ်ပါ။",
        "examples": [
            _example("Render a list", "from django.shortcuts import render\n\ndef list_students(request):\n    students = [{\"id\": 1, \"name\": \"Mya\"}]\n    return render(request, \"students/list.html\", {\"students\": students})", "HTTP 200 and students context", "GET request with an in-memory list.", "render keeps presentation in the template while the view prepares context.", "render သည် presentation ကို template ထဲထားပြီး view က context ပြင်ဆင်သည်။"),
            _example("Return JSON", "from django.http import JsonResponse\n\ndef health_json(request):\n    return JsonResponse({\"status\": \"ok\"})", "{\"status\": \"ok\"}", "GET /health.json/", "JsonResponse sets a JSON content type and serializes the mapping.", "JsonResponse သည် JSON content type သတ်မှတ်ပြီး mapping ကို serialize လုပ်သည်။"),
            _example("Use 404 for a missing record", "from django.shortcuts import get_object_or_404\n\ndef student_detail(request, student_id):\n    student = get_object_or_404(Student, pk=student_id)\n    return render(request, \"students/detail.html\", {\"student\": student})", "Missing IDs produce HTTP 404", "student_id from the URL is looked up by the ORM.", "The shortcut makes missing-resource behavior explicit.", "Shortcut သည် resource မရှိမှုကို ရှင်းလင်းစွာ ဖော်ပြသည်။"),
            _example("Redirect after POST", "from django.shortcuts import redirect\n\ndef create_student(request):\n    if request.method == \"POST\":\n        # validate and save here\n        return redirect(\"students:list\")\n    return render(request, \"students/form.html\")", "POST redirects to the named list route", "A valid submitted form.", "Post/redirect/get avoids accidental duplicate submission on refresh.", "Post/redirect/get သည် refresh လုပ်ရာတွင် duplicate submit မဖြစ်စေပါ။"),
        ],
        "exercises": "Implement list, detail, and create views for in-memory students. Add tests for GET list, missing detail (404), valid POST redirect, and invalid POST redisplay. Keep validation in a helper function.",
        "exercises_mm": "In-memory student data အတွက် list၊ detail နှင့် create view များရေးပါ။ GET list၊ missing detail (404)၊ valid POST redirect နှင့် invalid POST redisplay အတွက် test ရေးပါ။ Validation ကို helper function ထဲထားပါ။",
        "homework": "Thin View Refactor: start with one large view and refactor it into input parsing, service operation, and response selection. Explain why each function has one reason to change.",
        "homework_mm": "Thin View Refactor ပြုလုပ်ပါ။ View ကြီးတစ်ခုမှ input parsing၊ service operation နှင့် response selection သို့ ခွဲပါ။ Function တစ်ခုစီတွင် change reason တစ်ခုသာရှိကြောင်း ရှင်းပြပါ။",
        "summary": "Function-based views are simple adapters: receive a request, invoke a focused operation, and return an intentional response.",
        "summary_mm": "Function-based view သည် request လက်ခံ၊ focused operation ခေါ်ပြီး ရည်ရွယ်ချက်ရှိသော response ပြန်ပေးသော adapter ရိုးရှင်းတစ်ခု ဖြစ်သည်။",
        "quiz": [
            _q("What does render() combine?", ["Request, template, and context", "Database and password", "URL and CSS only", "Two migrations"], "Request, template, and context", "It produces a template response."),
            _q("Why redirect after a successful POST?", ["To avoid duplicate submission on refresh", "To hide errors", "To skip validation", "To create a model automatically"], "To avoid duplicate submission on refresh", "Post/redirect/get separates mutation and refreshable GET."),
            _q("What should missing detail usually return?", ["404", "200 with a secret", "500 always", "301"], "404", "The requested resource does not exist."),
            _q("True or false: a view should contain every business rule in a large block.", ["True", "False"], "False", "Reusable rules belong in focused testable boundaries."),
            _q("Which helper produces JSON?", ["JsonResponse", "Http404", "reverse_lazy", "include"], "JsonResponse", "JsonResponse serializes JSON data for an HTTP response."),
            _q("What must happen before using request.POST values?", ["Validate and normalize them", "Print passwords", "Reverse a CSS URL", "Disable CSRF"], "Validate and normalize them", "Request data is untrusted input.", "intermediate"),
            _q("What is a good view test assertion?", ["Status, context/body, and side effects", "Only the function name", "Only the file length", "Nothing"], "Status, context/body, and side effects", "A test should protect observable behavior.", "intermediate"),
            _q("Which shortcut turns missing ORM objects into 404?", ["get_object_or_404", "get_or_create_only", "reverse", "startapp"], "get_object_or_404", "It raises Http404 when no object matches."),
        ],
    },
    {
        "title": "HTTP Requests and Responses in Django",
        "slug": "03-http-requests-and-responses-in-django",
        "topic": "HttpRequest, HttpResponse, JsonResponse, Http404, GET, POST, methods, status codes, and CSRF",
        "description": "Handle browser input and communicate outcomes with correct HTTP semantics.",
        "description_mm": "Browser input ကို ကိုင်တွယ်ပြီး မှန်ကန်သော HTTP semantics ဖြင့် outcome ပြပါ။",
        "syntax": "request.method\nrequest.GET.get(\"q\", \"\")\nrequest.POST.get(\"name\")\nreturn JsonResponse(data, status=201)",
        "syntax_mm": "request.method\nrequest.GET.get(\"q\", \"\")\nrequest.POST.get(\"name\")\nreturn JsonResponse(data, status=201)",
        "theory": "HttpRequest exposes the method, path, headers, query string, body, authenticated user, and files. GET query parameters are for retrieval/filtering and may be bookmarked; POST form data is for a state-changing operation and must be validated and protected with CSRF for browser forms. HttpResponse is suitable for text or HTML, JsonResponse for JSON, and Http404 for a missing resource. Status codes are part of the API: 200 means success, 201 creation, 204 no body, 302 redirect, 400 invalid input, 403 forbidden, and 404 missing. A 500 is a server failure, not a validation response.",
        "theory_mm": "HttpRequest တွင် method၊ path၊ header၊ query string၊ body၊ authenticated user နှင့် file များပါသည်။ GET query parameter သည် retrieval/filter အတွက်ဖြစ်ပြီး bookmark လုပ်နိုင်သည်။ POST form data သည် state ပြောင်းလဲမှုအတွက်ဖြစ်၍ validate လုပ်ရမည်၊ browser form အတွက် CSRF ကာကွယ်မှုလိုသည်။ HttpResponse သည် text/HTML၊ JsonResponse သည် JSON၊ Http404 သည် resource မရှိမှုအတွက် သုံးသည်။ Status code များသည် API အစိတ်အပိုင်းဖြစ်ပြီး 200 success၊ 201 creation၊ 204 no body၊ 302 redirect၊ 400 invalid input၊ 403 forbidden၊ 404 missing ဖြစ်သည်။ 500 သည် validation မဟုတ်ဘဲ server failure ဖြစ်သည်။",
        "concepts": "Request attributes, query versus body data, method allow-listing, response content types, status codes, CSRF, and safe error messages.",
        "concepts_mm": "Request attribute များ၊ query နှင့် body data ခွဲခြားမှု၊ method allow-list၊ response content type၊ status code၊ CSRF နှင့် safe error message များကို လေ့လာရမည်။",
        "mistakes": ["Using GET for a destructive action.", "Disabling CSRF to make a form test pass.", "Returning 200 for every failure.", "Echoing raw input into HTML without escaping or validation."],
        "mistakes_mm": ["ဖျက်ဆီးသော action အတွက် GET သုံးခြင်း။", "Form test အောင်ရန် CSRF ပိတ်ခြင်း။", "Failure အားလုံးအတွက် 200 ပြန်ခြင်း။", "Raw input ကို escaping/validation မလုပ်ဘဲ HTML ထဲ ပြန်ထည့်ခြင်း။"],
        "best_practices": "Allow-list methods, validate every input, preserve CSRF protection, choose a status that tells the truth, and keep error bodies useful but non-sensitive.",
        "best_practices_mm": "ခွင့်ပြုသော method များကို allow-list လုပ်ပါ၊ input အားလုံး validate လုပ်ပါ၊ CSRF မပိတ်ပါနှင့်၊ အမှန်ကိုဖော်ပြသော status ရွေးပြီး sensitive မဟုတ်သော အသုံးဝင်သည့် error body ပြန်ပါ။",
        "examples": [
            _example("Read a safe search query", "def search(request):\n    query = request.GET.get(\"q\", \"\").strip()\n    return JsonResponse({\"query\": query, \"results\": []})", "GET /search/?q=django returns the normalized query", "q is browser-controlled text.", "get() supplies a default and strip() normalizes whitespace.", "get() က default ပေးပြီး strip() က whitespace ကို normalize လုပ်သည်။"),
            _example("Allow only POST for mutation", "from django.http import HttpResponseNotAllowed\n\ndef publish(request):\n    if request.method != \"POST\":\n        return HttpResponseNotAllowed([\"POST\"])\n    return JsonResponse({\"published\": True})", "GET receives Allow: POST and 405", "The caller uses the wrong HTTP method.", "A mutation should not be triggered by a link or crawler.", "Mutation ကို link/crawler မှ မတော်တဆ ခေါ်မရအောင် POST သာခွင့်ပြုသည်။"),
            _example("Create with an explicit status", "return JsonResponse({\"id\": 7, \"name\": \"Mya\"}, status=201)", "HTTP 201", "A new in-memory student was accepted.", "201 communicates creation instead of generic success.", "201 သည် generic success မဟုတ်ဘဲ creation ကို ဖော်ပြသည်။"),
            _example("Return a missing-resource error", "from django.http import Http404\n\ndef student(request, student_id):\n    if student_id != 7:\n        raise Http404(\"Student not found\")\n    return JsonResponse({\"id\": 7})", "Unknown IDs receive HTTP 404", "student_id is converted by the URL route.", "Do not reveal whether a protected object exists through verbose errors.", "Protected object ရှိ/မရှိကို verbose error ဖြင့် မဖော်ပြပါနှင့်။"),
        ],
        "exercises": "Create a JSON endpoint with GET search and POST create behavior. Test 200, 201, 400 invalid payload, 405 wrong method, and 404 missing ID. Add a CSRF-protected HTML form test using the real test client.",
        "exercises_mm": "GET search နှင့် POST create ပါသော JSON endpoint တည်ဆောက်ပါ။ 200၊ 201၊ 400 invalid payload၊ 405 wrong method နှင့် 404 missing ID test များရေးပါ။ Real test client ဖြင့် CSRF-protected HTML form test ထည့်ပါ။",
        "homework": "HTTP Status Decision Log: for ten Student Portal scenarios, choose method, response class, status code, and whether CSRF applies. Explain every choice.",
        "homework_mm": "HTTP Status Decision Log ပြုလုပ်ပါ။ Student Portal scenario ၁၀ ခုအတွက် method၊ response class၊ status code နှင့် CSRF လို/မလို ရွေးပြီး အကြောင်းပြချက်ရေးပါ။",
        "summary": "Requests carry untrusted input; responses communicate both data and the truthful outcome through content type and status code.",
        "summary_mm": "Request သည် မယုံကြည်ရသော input ကို သယ်ဆောင်ပြီး response သည် content type နှင့် မှန်ကန်သော status code ဖြင့် outcome ကို ပြောပြသည်။",
        "quiz": [
            _q("Where are query-string values read?", ["request.GET", "request.POST only", "request.COOKIES only", "settings.URL"], "request.GET", "GET carries query-string data."),
            _q("Which request is preferred for a state-changing form?", ["POST", "GET", "HEAD only", "TRACE"], "POST", "POST communicates a state-changing submission."),
            _q("Which class returns JSON?", ["JsonResponse", "Http404", "HttpResponseNotAllowed only", "URLPattern"], "JsonResponse", "It serializes a JSON-compatible value."),
            _q("What does 201 communicate?", ["A resource was created", "The resource is missing", "The method is forbidden", "A server crashed"], "A resource was created", "201 is the creation success status."),
            _q("True or false: CSRF should be disabled for convenience.", ["True", "False"], "False", "CSRF protects browser-based state-changing requests."),
            _q("What status represents a wrong method?", ["405", "200", "201", "304"], "405", "405 means method not allowed."),
            _q("What should happen to raw user input before HTML output?", ["Validate and escape it through the chosen rendering path", "Trust it", "Use it as a template", "Put it in a password"], "Validate and escape it through the chosen rendering path", "Input is not trusted merely because it came from a form.", "intermediate"),
            _q("Why is returning 500 for invalid form data wrong?", ["It mislabels client input as a server failure", "500 is always faster", "It enables CSRF", "It creates a URL"], "It mislabels client input as a server failure", "Validation failures should not look like infrastructure failures.", "intermediate"),
        ],
    },
    {
        "title": "Dynamic URLs and Route Parameters",
        "slug": "03-dynamic-urls-and-route-parameters",
        "topic": "path converters, dynamic IDs, slugs, validation, 404, and route security",
        "description": "Build detail routes with integer IDs and slugs while keeping lookup and authorization explicit.",
        "description_mm": "Integer ID နှင့် slug detail route များကို lookup/authorization ရှင်းလင်းစွာဖြင့် တည်ဆောက်ပါ။",
        "syntax": "path(\"<int:student_id>/\", views.detail, name=\"detail\")\npath(\"<slug:slug>/\", views.by_slug, name=\"by-slug\")",
        "syntax_mm": "path(\"<int:student_id>/\", views.detail, name=\"detail\")\npath(\"<slug:slug>/\", views.by_slug, name=\"by-slug\")",
        "theory": "Dynamic routes capture a portion of a path and pass it as a keyword argument to the view. Built-in converters such as int, slug, uuid, str, and path perform basic shape matching; they do not prove that a record exists or that the current user may access it. Choose IDs for stable identity and slugs for readable public URLs. Validate lookup results, return 404 when a public resource is absent, and apply authorization before exposing private data. Always reverse the named route with the same keyword names used by the pattern.",
        "theory_mm": "Dynamic route သည် path အပိုင်းတစ်ခုကို ဖမ်းယူပြီး view သို့ keyword argument အဖြစ် ပို့သည်။ int၊ slug၊ uuid၊ str နှင့် path converter များက shape ကိုသာ စစ်သည်။ Record ရှိကြောင်း သို့မဟုတ် current user ကြည့်ခွင့်ရှိကြောင်း မသက်သေပြပါ။ Stable identity အတွက် ID၊ ဖတ်ရလွယ်သော public URL အတွက် slug သုံးနိုင်သည်။ Lookup result ကို validate လုပ်ပြီး public resource မရှိလျှင် 404 ပြန်ပါ။ Private data မပြမီ authorization လုပ်ပါ။ Named route ကို pattern တွင်သုံးသော keyword name အတိုင်း reverse လုပ်ပါ။",
        "concepts": "Converters, keyword arguments, IDs versus slugs, lookup, 404, authorization, canonical URLs, and URL reversing.",
        "concepts_mm": "Converter၊ keyword argument၊ ID နှင့် slug၊ lookup၊ 404၊ authorization၊ canonical URL နှင့် URL reversing တို့ကို လေ့လာရမည်။",
        "mistakes": ["Using <str:student_id> and assuming it is an integer.", "Looking up by slug but reversing with a different keyword.", "Returning a private object's existence through different errors.", "Using path converter for arbitrary nested input without a clear contract."],
        "mistakes_mm": ["<str:student_id> သုံးပြီး integer ဖြစ်သည်ဟု ယူဆခြင်း။", "Slug ဖြင့် lookup လုပ်သော်လည်း keyword မတူဘဲ reverse ခြင်း။", "Private object ရှိ/မရှိကို error မတူခြင်းဖြင့် ဖော်ပြခြင်း။", "ရှင်းလင်းသော contract မရှိဘဲ arbitrary nested input အတွက် path converter သုံးခြင်း။"],
        "best_practices": "Use the narrowest converter, keep parameter names stable, normalize slugs, use get_object_or_404, and separate lookup from permission checks.",
        "best_practices_mm": "အကျဉ်းမြောင်းဆုံး converter သုံးပါ၊ parameter name တည်ငြိမ်စွာထားပါ၊ slug normalize လုပ်ပါ၊ get_object_or_404 သုံးပြီး lookup နှင့် permission check ခွဲပါ။",
        "examples": [
            _example("Integer detail route", "path(\"<int:student_id>/\", views.detail, name=\"detail\")\n\ndef detail(request, student_id):\n    return JsonResponse({\"student_id\": student_id})", "GET /students/7/ returns 7", "The converter accepts digits and passes an int.", "The int converter rejects a non-numeric path before the view.", "int converter သည် digit မဟုတ်သော path ကို view မရောက်မီ ငြင်းပယ်သည်။"),
            _example("Slug route", "path(\"<slug:slug>/\", views.by_slug, name=\"by-slug\")\n\ndef by_slug(request, slug):\n    return JsonResponse({\"slug\": slug.lower()})", "GET /students/mya-7/ returns mya-7", "The slug is a readable identifier.", "Normalize for comparison, but preserve canonical redirect rules separately.", "Comparison အတွက် normalize လုပ်သော်လည်း canonical redirect rule ကို သီးခြားထားပါ။"),
            _example("Reverse with matching keywords", "reverse(\"students:detail\", kwargs={\"student_id\": 7})\nreverse(\"students:by-slug\", kwargs={\"slug\": \"mya-7\"})", "'/students/7/' and '/students/mya-7/'", "Both routes are named and namespaced.", "Keyword names must match the route declaration.", "Keyword name သည် route declaration နှင့် ကိုက်ညီရမည်။"),
            _example("Lookup and permission boundary", "student = get_object_or_404(Student, pk=student_id)\nif student.owner_id != request.user.id:\n    return HttpResponse(status=403)\nreturn render(request, \"students/detail.html\", {\"student\": student})", "Existing unauthorized record returns 403", "The object exists but belongs to another user.", "Existence and permission are separate decisions.", "Object ရှိမှုနှင့် permission သည် သီးခြားဆုံးဖြတ်ချက်များ ဖြစ်သည်။"),
        ],
        "exercises": "Add integer detail and slug detail routes to the Student Portal. Test valid and invalid converter input, missing records, reverse URLs, and an authenticated user attempting to view another user's private record.",
        "exercises_mm": "Student Portal တွင် integer detail နှင့် slug detail route ထည့်ပါ။ Valid/invalid converter input၊ missing record၊ reverse URL နှင့် အခြား user ၏ private record ကို ကြည့်ရန် ကြိုးစားမှုကို test လုပ်ပါ။",
        "homework": "Canonical URL Plan: decide whether each Student Portal page uses an ID or slug, document collision/rename behavior, and define the safe error policy for private records.",
        "homework_mm": "Canonical URL Plan ပြုလုပ်ပါ။ Student Portal page တစ်ခုစီတွင် ID သို့မဟုတ် slug ရွေးပါ။ Collision/rename behavior နှင့် private record အတွက် safe error policy ရေးပါ။",
        "summary": "Converters validate path shape; the view must still perform lookup, authorization, and safe error handling.",
        "summary_mm": "Converter သည် path shape ကိုသာ validate လုပ်ပြီး lookup၊ authorization နှင့် safe error handling ကို view က ဆက်လက်လုပ်ရသည်။",
        "quiz": [
            _q("What does <int:id> guarantee?", ["The captured value contains digits and is converted to int", "The row exists", "The user is authorized", "The URL is public"], "The captured value contains digits and is converted to int", "Converters do shape conversion only."),
            _q("Which converter is suited to readable hyphenated identifiers?", ["slug", "int", "uuid only", "path always"], "slug", "slug accepts URL-safe slug-like values."),
            _q("What should a missing public object return?", ["404", "200 with empty secret data", "201", "302 always"], "404", "The resource is not found."),
            _q("True or false: a valid converter proves authorization.", ["True", "False"], "False", "Authorization is a separate check."),
            _q("What must reverse kwargs match?", ["The converter parameter names", "The template filename", "The database port", "The CSS class"], "The converter parameter names", "Names are part of the URL contract."),
            _q("Why choose a narrow converter?", ["It rejects malformed paths early", "It disables all views", "It writes migrations", "It reveals secrets"], "It rejects malformed paths early", "Narrow input shape reduces ambiguity."),
            _q("What status can represent an existing but unauthorized record?", ["403 or a deliberately uniform policy response", "201", "304 always", "204 only"], "403 or a deliberately uniform policy response", "The policy must avoid leaking sensitive existence information.", "intermediate"),
            _q("What is a slug commonly used for?", ["A readable stable URL identifier", "A password hash", "A response body", "A database connection"], "A readable stable URL identifier", "Slugs are convenient public identifiers when their lifecycle is designed."),
        ],
    },
    {
        "title": "Django Configuration and Application Settings",
        "slug": "03-django-configuration-and-application-settings",
        "topic": "DEBUG, ALLOWED_HOSTS, INSTALLED_APPS, environment configuration, and safe settings",
        "description": "Separate environment configuration from code and understand the settings that shape a Django app.",
        "description_mm": "Environment configuration ကို code မှခွဲပြီး Django application settings အဓိကများကို နားလည်ပါ။",
        "syntax": "DEBUG = False\nALLOWED_HOSTS = [\"example.com\"]\nINSTALLED_APPS = [\"students\"]",
        "syntax_mm": "DEBUG = False\nALLOWED_HOSTS = [\"example.com\"]\nINSTALLED_APPS = [\"students\"]",
        "theory": "Settings are executable Python configuration, so they must be deliberate and environment-aware. DEBUG helps development diagnostics but must be false in production. ALLOWED_HOSTS validates the Host header and should contain approved domains, not a casual wildcard. INSTALLED_APPS registers Django and project applications. Keep SECRET_KEY, database credentials, and provider tokens out of source control; read them from a secret manager or environment with validation. A settings change can affect security, routing, templates, migrations, and deployment, so use system checks and a reviewable configuration policy.",
        "theory_mm": "Settings သည် executable Python configuration ဖြစ်သောကြောင့် ရည်ရွယ်ချက်ရှိပြီး environment-aware ဖြစ်ရမည်။ DEBUG သည် development diagnostic အတွက် အသုံးဝင်သော်လည်း production တွင် false ဖြစ်ရမည်။ ALLOWED_HOSTS သည် Host header ကို validate လုပ်ပြီး အတည်ပြုထားသော domain များပါရမည်။ INSTALLED_APPS သည် Django နှင့် project app များကို register လုပ်သည်။ SECRET_KEY၊ database credential နှင့် provider token များကို source control ထဲမထည့်ဘဲ secret manager/environment မှ validate လုပ်ပြီး ဖတ်ပါ။ Settings change သည် security၊ routing၊ template၊ migration နှင့် deployment ကို ထိခိုက်နိုင်သဖြင့် system check နှင့် reviewable policy သုံးပါ။",
        "concepts": "Environment separation, DEBUG, ALLOWED_HOSTS, INSTALLED_APPS, secret injection, system checks, and deployment configuration.",
        "concepts_mm": "Environment ခွဲခြားမှု၊ DEBUG၊ ALLOWED_HOSTS၊ INSTALLED_APPS၊ secret injection၊ system check နှင့် deployment configuration တို့ကို လေ့လာရမည်။",
        "mistakes": ["Leaving DEBUG=True in production.", "Committing secrets in settings.py.", "Using ALLOWED_HOSTS=['*'] without a controlled reason.", "Adding an app but forgetting its import/configuration requirements."],
        "mistakes_mm": ["Production တွင် DEBUG=True ထားခြင်း။", "settings.py ထဲ secret ထည့်ပြီး commit လုပ်ခြင်း။", "ထိန်းချုပ်ထားသောအကြောင်းမရှိဘဲ ALLOWED_HOSTS=['*'] သုံးခြင်း။", "App ထည့်ပြီး import/configuration လိုအပ်ချက် မစစ်ခြင်း။"],
        "best_practices": "Use separate environment values, fail closed for missing production secrets, run manage.py check --deploy, and review settings as security-sensitive code.",
        "best_practices_mm": "Environment value သီးခြားသုံးပါ၊ production secret မရှိလျှင် fail closed လုပ်ပါ၊ manage.py check --deploy run ပြီး settings ကို security-sensitive code အဖြစ် review လုပ်ပါ။",
        "examples": [
            _example("Safe environment boolean", "import os\n\nDEBUG = os.environ.get(\"DJANGO_DEBUG\", \"false\").lower() == \"true\"", "DEBUG is False unless explicitly enabled", "DJANGO_DEBUG is absent in production.", "A conservative default prevents accidental debug exposure.", "Conservative default သည် debug exposure မဖြစ်စေရန် ကာကွယ်သည်။"),
            _example("Parse approved hosts", "import os\n\nALLOWED_HOSTS = [\n    host.strip()\n    for host in os.environ.get(\"DJANGO_ALLOWED_HOSTS\", \"\").split(\",\")\n    if host.strip()\n]", "['example.com', 'www.example.com']", "DJANGO_ALLOWED_HOSTS=example.com,www.example.com", "Whitespace and empty values are removed before Django validates the list.", "Whitespace နှင့် empty value များကို Django validation မတိုင်မီ ဖယ်ရှားသည်။"),
            _example("Register a local app", "INSTALLED_APPS = [\n    \"django.contrib.auth\",\n    \"django.contrib.contenttypes\",\n    \"students.apps.StudentsConfig\",\n]", "StudentsConfig is discoverable", "students/apps.py exists and is importable.", "The explicit config path makes app ownership visible.", "Explicit config path သည် app ownership ကို မြင်သာစေသည်။"),
            _example("Fail closed for a secret", "import os\n\nSECRET_KEY = os.environ.get(\"DJANGO_SECRET_KEY\")\nif not SECRET_KEY:\n    raise RuntimeError(\"DJANGO_SECRET_KEY is required\")", "Startup stops without a secret", "Production environment omits the secret.", "A missing security-critical value should fail early rather than use a public fallback.", "Security-critical value မရှိလျှင် public fallback မသုံးဘဲ အစောပိုင်း fail လုပ်ရမည်။"),
        ],
        "exercises": "Create development and production settings examples. Write tests for boolean parsing, host parsing, and missing secret behavior. Run manage.py check and explain which warnings are security-sensitive.",
        "exercises_mm": "Development နှင့် production settings example ပြုလုပ်ပါ။ Boolean parsing၊ host parsing နှင့် missing secret behavior အတွက် test ရေးပါ။ manage.py check run ပြီး security-sensitive warning များကို ရှင်းပြပါ။",
        "homework": "Configuration Threat Model: list ten values that should be configuration or secrets, their safe source, their development default (if any), and the failure behavior when missing.",
        "homework_mm": "Configuration Threat Model ပြုလုပ်ပါ။ Configuration/secret ဖြစ်သင့်သော value ၁၀ ခု၊ safe source၊ development default (ရှိလျှင်) နှင့် မရှိပါက failure behavior ရေးပါ။",
        "summary": "Django settings are code with security consequences; safe defaults and environment separation matter.",
        "summary_mm": "Django settings သည် security consequence ရှိသော code ဖြစ်ပြီး safe default နှင့် environment ခွဲခြားမှု အရေးကြီးသည်။",
        "quiz": [
            _q("What should DEBUG be in production?", ["False", "True always", "The database name", "A URL name"], "False", "Debug pages can expose sensitive details."),
            _q("What does ALLOWED_HOSTS validate?", ["The HTTP Host header", "POST passwords", "Template syntax", "URL names"], "The HTTP Host header", "It limits accepted hostnames."),
            _q("What does INSTALLED_APPS do?", ["Registers Django and project applications", "Stores student progress", "Creates a browser", "Sets a response status"], "Registers Django and project applications", "Installed apps participate in Django discovery."),
            _q("Where should production secrets live?", ["A secret manager or protected environment", "A public repository", "A template", "A URL parameter"], "A secret manager or protected environment", "Secrets should not be committed."),
            _q("True or false: a development default can be copied unchanged to production.", ["True", "False"], "False", "Environments have different security and operational requirements."),
            _q("Which command checks deployment warnings?", ["python manage.py check --deploy", "python manage.py startapp --deploy", "python manage.py urls", "python manage.py publish"], "python manage.py check --deploy", "Django provides deployment-oriented system checks."),
            _q("What does fail closed mean for a missing required secret?", ["Stop rather than use an unsafe fallback", "Print the secret", "Use an empty password", "Enable DEBUG"], "Stop rather than use an unsafe fallback", "Security-critical configuration should not silently degrade.", "intermediate"),
            _q("Why should settings changes be reviewed?", ["They affect security and runtime behavior", "They are only comments", "They cannot affect deployment", "They replace tests"], "They affect security and runtime behavior", "Configuration is part of the application contract.", "intermediate"),
        ],
    },
]


def _render_en(item: dict) -> str:
    examples = []
    for index, example in enumerate(item["examples"], 1):
        examples.append(
            f"Example {index}: {example['title']}\n"
            f"Input: {example['input']}\n"
            f"Code:\n```python\n{example['code']}\n```\n"
            f"Expected output: {example['output']}\n"
            f"Line-by-line explanation: {example['explanation']}\n"
            "Check the route, request boundary, and response status before moving on."
        )
    mistakes = "\n".join(f"- {value}" for value in item["mistakes"])
    quiz = "\n".join(f"{i}. {q['prompt']} Options: {', '.join(q['options'])}" for i, q in enumerate(item["quiz"], 1))
    example_text = "\n\n".join(examples)
    return dedent(f"""
        # {item['title']}

        ## Introduction
        {item['description']}

        ## Prerequisites
        Complete Module 01 and Module 02, know basic Python functions and dictionaries, and be able to use a terminal and a virtual environment. Django-specific examples should be run with the course's supported Django version.

        ## Learning objectives
        1. Explain {item['topic']}.
        2. Identify the input and output of each framework boundary.
        3. Implement the syntax in a small, testable Django feature.
        4. Choose safe error handling and meaningful HTTP behavior.

        ## Detailed theory
        {item['theory']}

        ## Core concepts
        {item['concepts']}

        ## Syntax and API reference
        ```python
        {item['syntax']}
        ```
        Read each argument as a contract: what enters, what is validated, what is returned, and what can fail. Prefer named APIs and official documentation over copying a snippet without understanding its boundary.

        ## Guided examples
        {example_text}

        ## Common mistakes
        {mistakes}

        ## Best practices
        {item['best_practices']}

        ## Exercises
        {item['exercises']}

        ## Independent practice
        Implement the exercise without copying the guided examples. Add one normal case, one boundary case, and one failure case. Record the command and actual output in your notes.

        ## Homework
        {item['homework']}

        ## Lesson quiz
        {quiz}
        Answer from your own reasoning, then run or inspect the relevant test. The answer key is kept private in the reviewable assessment data.

        ## Summary
        {item['summary']}

        ## Further reading
        Read the official Django documentation for URL dispatching, request/response objects, and settings. Compare the documented behavior with your tests and note any version-specific detail.
    """).strip()


def _render_mm(item: dict) -> str:
    examples = []
    for index, example in enumerate(item["examples"], 1):
        examples.append(
            f"နမူနာ {index}: {example['title']}\n"
            f"Input: {example['input']}\n"
            f"Code:\n```python\n{example['code']}\n```\n"
            f"မျှော်မှန်းရလဒ်: {example['output']}\n"
            f"ရှင်းလင်းချက်: {example['explanation_mm']}\n"
            "နောက်တစ်ဆင့်မတက်မီ route၊ request boundary နှင့် response status ကို စစ်ပါ။"
        )
    mistakes = "\n".join(f"- {value}" for value in item["mistakes_mm"])
    quiz = "\n".join(f"{i}. {q['prompt']} Options: {', '.join(q['options'])}" for i, q in enumerate(item["quiz"], 1))
    example_text = "\n\n".join(examples)
    return dedent(f"""
        # {item['title']}

        ## မိတ်ဆက်
        {item['description_mm']}

        ## ကြိုတင်လိုအပ်ချက်
        Module 01 နှင့် Module 02 ပြီးထားရမည်။ Python function နှင့် dictionary အခြေခံကို သိရမည်။ Terminal နှင့် virtual environment သုံးနိုင်ရမည်။ Django example များကို course က သတ်မှတ်ထားသော Django version ဖြင့် run ပါ။

        ## သင်ယူရမည့်ရည်မှန်းချက်
        ၁။ {item['topic']} ကို ရှင်းပြနိုင်ရန်။
        ၂။ Framework boundary တစ်ခုစီ၏ input နှင့် output ကို ခွဲခြားနိုင်ရန်။
        ၃။ ဤ syntax ကို သေးငယ်ပြီး test လုပ်နိုင်သော Django feature တွင် အသုံးချနိုင်ရန်။
        ၄။ Safe error handling နှင့် အဓိပ္ပာယ်ရှိသော HTTP behavior ကို ရွေးနိုင်ရန်။

        ## အသေးစိတ်သီအိုရီ
        {item['theory_mm']}

        ## အဓိက concept များ
        {item['concepts_mm']}

        ## Syntax နှင့် API reference
        ```python
        {item['syntax_mm']}
        ```
        Argument တစ်ခုစီကို contract အဖြစ်စဉ်းစားပါ။ ဘာဝင်လာသလဲ၊ ဘာ validate လုပ်သလဲ၊ ဘာပြန်သလဲ၊ ဘာအမှားဖြစ်နိုင်သလဲကို ရေးမှတ်ပါ။ Official documentation နှင့် test ရလဒ်ကို အခြေခံပါ။

        ## လမ်းညွှန်နမူနာများ
        {example_text}

        ## အများဆုံးမှားတတ်သောအချက်များ
        {mistakes}

        ## အကောင်းဆုံးနည်းလမ်းများ
        {item['best_practices_mm']}

        ## လေ့ကျင့်ခန်းများ
        {item['exercises_mm']}

        ## ကိုယ်တိုင်လေ့ကျင့်ရန်
        Guided example ကို မကူးဘဲ exercise ကို ကိုယ်တိုင်ရေးပါ။ Normal case တစ်ခု၊ boundary case တစ်ခုနှင့် failure case တစ်ခု ထည့်ပါ။ Run command နှင့် အမှန်တကယ်ရလဒ်ကို မှတ်တမ်းတင်ပါ။

        ## အိမ်စာ
        {item['homework_mm']}

        ## Lesson quiz
        {quiz}
        ကိုယ်တိုင်စဉ်းစားပြီးမှ သက်ဆိုင်ရာ test သို့မဟုတ် code ဖြင့် စစ်ဆေးပါ။ အဖြေ key ကို reviewable assessment data ထဲတွင်သာ သိမ်းထားသည်။

        ## အနှစ်ချုပ်
        {item['summary_mm']}

        ## ဆက်လက်ဖတ်ရှုရန်
        Django official documentation တွင် URL dispatching၊ request/response object နှင့် settings အပိုင်းများကို ဖတ်ပါ။ Documentation behavior နှင့် test ရလဒ်ကို နှိုင်းယှဉ်ပြီး version-specific အချက်များကို မှတ်ပါ။
    """).strip()


def _module_assessment():
    questions = [_q(item["quiz"][0]["prompt"], item["quiz"][0]["options"], item["quiz"][0]["correct_answer"], item["quiz"][0]["explanation"], item["quiz"][0]["difficulty"]) for item in LESSONS]
    questions.extend([
        _q("Which layer should own a route name?", ["URL configuration", "A password file", "A CSS rule", "A database row"], "URL configuration", "URL configuration declares route names.", "beginner"),
        _q("What is the safest default for a missing production secret?", ["Stop startup", "Use a public fallback", "Print it", "Enable DEBUG"], "Stop startup", "Fail closed for security-critical configuration.", "intermediate"),
        _q("What does a converter do?", ["Shape conversion and matching", "Authorization", "Database migration", "Template escaping"], "Shape conversion and matching", "A converter is not a permission policy.", "intermediate"),
        _q("Which code is appropriate after a successful create?", ["201", "404", "405", "500"], "201", "201 communicates resource creation.", "beginner"),
        _q("Why use POST/redirect/GET?", ["Prevent duplicate form submission on refresh", "Skip validation", "Make a secret public", "Disable CSRF"], "Prevent duplicate form submission on refresh", "The redirect separates the mutation from the refreshable GET.", "intermediate"),
        _q("What does include() enable?", ["An app to own child URL patterns", "A model to own passwords", "A template to run SQL", "A response to become a migration"], "An app to own child URL patterns", "include delegates a prefix.", "beginner"),
        _q("Which setting must be reviewed before production?", ["DEBUG", "A CSS color only", "A lesson bookmark", "A local screenshot"], "DEBUG", "Debug configuration can expose sensitive details.", "intermediate"),
        _q("What should be tested for a dynamic detail route?", ["Valid input, invalid shape, missing record, and authorization", "Only the URL color", "Only the file name", "Nothing"], "Valid input, invalid shape, missing record, and authorization", "The route contract has multiple observable boundaries.", "intermediate"),
        _q("What is the purpose of app_name?", ["Namespace URL names", "Create an app database", "Set DEBUG", "Choose a status code"], "Namespace URL names", "Namespaces prevent collisions.", "beginner"),
        _q("Which value should never be fabricated in a student API response?", ["A success claim for an operation that did not happen", "A documented status", "A validated ID", "An empty result list"], "A success claim for an operation that did not happen", "Responses must reflect confirmed backend state.", "intermediate"),
        _q("Which setting belongs in a production configuration review?", ["ALLOWED_HOSTS", "A lesson screenshot", "A browser bookmark", "A CSS comment"], "ALLOWED_HOSTS", "Host validation is part of deployment safety.", "intermediate"),
    ])
    return questions[:18]


def _ensure_examples(db, lesson, item):
    rows = db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all()
    for position, example in enumerate(item["examples"], 1):
        values = {"title": example["title"], "language": "python", "filename": f"lesson-{lesson.order_index:02d}.py", "code": example["code"], "description": f"Input: {example['input']}\nExpected output: {example['output']}\n\n{example['explanation']}", "position": position}
        if position <= len(rows):
            for key, value in values.items():
                setattr(rows[position - 1], key, value)
        else:
            db.add(CodeExample(lesson_id=lesson.id, **values))


def _ensure_quiz(db, lesson, item):
    quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
    if not quiz:
        quiz = LessonQuiz(lesson_id=lesson.id, title=f"{item['title']} knowledge check", explanation="Review the lesson examples and explain the boundary behind each answer.", status="draft")
        db.add(quiz)
        db.flush()
    quiz.title = f"{item['title']} knowledge check"
    quiz.explanation = "Review the lesson examples and explain the boundary behind each answer."
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
    values = {"title": f"{item['title']} practice", "description_en": item["exercises"], "description_mm": item["exercises_mm"], "difficulty": "intermediate" if lesson.order_index >= 3 else "beginner", "language": "python", "starter_code": "# Implement this exercise in the Student Portal project.\n", "status": "draft"}
    if exercise:
        for key, value in values.items():
            setattr(exercise, key, value)
    else:
        db.add(CodingExercise(lesson_id=lesson.id, slug=f"django-fundamentals-{lesson.order_index}-practice", **values))


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
            SECRET_KEY = "development-only-change-me"
            DEBUG = True
            ALLOWED_HOSTS = []
            ROOT_URLCONF = "school_site.urls"
            INSTALLED_APPS = ["django.contrib.contenttypes", "students", "courses"]
            MIDDLEWARE = []
            TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True}]
            DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
        ''').strip() + "\n",
        "school_site/urls.py": dedent('''
            from django.urls import include, path

            urlpatterns = [
                path("students/", include("students.urls")),
                path("courses/", include("courses.urls")),
            ]
        ''').strip() + "\n",
        "students/__init__.py": "",
        "students/apps.py": dedent('''
            from django.apps import AppConfig

            class StudentsConfig(AppConfig):
                default_auto_field = "django.db.models.BigAutoField"
                name = "students"
        ''').strip() + "\n",
        "students/urls.py": dedent('''
            from django.urls import path
            from . import views

            app_name = "students"
            urlpatterns = [
                path("", views.home, name="home"),
                path("<int:student_id>/", views.detail, name="detail"),
                path("slug/<slug:slug>/", views.by_slug, name="by-slug"),
            ]
        ''').strip() + "\n",
        "students/views.py": dedent('''
            from django.http import Http404, JsonResponse
            from django.shortcuts import render

            STUDENTS = [
                {"id": 1, "slug": "mya-htet", "name": "Mya Htet", "track": "Django"},
                {"id": 2, "slug": "ko-min", "name": "Ko Min", "track": "Python"},
            ]

            def home(request):
                return render(request, "students/home.html", {"students": STUDENTS})

            def detail(request, student_id):
                student = next((row for row in STUDENTS if row["id"] == student_id), None)
                if student is None:
                    raise Http404("Student not found")
                return JsonResponse(student)

            def by_slug(request, slug):
                student = next((row for row in STUDENTS if row["slug"] == slug), None)
                if student is None:
                    raise Http404("Student not found")
                return JsonResponse(student)
        ''').strip() + "\n",
        "courses/__init__.py": "",
        "courses/apps.py": dedent('''
            from django.apps import AppConfig

            class CoursesConfig(AppConfig):
                default_auto_field = "django.db.models.BigAutoField"
                name = "courses"
        ''').strip() + "\n",
        "courses/urls.py": dedent('''
            from django.urls import path
            from . import views

            app_name = "courses"
            urlpatterns = [path("", views.home, name="home")]
        ''').strip() + "\n",
        "courses/views.py": dedent('''
            from django.http import JsonResponse

            COURSES = [
                {"slug": "django-fundamentals", "title": "Django Fundamentals"},
                {"slug": "python-foundations", "title": "Python Foundations"},
            ]

            def home(request):
                return JsonResponse({"courses": COURSES})
        ''').strip() + "\n",
        "students/tests.py": dedent('''
            from django.test import SimpleTestCase
            from django.urls import reverse

            class StudentPortalTests(SimpleTestCase):
                def test_home_and_detail(self):
                    self.assertEqual(self.client.get(reverse("students:home")).status_code, 200)
                    self.assertEqual(self.client.get(reverse("students:detail", args=[1])).status_code, 200)
                    self.assertEqual(self.client.get(reverse("students:detail", args=[99])).status_code, 404)

                def test_slug_route(self):
                    response = self.client.get(reverse("students:by-slug", kwargs={"slug": "mya-htet"}))
                    self.assertEqual(response.json()["track"], "Django")
        ''').strip() + "\n",
    }


def _ensure_project(db, course, module):
    slug = "django-student-portal-fundamentals"
    source_files = _project_source_files()
    brief = {
        "goal": "Build a complete Student Portal with Django fundamentals.",
        "scope": "Module 03 only; the dataset is intentionally in memory and is not PostgreSQL persistence.",
        "setup_commands": ["python -m venv .venv", "pip install Django", "python manage.py check", "python manage.py test", "python manage.py runserver"],
        "sample_routes": ["/students/", "/students/1/", "/students/slug/mya-htet/", "/courses/"],
        "source_files": source_files,
        "expected_outputs": ["Student home returns 200", "Known detail returns JSON 200", "Unknown detail returns 404", "Course endpoint returns two in-memory course records"],
        "troubleshooting": ["Run commands from the directory containing manage.py.", "Install the supported Django version in the virtual environment.", "The sample data is in memory and resets when the process restarts.", "Do not add PostgreSQL models in this project; persistence is a later module concern."],
        "extensions": ["Add a validated POST form with CSRF.", "Add tests for method handling and 400 validation.", "Replace the in-memory boundary with models only after the relevant later module."],
    }
    project = db.scalar(select(ProjectTemplate).where(ProjectTemplate.slug == slug))
    values = {"title": "Student Portal — Django Fundamentals", "description_en": "Build a small two-app Django Student Portal with in-memory students and courses, named URLs, dynamic detail routes, correct response codes, and tests.", "description_mm": "In-memory student နှင့် course data၊ named URL၊ dynamic detail route၊ မှန်ကန်သော response code နှင့် test များပါသော Django Student Portal တစ်ခု တည်ဆောက်ပါ။", "difficulty": "beginner", "estimated_hours": 10, "requirements": "Python 3, virtual environment, supported Django version, terminal, and basic Python functions.", "learning_outcomes": "Explain project/app boundaries; write routes and function-based views; handle requests and responses; test dynamic routes; keep sample data in memory.", "technology_stack": "Python | Django | HTML | JSON | Django test client", "prerequisites": "Complete Django Modules 01 and 02.", "architecture_overview": "school_site owns settings and root URLs; students owns student routes and views; courses owns course routes and views; tests verify public behavior.", "folder_structure": "\n".join(source_files.keys()), "testing_guide": "Run python manage.py check followed by python manage.py test. Confirm the actual status codes and JSON body.", "deployment_guide": "This learning project is intentionally in-memory. Do not treat it as production persistence and do not deploy with DEBUG enabled.", "tags_json": json.dumps(["django", "urls", "views", "http", "student-portal"], ensure_ascii=False), "languages_json": json.dumps(["Python", "HTML"], ensure_ascii=False), "brief_json": json.dumps(brief, ensure_ascii=False), "status": "draft", "published": False}
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
        ("Project setup and app boundaries", "Create school_site, students, and courses; register the apps and root includes.", "school_site/settings.py and school_site/urls.py", "manage.py check passes."),
        ("Student routes and views", "Add home, integer detail, slug detail, named URLs, and 404 behavior.", "students/views.py and students/urls.py", "Known and unknown student routes return expected statuses."),
        ("Course endpoint and HTTP contract", "Add the course app and document GET/POST/status-code decisions.", "courses/views.py and courses/urls.py", "Course response is JSON and contains the in-memory records."),
        ("Tests and review", "Run checks and tests, record output, and explain why the dataset is not persisted.", "students/tests.py", "python manage.py test passes with 200 and 404 assertions."),
    ]
    for position, (title, description, filename, output) in enumerate(milestones, 1):
        row = db.scalar(select(ProjectMilestone).where(ProjectMilestone.project_id == project.id, ProjectMilestone.position == position))
        data = {"title": title, "slug": f"student-portal-{position}", "description_en": description, "description_mm": description + " ကို လက်တွေ့ပြုလုပ်ပါ။", "content_en": f"Required source boundary: {filename}\n\n{description}\n\nThe dataset remains in memory; do not add PostgreSQL persistence in this module.", "content_mm": "ဤ milestone တွင် source file များကို တည်ဆောက်ပြီး in-memory data boundary ကို ထိန်းသိမ်းပါ။", "code": source_files.get(filename, ""), "filename": filename, "expected_output": output, "line_explanation": "Read configuration first, then route ownership, then view input/output, and finally the assertion that proves behavior.", "completion_criteria": "The learner runs the focused command, records actual output, and explains one failure case.", "resources_json": json.dumps([{"title": "Django URL dispatcher", "url": "https://docs.djangoproject.com/en/stable/topics/http/urls/"}, {"title": "Django request and response", "url": "https://docs.djangoproject.com/en/stable/ref/request-response/"}], ensure_ascii=False), "required": True}
        if not row:
            db.add(ProjectMilestone(project_id=project.id, position=position, **data))
        else:
            for key, value in data.items():
                setattr(row, key, value)
    requirement = db.scalar(select(ProjectRequirement).where(ProjectRequirement.project_id == project.id, ProjectRequirement.position == 1))
    req = {"title": "Complete tested in-memory Student Portal", "description": "Implement the two-app project, routes, views, response semantics, and tests without adding a PostgreSQL persistence layer.", "acceptance_criteria": "All source files exist; check and tests pass; list/detail/course routes work; invalid and missing cases are handled; no secrets are committed; sample data is explicitly in memory.", "required": True}
    if not requirement:
        db.add(ProjectRequirement(project_id=project.id, position=1, **req))
    else:
        for key, value in req.items():
            setattr(requirement, key, value)
    rubric = [("Routing", "Named root and app routes, dynamic converters, and reverse usage are correct.", 25), ("Views and HTTP", "Views validate boundaries and return useful responses/status codes.", 25), ("Tests", "Tests cover normal, missing, invalid, and route contract behavior.", 25), ("Safety and scope", "No secrets, no PostgreSQL persistence, and clear in-memory limitations.", 15), ("Documentation", "Setup, output, troubleshooting, and extension path are explained.", 10)]
    for position, (name, description, weight) in enumerate(rubric, 1):
        criterion = db.scalar(select(ProjectRubricCriterion).where(ProjectRubricCriterion.project_id == project.id, ProjectRubricCriterion.position == position))
        if not criterion:
            db.add(ProjectRubricCriterion(project_id=project.id, position=position, name=name, description=description, weight=weight))
        else:
            criterion.name, criterion.description, criterion.weight = name, description, weight
    return project


SYNTAX_REFERENCES = [
    {"slug": "django-admin-startproject", "title": "django-admin startproject", "lesson": 2, "syntax": "django-admin startproject school_site .", "description": "Creates a Django project package and its initial command/settings boundary.", "examples": [("Create in current directory", "django-admin startproject school_site .", "manage.py and school_site/ are created")], "mm": "Django project package နှင့် command/settings boundary ကို စတင်ဖန်တီးရန် သုံးသည်။"},
    {"slug": "django-manage-py-commands", "title": "manage.py command family", "lesson": 2, "syntax": "python manage.py startapp students\npython manage.py runserver\npython manage.py check", "description": "Runs project-aware Django management commands.", "examples": [("Create and check", "python manage.py startapp students\npython manage.py check", "The app is created and checks run")], "mm": "Project-aware Django management command များကို run ရန် သုံးသည်။"},
    {"slug": "django-path", "title": "path() URL pattern", "lesson": 3, "syntax": "path(route, view, kwargs=None, name=None)", "description": "Maps a route string to a view or included URL module.", "examples": [("Named route", "path(\"students/\", views.list_students, name=\"list\")", "The named route resolves to the view")], "mm": "Route string ကို view သို့မဟုတ် included URL module နှင့် ချိတ်သည်။"},
    {"slug": "django-include", "title": "include() URL delegation", "lesson": 3, "syntax": "path(\"students/\", include(\"students.urls\"))", "description": "Delegates a URL prefix to an application's URL configuration.", "examples": [("Delegate app routes", "path(\"students/\", include(\"students.urls\"))", "The app owns child routes")], "mm": "URL prefix ကို application ၏ URL configuration သို့ လွှဲပေးသည်။"},
    {"slug": "django-urlpatterns", "title": "urlpatterns", "lesson": 3, "syntax": "urlpatterns = [path(\"\", views.home, name=\"home\")]", "description": "The ordered collection of URL patterns Django checks.", "examples": [("Ordered patterns", "urlpatterns = [path(\"\", views.home, name=\"home\")]", "Django checks the list")], "mm": "Django စစ်ဆေးသော အစီအစဉ်ရှိ URL pattern collection ဖြစ်သည်။"},
    {"slug": "django-url-app-name", "title": "app_name namespace", "lesson": 3, "syntax": "app_name = \"students\"", "description": "Namespaces names inside an included application URL module.", "examples": [("Namespace a route", "app_name = \"students\"", "Use students:list")], "mm": "Included application URL module ထဲက name များကို namespace လုပ်သည်။"},
    {"slug": "django-reverse", "title": "reverse()", "lesson": 3, "syntax": "reverse(\"students:detail\", kwargs={\"student_id\": 7})", "description": "Builds a URL from a named route and its arguments.", "examples": [("Reverse detail", "reverse(\"students:detail\", kwargs={\"student_id\": 7})", "'/students/7/'")], "mm": "Named route နှင့် argument များမှ URL ပြန်တည်ဆောက်သည်။"},
    {"slug": "django-reverse-lazy", "title": "reverse_lazy()", "lesson": 3, "syntax": "success_url = reverse_lazy(\"students:list\")", "description": "Defers URL reversal until the value is needed.", "examples": [("Lazy class value", "success_url = reverse_lazy(\"students:list\")", "Resolution is deferred")], "mm": "URL reversal ကို value လိုအပ်ချိန်အထိ နောက်ဆုတ်ထားသည်။"},
    {"slug": "django-httprequest", "title": "HttpRequest", "lesson": 4, "syntax": "request.method\nrequest.GET\nrequest.POST", "description": "The request object passed to a Django view.", "examples": [("Read request method", "request.method", "'GET' or 'POST'")], "mm": "Django view သို့ ပို့ပေးသော request object ဖြစ်သည်။"},
    {"slug": "django-httpresponse", "title": "HttpResponse", "lesson": 4, "syntax": "HttpResponse(content, status=200, content_type=None)", "description": "A basic HTTP response for text or HTML content.", "examples": [("Text response", "HttpResponse(\"ok\", content_type=\"text/plain\")", "HTTP 200 body ok")], "mm": "Text သို့မဟုတ် HTML content အတွက် အခြေခံ HTTP response ဖြစ်သည်။"},
    {"slug": "django-jsonresponse", "title": "JsonResponse", "lesson": 5, "syntax": "JsonResponse(data, status=200)", "description": "Serializes JSON-compatible data into an HTTP response.", "examples": [("JSON response", "JsonResponse({\"status\": \"ok\"})", "JSON body and application/json")], "mm": "JSON-compatible data ကို HTTP response အဖြစ် serialize လုပ်သည်။"},
    {"slug": "django-http404", "title": "Http404", "lesson": 4, "syntax": "raise Http404(\"Not found\")", "description": "Signals that the requested resource could not be found.", "examples": [("Missing resource", "raise Http404(\"Student not found\")", "HTTP 404")], "mm": "တောင်းဆိုသော resource မရှိကြောင်း ဖော်ပြသည်။"},
    {"slug": "django-request-get-post-method", "title": "request.GET, request.POST, request.method", "lesson": 5, "syntax": "request.method\nrequest.GET.get(\"q\")\nrequest.POST.get(\"name\")", "description": "Reads method and untrusted query/form input at the view boundary.", "examples": [("Read input", "query = request.GET.get(\"q\", \"\").strip()", "A normalized query string")], "mm": "View boundary တွင် method နှင့် မယုံကြည်ရသော query/form input ကို ဖတ်သည်။"},
    {"slug": "django-settings-debug", "title": "DEBUG setting", "lesson": 7, "syntax": "DEBUG = False", "description": "Controls development diagnostics and must be disabled in production.", "examples": [("Safe production value", "DEBUG = False", "Sensitive debug pages are not enabled")], "mm": "Development diagnostic ကို ထိန်းပြီး production တွင် ပိတ်ထားရမည်။"},
    {"slug": "django-settings-allowed-hosts", "title": "ALLOWED_HOSTS setting", "lesson": 7, "syntax": "ALLOWED_HOSTS = [\"example.com\"]", "description": "Lists accepted Host header values.", "examples": [("Approved host", "ALLOWED_HOSTS = [\"example.com\"]", "Only the approved host is accepted")], "mm": "လက်ခံမည့် Host header value များကို သတ်မှတ်သည်။"},
    {"slug": "django-settings-installed-apps", "title": "INSTALLED_APPS setting", "lesson": 2, "syntax": "INSTALLED_APPS = [\"students.apps.StudentsConfig\"]", "description": "Registers Django and project applications for discovery.", "examples": [("Register app config", "INSTALLED_APPS = [\"students.apps.StudentsConfig\"]", "The students app is discovered")], "mm": "Django နှင့် project application များကို discovery အတွက် register လုပ်သည်။"},
]


def _ensure_syntax_references(db, course, lessons_by_position):
    created = 0
    for order, item in enumerate(SYNTAX_REFERENCES, 1):
        ref = db.scalar(select(SyntaxReference).where(SyntaxReference.course_id == course.id, SyntaxReference.slug == item["slug"]))
        values = {"title": item["title"], "category": "Django Fundamentals", "description": item["description"], "basic_syntax": item["syntax"], "when_to_use": "Use this API when implementing the matching Module 03 boundary.", "important_notes": "Verify behavior against the supported Django version and keep the reference in draft until reviewed.", "reference_type": "framework_api", "difficulty": "beginner", "purpose": item["description"], "syntax_format": item["syntax"], "parameters": "See the official Django API documentation for parameter semantics.", "return_value": "A framework object, URL, response, or setting value as documented.", "version_compatibility": "Validate against the course-supported Django version.", "input_output": "Input: the documented arguments. Output: the documented framework behavior.", "common_mistakes": "Do not confuse routing with authorization; do not expose secrets; test status codes.", "best_practices": "Use named APIs, small examples, explicit validation, and official documentation.", "practice_exercises": "Implement the lesson exercise and add one normal and one failure test.", "further_reading": "https://docs.djangoproject.com/en/stable/", "minimum_examples": 1, "review_notes": "Phase 05 Module 03 draft; answer keys and publication remain review-only.", "status": "draft", "display_order": order}
        if not ref:
            ref = SyntaxReference(course_id=course.id, slug=item["slug"], **values)
            db.add(ref)
            db.flush()
            created += 1
        elif ref.status not in {"published", "approved", "in_review"}:
            for key, value in values.items():
                setattr(ref, key, value)
        translation = db.scalar(select(SyntaxReferenceTranslation).where(SyntaxReferenceTranslation.reference_id == ref.id, SyntaxReferenceTranslation.locale == "my"))
        if not translation:
            db.add(SyntaxReferenceTranslation(reference_id=ref.id, locale="my", title=item["title"], description=item["mm"], purpose=item["mm"], syntax_format=item["syntax"], parameters="Official API parameter များကို supported Django version နှင့် တိုက်ဆိုင်စစ်ဆေးပါ။", return_value="Documentation တွင် ဖော်ပြထားသော framework result ဖြစ်သည်။", version_compatibility="Course တွင် သတ်မှတ်ထားသော Django version နှင့် စစ်ဆေးပါ။", input_output="Input နှင့် output ကို example ဖြင့် စမ်းသပ်ပါ။", common_mistakes="Routing ကို authorization နှင့် မရောပါနှင့်။", best_practices="Named API၊ validation နှင့် official documentation ကို သုံးပါ။", practice_exercises="သက်ဆိုင်ရာ lesson exercise နှင့် failure test ရေးပါ။", further_reading="https://docs.djangoproject.com/en/stable/", status="draft"))
        for number, (title, code, output) in enumerate(item["examples"], 1):
            example = db.scalar(select(SyntaxReferenceExample).where(SyntaxReferenceExample.reference_id == ref.id, SyntaxReferenceExample.example_number == number))
            values = {"title": title, "code": code, "language": "python", "difficulty": "beginner", "description": item["description"], "setup": "Use the supported Django environment.", "sample_input": item["syntax"], "expected_output": output, "explanation": "Read the route/configuration declaration, then verify the observed behavior with a focused test.", "common_mistakes": "Use the exact keyword names and do not skip validation.", "verification_steps": "Run the focused Django check or test and record its actual output."}
            if not example:
                example = SyntaxReferenceExample(reference_id=ref.id, example_number=number, **values)
                db.add(example)
                db.flush()
            else:
                for key, value in values.items():
                    setattr(example, key, value)
            example_translation = db.scalar(select(SyntaxExampleTranslation).where(SyntaxExampleTranslation.example_id == example.id, SyntaxExampleTranslation.locale == "my"))
            if not example_translation:
                db.add(SyntaxExampleTranslation(example_id=example.id, locale="my", title=title, description=item["mm"], setup="Supported Django environment တွင် run ပါ။", sample_input=item["syntax"], expected_output=output, explanation="Code ကို run ပြီး output နှင့် နှိုင်းယှဉ်ပါ။", common_mistakes="Keyword name နှင့် validation ကို မလွတ်ပါစေနှင့်။", verification_steps="Focused test/check ကို run ပြီး အမှန်တကယ် output မှတ်တမ်းတင်ပါ။", status="draft"))
        lesson = lessons_by_position.get(item["lesson"])
        if lesson and not db.scalar(select(LessonSyntaxReference).where(LessonSyntaxReference.lesson_id == lesson.id, LessonSyntaxReference.reference_id == ref.id)):
            db.add(LessonSyntaxReference(lesson_id=lesson.id, reference_id=ref.id, position=order))
    return created


def seed_django_module_three(db, course):
    """Populate only canonical Django Module 03 as reviewable draft content."""
    module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == 3))
    if not module:
        module = CourseModule(course_id=course.id, title=MODULE_TITLE, order_index=3)
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
            lesson = Lesson(module_id=module.id, title=item["title"], slug=item["slug"], description=item["description"], content_en="", content_mm="", order_index=position, duration_minutes=75, status="draft", published=False)
            db.add(lesson)
            db.flush()
            created_lessons += 1
        content_en, content_mm = _render_en(item), _render_mm(item)
        if lesson.published or lesson.status in {"published", "approved", "in_review"}:
            draft = db.scalar(select(LessonContentDraft).where(LessonContentDraft.lesson_id == lesson.id))
            if not draft:
                draft = LessonContentDraft(lesson_id=lesson.id, base_content_version=lesson.content_version, draft_version=1, title=item["title"], slug=lesson.slug, description=item["description"], content_en=content_en, content_mm=content_mm, duration_minutes=75, status="draft", change_summary="Phase 05 Module 03 authoring")
                db.add(draft)
            elif draft.status == "draft":
                draft.title, draft.description, draft.content_en, draft.content_mm, draft.duration_minutes = item["title"], item["description"], content_en, content_mm, 75
        else:
            lesson.title = item["title"]
            lesson.description = item["description"]
            lesson.content_en = content_en
            lesson.content_mm = content_mm
            lesson.duration_minutes = 75
            lesson.status = "draft"
            lesson.published = False
            _ensure_examples(db, lesson, item)
            _ensure_quiz(db, lesson, item)
            _ensure_exercise(db, lesson, item)
        lessons_by_position[position] = lesson
    assessment = _module_assessment()
    assessment_row = db.scalar(select(ModuleQuizDraft).where(ModuleQuizDraft.module_id == module.id))
    payload = [{"position": i, **question} for i, question in enumerate(assessment, 1)]
    if not assessment_row:
        assessment_row = ModuleQuizDraft(module_id=module.id, title_en="Django Fundamentals Module Assessment", title_mm="Django အခြေခံ Module စစ်ဆေးမှု", questions_json=json.dumps(payload, ensure_ascii=False), pass_percent=70, status="draft")
        db.add(assessment_row)
    elif assessment_row.status not in {"published", "approved", "in_review"}:
        assessment_row.title_en = "Django Fundamentals Module Assessment"
        assessment_row.title_mm = "Django အခြေခံ Module စစ်ဆေးမှု"
        assessment_row.questions_json = json.dumps(payload, ensure_ascii=False)
        assessment_row.pass_percent = 70
        assessment_row.status = "draft"
    project = _ensure_project(db, course, module)
    syntax_created = _ensure_syntax_references(db, course, lessons_by_position)
    db.flush()
    return {"module": module, "created_lessons": created_lessons, "lesson_count": len(LESSONS), "assessment_questions": len(assessment), "project": project, "syntax_created": syntax_created}

