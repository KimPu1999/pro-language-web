"""Authored content for Django Module 02: Python Foundations for Django.

The module is intentionally stored as reviewable drafts.  The seed keeps the
existing module and lesson identities, updates only unpublished lessons, and
creates the missing sixth lesson additively.
"""

from __future__ import annotations

import json
from textwrap import dedent

from sqlalchemy import select

from .models import (
    CodeExample,
    CodingExercise,
    CourseModule,
    Lesson,
    LessonContentDraft,
    LessonQuiz,
    ModuleQuizDraft,
    ProjectCourseLink,
    ProjectMilestone,
    ProjectRequirement,
    ProjectRubricCriterion,
    ProjectTemplate,
    QuizQuestion,
)


MODULE_TITLE = "Python Foundations for Django"
MODULE_TITLE_MM = "Django အတွက် Python အခြေခံများ"
MODULE_DESCRIPTION = (
    "Master essential Python concepts used throughout Django development, including "
    "data structures, functions, modules, classes, packages, exception handling, "
    "type annotations, and clean code."
)
MODULE_DESCRIPTION_MM = (
    "Django development တစ်လျှောက် အသုံးများမည့် Python data structures၊ functions၊ "
    "modules၊ classes၊ packages၊ exception handling၊ type annotations နှင့် clean code "
    "အခြေခံများကို လက်တွေ့ကျွမ်းကျင်စေရန် လေ့လာမည့် module ဖြစ်သည်။"
)
OBJECTIVES = [
    "Use fundamental Python data types and structures.",
    "Write reusable functions and organize modules and packages.",
    "Design classes and objects for Django-ready code.",
    "Handle exceptions, files, and JSON safely.",
    "Add meaningful type hints and write maintainable, testable programs.",
    "Connect Python foundations to future Django lessons.",
]
OBJECTIVES_MM = [
    "Python data type နှင့် data structure များကို မှန်ကန်စွာ အသုံးပြုနိုင်ရန်။",
    "ပြန်လည်အသုံးပြုနိုင်သော function များရေးပြီး module/package များ စီမံနိုင်ရန်။",
    "Django-ready code အတွက် class နှင့် object များ ဒီဇိုင်းလုပ်နိုင်ရန်။",
    "Exception၊ file နှင့် JSON data များကို လုံခြုံစွာ ကိုင်တွယ်နိုင်ရန်။",
    "အဓိပ္ပာယ်ရှိသော type hint များထည့်ပြီး ထိန်းသိမ်းရလွယ်ကူသော testable code ရေးနိုင်ရန်။",
    "Python အခြေခံများကို နောက်လာမည့် Django lesson များနှင့် ချိတ်ဆက်နိုင်ရန်။",
]


def _example(title, code, output, input_text, explanation, relevance, explanation_mm, relevance_mm):
    return {
        "title": title,
        "code": dedent(code).strip(),
        "output": output,
        "input": input_text,
        "explanation": explanation,
        "relevance": relevance,
        "explanation_mm": explanation_mm,
        "relevance_mm": relevance_mm,
    }


