"""Idempotent authored jQuery curriculum.

Module 1 is the complete vertical slice. Remaining modules contain a real
foundation lesson each so published modules are never empty; deeper labs and
projects remain explicitly incremental work.
"""
import json
import re
from sqlalchemy import select
from .models import CourseModule, Lesson, LessonQuiz, QuizQuestion, CodeExample

MODULES = [
    "Introduction to jQuery", "Environment Setup & Installation", "jQuery Syntax & Ready Handler",
    "jQuery Selectors", "DOM Traversal", "DOM Manipulation", "CSS Manipulation & Classes",
    "Event Handling", "Event Delegation", "Effects & Animations", "Forms & Validation",
    "UI Components with jQuery", "AJAX Fundamentals", "jQuery AJAX Methods", "JSON & API Integration",
    "Promises & Deferred", "Dynamic Tables & Search", "Local Storage & State", "Plugin Development",
    "WordPress & jQuery", "Security & Best Practices", "Performance & Debugging",
    "Real-World jQuery Projects", "Final Capstone & Assessment",
]

MODULE_ONE = [
    ("What Is jQuery?", "a focused library over browser DOM APIs", "const label = $(\"#status\");\nlabel.text(\"jQuery is ready\");", "jQuery is a small JavaScript library that simplifies DOM selection, traversal, events, effects, and asynchronous requests. It does not replace HTML, CSS, or JavaScript. The course targets modern jQuery 4.x and records a compatibility note: review the official migration guidance when maintaining jQuery 3.x applications.", "$(selector).method(value);", "jQuery သည် DOM selection၊ event နှင့် AJAX လုပ်ဆောင်ချက်များကို ရိုးရှင်းစေသော JavaScript library ဖြစ်သည်။"),
    ("Environment Setup and Version Compatibility", "local files, browser tools, and pinned library versions", "<script src=\"/vendor/jquery-4.x.min.js\"></script>\n<script src=\"app.js\"></script>", "A learning project should pin a reviewed jQuery build rather than depending on an unknown CDN response. Keep the library version in project documentation, verify the checksum or package lock, and test the browser support matrix. jQuery 3.x syntax is often familiar, but migration warnings and deprecated APIs must be reviewed.", "<script src=\"jquery.min.js\"></script>", "Project တွင် jQuery version ကို pin လုပ်ပြီး browser compatibility နှင့် migration notes များကို မှတ်တမ်းတင်ပါ။"),
    ("The Ready Handler", "running code after the document is available", "$(function () {\n  $(\"#message\").text(\"Document ready\");\n});", "The ready handler waits until the document can be queried. Modern scripts may use defer, but the ready handler remains useful in legacy integrations and plugins. Keep initialization in a named function when a page has multiple components.", "$(function () { /* initialize */ });", "Ready handler သည် document ကို query လုပ်နိုင်သည့်အချိန်တွင် initialization ကို run စေသည်။"),
    ("Selectors and Safe Text", "finding elements without unsafe HTML injection", "$(\".notice\").text(userMessage);\n$(\"#count\").attr(\"aria-live\", \"polite\");", "Selectors can target IDs, classes, attributes, and relationships. Use text() for untrusted text. html() interprets markup and should only receive trusted, sanitized content. Add meaningful labels and ARIA state where dynamic content changes.", "$(\"#id\"); $(\".class\"); $(\"[data-role='item']\");", "Untrusted text အတွက် text() ကို အသုံးပြုပြီး html() ကို trusted content မဟုတ်လျှင် မသုံးပါနှင့်။"),
    ("DOM Traversal and Collections", "moving through related elements", "$(\".card\").first().find(\".title\").text(\"Selected\");\n$(\"li\").each(function () { console.log($(this).text()); });", "Traversal methods such as find, children, closest, first, and each help code follow the document structure. Prefer a stable data attribute or semantic relationship over fragile selector chains. Check empty collections before assuming an element exists.", "$(root).find(selector); $(child).closest(selector);", "find၊ closest နှင့် each တို့သည် DOM relationship များကို လုံခြုံစွာ အသုံးချနိုင်စေသည်။"),
    ("DOM Manipulation and Classes", "creating nodes and representing UI state", "const item = $(\"<li>New item</li>\");\nitem.addClass(\"is-new\");\n$(\"#items\").append(item);", "Use text or controlled element creation for user data. Classes are a useful state boundary between behavior and CSS. Keep manipulation small, preserve focus, and announce important updates to assistive technology.", "$(element).addClass(name); $(parent).append(child);", "UI state ကို class များဖြင့် ကိုယ်စားပြုပြီး user data ကို text အဖြစ် ထည့်သွင်းပါ။"),
    ("Module 1 Review and Assessment", "selectors, ready, traversal, safe text, and state", "$(function () {\n  $(\"#save\").on(\"click\", function () {\n    $(\"#status\").text(\"Saved\").addClass(\"is-success\");\n  });\n});", "This assessment combines initialization, event handling, safe text insertion, and a CSS state class. A good jQuery component has a small selector surface, a keyboard-accessible control, predictable cleanup, and tests for missing or repeated elements.", "$(selector).on(event, handler);", "Module 1 တွင် ready handler၊ selectors၊ traversal၊ safe text နှင့် state class များကို ပေါင်းစပ်လေ့လာပါမည်။"),
]

