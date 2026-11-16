"""Idempotent Python for Artificial Intelligence vertical-slice seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion


PLANNED_MODULES = [
    "Introduction to Python for AI", "Python Installation & Environment", "Python Programming Fundamentals",
    "Control Flow & Functions", "Python Data Structures", "Object-Oriented Python", "Python Files, Modules & APIs",
    "Mathematics for AI", "NumPy Fundamentals", "Pandas Data Analysis", "Data Visualization", "Data Cleaning & Preprocessing",
    "Statistics for Machine Learning", "Machine Learning Fundamentals", "Regression Algorithms", "Classification Algorithms",
    "Clustering & Unsupervised Learning", "Model Evaluation & Optimization", "Neural Network Fundamentals", "Gradient Descent & Backpropagation",
    "PyTorch Fundamentals", "Deep Learning Model Training", "Convolutional Neural Networks", "Computer Vision with Python",
    "Natural Language Processing", "Transformers & Attention", "Sequence Models & Time Series", "Generative AI Fundamentals",
    "Large Language Models", "Prompt Engineering", "Hugging Face & Open Models", "Embeddings & Vector Databases",
    "Retrieval-Augmented Generation", "AI Agents & Tool Calling", "AI Safety, Security & Evaluation", "FastAPI for AI Applications",
    "MLOps & Model Lifecycle", "Docker, Cloud & AI Deployment", "Professional Python AI Projects", "Final AI Engineer Capstone",
]

MODULE_ONE = [
    ("What Python for AI Means", "Python as a readable language, scientific ecosystem, and model-development tool",
     "problem -> data -> features -> model -> evaluation\nimport math\nprint(math.sqrt(16))", "python",
     "Python is used across data preparation, numerical computing, machine learning, deep learning, and AI services. A Python library does not guarantee a correct model: data contracts, evaluation, privacy, reproducibility, and deployment context still matter.",
     "Python သည် data preparation၊ numerical computing၊ machine learning နှင့် AI service များအတွက်အသုံးများသည်။ Library သုံးရုံဖြင့် model မှန်ကန်မည်မဟုတ်ပါ။",
     "Draw an AI workflow from a measurable problem to deployment and label where data leakage, privacy, and human review belong.",
     ("AI အတွက် Python ၏ အခန်းကဏ္ဍက ဘာလဲ?", ["Data, models, evaluation, and services ကိုချိတ်ဆက်ပေးခြင်း", "Guarantee truth", "Replace all human decisions"], "Data, models, evaluation, and services ကိုချိတ်ဆက်ပေးခြင်း", "Python is a tool in an evidence-based AI workflow.")),
    ("Reproducible Python Environments", "virtual environments, pinned packages, seeds, notebooks, and project structure",
     "python -m venv .venv\npython -m pip install numpy pandas scikit-learn\npython -c \"import sys; print(sys.version)\"", "bash",
     "Reproducibility depends on code, package versions, data provenance, random seeds, and documented hardware or runtime assumptions. Use an isolated environment and keep credentials out of notebooks, source control, and client bundles.",
     "Reproducibility အတွက် code၊ package version၊ data provenance၊ seed နှင့် runtime assumption ကို မှတ်တမ်းတင်ရသည်။ Virtual environment သုံးပြီး secret မထည့်ပါနှင့်။",
     "Create an environment checklist with Python version, dependency lock, dataset source, random seed, and intended use.",
     ("Reproducible AI setup တွင် ဘာတွေလိုအပ်သနည်း?", ["Isolated environment, versions, data provenance, and seeds", "Only a notebook", "A production API key"], "Isolated environment, versions, data provenance, and seeds", "Reproducibility requires both software and data context.")),
    ("Python Data and Functions", "variables, types, functions, exceptions, and testable transformations",
     "def normalize_score(value: float) -> float:\n    return max(0.0, min(1.0, value))\n\nprint(normalize_score(1.2))", "python",
     "AI pipelines are easier to test when transformations are small, typed, deterministic functions. Handle invalid data explicitly and distinguish a missing value from a valid zero. Tests should cover normal, boundary, and error cases.",
     "AI pipeline တွင် transformation များကို သေးငယ်ပြီး typed၊ deterministic function အဖြစ်ရေးပါ။ Missing value နှင့် zero ကို မရောပါနှင့်။",
     "Write a typed feature transformation with boundary tests for missing, negative, and out-of-range values.",
     ("AI preprocessing function က ဘာကြောင့် testable ဖြစ်သင့်သနည်း?", ["Inputs, boundaries, and errors ကိုရှင်းလင်းစွာစစ်နိုင်ရန်", "Model score ကိုအလိုအလျောက်မြှင့်ရန်", "Data provenance ဖျက်ရန်"], "Inputs, boundaries, and errors ကိုရှင်းလင်းစွာစစ်နိုင်ရန်", "Small deterministic functions are easier to validate.")),
    ("NumPy Arrays and Vectorization", "arrays, shapes, dtypes, broadcasting, and numeric assumptions",
     "import numpy as np\nx = np.array([1.0, 2.0, 3.0])\nprint(x.shape, x.mean(), x * 2)", "python",
     "NumPy arrays make numeric operations explicit through shape and dtype. Vectorization can be efficient, but it does not remove the need to check dimensions, missing values, overflow, and reproducibility.",
     "NumPy array တွင် shape နှင့် dtype ကိုသိရှိပြီး vectorized operation သုံးနိုင်သည်။ Dimension နှင့် missing value ကို မစစ်ဘဲ မတွက်ပါနှင့်။",
     "Predict the shape and output of a small array operation, then add an assertion for the expected shape.",
     ("NumPy computation မလုပ်မီ ဘာစစ်သင့်သနည်း?", ["Shape, dtype, and missing-value assumptions", "A private token", "Only the last value"], "Shape, dtype, and missing-value assumptions", "Shape and dtype determine whether operations are valid.")),
    ("Pandas DataFrames and Dataset Contracts", "columns, missing values, duplicates, provenance, and inspection",
     "import pandas as pd\ndf = pd.DataFrame({'hours': [2, 4, None], 'passed': [False, True, True]})\nprint(df.shape)\nprint(df.isna().sum())", "python",
     "A DataFrame is useful for labeled tabular data, but the important work is defining a dataset contract: row meaning, feature types, target, collection time, missingness, license, and intended use. Inspect before modeling.",
     "Pandas DataFrame မသုံးမီ row meaning၊ feature type၊ target၊ missingness၊ license နှင့် intended use ကို dataset contract အဖြစ်သတ်မှတ်ပါ။",
     "Profile a synthetic DataFrame and decide whether missing values should be removed, imputed, or reported.",
     ("Modeling မလုပ်မီ DataFrame တွင် ဘာ inspect လုပ်သင့်သနည်း?", ["Shape, dtypes, missingness, and duplicates", "Only the first row", "A secret"], "Shape, dtypes, missingness, and duplicates", "Inspection reveals data quality and contract problems.")),
    ("Features, Labels, and Leakage", "problem framing, feature engineering, target definition, and prediction-time availability",
     "features = ['hours_studied', 'practice_count']\nlabel = 'passed'\nprint(features, label)", "python",
     "Features are inputs available at prediction time; a label is the target used for training or evaluation. Leakage happens when training uses information unavailable at prediction time, creating falsely optimistic scores.",
     "Feature သည် prediction time တွင်ရနိုင်သော input ဖြစ်ပြီး label သည် target ဖြစ်သည်။ မရနိုင်သည့် future information သုံးပါက leakage ဖြစ်သည်။",
     "Write a dataset card and identify one feature that would leak the outcome if collected after the event.",
     ("Data leakage ဆိုသည်မှာ ဘာလဲ?", ["Training uses information unavailable at prediction time", "A missing chart title", "A Python import"], "Training uses information unavailable at prediction time", "Leakage makes evaluation misleadingly optimistic.")),
    ("Train/Test Splitting and Metrics", "generalization, baselines, regression/classification metrics, and evaluation context",
     "from sklearn.model_selection import train_test_split\nX = [[1], [2], [3], [4]]\ny = [0, 0, 1, 1]\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=42)", "python",
     "A split estimates generalization when test data remains unseen during decisions. Choose metrics for the task and cost of errors. A single score without a baseline, dataset context, uncertainty, or subgroup analysis is not a complete evaluation.",
     "Test set ကို tuning အတွက်မသုံးဘဲ unseen data ပေါ် generalization ကို ခန့်မှန်းရန်သုံးပါ။ Metric ကို error cost နှင့်ကိုက်ညီအောင်ရွေးပါ။",
     "Design a split and metric plan for an imbalanced classifier and explain why accuracy alone may be insufficient.",
     ("Final test set ကို ဘာအတွက်သုံးသနည်း?", ["A final estimate on unseen data", "Unlimited tuning", "Storing private labels"], "A final estimate on unseen data", "The final test should remain held out from iterative choices.")),
    ("Responsible First AI Workflow", "provenance, privacy, fairness, reproducibility, human review, and rollback",
     "model_card = {'intended_use': 'synthetic learning demo', 'seed': 42, 'limitations': ['small data']}\nprint(model_card)", "python",
     "A responsible AI workflow documents intended use, data provenance and license, privacy, evaluation, subgroup limitations, human oversight, monitoring, and rollback. Models can amplify data problems; deployment must include an owner and a response plan.",
     "Responsible AI workflow တွင် intended use၊ data provenance၊ privacy၊ subgroup limitation၊ human oversight နှင့် rollback ကို မှတ်တမ်းတင်ရသည်။",
     "Create a model-card outline for a synthetic student-outcome model with limitations, review owner, and rollback trigger.",
     ("Responsible AI documentation တွင် ဘာပါသင့်သနည်း?", ["Provenance, intended use, metrics, limitations, and review", "Only the best score", "Private user records"], "Provenance, intended use, metrics, limitations, and review", "Documentation makes evidence and model risk visible.")),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(position: int, item: tuple) -> str:
    title, topic, example, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "Basic Python and high-school mathematics are helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the ML lab and neural-network visualizer."
    return f"""Introduction
{title} introduces {topic} in a reproducible, responsible AI workflow.

