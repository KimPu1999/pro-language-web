"""Idempotent authored Modern Java curriculum targeting Java 25 LTS."""
import json
import re
from sqlalchemy import select
from .models import CourseModule, Lesson, LessonQuiz, QuizQuestion, CodeExample

MODULES = [
    "Introduction to Java", "Java Environment Setup", "Your First Java Program", "Variables & Data Types",
    "Operators & Expressions", "Conditional Statements", "Loops & Iteration", "Methods & Scope",
    "Arrays & Multidimensional Arrays", "Strings & Text Processing", "Classes & Objects", "Object-Oriented Programming",
    "Advanced OOP", "Packages & Access Modifiers", "Exception Handling", "Collections Framework", "Generics & Type Safety",
    "Lambda Expressions", "Java Streams API", "File Handling & NIO", "Date, Time & Regular Expressions",
    "Multithreading & Concurrency", "JVM, Memory & Garbage Collection", "Maven, Gradle & Project Structure",
    "Debugging & Unit Testing", "Database Programming with JDBC", "PostgreSQL & Data Persistence", "Spring Boot Fundamentals",
    "REST API Development", "Security, Performance & Deployment", "Real-World Java Projects", "Final Capstone & Assessment",
]

MODULE_ONE = [
    ("What Is Java?", "the JVM and Java's design", "public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Java runs on the JVM.\");\n    }\n}", "Java is a statically typed, object-oriented language designed for portability through the Java Virtual Machine. Source code is compiled to bytecode, then a compatible JDK/JVM runs that bytecode. Java is used for services, Android foundations, enterprise systems, and tooling.", "public class Main { ... }\npublic static void main(String[] args) { ... }", "Java သည် JVM ပေါ်တွင် run နိုင်သော statically typed object-oriented language ဖြစ်သည်။"),
    ("Java Environment Setup", "JDK, JRE concepts, and Java 25 LTS", "public class Main {\n    public static void main(String[] args) {\n        System.out.println(Runtime.version().feature());\n    }\n}", "Use a JDK rather than only a runtime when compiling. This course targets Java 25 LTS; examples use standard language and library features compatible with Java 25. Record the output of java --version and javac --version when diagnosing compatibility.", "javac Main.java\njava Main\njava --version", "JDK 25 LTS ကို target ထားပြီး compile/run version များကို စစ်ဆေးပါ။"),
    ("Your First Java Program", "classes, main, and console output", "public class Main {\n    public static void main(String[] args) {\n        String name = \"CodeMaster\";\n        System.out.println(\"Welcome, \" + name + \"!\");\n    }\n}", "A Java application starts from a class containing a main method. Java statements end with semicolons and blocks use braces. The filename must match a public class name, so Main.java contains public class Main.", "public static void main(String[] args) { ... }", "Java program သည် main method မှ စတင်ပြီး class နှင့် braces ကို အသုံးပြုသည်။"),
    ("Comments and Readable Java", "naming, comments, and formatting", "public class Main {\n    public static void main(String[] args) {\n        // Explain intent, not obvious syntax.\n        int minutesPerLesson = 30;\n        System.out.println(minutesPerLesson);\n    }\n}", "Use lowerCamelCase for variables and methods, UpperCamelCase for classes, and constants in a deliberate style. Comments should explain decisions or constraints. Keep methods small and use a formatter.", "// comment\nint variableName = value;", "Readable Java အတွက် naming convention နှင့် ရိုးရှင်းသော methods များကို အသုံးပြုပါ။"),
    ("The JVM and Compilation", "source, bytecode, and execution", "public class Main {\n    public static void main(String[] args) {\n        int result = 2 + 3;\n        System.out.println(result);\n    }\n}", "javac translates source into bytecode and java launches that bytecode on a JVM. The compiler catches many type and syntax errors before execution. Runtime exceptions still require tests and defensive handling.", "javac Main.java -> Main.class -> java Main", "javac သည် source ကို bytecode ပြောင်းပြီး JVM က ထို bytecode ကို run သည်။"),
    ("Java Files and Packages", "source layout and package names", "package lessons;\n\npublic class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Package boundary\");\n    }\n}", "Packages organize classes and prevent naming collisions. The package declaration must match the directory layout used by the build tool. Keep public APIs small and avoid relying on default-package code in real projects.", "package name;\npublic class ClassName { ... }", "Package များသည် class များကို စနစ်တကျခွဲပြီး naming collision ကို လျှော့ချပေးသည်။"),
    ("Module 1 Review and Assessment", "a small typed Java program", "public class Main {\n    public static void main(String[] args) {\n        int[] scores = {80, 92, 75};\n        int total = scores[0] + scores[1] + scores[2];\n        System.out.println(total / (double) scores.length);\n    }\n}", "This review combines a class, main method, a typed array, arithmetic, casting, and deterministic output. Prefer explicit types, safe resource handling, and tests before moving to larger programs.", "int[] values = { ... };\nSystem.out.println(expression);", "Module 1 တွင် Java class၊ main၊ types၊ arrays နှင့် JVM အခြေခံများကို ပြန်လည်သုံးသပ်ပါ။"),
]

