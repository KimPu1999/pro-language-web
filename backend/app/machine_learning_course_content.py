"""Authored Machine Learning vertical slice for the idempotent catalog seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion
from .machine_learning_complete_curriculum import _ensure_exercise, seed_machine_learning_additional_curriculum

PLANNED_MODULES = [
    "Introduction to Machine Learning", "Python for Machine Learning", "Development Environment & Tools", "Mathematics for ML",
    "Probability & Statistics", "NumPy Fundamentals", "Pandas & DataFrames", "Data Visualization", "Machine Learning Workflow",
    "Data Collection & Datasets", "Exploratory Data Analysis", "Data Cleaning & Preprocessing", "Feature Engineering",
    "Train, Validation & Test Splits", "Supervised Learning Fundamentals", "Linear Regression", "Multiple & Polynomial Regression",
    "Logistic Regression", "K-Nearest Neighbors", "Decision Trees", "Random Forest & Ensemble Learning", "Gradient Boosting",
    "Support Vector Machines", "Naive Bayes", "Clustering Algorithms", "Dimensionality Reduction", "Anomaly Detection",
    "Model Evaluation & Metrics", "Hyperparameter Tuning", "Pipelines & Reproducibility", "Neural Network Fundamentals",
    "Deep Learning with PyTorch", "Computer Vision Fundamentals", "Natural Language Processing", "Time Series Forecasting",
    "Responsible ML & Explainability", "Model Deployment & APIs", "MLOps & Model Monitoring",
    "Professional Machine Learning Projects", "Final Machine Learning Capstone",
]

MODULE_ONE = [
    ("What Machine Learning Is", "patterns, data, models, and evidence-based predictions", "python --version\npython -c \"print('ML workflow: data -> model -> evaluation')\"", "terminal", "Machine learning uses data and an objective to fit a model that can make predictions or decisions. A model is not automatically intelligent or correct: its data, target, evaluation, assumptions, and deployment context must be inspected. Separate training evidence from unseen evaluation evidence.", "Machine Learning သည် data နှင့် objective ကို သုံးပြီး prediction/decision ပြုလုပ်နိုင်သော model ကို fit လုပ်သည်။ Model သည် အလိုအလျောက် မှန်ကန်ခြင်းမဟုတ်သောကြောင့် data၊ target၊ evaluation နှင့် deployment context ကို စစ်ရသည်။", "Draw the loop data -> training -> evaluation -> deployment and label where leakage can occur.", ("Machine Learning model သည် ဘာလုပ်သနည်း?", ["Learns patterns from data for a defined task", "Guarantees unbiased truth", "Replaces all human review"], "Learns patterns from data for a defined task", "A model estimates patterns for a defined objective and evidence must be evaluated.")),
    ("Python Environment for Reproducible ML", "virtual environments, packages, notebooks, and versions", "python -m venv .venv\nsource .venv/bin/activate\npython -m pip install numpy pandas scikit-learn\npython -c \"import numpy, pandas, sklearn; print('ready')\"", "terminal", "Use an isolated Python environment and record package versions for reproducibility. Notebooks are useful for exploration, while scripts and tests make pipelines repeatable. Do not install unknown packages or place credentials in notebooks.", "Python ML အတွက် isolated virtual environment သုံးပြီး package version များကို မှတ်တမ်းတင်ပါ။ Notebook သည် exploration အတွက်ကောင်းသော်လည်း script/test က repeatable ဖြစ်စေသည်။", "Create an environment checklist with Python version, package lock, dataset source, and random seed.", ("Reproducible ML setup တွင် ဘာပါဝင်သနည်း?", ["Isolated environment, pinned dependencies, and documented data", "A random notebook only", "A production credential"], "Isolated environment, pinned dependencies, and documented data", "Reproducibility depends on tools, data, and documented choices.")),
    ("The ML Workflow", "problem framing, features, labels, training, and evaluation", "python -c \"steps=['frame','collect','split','train','evaluate','deploy']; print(' -> '.join(steps))\"", "terminal", "A reliable workflow begins with a measurable problem and target. Features are inputs, labels are target outcomes, training fits parameters, validation supports choices, and a final test estimates generalization. Deployment adds monitoring and rollback responsibilities.", "Workflow သည် problem framing မှ စပြီး data၊ split၊ train၊ evaluate နှင့် deploy အဆင့်များပါဝင်သည်။ Feature သည် input၊ label သည် target ဖြစ်သည်။", "For a support-ticket classifier, identify features, label, cost of false positives, and a validation plan.", ("Test set ၏ ရည်ရွယ်ချက်က ဘာလဲ?", ["Estimate performance on unseen data", "Tune every hyperparameter repeatedly", "Store secrets"], "Estimate performance on unseen data", "A held-out test estimates generalization when used once at the end.")),
    ("Features, Labels, and Dataset Contracts", "tabular rows, targets, leakage, and data documentation", "python -c \"row={'hours_studied':4,'practice_quizzes':3,'passed':True}; print(row)\"", "terminal", "A dataset contract documents row meaning, feature types, target definition, missing values, collection time, license, and intended use. Leakage occurs when training data contains information unavailable at prediction time. Sensitive attributes require careful governance and should not be collected casually.", "Dataset contract တွင် row meaning၊ feature type၊ target၊ missing value၊ collection time နှင့် license ကို မှတ်တမ်းတင်ရသည်။ Prediction time တွင် မရနိုင်သော information ပါပါက leakage ဖြစ်နိုင်သည်။", "Write a dataset card for a small synthetic student-outcome dataset and identify one possible leakage field.", ("Data leakage ဆိုသည်မှာ ဘာလဲ?", ["Using information unavailable at prediction time during training", "Missing a chart title", "Using a virtual environment"], "Using information unavailable at prediction time during training", "Leakage makes evaluation falsely optimistic.")),
    ("NumPy Arrays and Vectorized Computation", "numeric arrays, shapes, and deterministic transformations", "python -c \"import numpy as np; x=np.array([1,2,3]); print(x.mean(), x * 2)\"", "python", "NumPy arrays provide efficient numeric operations with explicit shape and dtype concepts. Vectorized operations reduce accidental loops, but shape assumptions must be checked. Random operations should use a documented seed when reproducibility matters.", "NumPy array သည် numeric computation အတွက် efficient ဖြစ်ပြီး shape/dtype ကို စစ်ရသည်။ Random operation တွင် seed သုံးပါ။", "Predict the shape and mean of a small array and document its dtype.", ("Array computation မလုပ်မီ ဘာကို စစ်သင့်သနည်း?", ["Shape, dtype, and missing-value assumptions", "A secret token", "A random production file"], "Shape, dtype, and missing-value assumptions", "Shape and dtype determine whether transformations are valid.")),
    ("Pandas DataFrames and Inspection", "rows, columns, missing values, and data profiles", "python -c \"import pandas as pd; df=pd.DataFrame({'score':[80,90,None]}); print(df.head()); print(df.isna().sum())\"", "python", "Pandas DataFrames represent labeled tabular data. Inspect head, shape, dtypes, missingness, duplicates, and summary statistics before modeling. Data previews can contain sensitive information, so use synthetic or approved samples.", "Pandas DataFrame သည် labeled tabular data ကို ကိုယ်စားပြုသည်။ Modeling မလုပ်မီ head၊ shape၊ dtype၊ missingness နှင့် duplicate ကို စစ်ပါ။", "Profile a synthetic DataFrame and decide whether missing values should be removed or imputed.", ("Modeling မလုပ်မီ ဘာကို inspect လုပ်သင့်သနည်း?", ["Shape, dtypes, missingness, and duplicates", "Only the last row", "A private credential"], "Shape, dtypes, missingness, and duplicates", "Inspection reveals data quality and contract problems.")),
    ("Train/Test Splitting and Evaluation", "generalization, leakage prevention, and baseline metrics", "python -c \"from sklearn.model_selection import train_test_split; X=[1,2,3,4]; y=[0,0,1,1]; print(train_test_split(X,y,test_size=.5,random_state=42))\"", "python", "Split data before fitting preprocessing or models when possible. A baseline gives context, while metrics must match the task and cost of errors. Do not tune against the final test set or report a single score without context.", "Data split ကို preprocessing/model fit မလုပ်မီ ပြုလုပ်ပြီး baseline နှင့် task-appropriate metric ကို သုံးပါ။ Final test ကို tuning အတွက် မသုံးပါနှင့်။", "Design a split and metric plan for an imbalanced binary classifier.", ("Final test set ကို ဘာအတွက်သုံးသနည်း?", ["A final generalization estimate", "Unlimited hyperparameter tuning", "Storing labels publicly"], "A final generalization estimate", "The final test should be held out from iterative decisions.")),
    ("Responsible ML and the First Reproducible Workflow", "fairness, privacy, reproducibility, and model review", "python -c \"seed=42; print(f'reproducible baseline seed={seed}')\"\n# Record data source, license, metrics, and limitations", "python", "Responsible ML includes privacy, consent, data license, representative evaluation, subgroup analysis, explainability, human oversight, and a rollback plan. Reproducibility requires a data/version contract, seeds, code, metrics, and documented limitations.", "Responsible ML တွင် privacy၊ consent၊ license၊ subgroup evaluation၊ explainability နှင့် human oversight ပါဝင်သည်။ Reproducibility အတွက် seed၊ code၊ metric နှင့် limitation ကို မှတ်တမ်းတင်ပါ။", "Create a model card outline with intended use, data source, metric, subgroup limitations, and rollback owner.", ("Responsible ML workflow တွင် ဘာကို documentation လုပ်သင့်သနည်း?", ["Data provenance, intended use, metrics, limitations, and review", "Only the best score", "Private user records"], "Data provenance, intended use, metrics, limitations, and review", "Documentation makes model risk and evidence visible.")),
]

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(position: int, item: tuple) -> str:
    title, topic, commands, filename, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    previous = "No ML experience is required; basic Python is helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: complete the first ML model lab and review the Module 1 assessment."
    return f"""Introduction
{title} introduces {topic} through reproducible, evidence-based ML practice.

