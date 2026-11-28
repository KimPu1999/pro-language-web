"""Idempotent Spring Boot vertical-slice course content seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion
from .spring_boot_complete_curriculum import _ensure_exercise, seed_spring_boot_additional_curriculum

PLANNED_MODULES = [
    "Introduction to Spring Boot", "Java Fundamentals for Spring Boot", "Development Environment Setup",
    "Spring Initializr & First Application", "Spring Framework Fundamentals", "Dependency Injection & Bean Lifecycle",
    "Spring Boot Project Architecture", "Configuration & Profiles", "Spring MVC Fundamentals", "REST API Development",
    "Request & Response Handling", "DTOs & Bean Validation", "Global Exception Handling", "Spring Data JPA Fundamentals",
    "Hibernate & ORM", "PostgreSQL Integration", "Database Migrations", "Advanced JPA & Transactions",
    "Spring Security Fundamentals", "JWT Authentication", "OAuth2 & OpenID Connect", "RBAC & Method Security",
    "Password Security & Account Recovery", "API Security & OWASP", "Redis & Spring Cache", "Async Processing & Scheduling",
    "Messaging & Event-Driven Systems", "File Uploads & Storage", "Email & Notifications", "WebSocket & Real-Time Applications",
    "API Documentation with OpenAPI", "Testing Spring Boot Applications", "Integration Testing & Testcontainers",
    "Microservices Architecture", "Spring Cloud Fundamentals", "Performance & Observability", "Docker, CI/CD & Deployment",
    "Enterprise Security & Production Hardening", "Professional Spring Boot Projects", "Final Spring Boot Capstone",
]

MODULE_ONE = [
    ("What Spring Boot Is", "convention over configuration, embedded servers, and production boundaries", "@SpringBootApplication\npublic class AcademyApplication {\n    public static void main(String[] args) {\n        SpringApplication.run(AcademyApplication.class, args);\n    }\n}", "java", "Spring Boot packages Spring application conventions, auto-configuration, dependency management, embedded runtime support, and operational defaults. It accelerates delivery but does not automatically secure authorization, secrets, database queries, or deployment. Keep the platform FastAPI backend separate; Spring Boot is the course subject.", "Spring Boot သည် Spring application များအတွက် convention၊ auto-configuration နှင့် embedded runtime ကိုပေးသည်။ Authorization၊ secret နှင့် deployment security ကို အလိုအလျောက်မလုပ်ပေးပါ။", "List three Spring Boot conveniences and three controls that still belong to the application team.", ("Spring Boot ၏ အဓိကအားသာချက်က ဘာလဲ?", ["Convention-based application setup", "Automatic authorization for every object", "A replacement for PostgreSQL"], "Convention-based application setup", "Boot reduces setup work while application policy and security remain explicit.")),
    ("Java and Spring Toolchain", "JDK, Maven/Gradle, Spring Initializr, and reproducible builds", "java --version\n./mvnw test\n./mvnw spring-boot:run", "bash", "A supported JDK and reviewed Maven or Gradle dependencies make builds reproducible. Use the project wrapper, lock or review dependency versions, keep secrets outside source, and test in disposable local environments. The Academy displays commands but never runs student Java applications on production.", "JDK၊ Maven/Gradle နှင့် Spring Initializr သည် project setup ၏ အခြေခံဖြစ်သည်။ Dependency version၊ secret နှင့် build ကိုစနစ်တကျထိန်းချုပ်ပါ။", "Create a local starter project, record the JDK and build tool version, and define a cleanup step.", ("Spring Boot project build အတွက် ဘာကိုသုံးသင့်သနည်း?", ["A reviewed JDK and Maven/Gradle wrapper", "A production shell with copied secrets", "An arbitrary public server"], "A reviewed JDK and Maven/Gradle wrapper", "Reproducible tooling improves review and release confidence.")),
    ("Spring Application Context", "IoC, components, beans, and dependency injection", "@Service\npublic class CourseService {\n    private final CourseRepository repository;\n\n    public CourseService(CourseRepository repository) {\n        this.repository = repository;\n    }\n}", "java", "The application context creates and wires managed beans. Constructor injection makes dependencies visible, supports testing, and avoids partially initialized objects. Component scanning and auto-configuration should be bounded and understood; do not treat a bean annotation as an authorization policy.", "Application context သည် managed bean များကိုဖန်တီးပြီး dependency injection ဖြင့်ချိတ်ဆက်သည်။ Constructor injection သည် dependency ကို explicit ဖြစ်စေသည်။", "Sketch a Controller-Service-Repository dependency graph and identify where authorization belongs.", ("Constructor injection ၏ အကျိုးက ဘာလဲ?", ["Dependencies are explicit and testable", "It bypasses authentication", "It stores secrets automatically"], "Dependencies are explicit and testable", "Explicit dependencies improve design and test isolation.")),
    ("Spring MVC and REST Controllers", "routes, request mapping, status codes, and API boundaries", "@RestController\n@RequestMapping(\"/api/courses\")\nclass CourseController {\n    @GetMapping(\"/{id}\")\n    ResponseEntity<CourseDto> get(@PathVariable UUID id) { return ResponseEntity.ok(service.get(id)); }\n}", "java", "Spring MVC maps HTTP requests to controller methods. Keep controllers thin, validate path/query/body values, return intentional status codes, and delegate business rules to services. Route parameters are not proof of access; each resource query needs server-side authentication and authorization.", "Spring MVC သည် HTTP request ကို controller method သို့ map လုပ်သည်။ Controller ကို thin ထားပြီး validation နှင့် authorization ကို server-side တွင်ပြုလုပ်ပါ။", "Design GET and POST contracts with status codes for success, validation failure, missing resource, and forbidden access.", ("REST controller တွင် ဘာကိုမယုံသင့်သနည်း?", ["A client-supplied id as authorization proof", "Validated request data", "An explicit response status"], "A client-supplied id as authorization proof", "Resource access must be authorized on the server.")),
    ("DTOs and Bean Validation", "request contracts, validation annotations, and safe response shapes", "public record CreateCourseRequest(\n    @NotBlank @Size(max = 120) String title,\n    @Pattern(regexp = \"[a-z0-9-]+\") String slug\n) {}", "java", "DTOs keep API contracts separate from persistence entities. Bean Validation rejects malformed input at the boundary, but business authorization and context-specific output safety remain necessary. Return only fields the caller is allowed to see and use consistent validation error responses.", "DTO သည် API contract ကို persistence entity နှင့်ခွဲထားသည်။ Bean Validation သည် malformed input ကိုတားပေးသော်လည်း authorization ကိုအစားမထိုးပါ။", "Create a DTO with title, slug, page size, and validation rules; define a structured 400 response.", ("DTO ၏ အဓိကအကျိုးက ဘာလဲ?", ["Separate API contracts from persistence entities", "Expose every database column", "Grant admin permission"], "Separate API contracts from persistence entities", "DTOs limit and validate data at the API boundary.")),
    ("Spring Data JPA and PostgreSQL", "entities, repositories, query boundaries, and transactions", "@Entity\nclass Course {\n    @Id UUID id;\n    @Column(nullable = false, unique = true) String slug;\n}\n\ninterface CourseRepository extends JpaRepository<Course, UUID> {}", "java", "JPA maps entities to relational data and repositories provide repeatable access patterns. Define constraints and indexes, use parameterized derived or explicit queries, bound pagination, and choose transaction boundaries deliberately. Do not connect student database exercises to platform PostgreSQL.", "JPA သည် entity ကို relational data နှင့် map လုပ်ပြီး repository သည် data access pattern ကိုစီမံသည်။ Constraint၊ index၊ pagination နှင့် transaction ကိုသေချာသတ်မှတ်ပါ။", "Model a course and enrollment relationship with a unique slug, owner scope, and paginated repository method.", ("Student database lab သည် ဘယ် database ကိုသုံးသင့်သနည်း?", ["A disposable local database or simulator", "Platform production PostgreSQL", "A public database with credentials"], "A disposable local database or simulator", "Practice must be isolated from platform data.")),
    ("Spring Security and Authorization", "authentication, JWT/session boundaries, RBAC, and object access", "@PreAuthorize(\"hasAuthority('course:read')\")\n@GetMapping(\"/{id}\")\nCourseDto get(@PathVariable UUID id) { ... }", "java", "Spring Security provides filter-chain and authorization building blocks. Authentication establishes identity; authorization decides whether that identity may perform this action on this object. Validate tokens server-side, use secure password hashing, deny by default, and test horizontal and vertical access. Frontend guards are not a backend security boundary.", "Spring Security သည် filter chain နှင့် authorization building blocks ကိုပေးသည်။ Authentication နှင့် object-level authorization နှစ်ခုလုံးလိုအပ်သည်။", "Write an access matrix for student, instructor, and admin; add an object ownership rule for course progress.", ("Frontend guard သည် backend authorization အစားထိုးနိုင်သလား?", ["မနိုင်ပါ; backend must enforce it", "အမြဲအစားထိုးနိုင်သည်", "Only for admin routes"], "မနိုင်ပါ; backend must enforce it", "Client navigation is not a security boundary.")),
    ("Testing and First Spring API Workflow", "unit/integration tests, safe errors, build checks, and release evidence", "@WebMvcTest(CourseController.class)\nclass CourseControllerTest {\n    @Test void returnsNotFoundForMissingCourse() { ... }\n}", "java", "A professional Spring workflow combines formatting, compile checks, unit tests, MVC tests, integration tests with disposable dependencies, dependency review, safe error responses, and observability. The course tools simulate requests and responses; they do not run arbitrary Java or contact production APIs.", "Spring workflow တွင် compile၊ unit/MVC/integration test၊ dependency review၊ safe error နှင့် observability evidence ပါဝင်သည်။", "Define tests for an allowed request, invalid DTO, missing course, and cross-user access denial.", ("Secure API workflow တွင် ဘာတွေပါသနည်း?", ["Tests, validation, authorization, and reviewed dependencies", "Only a browser screenshot", "Running untrusted apps on production"], "Tests, validation, authorization, and reviewed dependencies", "Evidence comes from repeatable checks and explicit boundaries.")),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, example, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "No Spring Boot experience is required; basic Java and HTTP concepts help." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the REST API simulator and architecture explorer."
    return f"""Introduction
{title} introduces {topic} through safe, reproducible Spring Boot practice.

