"""Reviewable Spring Boot curriculum batch with EN/MM content and safe examples."""
import json
import re
from sqlalchemy import select
from .models import CodeExample, CodingExercise, CourseModule, Lesson, LessonQuiz, QuizQuestion

MODULES = {
    2: "Java and Spring Boot Foundations",
    3: "IoC, Dependency Injection and Configuration",
    4: "Spring MVC and REST APIs",
    5: "Data Access, JPA and PostgreSQL",
    6: "Validation, Transactions and Security",
    7: "Testing, Messaging and Integration",
    8: "Performance, Observability and Deployment",
    9: "Professional Spring Boot Capstone",
}

LESSONS = {
    2: [("Modern Java for Spring", "classes, interfaces, generics, records, and exceptions", "record Course(String id, String title) {}\nSystem.out.println(new Course(\"1\", \"Java\"));", "Spring မတိုင်မီ Java class၊ record၊ interface နှင့် exception အခြေခံများကို စနစ်တကျ လေ့လာပါ။"), ("Maven and Gradle Dependencies", "build files, dependency versions, plugins, and reproducible builds", "String dependency = \"org.springframework.boot:spring-boot-starter-web\";\nSystem.out.println(dependency);", "Dependency version နှင့် build file ကို lock/review လုပ်ပါ။"), ("Spring Boot Project Structure", "application entry points, packages, resources, profiles, and conventions", "String[] layers = {\"controller\", \"service\", \"repository\"};\nSystem.out.println(String.join(\" -> \", layers));", "Project package boundary နှင့် layer responsibility ကို ခွဲထားပါ။"), ("Configuration and Profiles", "externalized configuration, profiles, and secret boundaries", "String profile = System.getenv().getOrDefault(\"SPRING_PROFILES_ACTIVE\", \"local\");\nSystem.out.println(profile);", "Profile အလိုက် config ခွဲပြီး secret ကို source ထဲ မထည့်ပါနှင့်။")],
    3: [("Inversion of Control", "container ownership, bean lifecycle, and explicit dependencies", "class CourseService { }\nSystem.out.println(CourseService.class.getSimpleName());", "IoC container က object lifecycle ကို စီမံပြီး dependency ကို explicit ထားပါ။"), ("Constructor Dependency Injection", "constructor injection, testability, and immutable collaborators", "record CourseService(String repositoryName) {}\nSystem.out.println(new CourseService(\"course-repository\"));", "Constructor injection သုံးပြီး dependency နှင့် test boundary ကို ရှင်းပါ။"), ("Component Scanning and Bean Scope", "components, configuration classes, scope, and lifecycle risks", "String[] beans = {\"controller\", \"service\", \"repository\"};\nSystem.out.println(java.util.Arrays.toString(beans));", "Component scan နှင့် bean scope ကို မလိုအပ်ဘဲ ကျယ်မသွားစေရန် စီမံပါ။"), ("Configuration Properties and Profiles", "typed properties, environment overrides, and validation", "record ApiProperties(String baseUrl, int timeoutMs) {}\nSystem.out.println(new ApiProperties(\"https://example.invalid\", 1000));", "Typed property နှင့် environment override ကို validate လုပ်ပါ။")],
    4: [("Spring MVC Request Flow", "DispatcherServlet, controller, service, and response boundaries", "record Response(int status, String body) {}\nSystem.out.println(new Response(200, \"ok\"));", "Request မှ controller/service/response flow ကို နားလည်ပါ။"), ("REST Controllers and Status Codes", "resources, verbs, status codes, and idempotency", "record Endpoint(String method, String path, int status) {}\nSystem.out.println(new Endpoint(\"GET\", \"/courses\", 200));", "REST endpoint တွင် method၊ resource နှင့် status code ကို မှန်ကန်စွာ သတ်မှတ်ပါ။"), ("DTOs and Mapping", "controlled input/output models and entity exposure prevention", "record CourseDto(String title) {}\nSystem.out.println(new CourseDto(\"Spring\"));", "Entity ကို တိုက်ရိုက်မပြဘဲ DTO ဖြင့် response ထိန်းပါ။"), ("Global Exception Handling", "stable error envelopes, validation errors, and request IDs", "record ApiError(String code, String requestId) {}\nSystem.out.println(new ApiError(\"VALIDATION_ERROR\", \"req-1\"));", "Exception ကို safe error contract နှင့် request ID ဖြင့် ပြန်ပါ။")],
    5: [("JPA Entities and Repositories", "entity identity, repositories, and persistence boundaries", "record EntityPlan(String table, String idStrategy) {}\nSystem.out.println(new EntityPlan(\"courses\", \"uuid\"));", "Entity identity နှင့် repository responsibility ကို သတ်မှတ်ပါ။"), ("PostgreSQL Schema and Migrations", "schema ownership, additive migrations, and compatibility", "String[] migrationSteps = {\"add_column\", \"backfill\", \"deploy\"};\nSystem.out.println(java.util.Arrays.toString(migrationSteps));", "Migration ကို additive ဖြစ်စေပြီး production schema ကို reset မလုပ်ပါနှင့်။"), ("Transactions and Consistency", "transaction boundaries, isolation, and rollback", "record TransferPlan(boolean atomic, boolean rollbackOnError) {}\nSystem.out.println(new TransferPlan(true, true));", "Business operation အလိုက် transaction boundary နှင့် rollback သတ်မှတ်ပါ။"), ("Pagination and Query Safety", "bounded queries, indexes, sorting, and N+1 risks", "record PageRequest(int page, int size, String sort) {}\nSystem.out.println(new PageRequest(1, 20, \"title\"));", "Pagination size limit၊ index နှင့် N+1 query ကို စစ်ပါ။")],
    6: [("Bean Validation", "DTO constraints, validation messages, and trust boundaries", "record CreateCourse(String title) {}\nSystem.out.println(new CreateCourse(\"Java\"));", "Client input ကို Bean Validation ဖြင့် စစ်ပြီး server-side rule ထားပါ။"), ("Spring Security Filter Chain", "authentication, authorization, CSRF, and secure defaults", "String[] controls = {\"authentication\", \"authorization\", \"csrf\"};\nSystem.out.println(java.util.Arrays.toString(controls));", "Security filter chain နှင့် protected route ကို နားလည်ပါ။"), ("Password Hashing and Sessions", "password encoders, sessions, tokens, and expiration", "record SessionPolicy(String cookie, String expiry) {}\nSystem.out.println(new SessionPolicy(\"httpOnly\", \"15m\"));", "Password ကို hash လုပ်ပြီး session/token expiry ထည့်ပါ။"), ("RBAC and Object Authorization", "roles, ownership, method security, and least privilege", "record Permission(String role, String action, boolean allowed) {}\nSystem.out.println(new Permission(\"editor\", \"course:update\", true));", "Role check အပြင် object ownership ကို server-side စစ်ပါ။"), ("OAuth2 and External Identity", "issuer validation, scopes, audience, and token trust", "record TokenClaims(String issuer, String audience, String scope) {}\nSystem.out.println(new TokenClaims(\"issuer\", \"api\", \"courses:read\"));", "External token ကို issuer၊ audience နှင့် scope စစ်ပြီး ယုံပါ။")],
    7: [("Spring Boot Unit Tests", "slices, mocks, deterministic fixtures, and assertions", "record TestCase(String name, int expected) {}\nSystem.out.println(new TestCase(\"course read\", 200));", "Unit test တွင် deterministic fixture နှင့် meaningful assertion ထည့်ပါ။"), ("Integration Tests and Testcontainers", "realistic dependencies, isolation, and cleanup", "record TestEnvironment(String database, boolean disposable) {}\nSystem.out.println(new TestEnvironment(\"postgres\", true));", "Integration dependency ကို disposable environment ထဲမှာ စစ်ပါ။"), ("Messaging and Async Work", "events, retries, idempotency, and dead letters", "record Job(String id, int attempts, String status) {}\nSystem.out.println(new Job(\"job-1\", 1, \"queued\"));", "Async job တွင် idempotency၊ retry နှင့် dead-letter policy ထည့်ပါ။"), ("OpenAPI and Contract Compatibility", "API documentation, versioning, and consumer safety", "record ApiVersion(String path, String version) {}\nSystem.out.println(new ApiVersion(\"/api/courses\", \"v1\"));", "API contract ကို document လုပ်ပြီး breaking change ကို ထိန်းပါ။")],
    8: [("Caching with Redis", "cache keys, TTL, invalidation, and stale data", "record CacheEntry(String key, int ttlSeconds) {}\nSystem.out.println(new CacheEntry(\"course:1\", 60));", "Cache key၊ TTL နှင့် invalidation policy ကို သတ်မှတ်ပါ။"), ("Async Executors and Scheduling", "bounded executors, timeouts, and scheduled work", "record ExecutorPolicy(int threads, int timeoutMs) {}\nSystem.out.println(new ExecutorPolicy(4, 1000));", "Thread pool နှင့် timeout ကို bounded ဖြစ်အောင်ထားပါ။"), ("Observability and Health Checks", "structured logs, metrics, traces, and readiness", "String[] signals = {\"logs\", \"metrics\", \"traces\", \"health\"};\nSystem.out.println(java.util.Arrays.toString(signals));", "Health/readiness နှင့် request ID/metric ကို သတ်မှတ်ပါ။"), ("Docker and Production Configuration", "non-root containers, secrets, health checks, and rollback", "record ContainerPlan(String user, String healthPath, boolean rollback) {}\nSystem.out.println(new ContainerPlan(\"app\", \"/actuator/health\", true));", "Container ကို non-root၊ secret manager နှင့် rollback ဖြင့် deploy ပါ။")],
    9: [("Spring Boot Service Capstone", "layered architecture, contracts, security, tests, and handoff", "record ServicePlan(boolean dto, boolean auth, boolean tests) {}\nSystem.out.println(new ServicePlan(true, true, true));", "Capstone တွင် DTO၊ auth၊ test နှင့် operation plan ပါစေ။"), ("Production Readiness Review", "SLOs, dependencies, migration safety, and incident response", "String[] review = {\"slo\", \"migration\", \"rollback\", \"owner\"};\nSystem.out.println(java.util.Arrays.toString(review));", "Production မတိုင်မီ SLO၊ migration၊ rollback နှင့် owner စစ်ပါ။"), ("Secure Handoff and Documentation", "runbooks, threat model, data handling, and support ownership", "record Runbook(String owner, String escalation, boolean threatModel) {}\nSystem.out.println(new Runbook(\"team\", \"on-call\", true));", "Runbook နှင့် threat model ဖြင့် service handoff လုပ်ပါ။"), ("Final Spring Boot Assessment", "end-to-end evidence, limitations, and responsible release", "record Release(boolean tests, boolean review, boolean rollback) {}\nSystem.out.println(new Release(true, true, true));", "Release သည် test၊ review နှင့် rollback evidence ပြည့်စုံမှသာ ဖြစ်ရမည်။")],
}

