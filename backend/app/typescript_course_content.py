"""Idempotent authored TypeScript curriculum.

Module 1 is the complete vertical slice. Later modules contain an authored
foundation lesson each so the catalog never publishes empty modules.
"""
import json
import re
from sqlalchemy import select
from .models import CourseModule, Lesson, LessonQuiz, QuizQuestion, CodeExample

MODULES = [
    "Introduction to TypeScript", "Environment Setup", "Your First TypeScript Program", "Variables & Basic Types",
    "Type Inference & Annotations", "Operators & Control Flow", "Functions & Parameters", "Arrays, Tuples & Readonly",
    "Objects & Type Aliases", "Interfaces", "Union & Intersection Types", "Type Narrowing & Guards",
    "Generics Fundamentals", "Advanced Generics", "Classes & OOP", "Enums, Literal Types & as const",
    "Utility Types", "Mapped & Conditional Types", "Template Literal Types", "Modules & Namespaces",
    "tsconfig & Compiler Options", "Async TypeScript & APIs", "Error Handling & Validation", "Type Declarations & Libraries",
    "React with TypeScript", "Next.js with TypeScript", "Node.js with TypeScript", "REST APIs & Backend Types",
    "Testing & Debugging", "Security, Performance & Best Practices", "Real-World TypeScript Projects", "Final Capstone & Assessment",
]

MODULE_ONE = [
    ("What Is TypeScript?", "static analysis for JavaScript programs", "const message: string = \"TypeScript checks intent before runtime.\";\nconsole.log(message);", "TypeScript is a language and toolchain that adds static types to JavaScript. The compiler checks many mistakes before code reaches a browser or server, then emits JavaScript. Types disappear at runtime, so external input still needs runtime validation. TypeScript is a complement to JavaScript, not a replacement for testing.", "const variable: type = value;", "TypeScript သည် JavaScript code ကို runtime မတိုင်မီ type စစ်ဆေးနိုင်ရန် static type system ထည့်ပေးသော language ဖြစ်သည်။"),
    ("Environment Setup and Strict Mode", "a reproducible compiler workflow", "{\n  \"compilerOptions\": {\n    \"strict\": true,\n    \"target\": \"ES2022\",\n    \"module\": \"NodeNext\"\n  }\n}", "A reliable project pins its TypeScript compiler and documents the runtime target. strict mode enables useful checks such as noImplicitAny and strictNullChecks. The target controls emitted JavaScript syntax; the runtime and bundler must support the chosen module configuration.", "npx tsc --noEmit\nnpx tsc", "strict mode နှင့် compiler target ကို project configuration ထဲတွင် သတ်မှတ်ပြီး reproducible build တည်ဆောက်ပါ။"),
    ("Your First Typed Program", "annotations, inference, and emitted JavaScript", "function greet(name: string): string {\n  return `Hello, ${name}`;\n}\nconsole.log(greet(\"CodeMaster\"));", "Annotations describe contracts at boundaries. Inference lets the compiler determine obvious local types, so adding types everywhere is not the goal. The compiler emits JavaScript and removes annotations; type checking and runtime execution are separate steps.", "function name(parameter: type): returnType { return value; }", "Typed program တွင် parameter နှင့် return type များကို သတ်မှတ်ပြီး compiler က error များကို ကြိုတင်ပြသည်။"),
    ("Primitive Types and Safe Values", "string, number, boolean, null, and undefined", "const count: number = 3;\nconst enabled: boolean = true;\nconst label: string = \"items\";\nconsole.log(`${count} ${label}`, enabled);", "Use primitive types for values and strict null checks for absence. Avoid any because it removes useful guarantees. unknown is safer for data whose shape has not been validated yet.", "let value: string | undefined;", "Primitive type များနှင့် null/undefined ကို strict mode အောက်တွင် သေချာစွာ ကိုင်တွယ်ပါ။"),
    ("Type Inference and Annotations", "letting the compiler infer safe local types", "const total = 2 + 3;\nlet status = \"pending\";\nstatus = \"ready\";\nconsole.log(total, status);", "Inference is strongest when values are initialized near their declaration. An annotation is valuable at public boundaries, function signatures, and intentionally broad values. Do not use assertions to silence an error you have not understood.", "const inferred = expression;\nconst explicit: Type = expression;", "Inference သည် local value များအတွက် အသုံးဝင်ပြီး public boundary တွင် explicit annotation ထည့်သွင်းပါ။"),
    ("Control Flow and Type-Safe Decisions", "conditions that preserve type information", "function format(value: string | number): string {\n  if (typeof value === \"number\") return value.toFixed(2);\n  return value.trim();\n}\nconsole.log(format(4));", "TypeScript narrows a union when control flow proves which member is present. Use clear guards, handle every branch, and keep runtime checks close to untrusted input. The checker does not make a network response safe automatically.", "if (typeof value === \"string\") { /* value is string */ }", "Control flow နှင့် type guard များသည် union type ကို branch အလိုက် safe ဖြစ်စေသည်။"),
    ("Module 1 Review and Assessment", "types, inference, narrowing, and emitted output", "type Score = number;\nfunction average(scores: Score[]): number {\n  return scores.reduce((sum, score) => sum + score, 0) / scores.length;\n}\nconsole.log(average([80, 92, 75]));", "This assessment combines a type alias, typed array, function contract, inference, and runtime output. Check the source with the compiler, inspect emitted JavaScript, then test empty input because static types do not prove business invariants.", "type Alias = ExistingType;\nfunction name(input: Type): ReturnType { }", "Module 1 တွင် types၊ inference၊ narrowing နှင့် transpiled JavaScript အခြေခံများကို ပြန်လည်လေ့လာပါမည်။"),
]

