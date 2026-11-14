"""Idempotent authored Data Structures curriculum.

Module 1 is the complete vertical slice. Later modules receive a substantive
foundation lesson so no published module is empty. Code is read-only in the
web app unless a separately verified isolated runner is available.
"""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

MODULES = [
    "Introduction to Data Structures", "Memory, Pointers & References", "Time & Space Complexity", "Arrays & Dynamic Arrays",
    "Strings & Character Data", "Recursion & Problem Solving", "Singly Linked Lists", "Doubly & Circular Linked Lists",
    "Stacks", "Queues & Circular Queues", "Deques & Priority Queues", "Hash Tables & Hash Maps", "Tree Fundamentals",
    "Binary Trees", "Binary Search Trees", "AVL Trees", "Red-Black Trees", "Heaps & Heap Operations", "Tries & Prefix Trees",
    "Graph Fundamentals", "Graph Traversals", "Graph Algorithms & Structures", "Disjoint Set Union", "Segment Trees",
    "Fenwick Trees", "Sparse Tables", "B-Trees & B+ Trees", "Skip Lists", "Bloom Filters & Probabilistic Structures",
    "Advanced Tries & Persistent Structures", "Data Structure Design Patterns", "Interview Problems & Challenges",
    "Real-World System Applications", "Performance & Memory Optimization", "Real-World Data Structure Projects", "Final Capstone & Assessment",
]

MODULE_ONE = [
    ("What Are Data Structures?", "organizing data so operations have predictable costs", "values = [4, 1, 7, 2]\nprint(values[2])", "A data structure is a representation plus operations and invariants. An array gives constant-time indexed access when its index is known; inserting in the middle may require shifting elements. Choosing a structure begins with the operations a program must perform, not with a visual shape alone.", "array[index]", "Data structure ဆိုသည်မှာ data ကို ကိုယ်စားပြုပုံ၊ operations နှင့် invariants တို့ပေါင်းစပ်ထားသော representation ဖြစ်သည်။"),
    ("Memory, References, and Ownership", "where values live and what a reference means", "items = [10, 20]\nalias = items\nalias.append(30)\nprint(items)", "A reference points to an object rather than copying the object automatically. Python lists demonstrate aliasing; C and C++ make addresses and ownership more explicit, while Java references point to objects managed by the JVM. Always state who owns allocated memory and who may mutate it.", "reference -> object\nowner -> lifetime\nborrower -> allowed operation", "Reference သည် object ကိုညွှန်ပြပြီး copy မလုပ်ဘဲ alias ဖြစ်နိုင်သည်။ C/C++ တွင် ownership နှင့် lifetime ကို ရှင်းလင်းစွာ စီမံရသည်။"),
    ("Time and Space Complexity", "measuring growth rather than one machine's speed", "def contains(values, target):\n    for value in values:\n        if value == target:\n            return True\n    return False\n\nprint(contains([2, 4, 6], 4))", "Big O describes how resource use grows with input size. A linear scan is O(n) time and O(1) extra space; it is not a promise about exact milliseconds. Separate best, average, and worst cases, and mention amortized cost when a resize occasionally performs extra work.", "scan: O(n) time, O(1) auxiliary space\nlookup by index: O(1) time", "Big O သည် input size တိုးလာသောအခါ resource usage မည်သို့တိုးသည်ကို ဖော်ပြသည်။ Exact milliseconds မဟုတ်ပါ။"),
    ("Arrays and Dynamic Arrays", "contiguous indexing and resizing", "items = [10, 20, 30]\nitems.append(40)\nprint(items[1], len(items))", "An array stores elements in indexed order. A dynamic array grows capacity when it fills; most appends are O(1) amortized, but a resize can be O(n). C and C++ require explicit capacity and bounds discipline; Python and Java library containers manage storage but still have complexity costs.", "append -> place at size\nresize -> allocate, copy, replace", "Array သည် index အလိုက် access လုပ်နိုင်ပြီး dynamic array သည် capacity ပြည့်လျှင် resize လုပ်သည်။"),
    ("Invariants and Operation Traces", "making state transitions testable", "items = []\nitems.append('A')\nitems.append('B')\nremoved = items.pop(0)\nprint(removed, items)", "An invariant is a statement that remains true after every valid operation. For a sequence, size equals the number of stored elements; for a stack, removal happens at the top. A deterministic trace lets a learner inspect each state rather than trusting decorative animation.", "state_0 -> insert(A) -> state_1 -> remove(0) -> state_2", "Invariant သည် operation များပြီးတိုင်း မှန်ကန်နေရမည့် rule ဖြစ်သည်။ Trace ဖြင့် state ပြောင်းလဲမှုကို စစ်ဆေးနိုင်သည်။"),
    ("Multi-Language Implementations", "comparing equivalent structures across languages", "class Stack:\n    def __init__(self):\n        self.items = []\n    def push(self, value):\n        self.items.append(value)\n    def pop(self):\n        return self.items.pop()\n\nstack = Stack()\nstack.push('A')\nprint(stack.pop())", "Equivalent code can differ in safety and defaults. C uses pointers and manual allocation, C++ can use standard containers and RAII, Python uses dynamic objects, and Java uses generic collections with garbage collection. Compare the operation contract and complexity, not just syntax.", "push(value) -> state'\npop() -> (value, state')", "C၊ C++၊ Python နှင့် Java တို့တွင် syntax မတူသော်လည်း operation contract နှင့် complexity ကို နှိုင်းယှဉ်ရသည်။"),
    ("Module 1 Review and Assessment", "choosing a structure from requirements", "requirements = {'lookup_by_index': True, 'remove_latest': False}\nchoice = 'array' if requirements['lookup_by_index'] else 'linked list'\nprint(choice)", "Review the decision process: identify operations, define invariants, estimate best/average/worst costs, and select a representation. No single structure is fastest for every workload. The visualizer uses deterministic array and stack traces; it does not claim to run arbitrary student code.", "requirements -> operations -> invariant -> complexity -> choice", "Module 1 တွင် structure ရွေးချယ်ခြင်း၊ memory၊ complexity၊ array၊ stack နှင့် invariant များကို ပြန်လည်သုံးသပ်ပါမည်။"),
]

