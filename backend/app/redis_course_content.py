"""Idempotent Redis vertical-slice course content seed.

Redis examples in this module are educational only. The platform never sends
student commands to its PostgreSQL or Redis infrastructure.
"""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion


PLANNED_MODULES = [
    "Introduction to Redis", "Redis Installation & Setup", "Redis CLI Fundamentals", "Redis Architecture",
    "Keys & Key Management", "Redis Strings", "Redis Lists", "Redis Hashes", "Redis Sets", "Sorted Sets",
    "Bitmaps & Bitfields", "HyperLogLog", "Geospatial Data", "Redis Streams Fundamentals", "Key Expiration & TTL",
    "Redis Caching Fundamentals", "Caching Strategies", "Redis Pub/Sub", "Redis Streams & Consumer Groups",
    "Queues & Background Jobs", "Rate Limiting", "Session Storage", "Distributed Locks",
    "Transactions & Optimistic Locking", "Lua Scripting & Redis Functions", "Redis with Python & FastAPI",
    "Redis with Node.js & Laravel", "Redis Persistence", "Redis Replication", "Redis Sentinel", "Redis Cluster",
    "Redis Memory Management", "Performance & Benchmarking", "Redis Security & ACLs",
    "Monitoring & Troubleshooting", "Redis Data Modeling & Architecture", "Redis with PostgreSQL & Applications",
    "Docker, Cloud & Production Operations", "Professional Redis Projects", "Final Redis Capstone & Assessment",
]

