"""Authored GitHub vertical slice for the idempotent catalog seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

PLANNED_MODULES = [
    "Introduction to GitHub", "GitHub Account & Profile", "Git & GitHub Installation",
    "GitHub Repository Fundamentals", "Repository Files & Documentation", "GitHub Authentication",
    "GitHub Branches", "Push, Pull, Fetch & Clone", "Pull Requests Fundamentals", "Code Reviews",
    "Merge Conflicts & Resolution", "Branch Protection & Rulesets", "GitHub Issues", "GitHub Projects",
    "GitHub Organizations", "Teams & Repository Permissions", "Forking & Open Source", "GitHub Discussions",
    "GitHub Templates", "GitHub Wiki & Documentation", "GitHub Actions Fundamentals", "Writing Workflow YAML",
    "CI Pipelines", "CD & Deployment Workflows", "Secrets & Variables", "Matrix Builds & Caching",
    "Reusable Workflows & Actions", "Self-Hosted Runners", "GitHub Security Fundamentals",
    "Dependabot & Dependency Security", "Code Scanning & Secret Scanning", "Supply Chain & Actions Security",
    "GitHub Releases & Tags", "GitHub Packages & Container Registry", "GitHub REST API & GraphQL",
    "GitHub CLI Automation", "GitHub Apps & Webhooks", "Enterprise Repository Management",
    "Real-World GitHub Projects", "Final GitHub Capstone",
]

MODULE_ONE = [
    ("What GitHub Adds to Git", "remote collaboration, visibility, and review", "git remote -v\ngit branch -M main\ngit push -u origin main", "terminal", "Git is the local version-control engine; GitHub is a hosted collaboration platform around repositories, pull requests, issues, reviews, permissions, and automation. A remote is a collaboration boundary, not a backup guarantee.", "Git သည် local version control ဖြစ်ပြီး GitHub သည် repository၊ pull request၊ issue၊ review၊ permission နှင့် automation တို့ကို ပေါင်းစပ်ထားသော collaboration platform ဖြစ်သည်။", "Draw the boundary between a local Git repository and a GitHub remote.", ("GitHub ၏ အဓိကအခန်းကဏ္ဍက ဘာလဲ?", ["Hosted collaboration around Git repositories", "A replacement for local commits", "A password vault"], "Hosted collaboration around Git repositories", "GitHub adds collaboration around Git.")),
    ("Create a Safe GitHub Profile", "profile identity, visibility, and account security", "gh auth status\ngh repo view\ngit config user.name\ngit config user.email", "terminal", "A professional profile should use a clear display identity, a protected email choice, two-factor authentication, and a reviewed public profile. The simulator does not connect to GitHub or store credentials.", "Profile တွင် display identity၊ protected email၊ 2FA နှင့် public information ကို စီမံပါ။ Simulator သည် GitHub သို့ မချိတ်ဆက်ပါ။", "Audit a fictional profile checklist and mark which fields are safe to make public.", ("ဘယ် credential ကို lesson ထဲ မထည့်သင့်သနည်း?", ["A real access token", "A public repository URL", "A display name"], "A real access token", "Tokens are secrets and need secure storage.")),
    ("Connect a Local Repository Safely", "remotes, authentication boundaries, and first push", "git remote add origin https://github.com/OWNER/REPO.git\ngit remote -v\ngit push -u origin main", "terminal", "A remote URL identifies where commits may be sent, while authentication decides whether the operation is allowed. Prefer credential managers or SSH agents, verify the owner and repository before pushing, and never embed tokens in URLs.", "Remote URL သည် commit ပို့မည့်နေရာကို သတ်မှတ်ပြီး authentication သည် ခွင့်ပြုချက်ကို စစ်သည်။ Credential manager သို့မဟုတ် SSH agent ကို သုံးပါ။", "Inspect a remote URL and explain why a token in a URL can leak into shell history.", ("Remote add လုပ်ပြီးနောက် ဘာကို verify လုပ်သင့်သနည်း?", ["Owner, repository, and authentication boundary", "A database password", "An arbitrary path"], "Owner, repository, and authentication boundary", "A wrong remote can publish code to an unintended repository.")),
    ("Repository README and Collaboration Contract", "documentation, visibility, and contribution expectations", "printf \"# Practice Project\\n\" > README.md\ngit add README.md\ngit commit -m \"Document practice project\"\ngit log --oneline", "terminal", "A README communicates purpose, setup, usage, license, and support boundaries. Contribution guides, code of conduct, and issue templates make collaboration predictable. Never include credentials or private data.", "README သည် project ရည်ရွယ်ချက်၊ setup၊ usage၊ license နှင့် support boundary ကို ဖော်ပြသည်။", "Draft a README outline with purpose, setup, usage, license, and disclosure guidance.", ("README တွင် ဘာကို မထည့်သင့်သနည်း?", ["Credentials and private data", "Setup commands", "Project purpose"], "Credentials and private data", "Documentation is public-facing content.")),
    ("Branches for Reviewable Changes", "feature branches and pull request boundaries", "git switch -c feature/readme\ngit status\ngit add README.md\ngit commit -m \"Improve project README\"\ngit push -u origin feature/readme", "terminal", "A feature branch isolates a focused change from the default branch. A pull request provides review, checks, discussion, and a merge decision. Do not use a shared branch for unreviewed experiments.", "Feature branch သည် default branch မှ change ကို ခွဲထားပြီး pull request သည် review၊ checks နှင့် merge decision ကို ပေးသည်။", "Create a fictional feature branch plan and list evidence reviewers need before merge.", ("Feature branch သုံးရခြင်း၏ အကြောင်းရင်းက ဘာလဲ?", ["To isolate a reviewable change", "To bypass checks", "To expose secrets"], "To isolate a reviewable change", "Branches separate work before review.")),
    ("Open and Understand a Pull Request", "changes, checks, review, and merge decisions", "git diff main...feature/readme\ngit log --oneline main..feature/readme\n# Open the pull request in GitHub UI", "terminal", "A pull request compares a source branch with a base branch. Reviewers inspect the diff, commit context, checks, and requested changes. A green check is evidence for configured checks only.", "Pull request သည် source branch နှင့် base branch ကို နှိုင်းယှဉ်သည်။ Reviewer သည် diff၊ commit context နှင့် checks ကို စစ်သည်။", "Write one correctness comment, one test request, and one documentation suggestion.", ("Pull request review သည် ဘာကို ပေးသနည်း?", ["A visible change and decision workflow", "Automatic code ownership", "Secret storage"], "A visible change and decision workflow", "Pull requests make proposed changes explicit.")),
    ("Checks, Permissions, and Protected Branches", "repository rules, least privilege, and merge gates", "git status\n# Example policy: require review, passing checks, and no force pushes\n# Review repository settings before enabling a rule", "terminal", "Branch protection and rulesets turn team expectations into enforceable merge gates. Require appropriate reviews and passing checks. Workflow permissions should be least privilege; untrusted pull requests must not receive privileged secrets.", "Branch protection သည် team expectation များကို merge gate အဖြစ် enforce လုပ်သည်။ Review နှင့် least-privilege permissions ကို သတ်မှတ်ပါ။", "Design a protection policy for main and identify quality versus security rules.", ("Least privilege ဆိုသည်မှာ ဘာလဲ?", ["Grant only needed permissions", "Give every workflow admin access", "Publish all secrets"], "Grant only needed permissions", "Smaller permission scope limits impact.")),
    ("First GitHub Actions Workflow", "workflow YAML, checks, and safe automation", "mkdir -p .github/workflows\n# Add reviewed workflow YAML\n# Open a pull request and inspect the check result", "yaml", "GitHub Actions workflows describe events, jobs, steps, runners, and permissions in YAML. Start with a small test check, pin third-party actions to reviewed immutable SHAs in production, and keep secrets out of logs. A simulator is not a real Actions run.", "GitHub Actions workflow သည် event၊ job၊ step၊ runner နှင့် permission များကို YAML ဖြင့် ဖော်ပြသည်။ Third-party action ကို reviewed SHA ဖြင့် pin လုပ်ပါ။", "Write a workflow outline for a Python test job and annotate its trigger, permissions, and secret boundary.", ("Production workflow တွင် ဘာကို pin လုပ်သင့်သနည်း?", ["Reviewed immutable action commit SHAs", "Random latest tags", "Real tokens in YAML"], "Reviewed immutable action commit SHAs", "Immutable references are reviewable and reproducible.")),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(position: int, item: tuple) -> str:
    title, topic, commands, filename, theory, mm, exercise, question_data = item
    note = "Use placeholders only. The Academy does not connect to GitHub, execute commands, or modify repositories."
    question, options, answer, explanation = question_data
    previous = "No GitHub experience is required; basic Git is helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: complete the first GitHub repository lab and review the Module 1 assessment."
    return f"""Introduction
{title} introduces {topic} through a safe, review-first GitHub workflow.

