"""Reviewed, portable C curriculum content used by the idempotent catalog seed."""
import json
from sqlalchemy import select

MODULES = [
    ("Introduction to Programming & C", "programming", [
        ("What a program is", "A program is a precise list of instructions. C source is translated by a compiler into a native executable. This lesson introduces source files, compilation, execution, and the edit-compile-run cycle.", '#include <stdio.h>\n\nint main(void) {\n    puts("Hello, C!");\n    return 0;\n}', "Hello, C!", "main starts the program, puts writes one line, and return 0 reports successful completion."),
        ("The shape of a C program", "C programs are built from functions, statements, expressions, and comments. Every statement ends with a semicolon, while braces group a block. The compiler checks syntax before the program runs.", '#include <stdio.h>\n\nint main(void) {\n    /* A comment explains intent to a reader. */\n    puts("C has a small core language.");\n    return 0;\n}', "C has a small core language.", "The include makes puts available; main is the required entry point; the comment has no runtime effect."),
    ]),
    ("C Environment Setup", "tooling", [
        ("Compiler and warnings", "A compiler turns C into an executable. Use warnings while learning: `-std=c11 -Wall -Wextra -Wpedantic` catches many mistakes before runtime.", '#include <stdio.h>\n\nint main(void) {\n    int answer = 42;\n    printf("answer = %d\\n", answer);\n    return 0;\n}', "answer = 42", "The compiler checks the declarations, then printf formats the integer using %d."),
        ("Source files and build steps", "Keep source files readable and build them deliberately. Compilation and linking are separate conceptual steps even when one command performs both.", '#include <stdio.h>\n\nint main(void) {\n    puts("Compile, link, run, repeat.");\n    return 0;\n}', "Compile, link, run, repeat.", "The source is compiled, linked with the standard library, and then executed by the operating system."),
    ]),
    ("Your First C Program", "syntax", [
        ("main and return", "Execution begins in main. `int main(void)` says that main receives no arguments and returns an integer status to the operating system.", '#include <stdio.h>\n\nint main(void) {\n    printf("My first program\\n");\n    return 0;\n}', "My first program", "printf writes the string and `\\n` moves to a new line; return 0 ends main successfully."),
        ("Comments and formatting", "Whitespace makes code easier to read but does not usually change its meaning. Use comments to explain why, not to repeat obvious syntax.", '#include <stdio.h>\n\nint main(void) {\n    int lines = 2;\n    printf("Readable code has %d lines here.\\n", lines);\n    return 0;\n}', "Readable code has 2 lines here.", "The integer is passed as an argument and `%d` is replaced with its value."),
    ]),
    ("Variables & Data Types", "types", [
        ("Integers and floating point", "A variable names storage with a type. `int` stores whole numbers, while `double` stores fractional values. Choose a type that matches the data.", '#include <stdio.h>\n\nint main(void) {\n    int minutes = 90;\n    double hours = minutes / 60.0;\n    printf("%d minutes is %.1f hours.\\n", minutes, hours);\n    return 0;\n}', "90 minutes is 1.5 hours.", "The decimal `60.0` makes the division floating point; `%.1f` prints one digit after the decimal point."),
        ("Characters and constants", "A char stores one character such as 'C'. `const` communicates that a value should not be changed after initialization.", '#include <stdio.h>\n\nint main(void) {\n    const char grade = \'A\';\n    printf("Grade: %c\\n", grade);\n    return 0;\n}', "Grade: A", "Character literals use single quotes and `%c` formats one character."),
    ]),
    ("Input & Output", "io", [
        ("Printing values", "Formatted output combines a format string with values. The conversion specifier must match the value type, otherwise the result is unreliable.", '#include <stdio.h>\n\nint main(void) {\n    int age = 20;\n    printf("Age: %d\\n", age);\n    return 0;\n}', "Age: 20", "`%d` is the format for an int and the argument supplies the value."),
        ("Reading simple input", "`scanf` can read small, well-formed numeric input. Always check its return value in production code so invalid input is handled deliberately.", '#include <stdio.h>\n\nint main(void) {\n    int number;\n    if (scanf("%d", &number) == 1) {\n        printf("You entered %d.\\n", number);\n    }\n    return 0;\n}', "Input 7 produces: You entered 7.", "The ampersand gives scanf the address where it should store the integer."),
    ]),
    ("Operators & Expressions", "operators", [
        ("Arithmetic operators", "C provides +, -, *, /, and %. Integer division discards a remainder, while `%` gives the remainder.", '#include <stdio.h>\n\nint main(void) {\n    int total = 17;\n    printf("quotient=%d remainder=%d\\n", total / 5, total % 5);\n    return 0;\n}', "quotient=3 remainder=2", "The expression is evaluated before printf receives the two integer results."),
        ("Comparison and logical operators", "Comparisons produce 1 for true and 0 for false. Combine conditions with `&&`, `||`, and `!`, using parentheses when they improve clarity.", '#include <stdio.h>\n\nint main(void) {\n    int age = 20;\n    int has_id = 1;\n    printf("allowed=%d\\n", age >= 18 && has_id);\n    return 0;\n}', "allowed=1", "Both conditions are true, so the logical AND expression evaluates to 1."),
    ]),
    ("Conditional Statements", "conditions", [
        ("if and else", "Use if when a block should run only when a condition is true. else provides the alternative branch.", '#include <stdio.h>\n\nint main(void) {\n    int score = 72;\n    if (score >= 50) puts("Pass");\n    else puts("Try again");\n    return 0;\n}', "Pass", "The comparison is true, so only the first branch executes."),
        ("switch statements", "switch is useful when one expression is compared with several constant cases. Include break unless deliberate fall-through is wanted.", '#include <stdio.h>\n\nint main(void) {\n    int day = 2;\n    switch (day) {\n        case 1: puts("Monday"); break;\n        case 2: puts("Tuesday"); break;\n        default: puts("Other day");\n    }\n    return 0;\n}', "Tuesday", "The matching case runs and break leaves the switch."),
    ]),
    ("Loops", "loops", [
        ("for loops", "A for loop groups initialization, continuation, and update. It is a good fit when the number of iterations is known.", '#include <stdio.h>\n\nint main(void) {\n    for (int i = 1; i <= 3; i++) {\n        printf("%d\\n", i);\n    }\n    return 0;\n}', "1\n2\n3", "i starts at 1, the condition is checked before each iteration, and i increases after each body."),
        ("while and do-while", "while checks before entering its body. do-while executes once before checking, which is useful for menu-style input.", '#include <stdio.h>\n\nint main(void) {\n    int value = 3;\n    while (value > 0) {\n        printf("%d\\n", value);\n        value--;\n    }\n    return 0;\n}', "3\n2\n1", "The decrement guarantees that the loop eventually reaches its stopping condition."),
    ]),
    ("Functions", "functions", [
        ("Parameters and return values", "Functions give a name to reusable behavior. Parameters receive inputs and a return value sends a result to the caller.", '#include <stdio.h>\n\nint add(int left, int right) {\n    return left + right;\n}\n\nint main(void) {\n    printf("%d\\n", add(4, 5));\n    return 0;\n}', "9", "main calls add; add receives two copies of the values and returns their sum."),
        ("Function prototypes", "A prototype tells the compiler a function's name, return type, and parameters before the call. Definitions can then appear later in the file.", '#include <stdio.h>\n\nint square(int value);\n\nint main(void) {\n    printf("%d\\n", square(6));\n    return 0;\n}\n\nint square(int value) {\n    return value * value;\n}', "36", "The prototype makes the earlier call type-safe; the definition supplies the implementation."),
    ]),
    ("Arrays", "arrays", [
        ("Fixed-size arrays", "An array stores values of one type in contiguous indexed positions. Indexing starts at zero and valid indexes stop at length minus one.", '#include <stdio.h>\n\nint main(void) {\n    int scores[] = {70, 80, 90};\n    printf("first=%d last=%d\\n", scores[0], scores[2]);\n    return 0;\n}', "first=70 last=90", "The initializer creates three ints; scores[0] and scores[2] access the first and last elements."),
        ("Array traversal", "Use a loop to visit each element. Keep the length available because a function receiving an array does not automatically know its size.", '#include <stdio.h>\n\nint main(void) {\n    int values[] = {2, 4, 6};\n    int total = 0;\n    for (size_t i = 0; i < 3; i++) total += values[i];\n    printf("total=%d\\n", total);\n    return 0;\n}', "total=12", "The loop visits indexes 0, 1, and 2 exactly once."),
    ]),
    ("Strings & Characters", "strings", [
        ("C strings", "A C string is an array of char ending with a null character `\\0`. The terminator lets library functions find its end.", '#include <stdio.h>\n\nint main(void) {\n    char name[] = "Ada";\n    printf("Hello, %s!\\n", name);\n    return 0;\n}', "Hello, Ada!", "The string literal initializes four characters including its terminator; `%s` prints until that terminator."),
        ("Safe character processing", "The ctype library provides character tests. Pass an unsigned-char value or EOF to these functions; this avoids issues with negative signed chars.", '#include <ctype.h>\n#include <stdio.h>\n\nint main(void) {\n    unsigned char letter = \'c\';\n    printf("%c\\n", toupper(letter));\n    return 0;\n}', "C", "toupper returns the uppercase form of the character."),
    ]),
    ("Pointers", "pointers", [
        ("Addresses and indirection", "A pointer stores an address. `&` obtains an address and `*` follows a pointer to read or write the pointed-to value.", '#include <stdio.h>\n\nint main(void) {\n    int value = 7;\n    int *pointer = &value;\n    *pointer = 8;\n    printf("%d\\n", value);\n    return 0;\n}', "8", "pointer points at value, so writing through *pointer changes value itself."),
        ("Pointers as function arguments", "Passing an address lets a function modify a caller-owned variable. The pointer must refer to a valid object for the duration of the call.", '#include <stdio.h>\n\nvoid double_value(int *value) {\n    *value *= 2;\n}\n\nint main(void) {\n    int value = 6;\n    double_value(&value);\n    printf("%d\\n", value);\n    return 0;\n}', "12", "The function receives the address of value and updates the original object."),
    ]),
    ("Memory Management", "memory", [
        ("Automatic storage", "Local variables normally have automatic storage: they exist while their block runs. Do not return a pointer to a local variable.", '#include <stdio.h>\n\nint main(void) {\n    int count = 3;\n    {\n        int extra = 2;\n        count += extra;\n    }\n    printf("%d\\n", count);\n    return 0;\n}', "5", "extra exists only inside the nested block; count remains available in main."),
        ("malloc and free", "Dynamic allocation requests storage at runtime. Check malloc, use the allocated object within its bounds, and call free exactly once when finished.", '#include <stdio.h>\n#include <stdlib.h>\n\nint main(void) {\n    int *value = malloc(sizeof *value);\n    if (value == NULL) return 1;\n    *value = 42;\n    printf("%d\\n", *value);\n    free(value);\n    return 0;\n}', "42", "sizeof *value requests the correct size; the null check handles allocation failure and free releases the storage."),
    ]),
    ("Structures, Unions & Enums", "records", [
        ("Structures", "A struct groups related fields that may have different types. Use the dot operator with a struct object.", '#include <stdio.h>\n\nstruct Point { int x; int y; };\n\nint main(void) {\n    struct Point point = {3, 4};\n    printf("(%d, %d)\\n", point.x, point.y);\n    return 0;\n}', "(3, 4)", "The initializer fills x and y in declaration order; dot selects a named field."),
        ("Enums and unions", "An enum gives readable names to integer constants. A union shares storage between fields, so only the most recently written member should be read.", '#include <stdio.h>\n\nint main(void) {\n    enum Status { READY, DONE };\n    enum Status state = DONE;\n    printf("%d\\n", state);\n    return 0;\n}', "1", "READY is zero and DONE is one unless explicit values are assigned."),
    ]),
    ("File Handling", "files", [
        ("Opening and writing files", "stdio FILE streams represent files. Check fopen, write deliberately, and close every successfully opened stream.", '#include <stdio.h>\n\nint main(void) {\n    FILE *file = fopen("notes.txt", "w");\n    if (file == NULL) return 1;\n    fputs("C notes\\n", file);\n    fclose(file);\n    puts("saved");\n    return 0;\n}', "saved", "fopen creates or truncates the file in write mode; fputs writes text and fclose finishes the operation."),
        ("Reading files", "Read a file with a bounded buffer and test the return value of fgets. Never assume a file exists or that one line fits an unbounded buffer.", '#include <stdio.h>\n\nint main(void) {\n    FILE *file = fopen("notes.txt", "r");\n    char line[80];\n    if (file == NULL) return 1;\n    if (fgets(line, sizeof line, file) != NULL) printf("%s", line);\n    fclose(file);\n    return 0;\n}', "For the previous file: C notes", "fgets limits the number of bytes written and returns NULL at end of file or on failure."),
    ]),
    ("Preprocessor & Headers", "preprocessor", [
        ("Macros and constants", "The preprocessor runs before compilation. Prefer typed const objects for most values; macros are textual substitution and have no type.", '#include <stdio.h>\n#define MAX_SCORE 100\n\nint main(void) {\n    printf("maximum=%d\\n", MAX_SCORE);\n    return 0;\n}', "maximum=100", "The preprocessor replaces MAX_SCORE before the compiler sees the source."),
        ("Header declarations", "Headers share declarations between source files. Include guards prevent a header's contents from being processed more than once.", '#include <stdio.h>\n\nstatic int cube(int value) { return value * value * value; }\n\nint main(void) {\n    printf("%d\\n", cube(3));\n    return 0;\n}', "27", "A small static function has internal linkage and keeps its implementation private to this source file."),
    ]),
    ("Debugging & Common Errors", "debugging", [
        ("Compiler diagnostics", "Read the first warning carefully. Common beginner errors include missing semicolons, wrong format specifiers, and using an uninitialized variable.", '#include <stdio.h>\n\nint main(void) {\n    int first = 2;\n    int second = 3;\n    printf("sum=%d\\n", first + second);\n    return 0;\n}', "sum=5", "Keeping declarations initialized and formats matched makes compiler diagnostics easier to trust."),
        ("Assertions and debugging", "An assertion documents an assumption during development. It should describe a condition that must be true, not replace normal user-input validation.", '#include <assert.h>\n#include <stdio.h>\n\nint main(void) {\n    int divisor = 2;\n    assert(divisor != 0);\n    printf("%d\\n", 8 / divisor);\n    return 0;\n}', "4", "The assertion checks the invariant before division; normal programs should still validate external input."),
    ]),
    ("Algorithms & Problem Solving", "algorithms", [
        ("Search and complexity", "An algorithm is a repeatable method. Linear search checks items one at a time and takes more work as the array grows.", '#include <stdio.h>\n\nint main(void) {\n    int values[] = {4, 8, 15};\n    int target = 8;\n    int found = 0;\n    for (int i = 0; i < 3; i++) if (values[i] == target) found = 1;\n    printf("found=%d\\n", found);\n    return 0;\n}', "found=1", "The loop compares target with each element and records whether a match exists."),
        ("Decomposition and pseudocode", "Solve problems by defining inputs, outputs, constraints, and small steps before writing C. Pseudocode exposes missing cases early.", '#include <stdio.h>\n\nint main(void) {\n    int a = 8, b = 3;\n    int larger = a > b ? a : b;\n    printf("larger=%d\\n", larger);\n    return 0;\n}', "larger=8", "The conditional operator expresses a small choice after the problem has been decomposed."),
    ]),
    ("Mini Projects", "projects", [
        ("Simple calculator", "A calculator combines input, validation, branching, and functions. Keep each operation small and reject division by zero.", '#include <stdio.h>\n\nint main(void) {\n    char operation = \'+\';\n    int left = 7, right = 5;\n    if (operation == \'+\') printf("%d\\n", left + right);\n    return 0;\n}', "12", "The operation selects the addition branch; a complete calculator would add validated branches for other operators."),
        ("Student grade calculator", "A grade calculator turns numeric scores into meaningful categories. Define boundary rules before coding and test values around each boundary.", '#include <stdio.h>\n\nint main(void) {\n    int score = 86;\n    char grade = score >= 80 ? \'A\' : score >= 60 ? \'B\' : \'C\';\n    printf("%c\\n", grade);\n    return 0;\n}', "A", "The conditions are evaluated from left to right; the first true threshold determines the grade."),
    ]),
    ("Final Project & Assessment", "assessment", [
        ("Planning a record manager", "A final project should have a written requirement, a small data model, input validation, reusable functions, and tests. Start with a version that can be verified.", '#include <stdio.h>\n\nstruct Student { char name[30]; int score; };\n\nint main(void) {\n    struct Student student = {"Mya", 91};\n    printf("%s: %d\\n", student.name, student.score);\n    return 0;\n}', "Mya: 91", "The struct models one record; the final application can add an array, search, and file persistence incrementally."),
        ("Assessment checklist", "Review syntax, types, control flow, functions, arrays, pointers, files, and testing. A correct solution is readable, bounded, and explains its assumptions.", '#include <stdio.h>\n\nint main(void) {\n    puts("Plan, implement, test, explain.");\n    return 0;\n}', "Plan, implement, test, explain.", "The checklist is a repeatable process for finishing a small C project responsibly."),
    ]),
]

