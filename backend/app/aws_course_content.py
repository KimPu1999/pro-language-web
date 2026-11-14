"""Idempotent, cost-safe AWS curriculum seed.

Module 1 is the complete vertical slice. The later modules intentionally have
one authored foundation lesson each until their full lesson sets are written.
This content never provisions AWS resources or executes a learner's commands.
"""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

MODULES = [
    "Introduction to Cloud Computing", "AWS Global Infrastructure", "AWS Account & Billing Setup",
    "AWS Management Console & CLI", "AWS Shared Responsibility & Well-Architected", "IAM Fundamentals",
    "Advanced IAM & Organizations", "Amazon EC2 Fundamentals", "EC2 Scaling & Load Balancing",
    "Amazon S3 Fundamentals", "Advanced AWS Storage", "Amazon VPC Fundamentals", "Advanced VPC Networking",
    "DNS & Amazon Route 53", "CloudFront & Content Delivery", "AWS Networking Security", "Amazon RDS",
    "Amazon Aurora & Database Scaling", "Amazon DynamoDB", "AWS Lambda Fundamentals", "Amazon API Gateway",
    "Event-Driven AWS Architecture", "Docker Fundamentals for AWS", "Amazon ECS & Fargate", "Amazon EKS & Kubernetes",
    "AWS CloudFormation", "Terraform for AWS", "AWS Systems Manager & Automation", "AWS CI/CD & Deployment",
    "CloudWatch & Observability", "CloudTrail, Config & Governance", "AWS Secrets & Encryption",
    "Security Operations & Threat Detection", "Backup, Disaster Recovery & Resilience", "AWS Solution Architecture",
    "High Availability & Performance", "AWS Cost Optimization & FinOps", "AWS Certification Preparation",
    "Real-World AWS Projects", "Final AWS Cloud Capstone",
]

MODULE_ONE = [
    ("What Is Cloud Computing?", "on-demand computing, storage, networking, and managed services", "echo 'Example only: cloud capacity is requested on demand'", "Cloud computing provides shared computing resources through a network. The important trade-off is not simply renting someone else's server: managed services change the amount of infrastructure you operate, the failure modes you design for, and the costs you monitor. Start with requirements, data sensitivity, availability, and an exit or cleanup plan.", "Cloud service model: workload -> provider-managed infrastructure -> observable result", "Cloud computing သည် network မှတစ်ဆင့် လိုအပ်သလို computing၊ storage နှင့် networking resources ရယူအသုံးပြုခြင်း ဖြစ်သည်။"),
    ("AWS Global Infrastructure", "regions, Availability Zones, edge locations, and fault domains", "echo 'Example only: choose a region after checking latency, services, and pricing'", "An AWS Region is a geographic area containing isolated Availability Zones. Availability Zones are separate locations within a Region; distributing replicas across them reduces correlated facility failure risk. Edge locations serve content closer to users. Region choice also affects legal residency, latency, service availability, and price.", "users -> edge location -> region -> Availability Zones", "Region၊ Availability Zone နှင့် edge location တို့သည် latency၊ resilience နှင့် data residency ဆုံးဖြတ်ချက်များကို သက်ရောက်စေသည်။"),
    ("AWS Account, Regions, and Billing Safety", "budgets, account boundaries, and safe first steps", "echo 'Example only: configure a budget before creating chargeable resources'", "An AWS account is a billing and security boundary, not a guarantee of zero cost. Use a dedicated email and strong recovery controls, enable MFA, configure a budget alert, and prefer a non-root administrator role for routine work. The course never asks learners to paste access keys into CodeMaster Academy.", "account -> identity -> budget alert -> approved resource lifecycle", "AWS account သည် billing နှင့် security boundary ဖြစ်ပြီး service အားလုံး အခမဲ့ဖြစ်ကြောင်း မဆိုလိုပါ။"),
    ("AWS Management Console and CLI Fundamentals", "console navigation, named profiles, and read-only inspection", "aws sts get-caller-identity\n# Example command: run locally only, never paste credentials here", "The console is useful for discovery; the CLI is repeatable and scriptable. Use a local named profile or temporary credentials supplied by an approved identity workflow. Begin with read-only inspection and confirm the account and Region before any change. Outputs in this lesson are examples, not live account data.", "identity check -> read-only describe/list -> review -> deliberate change", "Console သည် ရှာဖွေလေ့လာရန်ကောင်းပြီး CLI သည် repeatable ဖြစ်သည်။ Command များကို local environment တွင်သာ run လုပ်ပါ။"),
    ("Shared Responsibility and Well-Architected Thinking", "what AWS secures and what the customer must configure", "echo 'Example only: verify identity, logging, backups, and least privilege'", "AWS secures the underlying cloud infrastructure; customers remain responsible for choices such as data, identities, configuration, operating systems where applicable, network rules, backups, and application code. The Well-Architected pillars—operational excellence, security, reliability, performance efficiency, cost optimization, and sustainability—help expose trade-offs before deployment.", "requirements -> design principles -> controls -> evidence -> review", "AWS နှင့် customer တာဝန်ခွဲခြားမှုကို နားလည်ပြီး Well-Architected pillars ဖြင့် design ကို review လုပ်ရသည်။"),
    ("IAM Fundamentals and Least Privilege", "principals, policies, roles, and temporary access", "echo 'Example only: inspect a policy before attaching it'\necho 'Never use a wildcard policy as a shortcut'", "IAM controls who can do what on which resource under which conditions. Prefer federated or temporary access, MFA for privileged actions, groups or roles over individual long-lived keys, and policies that name only required actions and resources. Deny-by-default is safer than relying on a UI restriction.", "principal + action + resource + condition -> decision", "IAM တွင် ဘယ်သူက ဘာလုပ်နိုင်သည်ကို policy ဖြင့် သတ်မှတ်သည်။ Least privilege နှင့် temporary access ကို ဦးစားပေးပါ။"),
    ("Module 1 Review and Architecture Assessment", "evaluating a safe first architecture without provisioning it", "echo 'Example only: S3 + CloudFront can serve static content; validate requirements first'", "A sound architecture connects requirements to services and controls. For a static website, an origin, delivery layer, TLS policy, logging, access policy, cache behavior, and cleanup owner must be explicit. A diagram is a model—not proof that resources exist or that a design is production-ready.", "requirements -> architecture -> security/cost review -> documented decision", "Architecture diagram သည် resource တကယ်ရှိကြောင်း သက်သေမဟုတ်ဘဲ design model တစ်ခုသာ ဖြစ်သည်။"),
]

