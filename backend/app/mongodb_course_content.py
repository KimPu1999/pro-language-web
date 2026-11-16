"""Authored MongoDB vertical slice for the idempotent catalog seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

PLANNED_MODULES = [
    "Introduction to MongoDB", "Database & NoSQL Fundamentals", "MongoDB Installation & Setup", "MongoDB Atlas Fundamentals",
    "MongoDB Shell (mongosh)", "MongoDB Compass", "Documents, Collections & BSON", "MongoDB CRUD Fundamentals",
    "Insert Operations", "Find & Query Operations", "Query Operators", "Projection, Sorting & Pagination",
    "Update Operations", "Delete Operations", "Arrays & Embedded Documents", "MongoDB Data Modeling",
    "Schema Validation", "Indexes Fundamentals", "Advanced Indexing", "Aggregation Pipeline Fundamentals",
    "Advanced Aggregation", "Aggregation Performance", "Transactions & Data Consistency", "MongoDB with Node.js",
    "MongoDB with Express.js", "MongoDB with Mongoose", "MongoDB with Python", "MongoDB with FastAPI",
    "MongoDB with React Applications", "Authentication & Authorization", "MongoDB Security Best Practices",
    "Backup & Restore", "Replication & Replica Sets", "Sharding & Horizontal Scaling", "Change Streams & Real-Time Data",
    "Performance Monitoring & Optimization", "Docker & MongoDB Deployment", "MongoDB Atlas Production Operations",
    "Professional MongoDB Projects", "Final MongoDB Capstone & Assessment",
]

MODULE_ONE = [
    ("What MongoDB Is", "documents, collections, BSON, and flexible data access",
     "mongosh --nodb --eval 'printjson({course: \'mongodb\', mode: \'simulation\'})'",
     "javascript", "MongoDB is a document database that stores BSON documents in collections. Flexible documents help model application access patterns, but flexibility does not mean the absence of design. Choose fields, validation, indexes, and ownership deliberately.",
     "MongoDB သည် BSON document များကို collection များအတွင်း သိမ်းဆည်းသော document database ဖြစ်သည်။ Schema flexible ဖြစ်သော်လည်း data design မလိုအပ်တော့ခြင်းမဟုတ်ပါ။",
     "Compare a student profile document with a relational row and list the fields that should be validated.",
     ("MongoDB သည် မည်သည့် data model ကို အသုံးပြုသနည်း?", ["Document-oriented BSON data", "Only flat CSV files", "Only in-memory variables"], "Document-oriented BSON data", "MongoDB stores documents in collections.")),
    ("Databases and NoSQL Fundamentals", "access patterns, consistency, and relational versus document trade-offs",
     "use academy_demo\\nshow collections\\n// Design around known access patterns",
     "javascript", "NoSQL databases make different trade-offs around schema, joins, scaling, and access patterns. MongoDB supports rich documents and aggregation; application requirements still determine whether embedding, references, or another database is appropriate.",
     "NoSQL database များသည် schema၊ joins၊ scaling နှင့် access pattern များတွင် trade-off မတူပါ။ MongoDB တွင် embedding/reference ကို requirement အလိုက်ရွေးပါ။",
     "Choose embedding or references for an order and its line items, then explain the read/write pattern.",
     ("MongoDB data model ကို ဘာပေါ်မူတည်ပြီး design လုပ်သင့်သနည်း?", ["Application access patterns and consistency requirements", "Only document size", "Random field names"], "Application access patterns and consistency requirements", "Good document models begin with how data is used.")),
    ("Documents, Collections, and BSON", "JSON-like documents, BSON types, identifiers, and nested values",
     "db.students.insertOne({name: 'Mya', level: 'beginner', skills: ['python']})\\ndb.students.findOne({name: 'Mya'})",
     "javascript", "Documents contain fields and values, including nested objects and arrays. BSON adds types such as ObjectId, Date, Decimal128, and binary data. Keep identifiers, dates, numeric precision, and null semantics explicit.",
     "Document တွင် nested object နှင့် array များပါဝင်နိုင်သည်။ BSON တွင် ObjectId၊ Date နှင့် Decimal128 ကဲ့သို့ type များရှိသည်။",
     "Design a course document with an ObjectId, Date field, nested instructor, and tags array.",
     ("BSON သည် JSON ထက် ဘာကိုထပ်ပေးသနည်း?", ["Additional typed values such as ObjectId and Date", "Automatic authorization", "A frontend framework"], "Additional typed values such as ObjectId and Date", "BSON preserves database-oriented types.")),
    ("MongoDB CRUD Fundamentals", "create, read, update, delete, and verified outcomes",
     "db.courses.insertOne({slug: 'mongodb', published: true})\\ndb.courses.find({published: true})",
     "javascript", "CRUD operations should be scoped, validated, and observable. Reads should select the fields and indexes they need. Updates should use precise filters and operators, and deletes should be restricted to disposable practice data with a verified backup or cleanup plan.",
     "CRUD operation များတွင် filter၊ validation၊ index နှင့် cleanup ကိုသေချာစစ်ပါ။ Delete မလုပ်မီ disposable data ဖြစ်ကြောင်းအတည်ပြုပါ။",
     "Write a CRUD checklist that prevents an unscoped update or delete.",
     ("Update/delete မလုပ်မီ အရေးကြီးဆုံးက ဘာလဲ?", ["Use a precise filter and verify the target scope", "Run an empty filter", "Trust a client-supplied collection name"], "Use a precise filter and verify the target scope", "Precise filters protect data integrity.")),
    ("Find Queries and Query Operators", "filters, comparison operators, logical operators, and safe inputs",
     "db.courses.find({level: {$in: ['beginner', 'intermediate']}}, {title: 1, level: 1})",
     "javascript", "Find queries combine a filter and optional projection. Operators such as $eq, $in, $gt, $and, and $or express conditions. Validate query input, allow only supported fields/operators, and never expose unrestricted database queries from a public client.",
     "Find query တွင် filter နှင့် projection ပါဝင်သည်။ $in၊ $gt၊ $and စသော operator များကို သုံးပြီး public client မှ unrestricted query မပေးပါနှင့်။",
     "Build an allowlisted search filter for course level and publication status.",
     ("Public API query တွင် ဘာကိုကန့်သတ်သင့်သနည်း?", ["Allowed fields, operators, limits, and sort keys", "Every database operator", "Database credentials"], "Allowed fields, operators, limits, and sort keys", "Allowlisting prevents query abuse and unexpected load.")),
    ("Projection, Sorting, and Pagination", "field selection, deterministic ordering, skip/limit, and cursors",
     "db.courses.find({}, {title: 1, slug: 1}).sort({title: 1}).limit(10)",
     "javascript", "Projection reduces response size and protects unnecessary fields. Sorting needs a stable key, while skip/limit is simple for small pages and range or cursor pagination scales better for deep feeds. Index the access pattern you actually use.",
     "Projection သည် response size နှင့် မလိုအပ်သော field exposure ကိုလျှော့သည်။ Pagination တွင် stable sort key နှင့် index ကိုစဉ်းစားပါ။",
     "Design a page-two query and list the index needed for title sorting.",
     ("Projection သည် ဘာအကျိုးရှိသနည်း?", ["Returns only needed fields and reduces exposure", "Automatically encrypts every field", "Replaces authentication"], "Returns only needed fields and reduces exposure", "Projection supports performance and least data exposure.")),
    ("Updates, Deletes, and Data Integrity", "update operators, upserts, targeted deletes, and auditability",
     "db.students.updateOne({slug: 'mya'}, {$set: {level: 'intermediate'}})\\ndb.students.deleteOne({slug: 'temporary-demo'})",
     "javascript", "Use $set, $inc, $push, and $unset deliberately. Upsert only when the operation is idempotent and the filter is unique. Delete only disposable records in practice, preserve audit evidence, and use transactions when multiple documents must change together.",
     "Update တွင် $set၊ $inc၊ $push၊ $unset ကို သေချာသုံးပါ။ Upsert နှင့် delete တွင် unique filter နှင့် auditability လိုအပ်သည်။",
     "Review an update filter, add a unique condition, and describe how you would verify the result.",
     ("Unscoped update ၏ အန္တရာယ်က ဘာလဲ?", ["It can change every matching document or an unintended dataset", "It improves indexes", "It validates credentials"], "It can change every matching document or an unintended dataset", "Precise filters are a core integrity control.")),
    ("First MongoDB CRUD Workflow", "a safe virtual database workflow with verification and cleanup",
     "use academy_demo\\ndb.todos.insertMany([{title: 'Learn BSON', done: false}, {title: 'Build query', done: false}])\\ndb.todos.find({done: false})",
     "javascript", "A reliable workflow starts with a disposable database, known sample documents, small reads, precise writes, expected output, and reset/cleanup. The Academy playground uses in-memory state and does not connect to platform PostgreSQL or a real MongoDB server.",
     "Reliable workflow တွင် disposable data၊ sample documents၊ precise writes၊ expected output နှင့် reset ပါဝင်သည်။ Academy playground သည် in-memory state သာသုံးသည်။",
     "Complete the playground CRUD challenge and record the query, expected result, and reset step.",
     ("Academy MongoDB playground ၏ database က ဘာဖြစ်သနည်း?", ["An isolated in-memory simulation", "Production PostgreSQL", "A student's real Atlas cluster"], "An isolated in-memory simulation", "The simulator protects platform and student data.")),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(position: int, item: tuple) -> str:
    title, topic, commands, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "No database experience is required; basic JSON is helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the query playground and complete the first CRUD lab."
    return f"""Introduction
{title} introduces {topic} through safe, reproducible MongoDB practice.

