"""Idempotent OWASP Top 10:2025 vertical-slice course seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion


PLANNED_MODULES = [
    "Introduction to Web Security", "HTTP and HTTPS Fundamentals", "Web Application Architecture",
    "Browser Security Fundamentals", "Authentication and Sessions", "Authorization Fundamentals", "Threat Modeling",
    "OWASP Top 10 Introduction", "A01 Broken Access Control", "A02 Security Misconfiguration",
    "A03 Software Supply Chain Failures", "A04 Cryptographic Failures", "A05 Injection", "A06 Insecure Design",
    "A07 Authentication Failures", "A08 Software or Data Integrity Failures", "A09 Security Logging and Alerting Failures",
    "A10 Mishandling of Exceptional Conditions", "Secure Authorization Design", "Secure Authentication Implementation",
    "Input Validation and Output Encoding", "Cryptography and Secret Management", "Security Headers and Browser Protections",
    "Dependency and Supply Chain Security", "Secure Error and Exception Handling", "Security Logging and Alerting",
    "Security Testing Fundamentals", "OWASP ZAP Fundamentals", "Burp Suite Fundamentals", "Static Application Security Testing",
    "Dynamic Application Security Testing", "Vulnerability Assessment and Reporting", "Next.js and React Security",
    "Node.js and Express Security", "Laravel and PHP Security", "Python and FastAPI Security", "Database Security",
    "DevSecOps and Production Security", "Professional OWASP Security Projects", "Final Security Capstone and Assessment",
]

MODULE_ONE = [
    ("What Web Application Security Protects", "confidentiality, integrity, availability, privacy, and trust boundaries",
     "asset -> threat -> control -> evidence\nuser -> browser -> application -> database", "text",
     "Web application security protects users, data, services, and business operations. A useful model identifies assets, trust boundaries, abuse cases, controls, evidence, and recovery. No single scanner or framework makes an application secure by itself.",
     "Web application security သည် user၊ data၊ service နှင့် business operation များကို ကာကွယ်သည်။ Asset၊ trust boundary၊ abuse case၊ control နှင့် recovery ကို ချိတ်ဆက်စဉ်းစားရသည်။",
     "Draw a trust-boundary diagram for a course dashboard and label browser, API, database, and external service assumptions.",
     ("Security program ၏ ပထမဆုံးအခြေခံက ဘာလဲ?", ["Assets and trust boundaries ကိုသတ်မှတ်ခြင်း", "Only changing colors", "Publishing credentials"], "Assets and trust boundaries ကိုသတ်မှတ်ခြင်း", "You need scope and assets before selecting controls.")),
    ("HTTP, HTTPS, and Request Boundaries", "methods, status codes, TLS, cookies, headers, and transport assumptions",
     "GET /api/courses HTTP/1.1\nHost: academy.local\n\nHTTP/1.1 200 OK", "http",
     "HTTP carries requests and responses; HTTPS adds authenticated encryption through TLS. TLS protects transport but does not authorize a user, validate business rules, or prevent insecure server-side access checks.",
     "HTTP request/response သည် data သယ်ဆောင်ပြီး HTTPS တွင် TLS ဖြင့် transport ကိုကာကွယ်သည်။ TLS တစ်ခုတည်းက authorization မဖြစ်စေပါ။",
     "List which properties TLS protects and which properties must still be enforced by the API.",
     ("HTTPS သည် ဘာကိုအဓိကကာကွယ်သနည်း?", ["Transport confidentiality and integrity", "Every authorization decision", "Database schema correctness"], "Transport confidentiality and integrity", "TLS protects the transport channel, not application authorization.")),
    ("Application Architecture and Trust Zones", "browser, frontend, API, services, data stores, and external dependencies",
     "browser -> Next.js -> FastAPI -> PostgreSQL\n             -> identity provider", "text",
     "A secure architecture makes trust zones explicit. Browser code is user-controlled, API boundaries validate and authorize, databases use least privilege, and external providers are treated as dependencies with failure and privacy implications.",
     "Secure architecture တွင် browser ကို user-controlled အဖြစ်ယူပြီး API တွင် validation နှင့် authorization ပြန်လုပ်သည်။ Database နှင့် external provider တွင် least privilege သုံးပါ။",
     "Mark every boundary in a dashboard architecture where input validation, authorization, logging, or secret handling is required.",
     ("Browser မှပို့သော user ID ကို ဘယ်လိုယူဆသင့်သနည်း?", ["Untrusted input အဖြစ် server-side စစ်ရမည်", "Always trusted", "Only CSS data"], "Untrusted input အဖြစ် server-side စစ်ရမည်", "The server must derive identity from the authenticated session and authorize the object.")),
    ("Authentication, Authorization, and Sessions", "identity proof, session lifecycle, ownership, roles, and revocation",
     "authenticate identity -> issue session\nauthorize action + resource -> audit decision", "text",
     "Authentication answers who the subject is; authorization answers what that subject may do to a specific resource. Sessions need secure cookies or tokens, expiry, rotation, revocation, CSRF considerations, and server-side ownership checks.",
     "Authentication သည် identity ကိုသတ်မှတ်ပြီး authorization သည် resource/action ကိုခွင့်ပြုမပြုဆုံးဖြတ်သည်။ Session တွင် expiry၊ rotation နှင့် revocation လိုအပ်သည်။",
     "Write an authorization matrix for student, instructor, and admin actions over one course resource.",
     ("Authorization စစ်ရာတွင် ဘာနှစ်ခုကို စစ်သင့်သနည်း?", ["Action permission and resource ownership", "Only display name", "Only URL color"], "Action permission and resource ownership", "Role permission alone is insufficient without object-level scope.")),
    ("Threat Modeling with Abuse Cases", "assets, actors, entry points, trust boundaries, threats, and mitigations",
     "asset: student progress\nentry point: PATCH /progress\nabuse case: modify another user's record\ncontrol: server-side ownership check", "text",
     "Threat modeling is a structured design activity. Enumerate assets, actors, entry points, assumptions, abuse cases, controls, telemetry, and recovery. Use it before coding and revisit it when architecture changes.",
     "Threat modeling တွင် asset၊ actor၊ entry point၊ assumption၊ abuse case နှင့် control များကို ဖော်ထုတ်ပြီး architecture ပြောင်းလဲတိုင်း ပြန်စစ်ပါ။",
     "Create one abuse case for cross-user progress access and list prevention, detection, and recovery controls.",
     ("Threat model ၏ အကျိုးက ဘာလဲ?", ["Design မစမီ abuse cases နှင့် controls ကို ရှင်းလင်းစေခြင်း", "Vulnerability အားလုံးကိုအလိုအလျောက်ဖယ်ရှားခြင်း", "Only UI testing"], "Design မစမီ abuse cases နှင့် controls ကို ရှင်းလင်းစေခြင်း", "Threat modeling improves design decisions; it is not a magic scanner.")),
    ("OWASP Top 10:2025 Overview", "the 2025 awareness categories and how they differ from historical lists",
     "A01 Broken Access Control\nA02 Security Misconfiguration\nA03 Software Supply Chain Failures\nA04 Cryptographic Failures\nA05 Injection\nA06 Insecure Design\nA07 Authentication Failures\nA08 Software or Data Integrity Failures\nA09 Security Logging and Alerting Failures\nA10 Mishandling of Exceptional Conditions", "text",
     "OWASP Top 10:2025 is an awareness document, not a complete security standard. The 2025 list uses updated category names and must be distinguished from the 2021 list. Always read the official category guidance and apply it to the application's context.",
     "OWASP Top 10:2025 သည် awareness document ဖြစ်ပြီး complete security standard မဟုတ်ပါ။ 2025 category name များကို 2021 နှင့် မရောပါနှင့်။",
     "Create a mapping table that labels a finding as 2025 category, historical 2021 category, or context-dependent.",
     ("OWASP Top 10:2025 တွင် A03 ၏အမည်က ဘာလဲ?", ["Software Supply Chain Failures", "Sensitive Data Exposure", "Broken Authentication"], "Software Supply Chain Failures", "A03:2025 is Software Supply Chain Failures.")),
    ("Broken Access Control Scenario", "object-level authorization, least privilege, and safe remediation",
     "# unsafe concept\nGET /api/users/{id}/progress\n# secure concept: derive current_user and check ownership", "python",
     "Broken access control occurs when a server lets a subject perform an action or access an object outside its policy. A secure implementation derives the current identity from the session, checks role and ownership on the server, and returns a safe denial without leaking records.",
     "Broken Access Control သည် user တစ်ဦးက policy မခွင့်ပြုသော action/resource ကို ရနိုင်ခြင်းဖြစ်သည်။ Current identity၊ role နှင့် ownership ကို server တွင် စစ်ပါ။",
     "Review a synthetic progress endpoint and write three server-side authorization tests: owner allowed, other student denied, admin policy explicit.",
     ("IDOR ကာကွယ်ရန် အကောင်းဆုံး control က ဘာလဲ?", ["Server-side object ownership authorization", "Hide the link", "Trust the path ID"], "Server-side object ownership authorization", "A hidden link is not an authorization control.")),
    ("Injection and Defensive Input Handling", "parameterized queries, output encoding, validation, and safe errors",
     "# secure SQL concept\nSELECT * FROM courses WHERE slug = :slug", "sql",
     "Injection happens when untrusted data changes the meaning of an interpreter command. Use parameterized queries, typed validation, context-aware output encoding, allowlists where appropriate, and safe error responses. Client-side validation is only a usability aid.",
     "Injection မဖြစ်စေရန် parameterized query၊ typed validation၊ context-aware output encoding နှင့် safe error response သုံးပါ။ Client validation တစ်ခုတည်း မလုံလောက်ပါ။",
     "Convert a string-concatenated query into a parameterized query and add tests for quotes, delimiters, and unexpected types.",
     ("SQL injection ကာကွယ်ရန် ဘာသုံးသင့်သနည်း?", ["Parameterized queries", "String concatenation", "Hiding the error"], "Parameterized queries", "Parameters keep data separate from SQL structure.")),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, example, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "Basic web development familiarity is helpful; no security experience is required." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the OWASP visualizer and complete the authorization lab."
    return f"""Introduction
{title} introduces {topic} with an authorized, defensive learning scope.