GENERAL = [
    ("Global Infrastructure Concepts", "region selection, Availability Zones, and edge delivery"),
    ("Account and Billing Guardrails", "budgets, cost allocation, and cleanup ownership"),
    ("Console and CLI Workflow", "safe discovery and repeatable cloud operations"),
    ("Shared Responsibility Review", "service boundaries and Well-Architected trade-offs"),
    ("Identity Design", "least privilege, roles, MFA, and temporary credentials"),
    ("Organizations and Governance", "account separation, service control policies, and guardrails"),
    ("EC2 Compute Foundations", "instances, AMIs, storage, security groups, and lifecycle"),
    ("Scaling and Load Balancing", "health checks, target groups, and horizontal scaling"),
    ("S3 Object Storage", "buckets, object policies, encryption, and lifecycle rules"),
    ("Advanced Storage Choices", "EBS, EFS, S3 tiers, and durability trade-offs"),
    ("VPC Foundations", "subnets, route tables, internet gateways, and boundaries"),
    ("Advanced VPC Networking", "NAT, endpoints, peering, and transit patterns"),
    ("Route 53 DNS", "hosted zones, records, health checks, and routing policies"),
    ("CloudFront Delivery", "origins, caching, TLS, and invalidation costs"),
    ("Network Security", "security groups, network ACLs, and private access"),
    ("RDS Relational Databases", "subnet groups, backups, Multi-AZ, and connections"),
    ("Aurora Scaling", "cluster endpoints, replicas, and failover"),
    ("DynamoDB", "keys, indexes, capacity modes, and access patterns"),
    ("Lambda Functions", "events, permissions, timeouts, and observability"),
    ("API Gateway", "routes, authentication, throttling, and deployment stages"),
    ("Event-Driven Architecture", "SQS, SNS, EventBridge, retries, and idempotency"),
    ("Containers on AWS", "images, registries, tasks, and runtime boundaries"),
    ("ECS and Fargate", "service discovery, deployments, and task roles"),
    ("EKS and Kubernetes", "control planes, nodes, IAM integration, and cost"),
    ("CloudFormation", "declarative infrastructure, change sets, and drift"),
    ("Terraform for AWS", "state, plans, modules, and secret-safe workflows"),
    ("Systems Manager", "managed nodes, parameters, automation, and auditability"),
    ("CI/CD Deployment", "artifacts, approvals, rollback, and least privilege"),
    ("CloudWatch Observability", "metrics, logs, alarms, dashboards, and retention"),
    ("CloudTrail and Config", "audit events, configuration history, and governance"),
    ("Secrets and Encryption", "KMS, Secrets Manager, rotation, and key policy"),
    ("Threat Detection", "findings, triage, response, and evidence"),
    ("Backup and Disaster Recovery", "RPO, RTO, restore testing, and cleanup"),
    ("Solution Architecture", "requirements, diagrams, trade-offs, and review"),
    ("Availability and Performance", "failure domains, caching, and capacity"),
    ("FinOps and Cost Optimization", "budgets, tagging, rightsizing, and unit economics"),
    ("Certification Preparation", "scenario reasoning and documentation discipline"),
    ("Real-World AWS Projects", "secure project scope, verification, and teardown"),
    ("AWS Capstone Review", "defending an architecture with evidence and limitations"),
]

