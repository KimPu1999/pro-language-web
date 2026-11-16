"""Authored Go programming vertical slice for the idempotent catalog seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

PLANNED_MODULES = [
    "Introduction to Go", "Go Installation & Environment", "Go Syntax & First Program", "Variables & Constants",
    "Data Types & Operators", "Input, Output & Formatting", "Control Flow", "Functions", "Arrays & Slices",
    "Maps", "Strings, Runes & Unicode", "Pointers", "Structs & Methods", "Interfaces", "Packages & Modules",
    "Error Handling", "Defer, Panic & Recover", "Generics", "File Handling & I/O", "JSON & Data Serialization",
    "Date, Time & Regular Expressions", "Testing Fundamentals", "Goroutines", "Channels", "Select & Concurrency Patterns",
    "Mutexes & Synchronization", "Context & Cancellation", "Race Conditions & Deadlocks", "Performance & Profiling",
    "HTTP Servers & REST APIs", "Go Web Frameworks", "PostgreSQL Integration", "Authentication & API Security",
    "Advanced Testing & Quality", "Application Architecture", "Docker & Containerization", "Microservices & gRPC",
    "CI/CD, Deployment & Observability", "Professional Go Projects", "Final Go Capstone & Assessment",
]

MODULE_ONE = [
    ("Why Go and How Go Programs Run", "compiled programs, simplicity, and explicit tooling", "go version\ngo env GOROOT GOPATH\ngo help", "terminal", "Go is a compiled, statically typed language designed for readable software, fast builds, and practical concurrency. The compiler, formatter, module system, and test runner are part of the standard toolchain. Treat tool versions and dependencies as part of the build contract.", "Go သည် readable software၊ fast build နှင့် concurrency အတွက် ရည်ရွယ်ထားသော compiled၊ statically typed language ဖြစ်သည်။ Compiler၊ formatter၊ module system နှင့် test runner များသည် standard toolchain ၏ အစိတ်အပိုင်းများဖြစ်သည်။", "List three properties of Go that support maintainable backend services.", ("Go toolchain တွင် ဘာပါဝင်သနည်း?", ["Compiler, formatter, modules, and test tooling", "Only a text editor", "A hosted database"], "Compiler, formatter, modules, and test tooling", "Go ships with a cohesive developer toolchain.")),
    ("Install Go and Verify the Environment", "version checks, workspace boundaries, and reproducible setup", "go version\ngo env GOPATH GOMODCACHE\ngofmt -h\ngo test -h", "terminal", "Install Go from the official distribution and verify the version in a disposable workspace. GOPATH and the module cache are environment details, while a project module defines dependencies. Avoid copying binaries or dependencies from untrusted sources.", "Official Go distribution ကို install ပြီး version နှင့် environment ကို verify လုပ်ပါ။ Project module သည် dependency များကို သတ်မှတ်သည်။", "Record a fictional setup checklist that includes the Go version, operating system, and module policy.", ("Dependency များအတွက် ဘာကို verify လုပ်သင့်သနည်း?", ["Source, version, and module integrity", "A random binary URL", "A production secret"], "Source, version, and module integrity", "Reproducible builds require known tool and dependency inputs.")),
    ("Create a Module and First Program", "package main, modules, and the program entry point", "mkdir hello-go\ncd hello-go\ngo mod init example.com/hello\ngofmt -w main.go\ngo run .", "terminal", "A Go executable starts in package main and its main function. go.mod records the module path and Go version. go run is convenient for development; production builds should be reproducible and reviewed.", "Go executable သည် package main နှင့် main function မှ စတင်သည်။ go.mod သည် module path နှင့် Go version ကို မှတ်တမ်းတင်သည်။", "Create a hello program outline and identify which file belongs to package main.", ("Go program ၏ entry point က ဘာလဲ?", ["main function in package main", "Any random function", "The README file"], "main function in package main", "The main package and main function define an executable entry point.")),
    ("Variables, Constants, and Explicit Types", "declarations, zero values, and readable data flow", "var count int\nconst serviceName = \"learning-api\"\nmessage := \"hello\"\n_ = count\n_ = serviceName\n_ = message", "go", "Go declarations make types and zero values predictable. Short declarations are convenient inside functions, while constants represent values that should not change. Prefer clear names and narrow scopes; do not hide configuration or credentials in source.", "Go declaration များသည် type နှင့် zero value ကို predictable ဖြစ်စေသည်။ Function အတွင်း short declaration ကို သုံးနိုင်ပြီး constant သည် မပြောင်းလဲသင့်သော value များအတွက် ဖြစ်သည်။", "Explain when a constant is more appropriate than a variable and identify the type of each example.", ("Short declaration := ကို ဘယ်နေရာတွင် သုံးသနည်း?", ["Inside functions", "Only in package comments", "In a SQL database"], "Inside functions", "The short declaration form is scoped to function bodies.")),
    ("Types, Operators, and Zero Values", "numeric types, booleans, strings, and safe expressions", "var total int = 42\nvar enabled bool = true\nvar label string = \"Go\"\nresult := total + 8\n_ = enabled\n_ = label\n_ = result", "go", "Go has explicit built-in types and useful zero values. Operators follow clear precedence, but conversions between numeric types are explicit. Validate external input before converting or using it in security-sensitive logic.", "Go တွင် built-in type နှင့် zero value များရှိသည်။ Numeric conversion သည် explicit ဖြစ်ပြီး external input ကို validate လုပ်ပြီးမှ သုံးရသည်။", "Predict the result of a typed arithmetic expression and explain why implicit numeric conversion is not assumed.", ("Go တွင် numeric conversion သည် မည်သို့ဖြစ်သနည်း?", ["Explicitly", "Always implicitly", "Only through SQL"], "Explicitly", "Explicit conversions make data boundaries visible.")),
    ("Functions and Multiple Return Values", "parameters, results, and error-aware APIs", "package main\n\nimport \"fmt\"\n\nfunc divide(a, b float64) (float64, error) {\n\tif b == 0 { return 0, fmt.Errorf(\"division by zero\") }\n\treturn a / b, nil\n}", "go", "Functions are first-class building blocks in Go. Multiple return values make it natural to return a result and an error together. Keep functions focused, validate inputs at boundaries, and avoid swallowing errors.", "Function များသည် Go ၏ အဓိက building block ဖြစ်သည်။ Multiple return value ကြောင့် result နှင့် error ကို အတူပြန်နိုင်သည်။", "Design a function signature that returns a parsed value and an error without panicking on user input.", ("Go API တွင် error ကို ဘယ်လိုပြန်လေ့ရှိသနည်း?", ["As an explicit return value", "By hiding it globally", "By logging credentials"], "As an explicit return value", "Explicit errors keep failure handling visible to callers.")),
    ("Arrays, Slices, and Safe Mutation", "fixed arrays, dynamic slices, length, and capacity", "numbers := []int{1, 2, 3}\nnumbers = append(numbers, 4)\nfor index, value := range numbers {\n\tfmt.Println(index, value)\n}", "go", "Arrays have fixed length; slices provide a view over an array with length and capacity. append may allocate a new backing array, so code should not rely on hidden aliasing. Validate indexes and avoid exposing mutable internal slices without a contract.", "Array သည် fixed length ဖြစ်ပြီး slice သည် array ပေါ်ရှိ dynamic view ဖြစ်သည်။ append သည် backing array အသစ်ဖန်တီးနိုင်သောကြောင့် aliasing ကို သတိထားပါ။", "Compare an array and slice API and explain what append can change.", ("Slice တွင် ဘာကို သတိထားရမည်နည်း?", ["Length, capacity, and backing-array aliasing", "Only CSS styles", "Remote Git credentials"], "Length, capacity, and backing-array aliasing", "Slice operations can share or reallocate backing storage.")),
    ("Your First Tested Go Workflow", "gofmt, go test, and a small maintainable package", "gofmt -w .\ngo test ./...\ngo vet ./...\ngo build ./...", "terminal", "A professional Go loop formats code, runs tests, checks common mistakes, and builds an artifact. Tests should be deterministic and isolated. Do not treat a successful build as proof of authorization, security, or production readiness.", "Professional Go workflow တွင် gofmt၊ go test၊ go vet နှင့် go build ပါဝင်သည်။ Test များသည် deterministic နှင့် isolated ဖြစ်သင့်သည်။", "Create a checklist for a small package: format, test, vet, build, and review secrets before commit.", ("Go code quality workflow တွင် ဘာကို အရင် run လုပ်သင့်သနည်း?", ["gofmt and tests before build", "A destructive cleanup", "A production secret command"], "gofmt and tests before build", "Formatting and tests provide early feedback before packaging.")),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(position: int, item: tuple) -> str:
    title, topic, commands, filename, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    previous = "No Go experience is required; a text editor is helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: complete the first Go program lab and review the Module 1 assessment."
    return f"""Introduction
{title} introduces {topic} through small, runnable Go examples.

