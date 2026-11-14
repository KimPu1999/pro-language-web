"""Idempotent authored Modern PHP curriculum.

Module 1 is the complete vertical slice. Later modules have an authored
foundation lesson so no published module is empty; deeper Laravel, WordPress,
database, and project labs remain incremental work.
"""
import json
import re
from sqlalchemy import select
from .models import CourseModule, Lesson, LessonQuiz, QuizQuestion, CodeExample

MODULES = [
    "Introduction to PHP", "PHP Environment Setup", "Your First PHP Program", "Variables & Data Types",
    "Operators & Expressions", "Conditional Statements", "Loops & Iteration", "Functions & Scope",
    "Arrays & Array Functions", "Strings & Text Processing", "Date, Time & Regular Expressions",
    "Superglobals & HTTP Requests", "HTML Forms & PHP Processing", "Sessions & Cookies", "File Handling & Uploads",
    "Error & Exception Handling", "Object-Oriented PHP", "Advanced OOP & Design Patterns", "Namespaces & Autoloading",
    "Composer & Dependency Management", "Database Fundamentals & SQL", "PHP PDO with MySQL", "PHP PDO with PostgreSQL",
    "REST API Development", "Authentication & Authorization", "Web Security & OWASP", "Testing & Debugging",
    "Modern PHP Features", "Laravel Framework Fundamentals", "Laravel Database & Eloquent", "Laravel APIs & Authentication",
    "WordPress PHP Development", "PHP Architecture & Best Practices", "Performance, Deployment & DevOps",
    "Real-World PHP Projects", "Final PHP Capstone & Assessment",
]

MODULE_ONE = [
    ("What Is PHP?", "server-side web programming and generated responses", "<?php\n$title = \"CodeMaster Academy\";\necho \"<h1>\" . htmlspecialchars($title, ENT_QUOTES, 'UTF-8') . \"</h1>\";", "PHP is a server-side language used to build dynamic web pages, APIs, command-line tools, and applications. The server executes PHP and sends a response; the browser receives HTML, CSS, JavaScript, or JSON rather than the PHP source. Modern PHP 8.x should be written with strict types, safe output handling, and clear separation between request, application, and persistence code.", "<?php\n$variable = value;\necho expression;", "PHP သည် server-side web application နှင့် API များ တည်ဆောက်ရန် အသုံးပြုသော programming language ဖြစ်သည်။"),
    ("PHP Environment Setup", "PHP 8.x, Composer, and a local development workflow", "<?php\ndeclare(strict_types=1);\necho PHP_VERSION . PHP_EOL;", "Install a supported PHP 8.x runtime and verify it from the command line. Composer manages PHP dependencies and autoloading. Keep PHP, framework, database-driver, and extension compatibility documented, and never put production secrets in a repository or sample source.", "php --version\ncomposer --version", "PHP 8.x နှင့် Composer version များကို စစ်ဆေးပြီး project compatibility ကို မှတ်တမ်းတင်ပါ။"),
    ("Your First PHP Program", "strict types, variables, and output", "<?php\ndeclare(strict_types=1);\n$name = \"CodeMaster\";\necho \"Welcome, {$name}!\" . PHP_EOL;", "A PHP file starts with a PHP tag and can declare strict types. Variables use a dollar sign, statements end with semicolons, and interpolation is useful for trusted text. In HTML output, escape untrusted values with the correct context-aware function.", "declare(strict_types=1);\n$name = \"value\";\necho $name;", "PHP file သည် PHP tag နှင့် စတင်ပြီး strict_types၊ variables နှင့် output ကို အသုံးပြုနိုင်သည်။"),
    ("Variables and Scalar Types", "string, int, float, bool, null, and explicit contracts", "<?php\ndeclare(strict_types=1);\n$count = 3;\n$label = \"items\";\n$active = true;\necho \"{$count} {$label}: \" . ($active ? \"yes\" : \"no\");", "PHP is dynamically typed at runtime, but strict types, typed parameters, return types, and properties make intent clearer. Validate external input before using it and avoid confusing numeric strings with integers in security-sensitive logic.", "function total(int $count): string { return (string) $count; }", "PHP variable များတွင် type contract များ ထည့်သွင်းပြီး external input ကို validate လုပ်ပါ။"),
    ("Operators and Expressions", "arithmetic, comparison, and predictable evaluation", "<?php\ndeclare(strict_types=1);\n$subtotal = 12.50;\n$tax = 0.05;\n$total = $subtotal * (1 + $tax);\necho number_format($total, 2);", "Use parentheses when a business rule depends on evaluation order. Prefer strict comparisons where possible, validate numeric input, and keep monetary calculations precise enough for the business requirement instead of trusting unchecked request strings.", "$total = $subtotal * (1 + $tax);\nif ($total > 0) { /* ... */ }", "Operator နှင့် expression များကို parentheses၊ validation နှင့် explicit comparison ဖြင့် ရေးသားပါ။"),
    ("Conditions and Safe Branches", "decisions, validation, and early returns", "<?php\ndeclare(strict_types=1);\n$role = \"student\";\nif ($role === \"admin\") {\n    echo \"manage\";\n} else {\n    echo \"learn\";\n}", "Conditions should make authorization and validation decisions explicit. Authentication alone does not grant permission. Use strict comparisons, guard clauses, and a default safe branch when request data is missing or unexpected.", "if ($value === expected) { /* branch */ }", "Authorization နှင့် validation decisions များကို strict comparison နှင့် safe default branch ဖြင့် ရေးသားပါ။"),
    ("Module 1 Review and Assessment", "a small strict and safely escaped PHP response", "<?php\ndeclare(strict_types=1);\n$name = \"Learner\";\n$message = htmlspecialchars(\"Hello, {$name}\", ENT_QUOTES, 'UTF-8');\necho \"<p>{$message}</p>\";", "This review combines strict types, interpolation, context-aware HTML escaping, and deterministic output. Later lessons add forms, sessions, databases, APIs, Laravel, and WordPress while preserving the same security boundaries.", "htmlspecialchars($value, ENT_QUOTES, 'UTF-8');", "Module 1 တွင် strict types၊ output escaping နှင့် safe response အခြေခံများကို ပြန်လည်လေ့လာပါမည်။"),
]

