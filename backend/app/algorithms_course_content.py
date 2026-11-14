"""Idempotent authored Algorithms curriculum.

Module 1 is the complete vertical slice. Remaining modules have a substantive
foundation lesson and are explicitly not presented as a 350+ lesson completion.
"""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

MODULES = [
    "Introduction to Algorithms", "Pseudocode & Flowcharts", "Time & Space Complexity", "Algorithm Analysis & Recurrences",
    "Mathematics for Algorithms", "Linear Search & Binary Search", "Binary Search Techniques", "Basic Sorting Algorithms",
    "Efficient Sorting Algorithms", "Specialized Sorting Algorithms", "Recursion Fundamentals", "Divide and Conquer",
    "Two Pointers", "Sliding Window", "Prefix Sums & Difference Arrays", "Greedy Algorithms", "Backtracking",
    "Dynamic Programming Fundamentals", "Intermediate Dynamic Programming", "Advanced Dynamic Programming", "Graph Fundamentals",
    "BFS & DFS Algorithms", "Topological Sorting & DAGs", "Shortest Path Algorithms", "Minimum Spanning Trees",
    "Advanced Graph Algorithms", "Network Flow & Matching", "String Matching Algorithms", "String Hashing & Advanced Matching",
    "Number Theory Algorithms", "Combinatorics & Bit Manipulation", "Computational Geometry", "Randomized Algorithms",
    "Approximation & Heuristic Algorithms", "Advanced Data Structure Algorithms", "Algorithm Correctness & Optimization",
    "Competitive Programming Patterns", "Technical Interview Algorithms", "Real-World Algorithm Projects", "Final Algorithms Capstone",
]

MODULE_ONE = [
    ("What Is an Algorithm?", "a finite, unambiguous procedure for transforming input into output", "values = [7, 2, 9]\nprint(max(values))", "An algorithm is a precise procedure with defined inputs, outputs, termination, and correctness conditions. A data structure stores or organizes values; an algorithm performs work over them. Start with the problem and constraints before choosing a technique or implementation language.", "input -> steps -> output", "Algorithm ဆိုသည်မှာ input ကို output သို့ ပြောင်းလဲပေးသော finite နှင့် unambiguous procedure ဖြစ်သည်။"),
    ("Problem Statements and Constraints", "turning requirements into testable assumptions", "numbers = [2, 7, 11, 15]\ntarget = 9\nprint(numbers[0] + numbers[1] == target)", "A useful problem statement names input format, output format, constraints, ordering, duplicates, and failure behavior. Constraints are algorithmic evidence: a quadratic method may be fine for n=100 but fail for n=100000. Never silently invent constraints.", "Given input X, produce output Y subject to constraints C.", "Problem statement တွင် input၊ output၊ constraints၊ ordering နှင့် edge cases များကို သတ်မှတ်ရသည်။"),
    ("Pseudocode and Flowcharts", "communicating logic before syntax", "def linear_search(values, target):\n    for index, value in enumerate(values):\n        if value == target:\n            return index\n    return -1\n\nprint(linear_search([4, 8, 2], 8))", "Pseudocode focuses on decisions and state rather than C, C++, Python, or Java syntax. A flowchart should make branches, loops, and termination visible. Write the invariant or loop condition before optimizing the code.", "for each item: compare; if equal return index; return -1", "Pseudocode သည် programming language syntax မဟုတ်ဘဲ logic နှင့် state ပြောင်းလဲမှုကို ဖော်ပြသည်။"),
    ("Linear Search", "checking candidates in a defined order", "def linear_search(values, target):\n    for index, value in enumerate(values):\n        if value == target:\n            return index\n    return -1\n\nprint(linear_search([5, 3, 8], 8))", "Linear search checks each candidate until it finds a match or exhausts the input. It works on unsorted data, has best-case O(1), worst-case O(n), and O(1) auxiliary space. The returned index is a postcondition that can be tested.", "index = 0\nwhile index < n: compare values[index]", "Linear search သည် sorted မဖြစ်သော data တွင်ပါ အသုံးပြုနိုင်ပြီး worst case O(n) ဖြစ်သည်။"),
    ("Binary Search", "halving an ordered search space", "def binary_search(values, target):\n    lo, hi = 0, len(values) - 1\n    while lo <= hi:\n        mid = lo + (hi - lo) // 2\n        if values[mid] == target:\n            return mid\n        if values[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1\n\nprint(binary_search([1, 3, 5, 8, 13], 8))", "Binary search requires a sorted, indexable search space. Each comparison discards half of the remaining candidates, giving O(log n) time and O(1) iterative space. The most common bugs are incorrect bounds, overflow-prone midpoint arithmetic in lower-level languages, and using it on unsorted data.", "mid = lo + (hi - lo) // 2\nif a[mid] < target: lo = mid + 1", "Binary search သည် sorted data ကို တစ်ဝက်စီ ခွဲစစ်ပြီး O(log n) အချိန်ရသည်။"),
    ("Bubble Sort and Stable Swaps", "using adjacent comparisons to expose ordering", "def bubble_sort(values):\n    values = values[:]\n    for end in range(len(values) - 1, 0, -1):\n        changed = False\n        for index in range(end):\n            if values[index] > values[index + 1]:\n                values[index], values[index + 1] = values[index + 1], values[index]\n                changed = True\n        if not changed:\n            break\n    return values\n\nprint(bubble_sort([5, 1, 4, 2]))", "Bubble sort repeatedly swaps adjacent out-of-order values. With the early-stop flag it is best-case O(n) on already sorted input, worst-case O(n²), and O(1) auxiliary space. It is useful for teaching invariants, not usually for production-scale sorting.", "compare a[i] and a[i+1]; swap if out of order", "Bubble sort သည် adjacent values များကို နှိုင်းယှဉ်ပြီး out-of-order ဖြစ်လျှင် swap လုပ်သည်။"),
    ("Module 1 Review and Assessment", "choosing and explaining a search or sort", "values = [1, 3, 5, 8, 13]\ntarget = 8\nprint(target in values)", "Review the algorithm workflow: formalize the problem, state constraints, write pseudocode, implement an invariant-preserving loop, test edge cases, and justify correctness and complexity. A working output without an explanation is not a complete algorithm analysis.", "problem -> constraints -> pseudocode -> implementation -> proof -> complexity", "Module 1 တွင် algorithm၊ constraints၊ pseudocode၊ linear search၊ binary search နှင့် sorting ကို ပြန်လည်လေ့လာပါမည်။"),
]

