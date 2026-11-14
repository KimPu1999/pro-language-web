"""Idempotent authored HTML Living Standard curriculum."""
import json
import re
from sqlalchemy import select
from .models import CourseModule, Lesson, LessonQuiz, QuizQuestion, CodeExample

MODULES = [
    "Introduction to HTML", "HTML Environment Setup", "Your First HTML Document",
    "HTML Elements & Attributes", "Headings, Paragraphs & Text", "Links & Navigation",
    "Images & Multimedia", "Lists & Content Organization", "Tables in HTML",
    "HTML Forms — Fundamentals", "HTML Forms — Advanced", "Semantic HTML5",
    "HTML Accessibility", "HTML Metadata & SEO", "Responsive HTML Foundations",
    "Embedded Content & APIs", "HTML Best Practices & Security", "HTML Debugging & Testing",
    "Real-World HTML Mini Projects", "Final HTML Capstone Project",
]

MODULE_ONE = [
    ("What Is HTML?", "documents for the web", "<h1>Learning HTML</h1>\n<p>HTML gives a page structure and meaning.</p>", "HTML is the markup language used to describe the structure and meaning of web content. It is not a programming language: it does not calculate a result by itself, but browsers use its elements to build a document tree.", "<element>content</element>; <element attribute=\"value\">content</element>", "HTML သည် web content ၏ structure နှင့် meaning ကို ဖော်ပြသော markup language ဖြစ်သည်။ Programming language မဟုတ်ပါ။"),
    ("HTML Environment Setup", "editor and browser workflow", "<!doctype html>\n<html lang=\"en\">\n  <body><p>Ready to learn.</p></body>\n</html>", "A text editor, a modern browser, and a folder for your files are enough to begin. Save files with the .html extension, open them in a browser, and refresh after changes. Browser developer tools help inspect the document tree.", "<!doctype html>; file.html; browser refresh; developer tools", "Text editor၊ modern browser နှင့် .html file တစ်ခုရှိရုံဖြင့် စတင်နိုင်သည်။"),
    ("Your First HTML Document", "doctype, html, head, and body", "<!doctype html>\n<html lang=\"en\">\n  <head><meta charset=\"utf-8\"><title>First page</title></head>\n  <body><h1>Hello, web!</h1></body>\n</html>", "A valid document declares the HTML standard, gives the root element a language, and separates metadata in head from visible content in body. The title appears in the browser tab.", "doctype -> html -> head + body; meta charset; title", "doctype၊ head၊ body နှင့် title တို့သည် HTML document ၏ အခြေခံဖွဲ့စည်းပုံ ဖြစ်သည်။"),
    ("Elements and Attributes", "opening tags, closing tags, and attributes", "<p class=\"intro\" id=\"welcome\">Welcome to HTML.</p>", "Elements describe content; attributes add information or behavior to an element. Attribute values should be quoted, names should be meaningful, and nesting must be valid.", "<tag attribute=\"value\">content</tag>", "Element များက content ကို ဖော်ပြပြီး attribute များက အပိုအချက်အလက် ထည့်ပေးသည်။"),
    ("Headings, Paragraphs, and Text", "content hierarchy", "<h1>Course title</h1>\n<h2>Module one</h2>\n<p>Use paragraphs for complete ideas and headings for hierarchy.</p>", "Headings communicate document structure, not just visual size. Use one clear h1 for the page topic, then nest h2 and h3 according to meaning. Paragraphs hold readable blocks of text.", "<h1> through <h6>; <p>; <strong>; <em>", "Heading များသည် အရွယ်အစားအတွက်သာမဟုတ်ဘဲ document hierarchy ကို ဖော်ပြသည်။"),
    ("Links and Navigation", "href and accessible navigation", "<nav aria-label=\"Main navigation\">\n  <a href=\"/courses\">Courses</a>\n  <a href=\"#contact\">Contact</a>\n</nav>", "Links connect documents and locations. Use descriptive link text, valid href values, and nav landmarks for groups of primary navigation links. Do not use a button when the action is navigation.", "<a href=\"destination\">Descriptive link text</a>", "Link များသည် page နှင့် location များကို ချိတ်ဆက်သည်။ Link text ကို အဓိပ္ပါယ်ရှိစွာရေးပါ။"),
    ("Images and Alternative Text", "img, src, and alt", "<figure>\n  <img src=\"profile-placeholder.svg\" alt=\"A learner reviewing an HTML lesson\">\n  <figcaption>Learning with meaningful content.</figcaption>\n</figure>", "Images need a source and meaningful alternative text when they communicate information. Decorative images use an empty alt attribute. The figure and figcaption elements connect an image with its explanation.", "<img src=\"...\" alt=\"...\">; <figure>; <figcaption>", "Meaningful image များတွင် alt text ထည့်ပါ။ Decorative image အတွက် alt=\"\" သုံးပါ။"),
]

