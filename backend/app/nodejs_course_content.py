"""Idempotent Node.js Backend Development vertical-slice seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion
from .nodejs_complete_curriculum import _ensure_exercise, seed_nodejs_additional_curriculum


PLANNED_MODULES = [
    "Introduction to Node.js", "JavaScript Fundamentals Review", "Modern JavaScript (ES Modules)",
    "Node.js Installation & Setup", "Node.js Runtime Architecture", "npm & Package Management",
    "CommonJS & ES Modules", "Node.js Core APIs", "Asynchronous JavaScript", "Event Loop Fundamentals",
    "Timers & Events", "File System (fs)", "Buffers & Streams", "Error Handling & Debugging",
    "HTTP Fundamentals", "Building HTTP Servers", "Express.js Fundamentals", "REST API Design",
    "Express Routing & Middleware", "Request Validation & Errors", "PostgreSQL Integration",
    "MongoDB Integration", "Authentication Fundamentals", "JWT & Refresh Tokens", "Authorization & RBAC",
    "File Uploads & Storage", "API Documentation & OpenAPI", "TypeScript with Node.js",
    "Testing Node.js Applications", "Redis & Caching", "WebSockets & Real-Time APIs",
    "Queues & Background Jobs", "Node.js Security Best Practices", "Performance & Scalability",
    "Logging & Monitoring", "Backend Architecture & Design Patterns", "Microservices & Messaging",
    "Docker, CI/CD & Deployment", "Professional Node.js Projects", "Final Node.js Capstone & Assessment",
]

MODULE_ONE = [
    ("What Node.js Is", "the JavaScript runtime, server-side programs, and backend boundaries",
     "node --version\nnpm --version", "bash",
     "Node.js is a JavaScript runtime built around V8 and an event-driven I/O model. It lets a backend use JavaScript outside the browser, but it does not remove the need for authentication, validation, safe configuration, or database authorization.",
     "Node.js သည် browser အပြင် JavaScript ကို run နိုင်စေသော runtime ဖြစ်ပြီး event-driven I/O model ကိုအသုံးပြုသည်။ Authentication၊ validation နှင့် authorization တို့ကို မဖယ်ရှားပေးပါ။",
     "Draw a browser -> Node.js API -> database boundary and label which values are server-only.",
     ("Node.js သည် ဘာလဲ?", ["JavaScript runtime", "Database engine only", "CSS framework"], "JavaScript runtime", "Node.js runs JavaScript programs outside the browser.")),
    ("V8 and the Node.js Runtime", "V8 execution, the call stack, native bindings, and the event loop",
     "node -p \"process.versions.v8\"\nnode -p \"process.platform\"", "bash",
     "V8 executes JavaScript while Node.js adds APIs for files, networking, processes, and streams. The event loop coordinates callbacks and I/O; CPU-heavy synchronous work can still block other requests.",
     "V8 သည် JavaScript ကို execute လုပ်ပြီး Node.js က file၊ network၊ process နှင့် stream APIs များထပ်ပေးသည်။ CPU-heavy synchronous code သည် request များကို block လုပ်နိုင်သည်။",
     "Explain why a long synchronous loop can delay unrelated HTTP responses.",
     ("Node.js application တွင် JavaScript ကို ဘယ် engine က execute လုပ်သနည်း?", ["V8", "PostgreSQL", "Nginx"], "V8", "V8 is the JavaScript engine used by Node.js.")),
    ("Installing Node.js Safely", "supported versions, version managers, and reproducible project setup",
     "node --version\nnpm init -y", "bash",
     "Use a supported LTS release and pin project dependencies through package.json and a lockfile. Verify the runtime before installing packages, and never commit secrets or local credential files.",
     "Supported LTS version ကိုအသုံးပြုပြီး package.json နှင့် lockfile ဖြင့် dependency version များကို ထိန်းပါ။ Secret များကို repository ထဲမထည့်ပါနှင့်။",
     "Create a disposable folder, initialize package.json, and record the Node version used by the project.",
     ("Dependency versions ကို ဘယ်လို reproducible လုပ်မလဲ?", ["package.json နှင့် lockfile သုံးခြင်း", "README ဖျက်ခြင်း", "Client password ထည့်ခြင်း"], "package.json နှင့် lockfile သုံးခြင်း", "A lockfile records the resolved dependency graph.")),
    ("npm and package.json", "scripts, dependencies, devDependencies, and package lifecycle",
     "npm init -y\nnpm install express\nnpm run start", "bash",
     "package.json describes a Node project. Runtime packages belong in dependencies, tooling in devDependencies, and scripts should be explicit and reviewable. npm install changes the lockfile; review changes before committing.",
     "package.json သည် project metadata၊ scripts နှင့် dependencies ကိုဖော်ပြသည်။ Runtime package ကို dependencies နှင့် tooling ကို devDependencies ထဲထားပါ။",
     "Add start and test scripts to a small API package without adding credentials or arbitrary install hooks.",
     ("Express ကို runtime တွင်အသုံးပြုပါက ဘယ် field ထဲထည့်သင့်သနည်း?", ["dependencies", "devDependencies only", "comments"], "dependencies", "Runtime imports belong in dependencies.")),
    ("CommonJS and ES Modules", "require, import, exports, module boundaries, and interoperability",
     "import { readFile } from 'node:fs/promises';\nexport const health = { ok: true };", "js",
     "Node supports CommonJS and ES Modules. Choose one convention per project, configure it explicitly, and avoid mixing module assumptions without understanding package type and import behavior.",
     "CommonJS နှင့် ES Modules နှစ်မျိုးလုံးရှိသည်။ Project တစ်ခုတွင် convention တစ်ခုကို ရှင်းလင်းစွာ configure လုပ်ပါ။",
     "Convert a small utility from module.exports to named ES module exports and document the package type.",
     ("ES Module named export ကို import လုပ်ရာတွင် ဘာသုံးသနည်း?", ["import { name } from 'module'", "SELECT name", "CSS @use only"], "import { name } from 'module'", "Named exports are imported with an import binding.")),
    ("Node.js Core APIs", "node:fs, node:path, process, URL, and safe standard-library usage",
     "import path from 'node:path';\nconst file = path.join(process.cwd(), 'data', 'items.json');\nconsole.log(file);", "js",
     "Core APIs are available without third-party packages. Prefer platform-aware path utilities, explicit encodings, and asynchronous APIs for I/O. Validate paths and never let user input select arbitrary server files.",
     "Core API များကို package မထည့်ဘဲ သုံးနိုင်သည်။ Path ကို utility ဖြင့်တည်ဆောက်ပြီး user input ဖြင့် arbitrary server file မဖတ်ပါနှင့်။",
     "Build a safe path for a known uploads directory and reject traversal-like input before any I/O.",
     ("Path ကို platform-independent တည်ဆောက်ရန် ဘာသုံးသင့်သနည်း?", ["node:path", "String concatenation only", "SQL only"], "node:path", "node:path handles platform path rules.")),
    ("Async JavaScript and Promises", "callbacks, promises, async/await, and error propagation",
     "const result = await Promise.resolve({ ok: true });\nconsole.log(result);", "js",
     "Promises represent eventual completion. async/await improves readability, but errors still need explicit handling. Use Promise.all for independent operations and avoid unbounded concurrency against databases or APIs.",
     "Promise သည် နောက်ပိုင်းတွင်ပြီးဆုံးမည့် operation ကိုကိုယ်စားပြုသည်။ async/await သုံးသော်လည်း error handling လိုအပ်ပြီး concurrency ကိုကန့်သတ်ပါ။",
     "Write a function that loads two independent records with Promise.all and returns a typed error result.",
     ("Async function error ကို ဘယ်လို handle လုပ်သင့်သနည်း?", ["try/catch or a deliberate rejection boundary", "Ignore it", "Expose stack traces to users"], "try/catch or a deliberate rejection boundary", "Async failures must be handled at a deliberate boundary.")),
    ("Your First HTTP API Workflow", "request parsing, routing, response status, and safe API design",
     "import { createServer } from 'node:http';\ncreateServer((_req, res) => { res.writeHead(200, { 'content-type': 'application/json' }); res.end(JSON.stringify({ ok: true })); }).listen(3000);", "js",
     "An HTTP API receives a request, validates method/path/input, performs authorized work, and returns a status plus representation. Keep the example local and deterministic; the Academy simulator never executes arbitrary student code or opens a remote proxy.",
     "HTTP API သည် request ကိုလက်ခံ၊ method/path/input validate လုပ်၊ authorize လုပ်ပြီး status နှင့် response ပြန်ပေးသည်။",
     "Design GET /health and GET /courses endpoints with explicit status codes and an error response shape.",
     ("API response တွင် ဘာပါဝင်သင့်သနည်း?", ["Status code and validated representation", "Only a password", "An unbounded stack trace"], "Status code and validated representation", "Clients need a safe status and predictable response shape.")),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, commands, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "Basic JavaScript is helpful; no Node.js experience is required." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the Event Loop visualizer and complete the first API lab."
    return f"""Introduction
{title} introduces {topic} in a safe Node.js backend workflow.

