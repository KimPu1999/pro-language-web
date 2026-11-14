"""Idempotent Bootstrap 5.3 curriculum.

Module 1 is the complete vertical slice. Every later module has an authored
foundation lesson so no published module is empty; deeper projects remain
incremental work rather than being represented as complete.
"""
import json
import re
from sqlalchemy import select
from .models import CourseModule, Lesson, LessonQuiz, QuizQuestion, CodeExample

MODULES = [
    "Introduction to Bootstrap", "Environment Setup & Installation", "Bootstrap Containers & Layout",
    "Bootstrap Grid System", "Responsive Breakpoints", "Spacing Utilities", "Typography & Text Utilities",
    "Colors & Backgrounds", "Display, Flexbox & Position", "Borders, Shadows & Sizing", "Buttons & Button Groups",
    "Cards & Content Components", "Navbar & Navigation", "Forms & Inputs", "Form Validation & Feedback",
    "Tables & Responsive Data", "Alerts, Toasts & Progress", "Dropdowns & Collapse", "Modals & Offcanvas",
    "Accordion & Carousel", "Tooltips, Popovers & Scrollspy", "Bootstrap JavaScript API", "Sass & Theme Customization",
    "CSS Variables & Color Modes", "Accessibility & Best Practices", "Performance & Optimization",
    "Real-World Bootstrap Projects", "Final Capstone & Assessment",
]

MODULE_ONE = [
    ("What Is Bootstrap?", "a responsive component and utility framework", "<div class=\"container py-4\">\n  <h1 class=\"display-5\">Hello, Bootstrap</h1>\n  <p class=\"lead\">Responsive structure with useful defaults.</p>\n</div>", "Bootstrap 5.3.x is a front-end toolkit built from semantic HTML, CSS utilities, components, and optional JavaScript plugins. It accelerates common responsive layouts but does not replace HTML knowledge, accessibility judgment, or custom design decisions. Bootstrap 5 does not require jQuery; its interactive plugins use vanilla JavaScript.", "<div class=\"container\">content</div>", "Bootstrap သည် responsive layout နှင့် UI components များကို စနစ်တကျ တည်ဆောက်ရန် အသုံးပြုသော front-end toolkit ဖြစ်သည်။"),
    ("Environment Setup and Version Pinning", "HTML files, local assets, and Bootstrap 5.3.x compatibility", "<link rel=\"stylesheet\" href=\"/vendor/bootstrap-5.3.x.min.css\">\n<script src=\"/vendor/bootstrap-5.3.x.bundle.min.js\" defer></script>", "Pin and review the exact Bootstrap 5.3.x build used by a project. Keep CSS and the matching bundle version together, document browser support, and avoid mixing Bootstrap 3 or 4 markup with Bootstrap 5 defaults. A local or approved asset is safer than an unknown runtime dependency.", "<link rel=\"stylesheet\" href=\"bootstrap.min.css\">", "Bootstrap version ကို pin လုပ်ပြီး CSS နှင့် JavaScript bundle ကို matching version ဖြင့် အသုံးပြုပါ။"),
    ("Containers and Responsive Structure", "content width and page rhythm", "<div class=\"container py-5\">\n  <section aria-labelledby=\"intro-title\">\n    <h2 id=\"intro-title\">A readable section</h2>\n  </section>\n</div>", "Containers center content and apply responsive horizontal padding. Use container-fluid when content should span the viewport. Pair structural HTML with spacing utilities, and keep a readable measure instead of letting every paragraph stretch across a large screen.", ".container | .container-fluid | .container-{breakpoint}", "container များသည် content width နှင့် responsive horizontal padding ကို စီမံပေးသည်။"),
    ("Grid Concepts", "rows, columns, and mobile-first layout", "<div class=\"container\">\n  <div class=\"row g-3\">\n    <div class=\"col-12 col-md-6\">A</div>\n    <div class=\"col-12 col-md-6\">B</div>\n  </div>\n</div>", "The Bootstrap grid uses a container, row, and columns. The example is one column on narrow screens and two equal columns from the md breakpoint. Start with the small-screen layout, then add constraints only when the content needs them.", ".row | .col-12 | .col-md-6 | .g-3", "Bootstrap grid သည် container၊ row နှင့် columns တို့ကို ပေါင်းစပ်ပြီး mobile-first layout တည်ဆောက်သည်။"),
    ("Breakpoints and Mobile-First Thinking", "responsive behavior at content-driven thresholds", "<div class=\"d-none d-md-block\">Visible from medium screens</div>\n<div class=\"d-md-none\">Visible below medium screens</div>", "Breakpoints are named ranges, not device promises. Bootstrap 5.3 provides xs, sm, md, lg, xl, and xxl ranges. Choose a breakpoint when content needs a new layout, test intermediate widths, and never hide essential information only because a viewport is narrow.", ".d-none | .d-md-block | .d-md-none", "Breakpoint များကို device အလိုက်မဟုတ်ဘဲ content လိုအပ်ချက်အလိုက် ရွေးချယ်ပါ။"),
    ("Spacing Utilities and Visual Rhythm", "margin, padding, and consistent spacing", "<article class=\"p-4 mb-3 rounded-3 shadow-sm\">\n  <h2 class=\"mb-2\">A clear card</h2>\n  <p class=\"mb-0\">Spacing creates hierarchy.</p>\n</article>", "Spacing utilities use a predictable scale and responsive variants. Prefer a small set of consistent values instead of arbitrary inline styles. Check text zoom and long translations so spacing does not hide content or create horizontal overflow.", ".p-4 | .mb-3 | .gap-2 | .mx-auto", "Spacing utility များသည် hierarchy နှင့် readability ကို တိုးတက်စေသည်။"),
    ("Module 1 Review and Assessment", "a responsive accessible Bootstrap page", "<main class=\"container py-4\">\n  <div class=\"row g-4 align-items-center\">\n    <div class=\"col-12 col-lg-8\"><h1>Learn responsively</h1></div>\n    <div class=\"col-12 col-lg-4\"><a class=\"btn btn-primary\" href=\"#start\">Start</a></div>\n  </div>\n</main>", "This review combines a container, row, responsive columns, spacing, and an accessible link styled as a button. Verify the focus state, heading order, contrast, reading order, and behavior at narrow widths before moving to components.", ".container | .row | .col-12 | .col-lg-8 | .btn", "Module 1 တွင် container၊ grid၊ breakpoint၊ spacing နှင့် accessible button တို့ကို ပြန်လည်လေ့လာပါမည်။"),
]