MODULE_LESSONS = [
    [("Install an Editor", "files and folders", "<p>Keep related pages in one project folder.</p>"), ("Use Browser Developer Tools", "inspection workflow", "<p>Inspect this element to understand the document tree.</p>")],
    [("Document Structure Practice", "doctype and root structure", "<!doctype html>\n<html lang=\"en\"><head><title>Practice</title></head><body><p>Valid structure.</p></body></html>"), ("Preview and Validate", "refresh and validation", "<main><h1>Check the structure</h1><p>Use the browser and validator together.</p></main>")],
    [("Element Categories", "block and inline meaning", "<section><h2>Section</h2><p>Flow content belongs in a meaningful container.</p></section>"), ("Attributes in Practice", "global attributes", "<p id=\"note\" class=\"notice\" title=\"Helpful note\">Inspect my attributes.</p>")],
    [("Text Emphasis", "strong and em", "<p><strong>Important:</strong> semantic emphasis carries meaning.</p>"), ("Quotes and Code Text", "quotation and code elements", "<blockquote><p>Make the structure meaningful.</p></blockquote><p>Use <code>&lt;code&gt;</code> for code.</p>")],
    [("Relative and Absolute Links", "URL choices", "<a href=\"about.html\">About this site</a><a href=\"https://example.com\">External reference</a>"), ("Navigation Menus", "nav lists and anchors", "<nav><ul><li><a href=\"#one\">Section one</a></li></ul></nav>")],
    [("Responsive Images", "width, height, and picture", "<img src=\"small.jpg\" alt=\"A landscape\" width=\"640\" height=\"360\">"), ("Audio and Video", "media alternatives", "<video controls><source src=\"lesson.mp4\" type=\"video/mp4\"><p>Download the video instead.</p></video>")],
    [("Ordered and Unordered Lists", "list semantics", "<ol><li>Plan</li><li>Write</li><li>Review</li></ol>"), ("Definition and Description Lists", "term and description groups", "<dl><dt>HTML</dt><dd>Markup for document structure.</dd></dl>")],
    [("Table Structure", "caption, rows, and cells", "<table><caption>Study plan</caption><tr><th scope=\"col\">Day</th><th scope=\"col\">Topic</th></tr><tr><td>Mon</td><td>HTML</td></tr></table>"), ("Accessible Data Tables", "headers and scope", "<table><tr><th scope=\"row\">Module 1</th><td>Foundations</td></tr></table>")],
    [("Labels and Text Inputs", "form controls", "<form><label for=\"name\">Name</label><input id=\"name\" name=\"name\" required></form>"), ("Buttons and Form Submission", "button types", "<form action=\"/subscribe\" method=\"post\"><input name=\"email\" type=\"email\" required><button type=\"submit\">Subscribe</button></form>")],
    [("Selects, Checkboxes, and Radios", "choice controls", "<label for=\"topic\">Topic</label><select id=\"topic\" name=\"topic\"><option>HTML</option></select>"), ("Validation Attributes", "required, type, and minlength", "<input type=\"email\" required minlength=\"6\" aria-describedby=\"help\"><small id=\"help\">Use a valid email.</small>")],
    [("Header, Main, and Footer", "landmark elements", "<header><h1>Site</h1></header><main><p>Main content.</p></main><footer>Footer</footer>"), ("Article, Section, and Aside", "content relationships", "<article><h2>Story</h2><p>Independent content.</p></article><aside>Related link</aside>")],
    [("Keyboard-Friendly HTML", "focus and native controls", "<button type=\"button\">A keyboard-accessible action</button>"), ("Accessible Names and Labels", "labels and descriptions", "<label for=\"search\">Search courses</label><input id=\"search\" aria-describedby=\"search-help\"><p id=\"search-help\">Type a course name.</p>")],
    [("Title and Description Metadata", "head metadata", "<head><title>HTML Foundations</title><meta name=\"description\" content=\"Learn semantic HTML.\"></head>"), ("Canonical and Social Metadata", "metadata planning", "<link rel=\"canonical\" href=\"https://example.com/html\"><meta property=\"og:title\" content=\"HTML Foundations\">")],
    [("Mobile Viewport and Content", "mobile-friendly markup", "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><main><p>Content fits small screens.</p></main>"), ("Responsive Image Sources", "source selection", "<picture><source media=\"(min-width: 800px)\" srcset=\"wide.jpg\"><img src=\"small.jpg\" alt=\"Course illustration\"></picture>")],
    [("Iframes and Sandboxed Embeds", "embedded documents", "<iframe title=\"Map preview\" sandbox src=\"about:blank\"></iframe>"), ("Data Attributes and Web APIs", "data-* hooks", "<button data-topic=\"html\" type=\"button\">HTML topic</button>")],
    [("Safe Links and External Content", "security-aware markup", "<a href=\"https://example.com\" rel=\"noopener noreferrer\">Trusted reference</a>"), ("Avoiding Dangerous Markup", "untrusted content", "<p>Render untrusted text as text; do not paste it into innerHTML.</p>")],
    [("Inspecting Markup Errors", "developer tools", "<main><h1>Valid nesting</h1><p>Close elements in the correct order.</p></main>"), ("HTML Validation Checklist", "validation workflow", "<form><label for=\"email\">Email</label><input id=\"email\" type=\"email\"></form>")],
]