def lesson_content(title, topic, theory, code, output, explanation):
    return f"Introduction\n{theory}\n\nLearning objectives\n- Explain {title.lower()} in your own words.\n- Read and modify a complete, portable C program.\n- Predict the output before compiling.\n\nPrerequisites\nComplete the previous lesson in this course and be comfortable reading the basic shape of main.\n\nSyntax and theory\nThe topic is {topic}. Work from the declaration and control flow outward: identify the types, the inputs, the expressions, and the statements that produce the result. Compile with -std=c11 -Wall -Wextra -Wpedantic and treat warnings as questions to answer.\n\nComplete example\n```c\n{code}\n```\n\nExpected output\n```text\n{output}\n```\n\nLine-by-line explanation\n{explanation} The include supplies the standard library declaration used by the program. main owns the execution flow, and return 0 communicates success.\n\nCommon beginner mistakes\n- Forgetting a semicolon or a matching brace.\n- Using a format specifier that does not match the value.\n- Reading or writing outside an array's valid bounds.\n- Assuming input, memory allocation, or a file operation always succeeds.\n\nExercises\n1. Change one input value and predict the output before compiling.\n2. Add one validation check relevant to this lesson.\n3. Explain one design choice in a short comment without changing the C syntax.\n\nSummary\nYou practiced {title.lower()} and saw how a small, complete program turns the idea into observable output.\n"

