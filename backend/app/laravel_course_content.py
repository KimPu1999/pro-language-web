"""Authored Laravel vertical slice for the idempotent catalog seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

PLANNED_MODULES = [
    "Introduction to Laravel", "Modern PHP Fundamentals", "Composer & PHP Environment", "Laravel Installation & Setup",
    "Laravel Project Structure", "Laravel MVC Architecture", "Routing Fundamentals", "Controllers & Request Handling",
    "Blade Template Engine", "Middleware & Request Lifecycle", "Forms & Validation", "Sessions, Cookies & CSRF",
    "Database Fundamentals", "Migrations, Seeders & Factories", "Eloquent ORM Fundamentals", "Eloquent Relationships",
    "Advanced Eloquent", "Authentication Fundamentals", "Authorization & Policies", "REST API Development",
    "Laravel Sanctum", "File Uploads & Storage", "Blade Components & Livewire", "Inertia.js & React Integration",
    "Email & Notifications", "Events & Listeners", "Queues & Background Jobs", "Task Scheduling", "Redis & Caching",
    "Broadcasting & Real-Time Features", "Laravel Testing Fundamentals", "Advanced API & Database Testing",
    "Laravel Security Best Practices", "Performance Optimization", "Application Architecture & Patterns",
    "Multi-Tenant SaaS Development", "Docker & Laravel Development", "CI/CD, Deployment & Monitoring",
    "Professional Laravel Projects", "Final Laravel Capstone",
]

MODULE_ONE = [
    ("What Laravel Provides", "MVC architecture, conventions, and productive web development", "php -v\ncomposer --version\nphp artisan --version", "terminal", "Laravel is a PHP framework that provides conventions and components for routing, controllers, views, validation, database access, queues, authentication, and testing. Framework automation is helpful only when its boundaries and configuration are understood.", "Laravel သည် routing၊ controller၊ view၊ validation၊ database၊ queue၊ authentication နှင့် testing အတွက် convention များကို ပေးသော PHP framework ဖြစ်သည်။", "Draw the boundary between PHP, Laravel, and the database in a request.", ("Laravel သည် ဘာကို ပေးသနည်း?", ["Conventions and components for web applications", "A replacement for PostgreSQL", "A secret storage vault"], "Conventions and components for web applications", "Laravel provides application structure and framework components.")),
    ("Modern PHP Foundations", "types, functions, arrays, and secure input boundaries", "php -v\nphp -r 'echo strtoupper(\"php\");'", "terminal", "Laravel applications are PHP programs. Understand variables, functions, arrays, classes, namespaces, exceptions, and strict input handling before relying on framework helpers. External request data is untrusted and must be validated.", "Laravel application သည် PHP program ဖြစ်သောကြောင့် variable၊ function၊ array၊ class၊ namespace နှင့် exception အခြေခံများကို နားလည်ရမည်။ Request data ကို validate လုပ်ရသည်။", "Identify which values in a fictional request must be validated before use.", ("Request input ကို ဘယ်လို ကိုင်တွယ်သင့်သနည်း?", ["Validate it at the application boundary", "Trust all browser values", "Put it in a secret file"], "Validate it at the application boundary", "Browser input is untrusted.")),
    ("Composer and Project Dependencies", "Composer packages, lockfiles, and reproducible installs", "composer create-project laravel/laravel example-app\ncd example-app\ncomposer install\nphp artisan about", "terminal", "Composer installs PHP dependencies and composer.lock records resolved versions. Use trusted packages, review updates, and keep secrets in environment configuration rather than committed files. The Academy examples do not install packages on its host.", "Composer သည် PHP dependency များကို install လုပ်ပြီး lockfile က resolved version များကို မှတ်တမ်းတင်သည်။ Trusted package နှင့် environment configuration ကို သုံးပါ။", "Explain why composer.lock should be reviewed and why .env should not be committed.", ("Dependency reproducibility အတွက် ဘာကို အသုံးပြုသနည်း?", ["composer.lock", "A random download URL", "A committed password"], "composer.lock", "The lockfile records resolved dependency versions.")),
    ("Create and Configure a Laravel App", "application keys, environment configuration, and safe setup", "composer create-project laravel/laravel example-app\ncd example-app\ncp .env.example .env\nphp artisan key:generate\nphp artisan serve", "terminal", "A Laravel project separates source, configuration, routes, views, and storage. APP_KEY and database settings belong in protected environment configuration. Never publish real credentials or production .env files.", "Laravel project သည် source၊ configuration၊ route၊ view နှင့် storage ကို ခွဲထားသည်။ APP_KEY နှင့် database setting ကို protected environment configuration ထဲထားရသည်။", "Create a setup checklist that distinguishes local .env values from committed example configuration.", ("Real credential ကို ဘယ်မှာ မထားသင့်သနည်း?", ["Committed source or public logs", "A protected secret manager", "A local protected environment"], "Committed source or public logs", "Credentials in source or logs can be exposed.")),
    ("Laravel Project Structure", "routes, app code, resources, database, and storage", "php artisan route:list\nphp artisan config:show app\nphp artisan about", "terminal", "The app directory contains application code, routes define entry points, resources hold views and frontend assets, database holds migrations and seeders, and storage holds runtime files. Learn the structure before adding behavior so responsibilities remain clear.", "app သည် application code၊ routes သည် entry point၊ resources သည် view/assets၊ database သည် migration/seeder နှင့် storage သည် runtime file များကို ထားသည်။", "Map a request from routes/web.php to a controller and Blade view.", ("Migration များကို ဘယ် folder တွင် ထားသနည်း?", ["database/migrations", "public/passwords", "storage/tokens"], "database/migrations", "Laravel convention keeps migration files in database/migrations.")),
    ("MVC Request Lifecycle", "routes, controllers, models, views, and responses", "php artisan route:list\n# Route -> controller -> model/service -> view or JSON response", "terminal", "Laravel MVC separates request matching, application behavior, persistence, and presentation. A controller should coordinate rather than contain every rule. Use policies, validation, services, and resources when the feature grows.", "Laravel MVC သည် request matching၊ business behavior၊ persistence နှင့် presentation ကို ခွဲထားသည်။ Controller ထဲတွင် rule အားလုံး မထည့်ဘဲ validation/policy/service ကို သုံးပါ။", "Trace a profile update from route to controller, validation, model, and response.", ("MVC တွင် controller ၏ တာဝန်က ဘာလဲ?", ["Coordinate request handling and application behavior", "Store every secret", "Replace the database"], "Coordinate request handling and application behavior", "Controllers coordinate the request rather than replacing every layer.")),
    ("Routes, Controllers, and Validation", "safe request handling and explicit route boundaries", "php artisan make:controller ProfileController\nphp artisan route:list\nphp artisan make:request UpdateProfileRequest", "terminal", "Routes should be explicit and protected where needed. Controllers receive validated requests and return a view, redirect, or JSON resource. Use route model binding carefully and authorize access before exposing or changing a record.", "Route သည် explicit ဖြစ်ပြီး လိုအပ်ပါက protected ဖြစ်ရမည်။ Controller သည် validated request ကို လက်ခံပြီး view/redirect/JSON ပြန်သည်။", "Design a protected update route with a form request and ownership policy.", ("Record update မလုပ်မီ ဘာကို စစ်သင့်သနည်း?", ["Validation and authorization", "Only a hidden browser field", "A client-supplied user id"], "Validation and authorization", "Both input validity and ownership must be enforced server-side.")),
    ("Blade Views and the First Tested Workflow", "templates, escaping, tests, and review", "php artisan make:view profile\nphp artisan test\nphp artisan route:list\nphp artisan config:clear", "terminal", "Blade provides escaped output, layouts, components, and control structures for server-rendered UI. A professional workflow creates a focused feature, validates input, tests it, inspects configuration, and reviews secrets before commit.", "Blade သည် escaped output၊ layout နှင့် component များကို ပေးသည်။ Feature တစ်ခုကို test၊ config review နှင့် secret review ပြုလုပ်ပြီးမှ commit လုပ်ပါ။", "Create a checklist for a profile page: route, validation, authorization, escaped view, feature test, and review.", ("Blade output အတွက် ဘာကို ဦးစားပေးသင့်သနည်း?", ["Escaped output and validated data", "Raw untrusted HTML everywhere", "Credentials in templates"], "Escaped output and validated data", "Escaping and validation reduce injection and data-handling risk.")),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(position: int, item: tuple) -> str:
    title, topic, commands, filename, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    previous = "No Laravel experience is required; basic PHP is helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: complete the first Laravel application lab and review the Module 1 assessment."
    return f"""Introduction
{title} introduces {topic} through a safe Laravel workflow.