LESSONS = [
    {
        "title": "Python Fundamentals for Django",
        "topic": "variables, data types, control flow, collections, strings, and comprehensions",
        "description": "Review the Python syntax and data structures that Django views, forms, and services use every day.",
        "syntax": "value = expression\nif condition:\n    action()\nfor item in items:\n    process(item)\n{key: value for key, value in pairs}",
        "theory": (
            "Python gives Django developers a small set of composable primitives: values, names, "
            "conditions, loops, functions, and collections. A view receives request data, validates "
            "it, transforms it with these primitives, and passes safe values to a template or response. "
            "Lists preserve order, tuples communicate fixed groups, sets remove duplicates, and dictionaries "
            "represent named fields. Truthiness is useful, but explicit comparisons are clearer at validation boundaries."
        ),
        "theory_mm": (
            "Python သည် Django developer များနေ့စဉ်အသုံးပြုရသော value၊ name၊ condition၊ loop၊ "
            "function နှင့် collection အခြေခံများကို ပေါင်းစပ်အသုံးပြုနိုင်စေသည်။ View သည် request data ကို "
            "လက်ခံ၊ validate လုပ်ပြီး template သို့မဟုတ် response သို့ မပို့မီ ဤအခြေခံများဖြင့် ပြောင်းလဲစီမံသည်။ "
            "List သည် order ကို ထိန်းသည်၊ tuple သည် မပြောင်းလဲသင့်သော group ကို ဖော်ပြသည်၊ set သည် duplicate ဖယ်သည်၊ "
            "dictionary သည် အမည်ပါ field များကို ကိုယ်စားပြုသည်။ Validation boundary တွင် explicit comparison သည် ပိုရှင်းလင်းသည်။"
        ),
        "mistakes": [
            "Mixing strings and numbers without explicit conversion.",
            "Mutating a list while iterating over it.",
            "Using a dictionary key that may not exist without get() or validation.",
            "Putting business rules in a template instead of Python code.",
        ],
        "mistakes_mm": [
            "String နှင့် number ကို conversion မလုပ်ဘဲ တိုက်ရိုက်ပေါင်းခြင်း။",
            "Loop လုပ်နေစဉ် list ကို တစ်ပြိုင်နက် ပြင်ဆင်ခြင်း။",
            "မရှိနိုင်သော dictionary key ကို get() သို့မဟုတ် validation မပါဘဲ သုံးခြင်း။",
            "Business rule ကို Python အစား template ထဲတွင် ထည့်ခြင်း။",
        ],
        "best_practices": "Name values clearly, validate at the boundary, prefer small transformations, and keep templates focused on presentation.",
        "best_practices_mm": "Value name များကို ရှင်းလင်းစွာပေးပါ၊ boundary တွင် validate လုပ်ပါ၊ transformation များကို သေးငယ်စွာ ခွဲပြီး template ကို presentation အတွက်သာ ထားပါ။",
        "examples": [
            _example("Student name and age", """
                student_name = "Mya"
                student_age = 20
                is_adult = student_age >= 18
                print(f"{student_name} is {student_age}: adult={is_adult}")
            """, "Mya is 20: adult=True", "student_name and student_age are assigned in the program.", "Names hold values and the comparison produces a boolean.", "Django forms and serializers normalize named input fields in the same way.", "Name နှင့် အသက်ကို variable ထဲသိမ်းပြီး အသက် ၁၈ နှစ်ပြည့်/မပြည့် စစ်သည်။", "Django form နှင့် serializer များသည် named input field များကို ဤပုံစံဖြင့် စီမံသည်."),
            _example("Student grade calculation", """
                scores = [82, 74, 91]
                average = sum(scores) / len(scores)
                if average >= 80:
                    grade = "A"
                elif average >= 60:
                    grade = "B"
                else:
                    grade = "C"
                print(round(average, 2), grade)
            """, "82.33 A", "The scores list is the input.", "sum() and len() produce the average; the ordered branches choose a grade.", "A Django service can apply the same rule before saving a result.", "scores list ထဲက စုစုပေါင်းနှင့် item အရေအတွက်ဖြင့် average တွက်ပြီး grade ခွဲသည်။", "Django service တွင် result မသိမ်းမီ ဤ rule ကို အသုံးပြုနိုင်သည်."),
            _example("Student list processing", """
                students = ["Aye", "Bo", "Su"]
                passed = []
                for name, score in zip(students, [88, 55, 76]):
                    if score >= 60:
                        passed.append({"name": name, "score": score})
                print(passed)
            """, "[{'name': 'Aye', 'score': 88}, {'name': 'Su', 'score': 76}]", "Three names and three scores are paired by zip().", "The loop creates a new dictionary only for passing students.", "Query results are often converted into safe response dictionaries before rendering.", "Student နှင့် score ကို zip ဖြင့်တွဲပြီး အောင်မြင်သူများကို dictionary အဖြစ် စုသည်။", "Query result များကို response dictionary အဖြစ် ပြောင်းရာတွင် ဤ pattern ကို သုံးနိုင်သည်."),
            _example("Student dictionary records", """
                student = {"id": 7, "name": "Lin", "courses": ["Python", "Django"]}
                student["active"] = True
                print(student.get("email", "not provided"))
            """, "not provided", "The student dictionary is the input.", "get() supplies a safe default when the optional email key is absent.", "Optional request fields should have explicit defaults before they reach a template.", "Student record dictionary ထဲတွင် field ထည့်ပြီး မရှိသေးသော email ကို default ဖြင့် ဖတ်သည်။", "Optional request field များကို template မပို့မီ default သတ်မှတ်သင့်သည်."),
            _example("Filtering passed students", """
                records = [{"name": "Aye", "score": 88}, {"name": "Bo", "score": 55}]
                passed_names = [row["name"] for row in records if row["score"] >= 60]
                print(passed_names)
            """, "['Aye']", "records contains dictionaries with name and score.", "The comprehension reads each record and keeps names meeting the condition.", "List comprehensions are useful for small, readable display transformations in services.", "Comprehension ဖြင့် score သတ်မှတ်ချက်ပြည့်သူများ၏ name ကို ရွေးသည်။", "Service layer တွင် display အတွက် တိုတောင်းရှင်းလင်းသော transformation အဖြစ် သုံးနိုင်သည်."),
        ],
        "exercises": "1. Store and validate a student record.\n2. Calculate a grade from five scores.\n3. Find the highest score without sorting away the original list.\n4. Filter passed students into dictionaries.\n5. Build a summary containing count, average, highest score, and passed names.",
        "exercises_mm": "၁။ Student record တစ်ခုသိမ်းပြီး validate လုပ်ပါ။\n၂။ Score ငါးခုမှ grade တွက်ပါ။\n၃။ မူရင်း list မပျက်စေဘဲ အမြင့်ဆုံး score ရှာပါ။\n၄။ အောင်မြင်သူများကို dictionary အဖြစ် filter လုပ်ပါ။\n၅။ count၊ average၊ highest score နှင့် passed names ပါသော summary တည်ဆောက်ပါ။",
        "homework": "Student Grade Calculator: accept validated student names and scores, print a summary, and add tests for empty input, invalid scores, and a passing boundary of 60.",
        "homework_mm": "Student Grade Calculator တည်ဆောက်ပါ။ Student name နှင့် score များကို validate လုပ်ပြီး summary ပြပါ။ Empty input၊ မမှန်ကန်သော score နှင့် passing boundary 60 အတွက် test ရေးပါ။",
        "summary": "Python values and collections become predictable Django input transformations when validation and clear boundaries are kept explicit.",
        "summary_mm": "Validation နှင့် boundary ကို ရှင်းလင်းစွာထားပါက Python value နှင့် collection များသည် Django input transformation အဖြစ် ယုံကြည်စိတ်ချစွာ အသုံးပြုနိုင်သည်။",
        "quiz": [
            ("Which collection maps keys to values?", ["dict", "tuple", "set", "range"], "dict", "Dictionaries represent named fields."),
            ("What does len(scores) return?", ["The number of items", "The largest item", "A sorted list", "A boolean"], "The number of items", "len() returns the number of items."),
            ("Which operator tests equality?", ["==", "=", "!=", ":="], "==", "A single equals sign assigns; double equals compares."),
            ("True or false: a tuple is normally used for an ordered fixed group.", ["True", "False"], "True", "Tuples communicate an ordered group that should not be mutated."),
            ("What does a list comprehension create?", ["A new list", "A database table", "A function only", "A file"], "A new list", "The expression creates a list from an iterable and optional condition."),
            ("Why use int(value) at an input boundary?", ["To convert validated text to an integer", "To encrypt a value", "To sort a database", "To publish a page"], "To convert validated text to an integer", "Browser form values commonly arrive as text."),
            ("Which approach avoids a KeyError for an optional dictionary key?", ["record.get('email')", "record.email", "record->email", "record[missing]"], "record.get('email')", "get() can provide a default for a missing key."),
            ("What should a Django template primarily do?", ["Present trusted context", "Own database writes", "Validate passwords", "Run migrations"], "Present trusted context", "Application code owns business rules and persistence."),
        ],
    },
    {
        "title": "Functions, Parameters, Returns and Modules",
        "topic": "reusable functions, scope, annotations, docstrings, imports, and Django views",
        "description": "Learn to turn repeated logic into tested functions and small importable modules before using it in Django views.",
        "syntax": "def name(value: Type = default) -> ReturnType:\n    \"\"\"Document the contract.\"\"\"\n    return result\n\nfrom package.module import helper",
        "theory": "A function is a named contract: it receives inputs, performs one responsibility, and returns a result or deliberately raises an error. Parameters should be named for intent, defaults should be safe, and docstrings should state behavior. Local variables are safer than accidental globals. Modules provide import boundaries; a Django view should remain a thin request adapter that calls reusable service functions.",
        "theory_mm": "Function သည် input လက်ခံပြီး တာဝန်တစ်ခုကို ဆောင်ရွက်ကာ result ပြန်ပေးသော အမည်တပ်ထားသည့် contract ဖြစ်သည်။ Parameter များကို အဓိပ္ပာယ်ရှိစွာ အမည်ပေးပြီး default ကို လုံခြုံစွာ သတ်မှတ်ပါ။ Docstring တွင် လုပ်ဆောင်ပုံကို ရှင်းပြပါ။ Module သည် import boundary ဖြစ်ပြီး Django view သည် request adapter အဖြစ် service function ကို ခေါ်သင့်သည်။",
        "mistakes": ["Forgetting to return a computed value.", "Using mutable default arguments.", "Importing a module only for side effects.", "Putting all validation and database work directly in a view."],
        "mistakes_mm": ["တွက်ထားသော value ကို return မလုပ်ခြင်း။", "Mutable default argument အသုံးပြုခြင်း။", "Side effect အတွက်သာ module import လုပ်ခြင်း။", "Validation နှင့် database work အားလုံးကို view ထဲ တိုက်ရိုက်ထည့်ခြင်း။"],
        "best_practices": "Keep functions small, type-annotate public boundaries, test return values, and let views coordinate rather than contain every rule.",
        "best_practices_mm": "Function ကို သေးငယ်စွာထားပါ၊ public boundary များတွင် type hint ထည့်ပါ၊ return value ကို test လုပ်ပြီး view ကို coordination အတွက်သာ သုံးပါ။",
        "examples": [
            _example("Greeting function", """
                def greeting(name: str, punctuation: str = "!") -> str:
                    return f"Hello, {name}{punctuation}"

                print(greeting("Mya"))
            """, "Hello, Mya!", "The caller supplies the name and uses the safe punctuation default.", "The annotation describes the contract; the default keeps the common call short.", "A view can call a greeting helper without knowing how the string is assembled.", "name နှင့် punctuation parameter များပါသော function သည် string ပြန်ပေးသည်။", "View သည် string တည်ဆောက်ပုံမသိဘဲ helper ကို ခေါ်နိုင်သည်."),
            _example("Calculate student average", """
                def average(scores: list[float]) -> float:
                    if not scores:
                        raise ValueError("scores cannot be empty")
                    return sum(scores) / len(scores)

                print(round(average([70, 80, 90]), 2))
            """, "80.0", "The function receives a non-empty list of numbers.", "The guard prevents division by zero and makes the error contract explicit.", "A service can reject invalid enrollment results before persistence.", "Empty list ဖြစ်ပါက ValueError ပြန်ပြီး score များမှ average တွက်သည်။", "Persistence မလုပ်မီ invalid enrollment result ကို service က ပယ်ချနိုင်သည်."),
            _example("Student grade classification", """
                def classify(score: int) -> str:
                    if not 0 <= score <= 100:
                        raise ValueError("score must be between 0 and 100")
                    return "pass" if score >= 60 else "retry"

                print(classify(76))
            """, "pass", "score is the function input.", "Validation runs before the conditional expression chooses the result.", "A form may validate shape while the service enforces the domain range.", "Score 0 မှ 100 အတွင်းရှိ/မရှိ စစ်ပြီး pass သို့မဟုတ် retry ပြန်ပေးသည်။", "Form validation ရှိသော်လည်း domain range ကို service တွင် ထပ်စစ်သင့်သည်."),
            _example("Reusable student utility module", """
                # student_utils.py
                def passed_names(records: list[dict[str, int | str]]) -> list[str]:
                    return [row["name"] for row in records if int(row["score"]) >= 60]

                # main.py
                from student_utils import passed_names
                print(passed_names([{"name": "Aye", "score": 80}]))
            """, "['Aye']", "main.py imports passed_names from student_utils.py.", "The utility owns the transformation and the caller supplies data.", "Small utility modules can be unit-tested without starting Django.", "student_utils.py ထဲမှ function ကို main.py က import လုပ်ပြီး student data ပြောင်းသည်။", "Django server မစဘဲ utility module ကို သီးခြား test လုပ်နိုင်သည်."),
            _example("Simple Django view function", """
                from django.http import JsonResponse

                def health(request):
                    return JsonResponse({"status": "ok"})
            """, "GET /health returns {\"status\": \"ok\"} with HTTP 200.", "Django supplies request when the URL invokes the view.", "The view has one job: adapt the framework request to a response.", "Thin views are easier to authorize, test, and replace with a class-based view later.", "Django က request ကို ပေးသောအခါ JSON response ပြန်သည့် health view ဖြစ်သည်။", "View ကို သေးငယ်စွာထားလျှင် authorization နှင့် test လုပ်ရန် ပိုလွယ်သည်."),
        ],
        "exercises": "1. Write calculator functions with validation.\n2. Create a grade helper with type annotations.\n3. Build a reusable student_utils.py module.\n4. Import a custom module from main.py.\n5. Refactor repeated view logic into a service function and test it without Django.",
        "exercises_mm": "၁။ Validation ပါသော calculator function များရေးပါ။\n၂။ Type annotation ပါသော grade helper တည်ဆောက်ပါ။\n၃။ student_utils.py reusable module တည်ဆောက်ပါ။\n၄။ main.py မှ custom module import လုပ်ပါ။\n၅။ View ထဲက ထပ်နေသော logic ကို service function သို့ရွှေ့ပြီး Django မစဘဲ test လုပ်ပါ။",
        "homework": "Student Utility Library: create average, classify, validate, and summarize functions in a module, document their contracts, and write unit tests for normal and invalid inputs.",
        "homework_mm": "Student Utility Library တည်ဆောက်ပါ။ average၊ classify၊ validate နှင့် summarize function များကို module ထဲရေး၊ contract ကို docstring ဖြင့် ရှင်းပြပြီး valid/invalid input test များရေးပါ။",
        "summary": "Functions and modules give Django code reusable boundaries; views should connect framework input to those boundaries.",
        "summary_mm": "Function နှင့် module များသည် Django code အတွက် ပြန်လည်အသုံးပြုနိုင်သော boundary ပေးပြီး view သည် framework input ကို ထို boundary နှင့် ချိတ်ပေးရသည်။",
        "quiz": [
            ("What does return do?", ["Sends a value back to the caller", "Installs Django", "Creates a class automatically", "Deletes a variable"], "Sends a value back to the caller", "return ends the call and provides its result."),
            ("Why annotate a function?", ["To communicate its expected contract", "To encrypt arguments", "To run it twice", "To replace tests"], "To communicate its expected contract", "Annotations improve readability and tool support; they are not automatic runtime validation."),
            ("What is a module?", ["An importable Python file", "Only a database row", "A browser tab", "A CSS selector"], "An importable Python file", "A module provides a named import boundary."),
            ("True or false: a Django view must return an HTTP response.", ["True", "False"], "True", "Django dispatch expects a response-producing view."),
            ("What is a safe default argument?", ["One that does not share mutable state unexpectedly", "A password in source code", "A random global", "An unvalidated request"], "One that does not share mutable state unexpectedly", "Mutable defaults can leak state between calls."),
            ("Which import is explicit?", ["from student_utils import passed_names", "import *", "run everything", "load all files"], "from student_utils import passed_names", "Explicit imports make dependencies visible."),
            ("Where should reusable domain validation normally live?", ["A service or domain function", "Only in CSS", "A hidden button", "A log message"], "A service or domain function", "The server-side domain boundary must be testable and authoritative."),
            ("What does a docstring describe?", ["A function or module contract", "A database password", "A compiled binary", "A network route only"], "A function or module contract", "Docstrings communicate intended use and behavior."),
        ],
    },
    {
        "title": "Object-Oriented Programming for Django",
        "topic": "classes, objects, methods, properties, inheritance, composition, and Django models",
        "description": "Understand plain Python objects before connecting object-oriented design to Django models and class-based views.",
        "syntax": "class Student:\n    def __init__(self, name: str) -> None:\n        self.name = name\n\n    def summary(self) -> str:\n        return self.name",
        "theory": "A class defines behavior and data shape; an object is one instance created from that definition. Instance attributes belong to one object, class attributes are shared, and methods express operations. Composition is often safer than deep inheritance because a service can contain a validator or repository without pretending to be one. A plain Python object exists in memory only. A Django model is a framework-managed class whose instances can be persisted through the ORM; defining a class alone never writes a database row.",
        "theory_mm": "Class သည် data shape နှင့် behavior ကို သတ်မှတ်ပြီး object သည် ထို class မှ ဖန်တီးသော instance တစ်ခုဖြစ်သည်။ Instance attribute သည် object တစ်ခုအတွက်သာ ဖြစ်ပြီး class attribute သည် မျှဝေသုံးသည်။ Deep inheritance ထက် composition သည် မကြာခဏ ပိုလုံခြုံသည်။ Plain Python object သည် memory ထဲတွင်သာ ရှိပြီး database မသိမ်းပါ။ Django model သည် ORM က စီမံသော class ဖြစ်သောကြောင့် save() နှင့် migration စနစ်ဖြင့်သာ persistence ရသည်။",
        "mistakes": ["Confusing a class definition with a saved database row.", "Forgetting self on instance methods.", "Sharing mutable class state between students.", "Using inheritance where composition is clearer."],
        "mistakes_mm": ["Class definition ကို database row အဖြစ် မှားယွင်းယူဆခြင်း။", "Instance method တွင် self မထည့်ခြင်း။", "Mutable class state ကို student အားလုံး မျှဝေသုံးခြင်း။", "Composition ပိုရှင်းသည့်နေရာတွင် inheritance သုံးခြင်း။"],
        "best_practices": "Give objects one cohesive responsibility, keep state private through properties where useful, and test plain objects independently from Django.",
        "best_practices_mm": "Object တစ်ခုစီတွင် တာဝန်တစ်ခုကိုသာ ထားပါ၊ လိုအပ်ပါက property ဖြင့် state ကို ထိန်းပါ၊ plain object ကို Django နှင့် မချိတ်မီ သီးခြား test လုပ်ပါ။",
        "examples": [
            _example("Create a Student class", """
                class Student:
                    def __init__(self, student_id: int, name: str) -> None:
                        self.student_id = student_id
                        self.name = name

                student = Student(7, "Mya")
                print(student.name)
            """, "Mya", "The constructor receives an id and name.", "__init__ stores instance attributes on this particular object.", "A service can pass a plain Student object between validation and formatting steps.", "Student class နှင့် object တစ်ခုဖန်တီးပြီး name ကို ဖတ်သည်။", "Validation နှင့် formatting အဆင့်များအကြား plain object ကို ပို့နိုင်သည်."),
            _example("Student methods", """
                class Student:
                    def __init__(self, scores: list[int]) -> None:
                        self.scores = scores

                    def average(self) -> float:
                        return sum(self.scores) / len(self.scores)

                print(round(Student([70, 90]).average(), 1))
            """, "80.0", "The object is initialized with two scores.", "The method reads object state through self and returns a calculation.", "Encapsulated calculations can be reused by a Django service and tested without a database.", "Object ၏ score များမှ method ဖြင့် average တွက်သည်။", "Database မလိုဘဲ Django service တွင် ပြန်သုံး၍ test လုပ်နိုင်သည်."),
            _example("Teacher and Student classes", """
                class Person:
                    def __init__(self, name: str) -> None:
                        self.name = name

                class Teacher(Person):
                    role = "teacher"

                class Student(Person):
                    role = "student"

                print(Teacher("Ko").role, Student("Su").role)
            """, "teacher student", "Both objects receive a name from the base class.", "Inheritance reuses the common constructor while each subclass supplies a role.", "Use inheritance for a genuine is-a relationship with stable shared behavior.", "Teacher နှင့် Student သည် Person မှ name constructor ကို အမွေဆက်ခံပြီး role ခွဲသည်။", "အမှန်တကယ် is-a relationship ရှိသည့်အခါ inheritance သုံးပါ."),
            _example("Composition and overrides", """
                class GradePolicy:
                    def passed(self, score: int) -> bool:
                        return score >= 60

                class StudentService:
                    def __init__(self, policy: GradePolicy) -> None:
                        self.policy = policy

                    def can_progress(self, score: int) -> bool:
                        return self.policy.passed(score)

                print(StudentService(GradePolicy()).can_progress(72))
            """, "True", "StudentService receives a GradePolicy object.", "Composition delegates the rule instead of hardcoding it inside the service.", "Django services can receive repositories, validators, or policies as dependencies for testing.", "StudentService ထဲသို့ GradePolicy object ထည့်ပြီး rule ကို delegate လုပ်သည်။", "Django service တွင် repository/validator/policy ကို dependency အဖြစ် ထည့်ပြီး test လုပ်နိုင်သည်."),
            _example("Django model class boundary", """
                from django.db import models

                class Course(models.Model):
                    title = models.CharField(max_length=180)

                # Course.objects.create(title="Python") persists through the ORM.
            """, "The model definition describes a database table; persistence requires migrations and ORM calls.", "The model class is declared in an installed Django app.", "The class declaration alone does not create a row; migrations and a database operation are required.", "This distinction prevents learners from treating an in-memory object as saved data.", "Django model class သည် table ပုံစံကို သတ်မှတ်ပေးပြီး class ရေးရုံဖြင့် row မသိမ်းပါ။", "Migration နှင့် ORM operation လုပ်မှသာ database persistence ဖြစ်သည်."),
        ],
        "exercises": "1. Create a Student class with constructor and summary method.\n2. Add score validation and an average property.\n3. Model Course and Enrollment as plain objects.\n4. Implement a policy using composition.\n5. Explain which part would become a Django model and which part remains a service.",
        "exercises_mm": "၁။ Constructor နှင့် summary method ပါသော Student class တည်ဆောက်ပါ။\n၂။ Score validation နှင့် average property ထည့်ပါ။\n၃။ Course နှင့် Enrollment ကို plain object အဖြစ် model လုပ်ပါ။\n၄။ Composition သုံးသော policy တည်ဆောက်ပါ။\n၅။ Django model ဖြစ်မည့်အပိုင်းနှင့် service ဖြစ်မည့်အပိုင်းကို ခွဲရှင်းပါ။",
        "homework": "Object-Oriented Student Management System: implement Student, Course, and Enrollment objects, add validation, and write tests that prove objects are not persisted until an explicit repository or ORM operation runs.",
        "homework_mm": "Object-Oriented Student Management System တည်ဆောက်ပါ။ Student၊ Course နှင့် Enrollment object များ၊ validation နှင့် test များရေးပါ။ Explicit repository သို့မဟုတ် ORM operation မလုပ်မချင်း object များ database မသိမ်းကြောင်း စစ်ပါ။",
        "summary": "Object-oriented design clarifies state and behavior, while Django models add persistence as a separate framework responsibility.",
        "summary_mm": "Object-oriented design သည် state နှင့် behavior ကို ရှင်းလင်းစေပြီး Django model သည် framework persistence တာဝန်ကို ထပ်ပေးသည်။",
        "quiz": [
            ("What is an object?", ["An instance of a class", "Only a database schema", "A URL pattern", "A template filter"], "An instance of a class", "Objects are created from class definitions."),
            ("What does self refer to?", ["The current instance", "The database server", "The parent module", "The URLconf"], "The current instance", "self gives an instance method access to its object."),
            ("What does __init__ commonly do?", ["Initialize instance state", "Run migrations automatically", "Publish a course", "Render CSS"], "Initialize instance state", "The initializer assigns starting values."),
            ("True or false: defining a plain Python class saves a database row.", ["True", "False"], "False", "Persistence requires an explicit storage operation."),
            ("When is composition useful?", ["When one object uses another collaborator", "Only for CSS", "To avoid all tests", "To replace constructors"], "When one object uses another collaborator", "Composition makes dependencies explicit."),
            ("What adds ORM persistence to a Django model?", ["Migrations and ORM operations", "A class name alone", "A template comment", "A browser refresh"], "Migrations and ORM operations", "The database schema and write operation are separate steps."),
            ("What is a class attribute?", ["A value shared through the class", "Always a database row", "A request body", "A module import"], "A value shared through the class", "Class attributes can be shared by instances."),
            ("Why test plain domain objects separately?", ["To get fast feedback without framework or database setup", "To bypass all validation", "To make secrets public", "To delete migrations"], "To get fast feedback without framework or database setup", "Small isolated tests reveal domain errors quickly."),
        ],
    },
    {
        "title": "Modules, Packages and Project Organization",
        "topic": "module boundaries, packages, imports, dependency isolation, and Django app structure",
        "description": "Organize Python code into importable modules and packages that keep Django apps maintainable and testable.",
        "syntax": "package/\n    __init__.py\n    services.py\nfrom package.services import function\nfrom .validators import validate",
        "theory": "A module is an importable Python file; a package is a directory that groups modules under one namespace. Explicit absolute imports are easy to read across an application, while relative imports are useful inside a cohesive package. Keep dependency direction intentional: views may call services, services may call repositories, and low-level utilities should not import the web layer. Virtual environments and requirements files isolate dependencies; they do not replace a clear code boundary. Django projects contain configuration, while apps contain cohesive domain code.",
        "theory_mm": "Module သည် import လုပ်နိုင်သော Python file ဖြစ်ပြီး package သည် module များကို namespace တစ်ခုအောက်တွင် စုစည်းထားသော directory ဖြစ်သည်။ Application အတွင်း absolute import သည် ဖတ်ရလွယ်ပြီး package အတွင်း cohesive code ကို relative import ဖြင့် ချိတ်နိုင်သည်။ View က service ကို ခေါ်ပြီး service က repository ကို ခေါ်သည့် dependency direction ကို ထိန်းပါ။ Virtual environment နှင့် requirements file သည် dependency isolation အတွက်ဖြစ်ပြီး code boundary ကို အစားမထိုးပါ။",
        "mistakes": ["Using import * and hiding dependencies.", "Creating circular imports between services and views.", "Putting unrelated domains in one giant module.", "Assuming a virtual environment fixes poor package design."],
        "mistakes_mm": ["import * သုံးပြီး dependency မမြင်ရခြင်း။", "Service နှင့် view အချင်းချင်း circular import ဖြစ်ခြင်း။", "မဆိုင်သော domain များကို module ကြီးတစ်ခုထဲ ထည့်ခြင်း။", "Virtual environment ရှိရုံဖြင့် package design ကောင်းမည်ဟု ယူဆခြင်း။"],
        "best_practices": "Use explicit imports, cohesive modules, one-direction dependencies, package-level tests, and a documented project tree.",
        "best_practices_mm": "Explicit import၊ cohesive module၊ direction တစ်ဖက်တည်းသော dependency၊ package-level test နှင့် ရှင်းလင်းသော project tree ကို သုံးပါ။",
        "examples": [
            _example("Import the standard library", """
                from pathlib import Path

                project_root = Path("student_toolkit")
                print(project_root.name)
            """, "student_toolkit", "The code imports Path from the standard library.", "A Path object models a filesystem path without string concatenation.", "Django settings, uploads, and management commands benefit from explicit path handling.", "Standard library ထဲမှ pathlib.Path ကို import လုပ်ပြီး project folder name ဖတ်သည်။", "Django settings နှင့် upload path များတွင် path handling ကို ရှင်းလင်းစေသည်."),
            _example("Create a custom module", """
                # grades.py
                def passed(score: int) -> bool:
                    return score >= 60

                # main.py
                from grades import passed
                print(passed(75))
            """, "True", "main.py imports passed from the sibling grades.py module.", "The module owns one reusable domain rule.", "A Django app can place validation and service rules in modules instead of a large views.py.", "grades.py မှ passed function ကို main.py က import လုပ်သည်။", "Django app တွင် validation နှင့် service rule များကို views.py ကြီးထဲမထည့်ဘဲ module ခွဲနိုင်သည်."),
            _example("Create a Python package", """
                # student_toolkit/__init__.py
                # student_toolkit/validators.py
                def valid_age(age: int) -> bool:
                    return 0 < age < 130

                # main.py
                from student_toolkit.validators import valid_age
                print(valid_age(20))
            """, "True", "The package directory contains __init__.py and validators.py.", "The dotted import resolves a module inside the package namespace.", "Packages make a growing Django app easier to navigate and review.", "Package directory ထဲတွင် __init__.py နှင့် validators.py ထားပြီး dotted import သုံးသည်။", "Django app ကြီးလာသောအခါ package ခွဲခြင်းဖြင့် စီမံရန်လွယ်သည်."),
            _example("Import student utilities", """
                # student_toolkit/services.py
                def summary(name: str, score: int) -> str:
                    return f"{name}: {score}"

                # main.py
                from student_toolkit.services import summary
                print(summary("Aye", 88))
            """, "Aye: 88", "main.py calls the explicitly imported service function.", "The service exposes a small contract and does not know about the CLI or web layer.", "The same service can be called by a Django view, a command, or a test.", "Service function သည် CLI/web layer ကို မသိဘဲ summary ပြန်ပေးပြီး main.py က ခေါ်သည်။", "Django view၊ command နှင့် test သုံးခုလုံးမှ ပြန်သုံးနိုင်သည်."),
            _example("Organize Django-ready service code", """
                # learning/services/enrollment.py
                def can_enroll(age: int, capacity: int) -> bool:
                    return age >= 13 and capacity > 0

                # learning/views.py
                from learning.services.enrollment import can_enroll
                print(can_enroll(20, 3))
            """, "True", "The view imports a service from a focused subpackage.", "The service has no request or database dependency in this small example.", "Keeping domain decisions in services makes authorization and tests more deliberate.", "Django app ထဲတွင် enrollment service ကို subpackage ခွဲပြီး view က import လုပ်သည်။", "Domain decision ကို service ထဲထားခြင်းဖြင့် authorization နှင့် test ပိုရှင်းသည်."),
        ],
        "exercises": "1. Create a grades.py module.\n2. Build a student_toolkit package with validators and services.\n3. Move repeated functions out of main.py.\n4. Fix an intentional circular import by reversing the dependency direction.\n5. Write package tests and document each module's public functions.",
        "exercises_mm": "၁။ grades.py module တည်ဆောက်ပါ။\n၂။ validators နှင့် services ပါသော student_toolkit package တည်ဆောက်ပါ။\n၃။ main.py ထဲက ထပ်နေသော function များကို ရွှေ့ပါ။\n၄။ Circular import တစ်ခုကို dependency direction ပြန်စီပြီး ပြင်ပါ။\n၅။ Package test များရေးပြီး module တစ်ခုစီ၏ public function များကို မှတ်တမ်းတင်ပါ။",
        "homework": "Student Management Package Architecture: deliver the requested student_toolkit tree with imports, validators, services, storage boundary, tests, and a short dependency diagram.",
        "homework_mm": "Student Management Package Architecture တည်ဆောက်ပါ။ student_toolkit tree၊ import၊ validator၊ service၊ storage boundary နှင့် test များပါစေ။ Dependency diagram တိုတောင်းတစ်ခု ထည့်ပါ။",
        "summary": "Good package boundaries make Django code easier to import, test, review, and change without circular dependencies.",
        "summary_mm": "ကောင်းမွန်သော package boundary များသည် Django code ကို import၊ test၊ review နှင့် ပြင်ဆင်ရန် လွယ်ကူစေပြီး circular dependency ကို လျှော့ချပေးသည်။",
        "quiz": [
            ("What is a package?", ["A namespace grouping modules", "A database backup", "A template block", "A HTTP status"], "A namespace grouping modules", "Packages organize importable modules."),
            ("Why use explicit imports?", ["They make dependencies visible", "They disable tests", "They create a database", "They hide all names"], "They make dependencies visible", "Explicit imports improve reviewability."),
            ("What commonly causes a circular import?", ["Two modules importing each other during initialization", "A list comprehension", "A CSS file", "A database index"], "Two modules importing each other during initialization", "Circular imports arise from dependency cycles."),
            ("True or false: a virtual environment replaces package design.", ["True", "False"], "False", "Environment isolation and code organization solve different problems."),
            ("Where should a Django app's domain service live?", ["A focused service module", "Only in a template", "A browser cookie", "A migration filename"], "A focused service module", "Services provide a testable domain boundary."),
            ("What file commonly marks a traditional package?", ["__init__.py", "README.css", "manage.lock", "route.json"], "__init__.py", "__init__.py establishes package initialization in the conventional layout."),
            ("What should low-level utilities avoid importing?", ["The web layer when it creates a dependency cycle", "The standard library", "Their own types", "A test module"], "The web layer when it creates a dependency cycle", "Dependencies should point toward stable lower-level code."),
            ("What does requirements.txt primarily describe?", ["Project dependencies", "Student grades", "URL routes", "HTML headings"], "Project dependencies", "Dependency files record packages and compatible versions."),
        ],
    },
    {
        "title": "Error Handling, Files and JSON",
        "topic": "specific exceptions, context managers, pathlib, JSON, safe paths, and logging",
        "description": "Handle failures deliberately and use files or JSON as a safe learning boundary without confusing them with production database storage.",
        "syntax": "try:\n    value = operation()\nexcept SpecificError as exc:\n    recover(exc)\nelse:\n    use(value)\nfinally:\n    cleanup()\n\nwith path.open(encoding=\"utf-8\") as handle:\n    text = handle.read()",
        "theory": "Exceptions communicate that an operation could not complete normally. Catch the narrowest expected exception, recover or translate it at the correct boundary, and preserve useful context through logging or exception chaining. Context managers close files even when code fails. pathlib makes path operations explicit. JSON is excellent for a small learning project and interchange, but concurrent production writes, indexing, and transactions belong in a database. Never allow unvalidated user input to choose arbitrary filesystem paths.",
        "theory_mm": "Exception သည် operation တစ်ခု ပုံမှန်မပြီးဆုံးနိုင်ကြောင်း ဖော်ပြသည်။ မျှော်လင့်ထားသော exception ကိုသာ ကျဉ်းမြောင်းစွာ catch လုပ်ပြီး သင့်တော်သော boundary တွင် recover သို့မဟုတ် translate လုပ်ပါ။ Context manager သည် error ဖြစ်သော်လည်း file ကို ပိတ်ပေးသည်။ pathlib သည် path operation ကို ရှင်းလင်းစေသည်။ JSON သည် learning project နှင့် သေးငယ်သော interchange အတွက် သင့်တော်သော်လည်း production concurrent write၊ index နှင့် transaction အတွက် database လိုသည်။ User input ဖြင့် arbitrary path ကို မရွေးစေပါနှင့်။",
        "mistakes": ["Catching Exception and silently ignoring it.", "Using a user-provided path without resolving it under an allowed directory.", "Writing JSON without encoding or atomic replacement considerations.", "Returning internal exception details to a student or browser."],
        "mistakes_mm": ["Exception အားလုံးကို catch လုပ်ပြီး တိတ်တဆိတ် လျစ်လျူရှုခြင်း။", "User ပေးသော path ကို allowed directory အောက်ဟုတ်မဟုတ် မစစ်ဘဲ သုံးခြင်း။", "Encoding နှင့် safe replacement မစဉ်းစားဘဲ JSON ရေးခြင်း။", "အတွင်းပိုင်း error detail ကို student/browser သို့ ပြန်ပေးခြင်း။"],
        "best_practices": "Catch specific errors, log safe context, use UTF-8, use with blocks, validate paths, and separate educational JSON storage from database-backed production data.",
        "best_practices_mm": "Specific error ကိုသာ catch လုပ်ပါ၊ safe context ကို log လုပ်ပါ၊ UTF-8 သုံးပါ၊ with block သုံးပြီး path validate လုပ်ပါ။ JSON learning storage နှင့် production database ကို ခွဲခြားပါ။",
        "examples": [
            _example("Handle invalid student scores", """
                def parse_score(raw: str) -> int:
                    score = int(raw)
                    if not 0 <= score <= 100:
                        raise ValueError("score out of range")
                    return score

                try:
                    print(parse_score("82"))
                except ValueError:
                    print("Please enter a score from 0 to 100")
            """, "82", "The input string is converted and checked.", "ValueError covers both non-numeric input and an out-of-range score in this boundary.", "A Django form can show a friendly validation error while logging no sensitive input.", "String score ကို integer ပြောင်းပြီး 0–100 အတွင်း စစ်သည်။", "Django form သည် user ကို friendly validation error ပြနိုင်သည်."),
            _example("Custom validation exception", """
                class InvalidStudentError(ValueError):
                    pass

                def require_name(name: str) -> str:
                    if not name.strip():
                        raise InvalidStudentError("name is required")
                    return name.strip()

                print(require_name(" Aye "))
            """, "Aye", "The input has surrounding spaces.", "A domain-specific exception distinguishes invalid student data from unrelated failures.", "Services can translate this exception into a form error without exposing a traceback.", "မမှန်ကန်သော student data အတွက် custom exception သတ်မှတ်ပြီး name ကို trim လုပ်သည်။", "Service သည် traceback မဖော်ပြဘဲ form error အဖြစ် ပြောင်းနိုင်သည်."),
            _example("Read a text file safely", """
                from pathlib import Path

                path = Path("notes.txt")
                path.write_text("Python\\nDjango\\n", encoding="utf-8")
                with path.open(encoding="utf-8") as handle:
                    lines = [line.strip() for line in handle]
                print(lines)
            """, "['Python', 'Django']", "The example creates notes.txt in an isolated working directory.", "with closes the handle and encoding makes the text interpretation explicit.", "Use a configured storage service for uploads; do not expose arbitrary local paths in a web request.", "Isolated folder ထဲတွင် UTF-8 text file ရေးပြီး with ဖြင့် ဖတ်သည်။", "Web upload အတွက် storage service သုံးပြီး arbitrary local path မပေးသင့်ပါ."),
            _example("Save student data as JSON", """
                import json
                from pathlib import Path

                records = [{"id": 1, "name": "Aye", "score": 88}]
                Path("students.json").write_text(
                    json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                print("saved", len(records))
            """, "saved 1", "records is a list of JSON-compatible dictionaries.", "json.dumps serializes Python data and UTF-8 stores readable text.", "This is suitable for a small CLI exercise, not concurrent production enrollment storage.", "Python record များကို JSON string အဖြစ် serialize လုပ်ပြီး UTF-8 file ထဲ သိမ်းသည်။", "သေးငယ်သော CLI အတွက် သင့်တော်သော်လည်း production enrollment database ကို အစားမထိုးပါ."),
            _example("Load and validate student data", """
                import json
                from pathlib import Path

                data = json.loads(Path("students.json").read_text(encoding="utf-8"))
                valid = [row for row in data if isinstance(row.get("score"), int)]
                print(valid[0]["name"])
            """, "Aye", "students.json contains a JSON array with score fields.", "Loading is followed by shape validation before the value is used.", "Never trust a JSON file as validated just because it parsed successfully.", "JSON ဖတ်ပြီး data shape ကို validate လုပ်ကာ name ကို သုံးသည်။", "Parse အောင်မြင်ရုံဖြင့် data မှန်သည်ဟု မယူဆဘဲ shape စစ်ရသည်."),
        ],
        "exercises": "1. Validate integer input and report a friendly error.\n2. Handle a missing file without swallowing unrelated errors.\n3. Create a custom InvalidStudentError.\n4. Save student records to JSON with UTF-8.\n5. Load, validate, and reject malformed records.\n6. Add a safe allowed-directory path check.",
        "exercises_mm": "၁။ Integer input ကို validate လုပ်ပြီး friendly error ပြပါ။\n၂။ Missing file ကို handle လုပ်ပြီး မဆိုင်သော error များကို မဖုံးကွယ်ပါနှင့်။\n၃။ InvalidStudentError custom exception တည်ဆောက်ပါ။\n၄။ Student record များကို UTF-8 JSON အဖြစ် သိမ်းပါ။\n၅။ Record များကို load/validate လုပ်ပြီး malformed data ကို ပယ်ချပါ။\n၆။ Allowed directory အောက် path ဟုတ်မဟုတ် စစ်ပါ။",
        "homework": "JSON-Based Student Record Management: create add/list/search/update operations, use pathlib and context managers, validate every loaded record, and document why a database is needed for concurrent production writes.",
        "homework_mm": "JSON-Based Student Record Management တည်ဆောက်ပါ။ add/list/search/update operation များ၊ pathlib၊ context manager နှင့် loaded record validation ပါစေ။ Concurrent production write အတွက် database လိုရခြင်းကို ရှင်းပြပါ။",
        "summary": "Reliable Python programs distinguish expected invalid input from unexpected failures and treat files as an explicit trust boundary.",
        "summary_mm": "ယုံကြည်စိတ်ချရသော Python program သည် မျှော်လင့်ထားသော invalid input နှင့် မမျှော်လင့်သော failure ကို ခွဲပြီး file ကို trust boundary အဖြစ် စီမံသည်။",
        "quiz": [
            ("Which exception should be caught when int('x') fails?", ["ValueError", "KeyError", "IndexError", "FileExistsError"], "ValueError", "int() raises ValueError for invalid numeric text."),
            ("Why use a with block for a file?", ["It closes the file reliably", "It encrypts every line", "It creates a database", "It skips validation"], "It closes the file reliably", "Context managers perform cleanup."),
            ("True or false: parsing JSON proves every record is valid for the domain.", ["True", "False"], "False", "Parsing proves syntax, not domain shape or authorization."),
            ("What does pathlib provide?", ["Explicit filesystem path operations", "A template engine", "A quiz answer key", "A password hash"], "Explicit filesystem path operations", "pathlib models and manipulates paths."),
            ("Why avoid catching Exception silently?", ["It hides bugs and loses useful context", "It improves type checking", "It creates indexes", "It validates all inputs"], "It hides bugs and loses useful context", "Unexpected errors need visibility and safe handling."),
            ("Which encoding is a good default for text examples?", ["UTF-8", "Unknown binary", "ASCII only", "Random"], "UTF-8", "UTF-8 handles Burmese and other Unicode text."),
            ("What is a custom exception useful for?", ["Naming a domain-specific failure", "Skipping every test", "Making paths public", "Replacing JSON"], "Naming a domain-specific failure", "Callers can handle the domain boundary intentionally."),
            ("Why is a JSON file not a full production database replacement?", ["Concurrency, indexing, and transactions need stronger storage", "JSON cannot contain text", "Python cannot read JSON", "Files are always encrypted"], "Concurrency, indexing, and transactions need stronger storage", "Production persistence has operational requirements beyond serialization."),
        ],
    },
    {
        "title": "Type Hints, Clean Code and Professional Python",
        "topic": "annotations, dataclasses, typed structures, testing, formatting, and separation of concerns",
        "description": "Use type hints and clean-code practices to make Python services easier to understand, test, and safely evolve into Django applications.",
        "syntax": "from dataclasses import dataclass\n\n@dataclass\nclass Student:\n    name: str\n    score: int\n\ndef passed(student: Student) -> bool:\n    return student.score >= 60",
        "theory": "Type hints document intended shapes and help editors, linters, and type checkers find mistakes; Python does not automatically enforce them at runtime. Use built-in generics supported by the project's Python version, TypedDict for dictionary-shaped data, dataclasses for value objects, and Callable or Protocol when describing behavior. Clean functions have one reason to change, explicit inputs, and deterministic outputs. Unit tests verify behavior; formatting and static analysis improve consistency but do not replace tests.",
        "theory_mm": "Type hint သည် data shape နှင့် function contract ကို မှတ်တမ်းတင်ပြီး editor၊ linter နှင့် type checker များက error ရှာရန် ကူညီသည်။ Python သည် type hint ကို runtime တွင် အလိုအလျောက် မစစ်ပါ။ Project Python version နှင့် ကိုက်ညီသော generic syntax သုံးပါ။ Dictionary shape အတွက် TypedDict၊ value object အတွက် dataclass နှင့် behavior အတွက် Callable/Protocol ကို သုံးနိုင်သည်။ Clean function သည် တာဝန်တစ်ခု၊ input ရှင်းလင်းမှုနှင့် deterministic output ရှိရမည်။",
        "mistakes": ["Believing annotations validate runtime input automatically.", "Creating long functions with hidden side effects.", "Testing implementation details instead of behavior.", "Using a syntax newer than the project's Python version."],
        "mistakes_mm": ["Type hint ရှိရုံဖြင့် runtime input validate ဖြစ်သည်ဟု ယူဆခြင်း။", "Side effect များဖုံးကွယ်ထားသော function ရှည်များရေးခြင်း။", "Behavior အစား implementation detail ကို test လုပ်ခြင်း။", "Project Python version ထက် အသစ်သော syntax သုံးခြင်း။"],
        "best_practices": "Choose a supported syntax version, keep functions cohesive, validate external data at runtime, format consistently, and test user-visible behavior.",
        "best_practices_mm": "အသုံးပြုမည့် Python version ကို အရင်သတ်မှတ်ပါ၊ function ကို cohesive ထားပါ၊ external data ကို runtime တွင် validate လုပ်ပြီး format နှင့် behavior test ကို ထိန်းပါ။",
        "examples": [
            _example("Typed variables", """
                student_name: str = "Mya"
                enrolled: bool = True
                score: int = 88
                print(student_name, enrolled, score)
            """, "Mya True 88", "The annotations describe the intended value types.", "Annotations are documentation and tool input; runtime validation still needs code.", "Typed boundaries make service data easier to review before it reaches a Django model.", "Variable တစ်ခုစီ၏ ရည်ရွယ်ထားသော type ကို annotation ဖြင့် ဖော်ပြသည်။", "Annotation သည် documentation/tool အတွက်ဖြစ်ပြီး runtime validation ကို သီးခြားရေးရသည်."),
            _example("Typed functions", """
                def passed(score: int, minimum: int = 60) -> bool:
                    return score >= minimum

                print(passed(72))
            """, "True", "The function accepts integer score and minimum values.", "The return annotation communicates a boolean result while the body enforces the comparison.", "Typed service signatures help a Django view call domain logic consistently.", "Function parameter နှင့် return type ကို annotation ဖြင့် ဖော်ပြပြီး pass စစ်သည်။", "Django view မှ service logic ကို consistency ရှိစွာ ခေါ်နိုင်ရန် ကူညီသည်."),
            _example("Typed student records", """
                from typing import TypedDict

                class StudentRecord(TypedDict):
                    name: str
                    score: int

                record: StudentRecord = {"name": "Aye", "score": 88}
                print(record["name"])
            """, "Aye", "record follows the StudentRecord dictionary shape.", "TypedDict documents required keys but does not validate a raw JSON object at runtime.", "It makes request-to-service data contracts visible to maintainers.", "TypedDict ဖြင့် student dictionary အတွက် လိုအပ်သော key/type များ ဖော်ပြသည်။", "Raw JSON ကို runtime တွင် ထပ်မံ validate လုပ်ရပြီး contract ကို maintainers မြင်နိုင်သည်."),
            _example("Dataclass student model", """
                from dataclasses import dataclass

                @dataclass
                class Student:
                    name: str
                    score: int

                print(Student("Su", 91))
            """, "Student(name='Su', score=91)", "The dataclass constructor receives name and score.", "dataclass supplies a useful initializer and representation for a value object.", "A dataclass can represent validated service data; it is not automatically a Django database model.", "dataclass သည် initializer နှင့် readable representation ကို အလိုအလျောက် ပေးသည်။", "Service data ကို ကိုယ်စားပြုနိုင်သော်လည်း Django database model အလိုအလျောက် မဖြစ်ပါ."),
            _example("Validated student service", """
                from dataclasses import dataclass

                @dataclass
                class Student:
                    name: str
                    score: int

                def build_student(name: str, score: int) -> Student:
                    if not name.strip() or not 0 <= score <= 100:
                        raise ValueError("invalid student")
                    return Student(name.strip(), score)

                print(build_student(" Aye ", 88).name)
            """, "Aye", "The service validates before constructing the dataclass.", "External values are checked at runtime, then a clean value object is returned.", "A Django form can validate presentation while this service keeps the domain invariant testable.", "Student object မတည်ဆောက်မီ name နှင့် score ကို runtime validate လုပ်သည်။", "Django form အပြင် domain invariant ကို service တွင် ထိန်းထားနိုင်သည်."),
        ],
        "exercises": "1. Add annotations to existing helpers.\n2. Refactor a long function into cohesive functions.\n3. Create a Student dataclass and validate it.\n4. Describe a JSON record with TypedDict.\n5. Write unit tests for valid, invalid, and boundary scores.\n6. Run a formatter and static checker using the project's supported Python version.",
        "exercises_mm": "၁။ ရှိပြီးသား helper များတွင် annotation ထည့်ပါ။\n၂။ Function ရှည်တစ်ခုကို တာဝန်ခွဲ၍ refactor လုပ်ပါ။\n၃။ Student dataclass နှင့် validation တည်ဆောက်ပါ။\n၄။ JSON record ကို TypedDict ဖြင့် ဖော်ပြပါ။\n၅။ Valid၊ invalid နှင့် boundary score အတွက် unit test ရေးပါ။\n၆။ Project Python version နှင့် ကိုက်ညီသော formatter နှင့် static checker run ပါ။",
        "homework": "Refactor Student Toolkit using clean Python patterns: typed service functions, a dataclass value object, runtime validators, focused tests, and a short note distinguishing type checking from runtime validation.",
        "homework_mm": "Student Toolkit ကို clean Python pattern ဖြင့် refactor လုပ်ပါ။ Typed service function၊ dataclass value object၊ runtime validator နှင့် focused test များပါစေ။ Type checking နှင့် runtime validation ကွာခြားချက်ကို မှတ်စုရေးပါ။",
        "summary": "Professional Python combines explicit runtime validation with readable types, small functions, and tests that protect behavior.",
        "summary_mm": "Professional Python တွင် readable type၊ သေးငယ်သော function နှင့် behavior ကို ကာကွယ်သော test များနှင့် explicit runtime validation ကို ပေါင်းစပ်ရသည်။",
        "quiz": [
            ("Do Python type hints automatically validate runtime input?", ["No", "Yes"], "No", "Runtime validation must be implemented explicitly or supplied by a validation library."),
            ("What does dataclass provide conveniently?", ["Value-object methods such as an initializer and repr", "A database server", "A URL router", "A password"], "Value-object methods such as an initializer and repr", "dataclass reduces boilerplate for data-focused classes."),
            ("What does TypedDict describe?", ["The expected keys and value types of a dictionary", "A SQL table automatically", "A CSS class", "A file encoding"], "The expected keys and value types of a dictionary", "TypedDict is a static shape description."),
            ("True or false: a dataclass is automatically a Django model.", ["True", "False"], "False", "Django models need framework model fields and ORM configuration."),
            ("What is a clean function usually characterized by?", ["One cohesive responsibility", "Many hidden side effects", "No inputs", "A very long body"], "One cohesive responsibility", "Cohesion makes code easier to test and change."),
            ("Why must syntax match the selected Python version?", ["Unsupported syntax cannot run in that environment", "It changes database passwords", "It removes all tests", "It publishes code"], "Unsupported syntax cannot run in that environment", "Compatibility is part of a reliable learning example."),
            ("What should unit tests primarily verify?", ["Observable behavior and contracts", "Private whitespace", "A student's password", "Network availability only"], "Observable behavior and contracts", "Behavior-focused tests remain useful during refactoring."),
            ("Where should external JSON values be validated?", ["At the runtime trust boundary", "Only in a comment", "After saving blindly", "Never"], "At the runtime trust boundary", "Static hints do not replace runtime checks."),
        ],
    },
]


