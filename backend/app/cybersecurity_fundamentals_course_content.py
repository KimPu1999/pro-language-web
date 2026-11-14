"""Idempotent defensive cybersecurity curriculum seed.

Module 1 is the complete vertical slice. Later modules have authored
foundation lessons until their full lesson sets are written. Examples are
defensive and read-only; no scanning, malware, credential collection, or
untrusted execution is performed by the platform.
"""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

MODULES = [
    "Introduction to Cybersecurity", "CIA Triad & Security Principles", "Cyber Threats & Attack Types", "Security Risk Management",
    "Security Policies, Ethics & Governance", "Computer Networking Fundamentals", "Network Security Fundamentals", "Linux Fundamentals for Security",
    "Linux Security & Hardening", "Windows Security Fundamentals", "Authentication & Authorization", "Cryptography Fundamentals",
    "TLS, HTTPS & Certificates", "Web Application Security", "OWASP Top 10 Fundamentals", "Secure Coding Fundamentals", "API Security Fundamentals",
    "Database Security", "Endpoint & Device Security", "Vulnerability Management", "Security Logging & Monitoring", "SOC Fundamentals",
    "SIEM Fundamentals", "Threat Intelligence & MITRE ATT&CK", "Incident Response Fundamentals", "Digital Forensics Fundamentals",
    "Cloud Security Fundamentals", "AWS Security Fundamentals", "Container & Kubernetes Security", "DevSecOps Fundamentals",
    "Threat Modeling & Secure Design", "Zero Trust & Security Architecture", "Security Testing Ethics & Methodology", "Defensive Security Testing Labs",
    "Security Frameworks & Compliance", "Privacy & Data Protection", "Business Continuity & Disaster Recovery", "Security Career & Certification Preparation",
    "Real-World Cybersecurity Projects", "Final Cybersecurity Capstone & Assessment",
]

