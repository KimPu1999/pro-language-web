"""Complete the canonical DevOps Engineer roadmap from published records.

The repair is deliberately additive and idempotent. It keeps the existing
career_roadmaps row, stage IDs, step IDs, course IDs, lesson IDs, enrolments,
and learner progress. It expands the roadmap with reviewed metadata and twenty
module steps that point at real published lessons and project briefs.

Run from ``backend`` after the normal migrations and content seed:

    PYTHONPATH=. .venv/bin/python scripts/complete_devops_learning_path.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal
from app.models import (
    CareerRoadmap,
    Course,
    CourseModule,
    Lesson,
    ProjectTemplate,
    RoadmapRevision,
    RoadmapStage,
    RoadmapStep,
    RoadmapStepResource,
    User,
)


STAGES = [
    {
        "title": "Stage 1 · Beginner — Foundations and Automation",
        "title_mm": "အဆင့် ၁ · Beginner — အခြေခံများနှင့် Automation",
        "description_en": "Learn the operating-system, networking, collaboration, and automation foundations used by every DevOps team.",
        "description_mm": "DevOps အဖွဲ့တိုင်းအသုံးပြုသည့် operating system၊ networking၊ collaboration နှင့် automation အခြေခံများကို လေ့လာပါ။",
        "level": "beginner",
        "objectives": ["Explain the DevOps delivery loop", "Operate a Linux terminal safely", "Troubleshoot a small network", "Collaborate through GitHub"],
        "skills": ["Linux", "Networking", "Git", "GitHub", "Bash"],
    },
    {
        "title": "Stage 2 · Intermediate — Delivery and Containers",
        "title_mm": "အဆင့် ၂ · Intermediate — Delivery နှင့် Containers",
        "description_en": "Turn source code into repeatable delivery workflows with shell automation, tests, deployment strategies, and secure containers.",
        "description_mm": "Source code ကို shell automation၊ tests၊ deployment strategies နှင့် secure containers အသုံးပြု၍ ထပ်ခါတလဲလဲ deploy လုပ်နိုင်သော workflow အဖြစ် ပြောင်းလဲပါ။",
        "level": "intermediate",
        "objectives": ["Automate repeatable delivery tasks", "Design a tested CI pipeline", "Build and inspect a secure container", "Plan rollback and environment boundaries"],
        "skills": ["Bash automation", "CI/CD", "GitHub Actions", "Docker", "Release management"],
    },
    {
        "title": "Stage 2 · Intermediate — CI/CD Practice",
        "title_mm": "အဆင့် ၂ · Intermediate — CI/CD လက်တွေ့လေ့ကျင့်မှု",
        "description_en": "Practice the pipeline feedback loop with automated tests, artifacts, deployment environments, and an application delivery project.",
        "description_mm": "Automated tests၊ artifacts၊ deployment environments နှင့် application delivery project တို့ဖြင့် pipeline feedback loop ကို လက်တွေ့လေ့ကျင့်ပါ။",
        "level": "intermediate",
        "objectives": ["Connect tests to delivery decisions", "Read failed pipeline evidence", "Use artifacts and approvals safely", "Deliver an existing application without executing untrusted code on the platform"],
        "skills": ["Pipeline testing", "Artifacts", "Approvals", "Rollback", "Application delivery"],
    },
    {
        "title": "Stage 3 · Advanced — Cloud and Infrastructure",
        "title_mm": "အဆင့် ၃ · Advanced — Cloud နှင့် Infrastructure",
        "description_en": "Understand cloud infrastructure, identity, cost boundaries, Terraform workflows, and Kubernetes delivery without requiring paid cloud usage for the core exercises.",
        "description_mm": "Cloud infrastructure၊ identity၊ cost boundaries၊ Terraform workflow နှင့် Kubernetes delivery ကို လေ့လာပါ။ အခြေခံလေ့ကျင့်ခန်းများအတွက် အခကြေးငွေရှိသော cloud account မလိုအပ်ပါ။",
        "level": "advanced",
        "objectives": ["Choose compute, storage, and network boundaries", "Apply least privilege concepts", "Read Terraform delivery workflows", "Explain Kubernetes deployment boundaries"],
        "skills": ["AWS", "Azure", "Terraform", "Kubernetes", "IAM", "Cloud networking"],
    },
    {
        "title": "Stage 3 · Advanced — Security, Observability and Resilience",
        "title_mm": "အဆင့် ၃ · Advanced — Security၊ Observability နှင့် Resilience",
        "description_en": "Make delivery safer and easier to operate through supply-chain checks, observability, performance planning, incident troubleshooting, and recovery design.",
        "description_mm": "Supply-chain checks၊ observability၊ performance planning၊ incident troubleshooting နှင့် recovery design တို့ဖြင့် delivery ကို ပိုမိုလုံခြုံပြီး operation လုပ်ရလွယ်ကူအောင် ပြုလုပ်ပါ။",
        "level": "advanced",
        "objectives": ["Add security checks to a pipeline", "Read metrics and operational signals", "Plan availability and capacity", "Design backup and recovery verification"],
        "skills": ["DevSecOps", "Metrics", "Logs", "Tracing", "Availability", "Disaster recovery"],
    },
    {
        "title": "Stage 4 · Professional — Platform Operations and Capstone",
        "title_mm": "အဆင့် ၄ · Professional — Platform Operations နှင့် Capstone",
        "description_en": "Bring the skills together in production-style architecture, release operations, runbooks, recovery evidence, and a documented portfolio capstone.",
        "description_mm": "Production-style architecture၊ release operations၊ runbooks၊ recovery evidence နှင့် documentation ပါသော portfolio capstone တွင် ကျွမ်းကျင်မှုများကို ပေါင်းစပ်အသုံးချပါ။",
        "level": "professional",
        "objectives": ["Explain operational readiness", "Document incidents and rollback decisions", "Connect infrastructure to application delivery", "Present a verifiable DevOps portfolio project"],
        "skills": ["SRE thinking", "Incident response", "Platform engineering", "Runbooks", "Technical documentation"],
    },
]


STEPS = [
    (0, "DevOps Foundations", "DevOps အခြေခံများ", "Explain the DevOps principles, SDLC feedback loop, CI/CD boundary, and responsibilities of a DevOps engineer.", "DevOps principle၊ SDLC feedback loop၊ CI/CD boundary နှင့် DevOps engineer ၏ တာဝန်များကို ရှင်းပြနိုင်ရန် လေ့လာပါ။", [("course", "ci-cd"), ("lesson", "ci-cd:01-what-is-ci-cd")]),
    (0, "Linux Administration Fundamentals", "Linux Administration အခြေခံများ", "Use a terminal safely, navigate the filesystem, inspect files, and apply the first troubleshooting workflow.", "Terminal ကို လုံခြုံစွာအသုံးပြုခြင်း၊ filesystem လမ်းကြောင်းရှာခြင်း၊ ဖိုင်များစစ်ဆေးခြင်းနှင့် ပထမဆုံး troubleshooting workflow ကို လေ့ကျင့်ပါ။", [("course", "linux"), ("lesson", "linux:01-terminal-shell-and-command-syntax")]),
    (0, "Networking and Troubleshooting", "Networking နှင့် Troubleshooting", "Explain TCP/IP, names, ports, and the evidence needed to investigate a connectivity problem.", "TCP/IP၊ names၊ ports နှင့် connectivity ပြဿနာကို စစ်ဆေးရန်လိုအပ်သော evidence များကို လေ့လာပါ။", [("course", "networking-fundamentals"), ("lesson", "networking-fundamentals:01-first-network-troubleshooting-workflow")]),
    (0, "GitHub Collaboration Workflow", "GitHub Collaboration Workflow", "Use branches, pull requests, checks, and protected-branch boundaries for reviewable changes.", "Review လုပ်နိုင်သော change များအတွက် branches၊ pull requests၊ checks နှင့် protected-branch boundaries များကို အသုံးပြုပါ။", [("course", "github"), ("lesson", "github:01-open-and-understand-a-pull-request")]),
    (1, "Bash Automation and Safe Scripting", "Bash Automation နှင့် Safe Scripting", "Write repeatable shell automation with clear inputs, exit codes, logs, and safe cleanup behavior.", "Input၊ exit code၊ logs နှင့် safe cleanup behavior များကို ရှင်းလင်းစွာသတ်မှတ်ပြီး ထပ်ခါတလဲလဲအသုံးပြုနိုင်သော shell automation ရေးပါ။", [("lesson", "ci-cd:05-shell-automation")]),
    (1, "Deployment Strategies and Rollback", "Deployment Strategies နှင့် Rollback", "Compare rolling, staged, and rollback strategies and choose a safe release boundary for an application.", "Rolling၊ staged နှင့် rollback strategies များကို နှိုင်းယှဉ်ပြီး application အတွက် လုံခြုံသော release boundary ကို ရွေးချယ်ပါ။", [("lesson", "ci-cd:20-deployment-strategies")]),
    (1, "Docker Images and Secure Containers", "Docker Images နှင့် Secure Containers", "Build, run, inspect, and clean up a small container while keeping the image boundary and secrets safe.", "Image boundary နှင့် secrets များကို လုံခြုံစွာထားပြီး container အသေးတစ်ခုကို build၊ run၊ inspect နှင့် clean up လုပ်ပါ။", [("course", "docker"), ("lesson", "docker:01-write-a-secure-first-dockerfile")]),
    (2, "CI Testing and Application Delivery", "CI Testing နှင့် Application Delivery", "Connect automated tests and artifacts to a delivery decision, then document what must be verified before deployment.", "Automated tests နှင့် artifacts များကို delivery decision နှင့် ချိတ်ဆက်ပြီး deploy မလုပ်မီ verify လုပ်ရမည့်အချက်များကို မှတ်တမ်းတင်ပါ။", [("lesson", "ci-cd:09-testing-in-ci"), ("project", "nodejs-authentication-api")]),
    (2, "Cloud Compute and Network Boundaries", "Cloud Compute နှင့် Network Boundaries", "Explain compute, storage, networking, identity, and cost boundaries using a cloud architecture that can be practiced locally.", "Local တွင် လေ့ကျင့်နိုင်သော cloud architecture ဖြင့် compute၊ storage၊ networking၊ identity နှင့် cost boundaries များကို ရှင်းပြပါ။", [("course", "aws"), ("lesson", "aws:08-ec2-compute-foundations")]),
    (2, "Terraform and Multi-Cloud Foundations", "Terraform နှင့် Multi-Cloud Foundations", "Read an infrastructure-as-code workflow, identify state and drift risks, and compare AWS and Azure resource boundaries without provisioning paid infrastructure.", "Infrastructure-as-code workflow ကို ဖတ်ရှု၍ state နှင့် drift အန္တရာယ်များကို သိရှိပါ။ အခကြေးငွေရှိသော infrastructure မတည်ဆောက်ဘဲ AWS နှင့် Azure resource boundaries ကို နှိုင်းယှဉ်ပါ။", [("course", "microsoft-azure"), ("lesson", "aws:27-terraform-for-aws"), ("lesson", "microsoft-azure:01-azure-cli-and-cloud-shell")]),
    (3, "Kubernetes Architecture and Workloads", "Kubernetes Architecture နှင့် Workloads", "Explain clusters, pods, deployments, services, configuration, probes, and resource boundaries before using a local cluster.", "Local cluster မသုံးမီ clusters၊ pods၊ deployments၊ services၊ configuration၊ probes နှင့် resource boundaries များကို ရှင်းပြပါ။", [("lesson", "ci-cd:23-kubernetes-fundamentals")]),
    (3, "Helm, GitOps and Progressive Delivery", "Helm၊ GitOps နှင့် Progressive Delivery", "Compare Helm and GitOps workflows with rolling, blue-green, canary, and rollback decisions.", "Helm နှင့် GitOps workflows များကို rolling၊ blue-green၊ canary နှင့် rollback decisions များနှင့် နှိုင်းယှဉ်ပါ။", [("lesson", "ci-cd:25-helm-and-gitops")]),
    (4, "DevSecOps and Supply-Chain Checks", "DevSecOps နှင့် Supply-Chain Checks", "Add dependency, image, secret, and supply-chain checks to the delivery process with least-privilege controls.", "Least-privilege controls များဖြင့် dependency၊ image၊ secret နှင့် supply-chain checks များကို delivery process ထဲ ထည့်သွင်းပါ။", [("lesson", "ci-cd:29-devsecops-scanning")]),
    (4, "Metrics, Logs and Operational Signals", "Metrics၊ Logs နှင့် Operational Signals", "Use metrics and logs to describe service health, alert conditions, and the evidence required for a useful dashboard.", "Service health၊ alert conditions နှင့် အသုံးဝင်သော dashboard အတွက်လိုအပ်သည့် evidence များကို metrics နှင့် logs အသုံးပြု၍ ဖော်ပြပါ။", [("lesson", "aws:30-cloudwatch-observability")]),
    (4, "Scalability, Availability and Capacity", "Scalability၊ Availability နှင့် Capacity", "Plan load balancing, horizontal scaling, resource limits, capacity signals, and performance trade-offs.", "Load balancing၊ horizontal scaling၊ resource limits၊ capacity signals နှင့် performance trade-offs များကို စီမံကိန်းချပါ။", [("lesson", "aws:36-availability-and-performance")]),
    (4, "Incident Triage and Failed Delivery", "Incident Triage နှင့် Failed Delivery", "Investigate a failed pipeline or simulated outage using timestamps, logs, hypotheses, escalation, and a safe rollback decision.", "Timestamp၊ logs၊ hypotheses၊ escalation နှင့် safe rollback decision များအသုံးပြု၍ failed pipeline သို့မဟုတ် simulated outage ကို စစ်ဆေးပါ။", [("lesson", "ci-cd:32-failed-pipeline-troubleshooting")]),
    (4, "Backup, Recovery and Failure Drills", "Backup၊ Recovery နှင့် Failure Drills", "Define RPO and RTO, protect backup access, and verify recovery with a documented restore test rather than an untested promise.", "RPO နှင့် RTO သတ်မှတ်ခြင်း၊ backup access ကာကွယ်ခြင်းနှင့် မစမ်းသပ်ရသေးသော ကတိအစား restore test ကို မှတ်တမ်းတင်၍ recovery verify လုပ်ပါ။", [("lesson", "aws:34-backup-and-disaster-recovery")]),
    (5, "Platform Architecture and Operational Readiness", "Platform Architecture နှင့် Operational Readiness", "Design a platform boundary that balances self-service, governance, access control, reliability, and cost awareness.", "Self-service၊ governance၊ access control၊ reliability နှင့် cost awareness ကို ချိန်ညှိထားသော platform boundary တစ်ခုကို ဒီဇိုင်းဆွဲပါ။", [("lesson", "aws:35-solution-architecture")]),
    (5, "Production CI/CD Capstone", "Production CI/CD Capstone", "Combine infrastructure, containers, CI/CD, security checks, monitoring, rollback, and documentation into a reviewable capstone.", "Infrastructure၊ containers၊ CI/CD၊ security checks၊ monitoring၊ rollback နှင့် documentation များကို review လုပ်နိုင်သော capstone တစ်ခုအဖြစ် ပေါင်းစပ်ပါ။", [("lesson", "ci-cd:40-ci-cd-capstone")]),
    (5, "DevOps Portfolio and Real-World Delivery", "DevOps Portfolio နှင့် Real-World Delivery", "Present a verifiable portfolio project with architecture, runbooks, recovery evidence, incident notes, and a clear list of limitations.", "Architecture၊ runbooks၊ recovery evidence၊ incident notes နှင့် limitations များကို ရှင်းလင်းစွာဖော်ပြထားသော verify လုပ်နိုင်သည့် portfolio project ကို တင်ပြပါ။", [("lesson", "aws:39-real-world-aws-projects"), ("project", "python-fastapi-rest-api")]),
]


def snapshot(path: CareerRoadmap, stages: list[RoadmapStage], steps: list[RoadmapStep]) -> str:
    return json.dumps({
        "title": path.title,
        "title_mm": path.title_mm,
        "description_en": path.description_en,
        "description_mm": path.description_mm,
        "prerequisites_en": path.prerequisites_en,
        "prerequisites_mm": path.prerequisites_mm,
        "outcomes_en": path.outcomes_en,
        "outcomes_mm": path.outcomes_mm,
        "estimated_hours": path.estimated_hours,
        "goals_json": path.goals_json,
        "skills_json": path.skills_json,
        "completion_rules_json": path.completion_rules_json,
        "stages": [{"id": str(stage.id), "title": stage.title, "position": stage.position} for stage in stages],
        "steps": [{"id": str(step.id), "stage_id": str(step.stage_id), "title": step.title, "position": step.position} for step in steps],
    }, ensure_ascii=False)


def run() -> None:
    with SessionLocal.begin() as db:
        path = db.scalar(select(CareerRoadmap).where(CareerRoadmap.slug == "devops-engineer"))
        if path is None:
            raise RuntimeError("Canonical devops-engineer roadmap was not found")

        stages = db.scalars(select(RoadmapStage).where(RoadmapStage.roadmap_id == path.id).order_by(RoadmapStage.position)).all()
        steps = db.scalars(select(RoadmapStep).join(RoadmapStage).where(RoadmapStage.roadmap_id == path.id).order_by(RoadmapStage.position, RoadmapStep.position)).all()
        needs_revision = path.title_mm != "DevOps အင်ဂျင်နီယာ" or path.estimated_hours != 360 or len(stages) != len(STAGES) or len(steps) != len(STEPS) or not path.description_en.startswith("A practical, free roadmap from first")
        if needs_revision:
            actor_id = path.created_by or db.scalar(select(User.id).where(User.role.in_(["admin", "super_admin", "instructor"])).order_by(User.created_at).limit(1))
            if actor_id is None:
                raise RuntimeError("A revision actor is required before changing the roadmap")
            db.add(RoadmapRevision(roadmap_id=path.id, changed_by=actor_id, snapshot_json=snapshot(path, stages, steps)))

        path.title = "DevOps Engineer"
        path.title_mm = "DevOps အင်ဂျင်နီယာ"
        path.description_en = "A practical, free roadmap from first terminal commands to production-style DevOps engineering. Learn through published courses, real lesson evidence, safe local labs, and a documented portfolio project."
        path.description_mm = "ပထမဆုံး terminal command များမှ production-style DevOps engineering အထိ အခမဲ့လေ့လာနိုင်သော လက်တွေ့ roadmap ဖြစ်ပါသည်။ Published courses၊ အမှန်တကယ် lesson များ၊ လုံခြုံသော local lab များနှင့် မှတ်တမ်းတင်ထားသော portfolio project တစ်ခုမှတစ်ဆင့် လေ့လာပါ။"
        path.prerequisites_en = "Required: No prior DevOps experience is required. Recommended preparation: basic computer literacy, familiarity with files and terminal navigation, basic networking awareness, and interest in scripting and software delivery. The Beginner stage teaches the missing foundations."
        path.prerequisites_mm = "လိုအပ်ချက်: DevOps အတွေ့အကြုံ ကြိုတင်မလိုအပ်ပါ။ အကြံပြုထားသော ပြင်ဆင်မှု: computer အသုံးပြုမှုအခြေခံ၊ ဖိုင်များနှင့် terminal လမ်းကြောင်းရှာဖွေမှု၊ networking အခြေခံအသိနှင့် scripting၊ software delivery ကို စိတ်ဝင်စားမှု။ လိုအပ်သော foundation များကို Beginner အဆင့်တွင် သင်ကြားပေးပါမည်။"
        path.outcomes_en = "By the end, learners can administer Linux, troubleshoot networks, collaborate with Git, automate with Bash and Python, design CI/CD, build secure containers, explain cloud and Terraform boundaries, reason about Kubernetes and GitOps, apply DevSecOps checks, read metrics and logs, respond to incidents, verify backup recovery, and present a production-style capstone."
        path.outcomes_mm = "သင်ယူပြီးဆုံးပါက Linux administration၊ network troubleshooting၊ Git collaboration၊ Bash နှင့် Python automation၊ CI/CD design၊ secure container တည်ဆောက်မှု၊ cloud နှင့် Terraform boundaries၊ Kubernetes နှင့် GitOps၊ DevSecOps checks၊ metrics နှင့် logs ဖတ်ရှုမှု၊ incident response၊ backup recovery verification နှင့် production-style capstone တင်ပြမှုတို့ကို လက်တွေ့ပြနိုင်မည်။"
        path.estimated_hours = 360
        path.goals_json = json.dumps([
            "Target audience: learners moving from software foundations into DevOps, cloud operations, release engineering, or platform work.",
            "Career objective: build evidence of practical DevOps ability through course completion, safe labs, and a documented portfolio project.",
            "Equipment: a modern browser, Git, a local terminal or safe shell environment, Docker Desktop or an equivalent local runtime when available, and at least 8 GB RAM for optional local Kubernetes practice.",
            "Free-learning policy: core progress does not require paid AWS or Azure resources; cloud lessons can be read and simulated locally.",
            "Completion criteria: complete the required roadmap modules, verify linked lessons or courses, submit the capstone evidence, and document limitations and recovery decisions.",
        ], ensure_ascii=False)
        path.skills_json = json.dumps(["Linux", "Networking", "Git", "GitHub", "Bash", "Python automation", "CI/CD", "Docker", "AWS", "Azure", "Terraform", "Kubernetes", "GitOps", "DevSecOps", "Observability", "SRE", "Incident response", "Backup and recovery", "Platform engineering"], ensure_ascii=False)
        path.completion_rules_json = json.dumps({"required_stages": 4, "roadmap_levels": ["beginner", "intermediate", "advanced", "professional"], "required_modules": 20, "required_evidence": ["published lesson or course completion", "safe lab verification", "capstone documentation", "recovery and incident notes"], "paid_cloud_required": False}, ensure_ascii=False)

        while len(stages) < len(STAGES):
            position = len(stages)
            stage = RoadmapStage(roadmap_id=path.id, title=f"Stage {position + 1}", description_en="Editorial stage pending configuration.", level="advanced", position=position)
            db.add(stage)
            db.flush()
            stages.append(stage)

        # Avoid unique-position conflicts while the existing records are reused.
        for index, stage in enumerate(stages):
            stage.position = -(index + 1)
        db.flush()
        for index, config in enumerate(STAGES):
            stage = stages[index]
            stage.position = index
            stage.title = config["title"]
            stage.title_mm = config["title_mm"]
            stage.description_en = config["description_en"]
            stage.description_mm = config["description_mm"]
            stage.level = config["level"]
            stage.objectives_json = json.dumps(config["objectives"], ensure_ascii=False)
            stage.skills_json = json.dumps(config["skills"], ensure_ascii=False)
            stage.completion_rules_json = json.dumps({"required_modules": sum(1 for step in STEPS if step[0] == index)}, ensure_ascii=False)

        course_by_slug = {row.slug: row for row in db.scalars(select(Course).where(Course.published.is_(True))).all()}
        lesson_by_key = {}
        lesson_query = select(Course.slug, Lesson.slug, Lesson).join(CourseModule, Lesson.module_id == CourseModule.id).join(Course, CourseModule.course_id == Course.id).where(Lesson.published.is_(True))
        for course_slug, lesson_slug, lesson in db.execute(lesson_query).all():
            lesson_by_key[f"{course_slug}:{lesson_slug}"] = lesson
        project_by_slug = {row.slug: row for row in db.scalars(select(ProjectTemplate).where(ProjectTemplate.published.is_(True))).all()}

        while len(steps) < len(STEPS):
            steps.append(RoadmapStep(stage_id=stages[0].id, title="Pending module", instructions_en="Pending module", position=len(steps), required=False))
            db.add(steps[-1])
            db.flush()

        for index, step in enumerate(steps):
            step.position = -(index + 1)
        db.flush()

        for index, (stage_index, title, title_mm, instructions, instructions_mm, resources) in enumerate(STEPS):
            step = steps[index]
            step.stage_id = stages[stage_index].id
            step.position = index - sum(1 for item in STEPS[:index] if item[0] != stage_index)
            step.title = title
            step.title_mm = title_mm
            step.instructions_en = instructions
            step.instructions_mm = instructions_mm
            step.required = True
            db.query(RoadmapStepResource).filter(RoadmapStepResource.step_id == step.id).delete(synchronize_session=False)
            for resource_type, resource_key in resources:
                if resource_type == "course":
                    target = course_by_slug.get(resource_key)
                elif resource_type == "lesson":
                    target = lesson_by_key.get(resource_key)
                else:
                    target = project_by_slug.get(resource_key)
                if target is None:
                    raise RuntimeError(f"Missing published {resource_type}: {resource_key}")
                db.add(RoadmapStepResource(step_id=step.id, resource_type=resource_type, resource_id=target.id))

        path.status = path.status or "published"
        path.published = bool(path.published)
        print(f"updated_path={path.id} stages={len(STAGES)} modules={len(STEPS)}")
        print("linked_course_slugs=" + ",".join(sorted({key for _, _, _, _, _, resources in STEPS for resource_type, key in resources if resource_type == "course"})))
        print("linked_project_slugs=" + ",".join(sorted({key for _, _, _, _, _, resources in STEPS for resource_type, key in resources if resource_type == "project"})))


if __name__ == "__main__":
    run()