def _render_en(item: dict) -> str:
    examples = []
    for index, example in enumerate(item["examples"], 1):
        examples.append(
            f"""### Example {index}: {example['title']}\n\n"
            f"Introduction\n{example['title']} demonstrates one focused {item['topic']} idea.\n\n"
            f"Input\n{example['input']}\n\n"
            f"Code\n```python\n{example['code']}\n```\n\n"
            f"Expected output\n{example['output']}\n\n"
            f"Line-by-line explanation\n{example['explanation']} The imports or declarations establish the inputs, the body applies one rule, and the final print or response makes the result observable.\n\n"
            f"Common mistakes\n{'; '.join(item['mistakes'][:2])}\n\n"
            f"Real-world relevance\n{example['relevance']}"""
        )
    return dedent(
        f"""# {item['title']}

Introduction
{item['description']}

Learning objectives
- Explain {item['topic']} in your own words.
- Build and inspect five executable Python examples.
- Identify how the concept becomes a safe Django boundary.

Prerequisites
Basic Python syntax, a terminal, and the completed previous lesson. Run examples in an isolated temporary project; never execute learner code inside the live Learn-Coding application.

Detailed theory
{item['theory']}

Core concepts
{item['topic']}. Values cross trust boundaries only after validation. Keep domain decisions in Python code and keep framework adapters thin.

Syntax and usage
```python
{item['syntax']}
```

Code examples
{chr(10).join(examples)}

Common mistakes
- {item['mistakes'][0]}
- {item['mistakes'][1]}
- {item['mistakes'][2]}
- {item['mistakes'][3]}

Best practices
{item['best_practices']}

Practical exercises
{item['exercises']}

Homework
{item['homework']}

Knowledge quiz
Answer the lesson quiz after running the examples. Explain the reason for each answer instead of memorizing a keyword.

Lesson summary
{item['summary']}

Further learning
Read the official Python documentation for the relevant language feature and the Django documentation for the integration boundary. Continue with the next lesson only after the exercises and tests pass.
"""
    ).strip()


