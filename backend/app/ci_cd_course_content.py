"""Idempotent CI/CD curriculum seed.

Module 1 is the complete vertical slice. Later modules receive an authored
foundation lesson so the roadmap is visible without claiming 350+ lessons.
The seed stores examples only; it never executes YAML or shell commands.
"""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

MODULES = [
    "Introduction to CI/CD & DevOps", "Software Development Lifecycle", "Git Fundamentals", "GitHub & Collaboration",
    "Linux & Shell Scripting", "CI Pipeline Fundamentals", "GitHub Actions Fundamentals", "Advanced GitHub Actions",
    "Automated Testing in CI", "Build Automation & Artifacts", "GitLab CI/CD Fundamentals", "Advanced GitLab Pipelines",
    "Jenkins Fundamentals", "Jenkins Declarative Pipelines", "Advanced Jenkins Automation", "Docker Fundamentals",
    "Docker Build Optimization", "Container Registries & Supply Chain", "Continuous Delivery Fundamentals", "Deployment Strategies",
    "AWS CI/CD Fundamentals", "AWS Application Deployment", "Kubernetes Fundamentals", "Kubernetes CI/CD", "Helm & GitOps",
    "Terraform for CI/CD", "Infrastructure as Code Pipelines", "Secrets & Identity Management", "DevSecOps & Security Scanning",
    "Software Supply Chain Security", "Pipeline Monitoring & Observability", "Troubleshooting Failed Pipelines",
    "Performance & Cost Optimization", "Release Management & Rollbacks", "Multi-Environment CI/CD", "Enterprise Pipeline Architecture",
    "CI/CD for Full-Stack Applications", "CI/CD Testing & Quality Engineering", "Real-World CI/CD Projects", "Final CI/CD Capstone & Assessment",
]

MODULE_ONE = [
    ("What Is CI/CD?", "continuous integration, continuous delivery, and repeatable feedback", "echo 'Example only: source -> test -> build -> deploy -> verify'", "CI integrates small changes frequently and runs automated checks. Continuous delivery keeps a releasable artifact ready; continuous deployment additionally releases automatically under approved policy. DevOps is a collaboration and systems practice, not a tool brand. Measure feedback time, failure recovery, and change risk.", "commit -> checks -> artifact -> environment -> evidence", "CI/CD သည် code change များကို အမြန်စစ်ဆေးပြီး repeatable artifact အဖြစ် ထုတ်လုပ်သည့် workflow ဖြစ်သည်။"),
    ("Software Delivery Flow", "source, validation, packaging, deployment, and verification stages", "echo 'Example only: every stage has an owner and an observable result'", "A delivery pipeline is a set of explicit stages with inputs, outputs, dependencies, and failure handling. A green build means only that the defined checks passed; it is not proof of production safety. Add approvals, rollback signals, and environment boundaries where risk requires them.", "source -> lint -> test -> build -> scan -> publish -> deploy -> verify", "Pipeline တစ်ခုတွင် stage တိုင်း၏ input၊ output၊ dependency နှင့် failure handling ကို သတ်မှတ်ရသည်။"),
    ("Git Branches, Commits, and Pull Requests", "version history as the input to automation", "git status\ngit log --oneline -5\n# Run locally; examples are not executed by CodeMaster Academy", "Automation starts with trustworthy source history. Small commits, protected branches, reviewed pull requests, and reproducible tags make failures traceable. Never put credentials in commits; rotate anything exposed and treat history as persistent evidence.", "working tree -> commit -> review -> protected branch", "Git history သည် pipeline အတွက် source of truth ဖြစ်သောကြောင့် commit နှင့် pull request များကို သေချာစွာ review လုပ်ပါ။"),
    ("GitHub Collaboration and Protected Environments", "reviews, branch protection, permissions, and release ownership", "echo 'Example only: require review before production deployment'", "Repository settings are part of the security model. Use least-privilege workflow permissions, protected branches, environment approvals, and separate deployment identities. Untrusted pull requests must not receive privileged secrets. OIDC is preferable to long-lived cloud keys when a provider supports it.", "pull request -> checks -> review -> protected environment", "Protected branch နှင့် environment approval သည် repository security model ၏ အစိတ်အပိုင်းများ ဖြစ်သည်။"),
    ("Linux and Bash for Automation", "portable commands, exit codes, and defensive scripts", "set -euo pipefail\nprintf '%s\\n' 'Example only: fail fast and make output explicit'", "A shell script is an interface with quoting, inputs, exit codes, and side effects. Use strict modes deliberately, validate paths, avoid secret leakage, and make destructive operations opt-in. The platform displays scripts but never runs learner-provided shell on the host.", "input -> validated command -> exit code -> log", "Bash script တွင် input validation၊ exit code နှင့် secret redaction ကို ဦးစားပေးပါ။"),
    ("Your First CI Pipeline", "a deterministic lint-and-test workflow", "name: CI\non: [push, pull_request]\njobs:\n  checks:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - run: python -m compileall .", "A minimal pipeline checks out source and runs a deterministic validation step. Pin actions to reviewed immutable references for production, restrict permissions, cache only safe dependencies, and upload artifacts only when their contents are understood. This example is for reading and local review.", "event -> runner -> checkout -> check -> status", "ပထမ CI pipeline သည် source ကို checkout လုပ်ပြီး deterministic check တစ်ခု run လုပ်သည်။"),
    ("Module 1 Review and Pipeline Assessment", "designing a safe pipeline with evidence and rollback", "echo 'Example only: lint -> test -> scan -> package -> approval -> deploy'", "A professional pipeline makes quality, security, and release decisions visible. Define the artifact contract, test evidence, approval gate, deployment identity, environment configuration, monitoring signal, and rollback procedure before enabling automation. A simulator is not an actual GitHub Actions or production run.", "change -> evidence -> approval -> release -> verification/rollback", "Pipeline design တွင် artifact၊ test evidence၊ approval၊ identity၊ monitoring နှင့် rollback ကို ရှင်းလင်းစွာ ရေးသားပါ။"),
]

