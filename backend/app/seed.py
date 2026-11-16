"""Idempotent catalog metadata seed.

Creates catalog records only. It never creates placeholder lessons and does not
replace existing curriculum, enrollments, or progress.
Run from backend: python -m app.seed
"""
import json
from sqlalchemy import select

from .db import SessionLocal
from .models import (Challenge, ChallengeCategory, ChallengeHint, ChallengeLanguageConfig,
                     ChallengeTestCase, ChallengeTopic, ChallengeTopicLink, Course,
                     CourseCategory, ProgrammingLanguage, ProjectCategory,
                     ProjectMilestone, ProjectTemplate)
from .c_course_content import seed_c_curriculum
from .django_course_content import seed_django_course
from .docker_course_content import seed_docker_course
from .express_course_content import seed_express_course
from .fastapi_course_content import seed_fastapi_course
from .flutter_course_content import seed_flutter_course
from .git_course_content import seed_git_course
from .github_course_content import seed_github_course
from .go_course_content import seed_go_course
from .kotlin_course_content import seed_kotlin_course
from .cpp_course_content import seed_cpp_course
from .html_course_content import seed_html_course
from .css_course_content import seed_css_course
from .javascript_course_content import seed_javascript_course
from .python_course_content import seed_python_course
from .java_course_content import seed_java_course
from .advanced_java_course_content import seed_advanced_java_course
from .jquery_course_content import seed_jquery_course
from .bootstrap_course_content import seed_bootstrap_course
from .typescript_course_content import seed_typescript_course
from .php_course_content import seed_php_course
from .csharp_course_content import seed_csharp_course
from .dart_course_content import seed_dart_course
from .data_analysis_course_content import seed_data_analysis_course
from .data_structures_course_content import seed_data_structures_course
from .algorithms_course_content import seed_algorithms_course
from .aws_course_content import seed_aws_course
from .ci_cd_course_content import seed_ci_cd_course
from .cybersecurity_fundamentals_course_content import seed_cybersecurity_fundamentals_course

