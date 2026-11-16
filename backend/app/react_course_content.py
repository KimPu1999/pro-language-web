"""Idempotent React Development vertical-slice seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion


PLANNED_MODULES = [
    "Introduction to React", "HTML, CSS & JavaScript Prerequisites", "React Installation & Vite Setup", "React Project Structure",
    "JSX Fundamentals", "React Components", "Props & Component Communication", "Styling React Applications", "Events & Event Handling",
    "React State with useState", "Conditional Rendering", "Rendering Lists & Keys", "Forms & Controlled Inputs", "Effects with useEffect",
    "Refs with useRef", "Context API & useContext", "Custom React Hooks", "React Router", "API Integration & Fetch", "Server State & TanStack Query",
    "State Management Fundamentals", "Zustand & Redux Toolkit", "TypeScript with React", "React Forms & Validation", "Authentication & Protected UI",
    "Reusable UI Components", "Advanced Tailwind CSS & shadcn/ui", "React Rendering & Reconciliation", "Performance Optimization", "useReducer & Advanced Hooks",
    "Suspense & Lazy Loading", "Error Boundaries & Resilience", "Accessibility & Responsive UI", "React Security Best Practices", "React Testing",
    "React Application Architecture", "React with Next.js", "Deployment, CI/CD & Monitoring", "Professional React Projects", "Final React Capstone & Assessment",
]

MODULE_ONE = [
    ("What React Is", "declarative UI, component composition, state, and browser rendering",
     "function Welcome({ name }: { name: string }) {\n  return <h1>Welcome, {name}</h1>;\n}", "tsx",
     "React is a library for describing user interfaces as a tree of components. Components receive inputs, render UI, and coordinate state changes through explicit data flow. React does not replace backend authorization or validate untrusted data by itself.",
     "React သည် component tree ဖြင့် UI ကို declarative ဖော်ပြသော library ဖြစ်သည်။ Props၊ state နှင့် data flow ကို ရှင်းလင်းစွာစီမံပြီး backend authorization ကို React အစားမထိုးနိုင်ပါ။",
     "Sketch a course dashboard component tree and label props, local state, and server data boundaries.",
     ("React ၏ အဓိကအယူအဆက ဘာလဲ?", ["Declarative component-based UI", "A database server", "A password manager"], "Declarative component-based UI", "React composes UI from components and current state.")),
    ("Vite and a React Project", "modern local setup, scripts, modules, and reproducible frontend tooling",
     "npm create vite@latest react-learning -- --template react-ts\ncd react-learning\nnpm install\nnpm run dev", "bash",
     "Vite provides a fast development server and build tool for a React project. Keep dependencies in a lockfile, use environment variables deliberately, and do not put private API keys in browser bundles.",
     "Vite သည် React project အတွက် development server နှင့် build tool ပေးသည်။ Dependency lockfile သုံးပြီး private API key ကို browser bundle ထဲမထည့်ပါနှင့်။",
     "Create a disposable React TypeScript project and identify its entry point, component directory, assets, and test boundary.",
     ("React project ကို run ရန် ဘာက အဓိကဖြစ်သနည်း?", ["A documented package script and entry point", "A database password", "A hidden URL"], "A documented package script and entry point", "The project scripts and entry module define the local workflow.")),
    ("JSX and Component Syntax", "JSX expressions, fragments, attributes, and readable component boundaries",
     "export function CourseCard({ title }: { title: string }) {\n  return <article aria-label={title}>{title}</article>;\n}", "tsx",
     "JSX is syntax that describes elements and expressions for a renderer. Keep components focused, use semantic HTML, type props, and avoid injecting untrusted HTML. JSX is compiled; it is not a template that grants security privileges.",
     "JSX သည် renderer အတွက် element နှင့် expression များကို ဖော်ပြသော syntax ဖြစ်သည်။ Semantic HTML၊ typed props နှင့် safe text rendering သုံးပါ။",
     "Build an accessible CourseCard with a typed title, progress label, and keyboard-operable resume action.",
     ("JSX props ကို ဘာအတွက်သုံးသနည်း?", ["Pass data and configuration into a component", "Store database credentials", "Authorize a server request"], "Pass data and configuration into a component", "Props are inputs to a component; authorization remains server-side.")),
    ("Components and Composition", "single responsibility, children, reusable structure, and data flow",
     "function Dashboard({ children }: { children: React.ReactNode }) {\n  return <main>{children}</main>;\n}", "tsx",
     "Composition lets a parent provide structure while child components own focused behavior. Prefer explicit props and children over hidden global coupling. A component should render clear loading, empty, and error states when it owns data presentation.",
     "Composition ဖြင့် parent က structure ပေးပြီး child က focused behavior ကို စီမံနိုင်သည်။ Hidden global coupling အစား explicit props/children သုံးပါ။",
     "Compose a page shell, course list, and course card with a clear prop contract and an empty state.",
     ("Composition ၏ အကျိုးက ဘာလဲ?", ["Reusable structure and explicit boundaries", "Automatic database migrations", "Secret storage"], "Reusable structure and explicit boundaries", "Composition makes UI structure reusable and visible.")),
    ("Props and One-Way Data Flow", "parent-to-child data, callbacks, immutability, and controlled updates",
     "function SearchBox({ value, onChange }: { value: string; onChange: (value: string) => void }) {\n  return <input value={value} onChange={event => onChange(event.target.value)} />;\n}", "tsx",
     "React data normally flows down through props. Events flow up through callbacks. Treat props and state as immutable inputs and let the owner decide how updates are stored, validated, and persisted.",
     "React တွင် data သည် props ဖြင့် down flow သွားပြီး event သည် callback ဖြင့် up flow ပြန်သွားသည်။ State ကို owner ကစီမံပါ။",
     "Create a typed filter control that emits a query to its parent without mutating parent data.",
     ("React data flow သည် ပုံမှန်အားဖြင့် ဘယ်လိုသွားသနည်း?", ["Parent to child via props", "Database to CSS only", "Child secretly mutates parent"], "Parent to child via props", "Props make parent-to-child data flow explicit.")),
    ("State with useState", "local state, event handlers, functional updates, and state ownership",
     "const [count, setCount] = useState(0);\n<button onClick={() => setCount(value => value + 1)}>{count}</button>", "tsx",
     "useState stores local interactive state. Updates schedule a render; they should be based on the previous value when updates may be batched. Keep state at the smallest component that owns the behavior and do not use UI state as authorization.",
     "useState သည် local interactive state သိမ်းပြီး update လုပ်သောအခါ component ပြန် render ဖြစ်သည်။ Authorization အဖြစ် UI state ကို မယုံပါနှင့်။",
     "Build a daily-goal control with increment, decrement, and a bounded functional update.",
     ("Previous state ပေါ်မူတည်သော update တွင် ဘာသုံးသင့်သနည်း?", ["Functional state updater", "Direct mutation", "A URL parameter"], "Functional state updater", "Functional updates avoid stale values when updates are batched.")),
    ("Events and Conditional Rendering", "event contracts, safe text, loading states, and intentional branches",
     "function Status({ loading }: { loading: boolean }) {\n  if (loading) return <p>Loading…</p>;\n  return <p>Ready</p>;\n}", "tsx",
     "Event handlers connect user interaction to state transitions. Conditional rendering should make loading, error, empty, and success states explicit. Render text safely; dangerouslySetInnerHTML requires a carefully sanitized, trusted boundary.",
     "Event handler များသည် user interaction ကို state transition နှင့်ချိတ်ဆက်သည်။ Loading၊ error၊ empty၊ success state များကို ရှင်းလင်းစွာ render လုပ်ပါ။",
     "Add loading, error, empty, and success states to a course list and test each branch.",
     ("Untrusted HTML ကို render ရာတွင် ဘာကိုရှောင်သင့်သနည်း?", ["Unsafe HTML injection", "Semantic text", "Typed props"], "Unsafe HTML injection", "Untrusted HTML can create XSS; prefer safe text rendering or sanitization.")),
    ("Your First React Workflow", "component tree, typed props, state, accessible UI, and verification",
     "npm run dev\nnpm run build\nnpm run lint", "bash",
     "A professional React workflow combines a small component tree, typed contracts, explicit state, accessible markup, API boundaries, tests, lint, and a production build. Frontend route guards improve UX but do not replace server-side authorization.",
     "Professional React workflow တွင် component tree၊ typed contract၊ state၊ accessibility၊ API boundary၊ test၊ lint နှင့် build ပါဝင်သည်။ Route guard သည် server authorization အစားမထိုးပါ။",
     "Plan a small course dashboard with a server-authorized data loader, interactive search control, error boundary, and test cases.",
     ("Frontend route guard သည် server authorization အစားထိုးနိုင်သလား?", ["မနိုင်ပါ; protected action ကို server တွင် authorize လုပ်ရမည်", "အမြဲအစားထိုးနိုင်သည်", "Only CSS"], "မနိုင်ပါ; protected action ကို server တွင် authorize လုပ်ရမည်", "The server remains the authorization boundary.")),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, example, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "Basic HTML, CSS, and JavaScript are helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the component visualizer and hooks lab."
    return f"""Introduction
{title} introduces {topic} through a safe React UI workflow.

