"""Additive 40-module Operating Systems curriculum.

This module is intentionally separate from the original vertical slice. It
reuses matching lesson rows by slug, never deletes lessons or progress, and
keeps newly created content in draft state until an administrator reviews it.
"""
import json
import re

from sqlalchemy import select

from .models import (
    CodeExample, CodingExercise, CourseModule, Lesson, LessonQuiz,
    ProjectCategory, ProjectMilestone, ProjectRequirement,
    ProjectRubricCriterion, ProjectTask, ProjectTemplate, QuizQuestion,
    SyntaxReference, SyntaxReferenceExample,
)


MODULES = [
    ("Introduction to Operating Systems", ["What an Operating System Does", "Types of Operating Systems", "Hardware Foundations for OS Work", "Kernel and User Space", "The Boot Process"]),
    ("Computer System Foundations", ["Binary, Hexadecimal, and Word Size", "CPU Modes and Registers", "Caches and the Memory Hierarchy", "Storage and Device Controllers", "System Measurement and Units"]),
    ("Linux Fundamentals", ["Filesystem Navigation", "Files, Directories, and File Descriptors", "Shell Pipelines and Exit Status", "Processes with ps and /proc", "Linux Permissions and Ownership"]),
    ("C for Systems Programming", ["Compiling and Linking C", "Pointers and Object Lifetime", "Dynamic Memory and Ownership", "Structs, Enums, and Invariants", "Debugging and Sanitizers"]),
    ("Processes and Execution", ["System Calls and OS APIs", "Processes and the Process Control Block", "First OS Investigation Workflow", "fork, exec, and wait", "Signals and Process Lifecycle"]),
    ("File Systems and Basic I/O", ["Read, Write, and Buffering", "Paths, Links, and Inodes", "Buffered and Memory-Mapped I/O", "Errors, Durability, and fsync", "Safe File I/O Lab"]),
    ("CPU Scheduling", ["Scheduling Goals and Metrics", "First-Come First-Served", "Round Robin", "Priority and Multilevel Queues", "CPU Scheduling Simulator"]),
    ("Threads and Concurrency", ["Thread Model and Shared State", "Mutexes and Critical Sections", "Condition Variables", "Atomics and Memory Ordering", "Multithreaded Task Queue"]),
    ("Memory Management", ["Address Spaces and Segments", "Paging and Page Tables", "Page Faults and Demand Paging", "Allocation Strategies", "Memory Allocation Simulator"]),
    ("File System Internals", ["File-System Layers", "Directories and Namespace Resolution", "Journaling and Crash Consistency", "Inodes, Extents, and Allocation", "File-System Explorer"]),
    ("IPC and Networking", ["Pipes and FIFOs", "Shared Memory", "Unix Domain Sockets", "TCP, UDP, and Socket Lifecycle", "IPC Communication Project"]),
    ("Linux System Administration", ["Users, Groups, and sudo", "Services and systemd Concepts", "Packages and Reproducible Environments", "Logs, Metrics, and Rotation", "Linux Administration Lab"]),
    ("Kernel Architecture", ["Kernel Subsystems and Boundaries", "System-Call Entry and Validation", "Kernel Data Structures", "Loadable Modules and Trust", "Kernel Architecture Lab"]),
    ("Interrupts and Device I/O", ["Interrupts and Exceptions", "Top Halves and Deferred Work", "Device Drivers and DMA", "Blocking, Polling, and Async I/O", "Device I/O Lab"]),
    ("Containers and Isolation", ["Namespaces and Process Views", "Control Groups and Resource Limits", "Container Images and Layering", "Container Capabilities and Filesystems", "Container Isolation Lab"]),
    ("Operating System Security", ["Threat Models for Operating Systems", "Access Control and Capabilities", "Memory and Execution Protections", "Secure Boot and Trust Chains", "OS Security Review"]),
    ("Performance Engineering", ["Profiling Before Optimization", "CPU and Context-Switch Cost", "Memory and Cache Performance", "I/O and Tail Latency", "Linux Performance Analyzer"]),
    ("Virtualization and Reliability", ["Virtual Machines and Hypervisors", "QEMU and Safe OS Experiments", "Fault Models and Recovery", "Replication and Durable State", "Reliability Engineering Lab"]),
    ("Advanced Kernel Concurrency", ["Kernel Locking Design", "RCU and Read-Mostly Data", "Wait-Free and Lock-Free Algorithms", "Priority Inversion and Real-Time Locks", "Kernel Concurrency Lab"]),
    ("Advanced Virtual Memory", ["Multi-Level Page Tables", "TLBs and Address Translation", "Page Replacement Algorithms", "Copy-on-Write and Fork", "Virtual Memory Lab"]),
    ("Storage Engineering", ["Disk and SSD Geometry", "Disk Scheduling", "RAID and Failure Domains", "Checksums and Data Integrity", "Storage Engineering Lab"]),
    ("System Security Engineering", ["Secure System Design", "Credential and Secret Handling", "Sandboxing and Syscall Policies", "Security Monitoring and Incident Response", "System Security Engineering Review"]),
    ("Systems Performance and Reliability", ["SLOs for Systems", "Tracing Cross-Layer Requests", "Capacity Planning", "Chaos and Failure Testing", "Performance and Reliability Capstone Review"]),
    ("OS Engineering Capstone", ["Capstone Scope and Architecture", "Capstone Kernel or Simulator Design", "Capstone Verification Plan", "Capstone Operations and Documentation", "OS Engineering Capstone Defense"]),
]

