"""Idempotent Tailwind CSS v4 vertical-slice course content seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

PLANNED_MODULES = [
    "Introduction to Tailwind CSS", "HTML & CSS Prerequisites", "Tailwind CSS v4 Installation", "Project Structure & Configuration",
    "Utility Classes Fundamentals", "Colors & Backgrounds", "Spacing & Sizing", "Typography Fundamentals", "Borders, Radius & Shadows",
    "Display & Positioning", "Flexbox Layout", "CSS Grid Layout", "Responsive Design", "Container Queries", "Overflow, Visibility & Z-Index",
    "Images & Media", "Interactive States", "Pseudo-Classes & Variants", "Dark Mode & Color Schemes", "Transitions & Transforms",
    "Animations & Motion", "Custom Theme Tokens", "Custom Utilities & Variants", "Reusable UI Components", "Navigation & Header Design",
    "Forms & Validation UI", "Tables & Data Display", "Dashboard Layouts", "Landing Pages & Marketing UI", "Tailwind CSS with React",
    "Tailwind CSS with Next.js", "shadcn/ui & Component Libraries", "Advanced Responsive Patterns", "Accessibility & Inclusive UI",
    "Performance & CSS Optimization", "Design Systems & Theming", "Testing & Cross-Browser UI", "Production Deployment & Maintenance",
    "Professional Tailwind CSS Projects", "Final Tailwind CSS Capstone",
]

MODULE_ONE = [
    ("What Tailwind CSS Is", "utility-first styling, composition, and design constraints", '<button class="rounded-lg bg-cyan-600 px-4 py-2 font-semibold text-white hover:bg-cyan-500">Start learning</button>', "html", "Tailwind CSS provides small composable utility classes that map to CSS declarations. Instead of inventing a selector for every component, compose layout, spacing, color, typography, and state directly in markup. Keep a design vocabulary, extract repeated components, and treat class composition as code that needs review and accessibility checks.", "Tailwind CSS သည် CSS declaration သေးသေးများကို utility class အဖြစ်ပေးပြီး markup တွင် compose လုပ်စေသည်။ Repeated UI ကို component အဖြစ်ခွဲပြီး accessibility ကိုစစ်ပါ။", "Recreate a call-to-action with utilities for spacing, color, typography, radius, and hover state.", ("Tailwind CSS ၏ အဓိကအယူအဆက ဘာလဲ?", ["Composable utility classes", "Automatic HTML validation", "A database query language"], "Composable utility classes", "Utilities make styling decisions explicit and composable.")),
    ("Tailwind CSS v4 and CSS-First Configuration", "installation, source scanning, @import, and @theme tokens", "@import \"tailwindcss\";\n\n@theme {\n  --color-brand-500: oklch(0.72 0.16 190);\n  --radius-card: 1rem;\n}", "css", "Tailwind CSS v4 uses a CSS-first approach: import Tailwind and define theme variables with @theme. Source scanning generates only discovered utilities in the controlled build. Legacy v3 tailwind.config.js patterns should be labeled explicitly when teaching migration; do not mix syntax without understanding the version.", "Tailwind CSS v4 တွင် CSS-first `@import` နှင့် `@theme` ကိုအသုံးပြုသည်။ v3 config syntax ကို migration context အဖြစ်သာ label လုပ်ပါ။", "Create a v4 stylesheet with a brand color and card radius token; note the equivalent legacy v3 configuration separately.", ("Tailwind v4 theme token ကို ဘယ်မှာသတ်မှတ်သနည်း?", ["CSS @theme variables", "A SQL table", "A client cookie"], "CSS @theme variables", "v4 encourages CSS-first theme configuration.")),
    ("Utility Classes and Class Composition", "readable class groups, source scanning, and component boundaries", "<article class=\"mx-auto max-w-prose space-y-4 p-6 text-slate-900\">\n  <h2 class=\"text-2xl font-bold\">Course notes</h2>\n</article>", "html", "Utility classes are most useful when their composition reflects a clear component contract. Keep class strings stable enough for source scanning, avoid constructing arbitrary unbounded class names from user input, and use variants or component APIs for controlled differences.", "Utility class များကို component contract ရှင်းလင်းအောင် compose လုပ်ပြီး unbounded runtime class name မတည်ဆောက်ပါနှင့်။", "Group a card's layout, typography, and surface utilities, then extract a reusable component API.", ("Dynamic class generation တွင် ဘာကအရေးကြီးသနည်း?", ["Controlled known classes and a safe build strategy", "Any user string as a class", "Inline script execution"], "Controlled known classes and a safe build strategy", "Known utilities keep builds predictable and previews safe.")),
    ("Colors, Spacing, and Typography", "design tokens, responsive scale, and visual hierarchy", "<div class=\"space-y-3 rounded-xl bg-slate-900 p-6 text-slate-100\">\n  <p class=\"text-sm text-cyan-300\">MODULE 01</p>\n  <h1 class=\"text-3xl font-bold tracking-tight\">Build a clear hierarchy</h1>\n</div>", "html", "Tailwind scales make color, spacing, and typography consistent. Prefer tokens that communicate meaning, maintain contrast, and support light/dark themes. A visually polished UI still needs semantic HTML, readable focus states, text scaling, and content that works without color alone.", "Color၊ spacing နှင့် typography scale များသည် consistency နှင့် hierarchy ကိုပေးသည်။ Contrast၊ focus နှင့် semantic HTML ကိုလည်းစစ်ပါ။", "Build a dark card with a heading, metadata, body, and action using a consistent token scale.", ("Design token ၏ အကျိုးက ဘာလဲ?", ["Consistent and maintainable visual decisions", "Automatic accessibility compliance", "A replacement for semantic HTML"], "Consistent and maintainable visual decisions", "Tokens support consistency but accessibility still needs verification.")),
    ("Responsive and State Variants", "mobile-first breakpoints, hover, focus-visible, and dark mode", "<button class=\"w-full bg-cyan-600 p-3 text-white hover:bg-cyan-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300 sm:w-auto dark:bg-cyan-500\">Save</button>", "html", "Tailwind responsive variants are mobile-first: write the base mobile style and layer sm, md, lg, or custom container variants. State variants should include keyboard-visible focus and disabled behavior, not only hover. Dark mode is a theme decision and must preserve contrast and semantics.", "Responsive variant များသည် mobile-first ဖြစ်ပြီး focus-visible၊ disabled နှင့် dark mode state များကိုပါထည့်သွင်းစဉ်းစားရသည်။", "Add mobile, tablet, hover, focus-visible, disabled, and dark mode states to one accessible button.", ("Mobile-first responsive pattern ဆိုတာ ဘာလဲ?", ["Base styles target small screens, larger variants layer on", "Desktop-only CSS", "A hover-only experience"], "Base styles target small screens, larger variants layer on", "Mobile-first rules establish a usable default before larger breakpoints.")),
    ("Flexbox and Grid Layout", "layout utilities, gaps, alignment, and responsive composition", "<div class=\"grid gap-4 sm:grid-cols-2 lg:grid-cols-3\">\n  <div class=\"rounded-xl bg-slate-800 p-4\">Card</div>\n</div>", "html", "Flexbox is useful for one-dimensional alignment and Grid for explicit rows and columns. Use gap utilities, avoid negative margin hacks when a layout primitive solves the problem, and test content wrapping at real widths. Responsive layout should preserve reading order and keyboard order.", "Flex သည် one-dimensional alignment အတွက်၊ Grid သည် rows/columns အတွက်သင့်တော်သည်။ Content wrapping နှင့် reading order ကိုစစ်ပါ။", "Create a three-card grid that becomes one column on mobile and two columns on tablet.", ("Grid layout အတွက် ဘာကိုအဓိကစစ်သင့်သနည်း?", ["Content flow, gaps, and responsive columns", "Only the desktop screenshot", "Arbitrary unbounded class strings"], "Content flow, gaps, and responsive columns", "Responsive layouts must remain usable as content and width change.")),
    ("Reusable Components and Accessibility", "semantic structure, focus, contrast, and extracting patterns", "function Button({ children }: { children: React.ReactNode }) {\n  return <button className=\"rounded-lg px-4 py-2 focus-visible:ring-2 focus-visible:ring-cyan-300\">{children}</button>;\n}", "tsx", "Tailwind does not replace component design or accessibility. Use semantic buttons and headings, visible focus, sufficient contrast, labels for form controls, reduced-motion preferences, and keyboard-friendly interactions. Extract repeated patterns into components with constrained variants rather than giant unreviewable class strings.", "Tailwind သည် component design နှင့် accessibility ကိုအစားမထိုးပါ။ Semantic element၊ focus၊ contrast၊ label နှင့် reduced motion ကိုသေချာလုပ်ပါ။", "Audit a reusable button for semantics, keyboard focus, disabled state, contrast, and reduced-motion behavior.", ("Accessible Tailwind component တွင် ဘာလိုအပ်သနည်း?", ["Semantic HTML, focus, labels, and contrast", "Color alone for state", "Hover without keyboard support"], "Semantic HTML, focus, labels, and contrast", "Utility styling must be paired with accessible interaction semantics.")),
    ("First Tailwind UI Workflow", "preview, controlled rendering, build checks, and safe delivery", "@import \"tailwindcss\";\n\n.card {\n  @apply rounded-2xl border border-slate-700 bg-slate-900 p-6;\n}", "css", "A professional workflow uses a controlled Tailwind v4 build, stable source scanning, semantic markup, responsive preview, accessibility checks, and production CSS inspection. The Academy playground renders predefined templates and does not inject untrusted HTML or JavaScript into the privileged platform context.", "Professional Tailwind workflow တွင် controlled build၊ source scanning၊ semantic markup၊ responsive preview နှင့် accessibility check ပါဝင်သည်။", "Build a small course card, preview mobile/tablet/desktop states, inspect generated class choices, and write a cleanup note.", ("Playground safety အတွက် ဘာကိုသုံးသင့်သနည်း?", ["Controlled templates and isolated previews", "Direct privileged innerHTML with scripts", "Unbounded runtime class generation"], "Controlled templates and isolated previews", "Controlled rendering prevents untrusted markup from reaching the platform context.")),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, example, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "No Tailwind experience is required; basic HTML/CSS helps." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the playground, class explorer, and responsive lab."
    return f"""Introduction
{title} introduces {topic} using Tailwind CSS v4 and controlled UI composition.

