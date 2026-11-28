"""Reviewable Node.js curriculum batch with EN/MM content and safe examples."""
import json
import re

from sqlalchemy import select
from .models import CodeExample, CodingExercise, CourseModule, Lesson, LessonQuiz, QuizQuestion

MODULES = {
    2: "JavaScript and Node Runtime Foundations",
    3: "Modules, npm and Core APIs",
    4: "Asynchronous Node.js and the Event Loop",
    5: "HTTP, Express and REST APIs",
    6: "Databases, Validation and Authentication",
    7: "Testing, Security and Observability",
    8: "Performance, Caching and Real-Time Services",
    9: "TypeScript, Docker and Production Deployment",
}

LESSONS = {
    2: [("Modern JavaScript for Node", "const, let, functions, objects, and modules", "const add = (a, b) => a + b;\nconsole.log(add(2, 3));", "JavaScript syntax နှင့် function များကို Node runtime တွင် အသုံးပြုပါ။"), ("Arrays and Objects", "data transformation with arrays, objects, and immutability", "const users = [{name: 'A'}, {name: 'B'}];\nconsole.log(users.map(user => user.name));", "Array/object transformation တွင် input shape နှင့် mutation ကို စစ်ပါ။"), ("Errors and Input Validation", "explicit errors, boundary validation, and safe messages", "function positive(value) {\n  if (value < 0) throw new Error('invalid value');\n  return value;\n}\nconsole.log(positive(2));", "Invalid input ကို validate လုပ်ပြီး internal details မဖော်ပြပါနှင့်။"), ("JavaScript Testing Basics", "assertions, unit tests, and regression protection", "import assert from 'node:assert/strict';\nassert.equal(2 + 2, 4);\nconsole.log('test passed');", "Normal၊ boundary နှင့် error path များကို test ရေးပါ။")],
    3: [("CommonJS and ES Modules", "module boundaries, exports, imports, and package type", "export const answer = 42;\n// import { answer } from './answer.js';", "ES module boundary နှင့် import/export ကို ရှင်းလင်းစွာ သတ်မှတ်ပါ။"), ("npm and package-lock", "dependency manifests, scripts, lockfiles, and safe installs", "const packageInfo = {name: 'academy-api', private: true};\nconsole.log(packageInfo);", "Dependency version နှင့် lockfile ကို ထိန်းသိမ်းပြီး untrusted package မထည့်ပါနှင့်။"), ("Node Process and Environment", "process arguments, environment configuration, and signals", "const mode = process.env.NODE_ENV || 'development';\nconsole.log({mode});", "Secret ကို process environment မှသာ server-side ဖတ်ပါ။"), ("File System and Paths", "safe paths, async file APIs, and traversal prevention", "import path from 'node:path';\nconsole.log(path.join('data', 'demo.json'));", "User path ကို validate လုပ်ပြီး traversal မဖြစ်စေရန် ကာကွယ်ပါ။")],
    4: [("Promises and async/await", "promise states, await, and error propagation", "const getValue = async () => 42;\nconsole.log(await getValue());", "Async function တွင် await နှင့် rejection handling ကို ထည့်ပါ။"), ("Event Loop and Timers", "call stack, queues, timers, and non-blocking work", "console.log('start');\nsetTimeout(() => console.log('later'), 0);\nconsole.log('end');", "Event loop order ကို နားလည်ပြီး CPU-heavy work ကို မပိတ်စေပါနှင့်။"), ("Streams and Backpressure", "streaming data, chunks, and bounded memory", "const {Readable} = await import('node:stream');\nconsole.log(Readable.from(['a', 'b']));", "Stream သုံးရာတွင် backpressure နှင့် error handling စီမံပါ။"), ("Async Concurrency", "Promise.all, limits, retries, and cancellation", "const results = await Promise.all([Promise.resolve(1), Promise.resolve(2)]);\nconsole.log(results);", "Concurrency ကို limit ထားပြီး timeout/retry policy သတ်မှတ်ပါ။")],
    5: [("HTTP Server Fundamentals", "requests, responses, headers, and status codes", "import http from 'node:http';\nconst response = {status: 200, contentType: 'application/json'};\nconsole.log(response);", "HTTP request/response နှင့် status code ကို မှန်ကန်စွာ သတ်မှတ်ပါ။"), ("Express Routing and Middleware", "routes, middleware order, and request context", "const route = {method: 'GET', path: '/courses'};\nconsole.log(route);", "Middleware order နှင့် route responsibility ကို ခွဲပါ။"), ("REST Resource Design", "resources, verbs, pagination, and idempotency", "const endpoint = {method: 'GET', path: '/api/courses', page: 1};\nconsole.log(endpoint);", "REST endpoint တွင် resource၊ verb၊ pagination နှင့် idempotency ရှင်းပါ။"), ("Validation and Error Middleware", "schemas, safe error envelopes, and request IDs", "const error = {code: 'VALIDATION_ERROR', requestId: 'demo-id'};\nconsole.log(error);", "Validation error ကို safe shape နှင့် request ID ဖြင့် ပြန်ပါ။"), ("API Documentation and Contracts", "OpenAPI-style contracts, examples, and compatibility", "const contract = {method: 'POST', path: '/api/courses', response: 201};\nconsole.log(contract);", "API contract နှင့် backward compatibility ကို documentation လုပ်ပါ။")],
    6: [("PostgreSQL Access Patterns", "parameterized queries, transactions, and connection pools", "const query = {text: 'select * from courses where id = $1', values: ['id']};\nconsole.log(query);", "Parameterized query နှင့် transaction boundary ကို သုံးပါ။"), ("MongoDB Documents and Indexes", "document modeling, indexes, and consistency choices", "const index = {collection: 'courses', fields: {slug: 1}, unique: true};\nconsole.log(index);", "Document schema နှင့် index ကို query pattern အလိုက် သတ်မှတ်ပါ။"), ("Authentication and Sessions", "password hashing, sessions, tokens, and expiration", "const session = {userId: 'user-1', expiresIn: '15m'};\nconsole.log(session);", "Password ကို hash လုပ်ပြီး session/token expiry နှင့် revocation ထည့်ပါ။"), ("Authorization and RBAC", "roles, ownership, least privilege, and server checks", "const policy = {role: 'editor', action: 'course:update', allowed: true};\nconsole.log(policy);", "RBAC ကို server-side စစ်ပြီး ownership နှင့် least privilege ထည့်ပါ။")],
    7: [("Unit and Integration Testing", "test isolation, HTTP tests, fixtures, and cleanup", "const testCase = {name: 'GET courses', expectedStatus: 200};\nconsole.log(testCase);", "Unit/integration test ကို ခွဲပြီး fixture cleanup လုပ်ပါ။"), ("Security Headers and CORS", "headers, origins, cookies, CSRF, and secure defaults", "const security = {cors: ['https://academy.example'], cookies: 'httpOnly'};\nconsole.log(security);", "CORS၊ cookie နှင့် security headers ကို explicit allowlist ဖြင့် စီမံပါ။"), ("Rate Limits and Abuse Controls", "quotas, throttling, replay protection, and safe failures", "const limit = {key: 'user:1', requests: 10, windowSeconds: 60};\nconsole.log(limit);", "Rate limit နှင့် abuse response ကို endpoint risk အလိုက် သတ်မှတ်ပါ။"), ("Logging and Request Tracing", "structured logs, request IDs, metrics, and redaction", "const log = {requestId: 'req-1', event: 'course.read', secret: '[redacted]'};\nconsole.log(log);", "Structured log တွင် secret မထည့်ဘဲ request ID ဖြင့် trace လုပ်ပါ။")],
    8: [("Caching and Invalidation", "cache keys, TTL, invalidation, and stale data", "const cacheEntry = {key: 'course:1', ttlSeconds: 60};\nconsole.log(cacheEntry);", "Cache key/TTL နှင့် invalidation policy ကို ရှင်းပါ။"), ("Queues and Background Jobs", "job idempotency, retries, visibility, and dead letters", "const job = {id: 'job-1', attempts: 1, status: 'queued'};\nconsole.log(job);", "Background job တွင် idempotency၊ retry နှင့် dead-letter policy ထည့်ပါ။"), ("WebSockets and Server-Sent Events", "connection lifecycle, authorization, and backpressure", "const channel = {name: 'course-progress', authorized: true};\nconsole.log(channel);", "Realtime channel ကို auth နှင့် connection cleanup ဖြင့် ကာကွယ်ပါ။"), ("Performance Profiling", "latency budgets, CPU/memory pressure, and bottlenecks", "const budget = {p95Ms: 200, maxMemoryMb: 256};\nconsole.log(budget);", "Performance claim ကို measured latency နှင့် resource budget ဖြင့် ထောက်ပြပါ။")],
    9: [("TypeScript for Node APIs", "types, interfaces, runtime validation, and generated contracts", "type Course = {id: string; title: string};\nconst course: Course = {id: '1', title: 'Node'};\nconsole.log(course);", "TypeScript type သည် runtime validation အစား မဖြစ်သောကြောင့် schema validate ထည့်ပါ။"), ("Docker and Configuration", "reproducible images, non-root users, health checks, and secrets", "const image = {user: 'node', health: '/healthz', secretSource: 'runtime'};\nconsole.log(image);", "Container ကို non-root၊ pinned dependency နှင့် health check ဖြင့် deploy ပါ။"), ("CI/CD and Database Migrations", "checks, migrations, approvals, and rollback", "const pipeline = ['lint', 'test', 'migration-check', 'deploy'];\nconsole.log(pipeline);", "CI/CD တွင် test၊ migration review နှင့် rollback approval ထည့်ပါ။"), ("Production Readiness and Capstone", "service ownership, SLOs, incident response, and handoff", "const service = {owner: 'platform-team', slo: '99.9%', rollback: true};\nconsole.log(service);", "Production service တွင် owner၊ SLO၊ monitoring နှင့် incident response ပါစေ။")],
}

