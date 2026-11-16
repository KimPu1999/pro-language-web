"""Idempotent Secure Coding vertical-slice course seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

PLANNED_MODULES = [
    "Introduction to Secure Coding", "Software Security Fundamentals", "Secure SDLC", "Threat Modeling Fundamentals",
    "OWASP Top 10 & CWE", "Secure Coding Standards", "Input Validation & Data Sanitization", "Output Encoding & Context Safety",
    "SQL Injection Prevention", "Cross-Site Scripting Prevention", "CSRF Protection", "Authentication Security",
    "Password Storage & Recovery", "Authorization & Access Control", "Session Management", "Cryptography Fundamentals",
    "Secure File Uploads", "API Security Fundamentals", "OWASP API Security Top 10", "Secure JavaScript & TypeScript",
    "Secure React & Next.js", "Secure Python & FastAPI", "Secure PHP & Laravel", "Secure Java & Spring Boot",
    "Secure C/C++ & Rust", "Secure Database Programming", "Secrets & Configuration Management", "Security Headers & Browser Protection",
    "SSRF & Server-Side Request Safety", "Path Traversal & Filesystem Safety", "Deserialization & Injection Risks",
    "Race Conditions & Business Logic Security", "Dependency & Supply Chain Security", "Secure Code Review & SAST",
    "DAST, Fuzzing & Security Testing", "Secure CI/CD & DevSecOps", "Logging, Monitoring & Incident Response",
    "Production Hardening & Security Architecture", "Professional Secure Coding Projects", "Final Secure Coding Capstone",
]

MODULE_ONE = [
    ("What Secure Coding Means", "security properties, trust boundaries, and secure defaults", "# Insecure: trust a request value\nuser_id = request.query_params[\"user_id\"]\n\n# Secure boundary: authenticate and authorize server-side\nuser = current_user(request)\nresource = load_owned_resource(user.id)", "python", "Secure coding reduces the likelihood and impact of vulnerabilities by treating input, identity, authorization, output, dependencies, and operational failures as explicit boundaries. It is not a single scanner or framework setting. The server must authenticate the current principal and authorize each object access; client-supplied ids are data, not proof.", "Secure coding သည် input၊ identity၊ authorization၊ output၊ dependency နှင့် failure boundary များကို explicit သတ်မှတ်ပြီး vulnerability risk ကိုလျှော့ချပေးသည်။ Client id သည် authorization proof မဟုတ်ပါ။", "Identify the trust boundaries in a course details request and write one security property for each boundary.", ("Secure coding ၏ အဓိကရည်ရွယ်ချက်က ဘာလဲ?", ["Protect data and behavior at explicit trust boundaries", "Hide every error from developers", "Trust all browser input"], "Protect data and behavior at explicit trust boundaries", "Security is a set of verified properties across boundaries, not one tool.")),
    ("Threats, Assets, and Trust Boundaries", "assets, actors, entry points, impact, and abuse cases", "Asset: student progress\nEntry point: authenticated API\nTrust boundary: browser -> FastAPI\nAbuse case: access another student's record", "text", "Threat modeling starts with what must be protected, who can influence a system, where data crosses trust boundaries, and what happens when assumptions fail. Describe assets, entry points, actors, threats, mitigations, and evidence. Do not test public targets; use synthetic diagrams and authorized local labs.", "Threat modeling တွင် asset၊ actor၊ entry point၊ trust boundary နှင့် impact ကိုသတ်မှတ်သည်။ Public target များကို မစမ်းဘဲ authorized local lab သုံးပါ။", "Draw a browser/API/database flow and label assets, trust boundaries, and one STRIDE-style threat.", ("Trust boundary ဆိုတာ ဘာလဲ?", ["A point where assumptions or privilege change", "A CSS border", "A password stored in source"], "A point where assumptions or privilege change", "Boundaries need validation, authorization, and evidence.")),
    ("Secure SDLC and Security Requirements", "security requirements, design review, implementation, testing, and release", "requirement: every resource query is scoped to current_user.id\ntest: cross-user access returns 404 or 403", "text", "A secure SDLC carries security from requirements through design, implementation, review, testing, release, and operations. Make requirements testable: authentication, object authorization, validation, safe errors, logging, dependency policy, and recovery. A late scan cannot repair an undefined security property.", "Secure SDLC သည် requirement မှ design၊ implementation၊ testing၊ release နှင့် operations အထိ security ကိုထည့်သွင်းသည်။ Requirement များကို test လုပ်နိုင်အောင်ရေးပါ။", "Turn three vague security goals into testable requirements with evidence and owner.", ("Security requirement က ဘာဖြစ်သင့်သနည်း?", ["Specific, testable, and owned", "Only a slogan", "A secret in frontend code"], "Specific, testable, and owned", "Testable requirements produce reviewable evidence.")),
    ("Input Validation and Data Sanitization", "allowlists, types, bounds, canonicalization, and validation locations", "from pydantic import BaseModel, Field\n\nclass Search(BaseModel):\n    q: str = Field(min_length=1, max_length=80)", "python", "Validate untrusted input at the server boundary with types, size limits, allowlists, canonicalization, and business rules. Sanitization is context-specific and cannot replace parameterized queries or output encoding. Reject malformed input without leaking internal details, and validate again at important downstream boundaries.", "Untrusted input ကို server boundary တွင် type၊ size၊ allowlist နှင့် business rule ဖြင့် validate လုပ်ပါ။ Sanitization သည် context-specific ဖြစ်ပြီး parameterized query ကိုမအစားထိုးနိုင်ပါ။", "Design validation for a course search query, file name, and pagination limit; include rejection behavior.", ("Allowlist validation ၏ အားသာချက်က ဘာလဲ?", ["Accept only explicitly supported values", "Accept every string", "Move validation to CSS"], "Accept only explicitly supported values", "Allowlists reduce unexpected input surface when the domain is known.")),
    ("Output Encoding and Context Safety", "HTML, URL, JavaScript, SQL, and JSON contexts", "# Safe HTML template output\n{{ user_display_name }}\n\n# Never build JavaScript or SQL by string concatenation", "template", "Output encoding must match the destination context. HTML escaping does not make a string safe for JavaScript, URLs, SQL, or shell commands. Prefer framework auto-escaping, structured serializers, safe DOM APIs, and parameterized database statements. Avoid dangerous bypasses such as raw HTML rendering unless content is reviewed and sanitized for that exact context.", "Output encoding သည် destination context နှင့်ကိုက်ညီရမည်။ HTML escaping သည် JavaScript၊ URL၊ SQL သို့မဟုတ် shell အတွက် အလိုအလျောက်မလုံခြုံပါ။", "Classify three output locations and select the correct encoding or structured API for each.", ("HTML escaping သည် ဘာကိုမအာမခံသနည်း?", ["Safety in every other context", "HTML text safety when correctly applied", "A password hash"], "Safety in every other context", "Encoding must match the destination context.")),
    ("SQL Injection Prevention", "parameterized queries, least privilege, and safe query composition", "# Safe parameterized query\nstmt = text(\"SELECT id, title FROM courses WHERE slug = :slug\")\ndb.execute(stmt, {\"slug\": slug})", "python", "SQL injection occurs when data changes the structure of a query. Use ORM query builders or parameterized statements, allowlist dynamic identifiers such as sort fields, limit database permissions, and test rejection and authorization. Do not include a live exploit or connect exercises to platform PostgreSQL.", "SQL injection သည် data က query structure ကိုပြောင်းလဲသောအခါဖြစ်သည်။ ORM သို့မဟုတ် parameterized statement၊ dynamic identifier allowlist နှင့် least privilege သုံးပါ။", "Rewrite an unsafe string-built query as a parameterized query and add an authorization predicate.", ("SQL injection ကို ဘယ်လိုကာကွယ်သနည်း?", ["Parameterized queries and validated dynamic parts", "String concatenation", "Hiding the error only"], "Parameterized queries and validated dynamic parts", "Parameters keep data separate from SQL structure.")),
    ("Authentication and Authorization", "identity proof, object-level access, roles, and failure behavior", "principal = require_authenticated_user(request)\nrecord = get_record(record_id)\nif record.owner_id != principal.id:\n    raise NotFound()", "python", "Authentication answers who is calling; authorization answers what that principal may do to this object and action. Apply checks on the server for every sensitive operation, use deny-by-default policies, avoid leaking record existence, and test horizontal and vertical privilege boundaries.", "Authentication သည် caller identity ကိုစစ်ပြီး authorization သည် object/action access ကိုစစ်သည်။ Sensitive operation တိုင်းတွင် server-side check လုပ်ပါ။", "Create an access matrix for student, instructor, and admin actions and add an object ownership test.", ("Authentication နဲ့ authorization ကွာခြားချက်က ဘာလဲ?", ["Identity proof vs permission decision", "Two names for encryption", "Browser theme vs API route"], "Identity proof vs permission decision", "Both are needed and neither is replaced by a hidden client route.")),
    ("Secure Code Review Workflow", "before/after comparison, evidence, regression tests, and responsible disclosure", "Review checklist:\n- input boundary\n- output context\n- authn/authz\n- secrets and dependencies\n- logging and safe errors\n- regression test", "text", "A review classifies trust boundaries, data flows, dangerous sinks, missing controls, and evidence. Prefer a small reproducible finding, a secure remediation, a regression test, and a documented limitation. Heuristic playground feedback is educational and never a complete security assessment.", "Code review တွင် trust boundary၊ data flow၊ dangerous sink၊ missing control နှင့် evidence ကိုစစ်ပြီး regression test ထည့်ပါ။ Heuristic result သည် full assessment မဟုတ်ပါ။", "Review a synthetic snippet, name the weakness, propose a fix, and write the regression test that proves the fix.", ("Security review result ကို ဘယ်လိုဖော်ပြသင့်သနည်း?", ["Finding, impact, fix, evidence, and limitation", "A claim of complete security", "A public exploit target"], "Finding, impact, fix, evidence, and limitation", "Responsible review communicates evidence and scope honestly.")),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, example, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "No security experience is required; basic web/backend concepts help." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the secure code playground and threat modeling tool."
    return f"""Introduction
{title} introduces {topic} through authorized, synthetic security practice.

