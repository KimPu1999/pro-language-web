"""Idempotent authored Data Analysis curriculum.

Module 1 is the complete vertical slice. Later modules have an authored
foundation lesson so the catalog never exposes empty published modules.
Datasets in this course are synthetic and are labelled as such.
"""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion


MODULES = [
    "Introduction to Data Analysis", "Data Literacy & Data Sources", "Excel Fundamentals", "Advanced Excel Analysis",
    "Data Cleaning with Excel", "Business Metrics & KPIs", "SQL Fundamentals", "SQL Joins & Relationships",
    "SQL Aggregations", "Advanced SQL Queries", "PostgreSQL for Analytics", "SQL Analytics Projects",
    "Python Fundamentals for Analysts", "Jupyter Notebook & Python Setup", "NumPy Fundamentals", "Pandas Fundamentals",
    "Data Cleaning with Pandas", "Data Transformation & Aggregation", "Exploratory Data Analysis", "Descriptive Statistics",
    "Probability Fundamentals", "Statistical Inference", "Matplotlib & Seaborn", "Data Visualization Best Practices",
    "Power BI Fundamentals", "Power BI DAX & Dashboards", "Tableau & BI Concepts", "Time Series & Trend Analysis",
    "Customer & Marketing Analytics", "Financial & Sales Analytics", "Data Quality, Ethics & Privacy", "Analytics Automation & Reporting",
    "A/B Testing & Experiment Analysis", "Data Storytelling & Stakeholder Reports", "Real-World Data Analysis Projects", "Final Data Analyst Capstone",
]