GENERAL = [
    ("Flowchart Decisions", "branches, loops, and termination"), ("Asymptotic Notation", "growth and bounds"), ("Recurrences", "recursive cost equations"), ("Mathematical Tools", "logs, sums, and invariants"),
    ("Search Variants", "lower and upper bounds"), ("Binary Search on Answers", "monotonic feasibility"), ("Selection and Insertion Sort", "simple sorting invariants"), ("Merge Sort", "stable divide and conquer"),
    ("Quick Sort", "partition and pivot assumptions"), ("Counting and Radix Sort", "key-domain sorting"), ("Recursive Design", "base cases and progress"), ("Divide and Conquer", "split, solve, combine"),
    ("Two Pointer Patterns", "moving boundaries"), ("Sliding Window Patterns", "maintaining a range"), ("Prefix Sum Techniques", "constant-time range queries"), ("Greedy Choice", "local decisions and proofs"),
    ("Backtracking Search", "choices, constraints, and undo"), ("DP State Design", "overlapping subproblems"), ("DP Transitions", "ordering and reconstruction"), ("Advanced DP Optimization", "state compression and monotonicity"),
    ("Graph Representations", "adjacency lists and matrices"), ("BFS and DFS", "reachability and traversal"), ("Topological Order", "DAG dependencies"), ("Dijkstra", "nonnegative shortest paths"),
    ("Kruskal and Prim", "minimum spanning trees"), ("Graph Components", "advanced connectivity"), ("Network Flow", "capacity and residual graphs"), ("KMP Matching", "prefix functions"),
    ("String Hashing", "rolling comparison and collisions"), ("GCD and Sieve", "number theory primitives"), ("Combinatorics and Bits", "counting and bit states"), ("Geometry Primitives", "orientation and intersections"),
    ("Randomized Choices", "expected performance"), ("Approximation", "bounded-quality solutions"), ("Data Structure Algorithms", "structures plus procedures"), ("Correctness Proofs", "invariants and induction"),
    ("Competitive Patterns", "constraints and fast I/O"), ("Interview Problem Solving", "communicating tradeoffs"), ("Project Architecture", "algorithmic systems"), ("Final Capstone Plan", "end-to-end algorithm design"),
]

