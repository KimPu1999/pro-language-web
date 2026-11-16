"""Idempotent Operating Systems vertical-slice course seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion


PLANNED_MODULES = [
    "Introduction to Operating Systems", "Types of Operating Systems", "Computer Hardware Fundamentals",
    "OS Architecture & Components", "Kernel Architecture", "Boot Process & System Startup", "System Calls & OS APIs",
    "Linux, Windows & macOS Overview", "Process Fundamentals", "Process Creation & Management", "Threads & Multithreading",
    "CPU Scheduling Fundamentals", "Scheduling Algorithms", "Interprocess Communication", "Concurrency & Race Conditions",
    "Synchronization Mechanisms", "Deadlocks", "Memory Management Fundamentals", "Contiguous Memory Allocation",
    "Paging & Segmentation", "Virtual Memory", "Page Replacement Algorithms", "Memory Allocation & Caching",
    "File System Fundamentals", "File System Implementation", "Disk Scheduling & Storage", "I/O Systems & Device Drivers",
    "Protection & Access Control", "Operating System Security", "Users, Groups & Permissions", "OS Networking Fundamentals",
    "Virtualization & Hypervisors", "Containers & Namespaces", "System Monitoring & Troubleshooting", "OS Reliability & Recovery",
    "Linux Internals & Kernel Concepts", "Operating System Development Basics", "Real-Time & Distributed OS Concepts",
    "Professional Operating Systems Projects", "Final OS Engineering Capstone",
]

MODULE_ONE = [
    ("What an Operating System Does", "resource management, abstractions, and the boundary between applications and hardware",
     "user program -> system call -> kernel -> device or memory\nprocess scheduler -> CPU", "text",
     "An operating system manages CPU time, memory, storage, devices, and protection. It exposes stable abstractions such as processes, files, virtual memory, and system calls so applications do not need to control hardware directly.",
     "Operating System သည် CPU၊ memory၊ storage နှင့် device များကို စီမံပြီး process၊ file၊ virtual memory နှင့် system call abstraction များပေးသည်။",
     "Label the user-space, kernel-space, hardware, and system-call boundaries in a simple architecture diagram.",
     ("Operating System ၏ အဓိကတာဝန်က ဘာလဲ?", ["Resources and protection ကို စီမံခြင်း", "Only drawing UI", "Only storing passwords"], "Resources and protection ကို စီမံခြင်း", "An OS manages resources and protects competing programs.")),
    ("Types of Operating Systems", "desktop, server, mobile, embedded, real-time, and distributed operating-system tradeoffs",
     "desktop -> interactive latency\nserver -> throughput and isolation\nRTOS -> bounded response time", "text",
     "Operating systems are designed around workload constraints. A server prioritizes throughput, an interactive system prioritizes responsiveness, and a real-time system emphasizes predictable deadlines. Labels are useful only when tied to measurable requirements.",
     "OS အမျိုးအစားသည် workload နှင့် requirement အပေါ်မူတည်သည်။ Server တွင် throughput၊ interactive system တွင် responsiveness၊ real-time system တွင် deadline predictability အရေးကြီးသည်။",
     "Compare a learning laptop, an API server, and an embedded controller using latency, throughput, and isolation criteria.",
     ("Real-time OS တွင် အရေးကြီးဆုံးအချက်က ဘာလဲ?", ["Predictable deadline behavior", "Highest screen resolution", "Unlimited background work"], "Predictable deadline behavior", "Real-time systems emphasize bounded and predictable timing.")),
    ("Hardware Foundations for OS Work", "CPU privilege, memory, interrupts, storage, and device controllers",
     "uname -a\nfree -h\nls /proc", "bash",
     "The kernel coordinates CPU modes, address spaces, interrupts, memory controllers, storage, and devices. Hardware support differs by platform, so diagnostics should be observed rather than assumed.",
     "Kernel သည် CPU mode၊ address space၊ interrupt၊ memory controller နှင့် device များကို coordinate လုပ်သည်။ Platform ကွာခြားမှုကို diagnostics ဖြင့်စစ်ပါ။",
     "Record the hardware facts exposed by your local system and map each fact to an OS responsibility.",
     ("Interrupt သည် ဘာအတွက်အသုံးဝင်သနည်း?", ["CPU ကို event တစ်ခုကို သတိပေးရန်", "File ကို encrypt အမြဲလုပ်ရန်", "Only UI color ပြောင်းရန်"], "CPU ကို event တစ်ခုကို သတိပေးရန်", "Interrupts notify the processor about hardware or software events.")),
    ("Kernel and User Space", "privilege boundaries, protected instructions, and system-call transitions",
     "user space: application code\nprivileged space: kernel code\ntransition: syscall", "text",
     "User programs run with restricted privileges. A system call transfers control through a checked kernel boundary, where the OS validates arguments and performs privileged work. This separation limits damage from buggy or malicious applications.",
     "User space သည် restricted privilege ဖြင့် run ပြီး system call က checked kernel boundary မှတစ်ဆင့် privileged operation သို့ဝင်သည်။",
     "Explain why opening a file requires a kernel-mediated operation instead of direct disk instructions from an application.",
     ("User program က privileged instruction ကို ဘယ်လိုအသုံးပြုသနည်း?", ["Checked system call boundary မှတစ်ဆင့်", "Directly bypassing the kernel", "By changing CSS"], "Checked system call boundary မှတစ်ဆင့်", "System calls mediate privileged operations.")),
    ("The Boot Process", "firmware, bootloader, kernel initialization, and service startup",
     "firmware -> bootloader -> kernel -> init/system manager -> services", "text",
     "Booting establishes enough hardware state to load a kernel, initializes memory and devices, mounts a root filesystem, and starts user-space services. Each stage has a distinct trust and failure boundary.",
     "Boot process တွင် firmware၊ bootloader၊ kernel၊ system manager နှင့် services အဆင့်များ ပါဝင်သည်။ အဆင့်တိုင်းတွင် trust နှင့် failure boundary ရှိသည်။",
     "Create a boot timeline and identify where logs or recovery choices would help diagnose a failure.",
     ("Kernel မတိုင်မီ ဘာက boot code ကို စတင်ပေးသနည်း?", ["Firmware", "A user application", "A database query"], "Firmware", "Firmware initializes enough hardware to locate boot code.")),
    ("System Calls and OS APIs", "process, file, memory, and communication interfaces exposed to programs",
     "open -> read -> write -> close\nfork -> exec -> wait", "text",
     "System calls are the controlled API between user programs and the kernel. APIs differ by platform, but the concepts—process creation, file descriptors, memory mapping, and waiting—are broadly reusable.",
     "System call သည် user program နှင့် kernel ကြား controlled API ဖြစ်သည်။ Process၊ file descriptor၊ memory mapping နှင့် wait concept များကို လေ့လာပါ။",
     "Map open/read/write/close to file-descriptor lifecycle and specify what happens on an error.",
     ("System call ၏ အလုပ်က ဘာလဲ?", ["Kernel service ကို controlled interface ဖြင့်တောင်းခြင်း", "Every process ကို delete လုပ်ခြင်း", "Only compile CSS"], "Kernel service ကို controlled interface ဖြင့်တောင်းခြင်း", "System calls request kernel-managed services.")),
    ("Processes and the Process Control Block", "process identity, address space, registers, state, and scheduling metadata",
     "new -> ready -> running -> waiting -> ready -> terminated", "text",
     "A process is a running program plus execution context and resources. The process control block records identity, state, registers, memory mappings, open resources, and scheduling information so the OS can pause and resume it.",
     "Process သည် running program နှင့် execution context/resource များပေါင်းစပ်ထားခြင်းဖြစ်သည်။ PCB တွင် state၊ registers၊ memory mapping နှင့် scheduling data ပါသည်။",
     "Design a simulated PCB with pid, state, program counter, priority, and open-resource fields.",
     ("PCB ထဲတွင် ဘာကိုသိမ်းထားသနည်း?", ["Process state and execution context", "Only screen pixels", "Only a website URL"], "Process state and execution context", "The PCB enables process tracking and context switching.")),
    ("First OS Investigation Workflow", "safe observation, process state, memory facts, and evidence-driven troubleshooting",
     "uname -a\nps\nfree -h\ndf -h", "bash",
     "OS engineering starts with observation. Use read-only diagnostics to understand kernel version, processes, memory, and storage, then form a hypothesis. The Academy simulator uses in-memory educational state and never runs student commands on the host.",
     "OS troubleshooting တွင် read-only diagnostics ဖြင့် evidence စုဆောင်းပြီး hypothesis တည်ဆောက်ပါ။ Academy simulator သည် in-memory state ပဲသုံးသည်။",
     "Create a short report with command, observation, hypothesis, and safe next check columns.",
     ("Troubleshooting တွင် ပထမဆုံးအဆင့်က ဘာလဲ?", ["Observe and collect evidence", "Delete system files", "Guess without data"], "Observe and collect evidence", "Reliable diagnosis begins with safe observation.")),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, example, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "Basic programming and command-line familiarity are helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the OS architecture visualizer and complete the command lab."
    return f"""Introduction
{title} introduces {topic} using safe systems-engineering reasoning.

