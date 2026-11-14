"""Idempotent authored Modern JavaScript curriculum."""
import json
import re
from sqlalchemy import select
from .models import CourseModule, Lesson, LessonQuiz, QuizQuestion, CodeExample

MODULES = [
    "Introduction to JavaScript", "Development Environment Setup", "Your First JavaScript Program",
    "Variables & Data Types", "Operators & Expressions", "Conditional Statements", "Loops & Iteration",
    "Functions", "Scope, Hoisting & Closures", "Arrays & Array Methods", "Objects & Object Methods",
    "Strings, Numbers & Math", "Dates, Time & Intl", "DOM Fundamentals", "DOM Manipulation",
    "Events & Event Handling", "Forms & Validation", "Browser Storage", "JSON & Data Handling",
    "Asynchronous JavaScript", "Fetch API & HTTP", "Error Handling & Debugging", "Modern JavaScript Features",
    "ES Modules & Code Organization", "Object-Oriented JavaScript", "Advanced JavaScript Concepts",
    "Web Security & Best Practices", "Testing & Performance", "Real-World JavaScript Projects",
    "Final Capstone & Assessment",
]

MODULE_ONE = [
    ("What Is JavaScript?", "the role of behavior on the web", "const message = \"JavaScript adds behavior.\";\nconsole.log(message);", "JavaScript is a programming language that can respond to events, transform data, update documents, and communicate with services. HTML describes structure and CSS describes presentation; JavaScript adds behavior. It can run in browsers and other JavaScript runtimes.", "const identifier = value;\nconsole.log(identifier);", "JavaScript သည် web page များတွင် behavior နှင့် interaction ထည့်ပေးသော programming language ဖြစ်သည်။"),
    ("Development Environment Setup", "runtime, editor, console, and files", "console.log(\"Open the browser console to inspect output.\");", "A beginner workflow uses an editor, a browser, and developer tools. The console is useful for small experiments and diagnostics. Save source files, reload deliberately, and read the first error before making a change.", "console.log(value);\n<script src=\"app.js\" defer></script>", "Editor၊ browser နှင့် developer console တို့ဖြင့် JavaScript ကို စတင်လေ့လာနိုင်သည်။"),
    ("Your First JavaScript Program", "statements, expressions, and output", "const learner = \"CodeMaster\";\nconsole.log(`Welcome, ${learner}!`);", "A statement performs an action and an expression produces a value. Template literals make it easy to combine text and values. Prefer const by default, use let when reassignment is required, and avoid global variables.", "const name = \"value\";\nconsole.log(`Text ${name}`);", "Statement နှင့် expression တို့သည် program ၏ အခြေခံအစိတ်အပိုင်းများ ဖြစ်သည်။"),
    ("Comments and Readable Code", "comments, naming, and formatting", "// A short comment explains intent.\nconst minutesPerLesson = 30;\nconsole.log(minutesPerLesson);", "Comments should explain why a decision exists, not repeat obvious syntax. Clear names, small functions, consistent formatting, and strict equality make code easier to review and maintain.", "// comment\n/* block comment */\nconst descriptiveName = value;", "Comment များသည် syntax ကိုပြန်ရေးရန်မဟုတ်ဘဲ intent ကိုရှင်းပြရန် အသုံးပြုပါ။"),
    ("The JavaScript Runtime", "parsing, execution, and the console", "const result = 2 + 3;\nconsole.log(result);", "A runtime parses source, evaluates expressions, and reports errors. Browser JavaScript also has APIs such as document and fetch, but those APIs are not the language itself. Learn to distinguish language features from host APIs.", "source -> parse -> execute -> output", "Runtime က source ကို parse လုပ်ပြီး execute လုပ်ကာ output သို့မဟုတ် error ပြသည်။"),
    ("JavaScript in an HTML Page", "defer and safe script loading", "const title = document.querySelector(\"#title\");\nif (title) title.textContent = \"Loaded\";", "The defer attribute lets the browser parse the document before running an external script and preserves script order. Keep scripts in separate files and avoid inline event-handler attributes.", "<script src=\"app.js\" defer></script>", "defer သည် HTML document parse ပြီးမှ external script ကို run စေပြီး page ကိုပိုမိုယုံကြည်စိတ်ချရစေသည်။"),
    ("Module 1 Review and Assessment", "a small safe program", "const scores = [80, 92, 75];\nconst average = scores.reduce((sum, score) => sum + score, 0) / scores.length;\nconsole.log(average);", "This review combines constants, arrays, an expression, a callback, and console output. JavaScript code should be deterministic in examples, should validate inputs at boundaries, and should never expose secrets in browser source.", "const value = expression;\narray.method((item) => result);", "Module 1 တွင် JavaScript syntax၊ runtime၊ HTML integration နှင့် safe coding အခြေခံများကို ပြန်လည်သုံးသပ်ပါ။"),
]