def _slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(module_number, title, focus, code, next_title):
    return f"""# {title}

## Introduction
This lesson develops {focus} as part of a secure, observable Node.js service.

## Prerequisites
Complete the preceding lesson in Module {module_number}; use a supported Node.js LTS version and a project lockfile.

## Learning objectives
- Explain {focus} in a real Node.js application.
- Build or inspect a bounded example with explicit inputs and outputs.
- Identify async, data, security, testing, and operational risks.

## Detailed theory
{title} is useful only when its input contract, failure behavior, ownership, and runtime boundary are explicit. Keep credentials server-side, validate untrusted input, and separate tests from production data. A successful response is not proof that an API is secure or reliable.

## Main concepts
Runtime version, module boundary, request/response contract, timeout, cancellation, validation, authorization, structured errors, observability, and rollback are the core concepts.

## Syntax / API / command
```javascript
{code}
```

## Practical examples
### Example 1 — inspect
Run the safe example in an isolated local project and inspect its type, order, status, or schema.

### Example 2 — extend
Change one input or option, predict the result, and record the observed behavior. Add timeout or validation where the boundary is untrusted.

### Example 3 — verify
Add an assertion, HTTP contract check, error-path test, or structured log field. Compare with the stated expectation.

## Dataset and reproducibility notes
Use synthetic records and local fixtures. Record Node.js version, package-lock version, command, input contract, expected output, and limitation. Never put tokens, database passwords, or personal data in examples or logs.

## Expected output
The example should produce a small inspectable result related to {focus}. Exact ordering or timing can vary; verify the contract, status, error behavior, and resource boundary instead of inventing a performance claim.

## Line-by-line explanation
1. The first lines import or define a bounded input.
2. The central operation applies {focus} without accessing host secrets or unrestricted files.
3. The final statement prints or asserts a result that should be compared with the expectation.

## Common mistakes
- Forgetting to await promises or handling only the happy path.
- Trusting client IDs, paths, headers, or query values without validation.
- Leaking stack traces, tokens, SQL text, or personal data into responses/logs.
- Blocking the event loop or retrying a non-idempotent operation blindly.

## Best practices
- Use supported LTS releases, lockfiles, schemas, parameterized queries, least privilege, and focused tests.
- Define timeouts, rate limits, request IDs, metrics, health checks, and rollback criteria.
- Keep configuration and secrets server-only; return stable error envelopes.

## Security considerations
The Academy displays safe examples and does not execute arbitrary Node.js or shell code, access host files, or provide an unrestricted proxy. Apply authentication, authorization, input validation, redaction, and dependency review at every trust boundary.

## Exercises
1. Reproduce the example with synthetic input.
2. Add one boundary or error case and predict the result before running it.
3. Write one test and one security risk for this lesson.

## Practical exercises
Build a small local service component for {focus}. Include a contract, validation rule, expected response/error, focused test, and one limitation.

## Homework
Write an implementation note with runtime/package versions, route or function contract, observed behavior, test evidence, and rollback or recovery plan.

## Quiz
1. What protects a private credential? Server-only configuration and server-side authorization.
2. True or false: a 200 response alone proves production safety. False.
3. What improves reproducibility? Versioned dependencies, deterministic fixtures, tests, and documented assumptions.

## Mini project
Extend a local courses API with safe validation, structured errors, authorization, tests, request IDs, health checks, and a deployment note. Do not connect private production data.

## Summary
You can now apply {focus} with explicit runtime, async, data, security, and operational boundaries.

## Key takeaways
Reliable Node.js services make contracts, failures, permissions, tests, and observability visible.

## References
- Node.js documentation: https://nodejs.org/docs/latest/api/
- Express documentation: https://expressjs.com/
- OWASP API Security: https://owasp.org/www-project-api-security/

## Next lesson
{next_title}
"""