# One focused, substantive lesson for each module between foundations and projects.
GENERAL_LESSONS = [
    ("Install a JDK and IDE", "JDK installation and editor workflow", "public class Main { public static void main(String[] args) { System.out.println(\"Ready\"); } }"),
    ("Types, Variables, and Literals", "static types and declarations", "int count = 3;\nString label = \"Java\";\nSystem.out.println(label + count);"),
    ("Expressions and Assignment", "operators and evaluation", "int total = 2 * (3 + 4);\nSystem.out.println(total);"),
    ("if, else, and switch", "branching decisions", "int score = 82;\nif (score >= 80) { System.out.println(\"Strong\"); }"),
    ("for, while, and enhanced for", "iteration", "for (int index = 0; index < 3; index++) { System.out.println(index); }"),
    ("Methods and Parameters", "reusable behavior", "static int add(int a, int b) { return a + b; }"),
    ("Arrays and Nested Arrays", "fixed-size indexed data", "int[][] grid = {{1, 2}, {3, 4}};\nSystem.out.println(grid[1][0]);"),
    ("String API and Text Blocks", "immutable text", "String text = \"Modern Java\";\nSystem.out.println(text.toUpperCase());"),
    ("Classes, Fields, and Constructors", "object state", "class User { String name; User(String name) { this.name = name; } }"),
    ("Encapsulation and Interfaces", "object contracts", "interface Printable { void print(); }\nrecord Note(String text) implements Printable { public void print() { System.out.println(text); } }"),
    ("Inheritance and Polymorphism", "reusable object behavior", "class Animal { void speak() { System.out.println(\"sound\"); } }\nclass Dog extends Animal { void speak() { System.out.println(\"bark\"); } }"),
    ("Records and Sealed Types", "modern data modeling", "record Point(int x, int y) {}\nSystem.out.println(new Point(2, 3));"),
    ("Packages and Access", "visibility boundaries", "public class PublicApi { private int value = 1; public int value() { return value; } }"),
    ("try, catch, and finally", "recovering from errors", "try { Integer.parseInt(\"bad\"); } catch (NumberFormatException error) { System.out.println(\"Invalid number\"); }"),
    ("Lists, Sets, and Maps", "collection choices", "var names = new java.util.ArrayList<String>();\nnames.add(\"Aye\");\nSystem.out.println(names);"),
    ("Generic Classes and Methods", "type-safe reuse", "static <T> T first(T value) { return value; }\nSystem.out.println(first(\"Java\"));"),
    ("Lambda Expressions", "behavior as a value", "java.util.function.Predicate<Integer> positive = value -> value > 0;\nSystem.out.println(positive.test(3));"),
    ("Stream Pipelines", "map, filter, and reduce", "var result = java.util.List.of(1, 2, 3).stream().map(n -> n * 2).toList();\nSystem.out.println(result);"),
    ("Files and NIO Paths", "safe file operations", "var path = java.nio.file.Path.of(\"notes.txt\");\nSystem.out.println(path.getFileName());"),
    ("Date Time and Regex", "typed time and pattern matching", "var date = java.time.LocalDate.of(2025, 1, 1);\nSystem.out.println(date);"),
    ("Threads and Executors", "concurrent tasks", "try (var executor = java.util.concurrent.Executors.newSingleThreadExecutor()) {\n    System.out.println(executor.submit(() -> \"done\").get());\n}"),
    ("JVM Memory and Resources", "heap, stack, and cleanup", "var values = new java.util.ArrayList<Integer>();\nvalues.add(1);\nSystem.out.println(values.size());"),
    ("Maven and Gradle Structure", "repeatable builds", "// Java source belongs in src/main/java; tests belong in src/test/java.\nSystem.out.println(\"Build structure\");"),
    ("JUnit Testing and Debugging", "executable confidence", "int actual = 2 + 3;\nassert actual == 5;\nSystem.out.println(actual);"),
    ("JDBC and Prepared Statements", "safe database access", "String sql = \"SELECT name FROM users WHERE id = ?\";\nSystem.out.println(sql);"),
    ("PostgreSQL Persistence", "transactions and mapping", "String url = \"jdbc:postgresql://localhost/app\";\nSystem.out.println(url);"),
    ("Spring Boot Fundamentals", "application configuration", "// A Spring Boot app exposes typed components and configuration.\nSystem.out.println(\"Spring\");"),
    ("REST API Design", "HTTP resources and status", "int status = 200;\nSystem.out.println(\"HTTP \" + status);"),
    ("Security, Performance, and Deployment", "safe production boundaries", "String value = System.getenv(\"PUBLIC_CONFIG\");\nSystem.out.println(value == null ? \"unset\" : \"configured\");"),
]

