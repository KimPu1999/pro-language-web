"""Authored Next.js Full-Stack vertical slice for the idempotent catalog seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

PLANNED_MODULES = [
    "Introduction to Next.js", "Web Development Prerequisites", "React Fundamentals", "TypeScript for Next.js",
    "Next.js Installation & Setup", "Project Structure & Configuration", "JSX, Components & Composition",
    "Styling with Tailwind CSS", "Next.js App Router Fundamentals", "Nested Routes & Layouts", "Dynamic Routes & Parameters",
    "Navigation & Linking", "Loading, Error & Not Found UI", "Server Components", "Client Components & Hooks",
    "Rendering Strategies", "Suspense & Streaming", "Data Fetching Fundamentals", "Caching & Revalidation",
    "Server Functions & Actions", "Route Handlers & APIs", "Forms & Validation", "Authentication & Sessions",
    "Authorization & RBAC", "Database Integration", "File Uploads & Storage", "State Management",
    "UI Components & shadcn/ui", "Responsive UI/UX & Accessibility", "SEO & Metadata", "Images, Fonts & Assets",
    "Performance Optimization", "Testing Next.js Applications", "Next.js Security Best Practices",
    "Internationalization (i18n)", "Real-Time Features & Integrations", "Deployment & Environment Variables",
    "Monitoring, Debugging & Architecture", "Professional Next.js Projects", "Final Next.js Capstone & Assessment",
]

MODULE_ONE = [
    ("What Next.js Is", "React applications, routing, rendering, and full-stack boundaries",
     "npx create-next-app@latest academy-web\\ncd academy-web\\nnpm run dev",
     "bash", "Next.js is a React framework for building web applications with routing, server rendering, data access, APIs, and production tooling. A good application separates browser interactions from server-only data and credentials. The framework provides defaults, but architecture and authorization remain the team's responsibility.",
     "Next.js သည် React ကိုအခြေခံပြီး routing၊ rendering၊ data access နှင့် API tooling ပေးသော framework ဖြစ်သည်။ Browser နှင့် server-only data/credential boundary ကို သေချာခွဲပါ။",
     "Draw the browser → Next.js server → FastAPI/database boundary for a learning dashboard.",
     ("Next.js ၏ အဓိကအားသာချက်က ဘာလဲ?", ["React application အတွက် routing နှင့် full-stack tooling ပေးခြင်း", "Database password ကို client တွင်ထည့်ခြင်း", "Only CSS rendering"], "React application အတွက် routing နှင့် full-stack tooling ပေးခြင်း", "Next.js combines React UI with application architecture.")),
    ("React Components and Composition", "props, composition, reusable UI, and rendering responsibilities",
     "export function Welcome({ name }: { name: string }) { return <h1>Welcome, {name}</h1>; }",
     "tsx", "Components are functions that describe UI from inputs. Props should be typed, composition should express structure, and shared components should not own unrelated data fetching. Keep secrets and privileged operations outside browser bundles.",
     "Component များသည် input အပေါ်မူတည်ပြီး UI ကိုဖော်ပြသည်။ Props ကို type လုပ်ပြီး composition ဖြင့် structure ကိုဖော်ပြပါ။",
     "Create a typed CourseCard component with title, progress, and an accessible resume action.",
     ("Component props ကို ဘာကြောင့် type လုပ်သင့်သနည်း?", ["Expected inputs နှင့် UI contract ကိုရှင်းလင်းစေရန်", "Secrets ကို encrypt လုပ်ရန်", "Routing ကိုအလိုအလျောက်ဖန်တီးရန်"], "Expected inputs နှင့် UI contract ကိုရှင်းလင်းစေရန်", "Types make component contracts explicit.")),
    ("TypeScript for Next.js", "typed props, async data, unions, and safe boundaries",
     "type Course = { id: string; title: string; progress: number };\\nconst course: Course = { id: 'demo', title: 'Next.js', progress: 0 };",
     "tsx", "TypeScript describes data contracts at compile time. Use narrow types, discriminated states for loading/error/success, and runtime validation at external boundaries. Types do not validate untrusted JSON at runtime and must not be treated as authorization.",
     "TypeScript သည် compile-time data contract ကိုဖော်ပြသည်။ External JSON တွင် runtime validation လိုအပ်ပြီး type သည် authorization မဟုတ်ပါ။",
     "Model a dashboard response as loading, success, and error states with a discriminated union.",
     ("TypeScript type သည် runtime validation အစားထိုးနိုင်သလား?", ["မနိုင်ပါ; external data ကို runtime တွင် validate လုပ်ရမည်", "အမြဲအစားထိုးနိုင်သည်", "Only CSS validation"], "မနိုင်ပါ; external data ကို runtime တွင် validate လုပ်ရမည်", "Compile-time types cannot inspect untrusted runtime data.")),
    ("Project Structure and Configuration", "app directory, tsconfig, environment boundaries, and conventions",
     "app/page.tsx\\napp/layout.tsx\\napp/loading.tsx\\napp/error.tsx\\n.env.local  # server-only values stay out of client code",
     "text", "A maintainable project makes route, component, library, test, and asset boundaries clear. Environment variables need a server/client distinction: only intentionally public values receive a public prefix. Never commit secrets or expose server-only modules to client components.",
     "Project structure တွင် route၊ component၊ library နှင့် asset boundary များရှင်းရသည်။ Secret environment variable များကို client bundle သို့မပို့ပါနှင့်။",
     "Create a folder map for a course dashboard and mark server-only and client-interactive modules.",
     ("Secret environment variable ကို ဘယ်မှာထားသင့်သနည်း?", ["Server-only configuration and secret storage", "A client component prop", "A public image URL"], "Server-only configuration and secret storage", "Secrets must not enter browser bundles.")),
    ("App Router Fundamentals", "page.tsx, layout.tsx, route segments, and nested UI",
     "app/dashboard/page.tsx\\napp/dashboard/layout.tsx\\napp/dashboard/courses/page.tsx",
     "text", "The App Router maps folders to URL segments. page.tsx renders a route, layout.tsx persists shared UI, and nested layouts compose navigation and data boundaries. Route groups organize code without changing the URL.",
     "App Router တွင် folder များသည် URL segment ဖြစ်ပြီး page.tsx သည် route၊ layout.tsx သည် shared UI ကိုဖန်တီးသည်။",
     "Design nested routes for dashboard, courses, and a dynamic course lesson page.",
     ("layout.tsx ၏ အကျိုးက ဘာလဲ?", ["Nested routes များတွင် shared UI ကို persist လုပ်ပေးခြင်း", "Database ကို browser တွင်ဖွင့်ခြင်း", "CSS ကို delete လုပ်ခြင်း"], "Nested routes များတွင် shared UI ကို persist လုပ်ပေးခြင်း", "Layouts compose persistent route UI.")),
    ("Server and Client Components", "use client, serialization, hooks, and secure server boundaries",
     "export default async function Page() { const data = await getCourses(); return <CourseList data={data} />; }\\n// Add 'use client' only to interactive components",
     "tsx", "Server Components can access server-side data and keep secrets out of the client bundle. Client Components provide state, event handlers, and browser APIs. Client Components may still be pre-rendered, so the boundary is about capabilities and bundling, not a promise that no HTML is produced on the server.",
     "Server Component သည် server-side data access လုပ်နိုင်ပြီး secret ကို client bundle မှကာကွယ်သည်။ Client Component သည် state၊ event handler နှင့် browser API အတွက်သုံးသည်။",
     "Split a search page into a server data loader and a client search control with a typed serializable prop.",
     ("Client Component လိုအပ်သည့်အခါက ဘယ်အချိန်လဲ?", ["State, event handlers, or browser APIs လိုအပ်သောအခါ", "Every static heading အတွက်", "Database credential အတွက်"], "State, event handlers, or browser APIs လိုအပ်သောအခါ", "Client components are for browser-interactive capabilities.")),
    ("Rendering, Loading, and Errors", "static/dynamic rendering, loading UI, error boundaries, and not-found states",
     "app/courses/loading.tsx\\napp/courses/error.tsx\\napp/courses/not-found.tsx",
     "text", "Next.js supports different rendering and caching strategies. loading.tsx provides a route-level pending UI, error.tsx catches recoverable rendering errors, and not-found.tsx handles missing resources. Data freshness and authorization must be decided per request.",
     "Next.js တွင် loading၊ error နှင့် not-found UI များကို route အလိုက်ဖန်တီးနိုင်သည်။ Data freshness နှင့် authorization ကို request အလိုက်ဆုံးဖြတ်ပါ။",
     "Write an empty, loading, error, and not-found state for a course detail page.",
     ("not-found.tsx ကို ဘာအတွက်သုံးသနည်း?", ["မရှိသော resource အတွက် user-friendly state ပြရန်", "Every server error ကို hide လုပ်ရန်", "Authentication ကိုဖယ်ရန်"], "မရှိသော resource အတွက် user-friendly state ပြရန်", "Not-found is distinct from an unexpected server error.")),
    ("First Next.js Full-Stack Workflow", "route design, typed data, secure fetching, and testable UI",
     "app/courses/[slug]/page.tsx\\nconst response = await fetch(API_URL + '/courses/' + slug);\\n// Validate response and render explicit states",
     "tsx", "A production workflow combines route structure, typed boundaries, server-side fetching, explicit loading/error/empty states, secure authorization, accessible UI, and tests. A browser-visible route must never trust a client-supplied identity for protected data.",
     "Production workflow တွင် route structure၊ typed data၊ server fetch၊ loading/error/empty state၊ authorization နှင့် test ပါဝင်ရသည်။",
     "Build a small course route plan with a server loader, client filter, API error state, and authorization checklist.",
     ("Protected data ကို ဘယ်လို authorize လုပ်သင့်သနည်း?", ["Server-side user-scoped authorization for every protected request", "Client-side hidden button only", "A URL slug only"], "Server-side user-scoped authorization for every protected request", "The server is the security boundary.")),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(position: int, item: tuple) -> str:
    title, topic, commands, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "No Next.js experience is required; basic React is helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the TSX playground and complete the homepage lab."
    return f"""Introduction
{title} introduces {topic} through an App Router workflow.