GENERAL = [
    ("Pointers and References", "safe address and reference reasoning"), ("Ownership and Lifetime", "allocation boundaries"),
    ("Complexity Tradeoffs", "time-space decisions"), ("Array Operations", "indexed updates and shifts"),
    ("String Storage", "characters and encoding"), ("Recursive State", "base cases and progress"),
    ("Linked Node Design", "links and traversal"), ("Bidirectional Links", "prev and next invariants"),
    ("Stack Operations", "LIFO behavior"), ("Queue Operations", "FIFO behavior"), ("Deque and Priority Queue", "two-ended and priority access"),
    ("Hashing and Collisions", "keys, buckets, and expected cost"), ("Tree Nodes and Traversal", "hierarchical data"),
    ("Binary Tree Traversals", "preorder, inorder, and postorder"), ("BST Invariants", "ordered search"), ("AVL Rotations", "height balance"),
    ("Red-Black Invariants", "balanced search trees"), ("Heap Invariants", "priority access"), ("Trie Prefix Search", "character paths"),
    ("Graph Models", "vertices, edges, and representation"), ("BFS and DFS", "systematic traversal"), ("Weighted Graphs", "shortest-path choices"),
    ("Union-Find", "components and path compression"), ("Segment Tree Queries", "range aggregation"), ("Fenwick Prefix Sums", "compact updates"),
    ("Sparse Table Queries", "static range operations"), ("B-Tree Pages", "database index locality"), ("Skip List Levels", "probabilistic ordering"),
    ("Bloom Filter Guarantees", "false positives and memory"), ("Persistent Structures", "versioned state"), ("Design Patterns", "composable structure choices"),
    ("Interview Traces", "explain operations and complexity"), ("System Applications", "caches, indexes, and schedulers"),
    ("Memory Optimization", "measurement and locality"), ("Project Architecture", "testing a complete structure"), ("Final Capstone Plan", "integrated DSA design"),
]

