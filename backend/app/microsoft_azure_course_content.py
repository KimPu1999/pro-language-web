"""Authored Microsoft Azure vertical slice for the idempotent catalog seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

PLANNED_MODULES = [
    "Introduction to Cloud Computing", "Introduction to Microsoft Azure", "Azure Account & Subscription Setup",
    "Azure Portal Fundamentals", "Azure CLI & Cloud Shell", "Azure Resource Manager", "Azure Pricing & Cost Management",
    "Azure Virtual Machines", "Azure VM Administration", "Azure Virtual Networking", "Network Security Groups",
    "Azure DNS & Load Balancing", "VPN, Private Connectivity & Peering", "Azure Storage Fundamentals",
    "Blob, Files, Queues & Tables", "Microsoft Entra ID Fundamentals", "Azure RBAC & Managed Identities",
    "Azure App Service", "Azure Functions & Serverless", "Azure Container Apps", "Azure Kubernetes Service",
    "Azure SQL Database", "Azure Database for PostgreSQL", "Azure Cosmos DB", "Azure Key Vault & Secrets",
    "Azure Security Fundamentals", "Microsoft Defender for Cloud", "Azure Monitor & Log Analytics",
    "Application Insights", "Azure Backup & Disaster Recovery", "High Availability & Scalability",
    "Infrastructure as Code with Bicep", "Terraform on Azure", "Azure DevOps Fundamentals",
    "GitHub Actions for Azure", "Azure Networking & Security Architecture", "Production Application Deployment",
    "Cloud Governance & Architecture", "Professional Azure Cloud Projects", "Final Azure Capstone & Assessment",
]

MODULE_ONE = [
    ("Cloud Computing and Shared Responsibility", "cloud models, elasticity, and responsibility boundaries",
     "printf 'client -> cloud service -> provider responsibility\\n'\\n# Record which controls belong to you",
     "bash", "Cloud computing provides on-demand access to compute, storage, networking, and managed services. IaaS leaves more operating-system responsibility with the customer, while PaaS and SaaS shift more maintenance to the provider. Shared responsibility must be checked for every service.",
     "Cloud computing သည် compute၊ storage နှင့် networking services များကို on-demand ပေးသည်။ IaaS/PaaS/SaaS တိုင်းတွင် customer နှင့် provider တာဝန်ကွာခြားသည်။",
     "Create a responsibility table for an Azure VM, App Service, and Storage account.",
     ("Which statement describes shared responsibility?", ["Provider and customer split controls according to the service", "The provider owns every customer secret", "The customer manages the provider datacenter"], "Provider and customer split controls according to the service", "Responsibility changes with the selected service model.")),
    ("Microsoft Azure Global Infrastructure", "regions, availability zones, and resiliency choices",
     "az account list\\naz account show\\n# Use a permitted region only after checking policy",
     "azure-cli", "Azure resources are deployed into regions and some services support availability zones. Region selection affects latency, compliance, resilience, and price. A design should document its recovery region and avoid assuming every service exists everywhere.",
     "Azure resource များသည် region နှင့် availability zone များတွင် deploy လုပ်သည်။ Region ရွေးချယ်မှုသည် latency၊ compliance၊ resilience နှင့် cost ကို သက်ရောက်သည်။",
     "Compare primary and recovery regions for a small API and explain the trade-offs.",
     ("Region ရွေးချယ်ရာတွင် ဘာကိုစဉ်းစားရမည်နည်း?", ["Latency, compliance, availability, service support, and cost", "Only the region name", "A private access token"], "Latency, compliance, availability, service support, and cost", "Infrastructure placement is a reliability and governance decision.")),
    ("Azure Accounts, Tenants, and Subscriptions", "Microsoft Entra tenants, subscriptions, and billing boundaries",
     "az account list --output table\\naz account show --query '{name:name,id:id,tenantId:tenantId}'",
     "azure-cli", "A tenant represents an identity boundary and a subscription is a management and billing boundary. A user can have access to multiple subscriptions. Never confuse a subscription identifier with a secret, and never paste tokens into terminal history or lessons.",
     "Tenant သည် identity boundary ဖြစ်ပြီး subscription သည် management နှင့် billing boundary ဖြစ်သည်။ Subscription ID သည် secret မဟုတ်သော်လည်း token များကို မဖော်ပြပါနှင့်။",
     "Draw tenant → subscription → resource group → resource hierarchy and mark authorization points.",
     ("Subscription က ဘာကို ကိုယ်စားပြုသနည်း?", ["A management and billing boundary", "A VM password", "A public DNS record"], "A management and billing boundary", "Subscriptions organize access, resources, and charges.")),
    ("Azure Portal Fundamentals", "resource search, dashboards, tags, and safe navigation",
     "az group list --output table\\naz resource list --resource-group learn-rg --output table",
     "azure-cli", "The Azure Portal is a management interface, not a substitute for governance. Use resource search, activity history, tags, and deployment views to understand what changed. Confirm subscription, region, resource group, and estimated cost before creating anything.",
     "Azure Portal သည် management interface ဖြစ်သည်။ Subscription၊ region၊ resource group နှင့် cost ကို မစစ်ဘဲ resource မဖန်တီးပါနှင့်။",
     "Write a preflight checklist for creating a disposable learning resource group.",
     ("Resource မဖန်တီးမီ ဘာကိုစစ်သင့်သနည်း?", ["Subscription, region, permissions, naming, and cost", "Only the display color", "A copied secret"], "Subscription, region, permissions, naming, and cost", "A preflight check prevents accidental scope and billing mistakes.")),
    ("Azure CLI and Cloud Shell", "authenticated command workflows and command safety",
     "az version\\naz login\\naz account show\\naz group list",
     "azure-cli", "Azure CLI provides repeatable management commands. Cloud Shell is a managed shell, while a local CLI uses your workstation. Login is simulated in Academy exercises; never collect credentials or run arbitrary shell commands on the application host.",
     "Azure CLI သည် repeatable management workflow ပေးသည်။ Academy တွင် login ကို simulation အဖြစ်သာ လေ့လာပြီး credential မစုဆောင်းပါ။",
     "Annotate each command with its scope, read/write behavior, and cleanup plan.",
     ("Azure CLI lesson တွင် အရေးကြီးဆုံး safety practice က ဘာလဲ?", ["Inspect account context and scope before write commands", "Paste tokens into scripts", "Run unknown commands as administrator"], "Inspect account context and scope before write commands", "Context and least privilege reduce accidental mutations.")),
    ("Azure Resource Groups and ARM", "resource organization, deployments, tags, and lifecycle",
     "az group create --name learn-rg --location eastus --tags purpose=learning\\naz group show --name learn-rg",
     "azure-cli", "Resource groups are lifecycle and organization boundaries. Azure Resource Manager coordinates deployments and policy. A resource can have dependencies, so deletion should be planned and confirmed; use a disposable group for practice.",
     "Resource group သည် lifecycle နှင့် organization boundary ဖြစ်သည်။ ARM သည် deployment နှင့် policy ကို စီမံသည်။ Practice အတွက် disposable group သုံးပါ။",
     "Design a naming and tagging policy with owner, environment, expiry, and cost-center tags.",
     ("Resource group ကို ဘာအတွက်အသုံးပြုသနည်း?", ["Organize resources and manage a lifecycle boundary", "Store plaintext passwords", "Replace all identity controls"], "Organize resources and manage a lifecycle boundary", "Groups support organization, policy, and cleanup.")),
    ("Azure Pricing and Cost Management", "budgets, estimates, quotas, and cleanup",
     "az consumption budget list\\n# Review pricing and delete disposable resources after practice",
     "azure-cli", "Azure course content is free, but real cloud resources can incur charges. Pricing depends on service, region, tier, usage, egress, and retention. Set budgets and alerts, use tags, choose free or sandbox alternatives where eligible, and clean up resources.",
     "Course content သည် free ဖြစ်သော်လည်း real Azure resource များသည် charge ဖြစ်နိုင်သည်။ Service၊ region၊ tier၊ usage နှင့် egress ကိုစစ်ပါ။",
     "Create a cost checklist that includes budget, expiry tag, alert, and cleanup verification.",
     ("Azure cost ကို ဘယ်လိုလျှော့ချနိုင်သနည်း?", ["Estimate usage, set budgets, tag resources, and clean up", "Assume every service is permanently free", "Ignore egress and running time"], "Estimate usage, set budgets, tag resources, and clean up", "Cost control requires estimates and lifecycle discipline.")),
    ("First Resource Group Workflow", "a safe, reproducible Azure foundation",
     "az group create --name academy-learn-rg --location eastus --tags purpose=education expires=soon\\naz group show --name academy-learn-rg",
     "azure-cli", "A first resource group workflow combines context checks, naming, tags, least privilege, cost awareness, verification, and cleanup. The Academy simulator demonstrates the same reasoning without contacting Azure.",
     "First resource group workflow တွင် context၊ naming၊ tags၊ permission၊ cost နှင့် cleanup ကို အမြဲစစ်ရသည်။ Academy simulator သည် Azure ကိုမချိတ်ဘဲ ထို reasoning ကိုပြသည်။",
     "Complete the simulator walkthrough, document expected output, and write a cleanup confirmation.",
     ("Learning simulator ၏ အဓိကရည်ရွယ်ချက်က ဘာလဲ?", ["Practice cloud decisions without creating real billable resources", "Provision a live subscription automatically", "Collect Azure credentials"], "Practice cloud decisions without creating real billable resources", "The simulator is educational and local-only.")),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(position: int, item: tuple) -> str:
    title, topic, commands, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "No cloud experience is required; basic command-line familiarity helps." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: use the Azure Portal simulator and complete the resource-group lab."
    return f"""Introduction
{title} introduces {topic} using safe Azure administration practices.