Learning objectives
- Explain {topic} and its place in a full-stack Next.js application.
- Choose server/client, route, data, and UI boundaries deliberately.
- Keep secrets, authorization, and untrusted input on safe server boundaries.

Prerequisites
{prerequisite}

Next.js architecture explanation
browser -> route segment -> server/client component boundary -> FastAPI/database -> rendered UI

Detailed theory
{theory}

TypeScript/TSX and folder examples
{commands}

Expected UI output
Verify route structure, rendered states, accessible labels, and data boundaries. Exact output depends on the project version and API response; never assume external data is valid without runtime validation.

Step-by-step implementation
1. Identify the route and layout boundary.
2. Define a typed data contract and loading/error/empty states.
3. Keep server-only fetching and credentials on the server.
4. Add client behavior only where state, events, or browser APIs require it.
5. Verify authorization, accessibility, and tests.

Architecture diagram
browser -> Next.js App Router -> server component/route handler -> FastAPI -> PostgreSQL

Common errors
- Adding 'use client' to a whole route unnecessarily.
- Exposing secrets through public environment variables.
- Trusting client-supplied user IDs or unvalidated JSON.
- Omitting loading, error, not-found, or empty states.

Troubleshooting
Check route segment names, params, server logs, API response shape, serialization boundaries, environment variables, network errors, and the smallest reproducible component. Confirm that the authenticated user is scoped server-side.