MODULE_ONE = [
    ("What Is Cybersecurity?", "defensive protection of systems, people, data, and services", "from hashlib import sha256\n\nmessage = b\"defensive learning\"\nprint(sha256(message).hexdigest())", "Cybersecurity protects confidentiality, integrity, and availability while managing safety, privacy, resilience, and business risk. A professional defensive program combines people, process, technology, evidence, and continuous improvement. Security is not a single product and no control is perfect.", "asset -> threat -> control -> evidence -> response", "Cybersecurity သည် system၊ user၊ data နှင့် service များကို defensive controls ဖြင့် ကာကွယ်ခြင်း ဖြစ်သည်။"),
    ("CIA Triad and Security Principles", "confidentiality, integrity, availability, and their trade-offs", "controls = {\"confidentiality\": \"least privilege\", \"integrity\": \"hash and review\", \"availability\": \"backup and recovery\"}\nfor goal, control in controls.items():\n    print(f\"{goal}: {control}\")", "Confidentiality limits disclosure, integrity protects correctness and trust, and availability keeps an authorized service usable. Controls can improve one property while creating cost or operational trade-offs. State the asset, impact, threat, control, and evidence instead of using the triad as a slogan.", "asset -> CIA objective -> control -> measurable evidence", "CIA Triad သည် confidentiality၊ integrity နှင့် availability ကို စနစ်တကျ စဉ်းစားရန် framework ဖြစ်သည်။"),
    ("Cyber Threats and Attack Types", "threat actors, vulnerabilities, impacts, and defensive response", "events = [\"phishing report\", \"unexpected login\", \"missing patch\"]\nfor event in events:\n    print(\"triage:\", event)", "A threat is a potential cause of harm; a vulnerability is a weakness; risk combines likelihood and impact in context. Learn attack categories to recognize signals, but practice only with simulated data and systems you own or are explicitly authorized to assess. Defensive triage starts with preservation, scope, and safe containment.", "signal -> triage -> contain -> recover -> learn", "Threat၊ vulnerability နှင့် risk တို့ကို ခွဲခြားပြီး authorized environment တွင်သာ လေ့ကျင့်ပါ။"),
    ("Security Risk Management", "asset inventories, risk statements, treatment, and residual risk", "risk = {\"asset\": \"student records\", \"impact\": \"high\", \"control\": \"MFA and audit logs\"}\nprint(risk)", "Risk management makes security decisions explicit. Identify assets and owners, describe a plausible threat and weakness, estimate impact and likelihood with a documented scale, select treatment, and record residual risk. A high score is not automatically a technical emergency without business context and evidence.", "asset -> threat -> vulnerability -> impact/likelihood -> treatment -> review", "Risk management သည် asset၊ threat၊ vulnerability၊ impact နှင့် treatment ကို မှတ်တမ်းတင်ပြီး ဆုံးဖြတ်ခြင်း ဖြစ်သည်။"),
    ("Policies, Ethics, and Responsible Disclosure", "governance, authorization boundaries, and professional conduct", "policy = {\"scope\": \"owned lab only\", \"evidence\": \"redacted\", \"contact\": \"security team\"}\nprint(policy)", "Policies define acceptable use, data handling, access, retention, and escalation. Ethical security work requires explicit authorization, minimal impact, privacy protection, and responsible disclosure. Never scan public systems, collect real credentials, or publish sensitive findings without the owner's process and consent.", "scope -> authorization -> evidence -> disclosure -> remediation", "Ethical security work အတွက် authorization၊ privacy၊ minimal impact နှင့် responsible disclosure လိုအပ်သည်။"),
    ("Computer Networking Fundamentals for Defenders", "addresses, protocols, boundaries, and observable traffic", "from ipaddress import ip_network\n\nnetwork = ip_network(\"192.0.2.0/24\")\nprint(network.num_addresses)", "Defenders need enough networking to reason about trust boundaries, routing, DNS, HTTP, TLS, and logs. Documentation ranges such as 192.0.2.0/24 are safe examples. Segment systems by need, expose only required services, and observe traffic through authorized logs rather than probing public hosts.", "client -> boundary -> service -> log", "Network fundamentals သည် boundary၊ protocol နှင့် log များကို နားလည်ရန် အရေးကြီးသည်။"),
    ("Module 1 Review and Defensive Assessment", "connecting principles, threats, risk, ethics, and network boundaries", "checks = [\"authorization\", \"least privilege\", \"logging\", \"recovery\"]\nprint(\"reviewed:\", \", \".join(checks))", "A defensible design identifies assets, states the CIA objective, describes threats and assumptions, selects proportionate controls, preserves evidence, and defines recovery. A security visualizer is a conceptual model, not a live SOC or security system. Review decisions with the system owner and document limitations.", "asset -> principle -> threat model -> control -> monitor -> respond", "Module 1 တွင် security principle၊ threat၊ risk နှင့် ethics ကို ဆက်စပ်စဉ်းစားပါမည်။"),
]

GENERAL = [
    ("Security Foundations", "security objectives, assets, trust boundaries, and controls"), ("Threat Modeling", "assets, abuse cases, mitigations, and residual risk"), ("Risk Treatment", "likelihood, impact, ownership, and review"), ("Governance and Ethics", "policies, authorization, privacy, and disclosure"), ("Network Fundamentals", "protocols, segmentation, routing, and defensive visibility"), ("Network Security", "firewalls, secure boundaries, and approved traffic"), ("Linux Security", "users, permissions, services, and safe hardening"), ("Linux Hardening", "patching, configuration baselines, and audit evidence"), ("Windows Security", "identity, endpoint controls, logging, and updates"), ("Authentication and Authorization", "identity proof, sessions, MFA, and least privilege"), ("Cryptography", "hashing, encryption, keys, and correct use cases"), ("TLS and Certificates", "trust chains, HTTPS, and certificate lifecycle"), ("Web Application Security", "input handling, sessions, browser boundaries, and headers"), ("OWASP Top 10", "common web risks and defensive mitigations"), ("Secure Coding", "validation, safe output, dependency hygiene, and errors"), ("API Security", "authentication, authorization, rate limits, and validation"), ("Database Security", "least privilege, parameterized queries, backups, and auditing"), ("Endpoint Security", "device posture, patching, and containment"), ("Vulnerability Management", "inventory, prioritization, remediation, and verification"), ("Security Logging", "structured events, redaction, retention, and integrity"), ("SOC Operations", "alert triage, escalation, and case evidence"), ("SIEM Concepts", "collection, correlation, detection, and false positives"), ("Threat Intelligence", "context, confidence, and defensive use of ATT&CK"), ("Incident Response", "prepare, detect, contain, eradicate, recover, and learn"), ("Digital Forensics", "preservation, chain of custody, and safe analysis"), ("Cloud Security", "shared responsibility, identity, network, and data controls"), ("AWS Security", "IAM, logging, encryption, and cost-aware guardrails"), ("Container Security", "images, runtime boundaries, and Kubernetes controls"), ("DevSecOps", "security checks throughout software delivery"), ("Threat Modeling Design", "security requirements and abuse-case review"), ("Zero Trust", "continuous verification and explicit policy"), ("Security Testing Ethics", "scope, safe methodology, and reporting"), ("Defensive Testing Labs", "isolated scenarios and evidence-based validation"), ("Frameworks and Compliance", "control mapping, evidence, and limitations"), ("Privacy and Data Protection", "minimization, retention, access, and user rights"), ("Business Continuity", "RPO, RTO, backups, and recovery tests"), ("Security Career Preparation", "portfolio evidence, communication, and responsible practice"), ("Cybersecurity Projects", "defensive project scope, verification, and documentation"), ("Cybersecurity Capstone", "defending a secure architecture and response plan"),
]