Learning objectives
- Explain {topic} in your own words.
- Identify data, target, evaluation, and reproducibility boundaries.
- Recognize leakage, privacy, fairness, and deployment risks.

Prerequisites
{previous}

Machine learning architecture explanation
problem -> dataset -> features/labels -> split -> preprocessing/model -> evaluation -> monitored deployment

Detailed theory
{theory}

Mathematical intuition
Training estimates parameters that reduce a defined loss on training data; evaluation estimates how well the resulting function generalizes to unseen data. A metric is evidence, not a guarantee.

Python and step-by-step examples
{commands}

Dataset description
Use the included synthetic examples only. Record source, license, columns, target, missing-value policy, and intended use for any real dataset.

Expected output
Exact output depends on Python and package versions. Verify shapes, metrics, and assumptions instead of copying an unverified result.

Code explanation
Inspect inputs and shapes, set seeds where appropriate, separate training from evaluation, and explain each transformation. Never execute arbitrary student code on the Academy host.

Common errors
- Data leakage between preprocessing and test data.
- Confusing classification and regression metrics.
- Ignoring missing values, imbalance, or subgroup performance.
- Treating a high score as proof of safe deployment.

Troubleshooting
Check Python/package versions, array shapes, dtypes, missingness, split sizes, warnings, and the smallest reproducible example. Preserve the dataset and metric context before changing code.