MODULE_ONE = [
    ("What Is Data Analysis?", "turning observations into defensible decisions", "import pandas as pd\n\nsales = pd.DataFrame({'region': ['North', 'South'], 'revenue': [1200, 900]})\nprint(sales['revenue'].sum())", "Data analysis is a disciplined process: define a question, inspect data, clean it, calculate measures, communicate uncertainty, and recommend an action. A dashboard is not automatically an analysis. Good analysts make the business question, population, time period, metric definition, and limitations explicit.", "df['revenue'].sum()", "Data analysis သည် business question ကို သတ်မှတ်ခြင်း၊ data ကိုစစ်ဆေးခြင်း၊ သန့်စင်ခြင်း၊ တိုင်းတာခြင်းနှင့် ကန့်သတ်ချက်များကို ရှင်းပြခြင်းတို့ပါဝင်သော process ဖြစ်သည်။"),
    ("Data Literacy and Synthetic Sources", "provenance, grain, fields, and responsible interpretation", "records = [\n    {'order_id': 1, 'region': 'North', 'revenue': 1200},\n    {'order_id': 2, 'region': 'South', 'revenue': 900},\n]\nprint(records[0]['region'])", "Data literacy means asking what one row represents, where a field came from, when it was collected, and what is missing. This course uses small synthetic datasets for practice; they are not evidence about real customers or markets. Correlation is not causation, and a source note belongs beside every meaningful result.", "row['field']\nsource -> collection time -> validation -> analysis", "Data source၊ row grain၊ field meaning နှင့် synthetic dataset ဆိုသည်များကို ခွဲခြားနားလည်ပါ။"),
    ("The Analyst Workflow", "from a business question to a reproducible finding", "question = 'Which region needs attention?'\nrows = [{'region': 'North', 'revenue': 1200}, {'region': 'South', 'revenue': 900}]\nsummary = {}\nfor row in rows:\n    summary[row['region']] = row['revenue']\nprint(summary)", "A reproducible workflow records the question, dataset version, cleaning decisions, formulas or queries, result, and interpretation. Start with a measurable question rather than choosing a chart first. Define a success metric and a comparison group before looking for a story.", "question -> inspect -> clean -> calculate -> visualize -> interpret", "မေးခွန်းမှ စပြီး inspect၊ clean၊ calculate၊ visualize၊ interpret အဆင့်များကို ပြန်လည်လုပ်ဆောင်နိုင်အောင် မှတ်တမ်းတင်ပါ။"),
    ("Excel Fundamentals for Analysts", "tables, formulas, filters, and transparent calculations", "rows = [1200, 900, 1500]\ntotal = sum(rows)\naverage = total / len(rows)\nprint(f'Total: {total}, Average: {average:.1f}')", "Excel is useful for small, transparent analyses. Convert ranges to tables, name columns clearly, keep raw data separate from calculated fields, and document formulas. A SUMIFS-style metric should state its filter, time range, and denominator; do not treat a formatted cell as a validated result.", "=SUM(B2:B4)\n=AVERAGE(B2:B4)\n=SUMIFS(Revenue, Region, \"North\")", "Excel သည် small analysis အတွက် အသုံးဝင်ပြီး raw data၊ formula နှင့် summary ကို သီးခြားထားပါ။"),
    ("SQL and Tabular Data", "selecting, filtering, and checking rows", "rows = [\n    {'region': 'North', 'revenue': 1200},\n    {'region': 'South', 'revenue': 900},\n]\nprint([row for row in rows if row['revenue'] >= 1000])", "SQL expresses analysis over tables. SELECT chooses fields, WHERE filters rows, and GROUP BY changes the grain of the result. This lesson uses a controlled sample only; the lab never connects to production and does not execute arbitrary SQL. Always inspect row counts after a filter or join.", "SELECT region, revenue\nFROM sales\nWHERE revenue >= 1000;", "SQL တွင် SELECT၊ WHERE နှင့် GROUP BY တို့သည် table analysis ၏ အခြေခံများဖြစ်သည်။"),
    ("Python and Jupyter for Analysis", "notebooks, Pandas, and executable documentation", "import pandas as pd\n\ndf = pd.DataFrame({'region': ['North', 'South', 'North'], 'revenue': [1200, 900, 500]})\nprint(df.groupby('region', as_index=False)['revenue'].sum())", "Jupyter notebooks combine narrative, code, tables, and charts. Use Pandas for tabular work, keep cells ordered, restart-and-run before sharing, and state assumptions beside results. A notebook is reproducible only when its input data, package versions, and transformations are known.", "df.groupby('region', as_index=False)['revenue'].sum()", "Jupyter notebook နှင့် Pandas ကို အသုံးပြုပြီး code၊ table နှင့် explanation ကို ပြန်လည်လုပ်ဆောင်နိုင်အောင် ရေးသားပါ။"),
    ("Module 1 Analysis Review", "a small revenue summary with limitations", "import pandas as pd\n\ndf = pd.DataFrame({'region': ['North', 'South', 'North'], 'revenue': [1200, 900, 500]})\nsummary = df.groupby('region', as_index=False)['revenue'].sum()\nprint(summary.to_string(index=False))", "The summary aggregates synthetic revenue by region. It answers only that narrow question: it does not prove profitability, customer satisfaction, or a causal explanation. Before sharing, verify duplicates, missing values, currency, period, source, and whether each row is an order or a line item.", "summary = df.groupby('region', as_index=False).agg(total_revenue=('revenue', 'sum'))", "Module 1 တွင် business question၊ source၊ Excel၊ SQL၊ Python နှင့် interpretation ကို ပေါင်းစပ်လေ့လာပါမည်။"),
]

