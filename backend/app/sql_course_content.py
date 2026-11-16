"""Idempotent SQL vertical-slice course content seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

PLANNED_MODULES = [
    "Introduction to SQL", "Relational Database Fundamentals", "SQL Environment & Tools", "SQL Syntax & Query Structure",
    "SELECT Statement Fundamentals", "Filtering with WHERE", "Sorting & Limiting Results", "SQL Data Types",
    "INSERT Statements", "UPDATE Statements", "DELETE Statements", "CREATE, ALTER & DROP", "Constraints & Data Integrity",
    "SQL Functions & Expressions", "Aggregate Functions", "GROUP BY & HAVING", "SQL Joins Fundamentals", "Advanced Joins & Relationships",
    "Subqueries", "Common Table Expressions", "Set Operations", "Window Functions", "Advanced Analytical SQL",
    "Views & Materialized Views", "Database Design & ER Diagrams", "Database Normalization", "Transactions & ACID",
    "Indexes Fundamentals", "Query Optimization & EXPLAIN", "Locks, Isolation & Concurrency", "Stored Procedures & Functions",
    "Triggers & Audit Logging", "SQL Injection Prevention", "Database Roles & Permissions", "SQL with Python & Backend APIs",
    "SQL for Reporting & Business Intelligence", "SQL Dialects & Database Differences", "Production SQL & Database Operations",
    "Professional SQL Projects", "Final SQL Capstone & Assessment",
]

MODULE_ONE = [
    ("What SQL Is", "relational data, tables, rows, columns, and declarative queries", "SELECT id, title\nFROM courses\nWHERE published = TRUE;", "sql", "SQL is a declarative language for defining, reading, and changing structured data. A relational database stores facts in tables with keys and constraints, while the query planner chooses an execution strategy. SQL is not a security boundary by itself: authorization, parameterization, and least privilege belong in the complete application.", "SQL သည် structured data ကို define၊ read နှင့် change လုပ်ရန် declarative language ဖြစ်သည်။ Key၊ constraint နှင့် authorization boundary များကိုလည်းသတ်မှတ်ရမည်။", "List three entities in a learning platform and identify one key and one relationship for each.", ("SQL ၏ အဓိကသဘောတရားက ဘာလဲ?", ["Declarative operations over structured data", "A frontend styling language", "Automatic authorization"], "Declarative operations over structured data", "SQL describes data results or changes while the database plans execution.")),
    ("Relational Tables and Keys", "entities, attributes, primary keys, foreign keys, and relationships", "CREATE TABLE enrollments (\n  id BIGINT PRIMARY KEY,\n  user_id BIGINT NOT NULL,\n  course_id BIGINT NOT NULL\n);", "sql", "Tables model entities and columns model attributes. Primary keys identify rows; foreign keys protect references; unique and check constraints preserve invariants. Design around ownership, cardinality, access patterns, and the authoritative source of truth.", "Table သည် entity၊ column သည် attribute ဖြစ်ပြီး primary key က row ကိုခွဲခြားသည်။ Foreign key နှင့် constraint များက relationship/data integrity ကိုကာကွယ်သည်။", "Sketch users, courses, and enrollments with keys, uniqueness, and a foreign-key relationship.", ("Foreign key ၏ အဓိကတာဝန်က ဘာလဲ?", ["Protect references between related tables", "Encrypt every value", "Create UI navigation"], "Protect references between related tables", "Foreign keys preserve referential integrity.")),
    ("SQL Environment and Safe Practice", "clients, dialects, disposable databases, and query boundaries", "-- Use a disposable database\nSELECT current_database();\nSELECT version();", "sql", "SQL dialects differ in types, pagination, date functions, JSON features, and DDL behavior. Practice in a disposable local or browser-isolated database, label the dialect, use bounded queries, and never point student exercises at platform PostgreSQL. Keep credentials server-side.", "SQL dialect များသည် type၊ pagination၊ date function နှင့် DDL တွင်ကွာခြားနိုင်သည်။ Disposable database သို့မဟုတ် isolated simulator သုံးပါ။", "Write a setup checklist that names the dialect, target database, timeout, row limit, and cleanup step.", ("Student SQL lab သည် ဘယ် environment ကိုသုံးသင့်သနည်း?", ["An isolated disposable database", "Platform production PostgreSQL", "A database URL in frontend code"], "An isolated disposable database", "Practice must be separated from platform infrastructure and secrets.")),
    ("SELECT and Query Structure", "projection, FROM, aliases, and logical query thinking", "SELECT c.title AS course_title\nFROM courses AS c;", "sql", "SELECT projects columns from a source relation. Use explicit columns and clear aliases rather than SELECT *. Logical processing concepts help explain results, while physical execution plans may reorder work for performance. Always bound rows in exploratory queries.", "SELECT သည် source relation မှ column များကို project လုပ်သည်။ Explicit column၊ alias နှင့် bounded result ကိုသုံးပါ။", "Write a query that returns only course id, title, and publication state with a stable alias.", ("Production query တွင် ဘာကိုရှောင်သင့်သနည်း?", ["Unbounded SELECT *", "Explicit columns", "A clear alias"], "Unbounded SELECT *", "Explicit projections reduce accidental data exposure and payload size.")),
    ("Filtering with WHERE", "comparisons, boolean logic, NULL, and parameterized filters", "SELECT id, title\nFROM courses\nWHERE published = :published\n  AND title IS NOT NULL;", "sql", "WHERE filters rows before projection. Use parameters for values, IS NULL for null checks, deliberate parentheses for OR logic, and allowlists for dynamic identifiers. Validation and authorization must still scope the query to the current user or permitted tenant.", "WHERE သည် row များကို filter လုပ်သည်။ Value များအတွက် parameter သုံးပြီး NULL ကို IS NULL ဖြင့်စစ်ပါ။", "Add a parameterized title search and bounded page size; explain the unauthorized case.", ("User input ကို SQL ထဲဘယ်လိုထည့်သင့်သနည်း?", ["Parameterized values and allowlisted identifiers", "String concatenation", "A hidden HTML input"], "Parameterized values and allowlisted identifiers", "Parameters keep data separate from SQL structure.")),
    ("ORDER BY and LIMIT", "stable sorting, pagination, and predictable result sets", "SELECT id, title\nFROM courses\nORDER BY title ASC, id ASC\nLIMIT :page_size OFFSET :offset;", "sql", "Stable ordering is essential for pagination. Limit page size at the API boundary, use a deterministic tie-breaker, and avoid exposing arbitrary sort expressions. Indexes should follow measured access patterns rather than guesswork.", "Pagination တွင် stable ordering၊ bounded page size နှင့် tie-breaker လိုအပ်သည်။ Sort field ကို allowlist လုပ်ပါ။", "Design page two of a course list and choose a stable order for duplicate titles.", ("Stable pagination အတွက် ဘာကအရေးကြီးသနည်း?", ["Deterministic ordering and bounded limits", "Unlimited rows", "Client-controlled SQL fragments"], "Deterministic ordering and bounded limits", "Stable ordering reduces duplicates and gaps between pages.")),
    ("INSERT, UPDATE, and DELETE Safely", "data changes, transactions, precise predicates, and affected rows", "INSERT INTO courses (id, title) VALUES (:id, :title);\nUPDATE courses SET title = :title WHERE id = :id;\nDELETE FROM courses WHERE id = :id;", "sql", "Mutation statements need explicit columns, parameters, precise predicates, constraints, transaction boundaries, and affected-row verification. Never run broad UPDATE or DELETE in a shared environment. Authorization is part of the service that chooses which row may change.", "Mutation query များတွင် explicit column၊ parameter၊ precise predicate၊ transaction နှင့် affected-row check လိုအပ်သည်။", "Write a transaction plan for creating an enrollment, including duplicate and unauthorized cases.", ("UPDATE/DELETE မလုပ်မီ ဘာကိုစစ်သင့်သနည်း?", ["Precise predicate, authorization, and affected rows", "Only the button label", "A production-wide wildcard"], "Precise predicate, authorization, and affected rows", "Safe mutations require exact scope and verification.")),
    ("Joins, Aggregates, and the First SQL Workflow", "relationships, counts, GROUP BY, review, and cleanup", "SELECT c.title, COUNT(e.id) AS enrollments\nFROM courses c\nLEFT JOIN enrollments e ON e.course_id = c.id\nGROUP BY c.id, c.title\nORDER BY enrollments DESC;", "sql", "Joins combine related rows and aggregates summarize groups. A reliable workflow uses a small known dataset, explicit join conditions, null-aware reasoning, bounded output, expected results, parameterized values, and reset. The playground is an isolated simulation and never executes against platform PostgreSQL.", "Join သည် relationship row များကိုပေါင်းပြီး aggregate သည် group ကို summarize လုပ်သည်။ Small dataset၊ explicit condition နှင့် reset workflow ကိုသုံးပါ။", "Complete a course enrollment report and document its join condition, null behavior, authorization scope, and reset step.", ("SQL playground သည် ဘာကိုသုံးသနည်း?", ["An isolated deterministic simulation", "Platform production PostgreSQL", "A student's private credentials"], "An isolated deterministic simulation", "The simulator protects platform data and keeps results repeatable.")),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, example, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "No SQL experience is required; basic data concepts help." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the SQL playground, query visualizer, and JOIN visualizer."
    return f"""Introduction
{title} introduces {topic} through safe, dialect-labelled SQL practice.