Best practices
- Use pipelines, deterministic seeds, baselines, cross-validation, and documented model cards.
- Keep private data out of notebooks and logs.
- Report uncertainty, limitations, subgroup behavior, and rollback criteria.

Responsible ML considerations
Review consent, license, privacy, fairness, representativeness, explainability, human oversight, and misuse risk before using a dataset or model.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Build a reproducible baseline using a synthetic dataset, documented split, metric, seed, data card, and model limitations. Do not use private records.

Summary
You can now reason about {topic} as an evidence-producing ML workflow rather than a single model score.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
The Academy displays Python/ML examples and does not execute untrusted code or load untrusted model artifacts.
"""


def _repair_module_one_sections(lesson, item: tuple) -> None:
    """Append review sections without replacing existing Module 1 content."""
    theory, code, mm, exercise = item[4], item[2], item[5], item[6]
    if "## Detailed theory" not in (lesson.content_en or ""):
        lesson.content_en = (lesson.content_en or "") + f"""

## Detailed theory
{theory}

## Core concepts
The model boundary, data contract, evaluation evidence, and responsible-use boundary are the core concepts for this lesson.

## Syntax and usage
```python
{code}
```

## Expected output
Inspect the command output and verify the stated shape, workflow step, or environment result. Exact values may vary by Python and package version.

## Line-by-line explanation
Read imports and declarations first, then trace the input through the transformation or workflow step, and finally compare the returned output with the expectation. Change one value at a time and rerun the focused check.

