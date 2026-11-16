"""Idempotent React Native vertical-slice course seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion


PLANNED_MODULES = [
    "Introduction to React Native", "JavaScript, TypeScript & React Review", "React Native & Expo Setup", "Project Structure & Development Tools",
    "Core React Native Components", "Styling with StyleSheet & Flexbox", "Responsive Mobile UI", "Mobile App Architecture Fundamentals",
    "React Native State & Hooks", "Lists & Performance Basics", "Touch, Gestures & Interactions", "Expo Router Fundamentals",
    "Stack, Tabs & Drawer Navigation", "Forms & Validation", "Context API & State Management", "TypeScript for React Native",
    "Animations & Transitions", "REST API Integration", "Server State & TanStack Query", "Authentication & Session Management",
    "Local Storage & Secure Storage", "Offline-First Mobile Applications", "Camera & Image Picker", "File Uploads & Document Handling",
    "Maps & Location Services", "Push & Local Notifications", "Deep Linking & App Links", "Native Device APIs",
    "Background Tasks & App Lifecycle", "Real-Time Mobile Applications", "Mobile UI Component Systems", "Accessibility & Internationalization",
    "React Native Performance", "Mobile App Security", "Testing React Native Apps", "Native Modules & Platform Differences",
    "Build, Signing & Release Management", "App Store Deployment & Monitoring", "Professional React Native Projects", "Final React Native Capstone",
]

MODULE_ONE = [
    ("What React Native Is", "declarative mobile UI, native platform views, and cross-platform boundaries",
     "import { View, Text } from 'react-native';\n\nexport function Welcome() {\n  return <View><Text>Welcome to mobile</Text></View>;\n}", "tsx",
     "React Native lets React component trees describe native Android and iOS UI primitives. Shared code is valuable, but platform differences remain for permissions, navigation, storage, performance, accessibility, and release signing. A browser preview is not a native runtime.",
     "React Native သည် React component tree ဖြင့် Android/iOS native UI primitive များကို ဖော်ပြစေသည်။ Shared code ရှိသော်လည်း permission၊ storage၊ performance နှင့် release signing ကွာခြားမှုများရှိသည်။",
     "Sketch a mobile screen tree with SafeAreaView, View, Text, Pressable, and a server API boundary.",
     ("React Native သည် UI ကို ဘာဖြင့်တည်ဆောက်သနည်း?", ["React components mapped to native views", "Only browser HTML", "A PostgreSQL table"], "React components mapped to native views", "React Native maps component descriptions to platform UI.")),
    ("Expo and Project Setup", "Expo tooling, development builds, scripts, and reproducible mobile setup",
     "npx create-expo-app@latest mobile-learning\ncd mobile-learning\nnpm install\nnpx expo start", "bash",
     "Expo provides a productive toolchain for React Native applications, while development builds and native configuration become important as device capabilities grow. Pin dependencies, review scripts, and keep signing credentials outside source control.",
     "Expo သည် React Native project အတွက် toolchain ပေးသည်။ Native configuration တိုးလာသောအခါ development build လိုအပ်နိုင်ပြီး signing credential များကို source control မထည့်ပါနှင့်။",
     "Create a disposable Expo project and identify app entry, route files, assets, platform configuration, and local verification steps.",
     ("Expo project setup တွင် ဘာကိုထိန်းသိမ်းသင့်သနည်း?", ["Dependency versions and platform configuration", "A production token in app code", "Only a screenshot"], "Dependency versions and platform configuration", "Reproducible mobile builds depend on explicit versions and configuration.")),
    ("Core Components: View, Text, and Pressable", "native layout primitives, accessibility labels, and interaction",
     "<View style={styles.card}>\n  <Text accessibilityRole=\"header\">Course</Text>\n  <Pressable accessibilityRole=\"button\" onPress={onResume}>\n    <Text>Resume</Text>\n  </Pressable>\n</View>", "tsx",
     "View, Text, Image, Pressable, ScrollView, and FlatList are common primitives. Use semantic accessibility labels, keep touch targets comfortable, and avoid treating visual feedback as authorization.",
     "View၊ Text၊ Image၊ Pressable၊ ScrollView နှင့် FlatList တို့သည် အခြေခံ mobile component များဖြစ်သည်။ Accessibility label နှင့် touch target ကို သေချာစီမံပါ။",
     "Build an accessible course card using View, Text, and Pressable with a disabled loading state.",
     ("Pressable ကို ဘာအတွက်သုံးသနည်း?", ["Handle intentional touch interaction", "Store private tokens", "Replace server authorization"], "Handle intentional touch interaction", "Pressable provides a mobile interaction boundary, not security.")),
    ("StyleSheet and Flexbox", "styles, dimensions, flex direction, alignment, and platform-aware layout",
     "const styles = StyleSheet.create({\n  screen: { flex: 1, padding: 20 },\n  row: { flexDirection: 'row', alignItems: 'center', gap: 12 },\n});", "tsx",
     "React Native layout uses a Flexbox-based model with platform details. Prefer StyleSheet and responsive constraints over hard-coded screen assumptions. Test narrow, large, portrait, landscape, and dynamic text sizes.",
     "React Native layout သည် Flexbox ကိုအသုံးပြုသည်။ Fixed screen assumption အစား responsive constraint နှင့် StyleSheet သုံးပြီး orientation/dynamic text ကို စမ်းပါ။",
     "Create a responsive row that wraps or stacks a course title and action on a narrow device width.",
     ("Mobile layout တွင် ဘာကိုရှောင်သင့်သနည်း?", ["Fixed assumptions about screen size", "Flexbox constraints", "Accessible text"], "Fixed assumptions about screen size", "Devices vary in size, orientation, and text scaling.")),
    ("Props and Mobile Component Composition", "typed props, platform-neutral components, and reusable screen structure",
     "type CourseCardProps = { title: string; progress: number; onResume: () => void };\n\nfunction CourseCard({ title, progress, onResume }: CourseCardProps) {\n  return <View><Text>{title}</Text><Text>{progress}%</Text></View>;\n}", "tsx",
     "Reusable mobile components should have explicit prop contracts and keep platform-specific concerns at clear boundaries. Pass callbacks for actions, validate API data, and do not let a client prop determine permission to access a resource.",
     "Mobile component များတွင် typed prop contract ရှိပြီး platform-specific code ကို boundary ခွဲပါ။ Callback သုံးပြီး server authorization ကို မလျှော့ပါနှင့်။",
     "Design a typed CourseCard and screen composition with a progress label, loading state, and resume callback.",
     ("Props ၏ ရည်ရွယ်ချက်က ဘာလဲ?", ["Pass typed data and callbacks", "Authorize database rows", "Store signing keys"], "Pass typed data and callbacks", "Props make component inputs and actions explicit.")),
    ("State, Hooks, and Touch Events", "useState, event handlers, state ownership, and predictable updates",
     "const [selected, setSelected] = useState(false);\n<Pressable onPress={() => setSelected(value => !value)}>\n  <Text>{selected ? 'Selected' : 'Select'}</Text>\n</Pressable>", "tsx",
     "React Native uses the same React state model. Keep state near its owner, use functional updates when based on previous state, and model loading/error/success states explicitly. A local selected flag is not a permission check.",
     "React Native တွင် React state model ကို သုံးသည်။ Previous state အပေါ်မူတည်လျှင် functional update သုံးပြီး authorization အဖြစ် local state ကို မယုံပါနှင့်။",
     "Build a selectable list item with a reset action and an explicit loading state.",
     ("Previous state ပေါ်မူတည်သော toggle တွင် ဘာသုံးသင့်သနည်း?", ["Functional updater", "Direct mutation", "A public API key"], "Functional updater", "Functional updates avoid stale state in batched events.")),
    ("Mobile Navigation Concepts", "Expo Router files, stack/tabs, parameters, and navigation history",
     "app/_layout.tsx\napp/index.tsx\napp/courses/[slug].tsx\n<Stack.Screen name=\"courses/[slug]\" />", "text",
     "Expo Router maps files to routes and can compose stack, tabs, and drawer layouts. Route parameters are navigation data, not proof of access. A protected screen still needs server-side authentication and resource authorization.",
     "Expo Router တွင် file structure သည် route ဖြစ်ပြီး Stack၊ Tabs၊ Drawer layout များကို compose လုပ်နိုင်သည်။ Route parameter သည် access proof မဟုတ်ပါ။",
     "Plan a stack route for course details and tabs for Overview, Lessons, and Profile with a deep-linking note.",
     ("Mobile route guard သည် server authorization အစားထိုးနိုင်သလား?", ["မနိုင်ပါ; server must authenticate and authorize", "အမြဲအစားထိုးနိုင်သည်", "Only changes status bar"], "မနိုင်ပါ; server must authenticate and authorize", "Client navigation improves UX but is not the security boundary.")),
    ("REST API Integration and Secure Sessions", "fetch, loading/error states, tokens, secure storage, and backend authorization",
     "const response = await fetch(`${API_URL}/courses/${slug}`);\nif (!response.ok) throw new Error('Request failed');\nconst data: Course = await response.json();", "tsx",
     "Mobile clients call authenticated backend APIs over HTTPS, validate response shapes, handle offline and error states, and store tokens using platform-appropriate secure storage. Never embed database credentials or trust a client-supplied user ID.",
     "Mobile client သည် HTTPS ဖြင့် authenticated API ကိုခေါ်ပြီး response shape validate၊ offline/error state handle လုပ်ရသည်။ Database credential ကို app ထဲမထည့်ပါနှင့်။",
     "Design a course fetch hook with loading, error, empty, retry, and secure-session expiration states.",
     ("Mobile token ကို ဘယ်မှာသိမ်းသင့်သနည်း?", ["Platform secure storage with server authorization", "Plain source code", "A public route parameter"], "Platform secure storage with server authorization", "Secure storage helps protect tokens; server authorization remains required.")),
    ("First Expo Mobile Workflow", "component tree, navigation, API boundary, device verification, and release safety",
     "npx expo start\nnpm run lint\nnpx expo-doctor", "bash",
     "A professional workflow combines a small component tree, typed data, accessible mobile UI, explicit state, navigation, API authorization, device testing, linting, and build checks. Browser or web previews are conceptual and do not prove native behavior.",
     "Professional mobile workflow တွင် component၊ typed data၊ accessibility၊ navigation၊ API authorization၊ device test နှင့် build checks ပါဝင်သည်။ Web preview သည် native behavior အာမခံချက်မဟုတ်ပါ။",
     "Plan a small Expo course screen with a stack route, secure API loader, retry state, dark mode, and Android/iOS verification checklist.",
     ("Native release မလုပ်မီ ဘာကိုစစ်သင့်သနည်း?", ["Build configuration, permissions, tests, and platform behavior", "Only a browser screenshot", "A committed signing key"], "Build configuration, permissions, tests, and platform behavior", "Native builds require platform-aware verification and secure release handling.")),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, example, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "Basic JavaScript, React, and mobile UI familiarity are helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the device preview and navigation lab."
    return f"""Introduction
{title} introduces {topic} through a safe React Native and Expo workflow.