CATEGORIES = [
    ("Frontend Development", "frontend-development"),
    ("Web Development", "web-development"),
    ("Programming", "programming"),
    ("Programming Languages", "programming-languages"),
    ("Backend Development", "backend-development"),
    ("Database Development", "database-development"),
    ("DevOps & Cloud", "devops-cloud"),
    ("Developer Tools", "developer-tools"),
    ("Cybersecurity", "cybersecurity"),
    ("Mobile Development", "mobile-development"),
    ("AI & Data Science", "ai-data-science"),
    ("Computer Science", "computer-science"),
    ("Data Science & Analytics", "data-analytics"),
    ("Cloud Computing & AWS", "cloud-computing"),
    ("DevOps & CI/CD", "devops-ci-cd"),
    ("Cybersecurity & Information Security", "cybersecurity-information-security"),
]
COURSES = [
    ("HTML", "html", "html", "#E34F26", "web-development"), ("CSS", "css", "css", "#264DE4", "web-development"),
    ("JavaScript", "javascript", "javascript", "#F7DF1E", "web-development"), ("TypeScript", "typescript", "typescript", "#3178C6", "web-development"),
    ("React", "react", "javascript", "#61DAFB", "frontend-development"), ("Next.js", "next-js", "javascript", "#F8FAFC", "frontend-development"),
    ("jQuery", "jquery", "javascript", "#0769AD", "web-development"), ("Tailwind CSS", "tailwind-css", "css", "#06B6D4", "frontend-development"),
    ("Bootstrap 5 — From Zero to Professional Responsive Web Design", "bootstrap", "css", "#7952B3", "web-development"), ("C Programming", "c-programming", "c", "#A8B9CC", "programming-languages"),
    ("C++ Programming — Beginner to Professional Foundations", "cpp-programming", "cpp", "#00599C", "programming-languages"), ("Java", "java", "java", "#E76F51", "programming"),
    ("Advanced Java — Enterprise Backend Engineering", "advanced-java", "java", "#E76F51", "backend-development"), ("Python", "python", "python", "#3776AB", "programming"),
    ("C# Programming — From Zero to Advanced", "csharp", "c-sharp", "#68217A", "backend-development"), ("Go", "go", "go", "#00ADD8", "programming-languages"),
    ("Rust", "rust", "rust", "#DEA584", "programming-languages"), ("Node.js", "node-js", "javascript", "#339933", "backend-development"),
    ("Express.js", "express-js", "javascript", "#F8FAFC", "backend-development"), ("PHP Programming — From Zero to Advanced", "php", "php", "#777BB4", "backend-development"),
    ("Laravel", "laravel", "php", "#FF2D20", "backend-development"), ("FastAPI", "fastapi", "python", "#009688", "backend-development"),
    ("Django", "django", "python", "#087F5B", "backend-development"), ("Spring Boot", "spring-boot", "java", "#6DB33F", "backend-development"),
    ("SQL", "sql", "sql", "#22C55E", "database-development"), ("MySQL", "mysql", "sql", "#4479A1", "database-development"),
    ("PostgreSQL", "postgresql", "sql", "#4169E1", "database-development"), ("SQLite", "sqlite", "sql", "#003B57", "database-development"),
    ("MongoDB", "mongodb", "mongodb", "#47A248", "database-development"), ("Redis", "redis", "redis", "#DC382D", "database-development"),
    ("Linux", "linux", "linux", "#FCC624", "devops-cloud"), ("Git", "git", "git", "#F05032", "devops-cloud"),
    ("GitHub", "github", "git", "#F8FAFC", "devops-cloud"), ("Docker", "docker", "docker", "#2496ED", "devops-cloud"),
    ("CI/CD & DevOps Engineering — From Zero to Professional", "ci-cd", "ci-cd", "#2563EB", "devops-ci-cd"), ("AWS", "aws", "aws", "#FF9900", "cloud-computing"),
    ("Microsoft Azure", "microsoft-azure", "azure", "#0078D4", "devops-cloud"), ("Cybersecurity Fundamentals — From Zero to Professional", "cybersecurity-fundamentals", "cybersecurity", "#059669", "cybersecurity-information-security"),
    ("Networking Fundamentals", "networking-fundamentals", "networking", "#38BDF8", "cybersecurity"), ("Web Security", "web-security", "cybersecurity", "#F97316", "cybersecurity"),
    ("Secure Coding", "secure-coding", "cybersecurity", "#A855F7", "cybersecurity"), ("OWASP Top 10", "owasp-top-10", "cybersecurity", "#F43F5E", "cybersecurity"),
    ("Dart Programming — From Zero to Advanced", "dart", "dart", "#0175C2", "mobile-development"), ("Flutter", "flutter", "dart", "#54C5F8", "mobile-development"),
    ("React Native", "react-native", "javascript", "#61DAFB", "mobile-development"), ("Kotlin", "kotlin", "kotlin", "#7F52FF", "mobile-development"),
    ("Python for AI", "python-for-ai", "python", "#3776AB", "ai-data-science"), ("Machine Learning", "machine-learning", "python", "#10B981", "ai-data-science"),
    ("Data Analysis — From Zero to Professional Data Analyst", "data-analysis", "python", "#0D9488", "data-analytics"), ("Data Structures — From Zero to Advanced", "data-structures", "python", "#7C3AED", "computer-science"),
    ("Algorithms — From Zero to Advanced", "algorithms", "python", "#EA580C", "computer-science"), ("Operating Systems", "operating-systems", "computer-science", "#64748B", "computer-science"),
]

CHALLENGE_CATEGORIES = [
    ("Programming Fundamentals", "programming-fundamentals"),
    ("Strings and Arrays", "strings-arrays"),
    ("Data Structures", "data-structures"),
    ("Algorithms", "algorithms"),
    ("SQL and Databases", "sql-databases"),
    ("Debugging", "debugging"),
    ("Interview Preparation", "interview-preparation"),
]