Learning objectives
- Explain {topic} in your own words.
- Trace a request through Laravel's layers.
- Identify validation, authorization, configuration, and secret boundaries.

Prerequisites
{previous}

Laravel architecture explanation
HTTP request -> route -> middleware -> controller/service -> model/database -> Blade or JSON response

Detailed theory
{theory}

Step-by-step PHP and Artisan examples
{commands}

File paths and folder structure
project/
  app/
  routes/web.php
  resources/views/
  database/migrations/
  tests/
  .env

Expected output
Exact output depends on the Laravel/PHP versions and local configuration. Verify the state with the relevant Artisan command instead of copying unverified output.

Code explanation
Read each route, class, command, and configuration boundary. Keep examples in a disposable project and distinguish local settings from committed source.

Common errors
- Using incompatible PHP, Composer, or Laravel versions.
- Trusting request fields without validation or authorization.
- Committing .env, APP_KEY, or database credentials.
- Putting business rules and queries into a single controller.

Troubleshooting
Check php -v, composer diagnose, php artisan about, route:list, configuration cache, and the first application error. Preserve error context before changing multiple files.

Best practices
- Validate at request boundaries, authorize resource ownership, and use escaped Blade output.
- Keep controllers focused and test the behavior you publish.
- Use parameterized Eloquent/query-builder operations and review dependencies.