RETAINED = {
    "01-what-an-operating-system-does": (1, 1), "01-types-of-operating-systems": (1, 2),
    "01-hardware-foundations-for-os-work": (1, 3), "01-kernel-and-user-space": (1, 4),
    "01-the-boot-process": (1, 5), "01-system-calls-and-os-apis": (5, 1),
    "01-processes-and-the-process-control-block": (5, 2), "01-first-os-investigation-workflow": (5, 3),
}

PROJECTS = [
    ("Linux Process Inspector", "linux-process-inspector", "Read-only PID, state, memory, and open-resource reporting."),
    ("CPU Scheduling Simulator", "cpu-scheduling-simulator", "Trace FCFS, Round Robin, and priority scheduling with metrics."),
    ("Mini Unix Shell", "mini-unix-shell", "Build a bounded shell with parsing, pipes, redirection, and wait."),
    ("Multithreaded Task Queue", "multithreaded-task-queue", "Implement a pthread worker queue with backpressure and shutdown."),
    ("Memory Allocation Simulator", "memory-allocation-simulator", "Compare allocation policies with fragmentation and invariants."),
    ("IPC Communication Project", "ipc-communication-project", "Design a framed local IPC service with validation and timeouts."),
    ("File System Explorer", "file-system-explorer", "Inspect metadata and namespace boundaries without mutation."),
    ("Linux Performance Analyzer", "linux-performance-analyzer", "Collect bounded read-only counters and produce a regression report."),
    ("Container Isolation Lab", "container-isolation-lab", "Study namespaces, cgroups, capabilities, and teardown in a VM."),
    ("xv6 Kernel Engineering Capstone", "xv6-kernel-engineering-capstone", "Implement and defend an isolated xv6 kernel change with tests."),
]

