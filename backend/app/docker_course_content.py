"""Reviewed Docker vertical slice for the idempotent catalog seed.

Only authored lessons are published. The remaining module names are retained
as a plan so empty curriculum records are never presented as completed work.
"""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion


PLANNED_MODULES = [
    "Introduction to Docker", "Containers vs Virtual Machines", "Docker Installation & Setup",
    "Docker Architecture", "Docker CLI Fundamentals", "Container Lifecycle", "Docker Images",
    "Dockerfile Fundamentals", "Advanced Dockerfile", "Docker Build & BuildKit", "Multi-Stage Builds",
    "Docker Networking Fundamentals", "Advanced Container Networking", "Docker Volumes", "Bind Mounts & Storage",
    "Environment Variables & Configuration", "Docker Compose Fundamentals", "Advanced Docker Compose",
    "Dockerizing Python Applications", "Dockerizing Django Applications", "Dockerizing Node.js & React",
    "Dockerizing Laravel & PHP", "Docker Hub & Registries", "Image Versioning & Publishing",
    "Docker Security Fundamentals", "Image Scanning & Supply Chain", "Secrets & Runtime Security",
    "Rootless Docker & Hardening", "Container Logs & Monitoring", "Container Resource Management",
    "Docker Performance Optimization", "Backup & Recovery", "Docker in Production", "Docker CI/CD Pipelines",
    "Cloud Container Deployment", "Docker & Kubernetes Fundamentals", "Docker Troubleshooting",
    "Professional Docker Architecture", "Real-World Docker Projects", "Final Docker Capstone & Assessment",
]