Security considerations
Do not expose APP_KEY, passwords, tokens, private uploads, or debug details. Protect CSRF, sessions, policies, file validation, and tenant boundaries server-side.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Create a disposable Laravel profile feature with a route, validated request, authorization check, escaped Blade view, and feature test. Use placeholder data only.

Summary
You can now reason about {topic} as a sequence of protected Laravel request and response boundaries.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
The Academy displays PHP/Laravel examples and does not execute untrusted code on its application host.
"""

def seed_laravel_course(db, course):
    course.title = "Laravel & PHP Full-Stack Development — From Zero to Professional"
    course.short_description = "A free, practical path from PHP and Laravel fundamentals to secure APIs, database applications, and deployment."
    course.description = "Learn PHP, Composer, Laravel MVC, routing, Blade, validation, Eloquent, authentication, APIs, queues, caching, testing, security, Docker, and professional full-stack workflows through safe examples."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 35
    course.outcomes = "Build structured Laravel applications with routing, controllers, Blade, validation, and Eloquent|Create secure APIs with authentication, authorization, and resource ownership|Use migrations, queues, caching, testing, and deployment practices|Apply Laravel security, dependency, file, session, and tenant-isolation principles"
    course.requirements = "A text editor and basic command-line familiarity; no previous Laravel experience is required."
    module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == 1))
    if not module:
        module = CourseModule(course_id=course.id, title=PLANNED_MODULES[0], order_index=1)
        db.add(module)
        db.flush()
    module.title = PLANNED_MODULES[0]
    for position, item in enumerate(MODULE_ONE, 1):
        title = item[0]
        slug = f"01-{_slug(title)}"
        lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == position))
        if not lesson:
            lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=position, content_en="", content_mm="")
            db.add(lesson)
            db.flush()
        lesson.title, lesson.slug = title, slug
        lesson.description = item[1]
        lesson.content_en = _content(position, item)
        lesson.content_mm = f"{title}\n\n{item[5]}\n\nလေ့ကျင့်ခန်း\n{item[6]}"
        lesson.duration_minutes, lesson.status, lesson.published = 35, "published", True
        example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        values = {"title": f"{title} example", "language": "php" if item[3] == "php" else "bash", "filename": item[3], "code": item[2], "description": "Read-only PHP/Laravel example. Run locally in an isolated workspace; the Academy does not execute code on its host.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the Laravel request boundary and security boundary before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [(item[7][0], item[7][1], item[7][2], item[7][3]), ("True or false: the Academy executes arbitrary PHP or Laravel code on its application host.", ["True", "False"], "False", "Examples are displayed as read-only learning content."), ("Which practice protects a Laravel application?", ["Validate input, authorize access, escape output, and keep secrets out of source", "Trust hidden form fields", "Commit .env and APP_KEY"], "Validate input, authorize access, escape output, and keep secrets out of source", "Server-side validation, authorization, output escaping, and secret hygiene reduce risk.")]
        for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
            row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
            values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
            if not row:
                db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
            else:
                for key, value in values.items():
                    setattr(row, key, value)
    db.flush()
