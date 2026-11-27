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
     ("What database does the Academy MongoDB playground use?", ["An isolated in-memory simulation", "Production PostgreSQL", "A student's real Atlas cluster"], "An isolated in-memory simulation", "The simulator protects platform and student data.")),
]

# Keep the Burmese lesson body complete. Code, commands, identifiers, and
# expected values remain unchanged so both locales contain the same runnable
# material.
FIRST_CRUD_MM_CONTENT = """Introduction
First MongoDB CRUD Workflow သင်ခန်းစာတွင် MongoDB ကို လုံခြုံစွာ လေ့ကျင့်ရန် သီးခြား virtual database တစ်ခုကို အသုံးပြုပြီး data ထည့်ခြင်း၊ ဖတ်ခြင်း၊ ပြင်ခြင်း၊ ဖျက်ခြင်း၊ ရလဒ်စစ်ဆေးခြင်းနှင့် လေ့ကျင့်ခန်းအပြီး cleanup ပြုလုပ်ခြင်းတို့ကို အဆင့်လိုက် လေ့လာမည်။

Learning objectives
- Disposable database နှင့် sample documents များကို အသုံးပြုပြီး CRUD workflow တစ်ခုကို အစမှအဆုံး ဆောင်ရွက်နိုင်ရန်။
- Query filter များ၊ field များ၊ index များနှင့် write operation များကို ရည်ရွယ်ချက်ရှိရှိ ရွေးချယ်နိုင်ရန်။
- Write ပြီးတိုင်း result ကို စစ်ဆေးပြီး လေ့ကျင့်ခန်း data ကို reset သို့မဟုတ် cleanup ပြုလုပ်နိုင်ရန်။
- Browser ထဲသို့ database credential မထည့်ဘဲ server-side boundary နှင့် data safety ကို ထိန်းသိမ်းနိုင်ရန်။

Prerequisites
Module 1 lesson 7 ကို အရင်ပြီးဆုံးထားပါ။ JSON အခြေခံ၊ collection နှင့် document အဓိပ္ပာယ်၊ filter ရေးသားပုံတို့ကို သိထားလျှင် လေ့ကျင့်ခန်းကို ပိုမိုလွယ်ကူစွာ လိုက်လုပ်နိုင်မည်။ ဤသင်ခန်းစာအတွက် အမှန်တကယ် MongoDB server သို့မဟုတ် Atlas account မလိုအပ်ပါ။

MongoDB architecture explanation
application/API -> driver -> database -> collection -> BSON document -> index/query plan

Detailed theory
စိတ်ချရသော CRUD workflow သည် မည်သည့် data ကို ပြင်မည်၊ မည်သည့် result ကို မျှော်လင့်မည်နှင့် လေ့ကျင့်ခန်းပြီးလျှင် မည်သို့ရှင်းလင်းမည်ကို အရင်သတ်မှတ်ခြင်းမှ စတင်သည်။ ပထမဦးစွာ production data မဟုတ်သော disposable database နှင့် သိပြီးသား sample documents များကို ရွေးပါ။ ထို့နောက် data အများကြီးကို တစ်ခါတည်း မဖတ်ဘဲ document အနည်းငယ်ကို စစ်ဆေးပြီး field အမည်၊ type နှင့် လက်ရှိအခြေအနေကို သိအောင်လုပ်ပါ။

Create operation သည် document အသစ်ထည့်ခြင်းဖြစ်သည်။ ထည့်မည့် field များ၏ အမည်၊ type နှင့် လိုအပ်ချက်ကို စစ်ဆေးပြီး collection မှာ မှန်ကန်ကြောင်း အတည်ပြုပါ။ Read operation တွင် filter ဖြင့် လိုအပ်သော document များကိုသာ ရွေးပြီး projection ဖြင့် မလိုအပ်သော field များကို မပြန်ပေးပါနှင့်။ Update operation သည် မည်သည့် document ကို ပြင်မည်ဆိုသည်ကို unique သို့မဟုတ် လုံလောက်စွာ တိကျသော filter ဖြင့် သတ်မှတ်ရမည်။ Delete operation ကို disposable practice data အတွက်သာ အသုံးပြုပြီး မဖျက်မီ target scope ကို ပြန်စစ်ပါ။

Academy playground သည် in-memory state ကို အသုံးပြုသော သင်ကြားရေး simulator ဖြစ်သည်။ ထို့ကြောင့် platform PostgreSQL၊ production MongoDB server သို့မဟုတ် ကျောင်းသား၏ Atlas cluster သို့ ချိတ်ဆက်ခြင်းမရှိပါ။ ဒီအချက်ကြောင့် reset လုပ်ခြင်းသည် လေ့ကျင့်ခန်းအတွင်းရှိ virtual documents များကိုသာ ပြန်ထားပေးပြီး အပြင်ဘက် data ကို မထိခိုက်စေပါ။ တကယ့် application တွင်တော့ database connection, authorization, validation, backup နှင့် audit policy များကို server-side တွင် ထည့်သွင်းထားရမည်။

mongosh and JSON/BSON examples
use academy_demo
db.todos.insertMany([{title: 'Learn BSON', done: false}, {title: 'Build query', done: false}])
db.todos.find({done: false})

အပေါ်က command များတွင် academy_demo database ကို ရွေးပြီး todos collection ထဲသို့ document နှစ်ခု ထည့်ထားသည်။ done: false filter သည် မပြီးသေးသော todo များကိုသာ ရွေးသည်။ title နှင့် done တို့သည် field identifier များဖြစ်သောကြောင့် အမည်နှင့် type ကို မတော်တဆ ပြောင်းမရေးပါနှင့်။

Expected output
ပထမ command ၏ output တွင် ထည့်သွင်းထားသော document အရေအတွက်နှင့် MongoDB က ထုတ်ပေးသော identifier များကို စစ်ပါ။ နောက် command ၏ result တွင် Learn BSON နှင့် Build query document နှစ်ခုလုံး၌ done တန်ဖိုးသည် false ဖြစ်နေကြောင်း စစ်ဆေးပါ။ mongosh version အလိုက် output format ကွာနိုင်သော်လည်း result count၊ field value နှင့် document အရေအတွက်ကို မစစ်ဘဲ write အောင်မြင်သည်ဟု မယူဆပါနှင့်။

Step-by-step implementation
1. Academy playground ကိုဖွင့်ပြီး isolated database နှင့် sample collection ကို ရွေးပါ။
2. လက်ရှိ documents အနည်းငယ်ကို အရင်ဖတ်ပြီး collection အမည်၊ field များနှင့် data type များကို စစ်ပါ။
3. လိုအပ်သော CRUD operation တစ်ခုစီကို တိကျသော filter နှင့် allowlisted field များဖြင့် လုပ်ဆောင်ပါ။
4. Write result၊ ပြောင်းလဲသွားသော document နှင့် count ကို ပြန်ဖတ်ပြီး မျှော်လင့်ထားသည့် result နှင့် နှိုင်းယှဉ်ပါ။
5. Query၊ မျှော်လင့်ထားသော result နှင့် reset လုပ်မည့်အဆင့်ကို မှတ်တမ်းတင်ပါ။
6. လေ့ကျင့်ခန်းပြီးလျှင် virtual database ကို reset လုပ်ပြီး နောက်တစ်ကြိမ် စမ်းသပ်ရာတွင် state အဟောင်း မကျန်စေပါနှင့်။

Data modeling explanation
Document တစ်ခုကို မည်သို့ဖတ်မည်၊ မည်သို့ပြင်မည်၊ ဆက်စပ် data ကို ဘယ်နှစ်ကြိမ်လိုမည်ဆိုသော access pattern ကို အရင်စဉ်းစားပါ။ Document size၊ array cardinality၊ consistency လိုအပ်ချက်၊ validation နှင့် index လိုအပ်ချက်တို့ကိုလည်း ထည့်တွက်ပါ။ အတူတကွ အမြဲဖတ်ရသော data နှင့် အရွယ်အစားကန့်သတ်ချက်အတွင်းရှိ data ကို embed လုပ်နိုင်သော်လည်း သီးခြားလွတ်လပ်စွာ တိုးပွားမည့် data ကို reference လုပ်ရန် လိုနိုင်သည်။ Relational table ကို တိုက်ရိုက်ကူးယူခြင်းထက် application ၏ အမှန်တကယ်ဖတ်ရှုရေးသားပုံနှင့် ကိုက်ညီအောင် model ပြုလုပ်ပါ။

Common errors
- Empty filter ဖြင့် update သို့မဟုတ် delete လုပ်ခြင်းကြောင့် document အားလုံး ပြောင်းလဲသွားခြင်း သို့မဟုတ် ဖျက်သွားခြင်း။
- Flexible schema ကို design မလိုဟု မှားယွင်းယူဆခြင်း။
- Public API မှ unrestricted query operator များကို တိုက်ရိုက်လက်ခံခြင်း။
- Projection မသုံးဘဲ မလိုအပ်သော field သို့မဟုတ် sensitive data များကို ပြန်ပေးခြင်း။
- Write result ကို မစစ်ဘဲ operation အောင်မြင်သည်ဟု ယူဆခြင်း။
- Reset မလုပ်ဘဲ လေ့ကျင့်ခန်းဟောင်း၏ state နှင့် အသစ်ကို ရောထွေးခြင်း။

Troubleshooting
ရလဒ်မမှန်လျှင် database အမည်၊ collection အမည်၊ field path၊ BSON type နှင့် filter shape ကို အရင်စစ်ပါ။ done သည် Boolean ဖြစ်သော်လည်း string false ဖြင့် ရှာမိလျှင် တူညီသော result မရနိုင်ပါ။ Result count နှင့် လက်ရှိ documents ကို သီးခြားဖတ်ပြီး query ကို အနည်းဆုံး reproducible sample ဖြင့် ပြန်စမ်းပါ။ Index သို့မဟုတ် permission ပြဿနာဖြစ်နိုင်သည့် real deployment တွင် server log နှင့် explain plan ကိုလည်း စစ်ဆေးပါ။ Playground state မရှင်းလင်းတော့လျှင် virtual database ကို reset ပြုလုပ်ပါ။

Best practices
- User input ကို validate လုပ်ပြီး field၊ operator၊ sort key နှင့် page size များကို allowlist သတ်မှတ်ပါ။
- Update နှင့် delete တွင် တိကျသော filter သုံးပြီး write ပြီးတိုင်း result ကို verify လုပ်ပါ။
- အမှန်တကယ်အသုံးပြုသည့် access pattern ကို တိုင်းတာပြီးမှ index ထည့်ကာ explain plan ဖြင့် စစ်ပါ။
- List response များတွင် projection၊ deterministic sorting နှင့် pagination သုံးပါ။
- Credential များကို server-side တွင်သာ သိမ်းပြီး TLS၊ RBAC၊ backup နှင့် audit log များကို real deployment တွင် အသုံးပြုပါ။

Security considerations
Academy playground သည် isolated in-memory simulator ဖြစ်ပြီး untrusted query ကို platform PostgreSQL၊ production database သို့မဟုတ် ကျောင်းသား၏ MongoDB account ပေါ်တွင် မလုပ်ဆောင်ပါ။ Browser code ထဲသို့ credential မထည့်ပါနှင့်။ Real API တစ်ခုတည်ဆောက်ရာတွင် client က collection name နှင့် operator အားလုံးကို အလိုအလျောက်ပေးနိုင်အောင် မလုပ်ဘဲ server-side schema၊ authorization နှင့် query allowlist ဖြင့် ကန့်သတ်ပါ။

Hands-on exercise
Academy MongoDB playground တွင် CRUD challenge ကို ပြီးအောင်လုပ်ပါ။ အောက်ပါအချက်များကို မှတ်တမ်းတင်ပါ။
1. အသုံးပြုခဲ့သော query သို့မဟုတ် command။
2. မျှော်လင့်ထားသော document၊ field value နှင့် result count။
3. Write ပြီးနောက် အတည်ပြုရန် အသုံးပြုခဲ့သော read query။
4. လေ့ကျင့်ခန်းအပြီး virtual data ကို reset လုပ်ရန် အဆင့်။

Quiz
Academy MongoDB playground တွင် အသုံးပြုသော database သည် မည်သည့်အမျိုးအစား ဖြစ်သနည်း?
ရွေးချယ်ရန် - သီးခြား in-memory simulation | Production PostgreSQL | ကျောင်းသား၏ အမှန်တကယ် Atlas cluster
မှန်ကန်သောအဖြေ - သီးခြား in-memory simulation
ရှင်းလင်းချက် - Simulator သည် platform data နှင့် ကျောင်းသား၏ data များကို မထိခိုက်စေရန် သီးခြား memory state ကိုသာ အသုံးပြုသည်။

Mini project
Virtual course catalog တစ်ခုကို တည်ဆောက်ပါ။ Sample documents များထည့်ခြင်း၊ CRUD operation များ၊ ခွင့်ပြုထားသော search filter၊ projection၊ တည်ငြိမ်သော sorting၊ pagination နှင့် reset/cleanup မှတ်စုတို့ ပါဝင်ရမည်။ Project အတွက် query တစ်ခုစီ၏ ရည်ရွယ်ချက်၊ မျှော်လင့်ထားသော result နှင့် data မထိခိုက်စေရန် အသုံးပြုထားသော filter ကို ရေးပြပါ။

Summary
ယခုအခါ isolated virtual database တစ်ခုအတွင်း MongoDB CRUD workflow ကို စနစ်တကျ ဆောင်ရွက်နိုင်ပြီဖြစ်သည်။ Data ကို အရင်စစ်ဆေးခြင်း၊ တိကျသော filter ဖြင့် write လုပ်ခြင်း၊ result ကို ပြန်လည်အတည်ပြုခြင်း၊ မလိုအပ်သော field များကို မပြခြင်းနှင့် လေ့ကျင့်ခန်းပြီးနောက် reset လုပ်ခြင်းတို့သည် data integrity နှင့် security boundary ကို ထိန်းသိမ်းပေးသည်။

Next lesson
နောက်သင်ခန်းစာတွင် query playground ကို ဆက်လက်အသုံးပြုပြီး filtering နှင့် read result များကို ပိုမိုလေ့ကျင့်ပါ။

Safety note
ဤဥပမာများသည် ကြိုတင်သတ်မှတ်ထားသော educational content များဖြစ်သည်။ Production database သို့ ချိတ်ဆက်ခြင်း သို့မဟုတ် မယုံကြည်ရသော query ကို အမှန်တကယ် execute လုပ်ခြင်း မရှိပါ။
"""

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

def _content_mm(position: int, item: tuple) -> str:
    if item[0] == "First MongoDB CRUD Workflow":
        return FIRST_CRUD_MM_CONTENT
    title, _, _, _, _, mm, exercise, _ = item
    return f"{title}\n\n{mm}\n\nလေ့ကျင့်ခန်း\n{exercise}"

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
        lesson.content_mm = _content_mm(position, item)
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