MODULE_LESSONS = [
    [("Install a JavaScript Workspace", "editors, browsers, and developer tools", "console.log(\"Workspace ready\");"), ("Use the Console", "experiments and diagnostics", "console.table([{ topic: \"console\" }, { topic: \"debugging\" }]);")],
    [("Scripts, defer, and Modules", "safe script loading", "document.querySelector(\"#app\").textContent = \"Loaded\";"), ("Values and Expressions", "readable expression evaluation", "const total = 4 * (3 + 2);\nconsole.log(total);")],
    [("const, let, and Reassignment", "bindings and mutability", "const language = \"JavaScript\";\nlet lessons = 1;\nlessons += 1;\nconsole.log(language, lessons);"), ("Primitive and Reference Values", "value categories", "const isReady = true;\nconst learner = { name: \"Aye\" };\nconsole.log(typeof isReady, learner.name);")],
    [("Arithmetic and Assignment", "numeric operators", "let points = 10;\npoints += 5;\nconsole.log(points);"), ("Comparison and Logical Operators", "boolean expressions", "const canStart = age >= 13 && accepted === true;\nconsole.log(canStart);")],
    [("if, else if, and else", "branching decisions", "const score = 82;\nif (score >= 80) console.log(\"Strong\");"), ("switch and Guard Clauses", "clear multi-branch logic", "const role = \"student\";\nswitch (role) { case \"student\": console.log(\"Learn\"); break; default: console.log(\"Review\"); }")],
    [("for and while Loops", "repetition and termination", "for (let index = 0; index < 3; index += 1) console.log(index);"), ("for...of and Loop Control", "iterating collections", "for (const language of [\"HTML\", \"CSS\", \"JS\"]) console.log(language);")],
    [("Function Declarations and Expressions", "reusable behavior", "function greet(name) { return `Hello, ${name}`; }\nconsole.log(greet(\"Mya\"));"), ("Arrow Functions and Parameters", "concise callbacks", "const double = (value) => value * 2;\nconsole.log(double(4));")],
    [("Block Scope and Shadowing", "where bindings are visible", "{ const local = \"inside\"; console.log(local); }"), ("Closures", "functions remembering context", "function makeCounter() { let count = 0; return () => ++count; }\nconst next = makeCounter(); console.log(next(), next());")],
    [("Creating and Reading Arrays", "ordered collections", "const topics = [\"HTML\", \"CSS\", \"JS\"];\nconsole.log(topics[2]);"), ("map, filter, and reduce", "transforming data", "const doubled = [1, 2, 3].map(number => number * 2);\nconsole.log(doubled);")],
    [("Object Properties and Methods", "key-value data", "const user = { name: \"Lin\", greet() { return `Hi ${this.name}`; } };\nconsole.log(user.greet());"), ("Destructuring and Spread", "copying and extracting data", "const user = { name: \"Lin\", level: \"beginner\" };\nconst { name } = user;\nconsole.log(name);")],
    [("String Methods", "searching and transforming text", "const title = \"Modern JavaScript\";\nconsole.log(title.toUpperCase());"), ("Numbers, Math, and Precision", "numeric operations", "console.log(Math.round(4.6), Number.isFinite(4));")],
    [("Date Objects and Time", "timestamps and formatting", "const date = new Date(\"2025-01-01T00:00:00Z\");\nconsole.log(date.toISOString());"), ("Intl Formatting", "locale-aware presentation", "const money = new Intl.NumberFormat(\"en-US\", { style: \"currency\", currency: \"USD\" });\nconsole.log(money.format(12.5));")],
    [("Selecting DOM Elements", "document queries", "const heading = document.querySelector(\"h1\");\nconsole.log(heading?.textContent);"), ("DOM Nodes and Properties", "reading document state", "const list = document.querySelector(\"ul\");\nconsole.log(list?.children.length);")],
    [("Creating and Updating Elements", "safe text and nodes", "const item = document.createElement(\"li\");\nitem.textContent = \"New item\";\ndocument.querySelector(\"ul\")?.append(item);"), ("Classes and Attributes", "stateful presentation hooks", "const card = document.querySelector(\".card\");\ncard?.classList.add(\"is-active\");")],
    [("Event Listeners", "responding to user actions", "button.addEventListener(\"click\", () => console.log(\"Clicked\"));"), ("Event Delegation", "handling dynamic children", "list.addEventListener(\"click\", event => { if (event.target instanceof Element) console.log(event.target.textContent); });")],
    [("Reading Form Values", "controlled form input", "form.addEventListener(\"submit\", event => { event.preventDefault(); console.log(new FormData(form).get(\"email\")); });"), ("Native and Custom Validation", "useful error messages", "input.setCustomValidity(input.value ? \"\" : \"Email is required\");")],
    [("localStorage and sessionStorage", "small client preferences", "localStorage.setItem(\"theme\", \"dark\");\nconsole.log(localStorage.getItem(\"theme\"));"), ("Storage Privacy and Limits", "safe persistence boundaries", "const preferences = { compact: true };\nlocalStorage.setItem(\"preferences\", JSON.stringify(preferences));")],
    [("JSON Parse and Stringify", "serializing data", "const json = JSON.stringify({ ok: true });\nconsole.log(JSON.parse(json).ok);"), ("Data Validation at Boundaries", "defensive input handling", "const data = JSON.parse(\"{\\\"count\\\":2}\");\nif (typeof data.count === \"number\") console.log(data.count);")],
    [("Promises and States", "future values", "Promise.resolve(\"loaded\").then(value => console.log(value));"), ("async and await", "readable asynchronous flow", "async function load() { const value = await Promise.resolve(\"ready\"); console.log(value); }\nload();")],
    [("Fetch and Request Basics", "HTTP requests", "fetch(\"/api/courses\").then(response => response.json()).then(data => console.log(data));"), ("Response Status and JSON", "checking remote results", "async function read(response) { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json(); }")],
    [("try, catch, and finally", "recoverable failures", "try { JSON.parse(\"bad\"); } catch (error) { console.error(\"Invalid data\"); }"), ("Debugging with Breakpoints", "investigating behavior", "const value = 2;\ndebugger;\nconsole.log(value);")],
    [("Optional Chaining and Nullish Coalescing", "safe access defaults", "const label = user?.profile?.name ?? \"Guest\";\nconsole.log(label);"), ("Rest, Spread, and Default Parameters", "flexible function APIs", "function sum(...values) { return values.reduce((a, b) => a + b, 0); }\nconsole.log(sum(1, 2, 3));")],
    [("export and import", "module boundaries", "export const appName = \"CodeMaster\";"), ("Organizing Modules", "small maintainable files", "import { appName } from \"./config.js\";\nconsole.log(appName);")],
    [("Classes and Instances", "object-oriented syntax", "class Counter { constructor() { this.value = 0; } increment() { this.value += 1; } }\nconst counter = new Counter(); counter.increment();"), ("Composition over Inheritance", "reusable behavior", "const withLogging = operation => value => { console.log(value); return operation(value); };\nconsole.log(withLogging(value => value * 2)(3));")],
    [("The Event Loop", "tasks and microtasks", "console.log(\"A\");\nqueueMicrotask(() => console.log(\"B\"));\nconsole.log(\"C\");"), ("Iterators and Generators", "controlled sequences", "function* ids() { yield 1; yield 2; }\nconsole.log([...ids()]);")],
    [("XSS Prevention", "safe DOM output", "const output = document.querySelector(\"#output\");\noutput.textContent = userInput;"), ("Secrets and Safe APIs", "browser security boundaries", "const publicConfig = { theme: \"dark\" };\nconsole.log(publicConfig);")],
    [("Testing Pure Functions", "deterministic checks", "const add = (a, b) => a + b;\nconsole.assert(add(2, 3) === 5);"), ("Performance and Rendering", "measure before optimizing", "const start = performance.now();\nconst elapsed = performance.now() - start;\nconsole.log(elapsed >= 0);")],
]

