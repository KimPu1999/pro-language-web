"""Authored Linux vertical slice for the idempotent catalog seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

PLANNED_MODULES = [
    "Introduction to Linux", "Linux Installation & Setup", "Terminal & Shell Fundamentals", "Linux File System Structure",
    "Navigation Commands", "Files & Directories", "Viewing & Editing Files", "Searching Files & Text", "Pipes & Redirection",
    "File Permissions", "Users & Groups", "Sudo & Privilege Management", "Processes & Jobs", "Package Management",
    "Archives & Compression", "Linux Boot Process", "systemd & Service Management", "Logs & Troubleshooting",
    "Storage & File Systems", "Disk & Partition Management", "Scheduled Tasks", "Environment Variables & Shell Config",
    "Bash Scripting Fundamentals", "Advanced Bash Scripting", "Linux Networking Fundamentals", "Networking Commands",
    "SSH & Remote Server Access", "Firewalls & Network Security", "Web Servers & Reverse Proxies", "Linux Security Fundamentals",
    "Monitoring & Performance", "Backup & Disaster Recovery", "Docker on Linux", "Linux Automation & Ansible",
    "Linux for CI/CD", "Linux Cloud Server Administration", "Production Server Deployment", "Advanced Troubleshooting & Reliability",
    "Professional Linux Projects", "Final Linux Capstone & Assessment",
]

MODULE_ONE = [
    ("What Linux Is and Why It Matters", "kernel, user space, distributions, and server reliability", "uname -a\ncat /etc/os-release\nwhoami", "terminal", "Linux is an operating system family built around a kernel and user-space tools. Distributions package the kernel, libraries, package manager, services, and defaults. The same command can differ across distributions, so identify the platform before changing configuration.", "Linux သည် kernel နှင့် user-space tools ပေါ်တွင် တည်ဆောက်ထားသော operating system family ဖြစ်သည်။ Distribution တစ်ခုစီတွင် package manager နှင့် default configuration မတူနိုင်သောကြောင့် platform ကို အရင်သိရမည်။", "Compare kernel, shell, and distribution responsibilities in a three-layer diagram.", ("Linux distribution တွင် ဘာတွေပါဝင်သနည်း?", ["Kernel, user-space tools, packages, and defaults", "Only a web browser", "A database password"], "Kernel, user-space tools, packages, and defaults", "A distribution combines the kernel and user-space operating environment.")),
    ("Install Linux Safely in a Practice Environment", "virtual machines, images, and isolated administration", "cat /etc/os-release\nuname -r\nhostnamectl", "terminal", "Practice Linux administration in a disposable virtual machine or approved container. Confirm the image source, architecture, user identity, and network boundary. Never experiment with destructive commands on production systems or student data.", "Linux administration ကို disposable VM သို့မဟုတ် approved container ထဲတွင် လေ့ကျင့်ပါ။ Image source၊ architecture၊ identity နှင့် network boundary ကို verify လုပ်ပါ။", "Create a safe lab checklist covering image source, snapshot, user, network, and recovery plan.", ("Linux command လေ့ကျင့်မှုကို ဘယ်မှာလုပ်သင့်သနည်း?", ["An isolated practice environment", "A production server blindly", "A shared secrets directory"], "An isolated practice environment", "Isolation limits the impact of mistakes.")),
    ("Terminal, Shell, and Command Syntax", "command names, arguments, options, and exit status", "printf 'hello\\n'\necho $SHELL\ncommand -v bash\ntrue\necho $?", "terminal", "A terminal provides an interface, while a shell parses commands and expands variables, paths, pipes, and redirection. Read command help before using options. Exit status is evidence for automation, but output and side effects must also be reviewed.", "Terminal သည် interface ဖြစ်ပြီး shell သည် command များကို parse လုပ်သည်။ Option မသုံးမီ help ဖတ်ပြီး exit status နှင့် side effect ကို စစ်ပါ။", "Annotate a command into name, option, argument, output, and exit status.", ("Shell သည် ဘာကိုလုပ်သနည်း?", ["Parse and run commands in a user environment", "Replace the kernel", "Store passwords publicly"], "Parse and run commands in a user environment", "The shell interprets command syntax and invokes programs.")),
    ("Linux File System Hierarchy", "root, home, etc, var, tmp, and device boundaries", "pwd\nls /\nls /etc\nls /var\nls /tmp", "terminal", "Linux presents files through a hierarchy rooted at /. /etc contains configuration, /var commonly contains changing data and logs, /tmp is temporary, and /home contains user data. Paths and permissions are safety boundaries; do not edit system files casually.", "Linux filesystem root သည် / ဖြစ်ပြီး /etc သည် configuration၊ /var သည် changing data/log၊ /tmp သည် temporary နှင့် /home သည် user data အတွက် ဖြစ်သည်။", "Draw a filesystem map and label which locations are configuration, user data, logs, and temporary storage.", ("Linux filesystem ၏ root path က ဘာလဲ?", ["/", "/home only", "C:\\\\ only"], "/", "Linux paths begin at the root directory /.")),
    ("Navigate with Absolute and Relative Paths", "pwd, cd, ls, and path safety", "pwd\ncd /tmp\npwd\ncd ..\npwd\nls -la", "terminal", "pwd identifies the current directory, cd changes it, and ls inspects entries. Absolute paths begin at /; relative paths depend on the current directory. Confirm the current path before copying, moving, removing, or changing permissions.", "pwd သည် current directory ကို ပြပြီး cd သည် ပြောင်းသည်။ Absolute path သည် / ဖြင့်စပြီး relative path သည် current directory ပေါ်မူတည်သည်။", "Predict the result of cd .. from a nested path and explain why pwd should precede destructive commands.", ("Destructive command မလုပ်မီ ဘာကိုစစ်သင့်သနည်း?", ["Current path and target entries", "Only a copied command", "A production token"], "Current path and target entries", "Path verification prevents changes in the wrong directory.")),
    ("Create and Inspect Files and Directories", "mkdir, touch, ls, cp, and mv", "mkdir -p lab/notes\ntouch lab/notes/readme.txt\nls -la lab/notes\ncp lab/notes/readme.txt lab/notes/backup.txt\nmv lab/notes/backup.txt lab/notes/archive.txt", "terminal", "Filesystem commands mutate state. mkdir creates directories, touch creates or updates a file timestamp, cp copies, and mv moves or renames. Use explicit targets and inspect before and after; avoid broad globs until their expansion is understood.", "mkdir သည် directory ဖန်တီးပြီး touch သည် file ဖန်တီး/တိုးတက်၊ cp သည် copy နှင့် mv သည် move/rename လုပ်သည်။ Mutation မလုပ်မီ target ကို စစ်ပါ။", "Build a disposable directory tree and record each state change after one command.", ("cp နှင့် mv ၏ ကွာခြားချက်က ဘာလဲ?", ["cp preserves the source while mv moves or renames", "Both always delete all files", "Neither changes state"], "cp preserves the source while mv moves or renames", "Copy and move have different filesystem effects.")),
    ("View, Search, and Filter Text", "cat, less, grep, and evidence-driven inspection", "printf 'error\\ninfo\\nerror\\n' > lab.log\ncat lab.log\ngrep -n 'error' lab.log\nwc -l lab.log", "terminal", "Text inspection is safer than editing blindly. cat is useful for small files, less for larger files, grep filters matching lines, and wc summarizes counts. Logs may contain private data, so do not paste them into public channels.", "Text inspection တွင် cat၊ less၊ grep နှင့် wc ကို သုံးနိုင်သည်။ Log တွင် private data ပါနိုင်သောကြောင့် public channel ထဲ မကူးပါနှင့်။", "Filter a sample log for warning lines and state what evidence is safe to share.", ("Log file ကို စစ်ရာတွင် ဘာကို သတိထားရမည်နည်း?", ["Sensitive data may be present", "All logs are public", "grep deletes the file"], "Sensitive data may be present", "Logs often include private or security-sensitive values.")),
    ("Pipes, Permissions, and the First Safe Workflow", "pipelines, chmod concepts, and review before mutation", "printf 'read\\nwrite\\nread\\n' | grep read | wc -l\nls -l lab.log\nchmod u=rw,go= lab.log\nls -l lab.log", "terminal", "A pipe connects one command's output to another's input. chmod changes permission bits, so calculate the intended owner/group/other access before applying it. A safe workflow is inspect, change one isolated target, verify, and record recovery steps.", "Pipe သည် command output ကို နောက် command input သို့ ပို့သည်။ chmod မသုံးမီ owner/group/other permission ကို တွက်ပြီး isolated target တွင်သာ စမ်းပါ။", "Calculate a permission policy for a private log and explain why chmod 777 is usually unsafe.", ("Why should chmod 777 usually be avoided?", ["It grants broad access to everyone", "It always encrypts a file", "It only reads a file"], "It grants broad access to everyone", "Overly broad permissions increase exposure and modification risk.")),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(position: int, item: tuple) -> str:
    title, topic, commands, filename, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    previous = "No Linux experience is required; a terminal is helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: complete the first Linux commands lab and review the Module 1 assessment."
    return f"""Introduction
{title} introduces {topic} through safe, observable Linux command practice.

