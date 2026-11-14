"""Idempotent authored Modern Python 3 curriculum."""
import json
import re
from sqlalchemy import select
from .models import CourseModule, Lesson, LessonQuiz, QuizQuestion, CodeExample

MODULES = [
    "Introduction to Python", "Python Environment Setup", "Your First Python Program", "Variables & Data Types",
    "Operators & Expressions", "Conditional Statements", "Loops & Iteration", "Functions", "Strings & Text Processing",
    "Lists & Tuples", "Sets & Dictionaries", "Python Data Structures & Algorithms", "Modules & Packages", "File Handling & Paths",
    "Error & Exception Handling", "Object-Oriented Programming", "Advanced OOP", "Iterators, Generators & Decorators",
    "Functional Python", "Type Hints & Clean Code", "Virtual Environments & Dependencies", "Debugging & Testing",
    "Python Standard Library", "Working with APIs & HTTP", "Database Programming", "Web Development with FastAPI",
    "Automation & Scripting", "Data Analysis Foundations", "Concurrency & Async Python", "Security & Performance",
    "Real-World Python Projects", "Final Capstone & Assessment",
]

MODULE_ONE = [
    ("What Is Python?", "Python's design and common uses", "message = 'Python makes ideas readable.'\nprint(message)", "Python is a high-level general-purpose language known for readable syntax and a large standard library. It is used for automation, web services, data work, education, and tooling. Readability is a design goal, but production code still needs tests, validation, and security boundaries.", "name = value\nprint(value)", "Python သည် ဖတ်ရလွယ်သော syntax နှင့် standard library ကြီးမားသော general-purpose language ဖြစ်သည်။"),
    ("Python Environment Setup", "Python 3, an editor, and the terminal", "from platform import python_version\nprint(python_version())", "Use a supported Python 3 interpreter, an editor, and a terminal. Check the interpreter with python --version. Projects should use an isolated virtual environment so dependencies do not conflict.", "python3 --version\npython3 -m venv .venv", "Python 3 interpreter၊ editor နှင့် terminal တို့ဖြင့် စတင်နိုင်သည်။ Project တစ်ခုစီအတွက် virtual environment သုံးပါ။"),
    ("Your First Python Program", "statements, indentation, and output", "name = 'CodeMaster'\nprint(f'Welcome, {name}!')", "Python executes statements in order. Indentation is syntax, not decoration, so consistent four-space indentation matters. F-strings provide readable interpolation while print sends output.", "if condition:\n    statement\nprint(f'{value}')", "Python တွင် indentation သည် syntax ၏ အစိတ်အပိုင်းဖြစ်ပြီး statements များကို အစီအစဉ်အတိုင်း run သည်။"),
    ("Comments and Readable Code", "names, comments, and formatting", "# Explain intent, not obvious syntax.\nminutes_per_lesson = 30\nprint(minutes_per_lesson)", "Use descriptive snake_case names and comments for decisions or constraints. Keep functions focused, follow a formatter when appropriate, and prefer simple code over clever code.", "# comment\nvariable_name = value", "Comment နှင့် descriptive name များကို အသုံးပြုပြီး ဖတ်ရလွယ်သော code ရေးပါ။"),
    ("The Python Runtime", "source, bytecode, and execution", "value = 2 + 3\nprint(value)", "The interpreter parses source, evaluates expressions, and reports exceptions. The standard library and third-party packages extend Python, but reading tracebacks remains a core debugging skill.", "source -> parse -> execute -> output", "Interpreter သည် source ကို parse လုပ်ပြီး execute လုပ်ကာ output သို့မဟုတ် exception ပြသည်။"),
    ("Python Files and Modules", "scripts, imports, and main guards", "def main():\n    print('Run as a script')\n\nif __name__ == '__main__':\n    main()", "A .py file can be imported as a module or run as a script. The main guard prevents script-only behavior from running unexpectedly during import and makes code easier to test.", "def main():\n    ...\nif __name__ == '__main__':", "Python file ကို module အဖြစ် import လုပ်နိုင်သလို script အဖြစ်လည်း run နိုင်သည်။"),
    ("Module 1 Review and Assessment", "a small safe Python program", "scores = [80, 92, 75]\naverage = sum(scores) / len(scores)\nprint(round(average, 2))", "This review combines names, a list, built-in functions, an expression, and deterministic output. Use clear inputs and validate data at boundaries before trusting it.", "values = [...]\nresult = function(values)\nprint(result)", "Module 1 တွင် Python syntax၊ runtime၊ files နှင့် readable code အခြေခံများကို ပြန်လည်သုံးသပ်ပါ။"),
]