def _slug(value): return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(module_number, title, focus, code, next_title):
    return f"""# {title}

## Introduction
This lesson develops {focus} in a secure, testable Spring Boot service.

## Prerequisites
Complete the preceding lesson in Module {module_number}; use a supported JDK and pinned build dependencies.

## Learning objectives
- Explain {focus} and its responsibility in a Spring Boot application.
- Inspect a typed example with explicit inputs, outputs, and failure behavior.
- Identify data, authorization, testing, and deployment risks.

## Detailed theory
{title} is useful only when its contract, transaction or request boundary, ownership, and operational limits are explicit. Spring conventions reduce boilerplate but do not replace validation, server-side authorization, tests, observability, or secure configuration.

## Main concepts
IoC boundary, constructor dependency injection, DTO contract, validation, transaction, persistence identity, least privilege, migration compatibility, metrics, and rollback are the core concepts.

## Syntax / API / command
```java
{code}
```

## Practical examples
### Example 1 — inspect
Run or read the safe example in a disposable local project and inspect its type, status, configuration, or contract.

### Example 2 — extend
Change one value or boundary, predict the result, and record the observed behavior. Add validation or authorization where the input is untrusted.

### Example 3 — verify
Add an assertion, controller contract test, repository test, migration check, or health signal. Compare it with the expectation.

## Dataset and reproducibility notes
Use synthetic records and a disposable local database. Record JDK, build tool, dependency versions, schema migration, input contract, expected output, and limitation. Never add credentials or platform production data.

## Expected output
The example should produce a small inspectable result related to {focus}. Verify types, status, transaction behavior, security boundary, and tests rather than inventing production claims.

## Line-by-line explanation
1. The first lines define a typed input, record, or reviewed API.
2. The central operation applies {focus} without accessing platform secrets or unrestricted data.
3. The final statement prints or asserts a result that should be compared with the stated expectation.

## Common mistakes
- Returning entities directly, skipping validation, or trusting frontend route guards.
- Missing transaction boundaries, unbounded queries, or N+1 database access.
- Hardcoding secrets, exposing stack traces, or accepting invalid tokens.
- Changing schemas destructively or deploying without rollback evidence.

## Best practices
- Use constructor injection, DTOs, Bean Validation, parameterized queries, pagination, least privilege, and focused tests.
- Externalize secrets, pin dependencies, document migrations, emit structured logs, expose safe health checks, and monitor SLOs.

## Security considerations
The Academy displays predefined Spring examples and simulations only. It does not execute arbitrary Java, connect to platform PostgreSQL, expose credentials, or provide unrestricted sandbox access. Enforce authentication and object authorization on the server.

## Exercises
1. Reproduce the example with synthetic data in a disposable project.
2. Add one validation, authorization, or error case and predict the result.
3. Write one focused test and one operational risk for this lesson.

## Practical exercises
Build a small local component for {focus} with a typed contract, validation, safe error behavior, focused test, and one limitation.

## Homework
Write a Spring implementation note with JDK/dependency versions, contract, observed behavior, test evidence, security boundary, migration note, and recovery plan.

## Quiz
1. What replaces frontend-only authorization? Server-side authentication and object authorization.
2. True or false: auto-configuration is a complete security policy. False.
3. What improves safe deployment? Tests, additive migrations, observability, externalized secrets, and rollback.

## Mini project
Design a local course API with Controller-Service-Repository layers, DTO validation, RBAC, PostgreSQL migration notes, tests, health checks, and a secure handoff runbook.

## Summary
You can now apply {focus} with Spring boundaries, data contracts, security, testing, and operations in view.

## Key takeaways
Professional Spring Boot services make dependencies, contracts, authorization, persistence, tests, and recovery visible.

## References
- Spring Boot documentation: https://docs.spring.io/spring-boot/docs/current/reference/html/
- Spring Security documentation: https://docs.spring.io/spring-security/reference/
- OWASP API Security: https://owasp.org/www-project-api-security/

## Next lesson
{next_title}
"""