Learning objectives
- Explain {topic} and its role in an AI pipeline.
- Use explicit data, code, evaluation, and deployment boundaries.
- Identify leakage, privacy, safety, and reproducibility risks.

Prerequisites
{prerequisite}

AI architecture diagram
problem -> dataset contract -> features/labels -> train -> evaluate -> deploy -> monitor -> review

Detailed theory
{theory}

Python AI example ({language})
{example}

Mathematical intuition
AI systems optimize an objective using evidence. A metric is a summary of chosen outcomes, not a guarantee of truth. State the target, assumptions, scale, split, and uncertainty before comparing results.

Expected output
Exact output depends on Python and library versions. Verify shapes, dtypes, metrics, random seeds, and dataset assumptions rather than copying an unexplained number.

Step-by-step implementation
1. Define a measurable problem and intended use.
2. Document data source, license, feature/label contract, and missingness.
3. Build a small deterministic transformation or baseline.
4. Split data before fitting choices that could leak information.
5. Evaluate with task-appropriate metrics and document limitations.
6. Plan monitoring, human review, privacy, and rollback before deployment.

Architecture explanation
Python code -> NumPy/Pandas transformation -> model -> evaluation -> FastAPI inference boundary -> monitored service

Common errors
- Training on future information or tuning on the final test set.
- Reporting accuracy without class balance or error cost.
- Loading private data or model artifacts without authorization.
- Treating a high score as proof of fairness, safety, or generalization.