Learning objectives
- Explain {topic} and its relational data boundary.
- Write readable queries with validation, parameters, limits, and verification.
- Keep experiments isolated from platform PostgreSQL and private data.

Prerequisites
{prerequisite}

Database architecture diagram
application/API -> parameterized SQL -> database planner -> tables/indexes -> transaction/log -> result

Detailed theory
{theory}

SQL example ({language}; confirm dialect)
{example}

Expected query output
Exact rows, type names, timestamps, and error wording vary by engine. Verify columns, order, row counts, affected rows, transaction state, and null behavior.

Step-by-step implementation
1. Choose an isolated sample database and label its SQL dialect.
2. Inspect a small known dataset and explicit schema.
3. Use parameters, precise predicates, bounded output, and explicit columns.
4. Verify results and authorization scope; test empty and error cases.
5. Reset disposable data and document cleanup before trying mutations.

Interactive visualizer
Use the SQL playground, logical query visualizer, JOIN visualizer, ERD designer, normalization lab, transaction lab, and guided labs. They are deterministic simulations and never send student SQL to platform PostgreSQL.

Common SQL errors
- Ambiguous column names after a join.
- NULL compared with = instead of IS NULL.
- Missing GROUP BY columns or an incorrect join condition.
- UPDATE/DELETE without a precise predicate.
- SQL injection from concatenated user input.