# The original 24-module course remains intact. These sixteen modules extend it
# into the requested systems-engineering track without renumbering or deleting
# any existing lesson row, which keeps lesson-progress foreign keys valid.
MODULES.extend([
    ("Advanced File Systems", ["VFS and Mount Namespaces", "Copy-on-Write File Systems", "Log-Structured Storage", "Recovery and fsck", "Advanced File-System Lab"]),
    ("Device Drivers", ["Driver Model and Probes", "Character Devices", "Block Devices and Queues", "DMA and Memory Barriers", "Driver Safety Lab"]),
    ("Virtualization Engineering", ["Type-1 and Type-2 Hypervisors", "Hardware-Assisted Virtualization", "Virtual CPU Scheduling", "Virtual Device Models", "Virtualization Lab"]),
    ("Containers and Isolation Engineering", ["Rootless Containers", "User and Mount Namespaces", "Seccomp and Capability Sets", "Cgroup v2 Resource Policy", "Isolation Verification Lab"]),
    ("Operating System Security Engineering", ["Security Boundary Modeling", "MAC Policies and Labels", "Kernel Attack Surface", "Secure Update Pipelines", "Security Engineering Lab"]),
    ("Performance and Tracing", ["Sampling and Instrumentation", "perf and Flame Graphs", "eBPF Safety Model", "Latency Histograms", "Tracing Lab"]),
    ("OS Kernel Development", ["xv6 Source Tour", "System Call Extension", "Page Allocator Extension", "Scheduler Extension", "Kernel Patch Review"]),
    ("Advanced Scheduling", ["Fair Scheduling", "Real-Time Scheduling", "Work Conservation", "Admission Control", "Scheduling Research Lab"]),
    ("Memory Engineering", ["Allocator Design", "NUMA Locality", "Huge Pages", "Memory Pressure and Reclaim", "Memory Engineering Lab"]),
    ("Advanced Storage Engineering", ["Write Paths and FUA", "SSD Garbage Collection", "RAID Reconstruction", "End-to-End Integrity", "Storage Failure Lab"]),
    ("Systems Security Engineering", ["Threat Modeling a Host", "Privilege Separation", "Secrets and Key Rotation", "Incident Evidence Collection", "Host Security Review"]),
    ("Distributed Systems Foundations", ["Clocks and Ordering", "Consensus Concepts", "Replication and Quorums", "Failure Detectors", "Distributed Systems Lab"]),
    ("Real-Time and Embedded OS", ["Deadlines and Jitter", "Interrupt Latency", "RTOS Scheduling", "Embedded Memory Budgets", "Real-Time Lab"]),
    ("Production Linux Engineering", ["Boot Reliability", "Service Supervision", "Kernel and Package Lifecycle", "Capacity and On-Call Signals", "Production Readiness Lab"]),
    ("Reliability and Systems Testing", ["Invariants and Model Tests", "Fault Injection", "Load and Soak Testing", "Recovery Objectives", "Reliability Test Lab"]),
    ("Final Systems Engineering Capstone", ["Capstone Requirements", "Capstone Architecture", "Capstone Implementation", "Capstone Verification", "Capstone Defense"]),
])


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _profile(module_title: str, lesson_title: str, position: int):
    text = f"{module_title} {lesson_title}".lower()
    if "schedule" in text or "round robin" in text or "first-come" in text:
        language, example, expected = "python", "jobs = [(\"A\", 0, 5), (\"B\", 1, 2)]\n# produce a deterministic timeline", "A valid trace with waiting and turnaround metrics"
    elif "thread" in text or "mutex" in text or "atomic" in text or "concurrency" in text:
        language, example, expected = "c", "pthread_mutex_lock(&lock);\n/* update shared state */\npthread_mutex_unlock(&lock);", "The shared-state invariant remains true"
    elif "memory" in text or "paging" in text or "page" in text or "allocation" in text or "tlb" in text:
        language, example, expected = "text", "virtual address -> page table -> physical frame\npermission check -> access", "The trace reports translation, permission, and fault behavior"
    elif "file" in text or "storage" in text or "disk" in text or "inode" in text or "i/o" in text:
        language, example, expected = "bash", "stat sample\ndf -T\n# use a disposable directory for writes", "Metadata and storage observations are recorded without host mutation"
    elif "socket" in text or "network" in text or "ipc" in text or "pipe" in text:
        language, example, expected = "c", "socket(AF_UNIX, SOCK_STREAM, 0);\n/* validate length and peer before reading */", "A framed message is accepted or rejected deterministically"
    elif "container" in text or "namespace" in text or "qemu" in text or "virtual" in text:
        language, example, expected = "bash", "qemu-system-x86_64 -snapshot -m 512 -nographic\n# run only inside an isolated lab", "The disposable guest can be torn down without host changes"
    elif "c " in text or "pointer" in text or "compile" in text or "debug" in text:
        language, example, expected = "c", "cc -Wall -Wextra -std=c17 main.c -o main\n./main", "The compiler or sanitizer reports the observed result"
    else:
        language, example, expected = "bash", "uname -a\nps -eo pid,stat,comm\nfree -h", "The command output is captured with platform-specific details noted"
    focus = lesson_title.lower().rstrip(".")
    exercise = f"Create a small, reviewable experiment for {focus}. Define inputs, state transitions, expected behavior, one failure case, and cleanup. Use a disposable VM/emulator whenever the experiment can affect kernel, storage, device, or namespace state."
    answer = f"A validated, observable treatment of {focus}"
    return language, example, expected, exercise, answer


