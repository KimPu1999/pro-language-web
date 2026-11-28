"""The first reviewable Django curriculum batch.

This module deliberately owns only the missing Django modules (2-10).  The
existing Module 1 lessons are seeded by ``django_course_content`` and are not
rewritten here.  Every new lesson is complete enough for an editor to review,
but remains a draft until an authorised reviewer publishes it.
"""

import json
import re

from sqlalchemy import select

from .models import CodeExample, CodingExercise, CourseModule, Lesson, LessonQuiz, QuizQuestion


MODULES = {
    2: "Django Fundamentals",
    3: "Templates and Frontend",
    4: "Database and Models",
    5: "Forms and Validation",
    6: "Authentication",
    7: "Advanced Django",
    8: "Django REST APIs",
    9: "Security and Testing",
    10: "Production Engineering",
}


def _lesson(title, topic, theory, syntax, code, filename, output, mm, exercise, homework):
    return {
        "title": title,
        "topic": topic,
        "theory": theory,
        "syntax": syntax,
        "code": code,
        "filename": filename,
        "output": output,
        "mm": mm,
        "exercise": exercise,
        "homework": homework,
    }


LESSONS = {
    2: [
        _lesson("Django MVT Architecture", "models, views, templates, and URL configuration",
                "Django uses a Model-View-Template vocabulary. Models describe persisted data, views coordinate a request and response, templates present trusted context, and URL configuration maps paths to views. Keep domain rules in Python services or views rather than hiding them in templates.",
                "path(\"courses/\", views.course_list, name=\"course-list\")\nreturn render(request, \"courses/list.html\", {\"courses\": courses})",
                "from django.shortcuts import render\n\n\ndef course_list(request):\n    courses = [\"Django\", \"FastAPI\"]\n    return render(request, \"courses/list.html\", {\"courses\": courses})",
                "courses/views.py", "The template receives two course names.",
                "MVT တွင် Model က သိမ်းထားသော data ကို ကိုယ်စားပြုသည်။ View က request ကို စီမံပြီး response ပြန်သည်။ Template က context ကို HTML အဖြစ် ပြသည်။ URL configuration က path နှင့် view ကို ချိတ်ပေးသည်။",
                "Draw the request → URLconf → view → model → template → response flow and identify the responsibility of each layer.",
                "Build a small course-list page with a named route and a test for its response status and heading."),
        _lesson("URL Routing and Named Paths", "ordered URL patterns, converters, includes, and reverse resolution",
                "Django checks URL patterns in order and dispatches the first match. Converters such as int validate path shape before the view runs. Named URLs and reverse() keep links stable when a path changes. Use include() to keep application routes separate from the project URLconf.",
                "path(\"courses/<int:course_id>/\", views.detail, name=\"course-detail\")\nreverse(\"course-detail\", kwargs={\"course_id\": 7})",
                "from django.urls import path\nfrom . import views\n\nurlpatterns = [\n    path(\"<int:course_id>/\", views.detail, name=\"course-detail\"),\n]",
                "courses/urls.py", "The route accepts an integer course_id and can be reversed by name.",
                "URL pattern များကို အပေါ်မှအောက်သို့ စစ်ဆေးသည်။ int converter က path parameter ၏ ပုံစံကို စစ်သည်။ Named URL နှင့် reverse() သုံးပါက path ကို hardcode မလုပ်ရပါ။ include() ဖြင့် app routes ကို ခွဲထားနိုင်သည်။",
                "Add an about route, reverse it in a template, and verify that a non-integer course path returns 404.",
                "Document the public paths of a small learning app and state which routes require authentication."),
        _lesson("Views and Request Handling", "function-based views, request data, and server-side decisions",
                "A view receives an HttpRequest and must return an HttpResponse. Query parameters, form data, files, and authenticated user information are separate inputs and must be validated independently. A browser-supplied user id is not proof of ownership; use request.user and a server-side authorization check.",
                "request.method\nrequest.GET.get(\"q\", \"\")\nrequest.user.is_authenticated",
                "from django.http import JsonResponse\n\n\ndef health(request):\n    return JsonResponse({\"status\": \"ok\"})",
                "learning/views.py", "GET /health returns JSON with status ok.",
                "View သည် HttpRequest လက်ခံပြီး HttpResponse ပြန်ရမည်။ Query parameter၊ form data၊ file နှင့် authenticated user တို့ကို သီးခြား validate လုပ်ရမည်။ Browser မှပို့သော user id ကို ownership အဖြစ် မယုံပါနှင့်။",
                "Create a search view that trims a query, rejects an overlong value, and returns a deterministic JSON response.",
                "Write tests for an empty query, a valid query, and a request from an unauthenticated user."),
        _lesson("Response Types and Status Codes", "HTML, JSON, redirects, 404, and deliberate response contracts",
                "Response type is part of an endpoint contract. render() returns HTML, JsonResponse returns structured data, redirect() moves a browser to a named route, and get_object_or_404() communicates absence without leaking database details. Choose status codes deliberately: 200 for success, 201 for creation, 400 for invalid input, 403 for forbidden access, and 404 for missing resources.",
                "return JsonResponse({\"created\": True}, status=201)\nreturn redirect(\"course-list\")\nget_object_or_404(Course, pk=course_id)",
                "from django.http import JsonResponse\n\n\ndef create_preview(request):\n    if request.method != \"POST\":\n        return JsonResponse({\"detail\": \"POST required\"}, status=405)\n    return JsonResponse({\"created\": True}, status=201)",
                "learning/views.py", "POST /preview returns HTTP 201 and created=true.",
                "Response type သည် endpoint contract ၏ အစိတ်အပိုင်း ဖြစ်သည်။ render() သည် HTML၊ JsonResponse သည် structured data၊ redirect() သည် လမ်းကြောင်းပြောင်းခြင်းနှင့် get_object_or_404() သည် မရှိသော resource ကို 404 ပြန်ရန် အသုံးဝင်သည်။",
                "Add a JSON endpoint that returns 405 for GET and 201 for a valid local POST.",
                "Create a response contract table for one HTML endpoint and one JSON endpoint, including failure statuses."),
        _lesson("Application Configuration", "installed apps, AppConfig, settings boundaries, and startup checks",
                "An app is enabled through INSTALLED_APPS. AppConfig is the right place for stable app metadata and carefully controlled startup registration; it is not a place to perform requests or expensive database writes. Keep secrets, hosts, databases, and external service settings in environment-specific configuration.",
                "class LearningConfig(AppConfig):\n    name = \"learning\"\n    verbose_name = \"Learning\"",
                "from django.apps import AppConfig\n\n\nclass LearningConfig(AppConfig):\n    default_auto_field = \"django.db.models.BigAutoField\"\n    name = \"learning\"\n    verbose_name = \"Learning\"",
                "learning/apps.py", "Django loads the learning app with an explicit display name.",
                "INSTALLED_APPS ထဲတွင် app ကို register လုပ်ရသည်။ AppConfig သည် app metadata နှင့် သေချာစွာထိန်းချုပ်ထားသော startup registration အတွက် ဖြစ်ပြီး database write သို့မဟုတ် network request များကို မလုပ်သင့်ပါ။ Secret နှင့် environment-specific settings များကို source code မှ ခွဲထားပါ။",
                "Register a learning app with AppConfig, run manage.py check, and explain why startup code must stay lightweight.",
                "List the settings that differ between local, test, and production environments."),
    ],
    3: [
        _lesson("Template Variables and Filters", "safe context rendering, escaping, and presentation filters",
                "Templates should present values selected by application code. Django auto-escapes normal variable output, while filters such as truncatewords and date make presentation consistent. Never mark user input safe merely to remove an escaping symptom; sanitize trusted rich text with an explicit policy.",
                "{{ course.title|truncatewords:12 }}\n{{ lesson.created_at|date:\"Y-m-d\" }}",
                "{% for course in courses %}\n  <h2>{{ course.title|truncatewords:12 }}</h2>\n{% empty %}\n  <p>No courses yet.</p>\n{% endfor %}",
                "templates/courses/list.html", "Each course title is rendered once, with an empty-state fallback.",
                "Template သည် application code မှ ပေးသော context ကိုသာ ပြသသင့်သည်။ ပုံမှန် variable output ကို auto-escape လုပ်ပြီး filter များဖြင့် display format ပြောင်းနိုင်သည်။ User input ကို safe ဟု မမှတ်ပါနှင့်။",
                "Render a list with a title filter and an empty state, then test that angle brackets in a title are escaped.",
                "Compare truncatewords with CSS line clamping and state when each belongs."),
        _lesson("Template Inheritance", "base templates, blocks, includes, and consistent page structure",
                "Template inheritance keeps navigation, metadata, and accessibility landmarks in one base file. A child template overrides named blocks, while include renders a focused partial with an explicit context. Keep reusable components free of hidden database queries so page performance remains predictable.",
                "{% extends \"base.html\" %}\n{% block content %}...{% endblock %}\n{% include \"courses/_card.html\" with course=course %}",
                "{% extends \"base.html\" %}\n{% block title %}Courses{% endblock %}\n{% block content %}\n  <main><h1>Courses</h1></main>\n{% endblock %}",
                "templates/courses/index.html", "The page uses the shared base layout and replaces its content block.",
                "Base template တစ်ခုတွင် navigation နှင့် accessibility landmark များထားပြီး child template က block များကို override လုပ်နိုင်သည်။ Include partial များတွင် context ကို ရှင်းလင်းစွာ ပေးပါ။",
                "Create base.html, a course index child, and a card partial; verify the page has one main landmark.",
                "Add a reusable empty-state partial and document the context variables it requires."),
        _lesson("Static Files", "CSS, JavaScript, collectstatic, and safe asset references",
                "Static files are versioned application assets such as CSS and JavaScript; uploaded media is user or administrator data and follows a different storage policy. Use static and staticfiles storage helpers instead of hardcoded deployment paths. collectstatic gathers assets for a production web server but does not make user uploads public.",
                "{% load static %}\n<link rel=\"stylesheet\" href=\"{% static 'learning/app.css' %}\">",
                "{% load static %}\n<script defer src=\"{% static 'learning/app.js' %}\"></script>",
                "templates/base.html", "The rendered asset URL is resolved through Django's staticfiles configuration.",
                "Static file သည် versioned CSS/JS asset ဖြစ်ပြီး user upload media နှင့် မတူပါ။ static helper နှင့် staticfiles storage ကို သုံးပါ။ collectstatic သည် production web server အတွက် asset စုစည်းပေးသော်လည်း upload ကို public မလုပ်ပေးပါ။",
                "Add one CSS file and one deferred script using the static template tag, then run collectstatic only in an isolated test setting.",
                "Write a deployment note distinguishing STATIC_ROOT, MEDIA_ROOT, and their access controls."),
        _lesson("Forms in Templates", "POST forms, CSRF, validation feedback, and accessible controls",
                "A browser form is a trust boundary. Render a CSRF token, bind submitted data to a form class, show field and non-field errors, and preserve safe user input after a failed submission. Use labels, help text, and an accessible error summary so keyboard and assistive-technology users can recover.",
                "<form method=\"post\">\n  {% csrf_token %}\n  {{ form.non_field_errors }}\n  {{ form.as_p }}\n  <button type=\"submit\">Save</button>\n</form>",
                "from django import forms\n\n\nclass CourseSearchForm(forms.Form):\n    query = forms.CharField(max_length=80, required=False)",
                "courses/forms.py", "The form accepts an optional query and rejects values longer than 80 characters.",
                "Browser form သည် trust boundary ဖြစ်သည်။ CSRF token ထည့်ပြီး submitted data ကို form class ဖြင့် bind/validate လုပ်ပါ။ Field error နှင့် non-field error များကို ပြပြီး label၊ help text နှင့် error summary ပါစေ။",
                "Build a search form with a visible label, max length, CSRF token, and a test for invalid input.",
                "Inspect the rendered HTML for label association and keyboard-friendly error recovery."),
        _lesson("Reusable Template Components", "component boundaries, context contracts, and accessibility",
                "A reusable template component should have a small, documented context contract. Keep visual decisions close to the component, expose meaningful text alternatives, and do not hide authorization decisions inside presentation. A component can render a status badge, course card, or pagination control without owning database mutations.",
                "{% include \"components/status_badge.html\" with label=course.status tone=course.status %}",
                "<article class=\"course-card\" aria-labelledby=\"course-{{ course.id }}\">\n  <h2 id=\"course-{{ course.id }}\">{{ course.title }}</h2>\n  <p>{{ course.description }}</p>\n</article>",
                "templates/components/course_card.html", "Each card exposes a heading and description with a stable relationship.",
                "Reusable component တစ်ခုတွင် context contract သေးငယ်ပြီး ရှင်းလင်းရမည်။ Accessibility text၊ heading relationship နှင့် authorization boundary ကို မဖျောက်ပါနှင့်။ Database mutation ကို presentation component ထဲ မထည့်ပါနှင့်။",
                "Extract a course card partial, define its required context, and render it with a missing optional thumbnail.",
                "Write a short component README describing inputs, output semantics, and keyboard behavior."),
    ],
    4: [
        _lesson("Models and Field Types", "Django models, constraints, indexes, and domain fields",
                "A model describes a persisted domain object, not merely a form. Select field types that match the domain, define null and blank deliberately, add constraints for invariants, and index fields used by real access patterns. Database constraints remain important even when forms validate the same rule.",
                "class Course(models.Model):\n    slug = models.SlugField(unique=True)\n    title = models.CharField(max_length=180)\n    published = models.BooleanField(default=False)",
                "from django.db import models\n\n\nclass Course(models.Model):\n    slug = models.SlugField(unique=True)\n    title = models.CharField(max_length=180)\n    published = models.BooleanField(default=False)",
                "courses/models.py", "A course cannot have a duplicate slug and starts unpublished by default.",
                "Model သည် persisted domain object ကို ကိုယ်စားပြုသည်။ Field type၊ null/blank၊ constraint နှင့် access pattern အပေါ် မူတည်သော index များကို ရွေးချယ်ပါ။ Form validation ရှိသော်လည်း database constraint များ လိုအပ်သည်။",
                "Define a Course model with a unique slug, bounded title, publication flag, and one database index.",
                "Explain which invariants belong in model validation and which must be enforced by the database."),
        _lesson("Migrations Safely", "schema history, makemigrations, migrate, and reversible changes",
                "Migrations are versioned schema changes. Review generated operations before applying them, test them against a copy or test database, and keep data migrations separate from risky schema operations when possible. A migration must be deterministic and compatible with the deployment order of application code.",
                "python manage.py makemigrations\npython manage.py sqlmigrate courses 0002\npython manage.py migrate",
                "from django.db import migrations, models\n\n\nclass Migration(migrations.Migration):\n    dependencies = [(\"courses\", \"0001_initial\")]\n    operations = [migrations.AddField(\"course\", \"published\", models.BooleanField(default=False))]",
                "courses/migrations/0002_course_published.py", "The migration adds a defaulted published column after review.",
                "Migration သည် schema change history ဖြစ်သည်။ Generated operation ကို review လုပ်ပြီး test database တွင် စမ်းသပ်ကာမှ apply လုပ်ပါ။ Data migration နှင့် schema operation ကို လိုအပ်သလို ခွဲပါ။",
                "Add a nullable field in a local test project, inspect sqlmigrate output, apply it, and verify the rollback plan.",
                "Write a release checklist for a migration that changes a large table without locking it unexpectedly."),
        _lesson("Relationships", "foreign keys, many-to-many data, deletion policy, and query shape",
                "Relationships express ownership and association. ForeignKey requires an on_delete policy that matches the domain; PROTECT can preserve important records while CASCADE is appropriate only when child data has no independent meaning. Many-to-many relations need an explicit through model when metadata or constraints matter.",
                "class Lesson(models.Model):\n    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name=\"lessons\")",
                "class Enrollment(models.Model):\n    student = models.ForeignKey(\"accounts.User\", on_delete=models.CASCADE)\n    course = models.ForeignKey(Course, on_delete=models.PROTECT)\n    created_at = models.DateTimeField(auto_now_add=True)",
                "learning/models.py", "An enrollment points to a student and a protected course record.",
                "Relationship သည် ownership နှင့် association ကို ဖော်ပြသည်။ on_delete policy ကို domain အလိုက်ရွေးပါ။ အရေးကြီး record များကို PROTECT ဖြင့် ထိန်းနိုင်ပြီး child data သီးခြားအဓိပ္ပါယ်မရှိမှ CASCADE သုံးပါ။",
                "Model a course enrollment, choose deletion behavior, and query a student's courses without exposing another student's data.",
                "Add a uniqueness constraint so one student cannot enroll in the same course twice."),
        _lesson("QuerySets and Query Optimization", "lazy queries, select_related, prefetch_related, and bounded results",
                "QuerySets are lazy until evaluated, which lets Django compose filters efficiently. Use select_related for single-valued relationships and prefetch_related for collections. Measure query count with tests or tooling, select only needed fields when appropriate, and always bound list endpoints with pagination.",
                "Course.objects.select_related(\"category\").prefetch_related(\"modules\").filter(published=True).order_by(\"title\")",
                "published = (Course.objects.select_related(\"category\")\n    .prefetch_related(\"modules\")\n    .filter(published=True)\n    .order_by(\"title\")[:20])",
                "courses/services.py", "The query loads published courses with related category and modules and limits the page to 20.",
                "QuerySet သည် evaluate မလုပ်မချင်း lazy ဖြစ်သည်။ Single-valued relationship အတွက် select_related၊ collection အတွက် prefetch_related သုံးပါ။ Query count တိုင်းပြီး list endpoint ကို pagination ဖြင့် bound လုပ်ပါ။",
                "Create a published course list, compare query counts with and without prefetch_related, and add a page-size limit.",
                "Document the relationship path that causes an N+1 query and the measured fix."),
        _lesson("Database Transactions", "atomic writes, integrity, and explicit failure handling",
                "A transaction groups related writes so readers do not observe a half-complete state. transaction.atomic() rolls back when an exception escapes. Transactions do not automatically solve concurrency or authorization: lock rows when required, enforce constraints, and keep external API calls outside the database transaction.",
                "with transaction.atomic():\n    enrollment = Enrollment.objects.create(...)\n    AuditEvent.objects.create(enrollment_id=enrollment.id)",
                "from django.db import transaction\n\n\n@transaction.atomic\ndef enroll(student, course):\n    return Enrollment.objects.create(student=student, course=course)",
                "learning/services.py", "The enrollment write is committed together or rolled back together.",
                "Transaction သည် ဆက်စပ် write များကို တစ်စုတစ်စည်း commit/rollback လုပ်စေသည်။ ဒါပေမယ့် concurrency နှင့် authorization ကို အလိုအလျောက် မဖြေရှင်းပေးပါ။ လိုအပ်ပါက row lock၊ constraint နှင့် external call boundary သုံးပါ။",
                "Write a transactional enrollment service and test that a deliberate exception leaves no partial enrollment.",
                "Explain when select_for_update is necessary and why it should be used only with a narrow transaction."),
        _lesson("Database Performance", "indexes, query plans, pagination, and safe optimization",
                "Performance work starts with an observed slow query and a representative dataset. Index columns used in filtering or ordering, but remember that indexes cost storage and write time. Inspect EXPLAIN output, avoid selecting unused large text fields, and prefer cursor or keyset pagination for very large ordered tables.",
                "Course.objects.filter(published=True).order_by(\"-updated_at\")\n# inspect with QuerySet.explain()",
                "query = Course.objects.filter(published=True).order_by(\"-updated_at\")\nprint(query.explain())",
                "courses/performance.py", "The query plan is printed for review instead of guessed from intuition.",
                "Performance optimization ကို observed slow query နှင့် representative data ဖြင့် စပါ။ Filter/order field များကို index လုပ်သော်လည်း index သည် write/storage cost ရှိသည်။ EXPLAIN နှင့် pagination ကို သုံးပါ။",
                "Measure a course list query before and after an index in a disposable test database.",
                "Prepare a note describing the query, dataset size, plan change, and rollback of an unnecessary index."),
    ],
    5: [
        _lesson("Django Forms", "form classes, bound data, widgets, and validation lifecycle",
                "A Form class centralizes input fields, labels, widgets, and validation. An unbound form is for display; a bound form represents submitted data and can be valid or invalid. Keep field types and max lengths explicit so invalid input is rejected before business logic runs.",
                "form = CourseSearchForm(request.GET or None)\nif form.is_valid():\n    query = form.cleaned_data[\"query\"]",
                "class CourseSearchForm(forms.Form):\n    query = forms.CharField(label=\"Search\", max_length=80, required=False)",
                "courses/forms.py", "The cleaned query is normalized and is at most 80 characters.",
                "Form class သည် input field၊ label၊ widget နှင့် validation ကို စုစည်းပေးသည်။ Bound form သည် submit data ကို ကိုယ်စားပြုပြီး valid/invalid အခြေအနေ ရှိသည်။ Field type နှင့် max length ကို သတ်မှတ်ပါ။",
                "Create a search form with a custom label and validate GET data without mutating the database.",
                "Test valid, blank, overlong, and whitespace-only values."),
        _lesson("ModelForms", "model-backed editing, field allowlists, and safe save boundaries",
                "ModelForm generates form fields from a model, but fields must be explicitly allowed. Never expose owner, role, publication, or audit fields merely because they exist on the model. Use commit=False only when the service must attach server-owned fields before saving.",
                "class CourseForm(forms.ModelForm):\n    class Meta:\n        model = Course\n        fields = [\"title\", \"description\"]",
                "class CourseForm(forms.ModelForm):\n    class Meta:\n        model = Course\n        fields = [\"title\", \"short_description\"]\n\n    def save_for_editor(self, editor):\n        course = super().save(commit=False)\n        course.updated_by = editor\n        course.save()\n        return course",
                "courses/forms.py", "Only editor-safe fields are accepted and updated_by comes from the server.",
                "ModelForm သည် model မှ form field ဖန်တီးပေးသော်လည်း fields ကို allowlist လုပ်ရမည်။ Owner၊ role၊ publication နှင့် audit field များကို client ထံ မပေးပါနှင့်။ Server-owned field ကို commit=False ဖြင့် သတ်မှတ်ပါ။",
                "Build an editor form that accepts title and description but cannot change published or owner fields.",
                "Add a test that submits an unexpected published field and proves it is ignored."),
        _lesson("Validation and Clean Methods", "field validation, cross-field rules, and error messages",
                "Validation should provide useful, safe feedback without disclosing secrets or internal stack traces. Field clean methods validate one field; clean() validates relationships between fields. Raise ValidationError with actionable messages and normalize values before the service uses them.",
                "def clean_title(self):\n    value = self.cleaned_data[\"title\"].strip()\n    if not value:\n        raise forms.ValidationError(\"Enter a title.\")\n    return value",
                "class PublishForm(forms.Form):\n    title = forms.CharField(max_length=180)\n    confirm = forms.BooleanField(required=True)\n\n    def clean(self):\n        data = super().clean()\n        if data.get(\"title\") and not data.get(\"confirm\"):\n            raise forms.ValidationError(\"Confirm before publishing.\")\n        return data",
                "courses/forms.py", "A title can be published only when the explicit confirmation is checked.",
                "Validation သည် internal detail မဖော်ဘဲ အသုံးဝင်သော error ပြန်ရမည်။ Field clean method သည် field တစ်ခု၊ clean() သည် field များအကြား rule ကို စစ်သည်။ Value ကို normalize ပြီး service သို့ ပို့ပါ။",
                "Add a cross-field validation rule requiring confirmation before a publish action.",
                "Write tests for the valid path and both validation failures."),
        _lesson("Secure File Uploads", "uploaded files, content limits, names, and storage isolation",
                "Uploaded files are untrusted input. Validate size, extension, content type, and authorization; generate server-side names; store outside executable code paths; and serve with safe content-disposition headers where appropriate. Do not trust a browser MIME type and do not process arbitrary archives in the web request.",
                "file = forms.FileField(max_length=10 * 1024 * 1024)\nrequest.FILES.get(\"document\")",
                "class DocumentForm(forms.Form):\n    document = forms.FileField()\n\n    def clean_document(self):\n        document = self.cleaned_data[\"document\"]\n        if document.size > 10 * 1024 * 1024:\n            raise forms.ValidationError(\"File is too large.\")\n        return document",
                "courses/forms.py", "Files above 10 MiB are rejected before storage.",
                "Upload file သည် untrusted input ဖြစ်သည်။ Size၊ extension၊ content type၊ authorization ကို စစ်ပြီး server-side name သုံးပါ။ Executable path အပြင် storage ထားပြီး browser MIME type ကို မယုံပါနှင့်။",
                "Add a size-limited upload form and test an oversized file using an in-memory upload.",
                "Write an upload threat model covering malware, path traversal, public exposure, and retention."),
    ],
    6: [
        _lesson("User Model and Authentication", "custom user boundaries, password hashing, and identity checks",
                "Authentication answers who the user is; authorization answers what they may do. Use Django's configured user model and password hashing rather than storing passwords yourself. Read the authenticated user from request.user and avoid exposing whether a private account exists.",
                "AUTH_USER_MODEL = \"accounts.User\"\nrequest.user.is_authenticated\nuser.check_password(raw_password)",
                "from django.contrib.auth import get_user_model\n\nUser = get_user_model()\nuser = User.objects.create_user(email=\"learner@example.com\", password=\"local-only\")\nassert user.check_password(\"local-only\")",
                "accounts/services.py", "The password is hashed and check_password returns true without exposing the hash.",
                "Authentication သည် user identity ကို စစ်ပြီး authorization သည် လုပ်ဆောင်ခွင့်ကို စစ်သည်။ Configured user model နှင့် password hashing ကို သုံးပါ။ request.user မှ identity ဖတ်ပြီး private account ရှိ/မရှိကို မဖော်ပြပါနှင့်။",
                "Create a local user with create_user, verify check_password, and ensure the raw password is never stored in a model field.",
                "Document the difference between authentication, authorization, and session state."),
        _lesson("Login and Logout", "credential verification, sessions, redirects, and failure handling",
                "Login verifies credentials and attaches a session; logout clears the session. Use Django's built-in auth views or their documented patterns, rotate session identifiers at login, rate-limit repeated failures at the edge, and return a generic failure message so account existence is not disclosed.",
                "from django.contrib.auth import authenticate, login, logout\nuser = authenticate(request, username=email, password=password)",
                "def sign_in(request):\n    user = authenticate(request, username=request.POST.get(\"email\"), password=request.POST.get(\"password\"))\n    if user is None:\n        return render(request, \"accounts/login.html\", {\"error\": \"Invalid credentials.\"}, status=400)\n    login(request, user)\n    return redirect(\"dashboard\")",
                "accounts/views.py", "Valid credentials create a session and invalid credentials return a generic 400 response.",
                "Login သည် credentials ကို verify ပြီး session ချိတ်သည်။ Logout သည် session ရှင်းသည်။ Built-in auth view သို့မဟုတ် document လုပ်ထားသော pattern သုံးပြီး session rotation၊ rate limit နှင့် generic error message ထားပါ။",
                "Build a login view with CSRF protection, generic errors, and a redirect after successful authentication.",
                "Test invalid credentials, successful login, logout, and a protected view without a session."),
        _lesson("Registration Workflow", "account creation, duplicate identities, and verification boundaries",
                "Registration accepts untrusted identity data and creates a user only after validation. Normalize email addresses, enforce uniqueness at the database level, hash the password, and consider email verification before granting sensitive access. Do not reveal whether an email is already registered in a security-sensitive flow.",
                "email = User.normalize_email(form.cleaned_data[\"email\"])\nUser.objects.create_user(email=email, password=form.cleaned_data[\"password\"])",
                "class RegistrationForm(forms.Form):\n    email = forms.EmailField()\n    password = forms.CharField(min_length=12, widget=forms.PasswordInput)\n    confirm = forms.CharField(widget=forms.PasswordInput)\n\n    def clean(self):\n        data = super().clean()\n        if data.get(\"password\") != data.get(\"confirm\"):\n            raise forms.ValidationError(\"Passwords do not match.\")\n        return data",
                "accounts/forms.py", "The form enforces email shape, password length, and matching confirmation.",
                "Registration သည် untrusted identity data ကို validate ပြီးမှ user ဖန်တီးရမည်။ Email normalize လုပ်ပြီး database uniqueness၊ password hashing နှင့် email verification boundary ထားပါ။ Registered email ရှိ/မရှိကို မဖော်ပြပါနှင့်။",
                "Create a registration form with password confirmation and a service that uses create_user.",
                "Add tests for weak passwords, mismatched confirmation, duplicate email, and successful creation."),
        _lesson("Permissions and Groups", "authorization policies, groups, decorators, and object ownership",
                "Django permissions are a foundation, not a complete policy. Use groups for role bundles and explicit object-level checks for ownership or course assignment. Enforce authorization on the server for every mutation; hiding a button does not protect an endpoint.",
                "@permission_required(\"courses.change_course\")\ndef edit_course(request, course_id): ...",
                "from django.contrib.auth.decorators import permission_required\n\n\n@permission_required(\"courses.change_course\", raise_exception=True)\ndef edit_course(request, course_id):\n    return JsonResponse({\"allowed\": True})",
                "courses/views.py", "Users without the permission receive a server-side 403.",
                "Permission သည် foundation ဖြစ်ပြီး policy အားလုံးမဟုတ်ပါ။ Group ကို role bundle အတွက်သုံးပြီး ownership/course assignment ကို object-level check ဖြင့် စစ်ပါ။ Button ဖျောက်ခြင်းတစ်ခုတည်းဖြင့် endpoint မကာကွယ်နိုင်ပါ။",
                "Protect a course edit view with a permission and an object ownership check.",
                "Write an authorization matrix for learner, instructor, editor, and platform administrator roles."),
        _lesson("Session Security", "cookies, expiry, CSRF, fixation, and secure deployment settings",
                "Sessions carry authenticated state, so cookie flags and expiry matter. Use Secure and HttpOnly cookies in HTTPS deployments, SameSite appropriate to the flow, short idle and absolute lifetimes, session rotation after login, and logout invalidation. CSRF protection remains necessary for cookie-authenticated state changes.",
                "SESSION_COOKIE_SECURE = True\nSESSION_COOKIE_HTTPONLY = True\nSESSION_COOKIE_SAMESITE = \"Lax\"\nCSRF_COOKIE_SECURE = True",
                "SESSION_COOKIE_AGE = 60 * 60 * 8\nSESSION_EXPIRE_AT_BROWSER_CLOSE = True\nSESSION_SAVE_EVERY_REQUEST = False",
                "config/settings/production.py", "Production settings use bounded sessions and browser-close expiry.",
                "Session သည် authenticated state ကို သယ်ဆောင်သဖြင့် cookie flag နှင့် expiry အရေးကြီးသည်။ HTTPS production တွင် Secure/HttpOnly၊ သင့်တော်သော SameSite၊ bounded lifetime နှင့် login အပြီး rotation သုံးပါ။ Cookie-authenticated mutation တွင် CSRF လိုအပ်သည်။",
                "Review session and CSRF settings for an HTTPS deployment and explain each flag.",
                "Create a session incident checklist for logout, rotation, cookie revocation, and audit logs."),
    ],
    7: [
        _lesson("Class-Based Views", "generic views, mixins, method boundaries, and explicit overrides",
                "Class-based views package request behavior into reusable methods and mixins. Generic views reduce repeated list, detail, and form plumbing, but they can hide control flow when over-composed. Override the smallest method, keep authorization explicit, and test the resolved behavior rather than the class shape.",
                "class CourseListView(LoginRequiredMixin, ListView):\n    model = Course\n    paginate_by = 20",
                "from django.views.generic import ListView\n\n\nclass CourseListView(ListView):\n    template_name = \"courses/list.html\"\n    context_object_name = \"courses\"\n    queryset = Course.objects.filter(published=True).order_by(\"title\")",
                "courses/views.py", "Only published courses are exposed through the list view.",
                "Class-based view သည် request behavior ကို method နှင့် mixin များဖြင့် ပြန်သုံးနိုင်စေသည်။ Generic view သည် boilerplate လျှော့ပေးသော်လည်း authorization နှင့် control flow မဖျောက်ပါနှင့်။",
                "Create a paginated published-course ListView and test its template context.",
                "Compare the same endpoint as a function-based view and record the readability trade-off."),
        _lesson("Middleware", "request lifecycle, cross-cutting policy, and safe ordering",
                "Middleware wraps the request and response lifecycle. It is appropriate for cross-cutting concerns such as security headers, request IDs, or timing, not domain-specific authorization that needs a course object. Ordering matters because one middleware can depend on state created by another.",
                "class RequestIdMiddleware:\n    def __call__(self, request):\n        response = self.get_response(request)\n        response[\"X-Request-ID\"] = request.request_id\n        return response",
                "import uuid\n\n\nclass RequestIdMiddleware:\n    def __init__(self, get_response):\n        self.get_response = get_response\n\n    def __call__(self, request):\n        request.request_id = str(uuid.uuid4())\n        return self.get_response(request)",
                "config/middleware.py", "Every request receives a correlation identifier before reaching the view.",
                "Middleware သည် request/response lifecycle ကို wrap လုပ်သည်။ Security header၊ request ID၊ timing ကဲ့သို့ cross-cutting concern အတွက်သင့်တော်ပြီး domain authorization ကို မဖျောက်သင့်ပါ။ Ordering အရေးကြီးသည်။",
                "Implement a request ID middleware and add a test that the response echoes a non-empty identifier.",
                "Document middleware ordering for security, sessions, authentication, and your request ID layer."),
        _lesson("Signals", "event hooks, transaction timing, and when not to use signals",
                "Signals notify decoupled listeners when model or request events occur, but they can hide side effects and make ordering difficult to reason about. Prefer an explicit service for business-critical workflows. If a signal is appropriate, make it idempotent, register it predictably, and never assume an external side effect committed with the database.",
                "@receiver(post_save, sender=Course)\ndef course_saved(sender, instance, created, **kwargs): ...",
                "from django.db.models.signals import post_save\nfrom django.dispatch import receiver\n\n\n@receiver(post_save, sender=Course)\ndef course_saved(sender, instance, created, **kwargs):\n    if created:\n        AuditEvent.objects.get_or_create(course_id=instance.id, event=\"created\")",
                "courses/signals.py", "Course creation creates one idempotent audit event.",
                "Signal သည် event hook ဖြစ်သော်လည်း side effect ဖျောက်ထားနိုင်ပြီး ordering ခက်စေသည်။ Business-critical workflow အတွက် explicit service ကို ဦးစားပေးပါ။ သုံးရပါက idempotent ဖြစ်ပြီး external side effect ကို transaction နှင့် မရောပါနှင့်။",
                "Add an idempotent audit signal for course creation and test that repeated handling does not duplicate the event.",
                "Write a decision note explaining why an enrollment email belongs in a service or task instead of a model signal."),
        _lesson("Transactions and Service Boundaries", "application services, atomicity, and side-effect coordination",
                "A service function can make a domain operation visible and testable. Keep validation, authorization, transactional writes, and external side effects at separate boundaries. Use on_commit for work that should happen only after the database commits, and make retries idempotent.",
                "with transaction.atomic():\n    course = publish_course(editor, course_id)\n    transaction.on_commit(lambda: notify.delay(course.id))",
                "from django.db import transaction\n\n\ndef publish_course(editor, course):\n    if not editor.has_perm(\"courses.publish_course\"):\n        raise PermissionError\n    course.published = True\n    course.save(update_fields=[\"published\"])\n    transaction.on_commit(lambda: audit_publish(course.id))\n    return course",
                "courses/services.py", "The publication flag commits before the audit callback runs.",
                "Service function သည် domain operation ကို မြင်သာပြီး testable ဖြစ်စေသည်။ Authorization၊ transactional write နှင့် external side effect ကို boundary ခွဲပါ။ Database commit ပြီးမှသာလုပ်ရမည့် အလုပ်ကို on_commit သုံးပါ။",
                "Implement a publish service with a permission check, atomic update, and on_commit audit callback.",
                "Test rollback and prove that the on_commit callback is not called when the transaction fails."),
        _lesson("Caching and Async Capabilities", "cache keys, invalidation, async views, and workload boundaries",
                "Caching is a correctness decision as well as a speed decision. Design keys with tenant, locale, and version boundaries; set expiry; and invalidate after writes. Async views help with non-blocking I/O, but synchronous database work must not be called carelessly from an async context. Measure before adding a cache.",
                "cache.get_or_set(\"course-list:v1:en\", load_courses, 60)\nasync def health(request): ...",
                "from django.core.cache import cache\n\n\ndef published_course_ids():\n    return cache.get_or_set(\"courses:published:v1\", lambda: list(Course.objects.filter(published=True).values_list(\"id\", flat=True)), 60)",
                "courses/cache.py", "Published course IDs are cached for 60 seconds under a versioned key.",
                "Cache သည် speed တင်မက correctness decision လည်း ဖြစ်သည်။ Key တွင် tenant၊ locale၊ version boundary ထည့်ပြီး expiry/invalidation စီမံပါ။ Async view ထဲ sync database ကို မသတိမထားဘဲ မခေါ်ပါနှင့်။",
                "Cache a bounded published-course lookup, invalidate it after publication, and document stale-data behavior.",
                "Compare a synchronous view, async external request, and background task for three workloads."),
    ],
    8: [
        _lesson("REST API Architecture", "resources, HTTP semantics, contracts, and service boundaries",
                "A REST API exposes stable resource representations over HTTP. Define URL and method semantics, response shapes, status codes, authentication boundaries, and error format before writing views. Keep serializer/schema concerns separate from domain services and never let a client choose server-owned fields.",
                "GET /api/courses/\nPOST /api/courses/\nGET /api/courses/{id}/",
                "from django.http import JsonResponse\n\n\ndef course_collection(request):\n    if request.method == \"GET\":\n        return JsonResponse({\"items\": [], \"next\": None})\n    return JsonResponse({\"detail\": \"Method not allowed\"}, status=405)",
                "api/views.py", "GET returns an items collection and other methods receive a deliberate 405.",
                "REST API သည် HTTP အပေါ် stable resource representation ပေးသည်။ URL/method semantics၊ response shape၊ status၊ auth boundary နှင့် error format ကို ကြိုသတ်မှတ်ပါ။ Client ကို server-owned field ရွေးခွင့် မပေးပါနှင့်။",
                "Design a read-only course collection endpoint with a documented JSON response and status codes.",
                "Write an API contract for list, detail, missing resource, and validation failures."),
        _lesson("Serializers and Schemas", "input allowlists, output shapes, and safe serialization",
                "A serializer maps domain data to a public representation and validates incoming data. Use explicit read and write fields, nested shapes only when needed, and avoid exposing internal ids, hashes, ownership metadata, or audit fields. Serialization is not authorization; the service must still check access.",
                "class CourseSerializer(serializers.ModelSerializer):\n    class Meta:\n        model = Course\n        fields = [\"id\", \"title\", \"slug\"]",
                "class CourseSerializer(serializers.Serializer):\n    title = serializers.CharField(max_length=180)\n    description = serializers.CharField()\n\n    def validate_title(self, value):\n        return value.strip()",
                "api/serializers.py", "The API accepts a bounded title and description and strips title whitespace.",
                "Serializer သည် domain data ကို public representation အဖြစ် map လုပ်ပြီး input validate သည်။ Read/write fields explicit ထားပြီး internal id၊ hash၊ owner၊ audit field များ မဖော်ပြပါနှင့်။ Serializer သည် authorization မဟုတ်ပါ။",
                "Create a write serializer with an allowlist and a field validator, then test an overlong title.",
                "List which model fields must never appear in the public course response and why."),
        _lesson("API Views and ViewSets", "request dispatch, CRUD operations, and explicit action boundaries",
                "API views coordinate authentication, validation, service calls, and response formatting. ViewSets can reduce repeated routing for standard resources, but custom actions should be named and permissioned explicitly. Use a service for multi-step writes instead of embedding transaction logic in a serializer method without tests.",
                "class CourseViewSet(viewsets.ModelViewSet):\n    queryset = Course.objects.filter(published=True)\n    serializer_class = CourseSerializer",
                "class CourseList(APIView):\n    def get(self, request):\n        data = Course.objects.filter(published=True).values(\"id\", \"title\")\n        return Response({\"items\": list(data)})",
                "api/views.py", "The list view returns only published course fields selected for the contract.",
                "API view သည် authentication၊ validation၊ service call နှင့် response formatting ကို စုစည်းသည်။ ViewSet သုံးပါက custom action ကို explicit name နှင့် permission ထားပါ။ Multi-step write ကို service ဖြင့် ခွဲထားပါ။",
                "Implement a published course list view and test that draft rows and private fields are excluded.",
                "Compare APIView and ViewSet for one resource and record the routing and permission implications."),
        _lesson("API Permissions and Authentication", "token/session auth, permission classes, and object checks",
                "An API must authenticate the caller and authorize the requested resource. Permission classes can provide a first boundary, but object-level checks are still required for updates. Return a consistent 401 or 403 contract, do not trust user ids in JSON, and keep tokens out of logs and URLs.",
                "permission_classes = [IsAuthenticated]\nif obj.owner_id != request.user.id:\n    raise PermissionDenied",
                "class IsCourseEditor(BasePermission):\n    def has_object_permission(self, request, view, obj):\n        return request.user.has_perm(\"courses.change_course\") and obj.owner_id == request.user.id",
                "api/permissions.py", "Only an authenticated owner with the change permission may edit the course.",
                "API တွင် caller authentication နှင့် resource authorization နှစ်ခုလုံးလိုသည်။ Permission class သည် boundary တစ်ခုသာဖြစ်ပြီး update အတွက် object-level check ထပ်လိုသည်။ JSON ထဲ user id ကို မယုံပါနှင့်။",
                "Add an object permission for course editing and test authenticated owner, authenticated non-owner, and anonymous callers.",
                "Create a 401/403 decision table and include token redaction rules for logs."),
        _lesson("Pagination and Filtering", "bounded lists, stable ordering, and safe query parameters",
                "List APIs must have a maximum page size and a stable ordering. Validate filter fields against an allowlist, normalize search values, and return total or continuation metadata consistently. Do not build raw SQL from query parameters; use ORM expressions or parameterized queries.",
                "?page=2&page_size=20&level=beginner&search=django\nPageNumberPagination.page_size_query_param = \"page_size\"",
                "class CoursePagination(PageNumberPagination):\n    page_size = 20\n    max_page_size = 100\n\nclass CourseFilter(FilterSet):\n    level = filters.CharFilter(field_name=\"level\")",
                "api/pagination.py", "The API caps client-requested page size at 100.",
                "List API သည် maximum page size နှင့် stable ordering ရှိရမည်။ Filter field ကို allowlist လုပ်ပြီး search normalize လုပ်ပါ။ Query parameter ကို raw SQL အဖြစ် မပေါင်းပါနှင့်။",
                "Add a bounded page-size parameter and a level filter, then test the maximum and invalid values.",
                "Document how the client follows next-page metadata without assuming a fixed page count."),
        _lesson("API Versioning and Documentation", "backward compatibility, deprecation, and observable contracts",
                "An API version is a compatibility promise, not merely a URL prefix. Keep a stable response shape, document authentication and errors, add contract tests, and announce deprecations before removing fields. Use generated OpenAPI documentation as a starting point and review it for sensitive fields.",
                "path(\"api/v1/courses/\", include(router.urls))\nclass CourseOutSerializer(...): ...",
                "urlpatterns = [\n    path(\"api/v1/\", include(\"courses.api_urls\")),\n]\n\n# Keep v2 changes behind an explicit serializer and route.",
                "api/urls.py", "The v1 contract remains explicit while a future v2 can evolve separately.",
                "API version သည် compatibility promise ဖြစ်သည်။ Response shape၊ auth/error contract၊ contract test နှင့် deprecation notice ကို ထိန်းပါ။ OpenAPI ကို sensitive field မပါစေရန် review လုပ်ပါ။",
                "Document the v1 course endpoint, generate an example response, and identify one change that requires v2.",
                "Write a deprecation note with a date, migration guidance, and the test that protects the old contract."),
    ],
    9: [
        _lesson("CSRF Protection", "cookie-authenticated mutations, tokens, and trusted origins",
                "Cross-site request forgery tricks a browser into sending an authenticated cookie with an unwanted mutation. Django's CSRF middleware and template token protect state-changing forms. Configure trusted origins narrowly, keep SameSite settings deliberate, and do not replace CSRF with a hidden field that the server does not validate.",
                "{% csrf_token %}\nCSRF_TRUSTED_ORIGINS = [\"https://admin.example.com\"]",
                "from django.views.decorators.csrf import csrf_protect\n\n\n@csrf_protect\ndef update_course(request, course_id):\n    ...",
                "config/security.py", "The mutation requires a valid CSRF token from a configured trusted origin.",
                "CSRF သည် authenticated cookie ကို အသုံးပြုသော mutation ကို မလိုလားဘဲ မပို့နိုင်စေရန် ကာကွယ်သည်။ Middleware နှင့် template token သုံးပြီး trusted origin ကို ကျဉ်းမြောင်းစွာ configure လုပ်ပါ။",
                "Protect a POST form with csrf_token and test that a missing token is rejected.",
                "Review all state-changing methods and mark which authentication mechanism each uses."),
        _lesson("XSS Prevention", "escaping, safe HTML boundaries, CSP, and output review",
                "Cross-site scripting occurs when attacker-controlled text becomes executable markup or script. Keep auto-escaping enabled, avoid mark_safe for user input, sanitize rich text with an allowlist, use safe DOM APIs, and add a Content-Security-Policy appropriate to the application. Test dangerous strings at every output boundary.",
                "{{ comment.body }}\n# Avoid: {{ comment.body|safe }}",
                "from django.utils.html import escape\n\n\ndef preview_label(value):\n    return escape(value.strip())",
                "learning/safety.py", "A label containing markup is returned as escaped text.",
                "XSS သည် attacker-controlled text ကို executable markup/script အဖြစ် ပြောင်းလဲစေခြင်း ဖြစ်သည်။ Auto-escape ထားပြီး user input ကို safe မလုပ်ပါနှင့်။ Rich text ကို allowlist sanitize လုပ်ပြီး CSP နှင့် output test ထားပါ။",
                "Render a comment containing a script-looking string and verify it is text, not executable markup.",
                "Create an output-boundary checklist for templates, JSON, emails, and client-side DOM updates."),
        _lesson("SQL Injection Prevention", "ORM parameters, raw query boundaries, and least-privilege data access",
                "SQL injection happens when untrusted text changes query structure. Django ORM filters parameterize values, but raw() and cursor.execute() still require placeholders. Never concatenate a search term into SQL, validate dynamic identifiers through an allowlist, and use a database role with only required privileges.",
                "Course.objects.filter(title__icontains=query)\ncursor.execute(\"SELECT id FROM courses WHERE slug = %s\", [slug])",
                "from django.db import connection\n\n\ndef course_by_slug(slug):\n    with connection.cursor() as cursor:\n        cursor.execute(\"SELECT id, title FROM courses WHERE slug = %s\", [slug])\n        return cursor.fetchone()",
                "courses/repository.py", "The slug is passed as a parameter, not concatenated into SQL.",
                "SQL injection သည် untrusted text က query structure ကို ပြောင်းစေခြင်း ဖြစ်သည်။ ORM filter နှင့် SQL placeholder သုံးပါ။ Query string မပေါင်းပါနှင့်။ Dynamic identifier ကို allowlist လုပ်ပြီး database role privilege လျှော့ပါ။",
                "Refactor a string-concatenated query to an ORM filter or parameterized cursor query and add a malicious-input test.",
                "Explain why parameterization does not authorize access to another student's course."),
        _lesson("Unit and Integration Tests", "test isolation, factories, assertions, and useful coverage",
                "Unit tests isolate one function or service; integration tests exercise real framework boundaries such as models, URLs, templates, and transactions. Use a disposable test database, deterministic fixtures, meaningful assertions, and a focused test name. Coverage is a signal, not evidence that assertions are useful.",
                "python manage.py test courses.tests.test_services\nself.assertEqual(response.status_code, 200)",
                "from django.test import TestCase\n\n\nclass CourseListTests(TestCase):\n    def test_draft_courses_are_hidden(self):\n        Course.objects.create(title=\"Draft\", published=False)\n        response = self.client.get(\"/courses/\")\n        self.assertNotContains(response, \"Draft\")",
                "courses/tests/test_views.py", "The public list does not expose a draft course.",
                "Unit test သည် function/service တစ်ခုကို သီးခြားစစ်ပြီး integration test သည် model၊ URL၊ template၊ transaction boundary ကို စစ်သည်။ Disposable test database၊ deterministic fixture နှင့် meaningful assertion သုံးပါ။",
                "Write one service unit test and one public list integration test that protects draft visibility.",
                "Run the focused tests first, then the full suite, and record failures with their request ID or traceback."),
        _lesson("API Testing", "contract assertions, authentication cases, and failure behavior",
                "API tests should assert status, response shape, authorization, validation errors, pagination metadata, and persistence. Test both happy and hostile inputs. Do not assert implementation details such as a private helper call when the contract is what clients rely on.",
                "response = self.client.post(\"/api/v1/courses/\", data=payload, content_type=\"application/json\")\nself.assertEqual(response.status_code, 201)",
                "def test_draft_is_not_public(self):\n    response = self.client.get(\"/api/v1/courses/\")\n    self.assertEqual(response.status_code, 200)\n    self.assertEqual(response.json()[\"items\"], [])",
                "api/tests/test_courses.py", "The API returns the documented collection shape and hides drafts.",
                "API test တွင် status၊ response shape၊ authorization၊ validation error၊ pagination metadata နှင့် persistence ကို စစ်ရမည်။ Happy path နှင့် hostile input နှစ်မျိုးစလုံး test လုပ်ပါ။",
                "Add API tests for anonymous read, unauthorized write, invalid payload, and successful editor update.",
                "Create a contract fixture for a course response and use it to protect future serializer changes."),
        _lesson("Security Review Checklist", "headers, dependencies, secrets, logging, and incident readiness",
                "A security review is a repeatable evidence exercise. Check dependency updates, secret handling, authentication and authorization, CSRF/XSS/SQL injection boundaries, secure headers, upload rules, rate limits, audit logs, backups, and incident response. Record unresolved risks instead of claiming perfect security.",
                "python manage.py check --deploy\npip-audit\npython manage.py test",
                "SECURE_HSTS_SECONDS = 31536000\nSECURE_CONTENT_TYPE_NOSNIFF = True\nSECURE_REFERRER_POLICY = \"same-origin\"",
                "config/settings/production.py", "Deployment checks and secure response headers are reviewed before release.",
                "Security review သည် dependency၊ secret၊ auth၊ CSRF/XSS/SQLi၊ header၊ upload၊ rate limit၊ audit၊ backup နှင့် incident response evidence ကို စစ်သော repeatable process ဖြစ်သည်။ မဖြေရှင်းရသေးသော risk ကို မှတ်တမ်းတင်ပါ။",
                "Run deployment checks in an isolated configuration, inspect headers, and create a risk register with owner and due date.",
                "Review the Django course project against the checklist and attach test or configuration evidence for each item."),
    ],
    10: [
        _lesson("Environment Configuration", "settings modules, environment variables, and secret boundaries",
                "Production configuration must be explicit and separate from local defaults. Read secrets from the deployment environment or a secret manager, validate required values at startup, and keep DEBUG false. Configuration errors should fail safely without printing credentials.",
                "DEBUG = env.bool(\"DJANGO_DEBUG\", default=False)\nSECRET_KEY = env(\"DJANGO_SECRET_KEY\")",
                "from os import environ\n\nDEBUG = environ.get(\"DJANGO_DEBUG\", \"false\").lower() == \"true\"\nif DEBUG is False and not environ.get(\"DJANGO_SECRET_KEY\"):\n    raise RuntimeError(\"DJANGO_SECRET_KEY is required\")",
                "config/settings/production.py", "Production refuses to start without a secret key and does not enable DEBUG by default.",
                "Production configuration သည် local default မှ သီးခြားဖြစ်ရမည်။ Secret ကို environment သို့ secret manager မှ ဖတ်ပြီး required value validate လုပ်ပါ။ DEBUG false ထားပြီး credential များကို error ထဲ မထုတ်ပါနှင့်။",
                "Create a production settings module that validates DEBUG and SECRET_KEY without printing the secret.",
                "List required environment variables, safe defaults, and rotation ownership."),
        _lesson("PostgreSQL in Production", "connection pooling, migrations, backups, and least privilege",
                "PostgreSQL production work includes a dedicated role, TLS where required, bounded connection pooling, migration coordination, backups, restore tests, and monitoring. Django's connection settings must match the deployment topology. A backup is not a recovery plan until a restore has been exercised.",
                "DATABASES = {\"default\": {\"ENGINE\": \"django.db.backends.postgresql\", \"NAME\": env(\"DB_NAME\")}}",
                "DATABASES = {\n    \"default\": {\n        \"ENGINE\": \"django.db.backends.postgresql\",\n        \"NAME\": environ[\"DB_NAME\"],\n        \"USER\": environ[\"DB_USER\"],\n        \"PASSWORD\": environ[\"DB_PASSWORD\"],\n        \"HOST\": environ[\"DB_HOST\"],\n        \"PORT\": environ.get(\"DB_PORT\", \"5432\"),\n    }\n}",
                "config/settings/production.py", "The app reads PostgreSQL connection values from the environment.",
                "Production PostgreSQL တွင် dedicated role၊ TLS၊ bounded pool၊ migration coordination၊ backup နှင့် restore test လိုသည်။ Backup ရှိရုံဖြင့် recovery plan မဖြစ်သေးပါ။",
                "Configure an isolated PostgreSQL connection from environment variables and write a restore drill without touching production.",
                "Prepare a migration, backup, restore, and rollback runbook with explicit approval points."),
        _lesson("Static and Media Storage", "collectstatic, object storage, uploads, and cache headers",
                "Static assets can be collected and served by a CDN or web server; media is application data with ownership and retention rules. Use hashed static filenames, private media URLs when needed, content-type validation, and object-storage lifecycle policies. Never expose storage credentials to the browser.",
                "python manage.py collectstatic --noinput\nSTORAGES = {\"staticfiles\": {\"BACKEND\": \"django.contrib.staticfiles.storage.ManifestStaticFilesStorage\"}}",
                "STORAGES = {\n    \"staticfiles\": {\n        \"BACKEND\": \"django.contrib.staticfiles.storage.ManifestStaticFilesStorage\"\n    },\n    \"default\": {\n        \"BACKEND\": \"storages.backends.s3.S3Storage\"\n    },\n}",
                "config/settings/production.py", "Static files use manifest names while media uses a configured server-side storage backend.",
                "Static asset ကို collectstatic/CDN ဖြင့် serve နိုင်သော်လည်း media သည် ownership/retention ရှိသော application data ဖြစ်သည်။ Hashed filename၊ private URL၊ content validation နှင့် lifecycle policy သုံးပါ။ Credential ကို browser သို့ မပို့ပါနှင့်။",
                "Configure manifest static storage in a test project and document how private media access is authorized.",
                "Create an asset release checklist covering cache invalidation and an upload retention policy."),
        _lesson("Gunicorn and ASGI Deployment", "WSGI/ASGI servers, workers, health checks, and graceful shutdown",
                "Django can run through WSGI for synchronous workloads and ASGI for async-capable deployments. The process manager or container should own restarts, while the application exposes a lightweight health check. Tune worker count from measured CPU, memory, and request behavior; do not copy a universal number.",
                "gunicorn config.wsgi:application --bind 0.0.0.0:8000\ndaphne -b 0.0.0.0 -p 8000 config.asgi:application",
                "[Unit]\nDescription=Django web process\n[Service]\nExecStart=/srv/app/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000\nRestart=on-failure",
                "deploy/codemaster.service", "The service manager starts Gunicorn and restarts it after a failure.",
                "Django ကို synchronous workload အတွက် WSGI နှင့် async-capable deployment အတွက် ASGI ဖြင့် run နိုင်သည်။ Worker count ကို CPU/memory/request behavior တိုင်းတာပြီး သတ်မှတ်ပါ။ Health check နှင့် graceful shutdown ထားပါ။",
                "Write a local service definition with a non-root user, bounded environment, health endpoint, and graceful restart.",
                "Document readiness, liveness, timeout, and rollback behavior for one deployment."),
        _lesson("Docker and CI/CD", "repeatable builds, non-root runtime, tests, and release gates",
                "A production image should use a pinned base, a small build context, a non-root runtime user, and no secrets baked into layers. CI should run formatting, static checks, migrations checks, focused tests, and the full suite before an authorised deployment. Build once and promote the same artifact.",
                "docker build --pull --tag learn-coding-django:ci .\ndocker run --read-only --user 10001:10001 learn-coding-django:ci",
                "FROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nUSER 10001\nCMD [\"gunicorn\", \"config.wsgi:application\"]",
                "Dockerfile", "The container runs the Django process as a non-root numeric user.",
                "Production image တွင် pinned base၊ ကျဉ်းသော build context၊ non-root user နှင့် layer ထဲ secret မပါရပါ။ CI တွင် lint၊ static check၊ migration check နှင့် tests run ပြီး authorization ဖြင့် deploy လုပ်ပါ။",
                "Build a local image with a non-root user and add a CI job that runs Django checks and tests without deploying.",
                "Write a release gate that blocks deployment on failed migrations, tests, or vulnerability findings."),
        _lesson("Logging, Monitoring, and Production Capstone", "structured logs, metrics, traces, alerts, and a safe release",
                "Operational visibility turns a failure into evidence. Log structured events without passwords or tokens, include a request or job id, measure latency and error rate, track database and queue health, and alert on user-impacting symptoms. A capstone release needs a rollback plan, owner, and post-release verification.",
                "logger.info(\"course_publish\", extra={\"request_id\": request_id, \"course_id\": str(course.id)})\nGET /healthz",
                "import logging\n\nlogger = logging.getLogger(\"learning\")\n\n\ndef publish_complete(course, request_id):\n    logger.info(\"course_publish_complete\", extra={\"request_id\": request_id, \"course_id\": str(course.id)})\n    return {\"status\": \"published\"}",
                "learning/observability.py", "The event includes correlation data but not credentials or full request bodies.",
                "Structured log သည် password/token မပါဘဲ request/job id ထည့်ရမည်။ Latency၊ error rate၊ database/queue health တိုင်းပြီး user-impacting symptom ပေါ် alert လုပ်ပါ။ Release တွင် rollback plan နှင့် post-release verification လိုသည်။",
                "Design and test a production release for a Django education app: health check, logs, metrics, migration gate, rollback, and verification.",
                "Submit a capstone runbook with architecture, threat model, test evidence, deployment steps, and an incident rollback rehearsal."),
    ],
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(module_number, position, item):
    previous = "Complete Django Module 1 or equivalent Python web fundamentals." if module_number == 2 and position == 1 else f"Complete the earlier lessons in Module {module_number}, then verify the previous exercise."
    next_step = "Continue to the next lesson in this module." if position < len(LESSONS[module_number]) else f"Continue to Module {module_number + 1} after review." if module_number < 10 else "Complete the Django production capstone and submit it for review."
    return f"""# {item['title']}

## Introduction
{item['title']} covers {item['topic']} in a maintainable Django application.

## Learning objectives
- Explain the boundary and trade-offs of {item['topic']}.
- Build the smallest useful example and verify its expected behavior.
- Identify validation, authorization, and operational risks before shipping.

## Prerequisites
{previous}

## Detailed theory
{item['theory']}

## Core concepts
The framework feature is a boundary, not a substitute for domain rules. Keep inputs explicit, make server-side decisions authoritative, and record the assumptions that make the example reproducible.

## Syntax and usage
```text
{item['syntax']}
```

## Practical code example
File: `{item['filename']}`
```python
{item['code']}
```

## Setup and run
Use an isolated virtual environment, install the project's pinned dependencies, and run `python manage.py check` before exercising the example. Use a disposable test database; never paste production credentials into a lesson or terminal.

## Expected output
{item['output']}

## Line-by-line explanation
1. The first step establishes the Django boundary or input used by the example.
2. The middle statements apply the feature and keep the decision explicit.
3. The final statement returns, stores, or verifies the result described above.
Read the first traceback line that points to your code when the result differs.

## Common mistakes
- Trusting browser-supplied identity, role, or publication fields.
- Skipping CSRF, validation, authorization, or bounded query results.
- Running outside the virtual environment or mixing local and production settings.

## Best practices
- Prefer named URLs, explicit allowlists, server-side authorization, and focused tests.
- Measure database behavior before adding indexes, caches, or async complexity.
- Keep secrets out of source, logs, examples, images, and uploaded files.

## Practical exercises
{item['exercise']}

## Homework
{item['homework']}

## Knowledge quiz
1. What is the main responsibility of the feature in this lesson? Explain it using the example above.
2. Which trust boundary must be validated before the feature is used?
3. True or false: a hidden UI control is sufficient server-side authorization. (Answer: False.)

## Related references
- Django documentation: https://docs.djangoproject.com/
- Django security topics: https://docs.djangoproject.com/en/stable/topics/security/
- Use the project's installed Django version and review release notes before copying an API.

## Lesson summary
You can now apply {item['topic']}, verify the output, and describe the security and operational boundary.

## Next lesson
{next_step}
"""


def _content_mm(module_number, position, item):
    next_step = "နောက် lesson သို့ ဆက်လက်လေ့လာပါ။" if position < len(LESSONS[module_number]) else f"Module {module_number + 1} သို့ reviewer စစ်ဆေးပြီး ဆက်ပါ။" if module_number < 10 else "Django production capstone ကို ပြီးစီးပြီး review အတွက် တင်ပါ။"
    return f"""# {item['title']}

## မိတ်ဆက်
ဤသင်ခန်းစာတွင် {item['mm']} ကို Django application အတွင်း လက်တွေ့လေ့လာပါမည်။

## လေ့လာရမည့် ရည်မှန်းချက်များ
- {item['mm']} ၏ အဓိပ္ပါယ်နှင့် boundary ကို ရှင်းပြနိုင်ရန်။
- ဥပမာကို isolated environment တွင် run ပြီး result စစ်နိုင်ရန်။
- Validation၊ authorization နှင့် production risk များကို ခွဲခြားနိုင်ရန်။

## လိုအပ်သော ကြိုတင်သိထားရမည့်အရာ
ယခင် Django lesson များနှင့် Python၊ terminal အခြေခံများကို ပြန်လည်လေ့လာထားပါ။

## အသေးစိတ်သီအိုရီ
{item['mm']}

## အဓိကအယူအဆများ
Framework feature သည် domain rule ကို အစားမထိုးပါ။ Input ကို စစ်ဆေးပြီး server-side ဆုံးဖြတ်ချက်ကို authoritative ထားကာ assumptions များကို မှတ်တမ်းတင်ပါ။

## Syntax နှင့် အသုံးပြုပုံ
Executable keywords၊ Django API နှင့် CLI command များကို မူရင်းအတိုင်း ထားပါသည်။
```text
{item['syntax']}
```

## လက်တွေ့ code ဥပမာ
File: `{item['filename']}`
```python
{item['code']}
```

## Setup နှင့် run
Virtual environment သီးခြားဖန်တီးပြီး project ၏ pinned dependencies ကို install လုပ်ပါ။ `python manage.py check` ကို အရင် run လုပ်ပါ။ Production credential များကို lesson သို့ မထည့်ပါနှင့်။

## မျှော်မှန်းရလဒ်
{item['output']}

## Code ရှင်းလင်းချက်
အစပိုင်းတွင် Django boundary သို့မဟုတ် input ကို သတ်မှတ်သည်။ အလယ်ပိုင်းတွင် feature ကို အသုံးပြုပြီး ဆုံးဖြတ်ချက်ကို ရှင်းလင်းစွာထားသည်။ နောက်ဆုံးတွင် result ကို ပြန်ပေး သို့မဟုတ် စစ်ဆေးသည်။ Error ဖြစ်ပါက ကိုယ်ရေးထားသော code ကိုညွှန်ပြသော ပထမဆုံး traceback ကို ဖတ်ပါ။

## အများဆုံးမှားတတ်သောအချက်များ
- Browser မှပို့သော identity၊ role သို့မဟုတ် publication field ကို ယုံခြင်း။
- CSRF၊ validation၊ authorization သို့မဟုတ် query limit မထည့်ခြင်း။
- Virtual environment မဖွင့်ဘဲ command run ခြင်း။

## ကောင်းမွန်သောနည်းလမ်းများ
- Named URL၊ explicit allowlist၊ server-side authorization နှင့် focused test သုံးပါ။
- Index၊ cache သို့မဟုတ် async complexity မထည့်မီ အမှန်တကယ် တိုင်းတာပါ။
- Secret များကို source၊ log၊ example နှင့် upload file ထဲ မထားပါနှင့်။

## လက်တွေ့လေ့ကျင့်ခန်း
{item['exercise']}

## အိမ်စာ
{item['homework']}

## အသိပညာစစ်ဆေးရန်
1. ဤ lesson မှ feature ၏ အဓိကတာဝန်ကို ဥပမာဖြင့် ရှင်းပြပါ။
2. Feature ကို အသုံးမပြုမီ ဘယ် trust boundary ကို စစ်ရမလဲ။
3. UI control ကို ဖျောက်ထားရုံဖြင့် server-side authorization ပြည့်စုံသည်။ (အဖြေ: မမှန်ပါ။)

## ဆက်စပ်ရည်ညွှန်းချက်များ
- Django documentation: https://docs.djangoproject.com/
- Django security topics: https://docs.djangoproject.com/en/stable/topics/security/
- Project ထဲတွင် install လုပ်ထားသော Django version နှင့် release notes ကို စစ်ပါ။

## သင်ခန်းစာအနှစ်ချုပ်
{item['mm']} ကို လက်တွေ့အသုံးပြုပြီး output၊ security နှင့် operational boundary ကို ရှင်းပြနိုင်ပါပြီ။

## နောက် lesson
{next_step}
"""


def _ensure_quiz(db, lesson, item):
    quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
    if not quiz:
        quiz = LessonQuiz(lesson_id=lesson.id, title=f"{item['title']} knowledge check", explanation="Review the lesson and verify the trust boundary before retrying.", status="draft")
        db.add(quiz)
        db.flush()
    questions = [
        (f"Which practice is most important when applying {item['topic']}?", ["Validate input and enforce the server-side boundary", "Trust every browser field", "Skip tests"], "Validate input and enforce the server-side boundary", "Django features still need explicit validation, authorization, and tests."),
        ("What should a learner verify after running the example?", [item["output"], "A production database deletion", "A secret printed to logs"], item["output"], "The expected output is the evidence for this lesson's local example."),
        ("A hidden UI control is sufficient server-side authorization.", ["True", "False"], "False", "The server must enforce authorization for every protected operation."),
    ]
    for position, (prompt, options, answer, explanation) in enumerate(questions, 1):
        question = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
        values = {"prompt": prompt, "question_type": "true_false" if options == ["True", "False"] else "multiple_choice", "options_json": json.dumps(options), "correct_answer": answer, "explanation": explanation}
        if not question:
            db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
        elif not question.prompt.strip():
            for key, value in values.items():
                setattr(question, key, value)


def _ensure_exercise(db, lesson, title, description_en, description_mm):
    """Attach one reviewable coding/practical exercise without duplicates."""
    slug = f"django-{lesson.slug}-practice"
    exercise = db.scalar(select(CodingExercise).where(CodingExercise.slug == slug))
    if exercise:
        return
    db.add(CodingExercise(
        lesson_id=lesson.id,
        title=f"{title} practice",
        slug=slug,
        description_en=description_en,
        description_mm=description_mm,
        difficulty="beginner" if lesson.order_index <= 2 else "intermediate",
        language="python",
        starter_code="# Implement the exercise in an isolated Django project.\n",
        status="draft",
    ))


def seed_django_additional_curriculum(db, course):
    """Add Django Modules 2-10 without changing existing lesson identities.

    Existing lessons are located by ``module_id`` and ``order_index``.  An
    existing non-empty lesson is never rewritten.  New or empty lessons are
    complete drafts, and their quizzes/examples are inserted idempotently.
    """
    created_modules = 0
    created_lessons = 0
    preserved_lessons = 0
    for module_number, module_title in MODULES.items():
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_number))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_number)
            db.add(module)
            db.flush()
            created_modules += 1
        elif module.title != module_title:
            module.title = module_title
        for position, item in enumerate(LESSONS[module_number], 1):
            slug = f"{module_number:02d}-{_slug(item['title'])}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == position))
            is_new = lesson is None
            if lesson is None:
                lesson = Lesson(module_id=module.id, title=item["title"], slug=slug, order_index=position, content_en="", content_mm="")
                db.add(lesson)
                db.flush()
                created_lessons += 1
            if lesson.content_en and lesson.content_en.strip():
                preserved_lessons += 1
            else:
                lesson.title = item["title"]
                lesson.slug = lesson.slug or slug
                lesson.description = item["topic"]
                lesson.content_en = _content(module_number, position, item)
                lesson.content_mm = _content_mm(module_number, position, item)
                lesson.duration_minutes = 45
                lesson.status = "draft"
                lesson.published = False

            example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
            if not example:
                db.add(CodeExample(lesson_id=lesson.id, title=f"{item['title']} example", language="python", filename=item["filename"], code=item["code"], description=f"Expected output: {item['output']}\n\nRun only in an isolated local Django project.", position=1))
            _ensure_quiz(db, lesson, item)
            _ensure_exercise(db, lesson, item["title"], item["exercise"], f"{item['mm']} ကို isolated Django project ထဲတွင် လက်တွေ့လေ့ကျင့်ပါ။")
    db.flush()
    return {"created_modules": created_modules, "created_lessons": created_lessons, "preserved_lessons": preserved_lessons, "draft_modules": len(MODULES), "draft_lessons": sum(len(items) for items in LESSONS.values())}
