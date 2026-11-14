"""Idempotent Advanced Java enterprise curriculum.

The first module is a complete, reviewable vertical slice. Later modules have
one authored foundation lesson each so no published module is empty; they are
explicitly not represented as a complete enterprise course until their deeper
labs and project material are authored.
"""
import json
import re
from sqlalchemy import select
from .models import CourseModule, Lesson, LessonQuiz, QuizQuestion, CodeExample

MODULES = [
    "Advanced Java Overview", "Advanced OOP & Design Principles", "Generics, Collections & Streams",
    "Functional Programming in Java", "Concurrency & Virtual Threads", "JVM Internals & Performance",
    "Maven, Gradle & Modular Projects", "Testing with JUnit & Mockito", "JDBC & Database Transactions",
    "Jakarta Servlet Fundamentals", "Jakarta Persistence & Hibernate", "Enterprise Architecture Patterns",
    "Spring Core & Dependency Injection", "Spring Boot Fundamentals", "REST API Development",
    "Spring Data JPA & PostgreSQL", "Spring Security Fundamentals", "OAuth2, OIDC & JWT",
    "Redis & Caching Strategies", "Messaging with Kafka", "Microservices Architecture",
    "Service Communication & Resilience", "Event-Driven Architecture", "Distributed Transactions & Sagas",
    "Advanced Testing & Testcontainers", "Logging, Metrics & Tracing", "Application Security & OWASP",
    "Docker & Containerization", "Kubernetes & Cloud Fundamentals", "CI/CD & Production Deployment",
    "API Design & Documentation", "System Design & Scalability", "Database Optimization",
    "Real-World Enterprise Projects", "Production Readiness & Operations", "Final Enterprise Capstone",
]