Best practices
- Keep server data access close to server components or route handlers.
- Use runtime validation, least privilege, secure sessions, and explicit cache/revalidation choices.
- Prefer accessible semantic HTML, responsive states, tests, and small client boundaries.

Security considerations
The Academy playground uses predefined examples and simulated output. It does not execute arbitrary student code, access host filesystems, or expose server secrets. Never put database credentials or private API tokens in client bundles.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Build a small typed course route with a nested layout, server-side data boundary, client search control, loading/error/empty states, and an authorization checklist. Do not execute untrusted code on the Academy host.

Summary
You can now reason about {topic} using explicit App Router, rendering, data, security, and UI boundaries.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
Examples are predefined educational content. No arbitrary TypeScript/TSX execution is available.
"""

def seed_nextjs_course(db, course):
    course.title = "Next.js Full-Stack Development — From Zero to Professional"
    course.short_description = "A free, practical path through App Router, React, TypeScript, APIs, databases, security, testing, and deployment."
    course.description = "Learn Next.js App Router, React, TypeScript, Tailwind, server/client components, rendering, data fetching, caching, actions, APIs, authentication, databases, performance, security, i18n, testing, and deployment."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 45
    course.outcomes = "Build accessible React interfaces with typed props and reusable components|Design App Router layouts, dynamic routes, loading/error states, server/client boundaries, and APIs|Integrate authenticated FastAPI/PostgreSQL workflows without exposing secrets|Prepare production applications with testing, performance, security, SEO, deployment, and monitoring"
    course.requirements = "Basic HTML, CSS, and JavaScript are helpful; no Next.js experience is required."
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
        lesson.duration_minutes, lesson.status, lesson.published = 45, "published", True
        example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        values = {"title": f"{title} example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe Next.js example for an isolated project; the Academy does not execute arbitrary code.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review route boundaries, server/client capabilities, authorization, and validation before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: the Academy executes arbitrary student TSX on the production host.", ["True", "False"], "False", "The playground displays predefined examples and simulated output."),
            ("Which practice protects a Next.js full-stack route?", ["Server-side authorization and keeping secrets out of client bundles", "Trusting a client user ID", "Putting tokens in public environment variables"], "Server-side authorization and keeping secrets out of client bundles", "Security boundaries must remain server-side.")
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