LANGUAGE_EXAMPLES = {
    "c": "#include <stdio.h>\n\nint main(void) {\n    int values[] = {10, 20, 30};\n    printf(\"%d\\n\", values[1]);\n    return 0;\n}",
    "cpp": "#include <iostream>\n#include <vector>\n\nint main() {\n    std::vector<int> values{10, 20, 30};\n    std::cout << values.at(1) << '\\n';\n}",
    "python": "values = [10, 20, 30]\nprint(values[1])",
    "java": "import java.util.List;\n\nclass Main {\n    public static void main(String[] args) {\n        var values = List.of(10, 20, 30);\n        System.out.println(values.get(1));\n    }\n}",
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(title, topic, theory, syntax, code, mm, previous, next_title):
    return f"""Introduction
{title} introduces {topic} through an inspectable, deterministic trace.

Learning objectives
- Define the structure, operations, and invariant for {topic}.
- Explain best, average, and worst-case behavior without overclaiming.
- Compare safe implementations across C, C++, Python, and Java.

Prerequisites
{previous}

Data structure definition
A data structure combines a representation, permitted operations, and invariants that must remain true after each operation.

Memory or structure diagram
`input -> representation -> operation -> new state`; ownership and references must be explicit for every mutable node or buffer.

Operations and invariants
State transitions are valid only when their preconditions hold. Record size, links, root/parent relationships, capacity, and empty-state behavior.

Step-by-step visualization
Apply one operation at a time, capture the state before and after it, and check the invariant after each step. The course visualizer uses deterministic traces rather than decorative animation.

Pseudocode
```text
inspect state
if operation precondition is false: report edge case
apply one mutation
check invariant
report complexity
```

Detailed theory
{theory}

Working implementations
```python
{code}
```

Expected output
The example prints a deterministic result from a small in-memory input. Run each language locally with the documented compiler or interpreter.

Line-by-line explanation
The declaration creates the representation, the operation changes or reads one state, and the final output exposes the result. Check the empty, singleton, duplicate, and boundary cases before generalizing.

Time complexity
State the operation-specific cost. Complexity depends on the representation and workload; an average-case claim is not a worst-case guarantee. Include auxiliary space separately from input storage.

Best / average / worst cases
Best case may stop early, average case depends on a stated model, and worst case must include the maximum valid input. Mention amortized analysis when occasional resizing or rebuilding occurs.

Common mistakes
- Forgetting empty and singleton cases.
- Updating one link or index without preserving the invariant.
- Claiming O(1) for an operation that scans or shifts elements.
- Confusing a reference/alias with an independent copy.

Best practices
Use bounds checks, explicit ownership, RAII or managed collections where appropriate, deterministic tests, and operation traces. Document the chosen complexity and its assumptions.

Security considerations
The web lesson is read-only. Arbitrary C/C++/Python/Java code is not executed in FastAPI workers, and hidden production services are never exposed. Use isolated runners with resource limits before enabling execution.

Practice exercises
- Easy: trace the structure for three valid operations.
- Medium: add an empty-state guard and state the resulting complexity.
- Challenge: implement the same contract in two supported languages and compare memory ownership.
Hints: write the invariant first, then test the smallest and largest valid states.
Guided solution: define -> trace -> mutate -> validate -> measure -> explain.

Quiz
1. What must remain true after a valid operation? The data structure invariant.
2. True or false: average-case O(1) always means worst-case O(1). False.
3. What should be tested first? Empty, singleton, boundary, and duplicate cases.
4. Which language concern is especially explicit in C/C++? Allocation, ownership, and bounds safety.

Summary
You can now reason about {topic}, trace real state changes, and communicate complexity with its assumptions.

Next lesson
{next_title}
"""


def _questions(topic):
    return [
        (f"What is essential when implementing {topic}?", ["An invariant", "Only a visual animation", "An unbounded loop"], "An invariant", "An invariant describes the state that must remain valid."),
        ("True or false: average-case complexity is automatically a worst-case guarantee.", ["True", "False"], "False", "Average and worst cases are different claims."),
        ("Which edge cases should be tested?", ["Empty and boundary states", "Only a typical state", "No states"], "Empty and boundary states", "Boundary tests expose missing preconditions and invalid indexing."),
        ("What is unsafe to do in the API process?", ["Execute arbitrary student code", "Display read-only code", "Explain local commands"], "Execute arbitrary student code", "Untrusted code requires a strongly isolated runner."),
    ]


def seed_data_structures_course(db, course):
    course.title = "Data Structures — From Zero to Advanced"
    course.short_description = "A free DSA pathway covering arrays, linked structures, trees, heaps, graphs, indexing, complexity, and real projects."
    course.description = "Learn data structures through deterministic visual traces, complexity analysis, and equivalent C, C++, Python, and Java implementations."
    course.level, course.status, course.published = "advanced", "published", True
    course.outcomes = "Choose structures from operation requirements|Implement and trace core structures|Analyze time and space complexity|Compare C C++ Python and Java implementations|Build safe tested DSA projects"
    course.requirements = "Basic programming in at least one supported language. Code examples are read-only in the web app unless an isolated runner is verified."
    authored = []
    for module_index, module_title in enumerate(MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_index))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_index)
            db.add(module); db.flush()
        module.title = module_title
        if module_index == 1:
            specs = [{"title": a, "topic": b, "code": c, "theory": d, "syntax": e, "mm": f} for a, b, c, d, e, f in MODULE_ONE]
        else:
            title, topic = GENERAL[module_index - 2]
            specs = [{"title": title, "topic": topic, "code": "values = [3, 1, 2]\nprint(sorted(values))", "theory": f"This foundation lesson explains {topic}. Select a representation from required operations, state its invariant, trace edge cases, and verify complexity with deterministic tests.", "syntax": "operation(state, value) -> new_state", "mm": f"ဤ lesson တွင် {topic} ကို data structures နှင့် complexity workflow ဖြင့် လေ့လာပါမည်။"}]
        for lesson_index, spec in enumerate(specs, 1):
            title, topic = spec["title"], spec["topic"]
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm="")
                db.add(lesson); db.flush()
            previous = "Basic programming and one supported language." if module_index == 1 else f"Complete the earlier lessons in Module {module_index - 1}."
            next_title = "Continue to the next lesson." if module_index < 36 else "Continue to the final capstone review."
            lesson.title, lesson.slug = title, slug
            lesson.content_en = _content(title, topic, spec["theory"], spec["syntax"], spec["code"], spec["mm"], previous, next_title)
            lesson.content_mm = f"{title} ကို English theory နှင့်အတူ လေ့လာနိုင်ပါသည်။\n\n{spec['mm']}"
            lesson.description, lesson.duration_minutes = spec["theory"], 40
            lesson.status, lesson.published = "published", True
            authored.append(lesson)
            examples = list(db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all())
            for duplicate in examples[4:]:
                db.delete(duplicate)
            existing = {example.language: example for example in examples[:4]}
            for position, (language, code) in enumerate(LANGUAGE_EXAMPLES.items(), 1):
                example = existing.get(language)
                if not example:
                    db.add(CodeExample(lesson_id=lesson.id, title=f"{title} — {language}", language=language, filename=f"main.{language}", code=code, description="Read-only implementation. Use local compiler instructions; hosted arbitrary execution is disabled.", position=position))
                else:
                    example.title, example.language, example.filename, example.code, example.description, example.position = f"{title} — {language}", language, f"main.{language}", code, "Read-only implementation. Use local compiler instructions; hosted arbitrary execution is disabled.", position
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz:
                quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the invariant and complexity notes, then retry missed concepts.", status="published")
                db.add(quiz); db.flush()
            for position, (prompt, options, answer, explanation) in enumerate(_questions(topic), 1):
                values = dict(prompt=prompt, question_type="true_false" if options == ["True", "False"] else "multiple_choice", options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                question = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
                if not question:
                    db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(question, key, value)
    course.duration_minutes = sum(lesson.duration_minutes or 40 for lesson in authored)
    db.flush()