MODULE_ONE = [
    {
        "title": "What Makes Java Enterprise?",
        "topic": "the boundaries and operational expectations of backend systems",
        "theory": "Enterprise Java is not a single framework. It is a set of engineering practices for software that serves many users, integrates with other systems, protects data, and can be operated safely. A useful boundary separates HTTP delivery, application use cases, domain rules, persistence, and infrastructure. Java 25 LTS is the course target; Spring Boot 4.x examples require Java 17+ and should be checked against the selected Spring release before use.",
        "syntax": "public final class OrderService {\n    public Order place(PlaceOrder command) {\n        return repository.save(factory.create(command));\n    }\n}",
        "code": "public class Main {\n    public static void main(String[] args) {\n        String[] boundaries = {\"api\", \"application\", \"domain\", \"persistence\"};\n        System.out.println(String.join(\" -> \", boundaries));\n    }\n}",
        "output": "api -> application -> domain -> persistence",
        "mm": "Enterprise Java သည် framework တစ်ခုတည်းမဟုတ်ဘဲ API၊ application၊ domain နှင့် persistence boundary များကို စနစ်တကျ ခွဲခြားထားသော backend engineering ဖြစ်သည်။",
    },
    {
        "title": "Advanced Java Toolchain and Compatibility",
        "topic": "JDK toolchains, dependency compatibility, and reproducible builds",
        "theory": "A production repository declares its Java toolchain instead of depending on a developer's default JDK. Use Java 25 LTS for course examples. Spring Boot, Jakarta EE, Maven, Gradle, Hibernate, and database drivers each publish their own supported Java ranges; record those ranges in the README and CI configuration. Pin compatible dependency versions, run tests in CI, and avoid copying a version from an unrelated tutorial.",
        "syntax": "<properties>\n  <java.version>25</java.version>\n</properties>",
        "code": "public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"java.version=\" + System.getProperty(\"java.version\"));\n        System.out.println(\"toolchain=declared\");\n    }\n}",
        "output": "java.version=<installed JDK>\ntoolchain=declared",
        "mm": "JDK version နှင့် dependency compatibility ကို project နှင့် CI ထဲတွင် သတ်မှတ်ထားခြင်းက build မတူညီမှုများကို လျှော့ချပေးသည်။",
    },
    {
        "title": "Layered Architecture and Dependency Direction",
        "topic": "use cases, domain rules, adapters, and dependency inversion",
        "theory": "A layered design is useful when dependencies point toward stable business rules. Controllers translate transport data into commands. Application services coordinate a use case. Domain objects protect invariants. Repositories and clients are interfaces owned by the inner layer, with infrastructure implementations outside it. This makes tests faster and keeps framework details from becoming business rules.",
        "syntax": "public interface AccountRepository {\n    Account findById(AccountId id);\n}",
        "code": "public class Main {\n    public static void main(String[] args) {\n        String direction = \"adapter -> application -> domain\";\n        System.out.println(direction);\n        System.out.println(\"business rules stay framework-independent\");\n    }\n}",
        "output": "adapter -> application -> domain\nbusiness rules stay framework-independent",
        "mm": "Layered architecture တွင် outer adapter များက inner application နှင့် domain rule များကို အသုံးပြုရပြီး dependency direction ကို ထိန်းထားရသည်။",
    },
    {
        "title": "Dependency Injection and Configuration",
        "topic": "explicit collaborators, configuration boundaries, and testability",
        "theory": "Dependency injection supplies a class with the collaborators it needs rather than constructing global services inside the class. Configuration is externalized and validated at startup. Never place passwords or tokens in source code. In Spring, constructor injection is the default choice because required dependencies are visible and immutable.",
        "syntax": "public OrderService(OrderRepository repository, Clock clock) {\n    this.repository = repository;\n    this.clock = clock;\n}",
        "code": "public class Main {\n    public static void main(String[] args) {\n        String environment = System.getenv().getOrDefault(\"APP_ENV\", \"local\");\n        System.out.println(\"configuration source=environment\");\n        System.out.println(\"environment=\" + environment);\n    }\n}",
        "output": "configuration source=environment\nenvironment=local",
        "mm": "Dependency injection သည် collaborator များကို constructor မှတစ်ဆင့် ထည့်ပေးပြီး test လုပ်ရလွယ်ကူစေသည်။ Secret များကို source code ထဲမထည့်ပါနှင့်။",
    },
    {
        "title": "Transactions and Failure Boundaries",
        "topic": "atomic work, rollback, and explicit failure handling",
        "theory": "A transaction groups changes that must succeed or fail together. Keep transaction boundaries around a use case, not around every individual statement. Handle constraint violations and timeouts deliberately, and distinguish a business rejection from an infrastructure outage. A retry is safe only when the operation is idempotent or has a reliable idempotency key.",
        "syntax": "try (var connection = dataSource.getConnection()) {\n    connection.setAutoCommit(false);\n    // work\n    connection.commit();\n}",
        "code": "public class Main {\n    public static void main(String[] args) {\n        boolean committed = true;\n        System.out.println(committed ? \"transaction committed\" : \"transaction rolled back\");\n    }\n}",
        "output": "transaction committed",
        "mm": "Transaction သည် တစ်စုတစ်စည်းတည်း အောင်မြင်ခြင်း သို့မဟုတ် rollback ဖြစ်ခြင်းကို အာမခံပေးသည်။ Retry ပြုလုပ်ရန် idempotency ကို စစ်ဆေးပါ။",
    },
    {
        "title": "Secure Enterprise API Boundaries",
        "topic": "validation, authorization, and safe error responses",
        "theory": "An API boundary validates shape and size before application logic. Authentication identifies a caller; authorization checks whether that caller may perform the action. Return stable error codes without stack traces, secrets, SQL, or internal topology. Apply least privilege, request limits, audit events, and parameterized queries at the boundary where they belong.",
        "syntax": "if (!authorization.canEdit(user, resource)) {\n    throw new ForbiddenException();\n}",
        "code": "public class Main {\n    public static void main(String[] args) {\n        String[] controls = {\"validation\", \"authorization\", \"redaction\"};\n        for (String control : controls) {\n            System.out.println(control + \" enabled\");\n        }\n    }\n}",
        "output": "validation enabled\nauthorization enabled\nredaction enabled",
        "mm": "API boundary တွင် validation၊ authentication၊ authorization နှင့် error redaction ကို ခွဲခြားအကောင်အထည်ဖော်ပါ။",
    },
    {
        "title": "Module 1 Enterprise Architecture Assessment",
        "topic": "connecting architecture, compatibility, transactions, and security",
        "theory": "A reliable enterprise service has a documented boundary, a declared Java toolchain, explicit dependencies, controlled transactions, safe API errors, tests, and operational signals. Before adding a framework, write the use case, data ownership, failure modes, security rules, and compatibility matrix. This assessment prepares you for the Spring, persistence, messaging, and deployment modules.",
        "syntax": "record Compatibility(String java, String framework, String database) {}",
        "code": "public class Main {\n    public static void main(String[] args) {\n        String java = \"25 LTS\";\n        String framework = \"verify against selected release\";\n        System.out.println(java + \" / \" + framework);\n    }\n}",
        "output": "25 LTS / verify against selected release",
        "mm": "Assessment တွင် Java 25 LTS၊ framework compatibility၊ transaction၊ security နှင့် operations အခြေခံများကို ဆက်စပ်စဉ်းစားပါ။",
    },
]