# Two authored lessons for each module from environment through security.
GENERAL_LESSONS = [
    (("Install Python and an Editor", "interpreter and workspace", "from pathlib import Path\nprint(Path.cwd())"), ("Run Scripts and the REPL", "terminal workflows", "print('REPL experiment')")),
    (("Syntax, Indentation, and Blocks", "valid Python structure", "if True:\n    print('Indented block')"), ("Expressions and Statements", "evaluation order", "total = 2 * (3 + 4)\nprint(total)")),
    (("Variables and Assignment", "bindings and names", "language = 'Python'\nversion = 3\nprint(language, version)"), ("Numbers, Booleans, and None", "core value types", "ready = True\ncount = 0\nprint(ready, count, None)")),
    (("Arithmetic and Assignment Operators", "numeric expressions", "points = 10\npoints += 5\nprint(points)"), ("Comparisons and Boolean Logic", "truth values", "can_start = age >= 13 and accepted\nprint(can_start)")),
    (("if, elif, and else", "branching", "score = 82\nif score >= 80:\n    print('Strong')"), ("match and Guard Clauses", "clear decisions", "role = 'student'\nmatch role:\n    case 'student': print('Learn')\n    case _: print('Review')")),
    (("for and while Loops", "repetition", "for index in range(3):\n    print(index)"), ("Comprehensions and Loop Control", "compact transformations", "squares = [n * n for n in range(4)]\nprint(squares)")),
    (("Defining and Calling Functions", "reusable behavior", "def greet(name: str) -> str:\n    return f'Hello, {name}'\nprint(greet('Mya'))"), ("Parameters, Defaults, and Returns", "function interfaces", "def power(value, exponent=2):\n    return value ** exponent\nprint(power(3))")),
    (("String Methods and Slices", "text transformation", "title = 'Modern Python'\nprint(title.upper(), title[:6])"), ("Formatting and Regular Expressions", "structured text", "import re\nprint(bool(re.fullmatch(r'[A-Z]+', 'PYTHON')))")),
    (("Lists and Mutability", "ordered mutable data", "items = ['a', 'b']\nitems.append('c')\nprint(items)"), ("Tuples and Unpacking", "fixed records", "first, second = ('HTML', 'Python')\nprint(first, second)")),
    (("Sets and Membership", "unique values", "tags = {'python', 'api', 'python'}\nprint(len(tags))"), ("Dictionaries and Safe Access", "key-value data", "user = {'name': 'Lin'}\nprint(user.get('name', 'Guest'))")),
    (("Stacks, Queues, and Heaps", "choosing structures", "from collections import deque\nqueue = deque(['first'])\nqueue.append('second')\nprint(queue.popleft())"), ("Sorting and Searching", "algorithmic thinking", "values = [3, 1, 2]\nprint(sorted(values))")),
    (("Imports and Module Names", "reuse and namespaces", "from math import sqrt\nprint(sqrt(16))"), ("Packages and __init__", "organizing a project", "from pathlib import Path\nprint(Path('package').name)")),
    (("Reading and Writing Text Files", "safe file access", "from pathlib import Path\npath = Path('notes.txt')\npath.write_text('study', encoding='utf-8')\nprint(path.read_text(encoding='utf-8'))"), ("Paths and Directories", "portable filesystem work", "from pathlib import Path\nprint(Path.cwd().exists())")),
    (("try and except", "recovering from expected errors", "try:\n    number = int('bad')\nexcept ValueError:\n    print('Invalid number')"), ("finally and Custom Exceptions", "cleanup and domain errors", "class InvalidScoreError(ValueError):\n    pass\nprint(InvalidScoreError.__name__)")),
    (("Classes and Instances", "encapsulated state", "class Counter:\n    def __init__(self):\n        self.value = 0\ncounter = Counter()\nprint(counter.value)"), ("Properties and Dataclasses", "clear data models", "from dataclasses import dataclass\n@dataclass\nclass User:\n    name: str\nprint(User('Aye').name)")),
    (("Inheritance and Composition", "reusable object design", "class Admin:\n    def can_edit(self):\n        return True\nprint(Admin().can_edit())"), ("Protocols and Dunder Methods", "Python object behavior", "class Box:\n    def __len__(self):\n        return 3\nprint(len(Box()))")),
    (("Iterators and Generators", "lazy sequences", "def numbers():\n    yield 1\n    yield 2\nprint(list(numbers()))"), ("Decorators and Context Managers", "wrapping behavior safely", "from contextlib import contextmanager\n@contextmanager\ndef marker():\n    yield\nwith marker():\n    print('inside')")),
    (("map, filter, and zip", "functional transformations", "values = [1, 2, 3]\nprint(list(map(lambda n: n * 2, values)))"), ("Pure Functions and Callbacks", "predictable transformations", "def add(a, b):\n    return a + b\nprint(add(2, 3))")),
    (("Type Hints and Generics", "communicating intent", "def total(values: list[int]) -> int:\n    return sum(values)\nprint(total([1, 2]))"), ("Clean Code and Documentation", "maintainable interfaces", "def area(width: float, height: float) -> float:\n    '''Return rectangle area.'''\n    return width * height\nprint(area(2, 3))")),
    (("Virtual Environments", "isolated dependencies", "# python3 -m venv .venv\nprint('Use an isolated environment')"), ("Dependency Pinning", "repeatable installs", "requirements = ['fastapi==0.115.0']\nprint(requirements)")),
    (("Logging and Tracebacks", "diagnostic evidence", "import logging\nlogging.basicConfig(level=logging.INFO)\nlogging.info('started')"), ("Unit Tests with unittest", "executable checks", "import unittest\nclass TestAdd(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(2 + 3, 5)")),
    (("Collections and Itertools", "useful standard tools", "from collections import Counter\nprint(Counter('banana')['a'])"), ("Pathlib and Datetime", "portable standard-library utilities", "from datetime import date\nprint(date(2025, 1, 1).isoformat())")),
    (("HTTP Requests and JSON", "API client boundaries", "import json\npayload = json.dumps({'ok': True})\nprint(json.loads(payload)['ok'])"), ("API Status and Timeouts", "reliable network calls", "timeout_seconds = 5\nprint(timeout_seconds > 0)")),
    (("Parameterized Database Queries", "safe persistence", "query = 'SELECT * FROM users WHERE id = ?'\nprint(query)"), ("Transactions and Contexts", "durable database changes", "with open('record.txt', 'w', encoding='utf-8') as file:\n    file.write('saved')\nprint('closed safely')")),
    (("FastAPI Routes and Models", "typed web endpoints", "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/health')\ndef health():\n    return {'status': 'ok'}"), ("Request Validation", "safe API boundaries", "from pydantic import BaseModel\nclass Item(BaseModel):\n    name: str")),
    (("Automation with pathlib", "controlled file workflows", "from pathlib import Path\nfor path in Path('.').glob('*.py'):\n    print(path.name)"), ("CLI Arguments", "reusable command tools", "import argparse\nparser = argparse.ArgumentParser()\nparser.add_argument('--name')")),
    (("CSV and Tabular Data", "structured files", "import csv\nrows = [{'name': 'Aye', 'score': 90}]\nprint(rows[0]['score'])"), ("Statistics and Data Cleaning", "safe analysis inputs", "values = [10, 20, 30]\nprint(sum(values) / len(values))")),
    (("asyncio Tasks", "concurrent waiting", "import asyncio\nasync def main():\n    await asyncio.sleep(0)\n    print('ready')\nasyncio.run(main())"), ("Async Contexts and Cancellation", "reliable async services", "import asyncio\nasync def work():\n    await asyncio.sleep(0)\n    return 'done'\nprint(asyncio.run(work()))")),
    (("Input Validation and Secrets", "security boundaries", "import os\napi_key = os.environ.get('PUBLIC_DEMO_KEY')\nprint(api_key is None or isinstance(api_key, str))"), ("Performance Measurement", "measure before optimizing", "from time import perf_counter\nstart = perf_counter()\nresult = sum(range(100))\nprint(result, perf_counter() >= start)")),
]

