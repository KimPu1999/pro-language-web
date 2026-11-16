"""Idempotent SQLite vertical-slice course content seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

PLANNED_MODULES = [
    "Introduction to SQLite", "SQLite vs MySQL vs PostgreSQL", "Installation & Development Tools", "SQLite Database Files",
    "SQLite CLI Fundamentals", "SQLite Data Types & Affinity", "CREATE TABLE & Schema Design", "INSERT & SELECT Fundamentals",
    "WHERE & Filtering", "ORDER BY, LIMIT & OFFSET", "UPDATE & DELETE", "Constraints & Data Integrity", "Foreign Keys & Relationships",
    "SQLite Functions", "Aggregate Functions", "GROUP BY & HAVING", "SQLite Joins", "Subqueries & Nested Queries",
    "Common Table Expressions", "Window Functions", "Views & Reusable Queries", "Indexes & Query Optimization", "EXPLAIN QUERY PLAN",
    "Transactions & ACID", "Concurrency & WAL Mode", "Triggers & Audit Tables", "JSON & Full-Text Search", "Database Normalization & ERD",
    "SQLite with Python", "SQLite with Node.js", "SQLite with React & Web Apps", "SQLite for Mobile & Flutter", "SQLite with FastAPI",
    "SQLite Security Best Practices", "Backup, Recovery & Integrity", "Schema Migrations & Versioning", "Performance & Large Datasets",
    "Production SQLite Architecture", "Professional SQLite Projects", "Final SQLite Capstone & Assessment",
]

MODULE_ONE = [
    ("What SQLite Is", "embedded database files, zero-configuration operation, and application boundaries", "CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT NOT NULL);\nINSERT INTO courses(title) VALUES ('SQLite Foundations');\nSELECT * FROM courses;", "sql", "SQLite is a small embedded relational database engine stored in a file or memory. It is useful for local apps, tests, mobile, prototypes, and some production workloads. It is not the platform's PostgreSQL database and must be selected with concurrency, durability, backup, and access requirements in mind.", "SQLite သည် file သို့မဟုတ် memory ထဲတွင် embedded relational database အဖြစ် run သည်။ Local app၊ test နှင့် mobile အတွက်အသုံးဝင်ပြီး platform PostgreSQL ကိုအစားမထိုးပါ။", "List three SQLite use cases and one workload better served by a client/server database.", ("SQLite ၏ အဓိကလက္ခဏာက ဘာလဲ?", ["An embedded relational database", "A CSS framework", "A public database service"], "An embedded relational database", "SQLite runs inside an application process and stores data in a database file or memory.")),
    ("SQLite Compared with Server Databases", "embedded files, client/server tradeoffs, and workload selection", "SQLite: application -> local file\nPostgreSQL: application -> network server -> database", "text", "SQLite has no separate server process, which simplifies deployment and local development. PostgreSQL and MySQL provide stronger multi-client operational features and network service boundaries. Choose from measured concurrency, scale, backup, replication, authorization, and operational requirements rather than brand preference.", "SQLite တွင် server process သီးသန့်မလိုဘဲ local file ကိုသုံးသည်။ PostgreSQL/MySQL သည် multi-client၊ network နှင့် operations အတွက်ပိုသင့်တော်နိုင်သည်။", "Build a comparison table for a mobile cache, analytics report, and multi-tenant API database.", ("SQLite ကို ဘယ်လိုရွေးသင့်သနည်း?", ["Match workload and operational requirements", "Use it for every production database", "Ignore concurrency and backups"], "Match workload and operational requirements", "Database selection depends on workload and operational needs.")),
    ("SQLite Installation and CLI", "sqlite3, database files, in-memory mode, and safe local practice", "sqlite3 academy.db\n.schema\n.tables\n.quit", "bash", "The sqlite3 CLI opens a database file or `:memory:` database. Use disposable paths for practice, inspect schema before changing data, set a bounded workflow, and never open platform PostgreSQL or private files from a learning tool. SQLite syntax differs from other dialects in types, ALTER TABLE support, and operational commands.", "sqlite3 CLI သည် database file သို့မဟုတ် `:memory:` database ကိုဖွင့်သည်။ Practice တွင် disposable path သုံးပြီး platform data ကိုမထိပါနှင့်။", "Create an in-memory practice database, inspect tables and schema, then reset it.", ("SQLite practice အတွက် ဘယ် database ကိုသုံးသင့်သနည်း?", ["A disposable file or :memory: database", "Platform PostgreSQL", "A copied production file"], "A disposable file or :memory: database", "Isolated practice protects platform and private data.")),
    ("Database Files and Schema", "database file boundaries, pages, schema, and integrity checks", ".databases\nPRAGMA journal_mode;\nPRAGMA integrity_check;", "sql", "A SQLite database file contains pages for schema, tables, indexes, and journal/WAL state. File permissions and backups matter because the file is the data boundary. Use integrity checks, atomic replacement, tested restores, and secure storage; do not treat a file path as authorization.", "SQLite database file သည် schema၊ table၊ index နှင့် journal/WAL state ကိုသိမ်းသည်။ File permission၊ backup နှင့် restore test လိုအပ်သည်။", "Document a disposable database file, backup copy, integrity check, and restore verification.", ("Database file security အတွက် ဘာကိုစစ်သင့်သနည်း?", ["Permissions, backup, restore, and integrity", "Only its filename", "A frontend route"], "Permissions, backup, restore, and integrity", "The file is a sensitive data boundary.")),
    ("SQLite Types and Affinity", "INTEGER, TEXT, REAL, BLOB, NULL, and flexible affinity", "CREATE TABLE measurements (\n  value INTEGER,\n  label TEXT,\n  reading REAL\n) STRICT;", "sql", "SQLite uses dynamic typing with column affinity, while STRICT tables can enforce more predictable storage classes. INTEGER PRIMARY KEY has special rowid behavior. Validate application input, use constraints, and test conversions; do not assume a type declaration provides all business validation.", "SQLite တွင် dynamic typing နှင့် type affinity ရှိပြီး STRICT table ကပိုတိကျသော storage behavior ကိုပေးသည်။", "Choose types and constraints for a local settings table; explain when STRICT is useful.", ("SQLite data type behavior ကို ဘယ်လိုထိန်းသင့်သနည်း?", ["Affinity plus constraints and application validation", "Assume every value is strongly typed automatically", "Skip tests"], "Affinity plus constraints and application validation", "SQLite typing needs explicit constraints and verification.")),
    ("CREATE TABLE, Constraints, and Foreign Keys", "DDL, primary keys, UNIQUE, CHECK, NOT NULL, and relationships", "PRAGMA foreign_keys = ON;\nCREATE TABLE enrollments (\n  user_id INTEGER NOT NULL,\n  course_id INTEGER NOT NULL,\n  UNIQUE(user_id, course_id)\n);", "sql", "Define schema invariants in SQLite with primary keys, NOT NULL, UNIQUE, CHECK, and foreign keys. Enable foreign-key enforcement deliberately for each connection and test violations. DDL support and migration behavior differ from PostgreSQL; use reviewed migration steps.", "SQLite တွင် primary key၊ NOT NULL၊ UNIQUE၊ CHECK နှင့် foreign key ဖြင့် schema invariant သတ်မှတ်ပါ။ Connection တိုင်း foreign_keys ကိုစစ်ပါ။", "Design users, courses, and enrollments with a composite uniqueness rule and a foreign key.", ("SQLite foreign key enforcement အတွက် ဘာကိုလုပ်ရသနည်း?", ["Enable and verify PRAGMA foreign_keys per connection", "Assume it is always enabled", "Use a CSS class"], "Enable and verify PRAGMA foreign_keys per connection", "SQLite foreign-key enforcement must be deliberately configured and tested.")),
    ("SELECT, Joins, and Query Results", "reading data, relationships, aliases, and NULL behavior", "SELECT c.title, COUNT(e.user_id) AS learners\nFROM courses AS c\nLEFT JOIN enrollments AS e ON e.course_id = c.id\nGROUP BY c.id, c.title;", "sql", "SELECT reads rows, JOIN combines relations, and GROUP BY aggregates them. Use explicit columns, aliases, stable ordering, and bounded output. A LEFT JOIN preserves the left row and may produce NULL right-side fields. Parameterize user values and scope data to the authorized principal.", "SELECT ဖတ်ပြီး JOIN က relation များကိုပေါင်းသည်။ LEFT JOIN တွင် match မရှိသောညာဘက် value သည် NULL ဖြစ်နိုင်သည်။", "Write a course report that includes courses with zero enrollments and explain the NULL case.", ("LEFT JOIN ၏ အကျိုးက ဘာလဲ?", ["Preserve every row from the left table", "Return only matching rows", "Disable constraints"], "Preserve every row from the left table", "LEFT JOIN keeps the left relation even when no right match exists.")),
    ("Transactions, WAL, and Safe SQLite Workflow", "BEGIN, COMMIT, ROLLBACK, SAVEPOINT, WAL, and cleanup", "BEGIN;\nUPDATE courses SET title = :title WHERE id = :id;\nCOMMIT;\nPRAGMA journal_mode = WAL;", "sql", "Transactions provide atomicity and rollback; SAVEPOINT supports nested recovery points. WAL can improve reader/writer behavior but does not remove locking, busy timeouts, backup, or filesystem concerns. A safe workflow uses isolated sample data, parameters, expected output, integrity checks, and reset.", "Transaction သည် atomicity နှင့် rollback ကိုပေးပြီး WAL သည် read/write behavior ကိုကူညီနိုင်သော်လည်း lock/backup ကိုမဖျောက်နိုင်ပါ။", "Simulate a successful update, rollback, savepoint, WAL mode note, busy timeout, and reset plan.", ("Student SQLite query သည် ဘယ်နေရာမှာ run သင့်သနည်း?", ["An isolated browser/local SQLite environment", "Platform production database", "A private file copied without permission"], "An isolated browser/local SQLite environment", "SQLite practice must be isolated, bounded, and authorized.")),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, example, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "No SQLite experience is required; basic SQL concepts help." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the SQLite playground, schema designer, and transaction lab."
    return f"""Introduction
{title} introduces {topic} through safe, dialect-labelled SQLite practice.