def _content_mm(title, focus, code, mm, next_title):
    return f"""# {title}

## မိတ်ဆက်
ဤ lesson တွင် {mm} ကို secure၊ testable Spring Boot service အတွင်း လေ့လာပါမည်။

## လိုအပ်ချက်
Module {title} မတိုင်မီ lesson များကို ပြီးစီးထားပြီး supported JDK နှင့် pinned dependency သုံးပါ။

## လေ့လာရမည့် ရည်မှန်းချက်များ
- {mm} ၏ Spring Boot အတွင်းရှိ တာဝန်ကို ရှင်းပြနိုင်ရန်။
- Typed example ၏ input၊ output နှင့် failure ကို စစ်နိုင်ရန်။
- Data၊ authorization၊ testing နှင့် deployment risk ကို ဖော်ထုတ်နိုင်ရန်။

## အသေးစိတ်သီအိုရီ
{mm} ကို အသုံးပြုရာတွင် contract၊ transaction/request boundary၊ ownership နှင့် operation limitation ကို ရှင်းလင်းရပါမည်။ Spring convention သည် validation၊ server-side authorization၊ test နှင့် secure configuration အစားမဖြစ်ပါ။

## အဓိကအယူအဆများ
IoC၊ constructor injection၊ DTO၊ validation၊ transaction၊ persistence identity၊ least privilege၊ migration compatibility၊ metric နှင့် rollback ကို မှတ်တမ်းတင်ပါ။

## Syntax / API / command
```java
{code}
```

## လက်တွေ့ဥပမာများ
Disposable local project တွင် example ကို run/read ပါ။ Value တစ်ခု ပြောင်းပြီး result ကို ကြိုခန့်မှန်းပါ။ နောက်ဆုံးတွင် assertion၊ controller test၊ migration check သို့မဟုတ် health signal ထည့်ပါ။

## Dataset နှင့် ပြန်လည်လုပ်ဆောင်နိုင်မှု
Synthetic record နှင့် disposable local database သုံးပါ။ JDK၊ build tool၊ dependency၊ schema migration၊ contract၊ expected output နှင့် limitation ကို မှတ်တမ်းတင်ပါ။ Credential နှင့် production data မထည့်ပါနှင့်။

## မျှော်မှန်းရလဒ်
Example သည် {mm} နှင့် သက်ဆိုင်သော inspect လုပ်နိုင်သည့် result ပေးရမည်။ Type၊ status၊ transaction၊ security boundary နှင့် test ကို စစ်ပါ။

## Code ရှင်းလင်းချက်
အစတွင် typed input/record/API ကို သတ်မှတ်သည်။ အလယ်တွင် feature ကို အသုံးပြုပြီး platform secret/data ကို မထိတွေ့စေပါ။ နောက်ဆုံးတွင် result ကို print/assert လုပ်သည်။

## အများဆုံးမှားတတ်သောအချက်များ
- Entity ကို တိုက်ရိုက်ပြခြင်း၊ validation မလုပ်ခြင်း၊ frontend guard ကိုသာ ယုံခြင်း။
- Transaction မထားခြင်း၊ unbounded query/N+1 query ဖြစ်ခြင်း။
- Secret hardcode လုပ်ခြင်း၊ stack trace/token ဖော်ပြခြင်း။
- Schema ကို destructive ပြောင်းခြင်း၊ rollback evidence မရှိဘဲ deploy လုပ်ခြင်း။

## ကောင်းမွန်သောနည်းလမ်းများ
Constructor injection၊ DTO၊ Bean Validation၊ parameterized query၊ pagination၊ least privilege၊ focused test၊ externalized secret၊ pinned dependency၊ migration review၊ structured log၊ health check နှင့် SLO သုံးပါ။

## Security considerations
Academy သည် predefined Spring example နှင့် simulation သာ ပြသသည်။ Arbitrary Java ကို execute မလုပ်ဘဲ platform PostgreSQL/credential ကို မထိပါ။ Authorization ကို server-side စစ်ပါ။

## လေ့ကျင့်ခန်း
1. Disposable project တွင် synthetic data ဖြင့် example ကို ပြန်လုပ်ပါ။
2. Validation၊ authorization သို့မဟုတ် error case တစ်ခု ထည့်ပါ။
3. Focused test တစ်ခုနှင့် operational risk တစ်ခု ရေးပါ။

## Practical exercises
{focus} အတွက် typed contract၊ validation၊ safe error၊ focused test နှင့် limitation ပါသော local component တည်ဆောက်ပါ။

## အိမ်စာ
JDK/dependency version၊ contract၊ observed behavior၊ test evidence၊ security boundary၊ migration note နှင့် recovery plan ပါသော note ရေးပါ။

## Quiz
1. Frontend-only authorization အစား ဘာလိုသနည်း။ Server-side authentication နှင့် object authorization လိုသည်။
2. Auto-configuration သည် complete security policy ဖြစ်သလား။ မဖြစ်ပါ။
3. Safe deployment အတွက် test၊ additive migration၊ observability၊ externalized secret နှင့် rollback လိုသည်။

## Mini project
Controller-Service-Repository layer၊ DTO validation၊ RBAC၊ PostgreSQL migration note၊ test၊ health check နှင့် secure runbook ပါသော local course API design လုပ်ပါ။

## အနှစ်ချုပ်
{mm} ကို Spring boundary၊ data contract၊ security၊ testing နှင့် operation ဖြင့် အသုံးပြုနိုင်ပါပြီ။

## Key takeaways
Professional Spring Boot service သည် dependency၊ contract၊ authorization၊ persistence၊ test နှင့် recovery ကို ရှင်းလင်းရသည်။

## References
Spring Boot၊ Spring Security နှင့် OWASP API Security documentation ကို project version နှင့် ကိုက်ညီအောင် ဖတ်ပါ။

## နောက် lesson
{next_title}
"""