def _render_mm(item: dict) -> str:
    examples = []
    for index, example in enumerate(item["examples"], 1):
        examples.append(
            f"""### ဥပမာ {index}: {example['title']}\n\n"
            f"မိတ်ဆက်\n{example['explanation_mm']}\n\n"
            f"Input\n{example['input']}\n\n"
            f"Code\n```python\n{example['code']}\n```\n\n"
            f"မျှော်မှန်းရလဒ်\n{example['output']}\n\n"
            f"ရှင်းလင်းချက်\n{example['explanation_mm']} Code ထဲရှိ declaration များက input ကို သတ်မှတ်ပြီး body က rule တစ်ခုကို လုပ်ဆောင်ကာ နောက်ဆုံး print/response က ရလဒ်ကို ပြသည်။\n\n"
            f"အမှားများ\n{'; '.join(item['mistakes_mm'][:2])}\n\n"
            f"လက်တွေ့အသုံးဝင်မှု\n{example['relevance_mm']}"""
        )
    return dedent(
        f"""# {item['title']}

မိတ်ဆက်
{item['description']} ကို Python နှင့် Django ဆက်စပ်အသုံးပြုနိုင်အောင် လေ့လာမည်။

သင်ယူပြီးနောက် လုပ်နိုင်ရမည့်အရာများ
- {item['topic']} ကို ကိုယ်ပိုင်စကားဖြင့် ရှင်းပြနိုင်ရန်။
- Python example ငါးခုကို isolated environment တွင် run/test လုပ်နိုင်ရန်။
- Concept ကို Django boundary အဖြစ် လုံခြုံစွာ ချိတ်ဆက်နိုင်ရန်။

လိုအပ်ချက်
Python syntax အခြေခံ၊ terminal အသုံးပြုနိုင်မှုနှင့် ယခင် lesson ပြီးမြောက်မှု လိုအပ်သည်။ Example များကို temporary project ထဲတွင်သာ run ပါ။ Live Learn-Coding application ထဲတွင် learner code မ run ပါနှင့်။

အသေးစိတ်သီအိုရီ
{item['theory_mm']}

အဓိကအယူအဆများ
{item['topic']} ကို နားလည်ပြီး user input သို့မဟုတ် file data များကို trust boundary တွင် validate လုပ်ပါ။ Business rule များကို Python code ထဲတွင်ထားပြီး framework adapter ကို သေးငယ်စွာထားပါ။

Syntax နှင့် အသုံးပြုပုံ
```python
{item['syntax']}
```

Code ဥပမာများ
{chr(10).join(examples)}

တွေ့ရများသောအမှားများ
- {item['mistakes_mm'][0]}
- {item['mistakes_mm'][1]}
- {item['mistakes_mm'][2]}
- {item['mistakes_mm'][3]}

အကောင်းဆုံးနည်းလမ်းများ
{item['best_practices_mm']}

လက်တွေ့လေ့ကျင့်ခန်းများ
{item['exercises_mm']}

အိမ်စာ
{item['homework_mm']}

အသိပညာစစ်ဆေးမှု
Example များကို run ပြီး lesson quiz ကို ဖြေပါ။ အဖြေကို မှတ်မိရုံမဟုတ်ဘဲ အကြောင်းရင်းကို ရှင်းပြပါ။

Lesson အနှစ်ချုပ်
{item['summary_mm']}

ဆက်လက်လေ့လာရန်
သက်ဆိုင်ရာ Python official documentation နှင့် Django integration documentation ကို project version နှင့် ကိုက်ညီအောင် ဖတ်ပါ။ Exercise နှင့် test များ အောင်မြင်ပြီးမှ နောက် lesson သို့ ဆက်ပါ။
"""
    ).strip()