GENERAL = [
    ("SDLC and Feedback Loops", "planning, implementation, validation, release, and learning loops"), ("Git Internals", "objects, refs, merges, rebases, and safe history"), ("GitHub Repository Operations", "issues, reviews, permissions, and collaboration"), ("Shell Automation", "portable Bash, exit codes, and safe side effects"), ("CI Concepts", "triggers, runners, jobs, steps, and artifacts"), ("GitHub Actions Basics", "workflow syntax, permissions, and event filters"), ("GitHub Actions at Scale", "matrices, reusable workflows, environments, and approvals"), ("Testing in CI", "unit, integration, contract, and end-to-end checks"), ("Builds and Artifacts", "reproducible builds, provenance, and retention"), ("GitLab CI Basics", "stages, jobs, runners, and variables"), ("GitLab Pipeline Design", "rules, needs, environments, and protected variables"), ("Jenkins Fundamentals", "controllers, agents, credentials, and jobs"), ("Jenkins Declarative Pipelines", "Jenkinsfile stages, post actions, and approvals"), ("Jenkins Automation", "shared libraries, agents, and safe credentials"), ("Docker Fundamentals", "images, containers, layers, and lifecycle"), ("Docker Build Optimization", "multi-stage builds, caching, and small images"), ("Container Supply Chain", "registries, signing, scanning, and provenance"), ("Continuous Delivery", "release candidates, environments, and promotion"), ("Deployment Strategies", "rolling, blue-green, canary, and feature flags"), ("AWS CI/CD", "OIDC, artifacts, and service boundaries"), ("AWS Application Delivery", "deploying with approvals and rollback evidence"), ("Kubernetes Fundamentals", "workloads, services, namespaces, and probes"), ("Kubernetes Delivery", "manifests, rollout status, and safe promotion"), ("Helm and GitOps", "charts, values, reconciliation, and drift"), ("Terraform Pipelines", "fmt, validate, plan, apply approval, and state"), ("Infrastructure Pipeline Design", "drift, policy checks, and environment isolation"), ("Secrets and Identity", "OIDC, vaults, rotation, and redaction"), ("DevSecOps Scanning", "SAST, dependency, container, and IaC checks"), ("Software Supply Chain", "SBOMs, signing, attestations, and trusted inputs"), ("Pipeline Observability", "logs, metrics, traces, and failure alerts"), ("Failed Pipeline Troubleshooting", "failure isolation, evidence, and safe retries"), ("Pipeline Performance and Cost", "caching, concurrency, and runner economics"), ("Release and Rollback", "versioning, approvals, health checks, and recovery"), ("Multi-Environment Delivery", "development, staging, production, and configuration"), ("Enterprise Pipeline Architecture", "governance, reusable workflows, and ownership"), ("Full-Stack CI/CD", "React, Next.js, FastAPI, Laravel, and database checks"), ("Quality Engineering", "test strategy, flaky tests, and quality gates"), ("CI/CD Projects", "scoping, documentation, verification, and teardown"), ("CI/CD Capstone", "defending a secure pipeline architecture and trade-offs"),
]

