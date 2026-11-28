"""Authored draft content for Django Module 05: models, ORM and PostgreSQL.

This module is deliberately scoped to the canonical fifth module of the
``django`` course.  It keeps existing lesson identities and published rows
protected, while making the existing draft placeholder useful for review.
The examples are educational source files; they are not run against the
Learn-Coding database.
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


MODULE_TITLE = "Django Models, ORM and PostgreSQL"
MODULE_TITLE_MM = "Django Model၊ ORM နှင့် PostgreSQL"
MODULE_DESCRIPTION = (
    "Design durable Django models, configure PostgreSQL safely, evolve schemas with migrations, "
    "query data with the ORM, model relationships, optimize database access, and protect writes "
    "with constraints and transactions."
)
MODULE_DESCRIPTION_MM = (
    "Django model များကို ခိုင်မာစွာ design လုပ်ခြင်း၊ PostgreSQL ကို လုံခြုံစွာ configure လုပ်ခြင်း၊ "
    "migration ဖြင့် schema ပြောင်းလဲခြင်း၊ ORM query ရေးခြင်း၊ relationship တည်ဆောက်ခြင်း၊ "
    "database access ကို optimize လုပ်ခြင်းနှင့် constraint/transaction ဖြင့် data integrity ကာကွယ်ခြင်းကို လေ့လာမည့် module ဖြစ်သည်။"
)
OBJECTIVES = [
    "Design normalized Student, Course, Profile and Enrollment models with appropriate field types and constraints.",
    "Configure an isolated PostgreSQL database through environment variables and verify the connection without exposing secrets.",
    "Create, inspect, test and safely evolve migrations without resetting a database or dropping useful history.",
    "Use lazy QuerySets, CRUD operations, filtering, pagination, relationships, annotations and aggregation accurately.",
    "Diagnose N+1 queries and choose select_related(), prefetch_related(), indexes and explain() from measured query patterns.",
    "Implement atomic enrollment workflows with database constraints, safe exception handling and concurrency-aware locking.",
]
OBJECTIVES_MM = [
    "Field type နှင့် constraint သင့်တော်စွာသုံးပြီး Student၊ Course၊ Profile နှင့် Enrollment model များကို normalized design လုပ်နိုင်ရန်။",
    "Environment variable မှတစ်ဆင့် isolated PostgreSQL database ကို configure လုပ်ပြီး secret မဖော်ဘဲ connection စစ်နိုင်ရန်။",
    "Database ကို reset/drop မလုပ်ဘဲ migration ဖန်တီး၊ စစ်ဆေး၊ test လုပ်ပြီး schema ကို လုံခြုံစွာပြောင်းနိုင်ရန်။",
    "Lazy QuerySet၊ CRUD၊ filtering၊ pagination၊ relationship၊ annotation နှင့် aggregation ကို မှန်ကန်စွာအသုံးပြုနိုင်ရန်။",
    "N+1 query ကို ရှာဖွေပြီး တိုင်းတာထားသော query pattern အပေါ်မူတည်၍ select_related၊ prefetch_related၊ index နှင့် explain ကို ရွေးနိုင်ရန်။",
    "Constraint၊ exception handling နှင့် concurrency-aware locking ဖြင့် atomic enrollment workflow တည်ဆောက်နိုင်ရန်။",
]


def _example(title, files, input_text, output, steps, steps_mm):
    return {"title": title, "files": files, "input": input_text, "output": output, "steps": steps, "steps_mm": steps_mm}


def _q(prompt, options, answer, explanation, difficulty="intermediate", lesson=1):
    return {
        "prompt": prompt,
        "options": options,
        "correct_answer": answer,
        "explanation": explanation,
        "difficulty": difficulty,
        "points": 2 if difficulty == "intermediate" else 3 if difficulty == "advanced" else 1,
        "lesson_position": lesson,
    }


COMMON_PREREQ = "Complete Django Modules 01–04, know Python classes and functions, and use a dedicated isolated learning project. The project database is school_portal_dev; never point tutorial commands at the Learn-Coding platform database."
COMMON_PREREQ_MM = "Django Module 01–04 ပြီးထားရမည်။ Python class/function ကို နားလည်ပြီး သီးခြား isolated learning project သုံးပါ။ Project database သည် school_portal_dev ဖြစ်ပြီး tutorial command များကို Learn-Coding platform database သို့ မညွှန်ပါနှင့်။"


LESSONS = [
    {
        "title": "Django Models, Fields and Database Design",
        "slug": "05-django-forms",
        "description": "Turn an education domain into explicit Django model classes, field definitions, validation rules and readable database metadata.",
        "description_mm": "Education domain ကို Django model class၊ field definition၊ validation rule နှင့် ဖတ်ရှုလွယ်သော database metadata အဖြစ် တည်ဆောက်ပါ။",
        "topic": "model classes, field types, null versus blank, defaults, choices, validators, Meta options and schema design",
        "theory": "A Django model is the application’s definitive description of a persisted domain object. A model normally maps to one database table, and each field maps to a column. Django adds a primary key when one is not declared, but the design decision still matters: a natural identifier such as email may be unique while an internal key remains stable. CharField needs a maximum length; TextField is appropriate for unbounded prose; IntegerField and PositiveIntegerField express counts; DecimalField is safer than floating point for money; BooleanField represents a true/false state; DateField and DateTimeField carry different time semantics; EmailField adds model-level validation; UUIDField can expose an opaque identifier. null is a database storage decision, while blank is a validation/form decision, so a text field often uses blank=True rather than null=True. Defaults should be deterministic and callable when a fresh value is required. choices improve readability but are not a substitute for business validation. Validators run during validation, and save() does not automatically call full_clean(). Meta can define ordering, indexes and constraints, while __str__ should provide a useful human label. Design tables around stable concepts, avoid storing derived values unnecessarily, and decide deletion behavior before data exists.",
        "theory_mm": "Django model သည် သိမ်းဆည်းထားသော domain object ၏ အဓိကအဓိပ္ပာယ်ဖော်ပြချက် ဖြစ်သည်။ ပုံမှန်အားဖြင့် model တစ်ခုသည် database table တစ်ခုနှင့် field တစ်ခုသည် column တစ်ခုနှင့် ကိုက်ညီသည်။ Primary key ကို မရေးလျှင် Django က ထည့်ပေးသော်လည်း identifier design ကို လျစ်လျူမရှုသင့်ပါ။ Email ကဲ့သို့ natural identifier ကို unique ထားနိုင်သော်လည်း internal key သည် တည်ငြိမ်နေသင့်သည်။ CharField တွင် max_length လိုပြီး TextField သည် ရှည်သောစာအတွက် သင့်တော်သည်။ IntegerField/PositiveIntegerField သည် အရေအတွက်ကို ဖော်ပြပြီး ငွေကြေးအတွက် floating point ထက် DecimalField က ပိုလုံခြုံသည်။ BooleanField သည် true/false၊ DateField နှင့် DateTimeField သည် date/time အဓိပ္ပာယ်မတူမှုကို ဖော်ပြသည်။ EmailField သည် model-level validation ရှိသည်။ UUIDField သည် ခန့်မှန်းရခက်သော identifier သုံးနိုင်စေသည်။ null သည် database storage ဆိုင်ရာဆုံးဖြတ်ချက်၊ blank သည် validation/form ဆိုင်ရာဆုံးဖြတ်ချက်ဖြစ်သောကြောင့် text field တွင် blank=True ကိုသာသုံးလေ့ရှိသည်။ Default သည် deterministic ဖြစ်သင့်ပြီး fresh value လိုလျှင် callable သုံးပါ။ choices သည် ဖတ်ရှုလွယ်စေသော်လည်း business validation အစားထိုးမဟုတ်ပါ။ Validators သည် validation အချိန်တွင်လုပ်ဆောင်ပြီး save() က full_clean() ကို အလိုအလျောက်မခေါ်ပါ။ Meta မှ ordering၊ index၊ constraint သတ်မှတ်နိုင်ပြီး __str__ သည် လူဖတ်လွယ်သော label ပြန်သင့်သည်။ Data မရှိမီ deletion behavior ကို ဆုံးဖြတ်ပါ။",
        "concepts": "Model/table mapping; primary key; field metadata; null and blank; callable defaults; choices; validators; model validation; Meta.ordering; Meta.constraints; __str__; normalization; derived data; stable identifiers.",
        "concepts_mm": "Model/table mapping၊ primary key၊ field metadata၊ null/blank၊ callable default၊ choices၊ validator၊ model validation၊ Meta.ordering၊ Meta.constraints၊ __str__၊ normalization၊ derived data နှင့် stable identifier တို့ကို လေ့လာရမည်။",
        "syntax": "class Student(models.Model):\n    email = models.EmailField(unique=True)\n    age = models.PositiveIntegerField(null=True, blank=True)\n    joined_at = models.DateTimeField(auto_now_add=True)\n\n    class Meta:\n        ordering = [\"last_name\", \"first_name\"]",
        "examples": [
            _example("Create a Student model", {"students/models.py": "from django.core.validators import MinValueValidator\nfrom django.db import models\n\nclass Student(models.Model):\n    first_name = models.CharField(max_length=80)\n    last_name = models.CharField(max_length=80)\n    email = models.EmailField(unique=True)\n    age = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(13)])\n    joined_at = models.DateTimeField(auto_now_add=True)\n\n    class Meta:\n        ordering = [\"last_name\", \"first_name\"]\n\n    def __str__(self):\n        return f\"{self.first_name} {self.last_name}\""}, "A new app named students", "makemigrations detects a Student table with a unique email column and automatic primary key.", "Create the app, add it to INSTALLED_APPS, run check, then inspect the generated migration before applying it.", "App ပြုလုပ်ပြီး INSTALLED_APPS ထဲထည့်ပါ။ check run လုပ်ပြီး generated migration ကို စစ်ပြီးမှ apply လုပ်ပါ။"),
            _example("Model choices and defaults", {"students/models.py": "class Enrollment(models.Model):\n    class Status(models.TextChoices):\n        ACTIVE = \"active\", \"Active\"\n        COMPLETED = \"completed\", \"Completed\"\n        ARCHIVED = \"archived\", \"Archived\"\n\n    status = models.CharField(max_length=20, choices=Status, default=Status.ACTIVE)\n    notes = models.TextField(blank=True, default=\"\")"}, "Create an Enrollment instance without status", "Django stores the ACTIVE default and permits an empty notes value during validation.", "Use a TextChoices class for stable stored values and keep labels for human presentation.", "TextChoices ဖြင့် သိမ်းမည့် value နှင့် လူဖတ် label ခွဲပါ။ Default နှင့် optional notes ကို သတ်မှတ်ပါ။"),
            _example("Validate before a service save", {"students/services.py": "from django.core.exceptions import ValidationError\n\ndef save_student(**values):\n    student = Student(**values)\n    student.full_clean()\n    student.save()\n    return student"}, "email='learner@example.test', age=12", "full_clean() raises ValidationError before the database write because the age validator requires 13 or older.", "Construct the instance, run full_clean explicitly at the service boundary, then save only after validation succeeds.", "Instance တည်ဆောက်ပြီး service boundary တွင် full_clean() အရင်ခေါ်ပါ။ အောင်မြင်မှ save လုပ်ပါ။"),
            _example("Design an education schema", {"students/models.py": "class StudentProfile(models.Model):\n    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name=\"profile\")\n    guardian_phone = models.CharField(max_length=32, blank=True)\n\nclass Course(models.Model):\n    code = models.CharField(max_length=20, unique=True)\n    title = models.CharField(max_length=160)\n    credits = models.PositiveSmallIntegerField(default=1)"}, "Student, profile and course concepts", "The schema separates student identity, optional profile data and course identity instead of repeating columns.", "Identify entities first, decide ownership and optionality, then encode the relationship and uniqueness rules.", "Entity များကို အရင်ခွဲပါ။ Ownership/optionality ဆုံးဖြတ်ပြီး relationship နှင့် uniqueness rule ထည့်ပါ။"),
        ],
        "mistakes": ["Using null=True and blank=True interchangeably without deciding storage and validation semantics.", "Assuming save() runs full_clean().", "Using FloatField for currency or storing repeated derived totals without a consistency plan.", "Making every field nullable instead of modeling required domain facts."],
        "mistakes_mm": ["Storage နှင့် validation အဓိပ္ပာယ်မခွဲဘဲ null=True/blank=True ကို အတူတူသုံးခြင်း။", "save() က full_clean() အလိုအလျောက်ခေါ်သည်ဟု ယူဆခြင်း။", "ငွေကြေးအတွက် FloatField သုံးခြင်း သို့မဟုတ် derived total ကို စနစ်မရှိဘဲ ထပ်သိမ်းခြင်း။", "လိုအပ်သော domain fact အားလုံးကို nullable ထားခြင်း။"],
        "best_practices": "Keep one authoritative field for each fact, use explicit names and help text, choose database and validation options separately, add constraints for invariants, test full_clean at service boundaries, and document the reason for every non-default on_delete choice.",
        "best_practices_mm": "Fact တစ်ခုအတွက် authoritative field တစ်ခုသာထားပါ။ အမည်/အဓိပ္ပာယ်ရှင်းလင်းစွာရေးပါ။ Database option နှင့် validation option ကို ခွဲစဉ်းစားပြီး invariant အတွက် constraint ထည့်ပါ။ Service boundary တွင် full_clean test လုပ်ကာ on_delete ရွေးချယ်မှု၏အကြောင်းရင်းကို မှတ်တမ်းတင်ပါ။",
        "exercises": "Create Student, StudentProfile, Course and Enrollment model sketches. Add email uniqueness, a non-negative age, a status choice, a readable __str__, Meta ordering, and one validator. Run check and inspect the migration without applying it to a production database.",
        "exercises_mm": "Student၊ StudentProfile၊ Course နှင့် Enrollment model sketch ပြုလုပ်ပါ။ Email uniqueness၊ non-negative age၊ status choice၊ __str__၊ Meta ordering နှင့် validator တစ်ခုထည့်ပါ။ check run လုပ်ပြီး production database မသုံးဘဲ migration စစ်ပါ။",
        "homework": "Submit an Education Database Model Design document that lists entities, fields, required/optional decisions, identifiers, deletion policies, constraints, and one example query for each relationship.",
        "homework_mm": "Entity၊ field၊ required/optional ဆုံးဖြတ်ချက်၊ identifier၊ deletion policy၊ constraint နှင့် relationship တစ်ခုစီအတွက် query ဥပမာပါသော Education Database Model Design document တင်ပါ။",
        "summary": "Models are a contract between domain language and database structure. Field options, validation and constraints should express real invariants instead of hiding them in views.",
        "summary_mm": "Model သည် domain language နှင့် database structure ကြား contract ဖြစ်သည်။ Field option၊ validation နှင့် constraint များသည် view ထဲဖုံးထားသော rule မဟုတ်ဘဲ တကယ့် invariant ကို ဖော်ပြသင့်သည်။",
        "quiz": [
            _q("Which class is the base for a Django model?", ["models.Model", "models.Table", "models.Record", "models.Schema"], "models.Model", "Django model classes subclass django.db.models.Model.", "beginner", 1),
            _q("What does blank=True primarily affect?", ["Validation and forms", "PostgreSQL table existence", "Primary key generation", "Index order"], "Validation and forms", "blank controls whether validation permits an empty value.", "intermediate", 1),
            _q("What does unique=True enforce?", ["A uniqueness constraint for the field", "Automatic encryption", "A default value", "A database connection"], "A uniqueness constraint for the field", "The database and Django validation enforce uniqueness semantics.", "intermediate", 1),
            _q("True or false: model.save() always calls full_clean().", ["True", "False"], "False", "Call full_clean explicitly when that validation boundary is required.", "intermediate", 1),
            _q("Which field is appropriate for exact decimal money values?", ["DecimalField", "FloatField", "BooleanField", "TextField"], "DecimalField", "DecimalField stores fixed precision and scale.", "beginner", 1),
            _q("Why use a callable default for a fresh timestamp or UUID?", ["It is evaluated for each new instance", "It disables migrations", "It exposes a secret", "It creates a relationship"], "It is evaluated for each new instance", "A callable avoids reusing one value created at import time.", "advanced", 1),
            _q("What is a useful __str__ implementation for?", ["A readable representation in admin and logs", "Running SQL joins", "Creating a database", "Disabling validation"], "A readable representation in admin and logs", "It improves human-facing object labels.", "beginner", 1),
            _q("Where is default ordering commonly declared?", ["class Meta", "settings.py only", "urls.py", "forms.py only"], "class Meta", "Meta.ordering describes a model's default query ordering.", "intermediate", 1),
        ],
    },
    {
        "title": "Django Database Configuration and Connection Management",
        "slug": "05-modelforms",
        "description": "Configure SQLite for a safe local demonstration, PostgreSQL for the learning project, and environment-driven credentials for development and production.",
        "description_mm": "Safe local demo အတွက် SQLite၊ learning project အတွက် PostgreSQL နှင့် development/production အတွက် environment-driven credential ကို configure လုပ်ပါ။",
        "topic": "DATABASES, backend engines, environment variables, connection lifecycle, health checks, multiple databases and troubleshooting",
        "theory": "Django routes ORM operations through the DATABASES setting. The default alias is usually named default and contains ENGINE plus backend-specific NAME, USER, PASSWORD, HOST and PORT values. SQLite is convenient for a tiny local demo because it is file-based, but PostgreSQL is the target for this module because it offers a server, roles, stronger concurrency behavior and production-grade features. Configuration must be environment-driven: commit a safe example such as DATABASE_URL without real credentials, load secrets from the process environment or a secret manager, and never render them in a response or log. Persistent connections are controlled by CONN_MAX_AGE; a health check should use a lightweight query and report a safe status without returning connection details. Multiple database aliases and routers are advanced tools, not a reason to scatter model reads across arbitrary connections. Connection failures can be authentication, DNS/host, port, database existence, TLS, role permission or driver problems. Diagnose one boundary at a time and use a dedicated school_portal_dev database, never the platform database.",
        "theory_mm": "Django သည် ORM operation များကို DATABASES setting မှတစ်ဆင့် database သို့ပို့သည်။ ပုံမှန် default alias တွင် ENGINE၊ backend အလိုက် NAME၊ USER၊ PASSWORD၊ HOST နှင့် PORT ပါသည်။ SQLite သည် file-based ဖြစ်သောကြောင့် သေးငယ်သော local demo အတွက် လွယ်ကူသော်လည်း ဤ module ၏ target သည် server၊ role၊ concurrency နှင့် production feature များရှိသော PostgreSQL ဖြစ်သည်။ Configuration ကို environment-driven ထားပါ။ Real credential မပါသော DATABASE_URL example ကိုသာ commit လုပ်ပြီး secret ကို process environment သို့မဟုတ် secret manager မှ load ပါ။ Browser response/log ထဲ password မထည့်ပါနှင့်။ Persistent connection ကို CONN_MAX_AGE ဖြင့် ထိန်းနိုင်ပြီး health check သည် ပေါ့ပါးသော query ဖြင့် safe status သာ ပြသသင့်သည်။ Multiple database alias နှင့် router သည် advanced feature ဖြစ်ပြီး query များကို မည်သည့် connection မဆို ဖြန့်ရန် အကြောင်းမဟုတ်ပါ။ Connection error သည် authentication၊ host၊ port၊ database မရှိခြင်း၊ TLS၊ role permission သို့မဟုတ် driver ပြဿနာဖြစ်နိုင်သည်။ Boundary တစ်ခုချင်းစီ စစ်ဆေးပြီး school_portal_dev ကိုသာ သုံးပါ။",
        "concepts": "DATABASES alias; ENGINE; NAME; USER; PASSWORD; HOST; PORT; environment variables; .env hygiene; connection lifecycle; CONN_MAX_AGE; health checks; multiple databases; routers; least privilege; safe error messages.",
        "concepts_mm": "DATABASES alias၊ ENGINE၊ NAME၊ USER၊ PASSWORD၊ HOST၊ PORT၊ environment variable၊ .env hygiene၊ connection lifecycle၊ CONN_MAX_AGE၊ health check၊ multiple database၊ router၊ least privilege နှင့် safe error message တို့ကို လေ့လာရမည်။",
        "syntax": "DATABASES = {\n    \"default\": {\n        \"ENGINE\": \"django.db.backends.postgresql\",\n        \"NAME\": env(\"POSTGRES_DB\"),\n        \"USER\": env(\"POSTGRES_USER\"),\n        \"PASSWORD\": env(\"POSTGRES_PASSWORD\"),\n        \"HOST\": env(\"POSTGRES_HOST\", default=\"127.0.0.1\"),\n        \"PORT\": env(\"POSTGRES_PORT\", default=\"5432\"),\n    }\n}",
        "examples": [
            _example("Inspect DATABASES safely", {"school_site/settings.py": "import os\n\nDATABASES = {\n    \"default\": {\n        \"ENGINE\": os.environ.get(\"DB_ENGINE\", \"django.db.backends.sqlite3\"),\n        \"NAME\": os.environ.get(\"DB_NAME\", BASE_DIR / \"db.sqlite3\"),\n    }\n}\n\ndef database_summary():\n    config = DATABASES[\"default\"]\n    return {\"ENGINE\": config[\"ENGINE\"], \"NAME_SET\": bool(config.get(\"NAME\"))}\n", "docs/command.txt": "python manage.py check"}, "Local settings inspection", "The summary reports engine and whether a name exists, but never prints a password.", "Keep a diagnostic summary allow-list based and make secrets impossible to include accidentally.", "Diagnostic summary တွင် allow-list သတ်မှတ်ပြီး password မထွက်နိုင်အောင်ထားပါ။"),
            _example("Use SQLite for a local demo", {"school_site/settings.py": "DATABASES = {\n    \"default\": {\n        \"ENGINE\": \"django.db.backends.sqlite3\",\n        \"NAME\": BASE_DIR / \"school_portal_demo.sqlite3\",\n    }\n}"}, "A clean demo checkout", "migrate creates the local SQLite schema file; no server process or production credential is required.", "Use SQLite only for the small demo, run migrate, and keep the file outside any production data path.", "သေးငယ်သော demo အတွက် SQLite သုံးပြီး migrate run လုပ်ပါ။ Production data path နှင့် မရောပါနှင့်။"),
            _example("Configure PostgreSQL from environment", {"school_site/settings.py": "import os\n\nDATABASES = {\n    \"default\": {\n        \"ENGINE\": \"django.db.backends.postgresql\",\n        \"NAME\": os.environ[\"POSTGRES_DB\"],\n        \"USER\": os.environ[\"POSTGRES_USER\"],\n        \"PASSWORD\": os.environ[\"POSTGRES_PASSWORD\"],\n        \"HOST\": os.environ.get(\"POSTGRES_HOST\", \"127.0.0.1\"),\n        \"PORT\": os.environ.get(\"POSTGRES_PORT\", \"5432\"),\n        \"CONN_MAX_AGE\": 60,\n    }\n}\n", ".env.example": "POSTGRES_DB=school_portal_dev\nPOSTGRES_USER=school_portal_app\nPOSTGRES_PASSWORD=replace-locally\nPOSTGRES_HOST=127.0.0.1\nPOSTGRES_PORT=5432"}, "Environment variables from .env or the process", "Django receives the configured backend without credentials appearing in source control or HTTP output.", "Create a local .env from the example, load it with the chosen environment tool, run check, and verify only the database name/host in logs.", "Example မှ .env local copy ပြုလုပ်ပြီး environment tool ဖြင့် load ပါ။ Log တွင် name/host ပဲ စစ်ပါ။"),
            _example("Check connectivity without leaking details", {"school_site/health.py": "from django.db import connection\n\ndef database_ready():\n    try:\n        with connection.cursor() as cursor:\n            cursor.execute(\"SELECT 1\")\n            return cursor.fetchone() == (1,)\n    except Exception:\n        return False"}, "A request to an internal readiness check", "The check returns True/False; it does not reveal a password, DSN or SQL exception to students.", "Keep the detailed exception in protected server logs, return a generic unhealthy status to the caller, and alert operators separately.", "အသေးစိတ် exception ကို protected server log တွင်သာထားပြီး caller ထံ generic unhealthy status ပေးပါ။"),
        ],
        "mistakes": ["Committing a real .env file or putting a password in a screenshot.", "Using 0.0.0.0 as a database host without understanding the network boundary.", "Treating a successful import as proof that the database is reachable.", "Returning raw driver errors and connection strings to browser clients."],
        "mistakes_mm": ["Real .env သို့မဟုတ် password ပါသော screenshot commit လုပ်ခြင်း။", "Network boundary မသိဘဲ database host ကို 0.0.0.0 ထားခြင်း။", "Import အောင်မြင်ရုံဖြင့် database reachable ဖြစ်သည်ဟု ယူဆခြင်း။", "Raw driver error/connection string ကို browser သို့ ပြန်ခြင်း။"],
        "best_practices": "Use a checked-in .env.example with synthetic values, fail fast when required variables are missing, separate local/demo and production settings, use least-privilege roles, set connection lifetime intentionally, and make readiness checks observable without becoming a secret oracle.",
        "best_practices_mm": "Synthetic value ပါသော .env.example ကိုသာ commit လုပ်ပါ။ လိုအပ်သော variable မရှိလျှင် အစောပိုင်း fail လုပ်ပါ။ Local/demo နှင့် production setting ခွဲပါ။ Least-privilege role သုံးပြီး connection lifetime ကို ရည်ရွယ်ချက်ရှိစွာသတ်မှတ်ပါ။ Readiness check ကို secret မဖော်ဘဲ observable ဖြစ်စေပါ။",
        "exercises": "Write a configuration checklist for SQLite demo and PostgreSQL school_portal_dev. Include required environment variables, safe diagnostics, role permissions, health-check behavior, and a troubleshooting decision tree for refused connection versus authentication failure.",
        "exercises_mm": "SQLite demo နှင့် PostgreSQL school_portal_dev အတွက် configuration checklist ရေးပါ။ Required environment variable၊ safe diagnostic၊ role permission၊ health-check behavior နှင့် refused connection/authentication failure troubleshooting decision tree ပါစေ။",
        "homework": "Create a safe local database configuration guide that another learner can follow without receiving a real password. Include copy-paste commands only with placeholders and explain how to rotate credentials.",
        "homework_mm": "Real password မပါဘဲ အခြား learner လိုက်လုပ်နိုင်သော safe local database configuration guide ပြုလုပ်ပါ။ Placeholder command နှင့် credential rotate လုပ်ပုံပါစေ။",
        "summary": "Database configuration is an operational boundary. Keep it environment-driven, least-privileged, observable and deliberately separate from student-facing content.",
        "summary_mm": "Database configuration သည် operational boundary ဖြစ်သည်။ Environment-driven၊ least-privilege၊ observable ဖြစ်ပြီး student-facing content နှင့် သီးခြားထားရမည်။",
        "quiz": [
            _q("Which DATABASES key selects Django's PostgreSQL backend?", ["ENGINE", "HOST", "PORT", "NAME"], "ENGINE", "ENGINE identifies the database backend.", "beginner", 2),
            _q("Why should a password not appear in a browser health response?", ["It is a secret and exposes database access", "Browsers cannot display text", "PostgreSQL forbids strings", "Django requires a template"], "It is a secret and exposes database access", "Health endpoints should reveal readiness, not credentials.", "intermediate", 2),
            _q("What is school_portal_dev in this module?", ["An isolated educational database", "The platform production database", "A Python package", "A CSS file"], "An isolated educational database", "Tutorial writes must be isolated from platform data.", "beginner", 2),
            _q("What does CONN_MAX_AGE control?", ["The lifetime of persistent connections", "The password length", "The table name", "The migration number"], "The lifetime of persistent connections", "It controls persistent connection reuse.", "intermediate", 2),
            _q("Which error class suggests a connection cannot reach the host/port?", ["Network/refused connection", "Template syntax only", "ValidationError only", "URL reversing"], "Network/refused connection", "Host and port failures occur before authentication.", "intermediate", 2),
            _q("True or false: .env.example should contain a real production password.", ["True", "False"], "False", "Examples must use placeholders or synthetic local values.", "beginner", 2),
            _q("What is least privilege?", ["Grant only the database permissions the app needs", "Give every user superuser access", "Hide all logs", "Disable migrations"], "Grant only the database permissions the app needs", "Reduced permissions limit blast radius.", "intermediate", 2),
            _q("A readiness check should normally return what to a student client?", ["A safe status", "The DSN and password", "A raw stack trace", "All environment variables"], "A safe status", "Detailed diagnostics belong in protected operations logs.", "intermediate", 2),
        ],
    },
    {
        "title": "Connecting Django to PostgreSQL",
        "slug": "05-validation-and-clean-methods",
        "description": "Build a safe PostgreSQL connection for the Student Portal, understand roles and schemas, and verify the driver/backend boundary.",
        "description_mm": "Student Portal အတွက် safe PostgreSQL connection တည်ဆောက်ပြီး role/schema နှင့် driver/backend boundary ကို စစ်ဆေးပါ။",
        "topic": "PostgreSQL server architecture, databases, schemas, roles, psycopg, timezone awareness and safe connection verification",
        "theory": "PostgreSQL separates a server cluster, databases, schemas, roles and objects. A Django connection chooses one database and authenticates a role; the role should own only the objects and actions needed by the application. A schema is a namespace inside a database, not a replacement for a separate database. Django’s PostgreSQL backend uses psycopg 3 or a supported alternative. For the Django 6.0 target, PostgreSQL 14 or newer and psycopg 3.1.12 or newer are documented support baselines; prefer a current compatible psycopg 3 release and record the exact lockfile version. Use UTC/timezone-aware datetimes, avoid putting a password in a command that will be saved in shell history, and create a separate school_portal_dev database and role. Connection verification should include python manage.py check, a safe SELECT 1 readiness query, and a migration dry-run plan in the isolated project. SQL inspection is useful, but destructive commands such as DROP DATABASE are deliberately outside this course workflow. Pooling and persistent connections change operational behavior and should be introduced only after measuring the deployment environment.",
        "theory_mm": "PostgreSQL သည် server cluster၊ database၊ schema၊ role နှင့် object များကို ခွဲထားသည်။ Django connection သည် database တစ်ခုကိုရွေးပြီး role ဖြင့် authenticate လုပ်ရသည်။ Role သည် app လိုအပ်သည့် object/action များကိုသာ ရပိုင်ခွင့်ရှိသင့်သည်။ Schema သည် database အတွင်း namespace ဖြစ်ပြီး database သီးခြားတစ်ခု၏ အစားထိုးမဟုတ်ပါ။ Django PostgreSQL backend သည် psycopg 3 သို့မဟုတ် support လုပ်သော alternative ကို သုံးသည်။ Django 6.0 target အတွက် PostgreSQL 14 နှင့်အထက်၊ psycopg 3.1.12 နှင့်အထက်ကို support baseline အဖြစ် document လုပ်ထားပြီး lockfile တွင် exact version မှတ်တမ်းတင်ပါ။ UTC/timezone-aware datetime သုံးပါ။ Shell history ထဲ password မကျန်စေရန် command line တွင် မထည့်ပါနှင့်။ school_portal_dev နှင့် role သီးခြားဖန်တီးပါ။ Verification တွင် manage.py check၊ safe SELECT 1 နှင့် isolated project migration plan ပါစေ။ DROP DATABASE ကဲ့သို့ destructive command မသုံးပါနှင့်။ Pooling/persistent connection သည် deployment behavior ပြောင်းလဲနိုင်သောကြောင့် တိုင်းတာပြီးမှ ထည့်ပါ။",
        "concepts": "Cluster; database; schema; role; grants; psycopg driver; backend adapter; client/server protocol; UTF-8; timezone-aware datetimes; connection verification; pooling; least privilege; isolated test database.",
        "concepts_mm": "Cluster၊ database၊ schema၊ role၊ grant၊ psycopg driver၊ backend adapter၊ client/server protocol၊ UTF-8၊ timezone-aware datetime၊ connection verification၊ pooling၊ least privilege နှင့် isolated test database တို့ကို လေ့လာရမည်။",
        "syntax": "DATABASES = {\"default\": {\n    \"ENGINE\": \"django.db.backends.postgresql\",\n    \"NAME\": \"school_portal_dev\",\n    \"USER\": \"school_portal_app\",\n    \"HOST\": \"127.0.0.1\",\n    \"PORT\": \"5432\",\n}}",
        "examples": [
            _example("Create an isolated learning role", {"docs/database-setup.md": "# Run as an authorized local PostgreSQL administrator in a disposable learning environment.\nCREATE ROLE school_portal_app LOGIN PASSWORD '<set-locally>';\nCREATE DATABASE school_portal_dev OWNER school_portal_app;\n-- Never run these statements against Learn-Coding production."}, "An authorized local PostgreSQL shell", "The learning project has its own database and application role; the password remains local and is not committed.", "Use the local provider’s secure secret prompt, record the database name, and keep the platform database out of the command context.", "Local provider ၏ secure secret prompt သုံးပြီး database name ကိုမှတ်ပါ။ Platform database မရောပါနှင့်။"),
            _example("Install and pin psycopg", {"requirements.txt": "Django==6.0.*\npsycopg[binary]>=3.1.12,<4"}, "A new isolated virtual environment", "pip install -r requirements.txt installs a documented compatible driver range; the final lockfile records the resolved version.", "Install inside the educational project, run python -c to print package metadata, and record the actual version rather than claiming an unexecuted result.", "Educational project အတွင်း install လုပ်ပြီး actual version ကိုသာ မှတ်တမ်းတင်ပါ။ မလုပ်ရသေးသော result မရေးပါနှင့်။"),
            _example("Configure connection and timezone", {"school_site/settings.py": "import os\n\nDATABASES = {\n    \"default\": {\n        \"ENGINE\": \"django.db.backends.postgresql\",\n        \"NAME\": os.environ[\"POSTGRES_DB\"],\n        \"USER\": os.environ[\"POSTGRES_USER\"],\n        \"PASSWORD\": os.environ[\"POSTGRES_PASSWORD\"],\n        \"HOST\": os.environ.get(\"POSTGRES_HOST\", \"127.0.0.1\"),\n        \"PORT\": os.environ.get(\"POSTGRES_PORT\", \"5432\"),\n    }\n}\nUSE_TZ = True\nTIME_ZONE = \"UTC\""}, "POSTGRES_DB=school_portal_dev and local role variables", "Django sends timezone-aware application datetimes through the configured PostgreSQL backend.", "Set variables in the process environment, run check, and use a temporary local shell rather than embedding a credential in source.", "Variable များကို process environment တွင်ထားပြီး check run လုပ်ပါ။ Source ထဲ credential မရေးပါနှင့်။"),
            _example("Verify the connection", {"school_site/management/commands/check_school_db.py": "from django.core.management.base import BaseCommand\nfrom django.db import connection\n\nclass Command(BaseCommand):\n    def handle(self, *args, **options):\n        with connection.cursor() as cursor:\n            cursor.execute(\"SELECT current_database(), current_user\")\n            database, user = cursor.fetchone()\n        self.stdout.write(f\"database={database} user={user}\")"}, "python manage.py check_school_db in the isolated project", "The command reports the intended database and role so a learner can catch an accidental wrong target before migration.", "Only run this command against school_portal_dev, confirm the output, then continue to migration inspection.", "school_portal_dev သို့သာ run လုပ်ပြီး output အတည်ပြုပြီးမှ migration ဆက်လုပ်ပါ။"),
        ],
        "mistakes": ["Confusing a schema with a database or giving the application role superuser privileges.", "Installing a driver outside the project environment and assuming Django uses it.", "Using naive datetimes when USE_TZ=True.", "Running a destructive PostgreSQL command copied from a tutorial without checking the target."],
        "mistakes_mm": ["Schema နှင့် database ကို ရောထွေးခြင်း သို့မဟုတ် app role ကို superuser ပေးခြင်း။", "Project environment အပြင် driver install လုပ်ပြီး Django က သုံးမည်ဟု ယူဆခြင်း။", "USE_TZ=True ဖြစ်နေသော်လည်း naive datetime သုံးခြင်း။", "Target မစစ်ဘဲ tutorial ထဲက destructive command copy/run လုပ်ခြင်း။"],
        "best_practices": "Record Django, Python, PostgreSQL and psycopg versions; keep roles narrow; verify the database name before migrations; use TLS and a secret provider in deployments; make timezone behavior explicit; and never paste production DSNs into learning material.",
        "best_practices_mm": "Django၊ Python၊ PostgreSQL နှင့် psycopg version မှတ်တမ်းတင်ပါ။ Role permission ကို ကျဉ်းထားပါ။ Migration မလုပ်မီ database name စစ်ပါ။ Deployment တွင် TLS/secret provider သုံးပါ။ Timezone behavior ရှင်းလင်းထားပြီး production DSN ကို learning material ထဲ မထည့်ပါနှင့်။",
        "exercises": "Provision school_portal_dev in an isolated environment, configure a least-privilege app role, install the supported psycopg driver, run a safe connection check, and write down the actual error classification for an intentionally wrong port.",
        "exercises_mm": "Isolated environment တွင် school_portal_dev ဖန်တီးပါ။ Least-privilege role configure လုပ်၊ supported psycopg install လုပ်၊ safe connection check run လုပ်ပြီး wrong port အတွက် actual error classification ရေးပါ။",
        "homework": "Prepare a PostgreSQL setup checklist for the Student Portal that distinguishes local developer, CI test database and production settings. Do not include a real password.",
        "homework_mm": "Student Portal အတွက် local developer၊ CI test database နှင့် production setting ခွဲထားသော PostgreSQL setup checklist ပြုလုပ်ပါ။ Real password မပါစေပါနှင့်။",
        "summary": "The driver, backend, role and database are separate boundaries. Verify each one in an isolated project and record versions and actual outputs.",
        "summary_mm": "Driver၊ backend၊ role နှင့် database သည် boundary သီးခြားစီဖြစ်သည်။ Isolated project တွင် တစ်ခုချင်း verify လုပ်ပြီး version/actual output မှတ်တမ်းတင်ပါ။",
        "quiz": [
            _q("What is a PostgreSQL schema?", ["A namespace inside a database", "A Python virtual environment", "A Django view", "A password file only"], "A namespace inside a database", "A schema groups database objects within a database.", "intermediate", 3),
            _q("Which driver is recommended for the Django 6.0 PostgreSQL target?", ["psycopg 3", "A browser fetch API", "SQLite3 only", "A CSS parser"], "psycopg 3", "Django documents psycopg 3 as the preferred PostgreSQL driver family.", "beginner", 3),
            _q("Why should the app role not be a superuser?", ["To limit blast radius if the app is compromised", "Because Django cannot connect", "To disable migrations", "Because schemas cannot exist"], "To limit blast radius if the app is compromised", "Least privilege is a security control.", "intermediate", 3),
            _q("What does USE_TZ=True encourage?", ["Timezone-aware datetime handling", "Dropping all timestamps", "Using a browser timezone as truth", "Disabling PostgreSQL"], "Timezone-aware datetime handling", "It keeps datetime semantics explicit and safer across deployments.", "intermediate", 3),
            _q("Which verification catches an accidentally wrong database target?", ["Print the safe current database and role", "Delete all tables", "Publish the app", "Hide the error"], "Print the safe current database and role", "A safe identity check should happen before migrations.", "intermediate", 3),
            _q("True or false: a schema and a database are interchangeable terms.", ["True", "False"], "False", "A schema is a namespace inside a database.", "beginner", 3),
            _q("What should a lockfile record?", ["The resolved dependency versions", "Production passwords", "Student answers", "Only CSS colors"], "The resolved dependency versions", "Repeatable installs need actual resolved versions.", "intermediate", 3),
            _q("What should you do before running a destructive SQL command?", ["Verify the target and use an isolated environment", "Paste it blindly", "Run it in production first", "Remove the database name"], "Verify the target and use an isolated environment", "Target verification is a safety boundary.", "advanced", 3),
        ],
    },
    {
        "title": "Django Migrations and Database Schema Evolution",
        "slug": "05-secure-file-uploads",
        "description": "Use makemigrations, migrate and inspection tools to evolve the Student Portal schema with reviewable, reversible and backward-compatible changes.",
        "description_mm": "Student Portal schema ကို reviewable၊ reversible နှင့် backward-compatible ဖြစ်အောင် makemigrations၊ migrate နှင့် inspection tool များသုံးပြီး ပြောင်းလဲပါ။",
        "topic": "migration state, schema/data changes, dependencies, generated SQL, reversibility, conflicts, deployment sequencing and rollback planning",
        "theory": "A migration is a versioned description of a database schema change. Django compares model state to migration state when makemigrations creates operations; migrate applies unapplied operations to the configured database. showmigrations reports the graph and applied marks, while sqlmigrate shows backend-specific SQL for one migration without applying it. Schema migrations add or alter structure; data migrations use RunPython and must consider historical model state, idempotency and reverse behavior. Migration files form a dependency graph, so two branches can conflict when they both extend the same app leaf. Safe changes usually follow expand, migrate data, deploy code, then contract: add a nullable or defaulted field, backfill in batches, teach code to read/write both versions, and only later remove an old column. PostgreSQL DDL behavior and transaction boundaries vary by operation, so inspect and test in an isolated database. Never use a reset command as a substitute for understanding migration history, and never apply a tutorial migration to the platform database.",
        "theory_mm": "Migration သည် database schema ပြောင်းလဲမှုကို version အလိုက်ဖော်ပြထားသော record ဖြစ်သည်။ makemigrations သည် model state နှင့် migration state ကို နှိုင်းပြီး operation ဖန်တီးသည်။ migrate သည် configure လုပ်ထားသော database သို့ မလုပ်ရသေးသော operation ကို apply လုပ်သည်။ showmigrations သည် graph နှင့် applied mark ပြပြီး sqlmigrate သည် migration တစ်ခုအတွက် backend-specific SQL ကို apply မလုပ်ဘဲ ပြသည်။ Schema migration သည် structure ပြောင်းပြီး data migration သည် RunPython အသုံးပြုရသဖြင့် historical model state၊ idempotency နှင့် reverse behavior စဉ်းစားရသည်။ Migration file များသည် dependency graph ဖြစ်သောကြောင့် branch နှစ်ခုက leaf တစ်ခုတည်းကို ဆက်လျှင် conflict ဖြစ်နိုင်သည်။ Safe change တွင် expand၊ data migrate၊ code deploy၊ contract အဆင့်များသုံးပါ။ Nullable/default field ထည့်၊ batch ဖြင့် backfill၊ code ကို version နှစ်ခုဖတ်/ရေးနိုင်အောင်ထားပြီးမှ old column ဖယ်ပါ။ PostgreSQL DDL နှင့် transaction boundary သည် operation အလိုက် ကွာနိုင်သဖြင့် isolated database တွင် စစ်ပါ။ Migration history နားမလည်ဘဲ reset မလုပ်ပါနှင့်။ Platform database သို့ tutorial migration မapply ပါနှင့်။",
        "concepts": "Migration graph; model state; makemigrations; migrate; showmigrations; sqlmigrate; AddField; AlterField; RenameField; RunPython; dependencies; conflict; reversible operation; expand/contract; backward compatibility; rollback.",
        "concepts_mm": "Migration graph၊ model state၊ makemigrations၊ migrate၊ showmigrations၊ sqlmigrate၊ AddField၊ AlterField၊ RenameField၊ RunPython၊ dependency၊ conflict၊ reversible operation၊ expand/contract၊ backward compatibility နှင့် rollback တို့ကို လေ့လာရမည်။",
        "syntax": "python manage.py makemigrations students\npython manage.py showmigrations students\npython manage.py sqlmigrate students 0001\npython manage.py migrate --plan",
        "examples": [
            _example("Create an initial migration", {"students/models.py": "class Student(models.Model):\n    name = models.CharField(max_length=120)\n    email = models.EmailField(unique=True)"}, "A model change in the isolated project", "makemigrations students creates a numbered migration; it does not yet change the database.", "Review the file, check dependencies and operations, then use migrate --plan before applying.", "File ကို review လုပ်ပြီး dependency/operation စစ်ကာ migrate --plan အရင် run ပါ။"),
            _example("Inspect generated SQL", {"docs/commands.txt": "python manage.py showmigrations students\npython manage.py sqlmigrate students 0001\npython manage.py migrate --plan"}, "The migration name reported by showmigrations", "The learner sees applied marks, backend SQL, and the pending plan without guessing what will execute.", "Run each command against school_portal_dev and save the actual output in the project notes; outputs vary by version and backend.", "school_portal_dev တွင် command တစ်ခုချင်း run လုပ်ပြီး version/backend အလိုက်ကွာနိုင်သော actual output ကိုမှတ်ပါ။"),
            _example("Add a field safely", {"students/models.py": "class Student(models.Model):\n    name = models.CharField(max_length=120)\n    email = models.EmailField(unique=True)\n    preferred_language = models.CharField(max_length=10, blank=True, default=\"en\")"}, "An additive optional field", "Django can generate AddField without requiring a fake value for existing rows.", "Deploy the additive schema, backfill if needed, update reads/writes, and only later tighten nullability after observing real data.", "Additive schema အရင် deploy လုပ်ပြီး backfill၊ read/write update လုပ်ကာ data စစ်ပြီးမှ constraint တင်းပါ။"),
            _example("Write a reversible data migration", {"students/migrations/0002_backfill_language.py": "from django.db import migrations\n\ndef set_language(apps, schema_editor):\n    Student = apps.get_model(\"students\", \"Student\")\n    Student.objects.filter(preferred_language=\"\").update(preferred_language=\"en\")\n\ndef undo_language(apps, schema_editor):\n    Student = apps.get_model(\"students\", \"Student\")\n    Student.objects.filter(preferred_language=\"en\").update(preferred_language=\"\")\n\nclass Migration(migrations.Migration):\n    dependencies = [(\"students\", \"0001_initial\")]\n    operations = [migrations.RunPython(set_language, undo_language)]"}, "A controlled historical model state", "Forward and reverse functions can be tested in a disposable database; they do not silently delete unrelated values.", "Use apps.get_model, make the operation idempotent, test reverse behavior, and document whether a real-world rollback is lossless.", "apps.get_model သုံးပြီး operation ကို idempotent ထားပါ။ Reverse behavior test လုပ်ပြီး rollback lossless ဖြစ်/မဖြစ် မှတ်ပါ။"),
            _example("Resolve a migration conflict", {"docs/migration-review.md": "1. Inspect both branch migration files.\n2. Run python manage.py makemigrations --merge only after understanding operations.\n3. Review the generated dependency graph.\n4. Test forward and reverse paths in school_portal_dev."}, "Two branches both create the next leaf migration", "The review records the conflict and an intentional merge rather than deleting migration history.", "Compare operations, preserve both valid changes, create a merge only when appropriate, and let CI run migration checks.", "Operation နှစ်ခုကို နှိုင်းပြီး valid change နှစ်ခုလုံးထိန်းပါ။ သင့်လျော်မှ merge migration ပြုလုပ်ပါ။"),
        ],
        "mistakes": ["Editing an already-applied migration to make history look clean.", "Using fake migrations or reset commands without evidence.", "Writing a data migration that imports the current model instead of historical apps.get_model.", "Dropping a column before deployed code stops reading it."],
        "mistakes_mm": ["Applied migration ကို history လှစေရန် ပြန်ပြင်ခြင်း။", "အထောက်အထားမရှိဘဲ fake migration/reset command သုံးခြင်း။", "Historical apps.get_model အစား current model import လုပ်ခြင်း။", "Deployed code က column ဖတ်နေသေးချိန်တွင် column drop လုပ်ခြင်း။"],
        "best_practices": "Review every generated migration, make data operations idempotent, use historical models, test both directions in a disposable database, deploy additive changes first, and keep rollback plans explicit instead of promising that every data rollback is lossless.",
        "best_practices_mm": "Generated migration တစ်ခုချင်း review လုပ်ပါ။ Data operation ကို idempotent ထားပြီး historical model သုံးပါ။ Disposable database တွင် forward/reverse test လုပ်ပါ။ Additive change အရင် deploy ပြီး rollback plan ကို တိတိကျကျရေးပါ။ Data rollback အားလုံး lossless ဖြစ်မည်ဟု မကတိပေးပါနှင့်။",
        "exercises": "Create an initial Student migration, add a field, inspect its SQL and plan, write a reversible backfill, and document the expand/contract deployment sequence. Run only in the isolated learning database.",
        "exercises_mm": "Student initial migration ပြုလုပ်ပါ။ Field ထပ်ထည့်၊ SQL/plan စစ်၊ reversible backfill ရေးပြီး expand/contract deployment sequence မှတ်တမ်းတင်ပါ။ Isolated learning database တွင်သာ run ပါ။",
        "homework": "Extend the education schema with Course and Enrollment using two additive migrations. Include a review note explaining dependencies, generated SQL, data safety and rollback limits.",
        "homework_mm": "Course နှင့် Enrollment ပါအောင် education schema ကို additive migration နှစ်ခုဖြင့် တိုးပါ။ Dependency၊ generated SQL၊ data safety နှင့် rollback limit ရှင်းပြသော review note ပါစေ။",
        "summary": "Migration files are durable history, not disposable setup scripts. Inspect operations, preserve compatibility, and test plans in an isolated database.",
        "summary_mm": "Migration file သည် ဖျက်ပစ်နိုင်သော setup script မဟုတ်ဘဲ တည်မြဲသော history ဖြစ်သည်။ Operation စစ်၊ compatibility ထိန်းပြီး isolated database တွင် test လုပ်ပါ။",
        "quiz": [
            _q("What does makemigrations create?", ["Migration files from model changes", "A production backup", "A browser response", "A student account"], "Migration files from model changes", "makemigrations records model changes as operations.", "beginner", 4),
            _q("What does sqlmigrate do?", ["Shows SQL for a migration without applying it", "Deletes a database", "Runs a view", "Publishes a lesson"], "Shows SQL for a migration without applying it", "It is an inspection command.", "intermediate", 4),
            _q("Why use apps.get_model in RunPython?", ["It uses the historical model state", "It disables transactions", "It loads CSS", "It exposes passwords"], "It uses the historical model state", "Migrations must not depend on future model code.", "advanced", 4),
            _q("Which sequence is safer for removing a field?", ["Stop reads, deploy compatible code, then remove later", "Drop first and fix errors later", "Reset the database", "Delete migration history"], "Stop reads, deploy compatible code, then remove later", "Expand/contract preserves compatibility during rollout.", "advanced", 4),
            _q("What does showmigrations reveal?", ["Migration graph and applied status", "Student passwords", "Only CSS", "The current browser URL"], "Migration graph and applied status", "It helps review history and pending work.", "beginner", 4),
            _q("True or false: editing an applied migration is a normal cleanup step.", ["True", "False"], "False", "Applied migration history should be preserved; add a new migration.", "intermediate", 4),
            _q("What makes a data migration safer to re-run?", ["An idempotent condition and explicit scope", "A DROP TABLE", "A hidden password", "No reverse plan"], "An idempotent condition and explicit scope", "Repeatable scoped operations reduce damage.", "advanced", 4),
            _q("Where should migration exercises run?", ["An isolated educational database", "The platform production database", "A student's browser", "A random shared database"], "An isolated educational database", "Tutorial schema changes must be isolated.", "beginner", 4),
        ],
    },
    {
        "title": "Django ORM CRUD Operations and QuerySet Fundamentals",
        "slug": "05-orm-crud-and-querysets",
        "description": "Create, read, update and delete synthetic Student records while understanding managers, lazy QuerySets, exceptions, pagination and safe query boundaries.",
        "description_mm": "Synthetic Student record များကို create/read/update/delete လုပ်ပြီး manager၊ lazy QuerySet၊ exception၊ pagination နှင့် safe query boundary ကို နားလည်ပါ။",
        "topic": "objects manager, CRUD methods, QuerySet laziness, evaluation, lookups, pagination, validation and error handling",
        "theory": "Django exposes a model manager, commonly objects, as the entry point to the ORM. create() constructs and saves one row; save() persists an instance and can run custom save behavior; get() expects exactly one result and may raise DoesNotExist or MultipleObjectsReturned; all(), filter(), exclude(), first(), last(), order_by(), exists() and count() compose QuerySets. A QuerySet is lazy until iteration, slicing that requires evaluation, bool(), len(), list(), count() or another operation consumes it, so building a QuerySet is not the same as running SQL. update() performs a direct bulk SQL update and does not call each instance’s save hooks; delete() can cascade according to relationships. get_or_create() and update_or_create() are useful but depend on database uniqueness for concurrent safety. Use parameterized ORM lookups instead of concatenating SQL, validate user input before filtering, paginate with a stable ordering, and handle database errors at a service boundary. Never use real personal data in a learning example.",
        "theory_mm": "Django ORM entry point သည် model manager ဖြစ်ပြီး အများအားဖြင့် objects ဟု ခေါ်သည်။ create() သည် row တစ်ခုဖန်တီးပြီး save လုပ်သည်။ save() သည် instance ကို persist လုပ်ပြီး custom save behavior ရှိလျှင် run နိုင်သည်။ get() သည် result တစ်ခုတည်းကို မျှော်လင့်ပြီး DoesNotExist/MultipleObjectsReturned ဖြစ်နိုင်သည်။ all၊ filter၊ exclude၊ first၊ last၊ order_by၊ exists နှင့် count သည် QuerySet တည်ဆောက်နိုင်သည်။ QuerySet သည် lazy ဖြစ်သောကြောင့် iteration၊ slicing evaluation၊ bool၊ len၊ list၊ count စသည်ဖြင့် consume လုပ်မှ SQL run လေ့ရှိသည်။ QuerySet တည်ဆောက်ခြင်းနှင့် SQL run ခြင်း မတူပါ။ update() သည် bulk SQL update ဖြစ်ပြီး instance save hook တစ်ခုချင်းမခေါ်ပါ။ delete() သည် relationship အလိုက် cascade ဖြစ်နိုင်သည်။ get_or_create/update_or_create သည် အသုံးဝင်သော်လည်း concurrent safety အတွက် database uniqueness လိုသည်။ ORM lookup ကို parameterized အဖြစ်သုံးပြီး raw SQL concatenate မလုပ်ပါနှင့်။ User input ကို validate လုပ်၊ stable order ဖြင့် paginate လုပ်ပြီး database error ကို service boundary တွင် ကိုင်တွယ်ပါ။ Learning example တွင် အမှန်တကယ် personal data မသုံးပါနှင့်။",
        "concepts": "Manager; QuerySet; lazy evaluation; get exceptions; filter lookups; update versus save; bulk delete; get_or_create; update_or_create; stable ordering; pagination; validation; IntegrityError; parameterized queries.",
        "concepts_mm": "Manager၊ QuerySet၊ lazy evaluation၊ get exception၊ filter lookup၊ update/save ကွာခြားချက်၊ bulk delete၊ get_or_create၊ update_or_create၊ stable ordering၊ pagination၊ validation၊ IntegrityError နှင့် parameterized query တို့ကို လေ့လာရမည်။",
        "syntax": "students = Student.objects.filter(last_name__istartswith=query).order_by(\"last_name\", \"id\")\nstudent = Student.objects.get(pk=student_id)\nStudent.objects.filter(pk=student_id).update(age=18)",
        "examples": [
            _example("Create synthetic records", {"school_site/seed_demo.py": "from students.models import Student\n\nStudent.objects.create(first_name=\"Aye\", last_name=\"Min\", email=\"aye@example.test\")\nStudent.objects.create(first_name=\"Ko\", last_name=\"Zaw\", email=\"ko@example.test\")"}, "Two synthetic records", "The database contains two test students with non-real example addresses.", "Run this only after migrations in school_portal_dev; repeatable seed scripts should use stable identifiers or get_or_create.", "Migration ပြီးမှ school_portal_dev တွင်သာ run ပါ။ Repeatable seed တွင် stable identifier/get_or_create သုံးပါ။"),
            _example("Read and search with a stable order", {"students/services.py": "from students.models import Student\n\ndef search_students(term):\n    return Student.objects.filter(\n        last_name__icontains=term\n    ).order_by(\"last_name\", \"first_name\", \"id\")"}, "term='a'", "The returned QuerySet is ordered consistently and is evaluated only when the caller iterates it.", "Keep the QuerySet composable, add a unique tie-breaker to ordering, and evaluate once at the response boundary.", "QuerySet ကို composable ထားပြီး ordering တွင် unique tie-breaker ထည့်ကာ response boundary တွင် တစ်ကြိမ်သာ evaluate လုပ်ပါ။"),
            _example("Handle get and update", {"students/services.py": "from django.core.exceptions import ValidationError\nfrom students.models import Student\n\ndef rename_student(student_id, first_name):\n    student = Student.objects.get(pk=student_id)\n    student.first_name = first_name.strip()\n    student.full_clean()\n    student.save(update_fields=[\"first_name\", \"updated_at\"] if hasattr(student, \"updated_at\") else [\"first_name\"])\n    return student"}, "An existing id and a non-empty name", "A missing id raises DoesNotExist; a valid change saves one instance after validation.", "Catch DoesNotExist at the service/API boundary, validate the normalized value, then save only intended fields.", "မတွေ့သော id ကို boundary တွင် DoesNotExist ကိုင်တွယ်ပါ။ Value normalize/validate ပြီး လိုသော field ပဲ save ပါ။"),
            _example("Paginate a safe QuerySet", {"students/views.py": "from django.core.paginator import Paginator\nfrom django.shortcuts import render\nfrom .models import Student\n\ndef list_students(request):\n    query = request.GET.get(\"q\", \"\").strip()\n    rows = Student.objects.filter(last_name__icontains=query).order_by(\"last_name\", \"id\")\n    page = Paginator(rows, 20).get_page(request.GET.get(\"page\"))\n    return render(request, \"students/list.html\", {\"page\": page, \"query\": query})"}, "GET /students/?q=an&page=2", "The second page contains at most 20 matching synthetic records and retains a stable order.", "Whitelist the lookup, use Paginator, pass a page object to the template, and render an empty state when there are no matches.", "Lookup ကို whitelist လုပ်၊ Paginator သုံးပြီး page object ပေးပါ။ Match မရှိလျှင် empty state ပြပါ။"),
            _example("Delete only a disposable record", {"students/services.py": "from students.models import Student\n\ndef delete_demo_student(student_id):\n    student = Student.objects.get(pk=student_id)\n    if not student.email.endswith(\"@example.test\"):\n        raise ValueError(\"Only synthetic demo rows may be deleted\")\n    student.delete()"}, "A synthetic demo id", "Only an explicitly synthetic row can be deleted; real-looking records are rejected by the exercise boundary.", "Make deletion policy explicit, confirm the target, and prefer archive flags when history must be preserved.", "ဖျက်မည့် target ကို အတည်ပြုပြီး synthetic row သာ ခွင့်ပြုပါ။ History လိုလျှင် archive flag သုံးပါ။"),
        ],
        "mistakes": ["Calling get() when zero or many rows are valid outcomes.", "Assuming a QuerySet has run SQL merely because it was constructed.", "Using update() while expecting per-instance save hooks or validation.", "Paginating without deterministic ordering or accepting unbounded page sizes."],
        "mistakes_mm": ["Zero/many result ဖြစ်နိုင်သော်လည်း get() သုံးခြင်း။", "QuerySet တည်ဆောက်ရုံနှင့် SQL run ပြီးပြီဟု ထင်ခြင်း။", "Per-instance save hook/validation မျှော်လင့်ပြီး update() သုံးခြင်း။", "Deterministic ordering မရှိဘဲ page size ကို ကန့်သတ်မထားခြင်း။"],
        "best_practices": "Keep user input normalized and bounded, compose QuerySets in services, order by a stable key before pagination, use select_for_update only inside a transaction when needed, add database uniqueness, and test both empty and exception paths.",
        "best_practices_mm": "User input ကို normalize/bound လုပ်ပါ။ Service တွင် QuerySet compose လုပ်ပြီး pagination မတိုင်မီ stable key ဖြင့် order လုပ်ပါ။ လိုအပ်မှ transaction အတွင်း select_for_update သုံးပါ။ Database uniqueness ထည့်ပြီး empty/exception path နှစ်ခုလုံး test လုပ်ပါ။",
        "exercises": "Insert synthetic students, search by name, filter by age, update one record with full_clean and update_fields, paginate results, and write tests for DoesNotExist, empty search and bounded page size.",
        "exercises_mm": "Synthetic student ထည့်ပါ။ Name search၊ age filter၊ full_clean/update_fields ဖြင့် update၊ pagination ပြုလုပ်ပြီး DoesNotExist၊ empty search နှင့် bounded page size test ရေးပါ။",
        "homework": "Build a Student CRUD service and view boundary with safe input normalization, pagination, empty states, error handling and an explicit archive policy for non-demo data.",
        "homework_mm": "Safe input normalization၊ pagination၊ empty state၊ error handling နှင့် non-demo data အတွက် archive policy ပါသော Student CRUD service/view boundary တည်ဆောက်ပါ။",
        "summary": "The ORM is composable and lazy, but each method has precise evaluation, validation and signal behavior. Make those boundaries explicit in services and tests.",
        "summary_mm": "ORM သည် composable/lazy ဖြစ်သော်လည်း method တစ်ခုချင်းစီတွင် evaluation၊ validation နှင့် signal behavior ကွာသည်။ Service/test တွင် boundary ကို ရှင်းလင်းထားပါ။",
        "quiz": [
            _q("Which method expects exactly one object?", ["get()", "all()", "filter()", "values()"], "get()", "get raises when zero or multiple rows match.", "beginner", 5),
            _q("When is a QuerySet commonly evaluated?", ["When iterated or otherwise consumed", "When a variable is named", "When a URL is reversed", "When a model is imported"], "When iterated or otherwise consumed", "QuerySets are lazy until evaluation is required.", "intermediate", 5),
            _q("What is a key difference between update() and save()?", ["update() is a bulk SQL operation and skips per-instance save hooks", "update() creates a project", "save() cannot write rows", "They always have identical behavior"], "update() is a bulk SQL operation and skips per-instance save hooks", "Use the method matching validation and hook requirements.", "advanced", 5),
            _q("Why add id as a pagination tie-breaker?", ["To make ordering deterministic when names repeat", "To expose passwords", "To disable filters", "To avoid migrations"], "To make ordering deterministic when names repeat", "Stable ordering avoids rows moving between pages unexpectedly.", "intermediate", 5),
            _q("Which exception can get() raise for zero matches?", ["DoesNotExist", "TemplateDoesNotExist", "IndexError always", "PermissionDenied always"], "DoesNotExist", "The model-specific DoesNotExist exception is raised.", "beginner", 5),
            _q("True or false: unbounded user page sizes are safe by default.", ["True", "False"], "False", "Limit and validate page sizes to protect database and response work.", "intermediate", 5),
            _q("What should a CRUD learning dataset contain?", ["Synthetic non-personal records", "Real private student records", "Passwords", "Production exports"], "Synthetic non-personal records", "Learning examples must protect privacy.", "beginner", 5),
            _q("Which method checks existence without loading every object?", ["exists()", "all() then print everything", "delete()", "migrate()"], "exists()", "exists is intended for an existence check.", "intermediate", 5),
        ],
    },
    {
        "title": "Foreign Keys, One-to-One and Many-to-Many Relationships",
        "slug": "05-model-relationships",
        "description": "Model Student, StudentProfile, Course and Enrollment relationships with deletion policies, reverse access, uniqueness and referential integrity.",
        "description_mm": "Student၊ StudentProfile၊ Course နှင့် Enrollment relationship များကို deletion policy၊ reverse access၊ uniqueness နှင့် referential integrity ဖြင့် model လုပ်ပါ။",
        "topic": "ForeignKey, OneToOneField, ManyToManyField, on_delete, related_name, through models and enrollment integrity",
        "theory": "Relationships encode ownership and navigation between rows. A ForeignKey models many child rows pointing to one parent and usually represents one-to-many; OneToOneField adds uniqueness to the foreign key; ManyToManyField creates a join table automatically, but an explicit through model is better when the relationship has data such as enrollment date, status or completion percentage. on_delete is a database and application policy: CASCADE removes dependent rows, PROTECT blocks deletion when history matters, SET_NULL preserves a child with a nullable reference, and RESTRICT provides a more explicit restriction in supported versions. related_name makes reverse queries readable. A Student-Course Enrollment model should use a database-level UniqueConstraint on student and course to prevent duplicates, plus a status field and timestamps. Normalize repeated facts, use select_related for a single-valued foreign key and prefetch_related for many-valued collections, and test deletion behavior rather than inferring it from a diagram. A relationship is not complete until its constraints, indexes, reverse queries and lifecycle policy are documented.",
        "theory_mm": "Relationship သည် row များကြား ownership နှင့် navigation ကို ဖော်ပြသည်။ ForeignKey သည် child row များစွာက parent တစ်ခုကိုညွှန်သော one-to-many model ဖြစ်သည်။ OneToOneField သည် foreign key ကို unique ဖြစ်စေသည်။ ManyToManyField သည် join table အလိုအလျောက်ဖန်တီးသော်လည်း enrollment date/status/completion ကဲ့သို့ metadata ရှိလျှင် explicit through model သုံးသင့်သည်။ on_delete သည် database/application policy ဖြစ်သည်။ CASCADE သည် dependent row ဖျက်၊ PROTECT သည် history ရှိလျှင် parent delete ပိတ်၊ SET_NULL သည် nullable reference ဖြင့် child ထိန်း၊ RESTRICT သည် explicit restriction ပေးသည်။ related_name သည် reverse query ကို ဖတ်လွယ်စေသည်။ Student-Course Enrollment တွင် student/course အတွဲကို UniqueConstraint ထားပြီး duplicate မဖြစ်အောင် database ကာကွယ်ရမည်။ Repeated fact ကို normalize လုပ်ပြီး single-valued relation အတွက် select_related၊ many-valued collection အတွက် prefetch_related သုံးပါ။ Diagram ကြည့်ရုံနှင့် deletion behavior မသတ်မှတ်ဘဲ test လုပ်ပါ။ Relationship တစ်ခုတွင် constraint၊ index၊ reverse query နှင့် lifecycle policy ပါမှ ပြည့်စုံသည်။",
        "concepts": "ForeignKey; OneToOneField; ManyToManyField; through model; on_delete; CASCADE; PROTECT; SET_NULL; RESTRICT; related_name; reverse manager; UniqueConstraint; referential integrity; enrollment metadata; normalization.",
        "concepts_mm": "ForeignKey၊ OneToOneField၊ ManyToManyField၊ through model၊ on_delete၊ CASCADE၊ PROTECT၊ SET_NULL၊ RESTRICT၊ related_name၊ reverse manager၊ UniqueConstraint၊ referential integrity၊ enrollment metadata နှင့် normalization တို့ကို လေ့လာရမည်။",
        "syntax": "class Enrollment(models.Model):\n    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name=\"enrollments\")\n    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name=\"enrollments\")\n\n    class Meta:\n        constraints = [models.UniqueConstraint(fields=[\"student\", \"course\"], name=\"unique_student_course\")]",
        "examples": [
            _example("Model profile and course", {"students/models.py": "class StudentProfile(models.Model):\n    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name=\"profile\")\n    biography = models.TextField(blank=True)\n\nclass Course(models.Model):\n    code = models.CharField(max_length=20, unique=True)\n    title = models.CharField(max_length=160)"}, "One profile per student and unique course code", "student.profile returns one profile; duplicate course codes fail validation/database uniqueness.", "Use OneToOneField when the child truly cannot have a second owner and use a unique course code as a stable domain identifier.", "Child တစ်ခုမှာ owner တစ်ခုသာရှိလျှင် OneToOneField သုံးပြီး course code ကို unique ထားပါ။"),
            _example("Add an Enrollment through model", {"students/models.py": "class Enrollment(models.Model):\n    class Status(models.TextChoices):\n        ACTIVE = \"active\", \"Active\"\n        COMPLETED = \"completed\", \"Completed\"\n\n    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name=\"enrollments\")\n    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name=\"enrollments\")\n    status = models.CharField(max_length=20, choices=Status, default=Status.ACTIVE)\n    enrolled_at = models.DateTimeField(auto_now_add=True)\n\n    class Meta:\n        constraints = [models.UniqueConstraint(fields=[\"student\", \"course\"], name=\"unique_enrollment\")]"}, "A student/course pair", "The second enrollment for the same pair is rejected by the uniqueness constraint.", "Add metadata to the through model and enforce duplicate prevention at the database boundary, not only in a view.", "Metadata ကို through model တွင်ထည့်ပြီး duplicate prevention ကို view တစ်ခုတည်းမဟုတ် database တွင်ပါ enforce လုပ်ပါ။"),
            _example("Query both directions", {"students/services.py": "student = Student.objects.prefetch_related(\"enrollments__course\").get(pk=student_id)\ncourse = Course.objects.get(code=\"DJ-ORM\")\nactive = course.enrollments.filter(status=Enrollment.Status.ACTIVE).select_related(\"student\")"}, "One student id and a course code", "The student page can list courses and the course page can list active students using readable reverse names.", "Choose prefetch for the collection, select_related for each enrollment's student, and keep status filtering in the QuerySet.", "Collection အတွက် prefetch၊ enrollment တစ်ခုချင်း student အတွက် select_related သုံးပြီး status filter ကို QuerySet တွင်ထားပါ။"),
            _example("Protect meaningful history", {"students/services.py": "from django.db.models import ProtectedError\n\ndef archive_course(course):\n    course.is_archived = True\n    course.save(update_fields=[\"is_archived\"])\n\ndef remove_course(course):\n    try:\n        course.delete()\n    except ProtectedError:\n        raise ValueError(\"Enrollment history must be archived, not deleted\")"}, "A course with enrollment history", "The service archives the course or reports that PROTECT prevents destructive deletion.", "Use lifecycle states for business history and let the database policy stop accidental removal.", "Business history အတွက် lifecycle state သုံးပြီး database policy က မတော်တဆ delete ကို တားစေပါ။"),
        ],
        "mistakes": ["Using ManyToManyField when enrollment metadata needs a through model.", "Relying only on a Python if-not-exists check for duplicate enrollment.", "Choosing CASCADE for historical records without documenting the loss.", "Querying reverse relationships in a loop without related loading."],
        "mistakes_mm": ["Enrollment metadata လိုသော်လည်း ManyToManyField တစ်ခုတည်းသုံးခြင်း။", "Duplicate enrollment အတွက် Python check တစ်ခုတည်းကို ယုံခြင်း။", "History ပျောက်နိုင်သော်လည်း CASCADE သုံးပြီး policy မရေးခြင်း။", "Related loading မလုပ်ဘဲ reverse relationship ကို loop ထဲ query လုပ်ခြင်း။"],
        "best_practices": "Name reverse relations intentionally, enforce invariants with database constraints, choose on_delete from business history, index foreign keys and common status filters, and use an explicit through model when the relationship is a first-class record.",
        "best_practices_mm": "Reverse relation အမည်ကို ရည်ရွယ်ချက်ရှိစွာပေးပါ။ Invariant ကို database constraint ဖြင့် enforce လုပ်ပါ။ on_delete ကို business history အပေါ်မူတည်ရွေးပါ။ Foreign key/status filter အတွက် index စဉ်းစားပြီး relationship က first-class record ဖြစ်လျှင် through model သုံးပါ။",
        "exercises": "Implement Student, StudentProfile, Course and Enrollment. Add duplicate prevention, choose PROTECT or archive behavior, query enrolled students and courses in both directions, and test each deletion policy.",
        "exercises_mm": "Student၊ StudentProfile၊ Course၊ Enrollment တည်ဆောက်ပါ။ Duplicate prevention၊ PROTECT/archive behavior ထည့်ပြီး direction နှစ်ခုလုံး query လုပ်ကာ deletion policy တစ်ခုချင်း test လုပ်ပါ။",
        "homework": "Submit a Student Course Enrollment data model with an ER-style explanation, field list, indexes, constraints, reverse queries and a written deletion/lifecycle policy.",
        "homework_mm": "ER-style explanation၊ field list၊ index၊ constraint၊ reverse query နှင့် deletion/lifecycle policy ပါသော Student Course Enrollment data model တင်ပါ။",
        "summary": "Relationships carry lifecycle meaning. The field type, reverse name, deletion policy and database constraint together define safe navigation and history.",
        "summary_mm": "Relationship တွင် lifecycle အဓိပ္ပာယ်ပါသည်။ Field type၊ reverse name၊ deletion policy နှင့် database constraint တို့ပေါင်းမှ safe navigation/history ကို သတ်မှတ်သည်။",
        "quiz": [
            _q("Which field models one child record per parent?", ["OneToOneField", "TextField", "DecimalField", "DateField"], "OneToOneField", "OneToOneField adds uniqueness to the relationship.", "beginner", 6),
            _q("When is an explicit through model useful?", ["When the relationship has metadata", "When no tables are needed", "Only for CSS", "Only for passwords"], "When the relationship has metadata", "Enrollment date and status belong on the relationship record.", "intermediate", 6),
            _q("What does PROTECT generally do?", ["Blocks deletion when dependent history exists", "Deletes all children", "Sets every field null", "Disables queries"], "Blocks deletion when dependent history exists", "It preserves meaningful references by refusing the delete.", "intermediate", 6),
            _q("Why add a UniqueConstraint to Enrollment?", ["To prevent duplicate student/course pairs", "To order templates", "To set a password", "To create a view"], "To prevent duplicate student/course pairs", "Database enforcement handles concurrent duplicate attempts.", "advanced", 6),
            _q("Which related loader fits many-valued enrollments?", ["prefetch_related()", "select_related() only", "migrate()", "reverse()"], "prefetch_related()", "Prefetch is designed for many-valued related collections.", "intermediate", 6),
            _q("True or false: CASCADE is always the safest deletion policy.", ["True", "False"], "False", "The correct policy depends on whether history may be removed.", "intermediate", 6),
            _q("What does related_name provide?", ["A readable reverse relation accessor", "A database password", "A migration file", "A form widget only"], "A readable reverse relation accessor", "It names reverse traversal such as student.enrollments.", "beginner", 6),
            _q("What should duplicate prevention rely on under concurrency?", ["A database uniqueness constraint", "A browser button state only", "A comment", "A template loop"], "A database uniqueness constraint", "Application checks alone can race.", "advanced", 6),
        ],
    },
    {
        "title": "Advanced Django ORM Queries and Database Optimization",
        "slug": "05-advanced-querysets",
        "description": "Use Q, F, annotations, aggregates, related loading, indexes and EXPLAIN to improve measured Student Portal queries without inventing benchmarks.",
        "description_mm": "Measured Student Portal query များကို Q၊ F၊ annotation၊ aggregate၊ related loading၊ index နှင့် EXPLAIN ဖြင့် optimize လုပ်ပါ။ မစမ်းဘဲ benchmark မဖန်တီးပါနှင့်။",
        "topic": "Q objects, F expressions, annotations, aggregation, subqueries, N+1 detection, related loading and PostgreSQL query plans",
        "theory": "Advanced ORM work starts with a question and a measurement, not a magic method. Q objects compose OR, AND and NOT conditions; F expressions let the database compare or update columns without copying stale values into Python. annotate adds per-row values, aggregate returns a summary, values and values_list project only the shape needed by a report, and Exists/Subquery can express correlated conditions. select_related follows single-valued joins in one query, while prefetch_related executes additional queries and joins objects in Python for many-valued relations. An N+1 problem appears when a list query is followed by one related query per row. Use assertNumQueries or connection.queries in a controlled test to compare actual query counts. Indexes speed some filters and ordering but add write/storage cost; a composite index must match real query prefixes. QuerySet.explain() asks the backend for a plan, and PostgreSQL EXPLAIN ANALYZE executes work, so use it carefully on non-destructive reads in a safe dataset. only() and defer() can reduce selected columns but may cause deferred follow-up queries. Optimize after correctness and measure before claiming a gain.",
        "theory_mm": "Advanced ORM ကို magic method ဖြင့်မစဘဲ မည်သည့် query question ကို ဖြေမည်နှင့် measurement မှ စတင်ပါ။ Q object သည် OR/AND/NOT condition ပေါင်းစပ်နိုင်သည်။ F expression သည် stale Python value မကူးဘဲ database column တစ်ခုနှင့်တစ်ခု compare/update လုပ်စေသည်။ annotate သည် row တစ်ခုချင်း computed value ထည့်၊ aggregate သည် summary ပြန်၊ values/values_list သည် report လိုသည့် shape ပဲ ယူစေသည်။ Exists/Subquery သည် correlated condition ဖော်ပြနိုင်သည်။ select_related သည် single-valued join ကို query တစ်ခုတည်းတွင်လိုက်ပြီး prefetch_related သည် query ထပ်လုပ်ကာ Python တွင် many-valued relation ချိတ်သည်။ N+1 သည် list query တစ်ခုပြီးတိုင်း row တစ်ခုစီအတွက် related query ထပ်ဖြစ်သောအခြေအနေဖြစ်သည်။ Controlled test တွင် assertNumQueries/connection.queries ဖြင့် actual query count နှိုင်းပါ။ Index သည် filter/order အချို့ကို မြန်စေသော်လည်း write/storage cost ရှိသည်။ Composite index သည် real query prefix နှင့် ကိုက်ညီရမည်။ QuerySet.explain() သည် backend plan ကို ပြပြီး EXPLAIN ANALYZE သည် query ကို execute နိုင်သောကြောင့် safe dataset တွင်သာသုံးပါ။ only/defer သည် column လျှော့သော်လည်း deferred query ထပ်ဖြစ်နိုင်သည်။ Correctness ပြီးမှ optimize လုပ်ပြီး measurement မရှိဘဲ gain မကတိပေးပါနှင့်။",
        "concepts": "Q; F; annotate; aggregate; Count; Sum; Avg; Min; Max; values; values_list; Exists; Subquery; select_related; prefetch_related; N+1; indexes; explain; query count; deferred fields.",
        "concepts_mm": "Q၊ F၊ annotate၊ aggregate၊ Count၊ Sum၊ Avg၊ Min၊ Max၊ values၊ values_list၊ Exists၊ Subquery၊ select_related၊ prefetch_related၊ N+1၊ index၊ explain၊ query count နှင့် deferred field တို့ကို လေ့လာရမည်။",
        "syntax": "from django.db.models import Count, F, Q\n\nCourse.objects.filter(Q(title__icontains=term) | Q(code__iexact=term)).annotate(\n    enrollment_count=Count(\"enrollments\")\n).order_by(\"-enrollment_count\")",
        "examples": [
            _example("Compose a complex filter", {"students/services.py": "from django.db.models import Q\n\ndef matching_students(term):\n    return Student.objects.filter(\n        Q(first_name__icontains=term) | Q(last_name__icontains=term),\n        is_archived=False,\n    ).order_by(\"last_name\", \"id\")"}, "term='a'", "Active students whose first or last name matches are returned in stable order.", "Group Q expressions deliberately, add ordinary keyword filters as AND conditions, and inspect the generated query in a controlled test.", "Q expression ကို group လုပ်ပြီး keyword filter ကို AND အဖြစ်ထည့်ပါ။ Controlled test တွင် query စစ်ပါ။"),
            _example("Update with an F expression", {"courses/services.py": "from django.db.models import F\n\ndef add_credit(course_id):\n    return Course.objects.filter(pk=course_id).update(credits=F(\"credits\") + 1)"}, "A course id", "The database increments credits without reading a possibly stale value into Python.", "Use F for relative updates, check the affected-row count, and refresh an instance if the caller needs its new value.", "Relative update အတွက် F သုံးပြီး affected-row count စစ်ပါ။ Instance value လိုလျှင် refresh_from_db လုပ်ပါ။"),
            _example("Annotate enrollment counts", {"courses/services.py": "from django.db.models import Count\n\ndef course_summary():\n    return Course.objects.annotate(\n        enrollment_count=Count(\"enrollments\", distinct=True)\n    ).values(\"code\", \"title\", \"enrollment_count\")"}, "Courses and enrollments", "Each returned dictionary includes the database-calculated enrollment_count.", "Aggregate at the database boundary, use distinct when joins could multiply rows, and inspect the SQL for the intended grouping.", "Database boundary တွင် aggregate လုပ်ပြီး join ကြောင့် duplicate ဖြစ်နိုင်လျှင် distinct သုံးပါ။"),
            _example("Remove an N+1 query", {"students/views.py": "students = Student.objects.select_related(\"profile\").prefetch_related(\"enrollments__course\")\nfor student in students:\n    display = [enrollment.course.title for enrollment in student.enrollments.all()]"}, "A list page that displays profiles and courses", "The page uses bounded related queries rather than one query per student relationship.", "Measure the baseline with assertNumQueries, add only the loaders needed by the template, and re-run the same test.", "Baseline ကို assertNumQueries ဖြင့်တိုင်းပြီး template လိုသည့် loader ပဲထည့်ကာ တူညီသော test ပြန် run ပါ။"),
            _example("Inspect a PostgreSQL query plan", {"students/tests/test_queries.py": "from django.test import TestCase\n\nclass QueryPlanTests(TestCase):\n    def test_student_search_plan_is_inspectable(self):\n        plan = Student.objects.filter(last_name__istartswith=\"A\").order_by(\"last_name\").explain()\n        self.assertTrue(plan)"}, "A test database with synthetic students", "The test records that the backend returns a plan; plan text and costs are environment-specific and must not be invented.", "Run explain on a representative dataset, decide whether an index matches the real predicate, and compare measured behavior before/after.", "Representative dataset တွင် explain run လုပ်ပြီး real predicate နှင့် index ကိုက်/မကိုက် စစ်ပါ။"),
        ],
        "mistakes": ["Adding indexes without a query pattern or measurement.", "Using select_related for a many-valued collection or prefetching every relation by default.", "Claiming a speedup from an unexecuted benchmark.", "Using F and then reading a stale in-memory instance without refreshing it."],
        "mistakes_mm": ["Query pattern/measurement မရှိဘဲ index ထည့်ခြင်း။", "Many-valued collection အတွက် select_related သုံးခြင်း သို့မဟုတ် relation အားလုံးကို default prefetch လုပ်ခြင်း။", "မစမ်းဘဲ performance gain ကတိပေးခြင်း။", "F update ပြီး stale in-memory instance ကို refresh မလုပ်ဘဲ ဖတ်ခြင်း။"],
        "best_practices": "Measure with representative synthetic data, keep correctness tests beside performance tests, use the narrowest related loading plan, document index rationale, inspect explain output on the target backend, and treat query-count results as environment-specific evidence.",
        "best_practices_mm": "Representative synthetic data ဖြင့် တိုင်းပါ။ Correctness test နှင့် performance test တွဲထားပါ။ လိုအပ်သည့် related loading ပဲသုံးပါ။ Index အကြောင်းရင်းမှတ်တမ်းတင်ပြီး target backend explain output စစ်ပါ။ Query-count result ကို environment-specific evidence အဖြစ်သာပြပါ။",
        "exercises": "Build a measured course summary, write a Q search, increment a counter with F, reproduce an N+1 list view, fix it with related loading, and record actual query counts and explain output without fabricating numbers.",
        "exercises_mm": "Measured course summary၊ Q search၊ F counter update ပြုလုပ်ပါ။ N+1 list view ပြန်ဖန်တီးပြီး related loading ဖြင့်ပြင်ကာ actual query count/explain output မှတ်ပါ။ မစမ်းဘဲ number မဖန်တီးပါနှင့်။",
        "homework": "Optimize the Student Portal query plan. Submit baseline and after measurements, query code, index rationale, data size, backend version and any tradeoffs observed.",
        "homework_mm": "Student Portal query plan ကို optimize လုပ်ပါ။ Baseline/after measurement၊ query code၊ index rationale၊ data size၊ backend version နှင့် tradeoff များတင်ပါ။",
        "summary": "Optimization is evidence-led ORM design: express the right query, load the right relationships, index the measured access pattern and report actual backend behavior.",
        "summary_mm": "Optimization သည် evidence-led ORM design ဖြစ်သည်။ Query မှန်ရေး၊ relation လိုသလောက် load၊ measured access pattern ကို index လုပ်ပြီး backend behavior အမှန်ကို report လုပ်ပါ။",
        "quiz": [
            _q("What do Q objects help compose?", ["Complex AND/OR/NOT conditions", "Migration files", "CSS classes", "Passwords"], "Complex AND/OR/NOT conditions", "Q provides composable query conditions.", "beginner", 7),
            _q("What does F protect against in a relative update?", ["Stale read-modify-write values", "Template syntax", "Missing URLs", "Static files"], "Stale read-modify-write values", "The database performs the relative expression.", "advanced", 7),
            _q("Which loader is generally for a ForeignKey object?", ["select_related()", "prefetch_related() only", "aggregate()", "migrate()"], "select_related()", "Single-valued joins are suited to select_related.", "intermediate", 7),
            _q("Which loader is generally for many related rows?", ["prefetch_related()", "select_related() only", "get()", "sqlmigrate()"], "prefetch_related()", "Prefetch handles many-valued collections with additional queries.", "intermediate", 7),
            _q("What is an N+1 problem?", ["One list query plus one related query per row", "A migration conflict", "A missing password", "A CSS grid"], "One list query plus one related query per row", "Related loading can avoid this repeated pattern.", "intermediate", 7),
            _q("True or false: an index is free for writes and storage.", ["True", "False"], "False", "Indexes add storage and maintenance cost.", "intermediate", 7),
            _q("What should an optimization claim include?", ["Actual measured conditions and results", "An invented benchmark", "Only a method name", "No dataset details"], "Actual measured conditions and results", "Evidence needs data, backend and measurement context.", "advanced", 7),
            _q("What can explain() provide?", ["A backend query plan", "A user password", "A migration rollback", "A template translation"], "A backend query plan", "It helps inspect how the database intends to execute a query.", "intermediate", 7),
        ],
    },
    {
        "title": "Database Transactions, Constraints and Data Integrity",
        "slug": "05-transactions-and-constraints",
        "description": "Build a transaction-safe enrollment service using constraints, rollback handling, on_commit callbacks and concurrency-aware locking.",
        "description_mm": "Constraint၊ rollback handling၊ on_commit callback နှင့် concurrency-aware locking သုံးသော transaction-safe enrollment service တည်ဆောက်ပါ။",
        "topic": "ACID, atomic blocks, savepoints, IntegrityError, UniqueConstraint, CheckConstraint, select_for_update and idempotency",
        "theory": "A transaction groups database operations so the system can commit a consistent unit or roll it back. Django runs in autocommit by default; transaction.atomic() creates an outer transaction or savepoint depending on nesting. Catch an IntegrityError outside the atomic block that may be marked broken, or use a nested atomic block when a smaller rollback boundary is intentional. Constraints belong in the database: UniqueConstraint prevents duplicate enrollment, CheckConstraint rejects impossible states, and foreign keys protect references. Application validation improves feedback but cannot replace concurrent database enforcement. select_for_update locks selected rows only inside a transaction and only where the backend supports the requested behavior; it does not magically prevent every race. Use it for a scarce seat or mutable balance after defining lock order and testing contention. transaction.on_commit() schedules side effects only after a successful commit, so do not send a message before the row is durable. Idempotency keys, safe retries and clear exception mapping make enrollment APIs reliable. Deadlocks and isolation tradeoffs require operational monitoring, small transactions and consistent lock ordering. Test rollback, duplicate attempts and concurrency with an isolated test database; never claim a concurrency result that was not actually run.",
        "theory_mm": "Transaction သည် database operation များကို consistent unit အဖြစ်စုစည်းပြီး အားလုံး commit သို့မဟုတ် rollback လုပ်စေသည်။ Django default သည် autocommit ဖြစ်ပြီး transaction.atomic() သည် outer transaction သို့မဟုတ် nested အတွင်း savepoint ဖန်တီးသည်။ IntegrityError ကို broken ဖြစ်နိုင်သော atomic block အတွင်း မဖမ်းဘဲ အပြင်တွင် ကိုင်တွယ်ပါ။ သေးငယ်သော rollback boundary လိုလျှင် nested atomic သုံးပါ။ Constraint များကို database တွင်ထားရမည်။ UniqueConstraint သည် duplicate enrollment တား၊ CheckConstraint သည် မဖြစ်နိုင်သော state တား၊ foreign key သည် reference ကာကွယ်သည်။ Application validation သည် feedback အတွက်ကောင်းသော်လည်း concurrent database enforcement အစားထိုးမဟုတ်ပါ။ select_for_update သည် transaction အတွင်း selected row ကို lock လုပ်ပြီး backend support လိုသည်။ Race အားလုံးကို အလိုအလျောက်မတားနိုင်ပါ။ transaction.on_commit() သည် successful commit ပြီးမှ side effect run စေသည်။ Idempotency key၊ safe retry နှင့် exception mapping သည် enrollment API ကို ယုံကြည်ရစေသည်။ Deadlock/isolation သည် monitoring၊ transaction သေးငယ်မှုနှင့် consistent lock order လိုသည်။ Rollback၊ duplicate attempt နှင့် concurrency ကို isolated test database တွင် run လုပ်ပြီး မစမ်းရသေးသော result မရေးပါနှင့်။",
        "concepts": "ACID; autocommit; atomic; savepoint; rollback; IntegrityError; UniqueConstraint; CheckConstraint; foreign-key integrity; on_commit; select_for_update; lock order; isolation; deadlock; idempotency; retry.",
        "concepts_mm": "ACID၊ autocommit၊ atomic၊ savepoint၊ rollback၊ IntegrityError၊ UniqueConstraint၊ CheckConstraint၊ foreign-key integrity၊ on_commit၊ select_for_update၊ lock order၊ isolation၊ deadlock၊ idempotency နှင့် retry တို့ကို လေ့လာရမည်။",
        "syntax": "from django.db import transaction\n\nwith transaction.atomic():\n    enrollment = Enrollment.objects.create(student=student, course=course)\n    transaction.on_commit(lambda: notify_enrollment(enrollment.pk))",
        "examples": [
            _example("Create an atomic enrollment", {"students/services.py": "from django.db import IntegrityError, transaction\n\ndef enroll(student_id, course_id):\n    try:\n        with transaction.atomic():\n            return Enrollment.objects.create(student_id=student_id, course_id=course_id)\n    except IntegrityError as exc:\n        raise DuplicateEnrollment from exc"}, "A student/course pair", "Either the enrollment is committed or the database rejects the duplicate; partial writes are not returned as success.", "Keep the atomic block small, let the database constraint decide duplicates, and map the error to a safe API response outside the block.", "Atomic block ကို သေးငယ်ထားပြီး duplicate ကို database constraint က ဆုံးဖြတ်စေပါ။ Error ကို block အပြင် API response အဖြစ် map လုပ်ပါ။"),
            _example("Add database constraints", {"students/models.py": "class Enrollment(models.Model):\n    student = models.ForeignKey(Student, on_delete=models.PROTECT)\n    course = models.ForeignKey(Course, on_delete=models.PROTECT)\n    status = models.CharField(max_length=20)\n\n    class Meta:\n        constraints = [\n            models.UniqueConstraint(fields=[\"student\", \"course\"], name=\"unique_student_course\"),\n            models.CheckConstraint(condition=models.Q(status__in=[\"active\", \"completed\", \"archived\"]), name=\"valid_enrollment_status\"),\n        ]"}, "A migration generated from the model constraints", "The database rejects duplicate pairs and invalid status values even if a caller bypasses a form.", "Generate and inspect the migration, then test both valid and invalid writes in school_portal_dev.", "Migration generate/inspect လုပ်ပြီး valid/invalid write နှစ်ခုလုံး test လုပ်ပါ။"),
            _example("Use on_commit for a side effect", {"students/services.py": "from django.db import transaction\n\ndef create_and_notify(student, course, send):\n    with transaction.atomic():\n        enrollment = Enrollment.objects.create(student=student, course=course)\n        transaction.on_commit(lambda: send(enrollment.pk))\n    return enrollment"}, "A successful enrollment and a notification function", "Notification runs only after the transaction commits; a rollback does not send a false success message.", "Register a small callback, keep it idempotent, and do not put a network call inside the transaction itself.", "Callback ကို သေးငယ်/idempotent ထားပြီး network call ကို transaction အတွင်း မထည့်ပါနှင့်။"),
            _example("Lock a scarce seat", {"students/services.py": "from django.db import transaction\n\ndef reserve_seat(course_id, student_id):\n    with transaction.atomic():\n        course = Course.objects.select_for_update().get(pk=course_id)\n        if course.available_seats < 1:\n            raise NoSeatsAvailable\n        course.available_seats = F(\"available_seats\") - 1\n        course.save(update_fields=[\"available_seats\"])\n        return Enrollment.objects.create(student_id=student_id, course=course)"}, "Concurrent requests for the same course", "The selected course row is locked during the small transaction; backend support and lock ordering must still be tested.", "Check database support, keep the lock scope small, enforce duplicate uniqueness, and test contention in a suitable isolated environment.", "Database support စစ်ပြီး lock scope သေးငယ်ထားကာ duplicate uniqueness နှင့် contention test လုပ်ပါ။"),
            _example("Test rollback", {"students/tests/test_transactions.py": "from django.test import TestCase\nfrom django.db import IntegrityError, transaction\n\nclass EnrollmentTransactionTests(TestCase):\n    def test_failure_rolls_back(self):\n        with self.assertRaises(IntegrityError):\n            with transaction.atomic():\n                Enrollment.objects.create(student=self.student, course=self.course)\n                Enrollment.objects.create(student=self.student, course=self.course)\n        self.assertEqual(Enrollment.objects.count(), 0)"}, "A test database with a unique enrollment constraint", "The duplicate causes the atomic block to roll back; the test observes the actual count in the isolated test database.", "Create fixtures in setUp, trigger the constraint, assert the exception outside atomic, and verify no partial row remains.", "setUp fixture ပြုလုပ်ပြီး constraint trigger လုပ်ပါ။ atomic အပြင် exception/count ကို assert လုပ်ပါ။"),
        ],
        "mistakes": ["Catching IntegrityError inside a broken outer atomic block and continuing queries.", "Assuming atomic alone prevents all races.", "Calling external services before commit or holding locks during network calls.", "Leaving a uniqueness rule only in application code."],
        "mistakes_mm": ["Broken outer atomic block အတွင်း IntegrityError ဖမ်းပြီး query ဆက်လုပ်ခြင်း။", "atomic တစ်ခုတည်းဖြင့် race အားလုံးတားနိုင်သည်ဟု ယူဆခြင်း။", "Commit မတိုင်မီ external service ခေါ်ခြင်း သို့မဟုတ် network call အတွင်း lock ထားခြင်း။", "Uniqueness rule ကို application code တစ်ခုတည်းတွင်ထားခြင်း။"],
        "best_practices": "Make the database authoritative for invariants, keep transactions short, catch exceptions outside the atomic boundary, use on_commit for durable side effects, define lock order, make retries idempotent and test the actual backend behavior.",
        "best_practices_mm": "Invariant အတွက် database ကို authoritative ထားပါ။ Transaction တိုတိုသုံးပြီး atomic အပြင် exception ကိုင်တွယ်ပါ။ Durable side effect ကို on_commit သုံးပါ။ Lock order သတ်မှတ်၊ retry ကို idempotent ထားပြီး actual backend behavior test လုပ်ပါ။",
        "exercises": "Implement a transaction-safe enrollment service with a unique constraint, a valid-status check, rollback test, on_commit callback and a documented decision about whether select_for_update is needed for seat allocation.",
        "exercises_mm": "Unique constraint၊ valid-status check၊ rollback test၊ on_commit callback ပါသော transaction-safe enrollment service တည်ဆောက်ပါ။ Seat allocation အတွက် select_for_update လို/မလို ဆုံးဖြတ်ချက်ရေးပါ။",
        "homework": "Design and test a Transaction-Safe Enrollment Management Service. Include failure mapping, idempotency key behavior, constraints, lock scope, retry policy, audit event timing and a concurrency test plan.",
        "homework_mm": "Failure mapping၊ idempotency key၊ constraint၊ lock scope၊ retry policy၊ audit event timing နှင့် concurrency test plan ပါသော Transaction-Safe Enrollment Management Service design/test ပြုလုပ်ပါ။",
        "summary": "Transactions provide boundaries, while constraints provide truth. Reliable enrollment combines both with safe exception handling, post-commit effects and measured concurrency tests.",
        "summary_mm": "Transaction သည် boundary ပေးပြီး constraint သည် truth ပေးသည်။ Reliable enrollment သည် safe exception handling၊ post-commit effect နှင့် measured concurrency test တို့ကို ပေါင်းစပ်ရသည်။",
        "quiz": [
            _q("What does transaction.atomic() provide?", ["A commit/rollback boundary", "A CSS layout", "A password hash", "A URL route"], "A commit/rollback boundary", "Atomic groups operations into a transaction or savepoint.", "beginner", 8),
            _q("Where should an IntegrityError commonly be caught?", ["Outside the atomic block that may be broken", "Only inside every query", "In a template", "Never"], "Outside the atomic block that may be broken", "The outer boundary can safely map the failure after rollback.", "advanced", 8),
            _q("What does on_commit ensure?", ["A callback runs after successful commit", "A query never fails", "A password is shown", "A migration is deleted"], "A callback runs after successful commit", "It prevents false success side effects on rollback.", "intermediate", 8),
            _q("Why is a UniqueConstraint important for enrollment?", ["It remains authoritative under concurrent writes", "It formats a template", "It creates a static file", "It disables PostgreSQL"], "It remains authoritative under concurrent writes", "Application checks can race; database constraints arbitrate.", "advanced", 8),
            _q("What does select_for_update generally do?", ["Locks selected rows within a transaction", "Publishes a course", "Runs a migration", "Creates a user"], "Locks selected rows within a transaction", "It requests row locking where the backend supports it.", "intermediate", 8),
            _q("True or false: atomic() alone prevents every race condition.", ["True", "False"], "False", "Correct constraints, locks, isolation and idempotency still matter.", "intermediate", 8),
            _q("Where should an external notification usually be scheduled?", ["transaction.on_commit()", "Before the write", "Inside a long-held lock", "In a model field"], "transaction.on_commit()", "The side effect should follow durable state.", "intermediate", 8),
            _q("What is idempotency useful for?", ["Safe retries without duplicate effects", "Disabling constraints", "Showing passwords", "Skipping tests"], "Safe retries without duplicate effects", "Retries are common in distributed systems.", "advanced", 8),
        ],
    },
]


def _render_examples(item, burmese=False):
    rendered = []
    for index, example in enumerate(item["examples"], 1):
        files = []
        for filename, source in example["files"].items():
            language = "python" if filename.endswith(".py") else "sql" if filename.endswith(".sql") else "text"
            files.append(f"File: {filename}\n```{language}\n{source}\n```")
        if burmese:
            rendered.append(f"နမူနာ {index}: {example['title']}\nSetup/Input: {example['input']}\n" + "\n\n".join(files) + f"\nမျှော်မှန်းရလဒ်: {example['output']}\nအဆင့်လိုက်ရှင်းလင်းချက်: {example['steps_mm']}\nActual output ကို isolated environment တွင် စစ်ဆေးပြီး မှတ်တမ်းတင်ပါ။")
        else:
            rendered.append(f"Example {index}: {example['title']}\nSetup/input: {example['input']}\n" + "\n\n".join(files) + f"\nExpected behavior: {example['output']}\nStep-by-step explanation: {example['steps']}\nRun the example only in the isolated educational project and record actual output.")
    return "\n\n".join(rendered)


def _render_en(item: dict) -> str:
    mistakes = "\n".join(f"- {value}" for value in item["mistakes"])
    quiz = "\n".join(f"{i}. {q['prompt']} Options: {', '.join(q['options'])}" for i, q in enumerate(item["quiz"], 1))
    objectives = "\n".join(f"{i}. Explain and apply {item['topic']} (objective {i})." for i in range(1, 5))
    return dedent(f"""
        # {item['title']}

        ## Introduction
        {item['description']}

        ## Prerequisites and safe scope
        {COMMON_PREREQ}

        ## Learning objectives
        {objectives}

        ## Detailed theory
        {item['theory']}

        ## Concepts and terminology
        {item['concepts']}

        ## Syntax and API reference
        ```python
        {item['syntax']}
        ```
        Read the syntax as a contract: inputs, database effects, evaluation timing and failure behavior must be understood before code is placed in a view.

        ## Complete progressive examples
        {_render_examples(item)}

        ## Common mistakes
        {mistakes}

        ## Best practices
        {item['best_practices']}

        ## Guided exercises
        {item['exercises']}

        ## Independent exercises
        Rebuild the lesson exercise from an empty Django app in the isolated Student Portal project. Add a normal case, an empty or missing case, an invalid-input case, and one focused test. Record commands and actual output; do not substitute a fabricated benchmark or connection result.

        ## Homework
        {item['homework']}

        ## Lesson quiz
        {quiz}
        Answer the questions before checking the private answer key. Student quiz payloads must not expose correct answers.

        ## Summary
        {item['summary']}

        ## Further reading and version note
        Target the documented Django 6.0 API surface with Python 3.12+, PostgreSQL 14+ and psycopg 3.1.12+ or a newer compatible psycopg 3 release. Verify exact versions in the project lockfile. Read the official Django models, queries, migrations, databases, transactions and optimization documentation. Never run tutorial migrations against the Learn-Coding platform database.
    """).strip()


def _render_mm(item: dict) -> str:
    mistakes = "\n".join(f"- {value}" for value in item["mistakes_mm"])
    quiz = "\n".join(f"{i}. {q['prompt']} Options: {', '.join(q['options'])}" for i, q in enumerate(item["quiz"], 1))
    objectives = "\n".join(f"{i}။ {item['topic']} ကို ရှင်းပြပြီး လက်တွေ့အသုံးချနိုင်ရန် (ရည်မှန်းချက် {i})။" for i in range(1, 5))
    return dedent(f"""
        # {item['title']}

        ## မိတ်ဆက်
        {item['description_mm']}

        ## ကြိုတင်လိုအပ်ချက်နှင့် လုံခြုံသော scope
        {COMMON_PREREQ_MM}

        ## သင်ယူရမည့်ရည်မှန်းချက်
        {objectives}

        ## အသေးစိတ်သီအိုရီ
        {item['theory_mm']}

        ## Concept နှင့် technical terminology
        {item['concepts_mm']}

        ## Syntax နှင့် API reference
        ```python
        {item['syntax']}
        ```
        Syntax ကို contract အဖြစ်ဖတ်ပါ။ Input၊ database effect၊ evaluation timing နှင့် failure behavior ကိုနားလည်ပြီးမှ view ထဲ code ထည့်ပါ။

        ## ပြည့်စုံသော progressive နမူနာများ
        {_render_examples(item, True)}

        ## အများဆုံးမှားတတ်သောအချက်များ
        {mistakes}

        ## အကောင်းဆုံးနည်းလမ်းများ
        {item['best_practices_mm']}

        ## လမ်းညွှန်လေ့ကျင့်ခန်း
        {item['exercises_mm']}

        ## ကိုယ်တိုင်လေ့ကျင့်ရန်
        Isolated Student Portal project ထဲက empty Django app မှ lesson exercise ကို ကိုယ်တိုင်ပြန်တည်ဆောက်ပါ။ Normal case၊ empty/missing case၊ invalid-input case နှင့် focused test တစ်ခုထည့်ပါ။ Command နှင့် actual output ကို မှတ်တမ်းတင်ပြီး မစမ်းရသေးသော benchmark/connection result မဖန်တီးပါနှင့်။

        ## အိမ်စာ
        {item['homework_mm']}

        ## Lesson quiz
        {quiz}
        အဖြေကို အရင်စဉ်းစားပြီး private answer key ဖြင့်သာ စစ်ပါ။ Student quiz payload ထဲ correct answer မထည့်ရပါ။

        ## အနှစ်ချုပ်
        {item['summary_mm']}

        ## ဆက်လက်ဖတ်ရှုရန်နှင့် version note
        Django 6.0 API၊ Python 3.12+၊ PostgreSQL 14+ နှင့် psycopg 3.1.12+ သို့မဟုတ် compatible psycopg 3 release ကို target ထားပါ။ Project lockfile ထဲ exact version ကို စစ်ပါ။ Django models၊ queries၊ migrations၊ databases၊ transactions နှင့် optimization official documentation ကို ဖတ်ပါ။ Tutorial migration ကို Learn-Coding platform database သို့ မrun ပါနှင့်။
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
        quiz = LessonQuiz(lesson_id=lesson.id, title=f"{item['title']} knowledge check", explanation="Review the database boundary and explain why each answer is safe.", status="draft")
        db.add(quiz)
        db.flush()
    if quiz.status not in {"published", "approved", "in_review"}:
        quiz.title = f"{item['title']} knowledge check"
        quiz.explanation = "Review the database boundary and explain why each answer is safe."
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
    values = {"title": f"{item['title']} practice", "description_en": item["exercises"], "description_mm": item["exercises_mm"], "difficulty": "intermediate", "language": "django", "starter_code": "# Build this exercise only in the isolated Student Portal project.\n", "status": "draft"}
    if exercise and exercise.status not in {"published", "approved", "in_review"}:
        for key, value in values.items():
            setattr(exercise, key, value)
    elif not exercise:
        db.add(CodingExercise(lesson_id=lesson.id, slug=f"django-module-five-{lesson.order_index}-practice", **values))