GENERAL = [
    ("Install PHP and Composer", "a reproducible PHP 8.x workspace"), ("PHP Scripts and Requests", "CLI and web entry points"),
    ("Typed Variables and Constants", "explicit PHP contracts"), ("Expression Evaluation", "safe calculations"),
    ("Branching and Validation", "trusted decisions"), ("Loops and Iteration", "bounded repetition"),
    ("Functions and Return Types", "reusable behavior"), ("Arrays and Collection Functions", "structured data"),
    ("Strings and Encoding", "safe text processing"), ("Dates and Regex", "time and pattern boundaries"),
    ("Request Superglobals", "HTTP input boundaries"), ("Forms and Escaping", "safe form processing"),
    ("Sessions and Cookie Flags", "state and browser security"), ("Safe File Uploads", "validated file handling"),
    ("Exceptions and Error Handling", "explicit failure paths"), ("Classes and Encapsulation", "object-oriented design"),
    ("Interfaces and Design Patterns", "replaceable collaborators"), ("Namespaces and Autoloading", "organized code"),
    ("Composer Dependencies", "versioned packages"), ("SQL and Data Modeling", "relational foundations"),
    ("PDO with MySQL", "prepared statements and transactions"), ("PDO with PostgreSQL", "portable persistence"),
    ("REST Resources", "HTTP contracts and status codes"), ("Authentication and Authorization", "identity and permissions"),
    ("OWASP PHP Security", "threat modeling and defenses"), ("PHP Testing", "behavioral confidence"),
    ("Modern PHP 8 Features", "attributes, enums, and readonly data"), ("Laravel Application Structure", "framework boundaries"),
    ("Eloquent and Migrations", "safe model persistence"), ("Laravel APIs and Auth", "typed service endpoints"),
    ("WordPress Plugin Boundaries", "hooks, escaping, and capabilities"), ("PHP Architecture", "maintainable application layers"),
    ("Deployment and Performance", "production operations"), ("Project Architecture", "a complete PHP application"),
    ("Final Capstone Plan", "integrating secure PHP systems"),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(title, topic, theory, syntax, code, mm, previous, next_title):
    return f"""Introduction
{title} introduces {topic} with Modern PHP 8.x.

Learning objectives
- Explain {topic} and identify the relevant request, application, or persistence boundary.
- Read and write PHP with strict types, safe output, and explicit failure handling.
- Connect the example to authentication, database, testing, and deployment concerns.

Prerequisites
{previous}

Detailed theory
{theory}

PHP syntax
{syntax}

Working code example
```php
{code}
```

Expected output
Run the example with a supported PHP 8.x CLI or within the documented local web environment. The output is deterministic for the shown input.

Line-by-line explanation
The PHP tag begins executable source. Declarations establish strict contracts and variables hold validated values. The central statement performs one focused operation; output should be escaped for its actual context. Read the first PHP diagnostic before changing other lines.

Common mistakes
- Trusting request data, file names, or database values without validation.
- Printing user data into HTML without context-aware escaping.
- Building SQL with string concatenation instead of prepared statements.
- Storing passwords, tokens, or connection strings in source code.
- Using deprecated framework or WordPress APIs without checking current guidance.

Best practices
Use strict_types, typed parameters and returns, password_hash/password_verify, prepared statements, CSRF protection, secure session flags, Composer lock files, dependency updates, tests, structured logs, and least-privilege database accounts.

Security considerations
Never execute untrusted PHP in the API process. Isolate runtime execution, disable network by default, restrict filesystem and process access, cap resources, rate-limit requests, and destroy execution environments after each run. Escape output for HTML and authorize every state-changing operation.

Practice exercises
- Easy: reproduce the example and change one validated input.
- Medium: add an error path and a focused function with a return type.
- Challenge: add a test, prepared SQL boundary, or authorization rule appropriate to the topic.
Hints: classify input as trusted or untrusted, identify its output context, and write the failure case first.
Guided solution: make the smallest valid script, run it locally, then add validation and a test.

Quiz
1. Which API should protect HTML output? htmlspecialchars with the correct context.
2. True or false: PHP configuration alone is a sufficient sandbox for arbitrary code. False.
3. Which SQL technique is recommended? Prepared statements.
4. What must authorization check? Whether the identified user may perform the operation.

Summary
You can now explain {topic}, write safer PHP 8.x, and identify the boundary that needs validation or authorization.

Next lesson
{next_title}
"""

def _questions(topic):
    return [
        (f"Which practice best supports {topic}?", ["Strict contracts and validated boundaries", "Trusting every request", "Secrets in source"], "Strict contracts and validated boundaries", "Typed contracts and validation make PHP behavior easier to review."),
        ("True or false: htmlspecialchars is useful when placing untrusted text into HTML.", ["True", "False"], "True", "Output escaping must match the destination context."),
        ("Which database approach is safest for values?", ["Prepared statements", "SQL concatenation", "Ignoring input"], "Prepared statements", "Prepared statements separate SQL instructions from values."),
        ("What should be done before running arbitrary PHP?", ["Use a strongly isolated sandbox", "Run it in FastAPI", "Disable all validation"], "Use a strongly isolated sandbox", "PHP configuration flags alone are not a sufficient security boundary."),
    ]

def seed_php_course(db, course):
    course.title = "PHP Programming — From Zero to Advanced"
    course.short_description = "A free Modern PHP 8.x course covering web requests, security, PDO, REST APIs, Composer, Laravel, WordPress, testing, and real projects."
    course.description = "Learn PHP from first principles through secure forms, sessions, files, OOP, Composer, SQL, PDO, REST APIs, authentication, Laravel, WordPress, deployment, and a final capstone."
    course.level, course.status, course.published = "advanced", "published", True
    course.outcomes = "Write modern typed PHP|Build secure forms and APIs|Use PDO with MySQL and PostgreSQL|Apply Composer, Laravel, and WordPress practices|Test, deploy, and operate PHP applications safely"
    course.requirements = "Basic HTML and CSS; JavaScript is helpful. HTML and CSS courses are recommended. Examples target supported PHP 8.x and document Composer, database, Laravel, and WordPress compatibility per project."
    authored = []
    for module_index, module_title in enumerate(MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_index))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_index); db.add(module); db.flush()
        module.title = module_title
        if module_index == 1:
            specs = [{"title": a, "topic": b, "code": c, "theory": d, "syntax": e, "mm": f} for a, b, c, d, e, f in MODULE_ONE]
        else:
            title, topic = GENERAL[module_index - 2]
            code = f"<?php\ndeclare(strict_types=1);\n$status = \"{_slug(title)} ready\";\necho $status . PHP_EOL;"
            specs = [{"title": title, "topic": topic, "code": code, "theory": f"This foundation lesson explains {topic}. Apply the concept to a small PHP feature, then test invalid input, safe output, and the relevant failure path.", "syntax": "declare(strict_types=1);\nfunction name(Type $value): ReturnType { }", "mm": f"ဤ lesson တွင် {topic} ကို Modern PHP 8.x ဖြင့် လေ့လာပါမည်။"}]
        for lesson_index, spec in enumerate(specs, 1):
            title, topic = spec["title"], spec["topic"]
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm=""); db.add(lesson); db.flush()
            previous = "Basic HTML and CSS; JavaScript is helpful. HTML and CSS courses are recommended." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
            next_title = "Continue to the next lesson." if module_index < 36 else "Continue to the final capstone review."
            lesson.title, lesson.slug = title, slug
            lesson.content_en = _content(title, topic, spec["theory"], spec["syntax"], spec["code"], spec["mm"], previous, next_title)
            lesson.content_mm = f"{title} ကို English theory နှင့်အတူ လေ့လာနိုင်ပါသည်။\n\n{spec['mm']}"
            lesson.description, lesson.duration_minutes = spec["theory"], 35
            lesson.status, lesson.published = "published", True; authored.append(lesson)
            examples = list(db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all())
            example = examples[0] if examples else None
            for duplicate in examples[1:]: db.delete(duplicate)
            if not example:
                db.add(CodeExample(lesson_id=lesson.id, title=f"{title} example", language="php", filename="index.php", code=spec["code"], description="Read-only PHP example. Use a local PHP 8.x environment; hosted arbitrary execution is disabled.", position=1))
            else:
                example.title, example.language, example.filename, example.code, example.description, example.position = f"{title} example", "php", "index.php", spec["code"], "Read-only PHP example. Use a local PHP 8.x environment; hosted arbitrary execution is disabled.", 1
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz: quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the PHP and security explanation, then retry missed concepts.", status="published"); db.add(quiz); db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(topic), 1):
                values = dict(prompt=prompt, question_type="true_false" if options == ["True", "False"] else "multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                question = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
                if not question: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(question, key, value)
    course.duration_minutes = sum(x.duration_minutes or 35 for x in authored)
    db.flush()