PROJECTS = ["Personal Introduction", "Calculator", "Number Guessing Game", "Student Grade Calculator", "Unit Converter", "Bank Account Simulator", "Quiz Application", "Contact Book CLI", "To-Do List CLI", "Expense Tracker", "Library Management System", "Inventory Management System", "Employee Payroll System", "Student Management System", "File Organizer", "Weather API Client", "PostgreSQL CRUD Application", "Spring Boot REST API", "Authentication API Demo", "Final Java Capstone"]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(title, topic, code, theory, syntax, mm, previous, next_title):
    return f"""Introduction
{title} introduces {topic} using Modern Java targeting Java 25 LTS.

Learning objectives
- Explain {topic} in your own words.
- Read and write type-safe Java with predictable behavior.
- Identify compatibility, error handling, and resource boundaries.

Prerequisites
{previous}

Detailed theory
{theory} The examples target Java 25 LTS and use standard language or library features. Check both javac and java versions before compiling; build tools should declare a compatible toolchain rather than relying on an undocumented local JDK.

Java syntax
{syntax}

Code example
```java
{code}
```

Expected output
Compile examples locally with Java 25 LTS using `javac Main.java` and run with `java Main`. Examples involving packages, build tools, databases, or Spring require the matching project structure and dependencies.

Line-by-line explanation
Imports provide the APIs used by the example. Declarations establish typed state, the central statement performs one focused operation, and the final statement exposes a result. Read compiler diagnostics from the first reported source line and fix the smallest cause first.

Common mistakes
- Using the wrong JDK, filename, package path, or language level.
- Forgetting null handling, resource cleanup, or thread shutdown.
- Catching broad exceptions and hiding the root cause.
- Building SQL with string concatenation or placing credentials in source code.

Best practices
Prefer immutable values, records for simple data, try-with-resources, parameterized SQL, explicit exception handling, tests, clear package boundaries, and a declared Java 25 toolchain. Keep secrets in environment or secret-management systems.

Practice exercises
- Easy: reproduce the example and change one input.
- Medium: add validation and a useful error path.
- Challenge: refactor the behavior into a tested method with clear types.
Hints: identify types, inputs, state changes, outputs, and failure cases first.
Guided solution: compile the smallest program, read the first diagnostic, test the normal path, then test an invalid path.

Summary
You can now explain {topic}, write modern Java, predict output, and choose safer boundaries for real applications.

Next lesson
{next_title}

Myanmar explanation
{mm}
"""

def _questions(title, topic):
    return [
        (f"Which practice best supports {topic}?", ["Use explicit types and resource-safe code", "Ignore compiler diagnostics", "Put secrets in source"], "Use explicit types and resource-safe code", "Java's type system and explicit resource boundaries make behavior easier to verify."),
        ("True or false: Java source with a public class must use the matching filename.", ["True", "False"], "True", "A public class name and source filename must match for the normal javac workflow."),
        ("Which database pattern is recommended?", ["Prepared statements", "SQL string concatenation", "Trust all input"], "Prepared statements", "Prepared statements separate SQL instructions from values."),
        ("What should reliable Java code do with expected failures?", ["Handle them explicitly", "Catch everything silently", "Ignore compiler and runtime diagnostics"], "Handle them explicitly", "Explicit handling preserves useful context for users and maintainers."),
    ]