def _module_assessment():
    questions = []
    for item in LESSONS:
        questions.extend(item["quiz"][:3])
    questions.extend([
        _q("Which Django operation should be inspected before applying a migration?", ["migrate --plan and sqlmigrate", "Delete the database", "Publish the course", "Render a template"], "migrate --plan and sqlmigrate", "Inspection reveals pending operations and backend SQL before execution.", "advanced", 4),
        _q("Which relationship model is appropriate for enrollment date and status?", ["An explicit Enrollment through model", "A CSS class", "A plain template variable", "A password field"], "An explicit Enrollment through model", "Relationship metadata belongs on a first-class record.", "intermediate", 6),
        _q("What should an optimization report include?", ["Actual dataset, backend and measured result", "An invented speedup", "Only a method name", "No test"], "Actual dataset, backend and measured result", "Performance claims need reproducible context.", "advanced", 7),
        _q("Which boundary should send a post-enrollment notification?", ["transaction.on_commit()", "Before the transaction", "Inside a long lock", "A template filter"], "transaction.on_commit()", "The notification should follow durable state.", "intermediate", 8),
    ])
    return questions[:24]


SYNTAX_REFERENCES = [
    {"slug": "django-models-model", "title": "models.Model", "lesson": 1, "syntax": "class Student(models.Model): ...", "description": "Base class for persisted Django model definitions.", "example": "class Student(models.Model):\n    name = models.CharField(max_length=120)", "output": "A model state that maps to a table.", "mm": "Database table နှင့် mapping လုပ်သော model base class ဖြစ်သည်။"},
    {"slug": "django-models-fields", "title": "Django model fields", "lesson": 1, "syntax": "models.CharField(max_length=120)", "description": "Declares column type, validation metadata and storage options.", "example": "email = models.EmailField(unique=True)", "output": "A validated unique email field.", "mm": "Column type၊ validation metadata နှင့် storage option သတ်မှတ်သည်။"},
    {"slug": "django-models-constraints", "title": "UniqueConstraint and CheckConstraint", "lesson": 1, "syntax": "models.UniqueConstraint(fields=[...], name=...)", "description": "Expresses database-level invariants.", "example": "models.CheckConstraint(condition=models.Q(age__gte=13), name=\"adult_age\")", "output": "Invalid writes are rejected by the database.", "mm": "Database-level invariant ကို ဖော်ပြသည်။"},
    {"slug": "django-databases-setting", "title": "DATABASES setting", "lesson": 2, "syntax": "DATABASES = {\"default\": {\"ENGINE\": ..., \"NAME\": ...}}", "description": "Maps Django database aliases to backend connection settings.", "example": "DATABASES[\"default\"][\"ENGINE\"]", "output": "The configured backend name.", "mm": "Django database alias နှင့် backend setting ချိတ်သည်။"},
    {"slug": "django-postgres-backend", "title": "PostgreSQL backend", "lesson": 3, "syntax": "django.db.backends.postgresql", "description": "Django backend adapter for PostgreSQL.", "example": "\"ENGINE\": \"django.db.backends.postgresql\"", "output": "ORM uses the PostgreSQL adapter.", "mm": "PostgreSQL အတွက် Django backend adapter ဖြစ်သည်။"},
    {"slug": "django-makemigrations", "title": "makemigrations", "lesson": 4, "syntax": "python manage.py makemigrations app_label", "description": "Creates migration files from model state changes.", "example": "python manage.py makemigrations students", "output": "A numbered migration file is created.", "mm": "Model state ပြောင်းလဲမှုမှ migration file ဖန်တီးသည်။"},
    {"slug": "django-migrate", "title": "migrate", "lesson": 4, "syntax": "python manage.py migrate --plan", "description": "Applies or plans unapplied migrations.", "example": "python manage.py migrate --plan", "output": "Pending operations are listed.", "mm": "မလုပ်ရသေးသော migration ကို plan/apply လုပ်သည်။"},
    {"slug": "django-showmigrations", "title": "showmigrations", "lesson": 4, "syntax": "python manage.py showmigrations students", "description": "Shows migration graph and applied state.", "example": "python manage.py showmigrations students", "output": "Migration names and marks are displayed.", "mm": "Migration graph နှင့် applied state ပြသည်။"},
    {"slug": "django-sqlmigrate", "title": "sqlmigrate", "lesson": 4, "syntax": "python manage.py sqlmigrate students 0001", "description": "Displays backend SQL for a migration.", "example": "python manage.py sqlmigrate students 0001", "output": "SQL is shown without being applied.", "mm": "Migration အတွက် backend SQL ပြသည်။"},
    {"slug": "django-objects-create", "title": "objects.create()", "lesson": 5, "syntax": "Student.objects.create(name=...)", "description": "Creates and saves one model instance.", "example": "Student.objects.create(email=\"learner@example.test\")", "output": "A saved Student row.", "mm": "Model instance တစ်ခုဖန်တီးပြီး save လုပ်သည်။"},
    {"slug": "django-objects-get-filter", "title": "objects.get() and filter()", "lesson": 5, "syntax": "Student.objects.get(pk=1)\nStudent.objects.filter(active=True)", "description": "Retrieves one expected row or a composable QuerySet.", "example": "Student.objects.filter(last_name__icontains=\"a\")", "output": "A lazy matching QuerySet.", "mm": "တစ်ခုတည်းသော row သို့မဟုတ် composable QuerySet ရယူသည်။"},
    {"slug": "django-objects-update", "title": "objects.update()", "lesson": 5, "syntax": "Student.objects.filter(pk=1).update(age=18)", "description": "Performs a direct bulk update.", "example": "Student.objects.filter(pk=1).update(age=F(\"age\") + 1)", "output": "The database updates matching rows.", "mm": "Matching row များကို bulk update လုပ်သည်။"},
    {"slug": "django-get-or-create", "title": "get_or_create() and update_or_create()", "lesson": 5, "syntax": "Model.objects.get_or_create(...)\nModel.objects.update_or_create(...) ", "description": "Convenience operations that still require database uniqueness for concurrency.", "example": "Student.objects.get_or_create(email=\"learner@example.test\")", "output": "An existing or newly created object.", "mm": "ရှိပြီးသားကိုရယူ/မရှိလျှင်ဖန်တီးသော convenience operation ဖြစ်သည်။"},
    {"slug": "django-select-related", "title": "select_related()", "lesson": 7, "syntax": "Student.objects.select_related(\"profile\")", "description": "Joins single-valued related objects.", "example": "Student.objects.select_related(\"profile\")", "output": "Profile data is loaded with the main query.", "mm": "Single-valued relation ကို join ဖြင့် load လုပ်သည်။"},
    {"slug": "django-prefetch-related", "title": "prefetch_related()", "lesson": 7, "syntax": "Student.objects.prefetch_related(\"enrollments__course\")", "description": "Loads many-valued relations with additional coordinated queries.", "example": "Course.objects.prefetch_related(\"enrollments\")", "output": "Related collections are cached for access.", "mm": "Many-valued relation ကို coordinated query ဖြင့် load လုပ်သည်။"},
    {"slug": "django-q-f-expressions", "title": "Q() and F()", "lesson": 7, "syntax": "Q(a=1) | Q(b=2)\nF(\"credits\") + 1", "description": "Composes conditions and database-side column expressions.", "example": "Student.objects.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q))", "output": "A combined condition is evaluated by the database.", "mm": "Condition ပေါင်းစပ်ပြီး column expression ကို database တွင်တွက်သည်။"},
    {"slug": "django-annotate-aggregate", "title": "annotate() and aggregate()", "lesson": 7, "syntax": "Course.objects.annotate(total=Count(\"enrollments\"))", "description": "Adds per-row values or returns summary aggregates.", "example": "Course.objects.aggregate(total=Count(\"id\"))", "output": "A computed count dictionary.", "mm": "Row တစ်ခုချင်း computed value သို့မဟုတ် summary aggregate ရသည်။"},
    {"slug": "django-queryset-explain", "title": "QuerySet.explain()", "lesson": 7, "syntax": "queryset.explain()", "description": "Requests a database execution plan for inspection.", "example": "Student.objects.filter(last_name__startswith=\"A\").explain()", "output": "Backend-specific plan text.", "mm": "Database execution plan ကို စစ်ဆေးရန်တောင်းသည်။"},
    {"slug": "django-transaction-atomic", "title": "transaction.atomic()", "lesson": 8, "syntax": "with transaction.atomic(): ...", "description": "Groups database work into a commit/rollback boundary.", "example": "with transaction.atomic():\n    Enrollment.objects.create(...)" , "output": "All operations commit or roll back together.", "mm": "Database operation များကို commit/rollback boundary ထဲစုသည်။"},
    {"slug": "django-transaction-on-commit", "title": "transaction.on_commit()", "lesson": 8, "syntax": "transaction.on_commit(callback)", "description": "Runs a callback only after a successful commit.", "example": "transaction.on_commit(lambda: send_email(enrollment.pk))", "output": "The side effect follows durable state.", "mm": "Successful commit ပြီးမှ callback run သည်။"},
    {"slug": "django-select-for-update", "title": "select_for_update()", "lesson": 8, "syntax": "Model.objects.select_for_update().get(pk=...)", "description": "Requests a row lock inside a suitable transaction.", "example": "with transaction.atomic():\n    course = Course.objects.select_for_update().get(pk=course_id)", "output": "The selected row is locked for the transaction.", "mm": "သင့်တော်သော transaction အတွင်း row lock တောင်းသည်။"},
]