Learning objectives
- Explain {topic} and its place in an Azure architecture.
- Inspect scope, identity, cost, and lifecycle boundaries.
- Practice read-only or disposable workflows without exposing credentials.

Prerequisites
{prerequisite}

Azure architecture explanation
tenant -> subscription -> resource group -> resource -> identity/policy/network dependencies

Detailed theory
{theory}

Portal walkthrough
Open the educational simulator, confirm the simulated subscription, inspect the resource group or service blade, review relationships, and reset the local state. The simulator is not a Microsoft Portal clone and never connects to a real Azure account.

Azure CLI examples
{commands}

Expected results
Expected output depends on the simulator state and Azure CLI version. Verify subscription context, resource names, region, tags, permissions, and cost warnings instead of copying an unverified result.

Configuration explanation
Treat every resource as a scoped change. Record owner, environment, region, tags, permissions, dependencies, expiry, and cleanup steps before creating it.

Common errors
- Working in the wrong subscription or tenant.
- Missing provider registration, quota, or RBAC permissions.
- Selecting an unavailable region or assuming a service is free.
- Leaving disposable resources running.

Troubleshooting
Check account context, activity history, policy, region support, quota, role assignment, deployment output, and billing scope. If a subscription is unavailable, use the local simulator and do not invent activation success.