def seed_java_course(db, course):
    course.title = "Java Programming — From Zero to Advanced"
    course.short_description = "A free Modern Java course targeting Java 25 LTS, covering OOP, collections, streams, concurrency, JDBC, Spring Boot, security, testing, and real projects."
    course.description = "Learn Java from first principles through object-oriented design, collections, streams, files, concurrency, JDBC, PostgreSQL, Spring Boot REST APIs, security, testing, and a final capstone."
    course.level, course.status, course.published = "beginner", "published", True
    course.outcomes = "Write type-safe Modern Java|Design object-oriented applications|Use collections, generics, streams, and concurrency|Build database and REST applications|Test, secure, and deploy Java projects"
    course.requirements = "Basic computer literacy, a text editor or IDE, and a terminal. Examples target Java 25 LTS; no previous Java experience is required."
    authored = []
    for module_index, module_title in enumerate(MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_index))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_index); db.add(module); db.flush()
        module.title = module_title
        if module_index == 1:
            specs = MODULE_ONE
        elif module_index == 31:
            specs = [(name, "a guided Java project", f"public class Main {{\n    public static void main(String[] args) {{\n        String project = \"{name}\";\n        System.out.println(project + \" is ready to build.\");\n    }}\n}}", "A real project combines typed domain models, validation, clear methods, tests, and safe handling of files or services.", "public class Main { ... }", "Project တွင် typed model၊ validation၊ methods နှင့် tests များကို ပေါင်းစပ်ပါ။") for name in PROJECTS]
        elif module_index == 32:
            specs = [("Capstone Plan and Architecture", "planning a maintainable Java system", "public class Main {\n    public static void main(String[] args) {\n        String[] features = {\"validation\", \"tests\", \"logging\"};\n        System.out.println(features.length);\n    }\n}", "Plan domain objects, package boundaries, persistence, error paths, security controls, tests, and deployment configuration before building the final application.", "String[] features = { ... };", "Final project မစမီ domain object၊ package၊ persistence နှင့် tests ကို စီစဉ်ပါ။"), ("Final Java Capstone", "combining Modern Java techniques", "public class Main {\n    public static void main(String[] args) {\n        String app = \"Learning API: ready\";\n        System.out.println(app);\n    }\n}", "Combine clean packages, typed boundaries, persistence, validation, tests, logging, security controls, and measured performance into a useful Java application.", "String app = \"...\";", "Capstone တွင် Java techniques၊ security၊ testing နှင့် maintainability ကို ပေါင်းစပ်ပါ။")]
        else:
            title, topic, code = GENERAL_LESSONS[module_index - 2]
            specs = [(title, topic, code, f"This lesson explains {topic} and shows how it supports a reliable Java program.", f"Use the Java feature deliberately: {topic}.", "ဒီ lesson တွင် Java feature ကို အဓိပ္ပါယ်ရှိစွာ အသုံးပြုနည်းကို လေ့လာပါမည်။")]
        for lesson_index, (title, topic, code, theory, syntax, mm) in enumerate(specs, 1):
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm=""); db.add(lesson); db.flush()
            lesson.title, lesson.slug = title, slug
            previous = "No Java experience is required. Examples target Java 25 LTS." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
            next_title = "Continue to the next module." if module_index == 32 else "Continue with the next lesson."
            lesson.content_en = _content(title, topic, code, theory, syntax, mm, previous, next_title)
            lesson.content_mm = f"{title} ကို English theory နှင့်အတူ လေ့လာနိုင်ပါသည်။\n\n{mm}"
            lesson.description, lesson.duration_minutes = theory, 40 if module_index == 31 else 30
            lesson.status, lesson.published = "published", True; authored.append(lesson)
            examples = list(db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all())
            example = examples[0] if examples else None
            for duplicate in examples[1:]: db.delete(duplicate)
            if not example: db.add(CodeExample(lesson_id=lesson.id, title=f"{title} example", language="java", filename="Main.java", code=code, description="Read-only example. Copy it to a local Java 25 LTS environment to compile safely.", position=1))
            else: example.title, example.language, example.filename, example.code, example.description, example.position = f"{title} example", "java", "Main.java", code, "Read-only example. Copy it to a local Java 25 LTS environment to compile safely.", 1
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz: quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the explanations and retry after studying missed concepts.", status="published"); db.add(quiz); db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(title, topic), 1):
                q = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position)); values = dict(prompt=prompt, question_type="true_false" if options == ["True", "False"] else "multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                if not q: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(q, key, value)
    course.duration_minutes = sum(x.duration_minutes or 30 for x in authored); db.flush()