Learning objectives
- Explain {topic}, the trust boundary, and the likely failure mode.
- Compare insecure and secure patterns without executing an attack.
- Produce a mitigation, verification step, and security checklist item.

Prerequisites
{prerequisite}

Secure architecture diagram
browser/client -> authenticated API -> validation/authorization -> safe service/database -> audit evidence

Detailed theory
{theory}

Insecure pattern (static educational example)
{example}

Root cause analysis
The risk appears when untrusted data, identity, or control flow crosses a boundary without a context-appropriate control. Review the source, sink, assumptions, impact, and missing evidence.

Secure implementation guidance
Use typed contracts, allowlists, context-specific encoding, parameterized queries, server-side authorization, safe errors, least privilege, secure secrets, and regression tests. Keep all vulnerable examples isolated and non-executable.

Expected secure behavior
Malformed input is rejected, unauthorized access is denied without unnecessary disclosure, data remains separate from commands or markup, and logs contain useful evidence without secrets.

Step-by-step implementation
1. Identify assets, actors, entry points, trust boundaries, and dangerous sinks.
2. Reproduce the issue only with synthetic data in an authorized local diagram or static simulator.
3. Apply the smallest appropriate mitigation at the server boundary.
4. Add positive, negative, authorization, and regression tests.
5. Review dependencies, secrets, logging, deployment, and recovery assumptions.