PROJECTS = [
    ("Personal Profile Page", "Show a name, biography, skills list, and contact link."), ("Favorite Websites Page", "Organize useful links with descriptive labels."),
    ("Restaurant Menu", "Present categories, prices, and dietary notes."), ("Student Timetable", "Build an accessible table for a weekly schedule."),
    ("Registration Form", "Create labeled controls with native validation."), ("Survey Form", "Collect structured feedback with form controls."),
    ("Blog Article Page", "Use article, header, sections, and figure content."), ("Product Detail Page", "Describe a product with image, facts, and purchase form."),
    ("Multi-Page Portfolio", "Connect pages with consistent navigation."), ("Final HTML Website", "Combine semantic structure, accessibility, metadata, and responsive content."),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(title, topic, code, theory, syntax, mm, previous, next_title):
    return f"""Introduction\n{title} introduces {topic} with a practical, standards-aware HTML example.\n\nLearning objectives\n- Explain {topic} in your own words.\n- Write valid, semantic HTML for a real page.\n- Preview the result and check accessibility before publishing.\n\nPrerequisites\n{previous}\n\nComplete theory\n{theory} HTML describes document meaning and structure; CSS controls presentation and JavaScript controls behavior. Keeping those responsibilities clear makes pages easier to maintain.\n\nHTML syntax\n{syntax}\n\nCode example\n```html\n{code}\n```\n\nBrowser preview\nOpen the example in a modern browser. The learning page's sandboxed preview renders markup without granting the example access to the parent application.\n\nLine-by-line explanation\nThe opening elements establish the document or component boundary. Attributes provide machine-readable context such as a destination, label, or alternative description. Content appears between the relevant tags, and closing tags preserve valid nesting. Inspect the DOM tree to connect each source line with the rendered result.\n\nCommon mistakes\n- Skipping the doctype or using invalid nesting.\n- Using a vague link label, missing form label, or missing meaningful alt text.\n- Using headings for visual size instead of document hierarchy.\n- Putting untrusted HTML directly into a parent page.\n\nAccessibility guidance\nUse semantic elements, visible focus, descriptive labels, logical heading order, keyboard-friendly native controls, and alternative text for meaningful images. Test with keyboard navigation and browser accessibility tools.\n\nBest practices\nKeep HTML semantic and valid, separate CSS/JavaScript concerns, use lowercase attributes with quoted values, and validate before publishing.\n\nExercises\n- Easy: reproduce the example and change one piece of content.\n- Medium: add a related semantic element and explain why it fits.\n- Challenge: add an accessibility check and test the page using only a keyboard.\nHints: identify the document structure first; then add content and attributes one change at a time.\nGuided solution: write the smallest valid structure, preview it, validate it, and fix the first reported issue before adding another feature.\n\nSummary\nYou can now explain {topic}, write the corresponding HTML, preview it safely, and review its accessibility.\n\nNext lesson\n{next_title}\n\nMyanmar explanation\n{mm}\n"""

def _questions(title, topic):
    return [
        (f"Which HTML idea is central to {topic}?", [f"Use {topic} semantically", "Ignore document structure", "Paste untrusted HTML"], f"Use {topic} semantically", "Semantic structure gives browsers and assistive technology useful meaning."),
        ("True or false: HTML should be checked for valid nesting and accessible labels.", ["True", "False"], "True", "Validation and accessibility checks catch structural and usability problems."),
        ("Which practice is safest?", ["Keep untrusted markup sandboxed", "Insert untrusted HTML into the parent DOM", "Remove all labels"], "Keep untrusted markup sandboxed", "The course preview isolates authored markup in a sandboxed iframe."),
    ]

def seed_html_course(db, course):
    course.title = "HTML — From Zero to Web Development Foundations"
    course.short_description = "A free, beginner-friendly HTML Living Standard course with semantic markup, accessibility, forms, projects, and safe browser previews."
    course.description = "Learn modern HTML from the document structure up through semantic pages, accessible forms, metadata, responsive content, validation, and real-world websites."
    course.level, course.status, course.published = "beginner", "published", True
    course.outcomes = "Write valid HTML documents|Use semantic and accessible elements|Build forms, tables, links, and media|Apply metadata and responsive foundations|Create real HTML projects"
    course.requirements = "Basic computer literacy; a text editor and modern browser; no previous web development experience required."
    authored = []
    for module_index, module_title in enumerate(MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_index))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_index); db.add(module); db.flush()
        module.title = module_title
        if module_index == 1:
            specs = MODULE_ONE
        elif module_index == 19:
            specs = [(name, "guided HTML project", f"<!doctype html>\n<html lang=\"en\"><body><main><h1>{name}</h1><p>Build this project with semantic HTML.</p></main></body></html>", requirements, "Use a semantic page structure, labeled content, and a validation checklist.", "Project ကို semantic structure၊ labels နှင့် validation checklist ဖြင့် တည်ဆောက်ပါ။") for name, requirements in PROJECTS]
        elif module_index == 20:
            specs = [("Capstone Requirements and Architecture", "capstone planning", "<main><h1>Final HTML website</h1><p>Plan content, structure, accessibility, and validation.</p></main>", "Choose a useful website, write its content structure, and plan the accessibility checks before authoring.", "requirements -> semantic structure -> validation", "Capstone မစမီ content structure နှင့် accessibility checks ကို စီစဉ်ပါ။"), ("Final HTML Capstone Project", "complete HTML website", "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><title>Capstone</title></head><body><header><h1>My HTML website</h1></header><main><p>Accessible, semantic, and validated.</p></main></body></html>", "Combine document structure, navigation, content, media alternatives, forms, metadata, and accessibility into a complete HTML-only website.", "combine semantic elements, metadata, labels, and validation", "Final project တွင် semantic elements၊ metadata၊ label နှင့် validation တို့ကို ပေါင်းစပ်ပါ။")]
        else:
            pair = MODULE_LESSONS[module_index - 2]
            specs = [(title, topic, code, f"This lesson explains {topic} and shows how it supports clear, maintainable web documents.", f"Use the standard HTML element and choose attributes that describe its purpose: {topic}.", "HTML element နှင့် attribute များကို ၎င်းတို့၏ အဓိပ္ပါယ်နှင့်ကိုက်ညီအောင် အသုံးပြုပါ။") for title, topic, code in pair]
        for lesson_index, (title, topic, code, theory, syntax, mm) in enumerate(specs, 1):
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm=""); db.add(lesson); db.flush()
            lesson.title, lesson.slug = title, slug
            previous = "No previous experience is required." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
            next_title = "Continue to the next module." if module_index == 20 else "Continue with the next lesson."
            lesson.content_en = _content(title, topic, code, theory, syntax, mm, previous, next_title)
            lesson.content_mm = f"{title} ကို English theory နှင့်အတူ လေ့လာနိုင်ပါသည်။\n\n{mm}"
            lesson.description, lesson.duration_minutes = theory, 35 if module_index == 19 else 25
            lesson.status, lesson.published = "published", True; authored.append(lesson)
            examples = list(db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all())
            example = examples[0] if examples else None
            for duplicate in examples[1:]:
                db.delete(duplicate)
            if not example: db.add(CodeExample(lesson_id=lesson.id, title=f"{title} example", language="html", filename="index.html", code=code, description="Open this example in the sandboxed browser preview.", position=1))
            else: example.title, example.language, example.filename, example.code, example.position = f"{title} example", "html", "index.html", code, 1
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz: quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the explanations and retry after studying missed concepts.", status="published"); db.add(quiz); db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(title, topic), 1):
                q = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position)); values = dict(prompt=prompt, question_type="true_false" if options == ["True", "False"] else "multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                if not q: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(q, key, value)
    course.duration_minutes = sum(x.duration_minutes or 25 for x in authored); db.flush()
