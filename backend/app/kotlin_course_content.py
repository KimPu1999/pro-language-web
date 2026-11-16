"""Authored Kotlin vertical slice for the idempotent catalog seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

PLANNED_MODULES = [
    "Introduction to Kotlin", "Kotlin Installation & Setup", "Kotlin Syntax & First Program", "Variables & Data Types",
    "Operators & Expressions", "Control Flow", "Functions", "Arrays & Collections", "Null Safety", "Strings & Text Processing",
    "Classes & Objects", "Inheritance & Polymorphism", "Interfaces & Data Classes", "Generics & Type System",
    "Extension Functions & Properties", "Higher-Order Functions & Lambdas", "Scope Functions", "Exception Handling",
    "File I/O & Serialization", "Coroutines Fundamentals", "Kotlin Flow", "Concurrency & Cancellation", "Kotlin Testing",
    "Android Development Fundamentals", "Android Studio & Gradle", "Jetpack Compose Fundamentals", "Compose Layouts & Material Design",
    "Navigation & State Management", "MVVM & Clean Architecture", "Android Networking & REST APIs", "Room Database & DataStore",
    "Dependency Injection", "Android Authentication & Security", "Android Background Work", "Advanced Compose UI & Performance",
    "Android Testing & Quality", "Kotlin Backend with Ktor & Spring", "Kotlin Multiplatform & Deployment",
    "Professional Kotlin Projects", "Final Kotlin Capstone & Assessment",
]

MODULE_ONE = [
    ("What Kotlin Is and Where It Runs", "expressive syntax, type safety, and JVM interoperability", "kotlinc -version\nkotlin -version\ngradle -v", "terminal", "Kotlin is a statically typed language used on the JVM, Android, backend services, and multiplatform projects. Its compiler, null-safety type system, concise syntax, and Java interoperability support maintainable applications. Tool and dependency versions are part of a reproducible build.", "Kotlin သည် JVM၊ Android၊ backend နှင့် multiplatform project များတွင်သုံးသော statically typed language ဖြစ်သည်။ Compiler၊ null-safety နှင့် Java interoperability က maintainable application များကို ကူညီသည်။", "List three Kotlin target environments and one reason type safety matters.", ("Kotlin ကို ဘယ်နေရာတွင် သုံးနိုင်သနည်း?", ["JVM, Android, backend, and multiplatform targets", "Only in a database", "Only in CSS"], "JVM, Android, backend, and multiplatform targets", "Kotlin supports JVM, Android, server, and multiplatform development.")),
    ("Set Up Kotlin and Verify Tools", "Kotlin compiler, Gradle, and project boundaries", "kotlinc -version\ngradle -v\njava -version", "terminal", "Use official Kotlin, JDK, and Gradle distributions or the project wrapper. Verify versions in a disposable workspace and keep dependency resolution reproducible. Never copy unknown binaries or store credentials in build files.", "Official Kotlin၊ JDK နှင့် Gradle tools ကို install ပြီး version များကို verify လုပ်ပါ။ Unknown binary မသုံးပါနှင့်။", "Create a setup checklist containing JDK, Kotlin, Gradle, and target Android versions.", ("Build setup တွင် ဘာကို စစ်သင့်သနည်း?", ["Tool versions and trusted dependency sources", "A production secret", "An arbitrary binary"], "Tool versions and trusted dependency sources", "Reproducible builds require known tool inputs.")),
    ("Write Your First Kotlin Program", "main function, expressions, and compiler feedback", "mkdir hello-kotlin\ncd hello-kotlin\nkotlinc Main.kt -include-runtime -d hello.jar\njava -jar hello.jar", "terminal", "A Kotlin executable starts from a main function. The compiler checks syntax and types before producing a JVM artifact. Small compiler feedback loops make it easier to learn; keep source, build output, and dependencies separate.", "Kotlin executable သည် main function မှ စတင်သည်။ Compiler သည် syntax နှင့် type များကို စစ်ပြီး JVM artifact ဖန်တီးသည်။", "Draft a Main.kt file and explain which line produces output.", ("Kotlin program ၏ entry point က ဘာလဲ?", ["A main function", "Any XML file", "A database table"], "A main function", "The main function is the normal executable entry point.")),
    ("val, var, and Type Inference", "immutable values, mutable variables, and readable declarations", "val language = \"Kotlin\"\nvar count = 0\ncount += 1\nprintln(language)\nprintln(count)", "kotlin", "Use val for references that should not be reassigned and var only when mutation is required. Type inference keeps local code concise while explicit types clarify public APIs and boundaries. Do not put credentials in constants or source files.", "မပြောင်းလဲသင့်သော reference အတွက် val သုံးပြီး mutation လိုသောအခါ var သုံးပါ။ Public API တွင် explicit type က ပိုရှင်းလင်းစေသည်။", "Convert a mutable example to val where possible and explain the remaining mutation.", ("ဘယ်အခြေအနေတွင် val သုံးသင့်သနည်း?", ["When a reference should not be reassigned", "For every secret", "Only in XML"], "When a reference should not be reassigned", "Immutable references make data flow easier to reason about.")),
    ("Expressions, Types, and Collections", "values, operators, lists, and predictable data", "val numbers = listOf(1, 2, 3)\nval total = numbers.sum()\nval active = total > 0\nprintln(total)\nprintln(active)", "kotlin", "Kotlin treats many constructs as expressions and provides typed collections. Standard library operations are concise, but inputs still need validation and collection sizes should be considered. Prefer immutable collection views for shared state.", "Kotlin တွင် expression နှင့် typed collection များကို အသုံးများသည်။ Input validation ပြုလုပ်ပြီး shared state အတွက် immutable collection view ကို ဦးစားပေးပါ။", "Predict the total and boolean result, then explain why the list type is known by the compiler.", ("Kotlin collection example တွင် ဘာကို ဦးစားပေးသင့်သနည်း?", ["Typed and immutable views where possible", "Unvalidated mutable global state", "Embedded credentials"], "Typed and immutable views where possible", "Clear collection contracts reduce accidental mutation.")),
    ("Functions and Default Arguments", "function contracts, named arguments, and reusable behavior", "fun greet(name: String, prefix: String = \"Hello\"): String {\n    return \"$prefix, $name\"\n}\nprintln(greet(name = \"Ada\"))", "kotlin", "Functions make behavior testable and reusable. Named and default arguments can improve call-site clarity. Keep public contracts small, validate external values, and return domain errors instead of hiding failures.", "Function များသည် behavior ကို reusable နှင့် testable ဖြစ်စေသည်။ Named/default argument သည် call-site ကို ရှင်းလင်းစေသည်။", "Design a function that returns a validated username or a safe error result.", ("Function contract က ဘာကို ဖော်ပြသနည်း?", ["Inputs, output, and failure behavior", "Only a UI color", "A password"], "Inputs, output, and failure behavior", "A clear contract tells callers how to use and handle a function.")),
    ("Null Safety and Safe Calls", "nullable types, safe calls, Elvis, and validation", "val nickname: String? = null\nval display = nickname?.uppercase() ?: \"Guest\"\nprintln(display)", "kotlin", "Kotlin makes nullability part of the type system. Safe calls and the Elvis operator make absence explicit, while the not-null assertion should be rare and justified. Validate data at boundaries instead of forcing null values through the application.", "Kotlin တွင် nullability သည် type system ၏ အစိတ်အပိုင်းဖြစ်သည်။ Safe call နှင့် Elvis operator က absence ကို explicit ဖြစ်စေသည်။", "Rewrite a nullable profile field using a safe default and explain when a missing value should be rejected.", ("Null safety အတွက် ဘာကို ဦးစားပေးသင့်သနည်း?", ["Explicit nullable types and safe handling", "Not-null assertions everywhere", "Ignoring validation"], "Explicit nullable types and safe handling", "Nullability becomes visible and must be handled deliberately.")),
    ("First Tested Kotlin Workflow", "formatting, tests, and a small maintainable project", "./gradlew ktlintCheck\n./gradlew test\n./gradlew build", "terminal", "A professional Kotlin loop formats or checks style, runs deterministic tests, and builds an artifact. A successful build is not proof of runtime correctness or security. Review dependencies, logs, and configuration before sharing a project.", "Professional Kotlin workflow တွင် style check၊ test နှင့် build ပါဝင်သည်။ Build အောင်မြင်ခြင်းတစ်ခုတည်းက runtime correctness/security အာမခံချက်မဟုတ်ပါ။", "Create a checklist for a small Kotlin package: format, test, build, review dependencies, and remove secrets.", ("Kotlin quality workflow တွင် ဘာကို အရင်စစ်သင့်သနည်း?", ["Style, tests, dependencies, and build output", "A production token", "An unknown binary"], "Style, tests, dependencies, and build output", "Quality is evidence from several repeatable checks.")),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(position: int, item: tuple) -> str:
    title, topic, commands, filename, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    previous = "No Kotlin experience is required; a text editor is helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: complete the first Kotlin program lab and review the Module 1 assessment."
    return f"""Introduction
{title} introduces {topic} through small Kotlin examples.