def _ensure_quiz(db, lesson, title, focus):
    quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
    if not quiz:
        quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review Spring boundaries, validation, authorization, testing, and deployment before retrying.", status="draft"); db.add(quiz); db.flush()
    questions = [(f"Which practice supports {focus}?", ["Use typed contracts, validation, and focused tests", "Trust all client values", "Expose entities and secrets"], "Use typed contracts, validation, and focused tests", "Safe Spring applications make contracts and boundaries explicit."), ("True or false: frontend guards replace server authorization.", ["True", "False"], "False", "Every protected action must be authorized on the server."), ("Where should credentials be stored?", ["Externalized server-side secret configuration", "Source code", "DTO response"], "Externalized server-side secret configuration", "Credentials must not be committed or returned to clients.")]
    for position, (prompt, options, answer, explanation) in enumerate(questions, 1):
        row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
        values = {"prompt": prompt, "question_type": "true_false" if options == ["True", "False"] else "multiple_choice", "options_json": json.dumps(options), "correct_answer": answer, "explanation": explanation}
        if not row: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))

def _ensure_exercise(db, lesson, title, focus, mm):
    slug = f"spring-boot-{lesson.slug}-practice"
    if db.scalar(select(CodingExercise).where(CodingExercise.slug == slug)): return
    db.add(CodingExercise(lesson_id=lesson.id, title=f"{title} practice", slug=slug, description_en=f"Practice {focus} in a disposable Spring Boot project with DTO validation, a focused test, safe errors, and one limitation. Do not connect platform infrastructure.", description_mm=f"Disposable Spring Boot project တွင် {mm} ကို လေ့ကျင့်ပါ။ DTO validation၊ focused test၊ safe error နှင့် limitation ထည့်ပါ။ Platform infrastructure မချိတ်ပါနှင့်။", difficulty="intermediate", language="java", starter_code="// Work in a disposable local Spring Boot project.\n", status="draft"))

def seed_spring_boot_additional_curriculum(db, course):
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
                next_title = specs[position][0] if position < len(specs) else f"Module {module_number + 1} review" if module_number < 9 else "Spring Boot capstone review"
                lesson.title, lesson.slug, lesson.description = title, lesson.slug or slug, focus
                lesson.content_en = _content(module_number, title, focus, code, next_title); lesson.content_mm = _content_mm(title, focus, code, mm, next_title)
                lesson.duration_minutes, lesson.status, lesson.published = 50, "draft", False
            elif not lesson.published and "## Practical exercises" not in lesson.content_en and "## Exercises" in lesson.content_en:
                lesson.content_en = lesson.content_en.replace("## Exercises", "## Practical exercises", 1)
            example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
            if not example: db.add(CodeExample(lesson_id=lesson.id, title=f"{title} example", language="java", filename=f"module_{module_number:02d}.java", code=code, description="Safe local Spring Boot example; the Academy does not execute arbitrary Java.", position=1))
            _ensure_quiz(db, lesson, title, focus); _ensure_exercise(db, lesson, title, focus, mm)
    db.flush()
    return {"created_modules": created_modules, "created_lessons": created_lessons, "planned_lessons": sum(len(items) for items in LESSONS.values())}