def _quiz_questions(item: dict):
    return [
        {"prompt": prompt, "options": options, "correct_answer": answer, "explanation": explanation, "difficulty": "beginner" if index < 5 else "intermediate", "points": 1, "topic": item["topic"]}
        for index, (prompt, options, answer, explanation) in enumerate(item["quiz"], 1)
    ]


def _ensure_examples(db, lesson, item):
    rows = db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all()
    for position, example in enumerate(item["examples"], 1):
        values = {"title": example["title"], "language": "python", "filename": f"lesson-{lesson.order_index:02d}.py", "code": example["code"], "description": f"Expected output: {example['output']}\n\n{example['relevance']}", "position": position}
        if position <= len(rows):
            for key, value in values.items():
                setattr(rows[position - 1], key, value)
        else:
            db.add(CodeExample(lesson_id=lesson.id, **values))


def _ensure_lesson_quiz(db, lesson, item):
    quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
    if not quiz:
        quiz = LessonQuiz(lesson_id=lesson.id, title=f"{item['title']} knowledge check", explanation="Review the examples and explain each boundary before retrying.", status="draft")
        db.add(quiz)
        db.flush()
    quiz.title = f"{item['title']} knowledge check"
    quiz.explanation = "Review the examples and explain each boundary before retrying."
    quiz.status = "draft"
    questions = db.scalars(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id).order_by(QuizQuestion.position)).all()
    for position, question_data in enumerate(_quiz_questions(item), 1):
        values = {"prompt": question_data["prompt"], "question_type": "true_false" if question_data["options"] == ["True", "False"] else "multiple_choice", "options_json": json.dumps(question_data["options"], ensure_ascii=False), "correct_answer": question_data["correct_answer"], "explanation": question_data["explanation"]}
        if position <= len(questions):
            for key, value in values.items():
                setattr(questions[position - 1], key, value)
        else:
            db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))


