"""Idempotent authored CSS course curriculum for the free CSS track."""
import json
import re
from sqlalchemy import select
from .models import CourseModule, Lesson, LessonQuiz, QuizQuestion, CodeExample

MODULES = [
    "Introduction to CSS", "CSS Environment Setup", "CSS Syntax & Integration", "CSS Selectors",
    "Colors & Backgrounds", "CSS Units & Values", "Typography & Fonts", "CSS Box Model",
    "Display & Visibility", "CSS Positioning", "CSS Flexbox", "CSS Grid", "Responsive Web Design",
    "Advanced Selectors & Cascade", "Pseudo-Classes & Pseudo-Elements", "Transitions & Transforms",
    "CSS Animations", "CSS Custom Properties", "Modern CSS Features", "Forms & UI Components",
    "Accessibility & Responsive UI", "CSS Architecture & Performance", "Real-World CSS Projects",
    "Final CSS Capstone & Assessment",
]

MODULE_ONE = [
    ("What Is CSS?", "the role of presentation in the web", "<main class=\"intro\">\n  <h1>Learn CSS</h1>\n  <p>CSS controls presentation while HTML describes meaning.</p>\n</main>", ".intro { color: #264de4; }\n.intro p { line-height: 1.6; }", "CSS (Cascading Style Sheets) describes how a document should look and lay out. HTML supplies structure, CSS supplies presentation, and JavaScript supplies behavior. Separating these responsibilities keeps a page understandable and reusable.", "selector { property: value; }", "CSS သည် HTML document ၏ presentation နှင့် layout ကို သတ်မှတ်ပေးသော language ဖြစ်သည်။ HTML က structure၊ CSS က appearance ကို တာဝန်ယူသည်။"),
    ("CSS Environment Setup", "editors, browsers, and developer tools", "<!doctype html>\n<html lang=\"en\">\n  <head><link rel=\"stylesheet\" href=\"styles.css\"></head>\n  <body><h1>Ready for CSS</h1></body>\n</html>", "body {\n  font-family: system-ui, sans-serif;\n  margin: 2rem;\n}", "A CSS workflow needs a text editor, a modern browser, and developer tools. Keep HTML and CSS in a project folder, load the stylesheet with link, save changes, then refresh or use the tools to inspect computed styles.", "<link rel=\"stylesheet\" href=\"styles.css\">; selector { property: value; }", "Editor၊ browser နှင့် developer tools များဖြင့် CSS လေ့လာနိုင်သည်။ CSS file ကို link element ဖြင့် ချိတ်ဆက်ပါ။"),
    ("CSS Syntax and Rules", "declarations and rule blocks", "<p class=\"notice\">A rule targets an element.</p>", ".notice {\n  background-color: #eef2ff;\n  color: #1e1b4b;\n  padding: 1rem;\n}", "A rule combines a selector with a declaration block. Each declaration has a property, a colon, a value, and usually a semicolon. Whitespace and comments can improve readability without changing the result.", ".notice { property: value; }", "Selector က target ကိုရွေးပြီး declaration များက style property နှင့် value ကို သတ်မှတ်သည်။"),
    ("HTML and CSS Integration", "external, internal, and inline styles", "<link rel=\"stylesheet\" href=\"styles.css\">\n<h1 class=\"page-title\">A maintainable page</h1>", ".page-title {\n  color: #264de4;\n  margin-block: 0 1rem;\n}", "External stylesheets are the preferred default for maintainability and caching. Internal style blocks can be useful for a small document, while inline style is best reserved for carefully controlled one-off values.", "<link>; <style>; style=\"property: value\"", "External stylesheet သည် maintainable ဖြစ်၍ page များစွာတွင် ပြန်လည်အသုံးပြုနိုင်သည်။"),
    ("The Cascade and Inheritance", "why a final style wins", "<article class=\"card\"><h2>CSS rules</h2><p>Some properties inherit.</p></article>", "body { color: #172033; }\n.card { color: #264de4; }\n.card h2 { color: #0f172a; }", "The cascade resolves competing declarations using origin, importance, layers, specificity, and source order. Inherited properties such as color can flow from a parent; layout properties such as margin usually do not inherit.", "selector specificity -> source order; inherited property", "Rule များတိုက်ဆိုင်သောအခါ cascade က ဘယ် rule အနိုင်ရမလဲ ဆုံးဖြတ်သည်။"),
    ("CSS Values and the Browser", "properties, values, and computed styles", "<div class=\"meter\" aria-label=\"Progress: 60 percent\"></div>", ".meter {\n  width: 60%;\n  height: 1rem;\n  background: #818cf8;\n  border-radius: 999px;\n}", "Browsers parse declarations into computed styles. Values can be lengths, colors, functions, keywords, percentages, or custom properties. Developer tools show the winning rule and help diagnose overridden declarations.", "width: 60%; background: #818cf8; border-radius: 999px;", "Browser က property/value များကို parse လုပ်ပြီး computed style အဖြစ် အသုံးပြုသည်။"),
    ("Module 1 Review and Assessment", "a small accessible CSS component", "<section class=\"summary-card\" aria-labelledby=\"summary-title\">\n  <h2 id=\"summary-title\">CSS foundations</h2>\n  <p>Structure first, presentation second.</p>\n</section>", ".summary-card {\n  max-width: 32rem;\n  padding: 1.5rem;\n  color: #f8fafc;\n  background: #131f36;\n  border: 2px solid #818cf8;\n  border-radius: 1rem;\n}\n.summary-card:focus-within { outline: 3px solid #fbbf24; }", "A useful first component combines semantic HTML with a readable, focused CSS rule set. Review selectors, declarations, the cascade, inheritance, and the separation between document meaning and presentation before moving to layout.", ".summary-card { property: value; } .summary-card:focus-within { outline: ...; }", "Module 1 တွင် selector၊ declaration၊ cascade၊ inheritance နှင့် accessibility အခြေခံများကို ပြန်လည်သုံးသပ်ပါ။"),
]