Learning objectives
- Explain {topic} in your own words.
- Predict the result before running the example.
- Identify type, dependency, build, and security boundaries.

Prerequisites
{previous}

Kotlin architecture explanation
source files -> package/project -> compiler or Gradle -> JVM/Android artifact

Detailed theory
{theory}

Step-by-step code and commands
{commands}

File paths and folder structure
project/
  settings.gradle.kts
  build.gradle.kts
  src/main/kotlin/Main.kt
  src/test/kotlin/

Expected output
Exact output depends on the Kotlin/JDK/Gradle versions and local project. Verify the state with the relevant command instead of copying unverified output.

Code explanation
Read each declaration, identify its type and scope, then explain how the value moves through the program. Keep examples in an isolated project.

Common errors
- Using an incompatible JDK, Kotlin, or Gradle version.
- Mixing nullable and non-null values without handling absence.
- Putting multiple unrelated responsibilities in one function.
- Assuming a successful build proves runtime or security correctness.

Troubleshooting
Check java -version, Kotlin/Gradle versions, the first compiler error, dependency resolution, and the smallest failing test. Preserve error context before changing multiple files.

Best practices
- Prefer val, explicit public types, small functions, and deterministic tests.
- Validate external input and handle nullable values deliberately.
- Keep secrets out of source, logs, build files, and committed configuration.