Learning objectives
- Explain {topic} and its role in a React application.
- Use typed components, explicit state, accessible UI, and predictable data flow.
- Separate browser interaction from server-side authorization and private data.

Prerequisites
{prerequisite}

React architecture diagram
route -> component tree -> props/state -> event -> render -> API boundary -> server authorization

Detailed theory
{theory}

JSX/TSX example ({language})
{example}

Component structure
AppShell -> DashboardPage -> CourseList -> CourseCard -> ResumeButton

Expected UI output
Verify semantic markup, keyboard interaction, loading/error/empty states, and responsive layout. Exact API data depends on the authenticated response and must be runtime-validated.

Step-by-step implementation
1. Define the component and prop contract.
2. Keep state at the smallest owner that needs it.
3. Render explicit loading, error, empty, and success states.
4. Validate API data and keep protected decisions server-side.
5. Run lint, typecheck, tests, and a production build.

Interactive visualizer
Use the React visualizer to step through component tree, props, state, effects, and rendering. It is a conceptual simulation and does not evaluate arbitrary student code.

Common errors
- Mutating props or arrays instead of creating new state.
- Using array index as a key for reordered data.
- Missing effect dependencies or creating unnecessary effects.
- Treating a hidden button or route guard as authorization.

Troubleshooting
Check component props, state transitions, browser console, network response shape, effect dependencies, key stability, TypeScript errors, and the smallest reproducible component. Keep secrets out of public environment variables.