PROJECTS = ["Personal Introduction", "Calculator", "Number Guessing Game", "Student Grade Calculator", "Unit Converter", "Password Strength Checker", "Quiz Application", "Contact Book CLI", "To-Do List CLI", "Expense Tracker", "File Organizer", "CSV Report Generator", "Library Management System", "Inventory Management CLI", "Weather API Client", "FastAPI Web API", "Authentication API Demo", "Database CRUD Application", "Automation & Reporting Tool", "Final Python Capstone"]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(title, topic, code, theory, syntax, mm, previous, next_title):
    return f"""Introduction
{title} introduces {topic} through a deterministic Modern Python 3 example.

Learning objectives
- Explain {topic} in your own words.
- Write readable Python and predict its behavior.
- Validate inputs and identify the correct failure boundary.

Prerequisites
{previous}

Detailed theory
{theory} Python's standard library provides strong building blocks, but production code still needs explicit validation, tests, dependency control, and secure handling of files, network data, and credentials.

Python syntax
{syntax}

Code example
```python
{code}
```

Expected output
Run the example locally with Python 3. The example is deterministic where it prints output; filesystem, network, and browser examples require the matching local environment and should be reviewed before execution.

Line-by-line explanation
The imports provide only the APIs used by the example. The declarations establish input or state, the central expression performs one focused operation, and the final statement exposes a result. Read the traceback from the exception type to the source line when behavior differs.

Common mistakes
- Mixing tabs and spaces or using a variable before assigning it.
- Mutating shared data unexpectedly or assuming input has the correct type.
- Catching every exception and hiding the real failure.
- Opening files, building SQL, or calling APIs without safe boundaries.

Best practices
Use four-space indentation, type hints where helpful, context managers for resources, parameterized SQL, explicit exception handling, environment-based configuration, tests, and small functions. Never put private credentials in source code.

Practice exercises
- Easy: reproduce the example and change one input.
- Medium: validate a bad input and return a useful error.
- Challenge: refactor the behavior into a tested function with a type hint.
Hints: identify inputs, transformations, outputs, and failure cases first.
Guided solution: implement the smallest valid function, test the normal path, test an invalid path, then connect it to files or services.

Summary
You can now explain {topic}, write modern Python, predict output, and choose safer boundaries for real programs.

Next lesson
{next_title}

Myanmar explanation
{mm}
"""