Troubleshooting
Check Python/package versions, array shapes, dtypes, missing values, split sizes, random seeds, warnings, and the smallest reproducible example. Preserve the dataset and metric context before changing code.

Best practices
- Use synthetic or approved data, pinned dependencies, deterministic seeds, dataset cards, baseline comparisons, subgroup analysis, and reproducible tests.
- Keep credentials server-side; use bounded inference, rate limits, content safeguards, and rollback.
- Report uncertainty, limitations, and intended use next to model results.

AI safety considerations
The Academy playground displays safe examples and deterministic simulations. It does not execute arbitrary Python, load untrusted model artifacts, expose private data, or require paid API credentials. Protect prompts, outputs, embeddings, and user data.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Build a reproducible synthetic-data baseline with a dataset contract, train/test split, metric table, model card, error analysis, safety review, and rollback plan.

Summary
You can now reason about {topic} using data, model, evaluation, safety, and operations boundaries.

Next lesson
{next_lesson}

Myanmar explanation
{mm}
"""


def seed_python_ai_course(db, course):
    course.title = "Python for Artificial Intelligence — From Zero to AI Engineer"
    course.short_description = "A free practical path from Python and data foundations to machine learning, deep learning, GenAI, and responsible AI deployment."
    course.description = "Learn Python for AI, NumPy, Pandas, visualization, preprocessing, statistics, machine learning, neural networks, PyTorch, computer vision, NLP, transformers, LLMs, embeddings, RAG, agents, safety, FastAPI, MLOps, and deployment."
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 55
    course.outcomes = "Build reproducible Python data workflows with NumPy, Pandas, visualization, and preprocessing|Train and evaluate responsible regression, classification, clustering, and neural-network baselines|Understand PyTorch, CNNs, NLP, transformers, LLMs, embeddings, RAG, and agent boundaries|Deploy AI services with FastAPI, Docker, monitoring, secrets management, rate limits, and rollback"
    course.requirements = "Basic Python and high-school mathematics are helpful; no machine-learning experience is required."
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
        lesson.duration_minutes, lesson.status, lesson.published = 55, "published", True
        example_row = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        values = {"title": f"{title} example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe synthetic-data AI example; the Academy does not execute arbitrary code or load untrusted artifacts.", "position": 1}
        if not example_row:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example_row, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review data contracts, evaluation evidence, reproducibility, privacy, and safety before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: the Academy executes arbitrary student Python or loads untrusted model artifacts.", ["True", "False"], "False", "Examples are displayed as safe content and simulations."),
            ("Which practice improves ML evidence quality?", ["Hold out evaluation data and document provenance and limitations", "Tune on the final test repeatedly", "Use private records without authorization"], "Hold out evaluation data and document provenance and limitations", "Reliable evaluation needs separation, provenance, and context."),
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
