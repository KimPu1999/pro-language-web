"""Authored Flutter/Dart vertical slice for the idempotent catalog seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion


PLANNED_MODULES = [
    "Introduction to Flutter", "Dart Programming Fundamentals", "Dart Functions & Collections", "Object-Oriented Dart",
    "Async Dart & Null Safety", "Flutter Installation & Setup", "Flutter Project Structure", "Flutter Widgets Fundamentals",
    "Layout Widgets", "Material Design & Theming", "Forms & Input Validation", "Lists, Grids & Scrolling", "Navigation & Routing",
    "State Management Fundamentals", "Provider & ChangeNotifier", "Riverpod State Management", "BLoC & Cubit", "Clean Architecture & MVVM",
    "HTTP & REST API Integration", "FastAPI & Flutter Integration", "Local Storage & SQLite", "Firebase Fundamentals", "Firebase Authentication",
    "Cloud Firestore & Storage", "Advanced UI & Responsive Design", "Animations & Motion", "Media, Camera & Files", "Location, Maps & Device APIs",
    "Push Notifications", "Offline-First Applications", "Internationalization & Localization", "Flutter Security Best Practices",
    "Flutter Testing Fundamentals", "Performance Optimization", "Platform Integration", "Flutter Web & Desktop", "CI/CD & Automated Builds",
    "App Deployment & Maintenance", "Professional Flutter Projects", "Final Flutter Capstone",
]

MODULE_ONE = [
    ("What Flutter Is and Why It Exists", "cross-platform UI development with a reactive widget model", "import 'package:flutter/material.dart';\n\nvoid main() {\n  runApp(const AcademyApp());\n}\n\nclass AcademyApp extends StatelessWidget {\n  const AcademyApp({super.key});\n\n  @override\n  Widget build(BuildContext context) {\n    return const MaterialApp(home: Scaffold(body: Center(child: Text('Hello Flutter'))));\n  }\n}", "lib/main.dart", "Flutter is a UI toolkit that renders a widget tree from Dart code. A declarative build method describes what the UI should look like for current state; when state changes, Flutter rebuilds the relevant subtree. Cross-platform does not mean platform concerns disappear: accessibility, permissions, storage, release signing, and secure API integration still need deliberate design.", "Flutter သည် Dart code ဖြင့် widget tree တည်ဆောက်ပြီး platform များစွာအတွက် UI render လုပ်သော toolkit ဖြစ်သည်။ State ပြောင်းလဲလျှင် သက်ဆိုင်ရာ subtree ကို rebuild လုပ်သည်။ Accessibility၊ permission၊ storage နှင့် secure API integration ကို မမေ့ရပါ။", "Sketch a widget tree for a screen with an AppBar, title, and action button. Label which widgets are configuration and which state might change.", ("Flutter UI ကို ဘာက တည်ဆောက်သနည်း?", ["A widget tree", "A PostgreSQL table", "A server-side HTML template only"], "A widget tree", "Flutter composes UI from widgets and renders the tree for the current state."), "This content explains Flutter concepts; it does not execute Dart on the Academy host."),
    ("Dart Fundamentals for Flutter", "types, variables, functions, and readable Dart code", "void main() {\n  final username = 'Aye';\n  const lessons = 8;\n  print('$username has $lessons lessons');\n}\n\nString greeting(String name) => 'Welcome, $name';", "bin/intro.dart", "Dart provides sound null safety, static typing, classes, async features, and concise collection syntax. Use final for values assigned once and const for compile-time constants. Clear types and small functions make widget code easier to test and refactor.", "Dart တွင် sound null safety၊ static typing၊ class နှင့် async features ပါရှိသည်။ တစ်ကြိမ်သာ assign လုပ်မည့် value အတွက် final၊ compile-time constant အတွက် const သုံးပါ။", "Rewrite the example with an explicit String return type and a list of course titles. Explain why final and const are different.", ("Dart တွင် compile-time constant အတွက် ဘာသုံးသနည်း?", ["const", "late final always", "dynamic password"], "const", "const values can be evaluated at compile time when their inputs are constant."), "Do not put API keys or private service credentials in Dart client code."),
    ("Install Flutter and Verify the Toolchain", "Flutter SDK, Dart SDK, device targets, and reproducible setup", "flutter --version\ndart --version\nflutter doctor\nflutter create flutter_learning\ncd flutter_learning\nflutter run", "Install Flutter using the official channel for your operating system and use flutter doctor to inspect missing dependencies. A project includes the Dart SDK constraints and platform folders. Keep SDK versions documented for a team, and never copy private signing keys or service-account files into the application repository.", "Official Flutter SDK ကို install လုပ်ပြီး flutter doctor ဖြင့် toolchain ကို စစ်ပါ။ Project ထဲတွင် Dart SDK constraint နှင့် platform folder များ ပါသည်။ Signing key နှင့် service-account file များကို repository ထဲ မထည့်ပါနှင့်။", "Create a disposable Flutter project, run flutter doctor, and record which local target you will use for the remaining Module 1 lessons.", ("Toolchain အခြေအနေစစ်ရန် ဘာကိုသုံးသနည်း?", ["flutter doctor", "flutter delete-everything", "pub expose-secrets"], "flutter doctor", "flutter doctor reports SDK, platform, and dependency setup issues."), "The Academy provides commands for local learning and does not run Flutter builds on its server."),
    ("Create Your First Flutter App", "main.dart, runApp, MaterialApp, and the first screen", "import 'package:flutter/material.dart';\n\nvoid main() => runApp(const MaterialApp(\n  home: Scaffold(\n    appBar: AppBar(title: const Text('Learning Dashboard')),\n    body: Center(child: Text('Start building')),\n  ),\n));", "lib/main.dart", "A Flutter app starts at main and passes a root widget to runApp. MaterialApp supplies common Material behavior, theme, navigation, and localization hooks. Scaffold provides a screen structure, while Center and Text compose the visible body. Keep the root composition small and move screens into focused files as the app grows.", "main function မှ runApp သို့ root widget ပို့ပြီး Flutter app စတင်သည်။ MaterialApp သည် theme၊ navigation နှင့် localization အတွက် foundation ဖြစ်သည်။ Scaffold သည် screen structure ကို ပေးသည်။", "Change the title and body text, run the app on a local device or emulator, and describe the resulting widget tree.", ("Flutter app စတင်ရန် ဘာကိုခေါ်သနည်း?", ["runApp", "runSQL", "startPostgresOnly"], "runApp", "runApp attaches the root widget to the Flutter rendering pipeline."), "Use local development devices only and remove test data before sharing screenshots."),
    ("Stateless and Stateful Widgets", "immutable configuration, mutable UI state, and rebuilds", "class CounterLabel extends StatefulWidget {\n  const CounterLabel({super.key});\n\n  @override\n  State<CounterLabel> createState() => _CounterLabelState();\n}\n\nclass _CounterLabelState extends State<CounterLabel> {\n  int count = 0;\n\n  @override\n  Widget build(BuildContext context) {\n    return TextButton(onPressed: () => setState(() => count++), child: Text('$count'));\n  }\n}", "lib/widgets/counter_label.dart", "StatelessWidget describes UI from immutable configuration. StatefulWidget pairs a configuration object with a State object whose changes can trigger rebuilds through setState. Keep state local when it belongs to one screen; move shared or asynchronous state to a deliberate state-management layer later in the course.", "StatelessWidget သည် immutable configuration အပေါ်မူတည်ပြီး UI ကိုဖော်ပြသည်။ StatefulWidget တွင် State object ပါပြီး setState ခေါ်သောအခါ သက်ဆိုင်ရာ UI ကို rebuild လုပ်သည်။ State ကို လိုအပ်သည့် scope တွင်သာထားပါ။", "Add a reset button to the counter and explain why changing a field without setState does not refresh the visible UI.", ("State ပြောင်းလဲပြီး UI update ဖြစ်စေရန် ဘာလိုသနည်း?", ["setState", "A database restart", "A CSS import only"], "setState", "setState schedules a rebuild for the state object's widget subtree."), "Do not put access tokens or sensitive records in a widget field without secure storage and lifecycle planning."),
    ("Widget Trees and BuildContext", "composition, context lookup, and readable screen structure", "class WelcomeScreen extends StatelessWidget {\n  const WelcomeScreen({super.key});\n\n  @override\n  Widget build(BuildContext context) {\n    return Padding(\n      padding: const EdgeInsets.all(24),\n      child: Column(\n        crossAxisAlignment: CrossAxisAlignment.start,\n        children: const [Text('Welcome'), SizedBox(height: 8), Text('Keep learning')],\n      ),\n    );\n  }\n}", "lib/screens/welcome_screen.dart", "Flutter UI is a tree: parent widgets provide layout constraints and inherited configuration to children. BuildContext identifies a widget's location in that tree and can access theme, media queries, localization, or providers above it. Avoid using a context after a widget is disposed and keep large build methods split into meaningful widgets.", "Flutter UI သည် parent-child widget tree ဖြစ်သည်။ Parent က layout constraint ပေးပြီး BuildContext က tree ထဲမှ widget location ကို ကိုယ်စားပြုသည်။ Theme၊ MediaQuery နှင့် localization ကို context မှ ရနိုင်သည်။", "Draw the tree Padding → Column → Text/SizedBox/Text. Then move the Column into a reusable WelcomeContent widget.", ("BuildContext က ဘာကိုကိုယ်စားပြုသနည်း?", ["A widget's location in the tree", "A database password", "A compiled APK only"], "A widget's location in the tree", "BuildContext provides access to the widget's position and inherited information."), "Do not retain a context beyond its widget lifecycle or use it for authorization decisions."),
    ("Layout Constraints with Row and Column", "constraints, axes, spacing, and overflow prevention", "Scaffold(\n  body: Padding(\n    padding: const EdgeInsets.all(16),\n    child: Row(\n      children: [\n        Expanded(child: Text('A flexible title')),\n        const SizedBox(width: 12),\n        const Icon(Icons.check),\n      ],\n    ),\n  ),\n)", "lib/screens/summary_screen.dart", "Flutter layout follows constraints go down, sizes go up, and parents set positions. Row lays children horizontally and Column vertically. Expanded or Flexible shares available space; without it, long content can overflow. Test narrow mobile, tablet, and text-scale configurations instead of assuming one screen size.", "Flutter layout တွင် constraint သည် parent မှ child သို့ ဆင်းပြီး size သည် child မှ parent သို့ တက်သည်။ Row သည် horizontal၊ Column သည် vertical layout ဖြစ်သည်။ Long text အတွက် Expanded/Flexible သုံးပါ။", "Build a row with a title and trailing icon at a narrow width. Fix the overflow using Expanded and verify with larger text settings.", ("Row ထဲတွင် flexible space ပေးရန် ဘာသုံးနိုင်သနည်း?", ["Expanded", "Hardcoded overflow", "A database migration"], "Expanded", "Expanded allocates remaining flex space to a child."), "Do not hide overflow blindly; make important content accessible at small widths and large text sizes."),
    ("Material 3 Themes and Reusable Widgets", "theme data, design tokens, and component reuse", "MaterialApp(\n  theme: ThemeData(\n    colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF02569B)),\n    useMaterial3: true,\n  ),\n  home: const HomeScreen(),\n)", "lib/app.dart", "ThemeData centralizes colors, typography, shape, and component defaults. Material 3 makes a consistent design system easier, but each interactive control still needs a semantic label, focus behavior, and contrast. Build reusable widgets around meaning rather than making every screen a unique collection of padding values.", "ThemeData သည် color၊ typography၊ shape နှင့် component defaults ကို တစ်နေရာတည်းစီမံသည်။ Material 3 သုံးသော်လည်း accessibility၊ focus နှင့် contrast ကို စစ်ဆေးရမည်။", "Define a theme seed color, create a reusable primary action widget, and verify that it remains readable in dark mode.", ("ThemeData ၏ ရည်ရွယ်ချက်က ဘာလဲ?", ["Centralize visual design defaults", "Store user passwords", "Call PostgreSQL directly"], "Centralize visual design defaults", "ThemeData keeps visual decisions consistent across the widget tree."), "Never place secrets in ThemeData or use visual state as an authorization mechanism."),
    ("Forms, Input Validation, and First App Slice", "controllers, Form validation, feedback, and safe API boundaries", "final formKey = GlobalKey<FormState>();\n\nForm(\n  key: formKey,\n  child: TextFormField(\n    decoration: const InputDecoration(labelText: 'Email'),\n    validator: (value) {\n      if (value == null || !value.contains('@')) return 'Enter a valid email';\n      return null;\n    },\n  ),\n)", "lib/screens/sign_in_screen.dart", "A Form groups fields and validators, while controllers read values when submission is intentional. Client validation improves feedback but is not a security boundary: the FastAPI backend must validate again, authenticate the user, rate-limit attempts, and return safe errors. Dispose controllers when their owning State is disposed.", "Form နှင့် validator သည် client-side feedback အတွက် အသုံးဝင်သော်လည်း security boundary မဟုတ်ပါ။ FastAPI backend တွင် validate၊ authenticate နှင့် rate-limit ထပ်လုပ်ရမည်။ Controller များကို lifecycle အဆုံးတွင် dispose လုပ်ပါ။", "Build a sign-in form with email and password validation. Show a generic failed-login message and never display whether an account exists.", ("Client-side validation ကို security boundary အဖြစ် ယုံကြည်နိုင်သလား?", ["မယုံကြည်နိုင်; backend တွင် ထပ်စစ်ရမည်", "ယုံကြည်နိုင်သည်", "Only on Wi-Fi"], "မယုံကြည်နိုင်; backend တွင် ထပ်စစ်ရမည်", "Clients can be modified, so server-side validation and authorization are mandatory."), "Never embed database credentials or service-account private keys in a Flutter client."),
]

# Keep the first vertical slice at eight published lessons; Dart language
# foundations are expanded in the dedicated second module.
MODULE_ONE = [item for item in MODULE_ONE if item[0] != "Dart Fundamentals for Flutter"]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _parts(item: tuple) -> tuple:
    if len(item) == 8:
        title, topic, code, theory, mm, exercise, question_data, note = item
        return title, topic, code, "terminal", theory, mm, exercise, question_data, note
    return item


def _content(position: int, item: tuple) -> str:
    title, topic, code, filename, theory, mm, exercise, question_data, *notes = _parts(item)
    note = notes[0] if notes else "Use a local Flutter project and remove test data after practice."
    question, options, answer, explanation = question_data
    previous = "No Flutter experience is required; basic programming and terminal familiarity are helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: complete the first Flutter app lab and review the Module 1 assessment."
    return f"""Introduction
{title} introduces {topic} through a production-minded Flutter workflow.

