"""Authored Git vertical slice for the idempotent catalog seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion


PLANNED_MODULES = [
    "Introduction to Version Control", "Git Installation & Configuration", "Command Line Fundamentals", "Git Repository Fundamentals",
    "Working Directory & Staging Area", "Your First Git Commit", "Tracking Files & Changes", "Git Commit History", "Ignoring Files",
    "Undoing Local Changes", "Git Branch Fundamentals", "Git Merge Fundamentals", "GitHub Fundamentals", "Remote Repositories",
    "Git Authentication", "Pull Requests", "Code Reviews & Collaboration", "Merge Conflicts", "Git Rebase", "Interactive Rebase",
    "Cherry-Pick", "Git Stash", "Git Tags & Releases", "Git Reflog & Recovery", "Git Bisect", "Git Worktrees", "Git Internals",
    "Advanced History & Inspection", "Git Hooks", "Git Security Best Practices", "Git LFS & Large Files", "Submodules & Monorepos",
    "GitHub Actions & CI/CD", "Branching Strategies", "Team Collaboration Workflows", "Advanced Conflict Resolution", "Git Troubleshooting",
    "Repository Maintenance & Performance", "Real-World Git Projects", "Final Git Capstone & Assessment",
]

MODULE_ONE = [
    ("What Version Control Solves", "snapshots, collaboration, review, and recoverable history", "git init\ngit status\ngit add README.md\ngit commit -m \"Add project README\"", "terminal", "Version control records intentional snapshots of a project so changes can be reviewed, shared, compared, and recovered. Git stores content locally and lets teams exchange commits through remotes. A commit is not a backup by itself: use reliable remotes, access controls, and a recovery process. Never commit credentials or personal data.", "Version control သည် project ၏ intentional snapshot များကို သိမ်းပြီး change review၊ collaboration နှင့် recovery ကို ကူညီသည်။ Commit တစ်ခုတည်းသည် backup မဟုတ်သောကြောင့် remote၊ access control နှင့် recovery process လိုအပ်သည်။", "Draw a timeline with three commits and identify which change each snapshot makes recoverable.", ("Git ၏ အဓိကအကျိုးကျေးဇူးက ဘာလဲ?", ["Reviewable and recoverable project history", "Running a production database", "Hiding credentials"], "Reviewable and recoverable project history", "Git records project snapshots and relationships between them."), "Examples use isolated repositories and never execute commands on the Academy host."),
    ("Install and Configure Git Safely", "Git identity, defaults, editors, and credential boundaries", "git --version\ngit config --global user.name \"Your Name\"\ngit config --global user.email \"you@example.com\"\ngit config --global init.defaultBranch main\ngit config --list --show-origin", "terminal", "Install Git from the official distribution for your operating system. Configure an author identity that is appropriate for commits, but do not store access tokens in Git config or paste credentials into command history. Credential managers, SSH agents, and protected CI secrets are safer than plaintext tokens.", "OS အလိုက် official Git package ကို install လုပ်ပါ။ Commit author identity ကို configure လုပ်နိုင်သော်လည်း access token များကို Git config သို့မဟုတ် shell history ထဲ မထည့်ပါနှင့်။ Credential manager နှင့် SSH agent ကို သုံးပါ။", "Configure a local identity, inspect where each value comes from, and explain why a public email may be preferable for a shared repository.", ("Git config ထဲတွင် ဘာကို မသိမ်းသင့်သနည်း?", ["Long-lived access tokens", "A commit author name", "The default branch name"], "Long-lived access tokens", "Tokens in config files or history can be exposed and reused."), "Use dummy identity values in practice and never use a real token for a lesson."),
    ("Command Line Fundamentals for Git", "working directories, paths, exit status, and safe inspection", "pwd\nls\nmkdir git-learning\ncd git-learning\nprintf \"hello\\n\" > README.md\ncat README.md\ngit status", "terminal", "Git commands run against the current working directory and its repository. Learn to inspect before mutating: pwd, ls, git status, git diff, and git log provide evidence. Shell redirection and deletion can affect files immediately, so practice in a disposable folder and understand the command before running it.", "Git command များသည် current working directory နှင့် repository အပေါ် သက်ရောက်သည်။ Mutate မလုပ်မီ pwd၊ ls၊ git status၊ git diff နှင့် git log ဖြင့် inspect လုပ်ပါ။ Disposable folder ထဲတွင်သာ လေ့ကျင့်ပါ။", "Create a disposable directory, add a README, and record the output of pwd and git status before and after initialization.", ("Git mutation မလုပ်မီ ဘာကို အရင်စစ်သင့်သနည်း?", ["Current path and git status", "A production directory blindly", "A secret token"], "Current path and git status", "Inspection reduces accidental changes in the wrong repository."), "The Academy simulator does not access the host filesystem or run shell commands."),
    ("Create a Repository with git init", "the .git directory, repository scope, and safe initialization", "mkdir notes-repo\ncd notes-repo\ngit init\ngit status\nls -la", "terminal", "git init creates repository metadata in .git while leaving your working files unchanged. The .git directory contains objects, references, configuration, and index data; do not edit it casually. Confirm the repository root before running commands, especially inside nested projects.", "git init သည် .git metadata folder ကို ဖန်တီးပြီး working file များကို မပြောင်းလဲပါ။ .git ထဲတွင် object၊ ref၊ config နှင့် index data များရှိသဖြင့် တိုက်ရိုက်မပြင်ပါနှင့်။", "Initialize a disposable repository, identify the repository root with git rev-parse --show-toplevel, and inspect status.", ("git init သည် ဘာကိုဖန်တီးသနည်း?", ["A .git repository metadata directory", "A remote GitHub repository automatically", "A production backup"], "A .git repository metadata directory", "Initialization creates local repository metadata; it does not create a remote."), "Do not initialize inside a parent directory that contains unrelated private files."),
    ("Working Tree, Staging Area, and Repository", "the three Git states and the index", "printf \"first\\n\" > notes.txt\ngit status\ngit add notes.txt\ngit status\ngit diff --cached", "terminal", "The working tree is the files you edit. The staging area, or index, is the proposed next snapshot. The repository stores committed objects. git add copies the current file content into the index; it does not commit. Review staged changes with git diff --cached before committing.", "Working tree သည် edit လုပ်သော file များ၊ staging area သည် နောက် commit အတွက် ပြင်ဆင်ထားသော snapshot၊ repository သည် committed object များ ဖြစ်သည်။ git add သည် index သို့ copy လုပ်ပြီး commit မလုပ်သေးပါ။", "Change a file after staging it, then compare git diff with git diff --cached and explain why they differ.", ("Staging area ၏ အခန်းကဏ္ဍက ဘာလဲ?", ["Proposed next commit snapshot", "A remote server", "A password vault"], "Proposed next commit snapshot", "The index lets you select and review exactly what the next commit contains."), "Review staged content before committing; it can contain secrets accidentally added from the working tree."),
    ("Make Your First Commit", "commit snapshots, messages, and identity", "printf \"# Git Notes\\n\" > README.md\ngit add README.md\ngit commit -m \"Add notes README\"\ngit status\ngit log --oneline", "terminal", "A commit records the staged snapshot with an author, timestamp, parent relationship, and message. Good messages describe the intent of the change. A clean status after commit means the working tree and index match the latest commit, not that the project is tested or secure.", "Commit သည် staged snapshot ကို author၊ timestamp၊ parent နှင့် message ပါအောင် သိမ်းသည်။ Commit message သည် change intent ကို ဖော်ပြသင့်သည်။ Clean status သည် test အောင်မြင်သည်ဟု မဆိုလိုပါ။", "Create one focused commit, inspect its short log, then change the README without committing and observe status.", ("Commit ထဲတွင် ဘာပါဝင်သနည်း?", ["A staged snapshot and metadata", "Only a remote URL", "A live server process"], "A staged snapshot and metadata", "Commits point to content and carry authorship and parent metadata."), "Never commit passwords, private keys, .env files, or generated credentials."),
    ("Inspect History and Differences", "log, show, diff, and evidence-driven review", "git log --oneline --decorate --graph\ngit show --stat HEAD\nprintf \"second\\n\" >> README.md\ngit diff\ngit diff --check", "terminal", "History is a review tool. git log shows commit relationships, git show explains one commit, git diff compares working content, and git diff --check catches whitespace errors. Read changes before sharing or merging; a green command does not prove the behavior is correct.", "git log သည် history နှင့် commit relationship ကိုပြသည်။ git show သည် commit တစ်ခုကို ဖော်ပြပြီး git diff သည် working change ကို ပြသည်။ Share/merge မလုပ်မီ diff ကို အမြဲဖတ်ပါ။", "Make one intentional README change, inspect both unstaged and committed differences, and record the review conclusion.", ("Working tree change ကို စစ်ရန် ဘာသုံးသနည်း?", ["git diff", "git push --force", "git clean -x blindly"], "git diff", "git diff compares working tree changes that are not staged."), "Do not paste sensitive diff output into public issues or logs."),
    ("Ignore Files and Build a Safe First Workflow", "gitignore, clean commits, and a complete local workflow", "printf \".env\\n.venv/\\n__pycache__/\\nnode_modules/\\n\" > .gitignore\ngit add .gitignore README.md\ngit diff --cached\ngit commit -m \"Add project hygiene files\"\ngit status", "terminal", "A .gitignore prevents common generated files and local secrets from being proposed for commits, but it is not a security control for data already tracked. The first safe workflow is inspect, edit, review diff, stage intentionally, review staged diff, commit clearly, and verify status. Push only to a remote you trust.", ".gitignore သည် generated file နှင့် local secret များကို commit proposal ထဲ မပါအောင် ကူညီသော်လည်း tracked ဖြစ်ပြီးသား secret ကို မဖျက်ပေးနိုင်ပါ။ Safe workflow မှာ inspect၊ edit၊ diff review၊ intentional stage၊ staged diff review၊ commit နှင့် status verify ပါဝင်သည်။", "Create a .gitignore for your language, verify that a local .env is not shown as an untracked file, and explain how to rotate a secret that was already committed.", (".gitignore မည်သည့်အရာကို မဖြေရှင်းနိုင်သနည်း?", ["A secret already committed to history", "An untracked .env file", "A generated build directory"], "A secret already committed to history", "Removing a path from future commits does not erase old reachable history or rotate the secret."), "If a secret is committed, revoke/rotate it first and use a reviewed history-removal procedure; avoid casual force pushes on shared branches."),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, commands, filename, theory, mm, exercise, question_data, note = item
    question, options, answer, explanation = question_data
    previous = "No Git experience is required; terminal familiarity is helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: complete the first repository lab and review the Module 1 assessment."
    return f"""Introduction
{title} introduces {topic} through an isolated, review-first Git workflow.

