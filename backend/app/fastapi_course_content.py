"""Authored FastAPI vertical slice for the idempotent catalog seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion


PLANNED_MODULES = [
    "Introduction to FastAPI", "Python for FastAPI Developers", "HTTP & REST API Fundamentals", "FastAPI Installation & Setup",
    "FastAPI Project Structure", "Path Operations & Routing", "Path & Query Parameters", "Request Bodies & Pydantic",
    "Response Models & Status Codes", "Dependency Injection", "APIRouter & Modular APIs", "REST API Design & CRUD",
    "Error Handling & Exceptions", "Middleware, CORS & Lifespan", "PostgreSQL Fundamentals", "SQLAlchemy ORM",
    "Alembic Database Migrations", "Async Database Access", "Authentication Fundamentals", "OAuth2 & JWT",
    "Authorization & RBAC", "FastAPI Security Best Practices", "File Uploads & Storage", "Email & Notifications",
    "Async Programming in FastAPI", "Background Tasks & Queues", "WebSockets & Real-Time APIs", "Advanced API Features",
    "API Documentation & OpenAPI", "Testing FastAPI Applications", "Redis & Caching", "Performance Optimization",
    "Architecture & Design Patterns", "Dockerizing FastAPI", "CI/CD for FastAPI", "Production Deployment",
    "Monitoring & Observability", "Multi-Tenant SaaS APIs", "Professional FastAPI Projects", "Final FastAPI Capstone",
]

MODULE_ONE = [
    ("What FastAPI Is and Why It Exists", "typed Python APIs built on ASGI, Starlette, and Pydantic", "from fastapi import FastAPI\n\napp = FastAPI(title=\"Learning API\")\n\n@app.get(\"/health\")\ndef health():\n    return {\"status\": \"ok\"}", "app/main.py", "FastAPI is a Python framework for building APIs with typed declarations, automatic OpenAPI documentation, and validation through Pydantic. It builds on ASGI-compatible components for web handling. The framework accelerates development, but authentication, authorization, database transactions, rate limits, and safe error responses remain application responsibilities.", "FastAPI သည် type declaration၊ Pydantic validation နှင့် OpenAPI documentation အလိုအလျောက်ရရှိသော Python API framework ဖြစ်သည်။ Framework က development ကို မြန်စေသော်လည်း authentication၊ authorization၊ transaction နှင့် security ကို application က စီမံရမည်။", "Explain why a health endpoint should not expose credentials or database internals. Sketch a request-to-response flow.", ("FastAPI ၏ အဓိကအားသာချက်က ဘာလဲ?", ["Typed validation and automatic API documentation", "Replacing every database", "Executing browser JavaScript"], "Typed validation and automatic API documentation", "FastAPI uses Python type declarations to validate and document API contracts."), "Run examples only in your own isolated local project; the Academy does not execute learner code."),
    ("ASGI and the FastAPI Request Lifecycle", "ASGI servers, route matching, dependencies, handlers, and responses", "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get(\"/items/{item_id}\")\nasync def read_item(item_id: int):\n    return {\"item_id\": item_id}", "app/main.py", "An ASGI server receives a connection and forwards a request scope to the application. FastAPI matches a path operation, resolves dependencies, validates path/query/body data, calls a sync or async handler, serializes the result, and returns an HTTP response. This lifecycle is a boundary: authorization must happen before returning protected data.", "ASGI server က request scope ကို application သို့ ပို့သည်။ FastAPI သည် route match၊ dependency resolution၊ input validation၊ handler execution နှင့် response serialization ကို အစဉ်လိုက်လုပ်သည်။ Protected data မပြန်မီ authorization ပြုလုပ်ရမည်။", "Draw the lifecycle and label where validation, authentication, database access, and response serialization occur.", ("ASGI သည် ဘာကို ကိုယ်စားပြုသနည်း?", ["Async-capable Python server/application interface", "A SQL table", "A frontend styling system"], "Async-capable Python server/application interface", "ASGI defines an interface for Python web servers and applications, including async use cases."), "A visual lifecycle is explanatory and is not live API execution."),
    ("Install FastAPI and Uvicorn Safely", "virtual environments, dependency pinning, and the development server", "python3 -m venv .venv\nsource .venv/bin/activate\npython -m pip install --upgrade pip\npip install \"fastapi>=0.110,<1.0\" \"uvicorn[standard]>=0.27,<1.0\"\npython -c \"import fastapi; print(fastapi.__version__)\"", "terminal", "Use a supported Python release and isolate project dependencies in a virtual environment. Uvicorn runs the ASGI application locally. Record resolved dependencies in a lock or requirements workflow, review updates, and never put secrets in requirements files or source control.", "Python virtual environment သုံးပြီး FastAPI နှင့် Uvicorn ကို project-local install လုပ်ပါ။ Dependency version များကို record လုပ်ပြီး secret များကို source control ထဲ မထည့်ပါနှင့်။", "Create a fastapi-learning folder, install the dependencies, and record the Python and FastAPI versions from the isolated environment.", ("Uvicorn ၏ အခန်းကဏ္ဍက ဘာလဲ?", ["Run an ASGI application", "Validate a PostgreSQL schema", "Store passwords"], "Run an ASGI application", "Uvicorn is an ASGI server commonly used to serve FastAPI applications."), "Do not install packages from untrusted scripts or run a local app with production credentials."),
    ("Create Your First FastAPI Project", "application entry points, uvicorn reload, and health checks", "# app/main.py\nfrom fastapi import FastAPI\n\napp = FastAPI(title=\"CodeMaster API\")\n\n@app.get(\"/health\")\ndef health():\n    return {\"status\": \"ok\"}\n\n# terminal\nuvicorn app.main:app --reload --port 8000", "app/main.py + terminal", "Keep a small app entry point and start the development server with an explicit import path. Reload is useful locally but should not be used as a production process manager. A health route should be cheap, deterministic, and free of sensitive state.", "app/main.py ထဲတွင် FastAPI app တည်ဆောက်ပြီး uvicorn ဖြင့် local server run ပါ။ --reload သည် development အတွက်သာဖြစ်သည်။ Health route သည် cheap၊ deterministic ဖြစ်ပြီး sensitive data မပါသင့်ပါ။", "Run the server, request /health, and open /docs. Stop it and explain why the automatic docs route should be protected or disabled when an internal production API requires it.", ("FastAPI automatic interactive docs ကို ဘယ် route မှာတွေ့နိုင်သနည်း?", ["/docs", "/passwords", "/database-dump"], "/docs", "FastAPI exposes Swagger UI at /docs by default unless configured otherwise."), "Review whether API documentation should be public before deploying an internal service."),
    ("Path Operations and HTTP Methods", "decorators, methods, route ordering, and status codes", "from fastapi import FastAPI\nfrom fastapi import status\n\napp = FastAPI()\n\n@app.post(\"/items\", status_code=status.HTTP_201_CREATED)\ndef create_item():\n    return {\"created\": True}", "app/routes.py", "A path operation combines an HTTP method and path with a Python callable. Use method semantics consistently: GET reads, POST creates, PUT/PATCH updates, and DELETE removes. Return a deliberate status code and avoid ambiguous overlapping routes. The route is public until dependencies or authorization checks say otherwise.", "Path operation တွင် HTTP method နှင့် path ကို Python callable နှင့် ချိတ်ဆက်သည်။ GET၊ POST၊ PUT/PATCH၊ DELETE တို့၏ semantics ကို တိကျစွာ သုံးပါ။ Status code ကို deliberate ပြုလုပ်ပြီး authorization ကို မမေ့ပါနှင့်။", "Add GET /items and POST /items with separate response contracts. Document which operation requires authentication.", ("Resource create operation အတွက် သင့်တော်သော status code က ဘာလဲ?", ["201 Created", "302 Found always", "500 always"], "201 Created", "201 communicates a successful resource creation."), "Never assume a route is protected because it is not linked from the frontend."),
    ("Path and Query Parameters", "typed path values, optional filters, and bounded pagination", "from fastapi import FastAPI, Query\n\napp = FastAPI()\n\n@app.get(\"/courses/{course_id}\")\ndef course(course_id: int, limit: int = Query(10, ge=1, le=50)):\n    return {\"course_id\": course_id, \"limit\": limit}", "app/routes/courses.py", "FastAPI validates typed path and query parameters before calling the handler. Constraints such as ge and le prevent unbounded queries and make the API contract visible in OpenAPI. Validation is not authorization: after accepting a course_id, the service still must check whether the current user may view it.", "FastAPI သည် typed path/query parameter များကို handler မခေါ်မီ validate လုပ်သည်။ ge/le constraint များဖြင့် query ကို bounded ဖြစ်စေသည်။ Validation သည် authorization မဟုတ်သောကြောင့် user access ကို service တွင် ထပ်စစ်ရမည်။", "Add a search query and bounded limit to a local route. Record the validation response for a negative id and a limit above the maximum.", ("Query limit ကို bounded လုပ်ရန် ဘာကိုသုံးနိုင်သနည်း?", ["Query(..., ge=1, le=50)", "Trust any integer", "A client-side comment"], "Query(..., ge=1, le=50)", "Pydantic-based constraints reject values outside the intended range."), "Do not pass unvalidated user input directly into SQL or filesystem paths."),
    ("Request Bodies and Pydantic Models", "schema validation, coercion, and safe input boundaries", "from fastapi import FastAPI\nfrom pydantic import BaseModel, Field\n\nclass CourseCreate(BaseModel):\n    title: str = Field(min_length=1, max_length=180)\n    level: str = Field(pattern=r\"^(beginner|intermediate|advanced)$\")\n\napp = FastAPI()\n\n@app.post(\"/courses\")\ndef create_course(payload: CourseCreate):\n    return {\"title\": payload.title, \"level\": payload.level}", "app/schemas.py + app/main.py", "Pydantic models make request contracts explicit and produce structured validation errors. They should describe transport data, not replace authorization or persistence rules. Normalize and validate input at the boundary, then pass a trusted DTO to a service. Never accept a client-supplied owner_id as proof of ownership.", "Pydantic model သည် request contract နှင့် structured validation error ကို ပေးသည်။ သို့သော် authorization နှင့် persistence rule ကို အစားမထိုးနိုင်ပါ။ Boundary တွင် validate/normalize လုပ်ပြီး service သို့ DTO ပို့ပါ။", "Create a CourseCreate model, send valid and invalid JSON, and compare the 200/422 behavior. Add a test that invalid data never reaches the service.", ("FastAPI invalid request body အတွက် ပုံမှန် response က ဘာလဲ?", ["422 validation error", "Always 200", "HTML login page"], "422 validation error", "FastAPI returns a structured validation response when input does not match the schema."), "Keep secrets and server-owned fields out of client-create schemas."),
    ("Response Models and API Contracts", "output validation, status codes, and safe serialization", "from fastapi import FastAPI\nfrom pydantic import BaseModel\n\nclass CourseOut(BaseModel):\n    id: int\n    title: str\n\napp = FastAPI()\n\n@app.get(\"/courses/{course_id}\", response_model=CourseOut)\ndef read_course(course_id: int):\n    return {\"id\": course_id, \"title\": \"FastAPI Foundations\"}", "app/schemas.py + app/routes/courses.py", "A response model documents what clients may rely on and filters accidental fields from output. It is especially important when ORM objects contain internal flags, hashes, ownership ids, or audit metadata. Select the status code deliberately and keep the public contract stable while internal models evolve.", "Response model သည် client ယုံကြည်အသုံးပြုနိုင်သော output contract ဖြစ်သည်။ ORM object ထဲမှ internal field၊ hash၊ ownership id နှင့် audit metadata များ မထွက်စေရန် အသုံးဝင်သည်။", "Add a response model that excludes an internal field, return 404 for a missing course, and write a response-shape test.", ("response_model ၏ အကျိုးကျေးဇူးက ဘာလဲ?", ["Control and document serialized output", "Run migrations automatically", "Grant admin permissions"], "Control and document serialized output", "Response models make serialization explicit and help prevent accidental data exposure."), "Never serialize password hashes, tokens, or private ownership fields into a public response."),
    ("Dependency Injection and the First API Slice", "reusable dependencies, authentication boundaries, and test overrides", "from typing import Annotated\nfrom fastapi import Depends, FastAPI\n\ndef get_request_id() -> str:\n    return \"local-request\"\n\nRequestId = Annotated[str, Depends(get_request_id)]\napp = FastAPI()\n\n@app.get(\"/api/v1/courses\")\ndef list_courses(request_id: RequestId):\n    return {\"request_id\": request_id, \"data\": []}", "app/dependencies.py + app/routes/courses.py", "Dependencies make shared concerns explicit and composable: database sessions, current users, settings, request ids, and authorization policies can be injected into route handlers. They also enable dependency overrides in tests. A dependency that identifies a user is not enough; resource-level authorization still belongs at the service boundary.", "FastAPI dependency injection သည် database session၊ current user၊ settings နှင့် authorization policy များကို reusable ဖြစ်စေသည်။ Test တွင် dependency override လုပ်နိုင်သည်။ User identity ရှိခြင်းတစ်ခုတည်းဖြင့် resource access ခွင့် မဖြစ်သေးပါ။", "Create a get_settings dependency and override it in a test. Then describe where get_current_user and require_course_owner would be checked.", ("Dependency override ကို ဘာအတွက်အသုံးပြုသနည်း?", ["Replace dependencies in isolated tests", "Bypass all authorization in production", "Expose environment secrets"], "Replace dependencies in isolated tests", "Overrides provide controlled test collaborators without weakening production authorization."), "Keep overrides in tests and never ship a test dependency that bypasses production security."),
]

# Keep the first vertical slice at eight published lessons; ASGI internals are
# revisited in the dedicated request-lifecycle visualizer and later module.
MODULE_ONE = [item for item in MODULE_ONE if item[0] != "ASGI and the FastAPI Request Lifecycle"]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, code, filename, theory, mm, exercise, question_data, note = item
    question, options, answer, explanation = question_data
    previous = "No FastAPI experience is required; basic Python and terminal familiarity are helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: complete the first FastAPI lab and review the Module 1 assessment."
    return f"""Introduction
{title} introduces {topic} through a production-minded FastAPI workflow.