def _slug(value): return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(title, topic, theory, code, mm, previous, next_title):
    return f"""Introduction\n{title} introduces {topic} through a theory-first, read-only workflow. CodeMaster Academy displays configuration examples but never executes learner YAML, Bash, Docker, Kubernetes, Terraform, or cloud commands.\n\nLearning objectives\n- Explain {topic} and its role in a delivery system.\n- Identify inputs, outputs, dependencies, failure behavior, and evidence.\n- Apply least privilege, secret protection, and rollback thinking.\n\nPrerequisites\n{previous}\n\nPipeline diagram\nsource -> lint -> test -> build -> security scan -> package -> publish -> staging -> approval -> production -> verify -> rollback\n\nTheory\n{theory}\n\nYAML or script example\n```yaml\n{code}\n```\nThis is a read-only example. Pin third-party actions to reviewed immutable references for production, and do not place secrets in source control.\n\nLine-by-line explanation\n- The trigger or input starts a bounded workflow.\n- Each job should have a clear dependency and least-privilege permission.\n- Outputs should be traceable artifacts or reviewable logs.\n- A failure must stop or route to an explicit recovery path.\n\nCLI commands\nUse local documentation and a disposable repository for commands. The platform does not execute untrusted scripts or contact external services.\n\nExpected logs/output\nExample only: a successful check reports its status and an artifact identifier; a failed check reports the stage and exit code. No displayed output is live.\n\nHands-on lab\nModel {topic} using a local README and a simulated pipeline. Record the trigger, stage dependencies, artifact, approval gate, verification signal, and rollback action.\n\nVerification steps\n1. Confirm the workflow is syntactically valid with the relevant official tool locally.\n2. Check permissions and secret references.\n3. Trace one success and one failure path.\n4. Confirm the cleanup and rollback procedure.\n\nTroubleshooting\nRead the first failing stage, preserve logs, verify the working directory and dependency versions, then reproduce locally. Retry only idempotent steps; do not hide a failure with `|| true`.\n\nSecurity considerations\nUse least-privilege runner permissions, OIDC or short-lived credentials, protected environments, pinned dependencies, secret scanning, and redacted logs. Untrusted pull requests must not access privileged secrets.\n\nCost considerations\nHosted runners, artifact storage, registries, cloud services, and observability can incur charges. Review quotas, retention, concurrency, and cloud pricing before enabling a real pipeline.\n\nCleanup instructions\nThis lesson creates no external resource. Remove local containers, temporary artifacts, test credentials, and disposable branches after practice. Never delete shared production resources from a learning exercise.\n\nCommon mistakes\n- Treating a green unit test as proof of production readiness.\n- Giving every job administrator permissions.\n- Running untrusted pull-request code with deployment secrets.\n- Retrying non-idempotent deployment steps without review.\n\nBest practices\nKeep workflows small, observable, reproducible, reviewable, and reversible. Document ownership, artifact provenance, approval policy, and rollback signals.\n\nPractice exercises\n- Easy: label each pipeline stage and its output.\n- Medium: repair a workflow with an excessive permission and missing test dependency.\n- Challenge: design parallel test jobs followed by one protected deployment gate.\n\nQuiz\n1. What should protect production deployment? A policy-based approval and verification gate.\n2. True or false: pipeline simulation is an actual provider run. False.\n3. What should never be committed? Credentials and long-lived secrets.\n\nMini project\nCreate a local pipeline decision record for {title} with a diagram, sample configuration, security controls, cost risks, and rollback procedure.\n\nSummary\nYou can now reason about {topic} as a verifiable delivery system instead of a collection of commands.\n\nNext lesson\n{next_title}"""