Learning objectives
- Explain {topic} in your own words.
- Predict the effect of each command before running it.
- Identify destructive, secret, and collaboration boundaries.

Prerequisites
{previous}

Git workflow explanation
Working tree → staging area/index → commit history → trusted remote

Detailed theory
{theory}

Step-by-step commands
```bash
{commands}
```

Repository structure
```text
project/
├── .git/       # repository metadata; do not edit casually
├── .gitignore
└── README.md
```

Expected output
The exact output depends on your Git version and local files. Verify the stated state transition with `git status`, `git diff`, or `git log` rather than copying an unverified output.

Command explanation
Read each command before executing it: identify its repository scope, whether it mutates working files/index/history, and whether it can expose or delete data. Use isolated practice repositories.

Common errors
- Running a command in the wrong repository or outside a repository.
- Staging more files than intended or confusing unstaged and staged diff.
- Assuming .gitignore removes a secret already committed.
- Rewriting shared history or force pushing without a reviewed recovery plan.

Troubleshooting
Start with `pwd`, `git rev-parse --show-toplevel`, `git status`, and the relevant diff. Preserve evidence before reset/clean operations. Never run broad destructive commands in a shared or production checkout.

Best practices
- Make small focused commits with clear intent and review staged content.
- Keep secrets out of history, use credential managers, and protect shared branches.
- Prefer revert for shared history; treat reset, rebase, and force push as deliberate operations.

