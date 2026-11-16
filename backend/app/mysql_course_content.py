"""Authored MySQL vertical slice for the idempotent catalog seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

PLANNED_MODULES = [
    "Introduction to MySQL", "Database & SQL Fundamentals", "MySQL Installation & Setup", "MySQL Workbench & CLI",
    "MySQL Database Architecture", "Creating Databases & Tables", "SQL Data Types", "SQL Constraints & Keys",
    "INSERT Operations", "SELECT Queries", "Filtering & Operators", "Sorting & Pagination", "UPDATE Operations",
    "DELETE & TRUNCATE", "SQL Functions & Expressions", "Aggregate Functions", "GROUP BY & HAVING",
    "Relational Database Design", "SQL Joins", "Subqueries", "Common Table Expressions", "Views",
    "Stored Procedures & Functions", "Triggers & Events", "Transactions & ACID", "Database Normalization",
    "Indexes Fundamentals", "Query Optimization & EXPLAIN", "InnoDB & Concurrency", "MySQL Users & Privileges",
    "Database Security", "Backup & Restore", "Replication & High Availability", "MySQL Monitoring & Troubleshooting",
    "MySQL with PHP & Laravel", "MySQL with Python & FastAPI", "MySQL with Node.js & Express",
    "Docker, Cloud & Production MySQL", "Professional MySQL Projects", "Final MySQL Capstone & Assessment",
]

MODULE_ONE = [
    ("What MySQL Is", "relational tables, SQL, rows, columns, and constraints",
     "CREATE DATABASE academy_demo; USE academy_demo;",
     "sql", "MySQL is a relational database system that stores structured data in tables and uses SQL to define, query, and protect relationships. A reliable schema makes keys, constraints, ownership, and expected access patterns explicit.",
     "MySQL သည် structured data ကို table များအတွင်း သိမ်းဆည်းပြီး SQL ဖြင့် query နှင့် relationship များကို စီမံသည်။ Key နှင့် constraint များသည် data integrity ကိုကာကွယ်သည်။",
     "Compare a student table with a document model and list the fields that need keys or constraints.",
     ("MySQL သည် မည်သည့် database အမျိုးအစားဖြစ်သနည်း?", ["Relational database system", "Only a file compressor", "A frontend framework"], "Relational database system", "MySQL organizes structured data in related tables.")),
    ("Database and SQL Fundamentals", "schemas, tables, rows, columns, and declarative queries",
     "CREATE TABLE courses (id INT PRIMARY KEY, title VARCHAR(120) NOT NULL);",
     "sql", "SQL describes the result or data change while the database engine chooses an execution plan. Tables represent entities, columns represent attributes, and constraints express valid states. Separate schema design from application presentation.",
     "SQL သည် result နှင့် data change ကိုဖော်ပြသော declarative language ဖြစ်သည်။ Table သည် entity၊ column သည် attribute ဖြစ်ပြီး constraint က valid state ကိုသတ်မှတ်သည်။",
     "Design a courses table with a primary key, unique slug, publication flag, and created timestamp.",
     ("SQL query သည် ဘာကိုအဓိကဖော်ပြသနည်း?", ["The desired data result or change", "The browser layout", "A password"], "The desired data result or change", "The database chooses how to execute a declarative query.")),
    ("Tables, Data Types, and Keys", "numeric, text, date, boolean, primary, and foreign keys",
     "CREATE TABLE enrollments (id BIGINT PRIMARY KEY, course_id BIGINT NOT NULL, user_id BIGINT NOT NULL);",
     "sql", "Choose types based on range, precision, indexing, and semantics. Primary keys identify rows; foreign keys protect references. Use appropriate lengths and avoid storing secrets or ambiguous text where a constrained type is available.",
     "Data type ရွေးချယ်ရာတွင် range၊ precision၊ indexing နှင့် meaning ကိုစဉ်းစားပါ။ Primary key သည် row ကိုခွဲခြားပြီး foreign key သည် reference ကိုကာကွယ်သည်။",
     "Sketch courses, users, and enrollments with primary and foreign-key relationships.",
     ("Foreign key ၏ အဓိကတာဝန်က ဘာလဲ?", ["Protect references between related tables", "Encrypt every password", "Replace a transaction"], "Protect references between related tables", "Foreign keys preserve referential integrity.")),
    ("CREATE TABLE and Constraints", "NOT NULL, UNIQUE, CHECK, defaults, and referential integrity",
     "CREATE TABLE users (id BIGINT PRIMARY KEY, email VARCHAR(255) NOT NULL UNIQUE, active BOOLEAN NOT NULL DEFAULT TRUE);",
     "sql", "Constraints move important invariants into the database. NOT NULL prevents missing values, UNIQUE prevents duplicates, CHECK expresses allowed ranges where supported, and defaults make safe state explicit. Application validation is useful but not a replacement for database constraints.",
     "Constraint များသည် data invariant ကို database အတွင်းသတ်မှတ်ပေးသည်။ Application validation ရှိသော်လည်း database constraint ကိုအစားမထိုးနိုင်ပါ။",
     "Add constraints for a course slug, progress percentage, and enrollment relationship.",
     ("Database constraint များ၏ အကျိုးက ဘာလဲ?", ["They prevent invalid states at the data boundary", "They create UI buttons", "They expose credentials"], "They prevent invalid states at the data boundary", "Constraints protect integrity even when multiple clients write.")),
    ("INSERT and SELECT", "creating rows, selecting columns, and limiting exposure",
     "INSERT INTO courses (id, title) VALUES (1, 'MySQL Foundations'); SELECT id, title FROM courses;",
     "sql", "INSERT creates rows and SELECT reads them. Name columns explicitly, validate inputs, project only necessary fields, and use parameters from application code. Never concatenate user input into SQL strings.",
     "INSERT သည် row ဖန်တီးပြီး SELECT သည် row ဖတ်သည်။ Column များကို explicit ရေးပြီး application တွင် parameterized query သုံးပါ။",
     "Insert two disposable courses and select only id, title, and published fields.",
     ("Application SQL တွင် user input ကို ဘယ်လိုထည့်သင့်သနည်း?", ["Use prepared/parameterized statements", "Concatenate strings directly", "Store it in a password field"], "Use prepared/parameterized statements", "Parameters reduce SQL injection risk.")),
    ("WHERE, Operators, and NULL", "filters, comparisons, boolean logic, and three-valued logic",
     "SELECT id, title FROM courses WHERE published = TRUE AND title IS NOT NULL;",
     "sql", "WHERE filters rows. Use IS NULL rather than = NULL, group OR conditions deliberately, and validate sort/filter fields at API boundaries. Query behavior around NULL is different from ordinary equality and should be tested.",
     "WHERE သည် row များကို filter လုပ်သည်။ NULL ကို = ဖြင့်မစစ်ဘဲ IS NULL/IS NOT NULL သုံးပြီး OR condition ကို group လုပ်ပါ။",
     "Write a safe filter for published courses with a title search and an explicit limit.",
     ("NULL ကို ဘယ်လိုစစ်သင့်သနည်း?", ["Use IS NULL or IS NOT NULL", "Use = NULL", "Ignore the condition"], "Use IS NULL or IS NOT NULL", "NULL represents an unknown or missing value.")),
    ("Sorting, Pagination, and Aggregates", "ORDER BY, LIMIT, OFFSET, counts, and stable results",
     "SELECT title FROM courses ORDER BY title ASC, id ASC LIMIT 10 OFFSET 0;",
     "sql", "Pagination needs deterministic ordering and a bounded page size. COUNT, SUM, AVG, and other aggregates summarize rows; make sure the filter and null behavior match the requirement. Index fields used for common filters and ordering after measuring.",
     "Pagination တွင် stable ordering နှင့် bounded page size လိုအပ်သည်။ COUNT/SUM/AVG က row များကို summarize လုပ်ပြီး index ကို workload အလိုက်ထည့်ပါ။",
     "Design page two for a course list and a count query for published records.",
     ("Pagination အတွက် ဘာကအရေးကြီးသနည်း?", ["Stable ordering and a bounded page size", "Unlimited OFFSET", "Returning every column"], "Stable ordering and a bounded page size", "Stable ordering prevents duplicates or gaps between pages.")),
    ("First Safe SQL Workflow", "CRUD verification, transactions, cleanup, and application boundaries",
     "START TRANSACTION; UPDATE courses SET title = 'MySQL Basics' WHERE id = 1; COMMIT;",
     "sql", "A safe workflow uses isolated practice tables, explicit columns, precise WHERE clauses, prepared statements, transaction boundaries, expected results, and cleanup. The Academy playground simulates SQL in memory and never sends student queries to platform PostgreSQL.",
     "Safe SQL workflow တွင် isolated data၊ explicit column၊ precise WHERE၊ prepared statement၊ transaction နှင့် cleanup ပါဝင်သည်။ Academy playground သည် in-memory simulation ဖြစ်သည်။",
     "Complete the SQL playground CRUD challenge and record the query, expected result, and reset step.",
     ("Academy SQL playground သည် ဘာကိုအသုံးပြုသနည်း?", ["An isolated in-memory simulation", "Production PostgreSQL", "A student's real MySQL server"], "An isolated in-memory simulation", "The simulator protects platform and student data.")),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(position: int, item: tuple) -> str:
    title, topic, commands, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "No SQL experience is required; basic data concepts help." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the SQL playground and complete the first CRUD lab."
    return f"""Introduction
{title} introduces {topic} through safe, reproducible MySQL practice.