def _content_mm(title, focus, code, mm, next_title):
    return f"""# {title}

## မိတ်ဆက်
ဤ lesson တွင် {mm} ကို secure၊ observable Node.js service အတွင်း လေ့လာပါမည်။

## လိုအပ်ချက်
Module {title} မတိုင်မီ lesson များကို ပြီးစီးထားပြီး supported Node.js LTS နှင့် lockfile သုံးပါ။

## လေ့လာရမည့် ရည်မှန်းချက်များ
- {mm} ကို real Node.js application ထဲတွင် ရှင်းပြနိုင်ရန်။
- Bounded example ၏ input၊ output နှင့် failure ကို စစ်နိုင်ရန်။
- Async၊ data၊ security၊ testing နှင့် operations risk ကို ဖော်ထုတ်နိုင်ရန်။

## အသေးစိတ်သီအိုရီ
{mm} ကို အသုံးပြုရာတွင် input contract၊ failure behavior၊ ownership နှင့် runtime boundary ကို ရှင်းလင်းရပါမည်။ Credential ကို server-side ထားပြီး untrusted input ကို validate လုပ်ပါ။ Success response တစ်ခုတည်းဖြင့် API လုံခြုံ/ယုံကြည်ရသည်ဟု မဆိုနိုင်ပါ။

## အဓိကအယူအဆများ
Runtime version၊ module boundary၊ request/response contract၊ timeout၊ cancellation၊ validation၊ authorization၊ structured error၊ observability နှင့် rollback ကို မှတ်တမ်းတင်ပါ။

## Syntax / API / command
```javascript
{code}
```

## လက်တွေ့ဥပမာများ
Synthetic input ဖြင့် example ကို run ပါ။ Parameter တစ်ခု ပြောင်းပြီး result ကို ကြိုခန့်မှန်းပါ။ နောက်ဆုံးတွင် assertion၊ contract check သို့မဟုတ် error-path test တစ်ခုထည့်ပါ။

## Dataset နှင့် ပြန်လည်လုပ်ဆောင်နိုင်မှု
Local fixture နှင့် synthetic record သုံးပါ။ Node version၊ package lock၊ command၊ input contract၊ expected output နှင့် limitation ကို မှတ်တမ်းတင်ပါ။ Token၊ password နှင့် personal data မထည့်ပါနှင့်။

## မျှော်မှန်းရလဒ်
Example သည် {mm} နှင့် သက်ဆိုင်သော inspect လုပ်နိုင်သည့် result ကို ပေးရမည်။ Timing ကွာနိုင်သော်လည်း contract၊ status၊ error behavior နှင့် resource boundary ကို စစ်ပါ။

## Code ရှင်းလင်းချက်
အစတွင် bounded input သို့မဟုတ် module ကို သတ်မှတ်သည်။ အလယ်တွင် feature ကို အသုံးပြုပြီး host secret/file ကို မထိတွေ့စေပါ။ နောက်ဆုံးတွင် result ကို print/assert လုပ်သည်။

## အများဆုံးမှားတတ်သောအချက်များ
- Promise await/rejection မစီမံခြင်း။
- Client ID၊ path၊ header နှင့် query ကို မစစ်ဘဲ ယုံခြင်း။
- Stack trace၊ token၊ SQL နှင့် personal data ကို response/log ထဲ ဖော်ပြခြင်း။
- Event loop ကို block လုပ်ခြင်း သို့မဟုတ် non-idempotent retry ပြုလုပ်ခြင်း။

## ကောင်းမွန်သောနည်းလမ်းများ
Supported LTS၊ lockfile၊ schema၊ parameterized query၊ least privilege၊ focused test၊ timeout၊ rate limit၊ request ID၊ metric၊ health check နှင့် rollback သုံးပါ။

## Security considerations
Academy သည် arbitrary Node.js/shell code ကို execute မလုပ်ပါ။ Trust boundary တိုင်းတွင် authentication၊ authorization၊ validation၊ redaction နှင့် dependency review ထည့်ပါ။

## လေ့ကျင့်ခန်း
1. Synthetic input ဖြင့် example ကို ပြန်လုပ်ပါ။
2. Boundary/error case တစ်ခု ထည့်ပြီး result ကို ကြိုခန့်မှန်းပါ။
3. Test တစ်ခုနှင့် security risk တစ်ခု ရေးပါ။

## Practical exercises
{focus} အတွက် local component တစ်ခု တည်ဆောက်ပြီး contract၊ validation၊ response/error၊ test နှင့် limitation ပါစေ။

## အိမ်စာ
Runtime/package version၊ contract၊ observed behavior၊ test evidence နှင့် recovery plan ပါသော implementation note ရေးပါ။

## Quiz
1. Private credential ကို ဘာက ကာကွယ်သနည်း။ Server-only configuration နှင့် server-side authorization ဖြစ်သည်။
2. 200 response တစ်ခုတည်းဖြင့် production safety ကို အာမခံနိုင်သလား။ မနိုင်ပါ။
3. Reproducibility အတွက် versioned dependency၊ deterministic fixture၊ test နှင့် assumption documentation လိုသည်။

## Mini project
Local courses API တစ်ခုတွင် validation၊ structured error၊ authorization၊ test၊ request ID၊ health check နှင့် deployment note ထည့်ပါ။ Production private data မချိတ်ပါနှင့်။

## အနှစ်ချုပ်
{mm} ကို runtime၊ async၊ data၊ security နှင့် operation boundary များဖြင့် အသုံးပြုနိုင်ပါပြီ။

## Key takeaways
Reliable Node.js service သည် contract၊ failure၊ permission၊ test နှင့် observability ကို ရှင်းလင်းစွာ ဖော်ပြရသည်။

## References
Node.js၊ Express နှင့် OWASP API Security documentation ကို project version နှင့် ကိုက်ညီအောင် ဖတ်ပါ။

## နောက် lesson
{next_title}
"""

