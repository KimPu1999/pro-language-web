"""Authored Web Application Security vertical slice for the idempotent catalog seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

PLANNED_MODULES = [
    "Introduction to Web Security", "How the Web Works", "Networking for Web Security", "Linux & Security Fundamentals",
    "Web Application Architecture", "Security Principles & Threat Modeling", "OWASP Top 10 Overview", "Injection Vulnerabilities",
    "Cross-Site Scripting (XSS)", "Cross-Site Request Forgery (CSRF)", "Broken Access Control & IDOR",
    "Authentication Vulnerabilities", "Session Management Security", "Security Misconfiguration", "Cryptographic Failures",
    "Server-Side Request Forgery (SSRF)", "File Upload Security", "Path Traversal & File Access", "Insecure Deserialization",
    "API Security Fundamentals", "JWT & Token Security", "OAuth 2.0 & OpenID Connect", "CORS & Browser Security Headers",
    "Rate Limiting & Abuse Prevention", "Secure JavaScript & TypeScript", "Secure PHP & Laravel", "Secure Python & FastAPI",
    "Secure React & Next.js", "Database Security", "Web Security Testing Methodology", "Security Testing Tools",
    "SAST, DAST & Dependency Scanning", "Security Logging & Monitoring", "DevSecOps & Secure CI/CD",
    "Cloud & Container Web Security", "Security Incident Response", "Security Architecture & Zero Trust",
    "Security Assessments & Reporting", "Professional Web Security Projects", "Final Web Security Capstone",
]

MODULE_ONE = [
    ("Security Mindset and Authorization", "scope, consent, defensive thinking, and ethical boundaries",
     "printf 'scope -> observe -> validate -> remediate\\n' # Use only an authorized local lab",
     "bash", "Web security work starts with authorization, scope, evidence, and harm reduction. A defensive engineer models how a feature can fail, validates findings in a local or explicitly permitted environment, and reports remediation without accessing unrelated data. Curiosity is not authorization.",
     "Web security လေ့လာရာတွင် authorization၊ scope၊ evidence နှင့် harm reduction ကို အရင်သတ်မှတ်ရသည်။ Public target များကို ခွင့်ပြုချက်မရှိဘဲ မစမ်းသပ်ပါနှင့်။",
     "Write a rules-of-engagement sheet for a local training app: target, time window, allowed tools, prohibited actions, and reporting contact.",
     ("What must come before a security test?", ["Explicit authorization and a defined scope", "A public IP address", "A copied credential"], "Explicit authorization and a defined scope", "Authorization and scope protect users and systems.")),
    ("How Browser and Server Requests Work", "HTTP methods, headers, cookies, origins, and responses",
     "curl -I https://example.invalid # Inspect only an approved endpoint",
     "bash", "A browser sends a request containing a method, URL, headers, and sometimes a body. The server returns a status, headers, and content. Cookies, origins, redirects, caching, and content types affect security. In the Academy, use simulated examples or your own local application.",
     "Browser သည် method၊ URL၊ headers နှင့် body ပါသော request ပို့ပြီး server က status၊ headers နှင့် content ပြန်ပေးသည်။ Cookie၊ origin နှင့် redirect များက security ကို သက်ရောက်သည်။",
     "Label a sample login request and response, then identify which values are sensitive and why.",
     ("HTTP request တွင် ဘာတွေပါနိုင်သနည်း?", ["Method, URL, headers, and an optional body", "Only a password", "A database connection"], "Method, URL, headers, and an optional body", "Understanding the request boundary enables secure validation.")),
    ("Threat Modeling a Web Feature", "assets, actors, trust boundaries, threats, and mitigations",
     "printf 'asset: account data\\ntrust boundary: browser -> API\\nmitigation: authorization'",
     "bash", "Threat modeling asks what we protect, who can interact, where trust changes, what can go wrong, and how to reduce risk. Use a small feature such as profile editing to identify assets, abuse cases, controls, logging, and residual risk.",
     "Threat modeling တွင် asset၊ actor၊ trust boundary၊ abuse case နှင့် mitigation ကို ဖော်ပြရသည်။ Profile editing ကဲ့သို့ feature အသေးမှ စပါ။",
     "Create a threat table for profile editing with one spoofing, tampering, and information-disclosure scenario.",
     ("Threat model ၏ အစမှာ ဘာကိုသတ်မှတ်ရမည်နည်း?", ["Assets, actors, trust boundaries, and intended use", "Only the UI color", "A random exploit payload"], "Assets, actors, trust boundaries, and intended use", "Clear context makes security controls testable.")),
    ("Security Principles and Defense in Depth", "least privilege, fail-safe defaults, validation, and layered controls",
     "printf 'validate input + authorize action + protect secrets + log outcome\\n'",
     "bash", "Defense in depth combines independent controls: input validation, output encoding, authentication, authorization, secure defaults, secret management, rate limits, monitoring, and recovery. One control should not be treated as a complete security boundary.",
     "Defense in depth သည် validation၊ encoding၊ authentication၊ authorization၊ secrets၊ rate limit နှင့် monitoring ကို layer များအဖြစ်သုံးသည်။",
     "Map four independent controls to a password-reset feature and explain what each controls.",
     ("Defense in depth ဆိုသည်မှာ ဘာလဲ?", ["Multiple complementary controls across layers", "One hidden URL", "Disabling all logs"], "Multiple complementary controls across layers", "Layered controls reduce single-point failure.")),
    ("OWASP Top 10 as a Learning Map", "common web risk categories and remediation language",
     "printf 'find root cause -> reproduce locally -> fix -> add regression test\\n'",
     "bash", "OWASP risk categories are a learning map, not a permission to attack systems. Study root causes such as injection, broken access control, authentication failures, misconfiguration, and insecure design. Prefer prevention and regression tests over exploit collection.",
     "OWASP risk category များသည် learning map ဖြစ်ပြီး attack permission မဟုတ်ပါ။ Root cause၊ fix နှင့် regression test ကို အဓိကထားပါ။",
     "Choose a profile API and list the relevant OWASP categories, controls, and regression tests.",
     ("OWASP ကို ဘယ်လိုအသုံးပြုသင့်သနည်း?", ["As a risk and remediation framework in authorized environments", "As permission to scan public sites", "As a password list"], "As a risk and remediation framework in authorized environments", "Security knowledge must stay within authorization.")),
    ("Input Validation and Output Encoding", "allowlists, canonicalization, context-aware encoding, and safe errors",
     "python -c 'value = \"<script>\"; print(\"validate type, length, and context before output\")'",
     "python", "Validation checks type, length, format, and business constraints at trust boundaries. Encoding must match the output context: HTML, attribute, URL, JavaScript, and SQL are different. Reject unsafe input where appropriate and avoid returning stack traces or secrets.",
     "Input validation သည် type၊ length၊ format နှင့် business constraint ကို စစ်သည်။ Output encoding သည် HTML/URL/JavaScript context အလိုက် ကွာခြားသည်။",
     "Design validation for a username and a markdown comment; include safe error responses.",
     ("Output encoding ကို ဘာအတွက် context အလိုက်လုပ်ရသနည်း?", ["Different interpreters parse HTML, URLs, JS, and SQL differently", "All contexts share one escaping rule", "Encoding replaces authorization"], "Different interpreters parse HTML, URLs, JS, and SQL differently", "Context-aware encoding prevents misinterpretation.")),
    ("Authentication, Authorization, and Sessions", "identity proof, permission checks, cookies, and session lifecycle",
     "printf 'authenticate identity -> authorize resource -> rotate session -> log decision\\n'",
     "bash", "Authentication answers who the user is; authorization answers what they may do. Sessions need secure cookie attributes, rotation after privilege changes, expiry, revocation, CSRF protection where applicable, and server-side ownership checks. Never trust a user ID supplied by the browser.",
     "Authentication သည် identity ကိုစစ်ပြီး authorization သည် permission ကိုစစ်သည်။ Session တွင် secure cookie၊ rotation၊ expiry နှင့် ownership check လိုအပ်သည်။",
     "Draw a login-to-request session lifecycle and mark where authorization must occur.",
     ("Authorization check ကို ဘယ်မှာလုပ်သင့်သနည်း?", ["On the server for every protected resource/action", "Only by hiding a button", "Only in a client-side route"], "On the server for every protected resource/action", "Client UI is not a security boundary.")),
    ("First Defensive Web Security Workflow", "local evidence, remediation, regression tests, and reporting",
     "printf 'reproduce locally -> capture evidence -> remediate -> regression test -> report\\n'",
     "bash", "A safe workflow uses a disposable local app, minimal reproduction, non-sensitive evidence, a root-cause explanation, a corrective change, and a regression test. Reports should describe impact and remediation without publishing secrets or enabling unauthorized targeting.",
     "Safe workflow သည် local app၊ minimal reproduction၊ evidence၊ remediation၊ regression test နှင့် report ပါဝင်သည်။ Public website များကို မစမ်းသပ်ပါနှင့်။",
     "Complete the playground remediation challenge and write a short defensive report with impact, fix, and test.",
     ("Security finding တစ်ခုကို ပြီးဆုံးအောင် ဘာပါဝင်ရမည်နည်း?", ["Root cause, safe evidence, remediation, and regression verification", "Only an exploit string", "A public target list"], "Root cause, safe evidence, remediation, and regression verification", "A finding is useful when it leads to a verified fix.")),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(position: int, item: tuple) -> str:
    title, topic, commands, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "No security experience is required; basic web concepts help." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: complete the defensive security lab and review the Module 1 assessment."
    return f"""Introduction
{title} introduces {topic} through authorized defensive practice.