MODULE_ONE = [
    ("What Docker Is and Why It Exists", "container packaging and reproducible application environments", "docker --version\ndocker run --rm hello-world", "Docker packages an application and its user-space dependencies into an image that can run as an isolated container. Containers share the host kernel, so they are not virtual machines. Reproducibility improves when the image is built from a reviewed Dockerfile and dependencies are pinned. Docker does not make unsafe code safe: input validation, least privilege, patching, and access control still matter.", "Docker သည် application နှင့် dependencies များကို image အဖြစ် package လုပ်ပြီး container အဖြစ် run စေသော platform ဖြစ်သည်။ Container သည် VM မဟုတ်ဘဲ host kernel ကို share လုပ်သည်။ Reproducibility ရရန် Dockerfile နှင့် dependency version များကို စနစ်တကျ ထိန်းချုပ်ရမည်။", "A browser-free local exercise: identify the application, image, container, host kernel, and persistent data boundary in a diagram of a sample web service.", "Docker သည် ဘာအတွက် အသုံးပြုသနည်း?", ["Reproducible application packaging", "Replacing all databases", "Publishing passwords"], "Reproducible application packaging", "Images give teams a repeatable artifact for a runtime environment.", "Docker commands are shown for local learning only; the platform does not execute them."),
    ("Containers vs Virtual Machines", "isolation boundaries, images, kernels, and resource trade-offs", "docker run --rm alpine:3.20 uname -a\n# Compare with a VM conceptually", "A virtual machine contains a guest operating system and virtual hardware, while a container normally shares the host kernel and isolates processes, filesystems, networking, and capabilities. Containers often start faster and use fewer resources, but their boundary is different. Choose isolation based on threat model, workload, compliance, and operational requirements rather than speed alone.", "Container နှင့် VM တို့၏ isolation boundary မတူပါ။ VM တွင် guest OS ပါပြီး container တွင် host kernel ကို share လုပ်တတ်သည်။ Resource သက်သာခြင်းတစ်ခုတည်းဖြင့် architecture ဆုံးဖြတ်ခြင်းမပြုဘဲ security၊ compliance နှင့် workload ကို ထည့်သွင်းစဉ်းစားပါ။", "Create a comparison table with kernel, startup time, image contents, isolation assumptions, and common use cases.", "Container သည် VM နှင့် လုံးဝတူသည်ဟု ယူဆခြင်းသည် မှားသည်။", ["False", "True"], "False", "They provide different isolation and operational models.", "This comparison is conceptual and does not create a VM or container on the Academy host."),
    ("Install Docker and Verify the Engine", "safe local installation, contexts, and daemon access", "docker info\ndocker context show\ndocker run --rm hello-world", "Install Docker Desktop or Docker Engine using the official instructions for your operating system. Verify the client and engine separately. Docker contexts select a daemon endpoint, so inspect the active context before running commands. Never connect a learning environment to a production daemon or expose the Docker socket to an untrusted process.", "Operating system အလိုက် official Docker installation နည်းလမ်းကို သုံးပါ။ docker info နှင့် docker context show ဖြင့် client၊ engine နှင့် active context ကို စစ်ပါ။ Production daemon သို့ မချိတ်ဆက်ပါနှင့်၊ Docker socket ကို untrusted process သို့ မဖော်ပြပါနှင့်။", "Install Docker locally, verify the version and active context, then remove the hello-world container after observing its output.", "Docker engine မတွေ့ပါက active context၊ daemon status နှင့် user permission ကို စစ်ပါ။", ["Check the daemon and active context", "Expose the production socket", "Disable all security"], "Check the daemon and active context", "A client can be installed while the engine or selected context is unavailable.", "Examples assume a disposable local context, not the Academy host."),
    ("Docker Engine Architecture", "CLI, daemon, images, containers, and registries", "docker build -t academy-demo:1.0 .\ndocker create --name academy-demo academy-demo:1.0\ndocker start academy-demo", "The Docker CLI sends API requests to a Docker daemon. The daemon manages images, containers, networks, and volumes. A registry stores distributable images, but pulling an image is not the same as trusting it: verify provenance, scan it, pin a digest where appropriate, and minimize runtime privileges.", "Docker CLI က Docker daemon သို့ API request ပို့သည်။ Daemon က image၊ container၊ network နှင့် volume များကို စီမံသည်။ Registry မှ image ဆွဲယူခြင်းသည် ယုံကြည်စိတ်ချပြီးသားဟု မဆိုလိုပါ။ Provenance၊ scan၊ digest နှင့် privilege များကို စစ်ဆေးပါ။", "Draw CLI → daemon → image/container and registry → image flows. Mark which operations mutate local state.", "ဘယ်အစိတ်အပိုင်းက container lifecycle ကို စီမံသနည်း?", ["Docker daemon", "README only", "Browser cache"], "Docker daemon", "The daemon manages local Docker resources through the engine API.", "The displayed architecture is explanatory, not a live daemon connection."),
    ("Docker CLI Fundamentals", "safe inspection, explicit names, and repeatable commands", "docker images\ndocker ps --all\ndocker inspect academy-demo\ndocker logs academy-demo\ndocker stop academy-demo\ndocker rm academy-demo", "The CLI is an interface to inspect and manage Docker resources. Prefer explicit names, labels, and bounded commands. Inspect before deleting. Use docker ps, logs, inspect, and stats to gather evidence. Avoid broad prune commands in shared environments because they can remove resources owned by other work.", "CLI ဖြင့် image နှင့် container များကို inspect၊ log ကြည့်၊ stop နှင့် remove လုပ်နိုင်သည်။ Delete မလုပ်မီ inspect လုပ်ပါ။ Shared environment တွင် broad prune command များကို မသုံးပါနှင့်။", "Run the inspection commands against your disposable local lab and record the difference between a stopped container and a removed container.", "ဘယ် command က container ကို မဖျက်ဘဲ ရပ်စေသနည်း?", ["docker stop", "docker rm -f everything", "docker system prune"], "docker stop", "Stopping preserves the container object for inspection; removal deletes it."),
    ("Container Lifecycle", "create, start, stop, restart, logs, and removal", "docker run -d --name web-demo -p 8080:80 nginx:1.27\ndocker ps\ndocker logs web-demo\ndocker stop web-demo\ndocker rm web-demo", "A container moves through created, running, stopped, and removed states. `docker run` creates and starts by default; a restart policy can affect recovery but is not a substitute for health checks and observability. Publish only required ports and bind development services deliberately. Remove disposable resources during cleanup.", "Container lifecycle တွင် create၊ running၊ stopped နှင့် removed states ရှိသည်။ restart policy သည် health check နှင့် observability ကို အစားမထိုးနိုင်ပါ။ လိုအပ်သော port များကိုသာ publish လုပ်ပါ။", "Use a disposable local container, inspect it after stopping, and remove it only after saving the evidence you need.", "Container run သည် ဘာလုပ်သနည်း?", ["Create and start a container", "Push secrets to a registry", "Format a host disk"], "Create and start a container", "docker run creates a container from an image and starts it unless configured otherwise."),
    ("Docker Images and Tags", "immutable layers, tags, digests, and pull trust", "docker pull python:3.12-slim\ndocker image ls\ndocker image inspect python:3.12-slim\ndocker tag python:3.12-slim academy-python:local", "An image is composed of filesystem layers and metadata. Tags are mutable human-friendly pointers; digests identify exact content. Use small, maintained base images, record the source, and pin a digest for sensitive or reproducible deployments. Do not assume an image is safe because its name looks official.", "Image သည် filesystem layer များနှင့် metadata ပါဝင်သော artifact ဖြစ်သည်။ Tag သည် ပြောင်းလဲနိုင်သော်လည်း digest သည် exact content ကို ခွဲခြားပေးသည်။ Base image ကို maintained၊ small ဖြစ်စေပြီး source နှင့် version ကို မှတ်တမ်းတင်ပါ။", "Compare a mutable tag and a digest in your local notes, then explain why a deployment manifest should identify an exact artifact.", "ဘယ် identifier က exact image content ကို ခွဲခြားပေးသနည်း?", ["Digest", "A mutable tag only", "Container name"], "Digest", "A digest identifies the content-addressed image manifest."),
    ("Write a Secure First Dockerfile", "Dockerfile instructions, layers, non-root users, and build context", "FROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY app.py .\nRUN useradd --create-home appuser\nUSER appuser\nCMD [\"python\", \"app.py\"]", "A Dockerfile is a repeatable build recipe. Put stable dependency installation before frequently changing source code to improve cache reuse. Use a narrow build context, avoid copying secrets, run as a non-root user, and use JSON-array command syntax. The image should contain only what the process needs.", "Dockerfile သည် image build recipe ဖြစ်သည်။ Dependency layer ကို source code မတိုင်မီထားပါက cache reuse ကောင်းသည်။ Secret များကို context ထဲမထည့်ပါနှင့်၊ non-root user သုံးပါ၊ JSON-array CMD သုံးပါ။", "Create a tiny Python app and Dockerfile in a disposable directory, build it locally, inspect the image, and explain each layer before running it.", "Dockerfile တွင် secret ကို ဘယ်လိုထည့်သင့်သနည်း?", ["မထည့်ရ; secret manager/runtime injection သုံးရမည်", "COPY secrets.txt", "ARG password=..."], "မထည့်ရ; secret manager/runtime injection သုံးရမည်", "Build arguments and layers can leak credentials; inject secrets at runtime through a controlled mechanism."),
    ("Docker Build, Run, and Clean Up", "build context, cache, health expectations, and a first container lab", "docker build -t academy-hello:1.0 .\ndocker run --rm --name academy-hello academy-hello:1.0\ndocker image rm academy-hello:1.0", "The build context is the directory sent to the builder, so a .dockerignore file is essential for excluding virtual environments, git history, secrets, and large artifacts. Build output should be reviewable. A container should have one clear process, deterministic configuration, logs to stdout/stderr, and an explicit cleanup path.", "Build context ထဲမှ မလိုအပ်သော file များကို .dockerignore ဖြင့် ဖယ်ပါ။ Container တစ်ခုတွင် ရှင်းလင်းသော main process တစ်ခုထားပြီး logs ကို stdout/stderr သို့ ပို့ပါ။ Lab ပြီးလျှင် disposable image နှင့် container ကို cleanup လုပ်ပါ။", "Complete the first-container lab: create a hello image, run it with --rm, confirm its output, and remove the local image after the exercise.", "Docker build မလုပ်ခင် ဘာကို မထည့်သင့်သနည်း?", ["Secrets, .git, virtual environments, and build artifacts", "Application source needed by the image", "The Dockerfile itself when it is required"], "Secrets, .git, virtual environments, and build artifacts", ".dockerignore limits context size and prevents accidental inclusion of sensitive or irrelevant files."),
]

