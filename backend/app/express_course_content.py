"""Authored Express.js vertical slice for the catalog seed.

Only lessons with reviewed content are published. The complete 40-module plan
is retained for incremental authoring without presenting empty lessons.
"""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion


PLANNED_MODULES = [
    "Introduction to Express.js", "JavaScript for Backend Development", "Node.js Fundamentals", "HTTP & Web Fundamentals",
    "Express.js Installation & Setup", "Express Application Structure", "Routing Fundamentals", "Request & Response Objects",
    "Middleware Fundamentals", "Advanced Middleware", "Express Router", "REST API Design", "CRUD API Development",
    "Input Validation", "Error Handling & Logging", "PostgreSQL Fundamentals", "Express.js with PostgreSQL", "ORM & Query Builders",
    "Authentication Fundamentals", "Sessions, Cookies & JWT", "Authorization & RBAC", "Express.js Security", "File Uploads & Storage",
    "Email & Notifications", "TypeScript with Express.js", "Advanced API Features", "API Documentation", "Testing Express.js APIs",
    "Redis & Caching", "Background Jobs & Queues", "WebSockets & Real-Time APIs", "Performance Optimization", "API Architecture & Design Patterns",
    "Dockerizing Express.js", "CI/CD for Express.js", "Production Deployment", "Monitoring & Observability", "Multi-Tenant SaaS Backend",
    "Professional Express.js Projects", "Final Express.js Capstone",
]