MODULE_LESSONS = [
    [("Install a CSS Workspace", "files, folders, and stylesheet linking", "<h1 class=\"title\">Workspace</h1>", ".title { color: #264de4; }"), ("Inspect Computed Styles", "browser developer tools", "<button class=\"action\">Inspect me</button>", ".action { padding: .75rem 1rem; border: 2px solid currentColor; }")],
    [("Writing CSS Rules", "selectors and declaration blocks", "<p class=\"message\">A CSS rule has a target and declarations.</p>", ".message { color: #1d4ed8; }"), ("External, Internal, and Inline CSS", "stylesheet integration choices", "<h1 class=\"headline\">Separate content from presentation</h1>", ".headline { font-size: 2rem; }")],
    [("Type, Class, and ID Selectors", "common selector forms", "<p id=\"lead\" class=\"copy\">Selector practice</p>", "p { margin: 0; }\n.copy { color: #264de4; }\n#lead { font-weight: 700; }")],
    [("Color Notation", "hex, rgb, hsl, and contrast", "<div class=\"swatch\">Accessible color</div>", ".swatch { color: #0f172a; background: #a5b4fc; padding: 1rem; }")],
    [("Length Units", "rem, em, percent, and viewport units", "<div class=\"panel\">Flexible sizing</div>", ".panel { width: min(90%, 30rem); padding: 2rem; }")],
    [("Font Stacks and Readability", "font-family, size, and line-height", "<p class=\"reading\">Readable text supports every learner.</p>", ".reading { max-width: 60ch; font: 1rem/1.6 system-ui, sans-serif; }")],
    [("Margin, Border, Padding, and Content", "the four box model areas", "<div class=\"box\">Box model</div>", ".box { margin: 1rem; border: 2px solid #6366f1; padding: 1rem; }")],
    [("Block, Inline, and Inline-Block", "display behavior", "<span class=\"tag\">Inline tag</span><div class=\"block\">Block</div>", ".tag { display: inline-block; padding: .25rem .5rem; }\n.block { display: block; }")],
    [("Position Schemes", "static, relative, absolute, fixed, sticky", "<div class=\"badge\">New</div>", ".badge { position: relative; inset-inline-start: .5rem; }")],
    [("Flex Containers and Items", "one-dimensional layout", "<div class=\"actions\"><button>Save</button><button>Cancel</button></div>", ".actions { display: flex; gap: .75rem; align-items: center; }")],
    [("Grid Tracks and Areas", "two-dimensional layout", "<div class=\"grid\"><div>A</div><div>B</div><div>C</div></div>", ".grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }")],
    [("Media Queries", "responsive breakpoints", "<main class=\"layout\"><aside>Menu</aside><article>Content</article></main>", ".layout { display: grid; gap: 1rem; }\n@media (min-width: 48rem) { .layout { grid-template-columns: 14rem 1fr; } }")],
    [("Specificity and Layers", "predictable cascade control", "<p class=\"note\">Specificity is measurable.</p>", "@layer base, components;\n@layer components { .note { color: #264de4; } }")],
    [("Interactive Pseudo-Classes", "hover, focus, checked, and disabled", "<button class=\"button\">Focus me</button>", ".button:focus-visible { outline: 3px solid #fbbf24; }")],
    [("Transitions and Transforms", "smooth state changes", "<button class=\"lift\">Hover safely</button>", ".lift { transition: transform .2s ease; }\n.lift:hover { transform: translateY(-2px); }")],
    [("Keyframes and Motion", "animation timelines", "<div class=\"pulse\" aria-label=\"Loading\"></div>", "@keyframes pulse { to { opacity: .35; } }\n.pulse { animation: pulse 1s ease-in-out infinite alternate; }")],
    [("Custom Properties", "design tokens and fallbacks", "<button class=\"token-button\">Token button</button>", ":root { --brand: #264de4; }\n.token-button { color: white; background: var(--brand, navy); }")],
    [("Container Queries and Logical Properties", "modern component-aware CSS", "<article class=\"component\"><h2>Adaptive card</h2></article>", ".component { container-type: inline-size; padding-inline: 1rem; }\n@container (min-width: 30rem) { .component { display: grid; } }")],
    [("Accessible Form Controls", "focus, labels, and resilient controls", "<form class=\"form\"><label for=\"email\">Email</label><input id=\"email\" type=\"email\"><button type=\"submit\">Join</button></form>", ".form { display: grid; gap: .75rem; max-width: 28rem; }\n.form :focus-visible { outline: 3px solid #fbbf24; outline-offset: 2px; }")],
    [("Responsive UI Patterns", "accessible layouts across screen sizes", "<main class=\"responsive\"><h1>Responsive UI</h1><p>Content stays readable.</p></main>", ".responsive { width: min(92%, 70rem); margin-inline: auto; padding-block: clamp(1.5rem, 5vw, 4rem); }")],
    [("CSS Architecture and Performance", "layers, containment, and maintainable styles", "<article class=\"component\"><h2>Component</h2></article>", "@layer reset, base, components;\n@layer components { .component { contain: content; } }")],
]