Learning objectives
- Explain {topic} and its place in a document database.
- Choose fields, filters, indexes, and operations deliberately.
- Keep all exercises inside isolated practice data.

Prerequisites
{prerequisite}

MongoDB architecture explanation
application/API -> driver -> database -> collection -> BSON document -> index/query plan

Detailed theory
{theory}

mongosh and JSON/BSON examples
{commands}

Expected output
Verify returned documents, counts, fields, order, and write results. Exact formatting varies by mongosh version; never assume a mutation succeeded without checking it.

Step-by-step implementation
1. Select the isolated database and sample collection.
2. Inspect a small document set.
3. Apply a precise, allowlisted operation.
4. Verify the result and reset disposable data.

Data modeling explanation
Start with access patterns, document size, cardinality, consistency, validation, and indexes. Choose embedding or references intentionally instead of copying relational tables blindly.

Common errors
- Running an empty update or delete filter.
- Treating flexible schema as unplanned schema.
- Exposing unrestricted query operators through a public API.
- Returning secrets or unnecessary fields in projections.

Troubleshooting
Check database/collection names, BSON types, filter shape, field paths, indexes, permissions, result counts, and the smallest reproducible sample. Reset the virtual database when a practice state is unclear.

Best practices
- Validate input, allowlist fields/operators, use precise filters, and paginate.
- Add indexes from measured access patterns and inspect explain plans.
- Keep credentials server-side and use TLS, RBAC, backups, and audit logs in real deployments.