MODULE_ONE = [
    ("What Express.js Is and Why It Exists", "minimal routing and middleware on top of Node.js", "import express from 'express';\n\nconst app = express();\napp.get('/', (_request, response) => {\n  response.send('Hello from Express');\n});\n\napp.listen(3000, () => console.log('API listening on 3000'));", "src/server.js", "Express.js is a focused Node.js web framework. It provides routing, middleware composition, and response helpers while leaving application architecture, validation, persistence, and security decisions to the team. That flexibility is useful when boundaries are explicit: keep transport code thin, place business rules in services, and validate all untrusted input.", "Express.js သည် Node.js ပေါ်တွင် routing နှင့် middleware ကို ရိုးရှင်းစွာ တည်ဆောက်နိုင်ရန် အသုံးပြုသော web framework ဖြစ်သည်။ Flexibility ရှိသော်လည်း validation၊ database၊ authorization နှင့် security boundary များကို developer က ရှင်းလင်းစွာ စီမံရမည်။", "Write a one-paragraph comparison between Express middleware and a normal JavaScript function. Identify what the request and response objects represent.", ("Express.js အဓိကပေးသည့်အရာက ဘာလဲ?", ["Routing and middleware composition", "A PostgreSQL server", "A browser UI builder"], "Routing and middleware composition", "Express focuses on request handling and composition around Node.js."), "Use a local server only; never place credentials in this example."),
    ("Node.js Backend Fundamentals", "the runtime, modules, npm scripts, and asynchronous I/O", "import { readFile } from 'node:fs/promises';\n\nconst packageText = await readFile('package.json', 'utf8');\nconsole.log(JSON.parse(packageText).name);", "src/inspect-package.mjs", "Node.js runs JavaScript outside the browser and exposes APIs for files, networking, processes, and streams. npm manages dependencies and scripts, while package.json describes the project boundary. Async I/O keeps the event loop responsive, but CPU-heavy work can still block it and needs a separate strategy.", "Node.js သည် browser အပြင် JavaScript run ရန် runtime ဖြစ်သည်။ npm နှင့် package.json က dependencies နှင့် scripts ကို စီမံပေးသည်။ Async I/O သည် event loop ကို responsive ဖြစ်စေသော်လည်း CPU-heavy အလုပ်များကို သီးခြားစီမံရန် လိုအပ်သည်။", "Create a package.json with type: module, add a start script, and explain the difference between a dependency and a devDependency.", ("Node.js တွင် I/O ကို မည်သို့စီမံသင့်သနည်း?", ["Async APIs ဖြင့် မပိတ်ဆို့အောင် စီမံခြင်း", "Every request တွင် sync loop သုံးခြင်း", "Credentials ကို global variable ထားခြင်း"], "Async APIs ဖြင့် မပိတ်ဆို့အောင် စီမံခြင်း", "Asynchronous APIs help the event loop serve other work while I/O waits."), "Do not read arbitrary paths from a client-supplied request without authorization."),
    ("HTTP Request and Response Fundamentals", "methods, status codes, headers, and JSON bodies", "import express from 'express';\nconst app = express();\napp.use(express.json());\napp.post('/users', (request, response) => {\n  response.status(201).json({ received: request.body });\n});", "src/http-server.js", "HTTP is a contract between a client and a server. Methods communicate intent, status codes communicate outcome, headers carry metadata, and a JSON body carries structured data. A backend should make status codes predictable and avoid returning internal exception details to clients.", "HTTP တွင် method၊ status code၊ headers နှင့် JSON body တို့က client/server contract ဖြစ်သည်။ Status code ကို predictable ဖြစ်အောင် သုံးပြီး internal error detail များကို client သို့ မဖော်ပြသင့်ပါ။", "Use a local API client to send one valid JSON POST and one malformed body. Record the expected 201 and validation error behavior.", ("Resource အသစ်ဖန်တီးပြီးသည့်အခါ သင့်တော်သော status code က ဘာလဲ?", ["201 Created", "301 Moved Permanently", "204 only always"], "201 Created", "201 communicates that a resource was created."), "Never log authorization headers or passwords in request logs."),
    ("Install Express and Create a Project", "dependency isolation and a maintainable project start", "mkdir express-learning && cd express-learning\nnpm init -y\nnpm install express\nnpm install --save-dev nodemon\nnode --version\nnpm list express", "terminal", "Use a supported Node.js LTS release and keep dependencies local to the project. A package lock records resolved versions for repeatable installs. Start with a small src directory and a test directory rather than allowing server.js to become an unstructured feature dump.", "Node.js LTS version ကို သုံးပြီး dependency များကို project local တွင်ထားပါ။ package-lock.json သည် resolved version များကို မှတ်တမ်းတင်ပြီး repeatable install အတွက် အထောက်အကူပြုသည်။", "Create the project, add a start script that runs src/server.js, and confirm Express resolves from the local node_modules folder.", ("Dependencies ကို မည်သည့်နေရာတွင် install လုပ်သင့်သနည်း?", ["Project-local node_modules", "A shared production folder", "A client request body"], "Project-local node_modules", "Project-local dependencies make builds predictable and isolated."), "Use npm audit and reviewed lockfile updates; do not install packages from untrusted scripts."),
    ("Build the First Express Server", "application creation, listening, and graceful startup", "import express from 'express';\n\nconst app = express();\nconst port = Number(process.env.PORT ?? 3000);\n\napp.get('/health', (_request, response) => {\n  response.json({ status: 'ok' });\n});\n\napp.listen(port, () => console.log(`Listening on ${port}`));", "src/server.js", "Create one application instance, define a health route, and listen on a configuration-driven port. A health endpoint should be cheap and avoid exposing secrets. In production, startup should handle configuration failures explicitly and shutdown should stop accepting traffic before closing resources.", "Express app တစ်ခုဖန်တီးပြီး health route နှင့် configuration-driven port ကို သုံးပါ။ Health endpoint တွင် secret များမပါစေဘဲ cheap ဖြစ်ရမည်။ Production shutdown တွင် traffic ရပ်ပြီး resources များကို သေချာပိတ်ပါ။", "Start the server locally, request GET /health, then change PORT through an environment variable and verify the server uses it.", ("Port ကို ဘယ်နေရာမှဖတ်သင့်သနည်း?", ["Environment configuration", "A hardcoded password field", "A random client header"], "Environment configuration", "Environment variables keep deployment configuration outside source code."), "Never commit .env files containing real credentials."),
    ("Routing and Route Parameters", "named routes, parameters, query strings, and predictable resources", "app.get('/courses/:courseId', (request, response) => {\n  const { courseId } = request.params;\n  const { format = 'json' } = request.query;\n  response.json({ courseId, format });\n});", "src/routes.js", "Routes map method and path combinations to handlers. Parameters identify a resource, while query strings refine a collection request. Validate both before using them in a database query. Keep route handlers small and delegate business decisions to services so authorization is not accidentally skipped.", "Route path တွင် parameter သည် resource ကို identify လုပ်ပြီး query string သည် collection request ကို refine လုပ်သည်။ Database query မလုပ်မီ နှစ်ခုစလုံးကို validate လုပ်ပါ။ Handler များကို သေးငယ်စွာထားပြီး service သို့ delegate လုပ်ပါ။", "Add a GET /courses/:courseId route and return 400 for an invalid id format before any database access.", ("Route parameter ကို ဘာအတွက်အသုံးပြုသနည်း?", ["Resource identity", "A secret store", "A CSS selector only"], "Resource identity", "A path parameter commonly identifies one resource."), "Never treat a route parameter as proof that the current user may access the resource."),
    ("Middleware and the Request Pipeline", "ordered functions, next, authentication boundaries, and request parsing", "app.use(express.json());\n\napp.use((request, _response, next) => {\n  request.receivedAt = new Date().toISOString();\n  next();\n});\n\napp.get('/profile', requireUser, profileController);", "src/middleware.js", "Middleware runs in registration order and can inspect or change the request, end the response, or pass control with next. A middleware that neither responds nor calls next will hang a request. Authentication middleware establishes identity; authorization middleware checks permissions for a specific action or record. Keep these concerns separate.", "Middleware များသည် register လုပ်ထားသော order အတိုင်း run သည်။ Response မပြန်ဘဲ next မခေါ်ပါက request hang ဖြစ်နိုင်သည်။ Authentication သည် identity ကိုစစ်ပြီး authorization သည် action/resource permission ကို ထပ်စစ်သည်။", "Write a request timer middleware, then place it before a route. Add a second middleware that rejects a missing authorization header without logging its value.", ("Middleware က request ဆက်သွားရန် ဘာလုပ်ရမည်နည်း?", ["Call next() or send a response", "Wait forever", "Delete the route"], "Call next() or send a response", "Each middleware must pass control or complete the response."), "Do not log raw tokens or use client-supplied user ids for ownership decisions."),
    ("Controllers, Services, and Error Boundaries", "separating transport logic from business rules and failures", "app.get('/courses/:id', asyncHandler(async (request, response) => {\n  const course = await courseService.findVisible(request.params.id, request.user);\n  if (!course) return response.sendStatus(404);\n  return response.json(course);\n}));\n\napp.use((error, _request, response, _next) => {\n  console.error(error);\n  response.status(500).json({ error: 'Internal server error' });\n});", "src/app.js", "Controllers translate HTTP inputs and outputs. Services hold business decisions and authorization-aware operations. Repositories or query modules handle persistence. Central error middleware prevents duplicated responses and lets logs contain diagnostics while clients receive a safe message. Async handlers must forward rejected promises to the error boundary.", "Controller သည် HTTP input/output ကို translate လုပ်ပြီး service သည် business rule နှင့် authorization ကို စီမံသည်။ Error middleware တစ်နေရာတည်းတွင် ထားခြင်းဖြင့် duplicate response များကို ရှောင်နိုင်သည်။ Client သို့ safe error message ပြပြီး server log တွင် diagnostic ကိုသာ ထားပါ။", "Refactor one route into controller and service functions. Add one not-found branch and one unexpected-error branch with safe client output.", ("Internal exception detail ကို client သို့ ဘယ်လိုပြသသင့်သနည်း?", ["Safe generic error", "Full stack trace", "Database password"], "Safe generic error", "Detailed diagnostics belong in protected logs, not public responses."), "Avoid catch-all handlers that hide errors without preserving structured logs."),
    ("Build a First JSON API", "a complete read-only endpoint with validation and testable behavior", "app.get('/api/v1/courses', async (request, response, next) => {\n  try {\n    const limit = Math.min(Number(request.query.limit ?? 10), 50);\n    const courses = await courseService.list({ limit });\n    response.json({ data: courses, limit });\n  } catch (error) {\n    next(error);\n  }\n});", "src/routes/courses.js", "A useful API has a stable version prefix, explicit input limits, predictable JSON envelopes, and safe failure behavior. This first slice intentionally uses a service boundary so a database can be added later without rewriting the route. Pagination, authorization, rate limits, and tests belong to the contract, not as afterthoughts.", "ကောင်းမွန်သော API တွင် version prefix၊ input limit၊ predictable JSON response နှင့် safe failure behavior ရှိရမည်။ Service boundary ထားခြင်းဖြင့် database ထည့်သည့်အခါ route ကို မပြန်ရေးရပါ။ Pagination၊ authorization၊ rate limit နှင့် tests ကို အစကတည်းက contract ထဲတွင် ထည့်ပါ။", "Design GET /api/v1/courses with a bounded limit and write a small request/response table including 200 and 400 cases.", ("API version prefix ကို ဘာကြောင့်သုံးသနည်း?", ["Controlled evolution of the contract", "To hide every error", "To execute shell commands"], "Controlled evolution of the contract", "A version prefix gives clients and servers a deliberate compatibility boundary."), "The Academy shows examples only and never executes student Express code."),
]