## Common mistakes
- Fitting transformations on evaluation data or treating a score as proof of safety.
- Ignoring shapes, dtypes, missingness, class balance, or package versions.
- Loading untrusted artifacts or placing private records in notebooks and logs.

## Best practices
- Use explicit data contracts, reproducible seeds, baselines, pipelines, and task-appropriate metrics.
- Report limitations, uncertainty, subgroup behavior, privacy, fairness, and rollback criteria.

## Practical exercises
{exercise}

## Homework
Create a short experiment note with the data source, assumptions, setup versions, expected and observed behavior, evidence, and one limitation.

## Related references
- scikit-learn User Guide: https://scikit-learn.org/stable/user_guide.html
- NumPy documentation: https://numpy.org/doc/
- pandas documentation: https://pandas.pydata.org/docs/

## Key takeaways
ML results are evidence for a bounded question; reliable work keeps data, evaluation, privacy, and deployment boundaries explicit.
"""
    if "## အသေးစိတ်သီအိုရီ" not in (lesson.content_mm or ""):
        lesson.content_mm = (lesson.content_mm or "") + f"""

## အသေးစိတ်သီအိုရီ
{mm}

## လက်တွေ့လေ့ကျင့်ခန်း
{exercise}

## အိမ်စာ
Data source၊ setup version၊ expected/observed result၊ evidence နှင့် limitation ပါသော experiment note တစ်စောင်ရေးပါ။

## ဆက်စပ်ရည်ညွှန်းချက်
scikit-learn၊ NumPy နှင့် pandas documentation ကို project version နှင့် ကိုက်ညီအောင် ပြန်လည်ဖတ်ပါ။
"""

def seed_machine_learning_course(db, course):
    course.title = "Machine Learning with Python — From Zero to Professional AI & Machine Learning Engineer"
    course.short_description = "A free, practical path from Python data workflows to responsible modeling, deployment, and MLOps."
    course.description = "Learn ML workflows, NumPy, Pandas, preprocessing, supervised and unsupervised learning, evaluation, deep learning concepts, deployment, responsible AI, and monitoring through reproducible examples."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 40
    course.outcomes = "Frame ML problems with features, labels, baselines, splits, and task-appropriate metrics|Use Python, NumPy, Pandas, and scikit-learn safely and reproducibly|Recognize leakage, overfitting, fairness, privacy, and deployment risks|Build a foundation for model APIs, Docker, monitoring, and responsible MLOps"
    course.requirements = "Basic Python and high-school mathematics are helpful; no prior machine learning experience is required."
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
        if not lesson.content_en or not lesson.content_en.strip():
            lesson.title, lesson.slug = title, slug
            lesson.description = item[1]
            lesson.content_en = _content(position, item)
            lesson.content_mm = f"{title}\n\n{item[5]}\n\nလေ့ကျင့်ခန်း\n{item[6]}"
            lesson.duration_minutes, lesson.status, lesson.published = 40, "published", True
        _repair_module_one_sections(lesson, item)
        example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        values = {"title": f"{title} example", "language": "python" if item[3] == "python" else "bash", "filename": item[3], "code": item[2], "description": "Read-only ML example. Use synthetic data and an isolated environment; the Academy does not execute code on its host.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the data, evaluation, and responsible ML boundary before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [(item[7][0], item[7][1], item[7][2], item[7][3]), ("True or false: the Academy executes arbitrary Python or loads untrusted model artifacts.", ["True", "False"], "False", "Examples are displayed as read-only learning content."), ("Which practice improves ML reliability?", ["Separate evaluation data, document provenance, and report limitations", "Tune repeatedly on the final test set", "Use private records without consent"], "Separate evaluation data, document provenance, and report limitations", "Good ML practice protects evidence quality and affected people.")]
        for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
            row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
            values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
            if not row:
                db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
            else:
                for key, value in values.items():
                    setattr(row, key, value)
        _ensure_exercise(db, lesson, title, item[6], f"{item[5]} ကို isolated Python project ထဲတွင် လက်တွေ့လေ့ကျင့်ပါ။")
    db.flush()
    additional_report = seed_machine_learning_additional_curriculum(db, course)
    course.duration_minutes = sum(
        lesson.duration_minutes or 40
        for module in db.scalars(select(CourseModule).where(CourseModule.course_id == course.id)).all()
        for lesson in db.scalars(select(Lesson).where(Lesson.module_id == module.id)).all()
    )
    db.flush()
    return additional_report
