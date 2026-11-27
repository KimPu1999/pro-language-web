"""Idempotently seed the Phase 03 learning path catalog.

This importer creates path metadata and path specific stage/step relationships
only when the records do not already exist. It never copies courses, modules,
lessons, or learner progress. Run it after ``alembic upgrade head`` and the
normal course seed:

    PYTHONPATH=. .venv/bin/python scripts/seed_learning_paths.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.db import SessionLocal
from app.models import CareerRoadmap, Course, RoadmapStage, RoadmapStep, RoadmapStepResource


def topics(value: str) -> list[str]:
    return [item.strip() for item in value.split("|") if item.strip()]


# The phase names are deliberately domain-specific. The target count follows
# the Phase 03 curriculum contract; any final phases are production studios
# that turn the preceding concepts into a coherent deliverable.
CATALOG: list[tuple[str, str, str, int, str]] = [
    ("Computer Science Fundamentals", "computer-science-fundamentals", "Computer Science", 15, "Computer systems|Number systems and digital logic|Computer architecture|Programming models|Discrete mathematics|Data structures|Algorithms|Complexity analysis|Operating systems|Computer networking|Database fundamentals|Software engineering|Distributed computing|Systems design studio|Computer science capstone"),
    ("Programming Fundamentals", "programming-fundamentals", "Foundations", 12, "Development environment|Variables and data types|Operators and expressions|Control flow|Loops and iteration|Functions and decomposition|Collections and strings|Debugging and testing|Object-oriented foundations|Problem solving patterns|Foundational project studio|Programming portfolio project"),
    ("Frontend Developer", "frontend-developer", "Web Development", 20, "HTML5 document structure|CSS3 layout|Responsive design|Web accessibility|JavaScript essentials|DOM programming|Browser APIs|TypeScript foundations|Git and GitHub|Tailwind CSS|React fundamentals|React hooks|State management|Routing and navigation|API integration|Next.js applications|Frontend testing|Performance optimization|Frontend security|Professional frontend capstone"),
    ("Backend Developer", "backend-developer", "Backend Development", 25, "Backend foundations|HTTP and networking|Server-side programming|Framework architecture|REST API design|Data modeling|SQL databases|ORM and migrations|Validation and error handling|Authentication|Authorization and RBAC|Transactions|Caching|Background jobs|Messaging|File storage|WebSockets|Automated testing|Application security|Observability|Docker|Cloud deployment|Framework specialization|Production operations|Backend capstone"),
    ("Full-Stack Developer", "full-stack-developer", "Web Development", 30, "Computer science foundations|Development environment|Programming fundamentals|HTML5|CSS3|Responsive web design|JavaScript fundamentals|Advanced JavaScript|TypeScript|Git and GitHub|React fundamentals|Advanced React|Tailwind CSS|Next.js|Backend fundamentals|Node.js and Express.js|Python and FastAPI|PHP and Laravel|SQL and PostgreSQL|Database design and optimization|REST API architecture|Authentication and authorization|Full-stack application development|Testing and debugging|Web application security|Redis and performance|Docker and CI/CD|Cloud deployment|Enterprise system design|Professional capstone"),
    ("Software Engineer", "software-engineer", "Software Engineering", 30, "Computer science|Programming|Object-oriented design|Data structures|Algorithms|Clean code|SOLID principles|Design patterns|Requirements engineering|Version control|Software architecture|Database engineering|API design|Unit testing|Integration testing|System testing|DevOps practices|Distributed systems|Security engineering|Documentation|Code review|Team collaboration|Reliability|Performance|Technical leadership|Refactoring studio|Architecture decision records|Production operations|Engineering portfolio|Software engineering capstone"),
    ("Mobile App Developer", "mobile-app-developer", "Mobile Development", 25, "Mobile foundations|Dart language|Flutter widgets|Navigation|Forms and validation|State management|Animations|Responsive layouts|REST APIs|Authentication|Local databases|Offline-first architecture|Notifications|Device permissions|Camera integration|Secure storage|Mobile testing|Accessibility|Performance|Mobile security|App release workflows|Kotlin specialization|React Native specialization|Cross-platform architecture|Mobile capstone"),
    ("Python Developer", "python-developer", "Python", 25, "Python foundations|Data types and operators|Conditions and loops|Functions|Collections|Modules and packages|Object-oriented Python|Exceptions|Files and serialization|Regular expressions|Decorators|Generators and iterators|Type hints|Async programming|Testing|SQL with Python|Automation|FastAPI|Django|Performance|Security|Packaging and deployment|Professional tooling|Production service|Python capstone"),
    ("Java Developer", "java-developer", "Java", 30, "Java foundations|Object-oriented Java|Collections|Generics|Exceptions|Lambdas|Streams|Concurrency|JVM internals|JDBC|Maven|Gradle|Testing|Design patterns|Spring Framework|Spring Boot|Spring Security|JPA|Hibernate|REST APIs|Messaging|Microservices|Observability|Performance tuning|Cloud deployment|Enterprise integration|Transactions|Security hardening|Architecture studio|Enterprise Java capstone"),
    ("PHP and Laravel Developer", "php-laravel-developer", "PHP", 30, "PHP syntax|PHP types and functions|Object-oriented PHP|Composer|MVC architecture|Laravel application structure|Routing and controllers|Blade templates|Eloquent ORM|PostgreSQL|Relationships|Migrations|Validation|Authentication|Sanctum APIs|Authorization|Events and listeners|Queues|Caching|Notifications|API development|Testing|Security|Payments|Multi-tenancy|SaaS billing|Deployment|Performance|Enterprise Laravel architecture|Laravel capstone"),
    ("JavaScript and TypeScript Developer", "javascript-typescript-developer", "JavaScript", 25, "JavaScript fundamentals|Functions and scope|Objects and arrays|Closures|Prototypes|ES modules|Async programming|Promises and event loop|DOM|Browser APIs|Error handling|Functional programming|TypeScript types|Interfaces and generics|Advanced types|Utility types|Testing|Performance|Frontend integration|Backend integration|Package design|API clients|Build tooling|Professional project|JavaScript and TypeScript capstone"),
    ("Node.js Backend Developer", "nodejs-backend-developer", "Node.js", 30, "Node.js runtime|npm and package design|Modules|File systems|Streams and buffers|Events|HTTP servers|Async programming|Worker threads|Express.js|Routing|Middleware|Validation|Error handling|REST APIs|PostgreSQL|Authentication|Authorization|Transactions|Redis|Queues|WebSockets|Testing|Security|Performance|Microservices|Monitoring|Deployment|Enterprise backend architecture|Node.js capstone"),
    ("C and C++ Developer", "c-cpp-developer", "Systems Programming", 25, "C fundamentals|Pointers|Arrays and strings|Structures and unions|Enums|Memory management|File handling|Compilation|Debugging|Algorithms|Data structures|C++ foundations|C++ object-oriented programming|Templates|STL|RAII|Smart pointers|Concurrency|Modern C++|Performance|Systems programming|Build systems|Secure native code|Professional project|C and C++ capstone"),
    ("Database Engineer", "database-engineer", "Data Infrastructure", 25, "Relational database concepts|SQL|PostgreSQL|MySQL|SQLite|Schema design|Normalization|Constraints|Indexes|Joins|Subqueries and CTEs|Window functions|Transactions|Isolation levels|Locking|Query optimization|Execution plans|Stored procedures|Partitioning|Replication|Backup and recovery|Database security|High availability|Operations studio|Database engineering capstone"),
    ("Data Analyst", "data-analyst", "Data", 20, "Spreadsheet modeling|Descriptive statistics|SQL|Python for analysis|NumPy|pandas|Data cleaning|Data transformation|Exploratory analysis|Visualization|Dashboards|Reporting|Business metrics|Data quality|Analytical storytelling|Experiment basics|Analytics project planning|Portfolio dashboard|Stakeholder presentation|Data analyst capstone"),
    ("Data Scientist", "data-scientist", "Data Science", 30, "Python|Mathematics|Probability|Statistics|Data analysis|Visualization|Feature engineering|Regression|Classification|Clustering|Model validation|Ensemble methods|Time series|Experiments|Model interpretation|Deep learning foundations|Responsible AI|Model packaging|Deployment|Data science workflow|Reproducibility|Model monitoring|Research communication|Recommendation systems|NLP foundations|Computer vision foundations|Production project|Experimentation studio|Portfolio project|Data science capstone"),
    ("Data Engineer", "data-engineer", "Data Infrastructure", 30, "Python|SQL|Data modeling|ETL|ELT|Batch processing|Stream processing|Data warehouses|Data lakes|Apache Spark|Workflow orchestration|Messaging|Data quality|Distributed storage|Schema evolution|Governance|Monitoring|Security|Cloud data infrastructure|Pipeline testing|Cost optimization|Metadata management|Analytics serving|Real-time pipelines|Recovery planning|Data platform architecture|Scalable pipeline studio|Operations project|Portfolio project|Data engineering capstone"),
    ("AI and Machine Learning Engineer", "ai-machine-learning-engineer", "Artificial Intelligence", 35, "Python for AI|Linear algebra|Probability and statistics|Calculus fundamentals|Data preparation|Supervised learning|Unsupervised learning|Feature engineering|Model evaluation|Neural networks|Deep learning|Computer vision|Natural language processing|Transformers|Large language models|Embeddings|Vector databases|Retrieval augmented generation|AI API integration|AI agents|Tool calling|Workflow automation|Model serving|AI security|AI evaluation|Responsible AI|Human oversight|MLOps|Production AI architecture|Dataset versioning|Inference optimization|Multimodal systems|AI product design|Evaluation studio|AI engineering capstone"),
    ("Cybersecurity Engineer", "cybersecurity-engineer", "Cybersecurity", 35, "Networking|Linux|Operating systems|Security fundamentals|Cryptography|Identity management|Access control|Web security|OWASP|Secure coding|Network defense|Vulnerability management|Authorized security testing|Security monitoring|Incident response|Digital forensics|Cloud security|Container security|Application security|Threat modeling|Security architecture|Security operations|Detection engineering|Threat intelligence|Identity security|Privacy engineering|Security automation|Resilience|Risk management|Security testing lab|Forensics lab|Defense architecture|Professional practice|Capstone planning|Defensive security capstone"),
    ("DevOps Engineer", "devops-engineer", "DevOps", 30, "Linux|Shell scripting|Git|Build systems|Networking|Docker|Container registries|CI/CD|GitHub Actions|Infrastructure as code|Terraform|Kubernetes|Configuration management|Secrets management|Reverse proxies|Load balancing|Monitoring|Logging|Tracing|Deployment strategies|Rollback|Security automation|Cloud infrastructure|Disaster recovery|Release engineering|Platform operations|Reliability studio|Production runbooks|Portfolio project|DevOps capstone"),
    ("Cloud Engineer", "cloud-engineer", "Cloud", 30, "Cloud computing|Virtual machines|Object and block storage|Cloud networking|IAM|Managed databases|Serverless computing|Containers|Kubernetes|Infrastructure as code|Cloud monitoring|Cloud security|Cost optimization|High availability|Disaster recovery|AWS foundations|AWS architecture|Azure foundations|Azure architecture|Cloud automation|Landing zones|Network security|Data protection|Reliability testing|Migration planning|Multi-region design|Operations studio|Cloud governance|Portfolio project|Cloud engineering capstone"),
    ("Linux and Systems Engineer", "linux-systems-engineer", "Systems", 25, "Linux installation|Filesystem|Shell commands|Permissions|Processes|Users and groups|Services|systemd|Package management|Networking|SSH|Storage|Logs|Scripting|Scheduling|Backups|System hardening|Kernel fundamentals|Resource management|Troubleshooting|Automation|Production servers|Reliability operations|Systems project|Linux systems capstone"),
    ("WordPress Developer", "wordpress-developer", "WordPress", 20, "WordPress architecture|Local development|PHP|MySQL|Classic themes|Block themes|Template hierarchy|Hooks and filters|Custom post types|Taxonomies|Metadata|Custom fields|Plugin development|REST API|WooCommerce|Multilingual sites|Security|Performance|Deployment|Professional WordPress capstone"),
    ("Software Testing and QA Engineer", "software-testing-qa-engineer", "Quality Engineering", 25, "Testing fundamentals|SDLC|Test planning|Test cases|Bug reporting|Manual testing|Unit testing|Integration testing|API testing|End-to-end testing|Playwright|Test automation|Regression testing|Accessibility testing|Performance testing|Security testing|CI testing|Test data management|Test coverage|Quality metrics|Exploratory testing|Enterprise QA processes|Release quality|QA automation project|QA capstone"),
    ("API Developer", "api-developer", "API Engineering", 25, "HTTP|REST|JSON|Routing|API contracts|Validation|Authentication|Authorization|Pagination|Filtering and sorting|Versioning|OpenAPI|Error handling|Rate limiting|Idempotency|Transactions|Webhooks|WebSockets|GraphQL fundamentals|gRPC fundamentals|API testing|Monitoring|Performance|Security|Production API architecture"),
    ("Enterprise Application Developer", "enterprise-application-developer", "Enterprise Software", 35, "Enterprise requirements|Software architecture|Domain-driven design|Modular monoliths|Database engineering|Authentication|IAM|RBAC|ABAC|Audit logging|Approval workflows|Multi-tenancy|CRM systems|ERP systems|Inventory systems|Accounting fundamentals|HR systems|Reporting|Async jobs|Event-driven architecture|Microservices|Integrations|Enterprise testing|Security|Reliability|Deployment|Data governance|Change management|Operations|Architecture review|Enterprise project|Production readiness|Portfolio project|Enterprise application capstone|Enterprise application capstone review"),
    ("SaaS Developer", "saas-developer", "SaaS", 35, "SaaS architecture|Product planning|Organization management|Tenant isolation|Membership|Invitations|Permissions|Onboarding|Subscriptions|Billing|Plans|Entitlements|Metering|Usage limits|Payment integration|Webhooks|Background processing|Notifications|Analytics|Admin dashboards|Audit trails|Security|Scalability|Observability|Disaster recovery|SaaS operations|Growth experiments|Compliance foundations|Platform project|Production launch|SaaS capstone|Reliability review|Cost model|Support operations|SaaS architecture capstone"),
    ("System Design and Architecture", "system-design-architecture", "Architecture", 30, "System design fundamentals|Networking|Load balancing|Caching|Databases|Replication|Partitioning|Consistency|Availability|Distributed transactions|Messaging|Event-driven architecture|Microservices|API gateways|Service discovery|Circuit breakers|Rate limiting|Idempotency|Distributed locking|Observability|Capacity planning|Fault tolerance|Security architecture|Data architecture|Resilience testing|Architecture trade-offs|Design review|Reference architecture|System design project|Architecture capstone"),
    ("Site Reliability Engineer", "site-reliability-engineer", "Reliability", 30, "SRE principles|SLIs|SLOs|Error budgets|Monitoring|Metrics|Logging|Distributed tracing|Alerting|On-call operations|Incident management|Incident communication|Runbooks|Postmortems|Reliability testing|Resilience engineering|Controlled chaos engineering|Automated remediation|Capacity planning|Disaster recovery|Toil reduction|Service ownership|Release reliability|Availability design|Performance operations|Security operations|Platform health|Reliability project|Operations review|SRE capstone"),
    ("Game Developer", "game-developer", "Game Development", 30, "Programming fundamentals|Game mathematics|Game loops|Rendering|Sprites|Animation|Collision detection|Physics|Input handling|Game state|UI|Audio|Level design|Game AI|Save systems|2D development|3D fundamentals|Multiplayer fundamentals|Performance optimization|Game testing|Packaging|Engine specialization|Asset pipelines|Tools programming|Gameplay project|Systems project|Multiplayer project|Release planning|Professional game portfolio|Game development capstone"),
]


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def matching_course(courses: list[Course], title: str) -> Course | None:
    words = {word for word in slugify(title).split("-") if len(word) > 2}
    ranked = sorted(courses, key=lambda course: len(words & set(slugify(course.title).split("-"))), reverse=True)
    return ranked[0] if ranked and words & set(slugify(ranked[0].title).split("-")) else None


def seed() -> tuple[int, int, int]:
    created_paths = created_stages = created_steps = 0
    with SessionLocal.begin() as db:
        courses = list(db.scalars(select(Course).where(Course.published.is_(True))).all())
        for title, slug, category, target, phase_text in CATALOG:
            roadmap = db.scalar(select(CareerRoadmap).where(CareerRoadmap.slug == slug))
            if roadmap is None:
                roadmap = CareerRoadmap(title=title, slug=slug, career_category=category,
                    description_en=f"A structured {title.lower()} curriculum from first principles to production practice.",
                    description_mm=f"{title} အတွက် အခြေခံမှ production practice အထိ စနစ်တကျ လေ့လာနိုင်သော လမ်းကြောင်း။",
                    prerequisites_en="Start with the first phase unless a prerequisite is listed in your learner profile.",
                    outcomes_en=f"Build, test, explain, and deploy work relevant to {title.lower()}.",
                    estimated_hours=target * 8, goals_json=json.dumps([f"Progress through {target} domain phases", "Complete practical projects", "Build a reviewable portfolio"]),
                    skills_json=json.dumps([title, category]), status="draft", published=False)
                db.add(roadmap); db.flush(); created_paths += 1
            existing_stages = {stage.position: stage for stage in db.scalars(select(RoadmapStage).where(RoadmapStage.roadmap_id == roadmap.id)).all()}
            phase_names = topics(phase_text)[:target]
            for position, phase_title in enumerate(phase_names):
                stage = existing_stages.get(position)
                if stage is None:
                    level = "beginner" if position < max(1, target // 5) else "intermediate" if position < target * 3 // 5 else "advanced" if position < target * 4 // 5 else "professional"
                    stage = RoadmapStage(roadmap_id=roadmap.id, title=phase_title, description_en=f"Study {phase_title.lower()} through explanation, practice, and review.", description_mm=f"{phase_title} ကို ရှင်းလင်းချက်၊ လေ့ကျင့်ခန်းနှင့် ပြန်လည်သုံးသပ်မှုဖြင့် လေ့လာပါ။", level=level, objectives_json=json.dumps([f"Explain the core ideas in {phase_title}", "Apply the ideas in a small implementation", "Verify the result with tests or review"]), skills_json=json.dumps([phase_title]), completion_rules_json=json.dumps({"required_steps": 1}), position=position)
                    db.add(stage); db.flush(); created_stages += 1
                if db.scalar(select(RoadmapStep.id).where(RoadmapStep.stage_id == stage.id)) is not None:
                    continue
                course = matching_course(courses, phase_title)
                step = RoadmapStep(stage_id=stage.id, title=f"{phase_title} practice", instructions_en=f"Read the linked course material for {phase_title.lower()}, complete its available lessons, and record one implementation or reflection.", instructions_mm=f"{phase_title} အတွက် ချိတ်ဆက်ထားသော သင်ခန်းစာများကို လေ့လာပြီး implementation သို့မဟုတ် reflection တစ်ခု မှတ်တမ်းတင်ပါ။", position=0, required=True)
                db.add(step); db.flush(); created_steps += 1
                if course is not None:
                    db.add(RoadmapStepResource(step_id=step.id, resource_type="course", resource_id=course.id))
    return created_paths, created_stages, created_steps


if __name__ == "__main__":
    paths, stages, steps = seed()
    print(f"Learning path seed complete: {paths} paths, {stages} stages, {steps} steps created")