Learning objectives
- Explain {topic} and its Spring/Java/runtime boundary.
- Design typed API, persistence, validation, and authorization contracts.
- Verify behavior with tests without running untrusted applications on platform infrastructure.

Prerequisites
{prerequisite}

Spring architecture diagram
HTTP client -> Security filter chain -> Controller -> Service -> Repository/JPA -> PostgreSQL
                                      |-> validation/errors/observability

Detailed theory
{theory}

Java/Spring example ({language})
{example}

Expected API output
Exact JSON and stack traces vary by Spring Boot and JDK versions. Verify status code, response shape, validation behavior, logs, and transaction outcome.

Step-by-step implementation
1. Create a disposable project with a supported JDK and reviewed dependencies.
2. Define DTOs and validation before exposing a controller endpoint.
3. Keep business rules in services and data access behind repository boundaries.
4. Enforce authentication, object authorization, safe errors, and least privilege server-side.
5. Add unit/MVC/integration tests, dependency checks, and cleanup before release.

Interactive visualizer
Use the Spring Boot playground, REST API lab, architecture explorer, database lab, security lab, and guided labs. They are deterministic simulations and do not run arbitrary Java or contact platform databases.

Common errors
- Treating auto-configuration as a security policy.
- Returning entities directly instead of controlled DTOs.
- Missing transaction boundaries or unbounded queries.
- Relying on frontend route guards instead of backend authorization.
- Hardcoding secrets or accepting invalid DTOs.