Learning objectives
- Explain {topic} and its place in an API service.
- Select explicit runtime, module, async, and HTTP boundaries.
- Validate input, handle errors, and keep secrets server-side.

Prerequisites
{prerequisite}

Node.js architecture explanation
browser -> HTTP server -> route/service boundary -> database or external API -> response

Detailed theory
{theory}

JavaScript/TypeScript example ({language})
{commands}

Expected terminal/API output
The exact version and port may differ locally. Verify the documented response and inspect errors without exposing secrets.

Step-by-step implementation
1. Define the request and response contract.
2. Keep asynchronous work explicit and bounded.
3. Validate external input before filesystem, database, or network work.
4. Return safe errors and log server-side diagnostic context.
5. Add an automated test and verify authorization for protected data.

Architecture diagram
client -> Node.js runtime -> router -> service -> repository -> PostgreSQL/MongoDB

Common errors
- Blocking the event loop with long synchronous work.
- Mixing CommonJS and ES Module assumptions.
- Forgetting to await a promise or handle rejection.
- Trusting a client-supplied user ID or path.

Troubleshooting
Check the Node version, package type, lockfile, import path, port ownership, response status, server logs, and smallest reproducible example. Never paste credentials into logs or client code.

Best practices
- Prefer supported LTS releases, lockfiles, structured errors, validation, least privilege, and bounded concurrency.
- Keep configuration server-only and make health checks deterministic.
- Use semantic HTTP statuses, accessible documentation, tests, and observable request IDs.