Security considerations
Do not commit tokens, private keys, .env files, or personal data. Rotate leaked credentials immediately, use least-privilege access, verify remotes, and avoid copying sensitive diffs into public channels.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}

Mini project
Create an isolated repository with a README, .gitignore, and three focused commits. Capture status, staged diff, graph, and a short recovery note. Do not use real credentials or push the practice repository to a shared remote.

Summary
You can now reason about {topic} as a sequence of reviewable repository state transitions.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
{note}
"""


def seed_git_course(db, course):
    course.title = "Git & Version Control — From Zero to Professional"
    course.short_description = "A free, practical path from Git fundamentals to safe team workflows and advanced history recovery."
    course.description = "Learn Git repositories, staging, commits, branches, merges, remotes, pull requests, rebases, recovery, hooks, security, CI/CD, and professional collaboration workflows through safe examples."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 35
    course.outcomes = "Understand Git's working tree, index, objects, and commit graph|Create reviewable commits and collaborate through branches and remotes|Recover safely with history inspection and reflog concepts|Apply secure GitHub, review, branching, and CI/CD workflows"
    course.requirements = "Basic terminal usage and a text editor; no previous Git experience is required."

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
        values = {"title": f"{title} example", "language": "bash", "filename": item[3], "code": item[2], "description": "Read-only Git example. Run only in an isolated local repository; the Academy does not execute commands on its host.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)

        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the repository state transitions and retry after explaining the safety boundary.", status="published")
            db.add(quiz)
            db.flush()
        questions = [(item[7][0], item[7][1], item[7][2], item[7][3]), ("True or false: the Academy runs arbitrary Git commands on its application host.", ["True", "False"], "False", "Examples are displayed as read-only learning content."), ("Which practice protects a Git repository?", ["Review staged changes and keep secrets out of history", "Force push shared branches by default", "Commit access tokens for convenience"], "Review staged changes and keep secrets out of history", "Git safety depends on review, protected credentials, and deliberate history operations.")]
        for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
            question_row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
            values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
            if not question_row:
                db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
            else:
                for key, value in values.items():
                    setattr(question_row, key, value)
    db.flush()

