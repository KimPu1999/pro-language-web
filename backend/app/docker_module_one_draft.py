"""Draft content for the Docker Module 01 vertical slice.

Phase 02 selected Docker as the highest-priority incomplete course. This file
adapts the Phase 03 lesson-development contract to its existing eight-lesson
Module 01 without changing canonical lesson records or publishing content.
"""
from __future__ import annotations

import json
import re
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from .docker_course_content import MODULE_ONE
from .models import (
    CodingExercise,
    Course,
    CourseModule,
    Lesson,
    LessonContentDraft,
    ModuleQuizDraft,
    ProjectCategory,
    ProjectCourseLink,
    ProjectMilestone,
    ProjectRequirement,
    ProjectRubricCriterion,
    ProjectTask,
    ProjectTemplate,
    ProjectVersion,
)

DOCKER_COURSE_ID = UUID("73b0e7ab-0035-4012-92a6-7fbfe6fdfa1f")
MODULE_TITLE = "Introduction to Docker"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _lesson_content(index: int, item: tuple) -> tuple[str, str]:
    title, topic, commands, theory, legacy_mm, exercise, mm_prompt, options, answer, explanation, *notes = item
    previous = "No Docker experience is required; basic terminal navigation is useful." if index == 1 else f"Review the previous Module 01 lesson before starting lesson {index}."
    next_lesson = "Continue to the next Docker foundation lesson." if index < len(MODULE_ONE) else "Continue with the Module 01 project and assessment."
    note = notes[0] if notes else "Use a disposable local Docker context."
    en = f"""# {title}

## Level and duration
Beginner · 35–50 minutes

## Introduction
This lesson explains **{topic}** using a local-first Docker workflow. The goal is to understand the resource boundary before running a command, then collect evidence and clean up safely.

## Learning objectives
- Explain the role of {topic} in a container workflow.
- Predict what each command changes before running it.
- Verify the result with inspection, logs, or an explicit cleanup check.
- Apply least privilege and supply-chain hygiene in a disposable lab.

## Prerequisites
{previous}

## Detailed theory
{theory}

## Core concepts
Docker CLI → Docker Engine API → daemon → images, containers, networks, and volumes.
Registries provide image artifacts; they do not automatically prove that an artifact is trusted. A tag is a human-friendly reference, while a digest identifies content. A container is a process boundary, not a replacement for application security, access control, or backups.

## Syntax / API
```bash
{commands}
```
Read commands from left to right. `--name` gives a stable inspection target, `--rm` removes a disposable container when it exits, and `docker inspect` is the evidence-oriented API for configuration and state. Exact flags can vary by the installed Docker release; check `docker COMMAND --help` locally.

## Code example
The following examples progress from read-only inspection to a bounded local operation and then evidence collection. Do not run them against a shared or production context.
### Example 1 — inspect before acting
```bash
docker version
docker context show
docker ps --all
```
These commands are read-only. Record the client/engine availability, active context, and existing resources before changing anything.

### Example 2 — bounded disposable run
```bash
docker run --rm --name module01-demo alpine:3.20 echo "Module 01 check"
```
The container runs one short process and is removed after it exits. Use an approved, disposable local context and verify the image source before pulling it.

### Example 3 — evidence and cleanup
```bash
docker ps --all
docker inspect module01-demo
```
The inspect command is useful when the named resource still exists. If a command used `--rm`, record its output before the container exits.

## Expected output
Output depends on Docker Engine, operating system, image availability, and the active context. Expect a version/context/resource status or a one-line command result—not a guaranteed patch-version string. Treat a missing daemon, denied socket, or pull failure as diagnostic evidence and do not work around it by exposing a production socket.

## Step-by-step explanation
1. Confirm the selected local context and engine.
2. Read the command and identify image, resource name, ports, mounts, and cleanup behavior.
3. Run the smallest safe example.
4. Inspect logs or state and compare observed behavior with the prediction.
5. Remove disposable resources and keep only evidence needed for the exercise.

## Common mistakes
- Treating a container as a VM or assuming it has a separate kernel.
- Running an unreviewed tag as if it were a verified release.
- Using broad `prune` commands in a shared context.
- Copying secrets into a build context or image layer.
- Diagnosing the client binary while the daemon/context is the real problem.

## Best practices
- Use explicit names, bounded commands, and a disposable context.
- Prefer maintained base images and record source, tag, and digest where reproducibility matters.
- Run application processes as a non-root user where possible.
- Log to stdout/stderr and verify health independently of restart policy.
- Document the actual observed version instead of hardcoding a sample output.

## Practical exercises
1. {exercise}
2. Draw the CLI → daemon → resource flow for this lesson and mark which steps mutate local state.
3. Write a cleanup checklist that another learner can follow without deleting unrelated resources.

## Independent practice
Repeat the lab with a different small, reviewed image. Compare the predicted state with `docker ps --all` and `docker inspect`, then explain one limitation of your test.

## Homework
Create a one-page runbook for this topic. Include the command, pre-flight checks, expected behavior, evidence to capture, cleanup action, and one security warning. Do not include credentials, private image URLs, or production daemon addresses.

## Knowledge quiz
**Question:** {mm_prompt if False else title} — which evidence best demonstrates that the lesson objective was met?
**Answer:** A recorded prediction, a bounded local run, and an inspection/cleanup result.
**Explanation:** Evidence-based verification is safer than assuming a command succeeded because it returned quickly.

## Mini project
The Module 01 project, **My First Docker Service**, applies this lesson to a small containerized service. This lesson contributes the {topic} design decision and its verification note.

## Lesson summary
{title} is about {topic}. Understand the boundary, run a small example, verify actual state, and clean up deliberately.

## Further learning
Read the official Docker Engine, image-building, and security documentation for the installed release. Compare the documentation’s version-specific behavior with your local evidence.

## Next lesson
{next_lesson}
"""
    mm = f"""# {title} — မြန်မာဘာသာ

## အဆင့်နှင့် အချိန်
Beginner · ၃၅–၅၀ မိနစ်

## မိတ်ဆက်
ဒီသင်ခန်းစာမှာ **{topic}** ကို local-first Docker လေ့လာမှုနဲ့ ရှင်းပြထားပါတယ်။ Command မ run မီ ဘာ resource ပြောင်းလဲမလဲ ခန့်မှန်းပြီး၊ ရလဒ်ကို စစ်ဆေးကာ သန့်ရှင်းရေးလုပ်ခြင်းက အဓိကပါ။

## သင်ယူရမည့် ရည်မှန်းချက်များ
- {topic} ရဲ့ အခန်းကဏ္ဍကို ရှင်းပြနိုင်ရန်။
- Command တစ်ခုချင်းစီက ဘာလုပ်မလဲ ကြိုတင်ခန့်မှန်းနိုင်ရန်။
- Log၊ inspect သို့မဟုတ် cleanup စစ်ဆေးချက်ဖြင့် ရလဒ်ကို အတည်ပြုနိုင်ရန်။
- Least privilege နှင့် image supply-chain လုံခြုံရေးကို အသုံးချနိုင်ရန်။

## ကြိုတင်လိုအပ်ချက်များ
{legacy_mm} ဒီအကြောင်းအရာကို မစခင် local Docker context ကို စစ်ဆေးပါ။

## အသေးစိတ်သီအိုရီ
{theory} Docker က application ကို package လုပ်ပေးနိုင်သော်လည်း မလုံခြုံသော code ကို အလိုအလျောက် မလုံခြုံစေပါ။ Host၊ daemon၊ image နှင့် container တို့ရဲ့ နယ်နိမိတ်ကို သီးခြားစဉ်းစားရမယ်။

## အဓိကအယူအဆများ
Docker CLI က Engine API မှတစ်ဆင့် daemon ကို request ပို့ပြီး image၊ container၊ network နှင့် volume များကို စီမံပါတယ်။ Registry က image သိမ်းပေးသော်လည်း image ယုံကြည်စိတ်ချရကြောင်း အလိုအလျောက် မအတည်ပြုပါ။ Tag က ပြောင်းလဲနိုင်ပြီး digest က content ကို တိတိကျကျ ခွဲခြားပေးပါတယ်။

## Syntax / API
```bash
{commands}
```
`--name` က resource ကို ရှာရလွယ်စေပြီး `--rm` က disposable container ကို ပြီးဆုံးလျှင် ဖျက်ပေးပါတယ်။ `docker inspect` ကို configuration နှင့် state အထောက်အထားအတွက် သုံးပါ။ ကိုယ့်စက်မှာ `docker COMMAND --help` ဖြင့် version-specific option ကို စစ်ပါ။

## Code examples
### ဥပမာ ၁ — မလုပ်မီ စစ်ဆေးခြင်း
```bash
docker version
docker context show
docker ps --all
```
ဒီ command များက read-only ဖြစ်ပါတယ်။ Engine၊ active context နှင့် ရှိပြီးသား resource များကို မှတ်တမ်းတင်ပါ။

### ဥပမာ ၂ — အကန့်အသတ်ရှိသော local run
```bash
docker run --rm --name module01-demo alpine:3.20 echo "Module 01 check"
```
Process ပြီးသွားရင် container ကို ဖျက်ပေးတဲ့ disposable lab ဖြစ်ပါတယ်။ Image source ကို စစ်ပြီး local context မှာသာ run ပါ။

### ဥပမာ ၃ — အထောက်အထားနှင့် cleanup
```bash
docker ps --all
docker inspect module01-demo
```
`--rm` သုံးထားလျှင် container ပျောက်မသွားမီ လိုအပ်သော output ကို မှတ်သားပါ။

## မျှော်မှန်းရလဒ်
Output သည် Docker Engine၊ OS၊ image ရရှိမှုနှင့် active context ပေါ်မူတည်ပါတယ်။ Sample patch version တစ်ခုတည်းကို မယုံပါနှင့်။ Daemon မရခြင်း၊ permission denied ဖြစ်ခြင်း သို့မဟုတ် pull မအောင်မြင်ခြင်းကို diagnostic evidence အဖြစ်ယူပြီး production socket ကို မဖွင့်ပါနှင့်။

## အဆင့်လိုက်ရှင်းလင်းချက်
၁။ Local context နှင့် engine ကို စစ်ပါ။ ၂။ Image၊ name၊ port၊ mount နှင့် cleanup ကို ဖော်ထုတ်ပါ။ ၃။ သေးငယ်သော lab ကို run ပါ။ ၄။ Log/state ကို inspect လုပ်ပါ။ ၅။ Disposable resource ကို cleanup လုပ်ပါ။

## အများဆုံးမှားတတ်သည့်အချက်များ
- Container ကို VM လို့ ယူဆခြင်း။
- Mutable tag ကို verified release လို့ ယူဆခြင်း။
- Shared context မှာ အလွန်ကျယ်သော `prune` သုံးခြင်း။
- Secret ကို build context သို့ image layer ထဲ ထည့်ခြင်း။
- Client ရှိပေမယ့် daemon/context ပြဿနာကို မစစ်ခြင်း။

## အကောင်းဆုံးလုပ်ထုံးလုပ်နည်းများ
Explicit name၊ bounded command နှင့် disposable context သုံးပါ။ Maintained base image သုံးပြီး source၊ tag၊ digest ကို မှတ်တမ်းတင်ပါ။ Non-root user၊ stdout/stderr logging နှင့် သီးခြား health verification ကို အသုံးပြုပါ။

## လက်တွေ့လေ့ကျင့်ခန်းများ
၁။ {exercise} ၂။ CLI → daemon → resource flow ကို ပုံဆွဲပြီး state ပြောင်းတဲ့နေရာများကို အမှတ်အသားပြုပါ။ ၃။ မသက်ဆိုင်သော resource မဖျက်ဘဲ cleanup လုပ်နိုင်သော checklist ရေးပါ။

## ကိုယ်တိုင်လေ့ကျင့်ရန်
Reviewed small image တစ်ခုနဲ့ lab ကို ပြန်လုပ်ပါ။ `docker ps --all` နှင့် `docker inspect` output ကို ခန့်မှန်းချက်နဲ့ နှိုင်းယှဉ်ပြီး test limitation တစ်ခု ရေးပါ။

## အိမ်စာ
ဒီအကြောင်းအရာအတွက် runbook တစ်မျက်နှာရေးပါ။ Command၊ pre-flight check၊ expected behavior၊ evidence၊ cleanup နှင့် security warning ထည့်ပါ။ Credential သို့မဟုတ် production address မထည့်ပါနှင့်။

## Knowledge quiz
**မေးခွန်း:** ဒီသင်ခန်းစာကို နားလည်ကြောင်း ဘယ်အထောက်အထားက အကောင်းဆုံးပြသသလဲ။
**အဖြေ:** ခန့်မှန်းချက်၊ bounded local run နှင့် inspect/cleanup ရလဒ်ကို မှတ်တမ်းတင်ထားခြင်း။
**ရှင်းလင်းချက်:** Command မြန်မြန်ပြီးသွားတာကို အောင်မြင်တယ်လို့ ယူဆခြင်းထက် evidence ဖြင့် စစ်ဆေးခြင်းက ပိုလုံခြုံပါတယ်။

## Mini project
**My First Docker Service** project မှာ ဒီသင်ခန်းစာရဲ့ {topic} design ဆုံးဖြတ်ချက်နှင့် verification note ကို အသုံးချပါမယ်။

## သင်ခန်းစာအကျဉ်းချုပ်
{title} ရဲ့ အဓိကက {topic} ကို နားလည်ခြင်း၊ သေးငယ်သော example run ခြင်း၊ state စစ်ခြင်းနှင့် cleanup ကို ရည်ရွယ်ချက်ရှိရှိလုပ်ခြင်း ဖြစ်ပါတယ်။

## ဆက်လက်ဖတ်ရှုရန်
ကိုယ့် Docker release အတွက် official Engine၊ image-building နှင့် security documentation ကို ဖတ်ပြီး local evidence နဲ့ version-specific behavior ကို နှိုင်းယှဉ်ပါ။

## နောက်သင်ခန်းစာ
{next_lesson}
"""
    return en, mm