Learning objectives
- Explain {topic} in your own words.
- Predict command output and side effects before running it.
- Identify filesystem, privilege, network, and secret boundaries.

Prerequisites
{previous}

Linux architecture explanation
user command -> shell -> process -> kernel -> filesystem or network resource

Detailed theory
{theory}

Linux command syntax and step-by-step examples
{commands}

File system diagram
/
├── etc/       configuration
├── home/      user data
├── var/       changing data and logs
└── tmp/       temporary files

Expected output
Exact output depends on distribution, user, permissions, and local files. Inspect the state with pwd, ls, or the relevant command instead of copying unverified output.

Command explanation
Read each command and flag before running it. Identify its target, mutation, privilege requirement, output, and recovery path. Practice in an isolated environment.

Common errors
- Running a command in the wrong directory.
- Assuming flags are identical across distributions.
- Using sudo or broad globs without reviewing the target.
- Sharing logs, paths, or environment values that contain secrets.

Troubleshooting
Start with pwd, whoami, command -v, help/man, ls -la, and the first error. Preserve evidence before changing permissions, services, storage, or network settings.

Best practices
- Inspect before mutation, use least privilege, and verify after every change.
- Prefer reversible, narrow commands and documented recovery steps.
- Keep credentials out of commands, history, logs, and configuration committed to source control.