# These are small, reviewable starter challenges. Each one has a public example,
# a hidden test, a supported runtime, and a hint. Existing challenge rows are
# never overwritten by this seed.
CHALLENGES = [
    {"title":"Add Two Numbers", "slug":"add-two-numbers", "category":"programming-fundamentals", "topics":["fundamentals"], "language":"python", "difficulty":"beginner", "description":"Read two integers and print their sum. This first exercise reinforces input, conversion, and output.", "constraints":["The input contains two integers.", "Use integer arithmetic."], "examples":[{"input":"4 7", "output":"11", "explanation":"4 + 7 = 11."}], "starter":"a, b = map(int, input().split())\n# Print the sum\n", "tests":[("4 7","11",False),("-2 9","7",True)], "hint":"Split the line into two values, convert them to integers, then add them."},
    {"title":"Reverse a String", "slug":"reverse-a-string", "category":"strings-arrays", "topics":["strings"], "language":"python", "difficulty":"easy", "description":"Print a string in reverse order while preserving every character.", "constraints":["The input is one line.","The input length is at most 10,000 characters."], "examples":[{"input":"academy", "output":"ymedaca", "explanation":"The characters are read from right to left."}], "starter":"text = input()\n# Print the reversed text\n", "tests":[("academy","ymedaca",False),("CodeMaster","retsaM edoC",True)], "hint":"Python slicing can express a step of negative one."},
    {"title":"Count Vowels", "slug":"count-vowels", "category":"strings-arrays", "topics":["strings"], "language":"python", "difficulty":"easy", "description":"Count the vowels a, e, i, o, and u in a case-insensitive string.", "constraints":["Count only English vowels.","The input may contain spaces."], "examples":[{"input":"Learn Python", "output":"3", "explanation":"The vowels are e, a, and o."}], "starter":"text = input()\n# Count and print the vowels\n", "tests":[("Learn Python","3",False),("AEIOU","5",True)], "hint":"Normalize each character to lowercase and test membership in a small vowel set."},
    {"title":"Maximum in an Array", "slug":"maximum-in-an-array", "category":"strings-arrays", "topics":["arrays"], "language":"python", "difficulty":"easy", "description":"Find the largest integer in a list without sorting the list.", "constraints":["The first input value is n.","The second line contains n integers."], "examples":[{"input":"5\n3 9 2 8 4", "output":"9", "explanation":"9 is larger than every other value."}], "starter":"n = int(input())\nvalues = list(map(int, input().split()))\n# Find and print the maximum\n", "tests":[("5\n3 9 2 8 4","9",False),("3\n-8 -2 -5","-2",True)], "hint":"Keep the best value seen so far while scanning once from left to right."},
    {"title":"Fizz Buzz", "slug":"fizz-buzz", "category":"programming-fundamentals", "topics":["loops"], "language":"python", "difficulty":"beginner", "description":"Print numbers from 1 through n, replacing multiples of three with Fizz, five with Buzz, and both with FizzBuzz.", "constraints":["1 <= n <= 10,000."], "examples":[{"input":"5", "output":"1\n2\nFizz\n4\nBuzz", "explanation":"Three is divisible by three and five is divisible by five."}], "starter":"n = int(input())\n# Print the Fizz Buzz sequence\n", "tests":[("5","1\n2\nFizz\n4\nBuzz",False),("15","1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz",True)], "hint":"Check divisibility by both numbers before checking either one separately."},
    {"title":"Palindrome Check", "slug":"palindrome-check", "category":"strings-arrays", "topics":["strings"], "language":"javascript", "difficulty":"easy", "description":"Determine whether a word reads the same forward and backward.", "constraints":["The input contains one lowercase word."], "examples":[{"input":"level", "output":"true", "explanation":"The reversed word is also level."}], "starter":"const text = require('fs').readFileSync(0, 'utf8').trim();\n// Print true or false\n", "tests":[("level","true",False),("coding","false",True)], "hint":"Compare the original text with its reversed character sequence."},
    {"title":"Two Sum", "slug":"two-sum", "category":"algorithms", "topics":["arrays","algorithms"], "language":"python", "difficulty":"medium", "description":"Given a list and a target, print the zero-based indexes of two values that add to the target.", "constraints":["Exactly one pair exists.","Return the indexes in ascending order."], "examples":[{"input":"4 9\n2 7 11 15", "output":"0 1", "explanation":"The values at indexes 0 and 1 sum to 9."}], "starter":"n, target = map(int, input().split())\nvalues = list(map(int, input().split()))\n# Find the two indexes\n", "tests":[("4 9\n2 7 11 15","0 1",False),("3 6\n3 2 3","0 2",True)], "hint":"A dictionary can remember values already visited and their indexes."},
    {"title":"SQL Active Users", "slug":"sql-active-users", "category":"sql-databases", "topics":["sql"], "language":"sql", "difficulty":"beginner", "description":"Write a query that returns the names of users whose active flag is true, ordered alphabetically.", "constraints":["Use the users table with name and active columns.","Return only the name column."], "examples":[{"input":"users(name, active)", "output":"Ada\nLin", "explanation":"Only rows with active = true are selected."}], "starter":"SELECT name\nFROM users\n-- Add the filter and ordering\n", "tests":[("","Ada\nLin",False),("","Ada\nLin",True)], "hint":"Use WHERE for the boolean filter and ORDER BY for alphabetical output."},
    {"title":"Fix the Off-by-one Loop", "slug":"fix-off-by-one-loop", "category":"debugging", "topics":["debugging","loops"], "language":"python", "difficulty":"easy", "description":"Repair a loop so it prints every integer from 1 through n, including the final value.", "constraints":["1 <= n <= 1000."], "examples":[{"input":"3", "output":"1\n2\n3", "explanation":"The inclusive range must contain n."}], "starter":"n = int(input())\nfor number in range(1, n):\n    print(number)\n", "tests":[("3","1\n2\n3",False),("1","1",True)], "hint":"Python's range stop value is exclusive, so choose it deliberately."},
    {"title":"Balanced Parentheses", "slug":"balanced-parentheses", "category":"data-structures", "topics":["stacks"], "language":"python", "difficulty":"medium", "description":"Check whether every opening parenthesis is closed in the correct order.", "constraints":["The input contains only parentheses.","The input length is at most 10,000."], "examples":[{"input":"(()())", "output":"true", "explanation":"A stack can match each closing parenthesis with the latest opening one."}], "starter":"text = input().strip()\n# Validate the parentheses\n", "tests":[("(()())","true",False),("())(","false",True)], "hint":"Push opening parentheses and pop for closing ones; reject an empty pop or leftover openings."},
]