PROJECTS = ["Profile Card", "Styled Buttons", "Login Form", "Responsive Navbar", "Product Card", "Pricing Cards", "Image Gallery", "Blog Layout", "Portfolio Homepage", "Landing Page", "Admin Dashboard", "Responsive Website Capstone"]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(title, topic, html, css, theory, syntax, mm, previous, next_title):
    return f"""Introduction
{title} introduces {topic} through a small, inspectable component.

Learning objectives
- Explain {topic} in your own words.
- Write readable CSS using modern, maintainable patterns.
- Preview the result and check keyboard accessibility.

Prerequisites
{previous}

Detailed theory
{theory} CSS rules are matched against the HTML document tree. The browser resolves the cascade, computes values, and paints the result. Prefer semantic HTML, external stylesheets, logical properties, and progressive enhancement.

CSS syntax
{syntax}

HTML example
```html
{html}
```

CSS example
```css
{css}
```

Browser preview
The CSS playground renders the HTML and CSS inside a sandboxed iframe. Scripts are disabled and the preview cannot access the parent application.

Line-by-line explanation
The HTML supplies the content and class hooks. The selector identifies the intended element. Each declaration names one property and value; the browser applies the winning declarations after resolving the cascade. Layout and spacing should be tested at more than one viewport width.

Visual explanation
HTML document → selector matching → cascade and inheritance → computed style → layout → paint. Use developer tools to inspect each stage rather than guessing.

Common mistakes
- Writing a selector that does not match the intended element.
- Using fixed pixels everywhere instead of scalable units and constraints.
- Removing focus outlines or relying on hover for an essential action.
- Creating animation without a reduced-motion alternative.

Best practices
Use semantic HTML, keep selectors focused, prefer class and component-level styles, use custom properties for repeated tokens, use logical properties for international layouts, and test keyboard navigation and contrast.

Practice exercises
- Easy: reproduce the example and change one property.
- Medium: add a second component state and explain the cascade.
- Challenge: make the component responsive and add a visible focus state.
Hints: inspect the matched rules first; change one declaration at a time.
Guided solution: start with semantic HTML, add the smallest selector, preview at narrow and wide widths, then add the accessibility check.

Summary
You can now explain {topic}, write the matching CSS, preview it safely, and evaluate its responsive and accessible behavior.

Next lesson
{next_title}

Myanmar explanation
{mm}
"""