Learning objectives
- Explain {topic} and its embedded database boundary.
- Write queries and schema changes with parameters, constraints, and verification.
- Keep experiments isolated from platform PostgreSQL and private database files.

Prerequisites
{prerequisite}

SQLite architecture diagram
application -> sqlite connection -> database file/:memory: -> tables/indexes -> journal/WAL -> result

Detailed theory
{theory}

SQLite example ({language}; SQLite syntax)
{example}

Expected query output
Exact rows, affinity conversions, pragma values, and error wording vary by SQLite version and client. Verify schema, values, affected rows, transaction state, and integrity.

Step-by-step implementation
1. Use an isolated :memory: database or disposable local file.
2. Inspect schema and enable required connection settings such as foreign_keys.
3. Use parameters, explicit columns, constraints, bounded result sets, and precise predicates.
4. Test empty, invalid, rollback, lock, and restore cases.
5. Reset disposable state and document backup/cleanup before changing files.

Interactive visualizer
Use the SQLite playground, schema designer, query visualizer, index lab, transaction lab, ERD designer, and guided labs. They are deterministic simulations and never execute student SQL against platform PostgreSQL.

Common SQLite errors
- Foreign keys silently not enforced because the connection pragma was not enabled.
- Type affinity conversion differs from a server database expectation.
- `database is locked` during concurrent writes.
- Unsupported ALTER TABLE or dialect-specific syntax.
- UPDATE/DELETE without a precise predicate.