Security considerations
Do not hardcode credentials, execute untrusted code, or expose private Android data. Use least-privilege configuration and review dependencies.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Create a small isolated Kotlin project with a README, one focused function, a test, and a clean format/test/build workflow. Use placeholder data only.

Summary
You can now reason about {topic} as a typed, testable Kotlin program state transition.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
The Academy displays Kotlin examples and does not execute untrusted code on its application host.
"""

def seed_kotlin_course(db, course):
    course.title = "Kotlin Programming & Android Development — Zero to Professional"
    course.short_description = "A free, practical path from Kotlin fundamentals to Android, Compose, coroutines, and secure app architecture."
    course.description = "Learn Kotlin syntax, null safety, collections, classes, coroutines, Flow, testing, Android Compose, MVVM, networking, Room, security, Ktor, and multiplatform concepts through safe examples."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 35
    course.outcomes = "Write readable, type-safe Kotlin with functions, collections, classes, and null safety|Build a foundation for coroutines, Flow, testing, and Android Compose|Design Android features with state, MVVM, networking, and local storage|Apply reproducible build, dependency, and mobile security practices"
    course.requirements = "A text editor and basic command-line familiarity; no previous Kotlin or Android experience is required."
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
        lesson.duration_minutes, lesson.status, lesson.published = 35, "published", True
        example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        values = {"title": f"{title} example", "language": "kotlin" if item[3] == "kotlin" else "bash", "filename": item[3], "code": item[2], "description": "Read-only Kotlin example. Run locally in an isolated workspace; the Academy does not execute code on its host.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the Kotlin state transition and safety boundary before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [(item[7][0], item[7][1], item[7][2], item[7][3]), ("True or false: the Academy executes arbitrary Kotlin code on its application host.", ["True", "False"], "False", "Examples are displayed as read-only learning content."), ("Which practice improves Kotlin reliability?", ["Prefer val, handle nulls, test, and keep secrets out of source", "Ignore compiler errors and hardcode tokens", "Run untrusted code in production"], "Prefer val, handle nulls, test, and keep secrets out of source", "Type safety, explicit null handling, tests, and secret hygiene reduce risk.")]
        for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
            row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
            values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
            if not row:
                db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
            else:
                for key, value in values.items():
                    setattr(row, key, value)
    db.flush()