Security considerations
Never run destructive commands on production or student data. Protect SSH keys, use safe sudo policies, restrict permissions, verify packages, and isolate practice environments.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Create a disposable filesystem lab with directories, sample logs, a search pipeline, and a private file permission policy. Capture before/after state and a cleanup plan.

Summary
You can now reason about {topic} as an observable Linux state transition with explicit safety boundaries.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
The Academy displays Linux commands and does not execute arbitrary shell commands on its application host.
"""

def seed_linux_course(db, course):
    course.title = "Linux Fundamentals, System Administration & DevOps — From Zero to Professional"
    course.short_description = "A free, practical path from Linux command-line fundamentals to secure administration, automation, and DevOps."
    course.description = "Learn Linux filesystems, shell commands, permissions, users, processes, services, logs, networking, SSH, firewalls, Docker, automation, deployment, and reliability through safe examples."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 35
    course.outcomes = "Navigate Linux and inspect files, text, processes, services, logs, and network state|Apply least-privilege permissions, SSH, firewall, backup, and troubleshooting practices|Build a foundation for Bash, Docker, CI/CD, cloud administration, and deployment|Use safe, observable, reversible commands in isolated practice environments"
    course.requirements = "A computer and basic terminal curiosity; no previous Linux administration experience is required."
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
        lesson.duration_minutes, lesson.status, lesson.published = 35, "published", True
        example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        values = {"title": f"{title} example", "language": "bash", "filename": item[3], "code": item[2], "description": "Read-only Linux example. Run locally in an isolated environment; the Academy does not execute commands on its host.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the command effect and safety boundary before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [(item[7][0], item[7][1], item[7][2], item[7][3]), ("True or false: the Academy executes arbitrary Linux commands on its application host.", ["True", "False"], "False", "Examples are displayed as read-only learning content."), ("Which practice protects a Linux system?", ["Inspect targets, use least privilege, and practice in isolation", "Run broad destructive commands as root", "Publish SSH private keys"], "Inspect targets, use least privilege, and practice in isolation", "Inspection, isolation, and least privilege reduce operational risk.")]
        for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
            row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
            values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
            if not row:
                db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
            else:
                for key, value in values.items():
                    setattr(row, key, value)
    db.flush()