Learning objectives
- Explain {topic} and connect it to a security control.
- Identify root cause, risk, impact, detection, and remediation.
- Separate client hints from server-side security decisions.

Prerequisites
{prerequisite}

Official reference
OWASP Top 10:2025: https://top10.owasp.org/2025/
This lesson uses the 2025 categories and explicitly distinguishes them from historical 2021 names.

Detailed theory
{theory}

Security architecture diagram
asset -> entry point -> trust boundary -> control -> telemetry -> response

Root cause, risk, and impact
Root cause is the design or implementation decision that permits the weakness. Risk depends on likelihood, exposure, and impact. Impact can include unauthorized data access, integrity loss, service disruption, privacy harm, and recovery cost; validate claims with evidence.

Safe scenario
A synthetic Academy API receives a request from one student for another student's progress. The server derives the authenticated identity, checks ownership, records a redacted decision, and returns a safe denial.

Vulnerable concept and secure example ({language})
{example}

Secure prevention guidance
Use server-side authorization, validation, least privilege, safe defaults, parameterized queries, secure session handling, dependency review, redacted structured logs, and tested recovery. Do not rely on hidden UI controls.

Detection guidance
Add deterministic tests, structured security events without secrets, anomaly review, dependency checks, and explicit owner/action/resource evidence. A tool result is not automatically a confirmed vulnerability.