def _slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(title, topic, theory, code, mm, previous, next_title):
    return f"""Introduction\n{title} introduces {topic} using a provider-neutral mental model and AWS terminology. This is an educational, read-only lesson; no AWS resource is created by the platform.\n\nLearning objectives\n- Explain {topic} in your own words.\n- Identify the security, reliability, and cost decisions involved.\n- Verify assumptions with documentation rather than fabricated account data.\n\nPrerequisites\n{previous}\n\nAWS service overview\nAWS services are building blocks with different management boundaries, failure modes, permissions, and pricing. Confirm the current service documentation and Region availability before applying an example.\n\nArchitecture diagram\nrequirements -> identity and network boundary -> AWS service -> logs, alerts, backup, and cleanup owner\n\nConsole walkthrough\nOpen the relevant AWS console only in your own account, confirm the account alias and Region, inspect the read-only overview, and record the setting you intend to verify. Do not share screenshots containing account identifiers or secrets.\n\nAWS CLI example\n```bash\n{code}\n```\nThe command/output is an example. CodeMaster Academy does not execute it, access your AWS account, or display live account data.\n\nIAM permissions required\nUse the narrowest read-only permission needed for local inspection. Prefer a temporary role or approved identity provider. Never paste access keys, session tokens, or root credentials into the website.\n\nHands-on lab\nCreate a paper design or local checklist for {topic}. Mark the identity, public/private boundary, logging, budget, verification, and cleanup owner. This lab is simulation/read-only and does not provision AWS infrastructure.\n\nExpected results and verification\nYou can explain the design, name the assumptions, identify the evidence needed, and state what would prove the result. Any displayed output is illustrative, not a live result.\n\nSecurity considerations\nUse MFA for privileged access, least privilege, encryption where appropriate, private networking by default, HTTPS, and redacted logs. Do not treat a client-side UI restriction as authorization.\n\nCost considerations\nAWS infrastructure may incur charges. Check current regional pricing, quotas, budgets, and free-tier terms before creating anything; free learning content does not make AWS usage universally free.\n\nCleanup instructions\nNo resource is created by this lesson. If you run an example locally in your account, list what was created, remove it deliberately, verify dependent resources, and review billing after cleanup.\n\nTroubleshooting\nIf a command fails, confirm the selected profile, Region, permission boundary, resource identifiers, service availability, and current AWS documentation. Never solve an AccessDenied error by attaching AdministratorAccess blindly.\n\nExercises\n- Easy: summarize the service boundary and identify one read-only check.\n- Medium: draw the data flow and mark public/private components.\n- Challenge: compare two designs and document security, availability, and cost trade-offs.\n\nQuiz\n1. Should example output be treated as live account data? No; it is illustrative.\n2. What is the safest default for credentials? Temporary, least-privilege access outside this platform.\n3. What must every lab include? Verification, cost warning, and cleanup.\n\nMini project\nWrite a one-page architecture decision record for {title}, including assumptions, controls, estimated cost risks, and a rollback/cleanup plan.\n\nSummary\nYou can now reason about {topic} without confusing an architecture model with a deployed AWS resource.\n\nNext lesson\n{next_title}"""