Learning objectives
- Explain {topic} and its role in an operating system.
- Separate user space, kernel space, hardware, and observable evidence.
- Choose safe diagnostics and describe security and failure boundaries.

Prerequisites
{prerequisite}

OS architecture explanation
application -> system call -> kernel subsystem -> hardware or filesystem -> result

Detailed theory
{theory}

C/Python or command example ({language})
{example}

Architecture diagram
user process -> syscall boundary -> kernel -> scheduler/memory/filesystem -> device

Expected result
The exact platform output varies. Record the command, output, interpretation, and uncertainty; do not assume a Linux-specific detail applies everywhere.

Step-by-step implementation
1. State the resource or OS boundary being studied.
2. Observe a deterministic or read-only example.
3. Explain state transitions and failure modes.
4. Verify the result with a second observation or test.
5. Document security and cleanup considerations.

Common errors
- Confusing a process with a program or a thread.
- Treating user-space checks as a replacement for kernel authorization.
- Running destructive commands before understanding scope.
- Assuming scheduler or filesystem behavior is identical on every OS.

Troubleshooting
Check the OS version, command availability, permissions, process state, memory units, logs, and the smallest safe reproduction. Use disposable virtual machines or emulators for low-level experiments.

Best practices
- Prefer read-only diagnostics, least privilege, explicit cleanup, bounded experiments, and documented assumptions.
- Separate measurement from interpretation and test algorithms with deterministic inputs.
- Never expose credentials or use real process control in a shared learning simulator.