def _questions(title, topic):
    return [
        (f"What is the main CSS idea in {title}?", [f"Use {topic} intentionally", "Put every style inline", "Ignore the cascade"], f"Use {topic} intentionally", "CSS is easier to maintain when its rules and layout choices have a clear purpose."),
        ("True or false: a keyboard user should be able to see focus on interactive controls.", ["True", "False"], "True", "Visible focus is an important accessibility requirement."),
        ("Which pattern is recommended?", ["Use semantic HTML and focused CSS selectors", "Remove focus outlines", "Use fixed widths for every device"], "Use semantic HTML and focused CSS selectors", "Semantic structure and focused rules support maintainability and accessibility."),
        ("Which feature should respect reduced motion?", ["Animations and transitions", "Text content", "HTML headings"], "Animations and transitions", "Users can request reduced motion, so non-essential motion should have a safe alternative."),
    ]

def seed_css_course(db, course):
    course.title = "CSS — From Zero to Professional Web Design"
    course.short_description = "A free beginner-to-advanced CSS course covering selectors, layout, responsive design, animation, accessibility, architecture, and real projects."
    course.description = "Learn modern CSS from syntax and selectors through Flexbox, Grid, responsive UI, motion, custom properties, performance, accessibility, and professional projects."
    # Keep the catalog's established beginner/intermediate/advanced filter
    # values compatible while the description communicates the full range.
    course.level, course.status, course.published = "beginner", "published", True
    course.outcomes = "Write maintainable CSS rules|Build responsive layouts with Flexbox and Grid|Use the cascade and specificity deliberately|Create accessible forms and UI components|Design and optimize real websites"
    course.requirements = "Basic HTML knowledge, a text editor, and a modern browser; no prior CSS experience is required."
    authored = []
    for module_index, module_title in enumerate(MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_index))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_index); db.add(module); db.flush()
        module.title = module_title
        if module_index == 1:
            specs = MODULE_ONE
        elif module_index == 23:
            specs = [(name, "a guided CSS project", f"<main class=\"project\"><h1>{name}</h1><p>Build a responsive interface.</p></main>", ".project { max-width: 70rem; margin-inline: auto; padding: 1rem; }", "A real project combines component structure, layout, responsive behavior, and accessibility checks.", ".project { property: value; }", "Project တွင် layout၊ responsive behavior နှင့် accessibility ကို စစ်ဆေးပါ။") for name in PROJECTS]
        elif module_index == 24:
            specs = [("Capstone Plan and Rubric", "planning a professional CSS system", "<main class=\"capstone\"><h1>Capstone plan</h1><p>Structure, layout, states, and checks.</p></main>", ".capstone { container: inline-size; padding: 2rem; }", "Plan the content model, design tokens, responsive states, interaction states, and validation checklist before styling the final site.", ".capstone { property: value; }", "Final project မစမီ content၊ token၊ responsive state နှင့် validation ကို စီစဉ်ပါ။"), ("Responsive Website Capstone", "combining modern CSS techniques", "<header class=\"site-header\"><h1>My CSS website</h1></header><main class=\"site-main\"><p>Accessible, responsive, and maintainable.</p></main>", ":root { --brand: #264de4; }\n.site-main { width: min(92%, 70rem); margin-inline: auto; padding-block: 3rem; }", "Combine semantic HTML, custom properties, resilient layout, responsive rules, visible focus, reduced motion, and a final validation pass into a useful website.", ":root { --token: value; } .site-main { property: value; }", "Capstone တွင် semantic HTML၊ custom properties၊ responsive layout နှင့် accessibility ကို ပေါင်းစပ်ပါ။")]
        else:
            pair = MODULE_LESSONS[module_index - 2]
            specs = [(title, topic, html, css, f"This lesson explains {topic} and shows how it supports a clear, resilient interface.", f"Use the relevant CSS feature deliberately: {topic}.", "ဒီ lesson တွင် CSS feature ကို အဓိပ္ပါယ်ရှိစွာ အသုံးပြုနည်းကို လေ့လာပါမည်။") for title, topic, html, css in pair]
        for lesson_index, (title, topic, html, css, theory, syntax, mm) in enumerate(specs, 1):
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm=""); db.add(lesson); db.flush()
            lesson.title, lesson.slug = title, slug
            previous = "Basic HTML knowledge is helpful; no CSS experience is required." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
            next_title = "Continue to the next module." if module_index == 24 else "Continue with the next lesson."
            lesson.content_en = _content(title, topic, html, css, theory, syntax, mm, previous, next_title)
            lesson.content_mm = f"{title} ကို English theory နှင့်အတူ လေ့လာနိုင်ပါသည်။\n\n{mm}"
            lesson.description, lesson.duration_minutes = theory, 35 if module_index == 19 else 30
            lesson.status, lesson.published = "published", True; authored.append(lesson)
            examples = list(db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all())
            while len(examples) < 2:
                examples.append(None)
            values = [("HTML structure", "html", "index.html", html, "The semantic markup rendered by the CSS preview."), ("CSS stylesheet", "css", "styles.css", css, "The stylesheet applied inside the CSS preview.")]
            for position, (label, language, filename, code, description) in enumerate(values, 1):
                example = examples[position - 1]
                if not example: db.add(CodeExample(lesson_id=lesson.id, title=f"{title} — {label}", language=language, filename=filename, code=code, description=description, position=position))
                else: example.title, example.language, example.filename, example.code, example.description, example.position = f"{title} — {label}", language, filename, code, description, position
            for duplicate in examples[2:]:
                if duplicate: db.delete(duplicate)
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz: quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the explanations and retry after studying missed concepts.", status="published"); db.add(quiz); db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(title, topic), 1):
                q = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position)); values = dict(prompt=prompt, question_type="true_false" if options == ["True", "False"] else "multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                if not q: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(q, key, value)
    course.duration_minutes = sum(x.duration_minutes or 30 for x in authored); db.flush()
