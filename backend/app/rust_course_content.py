"""Idempotent Rust vertical-slice course content seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

PLANNED_MODULES = [
    "Introduction to Rust", "Rust Installation & Toolchain", "Rust Syntax & Variables", "Data Types & Operators",
    "Control Flow", "Functions & Expressions", "Ownership Fundamentals", "Borrowing & References",
    "Slices & String Handling", "Structs & Methods", "Enums & Pattern Matching", "Collections", "Error Handling",
    "Modules, Packages & Crates", "Generics", "Traits & Trait Bounds", "Lifetimes", "Smart Pointers",
    "Closures & Iterators", "Advanced Pattern Matching", "Advanced Types & Traits", "Macros & Metaprogramming",
    "Testing & Documentation", "Threads & Message Passing", "Synchronization & Concurrency", "Async/Await Fundamentals",
    "Tokio & Async Ecosystem", "File I/O & CLI Applications", "Networking Fundamentals", "HTTP APIs with Axum",
    "Rust with PostgreSQL", "Serialization & JSON", "Unsafe Rust & FFI", "Memory Layout & Performance",
    "WebAssembly with Rust", "Secure Rust Development", "Architecture & Design Patterns", "Docker, CI/CD & Deployment",
    "Professional Rust Projects", "Final Rust Capstone & Assessment",
]

MODULE_ONE = [
    ("What Rust Is", "memory-safe systems programming, compilation, and explicit boundaries", "fn main() {\n    println!(\"Hello, Rust!\");\n}", "rust", "Rust is a compiled systems language designed for performance, predictable resource use, and strong compile-time safety. Ownership, borrowing, and lifetimes make many memory errors explicit before a program runs. Rust is not magic: unsafe code, dependencies, I/O, authentication, and operational choices still require review.", "Rust သည် performance နှင့် compile-time safety ကိုပေးသော compiled systems language ဖြစ်သည်။ Ownership နှင့် borrowing က memory error များကို compile မလုပ်မီဖော်ပြပေးသည်။", "List two reasons to choose Rust and one boundary that still needs runtime validation.", ("Rust ၏ အဓိကအားသာချက်က ဘာလဲ?", ["Performance with compile-time safety", "Automatic authorization", "Replacing every database"], "Performance with compile-time safety", "Rust makes many memory invariants explicit while leaving application policy to the developer.")),
    ("Rust Installation and Cargo", "rustup, rustc, Cargo projects, and reproducible toolchains", "rustup toolchain list\ncargo new hello-rust\ncd hello-rust\ncargo run", "bash", "rustup manages toolchains and Cargo manages packages, builds, tests, and documentation. Keep lockfiles reviewed, pin supported toolchains in CI, and build in disposable local projects. The Academy displays commands but never compiles student code on the production host.", "rustup သည် toolchain ကိုစီမံပြီး Cargo သည် project၊ dependency၊ build နှင့် test ကိုစီမံသည်။ CI တွင် toolchain ကိုတိကျစွာသတ်မှတ်ပါ။", "Create a disposable Cargo binary, run it locally, and record the toolchain and expected output.", ("Rust project management အတွက် ဘာကိုသုံးသနည်း?", ["Cargo", "A browser cookie", "A production shell on the Academy"], "Cargo", "Cargo is Rust's project and package workflow tool.")),
    ("Variables, Mutability, and Shadowing", "let bindings, mut, constants, and explicit state changes", "let language = \"Rust\";\nlet mut lessons = 1;\nlessons += 1;\nprintln!(\"{language}: {lessons}\");", "rust", "Rust variables are immutable by default. `mut` makes a specific binding mutable, while shadowing creates a new binding and can change the type. Explicit mutability makes state changes easier to review; constants and configuration should not be confused with secret storage.", "Rust variable များသည် default အားဖြင့် immutable ဖြစ်သည်။ `mut` သည် state change ကို explicit ဖြစ်စေပြီး shadowing သည် binding အသစ်ဖန်တီးသည်။", "Rewrite a small counter using immutable bindings where possible and one explicit mutable state variable.", ("Rust တွင် default variable state က ဘာလဲ?", ["Immutable", "Always global", "Automatically shared mutable"], "Immutable", "Explicit mutability reduces accidental state changes.")),
    ("Types, Functions, and Expressions", "scalar types, return values, statements, and compiler inference", "fn add(completed: u32, next: u32) -> u32 {\n    completed + next\n}\nprintln!(\"{}\", add(2, 3));", "rust", "Rust has explicit scalar and compound types, type inference, and expression-oriented blocks. Function signatures communicate contracts; validate external input before converting it and avoid assuming compiler inference validates business rules.", "Rust တွင် scalar/compound type များ၊ type inference နှင့် expression block များရှိသည်။ Function signature သည် contract ကိုရှင်းလင်းစေသည်။", "Define a typed function that returns a Result when parsing an external lesson count.", ("Function signature ၏ အကျိုးက ဘာလဲ?", ["It documents and checks a data contract", "It grants database access", "It hides compiler errors"], "It documents and checks a data contract", "Types make interfaces and invalid states easier to review.")),
    ("Ownership Fundamentals", "move semantics, one owner, scope, and drop", "let first = String::from(\"academy\");\nlet second = first;\nprintln!(\"{second}\");", "rust", "Each Rust value has an owner, ownership moves by default for heap-backed values, and the value is dropped when the owner leaves scope. A moved binding cannot be used again. This prevents double frees and use-after-free without a tracing garbage collector.", "Value တစ်ခုတွင် owner တစ်ဦးရှိပြီး heap value များသည် default အားဖြင့် move ဖြစ်သည်။ Scope ပြီးလျှင် drop လုပ်သည်။", "Predict which binding is valid after moving a String and explain why a copied integer behaves differently.", ("Ownership move ပြီးနောက် ဘာဖြစ်သနည်း?", ["The original binding can no longer use the moved value", "Both bindings free the value", "The value becomes a global"], "The original binding can no longer use the moved value", "Move semantics maintain one clear owner for heap data.")),
    ("Borrowing and References", "shared references, mutable references, and borrow checker rules", "fn length(value: &String) -> usize { value.len() }\nlet name = String::from(\"Ada\");\nprintln!(\"{}\", length(&name));", "rust", "Borrowing lets code use a value without taking ownership. Many shared references may coexist, or one mutable reference may exist, but conflicting access is rejected. These rules are compile-time safety constraints; they do not replace authorization or validation at application boundaries.", "Borrowing သည် ownership မယူဘဲ value ကိုအသုံးပြုစေသည်။ Shared reference များစွာ သို့မဟုတ် mutable reference တစ်ခုကို စည်းကမ်းအတိုင်းအသုံးပြုနိုင်သည်။", "Refactor a function to borrow a String and then explain why simultaneous mutable and shared access is rejected.", ("Borrowing ၏ ရည်ရွယ်ချက်က ဘာလဲ?", ["Use a value without transferring ownership", "Bypass all validation", "Make every value global"], "Use a value without transferring ownership", "References provide temporary access governed by the borrow checker.")),
    ("Strings, Slices, and Collections", "UTF-8 strings, slices, Vec, and safe indexed access", "let words = vec![\"ownership\", \"borrowing\"];\nfor word in &words { println!(\"{word}\"); }", "rust", "Rust strings are UTF-8 and can have different byte and character boundaries. Slices borrow contiguous data, Vec owns a growable collection, and indexing must respect bounds. Prefer iterators and checked access for external indices; do not treat a byte offset as a character boundary.", "Rust String သည် UTF-8 ဖြစ်ပြီး slice သည် owned မဟုတ်သော contiguous borrow ဖြစ်သည်။ Vec သည် growable owned collection ဖြစ်သည်။", "Build a Vec of lesson titles, iterate by shared reference, and safely inspect an optional index.", ("External index အတွက် ဘာကိုသုံးသင့်သနည်း?", ["Checked access such as get", "Unchecked pointer arithmetic by default", "A hidden panic assumption"], "Checked access such as get", "Checked access makes invalid input an explicit Option result.")),
    ("First Safe Rust Workflow", "testing, compiler diagnostics, Result boundaries, and cleanup", "cargo fmt\ncargo check\ncargo test\ncargo clippy", "bash", "A professional workflow formats code, reads the first compiler diagnostic, checks types, runs tests, and reviews Clippy suggestions. Handle Result and Option explicitly, keep dependencies reviewed, and isolate experiments. The playground provides predefined examples and simulated output rather than arbitrary compilation.", "Professional Rust workflow တွင် fmt၊ check၊ test၊ clippy နှင့် compiler diagnostic ကိုစနစ်တကျစစ်သည်။ Result/Option ကို explicit handle လုပ်ပါ။", "Create a tiny typed CLI workflow with one test, one expected compiler error, and a cleanup note.", ("Rust code quality workflow တွင် ဘာတွေပါသနည်း?", ["cargo fmt, check, test, and reviewed diagnostics", "Only a screenshot", "Compiling untrusted code on production"], "cargo fmt, check, test, and reviewed diagnostics", "Repeatable local and CI checks make compiler and behavior evidence reviewable.")),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, example, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "No Rust experience is required; basic programming concepts help." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the Rust playground and ownership visualizer."
    return f"""Introduction
{title} introduces {topic} through safe, reproducible Rust practice.