Security considerations
The Academy playground and simulators use in-memory educational state. They do not execute arbitrary commands, access host filesystems, terminate real processes, or expose secrets. Kernel and driver exercises should run only in isolated local VMs or emulators.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Build a read-only OS investigation report with process, memory, storage, and kernel observations. Include assumptions, evidence, security boundaries, and a cleanup plan.

Summary
You can now reason about {topic} using resource, privilege, state, and evidence boundaries.

Next lesson
{next_lesson}

Myanmar explanation
{mm}
"""


def seed_operating_systems_course(db, course):
    course.title = "Operating Systems — From Zero to Advanced Systems Engineering"
    course.short_description = "A free systems-engineering path through kernels, processes, scheduling, memory, filesystems, security, virtualization, and reliability."
    course.description = "Learn operating-system architecture, hardware boundaries, system calls, processes, threads, CPU scheduling, synchronization, deadlocks, memory, virtual memory, filesystems, I/O, security, virtualization, containers, monitoring, and systems projects."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 50
    course.outcomes = "Explain OS abstractions, privilege boundaries, boot, system calls, processes, and threads|Simulate CPU scheduling, synchronization, memory, paging, filesystems, and process states|Use safe diagnostics and reason about security, isolation, virtualization, containers, and reliability|Design and test systems workflows with C/Python examples without unsafe host execution"
    course.requirements = "Basic programming and command-line familiarity are helpful; no operating-system internals experience is required."
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
        values = {"title": f"{title} example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe operating-systems example for local study; the Academy does not execute arbitrary commands.", "position": 1}
        if not example_row:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example_row, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review resource ownership, privilege boundaries, state transitions, and safe diagnostics before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: the Academy simulator executes arbitrary student commands on the production host.", ["True", "False"], "False", "The simulator uses isolated in-memory educational state."),
            ("Which boundary mediates privileged OS work?", ["A checked system-call boundary", "A hidden UI button", "An unvalidated filename"], "A checked system-call boundary", "The kernel validates and mediates privileged operations."),
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