PROJECTS = ["Calculator", "Number Guessing Game", "Digital Clock", "Counter App", "To-Do List", "Form Validation", "Quiz Application", "Expense Tracker", "Weather Application", "Movie Search Application", "Shopping Cart", "Notes Application", "Kanban Task Board", "Analytics Dashboard", "Final JavaScript Web App"]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(title, topic, code, theory, syntax, mm, previous, next_title):
    return f"""Introduction
{title} introduces {topic} with a small, deterministic Modern JavaScript example.

Learning objectives
- Explain {topic} in your own words.
- Read and write safe, modern JavaScript for a real feature.
- Identify output, errors, and the boundary between language and browser APIs.

Prerequisites
{previous}

Detailed theory
{theory} Prefer const, narrow scopes, explicit error handling, semantic HTML, textContent for untrusted text, and small testable functions. Browser APIs are powerful but must be treated as untrusted-input boundaries.

JavaScript syntax
{syntax}

Code example
```javascript
{code}
```

Expected output
Run the example in a local JavaScript runtime or browser console. The documented example is deterministic; browser-only APIs require the matching HTML page and are not executed by this learning viewer.

Line-by-line explanation
The declarations create the values or behavior used by the example. The expression or API call performs one focused operation, and the final statement exposes a result for inspection. Read the code from the inputs to the output, then change one value and predict the result before running locally.

Common mistakes
- Using undeclared globals, confusing == with ===, or mutating data unexpectedly.
- Trusting JSON, form values, or API responses without validation.
- Using innerHTML with untrusted content or placing secrets in browser code.
- Forgetting to handle rejected promises and non-OK HTTP responses.

Best practices
Use strict equality, const-first bindings, descriptive names, small functions, safe DOM APIs, explicit HTTP status checks, and tests for important behavior. Never put private credentials in frontend JavaScript.

Practice exercises
- Easy: reproduce the example and change one input.
- Medium: add validation and handle the error path.
- Challenge: refactor the behavior into a pure function and write an assertion.
Hints: identify inputs, transformations, and outputs before coding.
Guided solution: write the smallest valid function, test a normal input, test an invalid input, then connect it to the browser only at the boundary.

Summary
You can now explain {topic}, write modern JavaScript, predict deterministic output, and identify unsafe browser boundaries.

Next lesson
{next_title}

Myanmar explanation
{mm}
"""