def _slug(value): return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(title, topic, theory, code, mm, previous, next_title):
    return f"""Introduction\n{title} introduces {topic} with a defensive, authorized-learning focus. CodeMaster Academy uses simulated data and read-only examples; it never scans public systems, collects credentials, executes malware, or runs untrusted code in FastAPI workers.\n\nLearning objectives\n- Explain {topic} and connect it to a defensive control.\n- Identify assets, threats, assumptions, evidence, and recovery steps.\n- Apply authorization, privacy, least privilege, and responsible disclosure.\n\nPrerequisites\n{previous}\n\nSecurity architecture diagram\nasset -> trust boundary -> control -> telemetry -> triage -> recovery\n\nComplete theory\n{theory}\n\nReal-world scenario\nA small service receives an unusual login report. The defender confirms scope and authorization, preserves redacted logs, assesses impact, applies a proportionate control, and records follow-up work without exposing user data.\n\nThreats and vulnerabilities\nConsider excessive permissions, weak configuration, missing updates, unvalidated input, exposed secrets, insufficient logs, and untested recovery. Do not assume a threat is an incident without evidence.\n\nDefensive controls\nUse MFA, least privilege, secure defaults, segmentation, encryption, input validation, dependency review, rate limits, redacted structured logs, backups, and documented response ownership.\n\nCommands or examples\n```python\n{code}\n```\nThis is a safe local example. It uses synthetic values and does not contact external systems.\n\nLine-by-line explanation\n- The example creates or reads controlled local data.\n- Each operation has a defined defensive purpose.\n- Output is evidence for learning, not a live security finding.\n\nSafe hands-on lab\nUse a local, owned sample repository or the provided synthetic data to document {topic}. Define scope, authorization, expected evidence, containment, cleanup, and escalation before practice.\n\nExpected results\nYou can explain the control, reproduce the documented local result, and identify limitations. No public system is scanned and no credential is collected.\n\nVerification steps\n1. Confirm the lab scope is owned or explicitly authorized.\n2. Compare the output with the expected result.\n3. Review logs for secrets and personal data.\n4. Record remediation and recovery evidence.\n\nTroubleshooting\nCheck inputs, local versions, file permissions, redaction, and the documented scope. Stop if the action could affect a system or person outside the lab. Ask the owner rather than guessing authorization.\n\nSecurity ethics\nOnly test systems you own or have explicit permission to assess. Minimize impact, protect evidence, disclose responsibly, and follow the owner's incident process.\n\nCommon mistakes\n- Treating a tool result as proof without validating scope and evidence.\n- Using real credentials or personal data in a tutorial.\n- Fixing an access issue by granting broad administrator rights.\n- Publishing sensitive details before remediation.\n\nBest practices\nUse synthetic data, least privilege, secure defaults, redaction, reproducible notes, clear ownership, and tested recovery.\n\nPractice exercises\n- Easy: identify the asset, security objective, and one control.\n- Medium: rank two risks and justify likelihood, impact, and treatment.\n- Challenge: review a diagram and propose telemetry, response, and ethical boundaries.\n\nQuiz\n1. What must exist before a defensive lab? Explicit scope and authorization.\n2. True or false: a scanner result alone proves a vulnerability. False.\n3. What should be protected in logs? Credentials, secrets, and unnecessary personal data.\n\nMini project\nWrite a short defensive assessment for {title} with a threat model, control map, verification evidence, cleanup plan, and responsible-disclosure path.\n\nSummary\nYou can now reason about {topic} as an authorized defensive practice rather than an offensive action.\n\nNext lesson\n{next_title}"""