Learning objectives
- Explain {topic} in your own words.
- Predict the result before running the example.
- Identify input, dependency, build, and security boundaries.

Prerequisites
{previous}

Go architecture explanation
source files -> package -> module -> compiler/toolchain -> executable or test

Detailed theory
{theory}

Step-by-step code and commands
{commands}

File paths and folder structure
project/
  go.mod
  main.go
  internal/
  tests/

Expected output
Exact output depends on the Go version and local files. Verify the state with the relevant Go command instead of copying unverified output.

Code explanation
Read each declaration and command, identify its package and scope, then explain how data moves through the program. Keep examples in an isolated workspace.

Common errors
- Running commands outside the module root.
- Mixing package names in one directory.
- Ignoring returned errors or using an unsafe type conversion.
- Assuming a successful build proves runtime correctness.

Troubleshooting
Check go version, go env, go mod tidy output, package names, compiler errors, and the smallest failing test. Preserve the error context before changing multiple files.

Best practices
- Format with gofmt, test with go test, inspect dependencies, and keep functions focused.
- Validate external input and return explicit errors.
- Keep secrets out of source, examples, logs, and committed configuration.

Security considerations
Do not hardcode credentials, execute untrusted code, or expose filesystem paths in an API response. Use least-privilege configuration and review dependencies.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Create a small isolated Go package with a README, one focused function, a test, and a clean gofmt/go test workflow. Use placeholder data only.