Troubleshooting
Check JDK and dependency versions, package scanning, profile configuration, route mappings, validation messages, transaction logs, database schema, security filter order, and the first stack trace line you own.

Best practices
- Use constructor injection, DTOs, validation, parameterized queries, pagination, secure password hashing, least privilege, structured logs, tests, dependency review, and externalized secrets.
- Keep PostgreSQL authoritative when durability and relational integrity are required; use Redis only for explicit cache or coordination needs.

Security considerations
The Academy displays predefined Java/Spring examples and simulated requests only. It does not execute arbitrary student Java, expose credentials, connect to platform PostgreSQL, call production APIs, or provide unrestricted sandbox access.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Build a small typed Spring Boot course API design with Controller-Service-Repository boundaries, DTO validation, an authorization rule, a safe error contract, and tests for success and denial.

Summary
You can now reason about {topic} with Spring boundaries, data contracts, security, testing, and operations in view.

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
IoC boundaries, typed contracts, validation, transactions, authorization, observability, and recovery are the core concepts for this lesson.

## Syntax and usage
```java
{code}
```

## Expected output
Inspect the type, response, configuration, database, or test result and compare it with the stated contract. Exact runtime output can vary by JDK and dependency version.

## Line-by-line explanation
Read declarations first, trace input through the Spring boundary, and compare the result with the expectation. Change one value at a time and rerun the focused test.