Learning objectives
- Explain {topic} and its role in a mobile application.
- Design typed, accessible, responsive Android/iOS UI boundaries.
- Separate client interaction from secure backend authorization and private data.

Prerequisites
{prerequisite}

Mobile architecture diagram
screen -> component tree -> state/event -> navigation/API -> FastAPI authorization -> platform services

Detailed theory
{theory}

TSX example ({language})
{example}

Android/iOS considerations
Device sizes, safe areas, keyboard behavior, permissions, lifecycle, accessibility, network availability, and platform APIs vary. Verify on approved local devices or emulators and keep platform-specific code explicit.

Expected mobile UI
The Academy preview is conceptual. Verify component hierarchy, touch labels, loading/error/empty states, orientation, text scaling, and platform behavior locally.

Step-by-step implementation
1. Define a typed screen and component contract.
2. Compose native primitives with responsive StyleSheet rules.
3. Model state, touch events, navigation, loading, and errors explicitly.
4. Fetch only through an authenticated server API and validate response data.
5. Test narrow/large, light/dark, Android/iOS, offline, and accessibility states.
6. Review permissions, secure storage, signing, and cleanup before release.

Interactive visualizer
Use the React Native visualizers to step through component tree, device preview, navigation, and platform boundaries. They are simulations, not native Android/iOS runtimes.