Best practices
- Prefer least privilege, tags, budgets, managed identities, and infrastructure as code.
- Keep secrets in Key Vault or an approved secret manager, never in source or shell history.
- Use disposable resource groups and verify cleanup.

Security and cost considerations
Azure course content is free. Real Azure infrastructure can incur charges. Before any real write operation, confirm permission, pricing, budget, region, expiry, and cleanup. Never expose tokens, passwords, or subscription secrets.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Build a documented disposable Azure foundation: hierarchy diagram, naming/tags, cost checklist, least-privilege plan, simulator walkthrough, and cleanup record. Do not create real resources for this lesson.

Summary
You can now reason about {topic} with explicit identity, scope, security, and cost boundaries.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
The Academy uses local simulations and predefined examples. It does not collect Azure credentials, execute arbitrary shell/Azure CLI commands, or create real Azure resources.
"""

def seed_microsoft_azure_course(db, course):
    course.title = "Microsoft Azure — From Zero to Professional Cloud & DevOps Engineer"
    course.short_description = "A free, practical path from cloud fundamentals to secure Azure administration, DevOps, and architecture."
    course.description = "Learn Azure foundations, portal and CLI workflows, networking, identity, storage, compute, containers, databases, security, monitoring, IaC, DevOps, governance, and cost-aware cloud architecture."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 45
    course.outcomes = "Explain cloud models, Azure hierarchy, shared responsibility, and cost boundaries|Use safe Portal and Azure CLI workflows for disposable resources|Design secure identity, networking, compute, storage, monitoring, and deployment foundations|Prepare for Bicep, Terraform, Azure DevOps, GitHub Actions, and production architecture"
    course.requirements = "Basic command-line familiarity is helpful; an Azure subscription is not required because lessons provide local simulations."
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
        values = {"title": f"{title} example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe Azure example. Review scope, permissions, cost, and cleanup; the Academy does not execute it.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review Azure scope, identity, security, cost, and cleanup before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: the Academy creates real Azure resources during these lessons.", ["True", "False"], "False", "The Portal and CLI experiences are local educational simulations."),
            ("Which practice is safest for a disposable cloud lab?", ["Use least privilege, budgets, expiry tags, and cleanup", "Paste tokens into source code", "Assume every resource is free"], "Use least privilege, budgets, expiry tags, and cleanup", "Security and cost controls belong in the lab design.")
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