Learning objectives
- Explain {topic} and its place in a secure web architecture.
- Identify trust boundaries, root causes, and safe remediation.
- Keep all testing inside an authorized local training environment.

Prerequisites
{prerequisite}

Security architecture explanation
browser -> TLS/HTTP boundary -> application/API -> authorization -> data store -> audit and monitoring

Detailed theory
{theory}

Safe code and command examples
{commands}

Expected results
Use the local simulator or a disposable training app. Expected output should show the security decision, validation result, or remediation state; do not test public websites.

Root cause analysis
Describe which trust boundary failed, what the attacker-controlled input or identity could influence, why existing controls were insufficient, and which server-side control closes the gap.

Secure implementation
Use allowlists and context-aware encoding, parameterized database queries, server-side authorization, secure cookies, safe errors, secret managers, dependency updates, and regression tests.

Common mistakes
- Treating client-side checks or hidden buttons as authorization.
- Testing public targets without written permission.
- Logging passwords, tokens, or sensitive request bodies.
- Copying exploit payloads without understanding scope and remediation.

Troubleshooting
Confirm the local app, test account, scope, browser origin, request method, server logs, and expected security policy. Minimize reproduction and remove sensitive evidence before sharing.

Best practices
- Define scope and rules of engagement before testing.
- Use least privilege, secure defaults, defense in depth, and threat modeling.
- Fix root causes and add a regression test after each finding.

