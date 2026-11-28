"""Reviewable Python for Artificial Intelligence curriculum batch.

The existing Module 1 is preserved by ``python_ai_course_content``. This
batch adds Modules 2-12 as complete EN/MM drafts with safe synthetic examples.
"""

import json
import re

from sqlalchemy import select

from .models import CodeExample, CodingExercise, CourseModule, Lesson, LessonQuiz, QuizQuestion


MODULES = {
    2: "Python Foundations for AI",
    3: "Python Data Structures and Software Design",
    4: "NumPy, Pandas and Visualization",
    5: "Mathematics and Statistics for AI",
    6: "Data Preparation and Machine Learning Workflow",
    7: "Supervised Machine Learning",
    8: "Unsupervised Learning and Optimization",
    9: "Deep Learning with PyTorch",
    10: "Computer Vision, NLP and Transformers",
    11: "Generative AI, RAG and Agents",
    12: "AI Applications, MLOps and Capstone",
}


def _items(*rows):
    return list(rows)


# title, focus, safe example, Burmese teaching note
LESSONS = {
    2: _items(
        ("Variables, Types and Expressions", "Python values, types, operators, and explicit assumptions", "value = 3.5\nprint(type(value).__name__, value * 2)", "Variable type နှင့် expression များကို စစ်ပြီး AI data assumption ကို ရှင်းလင်းရေးပါ။"),
        ("Control Flow for Data Rules", "conditionals, loops, comprehensions, and bounded data rules", "scores = [40, 75, 90]\npassed = [score >= 50 for score in scores]\nprint(passed)", "Data rule များကို condition နှင့် loop ဖြင့် ရေးပြီး boundary case ကို စစ်ပါ။"),
        ("Functions and Type Hints", "small deterministic transformations and typed interfaces", "def clip(value: float, low: float = 0, high: float = 1) -> float:\n    return max(low, min(high, value))\n\nprint(clip(1.4))", "AI transformation များကို typed function အဖြစ်ရေးပြီး input/output ကို စစ်ပါ။"),
        ("Exceptions and Validation", "explicit validation, safe errors, and input boundaries", "def positive(value: float) -> float:\n    if value < 0:\n        raise ValueError('value must be non-negative')\n    return value\n\nprint(positive(2))", "Invalid input ကို ရှင်းလင်းသော error ဖြင့် တားပြီး secret မဖော်ပြပါနှင့်။"),
        ("Testing Python Data Functions", "unit tests, boundary cases, and regression protection", "def add(a: int, b: int) -> int:\n    return a + b\n\nassert add(2, 3) == 5\nprint('test passed')", "Normal၊ boundary နှင့် error case များကို test ရေးပါ။"),
    ),
    3: _items(
        ("Lists, Tuples and Sets", "ordered collections, immutability choices, and uniqueness", "items = ['ai', 'ml', 'ai']\nprint(list(dict.fromkeys(items)), set(items))", "List၊ tuple နှင့် set ကို data meaning အလိုက် ရွေးချယ်ပါ။"),
        ("Dictionaries and JSON", "key-value records, serialization boundaries, and schemas", "record = {'model': 'baseline', 'version': 1}\nimport json\nprint(json.dumps(record, sort_keys=True))", "Dictionary နှင့် JSON schema ကို သတ်မှတ်ပြီး untrusted input ကို validate လုပ်ပါ။"),
        ("Object-Oriented Python for Pipelines", "classes, composition, and state boundaries", "class Scaler:\n    def transform(self, value: float) -> float:\n        return value / 10\n\nprint(Scaler().transform(8))", "Pipeline component တစ်ခုစီ၏ state နှင့် responsibility ကို ခွဲထားပါ။"),
        ("Modules, Packages and Imports", "reusable package boundaries and dependency hygiene", "from math import sqrt\nprint(sqrt(25))", "Module boundary နှင့် dependency version ကို documentation ထဲတွင် ထားပါ။"),
        ("Files, Paths and Configuration", "safe file handling, environment configuration, and secrets", "from pathlib import Path\npath = Path('demo.txt')\nprint(path.name, path.suffix)", "Path ကို validate လုပ်ပြီး credentials ကို source/file ထဲ မသိမ်းပါနှင့်။"),
    ),
    4: _items(
        ("NumPy Arrays and Shapes", "arrays, dimensions, dtype, and vectorized arithmetic", "import numpy as np\nx = np.array([[1, 2], [3, 4]])\nprint(x.shape, x.mean(axis=0))", "NumPy array ၏ shape နှင့် dtype ကို စစ်ပြီး vectorized operation သုံးပါ။"),
        ("Broadcasting and Reshaping", "broadcasting rules, reshape, and dimensional safety", "import numpy as np\nx = np.array([1, 2, 3])\nprint((x + 10).reshape(1, 3))", "Broadcasting မလုပ်မီ dimension နှင့် intended meaning ကို စစ်ပါ။"),
        ("Pandas DataFrame Inspection", "tabular inspection, dtypes, missingness, and duplicates", "import pandas as pd\ndf = pd.DataFrame({'age': [20, 30, None]})\nprint(df.info())", "DataFrame ကို model မလုပ်မီ shape၊ dtype၊ missingness နှင့် duplicate စစ်ပါ။"),
        ("Grouping, Joining and Aggregation", "relational operations and leakage-aware summaries", "import pandas as pd\ndf = pd.DataFrame({'team': ['a', 'a', 'b'], 'score': [2, 4, 8]})\nprint(df.groupby('team')['score'].mean())", "Join/group operation တွင် row grain နှင့် leakage ကို စစ်ပါ။"),
        ("Visualization for Data Questions", "charts, distributions, outliers, and honest communication", "import matplotlib.pyplot as plt\nplt.plot([1, 2, 3], [2, 3, 5])\nplt.title('Synthetic trend')\nplt.close()", "Visualization သည် question တစ်ခုကို ဖြေဖို့ဖြစ်ပြီး misleading scale မသုံးပါနှင့်။"),
    ),
    5: _items(
        ("Vectors and Matrices", "linear algebra notation for features and model parameters", "import numpy as np\nX = np.array([[1, 2], [3, 4]])\nw = np.array([0.5, 0.25])\nprint(X @ w)", "Feature matrix နှင့် weight vector ၏ shape ကို ရှင်းလင်းစွာ သတ်မှတ်ပါ။"),
        ("Descriptive Statistics", "mean, median, variance, spread, and robust summaries", "import statistics\nvalues = [1, 2, 100]\nprint(statistics.mean(values), statistics.median(values))", "Outlier ရှိသော data တွင် mean နှင့် median ကို နှိုင်းယှဉ်ပါ။"),
        ("Probability and Distributions", "events, conditional probability, and uncertainty", "from collections import Counter\noutcomes = ['ok', 'ok', 'error']\nprint(Counter(outcomes))", "Probability ကို certainty မဟုတ်ဘဲ uncertainty evidence အဖြစ် ဖော်ပြပါ။"),
        ("Derivatives and Gradient Descent", "loss surfaces, gradients, learning rate, and convergence", "x = 3.0\nlearning_rate = 0.1\nfor _ in range(3):\n    gradient = 2 * x\n    x -= learning_rate * gradient\nprint(round(x, 3))", "Gradient descent တွင် loss၊ gradient နှင့် learning rate ကို စောင့်ကြည့်ပါ။"),
        ("Statistics and Sampling Bias", "samples, confidence, correlation, and causal limits", "sample = [2, 3, 4, 5]\nprint(sum(sample) / len(sample))", "Sample တစ်ခု၏ result ကို population truth ဟု မယူဆပါနှင့်။"),
    ),
    6: _items(
        ("Dataset Contracts and Provenance", "row meaning, target definition, license, and intended use", "contract = {'rows': 'one student attempt', 'target': 'passed', 'license': 'synthetic'}\nprint(contract)", "Dataset source၊ license၊ row meaning နှင့် target ကို contract အဖြစ်ရေးပါ။"),
        ("Missing Values and Imputation", "missingness patterns, imputation boundaries, and indicators", "values = [2, None, 4]\nfilled = [3 if value is None else value for value in values]\nprint(filled)", "Imputation ကို training data မှာသာ fit ပြီး missing indicator ကို စဉ်းစားပါ။"),
        ("Encoding and Scaling", "categorical encoding, numerical scaling, and leakage prevention", "categories = {'beginner': 0, 'advanced': 1}\nprint(categories['beginner'])", "Encoding/scaling ကို pipeline ထဲထားပြီး test data မထိပါစေနှင့်။"),
        ("Train, Validation and Test Splits", "generalization, cross-validation, and final evaluation", "from sklearn.model_selection import train_test_split\nX = list(range(10))\ntrain, test = train_test_split(X, test_size=0.2, random_state=42)\nprint(len(train), len(test))", "Validation နှင့် final test boundary ကို ခွဲထားပါ။"),
        ("Feature Engineering and Pipelines", "derived features, transformers, and reproducible preprocessing", "from sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nprint(Pipeline([('scale', StandardScaler())]))", "Feature engineering ကို repeatable pipeline အဖြစ် စီမံပါ။"),
    ),
    7: _items(
        ("Regression Fundamentals", "continuous targets, baselines, and linear models", "from sklearn.linear_model import LinearRegression\nmodel = LinearRegression()\nprint(model)", "Regression သည် continuous target ကို ခန့်မှန်းပြီး baseline နှင့် နှိုင်းယှဉ်ရသည်။"),
        ("Classification and Logistic Regression", "classes, probabilities, thresholds, and calibration", "from sklearn.linear_model import LogisticRegression\nmodel = LogisticRegression()\nprint(model)", "Classification တွင် class၊ probability၊ threshold နှင့် error cost ကို စဉ်းစားပါ။"),
        ("Decision Trees and Random Forests", "nonlinear rules, ensembles, and interpretability limits", "from sklearn.tree import DecisionTreeClassifier\nmodel = DecisionTreeClassifier(max_depth=3, random_state=42)\nprint(model.max_depth)", "Tree depth နှင့် ensemble သည် overfitting/interpretability ကို သက်ရောက်စေသည်။"),
        ("Nearest Neighbors and Support Vector Machines", "distance, margins, scaling, and model assumptions", "from sklearn.neighbors import KNeighborsClassifier\nprint(KNeighborsClassifier(n_neighbors=3))", "Distance-based model တွင် scaling နှင့် data geometry ကို စစ်ပါ။"),
        ("Metrics and Error Analysis", "confusion matrices, precision, recall, F1, and residuals", "from sklearn.metrics import confusion_matrix\nprint(confusion_matrix([0, 1], [0, 0]))", "Metric တစ်ခုတည်းမဟုတ်ဘဲ error type နှင့် affected group ကို စစ်ပါ။"),
    ),
    8: _items(
        ("K-Means Clustering", "centroids, distance, initialization, and cluster interpretation", "from sklearn.cluster import KMeans\nmodel = KMeans(n_clusters=2, random_state=42, n_init=10)\nprint(model.n_clusters)", "Cluster label ကို ground truth ဟု မယူဆဘဲ interpretation လုပ်ပါ။"),
        ("Hierarchical Clustering", "linkage, dendrogram reasoning, and similarity", "from sklearn.cluster import AgglomerativeClustering\nprint(AgglomerativeClustering(n_clusters=2))", "Hierarchical cluster သည် linkage နှင့် distance choice ပေါ်မူတည်သည်။"),
        ("PCA and Dimensionality Reduction", "variance, projections, visualization, and information loss", "from sklearn.decomposition import PCA\npca = PCA(n_components=2)\nprint(pca.n_components)", "PCA သည် visualization/compact representation ဖြစ်ပြီး meaning ကို မပျောက်အောင် စစ်ပါ။"),
        ("Hyperparameter Search", "validation-driven tuning, search spaces, and reproducibility", "from sklearn.model_selection import GridSearchCV\nprint(GridSearchCV)", "Tuning ကို validation ဖြင့်လုပ်ပြီး final test ကို မထိပါနှင့်။"),
        ("Bias, Variance and Overfitting", "underfitting, overfitting, regularization, and learning curves", "train_error = 0.05\nvalidation_error = 0.30\nprint(validation_error - train_error)", "Train/validation gap ကို ကြည့်ပြီး bias/variance ကို ခွဲခြမ်းပါ။"),
    ),
    9: _items(
        ("Tensors and PyTorch Basics", "tensor shapes, devices, and differentiable computation", "import torch\nx = torch.tensor([1.0, 2.0])\nprint(x.shape, x.mean())", "Tensor shape နှင့် device ကို စစ်ပြီး PyTorch computation စတင်ပါ။"),
        ("Datasets and DataLoaders", "batching, shuffling, and deterministic data input", "from torch.utils.data import DataLoader, TensorDataset\ndata = TensorDataset(torch.tensor([[1.0]]), torch.tensor([1]))\nprint(len(DataLoader(data, batch_size=1)))", "Dataset နှင့် DataLoader တွင် batch၊ shuffle နှင့် seed ကို မှတ်တမ်းတင်ပါ။"),
        ("Neural Network Modules", "layers, activations, parameters, and forward passes", "import torch.nn as nn\nmodel = nn.Sequential(nn.Linear(2, 4), nn.ReLU(), nn.Linear(4, 1))\nprint(model)", "Layer shape နှင့် activation ကို model objective အလိုက် ရွေးပါ။"),
        ("Loss, Optimizers and Training Loops", "loss functions, gradients, optimizer steps, and checkpoints", "import torch\nx = torch.tensor(2.0, requires_grad=True)\nloss = (x - 1) ** 2\nloss.backward()\nprint(x.grad)", "Training loop တွင် zero_grad၊ forward၊ loss၊ backward နှင့် step ကို စနစ်တကျထားပါ။"),
        ("Validation, Checkpoints and Reproducibility", "early stopping, checkpoints, seeds, and evaluation", "best = {'epoch': 3, 'val_loss': 0.18}\nprint(best)", "Checkpoint တွင် model version၊ data version နှင့် validation metric ပါစေ။"),
    ),
    10: _items(
        ("Image Tensors and Computer Vision", "image shape, normalization, augmentation, and privacy", "image = {'channels': 3, 'height': 32, 'width': 32}\nprint(image)", "Image shape၊ normalization နှင့် consent/privacy ကို စစ်ပါ။"),
        ("Convolutional Neural Networks", "kernels, feature maps, pooling, and visual inductive bias", "import torch.nn as nn\nlayer = nn.Conv2d(3, 8, kernel_size=3)\nprint(layer.out_channels)", "CNN layer shape နှင့် feature map ကို ရှင်းလင်းစွာ နားလည်ပါ။"),
        ("Text Cleaning and Tokenization", "tokens, vocabulary, normalization, and language limitations", "text = 'AI learns from data'\ntokens = text.lower().split()\nprint(tokens)", "Text preprocessing သည် language၊ privacy နှင့် token boundary ကို ထည့်သွင်းစဉ်းစားရသည်။"),
        ("Embeddings and Semantic Similarity", "vector representations, cosine similarity, and retrieval limits", "import math\na, b = [1, 0], [0.8, 0.2]\nscore = sum(x*y for x, y in zip(a, b)) / (math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(x*x for x in b)))\nprint(round(score, 3))", "Embedding similarity သည် relevance signal ဖြစ်ပြီး truth/causality မဟုတ်ပါ။"),
        ("Attention and Transformer Concepts", "queries, keys, values, context windows, and model limits", "tokens = ['what', 'is', 'attention']\nprint({'query': tokens[0], 'context': tokens[1:]})", "Attention နှင့် context limit ကို နားလည်ပြီး generated output ကို verify လုပ်ပါ။"),
    ),
    11: _items(
        ("Generative AI Boundaries", "generation, sampling, hallucination, and intended use", "response = {'text': 'synthetic answer', 'verified': False}\nprint(response)", "Generated text ကို verified fact ဟု မယူဆဘဲ human review ထည့်ပါ။"),
        ("Prompt Engineering and Evaluation", "clear instructions, constraints, test cases, and rubric evaluation", "prompt = {'task': 'summarize', 'format': 'three bullets', 'source': 'provided text'}\nprint(prompt)", "Prompt တွင် task၊ context၊ format နှင့် evaluation rubric ရှင်းပါစေ။"),
        ("Embeddings and Vector Search", "chunking, metadata filters, similarity search, and access control", "documents = [{'id': 'a', 'text': 'Python arrays', 'access': 'public'}]\nprint(documents)", "Vector index တွင် chunk metadata၊ tenant boundary နှင့် authorization ထားပါ။"),
        ("Retrieval-Augmented Generation", "retrieval, grounded context, citations, and prompt injection", "context = ['approved source paragraph']\nanswer = {'context_used': len(context), 'needs_review': True}\nprint(answer)", "RAG တွင် source citation၊ retrieval quality နှင့် prompt injection ကို စစ်ပါ။"),
        ("AI Agents and Tool Calling", "bounded tools, schemas, approvals, and audit logs", "tool = {'name': 'search_courses', 'requires_approval': False}\nprint(tool)", "Agent tool ကို schema၊ permission၊ rate limit နှင့် audit log ဖြင့် ကန့်သတ်ပါ။"),
        ("AI Safety and Red Team Evaluation", "privacy, abuse cases, refusal behavior, and incident response", "checks = ['privacy', 'prompt injection', 'unsafe output']\nprint(checks)", "Safety test case နှင့် incident response ကို deployment မတိုင်မီ စီစဉ်ပါ။"),
    ),
    12: _items(
        ("FastAPI Inference Contracts", "typed requests, validation, response schemas, and authorization", "from pydantic import BaseModel\nclass Features(BaseModel):\n    hours: float\nprint(Features(hours=4))", "Inference API တွင် typed input၊ validation၊ auth နှင့် model version ထည့်ပါ။"),
        ("Model Serialization and Versioning", "safe artifacts, compatibility, provenance, and rollback", "artifact = {'model_version': 'v1', 'data_version': 'demo-1'}\nprint(artifact)", "Untrusted pickle/artifact ကို မဖွင့်ဘဲ provenance နှင့် compatibility စစ်ပါ။"),
        ("Docker and Secure Deployment", "reproducible images, non-root runtime, health checks, and secrets", "container = {'user': 'non-root', 'health': '/healthz', 'secret_source': 'runtime'}\nprint(container)", "Container တွင် pinned dependency၊ non-root user၊ health check နှင့် secret manager သုံးပါ။"),
        ("Monitoring and MLOps", "latency, errors, drift, cost, feedback, and incident response", "metrics = {'latency_ms': 42, 'errors': 0, 'model_version': 'v1'}\nprint(metrics)", "Model မက service/data drift၊ latency၊ error နှင့် cost ကိုပါ monitor လုပ်ပါ။"),
        ("AI Testing and Governance", "data contracts, metric regression, API tests, review, and auditability", "assert {'schema': 'ok', 'authorization': 'checked'}['schema'] == 'ok'\nprint('governance check passed')", "AI system တွင် schema၊ metric၊ API၊ permission နှင့် audit ကို ခွဲစစ်ပါ။"),
        ("Professional Python AI Capstone", "end-to-end project scope, model card, evaluation, and safe handoff", "project = {'data': 'synthetic', 'baseline': True, 'review': 'required'}\nprint(project)", "Capstone တွင် baseline၊ model card၊ evaluation၊ safety review နှင့် rollback plan ပါရမည်။"),
    ),
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(module_number, title, focus, code, next_title):
    return f"""# {title}

## Introduction
This lesson develops {focus} as part of a reproducible Python for Artificial Intelligence workflow.

## Prerequisites
Complete the preceding lesson in Module {module_number} and use an isolated Python environment with documented package versions.

## Learning objectives
- Explain {focus} and its role in an AI system.
- Run a small synthetic example and inspect its assumptions.
- Identify leakage, privacy, safety, reproducibility, and deployment risks.

## Detailed theory
{title} is useful only when its input contract, transformation or model boundary, evaluation method, and operational limits are explicit. A metric or generated answer is evidence for a bounded question, not a guarantee of truth. Keep training, validation, and final evaluation evidence separate.

## Main concepts
Data provenance, license, row or token meaning, feature/target contract, deterministic seed, baseline, uncertainty, human review, and rollback are the core concepts. Never use private records in a tutorial dataset and never invent an accuracy or safety claim.

## Syntax / API / command
```python
{code}
```

## Practical examples
### Example 1 — inspect
Run the small synthetic example in the recorded Python and library environment. Inspect type, shape, schema, or output before interpreting it.

### Example 2 — extend
Change one input or parameter, predict the direction of change, and record the observed result. Keep learned transformations inside the training boundary.

### Example 3 — verify
Add a schema, shape, dtype, metric, permission, or output assertion. Compare with a simple baseline and explain discrepancies.

## Dataset and reproducibility notes
Use synthetic educational data unless an approved public source is documented. Record source, license, columns or tokens, target, split, random seed, Python version, package lock, and limitations. Do not place credentials or personal data in notebooks, prompts, logs, or model artifacts.

## Expected output
The example should produce a small inspectable result related to {focus}. Exact values can vary by compatible Python and library versions; verify direction, shape, schema, and assumptions instead of copying an unexplained score.

## Line-by-line explanation
1. The first lines define a bounded input or import a reviewed library.
2. The central operation applies {focus} without accessing private data or hidden final-test labels.
3. The final statement prints an inspectable result that should be compared with the stated expectation.

## Common mistakes
- Fitting preprocessing, selecting features, or tuning on the final test set.
- Confusing similarity, correlation, feature importance, or generated text with causation or verified fact.
- Omitting random seeds, package versions, dataset license, access control, or subgroup checks.
- Loading untrusted artifacts or exposing raw prompts, embeddings, or predictions.

## Best practices
- Use typed interfaces, pipelines, deterministic seeds, baselines, tests, and model cards.
- Report uncertainty, error costs, limitations, intended use, and human-approval requirements.
- Keep secrets server-side and add authorization, rate limits, monitoring, and rollback to services.

## AI safety considerations
Use approved data, protect privacy, test prompt injection and unsafe output, validate model artifacts, and require human review for high-impact decisions. The Academy displays examples and does not execute arbitrary student code or load untrusted artifacts.

## Exercises
1. Reproduce the example using only synthetic or approved data.
2. Change one parameter and explain the expected result before running it.
3. Add a validation check and document one leakage, privacy, or safety risk.

## Practical exercises
Build a small local experiment for {focus} with setup versions, expected behavior, observed behavior, and one limitation. Do not upload private data.

## Homework
Write a one-page experiment note containing the data card, code change, evaluation evidence, safety boundary, and review decision.

## Quiz
1. What boundary must remain separate from the final test set? Training and iterative tuning.
2. True or false: an AI score or generated answer alone proves production safety. False.
3. What supports reproducibility? Data version, code, environment, seed, metric, and limitations.

## Mini project
Add this concept to a synthetic Student Outcome Prediction or Document Assistant project. Include a baseline, evaluation plan, error analysis, access boundary, model card, and rollback owner. Do not claim production readiness from a toy result.

## Summary
You can now apply {focus} with explicit evidence, data, safety, and operations boundaries.

## Key takeaways
Reliable AI systems make inputs, transformations, evaluation, limitations, and human responsibility visible.

## References
- Python documentation: https://docs.python.org/3/
- scikit-learn User Guide: https://scikit-learn.org/stable/user_guide.html
- PyTorch documentation: https://pytorch.org/docs/stable/
- FastAPI documentation: https://fastapi.tiangolo.com/

## Next lesson
{next_title}
"""


def _content_mm(title, focus, code, mm, next_title):
    return f"""# {title}

## မိတ်ဆက်
ဤ lesson တွင် {mm} ကို Python for AI workflow အတွင်း လေ့လာပါမည်။

## လိုအပ်ချက်
Module {title} မတိုင်မီ lesson များကို ပြီးစီးထားပြီး isolated Python environment နှင့် package version များကို မှတ်တမ်းတင်ပါ။

## လေ့လာရမည့် ရည်မှန်းချက်များ
- {mm} ၏ AI system အတွင်းရှိ တာဝန်ကို ရှင်းပြနိုင်ရန်။
- Synthetic example ကို run ပြီး input၊ output နှင့် assumption များကို စစ်နိုင်ရန်။
- Leakage၊ privacy၊ safety နှင့် reproducibility risk များကို ဖော်ထုတ်နိုင်ရန်။

## အသေးစိတ်သီအိုရီ
{mm} ကို အသုံးပြုရာတွင် input contract၊ transformation/model boundary၊ evaluation နည်းလမ်းနှင့် limitation များကို ရှင်းလင်းစွာ သတ်မှတ်ရပါမည်။ Metric သို့မဟုတ် generated answer သည် အမှန်တရားအာမခံချက် မဟုတ်ပါ။ Training နှင့် final evaluation evidence ကို ခွဲထားပါ။

## အဓိကအယူအဆများ
Data provenance၊ license၊ feature/target သို့မဟုတ် token meaning၊ seed၊ baseline၊ uncertainty၊ human review နှင့် rollback ကို မှတ်တမ်းတင်ပါ။ Tutorial တွင် private data မသုံးပါနှင့်။ Score သို့မဟုတ် safety claim ကို မတီထွင်ပါနှင့်။

## Syntax / API / command
```python
{code}
```

## လက်တွေ့ဥပမာများ
ပထမဥပမာကို synthetic input ဖြင့် run ပါ။ ဒုတိယတွင် parameter တစ်ခုသာ ပြောင်းပြီး result direction ကို ကြိုခန့်မှန်းပါ။ တတိယတွင် shape၊ schema၊ permission သို့မဟုတ် output assertion ထည့်ပြီး baseline နှင့် နှိုင်းယှဉ်ပါ။

## Dataset နှင့် ပြန်လည်လုပ်ဆောင်နိုင်မှု
Approved source မရှိပါက synthetic data သုံးပါ။ Source၊ license၊ columns/tokens၊ target၊ split၊ random seed၊ Python version၊ package lock နှင့် limitation ကို မှတ်တမ်းတင်ပါ။ Secret နှင့် personal data ကို notebook၊ prompt၊ log ထဲ မထည့်ပါနှင့်။

## မျှော်မှန်းရလဒ်
Example သည် {mm} နှင့် သက်ဆိုင်သော inspect လုပ်နိုင်သည့် result ပေးရမည်။ Python/library version အလိုက် value ကွာနိုင်သော်လည်း shape၊ schema၊ direction နှင့် assumption ကို စစ်ပါ။

## Code ရှင်းလင်းချက်
အစတွင် bounded input သို့မဟုတ် reviewed library ကို သတ်မှတ်သည်။ အလယ်တွင် feature ကို အသုံးပြုပြီး private data နှင့် final test label ကို မထိတွေ့စေပါ။ နောက်ဆုံးတွင် result ကို print/assert လုပ်သည်။

## အများဆုံးမှားတတ်သောအချက်များ
- Final test set ကို preprocessing သို့မဟုတ် tuning တွင် အသုံးပြုခြင်း။
- Similarity၊ generated text သို့မဟုတ် feature importance ကို verified fact/causation ဟု ယူဆခြင်း။
- Seed၊ version၊ license၊ authorization နှင့် subgroup check မမှတ်တမ်းတင်ခြင်း။
- Untrusted artifact သို့မဟုတ် private prompt/embedding ကို မစစ်ဘဲ အသုံးပြုခြင်း။

## ကောင်းမွန်သောနည်းလမ်းများ
Typed interface၊ pipeline၊ deterministic seed၊ baseline၊ test၊ model card၊ authorization၊ rate limit၊ monitoring နှင့် rollback ကို အသုံးပြုပါ။ Uncertainty၊ limitation၊ intended use နှင့် human approval ကို ဖော်ပြပါ။

## AI safety considerations
Privacy၊ consent၊ data license၊ prompt injection၊ unsafe output၊ model artifact နှင့် high-impact decision များအတွက် human review ကို စစ်ပါ။ Academy သည် arbitrary code ကို execute မလုပ်ပါ။

## လေ့ကျင့်ခန်း
1. Synthetic သို့မဟုတ် approved data ဖြင့် example ကို ပြန်လုပ်ပါ။
2. Parameter တစ်ခု ပြောင်းပြီး result ကို မပြောင်းမီ ခန့်မှန်းပါ။
3. Validation check တစ်ခုနှင့် leakage/privacy/safety risk တစ်ခု ရေးပါ။

## Practical exercises
{focus} အတွက် local experiment တစ်ခုတည်ဆောက်ပြီး setup၊ expected/observed behavior နှင့် limitation ကို မှတ်တမ်းတင်ပါ။ Private data မတင်ပါနှင့်။

## အိမ်စာ
Dataset card၊ code change၊ evaluation evidence၊ safety boundary နှင့် review decision ပါသော experiment note တစ်စောင်ရေးပါ။

## Quiz
1. Final test set ကို ဘယ်အလုပ်မှ ခွဲထားရမလဲ။ Training နှင့် iterative tuning မှ ခွဲထားရမည်။
2. AI score သို့မဟုတ် generated answer တစ်ခုတည်းဖြင့် production safety ကို အာမခံနိုင်သလား။ မနိုင်ပါ။
3. Reproducibility အတွက် data version၊ code၊ environment၊ seed၊ metric နှင့် limitation ကို မှတ်တမ်းတင်ရမည်။

## Mini project
ဤ concept ကို synthetic Student Outcome Prediction သို့မဟုတ် Document Assistant project တွင် ထည့်ပါ။ Baseline၊ evaluation၊ error analysis၊ access boundary၊ model card နှင့် rollback owner ပါစေ။

## အနှစ်ချုပ်
{mm} ကို evidence၊ data၊ safety နှင့် operation boundary များဖြင့် အသုံးပြုနိုင်ပါပြီ။

## Key takeaways
Reliable AI system သည် input၊ transformation၊ evaluation၊ limitation နှင့် human responsibility ကို ရှင်းလင်းစွာ ဖော်ပြရသည်။

## References
Python၊ scikit-learn၊ PyTorch နှင့် FastAPI documentation ကို project version နှင့် ကိုက်ညီအောင် ဖတ်ပါ။

## နောက် lesson
{next_title}
"""


def _ensure_quiz(db, lesson, title, focus):
    quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
    if not quiz:
        quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review data contracts, evaluation evidence, reproducibility, privacy, and safety before retrying.", status="draft")
        db.add(quiz)
        db.flush()
    questions = [
        (f"Which practice supports {focus}?", ["Document assumptions and keep evaluation data separate", "Tune on the final test set", "Hide the data source"], "Document assumptions and keep evaluation data separate", "Reliable AI requires explicit data and evaluation boundaries."),
        ("True or false: an AI score alone proves production safety.", ["True", "False"], "False", "Safety also requires privacy, security, monitoring, authorization, and human review."),
        ("What should be recorded for reproducibility?", ["Data version, code, environment, seed, metric, and limitations", "Only the best score", "A private credential"], "Data version, code, environment, seed, metric, and limitations", "A run is reproducible only when inputs and decisions are documented."),
    ]
    for position, (prompt, options, answer, explanation) in enumerate(questions, 1):
        row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
        values = {"prompt": prompt, "question_type": "true_false" if options == ["True", "False"] else "multiple_choice", "options_json": json.dumps(options), "correct_answer": answer, "explanation": explanation}
        if not row:
            db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
        elif not row.prompt.strip():
            for key, value in values.items():
                setattr(row, key, value)


def _ensure_exercise(db, lesson, title, focus, mm):
    slug = f"python-ai-{lesson.slug}-practice"
    if db.scalar(select(CodingExercise).where(CodingExercise.slug == slug)):
        return
    db.add(CodingExercise(lesson_id=lesson.id, title=f"{title} practice", slug=slug, description_en=f"Use synthetic or approved data to practice {focus}. Record setup, expected behavior, observed result, evaluation evidence, and one limitation. Do not upload private data.", description_mm=f"Synthetic သို့မဟုတ် approved data ဖြင့် {mm} ကို လေ့ကျင့်ပါ။ Setup၊ expected/observed result၊ evidence နှင့် limitation ကို မှတ်တမ်းတင်ပါ။ Private data မတင်ပါနှင့်။", difficulty="intermediate", language="python", starter_code="# Work in an isolated local environment.\n", status="draft"))


def seed_python_ai_additional_curriculum(db, course):
    created_modules = 0
    created_lessons = 0
    for module_number, module_title in MODULES.items():
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_number))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_number)
            db.add(module)
            db.flush()
            created_modules += 1
        else:
            module.title = module_title
        specs = LESSONS[module_number]
        for position, (title, focus, code, mm) in enumerate(specs, 1):
            slug = f"{module_number:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == position))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=position, content_en="", content_mm="")
                db.add(lesson)
                db.flush()
                created_lessons += 1
            if not lesson.content_en or not lesson.content_en.strip():
                next_title = specs[position][0] if position < len(specs) else f"Module {module_number + 1} review" if module_number < 12 else "AI Engineer capstone review"
                lesson.title = title
                lesson.slug = lesson.slug or slug
                lesson.description = focus
                lesson.content_en = _content(module_number, title, focus, code, next_title)
                lesson.content_mm = _content_mm(title, focus, code, mm, next_title)
                lesson.duration_minutes = 50
                lesson.status = "draft"
                lesson.published = False
            elif not lesson.published and "## Practical exercises" not in lesson.content_en and "## Exercises" in lesson.content_en:
                lesson.content_en = lesson.content_en.replace("## Exercises", "## Practical exercises", 1)
            example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
            if not example:
                db.add(CodeExample(lesson_id=lesson.id, title=f"{title} example", language="python", filename=f"module_{module_number:02d}.py", code=code, description="Safe synthetic-data AI example. Run only in an isolated environment; the Academy does not execute arbitrary code or load untrusted artifacts.", position=1))
            _ensure_quiz(db, lesson, title, focus)
            _ensure_exercise(db, lesson, title, focus, mm)
    db.flush()
    return {"created_modules": created_modules, "created_lessons": created_lessons, "planned_lessons": sum(len(items) for items in LESSONS.values())}