# Keep the first vertical slice at eight published lessons; the dedicated
# Node.js runtime module will expand this topic later in the curriculum.
MODULE_ONE = [item for item in MODULE_ONE if item[0] != "Node.js Backend Fundamentals"]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, code, filename, theory, mm, exercise, question_data, note = item
    question, options, answer, explanation = question_data
    previous = "No Express.js experience is required; basic JavaScript and terminal familiarity are helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: complete the first Express API lab and review the Module 1 assessment."
    return f"""Introduction
{title} introduces {topic} through a production-minded Express.js workflow.

Learning objectives
- Explain {topic} in your own words.
- Build a small, testable Node.js/Express example.
- Identify validation, authorization, logging, and security boundaries.

Prerequisites
{previous}

Architecture explanation
Client → HTTP request → router → middleware → controller → service → data boundary → response

Detailed theory
{theory}

Step-by-step code example
1. Create or open the file below.
2. Install only reviewed project-local dependencies.
3. Run the command or request described in Expected output.
4. Change one input and observe the status, headers, and JSON response.

File path
```text
{filename}
```

Code
```javascript
{code}
```

Commands
Use `npm ci` when a lockfile is available and run the server only in a disposable local environment. Never place credentials in source, request bodies, or examples.

Expected output
The example should produce a predictable local response or console result. Verify status codes and response shape rather than trusting a client display.

Code explanation
The request enters through a public boundary, middleware parses or checks it, application code makes an explicit decision, and the response communicates the outcome. Keep database and authorization decisions on the server.

Common errors
- Running a module with the wrong Node.js version or outside the project folder.
- Forgetting `express.json()` before reading a JSON body.
- Registering middleware after a route that needs it.
- Returning a response and then calling `next()` or sending another response.

Troubleshooting
Read the first stack frame in your own code, inspect the request method/path/body, verify middleware order, and reproduce with a local request. Log structured metadata but redact tokens, passwords, cookies, and personal data.

Best practices
- Keep routes thin and move business decisions into services.
- Validate path, query, body, and headers before database access.
- Use stable API versions, bounded pagination, tests, and explicit error contracts.

Security considerations
Use parameterized queries, secure password hashing, authorization checks, rate limiting, safe cookies, CSRF defenses where cookie auth is used, and generic public error messages. Never build an unrestricted URL fetch proxy or execute user code.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}

Mini project
Build a small `/api/v1/courses` read-only endpoint with a request contract, validation, safe errors, one service function, and a test plan. Document its folder structure and security checklist.

Summary
You can now reason about {topic} as a verifiable backend boundary rather than a collection of route snippets.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
{note}
"""