GENERAL = [
    ("Install and Pin jQuery", "a reproducible browser library setup"), ("Ready Initialization Patterns", "reliable page startup"),
    ("CSS and Attribute Selectors", "precise element targeting"), ("Traversal APIs", "related DOM navigation"),
    ("Creating and Updating Nodes", "safe DOM updates"), ("Classes and Style State", "presentation state"),
    ("Events and Namespaces", "maintainable event handlers"), ("Delegated Events", "dynamic content behavior"),
    ("Effects with Reduced Motion", "accessible visual transitions"), ("Forms and Validation", "input boundaries"),
    ("Accessible jQuery Components", "keyboard and screen-reader behavior"), ("AJAX Request Lifecycle", "remote request states"),
    ("get, post, and Error Handling", "HTTP success and failure"), ("JSON Validation", "defensive API data handling"),
    ("Promises and Deferred Compatibility", "asynchronous composition"), ("Filtering Dynamic Data", "searchable tables"),
    ("Client State and Storage", "privacy-aware browser state"), ("Reusable Plugin Contracts", "small configurable plugins"),
    ("WordPress Enqueue and noConflict", "safe CMS integration"), ("XSS and CSRF Boundaries", "secure browser code"),
    ("Performance and Debugging", "measurement and cleanup"), ("Project Architecture", "maintainable interactive features"),
    ("Final Capstone Planning", "an accessible data-driven interface"),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(title, topic, theory, syntax, code, mm, previous, next_title):
    return f"""Introduction
{title} introduces {topic} with modern jQuery 4.x syntax and a compatibility note for maintained jQuery 3.x applications.

Learning objectives
- Explain {topic} and identify the browser boundary involved.
- Read and write jQuery with safe text handling, accessible state, and predictable cleanup.
- Compare the jQuery approach with the underlying browser API when choosing an implementation.

Prerequisites
{previous}

Detailed theory
{theory}

jQuery syntax
{syntax}

HTML/CSS/JavaScript example
```javascript
{code}
```

Expected result
The example updates only the intended element or reports the documented local state. Use a real browser page with the pinned, reviewed jQuery version to observe the interaction.

Live preview
Hosted arbitrary JavaScript execution is disabled until an isolated preview is configured and verified. Copy the example into a local test page using a pinned jQuery build; never load unknown scripts or put secrets in browser code.

Line-by-line explanation
The selector identifies a small DOM boundary. The jQuery method performs one focused operation, and the event or callback controls when it runs. Read the DOM state after each line and verify the result with browser developer tools.

Vanilla JavaScript comparison
The equivalent browser API may use querySelector, addEventListener, classList, textContent, fetch, or closest. jQuery is useful in existing applications and WordPress themes; choose native APIs for new code when they provide the same clarity without adding a dependency.

Common mistakes
- Running initialization before the document exists.
- Using html() with untrusted input instead of text().
- Binding the same handler repeatedly after partial page updates.
- Relying on fragile selectors or ignoring empty collections.
- Treating jQuery 3.x compatibility as automatic without migration testing.

Security considerations
Validate server responses, use text() for untrusted strings, protect state-changing requests with server-side CSRF controls, avoid secrets in browser code, and keep preview execution out of the parent application.

Best practices
Pin and audit the jQuery version, use namespaced handlers, support keyboard interaction, honor prefers-reduced-motion, handle AJAX failures, clean up handlers, and document browser compatibility.

Practice exercises
- Easy: reproduce the example and change one selector.
- Medium: add an empty-state message and keyboard support.
- Challenge: implement the same behavior with a native browser API and compare trade-offs.
Hints: identify the DOM boundary, input trust level, event lifecycle, and failure state before coding.
Guided solution: start with one element, test missing elements, then add repeated and keyboard interactions.

Quiz
1. Which method is safer for untrusted text? text().
2. True or false: jQuery should be loaded from an unknown unpinned URL. False.
3. What should AJAX code handle? Success, failure, timeout, and loading states.
4. Why compare vanilla APIs? To choose the smallest clear dependency for the project.

Summary
You can now explain {topic}, apply safe jQuery patterns, and compare them with native browser APIs.

Next lesson
{next_title}
"""

def _questions(topic):
    return [
        (f"Which practice best supports {topic}?", ["Small selectors and explicit states", "Global handlers everywhere", "Unknown library versions"], "Small selectors and explicit states", "Small boundaries are easier to test, clean up, and make accessible."),
        ("True or false: text() is preferred for untrusted user text.", ["True", "False"], "True", "text() does not interpret the value as HTML markup."),
        ("What must AJAX code handle?", ["Success and failure states", "Only success", "Passwords in browser source"], "Success and failure states", "Network and server failures are normal application states."),
        ("What should be pinned and reviewed?", ["The jQuery version and dependencies", "Any URL without a checksum", "Nothing"], "The jQuery version and dependencies", "Pinning makes behavior and security reviewable."),
    ]

def seed_jquery_course(db, course):
    course.title = "jQuery — From Zero to Advanced"
    course.short_description = "A free modern jQuery 4.x course covering DOM, events, AJAX, plugins, WordPress integration, security, performance, and interactive projects."
    course.description = "Learn jQuery from selectors and DOM updates through events, AJAX, JSON, plugins, WordPress integration, security, performance, and an accessible final project."
    course.level, course.status, course.published = "advanced", "published", True
    course.outcomes = "Use modern jQuery selectors and traversal|Build accessible interactive components|Handle AJAX, JSON, and failures safely|Create reusable plugins and WordPress integrations|Debug and secure browser applications"
    course.requirements = "Basic HTML, CSS, and JavaScript. JavaScript Programming is the recommended prerequisite. Target modern jQuery 4.x; review official migration notes for jQuery 3.x applications."
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
            code = "$(function () {\n  $(\"#demo\").text(\"" + _slug(title) + " ready\");\n});"
            specs = [{"title": title, "topic": topic, "code": code, "theory": f"This foundation lesson explains {topic}. Apply the pattern to a small accessible feature, then test it with missing data, keyboard input, and network failure where relevant.", "syntax": "$(function () { /* initialize a component */ });", "mm": f"ဤ lesson တွင် {topic} ကို လေ့လာပြီး accessible feature အဖြစ် အသုံးချပါမည်။"}]
        for lesson_index, spec in enumerate(specs, 1):
            title, topic = spec["title"], spec["topic"]
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm=""); db.add(lesson); db.flush()
            previous = "Basic HTML, CSS, and JavaScript; JavaScript Programming is recommended." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
            next_title = "Continue to the next lesson." if module_index < 24 else "Continue to the final capstone review."
            lesson.title, lesson.slug = title, slug
            lesson.content_en = _content(title, topic, spec["theory"], spec["syntax"], spec["code"], spec["mm"], previous, next_title)
            lesson.content_mm = f"{title} ကို English theory နှင့်အတူ လေ့လာနိုင်ပါသည်။\n\n{spec['mm']}"
            lesson.description, lesson.duration_minutes = spec["theory"], 35
            lesson.status, lesson.published = "published", True; authored.append(lesson)
            examples = list(db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all())
            example = examples[0] if examples else None
            for duplicate in examples[1:]: db.delete(duplicate)
            if not example:
                db.add(CodeExample(lesson_id=lesson.id, title=f"{title} example", language="jquery", filename="app.js", code=spec["code"], description="Read-only example. Use a pinned, reviewed jQuery build in a local page; hosted arbitrary execution is disabled.", position=1))
            else:
                example.title, example.language, example.filename, example.code, example.description, example.position = f"{title} example", "jquery", "app.js", spec["code"], "Read-only example. Use a pinned, reviewed jQuery build in a local page; hosted arbitrary execution is disabled.", 1
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz: quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the explanation and retry after studying missed concepts.", status="published"); db.add(quiz); db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(topic), 1):
                values = dict(prompt=prompt, question_type="true_false" if options == ["True", "False"] else "multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                question = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
                if not question: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(question, key, value)
    course.duration_minutes = sum(x.duration_minutes or 35 for x in authored)
    db.flush()