PROJECT_CATEGORIES = [
    ("Frontend Development", "frontend-development"),
    ("Backend Development", "backend-development"),
    ("Full-Stack Development", "full-stack-development"),
    ("Programming Languages", "programming-languages"),
    ("Database Development", "database-development"),
    ("Mobile Development", "mobile-development"),
    ("AI & Machine Learning", "ai-machine-learning"),
    ("Cybersecurity", "cybersecurity"),
    ("DevOps & Cloud", "devops-cloud"),
    ("Software Engineering", "software-engineering"),
]
PROJECTS = [
    ("Personal Portfolio Website", "personal-portfolio-website", "frontend-development", "beginner", "HTML, CSS, JavaScript", 8),
    ("Calculator Application", "calculator-application", "programming-languages", "beginner", "Python, JavaScript", 6),
    ("To-Do List", "todo-list", "frontend-development", "beginner", "HTML, CSS, JavaScript", 10),
    ("HTML/CSS Landing Page", "html-css-landing-page", "frontend-development", "beginner", "HTML, CSS", 6),
    ("Python CLI Calculator", "python-cli-calculator", "programming-languages", "beginner", "Python", 5),
    ("C Student Record Program", "c-student-record-program", "programming-languages", "intermediate", "C", 14),
    ("SQL Student Database", "sql-student-database", "database-development", "beginner", "SQL, PostgreSQL", 8),
    ("React Task Manager", "react-task-manager", "frontend-development", "intermediate", "React, TypeScript", 18),
    ("Python FastAPI REST API", "python-fastapi-rest-api", "backend-development", "intermediate", "Python, FastAPI, PostgreSQL", 24),
    ("Node.js Authentication API", "nodejs-authentication-api", "backend-development", "advanced", "Node.js, Express.js, PostgreSQL", 28),
    ("E-Commerce Application", "e-commerce-application", "full-stack-development", "advanced", "Next.js, FastAPI, PostgreSQL", 40),
    ("Real-Time Chat Application", "real-time-chat-application", "full-stack-development", "advanced", "React, FastAPI, WebSockets", 32),
    ("SaaS Dashboard", "saas-dashboard", "software-engineering", "professional", "Next.js, FastAPI, PostgreSQL", 48),
]
LEGACY_SLUGS = {slug: f"{language}-foundations" for _, slug, language, _, _ in COURSES}

