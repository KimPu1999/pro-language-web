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
                     CourseCategory, ProgrammingLanguage)

CATEGORIES = [
    ("Frontend Development", "frontend-development"),
    ("Programming Languages", "programming-languages"),
    ("Backend Development", "backend-development"),
    ("Database Development", "database-development"),
    ("DevOps & Cloud", "devops-cloud"),
    ("Cybersecurity", "cybersecurity"),
    ("Mobile Development", "mobile-development"),
    ("AI & Data Science", "ai-data-science"),
    ("Computer Science", "computer-science"),
]
COURSES = [
    ("HTML", "html", "html", "#E34F26", "frontend-development"), ("CSS", "css", "css", "#1572B6", "frontend-development"),
    ("JavaScript", "javascript", "javascript", "#F7DF1E", "frontend-development"), ("TypeScript", "typescript", "typescript", "#3178C6", "frontend-development"),
    ("React", "react", "javascript", "#61DAFB", "frontend-development"), ("Next.js", "next-js", "javascript", "#F8FAFC", "frontend-development"),
    ("jQuery", "jquery", "javascript", "#0769AD", "frontend-development"), ("Tailwind CSS", "tailwind-css", "css", "#06B6D4", "frontend-development"),
    ("Bootstrap", "bootstrap", "css", "#7952B3", "frontend-development"), ("C Programming", "c-programming", "c", "#A8B9CC", "programming-languages"),
    ("C++", "cpp", "cpp", "#00599C", "programming-languages"), ("Java", "java", "java", "#ED8B00", "programming-languages"),
    ("Advanced Java", "advanced-java", "java", "#ED8B00", "programming-languages"), ("Python", "python", "python", "#3776AB", "programming-languages"),
    ("C#", "c-sharp", "c-sharp", "#512BD4", "programming-languages"), ("Go", "go", "go", "#00ADD8", "programming-languages"),
    ("Rust", "rust", "rust", "#DEA584", "programming-languages"), ("Node.js", "node-js", "javascript", "#339933", "backend-development"),
    ("Express.js", "express-js", "javascript", "#F8FAFC", "backend-development"), ("PHP", "php", "php", "#777BB4", "backend-development"),
    ("Laravel", "laravel", "php", "#FF2D20", "backend-development"), ("FastAPI", "fastapi", "python", "#009688", "backend-development"),
    ("Django", "django", "python", "#092E20", "backend-development"), ("Spring Boot", "spring-boot", "java", "#6DB33F", "backend-development"),
    ("SQL", "sql", "sql", "#22C55E", "database-development"), ("MySQL", "mysql", "sql", "#4479A1", "database-development"),
    ("PostgreSQL", "postgresql", "sql", "#4169E1", "database-development"), ("SQLite", "sqlite", "sql", "#003B57", "database-development"),
    ("MongoDB", "mongodb", "mongodb", "#47A248", "database-development"), ("Redis", "redis", "redis", "#DC382D", "database-development"),
    ("Linux", "linux", "linux", "#FCC624", "devops-cloud"), ("Git", "git", "git", "#F05032", "devops-cloud"),
    ("GitHub", "github", "git", "#F8FAFC", "devops-cloud"), ("Docker", "docker", "docker", "#2496ED", "devops-cloud"),
    ("CI/CD", "ci-cd", "ci-cd", "#818CF8", "devops-cloud"), ("AWS", "aws", "aws", "#FF9900", "devops-cloud"),
    ("Microsoft Azure", "microsoft-azure", "azure", "#0078D4", "devops-cloud"), ("Cybersecurity Fundamentals", "cybersecurity-fundamentals", "cybersecurity", "#EF4444", "cybersecurity"),
    ("Networking Fundamentals", "networking-fundamentals", "networking", "#38BDF8", "cybersecurity"), ("Web Security", "web-security", "cybersecurity", "#F97316", "cybersecurity"),
    ("Secure Coding", "secure-coding", "cybersecurity", "#A855F7", "cybersecurity"), ("OWASP Top 10", "owasp-top-10", "cybersecurity", "#F43F5E", "cybersecurity"),
    ("Dart", "dart", "dart", "#0175C2", "mobile-development"), ("Flutter", "flutter", "dart", "#54C5F8", "mobile-development"),
    ("React Native", "react-native", "javascript", "#61DAFB", "mobile-development"), ("Kotlin", "kotlin", "kotlin", "#7F52FF", "mobile-development"),
    ("Python for AI", "python-for-ai", "python", "#3776AB", "ai-data-science"), ("Machine Learning", "machine-learning", "python", "#10B981", "ai-data-science"),
    ("Data Analysis", "data-analysis", "python", "#F59E0B", "ai-data-science"), ("Data Structures", "data-structures", "computer-science", "#6366F1", "computer-science"),
    ("Algorithms", "algorithms", "computer-science", "#8B5CF6", "computer-science"), ("Operating Systems", "operating-systems", "computer-science", "#64748B", "computer-science"),
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

def main():
    with SessionLocal.begin() as db:
        categories = {slug: get_or_create(db, CourseCategory, slug, name=name, status="active") for name, slug in CATEGORIES}
        languages = {}
        for title, course_slug, language_slug, color, _ in COURSES:
            language = db.scalar(select(ProgrammingLanguage).where(ProgrammingLanguage.slug == language_slug))
            if not language:
                display_name = title if language_slug == course_slug else language_slug.replace("-", " ").title()
                language = ProgrammingLanguage(name=display_name, slug=language_slug, color=color, status="active")
                db.add(language)
                db.flush()
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
        seed_challenges(db)

if __name__ == "__main__":
    main()