Interactive visualizer
Use the secure code playground, vulnerability lab, threat modeling, code review, checklist, and labs. They are educational simulations, not comprehensive security verification or public attack tools.

Common mistakes
- Treating client validation or hidden UI as authorization.
- Using one encoder for every output context.
- Concatenating SQL, shell, HTML, or JavaScript with untrusted values.
- Logging passwords, tokens, or sensitive personal data.
- Claiming a heuristic check proves an application is secure.

Troubleshooting
Check the exact context, identity and object scope, validation order, error behavior, dependency version, test fixture, and evidence. Keep findings reproducible and scoped to the authorized synthetic lab.

Best practices
- Deny by default, minimize privileges, use secure framework defaults, rotate secrets, patch dependencies, log security events safely, and test both allow and deny paths.
- Document residual risk and route real findings through an authorized disclosure or incident process.

Security checklist
Input boundary ✓  Output context ✓  Authentication ✓  Authorization ✓  Secrets ✓  Dependencies ✓  Regression evidence ✓

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Build a synthetic secure endpoint review: map the trust boundary, show an insecure static snippet, write the secure version, define an authorization and validation test, and document limitations.

Summary
You can now reason about {topic} with vulnerability cause, mitigation, evidence, and scope in view.

Next lesson
{next_lesson}

Myanmar explanation
{mm}
"""


def seed_secure_coding_course(db, course):
    course.title = "Secure Coding — From Zero to Professional Secure Software Developer"
    course.short_description = "A free practical path through secure SDLC, threat modeling, application security, code review, testing, and DevSecOps."
    course.description = "Learn secure coding from trust boundaries and threat modeling through validation, encoding, SQL injection prevention, XSS, CSRF, authentication, authorization, cryptography, API security, language-specific defenses, dependency security, SAST/DAST, secure CI/CD, monitoring, and production hardening."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 55
    course.outcomes = "Identify assets, trust boundaries, threats, vulnerable sinks, and security requirements|Implement validation, encoding, parameterized queries, authentication, authorization, secure sessions, and secrets controls|Review Python, JavaScript, PHP, SQL, Rust, and API patterns with evidence and regression tests|Integrate SAST, dependency scanning, security testing, logging, DevSecOps, and production hardening"
    course.requirements = "Basic web or backend programming familiarity is helpful; no security experience is required."
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
        values = {"title": f"{title} secure example", "language": item[3], "filename": item[3], "code": item[2], "description": "Static security example for authorized study; the Academy does not execute vulnerable code.", "position": 1}
        example_row = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        if not example_row:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example_row, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the trust boundary, secure fix, verification evidence, and remaining scope before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: client-side validation replaces server-side authorization.", ["True", "False"], "False", "Clients are untrusted; authorization must be enforced server-side for each object and action."),
            ("Where should vulnerability exercises run?", ["An authorized isolated synthetic lab", "A public target", "Production infrastructure"], "An authorized isolated synthetic lab", "Training must not target public or production systems."),
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