def _ensure_quiz(db, lesson, title, focus):
    quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
    if not quiz:
        quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review runtime, validation, security, testing, and operational boundaries before retrying.", status="draft")
        db.add(quiz); db.flush()
    questions = [(f"Which practice supports {focus}?", ["Validate inputs and document the contract", "Trust every client value", "Hide failures"], "Validate inputs and document the contract", "Reliable services make their contract and trust boundary explicit."), ("True or false: a 200 response alone proves production safety.", ["True", "False"], "False", "Safety also requires authorization, tests, monitoring, and recovery."), ("Where should a database credential remain?", ["Server-only configuration", "Browser source", "URL query string"], "Server-only configuration", "Credentials must not be exposed to clients or logs.")]
    for position, (prompt, options, answer, explanation) in enumerate(questions, 1):
        row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
        values = {"prompt": prompt, "question_type": "true_false" if options == ["True", "False"] else "multiple_choice", "options_json": json.dumps(options), "correct_answer": answer, "explanation": explanation}
        if not row: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))

def _ensure_exercise(db, lesson, title, focus, mm):
    slug = f"node-js-{lesson.slug}-practice"
    if db.scalar(select(CodingExercise).where(CodingExercise.slug == slug)): return
    db.add(CodingExercise(lesson_id=lesson.id, title=f"{title} practice", slug=slug, description_en=f"Practice {focus} with a local synthetic fixture. Include validation, a focused test, safe error handling, and one limitation. Do not use private data.", description_mm=f"{mm} ကို local synthetic fixture ဖြင့် လေ့ကျင့်ပါ။ Validation၊ focused test၊ safe error နှင့် limitation ထည့်ပါ။ Private data မသုံးပါနှင့်။", difficulty="intermediate", language="javascript", starter_code="// Work in an isolated local Node.js project.\n", status="draft"))