def _questions(topic):
    return [
        (f"Which evidence is appropriate when reviewing {topic}?", ["Documented read-only inspection", "A fabricated account screenshot", "A shared root key"], "Documented read-only inspection", "Reviewable evidence should come from an authorized environment and be redacted."),
        ("True or false: free course content makes every AWS resource free.", ["True", "False"], "False", "AWS usage can incur charges; pricing and cleanup must be checked."),
        ("What should happen before a chargeable lab?", ["Set a budget and understand cleanup", "Paste credentials into the browser", "Skip permissions review"], "Set a budget and understand cleanup", "Cost and identity guardrails belong before provisioning."),
        ("Where should untrusted cloud commands run?", ["Only in an explicitly authorized local workflow", "Inside the API worker", "With root credentials"], "Only in an explicitly authorized local workflow", "The platform never executes commands against learner accounts."),
    ]

def seed_aws_course(db, course):
    course.title = "AWS Cloud Computing & Architecture — Zero to Advanced"
    course.short_description = "A free, cost-aware AWS learning path from cloud foundations to architecture, security, operations, and capstone design."
    course.description = "Learn AWS concepts through service overviews, safe architecture diagrams, read-only CLI examples, cost warnings, labs, quizzes, and project planning. No AWS infrastructure is provisioned by this course."
    course.level, course.status, course.published = "advanced", "published", True
    course.outcomes = "Explain cloud and AWS architecture|Design secure and resilient service boundaries|Use least-privilege IAM concepts|Reason about cost and cleanup|Document architecture decisions and trade-offs"
    course.requirements = "Basic networking and programming concepts are helpful. An AWS account is optional for the introductory read-only lessons. AWS usage can incur charges."
    authored = []
    for module_index, module_title in enumerate(MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_index))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_index); db.add(module); db.flush()
        module.title = module_title
        specs = MODULE_ONE if module_index == 1 else [(GENERAL[module_index - 2][0], GENERAL[module_index - 2][1], "echo 'Example only: review the current AWS documentation locally'", f"This foundation lesson explains {GENERAL[module_index - 2][1]}. Apply explicit requirements, identity boundaries, verification evidence, cost controls, and cleanup before considering a real deployment.", "requirements -> controlled inspection -> evidence", "ဤ foundation lesson သည် AWS architecture နှင့် safety controls ကို လေ့လာစေသည်။")]
        for lesson_index, (title, topic, code, theory, _diagram, mm) in enumerate(specs, 1):
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm=""); db.add(lesson); db.flush()
            previous = "Basic cloud and networking concepts." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
            next_title = "Continue to the next AWS foundation." if module_index < 40 else "Continue to the AWS capstone review."
            lesson.title, lesson.slug = title, slug
            lesson.content_en = _content(title, topic, theory, code, mm, previous, next_title)
            lesson.content_mm = f"{title} ကို English lesson နှင့်အတူ လေ့လာနိုင်ပါသည်။\n\n{mm}\n\nAWS resource များကို platform က မဖန်တီးပါ။ Cost နှင့် cleanup ကို အမြဲစစ်ဆေးပါ။"
            lesson.description, lesson.duration_minutes = theory, 45
            lesson.status, lesson.published = "published", True
            authored.append(lesson)
            examples = list(db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all())
            for duplicate in examples[1:]: db.delete(duplicate)
            example = examples[0] if examples else CodeExample(lesson_id=lesson.id, title=f"{title} — AWS CLI example", language="bash", filename="aws-example.sh", code=code, position=1)
            if not examples: db.add(example)
            example.title, example.language, example.filename, example.code = f"{title} — AWS CLI example", "bash", "aws-example.sh", code
            example.description = "Read-only educational example. The platform does not execute AWS commands or access learner accounts."
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz:
                quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the security, cost, verification, and cleanup notes.", status="published"); db.add(quiz); db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(topic), 1):
                values = dict(prompt=prompt, question_type="multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                question = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
                if not question: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(question, key, value)
    course.duration_minutes = sum(lesson.duration_minutes or 45 for lesson in authored)
    db.flush()