MODULE_ONE = [
    ("What Redis Is", "in-memory data structures, low latency, and application boundaries",
     "SET academy:welcome \"Hello Redis\"\nGET academy:welcome", "redis",
     "Redis is an in-memory data-structure server commonly used for caching, ephemeral state, queues, rate limits, and real-time coordination. It is not a replacement for the platform's PostgreSQL system of record. Choose Redis from measured access patterns and define persistence, recovery, and eviction expectations.",
     "Redis သည် memory အတွင်း data structure များကို မြန်ဆန်စွာ ကိုင်တွယ်ပြီး cache၊ queue၊ rate limit နှင့် ephemeral state များအတွက် အသုံးဝင်သည်။ Platform PostgreSQL ကို အစားမထိုးပါ။",
     "List three Redis use cases and one case where PostgreSQL should remain the source of truth.",
     ("Redis ကို မည်သည့်အတွက် သင့်တော်သနည်း?", ["Low-latency cache and transient data", "Replacing every durable database", "Storing source credentials in the client"], "Low-latency cache and transient data", "Redis is selected for access patterns and latency needs, not as an automatic replacement for durable storage.")),
    ("Installing Redis Safely", "local development, versions, disposable data, and protected configuration",
     "redis-server --version\nredis-cli ping", "bash",
     "Use a supported local or containerized Redis version and keep practice data disposable. Production Redis needs network isolation, authentication, TLS where appropriate, ACLs, backups, monitoring, and a tested recovery plan. Never put credentials in frontend code.",
     "Redis ကို local သို့မဟုတ် disposable container ဖြင့် လေ့လာပြီး production တွင် network isolation၊ ACL၊ TLS၊ backup နှင့် recovery plan လိုအပ်သည်။",
     "Write a local setup checklist that includes version verification, a disposable namespace, and cleanup.",
     ("Redis installation ကို ဘယ်နေရာမှာ စမ်းသင့်သနည်း?", ["An isolated local or disposable environment", "The platform production server", "A public browser URL with credentials"], "An isolated local or disposable environment", "Practice environments must not share platform infrastructure.")),
    ("Redis CLI Fundamentals", "command syntax, replies, errors, and safe inspection",
     "SET user:42:name \"Ada\"\nEXISTS user:42:name\nTYPE user:42:name\nDEL user:42:name", "redis",
     "redis-cli sends commands and displays simple strings, integers, bulk strings, arrays, or errors. Inspect keys deliberately, use namespaces, and avoid KEYS * on production-sized databases. The Academy playground simulates replies in memory and does not connect to Redis.",
     "redis-cli သည် command များကိုပို့ပြီး reply type များကို ပြသည်။ Production တွင် `KEYS *` မသုံးဘဲ namespace နှင့် bounded inspection ကိုသုံးပါ။",
     "Predict each reply for the command sequence, then repeat it in the isolated simulator.",
     ("Production key inspection အတွက် ဘာကိုရှောင်သင့်သနည်း?", ["Unbounded KEYS * scans", "Namespaced keys", "Bounded checks"], "Unbounded KEYS * scans", "Unbounded scans can block or overload a production instance.")),
    ("Redis Architecture", "clients, server event loop, data structures, persistence, and boundaries",
     "client -> Redis server -> data structure\n                  |-> RDB/AOF persistence\n                  |-> replication or cluster", "text",
     "A Redis deployment includes clients, a server process, memory data structures, optional persistence, replication or clustering, and operational controls. Request paths and failure modes should be explicit: cache misses, reconnects, failover, stale data, and memory pressure all need application behavior.",
     "Redis architecture တွင် client၊ server၊ memory data structure၊ persistence၊ replication/cluster နှင့် operational controls ပါဝင်သည်။ Failure mode များကို ကြိုတင်သတ်မှတ်ပါ။",
     "Draw a request path for a cache read, including a database fallback and invalidation event.",
     ("Redis ကို architecture တွင် ဘယ်လိုထားသင့်သနည်း?", ["As an explicit dependency with failure behavior", "As a hidden source of truth", "Without memory limits"], "As an explicit dependency with failure behavior", "Operational behavior must be designed around cache failure, stale data, and memory pressure.")),
    ("Keys, Namespaces, and Types", "key naming, TYPE, EXISTS, DEL, and data ownership",
     "SET cache:course:42:title \"Redis\"\nTYPE cache:course:42:title\nEXISTS cache:course:42:title", "redis",
     "Key names are part of the data model. Use stable namespaces, avoid unbounded user-controlled key names, document ownership and TTL policy, and choose commands that match the stored type. A key collision or wrong-type command is an application bug, not a reason to bypass validation.",
     "Key name သည် data model ၏ အစိတ်အပိုင်းဖြစ်သည်။ Namespace၊ owner၊ TTL policy နှင့် type ကို document လုပ်ပါ။",
     "Design key names for courses, sessions, and rate-limit buckets with a tenant boundary.",
     ("Key namespace ၏ အကျိုးက ဘာလဲ?", ["Clear ownership and collision boundaries", "Unlimited memory", "Automatic authorization"], "Clear ownership and collision boundaries", "Namespaces improve operational clarity but do not replace authorization.")),
    ("Strings and Atomic Counters", "values, increments, compare-and-set thinking, and bounded counters",
     "SET rate:user:42 1 EX 60\nINCR rate:user:42\nGET rate:user:42", "redis",
     "Strings can hold text, serialized values, or counters. Atomic commands help coordinate small state transitions, but application rules still need validation, key scope, expiration, and limits. Do not store secrets or unbounded payloads without a reviewed policy.",
     "String သည် text၊ serialized value သို့မဟုတ် counter အဖြစ်အသုံးပြုနိုင်သည်။ Atomic command ရှိသော်လည်း validation၊ scope နှင့် limit လိုအပ်သည်။",
     "Model a one-minute request counter and explain what happens when the key expires.",
     ("Rate counter ကို ဘယ်လိုကန့်သတ်သင့်သနည်း?", ["Use a scoped key with an explicit TTL", "Use an unbounded global key forever", "Trust a client-provided user id"], "Use a scoped key with an explicit TTL", "A scoped expiring counter limits memory and aligns the state with the policy window.")),
    ("Lists, Hashes, Sets, and Sorted Sets", "choosing a data structure for queues, records, membership, and ranking",
     "LPUSH jobs:email job-1\nHSET user:42 name Ada role student\nSADD course:42:students user-42\nZADD leaderboard 98 user-42", "redis",
     "Lists model ordered sequences, hashes model field-value records, sets model unique membership, and sorted sets model scored ordering. The data structure does not define authorization or durability. Bound list length, validate fields, and plan cleanup and persistence.",
     "List သည် sequence၊ hash သည် field-value record၊ set သည် unique membership၊ sorted set သည် score အလိုက် ordering ကို ကိုင်တွယ်သည်။",
     "Choose a structure for a job queue, course membership, profile fields, and a leaderboard; justify each choice.",
     ("Unique membership အတွက် ဘယ် structure သုံးသင့်သနည်း?", ["Set", "List without bounds", "A random string"], "Set", "Sets provide unique membership semantics.")),
    ("TTL, Caching, and the First Safe Workflow", "expiration, cache-aside, invalidation, verification, and cleanup",
     "SET cache:course:42 \"payload\" EX 300\nTTL cache:course:42\nDEL cache:course:42", "redis",
     "A cache-aside flow reads Redis first, loads the authoritative database on a miss, stores a bounded representation with a suitable TTL, and invalidates or refreshes it after a write. TTL is not a substitute for authorization or durable storage. The safe workflow uses an isolated simulation, expected results, reset, and no platform connections.",
     "Cache-aside flow တွင် Redis hit မရှိလျှင် authoritative DB မှဖတ်ပြီး bounded TTL ဖြင့် cache ထည့်သည်။ TTL သည် authorization မဟုတ်ပါ။",
     "Complete a cache-aside scenario with a hit, miss, invalidation, TTL expiry, metrics, and reset notes.",
     ("Cache miss ဖြစ်လျှင် source of truth ကို ဘယ်ကဖတ်သင့်သနည်း?", ["An authorized authoritative database or service", "A client-supplied secret", "An arbitrary public endpoint"], "An authorized authoritative database or service", "Cache data is an optimization; authoritative data and authorization remain elsewhere.")),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, example, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "No Redis experience is required; basic backend concepts help." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the Redis playground and complete the first command lab."
    return f"""Introduction
{title} introduces {topic} through safe, reproducible Redis practice.

Learning objectives
- Explain {topic} and select an appropriate Redis boundary.
- Read command replies and verify state changes deliberately.
- Keep credentials, production infrastructure, and untrusted commands outside the learning sandbox.

Prerequisites
{prerequisite}

Redis architecture diagram
application -> authenticated client -> Redis data structure -> optional persistence/replication
                         |-> cache miss -> authoritative PostgreSQL/service

Detailed theory
{theory}

Redis command example ({language})
{example}

Expected command output
Exact replies vary by Redis version and client. Verify the value, type, affected count, and TTL rather than assuming a command succeeded.

Step-by-step implementation
1. Use an isolated local namespace or the Academy's deterministic simulator.
2. Inspect the initial state and choose a bounded key/data structure.
3. Execute the command sequence and record expected replies.
4. Verify type, value, membership, score, or TTL.
5. Reset disposable state and document failure, expiry, and recovery behavior.

Interactive visualizer
Use the Redis playground, cache simulator, TTL visualizer, Pub/Sub lab, Streams lab, and architecture explorer. They are deterministic simulations and never execute commands against platform Redis.

Common errors
- Running unbounded KEYS or large scans in a production instance.
- Using a command against the wrong Redis data type.
- Treating TTL as authorization or durable persistence.
- Storing secrets or unbounded user input in keys and values.

Troubleshooting
Check command spelling, data type, key namespace, TTL units, ACL permissions, connection target, memory policy, and the smallest reproducible sequence. Reset the simulator when the practice state is unclear.

Best practices
- Use namespaced keys, bounded payloads, explicit TTLs, least privilege, TLS where appropriate, metrics, backups, and tested recovery.
- Keep PostgreSQL or another authoritative service as the source of truth when durability and relational integrity are required.

Security considerations
The Academy provides predefined command simulations only. It does not evaluate arbitrary student commands, expose credentials, connect to platform Redis, access a student's local Redis, or provide unrestricted filesystem/network access.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Build an isolated course-cache simulation with namespaced keys, cache hit/miss metrics, TTL expiry, invalidation, a reset action, and a short PostgreSQL source-of-truth note.

Summary
You can now reason about {topic} with explicit data, expiry, security, and operational boundaries.

Next lesson
{next_lesson}

Myanmar explanation
{mm}
"""


def seed_redis_course(db, course):
    course.title = "Redis — From Zero to Professional"
    course.short_description = "A free practical path through Redis data structures, caching, real-time systems, persistence, clustering, security, and production operations."
    course.description = "Learn Redis from CLI fundamentals through strings, collections, TTL, cache-aside strategies, Pub/Sub, Streams, queues, rate limiting, sessions, locks, scripting, Python/FastAPI integration, persistence, replication, Sentinel, Cluster, memory management, security, monitoring, Docker, and production architecture."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 55
    course.outcomes = "Choose Redis data structures and key namespaces for real application access patterns|Build safe cache-aside, TTL, queues, rate-limit, session, Pub/Sub, and Streams workflows|Explain persistence, replication, Sentinel, Cluster, memory, security, monitoring, and recovery tradeoffs|Integrate Redis with backend services while preserving an authoritative database and secure operational boundaries"
    course.requirements = "Basic backend or command-line familiarity is helpful; no Redis experience is required."
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
        values = {"title": f"{title} command example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe Redis example for local study; the Academy does not execute student commands.", "position": 1}
        example_row = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        if not example_row:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example_row, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review Redis boundaries, types, TTL, security, and operational behavior before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: a TTL is an authorization boundary.", ["True", "False"], "False", "Expiration controls lifetime; server-side authentication and authorization protect access."),
            ("Where should practice commands run?", ["An isolated simulator or disposable local environment", "Platform production Redis", "An arbitrary public endpoint"], "An isolated simulator or disposable local environment", "The learning tools never connect student commands to platform infrastructure."),
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