Summary
You can now reason about {topic} as a typed, testable Go program state transition.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
The Academy displays Go examples and does not execute untrusted code on its application host.
"""

def seed_go_course(db, course):
    course.title = "Go Programming — From Zero to Professional"
    course.short_description = "A free, practical path from Go fundamentals to typed, tested backend services and concurrency."
    course.description = "Learn Go syntax, packages, errors, testing, concurrency, HTTP APIs, databases, security, Docker, gRPC, and observability through safe examples."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 35
    course.outcomes = "Write readable, typed Go programs with modules, packages, functions, and tests|Use explicit errors, slices, structs, and interfaces safely|Build a foundation for concurrent services and REST APIs|Apply reproducible tooling, dependency, and secret-management practices"
    course.requirements = "A text editor and basic command-line familiarity; no previous Go experience is required."
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
        values = {"title": f"{title} example", "language": "go" if item[3] == "go" else "bash", "filename": item[3], "code": item[2], "description": "Read-only Go example. Run locally in an isolated workspace; the Academy does not execute code on its host.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the Go state transition and safety boundary before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [(item[7][0], item[7][1], item[7][2], item[7][3]), ("True or false: the Academy executes arbitrary Go code on its application host.", ["True", "False"], "False", "Examples are displayed as read-only learning content."), ("Which practice improves Go reliability?", ["Format, test, validate inputs, and keep secrets out of source", "Ignore errors and hardcode tokens", "Run untrusted code in production"], "Format, test, validate inputs, and keep secrets out of source", "Tooling, explicit errors, validation, and secret hygiene reduce risk.")]
        for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
            row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
            values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
            if not row:
                db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
            else:
                for key, value in values.items():
                    setattr(row, key, value)
    db.flush()