Best practices
- Prefer semantic HTML, typed props, small components, explicit states, stable keys, focused hooks, accessible labels, and measured memoization.
- Use a server-authorized API, validate untrusted JSON, handle errors deliberately, and test user-visible behavior.

Security considerations
The Academy playground uses predefined examples and simulated previews. It does not evaluate arbitrary JSX/TSX in the privileged platform context, expose cookies or internal APIs, or provide secrets. Frontend guards never replace server-side authorization.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Build an accessible typed course dashboard with a component tree, search control, local state, explicit data states, secure API boundary, and tests. Keep protected actions authorized by the server.

Summary
You can now reason about {topic} using component, state, rendering, accessibility, and security boundaries.

Next lesson
{next_lesson}

Myanmar explanation
{mm}
"""


def seed_react_course(db, course):
    course.title = "React.js — From Zero to Professional Frontend Developer"
    course.short_description = "A free practical path through React components, hooks, routing, TypeScript, state, accessibility, testing, performance, and production UI."
    course.description = "Learn React, JSX, components, props, state, events, forms, effects, refs, context, custom hooks, routing, API integration, TypeScript, Tailwind, shadcn/ui, authentication UI, performance, Suspense, testing, security, Next.js, and deployment."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 50
    course.outcomes = "Build typed, accessible React components with JSX, props, state, events, forms, and composition|Use hooks, context, routing, API integration, TypeScript, Tailwind, shadcn/ui, and state management|Design resilient, responsive, secure interfaces with testing, accessibility, performance, and error handling|Prepare React applications for Next.js, CI/CD, deployment, and monitoring"
    course.requirements = "Basic HTML, CSS, and JavaScript are helpful; no React experience is required."
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
        lesson.duration_minutes, lesson.status, lesson.published = 50, "published", True
        example_row = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        values = {"title": f"{title} example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe React example for local study; the Academy does not evaluate arbitrary JSX/TSX.", "position": 1}
        if not example_row:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example_row, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review component contracts, state ownership, rendering, accessibility, and server boundaries before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: the Academy evaluates arbitrary student JSX/TSX in the production application context.", ["True", "False"], "False", "The playground uses predefined examples and simulated previews."),
            ("Which boundary protects a private course action?", ["Server-side authorization and user-scoped API data", "A hidden button", "A public environment variable"], "Server-side authorization and user-scoped API data", "Frontend UX controls do not replace server authorization."),
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