Learning objectives
- Explain {topic} in your own words.
- Build a small, readable Dart/Flutter example.
- Identify widget, state, responsive layout, and security boundaries.

Prerequisites
{previous}

Flutter architecture explanation
User interaction → widget tree → state change → rebuild → platform/rendering output

Complete theory
{theory}

Step-by-step Dart example
1. Create or open the file shown below.
2. Run it on your own local emulator/device or review the widget tree.
3. Change one property and observe the expected UI.
4. Verify narrow layout, dark mode, and accessibility behavior.

File path and folder structure
```text
{filename}
```

Code
```dart
{code}
```

Commands
Use `flutter pub get`, `flutter analyze`, and `flutter test` in your local project. The Academy does not execute learner Flutter/Dart code.

Expected UI/output
The example should render a predictable local widget state or print the described value. Verify behavior on a real target rather than treating a browser simulation as Flutter execution.

Widget tree explanation
The root widget owns app configuration, screen widgets compose layout, and leaf widgets render text or controls. State should live at the smallest scope that owns the behavior; shared state should use a deliberate architecture.

Common errors
- Flutter SDK or device setup is incomplete.
- A Row/Column overflows at a narrow width.
- State changes without setState or a chosen state-management solution.
- Client validation is mistaken for backend authorization.

Troubleshooting
Run `flutter doctor`, `flutter analyze`, and the smallest relevant test. Inspect the widget tree, check constraints, verify controller lifecycle, and reproduce on a narrow target with larger text.

