"""Idempotent authored Modern Dart curriculum.

Module 1 is the complete vertical slice. Later modules have an authored
foundation lesson so no published module is empty; deeper Flutter and package
projects remain incremental work.
"""
import json
import re
from sqlalchemy import select
from .models import CourseModule, Lesson, LessonQuiz, QuizQuestion, CodeExample

MODULES = [
    "Introduction to Dart", "Environment Setup & Installation", "Your First Dart Program", "Variables & Data Types",
    "Operators & Expressions", "Conditional Statements", "Loops & Iteration", "Functions & Parameters",
    "Strings & Text Processing", "Lists, Sets & Maps", "Null Safety & Type System", "Exception Handling & Debugging",
    "Classes & Objects", "Encapsulation & Inheritance", "Abstract Classes & Interfaces", "Mixins & Extensions",
    "Generics & Type Safety", "Modern Dart Features", "Futures & Async/Await", "Streams & Reactive Programming",
    "Isolates & Concurrency", "Files, Directories & I/O", "JSON & Serialization", "HTTP APIs & Networking",
    "Packages & pub.dev", "Testing, Linting & Debugging", "Flutter Fundamentals with Dart", "Flutter State & Navigation",
    "Flutter APIs & Local Storage", "Dart Backend & CLI Development", "Real-World Dart Projects", "Final Dart Capstone & Assessment",
]

MODULE_ONE = [
    ("What Are Dart and Flutter?", "Dart language fundamentals and Flutter's widget-based UI", "void main() {\n  const message = 'Dart runs on the Dart VM or compiles for the target platform.';\n  print(message);\n}", "Dart is a client-optimized language used by Flutter and also useful for command-line tools, services, and packages. Flutter builds interfaces from widgets and uses Dart for application logic. The course targets Dart 3.x with sound null safety; Flutter examples should use a compatible Flutter 3.x SDK declared by the project.", "void main() { print(value); }", "Dart သည် Flutter နှင့်အတူ mobile၊ web၊ desktop နှင့် server application များ တည်ဆောက်ရန် အသုံးပြုနိုင်သော language ဖြစ်သည်။"),
    ("Dart and Flutter Environment Setup", "SDK channels, pubspec.yaml, and reproducible projects", "dart --version\nflutter --version\ndart create console sample\ncd sample\ndart run", "Use a stable Dart 3.x SDK and a compatible stable Flutter 3.x SDK for Flutter lessons. Declare package constraints in pubspec.yaml, commit the lock file where appropriate, and verify the SDK channel before debugging code. Do not rely on an undocumented global installation.", "dart --version\nflutter doctor", "Dart SDK နှင့် Flutter SDK version များကို စစ်ဆေးပြီး pubspec.yaml ထဲတွင် compatibility ကို သတ်မှတ်ပါ။"),
    ("Your First Dart Program", "main, variables, interpolation, and output", "void main() {\n  final name = 'CodeMaster';\n  print('Welcome, $name!');\n}", "Dart programs start from main. final creates a single-assignment variable and const creates a compile-time constant when the value permits it. String interpolation improves readable output. Keep examples deterministic and validate external input before using it.", "final name = 'value';\nprint('Text $name');", "Dart program သည် main function မှ စတင်ပြီး final၊ const နှင့် string interpolation ကို အသုံးပြုနိုင်သည်။"),
    ("Variables and Core Types", "String, num, int, double, bool, and records of values", "void main() {\n  final int count = 3;\n  final String label = 'items';\n  final bool active = true;\n  print('$count $label: $active');\n}", "Dart has sound static typing with useful inference. Use final for values assigned once and const for compile-time constants. Explicit types are useful at public boundaries; inference keeps local code readable. Do not treat static types as runtime validation for JSON or user input.", "final Type name = value;\nconst compileTime = value;", "Dart type များနှင့် inference ကို အသုံးပြုပြီး value contract များကို ရှင်းလင်းစွာ ရေးသားပါ။"),
    ("Operators and Expressions", "typed calculations and predictable evaluation", "void main() {\n  const subtotal = 12.50;\n  const tax = 0.05;\n  final total = subtotal * (1 + tax);\n  print(total.toStringAsFixed(2));\n}", "Use parentheses when a business rule depends on evaluation order. Choose numeric types deliberately and validate values at input boundaries. For money, model currency and rounding rules explicitly rather than assuming binary floating-point is exact.", "final total = subtotal * (1 + tax);", "Expression များတွင် parentheses နှင့် domain-appropriate numeric rules ကို အသုံးပြုပါ။"),
    ("Conditions and Pattern Matching", "safe branches and exhaustive decisions", "void main() {\n  const score = 82;\n  final result = switch (score) {\n    >= 80 => 'Strong',\n    >= 60 => 'Developing',\n    _ => 'Review',\n  };\n  print(result);\n}", "Dart supports readable switch expressions and pattern matching. Keep decisions explicit and make the fallback safe. Authentication and authorization remain server-side concerns even when a Flutter UI displays roles or capabilities.", "final label = switch (value) { pattern => result, _ => fallback };", "Pattern matching သည် decision များကို readable နှင့် exhaustive ဖြစ်စေသည်။"),
    ("Module 1 Review and Assessment", "a small null-safe Dart program", "void main() {\n  final scores = <int>[80, 92, 75];\n  final average = scores.reduce((a, b) => a + b) / scores.length;\n  print('Average: ${average.toStringAsFixed(1)}');\n}", "This review combines typed collections, a callback, numeric output, and deterministic behavior. Before moving to Flutter, separate compile-time checks from runtime validation and test empty collections, network failure, and unavailable local state.", "final values = <int>[1, 2, 3];\nprint(values.length);", "Module 1 တွင် Dart syntax၊ types၊ collection၊ pattern matching နှင့် output ကို ပြန်လည်လေ့လာပါမည်။"),
]