Security considerations
Examples and playground output are predefined or simulated. The Academy does not execute arbitrary Node.js, JavaScript, or shell code, access host files, or provide an unrestricted URL proxy. Never commit tokens or database credentials.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Create a local, disposable health-and-courses API plan with an explicit route table, validation rules, safe error shape, and tests. Run commands only on your own machine.

Summary
You can now reason about {topic} using runtime, async, HTTP, data, and security boundaries.

Next lesson
{next_lesson}

Myanmar explanation
{mm}
"""


def _repair_module_one_sections(lesson, item: tuple) -> None:
    """Append review sections without replacing existing Module 1 content."""
    theory, code, mm, exercise = item[4], item[2], item[5], item[6]
    if "## Detailed theory" not in (lesson.content_en or ""):
        lesson.content_en = (lesson.content_en or "") + f"""

## Detailed theory
{theory}

## Core concepts
Runtime behavior, explicit contracts, validation, authorization, observability, and recovery are the core concepts for this lesson.

## Syntax and usage
```javascript
{code}
```

## Expected output
Inspect the response, order, status, or runtime result and verify it against the contract. Timing can vary by environment.

## Line-by-line explanation
Read imports and declarations first, trace the input through the Node.js boundary, and compare the result with the expectation. Change one value at a time.