Learning objectives
- Explain {topic} and its HTML/CSS rendering boundary.
- Build a responsive, accessible interface with known utility classes.
- Preview changes safely without executing untrusted scripts in the platform context.

Prerequisites
{prerequisite}

UI architecture diagram
semantic HTML -> Tailwind utilities/theme tokens -> controlled build -> responsive browser rendering

Detailed theory
{theory}

Tailwind example ({language}; v4)
{example}

Expected visual result
The preview should preserve hierarchy, readable contrast, keyboard focus, content order, and mobile/tablet/desktop behavior. Exact fonts and browser rendering vary.

Step-by-step implementation
1. Start with semantic HTML and a mobile-first base layout.
2. Add known Tailwind v4 utilities and CSS-first @theme tokens.
3. Add responsive, state, dark-mode, and reduced-motion behavior deliberately.
4. Preview at multiple widths and test keyboard, contrast, text scaling, and empty states.
5. Keep class generation controlled, review build output, and remove disposable examples.

Interactive visualizer
Use the Tailwind playground, class explorer, responsive lab, Flex/Grid lab, theme builder, component builder, and guided lab. They use predefined or controlled previews and do not execute arbitrary scripts.

Common errors
- Using Tailwind v3 config syntax as if it were v4 CSS-first syntax.
- Constructing unbounded runtime class names that the source scanner cannot detect.
- Styling only hover and ignoring keyboard focus or reduced motion.
- Using color alone to communicate state or omitting semantic HTML.