def get_or_create(db, model, slug, **values):
    row = db.scalar(select(model).where(model.slug == slug))
    if not row:
        row = model(slug=slug, **values)
        db.add(row)
        db.flush()
    return row

def seed_challenges(db):
    categories = {slug: get_or_create(db, ChallengeCategory, slug, name=name, description=f"{name} practice", status="active") for name, slug in CHALLENGE_CATEGORIES}
    topics = {}
    for challenge in CHALLENGES:
        for slug in challenge["topics"]:
            topics[slug] = get_or_create(db, ChallengeTopic, slug, name=slug.replace("-", " ").title())
    for item in CHALLENGES:
        row = db.scalar(select(Challenge).where(Challenge.slug == item["slug"]))
        if row:
            continue
        row = Challenge(title=item["title"], slug=item["slug"], category_id=categories[item["category"]].id,
                        description_en=item["description"], difficulty=item["difficulty"], status="published",
                        published=True, examples_json=json.dumps(item["examples"]), constraints_json=json.dumps(item["constraints"]))
        db.add(row); db.flush()
        db.add(ChallengeLanguageConfig(challenge_id=row.id, language=item["language"], starter_code=item["starter"]))
        for topic_slug in item["topics"]:
            db.add(ChallengeTopicLink(challenge_id=row.id, topic_id=topics[topic_slug].id))
        db.add(ChallengeHint(challenge_id=row.id, body_en=item["hint"], position=1))
        for position, (input_data, expected_output, hidden) in enumerate(item["tests"]):
            db.add(ChallengeTestCase(challenge_id=row.id, input_data=input_data, expected_output=expected_output, is_hidden=hidden, position=position))