Troubleshooting
Check SQLite version, connection pragmas, file permissions, journal mode, busy timeout, schema, parameters, indexes, transaction state, and `PRAGMA integrity_check`. Reset the simulator when its state is unclear.

Best practices
- Use parameterized queries, constraints, foreign keys, strict tables where appropriate, least file permissions, WAL with a tested backup plan, migrations, bounded queries, and integrity checks.
- Keep secrets server-side and do not replace the platform PostgreSQL source of truth with a course practice database.

Security considerations
The Academy uses isolated sample data and deterministic SQLite simulations. It does not run arbitrary student SQL against platform PostgreSQL, open private files, expose credentials, or provide unrestricted server-side query execution.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Build an isolated SQLite course catalog with STRICT or documented affinity choices, keys, foreign keys, a JOIN report, a transaction, integrity check, backup note, and reset plan.

Summary
You can now reason about {topic} with file, schema, query, transaction, security, and recovery boundaries in view.

Next lesson
{next_lesson}

Myanmar explanation
{mm}
"""


def seed_sqlite_course(db, course):
    course.title = "SQLite — From Zero to Professional Database Developer"
    course.short_description = "A free practical path through embedded databases, SQLite SQL, schema design, transactions, WAL, indexes, integrations, and production operations."
    course.description = "Learn SQLite from database files and CLI fundamentals through affinity, schema design, CRUD, constraints, foreign keys, joins, aggregation, CTEs, windows, views, indexes, EXPLAIN QUERY PLAN, transactions, WAL, triggers, JSON, FTS5, normalization, Python, Node.js, Flutter, FastAPI, security, backups, migrations, performance, and production architecture."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 55
    course.outcomes = "Build SQLite schemas with keys, constraints, foreign keys, affinity/STRICT choices, relationships, and migrations|Write safe SQLite queries with SELECT, filters, joins, aggregates, CTEs, windows, views, parameters, and bounded results|Use indexes, EXPLAIN QUERY PLAN, transactions, WAL, triggers, JSON/FTS concepts, backups, and integrity checks|Integrate SQLite with Python, Node.js, Flutter, and FastAPI while preserving secure file and connection boundaries"
    course.requirements = "Basic SQL and command-line familiarity are helpful; no SQLite experience is required."
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
        lesson.duration_minutes, lesson.status, lesson.published = 55, "published", True
        values = {"title": f"{title} query example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe SQLite example for local study; the Academy does not execute student SQL against production PostgreSQL.", "position": 1}
        example_row = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        if not example_row:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example_row, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review SQLite file boundaries, affinity, schema, joins, transactions, WAL, security, and cleanup before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: SQLite practice should use the platform PostgreSQL database.", ["True", "False"], "False", "Practice must use isolated SQLite memory or disposable files."),
            ("What protects a SQLite query boundary?", ["Parameters, constraints, scoped access, and isolated execution", "A filename alone", "A public database URL"], "Parameters, constraints, scoped access, and isolated execution", "Safe database work combines query and operational controls."),
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