def _questions(topic):
    return [
        (f"What makes a {topic} stage reviewable?", ["Explicit input, output, and evidence", "Only a green icon", "A shared root credential"], "Explicit input, output, and evidence", "A stage needs a contract and evidence that can be inspected."),
        ("True or false: a simulated pipeline is an actual provider run.", ["True", "False"], "False", "The simulator models deterministic state transitions only."),
        ("Which credential pattern is preferred for cloud delivery?", ["Short-lived identity or OIDC", "A key committed to YAML", "A shared root password"], "Short-lived identity or OIDC", "Short-lived access reduces exposure and supports auditable trust."),
        ("What should a failed deployment have?", ["A tested rollback or recovery path", "An ignored error", "An automatic destructive retry"], "A tested rollback or recovery path", "Failure handling must be explicit and proportionate."),
    ]

def seed_ci_cd_course(db, course):
    course.title = "CI/CD & DevOps Engineering — From Zero to Professional"
    course.short_description = "A free, security-conscious pathway from Git and CI fundamentals to containers, GitOps, infrastructure pipelines, and production release design."
    course.description = "Learn to design observable, secure, reproducible CI/CD pipelines with GitHub Actions, GitLab CI, Jenkins, Docker, Kubernetes, Terraform, AWS, testing, scanning, approvals, and rollback strategies."
    course.level, course.status, course.published = "advanced", "published", True
    course.outcomes = "Explain CI/CD and DevOps feedback loops|Build readable workflow configurations|Protect secrets and deployment identities|Design container and infrastructure pipelines|Troubleshoot failures and plan rollbacks"
    course.requirements = "Basic Git and programming concepts are helpful. Examples are read-only; no external pipeline, cloud resource, or deployment is created by this course."
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
            specs = [(title, topic, "echo 'Example only: validate this workflow locally'", f"This foundation lesson explains {topic}. Make the pipeline contract explicit, protect identities and secrets, preserve evidence, and test rollback before enabling automation.", "requirements -> workflow -> evidence", "ဤ foundation lesson တွင် CI/CD workflow၊ security နှင့် rollback ကို လေ့လာပါမည်။")]
        for lesson_index, (title, topic, code, theory, _diagram, mm) in enumerate(specs, 1):
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm=""); db.add(lesson); db.flush()
            previous = "Basic programming and Git concepts." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
            next_title = "Continue to the next CI/CD foundation." if module_index < 40 else "Continue to the final CI/CD capstone."
            lesson.title, lesson.slug = title, slug
            lesson.content_en = _content(title, topic, theory, code, mm, previous, next_title)
            lesson.content_mm = f"{title} ကို English lesson နှင့်အတူ လေ့လာနိုင်ပါသည်။\n\n{mm}\n\nPlatform သည် YAML သို့မဟုတ် shell command များကို မ run ပါ။"
            lesson.description, lesson.duration_minutes = theory, 45
            lesson.status, lesson.published = "published", True; authored.append(lesson)
            examples = list(db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all())
            for duplicate in examples[1:]: db.delete(duplicate)
            example = examples[0] if examples else CodeExample(lesson_id=lesson.id, title=f"{title} — workflow example", language="yaml", filename="workflow.yml", code=code, position=1)
            if not examples: db.add(example)
            example.title, example.language, example.filename, example.code = f"{title} — workflow example", "yaml", "workflow.yml", code
            example.description = "Read-only configuration example. The platform never executes learner workflow or shell content."
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz:
                quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review stage contracts, identity, secrets, evidence, cost, and rollback.", status="published"); db.add(quiz); db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(topic), 1):
                values = dict(prompt=prompt, question_type="multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                question = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
                if not question: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(question, key, value)
    course.duration_minutes = sum(lesson.duration_minutes or 45 for lesson in authored)
    db.flush()