Learning objectives
- Explain {topic} and its compiler/runtime boundary.
- Read Rust code, compiler output, and ownership state deliberately.
- Keep untrusted code, credentials, and production services outside the learning sandbox.

Prerequisites
{prerequisite}

Memory architecture diagram
source -> rustc/Cargo -> executable -> stack/heap/resource ownership -> OS/network/database boundary

Detailed theory
{theory}

Rust code example ({language})
{example}

Expected compiler output
Exact formatting varies by Rust toolchain. Verify warnings, errors, exit status, and program output rather than assuming compilation succeeded.

Step-by-step implementation
1. Work in a disposable local Cargo project.
2. Start with explicit types and the smallest function or ownership example.
3. Run cargo fmt, cargo check, cargo test, and inspect the first diagnostic.
4. Verify ownership, borrowing, Result/Option, and boundary behavior.
5. Review dependencies, permissions, secrets, and cleanup before publishing.

Interactive visualizer
Use the Rust playground, ownership visualizer, memory visualizer, Cargo explorer, concurrency lab, and labs. They are educational simulations and do not compile arbitrary student programs on the Academy host.

Common compiler errors
- Use of a moved value.
- Cannot borrow as mutable while borrowed as immutable.
- Missing type or lifetime information.
- Unhandled Result/Option or dependency/toolchain mismatch.