def _ensure_exercise(db, lesson, item):
    exercise = db.scalar(select(CodingExercise).where(CodingExercise.lesson_id == lesson.id).order_by(CodingExercise.created_at, CodingExercise.id))
    values = {"title": f"{item['title']} practice", "description_en": item["exercises"], "description_mm": item["exercises_mm"], "difficulty": "intermediate" if lesson.order_index >= 3 else "beginner", "language": "python", "starter_code": "# Implement the exercise in an isolated project.\n", "status": "draft"}
    if exercise:
        for key, value in values.items():
            setattr(exercise, key, value)
    else:
        db.add(CodingExercise(lesson_id=lesson.id, slug=f"django-python-foundations-{lesson.order_index}-practice", **values))


def _module_assessment():
    questions = []
    for item in LESSONS:
        questions.append(_quiz_questions(item)[0])
    questions.extend([
        {"prompt": "Which boundary should validate external JSON before a Django model write?", "options": ["A service or form boundary", "A CSS file", "A browser comment", "A database password"], "correct_answer": "A service or form boundary", "explanation": "Validation belongs at a server-side trust boundary before persistence.", "difficulty": "intermediate", "points": 2, "topic": "validation"},
        {"prompt": "Which statement best distinguishes a plain object from a Django model?", "options": ["A plain object is in memory; a model can be persisted through the ORM", "They are always identical", "A plain object automatically migrates", "A model cannot have methods"], "correct_answer": "A plain object is in memory; a model can be persisted through the ORM", "explanation": "Persistence is supplied by Django's model and database machinery.", "difficulty": "intermediate", "points": 2, "topic": "classes and Django"},
        {"prompt": "A function receives a list and returns a new filtered list. Which quality is most valuable?", "options": ["A clear contract and deterministic result", "A hidden global mutation", "A template-only implementation", "A random side effect"], "correct_answer": "A clear contract and deterministic result", "explanation": "Deterministic functions are easy to test and reuse.", "difficulty": "beginner", "points": 1, "topic": "functions"},
        {"prompt": "True or false: catching every Exception and returning an empty list is always safe.", "options": ["True", "False"], "correct_answer": "False", "explanation": "It can hide programming and infrastructure failures.", "difficulty": "intermediate", "points": 1, "topic": "exceptions"},
        {"prompt": "Which tool is appropriate for documenting a dictionary-shaped record to a type checker?", "options": ["TypedDict", "HttpResponse", "migrate", "collectstatic"], "correct_answer": "TypedDict", "explanation": "TypedDict describes expected keys and value types for mappings.", "difficulty": "intermediate", "points": 1, "topic": "type hints"},
        {"prompt": "Which project structure best separates a CLI entry point from reusable student logic?", "options": ["main.py plus student_toolkit/services.py and tests/", "One 2,000-line template", "Only a README", "A database table with no code"], "correct_answer": "main.py plus student_toolkit/services.py and tests/", "explanation": "A small package and tests create reusable boundaries.", "difficulty": "beginner", "points": 1, "topic": "packages"},
        {"prompt": "What must be tested after an example prints an expected result?", "options": ["The actual behavior and failure cases", "Only the screenshot color", "A production secret", "Nothing"], "correct_answer": "The actual behavior and failure cases", "explanation": "Expected output is evidence, while tests protect normal and invalid behavior.", "difficulty": "intermediate", "points": 1, "topic": "testing"},
        {"prompt": "Which storage is the correct production replacement for a learning JSON file when concurrent writes and transactions matter?", "options": ["A transactional database", "Another unvalidated JSON append", "A template", "A Python comment"], "correct_answer": "A transactional database", "explanation": "Concurrent durable application data needs database guarantees.", "difficulty": "intermediate", "points": 2, "topic": "JSON and storage"},
        {"prompt": "Code output analysis: what does [x * 2 for x in [1, 3]] return?", "options": ["[2, 6]", "[1, 3]", "6", "True"], "correct_answer": "[2, 6]", "explanation": "The comprehension transforms each item into a new list.", "difficulty": "beginner", "points": 1, "topic": "fundamentals"},
        {"prompt": "Which practice keeps a Django view maintainable?", "options": ["Use the view as a thin adapter around tested services", "Put all domain rules in HTML", "Trust hidden form fields", "Skip authorization"], "correct_answer": "Use the view as a thin adapter around tested services", "explanation": "Thin adapters keep domain behavior reusable and testable.", "difficulty": "intermediate", "points": 2, "topic": "Django integration"},
        {"prompt": "What does a context manager protect when reading a file?", "options": ["Resource cleanup", "The file from all changes forever", "Database migrations", "Type checking"], "correct_answer": "Resource cleanup", "explanation": "with ensures cleanup when the block exits.", "difficulty": "beginner", "points": 1, "topic": "files"},
        {"prompt": "Why should code use the selected Python version's type syntax?", "options": ["To keep examples executable in the target environment", "To hide imports", "To remove validation", "To change a URL"], "correct_answer": "To keep examples executable in the target environment", "explanation": "Syntax compatibility is required for runnable lessons.", "difficulty": "intermediate", "points": 1, "topic": "compatibility"},
    ])
    return questions