# Keep the vertical slice at eight published lessons; image tags are covered
# by the Dockerfile/build lesson until the dedicated later module is authored.
MODULE_ONE = [item for item in MODULE_ONE if item[0] != "Docker Images and Tags"]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, commands, theory, mm, exercise, prompt, options, answer, explanation, *notes = item
    note = notes[0] if notes else "Use a disposable local Docker context and remove resources after practice."
    previous = "No Docker experience is required; terminal familiarity is helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: complete the first-container lab and review the Module 1 assessment."
    return f"""Introduction
{title} introduces {topic} through a safe, local-first Docker workflow.

Learning objectives
- Explain {topic} and its operational boundary.
- Read the commands and predict their effect before running them.
- Apply least privilege, cleanup, and supply-chain thinking.

Prerequisites
{previous}

Architecture diagram
CLI → Docker API → daemon → image / container / network / volume
Registry ↔ image artifact

Complete theory
{theory}

Step-by-step commands
```bash
{commands}
```
The Academy displays commands as read-only instructional examples. Run them only in your own disposable local Docker context.

Expected output
The exact output depends on the installed Docker version and local platform. Verify the stated resource, status, logs, or cleanup result rather than copying an unverified output.

Command explanation
Read each command left to right: identify the client action, the selected image or resource, the ports or filesystem effects, and the cleanup boundary. Avoid broad deletion commands until you have inspected ownership.

Common errors
- Docker CLI is installed but the daemon is stopped or the wrong context is active.
- A tag points to a different image than expected because tags can change.
- The build context includes secrets, .git, virtual environments, or large artifacts.
- A container exits because its foreground process finished or configuration is invalid.

Troubleshooting
Run `docker context show`, `docker info`, `docker ps --all`, and `docker logs <name>` in a disposable local context. Read the first useful error, inspect before deleting, and do not expose the Docker socket to untrusted code.

Best practices
- Use small maintained base images and pin dependencies or digests where reproducibility matters.
- Add a .dockerignore, run as non-root, log to stdout/stderr, and define health checks for services.
- Keep one clear process per container and document ports, volumes, environment variables, and cleanup.

Security considerations
Never hardcode secrets, use privileged mode casually, mount the host filesystem, or publish unnecessary ports. Apply least privilege, read-only filesystems and resource limits where appropriate. Image scanning and signing complement, but do not replace, patching and review.

Hands-on exercise
{exercise}

Quiz
{prompt}

Mini project
Create a small README and Dockerfile for a deterministic hello service. Include the folder tree, .dockerignore, build/run commands, expected output, cleanup commands, and a security checklist. Do not run it on the CodeMaster Academy host.

Summary
You can now reason about {topic} and verify its effect without treating a Docker command as harmless by default.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
{note}
"""