Learning objectives
- Explain {topic} in your own words.
- Build a small, typed, testable FastAPI example.
- Identify validation, authorization, persistence, and security boundaries.

Prerequisites
{previous}

Architecture explanation
Client → ASGI server → FastAPI route → dependencies → validation → service/data boundary → response model

Detailed theory
{theory}

Step-by-step Python example
1. Create or open the file shown below.
2. Activate the isolated Python environment.
3. Run the command or request described in Expected API response.
4. Change one input and inspect the status code and JSON shape.

File path
```text
{filename}
```

Code
```python
{code}
```

Commands
Use `uvicorn app.main:app --reload` only for local development. Never put credentials in examples, request bodies, or source control.

Expected API response
The example should return a predictable local response or a structured validation error. Verify the response model and status code rather than trusting a client display.

Code explanation
The request enters through an ASGI boundary, FastAPI resolves dependencies and validates declared inputs, application code makes an explicit decision, and the response model controls public serialization.

Common errors
- Running uvicorn from the wrong working directory or using the wrong import path.
- Forgetting to install dependencies in the active virtual environment.
- Confusing validation with authentication or authorization.
- Returning ORM objects with private fields through an overly broad response model.

Troubleshooting
Read the first traceback frame in your code, inspect the method/path/body, verify the import path, and reproduce with a local request. Log structured metadata but redact tokens, passwords, cookies, and personal data.