def _project_source_files():
    return {
        "manage.py": "#!/usr/bin/env python\nimport os\nimport sys\n\nif __name__ == \"__main__\":\n    os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\", \"school_site.settings\")\n    from django.core.management import execute_from_command_line\n    execute_from_command_line(sys.argv)\n",
        "school_site/settings.py": "import os\nfrom pathlib import Path\nBASE_DIR = Path(__file__).resolve().parent.parent\nSECRET_KEY = os.environ.get(\"DJANGO_SECRET_KEY\", \"unsafe-local-only\")\nDEBUG = os.environ.get(\"DJANGO_DEBUG\", \"1\") == \"1\"\nINSTALLED_APPS = [\"django.contrib.auth\", \"django.contrib.contenttypes\", \"students\", \"courses\"]\nDATABASES = {\"default\": {\"ENGINE\": \"django.db.backends.postgresql\", \"NAME\": os.environ[\"POSTGRES_DB\"], \"USER\": os.environ[\"POSTGRES_USER\"], \"PASSWORD\": os.environ[\"POSTGRES_PASSWORD\"], \"HOST\": os.environ.get(\"POSTGRES_HOST\", \"127.0.0.1\"), \"PORT\": os.environ.get(\"POSTGRES_PORT\", \"5432\")}}\nUSE_TZ = True\nTIME_ZONE = \"UTC\"\nROOT_URLCONF = \"school_site.urls\"\nDEFAULT_AUTO_FIELD = \"django.db.models.BigAutoField\"\n",
        "school_site/urls.py": "from django.urls import include, path\nurlpatterns = [path(\"students/\", include(\"students.urls\")), path(\"courses/\", include(\"courses.urls\"))]\n",
        "students/models.py": "from django.db import models\n\nclass Student(models.Model):\n    first_name = models.CharField(max_length=80)\n    last_name = models.CharField(max_length=80)\n    email = models.EmailField(unique=True)\n    is_archived = models.BooleanField(default=False)\n    joined_at = models.DateTimeField(auto_now_add=True)\n    def __str__(self):\n        return f\"{self.first_name} {self.last_name}\"\n\nclass StudentProfile(models.Model):\n    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name=\"profile\")\n    guardian_phone = models.CharField(max_length=32, blank=True)\n\nclass Course(models.Model):\n    code = models.CharField(max_length=20, unique=True)\n    title = models.CharField(max_length=160)\n    available_seats = models.PositiveIntegerField(default=0)\n\nclass Enrollment(models.Model):\n    class Status(models.TextChoices):\n        ACTIVE = \"active\", \"Active\"\n        COMPLETED = \"completed\", \"Completed\"\n        ARCHIVED = \"archived\", \"Archived\"\n    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name=\"enrollments\")\n    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name=\"enrollments\")\n    status = models.CharField(max_length=20, choices=Status, default=Status.ACTIVE)\n    enrolled_at = models.DateTimeField(auto_now_add=True)\n    class Meta:\n        constraints = [models.UniqueConstraint(fields=[\"student\", \"course\"], name=\"unique_student_course\"), models.CheckConstraint(condition=models.Q(status__in=[\"active\", \"completed\", \"archived\"]), name=\"valid_enrollment_status\")]\n",
        "students/services.py": "from django.db import IntegrityError, transaction\nfrom .models import Course, Enrollment\n\nclass DuplicateEnrollment(Exception):\n    pass\n\ndef enroll(student_id, course_id):\n    try:\n        with transaction.atomic():\n            enrollment = Enrollment.objects.create(student_id=student_id, course_id=course_id)\n            transaction.on_commit(lambda: None)\n            return enrollment\n    except IntegrityError as exc:\n        raise DuplicateEnrollment from exc\n\ndef reserve_seat(course_id, student_id):\n    with transaction.atomic():\n        course = Course.objects.select_for_update().get(pk=course_id)\n        if course.available_seats < 1:\n            raise ValueError(\"No seats available\")\n        course.available_seats -= 1\n        course.save(update_fields=[\"available_seats\"])\n        return enroll(student_id, course_id)\n",
        "courses/services.py": "from django.db.models import Count\nfrom students.models import Course\n\ndef summaries():\n    return Course.objects.annotate(enrollment_count=Count(\"enrollments\", distinct=True)).order_by(\"code\")\n",
        "students/views.py": "from django.core.paginator import Paginator\nfrom django.shortcuts import get_object_or_404, render\nfrom .models import Student\n\ndef list_students(request):\n    query = request.GET.get(\"q\", \"\").strip()[:80]\n    rows = Student.objects.filter(is_archived=False, last_name__icontains=query).select_related(\"profile\").order_by(\"last_name\", \"id\")\n    return render(request, \"students/list.html\", {\"page\": Paginator(rows, 20).get_page(request.GET.get(\"page\")), \"query\": query})\n\ndef detail(request, pk):\n    student = get_object_or_404(Student.objects.prefetch_related(\"enrollments__course\"), pk=pk, is_archived=False)\n    return render(request, \"students/detail.html\", {\"student\": student})\n",
        "students/urls.py": "from django.urls import path\nfrom . import views\napp_name = \"students\"\nurlpatterns = [path(\"\", views.list_students, name=\"list\"), path(\"<int:pk>/\", views.detail, name=\"detail\")]\n",
        "courses/views.py": "from django.shortcuts import render\nfrom .services import summaries\n\ndef list_courses(request):\n    return render(request, \"courses/list.html\", {\"courses\": summaries()})\n",
        "courses/urls.py": "from django.urls import path\nfrom .views import list_courses\napp_name = \"courses\"\nurlpatterns = [path(\"\", list_courses, name=\"list\")]\n",
        "students/tests/test_models.py": "from django.test import TestCase\nfrom students.models import Course, Student, Enrollment\n\nclass EnrollmentTests(TestCase):\n    def test_duplicate_enrollment_is_rejected(self):\n        student = Student.objects.create(first_name=\"A\", last_name=\"Learner\", email=\"a@example.test\")\n        course = Course.objects.create(code=\"DJ-ORM\", title=\"Django ORM\")\n        Enrollment.objects.create(student=student, course=course)\n        with self.assertRaises(Exception):\n            Enrollment.objects.create(student=student, course=course)\n",
        "templates/students/list.html": "<h1>Students</h1>{% for student in page.object_list %}<article><a href=\"{% url 'students:detail' student.pk %}\">{{ student }}</a></article>{% empty %}<p>No students found.</p>{% endfor %}",
        "templates/students/detail.html": "<h1>{{ student }}</h1><ul>{% for enrollment in student.enrollments.all %}<li>{{ enrollment.course.title }}</li>{% empty %}<li>No enrollments.</li>{% endfor %}</ul>",
        "templates/courses/list.html": "<h1>Courses</h1>{% for course in courses %}<article><h2>{{ course.title }}</h2><p>{{ course.enrollment_count }}</p></article>{% empty %}<p>No courses.</p>{% endfor %}",
        "students/migrations/0001_initial.py": "from django.db import migrations, models\n\nclass Migration(migrations.Migration):\n    initial = True\n    dependencies = []\n    operations = [migrations.CreateModel(name=\"Student\", fields=[(\"id\", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name=\"ID\")), (\"first_name\", models.CharField(max_length=80)), (\"last_name\", models.CharField(max_length=80)), (\"email\", models.EmailField(max_length=254, unique=True))])]\n",
    }