GENERAL = [
    ("First Typed Workspace", "compiler, editor, and runtime workflow"), ("Program Structure", "entry points and modules"),
    ("Variables and Basic Types", "explicit values and contracts"), ("Inference in Real Code", "readable annotations"),
    ("Control Flow", "narrowing through branches"), ("Function Contracts", "parameters and return types"),
    ("Arrays and Tuples", "ordered data with fixed shapes"), ("Objects and Type Aliases", "named domain shapes"),
    ("Interfaces", "extensible object contracts"), ("Unions and Intersections", "composing alternatives"),
    ("Type Guards", "runtime checks with static narrowing"), ("Generic Functions", "reusable type-safe behavior"),
    ("Generic Constraints", "safe relationships between types"), ("Classes and Encapsulation", "typed object design"),
    ("Literal Types and as const", "precise immutable values"), ("Utility Types", "transforming existing contracts"),
    ("Mapped and Conditional Types", "type-level transformations"), ("Template Literal Types", "typed string patterns"),
    ("ES Modules", "imports and exports"), ("Namespaces and Legacy Code", "migration boundaries"),
    ("tsconfig for Production", "strict compiler options"), ("Async Functions and APIs", "typed asynchronous results"),
    ("Validation and Errors", "runtime validation at boundaries"), ("Declaration Files", "typing JavaScript libraries"),
    ("React Props and State", "component contracts"), ("Next.js Route Types", "typed full-stack boundaries"),
    ("Node.js Services", "server runtime types"), ("REST API Contracts", "request and response models"),
    ("Testing TypeScript", "type checks and behavioral tests"), ("Security and Performance", "safe and efficient code"),
    ("Project Architecture", "maintainable TypeScript systems"),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(title, topic, theory, syntax, code, mm, previous, next_title):
    return f"""Introduction
{title} introduces {topic} with modern TypeScript and JavaScript runtime behavior.

Learning objectives
- Explain {topic} and distinguish static checks from runtime behavior.
- Read and write strict TypeScript with useful contracts and safe boundaries.
- Inspect compiler diagnostics and understand the emitted JavaScript.

Prerequisites
{previous}

Detailed theory
{theory}

TypeScript syntax
{syntax}

Working code example
```typescript
{code}
```

Expected output
The program prints the documented deterministic result after compiling and running the emitted JavaScript.

Type-checking explanation
Run `tsc --noEmit` to check types without producing files. A successful type check does not validate network data, user input, or business rules at runtime. Use schemas and tests at those boundaries.

JavaScript transpiled output
Type annotations, interfaces, and type aliases are erased. The emitted JavaScript keeps executable statements and uses the configured target/module settings. Inspect actual compiler output rather than assuming every target emits the same syntax.

Line-by-line explanation
The type or signature describes a contract. The implementation performs runtime work. The final statement demonstrates output. Compiler diagnostics should be fixed at the smallest responsible line instead of silenced with an unsafe assertion.

JavaScript vs TypeScript
JavaScript executes directly in a runtime. TypeScript adds compile-time analysis and emits JavaScript; it cannot enforce types after data crosses a network or JSON boundary.

Common mistakes
- Using any or an assertion to hide an unresolved design problem.
- Assuming a type annotation validates runtime input.
- Ignoring strictNullChecks or compiler diagnostics.
- Publishing declarations that do not match the JavaScript implementation.

Best practices
Use strict mode, infer obvious locals, type public boundaries, prefer unknown over any, validate external data, keep modules small, and test runtime behavior as well as compiler behavior.

Practice exercises
- Easy: reproduce the example and introduce one intentional type error.
- Medium: fix it without using any or an unsafe assertion.
- Challenge: add runtime validation and a behavioral test for invalid input.
Hints: identify what the compiler knows, what the runtime receives, and where validation belongs.
Guided solution: run the checker first, inspect the error, then add the smallest explicit contract or guard.

Quiz
1. What does TypeScript emit? JavaScript.
2. True or false: a type annotation validates JSON at runtime. False.
3. Which type is safer for unknown input? unknown.
4. What does strict mode provide? Stronger compile-time checks.

Summary
You can now explain {topic}, interpret diagnostics, and separate static guarantees from runtime validation.

Next lesson
{next_title}
"""

def _questions(topic):
    return [
        (f"Which practice best supports {topic}?", ["Strict checks and runtime validation", "Assertions everywhere", "Defaulting all values to any"], "Strict checks and runtime validation", "TypeScript is strongest when static contracts and runtime boundary checks work together."),
        ("True or false: interfaces remain in emitted JavaScript.", ["True", "False"], "False", "Types and interfaces are erased during compilation."),
        ("Which type is safer for unvalidated external data?", ["unknown", "any", "never checking it"], "unknown", "unknown requires a check before use."),
        ("What does tsc --noEmit do?", ["Type-checks without writing output", "Runs arbitrary server code", "Validates all network data"], "Type-checks without writing output", "It checks the program but does not emit JavaScript files."),
    ]

def seed_typescript_course(db, course):
    course.title = "TypeScript Programming — From Zero to Advanced"
    course.short_description = "A free modern TypeScript course covering strict typing, generics, React, Next.js, Node.js, APIs, testing, security, and full-stack projects."
    course.description = "Learn TypeScript from JavaScript foundations through advanced type design, React, Next.js, Node.js, API contracts, testing, security, performance, and a final capstone."
    course.level, course.status, course.published = "advanced", "published", True
    course.outcomes = "Write strict TypeScript with useful contracts|Design generics and advanced types|Build typed React, Next.js, and Node.js applications|Validate API boundaries at runtime|Test, secure, and optimize full-stack TypeScript projects"
    course.requirements = "JavaScript fundamentals, HTML/CSS basics, and a terminal. JavaScript Programming is the recommended prerequisite. Examples target a current TypeScript compiler with strict mode; declare compatible Node.js and framework versions in each project."
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
            code = f"const status: string = \"{_slug(title)} ready\";\nconsole.log(status);"
            specs = [{"title": title, "topic": topic, "code": code, "theory": f"This foundation lesson explains {topic}. Apply the concept to a small strict TypeScript feature, then check both compiler diagnostics and runtime behavior.", "syntax": "const value: Type = expression;", "mm": f"ဤ lesson တွင် {topic} ကို strict TypeScript ဖြင့် လေ့လာပါမည်။"}]
        for lesson_index, spec in enumerate(specs, 1):
            title, topic = spec["title"], spec["topic"]
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm=""); db.add(lesson); db.flush()
            previous = "JavaScript fundamentals and a terminal. JavaScript Programming is recommended." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
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
                db.add(CodeExample(lesson_id=lesson.id, title=f"{title} example", language="typescript", filename="main.ts", code=spec["code"], description="Read-only TypeScript example. Use a pinned compiler locally; hosted arbitrary runtime execution is disabled.", position=1))
            else:
                example.title, example.language, example.filename, example.code, example.description, example.position = f"{title} example", "typescript", "main.ts", spec["code"], "Read-only TypeScript example. Use a pinned compiler locally; hosted arbitrary runtime execution is disabled.", 1
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz: quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the type-system explanation and retry missed concepts.", status="published"); db.add(quiz); db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(topic), 1):
                values = dict(prompt=prompt, question_type="true_false" if options == ["True", "False"] else "multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                question = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
                if not question: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(question, key, value)
    course.duration_minutes = sum(x.duration_minutes or 35 for x in authored)
    db.flush()