GENERAL = [
    ("Install Bootstrap 5.3.x", "reviewed assets and compatibility"), ("Containers in Real Pages", "readable page structure"),
    ("Rows and Columns", "mobile-first grid composition"), ("Breakpoint Strategy", "content-driven responsive changes"),
    ("Spacing Scale", "consistent layout rhythm"), ("Type Scale and Text Utilities", "readable hierarchy"),
    ("Color Utilities", "meaningful color and contrast"), ("Flex and Position Utilities", "alignment and placement"),
    ("Borders and Sizing", "surface and dimension controls"), ("Buttons and Focus", "action hierarchy"),
    ("Cards and Content", "structured information blocks"), ("Navbar Structure", "responsive navigation"),
    ("Form Controls", "labeled and usable input"), ("Validation Feedback", "clear error states"),
    ("Responsive Tables", "data that works on small screens"), ("Alerts and Progress", "status communication"),
    ("Dropdowns and Collapse", "disclosure interaction"), ("Modal and Offcanvas", "focus-aware overlays"),
    ("Accordion and Carousel", "content disclosure and motion"), ("Tooltips and Scrollspy", "context and navigation"),
    ("Bootstrap JavaScript API", "explicit component behavior"), ("Sass Customization", "maintainable theme tokens"),
    ("Color Modes and Variables", "light and dark design"), ("Accessible Bootstrap", "semantic and keyboard-ready UI"),
    ("Performance Review", "small assets and measured rendering"), ("Project Architecture", "a maintainable Bootstrap site"),
    ("Final Capstone Planning", "a complete responsive product site"),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(title, topic, theory, syntax, code, mm, previous, next_title):
    return f"""Introduction
{title} introduces {topic} using Bootstrap 5.3.x, HTML5, CSS3, and JavaScript.

Learning objectives
- Explain {topic} and choose the right Bootstrap utility or component.
- Build mobile-first markup with meaningful semantics and responsive behavior.
- Test layout, focus, contrast, motion, and long content at multiple widths.

Prerequisites
{previous}

Detailed theory
{theory}

Bootstrap syntax
{syntax}

HTML/CSS/JS example
```html
{code}
```

Expected result
The example produces the documented responsive structure or state. Test it at narrow, medium, and wide widths and verify keyboard focus and reading order.

Live responsive preview
Hosted arbitrary HTML/CSS/JavaScript execution is disabled until a verified isolated preview is available. Copy the example into a local page with the pinned Bootstrap 5.3.x CSS and matching bundle.

Line-by-line explanation
The semantic container establishes the content boundary. Rows and columns describe the layout relationship. Utility classes add one focused presentation rule, while labels, headings, and links preserve meaning for assistive technology.

Visual layout explanation
Bootstrap uses a mobile-first grid. A column that starts at col-12 stacks on small screens; a col-md or col-lg rule changes the layout only after its breakpoint. Spacing utilities provide the visual separation without changing document meaning.

Common mistakes
- Mixing Bootstrap 3/4 class names with Bootstrap 5 markup.
- Treating breakpoints as device-specific promises.
- Using color alone to communicate status.
- Removing focus outlines or hiding essential content on mobile.
- Loading mismatched CSS and JavaScript bundle versions.

Accessibility considerations
Use semantic landmarks, a logical heading hierarchy, visible focus, labels for controls, sufficient contrast, reduced-motion support, keyboard-operable disclosures, and readable content at 200% zoom.

Best practices
Use Bootstrap utilities deliberately, keep custom CSS small and namespaced, pin the 5.3.x release, validate markup, test real content, and prefer native HTML behavior before adding JavaScript.

Practice exercises
- Easy: reproduce the example and change one responsive class.
- Medium: add a keyboard-accessible state and a narrow-screen layout.
- Challenge: implement the same layout with minimal custom CSS and document the breakpoint decision.
Hints: start with semantics, then structure, then utilities, then component behavior.
Guided solution: verify the markup at each width before adding another class.

Quiz
1. What is the recommended grid progression? Container, row, then columns.
2. True or false: Bootstrap 5 requires jQuery for its JavaScript plugins. False.
3. What should be checked when loading Bootstrap assets? Matching pinned CSS and bundle versions.
4. What should not communicate meaning alone? Color.

Summary
You can now explain {topic}, use Bootstrap 5.3.x safely, and validate responsive accessible behavior.

Next lesson
{next_title}
"""

def _questions(topic):
    return [
        (f"Which practice best supports {topic}?", ["Semantic mobile-first structure", "Random device breakpoints", "Removing focus styles"], "Semantic mobile-first structure", "Semantics and content-driven breakpoints improve accessibility and maintainability."),
        ("True or false: Bootstrap 5 requires jQuery.", ["True", "False"], "False", "Bootstrap 5 JavaScript plugins use vanilla JavaScript."),
        ("Which class pattern creates a stacked-to-two-column layout?", ["col-12 col-md-6", "col-only", "hidden-all"], "col-12 col-md-6", "The first rule stacks; the md rule changes the layout at the medium breakpoint."),
        ("What should be pinned?", ["The Bootstrap 5.3.x asset version", "An unknown CDN response", "No dependencies"], "The Bootstrap 5.3.x asset version", "Pinned assets make compatibility and security reviewable."),
    ]

def seed_bootstrap_course(db, course):
    course.title = "Bootstrap 5 — From Zero to Professional Responsive Web Design"
    course.short_description = "A free Bootstrap 5.3.x course covering responsive layout, utilities, components, accessibility, themes, performance, and real projects."
    course.description = "Learn Bootstrap 5.3.x with HTML5, CSS3, and JavaScript through responsive layouts, components, forms, accessibility, color modes, performance, and a final capstone."
    course.level, course.status, course.published = "advanced", "published", True
    course.outcomes = "Build mobile-first responsive layouts|Use Bootstrap utilities and components|Create accessible forms and navigation|Customize themes and color modes|Optimize and validate professional Bootstrap sites"
    course.requirements = "Basic HTML and CSS; JavaScript is helpful for interactive components. HTML and CSS courses are recommended prerequisites. Target Bootstrap 5.3.x and use the matching JavaScript bundle."
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
            code = f"<div class=\"container py-4\">\n  <div class=\"alert alert-primary\" role=\"status\">{_slug(title)} ready</div>\n</div>"
            specs = [{"title": title, "topic": topic, "code": code, "theory": f"This foundation lesson explains {topic}. Apply it to a small responsive page, then test keyboard behavior, contrast, long content, and narrow widths before shipping.", "syntax": "<div class=\"container\">content</div>", "mm": f"ဤ lesson တွင် {topic} ကို responsive page အဖြစ် လေ့လာပါမည်။"}]
        for lesson_index, spec in enumerate(specs, 1):
            title, topic = spec["title"], spec["topic"]
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm=""); db.add(lesson); db.flush()
            previous = "Basic HTML and CSS; JavaScript is helpful. HTML and CSS courses are recommended." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
            next_title = "Continue to the next lesson." if module_index < 28 else "Continue to the final capstone review."
            lesson.title, lesson.slug = title, slug
            lesson.content_en = _content(title, topic, spec["theory"], spec["syntax"], spec["code"], spec["mm"], previous, next_title)
            lesson.content_mm = f"{title} ကို English theory နှင့်အတူ လေ့လာနိုင်ပါသည်။\n\n{spec['mm']}"
            lesson.description, lesson.duration_minutes = spec["theory"], 35
            lesson.status, lesson.published = "published", True; authored.append(lesson)
            examples = list(db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all())
            example = examples[0] if examples else None
            for duplicate in examples[1:]: db.delete(duplicate)
            if not example:
                db.add(CodeExample(lesson_id=lesson.id, title=f"{title} example", language="html", filename="index.html", code=spec["code"], description="Read-only Bootstrap example. Use matching, pinned Bootstrap 5.3.x assets in a local page.", position=1))
            else:
                example.title, example.language, example.filename, example.code, example.description, example.position = f"{title} example", "html", "index.html", spec["code"], "Read-only Bootstrap example. Use matching, pinned Bootstrap 5.3.x assets in a local page.", 1
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz: quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the responsive and accessibility explanations, then retry missed concepts.", status="published"); db.add(quiz); db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(topic), 1):
                values = dict(prompt=prompt, question_type="true_false" if options == ["True", "False"] else "multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                question = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
                if not question: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(question, key, value)
    course.duration_minutes = sum(x.duration_minutes or 35 for x in authored)
    db.flush()