Prevention and remediation
Review the secure code path, validate on the server, authorize the requested object/action, encode output for its context, rotate or revoke secrets, and monitor the outcome.

Security and ethics
The Academy does not scan external targets, execute arbitrary student code, access host filesystems, or collect credentials. Practice only on local or explicitly authorized environments.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Create a local feature threat model, document one safe reproduction, implement a defensive fix, add a regression test, and write a remediation report. Do not target any public system.

Summary
You can now approach web security as authorized risk reduction: scope, evidence, root cause, remediation, and verification.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
Examples are defensive and predefined. Never use them to test systems without explicit authorization.
"""

def seed_web_security_course(db, course):
    course.title = "Web Application Security — From Zero to Professional Web Security Engineer"
    course.short_description = "A free, defensive path through secure web architecture, OWASP risks, API security, testing, and DevSecOps."
    course.description = "Learn web security foundations, threat modeling, OWASP risks, authentication, authorization, secure coding, API security, testing methodology, DevSecOps, monitoring, and incident response through authorized local exercises."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 45
    course.outcomes = "Explain browser, server, identity, authorization, and data trust boundaries|Apply secure validation, encoding, authentication, authorization, and secret-management patterns|Use authorized local testing workflows and write useful remediation reports|Build a foundation for API security, DevSecOps, monitoring, and zero-trust architecture"
    course.requirements = "Basic web concepts are helpful; all practical work can run in an authorized local training environment."
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
        values = {"title": f"{title} example", "language": item[3], "filename": item[3], "code": item[2], "description": "Defensive example for an authorized local environment; the Academy does not execute it.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review authorization, root cause, remediation, and safe testing boundaries before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: the Academy authorizes testing public websites by default.", ["True", "False"], "False", "Practice is limited to local or explicitly authorized environments."),
            ("Which response best closes a web security finding?", ["Fix the root cause and add a regression test", "Hide the button only", "Publish a credential"], "Fix the root cause and add a regression test", "Server-side remediation and verification provide durable protection.")
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