Learning objectives
- Explain {topic} in your own words.
- Distinguish local Git state from GitHub-hosted state.
- Identify authentication, permission, secret, and review boundaries.

Prerequisites
{previous}

GitHub workflow explanation
local repository -> remote repository -> pull request -> checks/review -> protected merge

Detailed theory
{theory}

Step-by-step instructions
{commands}

Repository structure
project/
  .git/
  .github/workflows/
  README.md
  src/

Expected results
The exact result depends on account permissions and repository settings. Verify each state in the local repository or GitHub UI.

Command explanation
Identify whether each command changes local files, Git history, a remote repository, or only displays information. Use an isolated practice repository.

Common errors
- Using the wrong repository owner or remote URL.
- Storing a token in a URL, shell history, or workflow file.
- Opening a pull request from the wrong base branch.
- Assuming checks replace human review.

Troubleshooting
Start with git remote -v, git status, branch names, repository visibility, and the authenticated account. Preserve evidence before changing remotes or rewriting history.

Best practices
- Use protected default branches, focused pull requests, and least-privilege permissions.
- Review diffs, workflow permissions, and third-party actions before merge.
- Use credential managers or SSH agents; never commit secrets.

Security considerations
Never expose GitHub tokens, SSH private keys, recovery codes, or production secrets. Do not grant privileged secrets to untrusted pull-request code.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Design a disposable GitHub collaboration workflow with a README, feature branch, pull request, required check, and protected default branch. Use placeholders only.