Troubleshooting
Check Tailwind version, source scanning paths, @import/@theme syntax, class spelling, responsive breakpoint, generated CSS, browser width, contrast, and the smallest reproducible component. Reset the controlled preview when state is unclear.

Best practices
- Prefer stable utilities, semantic components, CSS-first v4 tokens, mobile-first layouts, explicit variants, reusable APIs, accessible focus, and measured CSS output.
- Label legacy v3 configuration during migration and do not mix versions accidentally.

Accessibility considerations
Use semantic elements, labels, logical reading order, visible focus-visible states, sufficient contrast, text alternatives, keyboard interaction, and prefers-reduced-motion handling. Tailwind classes do not provide automatic compliance.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Build a responsive course card with a semantic heading, accessible action, Tailwind v4 @theme token, light/dark states, focus-visible ring, and mobile/tablet/desktop preview.

Summary
You can now reason about {topic} with responsive layout, design tokens, accessibility, version boundaries, and safe preview behavior.

Next lesson
{next_lesson}

Myanmar explanation
{mm}
"""


def seed_tailwind_course(db, course):
    course.title = "Tailwind CSS — From Zero to Professional Frontend UI Developer"
    course.short_description = "A free practical path through Tailwind CSS v4, responsive UI, components, React, Next.js, shadcn/ui, accessibility, and design systems."
    course.description = "Learn Tailwind CSS v4 from utility fundamentals through colors, spacing, typography, Flexbox, Grid, responsive design, container queries, states, dark mode, motion, CSS-first theme tokens, reusable components, forms, dashboards, React, Next.js, shadcn/ui, accessibility, performance, testing, and production design systems."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 55
    course.outcomes = "Build responsive accessible UIs with Tailwind CSS v4 utilities, mobile-first variants, Flexbox, Grid, state styles, and dark mode|Use CSS-first @theme tokens, controlled custom utilities, component APIs, React, Next.js, and shadcn/ui patterns|Create forms, dashboards, navigation, tables, landing pages, and reusable design-system primitives|Test focus, contrast, reduced motion, responsive behavior, generated CSS, and production builds"
    course.requirements = "Basic HTML and CSS familiarity are helpful; no Tailwind experience is required."
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
        lesson.duration_minutes, lesson.status, lesson.published = 55, "published", True
        values = {"title": f"{title} example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe Tailwind CSS v4 example; the Academy uses controlled previews and does not execute arbitrary scripts.", "position": 1}
        example_row = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        if not example_row:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example_row, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review Tailwind v4 syntax, responsive behavior, accessibility, controlled classes, and preview safety before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: a hover style alone is sufficient keyboard accessibility.", ["True", "False"], "False", "Keyboard users need visible focus and appropriate semantic interaction."),
            ("Where should a student HTML/JS preview run?", ["A controlled isolated renderer", "Privileged platform innerHTML with scripts", "The production dashboard context"], "A controlled isolated renderer", "Untrusted markup and scripts must not reach the privileged application context."),
        ]
        for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
            row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
            values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
            if not row:
                db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
            else:
                for key, value in values.items():
                    setattr(row, key, value)
    db.flush()