def _content(module_title, lesson_title, focus, language, example, expected, exercise, next_title):
    return f"""Introduction\n{lesson_title} develops practical understanding of {focus} within {module_title}.\n\nLearning objectives\n- Explain the abstraction, state, and ownership model behind {focus}.\n- Trace its kernel or systems boundary and identify a failure mode.\n- Verify behavior with a safe, reproducible observation.\n\nPrerequisites\nComplete the preceding lesson in this module, basic C or command-line work, and safe lab practice.\n\nDetailed theory\n{focus.capitalize()} is a contract between programs, the operating system, and hardware. A professional design names the resource owner, validates inputs at the boundary, preserves invariants, handles partial or failed operations, and emits enough evidence to diagnose a fault. The same concept can be simulated in memory before it is attempted in a disposable VM.\n\nArchitecture explanation\napplication -> API/system call -> kernel subsystem -> resource or device -> observable result\n\nTerminology\n- Boundary: where authority, validation, or trust changes.\n- Invariant: a property that must remain true across transitions.\n- Backpressure: limiting producers when consumers or resources are full.\n\nPractical demonstration ({language})\n```{language}\n{example}\n```\n\nExpected output\n{expected}. Exact identifiers and timings vary by platform; record actual output and environment instead of inventing results.\n\nStep-by-step explanation\n1. Define the resource, input, and safety boundary.\n2. Run the smallest deterministic or read-only example.\n3. Trace state, ownership, ordering, and permission checks.\n4. Compare observed behavior with the contract.\n5. Test one failure path and document cleanup.\n\nCommon mistakes\n- Assuming one Linux implementation or scheduler policy is universal.\n- Ignoring partial I/O, races, stale state, permissions, or resource limits.\n- Running privileged or destructive commands on a host OS.\n\nDebugging guidance\nCheck platform/version, arguments, permissions, resource state, logs, and the smallest reproducer. Use sanitizers for C, deterministic traces for simulators, and QEMU/xv6 or a disposable Linux VM for kernel and isolation labs.\n\nSecurity considerations\nDo not execute arbitrary student commands in the API process or modify the student's host operating system. Keep credentials out of code and logs. Use least privilege, bounded inputs, snapshots, and explicit teardown.\n\nExercise\n{exercise}\n\nHomework\nWrite an evidence report with architecture, assumptions, observed output, one failure case, and a rollback or cleanup plan.\n\nQuiz\nWhich practice makes this lesson trustworthy?\nOptions: validated, observable, isolated experiment; bypassing checks; relying on an unverified guess\nCorrect answer: validated, observable, isolated experiment\nExplanation: Systems results require a defined boundary, evidence, and safe recovery.\n\nKey takeaways\n- {focus.capitalize()} has a measurable contract and failure behavior.\n- Invariants, least privilege, and bounded resources reduce risk.\n- Reproducible evidence is more useful than an unsupported claim.\n\nNext lesson\n{next_title}\n"""


def _quiz(db, lesson, title, answer):
    quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
    if not quiz:
        quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the contract, boundary, and failure behavior before continuing.", status="draft")
        db.add(quiz)
        db.flush()
    if not db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == 1)):
        db.add(QuizQuestion(quiz_id=quiz.id, position=1, prompt=f"Which approach best demonstrates {title}?", question_type="multiple_choice", options_json=json.dumps([answer, "Skip validation and trust the input", "Change the host system first"]), correct_answer=answer, explanation="The first option is the safe, evidence-based systems approach."))


def _exercise(db, lesson, title, focus, language, exercise):
    slug = f"os-{_slug(title)}"
    if not db.scalar(select(CodingExercise).where(CodingExercise.slug == slug)):
        db.add(CodingExercise(lesson_id=lesson.id, title=f"{title} lab", slug=slug, description_en=exercise, description_mm=f"{title} ကို လုံခြုံသော lab ထဲတွင် လေ့ကျင့်ပါ။ {focus} ကို စစ်ဆေးပြီး cleanup လုပ်ပါ။", difficulty="intermediate", language=language if language in {"c", "bash", "python"} else "text", starter_code="", status="draft"))