def _exercise_values(index: int, title: str, topic: str, mm_title: str) -> dict:
    return {
        "title": f"{title} — verified lab",
        "slug": f"docker-module-01-{index:02d}-{_slug(title)}-lab",
        "description_en": f"In a disposable local Docker context, practice {topic}. Write a prediction before the command, capture the observed state or output, explain one safety boundary, and clean up only resources created by the lab. Expected behavior: the evidence supports or corrects the prediction. Hint: start with docker version, docker context show, and docker ps --all. Evaluation: accurate explanation, reproducible steps, observed evidence, and safe cleanup.",
        "description_mm": f"Disposable local Docker context ထဲတွင် {mm_title} ကို လေ့ကျင့်ပါ။ Command မ run မီ ခန့်မှန်းချက်ရေးပြီး output/state၊ safety boundary တစ်ခုနှင့် cleanup ကို မှတ်တမ်းတင်ပါ။ အကဲဖြတ်ရာတွင် အကြောင်းပြချက်မှန်ကန်မှု၊ ပြန်လုပ်နိုင်သောအဆင့်များ၊ evidence နှင့် လုံခြုံသော cleanup ကို စစ်ပါမည်။",
        "difficulty": "beginner",
        "language": "bash",
        "starter_code": "# Write your pre-flight checks, lab commands, observations, and cleanup notes here.\n",
        "status": "draft",
    }