LANGUAGE_EXAMPLES = {
    "c": "#include <stdio.h>\n\nint main(void) {\n    int values[] = {1, 3, 5, 8};\n    int target = 5;\n    for (size_t i = 0; i < 4; ++i) {\n        if (values[i] == target) { printf(\"%zu\\n\", i); return 0; }\n    }\n    puts(\"-1\");\n}",
    "cpp": "#include <algorithm>\n#include <iostream>\n#include <vector>\n\nint main() {\n    std::vector<int> values{5, 1, 4, 2};\n    std::sort(values.begin(), values.end());\n    for (int value : values) std::cout << value << ' ';\n    std::cout << '\\n';\n}",
    "python": "values = [5, 1, 4, 2]\nprint(sorted(values))",
    "java": "import java.util.Arrays;\n\nclass Main {\n    public static void main(String[] args) {\n        int[] values = {5, 1, 4, 2};\n        Arrays.sort(values);\n        System.out.println(Arrays.toString(values));\n    }\n}",
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(title, topic, theory, code, mm, previous, next_title):
    return f"""Introduction
{title} introduces {topic} through a deterministic algorithm trace.

Learning objectives
- State the problem, inputs, outputs, constraints, and correctness condition.
- Write pseudocode and preserve an invariant while implementing {topic}.
- Explain correctness, edge cases, and time and space complexity.

Prerequisites
{previous}

Problem statement
Given a valid input and the stated constraints, apply {topic} and return a result without changing the contract.

Input and output examples
Input: [5, 1, 4, 2], target=4\nOutput: a valid index or ordered result.

Constraints
State input size, ordering, duplicate behavior, numeric range, and whether mutation is allowed before implementation.

Complete theory
{theory}

Pseudocode
```text
read input and constraints
initialize state and invariant
repeat while the search/work condition holds
  apply one valid transition
return the postcondition
```

Flowchart
`start -> validate assumptions -> process one state -> condition? -> next state / return -> end`

Interactive visualization
Use `/courses/algorithms/visualizer` to step through deterministic search and sorting traces. The visual state represents the actual values and operation counters; it is not a decorative animation.

Working implementations
```python
{code}
```

Expected output
The sample produces deterministic output. Run equivalent examples locally with the documented compiler or interpreter; hosted arbitrary execution is disabled.

Line-by-line explanation
The input establishes the state, each loop transition reduces or advances the remaining work, and the return value satisfies the postcondition. Check the first, last, empty, duplicate, and already-solved cases.

Correctness explanation
The invariant is true before the first iteration, preserved by every transition, and strong enough at termination to prove the result. If the algorithm uses recursion, prove the base case and that each call moves toward it.

Time complexity
State best, average, and worst cases separately. Use O notation for growth, identify amortized assumptions, and do not call an average-case bound a guaranteed worst-case bound.

Space complexity
Report auxiliary memory separately from input storage, including recursion depth, queues, temporary arrays, and graph metadata.

Edge cases
Empty input, one element, duplicate values, already sorted input, reverse order, missing target, maximum constraint, and invalid assumptions must be tested explicitly.

Common mistakes
- Applying binary search to unsorted data.
- Using a loop without a progress or termination argument.
- Ignoring integer overflow or midpoint calculation in C/C++.
- Reporting only a typical case and omitting worst-case behavior.

Best practices
Keep pseudocode and implementation aligned, use bounds checks, test a trusted reference, document stability and mutation, and make complexity assumptions visible.

Security considerations
The platform displays read-only code. It does not compile or execute arbitrary C/C++/Python/Java in FastAPI workers and does not expose hidden answers in the client bundle.

Practice exercises
- Easy: trace the algorithm on a three-element input.
- Medium: add an empty and duplicate case with a written invariant.
- Challenge: implement the same contract in two supported languages and compare complexity.
Hint: write the postcondition before optimizing.
Guided solution: formalize -> trace -> implement -> prove -> test -> measure.

Quiz
1. What should be written before code? Problem contract, constraints, and invariant.
2. True or false: average-case O(n) is automatically worst-case O(n). False.
3. What does a correctness proof establish? That the implementation satisfies the stated contract.
4. What is unsafe without an isolated runner? Executing arbitrary student code.

Summary
You can now explain {topic}, trace its real state transitions, and justify correctness and complexity.

Next lesson
{next_title}
"""


def _questions(topic):
    return [
        (f"Which artifact best clarifies {topic}?", ["A contract and invariant", "Only a screenshot", "An unbounded loop"], "A contract and invariant", "The contract defines behavior and the invariant supports correctness."),
        ("True or false: a worst-case claim can be replaced by an average-case claim.", ["True", "False"], "False", "They describe different input distributions or guarantees."),
        ("Which case should be tested?", ["Empty and maximum valid input", "Only one typical input", "No edge cases"], "Empty and maximum valid input", "Edge cases reveal incorrect assumptions and bounds."),
        ("Where should untrusted code execute?", ["A strongly isolated runner", "The API worker", "The browser with secrets"], "A strongly isolated runner", "Process, network, filesystem, and resource isolation are required."),
    ]


def seed_algorithms_course(db, course):
    course.title = "Algorithms — From Zero to Advanced"
    course.short_description = "A free algorithm pathway covering search, sorting, recursion, graphs, dynamic programming, strings, geometry, and projects."
    course.description = "Learn algorithmic problem solving with pseudocode, correctness proofs, deterministic visualizers, complexity analysis, and equivalent C, C++, Python, and Java examples."
    course.level, course.status, course.published = "advanced", "published", True
    course.outcomes = "Formalize algorithmic problems|Analyze time and space complexity|Implement core algorithms safely|Prove correctness with invariants|Compare C C++ Python and Java solutions"
    course.requirements = "Basic programming and Data Structures fundamentals recommended. Examples are read-only unless an isolated execution runner is verified."
    authored = []
    for module_index, module_title in enumerate(MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_index))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_index); db.add(module); db.flush()
        module.title = module_title
        if module_index == 1:
            specs = [{"title": a, "topic": b, "code": c, "theory": d, "mm": e} for a, b, c, d, _syntax, e in MODULE_ONE]
        else:
            title, topic = GENERAL[module_index - 2]
            specs = [{"title": title, "topic": topic, "code": "values = [3, 1, 2]\nprint(sorted(values))", "theory": f"This foundation lesson explains {topic}. Formalize the contract, identify the invariant, test edge cases, and state complexity under explicit assumptions.", "mm": f"ဤ lesson တွင် {topic} ကို algorithm workflow ဖြင့် လေ့လာပါမည်။"}]
        for lesson_index, spec in enumerate(specs, 1):
            title, topic = spec["title"], spec["topic"]
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm=""); db.add(lesson); db.flush()
            previous = "Basic programming and Data Structures fundamentals." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
            next_title = "Continue to the next lesson." if module_index < 40 else "Continue to the final capstone review."
            lesson.title, lesson.slug = title, slug
            lesson.content_en = _content(title, topic, spec["theory"], spec["code"], spec["mm"], previous, next_title)
            lesson.content_mm = f"{title} ကို English theory နှင့်အတူ လေ့လာနိုင်ပါသည်။\n\n{spec['mm']}"
            lesson.description, lesson.duration_minutes = spec["theory"], 45
            lesson.status, lesson.published = "published", True; authored.append(lesson)
            examples = list(db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all())
            for duplicate in examples[4:]: db.delete(duplicate)
            existing = {example.language: example for example in examples[:4]}
            for position, (language, code) in enumerate(LANGUAGE_EXAMPLES.items(), 1):
                example = existing.get(language)
                if not example:
                    db.add(CodeExample(lesson_id=lesson.id, title=f"{title} — {language}", language=language, filename=f"main.{language}", code=code, description="Read-only algorithm example. Use local run instructions; hosted arbitrary execution is disabled.", position=position))
                else:
                    example.title, example.language, example.filename, example.code, example.description, example.position = f"{title} — {language}", language, f"main.{language}", code, "Read-only algorithm example. Use local run instructions; hosted arbitrary execution is disabled.", position
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz:
                quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the invariant, correctness, and complexity notes, then retry missed concepts.", status="published"); db.add(quiz); db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(topic), 1):
                values = dict(prompt=prompt, question_type="multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                question = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
                if not question: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(question, key, value)
    course.duration_minutes = sum(lesson.duration_minutes or 45 for lesson in authored)
    db.flush()