def _syntax(db, course_id):
    refs = [("POSIX process APIs", "c"), ("POSIX file I/O", "c"), ("pthreads synchronization", "c"), ("Linux diagnostics", "bash"), ("QEMU and xv6 labs", "bash")]
    for order, (title, language) in enumerate(refs, 1):
        slug = f"os-{_slug(title)}"
        ref = db.scalar(select(SyntaxReference).where(SyntaxReference.course_id == course_id, SyntaxReference.slug == slug))
        if not ref:
            ref = SyntaxReference(course_id=course_id, title=title, slug=slug, category="Operating Systems", description=f"Five progressive {title} examples with safe execution notes.", basic_syntax=f"Review {title} with checked inputs and explicit cleanup.", when_to_use="Use in a bounded, reviewed systems experiment.", important_notes="Never run destructive examples against a host OS.", status="draft", display_order=order)
            db.add(ref)
            db.flush()
        for number in range(1, 6):
            if not db.scalar(select(SyntaxReferenceExample).where(SyntaxReferenceExample.reference_id == ref.id, SyntaxReferenceExample.example_number == number)):
                db.add(SyntaxReferenceExample(reference_id=ref.id, example_number=number, title=f"{title} example {number}", code=f"# Progressive example {number}\n# validate inputs; handle errors; record actual output", language=language, expected_output="Platform output varies; capture the real result.", explanation=f"Example {number} adds one carefully bounded concept while preserving validation and teardown."))


def _projects(db):
    category = db.scalar(select(ProjectCategory).where(ProjectCategory.slug == "operating-systems"))
    if not category:
        category = ProjectCategory(name="Operating Systems", slug="operating-systems", description="Safe systems-engineering projects", status="active")
        db.add(category)
        db.flush()
    for index, (title, slug, objective) in enumerate(PROJECTS, 1):
        project = db.scalar(select(ProjectTemplate).where(ProjectTemplate.slug == slug))
        if not project:
            project = ProjectTemplate(category_id=category.id, title=title, slug=slug, description_en=objective, description_mm=f"{title} ကို isolated VM သို့မဟုတ် emulator ထဲတွင် လုံခြုံစွာ တည်ဆောက်ပါ။", difficulty="advanced" if index > 6 else "intermediate", estimated_hours=16 + index * 2, requirements="C/POSIX or Bash as appropriate; no host OS mutation.", learning_outcomes="Design, implement, test, measure, document, and safely tear down a systems project.", technology_stack="C, POSIX, Bash, Linux VM, QEMU, xv6", prerequisites="C fundamentals, Linux command line, and safe lab practice.", architecture_overview=f"input -> validated boundary -> core state -> observable report -> cleanup ({objective})", folder_structure="src/  tests/  docs/  scripts/", testing_guide="Use deterministic tests, failure cases, bounded stress, and actual captured output.", deployment_guide="Run only in a disposable VM or emulator; destroy the environment after review.", tags_json=json.dumps(["operating-systems", "systems-engineering", "safe-lab"]), languages_json=json.dumps(["c", "bash"]), brief_json=json.dumps({"objective": objective}), status="draft", published=False)
            db.add(project)
            db.flush()
        for position, phase in enumerate(["Scope and architecture", "Implementation", "Testing and evidence", "Review and teardown"], 1):
            milestone = db.scalar(select(ProjectMilestone).where(ProjectMilestone.project_id == project.id, ProjectMilestone.position == position))
            if not milestone:
                milestone = ProjectMilestone(project_id=project.id, title=phase, slug=f"phase-{position}", description_en=f"{objective} — {phase}.", description_mm=f"{title} အဆင့် {position}။", content_en="Define requirements, interfaces, invariants, failure cases, and safe boundaries before implementation.", content_mm="Requirement၊ test၊ evidence နှင့် cleanup plan ကို မှတ်တမ်းတင်ပါ။", expected_output="Record actual output; do not invent results.", line_explanation="Explain ownership, validation, and failure behavior.", completion_criteria="A reviewer can reproduce the phase without host-system mutation.", position=position, required=True)
                db.add(milestone)
                db.flush()
                db.add(ProjectTask(milestone_id=milestone.id, title=f"Complete {phase.lower()}", description="Attach the design, test, or review evidence.", completion_criteria="Evidence is reproducible in an isolated environment.", position=1, required=True))
        for position, (name, weight) in enumerate([("Correctness", 35), ("Safety and security", 25), ("Testing evidence", 25), ("Documentation", 15)], 1):
            if not db.scalar(select(ProjectRubricCriterion).where(ProjectRubricCriterion.project_id == project.id, ProjectRubricCriterion.position == position)):
                db.add(ProjectRubricCriterion(project_id=project.id, name=name, description=f"Evidence for {name.lower()} in {title}.", weight=weight, position=position))