def _module_questions() -> list[dict]:
    questions = [
        ("What does Docker primarily package?", ["An application and its user-space dependencies", "A physical server", "A student password database", "A browser tab"], "An application and its user-space dependencies", "Docker packages an application and its user-space dependencies into an image.", "Docker က ဘာကို အဓိက package လုပ်သလဲ။", "Application နှင့် user-space dependencies များ", "basics"),
        ("Which component manages local images and containers?", ["Docker daemon", "README file", "DNS cache", "Text editor"], "Docker daemon", "The daemon manages local Docker resources through the Engine API.", "Local image နှင့် container များကို ဘယ် component က စီမံသလဲ။", "Docker daemon", "architecture"),
        ("Why are containers not simply virtual machines?", ["They normally share the host kernel", "They always include a full guest OS", "They cannot run processes", "They are only documentation"], "They normally share the host kernel", "The isolation and kernel model differs from a VM.", "Container သည် VM မဟုတ်ရသည့် အဓိကအကြောင်းရင်းက ဘာလဲ။", "Host kernel ကို share လုပ်တတ်ခြင်း", "architecture"),
        ("What is a safer first step before a destructive Docker command?", ["Inspect the context and target resources", "Run system prune everywhere", "Expose the production socket", "Delete all images"], "Inspect the context and target resources", "Inspection limits accidental impact in shared environments.", "ဖျက်နိုင်သော command မ run မီ ဘာလုပ်သင့်သလဲ။", "Context နှင့် target resource ကို inspect လုပ်ခြင်း", "cli"),
        ("What does a mutable image tag mean?", ["It can point to different content over time", "It is a cryptographic digest", "It proves the image is safe", "It is a container ID"], "It can point to different content over time", "Tags are convenient references; digests identify exact content.", "Mutable image tag ဆိုတာ ဘာကို ဆိုလိုသလဲ။", "အချိန်နှင့်အမျှ content မတူသောနေရာသို့ ညွှန်နိုင်ခြင်း", "images"),
        ("Which practice helps prevent secrets entering an image?", ["Keep secrets out of the build context and layers", "COPY every .env file", "Put passwords in ARG", "Commit credentials to Git"], "Keep secrets out of the build context and layers", "Use controlled runtime secret injection instead of baking credentials into layers.", "Secret များ image ထဲ မဝင်စေရန် ဘာလုပ်သင့်သလဲ။", "Build context နှင့် layer ထဲ secret မထည့်ခြင်း", "security"),
        ("What does docker run normally do?", ["Create and start a container", "Publish source code", "Format the host disk", "Review a pull request"], "Create and start a container", "docker run creates a container from an image and starts it.", "docker run က ပုံမှန်အားဖြင့် ဘာလုပ်သလဲ။", "Container create နှင့် start", "lifecycle"),
        ("Why use a narrow .dockerignore?", ["To exclude secrets, .git, and irrelevant large files", "To publish every host file", "To disable image layers", "To replace authentication"], "To exclude secrets, .git, and irrelevant large files", "A small context reduces accidental disclosure and improves build behavior.", ".dockerignore ကို ဘာကြောင့်သုံးသလဲ။", "Secret၊ .git နှင့် မလိုအပ်သော file များ ဖယ်ရန်", "build"),
        ("Which statement about restart policies is correct?", ["They do not replace health checks and observability", "They make code secure", "They publish every port", "They verify image provenance"], "They do not replace health checks and observability", "Recovery behavior is not the same as proving application health.", "Restart policy က ဘာကို အစားမထိုးနိုင်သလဲ။", "Health check နှင့် observability", "lifecycle"),
        ("What is a content-addressed image digest used for?", ["Identifying exact image content", "Naming a learner", "Opening a browser", "Changing a host kernel"], "Identifying exact image content", "Digests support reproducible artifact references.", "Image digest ကို ဘာအတွက် သုံးသလဲ။", "Exact image content ခွဲခြားရန်", "images"),
        ("Which process is safer for a first local lab?", ["Predict, run a bounded command, inspect, and clean up", "Run unbounded commands as root", "Use a production context", "Skip verification"], "Predict, run a bounded command, inspect, and clean up", "The workflow creates evidence and limits scope.", "Local lab အတွက် ဘယ် workflow က ပိုလုံခြုံသလဲ။", "ခန့်မှန်း၊ bounded run၊ inspect နှင့် cleanup", "safety"),
        ("Where should application logs normally be written for simple container collection?", ["stdout and stderr", "A secret file in the image", "An untracked host directory", "A password field"], "stdout and stderr", "Container log collection commonly reads the process streams.", "Application log ကို ပုံမှန်အားဖြင့် ဘယ်ကို ပို့သင့်သလဲ။", "stdout နှင့် stderr", "observability"),
        ("What does --rm request for a disposable container?", ["Remove the container after it exits", "Remove the host", "Delete the registry", "Disable all logs"], "Remove the container after it exits", "It is useful for bounded labs, but capture evidence before exit.", "--rm က ဘာကို တောင်းဆိုသလဲ။", "Exit ပြီးလျှင် container ဖျက်ရန်", "lifecycle"),
        ("Why should an application process run as non-root when possible?", ["It reduces the impact of a process compromise", "It makes the image immutable", "It guarantees no bugs", "It removes the need for updates"], "It reduces the impact of a process compromise", "Least privilege limits the blast radius; it is not a complete security control.", "Non-root user ကို ဘာကြောင့်သုံးသင့်သလဲ။", "Process compromise ဖြစ်လျှင် ထိခိုက်မှုလျော့စေရန်", "security"),
        ("Which item belongs in a Docker pre-flight check?", ["Active context and target resources", "A plaintext credential", "An unrelated production cleanup", "An unknown socket endpoint"], "Active context and target resources", "Pre-flight checks prevent operating on the wrong daemon.", "Docker pre-flight check မှာ ဘာပါသင့်သလဲ။", "Active context နှင့် target resources", "cli"),
        ("What is an image layer?", ["A filesystem change recorded by the image build", "A student progress row", "A browser cookie", "A VM hypervisor"], "A filesystem change recorded by the image build", "Layers support image construction and cache behavior.", "Image layer ဆိုတာ ဘာလဲ။", "Build အတွင်း မှတ်တမ်းတင်ထားသော filesystem change", "images"),
        ("Which statement is a valid cleanup boundary?", ["Remove only resources created by your lab", "Delete all resources on a shared daemon", "Use prune without inspection", "Delete another team’s volume"], "Remove only resources created by your lab", "Explicit cleanup prevents collateral deletion.", "မှန်ကန်သော cleanup boundary က ဘာလဲ။", "ကိုယ့် lab မှ ဖန်တီးသော resource များသာ ဖျက်ခြင်း", "safety"),
        ("What should a learner record instead of a guaranteed Docker patch output?", ["The actual observed version and platform", "A copied screenshot from a different machine", "A fabricated success message", "A production credential"], "The actual observed version and platform", "Software output varies; evidence should describe the environment that produced it.", "နမူနာ patch output အစား ဘာကို မှတ်တမ်းတင်သင့်သလဲ။", "အမှန်တကယ်တွေ့ရသော version နှင့် platform", "verification"),
    ]
    return [{"position": i, "prompt": p, "prompt_mm": pmm, "options": options, "correct_answer": answer, "explanation": explanation, "explanation_mm": expmm, "difficulty": "beginner", "topic": topic, "points": 1} for i, (p, options, answer, explanation, pmm, expmm, topic) in enumerate(questions, 1)]