Best practices
- Keep screens composable, use theme tokens, dispose controllers, and model loading/error/empty states explicitly.
- Treat client code as untrusted and keep server-owned permissions on FastAPI.
- Prefer typed models, secure storage, retries with limits, and tests around state transitions.

Security considerations
Never embed PostgreSQL credentials, Firebase service-account keys, or long-lived secrets in a Flutter client. Use authenticated backend APIs, secure token storage, certificate/platform guidance where appropriate, and server-side authorization.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}

Mini project
Build a small Learning Welcome screen with a theme, responsive widget tree, one validated form, explicit loading/error states, and a test plan. Document which data must come from a FastAPI backend.

Summary
You can now reason about {topic} as a widget and application boundary rather than a collection of visual snippets.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
{note}
"""


def seed_flutter_course(db, course):
    course.title = "Flutter & Dart Development — From Zero to Professional"
    course.short_description = "A free, practical path from Dart and Flutter foundations to tested cross-platform apps."
    course.description = "Learn Dart, Flutter widgets, responsive Material 3 UI, state management, FastAPI integration, local storage, Firebase, testing, performance, deployment, and professional mobile architecture through safe examples."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 35
    course.outcomes = "Build responsive Flutter interfaces with Dart|Compose reusable widgets and manage state deliberately|Integrate secure FastAPI services and local data|Test, optimize, and prepare cross-platform applications for release"
    course.requirements = "Basic programming concepts, a text editor, and a terminal; no previous Flutter experience is required."

    module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == 1))
    if not module:
        module = CourseModule(course_id=course.id, title=PLANNED_MODULES[0], order_index=1)
        db.add(module)
        db.flush()
    module.title = PLANNED_MODULES[0]

    for position, item in enumerate(MODULE_ONE, 1):
        item = _parts(item)
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
        lesson.duration_minutes, lesson.status, lesson.published = 35, "published", True

        example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        values = {"title": f"{title} example", "language": "dart", "filename": item[3], "code": item[2], "description": "Read-only Flutter/Dart example. Run only in your own local project; the Academy does not execute learner code.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)

        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the widget tree and retry after explaining the state and security boundary.", status="published")
            db.add(quiz)
            db.flush()
        questions = [(item[7][0], item[7][1], item[7][2], item[7][3]), ("True or false: the Academy executes student Flutter code on its application host.", ["True", "False"], "False", "Examples are displayed as read-only learning content."), ("Which practice protects a Flutter application?", ["Keep secrets out of the client and authorize on the server", "Embed a PostgreSQL password", "Trust client validation alone"], "Keep secrets out of the client and authorize on the server", "Client code is inspectable; sensitive access decisions belong to the backend.")]
        for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
            question_row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
            values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
            if not question_row:
                db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
            else:
                for key, value in values.items():
                    setattr(question_row, key, value)
    db.flush()