def _questions(title, topic):
    return [
        (f"Which practice best supports {topic}?", ["Use explicit, validated JavaScript", "Create globals everywhere", "Ignore rejected promises"], "Use explicit, validated JavaScript", "Clear boundaries and validation make JavaScript easier to reason about."),
        ("True or false: untrusted text should normally be written with textContent rather than innerHTML.", ["True", "False"], "True", "textContent does not parse the value as markup and is safer for untrusted text."),
        ("Which statement is recommended for a frontend app?", ["Never expose private API keys", "Put secrets in source code", "Assume every response is valid"], "Never expose private API keys", "Frontend source is delivered to users, so private credentials must remain server-side."),
        ("What should asynchronous code handle?", ["Rejected promises and non-OK responses", "Only the happy path", "No errors"], "Rejected promises and non-OK responses", "Reliable applications make failure behavior explicit."),
    ]

def seed_javascript_course(db, course):
    course.title = "JavaScript Programming — From Zero to Advanced"
    course.short_description = "A free Modern JavaScript course covering language foundations, browser APIs, asynchronous code, security, testing, performance, and real projects."
    course.description = "Learn JavaScript from first principles through DOM applications, async APIs, modules, object-oriented patterns, security, testing, performance, and a final web app."
    course.level, course.status, course.published = "beginner", "published", True
    course.outcomes = "Write modern JavaScript with confidence|Build interactive DOM features|Use async APIs and robust error handling|Organize code with modules|Create secure, tested, performant web applications"
    course.requirements = "Basic HTML and CSS knowledge, a text editor, and a modern browser; no previous JavaScript experience is required."
    authored = []
    for module_index, module_title in enumerate(MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_index))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_index); db.add(module); db.flush()
        module.title = module_title
        if module_index == 1:
            specs = [(title, topic, code, theory, syntax, mm) for title, topic, code, theory, syntax, mm in MODULE_ONE]
        elif module_index == 29:
            specs = [(name, "a guided JavaScript project", f"const project = \"{name}\";\nconsole.log(`${{project}} is ready to build.`);", "A real project combines a clear user flow, accessible HTML, small JavaScript functions, safe data boundaries, and tests for important behavior.", "const project = \"name\";\nconsole.log(project);", "Project တွင် user flow၊ accessible HTML၊ small functions နှင့် safe data boundary များကို ပေါင်းစပ်ပါ။") for name in PROJECTS]
        elif module_index == 30:
            specs = [("Capstone Plan and Architecture", "planning a maintainable application", "const plan = { features: [\"state\", \"validation\", \"tests\"] };\nconsole.log(plan.features.length);", "Plan the data model, UI states, error paths, security boundaries, accessibility checks, and test cases before building the final application.", "const plan = { features: [] };", "Final project မစမီ data model၊ UI states၊ error paths နှင့် tests ကို စီစဉ်ပါ။"), ("Final JavaScript Web App", "combining modern JavaScript techniques", "const app = { name: \"Learning dashboard\", status: \"ready\" };\nconsole.log(`${app.name}: ${app.status}`);", "Combine semantic HTML, safe DOM updates, validated inputs, asynchronous behavior, modules, responsive states, error handling, and a measured performance pass.", "const app = { name: \"...\", status: \"...\" };", "Capstone တွင် modern JavaScript technique များ၊ security၊ accessibility နှင့် testing ကို ပေါင်းစပ်ပါ။")]
        else:
            pair = MODULE_LESSONS[module_index - 2]
            specs = [(title, topic, code, f"This lesson explains {topic} and shows how it supports a reliable JavaScript feature.", f"Use the JavaScript feature deliberately: {topic}.", "ဒီ lesson တွင် JavaScript feature ကို အဓိပ္ပါယ်ရှိစွာ အသုံးပြုနည်းကို လေ့လာပါမည်။") for title, topic, code in pair]
        for lesson_index, (title, topic, code, theory, syntax, mm) in enumerate(specs, 1):
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm=""); db.add(lesson); db.flush()
            lesson.title, lesson.slug = title, slug
            previous = "Basic HTML and CSS knowledge is helpful; no JavaScript experience is required." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
            next_title = "Continue to the next module." if module_index == 30 else "Continue with the next lesson."
            lesson.content_en = _content(title, topic, code, theory, syntax, mm, previous, next_title)
            lesson.content_mm = f"{title} ကို English theory နှင့်အတူ လေ့လာနိုင်ပါသည်။\n\n{mm}"
            lesson.description, lesson.duration_minutes = theory, 40 if module_index == 29 else 30
            lesson.status, lesson.published = "published", True; authored.append(lesson)
            examples = list(db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all())
            example = examples[0] if examples else None
            for duplicate in examples[1:]: db.delete(duplicate)
            if not example: db.add(CodeExample(lesson_id=lesson.id, title=f"{title} example", language="javascript", filename="app.js", code=code, description="Read-only example. Copy it to a local JavaScript runtime to execute it safely.", position=1))
            else: example.title, example.language, example.filename, example.code, example.description, example.position = f"{title} example", "javascript", "app.js", code, "Read-only example. Copy it to a local JavaScript runtime to execute it safely.", 1
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz: quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the explanations and retry after studying missed concepts.", status="published"); db.add(quiz); db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(title, topic), 1):
                q = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position)); values = dict(prompt=prompt, question_type="true_false" if options == ["True", "False"] else "multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                if not q: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(q, key, value)
    course.duration_minutes = sum(x.duration_minutes or 30 for x in authored); db.flush()