def seed_operating_systems_curriculum(db, course):
    """Complete the requested structure without deleting existing records."""
    course.title = "Operating Systems — From Zero to Advanced Systems Engineering"
    course.short_description = "A four-level, 40-module path from OS foundations to kernel, virtualization, security, performance, reliability, and systems engineering."
    course.description = "Learn processes, scheduling, concurrency, memory, filesystems, I/O, Linux administration, kernel architecture, containers, security, virtualization, performance, reliability, and an xv6 capstone. Advanced experiments use isolated VMs or emulators and never modify the student's host OS."
    course.target_audience = "Learners progressing from programming and Linux fundamentals to advanced systems engineering."
    course.technologies = "C|POSIX|Bash|Linux|pthreads|QEMU|xv6|system calls|sockets|filesystems"
    course.level = "beginner"
    course.duration_minutes = 40 * 5 * 50
    course.outcomes = "Explain OS abstractions, privilege boundaries, boot, system calls, processes, and threads|Simulate scheduling, synchronization, memory, paging, filesystems, and process states|Use safe Linux diagnostics and reason about security, isolation, virtualization, performance, and reliability|Design, test, document, and defend systems projects in isolated environments"
    course.requirements = "Basic programming, C foundations, and command-line familiarity. Advanced kernel, driver, storage, and container labs require a disposable Linux VM or QEMU/xv6 environment; no experiment should modify the host OS."
    existing = {lesson.slug: lesson for module in course.modules for lesson in module.lessons}
    modules = {}
    for module_position, (module_title, lesson_titles) in enumerate(MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_position))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_position)
            db.add(module)
            db.flush()
        module.title = module_title
        modules[module_position] = module
    db.flush()
    for slug, (module_position, lesson_position) in RETAINED.items():
        if slug in existing:
            existing[slug].module_id = modules[module_position].id
            existing[slug].order_index = lesson_position
    db.flush()
    for module_position, (module_title, lesson_titles) in enumerate(MODULES, 1):
        for lesson_position, title in enumerate(lesson_titles, 1):
            slug = f"{module_position:02d}-{_slug(title)}"
            lesson = existing.get(slug) or db.scalar(select(Lesson).where(Lesson.module_id == modules[module_position].id, Lesson.order_index == lesson_position))
            if not lesson:
                lesson = Lesson(module_id=modules[module_position].id, title=title, slug=slug, order_index=lesson_position, content_en="", content_mm="")
                db.add(lesson)
                db.flush()
            lesson.module_id = modules[module_position].id
            lesson.order_index = lesson_position
            language, example, expected, exercise, answer = _profile(module_title, title, lesson_position)
            if not lesson.content_en or not lesson.content_en.strip():
                next_title = lesson_titles[lesson_position] if lesson_position < 5 else ("Capstone complete" if module_position == 40 else MODULES[module_position][0])
                lesson.content_en = _content(module_title, title, title.lower(), language, example, expected, exercise, next_title)
                lesson.content_mm = f"{title}\n\nရည်ရွယ်ချက်\n{title} ကို systems engineering အမြင်ဖြင့် လေ့လာပါမည်။\n\nလေ့ကျင့်ခန်း\n{exercise}\n\nQuiz\nမှန်ကန်သောနည်းလမ်းမှာ validated၊ observable၊ isolated experiment ဖြစ်သည်။\n\nHost OS ကို မပြုပြင်ဘဲ VM/QEMU/xv6 ထဲတွင်သာ အဆင့်မြင့် lab များ ပြုလုပ်ပါ။"
                lesson.description = f"{title} — {module_title}"
                lesson.duration_minutes = 50
                lesson.status = "draft"
                lesson.published = False
            if not db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id)):
                suffix = "c" if language == "c" else "sh" if language == "bash" else "txt"
                db.add(CodeExample(lesson_id=lesson.id, title=f"{title} example", language=language, filename=f"{_slug(title)}.{suffix}", code=example, description=f"Safe example for {title}; capture actual output in an isolated environment.", position=1))
            additions = {
                "Terminology": f"Key terms: {title} names the resource, boundary, invariant, failure state, and cleanup action used in this lesson.",
                "Practical demonstration": f"Use the smallest safe {language} demonstration for {title}:\n```{language}\n{example}\n```\nCapture the actual output and tool versions; the seed does not claim this snippet was executed.",
                "Step-by-step explanation": "1. Define the resource and trust boundary. 2. Validate inputs. 3. Trace state and ownership. 4. Observe output and failure behavior. 5. Clean up temporary state.",
                "Debugging guidance": "Check the exact command, platform version, permissions, resource limits, logs, and the smallest reproducer. Use sanitizers for C, deterministic traces for simulations, and a disposable VM or emulator for privileged experiments.",
                "Security considerations": "Use least privilege, bounded inputs, redacted logs, snapshots, and explicit teardown. Never execute arbitrary student code in the API process or modify the host operating system.",
                "Syntax and command notes": f"Use the smallest valid syntax for {title}; validate arguments, handle errors, and preserve cleanup boundaries.",
                "Relevant algorithms": f"Trace {title} as a state machine. Compare FIFO with a fair or priority policy where applicable, and record queue length, service time, failures, invariants, and cleanup state.",
                "Expected output": f"Expected output: {expected}. Capture the actual platform output and environment.",
                "Practical lab": f"Objective: verify {title} in a repeatable lab. Record tool versions, run the smallest example, capture stdout/stderr, vary one input, verify the invariant, then remove temporary state or destroy the VM snapshot. Troubleshoot permissions, limits, logs, and the exact command before changing multiple variables.",
                "Common mistakes": "Avoid unvalidated input, partial-operation assumptions, unsafe privileges, missing cleanup, and conclusions based on a single run.",
                "Exercise": exercise,
                "Homework": "Write a short evidence report with the command or code, observed output, one failure case, and a safe rollback or cleanup plan.",
                "Best practices": "Prefer least privilege, deterministic inputs, bounded resources, explicit ownership, reproducible tests, and disposable environments for risky experiments.",
                "Quiz": "Question: which approach is trustworthy? Answer: a validated, observable, isolated experiment. Explanation: it defines a boundary, records evidence, and supports recovery.",
                "Answer explanation": "The safe answer defines the boundary, records evidence, preserves invariants, and leaves a recovery path; unsafe alternatives hide failures or create unnecessary risk.",
                "Key takeaways": f"{title} has a measurable contract, ownership rules, failure behavior, and a safe verification path.",
            }
            content = lesson.content_en or ""
            for marker, addition in additions.items():
                if marker.casefold() not in content.casefold():
                    content += f"\n\n{marker}\n{addition}"
            lesson.content_en = content
            mm_addition = "\n\nလေ့ကျင့်ခန်းနှင့် Quiz\nInput ကို validate လုပ်ပြီး actual output ကို မှတ်တမ်းတင်ပါ။ အဖြေများကို reviewer စစ်ဆေးပြီးမှ publish လုပ်ပါ။"
            if "လေ့ကျင့်ခန်းနှင့် Quiz" not in (lesson.content_mm or ""):
                lesson.content_mm = (lesson.content_mm or f"{title}\n") + mm_addition
            _quiz(db, lesson, title, answer)
            _exercise(db, lesson, title, title, language, exercise)
    _syntax(db, course.id)
    _projects(db)
    db.flush()