## Common mistakes
- Returning entities directly, skipping validation, or trusting frontend-only route guards.
- Missing transaction boundaries, unbounded queries, or N+1 access.
- Hardcoding secrets, exposing stack traces, or accepting invalid tokens.

## Best practices
- Use constructor injection, DTOs, Bean Validation, parameterized queries, pagination, least privilege, tests, and additive migrations.
- Externalize secrets, emit structured logs, expose safe health checks, and define rollback criteria.

## Practical exercises
{exercise}

## Homework
Write a Spring implementation note with JDK/dependency versions, contract, test evidence, security boundary, migration note, and recovery plan.

## Related references
- Spring Boot documentation: https://docs.spring.io/spring-boot/docs/current/reference/html/
- Spring Security documentation: https://docs.spring.io/spring-security/reference/
- OWASP API Security: https://owasp.org/www-project-api-security/

## Key takeaways
Professional Spring Boot services make dependencies, contracts, authorization, persistence, tests, and recovery visible.
"""
    if "## အသေးစိတ်သီအိုရီ" not in (lesson.content_mm or ""):
        lesson.content_mm = (lesson.content_mm or "") + f"""

## အသေးစိတ်သီအိုရီ
{mm}

## လက်တွေ့လေ့ကျင့်ခန်း
{exercise}

## အိမ်စာ
JDK/dependency version၊ contract၊ test evidence၊ security boundary၊ migration note နှင့် recovery plan ကို မှတ်တမ်းတင်ပါ။

## ဆက်စပ်ရည်ညွှန်းချက်
Spring Boot၊ Spring Security နှင့် OWASP API Security documentation ကို project version နှင့် ကိုက်ညီအောင် ဖတ်ပါ။
"""


def seed_spring_boot_course(db, course):
    course.title = "Spring Boot — From Zero to Professional Java Backend Developer"
    course.short_description = "A free practical path through Spring Boot, MVC, REST APIs, JPA, PostgreSQL, Security, Redis, testing, microservices, and deployment."
    course.description = "Learn Spring Boot from Java and IoC fundamentals through dependency injection, MVC, REST APIs, DTO validation, JPA/Hibernate, PostgreSQL, Flyway, transactions, Spring Security, JWT/OAuth2, RBAC, Redis, async work, messaging, WebSockets, OpenAPI, testing, Testcontainers, microservices, observability, Docker, CI/CD, and production hardening."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 55
    course.outcomes = "Build typed Spring Boot applications with IoC, dependency injection, MVC, REST controllers, DTOs, validation, and safe exception handling|Integrate JPA/Hibernate, PostgreSQL, migrations, transactions, Redis, async work, messaging, and WebSockets|Implement Spring Security, JWT/OAuth2, RBAC, password security, object authorization, and OWASP-aware APIs|Test, observe, containerize, and prepare Spring Boot services for microservice and production deployment"
    course.requirements = "Basic Java, HTTP, and SQL familiarity are helpful; no Spring Boot experience is required."
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
            lesson.duration_minutes, lesson.status, lesson.published = 55, "published", True
        _repair_module_one_sections(lesson, item)
        values = {"title": f"{title} example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe Spring Boot example for local study; the Academy does not execute arbitrary Java.", "position": 1}
        example_row = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        if not example_row:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example_row, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review Spring boundaries, DTOs, data access, authorization, tests, and secure configuration before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: a frontend route guard replaces Spring Security authorization.", ["True", "False"], "False", "Authorization must be enforced server-side for every protected object and action."),
            ("Where should student Spring applications run for practice?", ["A disposable local project or isolated sandbox", "The platform production host", "The platform PostgreSQL server"], "A disposable local project or isolated sandbox", "Practice code and database work must stay isolated from platform infrastructure."),
        ]
        for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
            row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
            values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
            if not row:
                db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
            else:
                for key, value in values.items():
                    setattr(row, key, value)
        _ensure_exercise(db, lesson, title, item[6], f"{item[5]} ကို disposable Spring Boot project ထဲတွင် လက်တွေ့လေ့ကျင့်ပါ။")
    db.flush()
    additional_report = seed_spring_boot_additional_curriculum(db, course)
    course.duration_minutes = sum(
        lesson.duration_minutes or 50
        for module in db.scalars(select(CourseModule).where(CourseModule.course_id == course.id)).all()
        for lesson in db.scalars(select(Lesson).where(Lesson.module_id == module.id)).all()
    )
    db.flush()
    return additional_report