Remediation checklist
1. Confirm scope and authorization.
2. Reproduce only with synthetic data in an isolated environment.
3. Fix the server-side control and add a regression test.
4. Review logs, privacy, and related endpoints.
5. Record residual risk, owner, verification, and recovery.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Interactive visualizer
Use the OWASP visualizer to step through identity, policy, validation, telemetry, and remediation. It is a conceptual simulation and does not attack a live target.

Mini project
Write a defensive review for {title}: asset, trust boundaries, root cause, impact, secure fix, detection evidence, test cases, cleanup, and responsible-disclosure path.

Common errors
- Treating client-side hiding as access control.
- Testing public or unauthorized systems.
- Collecting real credentials or sensitive personal data.
- Publishing exploit details before owner coordination.

Troubleshooting
Check the local scope, synthetic inputs, server logs, response status, validation schema, authorization policy, dependency versions, and redaction. Stop if an action could affect a system outside the approved lab.

Best practices
Use least privilege, secure defaults, explicit ownership, reproducible tests, privacy minimization, clear evidence, and responsible disclosure. Keep security controls close to the server boundary.

Security ethics
Only test systems you own or have explicit permission to assess. The Academy never scans public targets, collects credentials, executes arbitrary code, or provides an unrestricted proxy.

Summary
You can now analyze {topic} by root cause, risk, impact, prevention, detection, and remediation.

Next lesson
{next_lesson}

Myanmar explanation
{mm}
"""


def seed_owasp_top_10_course(db, course):
    course.title = "OWASP Top 10 — Web Application Security & Secure Development"
    course.short_description = "A free defensive course based on OWASP Top 10:2025, secure design, testing, remediation, and production security."
    course.description = "Learn OWASP Top 10:2025 categories, authentication, authorization, threat modeling, injection prevention, cryptography, supply-chain security, logging, secure frameworks, testing, DevSecOps, and responsible security practice."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 50
    course.outcomes = "Explain OWASP Top 10:2025 and distinguish it from historical 2021 categories|Design server-side authentication, authorization, validation, cryptography, logging, and secure error controls|Practice safe security testing with synthetic, authorized environments and regression tests|Review Next.js, Node.js, Laravel, FastAPI, and database security boundaries"
    course.requirements = "Basic web development and HTTP familiarity are helpful; no offensive security experience is required."
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
        values = {"title": f"{title} defensive example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe synthetic security example; the Academy does not execute arbitrary code or attack live targets.", "position": 1}
        if not example_row:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example_row, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review scope, trust boundaries, server-side controls, evidence, and responsible disclosure before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: a hidden client button is sufficient authorization.", ["True", "False"], "False", "Authorization must be enforced server-side for the action and resource."),
            ("Which practice is required before a security lab?", ["Explicit scope and authorization", "A copied production token", "An unknown public target"], "Explicit scope and authorization", "Defensive testing must be authorized and bounded."),
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