def seed_nodejs_additional_curriculum(db, course):
    created_modules = created_lessons = 0
    for module_number, module_title in MODULES.items():
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_number))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_number); db.add(module); db.flush(); created_modules += 1
        else: module.title = module_title
        specs = LESSONS[module_number]
        for position, (title, focus, code, mm) in enumerate(specs, 1):
            slug = f"{module_number:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == position))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=position, content_en="", content_mm=""); db.add(lesson); db.flush(); created_lessons += 1
            if not lesson.content_en or not lesson.content_en.strip():
                next_title = specs[position][0] if position < len(specs) else f"Module {module_number + 1} review" if module_number < 9 else "Node.js capstone review"
                lesson.title, lesson.slug, lesson.description = title, lesson.slug or slug, focus
                lesson.content_en = _content(module_number, title, focus, code, next_title); lesson.content_mm = _content_mm(title, focus, code, mm, next_title)
                lesson.duration_minutes, lesson.status, lesson.published = 50, "draft", False
            elif not lesson.published and "## Practical exercises" not in lesson.content_en and "## Exercises" in lesson.content_en:
                lesson.content_en = lesson.content_en.replace("## Exercises", "## Practical exercises", 1)
            example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
            if not example: db.add(CodeExample(lesson_id=lesson.id, title=f"{title} example", language="javascript", filename=f"module_{module_number:02d}.mjs", code=code, description="Safe local Node.js example; the Academy does not execute arbitrary code.", position=1))
            _ensure_quiz(db, lesson, title, focus); _ensure_exercise(db, lesson, title, focus, mm)
    db.flush()
    return {"created_modules": created_modules, "created_lessons": created_lessons, "planned_lessons": sum(len(items) for items in LESSONS.values())}