def _ensure_module_assessment(db, module):
    questions = _module_assessment()
    row = db.scalar(select(ModuleQuizDraft).where(ModuleQuizDraft.module_id == module.id))
    payload = [{"position": index, **question} for index, question in enumerate(questions, 1)]
    if not row:
        row = ModuleQuizDraft(module_id=module.id, title_en="Python Foundations Module Assessment", title_mm="Python အခြေခံ Module စစ်ဆေးမှု", questions_json=json.dumps(payload, ensure_ascii=False), pass_percent=70, status="draft")
        db.add(row)
    else:
        row.title_en = "Python Foundations Module Assessment"
        row.title_mm = "Python အခြေခံ Module စစ်ဆေးမှု"
        row.questions_json = json.dumps(payload, ensure_ascii=False)
        row.pass_percent = 70
        if row.status not in {"in_review", "approved", "published"}:
            row.status = "draft"
    return len(questions)


def _project_source_files():
    return {
        "student_toolkit/__init__.py": "from .models import Student\n\n__all__ = [\"Student\"]\n",
        "student_toolkit/models.py": dedent('''
            from dataclasses import dataclass, field


            @dataclass
            class Student:
                student_id: str
                name: str
                age: int
                courses: list[str] = field(default_factory=list)
                scores: dict[str, int] = field(default_factory=dict)

                def grade(self) -> str:
                    if not self.scores:
                        return "N/A"
                    average = sum(self.scores.values()) / len(self.scores)
                    return "A" if average >= 80 else "B" if average >= 60 else "C"
        ''').strip() + "\n",
        "student_toolkit/validators.py": dedent('''
            class ValidationError(ValueError):
                pass


            def text(value: str, field: str) -> str:
                value = value.strip()
                if not value:
                    raise ValidationError(f"{field} is required")
                return value


            def age(value: int) -> int:
                if not 1 <= value <= 130:
                    raise ValidationError("age must be between 1 and 130")
                return value


            def score(value: int) -> int:
                if not 0 <= value <= 100:
                    raise ValidationError("score must be between 0 and 100")
                return value
        ''').strip() + "\n",
        "student_toolkit/storage.py": dedent('''
            import json
            from pathlib import Path
            from .models import Student
            from .validators import age, score, text


            def safe_path(base: Path, filename: str) -> Path:
                root = base.resolve()
                candidate = (root / filename).resolve()
                if candidate.parent != root or candidate.name != filename:
                    raise ValueError("storage filename must stay in the data directory")
                return candidate


            def save_students(base: Path, filename: str, students: list[Student]) -> Path:
                base.mkdir(parents=True, exist_ok=True)
                target = safe_path(base, filename)
                payload = [{"student_id": s.student_id, "name": s.name, "age": s.age, "courses": s.courses, "scores": s.scores} for s in students]
                target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                return target


            def load_students(base: Path, filename: str) -> list[Student]:
                target = safe_path(base, filename)
                rows = json.loads(target.read_text(encoding="utf-8"))
                result = []
                for row in rows:
                    result.append(Student(text(row["student_id"], "student_id"), text(row["name"], "name"), age(row["age"]), list(row.get("courses", [])), {name: score(value) for name, value in row.get("scores", {}).items()}))
                return result
        ''').strip() + "\n",
        "student_toolkit/services.py": dedent('''
            from pathlib import Path
            from .models import Student
            from .storage import load_students, save_students
            from .validators import age, score, text


            class StudentService:
                def __init__(self, data_dir: Path) -> None:
                    self.data_dir = data_dir
                    self.students: dict[str, Student] = {}

                def add(self, student_id: str, name: str, student_age: int, courses: list[str], scores: dict[str, int]) -> Student:
                    student_id = text(student_id, "student_id")
                    if student_id in self.students:
                        raise ValueError("student already exists")
                    student = Student(student_id, text(name, "name"), age(student_age), courses, {course: score(value) for course, value in scores.items()})
                    self.students[student_id] = student
                    return student

                def view(self) -> list[Student]:
                    return list(self.students.values())

                def edit(self, student_id: str, **changes) -> Student:
                    student = self.students[student_id]
                    if "name" in changes:
                        student.name = text(changes["name"], "name")
                    if "age" in changes:
                        student.age = age(changes["age"])
                    return student

                def remove(self, student_id: str) -> None:
                    del self.students[student_id]

                def search(self, term: str) -> list[Student]:
                    term = term.casefold()
                    return [student for student in self.students.values() if term in student.name.casefold() or term in student.student_id.casefold()]

                def save(self) -> None:
                    save_students(self.data_dir, "students.json", self.view())

                def load(self) -> None:
                    self.students = {student.student_id: student for student in load_students(self.data_dir, "students.json")}
        ''').strip() + "\n",
        "main.py": dedent('''
            from pathlib import Path
            from student_toolkit.services import StudentService


            def main() -> None:
                service = StudentService(Path("data"))
                try:
                    service.load()
                except FileNotFoundError:
                    pass
                print("Student Profile Toolkit")
                print("Loaded students:", len(service.view()))
                service.save()


            if __name__ == "__main__":
                main()
        ''').strip() + "\n",
        "tests/test_services.py": dedent('''
            import tempfile
            import unittest
            from pathlib import Path
            from student_toolkit.services import StudentService


            class StudentServiceTests(unittest.TestCase):
                def test_add_search_and_grade(self):
                    with tempfile.TemporaryDirectory() as directory:
                        service = StudentService(Path(directory))
                        student = service.add("S-1", "Aye", 20, ["Python"], {"Python": 88})
                        self.assertEqual(student.grade(), "A")
                        self.assertEqual(len(service.search("aye")), 1)


            if __name__ == "__main__":
                unittest.main()
        ''').strip() + "\n",
        "tests/test_storage.py": dedent('''
            import tempfile
            import unittest
            from pathlib import Path
            from student_toolkit.models import Student
            from student_toolkit.storage import load_students, save_students


            class StorageTests(unittest.TestCase):
                def test_json_round_trip(self):
                    with tempfile.TemporaryDirectory() as directory:
                        path = Path(directory)
                        original = [Student("S-1", "Aye", 20, ["Python"], {"Python": 88})]
                        save_students(path, "students.json", original)
                        loaded = load_students(path, "students.json")
                        self.assertEqual(loaded[0], original[0])


            if __name__ == "__main__":
                unittest.main()
        ''').strip() + "\n",
    }