def seed_projects(db):
    categories = {slug: get_or_create(db, ProjectCategory, slug, name=name, description=f"{name} projects", status="active") for name, slug in PROJECT_CATEGORIES}
    for title, slug, category_slug, difficulty, technologies, hours in PROJECTS:
        row = db.scalar(select(ProjectTemplate).where(ProjectTemplate.slug == slug))
        if row:
            continue
        row = ProjectTemplate(
            title=title, slug=slug, category_id=categories[category_slug].id,
            description_en=f"Build {title} through a guided, theory-first project with an honest scope and reviewable milestones.",
            difficulty=difficulty, estimated_hours=hours, requirements=f"Understand the basics of {technologies}. Read each project step and keep your own implementation notes.",
            learning_outcomes=f"Explain the architecture of {title}; identify the main implementation trade-offs; test and document a maintainable solution.",
            technology_stack=technologies, prerequisites="Complete the relevant beginner lessons before starting.",
            architecture_overview="Start with a small, testable boundary; keep presentation, application logic, and persistence responsibilities separate where the project requires them.",
            folder_structure="README.md\nsrc/\ntests/\ndocs/", testing_guide="Write focused tests for the core behavior and verify the documented examples.",
            deployment_guide="Review configuration, secrets, logging, and the deployment target before publishing a real service.",
            status="published", published=True,
        )
        db.add(row); db.flush()
        steps = [
            ("introduction", "Introduction and scope", "Understand the problem, users, constraints, and the completion criteria before writing code.", "README.md\n", "The project scope is written down before implementation."),
            ("architecture", "Architecture and folder structure", "Map the major components and choose boundaries that make the project easy to test and maintain.", "src/\ntests/\n", "The repository has a documented structure."),
            ("implementation", "Implementation plan", "Break the project into small deliverables and connect each deliverable to a verifiable behavior.", "# Implement one behavior at a time\n", "Each behavior has a clear verification step."),
            ("testing", "Testing and deployment checklist", "Review tests, error handling, security, configuration, and operational readiness.", "# Run the test suite\n", "The project is ready for a deliberate review."),
        ]
        for position, (step_slug, step_title, content, code, output) in enumerate(steps, 1):
            db.add(ProjectMilestone(project_id=row.id, title=step_title, slug=step_slug, description_en=content, content_en=content, code=code, filename="README.md", expected_output=output, line_explanation="Read the file path and the adjacent explanation together; each line identifies one part of the project workflow.", position=position, required=True))

