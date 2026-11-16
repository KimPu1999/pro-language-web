"""Idempotent PostgreSQL Database Development vertical-slice seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion


PLANNED_MODULES = [
    "Introduction to PostgreSQL", "Database & SQL Fundamentals", "PostgreSQL Installation & Setup", "psql & pgAdmin",
    "PostgreSQL Architecture", "Databases, Schemas & Tables", "PostgreSQL Data Types", "Constraints & Data Integrity",
    "SQL SELECT Fundamentals", "INSERT, UPDATE & DELETE", "Filtering & Operators", "Sorting, Pagination & Limits",
    "SQL Joins", "Subqueries & CTEs", "Aggregate Functions & GROUP BY", "Window Functions", "Views & Materialized Views",
    "Database Design & Normalization", "Indexes Fundamentals", "Advanced Indexing", "Query Planning & EXPLAIN",
    "Transactions & ACID", "MVCC & Isolation Levels", "Locks & Deadlocks", "Functions & PL/pgSQL", "Triggers & Procedures",
    "JSONB, Arrays & Full-Text Search", "PostgreSQL with Python & FastAPI", "PostgreSQL with Node.js", "PostgreSQL with Laravel",
    "PostgreSQL with Prisma", "Authentication, Roles & Privileges", "Row-Level Security & Multi-Tenancy", "SQL Injection Prevention",
    "Backup, Restore & PITR", "Replication & High Availability", "Performance Monitoring & Tuning", "Docker, Cloud & Production Operations",
    "Professional PostgreSQL Projects", "Final PostgreSQL Capstone & Assessment",
]

MODULE_ONE = [
    ("What PostgreSQL Is", "an open-source relational database, SQL, transactions, and extensibility",
     "CREATE TABLE courses (\n  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,\n  title text NOT NULL\n);", "sql",
     "PostgreSQL is a relational database with strong SQL semantics, transactions, constraints, indexes, extensions, and operational tooling. A production database needs schema ownership, migrations, least-privilege roles, backups, monitoring, and an application boundary.",
     "PostgreSQL သည် SQL၊ transaction၊ constraint၊ index နှင့် extension များပါသော relational database ဖြစ်သည်။ Production တွင် migration၊ least privilege၊ backup နှင့် monitoring လိုအပ်သည်။",
     "Describe a course database with courses, lessons, and enrollments, then identify the primary key and one foreign key.",
     ("PostgreSQL သည် ဘာအမျိုးအစား database ဖြစ်သနည်း?", ["Relational database", "Only a text editor", "A browser framework"], "Relational database", "PostgreSQL stores relational data and provides SQL and transaction semantics.")),
    ("Tables, Rows, and Columns", "relations, keys, data types, and schema ownership",
     "CREATE TABLE lessons (\n  id bigint PRIMARY KEY,\n  course_id bigint NOT NULL,\n  title text NOT NULL\n);", "sql",
     "A table models a relation with columns and rows. Primary keys identify rows, foreign keys represent relationships, and data types express valid values. Names and constraints should reflect business invariants rather than relying on application code alone.",
     "Table တွင် column နှင့် row များရှိပြီး primary key က row identity၊ foreign key က relationship ကိုဖော်ပြသည်။ Constraint များကို database တွင်ပါ ထိန်းပါ။",
     "Choose types and constraints for a lessons table and explain why course_id should reference courses.",
     ("Primary key ၏ ရည်ရွယ်ချက်က ဘာလဲ?", ["Identify a row uniquely", "Encrypt every value", "Replace backups"], "Identify a row uniquely", "A primary key provides row identity and uniqueness.")),
    ("Installing PostgreSQL Safely", "local environments, roles, connection strings, and disposable databases",
     "psql --version\ncreatedb academy_lab\npsql academy_lab", "bash",
     "Use a local or disposable environment for practice. Keep connection strings and passwords outside source control, use a dedicated role, and verify the target database before running DDL or writes. Never point the playground at the Academy production database.",
     "Practice အတွက် local/disposable database သုံးပြီး connection secret များကို source control မထည့်ပါနှင့်။ Target database ကို မစစ်ဘဲ write မလုပ်ပါနှင့်။",
     "Write a preflight checklist that confirms host, database, role, backup status, and cleanup before a schema exercise.",
     ("Database practice မစမီ ဘာကိုစစ်သင့်သနည်း?", ["Target, role, scope, and cleanup plan", "Only screen theme", "A production password in code"], "Target, role, scope, and cleanup plan", "A preflight prevents accidental writes to the wrong database.")),
    ("psql and Query Workflow", "connections, meta-commands, transactions, and readable SQL",
     "\\conninfo\n\\dt\nSELECT current_database();\nSELECT now();", "psql",
     "psql is a terminal client for SQL and database inspection. Meta-commands begin with a backslash, while SQL statements use the server parser. Use readable formatting, explicit schema names when needed, and transactions for multi-step changes.",
     "psql သည် SQL execute နှင့် database inspection အတွက် terminal client ဖြစ်သည်။ Backslash command နှင့် SQL statement ကို ခွဲခြားသိပါ။",
     "Connect to a disposable database, inspect tables, run a read-only query, and record the current database identity.",
     ("\\dt သည် ဘာကိုပြသနည်း?", ["Tables list", "Passwords", "Query plan only"], "Tables list", "\\dt is a psql meta-command that lists tables.")),
    ("PostgreSQL Architecture", "client/server processes, shared buffers, WAL, storage, and connections",
     "client -> connection -> PostgreSQL backend\n                 -> shared buffers\n                 -> WAL -> durable storage", "text",
     "A PostgreSQL deployment includes clients, backend processes, shared memory, storage files, WAL, and background workers. Connections, memory, durability, and failure recovery are operational concerns; an ORM does not remove them.",
     "PostgreSQL architecture တွင် client၊ backend process၊ shared buffer၊ WAL နှင့် storage ပါဝင်သည်။ ORM သုံးလည်း connection၊ durability နှင့် recovery ကို စီမံရမည်။",
     "Map a SELECT and a committed UPDATE through client, backend, shared buffers, WAL, and durable storage.",
     ("WAL ၏ အဓိကရည်ရွယ်ချက်က ဘာလဲ?", ["Durability and recovery record", "UI styling", "User avatar storage only"], "Durability and recovery record", "Write-ahead logging supports durability and crash recovery.")),
    ("Schema Design and Constraints", "normalization, foreign keys, uniqueness, checks, and integrity",
     "CREATE TABLE enrollments (\n  student_id bigint REFERENCES users(id),\n  course_id bigint REFERENCES courses(id),\n  PRIMARY KEY (student_id, course_id)\n);", "sql",
     "Schema design places important invariants close to data. Normalize repeated facts, use foreign keys for relationships, unique constraints for identity, and CHECK constraints for valid ranges. Application validation improves UX but cannot replace database constraints.",
     "Schema design တွင် repeated fact များကို normalize လုပ်ပြီး foreign key၊ unique နှင့် CHECK constraint များသုံးပါ။ Application validation တစ်ခုတည်း မလုံလောက်ပါ။",
     "Design an enrollment join table that prevents duplicate student-course rows and rejects missing references.",
     ("Duplicate enrollment ကာကွယ်ရန် ဘာသုံးသင့်သနည်း?", ["Unique or composite primary key", "A UI placeholder", "An unbounded text field"], "Unique or composite primary key", "Database uniqueness prevents duplicate relationships.")),
    ("SELECT, Filtering, and Ordering", "projection, WHERE, ORDER BY, limits, and safe parameterization",
     "SELECT id, title\nFROM courses\nWHERE published = true\nORDER BY title\nLIMIT 10;", "sql",
     "A SELECT should request only needed columns and rows. WHERE filters, ORDER BY makes ordering deterministic, and LIMIT bounds the result. Use parameters from application code instead of concatenating user input into SQL.",
     "SELECT တွင် လိုအပ်သော column/row ပဲယူပြီး WHERE၊ ORDER BY နှင့် LIMIT ကို သုံးပါ။ User input ကို SQL string ထဲ မပေါင်းပါနှင့်။",
     "Add a stable secondary sort to a paginated course query and explain what happens when titles are equal.",
     ("Pagination query တွင် ဘာထည့်သင့်သနည်း?", ["Deterministic ORDER BY and bounded LIMIT", "Only SELECT *", "A password"], "Deterministic ORDER BY and bounded LIMIT", "Stable ordering and bounds make pagination predictable.")),
    ("First PostgreSQL Data Workflow", "DDL, CRUD, transactions, verification, and safe cleanup",
     "BEGIN;\nINSERT INTO courses (title, published) VALUES ('Lab Course', false);\nSELECT title, published FROM courses WHERE title = 'Lab Course';\nROLLBACK;", "sql",
     "A reliable workflow uses a disposable target, explicit schema, a small change, verification, a transaction boundary, and cleanup. Read the result before committing. Never use course exercises to access platform tables or production data.",
     "Reliable database workflow တွင် disposable target၊ explicit schema၊ small change၊ verification နှင့် transaction boundary ပါသည်။ Platform production data ကို မထိပါနှင့်။",
     "Run a synthetic transaction that inserts a row, verifies it, and rolls back. Record expected and observed results.",
     ("Practice SQL ကို ဘယ် database တွင် run သင့်သနည်း?", ["Isolated disposable database", "Academy production database", "Unknown public database"], "Isolated disposable database", "Isolation prevents student experiments from affecting platform data.")),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, example, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "Basic programming and SQL familiarity are helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the query visualizer and complete the first database lab."
    return f"""Introduction
{title} introduces {topic} through a safe, reproducible database workflow.