def _ensure_project(db, course, module):
    slug = "django-python-student-profile-management-toolkit"
    source_files = _project_source_files()
    project_brief = {"goal": "Build a complete student profile CLI", "scope": "Module 02 only", "setup_commands": ["python -m venv .venv", "python -m unittest discover -s tests -v", "python main.py"], "sample_input": "The starter CLI loads data from data/students.json and writes a safe empty JSON array on first run.", "source_files": source_files, "extensions": ["Add interactive commands", "Add atomic file replacement", "Port the domain to Django models in Module 04"]}
    project = db.scalar(select(ProjectTemplate).where(ProjectTemplate.slug == slug))
    if not project:
        project = ProjectTemplate(title="Student Profile Management Toolkit", slug=slug, description_en="A Python CLI application that manages student profiles, grades, JSON storage, validation, reusable modules, type annotations, and tests.", description_mm="Student profile၊ grade၊ JSON storage၊ validation၊ reusable module၊ type annotation နှင့် test များပါသော Python CLI application တစ်ခု။", difficulty="intermediate", estimated_hours=8, requirements="Python 3, terminal, virtual environment, and basic file-system permissions.", learning_outcomes="Combine classes or dataclasses, functions, packages, exceptions, JSON storage, type hints, validation, and unit tests.", technology_stack="Python 3 | pathlib | json | dataclasses | unittest", prerequisites="Complete all six Module 02 lessons and understand basic Python syntax.", architecture_overview="main.py coordinates CLI input; student_toolkit contains models, services, validators, and storage; tests verify services and storage.", folder_structure="student_profile_toolkit/\n  main.py\n  student_toolkit/__init__.py\n  student_toolkit/models.py\n  student_toolkit/services.py\n  student_toolkit/validators.py\n  student_toolkit/storage.py\n  tests/test_services.py\n  tests/test_storage.py", testing_guide="Run python -m unittest discover -s tests -v in an isolated virtual environment.", deployment_guide="This is a learning CLI project. Do not treat the JSON file as production Django persistence; migrate the domain to Django models before deployment.", tags_json=json.dumps(["python", "cli", "json", "testing", "django-foundations"], ensure_ascii=False), languages_json=json.dumps(["Python"], ensure_ascii=False), brief_json=json.dumps(project_brief, ensure_ascii=False), status="draft", published=False)
        db.add(project)
        db.flush()
    project.brief_json = json.dumps(project_brief, ensure_ascii=False)
    link = db.scalar(select(ProjectCourseLink).where(ProjectCourseLink.project_id == project.id, ProjectCourseLink.course_id == course.id, ProjectCourseLink.module_id == module.id))
    if not link:
        db.add(ProjectCourseLink(project_id=project.id, course_id=course.id, module_id=module.id, position=1))
    milestones = [
        ("Project setup and models", "Set up the package and implement Student as a dataclass.", "Create the folder tree, dataclass, and input validators.", "student_toolkit/models.py", "A valid Student object can be created from sanitized values."),
        ("Services and CLI operations", "Implement add, view, edit, remove, search, and grade operations.", "Keep business rules in services and use main.py only for CLI coordination.", "student_toolkit/services.py", "Each operation returns a deterministic result and handles missing IDs."),
        ("JSON storage and safe errors", "Persist records through a JSON storage boundary.", "Use pathlib, UTF-8, validation on load, and specific exceptions.", "student_toolkit/storage.py", "The CLI can save, load, and reject malformed records without a traceback."),
        ("Tests and review", "Add service and storage tests and document the design.", "Cover normal, invalid, missing-file, and round-trip behavior.", "tests/test_services.py", "python -m unittest discover -s tests -v passes with meaningful cases."),
    ]
    for position, (title, description, content, filename, output) in enumerate(milestones, 1):
        milestone = db.scalar(select(ProjectMilestone).where(ProjectMilestone.project_id == project.id, ProjectMilestone.position == position))
        values = {"title": title, "slug": f"milestone-{position}", "description_en": description, "description_mm": f"{description} ကို လက်တွေ့တည်ဆောက်ပါ။", "content_en": content + "\n\nRequired files:\n" + project.folder_structure, "content_mm": "ဤ milestone တွင် လိုအပ်သော file များကို တည်ဆောက်ပြီး လက်တွေ့စစ်ဆေးပါ။", "code": "from dataclasses import dataclass\n\n@dataclass\nclass Student:\n    student_id: str\n    name: str\n    age: int\n", "filename": filename, "expected_output": output, "line_explanation": "Read the imports, validate the boundary, create or update the domain object, and assert the result in a focused test.", "completion_criteria": "The learner commits the files, runs the focused command, and records the actual output.", "resources_json": json.dumps([{"title": "Python documentation", "url": "https://docs.python.org/3/"}, {"title": "Django documentation", "url": "https://docs.djangoproject.com/"}], ensure_ascii=False), "required": True}
        if not milestone:
            db.add(ProjectMilestone(project_id=project.id, position=position, **values))
        else:
            for key, value in values.items():
                setattr(milestone, key, value)
    requirement = db.scalar(select(ProjectRequirement).where(ProjectRequirement.project_id == project.id, ProjectRequirement.position == 1))
    req_values = {"title": "Complete working CLI and tests", "description": "Implement all required operations with typed, validated, reusable Python code and JSON round-trip storage.", "acceptance_criteria": "Add/view/edit/remove/search work; invalid input is rejected; records load/save as UTF-8 JSON; unit tests cover services and storage; no credentials or unsafe paths are committed.", "required": True}
    if not requirement:
        db.add(ProjectRequirement(project_id=project.id, position=1, **req_values))
    else:
        for key, value in req_values.items():
            setattr(requirement, key, value)
    rubric = [("Functionality", "All CLI operations and grade calculations work.", 30), ("Design", "Modules, classes, validation, and storage boundaries are cohesive.", 25), ("Safety", "Specific errors, safe paths, UTF-8, and no secret leakage.", 20), ("Tests", "Meaningful service and storage tests pass.", 20), ("Documentation", "Setup, commands, outputs, and extensions are explained.", 5)]
    for position, (name, description, weight) in enumerate(rubric, 1):
        criterion = db.scalar(select(ProjectRubricCriterion).where(ProjectRubricCriterion.project_id == project.id, ProjectRubricCriterion.position == position))
        if not criterion:
            db.add(ProjectRubricCriterion(project_id=project.id, position=position, name=name, description=description, weight=weight))
        else:
            criterion.name, criterion.description, criterion.weight = name, description, weight
    return project


def seed_python_foundations_module(db, course):
    """Populate the canonical Module 02 as six reviewable draft lessons."""
    module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == 2))
    created_lessons = 0
    if not module:
        module = CourseModule(course_id=course.id, title=MODULE_TITLE, order_index=2)
        db.add(module)
        db.flush()
    module.title = MODULE_TITLE
    module.title_mm = MODULE_TITLE_MM
    module.description = MODULE_DESCRIPTION
    module.description_mm = MODULE_DESCRIPTION_MM
    module.learning_objectives = "\n".join(f"{index}. {value}" for index, value in enumerate(OBJECTIVES, 1))
    module.learning_objectives_mm = "\n".join(f"{index}. {value}" for index, value in enumerate(OBJECTIVES_MM, 1))
    for position, item in enumerate(LESSONS, 1):
        lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == position))
        if not lesson:
            lesson = Lesson(module_id=module.id, title=item["title"], slug=f"02-{item['title'].lower().replace(' ', '-').replace(',', '').replace('&', 'and')}", description=item["description"], content_en="", content_mm="", order_index=position, duration_minutes=60, status="draft", published=False)
            db.add(lesson)
            db.flush()
            created_lessons += 1
        content_en, content_mm = _render_en(item), _render_mm(item)
        if lesson.published or lesson.status in {"in_review", "approved", "published"}:
            draft = db.scalar(select(LessonContentDraft).where(LessonContentDraft.lesson_id == lesson.id))
            if not draft:
                draft = LessonContentDraft(lesson_id=lesson.id, base_content_version=lesson.content_version, draft_version=1, title=item["title"], slug=lesson.slug, description=item["description"], content_en=content_en, content_mm=content_mm, duration_minutes=60, status="draft", change_summary="Phase 04 Python Foundations authoring")
                db.add(draft)
            elif draft.status == "draft":
                draft.title, draft.description, draft.content_en, draft.content_mm, draft.duration_minutes = item["title"], item["description"], content_en, content_mm, 60
        else:
            lesson.title = item["title"]
            lesson.description = item["description"]
            lesson.content_en = content_en
            lesson.content_mm = content_mm
            lesson.duration_minutes = 60
            lesson.status = "draft"
            lesson.published = False
        _ensure_examples(db, lesson, item)
        _ensure_lesson_quiz(db, lesson, item)
        _ensure_exercise(db, lesson, item)
    assessment_count = _ensure_module_assessment(db, module)
    project = _ensure_project(db, course, module)
    db.flush()
    return {"module": module, "created_lessons": created_lessons, "lesson_count": len(LESSONS), "assessment_questions": assessment_count, "project": project}