def _ensure_project(db: Session, course: Course, module: CourseModule, actor_id: UUID | None) -> ProjectTemplate:
    slug = "docker-module-01-my-first-docker-service"
    project = db.scalar(select(ProjectTemplate).where(ProjectTemplate.slug == slug))
    category = db.scalar(select(ProjectCategory).where(ProjectCategory.slug.in_(("devops", "devops-cloud", "web-development"))).order_by(ProjectCategory.slug))
    values = {
        "title": "My First Docker Service",
        "slug": slug,
        "description_en": "Build and document a small reproducible Docker service from a reviewed image or Dockerfile in a disposable local environment.",
        "description_mm": "Disposable local environment ထဲတွင် reviewed image သို့မဟုတ် Dockerfile အသုံးပြုပြီး ပြန်လည်တည်ဆောက်နိုင်သော Docker service သေးငယ်တစ်ခု တည်ဆောက်ပြီး မှတ်တမ်းတင်ရန်။",
        "difficulty": "beginner", "estimated_hours": 3,
        "requirements": "Use a disposable local Docker context; do not use production credentials, private data, or an unapproved registry.",
        "learning_outcomes": "Explain image/container boundaries; write a safe first Dockerfile; run and inspect a service; document evidence and cleanup.",
        "technology_stack": "Docker Engine or Docker Desktop, Dockerfile, shell, optional Python or static HTTP service",
        "prerequisites": "Docker Module 01 draft lessons and basic terminal navigation",
        "architecture_overview": "Source and Dockerfile → build context → image → container → logs/inspection → explicit cleanup",
        "folder_structure": "docker-service/\n  Dockerfile\n  .dockerignore\n  app.py or index.html\n  README.md",
        "testing_guide": "Run the service in a disposable context, check the expected response or output, inspect the container, and record the actual Docker version/context.",
        "deployment_guide": "This is a local learning project. Do not deploy it until an independent reviewer validates the image source, configuration, secrets handling, resource limits, and rollback plan.",
        "tags_json": json.dumps(["docker", "containers", "beginner", "module-01"]),
        "languages_json": json.dumps(["bash", "dockerfile", "python"]),
        "brief_json": json.dumps({"review_status": "draft", "module": str(module.id)}, default=str),
        "category_id": category.id if category else None, "status": "draft", "published": False, "created_by": actor_id,
    }
    if not project:
        project = ProjectTemplate(**values); db.add(project); db.flush()
        db.add(ProjectVersion(project_id=project.id, version=1, status="draft", snapshot_json=json.dumps(values, default=str), created_by=actor_id))
    else:
        for key, value in values.items(): setattr(project, key, value)
    if not db.scalar(select(ProjectCourseLink).where(ProjectCourseLink.project_id == project.id, ProjectCourseLink.course_id == course.id, ProjectCourseLink.module_id == module.id, ProjectCourseLink.lesson_id.is_(None))):
        db.add(ProjectCourseLink(project_id=project.id, course_id=course.id, module_id=module.id, position=0))
    milestone_specs = [
        ("Plan the service", "Choose one bounded service, identify its input/output, image source, port, and cleanup boundary.", "Service decision, threat boundary, and acceptance checks are written before building."),
        ("Build a small image", "Write a minimal Dockerfile and .dockerignore, then build with an explicit tag.", "Build context is narrow, dependencies are documented, and no secret is copied."),
        ("Run and inspect", "Run the container with an explicit name, verify its response or output, and inspect logs/state.", "Observed evidence matches the project acceptance checks."),
        ("Document and clean up", "Record the actual environment, commands, result, limitation, and cleanup evidence.", "README is reproducible and only project-created resources are removed."),
    ]
    existing = db.scalars(select(ProjectMilestone).where(ProjectMilestone.project_id == project.id).order_by(ProjectMilestone.position)).all()
    for position, (title, description, criteria) in enumerate(milestone_specs):
        milestone = existing[position] if position < len(existing) else ProjectMilestone(project_id=project.id, position=position)
        milestone.title=title; milestone.slug=_slug(title); milestone.description_en=description; milestone.description_mm=f"{title} ကို လေ့ကျင့်ပါ။ {criteria}"; milestone.content_en=description; milestone.content_mm=f"{description} {criteria}"; milestone.completion_criteria=criteria; milestone.required=True
        db.add(milestone); db.flush()
        if not db.scalar(select(ProjectTask).where(ProjectTask.milestone_id == milestone.id, ProjectTask.position == 0)):
            db.add(ProjectTask(milestone_id=milestone.id, title=title, description=description, completion_criteria=criteria, position=0, required=True))
    if not db.scalar(select(ProjectRequirement).where(ProjectRequirement.project_id == project.id, ProjectRequirement.position == 0)):
        db.add(ProjectRequirement(project_id=project.id, position=0, title="Safe local evidence", description="Provide commands, observed output, environment details, and cleanup evidence.", acceptance_criteria="A reviewer can reproduce the result without production access or secret material.", required=True))
    if not db.scalar(select(ProjectRubricCriterion).where(ProjectRubricCriterion.project_id == project.id)):
        for position, (name, weight) in enumerate((("Technical correctness", 35), ("Safety and least privilege", 25), ("Verification evidence", 25), ("Documentation", 15))):
            db.add(ProjectRubricCriterion(project_id=project.id, position=position, name=name, description=f"Review {name.lower()} for the Docker service.", weight=weight))
    return project