Summary
You can now reason about {topic} as explicit local, remote, review, and permission state transitions.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
{note}
"""

def seed_github_course(db, course):
    course.title = "GitHub & Collaborative Development — From Zero to Professional"
    course.short_description = "A free, practical path from GitHub fundamentals to secure collaboration, reviews, and Actions workflows."
    course.description = "Learn GitHub repositories, authentication, branches, pull requests, reviews, issues, permissions, Actions, security, releases, APIs, and professional team workflows through safe examples."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 35
    course.outcomes = "Use GitHub repositories, branches, pull requests, reviews, and protected merges|Design secure Actions workflows with least-privilege permissions|Collaborate with issues, projects, releases, and open-source workflows|Recognize credential, runner, dependency, and supply-chain risks"
    course.requirements = "Basic Git and terminal usage are helpful; no prior GitHub administration experience is required."
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
        values = {"title": f"{title} example", "language": "yaml" if item[3] == "yaml" else "bash", "filename": item[3], "code": item[2], "description": "Read-only GitHub example. Use placeholders and an isolated repository; the Academy does not execute commands or modify GitHub.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review local/remote and permission boundaries before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [(item[7][0], item[7][1], item[7][2], item[7][3]), ("True or false: the Academy executes arbitrary GitHub commands or changes repositories.", ["True", "False"], "False", "The examples and simulator are read-only and in-memory."), ("Which practice protects a GitHub workflow?", ["Use least privilege and review changes before merge", "Commit access tokens to YAML", "Give every workflow admin permissions"], "Use least privilege and review changes before merge", "Review, protected branches, and scoped credentials reduce risk.")]
        for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
            row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
            values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
            if not row:
                db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
            else:
                for key, value in values.items():
                    setattr(row, key, value)
    db.flush()