GENERAL = [
    ("Install Dart and Flutter", "stable SDKs and project constraints"), ("Dart Project Structure", "pubspec and entry points"),
    ("Variables and Inference", "readable typed values"), ("Expression Evaluation", "safe calculations"),
    ("Branching and Guards", "clear decisions"), ("Loops and Iteration", "bounded repetition"),
    ("Functions and Parameters", "reusable behavior"), ("String APIs", "safe text processing"),
    ("Lists, Sets, and Maps", "collection choices"), ("Sound Null Safety", "nullable contracts"),
    ("Exceptions and Diagnostics", "explicit failure paths"), ("Classes and Constructors", "object state"),
    ("Encapsulation and Inheritance", "maintainable object design"), ("Abstract Contracts", "interfaces and substitution"),
    ("Mixins and Extensions", "composable behavior"), ("Generic Types", "type-safe reuse"),
    ("Records and Patterns", "modern Dart values"), ("Futures and Async", "non-blocking work"),
    ("Streams", "reactive sequences"), ("Isolates", "concurrent Dart work"),
    ("Files and Directories", "safe local persistence"), ("JSON Models", "validated serialization"),
    ("HTTP Clients", "network requests and failures"), ("pub.dev Packages", "dependency boundaries"),
    ("Testing and Lints", "behavioral confidence"), ("Flutter Widgets", "declarative UI"),
    ("Flutter State and Routes", "navigation and state"), ("Flutter APIs and Storage", "platform boundaries"),
    ("Dart CLI Services", "backend and command tools"), ("Project Architecture", "maintainable Dart systems"),
    ("Final Capstone Plan", "Dart and Flutter integration"),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(title, topic, theory, syntax, code, mm, previous, next_title):
    return f"""Introduction
{title} introduces {topic} with Dart 3.x and compatible Flutter 3.x guidance.

Learning objectives
- Explain {topic} and identify the language, package, platform, or runtime boundary.
- Read and write sound null-safe Dart with explicit failure handling.
- Connect the example to Flutter UI, networking, testing, and deployment decisions.

Prerequisites
{previous}

Chosen compatibility
Use a stable Dart 3.x SDK and a compatible stable Flutter 3.x SDK. Record exact versions in each pubspec.yaml, CI environment, and project README before running framework examples. Verify `dart --version`, `flutter --version`, and `flutter doctor` locally.

Detailed theory
{theory}

Dart syntax
{syntax}

Working code example
```dart
{code}
```

Expected output
Run the example with `dart run` in a local Dart project using the documented SDK. The shown input produces deterministic output.

Line-by-line explanation
The main function is the entry point. Declarations establish typed or inferred state. The central statement performs one focused operation, and the final statement exposes a result. Read the first analyzer diagnostic before changing unrelated code.

Compiler error explanation
Common diagnostics include assigning a nullable value where a non-null value is required, using a value with the wrong type, missing imports, and invalid async return types. Fix the contract or add a real guard rather than forcing null away.

Common mistakes
- Mixing Dart and Flutter SDK constraints without checking compatibility.
- Using `!` to silence null safety instead of proving a value exists.
- Ignoring Future errors or forgetting to await asynchronous work.
- Logging tokens, API keys, or private data in mobile or web builds.

Best practices
Use sound null safety, final and const deliberately, analyzer lints, immutable models where appropriate, cancellation/timeouts for requests, tests, secure storage for secrets, and declared package constraints.

Security considerations
Never execute arbitrary Dart or Flutter code inside FastAPI workers. A runner must isolate processes, network, filesystem, CPU, memory, output, concurrency, and cleanup. Treat JSON and HTTP responses as untrusted input and keep credentials out of client applications.

Practice exercises
- Easy: reproduce the example and introduce one intentional analyzer error.
- Medium: fix it with a type-safe guard or validation step.
- Challenge: add a test, timeout, JSON model, or Flutter state boundary appropriate to the topic.
Hints: identify what static analysis proves, what runtime input can violate, and where validation belongs.
Guided solution: run `dart analyze`, fix the first diagnostic, then add a focused test for the failure case.

Quiz
1. What protects a value that may be absent? Sound null safety and an explicit check.
2. True or false: a client app can safely contain a private API key. False.
3. Which command checks a Dart project? dart analyze.
4. What should network code handle? Timeouts, non-success responses, parsing errors, and cancellation.

Summary
You can now explain {topic}, interpret Dart analyzer diagnostics, and separate static checks from runtime validation.

Next lesson
{next_title}
"""

def _questions(topic):
    return [
        (f"Which practice best supports {topic}?", ["Null safety and runtime validation", "Silencing all analyzer warnings", "Secrets in the app bundle"], "Null safety and runtime validation", "Dart is strongest when static analysis and runtime boundary checks work together."),
        ("True or false: `!` proves a value is non-null in every runtime situation.", ["True", "False"], "False", "The operator asserts; it does not validate an external value at runtime."),
        ("Which tool checks Dart code?", ["dart analyze", "Ignoring diagnostics", "Only opening the file"], "dart analyze", "The analyzer reports many static problems before execution."),
        ("What should be documented for Flutter lessons?", ["Dart and Flutter SDK compatibility", "Only a color", "No version constraints"], "Dart and Flutter SDK compatibility", "Declared constraints make builds reproducible."),
    ]

def seed_dart_course(db, course):
    course.title = "Dart Programming — From Zero to Advanced"
    course.short_description = "A free Dart 3.x course covering sound null safety, async programming, streams, packages, HTTP APIs, testing, Flutter, and real projects."
    course.description = "Learn Dart from first principles through collections, null safety, OOP, async/await, streams, isolates, JSON, HTTP, packages, testing, Flutter, and a final capstone."
    course.level, course.status, course.published = "advanced", "published", True
    course.outcomes = "Write sound null-safe Dart|Build asynchronous and networked programs|Design reusable packages and models|Build Flutter interfaces with Dart|Test, secure, and deploy Dart projects"
    course.requirements = "Basic programming and a terminal. Use a stable Dart 3.x SDK and compatible Flutter 3.x SDK; document exact versions per project and verify them before running examples."
    authored = []
    for module_index, module_title in enumerate(MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_index))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_index); db.add(module); db.flush()
        module.title = module_title
        if module_index == 1:
            specs = [{"title": a, "topic": b, "code": c, "theory": d, "syntax": e, "mm": f} for a, b, c, d, e, f in MODULE_ONE]
        else:
            title, topic = GENERAL[module_index - 2]
            code = f"void main() {{\n  const status = '{_slug(title)} ready';\n  print(status);\n}}"
            specs = [{"title": title, "topic": topic, "code": code, "theory": f"This foundation lesson explains {topic}. Apply it to a small Dart or Flutter feature, then check analyzer diagnostics, null behavior, runtime failures, and resource boundaries.", "syntax": "final value = expression;\nprint(value);", "mm": f"ဤ lesson တွင် {topic} ကို modern Dart ဖြင့် လေ့လာပါမည်။"}]
        for lesson_index, spec in enumerate(specs, 1):
            title, topic = spec["title"], spec["topic"]
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm=""); db.add(lesson); db.flush()
            previous = "Basic programming and a terminal. Use compatible Dart 3.x/Flutter 3.x SDKs." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
            next_title = "Continue to the next lesson." if module_index < 32 else "Continue to the final capstone review."
            lesson.title, lesson.slug = title, slug
            lesson.content_en = _content(title, topic, spec["theory"], spec["syntax"], spec["code"], spec["mm"], previous, next_title)
            lesson.content_mm = f"{title} ကို English theory နှင့်အတူ လေ့လာနိုင်ပါသည်။\n\n{spec['mm']}"
            lesson.description, lesson.duration_minutes = spec["theory"], 35
            lesson.status, lesson.published = "published", True; authored.append(lesson)
            examples = list(db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all())
            example = examples[0] if examples else None
            for duplicate in examples[1:]: db.delete(duplicate)
            if not example:
                db.add(CodeExample(lesson_id=lesson.id, title=f"{title} example", language="dart", filename="main.dart", code=spec["code"], description="Read-only Dart example. Use a local compatible Dart SDK; hosted arbitrary execution is disabled.", position=1))
            else:
                example.title, example.language, example.filename, example.code, example.description, example.position = f"{title} example", "dart", "main.dart", spec["code"], "Read-only Dart example. Use a local compatible Dart SDK; hosted arbitrary execution is disabled.", 1
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz: quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the Dart and security explanations, then retry missed concepts.", status="published"); db.add(quiz); db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(topic), 1):
                values = dict(prompt=prompt, question_type="true_false" if options == ["True", "False"] else "multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                question = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
                if not question: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(question, key, value)
    course.duration_minutes = sum(x.duration_minutes or 35 for x in authored)
    db.flush()