GENERAL = [
    ("Data Sources and Grain", "source notes and row-level meaning"), ("Excel Tables and References", "repeatable spreadsheet structure"),
    ("PivotTables", "grouping and summarizing business data"), ("Lookup and Conditional Formulas", "controlled spreadsheet joins"),
    ("Cleaning Spreadsheet Data", "missing values and duplicates"), ("KPI Definitions", "numerators, denominators, and time windows"),
    ("SELECT and WHERE", "safe SQL filtering"), ("JOIN Fundamentals", "relationships and duplicate rows"),
    ("GROUP BY and Aggregates", "summary measures"), ("Window Functions", "rank, lag, and rolling context"),
    ("PostgreSQL Analytics", "types, indexes, and read-only analysis"), ("SQL Project Workflow", "query notes and validation"),
    ("Python for Analysts", "collections and functions"), ("Notebook Reproducibility", "environments and inputs"),
    ("NumPy Arrays", "vectorized numerical operations"), ("Pandas DataFrames", "columns, indexes, and selection"),
    ("Missing Values and Duplicates", "explicit cleaning decisions"), ("Transformations and Grouping", "reshape and aggregate"),
    ("Exploratory Analysis", "questions before modeling"), ("Descriptive Statistics", "center and spread"),
    ("Probability", "uncertainty and events"), ("Confidence and Inference", "samples and limitations"),
    ("Charts with Matplotlib", "controlled visual encoding"), ("Visualization Review", "honest axes and annotations"),
    ("Power BI Models", "relationships and report structure"), ("DAX Measures", "filter context and metric definitions"),
    ("Tableau Concepts", "dimensions, measures, and dashboards"), ("Time Series", "trend, seasonality, and leakage"),
    ("Customer Analytics", "cohorts and retention"), ("Sales and Finance Analytics", "revenue and margin"),
    ("Ethics and Privacy", "minimization and responsible use"), ("Automated Reporting", "scheduled, tested outputs"),
    ("A/B Testing", "randomization and effect size"), ("Data Storytelling", "audience, evidence, and action"),
    ("Project Portfolio", "scope, rubric, and delivery"), ("Final Capstone Plan", "end-to-end analyst workflow"),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(title, topic, theory, syntax, code, mm, previous, next_title):
    return f"""Introduction
{title} introduces {topic} using synthetic, documented data.

Learning objectives
- Define the business question, grain, metric, and limitation for {topic}.
- Apply a reproducible analysis step with Python, SQL, or spreadsheet reasoning.
- Interpret results without confusing correlation with causation.

Prerequisites
{previous}

Business problem
An analyst must answer a narrow stakeholder question with evidence while making the dataset, time period, assumptions, and limitations visible.

Sample dataset
This lesson uses a small synthetic sales dataset with region, order_id, revenue, and order_date fields. It is for education only and is not real customer data.

Analysis methodology
Define the question, inspect row grain and missing values, clean only with documented rules, calculate a verified measure, visualize when useful, and write an interpretation with uncertainty.

Detailed theory
{theory}

Python / SQL / Excel example
```python
{code}
```

Syntax and formulas
```text
{syntax}
```

Expected results
The example produces deterministic output from synthetic rows. Recalculate after changing the sample and check row counts, totals, and grouping grain.

Data visualization
Use a labelled bar chart for category totals or a line chart for ordered dates. Include units, a meaningful title, and a source note; never use visual decoration to imply a larger effect.

Step-by-step explanation
1. Load or define the documented sample rows.
2. Inspect field names, types, missing values, and duplicate keys.
3. Apply one transparent transformation or aggregate.
4. Compare the result with the question and state what it cannot prove.

Interpretation of findings
The result describes this synthetic sample only. It does not establish causation, generalize to an unseen population, or justify a business decision without additional context.

Common mistakes
- Changing the row grain during a join or aggregation without checking counts.
- Presenting synthetic practice data as a real-world finding.
- Omitting units, date ranges, denominators, or missing-value treatment.
- Treating a correlation or chart pattern as proof of cause.

Best practices
Keep raw data immutable, document transformations, use parameterized read-only SQL, pin Python packages, validate file uploads, and make charts accessible with text summaries.

Security considerations
The lab uses synthetic in-memory data. It does not connect to production databases or execute arbitrary SQL/Python. Never place credentials in notebooks, uploaded files, formulas, or client-side code.

Practice exercises
- Easy: reproduce the total and label its unit and time period.
- Medium: group the sample by region and verify the row count before and after aggregation.
- Challenge: add a limitation, a validation check, and a chart specification without claiming causation.
Hint: write down the grain and denominator before writing the formula.
Guided solution: inspect -> clean -> calculate -> validate -> visualize -> interpret.

Quiz
1. What should be defined before choosing a chart? The business question, grain, metric, and audience.
2. True or false: correlation alone proves causation. False.
3. Which SQL clause filters rows? WHERE.
4. What should a synthetic dataset be labelled as? Educational practice data, not real evidence.

Summary
You can now apply {topic}, document assumptions, and communicate a bounded finding.

Next lesson
{next_title}
"""


def _questions(topic):
    return [
        (f"Which practice best supports {topic}?", ["Document grain and validation", "Hide assumptions", "Use production credentials in a notebook"], "Document grain and validation", "Reproducible analysis makes assumptions and checks visible."),
        ("True or false: a chart pattern by itself proves causation.", ["True", "False"], "False", "Charts describe patterns; causal claims require an appropriate design and evidence."),
        ("Which SQL clause filters rows?", ["WHERE", "GROUP BY", "ORDER BY"], "WHERE", "WHERE limits rows before later grouping or ordering."),
        ("What is the correct label for the course sample?", ["Synthetic educational data", "Verified customer data", "Production data"], "Synthetic educational data", "The course sample is created for practice and is not real-world evidence."),
    ]


def seed_data_analysis_course(db, course):
    course.title = "Data Analysis — From Zero to Professional Data Analyst"
    course.short_description = "A free analyst pathway across Excel, SQL, Python, Pandas, statistics, visualization, BI, and responsible storytelling."
    course.description = "Learn a reproducible data analysis workflow with synthetic datasets, Excel, SQL, PostgreSQL, Python, NumPy, Pandas, statistics, visualization, Power BI, Tableau concepts, and a final capstone."
    course.level, course.status, course.published = "advanced", "published", True
    course.outcomes = "Define measurable business questions|Clean and validate tabular data|Analyze with Excel SQL and Python|Build honest visualizations and dashboards|Communicate limitations and recommendations"
    course.requirements = "Basic computer skills. Python and SQL are introduced progressively. Practice datasets are synthetic; document package and tool versions for local work."
    authored = []
    for module_index, module_title in enumerate(MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_index))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_index)
            db.add(module)
            db.flush()
        module.title = module_title
        if module_index == 1:
            specs = [{"title": a, "topic": b, "code": c, "theory": d, "syntax": e, "mm": f} for a, b, c, d, e, f in MODULE_ONE]
        else:
            title, topic = GENERAL[module_index - 2]
            specs = [{"title": title, "topic": topic, "code": "import pandas as pd\n\ndf = pd.DataFrame({'value': [10, 20, 30]})\nprint(df['value'].mean())", "theory": f"This foundation lesson explains {topic}. Use a synthetic, documented dataset and validate row counts, missing values, metric definitions, and interpretation before reporting a result.", "syntax": "df.groupby('category', as_index=False)['value'].sum()", "mm": f"ဤ lesson တွင် {topic} ကို data analysis workflow ဖြင့် လေ့လာပါမည်။"}]
        for lesson_index, spec in enumerate(specs, 1):
            title, topic = spec["title"], spec["topic"]
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm="")
                db.add(lesson)
                db.flush()
            previous = "Basic computer skills and a willingness to inspect data." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
            next_title = "Continue to the next lesson." if module_index < 36 else "Continue to the final capstone review."
            lesson.title, lesson.slug = title, slug
            lesson.content_en = _content(title, topic, spec["theory"], spec["syntax"], spec["code"], spec["mm"], previous, next_title)
            lesson.content_mm = f"{title} ကို English theory နှင့်အတူ လေ့လာနိုင်ပါသည်။\n\n{spec['mm']}"
            lesson.description, lesson.duration_minutes = spec["theory"], 35
            lesson.status, lesson.published = "published", True
            authored.append(lesson)
            examples = list(db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all())
            example = examples[0] if examples else None
            for duplicate in examples[1:]:
                db.delete(duplicate)
            if not example:
                db.add(CodeExample(lesson_id=lesson.id, title=f"{title} example", language="python", filename="analysis.py", code=spec["code"], description="Synthetic-data example. Hosted arbitrary Python and SQL execution is disabled.", position=1))
            else:
                example.title, example.language, example.filename, example.code, example.description, example.position = f"{title} example", "python", "analysis.py", spec["code"], "Synthetic-data example. Hosted arbitrary Python and SQL execution is disabled.", 1
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz:
                quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the data-quality and interpretation guidance, then retry missed concepts.", status="published")
                db.add(quiz)
                db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(topic), 1):
                values = dict(prompt=prompt, question_type="true_false" if options == ["True", "False"] else "multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                question = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
                if not question:
                    db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items():
                        setattr(question, key, value)
    course.duration_minutes = sum(lesson.duration_minutes or 35 for lesson in authored)
    db.flush()