Learning objectives
- Explain {topic} and its place in relational database design.
- Write precise SQL with constraints, parameters, filters, and verification.
- Keep all exercises inside isolated practice data.

Prerequisites
{prerequisite}

Relational architecture explanation
application/API -> prepared statement -> MySQL server -> database -> tables -> indexes/constraints -> transaction log

Detailed theory
{theory}

MySQL SQL examples
{commands}

Expected results
Verify returned rows, columns, order, affected-row counts, and transaction state. Exact formatting varies by MySQL client version; never assume a mutation succeeded without checking it.

Step-by-step implementation
1. Select the isolated database and practice tables.
2. Inspect a small, known dataset.
3. Apply a parameterized and precisely filtered operation.
4. Verify the result and reset disposable data.

ER and schema explanation
Start with entities, attributes, keys, cardinality, constraints, access patterns, and transaction boundaries. Normalize repeated facts where appropriate and denormalize only for a measured requirement.

Common errors
- Running UPDATE or DELETE without a precise WHERE clause.
- Comparing NULL with = instead of IS NULL.
- Concatenating user input into SQL.
- Returning unnecessary columns or unbounded result sets.

Troubleshooting
Check database/table names, column types, NULL behavior, constraint errors, affected-row counts, indexes, locks, permissions, and the smallest reproducible query. Reset the virtual database when a practice state is unclear.