def _questions(title, topic):
    return [
        (f"Which practice best supports {topic}?", ["Use explicit validation and readable Python", "Catch every error silently", "Put secrets in source code"], "Use explicit validation and readable Python", "Clear boundaries and validation make Python programs easier to test and maintain."),
        ("True or false: indentation is part of Python syntax.", ["True", "False"], "True", "Indentation defines blocks in Python."),
        ("Which pattern is recommended for database values?", ["Use parameterized queries", "Build SQL with string concatenation", "Trust every input"], "Use parameterized queries", "Parameterized queries keep values separate from SQL instructions."),
        ("What should a reliable program do with expected failures?", ["Handle them explicitly", "Hide every exception", "Ignore the traceback"], "Handle them explicitly", "Explicit error handling gives users and maintainers useful information."),
    ]

def seed_python_course(db, course):
    course.title = "Python Programming — From Zero to Advanced"
    course.short_description = "A free Modern Python 3 course covering foundations, files, OOP, APIs, databases, FastAPI, async programming, security, testing, and real projects."
    course.description = "Learn Python from first principles through clean code, data structures, web APIs, database programming, FastAPI, automation, data analysis, concurrency, security, and a final capstone."
    course.level, course.status, course.published = "beginner", "published", True
    course.outcomes = "Write readable Python programs|Use core data structures and algorithms|Build tested APIs and database applications|Automate useful workflows safely|Design secure, maintainable Python projects"
    course.requirements = "Basic computer literacy, a text editor, and a terminal; no previous Python experience is required."
    authored = []
    for module_index, module_title in enumerate(MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_index))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_index); db.add(module); db.flush()
        module.title = module_title
        if module_index == 1:
            specs = MODULE_ONE
        elif module_index == 31:
            specs = [(name, "a guided Python project", f"project = {name!r}\nprint(f\"{{project}} is ready to build.\")", "A real project combines a clear user flow, validated inputs, small functions, tests, and safe handling of files or services.", "project = 'name'\nprint(project)", "Project တွင် user flow၊ validation၊ functions နှင့် tests များကို ပေါင်းစပ်ပါ။") for name in PROJECTS]
        elif module_index == 32:
            specs = [("Capstone Plan and Architecture", "planning a maintainable Python system", "plan = {'features': ['validation', 'tests', 'logging']}\nprint(len(plan['features']))", "Plan the data model, interfaces, error paths, security boundaries, tests, and deployment configuration before building the final application.", "plan = {'features': []}", "Final project မစမီ data model၊ error paths၊ security နှင့် tests ကို စီစဉ်ပါ။"), ("Final Python Capstone", "combining modern Python techniques", "app = {'name': 'Learning API', 'status': 'ready'}\nprint(f\"{app['name']}: {app['status']}\")", "Combine clean modules, typed boundaries, persistence, validation, tests, logging, security controls, and measured performance into a useful Python application.", "app = {'name': '...', 'status': '...'}", "Capstone တွင် Python techniques၊ security၊ testing နှင့် maintainability ကို ပေါင်းစပ်ပါ။")]
        else:
            pair = GENERAL_LESSONS[module_index - 2]
            specs = [(title, topic, code, f"This lesson explains {topic} and shows how it supports a reliable Python program.", f"Use the Python feature deliberately: {topic}.", "ဒီ lesson တွင် Python feature ကို အဓိပ္ပါယ်ရှိစွာ အသုံးပြုနည်းကို လေ့လာပါမည်။") for title, topic, code in pair]
        for lesson_index, (title, topic, code, theory, syntax, mm) in enumerate(specs, 1):
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm=""); db.add(lesson); db.flush()
            lesson.title, lesson.slug = title, slug
            previous = "No Python experience is required." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
            next_title = "Continue to the next module." if module_index == 32 else "Continue with the next lesson."
            lesson.content_en = _content(title, topic, code, theory, syntax, mm, previous, next_title)
            lesson.content_mm = f"{title} ကို English theory နှင့်အတူ လေ့လာနိုင်ပါသည်။\n\n{mm}"
            lesson.description, lesson.duration_minutes = theory, 40 if module_index == 31 else 30
            lesson.status, lesson.published = "published", True; authored.append(lesson)
            examples = list(db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all())
            example = examples[0] if examples else None
            for duplicate in examples[1:]: db.delete(duplicate)
            if not example: db.add(CodeExample(lesson_id=lesson.id, title=f"{title} example", language="python", filename="main.py", code=code, description="Read-only example. Copy it to a local Python 3 environment to execute it safely.", position=1))
            else: example.title, example.language, example.filename, example.code, example.description, example.position = f"{title} example", "python", "main.py", code, "Read-only example. Copy it to a local Python 3 environment to execute it safely.", 1
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz: quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the explanations and retry after studying missed concepts.", status="published"); db.add(quiz); db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(title, topic), 1):
                q = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position)); values = dict(prompt=prompt, question_type="true_false" if options == ["True", "False"] else "multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                if not q: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(q, key, value)
    course.duration_minutes = sum(x.duration_minutes or 30 for x in authored); db.flush()