def _ensure_project(db, course, module):
    slug = "django-database-student-management-system"
    source_files = _project_source_files()
    brief = {
        "goal": "Upgrade the earlier Django Student Portal from in-memory samples to a PostgreSQL-backed Student Management System.",
        "scope": "Module 05 draft project only; use synthetic data and an isolated school_portal_dev database.",
        "setup_commands": ["python -m venv .venv", "pip install -r requirements.txt", "python manage.py check", "python manage.py makemigrations", "python manage.py migrate", "python manage.py test"],
        "routes": ["/students/", "/students/<id>/", "/courses/"],
        "source_files": source_files,
        "required_features": ["Student", "StudentProfile", "Course", "Enrollment", "PostgreSQL", "migrations", "CRUD", "pagination", "constraints", "transactions", "related loading", "tests"],
        "expected_behavior": ["Student list filters and paginates", "Student detail shows related enrollments", "Course summaries annotate enrollment counts", "Duplicate enrollment is rejected", "Seat reservation uses a short transaction and row lock", "Missing records return 404"],
        "testing_guide": "Run check, migration plan inspection, unit/integration tests and a controlled query-count test in an isolated test database. Record actual output.",
        "deployment_guide": "Use a secret provider, TLS, least-privilege PostgreSQL role, DEBUG=False and a reviewed migration plan. Do not deploy this draft automatically.",
        "review_checklist": ["No real student data", "No production DSN or password", "Published content remains protected", "Constraints are database-backed", "Transactions are short", "Query optimizations are measured", "Answer keys remain private"],
    }
    values = {"title": "Database-Driven Django Student Management System", "description_en": "A PostgreSQL-backed Django Student Management System with models, migrations, CRUD, relationships, constraints, transactions, query optimization and tests.", "description_mm": "Model၊ migration၊ CRUD၊ relationship၊ constraint၊ transaction၊ query optimization နှင့် test ပါသော PostgreSQL-backed Django Student Management System ဖြစ်သည်။", "difficulty": "advanced", "estimated_hours": 24, "requirements": "Python 3.12+, Django 6.0 target, PostgreSQL 14+, psycopg 3.1.12+, SQL basics and an isolated school_portal_dev database.", "learning_outcomes": "Design education models, run safe migrations, implement CRUD and enrollment rules, optimize related queries, and test transaction behavior.", "technology_stack": "Python | Django | PostgreSQL | psycopg | Django ORM | HTML | Django Test Framework", "prerequisites": "Complete Django Modules 01–04 and use synthetic data only.", "architecture_overview": "school_site owns settings and root URLs; students owns education models and enrollment services; courses owns course summaries; migrations evolve schema; templates render list/detail pages; tests run against an isolated test database.", "folder_structure": "\n".join(source_files.keys()), "testing_guide": brief["testing_guide"], "deployment_guide": brief["deployment_guide"], "tags_json": json.dumps(["django", "models", "orm", "postgresql", "transactions", "student-management"], ensure_ascii=False), "languages_json": json.dumps(["Python", "SQL", "HTML"], ensure_ascii=False), "brief_json": json.dumps(brief, ensure_ascii=False), "status": "draft", "published": False}
    project = db.scalar(select(ProjectTemplate).where(ProjectTemplate.slug == slug))
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
        ("Schema and PostgreSQL", "Configure the isolated database, define four models and inspect the first migration.", "students/models.py"),
        ("CRUD and relationships", "Implement synthetic student/course CRUD, profile access and Enrollment reverse queries.", "students/services.py"),
        ("Integrity and transactions", "Add constraints, duplicate handling, seat locking, rollback and post-commit behavior.", "students/services.py"),
        ("Measured quality", "Run tests, inspect query counts and explain output, then document the safe deployment plan.", "students/tests/test_models.py"),
    ]
    for position, (title, description, filename) in enumerate(milestones, 1):
        row = db.scalar(select(ProjectMilestone).where(ProjectMilestone.project_id == project.id, ProjectMilestone.position == position))
        data = {"title": title, "slug": f"database-portal-{position}", "description_en": description, "description_mm": description + " ကို isolated project တွင် လေ့ကျင့်ပါ။", "content_en": f"Required boundary: {filename}\n\n{description}\n\nUse synthetic records and record actual command output.", "content_mm": "Synthetic record နှင့် isolated database သုံးပြီး actual command output မှတ်တမ်းတင်ပါ။", "code": source_files.get(filename, ""), "filename": filename, "expected_output": "The learner records actual check/test/migration results and explains one tradeoff.", "line_explanation": "Read the model or service boundary, run the focused command, inspect the result, then add a regression test.", "completion_criteria": "Source exists, checks/tests are run, constraints and isolation are documented, and no production data is used.", "resources_json": json.dumps([{"title": "Django models", "url": "https://docs.djangoproject.com/en/6.0/topics/db/models/"}, {"title": "Django transactions", "url": "https://docs.djangoproject.com/en/6.0/topics/db/transactions/"}], ensure_ascii=False), "required": True}
        if not row:
            db.add(ProjectMilestone(project_id=project.id, position=position, **data))
        else:
            for key, value in data.items():
                setattr(row, key, value)
    requirements = [
        ("Persistent Student domain", "Student, StudentProfile, Course and Enrollment are modeled with PostgreSQL-compatible fields and relationships.", "Models and migrations exist; reverse queries and uniqueness are tested."),
        ("Safe enrollment workflow", "Enrollment creation handles duplicate attempts and transaction failure without partial success.", "Unique/check constraints, atomic boundary, exception mapping and rollback test are present."),
        ("Measured database access", "List/detail views use pagination and intentional related loading.", "Query count or plan evidence is recorded from the isolated test database."),
    ]
    for position, (title, description, acceptance) in enumerate(requirements, 1):
        row = db.scalar(select(ProjectRequirement).where(ProjectRequirement.project_id == project.id, ProjectRequirement.position == position))
        data = {"title": title, "description": description, "acceptance_criteria": acceptance, "required": True}
        if not row:
            db.add(ProjectRequirement(project_id=project.id, position=position, **data))
        else:
            for key, value in data.items():
                setattr(row, key, value)
    rubric = [("Schema design", "Models, relationships, field choices and constraints express the education domain.", 25), ("Persistence", "PostgreSQL configuration, migrations and safe environment boundaries are correct.", 20), ("Application behavior", "CRUD, pagination, enrollment and error handling work with synthetic data.", 25), ("Integrity and performance", "Transactions, duplicate protection, related loading and measured query evidence are present.", 20), ("Tests and documentation", "Tests run, outputs are recorded, privacy/security and remaining limits are documented.", 10)]
    for position, (name, description, weight) in enumerate(rubric, 1):
        row = db.scalar(select(ProjectRubricCriterion).where(ProjectRubricCriterion.project_id == project.id, ProjectRubricCriterion.position == position))
        if not row:
            db.add(ProjectRubricCriterion(project_id=project.id, position=position, name=name, description=description, weight=weight))
        else:
            row.name, row.description, row.weight = name, description, weight
    return project