Learning objectives
- Explain {topic} and its role in PostgreSQL.
- Design explicit schema, query, transaction, and verification boundaries.
- Keep credentials, production data, and unsafe execution outside the learning environment.

Prerequisites
{prerequisite}

Official database boundary
The Academy playground is a deterministic in-memory simulation. It never executes student SQL against platform PostgreSQL or exposes production tables.

Detailed theory
{theory}

Schema diagram
courses (id PK) 1 ---- * lessons (id PK, course_id FK)
users (id PK)   1 ---- * enrollments (student_id FK, course_id FK)

SQL example ({language})
{example}

Expected query result
Output depends on the disposable local dataset. Verify database name, role, affected rows, constraints, and result ordering; never assume an empty or missing result is a server failure.

Step-by-step implementation
1. Confirm the isolated target database and role.
2. Define or inspect the schema and constraints.
3. Use parameterized values and a bounded query.
4. Verify expected results and transaction behavior.
5. Commit only after review, then document cleanup and recovery.

Code explanation
Separate schema definition, query intent, parameters, result interpretation, and operational evidence. PostgreSQL constraints protect invariants even when multiple application clients write concurrently.

Common errors
- Running DDL or DELETE against the wrong database.
- Omitting a WHERE clause or deterministic ORDER BY.
- Treating application validation as a database constraint.
- Exposing connection strings or using platform tables in a playground.