Troubleshooting
Check table/column names, dialect syntax, data types, null behavior, join cardinality, parameters, indexes, locks, affected rows, and the smallest reproducible query. Reset the simulator when state is unclear.

Best practices
- Use explicit columns, parameters, constraints, least privilege, bounded pagination, transactions, stable ordering, tested migrations, and measured query plans.
- Keep credentials server-side and treat PostgreSQL or another durable database as the platform source of truth.

Security considerations
The Academy uses isolated sample data and deterministic simulations. It does not run arbitrary student SQL against platform PostgreSQL, expose credentials, connect to production databases, or provide unrestricted server-side query execution.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Build an isolated course-report schema with keys, a parameterized filter, a JOIN aggregate, stable pagination, an authorization note, expected output, and a reset plan.

Summary
You can now reason about {topic} with schema, query, performance, security, and cleanup boundaries in view.

Next lesson
{next_lesson}

Myanmar explanation
{mm}
"""


def seed_sql_course(db, course):
    course.title = "SQL — From Zero to Professional Database Developer"
    course.short_description = "A free practical path through relational design, queries, joins, analytics, transactions, performance, security, and production SQL."
    course.description = "Learn SQL from relational fundamentals through SELECT, filtering, mutations, constraints, functions, aggregation, joins, subqueries, CTEs, window functions, views, ER diagrams, normalization, transactions, indexes, EXPLAIN, concurrency, SQL injection prevention, roles, backend APIs, reporting, dialect differences, and production operations."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 55
    course.outcomes = "Write readable SQL with SELECT, filtering, sorting, mutations, constraints, functions, aggregation, GROUP BY, HAVING, and joins|Design relational schemas with keys, relationships, normalization, transactions, indexes, and migrations|Use subqueries, CTEs, window functions, views, reporting queries, and measured optimization|Integrate SQL safely with backend APIs using parameters, authorization, least privilege, and bounded execution"
    course.requirements = "Basic data and command-line familiarity are helpful; no SQL experience is required."
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
        values = {"title": f"{title} query example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe SQL example for local study; the Academy does not execute student queries against production PostgreSQL.", "position": 1}
        example_row = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        if not example_row:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example_row, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review query structure, schema, parameters, authorization, bounded output, and cleanup before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: SQL parameters replace server-side authorization.", ["True", "False"], "False", "Parameters protect query structure; authorization still scopes the current user's access."),
            ("Where should SQL practice run?", ["An isolated sample database or simulator", "Platform production PostgreSQL", "A public database with copied credentials"], "An isolated sample database or simulator", "Practice queries must not touch platform or private data."),
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