def _ensure_syntax_references(db, course, lessons_by_position):
    created = 0
    for display_order, item in enumerate(SYNTAX_REFERENCES, 1):
        ref = db.scalar(select(SyntaxReference).where(SyntaxReference.course_id == course.id, SyntaxReference.slug == item["slug"]))
        values = {"title": item["title"], "category": "Django Models ORM and PostgreSQL", "description": item["description"], "basic_syntax": item["syntax"], "when_to_use": "Use this reference in the matching Module 05 lesson and verify it against the target Django version.", "important_notes": "Keep credentials private, use an isolated database and inspect generated SQL before applying changes.", "reference_type": "framework_api", "difficulty": "intermediate", "purpose": item["description"], "syntax_format": item["syntax"], "parameters": "See the official Django documentation for the documented arguments.", "return_value": item["output"], "version_compatibility": "Django 6.0 target; verify against the exact project lockfile.", "input_output": f"Input: {item['example']}\nOutput: {item['output']}", "common_mistakes": "Do not expose credentials, mutate production data, or assume behavior without a focused test.", "best_practices": "Use explicit constraints, isolated test data, stable ordering, measured query plans and protected answer keys.", "practice_exercises": "Implement the linked lesson exercise and record the actual result.", "further_reading": "https://docs.djangoproject.com/en/6.0/", "minimum_examples": 1, "review_notes": "Phase 07 Module 05 draft; publication remains review-only.", "status": "draft", "display_order": display_order}
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
            db.add(SyntaxReferenceTranslation(reference_id=ref.id, locale="my", title=item["title"], description=item["mm"], purpose=item["mm"], syntax_format=item["syntax"], parameters="Official documentation နှင့် supported version ကို စစ်ပါ။", return_value=item["output"], version_compatibility="Django 6.0 target ဖြစ်ပြီး lockfile version နှင့် တိုက်စစ်ပါ။", input_output=f"Input: {item['example']}\nOutput: {item['output']}", common_mistakes="Credential မဖော်ပါနှင့်။ Production database မထိပါနှင့်။", best_practices="Constraint၊ isolated data၊ stable order နှင့် measured test သုံးပါ။", practice_exercises="သက်ဆိုင်ရာ lesson exercise ကို run ပြီး actual result မှတ်ပါ။", further_reading="https://docs.djangoproject.com/en/6.0/", status="draft"))
        example = db.scalar(select(SyntaxReferenceExample).where(SyntaxReferenceExample.reference_id == ref.id, SyntaxReferenceExample.example_number == 1))
        example_values = {"title": item["title"], "code": item["example"], "language": "django", "difficulty": "intermediate", "description": item["description"], "setup": "Use the supported isolated Django project.", "sample_input": item["syntax"], "expected_output": item["output"], "explanation": "Run the focused example and compare actual behavior with the documented expectation.", "common_mistakes": "Keep security and database target boundaries explicit.", "verification_steps": "Run check/test or inspect the generated SQL and record the actual result."}
        if not example:
            example = SyntaxReferenceExample(reference_id=ref.id, example_number=1, **example_values)
            db.add(example)
            db.flush()
        else:
            for key, value in example_values.items():
                setattr(example, key, value)
        if not db.scalar(select(SyntaxExampleTranslation).where(SyntaxExampleTranslation.example_id == example.id, SyntaxExampleTranslation.locale == "my")):
            db.add(SyntaxExampleTranslation(example_id=example.id, locale="my", title=item["title"], description=item["mm"], setup="Isolated Django project တွင် run ပါ။", sample_input=item["syntax"], expected_output=item["output"], explanation="Example ကို run ပြီး actual behavior နှင့် နှိုင်းပါ။", common_mistakes="Security/database boundary မလွတ်ပါစေနှင့်။", verification_steps="Focused check/test သို့မဟုတ် SQL inspection ပြုလုပ်ပြီး result မှတ်ပါ။", status="draft"))
        lesson = lessons_by_position[item["lesson"]]
        if not db.scalar(select(LessonSyntaxReference).where(LessonSyntaxReference.lesson_id == lesson.id, LessonSyntaxReference.reference_id == ref.id)):
            db.add(LessonSyntaxReference(lesson_id=lesson.id, reference_id=ref.id, position=display_order))
    return created