def seed_express_course(db, course):
    course.title = "Express.js Backend Development — From Zero to Professional"
    course.short_description = "A free, practical path from Node.js fundamentals to secure, tested Express.js APIs."
    course.description = "Learn Express.js routing, middleware, REST API design, validation, PostgreSQL integration, authentication, testing, TypeScript, Docker, CI/CD, and production architecture through safe examples."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 35
    course.outcomes = "Build maintainable Express.js APIs on Node.js|Design routes, middleware, services, and error boundaries|Connect secure APIs to PostgreSQL and authentication|Test, document, containerize, and deploy backend services responsibly"
    course.requirements = "Basic JavaScript syntax, a terminal, and a text editor; no previous Express.js experience is required."

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
        values = {"title": f"{title} example", "language": "javascript", "filename": item[3], "code": item[2], "description": "Read-only Express.js example. Run only in a disposable local Node.js project; the Academy does not execute student code.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)

        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the request flow and retry after explaining the security boundary.", status="published")
            db.add(quiz)
            db.flush()
        questions = [(item[7][0], item[7][1], item[7][2], item[7][3]), ("True or false: the Academy executes student Express.js code on its application host.", ["True", "False"], "False", "Examples are displayed as read-only learning content."), ("Which practice protects an Express API?", ["Validate input and authorize records server-side", "Trust a client user id", "Return stack traces publicly"], "Validate input and authorize records server-side", "Backend boundaries must validate and authorize independently of the browser.")]
        for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
            question_row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
            values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
            if not question_row:
                db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
            else:
                for key, value in values.items():
                    setattr(question_row, key, value)
    db.flush()

