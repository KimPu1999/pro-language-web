"""Idempotent catalog metadata seed.

Creates catalog records only. It never creates placeholder lessons and does not
replace existing curriculum, enrollments, or progress.
Run from backend: python -m app.seed
"""
from sqlalchemy import select

from .db import SessionLocal
from .models import Course, CourseCategory, ProgrammingLanguage

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
LEGACY_SLUGS = {slug: f"{language}-foundations" for _, slug, language, _, _ in COURSES}

def get_or_create(db, model, slug, **values):
    row = db.scalar(select(model).where(model.slug == slug))
    if not row:
        row = model(slug=slug, **values)
        db.add(row)
        db.flush()
    return row

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

if __name__ == "__main__":
    main()