def seed_django_module_five(db, course):
    """Populate only canonical Django Module 05 as reviewable draft content."""
    module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == 5))
    if not module:
        module = CourseModule(course_id=course.id, title=MODULE_TITLE, order_index=5)
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
            lesson = Lesson(module_id=module.id, title=item["title"], slug=item["slug"], description=item["description"], content_en="", content_mm="", order_index=position, duration_minutes=100, status="draft", published=False)
            db.add(lesson)
            db.flush()
            created_lessons += 1
        content_en, content_mm = _render_en(item), _render_mm(item)
        if lesson.published or lesson.status in {"published", "approved", "in_review"}:
            draft = db.scalar(select(LessonContentDraft).where(LessonContentDraft.lesson_id == lesson.id))
            if not draft:
                db.add(LessonContentDraft(lesson_id=lesson.id, base_content_version=lesson.content_version, draft_version=1, title=item["title"], slug=lesson.slug, description=item["description"], content_en=content_en, content_mm=content_mm, duration_minutes=100, status="draft", change_summary="Phase 07 Module 05 authoring"))
            elif draft.status == "draft":
                draft.title, draft.description, draft.content_en, draft.content_mm, draft.duration_minutes = item["title"], item["description"], content_en, content_mm, 100
        else:
            lesson.title = item["title"]
            lesson.description = item["description"]
            lesson.content_en = content_en
            lesson.content_mm = content_mm
            lesson.duration_minutes = 100
            lesson.status = "draft"
            lesson.published = False
            _ensure_examples(db, lesson, item)
            _ensure_quiz(db, lesson, item)
            _ensure_exercise(db, lesson, item)
        lessons_by_position[position] = lesson
    assessment_questions = _module_assessment()
    payload = [{"position": i, **question} for i, question in enumerate(assessment_questions, 1)]
    assessment = db.scalar(select(ModuleQuizDraft).where(ModuleQuizDraft.module_id == module.id))
    if not assessment:
        db.add(ModuleQuizDraft(module_id=module.id, title_en="Django Models, ORM and PostgreSQL Module Assessment", title_mm="Django Model၊ ORM နှင့် PostgreSQL Module စစ်ဆေးမှု", questions_json=json.dumps(payload, ensure_ascii=False), pass_percent=70, status="draft"))
    elif assessment.status not in {"published", "approved", "in_review"}:
        assessment.title_en = "Django Models, ORM and PostgreSQL Module Assessment"
        assessment.title_mm = "Django Model၊ ORM နှင့် PostgreSQL Module စစ်ဆေးမှု"
        assessment.questions_json = json.dumps(payload, ensure_ascii=False)
        assessment.pass_percent = 70
        assessment.status = "draft"
    project = _ensure_project(db, course, module)
    syntax_created = _ensure_syntax_references(db, course, lessons_by_position)
    db.flush()
    return {"module": module, "created_lessons": created_lessons, "lesson_count": len(LESSONS), "assessment_questions": len(assessment_questions), "project": project, "syntax_created": syntax_created}