def seed_c_curriculum(db, course):
    from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion
    for module_position, (module_title, topic, lessons) in enumerate(MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_position))
        if not module:
            module = CourseModule(course_id=course.id, title=f"{module_position:02d} {module_title}", order_index=module_position)
            db.add(module); db.flush()
        for lesson_position, (title, theory, code, output, explanation) in enumerate(lessons, 1):
            lesson_slug = f"{module_position:02d}-{title.lower().replace(' ', '-')[:50]}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_position))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=lesson_slug, description=theory[:240], content_en=lesson_content(title, topic, theory, code, output, explanation), content_mm=f"Myanmar explanation for {title} is available as an optional translation layer. The original C code remains unchanged.", order_index=lesson_position, duration_minutes=25, status="published", published=True)
                db.add(lesson); db.flush()
            if not db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id)):
                db.add(CodeExample(lesson_id=lesson.id, title=f"{title} example", language="c", code=code, filename="main.c", description=f"Expected output:\n{output}\n\nExplanation:\n{explanation}", position=1))
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz:
                quiz = LessonQuiz(lesson_id=lesson.id, title=f"Check your understanding: {title}", explanation="Review the lesson and try the exercises before repeating the quiz.")
                db.add(quiz); db.flush()
                db.add(QuizQuestion(quiz_id=quiz.id, prompt=f"Which idea is central to {title.lower()}?", options_json=json.dumps([title, "Ignoring compiler warnings", "Writing code without testing"]), correct_answer=title, explanation=f"The correct answer is {title}, because it is the focus of this lesson.", position=1))
    course.duration_minutes = len(MODULES) * 2 * 25
    course.outcomes = "Understand C program structure|Write and explain portable C programs|Use types, control flow, functions, arrays, pointers, and files safely|Plan and test beginner C projects"
    course.requirements = "No prior programming experience|A C11 compiler such as GCC or Clang|A text editor"
    course.status = "published"
    course.published = True