def seed_docker_module_one(db: Session, course: Course, actor_id: UUID | None = None) -> dict:
    module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == 1))
    if not module: raise ValueError("Docker Module 01 is missing")
    lessons = db.scalars(select(Lesson).where(Lesson.module_id == module.id).order_by(Lesson.order_index)).all()
    by_title = {lesson.title: lesson for lesson in lessons}
    drafts = exercises = 0
    for index, item in enumerate(MODULE_ONE, 1):
        title, topic = item[0], item[1]
        lesson = by_title.get(title)
        if not lesson: raise ValueError(f"Existing Docker lesson is missing: {title}")
        en, mm = _lesson_content(index, item)
        draft = db.scalar(select(LessonContentDraft).where(LessonContentDraft.lesson_id == lesson.id))
        if draft and draft.status in {"in_review", "approved", "published"}:
            # A review or published decision owns this version; an authoring
            # rerun must never reset it or replace its submitted content.
            continue
        if not draft:
            draft = LessonContentDraft(lesson_id=lesson.id, base_content_version=lesson.content_version, draft_version=1, created_by=actor_id)
            db.add(draft); drafts += 1
        desired = {"title": lesson.title, "slug": lesson.slug, "description": lesson.description, "content_en": en, "content_mm": mm, "duration_minutes": max(lesson.duration_minutes, 35), "status": "draft", "change_summary": "Phase 03 Docker Module 01 authoring batch"}
        if draft.id and any(getattr(draft, key) != value for key, value in desired.items()):
            draft.draft_version += 1
        for key, value in desired.items(): setattr(draft, key, value)
        draft.updated_by=actor_id
        exercise_values = _exercise_values(index, title, topic, title)
        exercise = db.scalar(select(CodingExercise).where(CodingExercise.slug == exercise_values["slug"]))
        if not exercise:
            db.add(CodingExercise(lesson_id=lesson.id, **exercise_values)); exercises += 1
        else:
            exercise.lesson_id=lesson.id
            for key, value in exercise_values.items(): setattr(exercise, key, value)
    quiz = db.scalar(select(ModuleQuizDraft).where(ModuleQuizDraft.module_id == module.id))
    questions_json = json.dumps(_module_questions(), ensure_ascii=False)
    if not quiz: quiz=ModuleQuizDraft(module_id=module.id,created_by=actor_id); db.add(quiz)
    if quiz.status not in {"in_review", "approved", "published"}:
        if quiz.id and any((getattr(quiz, key) != value for key, value in {"title_en": "Docker Module 01 Knowledge Check", "title_mm": "Docker Module 01 နားလည်မှု စစ်ဆေးခြင်း", "questions_json": questions_json, "pass_percent": 70, "status": "draft"}.items())): quiz.draft_version += 1
        quiz.title_en="Docker Module 01 Knowledge Check"; quiz.title_mm="Docker Module 01 နားလည်မှု စစ်ဆေးခြင်း"; quiz.questions_json=questions_json; quiz.pass_percent=70; quiz.status="draft"; quiz.updated_by=actor_id
    project=_ensure_project(db, course, module, actor_id)
    return {"course_id": str(course.id), "module_id": str(module.id), "lessons": len(lessons), "drafts_created": drafts, "exercises_created": exercises, "module_quiz_questions": 18, "project_id": str(project.id), "status": "draft"}