GENERAL = [
    ("Advanced OOP with SOLID", "SOLID design and polymorphism"),
    ("Collections and Stream Pipelines", "type-safe data transformations"),
    ("Functional Composition", "pure functions and side-effect boundaries"),
    ("Virtual Threads and Structured Concurrency", "bounded concurrent work"),
    ("JVM Profiling Basics", "heap, allocation, and latency measurement"),
    ("Reproducible Maven and Gradle Builds", "declared toolchains and modules"),
    ("JUnit, Mockito, and Test Design", "unit boundaries and test doubles"),
    ("JDBC Transactions", "parameterized SQL and transaction scope"),
    ("Servlet Request Lifecycle", "HTTP filters and request boundaries"),
    ("JPA Persistence Context", "entities, mappings, and transaction safety"),
    ("Enterprise Architecture Patterns", "ports, adapters, and use cases"),
    ("Spring Dependency Injection", "beans and constructor injection"),
    ("Spring Boot Configuration", "profiles, health, and startup validation"),
    ("REST Resources and Errors", "HTTP contracts and validation"),
    ("Spring Data with PostgreSQL", "repositories and migrations"),
    ("Spring Security Authorization", "authentication and least privilege"),
    ("OAuth2, OIDC, and JWT Boundaries", "token validation and audience checks"),
    ("Redis Cache Safety", "TTL, invalidation, and stale data"),
    ("Kafka Consumer Reliability", "offsets, retries, and idempotency"),
    ("Microservice Boundaries", "service ownership and contracts"),
    ("Resilience Patterns", "timeouts, retries, and circuit breakers"),
    ("Event-Driven Workflows", "events and eventual consistency"),
    ("Sagas and Compensation", "distributed transaction alternatives"),
    ("Testcontainers Integration Tests", "real dependency verification"),
    ("Metrics, Logs, and Traces", "correlation and sensitive-data redaction"),
    ("OWASP API Security", "threat modeling and defensive controls"),
    ("Containerized Java Services", "small images and non-root execution"),
    ("Kubernetes Deployment Basics", "health probes and resource limits"),
    ("CI/CD Release Safety", "quality gates and rollback"),
    ("OpenAPI Contract Design", "documented stable interfaces"),
    ("System Design and Scalability", "capacity, consistency, and failure"),
    ("Database Query Optimization", "indexes and measured query plans"),
    ("Enterprise Project Architecture", "delivery of a maintainable backend"),
    ("Production Readiness Review", "operability, recovery, and ownership"),
    ("Final Capstone Architecture", "integrating an enterprise service"),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(title, topic, theory, syntax, code, output, previous, next_title):
    return f"""Introduction\n{title} introduces {topic} for Java 25 LTS enterprise services.\n\nLearning objectives\n- Explain {topic} and identify its boundary in a backend system.\n- Read and write maintainable Java with explicit failure and security boundaries.\n- Connect the example to tests, observability, and deployment decisions.\n\nPrerequisites\n{previous}\n\nDetailed theory\n{theory}\n\nArchitecture explanation\nPlace this responsibility behind a small application boundary. Keep domain decisions independent from HTTP, database drivers, cloud SDKs, and framework annotations where practical. Document the owner, data flow, failure modes, authorization rule, and operational signal before implementation.\n\nJava syntax and example\n{syntax}\n\nComplete source code\n```java\n{code}\n```\n\nExpected output\n{output}\n\nLine-by-line explanation\nThe class provides a runnable entry point. Local variables make the important state visible. The central statement demonstrates the lesson topic, and the final output is deterministic so a learner can compare behavior. In a real service, replace console output with a tested application boundary and structured logs.\n\nCommon mistakes\n- Coupling business rules directly to controllers or framework globals.\n- Retrying non-idempotent writes without an idempotency key.\n- Logging tokens, passwords, private payloads, or stack traces to users.\n- Using dependency versions without checking Java and framework compatibility.\n\nSecurity considerations\nValidate untrusted input, authorize every protected operation, use parameterized SQL, keep secrets outside source control, limit resources, and return redacted errors. Do not execute arbitrary student code inside the API process.\n\nBest practices\nUse constructor injection, immutable values, focused tests, explicit transactions, timeouts, metrics, trace correlation, dependency scanning, and documented Java 25 toolchains.\n\nPractical exercises\n- Easy: reproduce the example and document its boundary.\n- Medium: add validation and a failure test.\n- Advanced: design an adapter, integration test, metric, and security control for the same use case.\n\nQuiz\n1. Which boundary should own authorization? The protected application operation, enforced server-side.\n2. True or false: framework compatibility should be recorded and tested. True.\n3. What makes a retry safer? Idempotency or a reliable idempotency key.\n4. What must not appear in user-facing errors? Secrets, SQL, internal topology, and raw stack traces.\n\nSummary\nYou can now explain {topic} and evaluate its reliability, security, and operational consequences.\n\nNext lesson\n{next_title}\n"""

def _questions(topic):
    return [
        (f"Which practice best supports {topic}?", ["Documented boundaries and tests", "Global mutable state", "Secrets in source"], "Documented boundaries and tests", "Explicit boundaries and tests make enterprise behavior reviewable."),
        ("True or false: authentication and authorization are the same check.", ["True", "False"], "False", "Authentication identifies a caller; authorization checks permission."),
        ("Which database approach is safest for user input?", ["Prepared statements", "String concatenation", "Ignoring validation"], "Prepared statements", "Prepared statements keep values separate from SQL instructions."),
        ("What should be verified before using a framework dependency?", ["Java and framework compatibility", "Only its logo", "No information"], "Java and framework compatibility", "A declared compatibility matrix prevents unreliable builds."),
    ]

def seed_advanced_java_course(db, course):
    course.title = "Advanced Java — Enterprise Backend Engineering"
    course.short_description = "A free advanced Java 25 LTS course covering Spring, persistence, security, messaging, microservices, deployment, and enterprise architecture."
    course.description = "Build reliable enterprise backends with modern Java, Spring, PostgreSQL, security, messaging, observability, containers, and a production-focused capstone."
    course.level, course.status, course.published = "advanced", "published", True
    course.outcomes = "Design maintainable enterprise Java services|Build secure REST APIs with Spring|Use PostgreSQL, Redis, Kafka, and transactions safely|Test, observe, containerize, and deploy production services|Evaluate scalability and failure modes"
    course.requirements = "Completed Java Programming — From Zero to Advanced, Java fundamentals, SQL basics, Git, and HTTP. Target JDK: Java 25 LTS. Verify Spring Boot, Jakarta, Maven, Gradle, database-driver, and container compatibility in each project README."
    authored = []
    for module_index, module_title in enumerate(MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_index))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_index); db.add(module); db.flush()
        module.title = module_title
        if module_index == 1:
            specs = MODULE_ONE
        else:
            title, topic = GENERAL[module_index - 2]
            code = "public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"" + _slug(title) + " boundary ready\");\n    }\n}"
            specs = [{"title": title, "topic": topic, "theory": f"This foundation lesson explains {topic}. Use a small example first, then apply the concept inside a tested enterprise service. Choose the framework and dependency versions only after checking their Java 25 LTS compatibility.", "syntax": "public final class Service { /* explicit boundary */ }", "code": code, "output": f"{_slug(title)} boundary ready", "mm": f"ဤ lesson တွင် {topic} ကို enterprise service အတွင်း အသုံးချနည်းကို လေ့လာပါမည်။"}]
        for lesson_index, spec in enumerate(specs, 1):
            title, topic = spec["title"], spec["topic"]
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm=""); db.add(lesson); db.flush()
            previous = "Complete the Java beginner course and understand classes, collections, exceptions, SQL, and HTTP." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
            next_title = "Continue to the next lesson." if module_index < 36 else "Continue to the final capstone review."
            lesson.title, lesson.slug = title, slug
            lesson.content_en = _content(title, topic, spec["theory"], spec["syntax"], spec["code"], spec["output"], previous, next_title)
            lesson.content_mm = f"{title} ကို English theory နှင့်အတူ လေ့လာနိုင်ပါသည်။\n\n{spec['mm']}"
            lesson.description, lesson.duration_minutes = spec["theory"], 45
            lesson.status, lesson.published = "published", True; authored.append(lesson)
            examples = list(db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all())
            example = next((item for item in examples if item.position == 1), examples[0] if examples else None)
            for duplicate in examples:
                if duplicate is not example:
                    db.delete(duplicate)
            if not example:
                db.add(CodeExample(lesson_id=lesson.id, title=f"{title} example", language="java", filename="Main.java", code=spec["code"], description="Read-only source viewer. Hosted execution is disabled until an isolated, verified enterprise Java runner is configured.", position=1))
            else:
                example.title, example.language, example.filename, example.code, example.description = f"{title} example", "java", "Main.java", spec["code"], "Read-only source viewer. Hosted execution is disabled until an isolated, verified enterprise Java runner is configured."
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz:
                quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the architecture and security explanations, then retry missed concepts.", status="published"); db.add(quiz); db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(topic), 1):
                values = dict(prompt=prompt, question_type="true_false" if options == ["True", "False"] else "multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                question = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
                if not question: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(question, key, value)
    course.duration_minutes = sum(x.duration_minutes or 45 for x in authored)
    db.flush()