Best practices
- Use prepared statements, least-privilege users, explicit columns, bounded pagination, and transactions.
- Add constraints and indexes from real access patterns.
- Keep credentials server-side and use TLS, backups, audit logs, and restore tests.

Security considerations
The Academy playground is isolated and in-memory. It never executes untrusted SQL against platform PostgreSQL, a production database, or a student's MySQL server. Never place database credentials in frontend code.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Build a small virtual course catalog with tables, keys, constraints, CRUD operations, a parameterized filter, deterministic sorting, pagination, and a reset/cleanup note.

Summary
You can now reason about {topic} with relational modeling, precise SQL, verification, and security boundaries.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
Examples are predefined educational content. No production database or untrusted SQL execution is available.
"""

def seed_mysql_course(db, course):
    course.title = "MySQL Database Development — From Zero to Professional Database Developer & Administrator"
    course.short_description = "A free, practical path from relational design and SQL to performance, security, operations, and application integration."
    course.description = "Learn MySQL architecture, tables, constraints, CRUD, joins, subqueries, CTEs, views, procedures, transactions, normalization, indexes, optimization, security, backups, replication, monitoring, and application integration."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 45
    course.outcomes = "Design relational schemas with keys, constraints, normalization, and referential integrity|Write safe SQL for CRUD, joins, subqueries, CTEs, aggregation, transactions, and pagination|Optimize queries with indexes and EXPLAIN while preserving correctness|Integrate MySQL securely with PHP, Python, FastAPI, Node.js, and production operations"
    course.requirements = "Basic programming and data concepts are helpful; no MySQL experience is required."
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
        lesson.duration_minutes, lesson.status, lesson.published = 45, "published", True
        example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        values = {"title": f"{title} example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe MySQL example using isolated practice data; the Academy does not execute it against production.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review schema design, precise SQL, verification, and secure server-side boundaries before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: the Academy playground executes student SQL against platform PostgreSQL.", ["True", "False"], "False", "The playground uses isolated in-memory simulation."),
            ("Which practice protects relational data integrity?", ["Constraints, prepared statements, precise filters, and verified writes", "Empty update filters", "Direct browser database credentials"], "Constraints, prepared statements, precise filters, and verified writes", "Safe database work combines schema and application controls.")
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