Common errors
- Treating a web preview as proof of native behavior.
- Hard-coding dimensions or ignoring safe areas and dynamic text.
- Storing tokens in plain AsyncStorage or source code.
- Treating client route guards as server authorization.

Troubleshooting
Check Expo/React Native versions, device logs, route file names, safe-area behavior, permissions, network state, response shape, and platform-specific differences. Use a disposable local project and never paste signing credentials into source.

Best practices
- Use typed props, accessible Pressable labels, secure storage, HTTPS, backend authorization, explicit offline/error states, stable list keys, and measured performance changes.
- Keep permission requests contextual and minimal, document platform differences, and test release builds separately from development.

Security considerations
The Academy uses predefined TSX examples and simulated device output. It does not evaluate arbitrary student code in a privileged context, expose cookies or internal APIs, access native devices, or store signing keys. Mobile guards never replace server-side authorization.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Build a small Expo course screen with a typed card, stack route, secure API-loading plan, offline state, accessibility labels, light/dark preview, and Android/iOS verification checklist.

Summary
You can now reason about {topic} using component, device, navigation, API, and security boundaries.

Next lesson
{next_lesson}

Myanmar explanation
{mm}
"""


def seed_react_native_course(db, course):
    course.title = "React Native — From Zero to Professional Mobile App Developer"
    course.short_description = "A free practical path through Expo, native components, navigation, APIs, secure storage, device features, testing, and mobile release."
    course.description = "Learn React Native, Expo, TypeScript, core components, StyleSheet, Flexbox, responsive UI, hooks, Expo Router, forms, API integration, authentication, secure storage, offline workflows, camera, maps, notifications, performance, accessibility, security, testing, native modules, and app deployment."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 55
    course.outcomes = "Build responsive accessible Android and iOS interfaces with React Native, Expo, TypeScript, and core components|Use state, hooks, navigation, forms, APIs, authentication, secure storage, offline state, and device capabilities|Handle platform differences, performance, accessibility, permissions, deep links, testing, and native modules|Prepare signed mobile builds with secure release credentials, monitoring, and rollback considerations"
    course.requirements = "Basic JavaScript, React, and mobile UI familiarity are helpful; no React Native experience is required."
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
        example_row = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        values = {"title": f"{title} example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe React Native example for local study; the Academy does not execute arbitrary mobile code.", "position": 1}
        if not example_row:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example_row, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review device boundaries, state, navigation, secure storage, backend authorization, and platform verification before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: a browser preview proves identical Android and iOS runtime behavior.", ["True", "False"], "False", "Platform APIs, permissions, lifecycle, and device behavior still require local verification."),
            ("Which boundary protects a mobile course resource?", ["Server-side authentication and object authorization", "A hidden tab", "Plain client storage only"], "Server-side authentication and object authorization", "Client navigation is not the authorization boundary."),
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