def main():
    with SessionLocal.begin() as db:
        categories = {slug: get_or_create(db, CourseCategory, slug, name=name, status="active") for name, slug in CATEGORIES}
        cpp_rows = list(db.scalars(select(Course).where(Course.slug.in_(["cpp", "cpp-programming"]))))
        if len(cpp_rows) > 1:
            # Keep the row that already owns curriculum/progress and archive
            # empty duplicate catalog rows created by older seed versions.
            populated = sorted(cpp_rows, key=lambda row: len(row.modules), reverse=True)[0]
            for duplicate in cpp_rows:
                if duplicate is populated:
                    continue
                duplicate.slug = f"cpp-programming-legacy-{str(duplicate.id)[:8]}"
                duplicate.status = "archived"
                duplicate.published = False
            populated.slug = "cpp-programming"
        # Keep any previously archived migration leftovers out of the public
        # catalog even if an older seed version left their status unchanged.
        for legacy in db.scalars(select(Course).where(Course.slug.like("cpp-programming-legacy-%"))).all():
            legacy.status = "archived"
            legacy.published = False
        # The old catalog seed used the generic ``cpp`` slug. Repoint that
        # same course row when possible so an existing enrollment/progress row
        # is preserved rather than creating a second C++ source of truth.
        old_cpp = db.scalar(select(Course).where(Course.slug == "cpp"))
        requested_cpp = db.scalar(select(Course).where(Course.slug == "cpp-programming"))
        if old_cpp and not requested_cpp:
            old_cpp.slug = "cpp-programming"
        old_csharp = db.scalar(select(Course).where(Course.slug == "c-sharp"))
        requested_csharp = db.scalar(select(Course).where(Course.slug == "csharp"))
        if old_csharp and not requested_csharp:
            old_csharp.slug = "csharp"
        csharp_rows = list(db.scalars(select(Course).where(Course.slug.in_(["c-sharp", "csharp"]))).all())
        if len(csharp_rows) > 1:
            populated_csharp = sorted(csharp_rows, key=lambda row: len(row.modules), reverse=True)[0]
            for duplicate in csharp_rows:
                if duplicate is populated_csharp:
                    continue
                duplicate.slug = f"csharp-legacy-{str(duplicate.id)[:8]}"
                duplicate.status = "archived"
                duplicate.published = False
            populated_csharp.slug = "csharp"
        for legacy in db.scalars(select(Course).where(Course.slug.like("csharp-legacy-%"))).all():
            legacy.status = "archived"
            legacy.published = False
        languages = {}
        for title, course_slug, language_slug, color, _ in COURSES:
            language = db.scalar(select(ProgrammingLanguage).where(ProgrammingLanguage.slug == language_slug))
            if not language:
                display_name = title if language_slug == course_slug else language_slug.replace("-", " ").title()
                language = ProgrammingLanguage(name=display_name, slug=language_slug, color=color, status="active")
                db.add(language)
                db.flush()
            if language_slug == "cpp":
                language.name = "C++"
                language.color = color
            languages[language_slug] = language
        for title, slug, language_slug, _, category_slug in COURSES:
            course = db.scalar(select(Course).where(Course.slug == slug))
            if not course:
                course = db.scalar(select(Course).where(Course.slug == LEGACY_SLUGS.get(slug, "")))
                if course:
                    course.slug = slug
            if not course:
                course = Course(
                    slug=slug,
                    title=title,
                    language_id=languages[language_slug].id,
                    category_id=categories[category_slug].id,
                    description=f"Learn {title} from first principles through a structured, free curriculum.",
                    short_description=f"A theory-first introduction to {title}.",
                    level="beginner",
                    duration_minutes=0,
                    outcomes="Understand the core concepts|Read and explain examples|Build a foundation for further study",
                    requirements="",
                    status="curriculum_pending",
                    published=True,
                )
                db.add(course)
                db.flush()
            # Metadata only. Existing lesson/progress/enrollment records are untouched.
            course.title = title
            course.language_id = languages[language_slug].id
            course.category_id = categories[category_slug].id
            course.description = f"Learn {title} from first principles through a structured, free curriculum."
            course.short_description = f"A theory-first introduction to {title}."
            course.level = "beginner"
            course.duration_minutes = course.duration_minutes or 0
            course.outcomes = course.outcomes or "Understand the core concepts|Read and explain examples|Build a foundation for further study"
            course.requirements = course.requirements or ""
            course.status = "curriculum_pending"
            course.published = True
        db.flush()
        c_course = db.scalar(select(Course).where(Course.slug == "c-programming"))
        if c_course:
            seed_c_curriculum(db, c_course)
        cpp_course = db.scalar(select(Course).where(Course.slug == "cpp-programming"))
        if cpp_course:
            seed_cpp_course(db, cpp_course)
        html_course = db.scalar(select(Course).where(Course.slug == "html"))
        if html_course:
            seed_html_course(db, html_course)
        css_course = db.scalar(select(Course).where(Course.slug == "css"))
        if css_course:
            seed_css_course(db, css_course)
        javascript_course = db.scalar(select(Course).where(Course.slug == "javascript"))
        if javascript_course:
            seed_javascript_course(db, javascript_course)
        python_course = db.scalar(select(Course).where(Course.slug == "python"))
        if python_course:
            seed_python_course(db, python_course)
        django_course = db.scalar(select(Course).where(Course.slug == "django"))
        if django_course:
            django_course.category_id = categories["backend-development"].id
            seed_django_course(db, django_course)
        docker_course = db.scalar(select(Course).where(Course.slug == "docker"))
        if docker_course:
            docker_course.category_id = categories["devops-cloud"].id
            seed_docker_course(db, docker_course)
        express_course = db.scalar(select(Course).where(Course.slug == "express-js"))
        if express_course:
            express_course.category_id = categories["backend-development"].id
            seed_express_course(db, express_course)
        fastapi_course = db.scalar(select(Course).where(Course.slug == "fastapi"))
        if fastapi_course:
            fastapi_course.category_id = categories["backend-development"].id
            seed_fastapi_course(db, fastapi_course)
        java_course = db.scalar(select(Course).where(Course.slug == "java"))
        if java_course:
            seed_java_course(db, java_course)
        advanced_java_course = db.scalar(select(Course).where(Course.slug == "advanced-java"))
        if advanced_java_course:
            seed_advanced_java_course(db, advanced_java_course)
        jquery_course = db.scalar(select(Course).where(Course.slug == "jquery"))
        if jquery_course:
            seed_jquery_course(db, jquery_course)
        bootstrap_course = db.scalar(select(Course).where(Course.slug == "bootstrap"))
        if bootstrap_course:
            seed_bootstrap_course(db, bootstrap_course)
        typescript_course = db.scalar(select(Course).where(Course.slug == "typescript"))
        if typescript_course:
            seed_typescript_course(db, typescript_course)
        php_course = db.scalar(select(Course).where(Course.slug == "php"))
        if php_course:
            seed_php_course(db, php_course)
        csharp_course = db.scalar(select(Course).where(Course.slug == "csharp"))
        if csharp_course:
            csharp_course.category_id = categories["backend-development"].id
            seed_csharp_course(db, csharp_course)
        dart_course = db.scalar(select(Course).where(Course.slug == "dart"))
        if dart_course:
            dart_course.category_id = categories["mobile-development"].id
            seed_dart_course(db, dart_course)
        flutter_course = db.scalar(select(Course).where(Course.slug == "flutter"))
        if flutter_course:
            flutter_course.category_id = categories["mobile-development"].id
            seed_flutter_course(db, flutter_course)
        git_course = db.scalar(select(Course).where(Course.slug == "git"))
        if git_course:
            git_course.category_id = categories["developer-tools"].id
            seed_git_course(db, git_course)
        github_course = db.scalar(select(Course).where(Course.slug == "github"))
        if github_course:
            github_course.category_id = categories["devops-cloud"].id
            seed_github_course(db, github_course)
        go_course = db.scalar(select(Course).where(Course.slug == "go"))
        if go_course:
            go_course.category_id = categories["programming-languages"].id
            seed_go_course(db, go_course)
        kotlin_course = db.scalar(select(Course).where(Course.slug == "kotlin"))
        if kotlin_course:
            kotlin_course.category_id = categories["mobile-development"].id
            seed_kotlin_course(db, kotlin_course)
        data_analysis_course = db.scalar(select(Course).where(Course.slug == "data-analysis"))
        if data_analysis_course:
            data_analysis_course.category_id = categories["data-analytics"].id
            seed_data_analysis_course(db, data_analysis_course)
        data_structures_course = db.scalar(select(Course).where(Course.slug == "data-structures"))
        if data_structures_course:
            data_structures_course.category_id = categories["computer-science"].id
            seed_data_structures_course(db, data_structures_course)
        algorithms_course = db.scalar(select(Course).where(Course.slug == "algorithms"))
        if algorithms_course:
            algorithms_course.category_id = categories["computer-science"].id
            seed_algorithms_course(db, algorithms_course)
        aws_course = db.scalar(select(Course).where(Course.slug == "aws"))
        if aws_course:
            aws_course.category_id = categories["cloud-computing"].id
            seed_aws_course(db, aws_course)
        ci_cd_course = db.scalar(select(Course).where(Course.slug == "ci-cd"))
        if ci_cd_course:
            ci_cd_course.category_id = categories["devops-ci-cd"].id
            seed_ci_cd_course(db, ci_cd_course)
        cybersecurity_course = db.scalar(select(Course).where(Course.slug == "cybersecurity-fundamentals"))
        if cybersecurity_course:
            cybersecurity_course.category_id = categories["cybersecurity-information-security"].id
            seed_cybersecurity_fundamentals_course(db, cybersecurity_course)
        seed_challenges(db)
        seed_projects(db)

if __name__ == "__main__":
    main()