Troubleshooting
Check connection identity, schema search path, role privileges, data types, constraints, locks, transaction state, and the exact query plan. Reproduce with synthetic data and reset disposable state before retrying.

Best practices
- Use migrations, explicit columns, parameterized queries, least-privilege roles, backups, bounded reads, indexes based on evidence, and tested recovery.
- Prefer transactions for related writes and verify affected rows.
- Keep database secrets server-side and use TLS for remote connections.

Security considerations
Student SQL must never run against the Academy production database. Use the in-memory simulator or an isolated disposable database with restrictions, timeouts, and no platform-data access.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Design a small course database with an ERD, constraints, migration plan, two verified queries, one transaction, test data, rollback steps, and a least-privilege role plan.

Summary
You can now reason about {topic} using schema, query, transaction, security, and operations boundaries.

Next lesson
{next_lesson}

Myanmar explanation
{mm}
"""


def seed_postgresql_course(db, course):
    course.title = "PostgreSQL Database Development — From Zero to Professional"
    course.short_description = "A free practical path through SQL, schema design, indexes, transactions, security, performance, recovery, and production PostgreSQL."
    course.description = "Learn PostgreSQL architecture, psql, schemas, constraints, SQL, joins, CTEs, indexes, EXPLAIN, ACID, MVCC, locks, PL/pgSQL, JSONB, application integration, roles, RLS, backups, replication, monitoring, Docker, and production operations."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 50
    course.outcomes = "Design relational schemas with keys, constraints, normalization, and migrations|Write safe SQL with filtering, joins, aggregates, CTEs, windows, and parameterization|Reason about indexes, query plans, transactions, MVCC, locks, backups, and recovery|Integrate PostgreSQL securely with FastAPI, Node.js, Laravel, Prisma, and multi-tenant systems"
    course.requirements = "Basic programming and SQL familiarity are helpful; no PostgreSQL administration experience is required."
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
        lesson.duration_minutes, lesson.status, lesson.published = 50, "published", True
        example_row = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        values = {"title": f"{title} SQL example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe PostgreSQL example for an isolated learning database; never run it against platform production data.", "position": 1}
        if not example_row:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example_row, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review target database identity, schema constraints, parameterization, transactions, and cleanup before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: the Academy playground executes student SQL against production PostgreSQL.", ["True", "False"], "False", "The playground uses deterministic in-memory state."),
            ("Which practice protects a database write workflow?", ["Verify target, use parameters, and use a deliberate transaction", "Run DELETE without a WHERE clause", "Embed credentials in frontend code"], "Verify target, use parameters, and use a deliberate transaction", "Safe database work is explicit, bounded, and isolated."),
        ]
        for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
            row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
            values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
            if not row:
                db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
            else:
                for key, value in values.items():
                    setattr(row, key, value)
    db.flush()
