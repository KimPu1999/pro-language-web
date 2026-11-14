"""Idempotent authored modern C# curriculum.

Module 1 is the complete vertical slice. Later modules have an authored
foundation lesson so no published module is empty; deeper .NET, EF Core,
ASP.NET Core, and project labs remain incremental work.
"""
import json
import re
from sqlalchemy import select
from .models import CourseModule, Lesson, LessonQuiz, QuizQuestion, CodeExample

MODULES = [
    "Introduction to C# & .NET", "Environment Setup & Installation", "Your First C# Program", "Variables & Data Types",
    "Operators & Expressions", "Conditional Statements", "Loops & Iteration", "Methods & Parameters",
    "Arrays & Multidimensional Arrays", "Strings & Text Processing", "Collections & Data Structures", "Exception Handling & Debugging",
    "Classes & Objects", "OOP Principles", "Interfaces & Abstract Classes", "Advanced OOP & Design Patterns",
    "Generics & Type Safety", "Delegates, Events & Lambdas", "LINQ Fundamentals", "Advanced LINQ & Query Optimization",
    "Async/Await & Task Programming", "Files, Streams & Serialization", "Modern C# Features", "SQL & ADO.NET",
    "Entity Framework Core", "SQL Server & PostgreSQL Integration", "ASP.NET Core Fundamentals", "REST API Development",
    "Authentication & Authorization", "Testing, Security & Performance", "Blazor & Desktop Development", "Architecture & Clean Code",
    "Docker, CI/CD & Deployment", "Microservices & Background Jobs", "Real-World C# Projects", "Final C# Capstone & Assessment",
]

MODULE_ONE = [
    ("What Are C# and .NET?", "managed application development and the .NET runtime", "using System;\n\nConsole.WriteLine(\"C# runs on .NET.\");", "C# is a strongly typed language used with the .NET runtime and SDK. The compiler produces an intermediate representation that the runtime executes and optimizes. Modern C# supports console tools, web APIs, desktop applications, cloud services, and games. Choose a supported .NET SDK and document the language version in the project file.", "using System;\nConsole.WriteLine(value);", "C# သည် .NET runtime နှင့်အတူ strongly typed application များ တည်ဆောက်ရန် အသုံးပြုသော language ဖြစ်သည်။"),
    (".NET SDK Environment Setup", "SDK selection, project files, and reproducible builds", "dotnet --version\ndotnet new console -n LearningApp\ndotnet run", "The .NET SDK includes the compiler, runtime tooling, templates, and restore commands. Pin or document a supported SDK through global.json and the project TargetFramework. Nullable reference types and analyzers should be enabled deliberately rather than relying on a developer machine default.", "dotnet new console\ndotnet build\ndotnet run", ".NET SDK version နှင့် TargetFramework ကို project configuration ထဲတွင် သတ်မှတ်ပါ။"),
    ("Your First C# Program", "top-level statements, types, and console output", "string name = \"CodeMaster\";\nConsole.WriteLine($\"Welcome, {name}!\");", "Modern C# supports top-level statements for small programs. Variables have compile-time types, interpolation combines trusted values into text, and the compiler reports many mistakes before execution. Keep output examples deterministic and validate external input at its boundary.", "string name = \"value\";\nConsole.WriteLine($\"Text {name}\");", "C# program သည် top-level statements၊ typed variables နှင့် console output တို့ဖြင့် စတင်နိုင်သည်။"),
    ("Variables and Nullable Types", "value types, reference types, and null safety", "int count = 3;\nstring label = \"items\";\nstring? optional = null;\nConsole.WriteLine($\"{count} {label} {optional ?? \"none\"}\");", "C# distinguishes value and reference types. Nullable reference type analysis helps identify possible null values, but it is a compiler aid rather than runtime validation. Use meaningful types, avoid null-forgiving operators unless the invariant is proven, and validate request data.", "string? value = null;\nvar safe = value ?? \"default\";", "Nullable reference type analysis သည် null ဖြစ်နိုင်သော value များကို compiler ဖြင့် စစ်ဆေးနိုင်စေသည်။"),
    ("Operators and Expressions", "typed evaluation and predictable calculations", "decimal subtotal = 12.50m;\ndecimal tax = 0.05m;\ndecimal total = subtotal * (1 + tax);\nConsole.WriteLine(total.ToString(\"F2\"));", "Use the type that matches the domain: decimal is often appropriate for monetary values, while double is useful for many measurements. Parenthesize business calculations and avoid implicit narrowing conversions that conceal loss of precision.", "decimal total = subtotal * (1 + tax);", "Operator နှင့် expression များတွင် domain နှင့်ကိုက်ညီသော type နှင့် explicit calculation ကို အသုံးပြုပါ။"),
    ("Conditions and Pattern Matching", "safe branches and readable decisions", "int score = 82;\nstring result = score switch\n{\n    >= 80 => \"Strong\",\n    >= 60 => \"Developing\",\n    _ => \"Review\"\n};\nConsole.WriteLine(result);", "Pattern matching expresses decisions while keeping the compiler involved in exhaustiveness and type checks. Authorization decisions must be server-side and explicit; never treat a client-provided role or flag as proof of permission.", "value switch { pattern => result, _ => fallback };", "Pattern matching သည် branch decision များကို readable နှင့် type-safe ဖြစ်စေသည်။"),
    ("Module 1 Review and Assessment", "a strict, nullable-aware C# console program", "int[] scores = { 80, 92, 75 };\ndouble average = scores.Average();\nConsole.WriteLine($\"Average: {average:F1}\");", "This review combines arrays, numeric conversion, LINQ-style aggregation, interpolation, and deterministic output. Before moving to web APIs, learn to separate compile-time guarantees from runtime validation and tests.", "int[] values = { 1, 2, 3 };\nConsole.WriteLine(values.Length);", "Module 1 တွင် .NET၊ typed variables၊ nullable behavior၊ pattern matching နှင့် output ကို ပြန်လည်လေ့လာပါမည်။"),
]