Best practices
- Keep route handlers thin and move business rules into services.
- Validate path, query, body, and headers before database access.
- Use response models, bounded pagination, typed settings, tests, and explicit errors.

Security considerations
Use parameterized queries, secure password hashing, server-side authorization, rate limits, safe cookies, and generic public errors. Do not execute user code or build an unrestricted URL proxy.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}

Mini project
Build a small `/api/v1/courses` endpoint with Pydantic input/output models, a dependency for settings, one service boundary, safe errors, and a test plan. Document the folder structure and security checklist.

Summary
You can now reason about {topic} as a typed backend boundary rather than a collection of decorators.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
{note}
"""


def seed_fastapi_course(db, course):
    course.title = "FastAPI Backend Development — From Zero to Professional"
    course.short_description = "A free, practical path from typed Python API foundations to secure production FastAPI services."
    course.description = "Learn FastAPI routing, Pydantic validation, dependency injection, PostgreSQL, SQLAlchemy, Alembic, authentication, async programming, testing, Docker, and production API architecture through safe examples."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 35
    course.outcomes = "Build typed APIs with FastAPI and Pydantic|Design routes, dependencies, services, and response contracts|Connect secure APIs to PostgreSQL and authentication|Test, containerize, observe, and deploy backend services responsibly"
    course.requirements = "Basic Python syntax, a terminal, and a text editor; no previous FastAPI experience is required."

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
        values = {"title": f"{title} example", "language": "python", "filename": item[3], "code": item[2], "description": "Read-only FastAPI example. Run only in a disposable local Python project; the Academy does not execute student code.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)

        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the request lifecycle and retry after explaining the validation and authorization boundary.", status="published")
            db.add(quiz)
            db.flush()
        questions = [(item[7][0], item[7][1], item[7][2], item[7][3]), ("True or false: the Academy executes student FastAPI code on its application host.", ["True", "False"], "False", "Examples are displayed as read-only learning content."), ("Which practice protects a FastAPI endpoint?", ["Validate input and authorize records server-side", "Trust a client owner_id", "Return tracebacks publicly"], "Validate input and authorize records server-side", "Backend boundaries must validate and authorize independently of the browser.")]
        for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
            question_row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
            values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
            if not question_row:
                db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
            else:
                for key, value in values.items():
                    setattr(question_row, key, value)
    db.flush()

