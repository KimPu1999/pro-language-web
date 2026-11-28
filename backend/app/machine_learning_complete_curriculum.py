"""Reviewable Machine Learning with Python curriculum batch.

The existing Module 1 is preserved by ``machine_learning_course_content``.
This module adds the missing Modules 2-12 as complete, unpublished drafts.
The examples use small synthetic data and never execute code on the Academy
host or load untrusted model artifacts.
"""

import json
import re

from sqlalchemy import select

from .models import CodeExample, CodingExercise, CourseModule, Lesson, LessonQuiz, QuizQuestion


MODULES = {
    2: "Python for Machine Learning",
    3: "Mathematics Foundations",
    4: "Data Preparation",
    5: "Regression",
    6: "Classification",
    7: "Ensemble Learning",
    8: "Unsupervised Learning",
    9: "Model Evaluation",
    10: "Feature Engineering",
    11: "Advanced Machine Learning",
    12: "Professional ML Engineering",
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


# title, focus, executable example, Burmese teaching note
LESSONS = {
    2: [
        ("Python Essentials for ML", "functions, comprehensions, typing, and reproducible data code", "def mean(values: list[float]) -> float:\n    return sum(values) / len(values)\n\nprint(mean([2.0, 4.0, 6.0]))", "Python function၊ list နှင့် type annotation များကို အသုံးပြုပြီး data transformation ကို ရှင်းလင်းစွာ ရေးသားပါ။"),
        ("NumPy Arrays and Shapes", "array dtype, shape, broadcasting, and vectorized computation", "import numpy as np\nx = np.array([[1.0, 2.0], [3.0, 4.0]])\nprint(x.shape, x.mean(axis=0))", "NumPy array ၏ shape နှင့် dtype ကို စစ်ပြီး vectorized computation ကို အသုံးပြုပါ။"),
        ("pandas DataFrames", "columns, indexes, missing values, and grouped summaries", "import pandas as pd\ndf = pd.DataFrame({'group': ['A', 'B', 'A'], 'score': [2, 4, 6]})\nprint(df.groupby('group')['score'].mean())", "pandas DataFrame ကို inspect၊ group နှင့် summary ပြုလုပ်ပါ။"),
        ("Matplotlib and Data Exploration", "plots, distributions, labels, and honest visual interpretation", "import matplotlib.pyplot as plt\nvalues = [2, 4, 6, 8]\nplt.plot(values)\nplt.xlabel('observation')\nplt.ylabel('value')\nplt.show()", "Visualization တွင် label၊ unit နှင့် data source ကို ဖော်ပြပြီး pattern ကို အလွန်အကျွံ မကောက်ချက်ချပါနှင့်။"),
        ("Exploratory Data Analysis", "profiling, distributions, correlations, and data questions", "import pandas as pd\ndf = pd.DataFrame({'hours': [1, 3, 5], 'passed': [0, 1, 1]})\nprint(df.describe(include='all'))", "Modeling မလုပ်မီ data profile၊ distribution၊ missingness နှင့် target relationship ကို စစ်ပါ။"),
    ],
    3: [
        ("Linear Algebra for Features", "vectors, matrices, dot products, and feature representations", "import numpy as np\nfeatures = np.array([[1., 2.], [3., 4.]])\nweights = np.array([.5, 1.])\nprint(features @ weights)", "Feature matrix၊ weight vector နှင့် dot product ၏ အဓိပ္ပါယ်ကို နားလည်ပါ။"),
        ("Statistics for ML", "mean, variance, distributions, and sampling uncertainty", "import numpy as np\nscores = np.array([60, 70, 80, 90])\nprint(scores.mean(), scores.std(ddof=1))", "Mean နှင့် variance ကို sample context နှင့်အတူ ဖတ်ပါ။"),
        ("Probability and Conditional Reasoning", "events, conditional probability, and model uncertainty", "from fractions import Fraction\npassed = Fraction(3, 5)\nprint(passed)", "Probability သည် certainty မဟုတ်ကြောင်းနှင့် conditional event များကို ရှင်းပြပါ။"),
        ("Calculus Intuition for Loss", "derivatives, slopes, and loss sensitivity", "def loss(weight: float, target: float = 3.0) -> float:\n    return (weight - target) ** 2\nprint(loss(2.0), loss(2.01))", "Loss curve ၏ slope နှင့် parameter ပြောင်းလဲမှုအပေါ် sensitivity ကို စဉ်းစားပါ။"),
        ("Gradient Descent and Optimization", "learning rate, gradients, convergence, and stopping criteria", "weight = 0.0\nfor _ in range(5):\n    gradient = 2 * (weight - 3)\n    weight -= 0.2 * gradient\nprint(round(weight, 3))", "Gradient descent တွင် learning rate၊ gradient နှင့် convergence ကို စစ်ပါ။"),
    ],
    4: [
        ("Loading and Documenting Datasets", "sources, licenses, row grain, target definitions, and dataset cards", "rows = [{'hours': 2, 'passed': 0}, {'hours': 5, 'passed': 1}]\nprint(len(rows), rows[0].keys())", "Dataset source၊ license၊ row meaning၊ target နှင့် intended use ကို မှတ်တမ်းတင်ပါ။"),
        ("Missing Values", "missingness mechanisms, imputation, and validation", "import pandas as pd\ndf = pd.DataFrame({'score': [80, None, 90]})\ndf['score'] = df['score'].fillna(df['score'].median())\nprint(df)", "Missing value ကို စစ်ပြီး train data အပေါ်တွင်သာ imputation rule fit လုပ်ပါ။"),
        ("Outlier Analysis", "robust statistics, legitimate extremes, and investigation", "import numpy as np\nvalues = np.array([10, 11, 12, 100])\nprint(np.median(values), np.percentile(values, 75))", "Outlier ကို အလိုအလျောက်ဖျက်မည့်အစား source နှင့် domain အဓိပ္ပါယ်ကို စစ်ပါ။"),
        ("Encoding Categorical Features", "one-hot encoding, unknown categories, and feature contracts", "from sklearn.preprocessing import OneHotEncoder\nencoder = OneHotEncoder(handle_unknown='ignore')\nprint(encoder.fit_transform([['red'], ['blue']]).toarray())", "Categorical value ကို encoder ဖြင့် ပြောင်းပြီး unknown category အတွက် policy ထားပါ။"),
        ("Feature Scaling", "standardization, normalization, and scale-sensitive models", "from sklearn.preprocessing import StandardScaler\nscaler = StandardScaler()\nprint(scaler.fit_transform([[1.], [2.], [3.]]).round(3))", "Scaling parameter ကို training partition မှသာ fit လုပ်ပြီး test leakage ကာကွယ်ပါ။"),
        ("Train Validation Test Splits", "stratification, temporal splits, and leakage prevention", "from sklearn.model_selection import train_test_split\nX_train, X_test = train_test_split([1, 2, 3, 4], test_size=.5, random_state=42)\nprint(X_train, X_test)", "Train၊ validation နှင့် test split ကို task နှင့် data collection time အလိုက် ရွေးပါ။"),
    ],
    5: [
        ("Linear Regression", "fitting a continuous target and interpreting coefficients", "from sklearn.linear_model import LinearRegression\nmodel = LinearRegression().fit([[1], [2], [3]], [2, 4, 6])\nprint(model.predict([[4]])[0])", "Continuous target အတွက် linear relationship နှင့် coefficient ကို အဓိပ္ပါယ်ဖော်ပါ။"),
        ("Multiple Regression", "multiple features, multicollinearity, and residual analysis", "from sklearn.linear_model import LinearRegression\nmodel = LinearRegression().fit([[1, 0], [2, 1], [3, 1]], [2, 5, 7])\nprint(model.coef_)", "Feature များစွာပါဝင်သော regression တွင် collinearity နှင့် residual ကို စစ်ပါ။"),
        ("Regularization", "Ridge, Lasso, bias-variance trade-offs, and feature selection", "from sklearn.linear_model import Ridge\nmodel = Ridge(alpha=1.0).fit([[1], [2], [3]], [2, 4, 6])\nprint(model.predict([[4]])[0])", "Regularization strength ကို validation data ဖြင့် ရွေးပြီး coefficient shrinkage ကို နားလည်ပါ။"),
        ("Regression Metrics and Prediction Project", "MAE, RMSE, R-squared, residuals, and a bounded prediction workflow", "from sklearn.metrics import mean_absolute_error\ny_true = [10, 12, 14]\ny_pred = [9, 13, 15]\nprint(mean_absolute_error(y_true, y_pred))", "Regression metric ကို business error cost နှင့် ကိုက်ညီအောင် ရွေးပါ။"),
    ],
    6: [
        ("Logistic Regression", "probabilities, decision thresholds, and calibrated classification", "from sklearn.linear_model import LogisticRegression\nmodel = LogisticRegression().fit([[0], [1], [2], [3]], [0, 0, 1, 1])\nprint(model.predict_proba([[1.5]]).round(3))", "Logistic regression output သည် probability ဖြစ်ပြီး threshold သည် business decision ဖြစ်သည်။"),
        ("K-Nearest Neighbors", "distance, scaling, neighborhood size, and local decisions", "from sklearn.neighbors import KNeighborsClassifier\nmodel = KNeighborsClassifier(n_neighbors=3).fit([[0], [1], [4]], [0, 0, 1])\nprint(model.predict([[2]]))", "KNN တွင် distance scale နှင့် neighbor count သည် result ကို သက်ရောက်သည်။"),
        ("Decision Trees", "splits, depth, interpretability, and overfitting", "from sklearn.tree import DecisionTreeClassifier\nmodel = DecisionTreeClassifier(max_depth=2, random_state=42).fit([[0], [1], [4]], [0, 0, 1])\nprint(model.predict([[2]]))", "Tree depth ကို ထိန်းပြီး overfitting နှင့် interpretability ကို ချိန်ညှိပါ။"),
        ("Naive Bayes", "conditional independence assumptions and text-friendly baselines", "from sklearn.naive_bayes import GaussianNB\nmodel = GaussianNB().fit([[1, 0], [0, 1]], [1, 0])\nprint(model.predict([[1, 1]]))", "Naive Bayes ၏ independence assumption နှင့် baseline အသုံးဝင်မှုကို နားလည်ပါ။"),
        ("Support Vector Machines", "margins, kernels, scaling, and regularization", "from sklearn.svm import SVC\nmodel = SVC(kernel='linear').fit([[0], [1], [3]], [0, 0, 1])\nprint(model.predict([[2]]))", "SVM တွင် margin၊ kernel နှင့် scaling ၏ သက်ရောက်မှုကို စမ်းသပ်ပါ။"),
        ("Classification Metrics", "confusion matrices, precision, recall, F1, and ROC-AUC", "from sklearn.metrics import classification_report\ny_true = [0, 0, 1, 1]\ny_pred = [0, 1, 1, 1]\nprint(classification_report(y_true, y_pred, zero_division=0))", "Metric တစ်ခုတည်းမဟုတ်ဘဲ error cost နှင့် confusion matrix ကို ဖတ်ပါ။"),
    ],
    7: [
        ("Bagging and Random Forests", "bootstrap samples, decorrelated trees, and feature importance", "from sklearn.ensemble import RandomForestClassifier\nmodel = RandomForestClassifier(n_estimators=10, random_state=42).fit([[0], [1], [3]], [0, 0, 1])\nprint(model.predict([[2]]))", "Random forest သည် tree များစွာ၏ variance ကို လျှော့ပေးနိုင်သော်လည်း explanation ကို စစ်ပါ။"),
        ("Boosting", "sequential error correction, learning rate, and weak learners", "from sklearn.ensemble import GradientBoostingRegressor\nmodel = GradientBoostingRegressor(random_state=42, n_estimators=10).fit([[0], [1], [2]], [0, 1, 2])\nprint(model.predict([[1.5]]))", "Boosting သည် ယခင် error များကို ပြင်ဆင်သော learner များကို ဆက်တိုက်တည်ဆောက်သည်။"),
        ("Gradient Boosting", "regularization, trees, validation, and feature effects", "from sklearn.ensemble import HistGradientBoostingClassifier\nmodel = HistGradientBoostingClassifier(random_state=42).fit([[0], [1], [3]], [0, 0, 1])\nprint(model.predict([[2]]))", "Gradient boosting တွင် depth၊ learning rate နှင့် early stopping ကို validation ဖြင့် ထိန်းပါ။"),
        ("Model Comparison", "baselines, repeated validation, cost-aware selection, and reproducibility", "models = {'baseline': 0.5, 'candidate': 0.75}\nprint(max(models, key=models.get))", "Model ရွေးချယ်ရာတွင် score၊ variance၊ cost၊ latency နှင့် maintainability ကို ပေါင်းစပ်စဉ်းစားပါ။"),
    ],
    8: [
        ("K-Means Clustering", "centroids, initialization, scaling, and cluster interpretation", "from sklearn.cluster import KMeans\nmodel = KMeans(n_clusters=2, random_state=42, n_init=10).fit([[0], [1], [9], [10]])\nprint(model.labels_)", "K-means cluster သည် ground-truth label မဟုတ်ဘဲ similarity grouping ဖြစ်သည်။"),
        ("Hierarchical Clustering", "linkage, dendrograms, and choosing a cut", "from sklearn.cluster import AgglomerativeClustering\nmodel = AgglomerativeClustering(n_clusters=2).fit([[0], [1], [9], [10]])\nprint(model.labels_)", "Hierarchical clustering တွင် linkage နှင့် tree cut ကို domain အဓိပ္ပါယ်နှင့် စစ်ပါ။"),
        ("DBSCAN", "density, epsilon, core points, and noise", "from sklearn.cluster import DBSCAN\nmodel = DBSCAN(eps=1.5, min_samples=2).fit([[0], [1], [10]])\nprint(model.labels_)", "DBSCAN သည် density နှင့် noise point ကို ဖော်ထုတ်နိုင်သည်။"),
        ("PCA and Dimensionality Reduction", "variance directions, projection, and visualization limits", "from sklearn.decomposition import PCA\nmodel = PCA(n_components=1).fit([[1, 2], [2, 4], [3, 6]])\nprint(model.transform([[4, 8]]).round(3))", "PCA သည် information ကို projection လုပ်ပြီး original meaning အားလုံးကို မထိန်းနိုင်ပါ။"),
        ("Unsupervised Learning Review", "cluster validation, stability, and human interpretation", "labels = ['cluster-a', 'cluster-a', 'cluster-b']\nprint({label: labels.count(label) for label in set(labels)})", "Unsupervised result ကို metric တစ်ခုတည်းမဟုတ်ဘဲ stability နှင့် domain review ဖြင့် စစ်ပါ။"),
    ],
    9: [
        ("Cross-Validation", "folds, stratification, grouped data, and temporal validation", "from sklearn.model_selection import cross_val_score\nfrom sklearn.linear_model import LogisticRegression\nprint(cross_val_score(LogisticRegression(), [[0], [1], [2], [3]], [0, 0, 1, 1], cv=2))", "Cross-validation fold တစ်ခုစီတွင် preprocessing နှင့် model fit ကို training portion အတွင်းသာ လုပ်ပါ။"),
        ("Confusion Matrix", "true positives, false positives, false negatives, and thresholds", "from sklearn.metrics import confusion_matrix\nprint(confusion_matrix([0, 0, 1, 1], [0, 1, 1, 0]))", "Confusion matrix မှ error အမျိုးအစားများကို တိုင်းပြီး threshold ကို ပြန်ရွေးပါ။"),
        ("Precision Recall and F1", "retrieval trade-offs and imbalanced targets", "from sklearn.metrics import precision_score, recall_score, f1_score\ny_true=[0,0,1,1]; y_pred=[0,1,1,1]\nprint(precision_score(y_true,y_pred), recall_score(y_true,y_pred), f1_score(y_true,y_pred))", "False positive နှင့် false negative cost အလိုက် precision/recall ကို ချိန်ပါ။"),
        ("ROC-AUC and Calibration", "ranking quality, probability quality, and threshold selection", "from sklearn.metrics import roc_auc_score\nprint(roc_auc_score([0, 0, 1, 1], [0.1, 0.4, 0.6, 0.9]))", "ROC-AUC သည် ranking ကိုတိုင်းပြီး probability calibration ကို အစားမထိုးပါ။"),
        ("Bias Variance and Class Imbalance", "underfitting, overfitting, resampling, and subgroup evidence", "from collections import Counter\nlabels = [0, 0, 0, 1]\nprint(Counter(labels))", "Bias/variance နှင့် imbalance ကို validation၊ subgroup metric နှင့် baseline ဖြင့် စစ်ပါ။"),
    ],
    10: [
        ("Feature Selection", "domain-informed selection, leakage checks, and stability", "from sklearn.feature_selection import SelectKBest, f_classif\nX = [[1, 3], [2, 2], [3, 1], [4, 0]]\nprint(SelectKBest(f_classif, k=1).fit_transform(X, [0,0,1,1]))", "Feature selection ကို training fold အတွင်းသာ fit လုပ်ပြီး selection stability စစ်ပါ။"),
        ("Feature Transformations", "log transforms, bins, interactions, and domain semantics", "import numpy as np\nvalues = np.array([1., 10., 100.])\nprint(np.log1p(values).round(3))", "Transform သည် skew ကို လျှော့နိုင်သော်လည်း feature meaning နှင့် inverse interpretation ကို မမေ့ပါနှင့်။"),
        ("Scikit-Learn Pipelines", "leakage-resistant preprocessing and estimator composition", "from sklearn.pipeline import make_pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\npipe = make_pipeline(StandardScaler(), LogisticRegression())\nprint(pipe.steps)", "Pipeline သည် preprocessing နှင့် estimator ကို တစ်ခုတည်းသော fit boundary အဖြစ် ထိန်းသည်။"),
        ("ColumnTransformer and Tuning", "mixed numeric/categorical columns, grids, and nested validation", "from sklearn.compose import ColumnTransformer\nfrom sklearn.preprocessing import StandardScaler, OneHotEncoder\npre = ColumnTransformer([('num', StandardScaler(), [0]), ('cat', OneHotEncoder(handle_unknown='ignore'), [1])])\nprint(pre.transformers)", "Numeric/categorical feature များကို ColumnTransformer ဖြင့် သီးခြား preprocess လုပ်ပြီး tuning ကို validation ဖြင့် စီမံပါ။"),
    ],
    11: [
        ("Model Interpretability", "global importance, local explanations, and causal limits", "feature_names = ['hours', 'quizzes']\nimportance = [0.7, 0.3]\nprint(dict(zip(feature_names, importance)))", "Importance သည် association ဖြစ်ပြီး causal effect သို့မဟုတ် fairness proof မဟုတ်ပါ။"),
        ("Data Drift and Model Monitoring", "input drift, performance drift, alerts, and retraining evidence", "baseline = {'mean_hours': 3.0}\ncurrent = {'mean_hours': 3.6}\nprint(current['mean_hours'] - baseline['mean_hours'])", "Drift ကို input distribution၊ label delay နှင့် business outcome နှင့်အတူ စောင့်ကြည့်ပါ။"),
        ("Reproducibility and Experiment Tracking", "seeds, artifacts, dataset versions, and experiment metadata", "run = {'seed': 42, 'data_version': 'demo-v1', 'metric': 'mae'}\nprint(run)", "Experiment တစ်ခုစီတွင် code၊ data version၊ seed၊ metric နှင့် environment ကို သိမ်းပါ။"),
        ("Responsible ML and Model Cards", "privacy, fairness, intended use, limitations, and human oversight", "model_card = {'intended_use': 'education demo', 'not_for': 'high-stakes decisions'}\nprint(model_card)", "Model card တွင် intended use၊ limitation၊ subgroup evidence နှင့် human review ကို ဖော်ပြပါ။"),
    ],
    12: [
        ("Model Serialization", "safe artifact formats, version compatibility, and provenance", "artifact = {'model': 'demo', 'library_version': 'record-me'}\nprint(artifact)", "Model artifact ကို untrusted pickle အဖြစ် မဖွင့်ဘဲ provenance နှင့် version ကို စစ်ပါ။"),
        ("FastAPI Inference Service", "request validation, prediction contracts, and safe responses", "from pydantic import BaseModel\nclass Features(BaseModel):\n    hours: float\nprint(Features(hours=4))", "Inference API သည် typed input၊ validation၊ authorization နှင့် model version ကို သတ်မှတ်ရမည်။"),
        ("Docker and Deployment", "repeatable images, non-root runtime, health checks, and rollback", "image = {'base': 'pinned', 'user': 'non-root', 'health': '/healthz'}\nprint(image)", "Deployment image တွင် pinned dependency၊ non-root user၊ health check နှင့် rollback plan ပါရမည်။"),
        ("Testing ML Systems", "data contracts, pipeline tests, metric regression, and API tests", "assert len([1, 2, 3]) == 3\nprint('contract test passed')", "ML test တွင် schema၊ preprocessing၊ metric regression နှင့် API contract ကို ခွဲစစ်ပါ။"),
        ("Monitoring and MLOps Fundamentals", "feature pipelines, feedback loops, cost, reliability, and incident response", "service = {'latency_ms': 42, 'errors': 0, 'model_version': 'v1'}\nprint(service)", "MLOps သည် model တင်မက data၊ service၊ monitoring နှင့် incident response ကို စီမံသည်။"),
    ],
}


def _content(module_number, position, title, focus, code, next_title):
    return f"""# {title}

## Introduction
This lesson develops {focus} as part of a reproducible Machine Learning with Python workflow.

## Prerequisites
Complete the preceding lesson in Module {module_number} and use an isolated Python environment with documented package versions.

## Learning objectives
- Explain {focus} and its role in a real ML system.
- Run a small synthetic-data example and inspect its assumptions.
- Evaluate leakage, reproducibility, privacy, and reliability risks.

## Detailed theory
{title} is useful only when its data contract, target or transformation, evaluation method, and operational limits are explicit. Separate training evidence from validation and test evidence. A metric or visual pattern is evidence for a bounded question, not a guarantee of real-world correctness.

## Main concepts
Data source and license, row grain, feature/target meaning, preprocessing boundary, deterministic seed, baseline, uncertainty, and human review are the core concepts. Never use private records in a tutorial dataset and never report an invented accuracy score.

## Syntax / API / command
```python
{code}
```

## Practical examples
### Example 1 — inspect
Run the example with the recorded Python and library versions using only the small synthetic values shown above.

### Example 2 — extend
Change one input or parameter, predict the direction of change before running, and record the observed result. Keep the transformation inside the training boundary when it learns parameters.

### Example 3 — verify
Add a shape, dtype, schema, metric, or output assertion. Compare the result with a simple baseline and explain any discrepancy instead of hiding it.

## Dataset and reproducibility notes
Use synthetic educational data unless an approved public source is documented. Record the source URL, license, columns, target, split strategy, random seed, Python version, package lock, and known limitations. For classification, inspect class balance; for regression, inspect target distribution; for unsupervised work, record the interpretation method.

## Expected output
The example should complete without changing the input contract and should print or produce a small, inspectable result related to {focus}. Exact floating-point output can vary with compatible library versions; verify the shape, direction, and assumptions rather than inventing a score.

## Line-by-line explanation
1. The first lines define a bounded input or import a reviewed library.
2. The central operation applies {focus} without accessing private data or the final test labels.
3. The final statement prints an inspectable result that should be compared with the stated expectation.

## Common mistakes
- Fitting preprocessing, selecting features, or tuning on the final test set.
- Confusing correlation, feature importance, or cluster membership with causation.
- Omitting random seeds, package versions, dataset license, or subgroup checks.
- Loading untrusted model artifacts or exposing raw predictions without authorization.

## Best practices
- Use scikit-learn Pipelines and ColumnTransformer where applicable.
- Keep train/validation/test boundaries explicit and choose task-appropriate metrics.
- Report uncertainty, error costs, limitations, and human-approval requirements.
- Test schemas, transformations, model behavior, API contracts, and monitoring alerts.

## Practical exercises
1. Reproduce the example with the documented synthetic input.
2. Change one parameter and explain the result before running it.
3. Add a validation check and write one leakage or privacy risk for this lesson.

## Homework
Create a one-page experiment note containing the dataset card, setup versions, code change, expected behavior, observed behavior, metric or validation evidence, and limitation.

## Quiz
1. What boundary must remain separate from the final test set? Training and iterative tuning.
2. True or false: an ML score alone proves that a model is safe for production. False.
3. What should be documented for reproducibility? Data version, code, environment, seed, metric, and limitations.

## Mini project
Add this concept to a synthetic Student Grade Prediction or Customer Segmentation notebook. Include a baseline, validation plan, data card, error analysis, and a review decision; do not claim production readiness from a toy result.

## Summary
You can now apply {focus} with a reproducible evidence boundary and explain what the result does not prove.

## References
- scikit-learn User Guide: https://scikit-learn.org/stable/user_guide.html
- NumPy documentation: https://numpy.org/doc/
- pandas documentation: https://pandas.pydata.org/docs/
- Use the versions pinned by the project before adopting an API.

## Next lesson
{next_title}
"""


def _content_mm(title, focus, code, mm, next_title):
    return f"""# {title}

## မိတ်ဆက်
ဤသင်ခန်းစာတွင် {mm} ကို Machine Learning workflow အတွင်း လေ့လာပါမည်။

## လိုအပ်ချက်
Python virtual environment နှင့် ယခင် module lesson ကို ပြီးစီးထားပါ။ Package version များကို မှတ်တမ်းတင်ပါ။

## လေ့လာရမည့် ရည်မှန်းချက်များ
- သင်ခန်းစာ၏ အဓိကအယူအဆနှင့် ML system အတွင်းရှိ တာဝန်ကို ရှင်းပြနိုင်ရန်။
- Synthetic data ဖြင့် example ကို run ပြီး assumption များကို စစ်နိုင်ရန်။
- Leakage၊ reproducibility၊ privacy နှင့် reliability risk များကို ဖော်ထုတ်နိုင်ရန်။

## အသေးစိတ်သီအိုရီ
{mm} သည် data contract၊ transformation boundary၊ evaluation method နှင့် operational limitation များကို ရှင်းလင်းစွာ သတ်မှတ်မှသာ အသုံးဝင်ပါသည်။ Training evidence ကို validation/test evidence နှင့် မရောပါနှင့်။ Metric သည် အမှန်တရားအာမခံချက် မဟုတ်ပါ။

## အဓိကအယူအဆများ
Data source၊ license၊ row meaning၊ feature/target၊ seed၊ baseline၊ uncertainty နှင့် human review ကို မှတ်တမ်းတင်ပါ။ Tutorial တွင် private record မသုံးပါနှင့်။ Accuracy score ကို မတီထွင်ပါနှင့်။

## Syntax / API / command
Executable code၊ library name နှင့် identifier များကို မူရင်းအတိုင်း ထားပါသည်။
```python
{code}
```

## လက်တွေ့ဥပမာများ
ပထမဥပမာကို run ပါ။ ဒုတိယတွင် parameter တစ်ခုသာ ပြောင်းပြီး result direction ကို ကြိုခန့်မှန်းပါ။ တတိယတွင် shape၊ dtype၊ schema သို့မဟုတ် metric assertion တစ်ခုထည့်ပြီး baseline နှင့် နှိုင်းယှဉ်ပါ။

## Dataset နှင့် ပြန်လည်လုပ်ဆောင်နိုင်မှု
Approved public source မရှိပါက synthetic educational data သုံးပါ။ Source URL၊ license၊ columns၊ target၊ split၊ random seed၊ Python version၊ package lock နှင့် limitation ကို မှတ်တမ်းတင်ပါ။

## မျှော်မှန်းရလဒ်
Example သည် {mm} နှင့် သက်ဆိုင်သော inspect လုပ်နိုင်သည့် result တစ်ခုကို ပေးရမည်။ Floating-point output သည် library version အလိုက် အနည်းငယ်ကွာနိုင်သော်လည်း shape၊ direction နှင့် assumption ကို စစ်ပါ။

## Code ရှင်းလင်းချက်
အစတွင် bounded input သို့ library ကို သတ်မှတ်သည်။ အလယ်တွင် feature ကို အသုံးပြုပြီး final test label မထိတွေ့စေရန် ထိန်းသည်။ နောက်ဆုံးတွင် result ကို print/assert လုပ်သည်။

## အများဆုံးမှားတတ်သောအချက်များ
- Final test set ကို preprocessing၊ feature selection သို့မဟုတ် tuning တွင် အသုံးပြုခြင်း။
- Feature importance၊ correlation သို့ cluster ကို causation ဟု ယူဆခြင်း။
- Seed၊ package version၊ license နှင့် subgroup check မမှတ်တမ်းတင်ခြင်း။
- Untrusted model artifact ကို load လုပ်ခြင်း။

## ကောင်းမွန်သောနည်းလမ်းများ
Pipeline၊ ColumnTransformer၊ explicit split၊ task-appropriate metric နှင့် human review သုံးပါ။ Error cost၊ uncertainty နှင့် limitation ကို ဖော်ပြပါ။

## လေ့ကျင့်ခန်း
1. Synthetic input ဖြင့် example ကို ပြန်လုပ်ပါ။
2. Parameter တစ်ခု ပြောင်းပြီး မပြောင်းမီ result ကို ခန့်မှန်းပါ။
3. Validation check တစ်ခုနှင့် leakage/privacy risk တစ်ခု ရေးပါ။

## အိမ်စာ
Dataset card၊ environment version၊ code change၊ expected/observed behavior၊ evidence နှင့် limitation ပါသော experiment note တစ်စောင်ရေးပါ။

## Quiz
1. Final test set ကို ဘယ်အလုပ်မှ ခွဲထားရမလဲ။ Training နှင့် iterative tuning မှ ခွဲထားရမည်။
2. ML score တစ်ခုတည်းဖြင့် production safety ကို အာမခံနိုင်သလား။ မနိုင်ပါ။
3. Reproducibility အတွက် data version၊ code၊ environment၊ seed၊ metric နှင့် limitation ကို မှတ်တမ်းတင်ရမည်။

## Mini project
ဤ concept ကို synthetic Student Grade Prediction သို့မဟုတ် Customer Segmentation project တွင် ထည့်ပါ။ Baseline၊ validation plan၊ data card နှင့် error analysis ပါစေ။ Toy result ကို production-ready ဟု မဆိုပါနှင့်။

## အနှစ်ချုပ်
{mm} ကို reproducible evidence boundary ဖြင့် အသုံးပြုပြီး result က မည်သည့်အရာကို မသက်သေပြနိုင်ကြောင်း ရှင်းပြနိုင်ပါပြီ။

## ရည်ညွှန်းချက်များ
- scikit-learn User Guide: https://scikit-learn.org/stable/user_guide.html
- NumPy documentation: https://numpy.org/doc/
- pandas documentation: https://pandas.pydata.org/docs/

## နောက် lesson
{next_title}
"""


def _ensure_quiz(db, lesson, title, focus):
    quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
    if not quiz:
        quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the data boundary, evaluation evidence, and responsible ML guidance before retrying.", status="draft")
        db.add(quiz)
        db.flush()
    questions = [
        (f"Which practice supports {focus}?", ["Document assumptions and keep evaluation data separate", "Tune on the final test set", "Hide the dataset source"], "Document assumptions and keep evaluation data separate", "Reliable ML requires an explicit data and evaluation boundary."),
        ("True or false: an ML score alone proves production safety.", ["True", "False"], "False", "Safety also requires privacy, fairness, monitoring, authorization, and human review."),
        ("What should be recorded for reproducibility?", ["Data version, code, environment, seed, metric, and limitations", "Only the best score", "A private credential"], "Data version, code, environment, seed, metric, and limitations", "A run is reproducible only when its inputs and decisions are documented."),
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
    slug = f"machine-learning-{lesson.slug}-practice"
    if db.scalar(select(CodingExercise).where(CodingExercise.slug == slug)):
        return
    db.add(CodingExercise(lesson_id=lesson.id, title=f"{title} practice", slug=slug, description_en=f"Use synthetic data to practice {focus}. Record setup, expected behavior, observed result, validation evidence, and one limitation. Do not upload private data.", description_mm=f"Synthetic data ဖြင့် {mm} ကို လေ့ကျင့်ပါ။ Setup၊ expected/observed result၊ validation evidence နှင့် limitation ကို မှတ်တမ်းတင်ပါ။ Private data မတင်ပါနှင့်။", difficulty="intermediate", language="python", starter_code="# Work in an isolated local environment.\n", status="draft"))


def seed_machine_learning_additional_curriculum(db, course):
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
                next_title = specs[position][0] if position < len(specs) else f"Module {module_number + 1} review" if module_number < 12 else "Machine Learning capstone review"
                lesson.title = title
                lesson.slug = lesson.slug or slug
                lesson.description = focus
                lesson.content_en = _content(module_number, position, title, focus, code, next_title)
                lesson.content_mm = _content_mm(title, focus, code, mm, next_title)
                lesson.duration_minutes = 50
                lesson.status = "draft"
                lesson.published = False
            elif not lesson.published and "## Practical exercises" not in lesson.content_en and "## Exercises" in lesson.content_en:
                # Repair only the generated draft heading so the quality audit
                # recognizes the exercise section; do not rewrite authored text.
                lesson.content_en = lesson.content_en.replace("## Exercises", "## Practical exercises", 1)
            example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
            values = {"title": f"{title} example", "language": "python", "filename": f"module_{module_number:02d}.py", "code": code, "description": "Synthetic-data ML example. Run only in an isolated environment; no untrusted code is executed by the Academy.", "position": 1}
            if not example:
                db.add(CodeExample(lesson_id=lesson.id, **values))
            _ensure_quiz(db, lesson, title, focus)
            _ensure_exercise(db, lesson, title, focus, mm)
    db.flush()
    return {"created_modules": created_modules, "created_lessons": created_lessons, "planned_lessons": sum(len(items) for items in LESSONS.values())}