def _questions(topic):
    return [
        (f"What is the safest starting point for {topic}?", ["Define scope and authorization", "Scan a public target", "Collect real passwords"], "Define scope and authorization", "Defensive work begins with an explicit, authorized boundary."),
        ("True or false: a tool output is automatically a confirmed security incident.", ["True", "False"], "False", "Evidence needs validation, scope, and context."),
        ("Which control reduces unnecessary access?", ["Least privilege", "Shared root credentials", "Unreviewed wildcard permissions"], "Least privilege", "Least privilege limits actions to what the identity needs."),
        ("What should a lab use by default?", ["Synthetic data and an owned environment", "Public systems", "Real user credentials"], "Synthetic data and an owned environment", "Safe labs minimize harm and protect privacy."),
    ]

def seed_cybersecurity_fundamentals_course(db, course):
    course.title = "Cybersecurity Fundamentals — From Zero to Professional"
    course.short_description = "A free defensive cybersecurity pathway covering security principles, secure engineering, monitoring, risk, cloud security, and incident response."
    course.description = "Build security foundations through ethical, authorized, defensive lessons on risk management, networking, secure coding, cloud security, monitoring, response, privacy, and professional practice."
    course.level, course.status, course.published = "advanced", "published", True
    course.outcomes = "Explain core security principles and risk|Design defensive controls and trust boundaries|Review secure code and configurations|Interpret logs and incident signals|Practice ethical security engineering"
    course.requirements = "Basic computer and programming concepts are helpful. All labs use synthetic data or explicitly authorized local environments. No public scanning, malware, or credential collection is permitted."
    authored = []
    for module_index, module_title in enumerate(MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_index))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_index); db.add(module); db.flush()
        module.title = module_title
        if module_index == 1:
            specs = MODULE_ONE
        else:
            title, topic = GENERAL[module_index - 2]
            specs = [(title, topic, "print('Synthetic defensive example; review scope before testing')", f"This foundation lesson explains {topic}. State the asset, authorization, security objective, threat assumptions, defensive controls, evidence, and recovery path before practical work.", "asset -> control -> evidence", "ဤ foundation lesson တွင် defensive security၊ authorization နှင့် evidence ကို လေ့လာပါမည်။")]
        for lesson_index, (title, topic, code, theory, _diagram, mm) in enumerate(specs, 1):
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm=""); db.add(lesson); db.flush()
            previous = "Basic computer and programming concepts." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
            next_title = "Continue to the next defensive security foundation." if module_index < 40 else "Continue to the cybersecurity capstone."
            lesson.title, lesson.slug = title, slug
            lesson.content_en = _content(title, topic, theory, code, mm, previous, next_title)
            lesson.content_mm = f"{title} ကို English lesson နှင့်အတူ လေ့လာနိုင်ပါသည်။\n\n{mm}\n\nAuthorized environment နှင့် synthetic data ကိုသာ အသုံးပြုပါ။"
            lesson.description, lesson.duration_minutes = theory, 45
            lesson.status, lesson.published = "published", True; authored.append(lesson)
            examples = list(db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all())
            for duplicate in examples[1:]: db.delete(duplicate)
            example = examples[0] if examples else CodeExample(lesson_id=lesson.id, title=f"{title} — defensive example", language="python", filename="defensive_example.py", code=code, position=1)
            if not examples: db.add(example)
            example.title, example.language, example.filename, example.code = f"{title} — defensive example", "python", "defensive_example.py", code
            example.description = "Safe, synthetic, read-only example. Do not use it against systems without explicit authorization."
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz:
                quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review scope, authorization, controls, evidence, privacy, and response.", status="published"); db.add(quiz); db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(topic), 1):
                values = dict(prompt=prompt, question_type="multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                question = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
                if not question: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(question, key, value)
    course.duration_minutes = sum(lesson.duration_minutes or 45 for lesson in authored)
    db.flush()