Troubleshooting
Check rustup toolchain, Cargo.toml, lockfile, module paths, the first compiler diagnostic, ownership scope, lifetimes, feature flags, and the smallest reproducible example. Reset the simulator when its state is unclear.

Best practices
- Prefer safe Rust, explicit error handling, least-privilege dependencies, deterministic tests, reviewed lockfiles, and measured performance changes.
- Keep secrets server-side, validate external input, use TLS, and authorize every resource access in backend services.

Security considerations
The Academy displays predefined Rust examples and simulations only. It does not compile arbitrary uploads, expose credentials or internal services, access local files, or execute Rust programs on the production host.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Build a small typed Cargo CLI that prints a course summary, handles a Result-based parse error, includes one unit test, and documents ownership and cleanup decisions.

Summary
You can now reason about {topic} with compiler, memory, safety, and production boundaries in view.

Next lesson
{next_lesson}

Myanmar explanation
{mm}
"""


def seed_rust_course(db, course):
    course.title = "Rust Programming — From Zero to Professional Systems Developer"
    course.short_description = "A free practical path through ownership, borrowing, concurrency, async systems, APIs, databases, security, and production Rust."
    course.description = "Learn Rust from syntax and Cargo through ownership, borrowing, lifetimes, traits, collections, error handling, testing, threads, async/Tokio, CLI tools, networking, Axum APIs, PostgreSQL, Serde, unsafe/FFI, WebAssembly, security, Docker, CI/CD, and professional systems architecture."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 55
    course.outcomes = "Write idiomatic Rust with ownership, borrowing, lifetimes, structs, enums, traits, collections, and explicit error handling|Build tested CLI, networking, async, Axum, PostgreSQL, and JSON workflows|Reason about memory, concurrency, unsafe boundaries, security, performance, and deployment|Use Cargo and CI checks to prepare maintainable production systems"
    course.requirements = "Basic programming and command-line familiarity are helpful; no Rust experience is required."
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
        values = {"title": f"{title} example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe Rust example for local study; the Academy does not compile arbitrary student code.", "position": 1}
        example_row = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        if not example_row:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example_row, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review Rust types, ownership, borrowing, compiler diagnostics, and safe boundaries before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: Rust's borrow checker replaces server-side authorization.", ["True", "False"], "False", "Memory safety and access authorization are different boundaries."),
            ("Where should practice Rust programs be compiled?", ["A disposable local project or isolated sandbox", "The Academy production host", "An arbitrary internal service"], "A disposable local project or isolated sandbox", "The Academy does not compile untrusted student code on production infrastructure."),
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