def seed_docker_course(db, course):
    course.title = "Docker & Containerization — From Zero to Professional DevOps"
    course.short_description = "A free, practical path from Docker fundamentals to secure production container workflows."
    course.description = "Learn Docker images, containers, Dockerfiles, networking, volumes, Compose, security, CI/CD, registries, troubleshooting, and production architecture through safe, reproducible examples."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 35
    course.outcomes = "Explain images, containers, layers, and the Docker Engine|Build reproducible images with secure Dockerfiles|Design Compose services with networks, volumes, and health checks|Apply container security, scanning, CI/CD, and deployment practices"
    course.requirements = "Basic terminal usage and a text editor; Docker commands are practiced locally and are never executed by the platform."

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
        lesson.content_mm = f"{title}\n\n{item[4]}\n\nလေ့ကျင့်ခန်း\n{item[5]}"
        lesson.duration_minutes, lesson.status, lesson.published = 35, "published", True

        example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        code = item[2]
        values = {"title": f"{title} example", "language": "bash", "filename": item[2].splitlines()[0] if item[2].startswith("docker") else "Dockerfile", "code": code, "description": "Read-only Docker example. Run only in a disposable local context; the Academy does not execute Docker commands.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)

        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the explanation and retry after identifying the resource and security boundary.", status="published")
            db.add(quiz)
            db.flush()
        options = item[7]
        questions = [(item[6], options, item[8], item[9]), ("True or false: Docker commands in this course are executed on the Academy host.", ["True", "False"], "False", "The platform only displays safe instructional examples."), ("Which practice improves container security?", ["Run as non-root and minimize privileges", "Mount the host filesystem by default", "Commit credentials into the image"], "Run as non-root and minimize privileges", "Least privilege and non-root execution reduce blast radius.")]
        for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
            question = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
            values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
            if not question:
                db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
            else:
                for key, value in values.items():
                    setattr(question, key, value)
    db.flush()