GENERAL = [
    ("Install a Supported .NET SDK", "SDK and target framework compatibility"), ("Project Structure and Build", "csproj, restore, build, and run"),
    ("Typed Variables", "primitive and nullable contracts"), ("Expression Evaluation", "safe calculations"),
    ("Branching and Guards", "readable decisions"), ("Loops and Iteration", "bounded repetition"),
    ("Methods and Parameters", "reusable typed behavior"), ("Arrays and Spans", "indexed data"),
    ("Strings and Encoding", "safe text handling"), ("Lists, Sets, and Dictionaries", "collection choices"),
    ("Exceptions and Diagnostics", "explicit failure paths"), ("Classes and Records", "object state and data models"),
    ("Encapsulation and OOP", "invariants and responsibilities"), ("Interfaces and Abstract Types", "replaceable contracts"),
    ("Patterns and Composition", "maintainable design"), ("Generic Methods", "type-safe reuse"),
    ("Delegates and Lambdas", "behavior as values"), ("LINQ Query Basics", "data transformation"),
    ("LINQ Performance", "deferred execution and measurement"), ("Async and Task", "non-blocking work"),
    ("Files and Serialization", "safe persistence"), ("Modern C# Features", "records, patterns, and required members"),
    ("ADO.NET and SQL", "parameterized data access"), ("EF Core Models", "tracked persistence"),
    ("Database Providers", "SQL Server and PostgreSQL boundaries"), ("ASP.NET Core Pipeline", "HTTP application structure"),
    ("REST API Contracts", "resources and status codes"), ("Identity and Authorization", "secure access control"),
    ("Testing and Security", "confidence and threat boundaries"), ("Blazor and Desktop", "UI runtime choices"),
    ("Clean Architecture", "dependency direction"), ("Containers and CI/CD", "repeatable delivery"), ("Background Services", "reliable asynchronous jobs"),
    ("Enterprise Project Architecture", "a maintainable C# system"), ("Final Capstone Plan", "integration and operational readiness"),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(title, topic, theory, syntax, code, mm, previous, next_title):
    return f"""Introduction
{title} introduces {topic} using modern C# and a supported .NET SDK.

Learning objectives
- Explain {topic} and identify its compile-time or runtime boundary.
- Read and write C# with nullable awareness, explicit contracts, and safe failures.
- Connect the example to APIs, databases, testing, security, and deployment choices.

Prerequisites
{previous}

Chosen compatibility
Use a supported .NET SDK documented by the project, enable nullable analysis and analyzers, and declare the target framework in the .csproj. Verify the exact SDK, ASP.NET Core, EF Core, and database-provider versions before running framework examples.

Detailed theory
{theory}

C# syntax
{syntax}

Working code example
```csharp
{code}
```

Expected output
Run the example with `dotnet run` in a local project using the documented SDK. The shown input produces deterministic output.

Line-by-line explanation
The using directive or project context supplies APIs. Declarations establish compile-time types. The central statement performs one focused operation, and the final statement exposes a result. Read compiler diagnostics from the first reported line before changing unrelated code.

Compiler error explanation
Common diagnostics include assigning a value of the wrong type, possible null dereference, missing namespace/reference, and invalid overload arguments. Fix the underlying contract or guard instead of suppressing the warning globally.

Common mistakes
- Running a project with an unsupported SDK or target framework.
- Disabling nullable warnings instead of handling a possible null.
- Blocking on async work with .Result or .Wait in server code.
- Building SQL by concatenation or logging secrets and tokens.

Best practices
Enable nullable reference types, use analyzers, prefer immutable records where appropriate, validate external input, use parameterized SQL, dispose resources with using, add cancellation and timeouts, test behavior, and document runtime compatibility.

Security considerations
Never execute arbitrary C# inside FastAPI workers. A runner must isolate processes, network, filesystem, CPU, memory, output, concurrency, and cleanup. Enforce authentication and authorization server-side and keep secrets outside source code.

Practice exercises
- Easy: reproduce the example and introduce one intentional compiler error.
- Medium: fix it without suppressing the diagnostic.
- Challenge: add validation, cancellation, or a database boundary appropriate to the topic.
Hints: identify what the compiler proves, what runtime input can violate, and where the boundary should validate.
Guided solution: run `dotnet build`, fix the first diagnostic, then add a focused test for the failure case.

Quiz
1. What should be enabled for null analysis? Nullable reference types.
2. True or false: the client may decide whether a server request is authorized. False.
3. Which SQL approach is recommended? Parameterized commands.
4. What must a code runner isolate? Process, network, filesystem, and resources.

Summary
You can now explain {topic}, interpret C# diagnostics, and separate compile-time checks from runtime validation.

Next lesson
{next_title}
"""

def _questions(topic):
    return [
        (f"Which practice best supports {topic}?", ["Nullable analysis and explicit contracts", "Suppressing all warnings", "Trusting client flags"], "Nullable analysis and explicit contracts", "Compiler analysis is useful when contracts and runtime validation are both respected."),
        ("True or false: async server code should block on .Result by default.", ["True", "False"], "False", "Blocking can cause poor throughput and deadlocks; await asynchronously with cancellation."),
        ("Which database approach is safest for values?", ["Parameterized commands", "String concatenation", "Ignoring validation"], "Parameterized commands", "Parameters keep values separate from SQL instructions."),
        ("What should be documented for framework lessons?", ["SDK and package compatibility", "Only a logo", "No version information"], "SDK and package compatibility", "Declared compatibility makes builds repeatable."),
    ]

def seed_csharp_course(db, course):
    course.title = "C# Programming — From Zero to Advanced"
    course.short_description = "A free modern C# and .NET course covering OOP, LINQ, async programming, EF Core, ASP.NET Core, APIs, security, testing, and enterprise projects."
    course.description = "Learn C# from first principles through modern .NET, collections, OOP, LINQ, async programming, EF Core, ASP.NET Core, REST APIs, security, testing, deployment, and a capstone."
    course.level, course.status, course.published = "advanced", "published", True
    course.outcomes = "Write modern nullable-aware C#|Design object-oriented and generic code|Use LINQ, async tasks, and files safely|Build APIs with ASP.NET Core and EF Core|Test, secure, containerize, and deploy .NET applications"
    course.requirements = "Basic programming, HTML/CSS familiarity, and a terminal. Use a supported .NET SDK documented by each project; examples target modern C# with nullable analysis enabled."
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
            code = f"using System;\n\nConsole.WriteLine(\"{_slug(title)} ready\");"
            specs = [{"title": title, "topic": topic, "code": code, "theory": f"This foundation lesson explains {topic}. Apply it to a small C# feature, then check compiler diagnostics, nullable behavior, runtime failures, and resource boundaries.", "syntax": "Type name = value;\nConsole.WriteLine(name);", "mm": f"ဤ lesson တွင် {topic} ကို modern C# ဖြင့် လေ့လာပါမည်။"}]
        for lesson_index, spec in enumerate(specs, 1):
            title, topic = spec["title"], spec["topic"]
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm=""); db.add(lesson); db.flush()
            previous = "Basic programming and a terminal. Use a supported .NET SDK." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
            next_title = "Continue to the next lesson." if module_index < 36 else "Continue to the final capstone review."
            lesson.title, lesson.slug = title, slug
            lesson.content_en = _content(title, topic, spec["theory"], spec["syntax"], spec["code"], spec["mm"], previous, next_title)
            lesson.content_mm = f"{title} ကို English theory နှင့်အတူ လေ့လာနိုင်ပါသည်။\n\n{spec['mm']}"
            lesson.description, lesson.duration_minutes = spec["theory"], 35
            lesson.status, lesson.published = "published", True; authored.append(lesson)
            examples = list(db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all())
            example = examples[0] if examples else None
            for duplicate in examples[1:]: db.delete(duplicate)
            if not example:
                db.add(CodeExample(lesson_id=lesson.id, title=f"{title} example", language="csharp", filename="Program.cs", code=spec["code"], description="Read-only C# example. Use a local supported .NET SDK; hosted arbitrary execution is disabled.", position=1))
            else:
                example.title, example.language, example.filename, example.code, example.description, example.position = f"{title} example", "csharp", "Program.cs", spec["code"], "Read-only C# example. Use a local supported .NET SDK; hosted arbitrary execution is disabled.", 1
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz: quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the C# and security explanations, then retry missed concepts.", status="published"); db.add(quiz); db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(topic), 1):
                values = dict(prompt=prompt, question_type="true_false" if options == ["True", "False"] else "multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                question = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
                if not question: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(question, key, value)
    course.duration_minutes = sum(x.duration_minutes or 35 for x in authored)
    db.flush()