Security considerations
The Academy playground is isolated and in-memory. It never executes untrusted queries against platform PostgreSQL, a production database, or a student's MongoDB account. Do not place credentials in frontend code.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Build a small virtual course catalog with sample documents, CRUD operations, an allowlisted search filter, projection, deterministic sorting, pagination, and a reset/cleanup note.

Summary
You can now reason about {topic} with document modeling, precise queries, verification, and security boundaries.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
Examples are predefined educational content. No production database or untrusted query execution is available.
"""

def seed_mongodb_course(db, course):
    course.title = "MongoDB — From Zero to Professional NoSQL Database Developer"
    course.short_description = "A free, practical path from document modeling and CRUD to aggregation, security, scaling, and production operations."
    course.description = "Learn MongoDB documents, BSON, CRUD, queries, schema validation, indexing, aggregation, transactions, Node.js, Python, FastAPI, security, replication, sharding, monitoring, and Atlas operations."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 45
    course.outcomes = "Model document data around application access patterns|Use safe CRUD, filtering, projection, sorting, pagination, and aggregation workflows|Integrate MongoDB with Node.js, Express, Python, FastAPI, and React through secure server-side APIs|Understand validation, indexes, transactions, security, backup, replication, sharding, and monitoring"
    course.requirements = "Basic JSON and programming familiarity are helpful; no MongoDB experience is required."
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
        values = {"title": f"{title} example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe MongoDB example using isolated practice data; the Academy does not execute it against production.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review document modeling, precise filters, verification, and secure server-side boundaries before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: the Academy playground executes student queries against platform PostgreSQL.", ["True", "False"], "False", "The playground uses isolated in-memory simulation."),
            ("Which practice protects MongoDB data integrity?", ["Precise filters, validation, least privilege, and verified writes", "Empty update filters", "Direct browser database credentials"], "Precise filters, validation, least privilege, and verified writes", "Safe database work combines scoped operations and server-side controls.")
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