## Common mistakes
- Forgetting to await promises or trusting client-controlled values.
- Leaking secrets, stack traces, SQL, or personal data.
- Blocking the event loop or retrying non-idempotent operations blindly.

## Best practices
- Use LTS versions, lockfiles, schemas, parameterized queries, least privilege, tests, request IDs, and health checks.
- Define timeouts, rate limits, redaction, monitoring, and rollback criteria.

## Practical exercises
{exercise}

## Homework
Write an implementation note with runtime versions, contract, observed behavior, test evidence, security boundary, and recovery plan.

## Related references
- Node.js documentation: https://nodejs.org/docs/latest/api/
- Express documentation: https://expressjs.com/
- OWASP API Security: https://owasp.org/www-project-api-security/

## Key takeaways
Reliable Node.js services make contracts, failures, permissions, tests, and observability visible.
"""
    if "## အသေးစိတ်သီအိုရီ" not in (lesson.content_mm or ""):
        lesson.content_mm = (lesson.content_mm or "") + f"""

## အသေးစိတ်သီအိုရီ
{mm}

## လက်တွေ့လေ့ကျင့်ခန်း
{exercise}

## အိမ်စာ
Runtime version၊ contract၊ observed behavior၊ test evidence၊ security boundary နှင့် recovery plan ကို မှတ်တမ်းတင်ပါ။

## ဆက်စပ်ရည်ညွှန်းချက်
Node.js၊ Express နှင့် OWASP API Security documentation ကို project version နှင့် ကိုက်ညီအောင် ဖတ်ပါ။
"""


def seed_nodejs_course(db, course):
    course.title = "Node.js Backend Development — From Zero to Professional"
    course.short_description = "A free, practical path through Node.js runtime architecture, APIs, databases, authentication, testing, security, and deployment."
    course.description = "Learn Node.js, npm, modules, core APIs, async JavaScript, the event loop, HTTP, Express, REST APIs, PostgreSQL, MongoDB, authentication, TypeScript, testing, caching, WebSockets, performance, security, and deployment."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 45
    course.outcomes = "Explain the Node.js runtime, V8, asynchronous I/O, modules, and the event loop|Build validated HTTP and Express APIs with safe error handling|Integrate databases, authentication, testing, caching, WebSockets, and TypeScript|Prepare secure, observable, scalable services for deployment"
    course.requirements = "Basic JavaScript and command-line familiarity are helpful; no Node.js experience is required."
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
        if not lesson.content_en or not lesson.content_en.strip():
            lesson.title, lesson.slug = title, slug
            lesson.description = item[1]
            lesson.content_en = _content(position, item)
            lesson.content_mm = f"{title}\n\n{item[5]}\n\nလေ့ကျင့်ခန်း\n{item[6]}"
            lesson.duration_minutes, lesson.status, lesson.published = 45, "published", True
        _repair_module_one_sections(lesson, item)
        example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        values = {"title": f"{title} example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe Node.js example for local study; the Academy does not execute arbitrary code.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the runtime boundary, async behavior, validation, and security notes before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: the Academy executes arbitrary student Node.js code on the production host.", ["True", "False"], "False", "The playground is predefined and simulated."),
            ("Which boundary protects a private database credential?", ["Server-only configuration and server-side authorization", "A hidden client button", "A URL query parameter"], "Server-only configuration and server-side authorization", "Credentials and authorization must remain on the server."),
        ]
        for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
            row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
            values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
            if not row:
                db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
            else:
                for key, value in values.items():
                    setattr(row, key, value)
        _ensure_exercise(db, lesson, title, item[6], f"{item[5]} ကို isolated Node.js project ထဲတွင် လက်တွေ့လေ့ကျင့်ပါ။")
    db.flush()
    additional_report = seed_nodejs_additional_curriculum(db, course)
    course.duration_minutes = sum(
        lesson.duration_minutes or 45
        for module in db.scalars(select(CourseModule).where(CourseModule.course_id == course.id)).all()
        for lesson in db.scalars(select(Lesson).where(Lesson.module_id == module.id)).all()
    )
    db.flush()
    return additional_report
