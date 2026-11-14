"""Complete, reviewed Module 3 content for the C Programming course.

The module is authored for absolute beginners. Every lesson is a real lesson:
it contains objectives, prerequisites, theory, definitions, syntax, a complete
compilable program, expected output, a line-by-line explanation, mistakes,
exercises with solutions, a quiz, a summary, and next-lesson navigation.
"""
import json
from sqlalchemy import select

MODULE_TITLE = "Your First C Program & C Syntax Fundamentals"


def _exercise_text(exercises):
    parts = []
    for index, (prompt, solution, explanation) in enumerate(exercises, 1):
        parts.append(
            f"{index}. {prompt}\n"
            f"   Solution:\n```c\n{solution}\n```\n"
            f"   Why it works: {explanation}"
        )
    return "\n\n".join(parts)


def _extra_example_text(extra_examples):
    if not extra_examples:
        return ""
    sections = ["Additional complete example"]
    for example in extra_examples:
        sections.append(
            f"{example['title']}\n```c\n{example['code']}\n```\n\n"
            f"Expected output\n```text\n{example['output']}\n```\n\n"
            f"Explanation\n{example['explanation']}"
        )
    return "\n\n".join(sections) + "\n\n"


def build_content(item):
    objectives = "\n".join(f"- {objective}" for objective in item["objectives"])
    definitions = "\n".join(f"- {definition}" for definition in item["definitions"])
    mistakes = "\n".join(f"- {mistake}" for mistake in item["mistakes"])
    return (
        f"Introduction\n{item['intro']}\n\n"
        f"Learning objectives\n{objectives}\n\n"
        f"Prerequisites\n{item['prerequisites']}\n\n"
        f"Detailed theory\n{item['theory']}\n\n"
        f"Visual explanation\n{item['diagram']}\n\n"
        f"Key definitions\n{definitions}\n\n"
        f"Syntax example\n```c\n{item['syntax']}\n```\n\n"
        f"Complete C program — {item['program_title']}\n```c\n{item['code']}\n```\n\n"
        f"Expected output\n```text\n{item['output']}\n```\n\n"
        f"Line-by-line explanation\n{item['explanation']}\n\n"
        f"{_extra_example_text(item.get('extra_examples'))}"
        f"Common mistakes\n{mistakes}\n\n"
        f"Practice exercises\n{_exercise_text(item['exercises'])}\n\n"
        f"Summary\n{item['summary']}\n\n"
        f"Next lesson\n{item['next']}\n"
    )


MODULE_THREE_LESSONS = [
    {
        "title": "Introduction to C Program Structure",
        "slug": "introduction-to-c-program-structure",
        "intro": (
            "A C program is not a single magical command. It is a text file written in a precise language, "
            "and that file is translated into a form the computer can run. Before you write a large program, "
            "you need a mental picture of its parts: the preprocessor directive, the main function, the function "
            "body, statements, comments, and the return value. In this lesson you will read the smallest useful "
            "C program line by line and understand why each line exists."
        ),
        "objectives": [
            "Describe what source code, compilation, and an executable are.",
            "Identify the header include, main function, body, statements, and return statement in a C program.",
            "Explain why every C program needs an entry point named main.",
            "Predict the output of a small program before compiling it.",
        ],
        "prerequisites": (
            "Complete Modules 1 and 2, or be able to create a file named with a .c extension and compile it with "
            "GCC or Clang. You do not need prior programming experience for this lesson."
        ),
        "theory": (
            "C source code is ordinary text. The compiler reads that text and checks it against the grammar of C. "
            "The linker then combines the compiled code with the standard library so that calls such as printf have "
            "a real implementation. The finished file is an executable: a program the operating system can start.\n\n"
            "Every C program has one entry point called main. Execution begins at main, not at the first line of the "
            "file and not at the first function you happen to write. A common beginner mistake is to assume that the "
            "line #include <stdio.h> is executed at runtime. It is not a runtime instruction. It is a preprocessor "
            "directive: before compilation, it makes declarations from the standard input/output header available to "
            "your program.\n\n"
            "The line int main(void) has three jobs. The word int says that main returns an integer exit status. The "
            "word main is the required name of the entry point. The (void) parameter list says that this version of "
            "main receives no arguments. The braces { and } group the function body. Inside the body, each statement "
            "is a complete instruction and usually ends with a semicolon.\n\n"
            "The statement printf(\"Hello, C!\\n\"); calls the printf function. The text inside the double quotes is a "
            "string literal. The two characters backslash and n form an escape sequence that moves the cursor to a new "
            "line. The semicolon ends the statement. Finally, return 0; sends the integer zero back to the operating "
            "system. By long-standing convention, zero means success and a nonzero value means failure.\n\n"
            "Read a program from the outside inward. First find the includes, then find main, then read the statements "
            "inside its braces in order. That habit will help you understand much larger programs later."
        ),
        "diagram": (
            "Source file hello.c\n"
            "        |\n"
            "        v\n"
            "  Preprocessor  -> expands #include and macros\n"
            "        |\n"
            "        v\n"
            "  Compiler      -> checks C syntax and creates object code\n"
            "        |\n"
            "        v\n"
            "  Linker        -> combines object code with the C library\n"
            "        |\n"
            "        v\n"
            "  Executable    -> starts at main() when run\n\n"
            "Program anatomy\n"
            "#include <stdio.h>      preprocessor directive\n"
            "int main(void) {        entry point, returns an int\n"
            "    printf(\"Hi\\n\");      statement: call printf\n"
            "    return 0;           statement: report success\n"
            "}                       end of the function body"
        ),
        "definitions": [
            "Source code: human-readable instructions stored in a .c file.",
            "Compiler: a program that translates C source into machine-oriented object code.",
            "Linker: the tool that joins object code with library code to create an executable.",
            "Executable: the runnable program produced after translation and linking.",
            "main: the required function where execution of a C program begins.",
            "Statement: one complete instruction inside a function body, normally ending with a semicolon.",
            "Preprocessor directive: a line beginning with # that is handled before compilation.",
        ],
        "syntax": (
            "#include <stdio.h>\n\n"
            "int main(void) {\n"
            "    /* statements go here */\n"
            "    return 0;\n"
            "}"
        ),
        "program_title": "reading the parts of a C program",
        "code": (
            '#include <stdio.h>\n\n'
            'int main(void) {\n'
            '    /* This program shows the structure of a C program. */\n'
            '    printf("A C program has a beginning, a body, and an end.\\n");\n'
            '    printf("Execution starts at main.\\n");\n'
            '    return 0;\n'
            '}'
        ),
        "output": (
            "A C program has a beginning, a body, and an end.\n"
            "Execution starts at main."
        ),
        "explanation": (
            "Line 1 tells the preprocessor to include declarations for standard input and output; printf is declared "
            "there. Line 3 starts the definition of main and says it returns an int and takes no arguments. Line 4 is "
            "a block comment, so the compiler ignores it. Line 5 calls printf with a string literal. The \\n at the "
            "end of that string moves output to the next line. Line 6 calls printf again, producing the second line. "
            "Line 7 returns zero to the operating system, which reports successful completion. Line 8 closes the "
            "function body."
        ),
        "mistakes": [
            "Writing Main or Printf with the wrong capitalisation. C is case-sensitive.",
            "Omitting the #include <stdio.h> line and then calling printf.",
            "Putting a semicolon after int main(void), which breaks the function definition.",
            "Forgetting the final return 0; in main. Modern C permits falling off main, but returning explicitly is clearer for beginners.",
            "Expecting text without \\n to appear on its own line.",
        ],
        "exercises": [
            (
                "Type the complete example, compile it, and run it. Then remove the second printf line and predict the new output before compiling.",
                '#include <stdio.h>\n\nint main(void) {\n    printf("A C program has a beginning, a body, and an end.\\n");\n    return 0;\n}',
                "Only the first line is printed because the second printf call was removed.",
            ),
            (
                "Add a third line that prints your name, using a separate printf call.",
                '#include <stdio.h>\n\nint main(void) {\n    printf("A C program has a beginning, a body, and an end.\\n");\n    printf("Execution starts at main.\\n");\n    printf("Student: Ada\\n");\n    return 0;\n}',
                "Each printf call writes its own text. The final \\n moves to a new line after the name.",
            ),
            (
                "Explain in one sentence why #include <stdio.h> is not a runtime instruction.",
                '/* The include is handled by the preprocessor before compilation. */',
                "It supplies declarations to the compiler; no program statement runs when the include is processed.",
            ),
        ],
        "summary": (
            "You can now name every part of a minimal C program. The include supplies declarations, main is the entry "
            "point, braces form the body, statements perform work, and return 0 reports success."
        ),
        "next": "Lesson 02 turns this structure into a complete first program that you can build and run.",
        "mm": (
            "C program တစ်ခုသည် လူဖတ်နိုင်သော source file တစ်ခုမှ executable တစ်ခုအဖြစ် ဘာသာပြန်ခံရသည်။ "
            "`#include <stdio.h>` သည် preprocessor directive ဖြစ်ပြီး `printf` အတွက် declaration များကို ထည့်ပေးသည်။ "
            "Program စတင်အလုပ်လုပ်သည့်နေရာမှာ `main` ဖြစ်သည်။ `int main(void)` သည် integer တန်ဖိုးတစ်ခု ပြန်ပေးပြီး "
            "argument မလိုအပ်ကြောင်း ဖော်ပြသည်။ Brace နှစ်ခုအတွင်းရှိ statement များသည် အစဉ်လိုက် အလုပ်လုပ်သည်။ "
            "`printf` သည် စာသားကို output ထုတ်ပြီး `\\n` သည် နောက်လိုင်းသို့ ရွှေ့ပေးသည်။ `return 0;` သည် "
            "program အောင်မြင်စွာ ပြီးဆုံးကြောင်း operating system သို့ အသိပေးသည်။ C keyword များနှင့် "
            "source code ကို ဘာသာမပြန်ဘဲ မူရင်းအတိုင်း ထားရှိပါ။"
        ),
        "questions": [
            (
                "Where does execution of a C program begin?",
                ["At main", "At the first comment", "At the #include line", "At the last statement"],
                "At main",
                "main is the required entry point. Preprocessor lines and comments are not runtime instructions.",
                "multiple_choice",
            ),
            (
                "What does #include <stdio.h> provide?",
                ["Declarations for standard input/output functions", "A running web server", "A database connection", "A replacement for main"],
                "Declarations for standard input/output functions",
                "stdio.h declares functions such as printf and puts so the compiler can check your calls.",
                "multiple_choice",
            ),
            (
                "True or false: return 0; convention reports successful completion.",
                ["True", "False"],
                "True",
                "Zero is the conventional success status returned to the operating system.",
                "true_false",
            ),
            (
                "Which part groups the statements of a function?",
                ["The braces { and }", "The double quotes", "The semicolon after return", "The .c file extension"],
                "The braces { and }",
                "Braces delimit a block, including the body of a function.",
                "multiple_choice",
            ),
        ],
    },
    {
        "title": "Writing Your First C Program",
        "slug": "writing-your-first-c-program",
        "intro": (
            "This lesson is a guided build. You will create a source file, write a complete program, compile it with "
            "warnings enabled, run it, and then change it deliberately. The goal is not to memorise a command. The "
            "goal is to become comfortable with the edit-compile-run cycle that every C programmer repeats."
        ),
        "objectives": [
            "Create a C source file with the correct .c extension.",
            "Write and explain a complete Hello World program.",
            "Compile with -std=c11 -Wall -Wextra -Wpedantic and run the executable.",
            "Change a program safely by predicting the output before rebuilding.",
        ],
        "prerequisites": "A working C compiler and a terminal or editor from Module 2. You should have a writable project folder.",
        "theory": (
            "Start with a folder for your practice work. Keeping every source file in a project folder makes compiler "
            "commands short and predictable. Create a file named hello.c. The .c extension tells you and your tools "
            "that this is C source, although the compiler ultimately cares about the contents, not the name.\n\n"
            "A first program should do one small thing and do it correctly. Write the include, the main function, one "
            "printf call, and return 0. Compile it before adding features. If something fails, you then know the "
            "problem is in the small program in front of you rather than in a large unfinished experiment.\n\n"
            "The command shown in this course is one command that performs preprocessing, compilation, assembly, and "
            "linking. The option -std=c11 asks for the C11 language standard. -Wall and -Wextra turn on useful "
            "warnings. -Wpedantic asks the compiler to warn about extensions outside the standard. -o hello chooses "
            "the output name. On Windows with GCC, the output is often hello.exe and may be started as hello.exe or "
            "./hello.exe depending on the terminal.\n\n"
            "After a successful build, run the executable from the same folder. On macOS and Linux, use ./hello. The "
            "dot-slash matters because many shells do not search the current directory for commands. On Windows with "
            "MSYS2, ./hello.exe is a reliable form. Compare the observed output with the output you predicted. That "
            "comparison is the beginning of testing."
        ),
        "diagram": (
            "Edit          Compile                    Run\n"
            "hello.c  ->  gcc/clang ... -o hello  ->  ./hello\n"
            "   ^                                          |\n"
            "   |                                          v\n"
            "   +-------- change one thing <--------- compare output\n\n"
            "hello.c\n"
            "#include <stdio.h>\n"
            "int main(void) { printf(\"Hello, World!\\n\"); return 0; }"
        ),
        "definitions": [
            "Source file: the .c text file you edit.",
            "Build: the process of turning source into an executable.",
            "Warning: a diagnostic about suspicious code that may still compile.",
            "Exit status: the integer value a program returns to its caller or shell.",
            "Working directory: the folder a terminal uses to resolve relative file names.",
        ],
        "syntax": (
            "#include <stdio.h>\n\n"
            "int main(void) {\n"
            "    printf(\"Hello, World!\\n\");\n"
            "    return 0;\n"
            "}"
        ),
        "program_title": "your first complete program",
        "code": (
            '#include <stdio.h>\n\n'
            'int main(void) {\n'
            '    printf("Hello, World!\\n");\n'
            '    printf("I am learning C.\\n");\n'
            '    return 0;\n'
            '}'
        ),
        "output": "Hello, World!\nI am learning C.",
        "explanation": (
            "Line 1 provides the declaration of printf. Line 3 defines main with no parameters and an int return "
            "type. Line 4 prints Hello, World! followed by a newline. Line 5 prints the second sentence followed by "
            "a newline. Line 6 returns zero, and line 7 closes the function. The two printf calls run in order, "
            "which is why the lines appear in the order you wrote them."
        ),
        "mistakes": [
            "Saving the file as hello.txt or hello.c.txt and then wondering why the compiler cannot find hello.c.",
            "Compiling from a different folder than the one that contains hello.c.",
            "Using curly quotes from a word processor instead of straight double quotes.",
            "Forgetting a semicolon after the printf statement.",
            "Running the source file itself instead of the executable produced by the compiler.",
        ],
        "exercises": [
            (
                "Compile hello.c into an executable named hello, run it, and write down the exact command that worked on your system.",
                "gcc -std=c11 -Wall -Wextra -Wpedantic hello.c -o hello\n./hello",
                "The compiler creates hello; the shell then runs that executable from the current folder.",
            ),
            (
                "Change the first message to Hello, C! and add a third line with your country. Predict the output before compiling.",
                '#include <stdio.h>\n\nint main(void) {\n    printf("Hello, C!\\n");\n    printf("I am learning C.\\n");\n    printf("Country: Myanmar\\n");\n    return 0;\n}',
                "Each printf writes one line. The program still has one entry point and one success return value.",
            ),
            (
                "Remove the newline from the first printf and describe the changed output.",
                '#include <stdio.h>\n\nint main(void) {\n    printf("Hello, World!");\n    printf("I am learning C.\\n");\n    return 0;\n}',
                "The two messages join on one line because the first printf no longer moves to a new line.",
            ),
        ],
        "summary": (
            "You created, compiled, ran, and modified a complete C program. You also practised predicting output, "
            "which is more valuable than copying a working result."
        ),
        "next": "Lesson 03 explains the syntax rules that decide whether your program is valid C in the first place.",
        "mm": (
            "ပထမဆုံး C program ကို `hello.c` ဖိုင်အဖြစ် သိမ်းပြီး `gcc -std=c11 -Wall -Wextra -Wpedantic hello.c -o hello` "
            "ဖြင့် compile လုပ်ပါ။ macOS/Linux တွင် `./hello` ဖြင့် run ပြီး Windows တွင် `./hello.exe` ဖြစ်နိုင်သည်။ "
            "`printf` သည် စာသားကို output ထုတ်ပြီး `\\n` သည် နောက်လိုင်းသို့ ရွှေ့သည်။ Program ကို run ပြီးနောက် "
            "output နှင့် မိမိကြိုတင်ခန့်မှန်းထားသည့် ရလဒ်ကို နှိုင်းယှဉ်ပါ။ ပြောင်းလဲမှုတစ်ခုကို တစ်ကြိမ်လျှင် "
            "တစ်ခုသာ လုပ်ပြီး ပြန် compile လုပ်ခြင်းသည် အမှားရှာရန် အလွယ်ဆုံးနည်းလမ်းဖြစ်သည်။ C keyword များကို "
            "မပြောင်းလဲပါ။"
        ),
        "questions": [
            (
                "Which file name is the conventional C source file for this lesson?",
                ["hello.c", "hello.txt", "hello.exe", "hello.html"],
                "hello.c",
                "C source files conventionally use the .c extension.",
                "multiple_choice",
            ),
            (
                "Which command compiles hello.c into hello with strict C11 warnings?",
                [
                    "gcc -std=c11 -Wall -Wextra -Wpedantic hello.c -o hello",
                    "gcc --run hello.c",
                    "gcc hello.c --publish",
                    "run hello.c",
                ],
                "gcc -std=c11 -Wall -Wextra -Wpedantic hello.c -o hello",
                "The flags choose C11 and enable warnings; -o names the executable.",
                "multiple_choice",
            ),
            (
                "What happens when two printf calls both end with \\n?",
                ["They produce two separate output lines", "They always produce one line", "The program fails to compile", "The second call is ignored"],
                "They produce two separate output lines",
                "Each newline moves output to the next line, so the messages occupy separate lines.",
                "code_output",
            ),
            (
                "True or false: you run the hello.c source file directly instead of the compiled executable.",
                ["True", "False"],
                "False",
                "The compiler produces an executable, such as hello, and that executable is what runs.",
                "true_false",
            ),
        ],
    },
    {
        "title": "C Syntax Rules",
        "slug": "c-syntax-rules",
        "intro": (
            "Syntax is the grammar of a programming language. A sentence can be meaningful to a human but still be "
            "invalid C, and the compiler will reject it. This lesson gives you the small set of rules that explain most "
            "beginner syntax errors: case sensitivity, semicolons, braces, parentheses, identifiers, keywords, "
            "whitespace, string literals, character literals, and comments."
        ),
        "objectives": [
            "Recognise valid and invalid C statements.",
            "Use semicolons, braces, and parentheses correctly.",
            "Distinguish identifiers, keywords, string literals, and character literals.",
            "Explain why whitespace and capitalisation affect the compiler's view of your code.",
        ],
        "prerequisites": "Lessons 01 and 02, including one successful compile and run.",
        "theory": (
            "C is case-sensitive. The names main, Main, and MAIN are three different identifiers. Keywords such as "
            "int, return, if, and while must be written in lowercase. If you type Return, the compiler treats it as an "
            "identifier rather than a keyword and reports an error.\n\n"
            "Most statements end with a semicolon. A semicolon is a terminator, not a separator that you may sprinkle "
            "anywhere. The function definition int main(void) { ... } does not take a semicolon after its closing brace. "
            "A declaration such as int age = 20; does. When the compiler reports a missing semicolon, inspect the line "
            "before the reported location as well as the reported line.\n\n"
            "Braces group a block of statements. The body of main is a block. Parentheses group expressions and also "
            "hold function arguments. The parentheses in printf(\"Hi\\n\") are required; removing one leaves an "
            "unbalanced expression. Braces and parentheses must balance, and every opening symbol needs a matching "
            "closing symbol.\n\n"
            "An identifier is a name you create, such as age, total_score, or main. It may contain letters, digits, and "
            "underscores, but it cannot begin with a digit and cannot be a keyword. C distinguishes uppercase and "
            "lowercase letters inside identifiers. Choose descriptive names so the compiler and your future self can "
            "understand the program.\n\n"
            "A string literal is text in double quotes, such as \"Hello\". A character literal is one character in "
            "single quotes, such as 'A'. They are not interchangeable. \"A\" is a string containing A and a terminating "
            "null character; 'A' is a single char value. Double quotes must be straight quotes, not typographic quotes. "
            "A comment begins with // and continues to the end of the line, or begins with /* and ends with */. "
            "Comments are removed before compilation and have no runtime effect.\n\n"
            "Whitespace includes spaces, tabs, and newlines. Outside strings and character literals, extra whitespace "
            "usually does not change meaning, but it can change token boundaries. The compiler needs to see separate "
            "tokens such as int and main. Formatting is therefore partly for correctness and partly for human readers."
        ),
        "diagram": (
            "VALID                                  INVALID\n"
            "int age = 20;                          int age = 20      (missing ;)\n"
            "printf(\"Hi\\n\");                       printf(\"Hi\\n\")   (missing ;)\n"
            "int Main(void) { ... }                 int main(void) ...  (no body braces)\n"
            "char grade = 'A';                      char grade = \"A\";  (string, not char)\n"
            "total_score                           2score              (starts with digit)\n"
            "/* comment */                          /* outer /* inner */ */ (nested)"
        ),
        "definitions": [
            "Syntax: the grammar that determines whether source text is valid C.",
            "Case-sensitive: uppercase and lowercase letters are distinct.",
            "Token: a meaningful unit such as a keyword, identifier, literal, or punctuation mark.",
            "Identifier: a programmer-defined name for a variable, function, or other entity.",
            "Keyword: a reserved word such as int, return, or while that has special meaning.",
            "Whitespace: spaces, tabs, and line breaks used to separate tokens and format code.",
            "String literal: zero or more characters enclosed in double quotes.",
            "Character literal: one character enclosed in single quotes.",
        ],
        "syntax": (
            "int main(void) {\n"
            "    int score = 90;\n"
            "    char grade = 'A';\n"
            "    printf(\"Score: %d\\n\", score);\n"
            "    printf(\"Grade: %c\\n\", grade);\n"
            "    return 0;\n"
            "}"
        ),
        "program_title": "valid C syntax in one small program",
        "code": (
            '#include <stdio.h>\n\n'
            'int main(void) {\n'
            '    int score = 90;\n'
            '    char grade = \'A\';\n'
            '    /* Braces group the body; semicolons end statements. */\n'
            '    printf("Score: %d\\n", score);\n'
            '    printf("Grade: %c\\n", grade);\n'
            '    return 0;\n'
            '}'
        ),
        "output": "Score: 90\nGrade: A",
        "explanation": (
            "The include ends with a newline rather than a semicolon because it is a preprocessor directive. The main "
            "definition uses a return type, a name, a parameter list, and a body. The declaration int score = 90; ends "
            "with a semicolon. The character literal 'A' uses single quotes. The comment starts with /* and ends with "
            "*/ on one line. Each printf statement ends with a semicolon. The format specifiers %d and %c match the "
            "int and char arguments respectively. The closing brace ends main without a semicolon."
        ),
        "mistakes": [
            "Using a capital letter for a keyword, such as Return or Int.",
            "Placing a semicolon after the closing brace of main's definition.",
            "Mixing up double-quoted strings and single-quoted character literals.",
            "Creating an identifier that starts with a digit, such as 2score.",
            "Nesting /* ... /* ... */ ... */ block comments; C block comments do not nest.",
            "Using smart quotes copied from a document editor.",
        ],
        "exercises": [
            (
                "Fix the missing semicolon: printf(\"Hello\\n\")",
                'printf("Hello\\n");',
                "A function call statement must end with a semicolon.",
            ),
            (
                "Fix the invalid identifiers: 2score, total-score, return.",
                "int score2;\nint total_score;\nint result;",
                "Identifiers cannot start with a digit, cannot contain a hyphen, and cannot reuse a keyword.",
            ),
            (
                "Change the program so it prints a tab-separated score and grade on one line.",
                '#include <stdio.h>\n\nint main(void) {\n    int score = 90;\n    char grade = \'A\';\n    printf("Score:\\t%d\\tGrade:\\t%c\\n", score, grade);\n    return 0;\n}',
                "The \\t escape sequences insert tabs between the labels and values.",
            ),
        ],
        "summary": (
            "C syntax is small but exact. Remember case sensitivity, statement semicolons, balanced braces and "
            "parentheses, legal identifiers, straight quotes, and the difference between strings and characters."
        ),
        "next": "Lesson 04 looks closely at comments, the part of syntax that is written for humans and ignored by the compiler.",
        "mm": (
            "C သည် case-sensitive ဖြစ်သည်။ `main` နှင့် `Main` သည် မတူပါ။ Keyword များဖြစ်သော `int`, `return`, "
            "`while` တို့ကို စာလုံးအသေးဖြင့် ရေးရသည်။ Statement အများစုကို semicolon `;` ဖြင့် အဆုံးသတ်ရသည်။ "
            "Brace `{}` သည် block တစ်ခုကို စုစည်းပြီး parenthesis `()` သည် function argument နှင့် expression များကို "
            "စုစည်းသည်။ Identifier သည် ကိုယ်တိုင်ပေးသော အမည်ဖြစ်ပြီး ဂဏန်းဖြင့် မစနိုင်ပါ။ `\"A\"` သည် string ဖြစ်ပြီး "
            "`'A'` သည် character ဖြစ်သည်။ Comment များကို compiler က မဖတ်ပါ။ Whitespace များသည် ဖတ်ရလွယ်စေရန် "
            "ကူညီသော်လည်း string အတွင်းတွင် အဓိပ္ပာယ်ရှိသည်။ C keyword များနှင့် code ကို မပြောင်းလဲပါ။"
        ),
        "questions": [
            (
                "Which statement is syntactically valid?",
                ['printf("Hi\\n");', 'printf("Hi\\n")', 'Printf("Hi\\n");', 'printf("Hi\\n"'],
                'printf("Hi\\n");',
                "The function call needs balanced parentheses and a terminating semicolon.",
                "multiple_choice",
            ),
            (
                "How many different identifiers are Main, main, and MAIN in C?",
                ["Three", "One", "Two", "Zero"],
                "Three",
                "C is case-sensitive, so each spelling is a distinct identifier.",
                "multiple_choice",
            ),
            (
                "Which literal is a character literal?",
                ["'A'", '"A"', "A", "/* A */"],
                "'A'",
                "Character literals use single quotes. Double quotes create a string literal.",
                "multiple_choice",
            ),
            (
                "Which name is NOT a valid C identifier?",
                ["2score", "score2", "total_score", "grade"],
                "2score",
                "An identifier may not begin with a digit.",
                "multiple_choice",
            ),
            (
                "True or false: extra spaces and newlines always change the meaning of C tokens.",
                ["True", "False"],
                "False",
                "Whitespace usually separates tokens and formats code; it does not normally change the program's meaning outside literals.",
                "true_false",
            ),
        ],
    },
    {
        "title": "Comments in C",
        "slug": "comments-in-c",
        "intro": (
            "A comment is a note for a human reader. The compiler removes comments before translation, so they do not "
            "change what the program does. Good comments explain why a decision was made, what an input means, or what "
            "a future maintainer must know. Bad comments repeat the code or, worse, contradict it."
        ),
        "objectives": [
            "Write single-line and block comments in C.",
            "Explain the difference between a comment and a string literal.",
            "Use comments to document intent without hiding important code.",
            "Recognise common comment syntax errors.",
        ],
        "prerequisites": "Lesson 03, especially the rules for source text and tokens.",
        "theory": (
            "C has two comment forms. A single-line comment begins with // and continues to the end of that line. A "
            "block comment begins with /* and ends with */. Everything between the delimiters is ignored. A block "
            "comment may span several lines, which makes it useful for a short explanation or a temporary note.\n\n"
            "Comments do not nest. If you write /* outer /* inner */ outer */, the first */ closes the comment. The "
            "text after it is compiled, often producing confusing errors. Use // inside a block of code that is already "
            "inside a block comment, or avoid nested block comments altogether.\n\n"
            "A comment inside a string is not a comment. The text \"// not a comment\" is a string literal and is printed "
            "or processed as data. This distinction matters when you write messages that contain URLs or C-like syntax.\n\n"
            "The best beginner habit is to comment the purpose of a program or a non-obvious decision, not every line. "
            "For example, // Convert minutes to hours using floating-point division explains why 60.0 is used. A comment "
            "such as // add one above total = total + 1 adds little because the code already says it. When code changes, "
            "update the comment in the same edit; a stale comment is worse than no comment.\n\n"
            "Comments can also temporarily disable code during debugging, but do not leave large blocks commented out "
            "in a finished program. Prefer deleting unused code and relying on version control to recover it."
        ),
        "diagram": (
            "// single-line comment: ignored to end of line\n"
            "/* block comment\n"
            "   can span lines */\n\n"
            "printf(\"// this is text, not a comment\\n\");\n"
            "        ^ string delimiters win inside a literal\n\n"
            "/* outer /* inner */  <-- the first */ closes the comment\n"
            "   this text is now compiled and probably causes an error"
        ),
        "definitions": [
            "Comment: source text ignored by the compiler and intended for human readers.",
            "Single-line comment: text from // to the end of the line.",
            "Block comment: text from /* to the matching */.",
            "Self-documenting code: code whose names and structure already make its purpose clear.",
        ],
        "syntax": (
            "// Explain the purpose of the next statement.\n"
            "int total = 0;\n\n"
            "/*\n"
            " * A block comment can describe a small section.\n"
            " */\n"
            "total = total + 1;"
        ),
        "program_title": "comments do not change the output",
        "code": (
            '#include <stdio.h>\n\n'
            'int main(void) {\n'
            '    // This comment is ignored by the compiler.\n'
            '    printf("Comments are for people.\\n");\n\n'
            '    /* A block comment can span\n'
            '       more than one line. */\n'
            '    printf("The output is unchanged.\\n");\n\n'
            '    printf("The text // inside a string is printed.\\n");\n'
            '    return 0; // report success\n'
            '}'
        ),
        "output": (
            "Comments are for people.\n"
            "The output is unchanged.\n"
            "The text // inside a string is printed."
        ),
        "explanation": (
            "The first comment has no effect. The first printf prints its sentence and a newline. The block comment "
            "is ignored even though it spans two lines. The second printf prints its sentence. The third printf "
            "contains // inside a string literal, so those characters are data and are printed. The final comment "
            "after return 0; is ignored, and the statement still returns success. None of the comments appear in the "
            "program output."
        ),
        "mistakes": [
            "Nesting block comments and expecting both /* markers to have separate endings.",
            "Forgetting the closing */, which comments out the rest of the file.",
            "Writing a comment that contradicts the code after a later change.",
            "Commenting every obvious line while leaving non-obvious decisions unexplained.",
            "Thinking a comment inside a string removes the text from output.",
        ],
        "exercises": [
            (
                "Add a single-line comment above the first printf that explains what the program is demonstrating.",
                '// Show that comments do not affect program output.\nprintf("Comments are for people.\\n");',
                "The comment documents intent for a reader and is removed before compilation.",
            ),
            (
                "Fix this block comment: /* first line * second line */",
                '/* first line\n * second line */',
                "The closing delimiter must be exactly */, and each line can be formatted for readability.",
            ),
            (
                "Add a useful comment that explains why floating-point division is used.",
                'double hours = minutes / 60.0; // 60.0 forces floating-point division.',
                "The comment explains a non-obvious choice rather than repeating the variable name.",
            ),
        ],
        "summary": (
            "Comments are removed before compilation and exist only for readers. Use // for short notes and /* ... */ "
            "for blocks, never nest them, and explain intent rather than restating syntax."
        ),
        "next": "Lesson 05 examines printf, the function that turns values into visible output.",
        "mm": (
            "Comment သည် လူဖတ်ရန် ရေးသားသော မှတ်ချက်ဖြစ်ပြီး compiler က လုံးဝ မဖတ်ပါ။ `//` သည် ထိုလိုင်း၏ အဆုံးအထိ "
            "comment ဖြစ်ပြီး `/* ... */` သည် လိုင်းများစွာကို ဖုံးလွှမ်းနိုင်သည်။ Block comment များကို ထပ်မံ nest လုပ်၍ "
            "မရပါ။ String အတွင်းရှိ `//` သည် comment မဟုတ်ဘဲ စာသားအဖြစ် output ထွက်သည်။ ကောင်းသော comment သည် "
            "code ကို ပြန်မဖော်ပြဘဲ ဘာကြောင့် ထိုနည်းလမ်းကို ရွေးချယ်သည်ကို ရှင်းပြသည်။ Code ပြောင်းလဲသောအခါ "
            "comment ကိုပါ တွဲဖက်ပြောင်းရပါသည်။ C keyword များနှင့် code ကို မပြောင်းလဲပါ။"
        ),
        "questions": [
            (
                "Which syntax starts a single-line comment?",
                ["//", "/*", "#", "<!--"],
                "//",
                "Two forward slashes begin a comment that continues to the end of the line.",
                "multiple_choice",
            ),
            (
                "Which pair correctly delimits a block comment?",
                ["/* and */", "// and //", "<!-- and -->", "{ and }"],
                "/* and */",
                "C block comments begin with /* and end with */.",
                "multiple_choice",
            ),
            (
                "What is printed by printf(\"// hello\\n\"); ?",
                ["// hello", "Nothing, because it is a comment", "hello only", "The program does not compile"],
                "// hello",
                "Inside a string literal, // is ordinary text, not a comment.",
                "code_output",
            ),
            (
                "True or false: C block comments can be nested safely.",
                ["True", "False"],
                "False",
                "The first */ closes the block; block comments do not nest.",
                "true_false",
            ),
        ],
    },
    {
        "title": "Understanding printf()",
        "slug": "understanding-printf",
        "intro": (
            "printf is the standard C function for formatted output. It receives a format string that describes what "
            "to print and, optionally, additional arguments whose values are inserted into the format string. Learning "
            "printf well gives you a reliable way to observe what a program is doing."
        ),
        "objectives": [
            "Call printf with a format string and matching arguments.",
            "Print text, integers, floating-point values, characters, and strings.",
            "Explain why newline escape sequences are needed for clean output.",
            "Recognise mismatches between a format specifier and an argument type.",
        ],
        "prerequisites": "Lesson 04 and the ability to compile and run a program with -Wall -Wextra -Wpedantic.",
        "theory": (
            "A function call has a name, a pair of parentheses, and zero or more arguments. In "
            "printf(\"Age: %d\\n\", age); the name is printf. The first argument is the format string. It contains "
            "ordinary characters and conversion specifications such as %d. Each conversion specification consumes a "
            "later argument. The argument age supplies the value for %d. The \\n moves output to a new line. The "
            "semicolon ends the statement.\n\n"
            "printf writes to standard output, which is normally the terminal. It does not automatically add a newline. "
            "If you omit \\n, the next output continues on the same line. This is why two printf calls can produce one "
            "visual line, and why forgetting a newline is a common reason for messy output. You can also put several "
            "values in one call, for example printf(\"%d + %d = %d\\n\", 2, 3, 5);.\n\n"
            "The format string is not a template language that guesses types. The conversion specification tells printf "
            "how to interpret the next argument. If the specification and the argument disagree, the behavior is "
            "undefined; the compiler may warn, or it may silently print nonsense. Always compile with warnings enabled "
            "and correct every format warning.\n\n"
            "printf returns an int: the number of characters written, or a negative value on failure. Beginners rarely "
            "need that return value, but it is useful to know that printf is a real function with a result. The function "
            "is declared in <stdio.h>, so a program that calls printf must include that header.\n\n"
            "Use printf deliberately. A short message before a value makes output readable: printf(\"Total: %d\\n\", "
            "total);. Avoid printing a bare number when you will later need to understand the output."
        ),
        "diagram": (
            "printf(\"Age: %d\\n\", age);\n"
            "       |        |     |\n"
            "       |        |     +-- argument consumed by %d\n"
            "       |        +-------- conversion specification\n"
            "       +----------------- format string\n\n"
            "Output pipeline\n"
            "format string + arguments -> printf -> standard output -> terminal"
        ),
        "definitions": [
            "Function call: an expression that invokes a function with arguments.",
            "Format string: the first printf argument, containing text and conversion specifications.",
            "Conversion specification: a % sequence such as %d that describes how to format a value.",
            "Standard output: the default output stream, usually the terminal.",
            "Argument: a value passed to a function.",
        ],
        "syntax": (
            "printf(\"literal text\");\n"
            "printf(\"integer: %d\\n\", 42);\n"
            "printf(\"two values: %d and %c\\n\", 7, 'A');"
        ),
        "program_title": "printing text and values with printf",
        "code": (
            '#include <stdio.h>\n\n'
            'int main(void) {\n'
            '    int lessons = 10;\n'
            '    int completed = 4;\n'
            '    double hours = 2.5;\n'
            '    char grade = \'A\';\n'
            '    const char *name = "Mya";\n\n'
            '    printf("Student: %s\\n", name);\n'
            '    printf("Lessons: %d\\n", lessons);\n'
            '    printf("Completed: %d of %d\\n", completed, lessons);\n'
            '    printf("Study time: %.1f hours\\n", hours);\n'
            '    printf("Grade: %c\\n", grade);\n'
            '    return 0;\n'
            '}'
        ),
        "output": (
            "Student: Mya\n"
            "Lessons: 10\n"
            "Completed: 4 of 10\n"
            "Study time: 2.5 hours\n"
            "Grade: A"
        ),
        "explanation": (
            "The include makes printf visible. The declarations create values of different types. The first printf "
            "uses %s for the string name. The second uses %d for the int lessons. The third uses two %d specifications "
            "and supplies two int arguments in the same order. The fourth uses %.1f to print a double with one digit "
            "after the decimal point. The fifth uses %c for a char. Each call ends its output with \\n."
        ),
        "mistakes": [
            "Calling printf without including <stdio.h>.",
            "Forgetting the newline and then wondering why messages run together.",
            "Passing a double to %d or an int to %f.",
            "Supplying fewer arguments than conversion specifications.",
            "Using a single quote instead of double quotes for the format string.",
            "Forgetting the semicolon after the printf statement.",
        ],
        "exercises": [
            (
                "Write one printf call that prints your name and age using %s and %d.",
                '#include <stdio.h>\n\nint main(void) {\n    printf("Name: %s, age: %d\\n", "Ada", 20);\n    return 0;\n}',
                "The string argument matches %s and the integer matches %d, in order.",
            ),
            (
                "Print the numbers 3 and 7 on one line separated by a tab.",
                '#include <stdio.h>\n\nint main(void) {\n    printf("%d\\t%d\\n", 3, 7);\n    return 0;\n}',
                "The \\t escape sequence inserts a tab between the two formatted integers.",
            ),
            (
                "Fix the incorrect call printf(\"%d\\n\", 3.5);",
                '#include <stdio.h>\n\nint main(void) {\n    printf("%.1f\\n", 3.5);\n    return 0;\n}',
                "A floating-point value requires a floating-point conversion, such as %f or %.1f, not %d.",
            ),
        ],
        "summary": (
            "printf combines a format string with matching arguments. Use %d, %f, %c, and %s for the common types, "
            "include \\n when you need a new line, and keep every format specifier consistent with its value."
        ),
        "next": "Lesson 06 expands the escape sequences that let you control spacing, quotes, and other special characters.",
        "mm": (
            "`printf` သည် format string တစ်ခုနှင့် နောက်ဆက်တွဲ argument များကို ပေါင်းစပ်ပြီး output ထုတ်သည်။ "
            "`Age: %d\\n` တွင် `Age: ` သည် ပုံမှန်စာသား၊ `%d` သည် integer တန်ဖိုးအတွက် နေရာဖြစ်ပြီး `\\n` သည် "
            "နောက်လိုင်းသို့ ရွှေ့သည်။ `printf` သည် newline ကို အလိုအလျောက် မထည့်ပါ။ Format specifier နှင့် "
            "argument အမျိုးအစား မတူညီပါက behavior သည် မသေချာသဖြင့် warning များကို မလျစ်လျူရှုပါနှင့်။ "
            "`printf` ကို အသုံးပြုရန် `#include <stdio.h>` လိုအပ်သည်။ C keyword များနှင့် code ကို "
            "မပြောင်းလဲပါ။"
        ),
        "questions": [
            (
                "Which header declares printf?",
                ["<stdio.h>", "<stdlib.h>", "<string.h>", "<math.h>"],
                "<stdio.h>",
                "The standard input/output header declares printf.",
                "multiple_choice",
            ),
            (
                "Which format specifier prints an int?",
                ["%d", "%f", "%c", "%s"],
                "%d",
                "%d is the conversion for a signed int.",
                "multiple_choice",
            ),
            (
                "What is the output of printf(\"A\"); printf(\"B\\n\"); ?",
                ["AB followed by a newline", "A and B on separate lines", "Only A", "Only B"],
                "AB followed by a newline",
                "The first call has no newline, so B follows immediately on the same line.",
                "code_output",
            ),
            (
                "True or false: printf adds a newline automatically after every call.",
                ["True", "False"],
                "False",
                "You must include \\n when you want a newline.",
                "true_false",
            ),
        ],
    },
    {
        "title": "Escape Sequences",
        "slug": "escape-sequences",
        "intro": (
            "An escape sequence is a pair of characters that represents one special character. Escape sequences let you "
            "put a newline, a tab, a double quote, a backslash, a carriage return, or a null character inside a string "
            "literal even though those characters would otherwise be difficult to type or would end the literal."
        ),
        "objectives": [
            "Use \\n, \\t, \\\", \\\\, \\r, and \\0 inside strings.",
            "Predict the visible output of a string containing escape sequences.",
            "Explain the difference between a visible backslash and an escape sequence.",
            "Avoid invalid escape sequences and accidental string termination.",
        ],
        "prerequisites": "Lessons 04 and 05, including printf and string literals.",
        "theory": (
            "A string literal is enclosed in double quotes. If you need a double quote inside it, write \\\" so the "
            "compiler knows the quote is data rather than the end of the string. If you need a literal backslash, write "
            "\\\\. A single backslash followed by an ordinary character may be an invalid escape sequence, so always "
            "check the pair.\n\n"
            "The newline escape \\n moves the output position to the beginning of the next line. The tab escape \\t "
            "moves to the next tab stop, which is useful for simple columns. These escapes do not print the letters n "
            "or t; they print control characters that affect the terminal.\n\n"
            "The carriage return escape \\r moves the cursor to the beginning of the current line without moving to the "
            "next line. A later character can overwrite what was already displayed. For example, the byte sequence "
            "Loading...\\rDone!\\n first displays Loading..., returns the cursor to the start, and then writes Done! "
            "over the beginning. On a terminal the visible result is usually Done! followed by spaces from the old text. "
            "The exact screen appearance depends on the terminal; the underlying output still contains the carriage "
            "return byte. Print a newline after using \\r so the final display is predictable.\n\n"
            "The null character \\0 has the integer value zero. C uses it to mark the end of a string in memory. When "
            "printf processes a format string containing \\0, it stops there. The text after the null character is not "
            "printed. Character arrays created from string literals automatically receive a terminating null character, "
            "but you do not normally type it yourself.\n\n"
            "Escape sequences are processed when the compiler translates the literal. They are not interpreted by "
            "printf as a special mini-language. By the time printf receives the string, the escape has already become "
            "the corresponding character."
        ),
        "diagram": (
            "Escape     Meaning                         Example output effect\n"
            "\\n         newline                         start a new line\n"
            "\\t         horizontal tab                  align simple columns\n"
            "\\\"         double quote                    \" inside a string\n"
            "\\\\         backslash                       \\ inside a string\n"
            "\\r         carriage return                 move to line start\n"
            "\\0         null character                  ends a C string\n\n"
            "Raw bytes for \"A\\tB\\n\":  A  TAB  B  NEWLINE\n"
            "Raw bytes for \"Loading...\\rDone!\\n\": Loading...  CR  Done!  NEWLINE"
        ),
        "definitions": [
            "Escape sequence: a backslash followed by a character that represents a special character.",
            "Newline: the control character that starts a new output line.",
            "Tab: a control character that advances to the next tab stop.",
            "Carriage return: a control character that returns the cursor to the start of the current line.",
            "Null character: the zero-valued character used to terminate a C string.",
        ],
        "syntax": (
            "printf(\"Line one\\nLine two\\n\");\n"
            "printf(\"Name:\\tAda\\n\");\n"
            "printf(\"She said, \\\"Hello\\\".\\n\");\n"
            "printf(\"Path: C:\\\\code\\\\main.c\\n\");"
        ),
        "program_title": "newlines, tabs, quotes, backslashes, and a null character",
        "code": (
            '#include <stdio.h>\n\n'
            'int main(void) {\n'
            '    printf("Name:\\tAda\\n");\n'
            '    printf("Quote:\\t\\\"Hello, C!\\\"\\n");\n'
            '    printf("Path:\\tC:\\\\code\\\\main.c\\n");\n'
            '    const char message[] = "A\\0B";\n'
            '    printf("%s", message);\n'
            '    printf("\\n");\n'
            '    return 0;\n'
            '}'
        ),
        "output": (
            "Name:\tAda\n"
            "Quote:\t\"Hello, C!\"\n"
            "Path:\tC:\\code\\main.c\n"
            "A"
        ),
        "explanation": (
            "Line 4 prints Name:, a tab, Ada, and a newline. Line 5 prints a literal double quote around Hello, C!. "
            "Line 6 uses \\\\ twice so the output path contains real backslashes rather than escape sequences. Line 7 "
            "creates a character array whose literal contains the bytes A, a null character, and B. Line 8 prints that "
            "array with %s; printf stops at the null character, so only A appears. Line 9 prints a newline so the "
            "program ends with a clean line. The difference between the source text \\\\ and the visible output \\ is "
            "the key idea in this lesson."
        ),
        "mistakes": [
            "Writing \\n as two visible characters when a newline was intended, or expecting \\n to print the letter n.",
            "Forgetting to escape a double quote inside a string.",
            "Using a single backslash before an ordinary character that has no defined escape.",
            "Expecting the text after \\0 to print.",
            "Assuming \\r creates a new line. It returns to the start of the current line.",
        ],
        "exercises": [
            (
                "Print a two-column table with Name and Score headers using tabs.",
                '#include <stdio.h>\n\nint main(void) {\n    printf("Name\\tScore\\n");\n    printf("Ada\\t95\\n");\n    return 0;\n}',
                "The \\t escape sequences advance to tab stops so the columns line up in a simple terminal.",
            ),
            (
                "Print the exact text She said, \"C is fun!\" including the double quotes.",
                '#include <stdio.h>\n\nint main(void) {\n    printf("She said, \\\"C is fun!\\\"\\n");\n    return 0;\n}',
                "The escaped quotes \\\" are data, so the string continues until the unescaped final quote.",
            ),
            (
                "Print a Windows-style path C:\\practice\\hello.c exactly.",
                '#include <stdio.h>\n\nint main(void) {\n    printf("C:\\\\practice\\\\hello.c\\n");\n    return 0;\n}',
                "Each visible backslash requires two backslashes in the source literal.",
            ),
            (
                "Explain why printf(\"A\\0B\\n\"); does not print B or the newline.",
                'printf("A");\nprintf("\\n");',
                "printf stops at the null character in the format string, so B and the trailing newline are never processed. A separate newline call keeps the output tidy.",
            ),
        ],
        "summary": (
            "Escape sequences represent control and special characters inside literals. Remember \\n for a newline, "
            "\\t for a tab, \\\" and \\\\ for literal quote and backslash, \\r for carriage return, and \\0 as the "
            "string terminator."
        ),
        "next": "Lesson 07 goes deeper into format specifiers, including width, precision, and type compatibility.",
        "mm": (
            "Escape sequence သည် string အတွင်းတွင် အထူးအက္ခရာတစ်ခုကို ကိုယ်စားပြုသည်။ `\\n` သည် နောက်လိုင်းသို့ "
            "ရွှေ့ပြီး `\\t` သည် tab အကွာအဝေးသို့ ရွှေ့သည်။ `\\\"` ဖြင့် စာသားအတွင်း double quote ထည့်နိုင်ပြီး `\\\\` "
            "ဖြင့် မြင်နိုင်သော backslash တစ်ခု ထုတ်နိုင်သည်။ `\\r` သည် လက်ရှိလိုင်း၏ အစသို့ ပြန်ရွှေ့ပြီး `\\0` သည် "
            "C string ကို အဆုံးသတ်ပေးသည်။ `\\0` နောက်ရှိ စာသားများကို `printf` က ဆက်မဖတ်ပါ။ Escape များကို "
            "compiler က literal ကို ဘာသာပြန်ချိန်တွင် ပြောင်းလဲပြီးဖြစ်သည်။ C keyword များနှင့် code ကို "
            "မပြောင်းလဲပါ။"
        ),
        "questions": [
            (
                "Which escape sequence inserts a tab?",
                ["\\t", "\\n", "\\r", "\\0"],
                "\\t",
                "\\t represents a horizontal tab.",
                "multiple_choice",
            ),
            (
                "Which escape sequence produces one visible backslash?",
                ["\\\\", "\\", "\\n", "\\t"],
                "\\\\",
                "A literal backslash is written as two backslashes in source code.",
                "multiple_choice",
            ),
            (
                "What is printed by printf(\"A\\tB\\n\"); ?",
                ["A, a tab, B, and a newline", "A, the letter t, B", "AB on two lines", "Nothing"],
                "A, a tab, B, and a newline",
                "The tab character separates A and B, and \\n ends the line.",
                "code_output",
            ),
            (
                "What happens when printf reaches \\0 in its format string?",
                ["It stops processing the string", "It prints the digit zero", "It starts a new line", "It restarts the program"],
                "It stops processing the string",
                "The null character terminates a C string, so later characters are not processed.",
                "multiple_choice",
            ),
        ],
    },
    {
        "title": "Format Specifiers",
        "slug": "format-specifiers",
        "intro": (
            "Format specifiers are the small codes inside a printf format string that tell the function how to display "
            "the next argument. Using the right specifier produces readable output; using the wrong one can produce "
            "warnings, nonsense, or undefined behavior. This lesson covers %d, %f, %c, %s, and %%, plus width and "
            "precision."
        ),
        "objectives": [
            "Match %d, %f, %c, %s, and %% with the correct kinds of values.",
            "Control field width and decimal precision in output.",
            "Explain why a format specifier must be type-compatible with its argument.",
            "Print a literal percent sign without a conversion.",
        ],
        "prerequisites": "Lesson 06 and confidence with printf calls.",
        "theory": (
            "The conversion specification begins with % and ends with a conversion character. %d or %i displays a "
            "signed int as a decimal integer. %f displays a double (and a float after default argument promotion) in "
            "decimal notation. %c displays one char. %s displays a string, which is a sequence of characters ending in "
            "a null character. %% does not consume an argument; it prints one literal percent sign.\n\n"
            "A format specifier is a promise about the argument's type. If you pass an int to %f, printf will try to "
            "read a floating-point value from storage that actually contains an int. The C standard does not define a "
            "useful result for that mismatch. Compilers with -Wall and -Wextra often diagnose it, but you must still "
            "read and fix the warning. Do not use a cast to silence a format warning unless you truly understand the "
            "conversion you are asking for.\n\n"
            "Width and precision add control. In %5d, the 5 is a minimum field width: the value is right-aligned in a "
            "field of at least five characters. In %-5d, the minus sign left-aligns it. In %05d, zeros pad the field. "
            "In %.2f, the .2 is precision: two digits after the decimal point for a floating-point value. In %8.3f, the "
            "field is at least eight characters wide and the value has three digits after the decimal point. For "
            "strings, %.3s prints at most three characters.\n\nThe percent sign has special meaning in a format string, "
            "so to print 100% you write 100%%. Writing a lone % at the end of a format string is invalid because the "
            "compiler and printf expect a conversion character after it.\n\n"
            "Be deliberate about types. An int is a whole number, a double is a floating-point number, a char is one "
            "character, and a string is a sequence of characters. Choose the specifier that matches the value you "
            "actually have, not the appearance you want."
        ),
        "diagram": (
            "%8.3f\n"
            " | | |\n"
            " | | +-- conversion: floating point\n"
            " | +---- precision: three digits after the decimal point\n"
            " +------ minimum field width: eight characters\n\n"
            "%d  int       42\n"
            "%f  double    3.140000 (default six decimals)\n"
            "%c  char      A\n"
            "%s  string    Ada\n"
            "%%  no value  %"
        ),
        "definitions": [
            "Format specifier: a conversion specification beginning with % in a formatted output string.",
            "Field width: the minimum number of characters used for one formatted value.",
            "Precision: the number of digits after the decimal point for floating-point output, or a maximum character count for strings.",
            "Type compatibility: the requirement that the argument type matches what the conversion expects.",
            "Default argument promotion: the automatic conversion of float arguments to double in a variadic call such as printf.",
        ],
        "syntax": (
            "printf(\"%d\\n\", 42);\n"
            "printf(\"%.2f\\n\", 3.14159);\n"
            "printf(\"%c\\n\", 'A');\n"
            "printf(\"%s\\n\", \"Ada\");\n"
            "printf(\"%5d|%-5d|%05d\\n\", 42, 42, 42);\n"
            "printf(\"100%% complete\\n\");"
        ),
        "program_title": "printing each common type correctly",
        "code": (
            '#include <stdio.h>\n\n'
            'int main(void) {\n'
            '    int age = 21;\n'
            '    double height = 1.68;\n'
            '    char grade = \'A\';\n'
            '    const char *name = "Mya";\n\n'
            '    printf("%s is %d years old.\\n", name, age);\n'
            '    printf("Height: %.2f m\\n", height);\n'
            '    printf("Grade: %c\\n", grade);\n'
            '    printf("Progress: 100%%\\n");\n'
            '    printf("|%5d|%-5d|%05d|\\n", 42, 42, 42);\n'
            '    return 0;\n'
            '}'
        ),
        "output": (
            "Mya is 21 years old.\n"
            "Height: 1.68 m\n"
            "Grade: A\n"
            "Progress: 100%\n"
            "|   42|42   |00042|"
        ),
        "explanation": (
            "The first printf uses %s for the string and %d for the integer. The second uses %.2f for a double with "
            "exactly two digits after the decimal point. The third uses %c for a single character. The fourth uses %% "
            "to print a literal percent sign; it does not consume an argument. The final printf shows three integer "
            "field formats: %5d right-aligns 42 in a width of five, %-5d left-aligns it, and %05d pads with zeros. "
            "All conversions match their arguments."
        ),
        "mistakes": [
            "Using %d for a double or %f for an int.",
            "Forgetting to double %% when a literal percent sign is required.",
            "Assuming %f always prints two decimal places; its default is six.",
            "Passing a character string to %c or a single char to %s.",
            "Supplying the wrong number of arguments for the format string.",
        ],
        "exercises": [
            (
                "Print 3.14159 rounded visually to two decimal places.",
                '#include <stdio.h>\n\nint main(void) {\n    printf("%.2f\\n", 3.14159);\n    return 0;\n}',
                "The precision .2 limits floating-point output to two digits after the decimal point.",
            ),
            (
                "Print the number 7 in a field of width 3, both right-aligned and zero-padded.",
                '#include <stdio.h>\n\nint main(void) {\n    printf("|%3d|%03d|\\n", 7, 7);\n    return 0;\n}',
                "%3d right-aligns in three characters; %03d uses zeros as padding.",
            ),
            (
                "Fix printf(\"Discount: 20%\\n\"); so it prints a literal percent sign.",
                '#include <stdio.h>\n\nint main(void) {\n    printf("Discount: 20%%\\n");\n    return 0;\n}',
                "A literal percent sign is written as %% in the format string.",
            ),
            (
                "Explain why printf(\"%d\\n\", 2.5); is unsafe.",
                'printf("%.1f\\n", 2.5);',
                "The %d conversion expects an int, but 2.5 is a double. The corrected call uses a floating-point conversion.",
            ),
        ],
        "summary": (
            "Use %d for int, %f for double, %c for char, %s for strings, and %% for a literal percent sign. Width and "
            "precision improve readability, but type compatibility is mandatory."
        ),
        "next": "Lesson 08 shows how the compiler and linker turn these source files into a running program.",
        "mm": (
            "Format specifier သည် `printf` အတွက် တန်ဖိုးတစ်ခုကို ဘယ်လိုပြသမည်ကို ဖော်ပြသည်။ `%d` သည် `int`၊ "
            "`%f` သည် `double`၊ `%c` သည် `char`၊ `%s` သည် string အတွက်ဖြစ်ပြီး `%%` သည် ရာခိုင်နှုန်းသင်္ကေတ "
            "တစ်ခုကို ပြသည်။ `%5d` တွင် 5 သည် အနည်းဆုံး field width ဖြစ်ပြီး `%.2f` တွင် 2 သည် ဒဿမနောက် "
            "ဂဏန်းနှစ်လုံးကို ပြသည်။ Format specifier နှင့် argument အမျိုးအစား မတူညီပါက ရလဒ်သည် မသေချာပါ။ "
            "ထို့ကြောင့် warning များကို ဖတ်ပြီး ပြင်ဆင်ပါ။ C keyword များနှင့် code ကို မပြောင်းလဲပါ။"
        ),
        "questions": [
            (
                "Which specifier prints a double with two digits after the decimal point?",
                ["%.2f", "%2d", "%c", "%s"],
                "%.2f",
                "The .2 precision controls the digits after the decimal point for a floating-point conversion.",
                "multiple_choice",
            ),
            (
                "Which specifier prints a string?",
                ["%s", "%c", "%d", "%f"],
                "%s",
                "%s consumes a pointer to a null-terminated string.",
                "multiple_choice",
            ),
            (
                "What is the output of printf(\"%.2f\\n\", 3.14159); ?",
                ["3.14", "3.14159", "3.1", "3"],
                "3.14",
                "The precision .2 rounds the displayed value to two digits after the decimal point.",
                "code_output",
            ),
            (
                "Which call correctly prints a literal percent sign?",
                ['printf("100%%\\n");', 'printf("100%\\n");', 'printf("100%s\\n");', 'printf("100%c\\n");'],
                'printf("100%%\\n");',
                "%% is the conversion that prints one percent sign without consuming an argument.",
                "multiple_choice",
            ),
            (
                "True or false: using %d with a double has a guaranteed, portable result.",
                ["True", "False"],
                "False",
                "The format and argument types must be compatible; a mismatch has undefined behavior.",
                "true_false",
            ),
        ],
    },
    {
        "title": "Compilation & Execution",
        "slug": "compilation-and-execution",
        "intro": (
            "Compilation turns your readable C source into an executable program. The process has several conceptual "
            "stages, and understanding them makes compiler messages much less mysterious. In this lesson you will build "
            "with C11 and strict warnings on Windows, macOS, and Linux, run the result, and interpret the most common "
            "diagnostics."
        ),
        "objectives": [
            "Describe preprocessing, compilation, assembly, and linking.",
            "Compile a C11 program with -Wall -Wextra -Wpedantic on three operating systems.",
            "Run an executable and inspect its exit status.",
            "Distinguish compiler errors, linker errors, warnings, and logical errors.",
        ],
        "prerequisites": "Lessons 01–07 and a working GCC or Clang installation from Module 2.",
        "theory": (
            "The preprocessor handles lines that begin with #. It expands #include directives, substitutes macros, and "
            "evaluates conditional compilation. The compiler then parses the resulting translation unit, checks syntax "
            "and types, and produces assembly or object code. The assembler turns that into machine-code object files. "
            "The linker combines your object file with library object code and startup code to produce the final "
            "executable. A single gcc or clang command normally performs all of these stages.\n\n"
            "Use explicit options while learning. -std=c11 selects the C11 standard. -Wall enables a broad set of "
            "warnings. -Wextra adds more warnings. -Wpedantic warns about language extensions that are not standard C. "
            "-o names the output file.\n\n"
            "Windows: install MSYS2, open the UCRT64 terminal, then run pacman -S mingw-w64-ucrt-x86_64-gcc. The same "
            "gcc and clang commands work in PowerShell, Command Prompt, and the MSYS2 shell; type hello.exe or "
            ".\\hello.exe to run the program.\n\n"
            "macOS: install the Apple Command Line Tools with xcode-select --install. Both clang and gcc are available, "
            "and ./hello runs the executable.\n\n"
            "Linux: install a compiler with sudo apt install build-essential (Debian/Ubuntu) or sudo dnf install gcc "
            "(Fedora). Use clang instead of gcc when you prefer Clang; the warning flags are the same.\n\n"
            "The shell runs the executable you produced, not the source file. On macOS and Linux, ./hello means run "
            "hello from the current directory. On Windows, hello.exe or .\\hello.exe is typical. After the program ends, "
            "the shell can report its exit status. In a POSIX shell, echo $? shows the status of the previous command. A "
            "status of 0 means success by convention.\n\n"
            "A compiler error means translation could not produce a valid program. A warning means the compiler found "
            "something suspicious but could still produce an executable. A linker error occurs after compilation when a "
            "referenced symbol has no definition. A runtime error occurs while the program runs, for example a division "
            "by zero. A logical error is worse in a different way: the program compiles, links, and runs, but produces "
            "the wrong answer. Tests and careful reasoning are required to catch logical errors.\n\n"
            "Read diagnostics from the first reported line. Fix one issue, rebuild, and read again. Chasing later "
            "messages before resolving the first one often wastes time because one syntax mistake can produce a cascade "
            "of misleading diagnostics."
        ),
        "diagram": (
            "hello.c\n"
            "   | preprocessor: includes, macros\n"
            "   v\n"
            "translation unit\n"
            "   | compiler: syntax and types\n"
            "   v\n"
            "assembly / object code\n"
            "   | assembler + linker + libraries\n"
            "   v\n"
            "hello (or hello.exe)\n"
            "   | operating system starts main\n"
            "   v\n"
            "program output + exit status"
        ),
        "definitions": [
            "Preprocessing: expanding directives and macros before compilation.",
            "Translation unit: the source file after preprocessing, as seen by the compiler.",
            "Object code: machine-oriented code that is not yet a complete executable.",
            "Linking: combining object code and libraries into an executable.",
            "Exit status: the integer value returned by main to the operating system.",
            "Diagnostic: a compiler or linker message describing a problem.",
        ],
        "syntax": (
            "# macOS: install the compiler once\n"
            "xcode-select --install\n"
            "clang -std=c11 -Wall -Wextra -Wpedantic hello.c -o hello\n"
            "./hello\n\n"
            "# Linux (Debian/Ubuntu): install the compiler once\n"
            "sudo apt install build-essential\n"
            "gcc -std=c11 -Wall -Wextra -Wpedantic hello.c -o hello\n"
            "./hello\n\n"
            "# Windows: install MSYS2 UCRT64, then build\n"
            "gcc -std=c11 -Wall -Wextra -Wpedantic hello.c -o hello.exe\n"
            "hello.exe\n\n"
            "# Windows PowerShell uses the same build command\n"
            ".\\hello.exe"
        ),
        "program_title": "a build-and-run test program",
        "code": (
            '#include <stdio.h>\n\n'
            'int main(void) {\n'
            '    int width = 6;\n'
            '    int height = 4;\n'
            '    printf("Rectangle area: %d\\n", width * height);\n'
            '    return 0;\n'
            '}'
        ),
        "output": "Rectangle area: 24",
        "explanation": (
            "The preprocessor supplies the declaration of printf. The compiler checks the declarations, the "
            "multiplication expression, and the printf call. The linker supplies the implementation of printf from the "
            "C standard library. At runtime the operating system starts main, width * height evaluates to 24, printf "
            "writes the line, and return 0 reports success. If the program printed a wrong number, the build would still "
            "have succeeded, which would make it a logical error rather than a compiler error."
        ),
        "mistakes": [
            "Typing gcc hello.c -o hello and then running hello.c instead of ./hello.",
            "Compiling an old file because the terminal is in the wrong directory.",
            "Ignoring warnings that identify a format-specifier mismatch.",
            "Assuming a successful compile proves the output is correct.",
            "Trying to run an executable after a linker error produced no new executable.",
        ],
        "exercises": [
            (
                "Compile the example with all three warning flags, run it, and report the exit status.",
                "gcc -std=c11 -Wall -Wextra -Wpedantic build.c -o build\n./build\necho $?",
                "The program prints the area and returns 0, so the shell reports 0.",
            ),
            (
                "Change width to 7 and height to 3, predict the output, and rebuild.",
                '#include <stdio.h>\n\nint main(void) {\n    int width = 7;\n    int height = 3;\n    printf("Rectangle area: %d\\n", width * height);\n    return 0;\n}',
                "The multiplication now evaluates to 21, so the output is Rectangle area: 21.",
            ),
            (
                "Introduce an unused variable, compile with -Wall -Wextra, and explain the warning.",
                '#include <stdio.h>\n\nint main(void) {\n    int unused = 5;\n    printf("Warnings are useful.\\n");\n    return 0;\n}',
                "The compiler warns that unused is set but not used, which often reveals leftover or misspelled code.",
            ),
            (
                "Remove a semicolon from the printf statement and classify the resulting problem.",
                'printf("Rectangle area: %d\\n", width * height);',
                "The missing semicolon is a compile-time syntax error; the compiler stops before producing a reliable executable.",
            ),
        ],
        "summary": (
            "A C build moves from source through preprocessing, compilation, assembly, and linking to an executable. "
            "Use -std=c11 -Wall -Wextra -Wpedantic, run the produced file, and separate compiler, linker, runtime, and "
            "logical errors."
        ),
        "next": "Lesson 09 collects the most common beginner mistakes and shows how to diagnose each one.",
        "mm": (
            "C build သည် preprocessing၊ compilation၊ assembly နှင့် linking အဆင့်များဖြင့် source ကို executable "
            "အဖြစ် ပြောင်းသည်။ `-std=c11` သည် C11 standard ကို ရွေးပြီး `-Wall -Wextra -Wpedantic` သည် warning "
            "များကို ဖွင့်ပေးသည်။ `-o hello` သည် output အမည်ကို သတ်မှတ်သည်။ macOS/Linux တွင် `./hello` ဖြင့် "
            "run ပြီး Windows တွင် `hello.exe` ဖြစ်နိုင်သည်။ Compiler error သည် ဘာသာပြန်ခြင်း မအောင်မြင်ခြင်း၊ "
            "linker error သည် symbol definition မတွေ့ခြင်း၊ logical error သည် run ဖြစ်သော်လည်း ရလဒ်မှားခြင်း "
            "ဖြစ်သည်။ ပထမဆုံး diagnostic ကို အရင်ဖတ်ပါ။ C keyword များနှင့် command များကို မပြောင်းလဲပါ။"
        ),
        "questions": [
            (
                "Which flag selects the C11 language standard?",
                ["-std=c11", "-o", "-Wall", "-Wpedantic"],
                "-std=c11",
                "The -std option selects the language standard used by the compiler.",
                "multiple_choice",
            ),
            (
                "Which command compiles hello.c into an executable named hello on macOS or Linux?",
                [
                    "clang -std=c11 -Wall -Wextra -Wpedantic hello.c -o hello",
                    "clang hello.c --execute",
                    "run hello.c",
                    "clang -o hello.c hello",
                ],
                "clang -std=c11 -Wall -Wextra -Wpedantic hello.c -o hello",
                "The source file comes before -o, and the desired output name follows -o.",
                "multiple_choice",
            ),
            (
                "What usually causes an undefined reference error?",
                ["The linker cannot find a referenced definition", "The source file has a comment", "The program printed too much", "The terminal is too small"],
                "The linker cannot find a referenced definition",
                "Linker errors occur when a symbol is used but no definition or required library is supplied.",
                "multiple_choice",
            ),
            (
                "True or false: a program that compiles without warnings is guaranteed to produce the correct answer.",
                ["True", "False"],
                "False",
                "Logical errors can survive compilation and warnings; tests are still required.",
                "true_false",
            ),
            (
                "What does the -o option do?",
                ["Names the output executable", "Turns off all warnings", "Runs the program", "Selects the C standard"],
                "Names the output executable",
                "The argument after -o is the path or name of the produced file.",
                "multiple_choice",
            ),
        ],
    },
    {
        "title": "Common Programming Errors",
        "slug": "common-c-programming-errors",
        "intro": (
            "Beginners tend to make the same small set of mistakes repeatedly. The good news is that these mistakes are "
            "predictable, and most of them produce clear diagnostics once you know what to look for. This lesson groups "
            "errors by stage: syntax, compilation, linking, runtime, and logic, then gives you a repair checklist."
        ),
        "objectives": [
            "Classify an error as syntax, compile-time, linker, runtime, or logical.",
            "Recognise missing semicolons, unbalanced braces, wrong case, and bad format specifiers.",
            "Read the first compiler diagnostic and locate the likely cause.",
            "Repair small broken programs and explain each repair.",
        ],
        "prerequisites": "Lesson 08 and experience compiling the previous examples.",
        "theory": (
            "A syntax error violates the grammar of C. A missing semicolon, an unmatched parenthesis, or an unterminated "
            "string literal usually stops compilation. The reported line is not always the line you must edit: a "
            "missing semicolon at the end of one statement is often reported at the beginning of the next statement. "
            "Read the message, then look at the line before it as well.\n\n"
            "A name error occurs when the compiler sees an identifier it does not know. Common causes are a misspelled "
            "variable, a missing declaration, or wrong capitalisation. If you call printf without including <stdio.h>, "
            "a modern C compiler may warn about an implicit declaration or reject the call. The fix is the include, not "
            "a random cast or a new variable.\n\n"
            "A type or format error means a value is being used as the wrong kind of thing. Passing a double to %d, "
            "comparing incompatible pointer types, or assigning a string literal to a single char are examples. With "
            "-Wall -Wextra, the compiler usually points at the exact call. Fix the type or the format so they agree.\n\n"
            "A linker error happens after successful compilation. An undefined reference means a function or variable was "
            "declared and used but never defined, or the required library was not linked. A duplicate symbol means the "
            "same definition appears more than once. Read the symbol name carefully; it tells you what is missing.\n\n"
            "Runtime errors happen while the program runs. Division by zero for integers, reading outside an array, using "
            "an uninitialised value, or dereferencing an invalid pointer can crash the program or, worse, appear to work. "
            "These are not reliably caught by the compiler. A logical error is a program that runs and produces a wrong "
            "answer, such as using the wrong formula or the wrong boundary in a loop. Debugging and tests are the tools "
            "for runtime and logical errors.\n\n"
            "Use a repair checklist: compile the smallest version, read the first diagnostic, inspect the previous line, "
            "check spelling and case, count braces and parentheses, verify format specifiers, then rebuild. Change one "
            "thing at a time so you know which change fixed the problem."
        ),
        "diagram": (
            "Error stage checklist\n"
            "1. Syntax        missing ; { } ) or quote\n"
            "2. Compile       unknown name, wrong type, bad format\n"
            "3. Link          undefined reference, duplicate definition\n"
            "4. Runtime       crash, divide by zero, invalid memory access\n"
            "5. Logic         runs but produces the wrong answer\n\n"
            "Broken:  printf(\"Hi\\n\")\n"
            "Fixed:   printf(\"Hi\\n\");"
        ),
        "definitions": [
            "Syntax error: a violation of C grammar detected by the compiler.",
            "Compile-time error: a problem that prevents translation into an executable.",
            "Linker error: a problem resolving symbols after compilation.",
            "Runtime error: a failure that occurs while the program executes.",
            "Logical error: a program that runs but produces an incorrect result.",
            "Undefined behavior: an operation for which the C standard imposes no requirements on the result.",
        ],
        "syntax": (
            "/* Broken: missing semicolon */\n"
            "printf(\"Hello\\n\")\n\n"
            "/* Fixed */\n"
            "printf(\"Hello\\n\");\n\n"
            "/* Broken: wrong case */\n"
            "Int main(void) { return 0; }\n\n"
            "/* Fixed */\n"
            "int main(void) { return 0; }"
        ),
        "program_title": "a clean program after repairing common mistakes",
        "code": (
            '#include <stdio.h>\n\n'
            'int main(void) {\n'
            '    int total = 0;\n'
            '    int first = 4;\n'
            '    int second = 6;\n\n'
            '    total = first + second;\n'
            '    printf("Total: %d\\n", total);\n'
            '    return 0;\n'
            '}'
        ),
        "output": "Total: 10",
        "explanation": (
            "The include is present, so printf is declared. Every statement ends with a semicolon. Identifiers use "
            "consistent lowercase spelling. Both values are initialised before use. The %d conversion matches the int "
            "total. The program returns 0. There is no undefined behavior in this example, which makes it a safe "
            "baseline for experimenting with one error at a time."
        ),
        "mistakes": [
            "Changing many lines at once after a compiler error, which hides the real fix.",
            "Ignoring the first diagnostic and reading only the last one.",
            "Using a semicolon after a function header or after a closing brace.",
            "Confusing = assignment with == comparison (covered in later modules).",
            "Assuming an uninitialised local variable starts at zero.",
            "Using a format specifier that does not match the argument.",
        ],
        "exercises": [
            (
                "Fix the missing semicolon: printf(\"Ready\\n\") return 0;",
                '#include <stdio.h>\n\nint main(void) {\n    printf("Ready\\n");\n    return 0;\n}',
                "The semicolon after the printf call terminates the statement.",
            ),
            (
                "Fix the wrong case: Int Main(void) { Return 0; }",
                "int main(void) {\n    return 0;\n}",
                "C keywords are lowercase, so int and return must be written exactly that way.",
            ),
            (
                "Fix the format mismatch: printf(\"%d\\n\", 2.5);",
                '#include <stdio.h>\n\nint main(void) {\n    printf("%.1f\\n", 2.5);\n    return 0;\n}',
                "A double argument needs a floating-point conversion such as %.1f.",
            ),
            (
                "Fix the unbalanced braces in this fragment: int main(void) { printf(\"Hi\\n\");",
                '#include <stdio.h>\n\nint main(void) {\n    printf("Hi\\n");\n    return 0;\n}',
                "The function body needs a closing brace, and main should return an int status.",
            ),
            (
                "Fix the missing include that causes printf to be undeclared.",
                '#include <stdio.h>\n\nint main(void) {\n    printf("Declared!\\n");\n    return 0;\n}',
                "stdio.h supplies the declaration of printf, so the compiler can check the call.",
            ),
        ],
        "summary": (
            "Most beginner errors fall into a few groups. Read the first diagnostic, check the previous line, verify "
            "case and spelling, balance braces, match format specifiers, and change one thing at a time."
        ),
        "next": "Lesson 10 brings everything together in a practice set, a mini project, and a module assessment.",
        "mm": (
            "C အမှားများကို syntax error၊ compile-time error၊ linker error၊ runtime error နှင့် logical error ဟူ၍ "
            "ခွဲနိုင်သည်။ Semicolon မပါခြင်း၊ brace မညီခြင်း၊ စာလုံးအကြီးအသေး မှားခြင်းနှင့် format specifier "
            "မကိုက်ညီခြင်းတို့သည် အဖြစ်များသည်။ Compiler က ပြသည့် ပထမဆုံး diagnostic ကို ဖတ်ပြီး ယင်းလိုင်းနှင့် "
            "ရှေ့လိုင်းကို စစ်ပါ။ Linker error တွင် symbol definition မတွေ့ခြင်းကို ရှာပါ။ Runtime နှင့် logical "
            "error များအတွက် test နှင့် debugger လိုအပ်သည်။ တစ်ကြိမ်လျှင် ပြောင်းလဲမှုတစ်ခုသာ လုပ်ပါ။ "
            "C keyword များနှင့် code ကို မပြောင်းလဲပါ။"
        ),
        "questions": [
            (
                "What kind of error is a missing semicolon?",
                ["A syntax error detected at compile time", "A linker error", "A logical error", "A successful build"],
                "A syntax error detected at compile time",
                "A missing semicolon violates C grammar, so compilation fails.",
                "multiple_choice",
            ),
            (
                "Which program is most likely to be a logical error?",
                ["It compiles and runs but prints the wrong total", "It reports an undefined reference", "It has an unmatched brace", "It cannot find stdio.h"],
                "It compiles and runs but prints the wrong total",
                "A logical error survives translation and execution but produces an incorrect result.",
                "multiple_choice",
            ),
            (
                "Which repair fixes printf(\"%d\\n\", 2.5); ?",
                ['printf("%.1f\\n", 2.5);', 'printf("%d\\n", (int)2.5);', 'printf("%s\\n", 2.5);', "Remove the semicolon"],
                'printf("%.1f\\n", 2.5);',
                "The floating-point argument should use a floating-point conversion. Casting changes the value and may not be intended.",
                "multiple_choice",
            ),
            (
                "What does an undefined reference usually indicate?",
                ["A missing definition or library at link time", "A missing newline", "A comment that is too long", "A slow program"],
                "A missing definition or library at link time",
                "The linker reports a symbol that was referenced but not resolved.",
                "multiple_choice",
            ),
            (
                "True or false: reading only the last compiler diagnostic is the best debugging strategy.",
                ["True", "False"],
                "False",
                "The first diagnostic usually identifies the root cause; later messages can be side effects.",
                "true_false",
            ),
        ],
    },
    {
        "title": "Module 3 Practice & Assessment",
        "slug": "module-3-practice-and-assessment",
        "intro": (
            "This final lesson turns Module 3 into practice. You will repair small programs, predict output, and build "
            "the Personal Introduction Program, a complete mini project that uses printf, escape sequences, comments, "
            "and correct formatting. Finish the checklist before moving to Module 4."
        ),
        "objectives": [
            "Repair syntax, printf, and escape-sequence mistakes without guessing.",
            "Predict the output of short programs containing comments, escapes, and format specifiers.",
            "Build and explain the Personal Introduction Program.",
            "Complete a module assessment and a project completion checklist.",
        ],
        "prerequisites": "Lessons 01–09. You should be able to compile and run a C file with warnings enabled.",
        "theory": (
            "Practice should be deliberate. For each exercise, first predict what the program will do, then compile it, "
            "then compare the result with your prediction. When the result differs, identify the smallest line that "
            "explains the difference. This loop is more valuable than copying a correct answer.\n\n"
            "The mini project for this module is a Personal Introduction Program. It must print your name, age, country, "
            "and programming goal. Use printf for every line, use escape sequences such as \\n and \\t where they improve "
            "the layout, and keep the format specifiers compatible with the values. Store values in variables rather "
            "than hard-coding every value inside the format string: this makes the program easier to change and gives "
            "you practice with types. Add comments that explain the purpose of each section. The expected output below "
            "uses sample values; replace them with your own while keeping the format.\n\n"
            "A complete solution is not just source code. It includes a short description of the requirements, a "
            "prediction of the output, a successful strict build, and a checklist that confirms each requirement was "
            "met. If a requirement is missing, fix it before declaring the project finished.\n\n"
            "The assessment questions mix multiple choice, true/false, code output, and error identification. Read every "
            "option before answering. For a code-output question, track the output character by character, especially "
            "newlines and tabs. For an error-identification question, name the stage at which the error appears.\n\n"
            "At the end of this module you should be able to write, compile, run, and explain a small C program from "
            "scratch. That is the foundation for variables, input, operators, and control flow in the modules that "
            "follow."
        ),
        "diagram": (
            "Module 3 completion path\n"
            "read theory -> predict output -> type program -> compile with warnings\n"
            "      -> run -> compare -> repair -> explain -> mark complete\n\n"
            "Mini project output plan\n"
            "Name:      Ada\n"
            "Age:       20\n"
            "Country:   Myanmar\n"
            "Goal:      Learn C and build reliable software"
        ),
        "definitions": [
            "Mini project: a small complete program that combines the skills from a module.",
            "Acceptance checklist: a list of observable requirements used to decide whether a project is finished.",
            "Regression: a previously working behaviour that breaks after a change.",
            "Assessment: a set of questions and tasks that checks understanding rather than copying.",
        ],
        "syntax": (
            "printf(\"Name:\\t%s\\n\", name);\n"
            "printf(\"Age:\\t%d\\n\", age);\n"
            "printf(\"Country:\\t%s\\n\", country);\n"
            "printf(\"Goal:\\t%s\\n\", goal);"
        ),
        "program_title": "Personal Introduction Program (mini project)",
        "code": (
            '#include <stdio.h>\n\n'
            'int main(void) {\n'
            '    /* Store the personal details in variables with suitable types. */\n'
            '    const char *name = "Ada";\n'
            '    int age = 20;\n'
            '    const char *country = "Myanmar";\n'
            '    const char *goal = "Learn C and build reliable software";\n\n'
            '    printf("=== Personal Introduction ===\\n");\n'
            '    printf("Name:\\t%s\\n", name);\n'
            '    printf("Age:\\t%d\\n", age);\n'
            '    printf("Country:\\t%s\\n", country);\n'
            '    printf("Goal:\\t%s\\n", goal);\n'
            '    printf("=============================\\n");\n'
            '    return 0;\n'
            '}'
        ),
        "output": (
            "=== Personal Introduction ===\n"
            "Name:\tAda\n"
            "Age:\t20\n"
            "Country:\tMyanmar\n"
            "Goal:\tLearn C and build reliable software\n"
            "============================="
        ),
        "explanation": (
            "The include supplies printf. The four variables hold the values used in the output. const char * is used "
            "for text that will not be modified. The heading and closing rule use ordinary text and newlines. Each "
            "detail line uses a label, a tab, the appropriate format specifier, and a newline. %s matches the strings "
            "and %d matches the int age. The program ends with return 0, so the shell receives a success status."
        ),
        "extra_examples": [
            {
                "title": "Required output check with your own details",
                "code": (
                    '#include <stdio.h>\n\n'
                    'int main(void) {\n'
                    '    const char *name = "Your Name";\n'
                    '    int age = 18;\n'
                    '    const char *country = "Your Country";\n'
                    '    const char *goal = "Become a confident C programmer";\n\n'
                    '    printf("Name:\\t%s\\n", name);\n'
                    '    printf("Age:\\t%d\\n", age);\n'
                    '    printf("Country:\\t%s\\n", country);\n'
                    '    printf("Goal:\\t%s\\n", goal);\n'
                    '    return 0;\n'
                    '}'
                ),
                "output": (
                    "Name:\tYour Name\n"
                    "Age:\t18\n"
                    "Country:\tYour Country\n"
                    "Goal:\tBecome a confident C programmer"
                ),
                "explanation": (
                    "Replace each sample value with your own but keep the types and format specifiers. This version "
                    "is the minimum acceptable project output; the main example adds a heading and a closing rule."
                ),
            }
        ],
        "mistakes": [
            "Using %d for the name or %s for the age.",
            "Forgetting to include <stdio.h>.",
            "Hard-coding every value inside one long format string, which makes the program difficult to change and hides type practice.",
            "Leaving missing semicolons after the printf calls.",
            "Declaring a goal string but misspelling its identifier in printf.",
            "Declaring the project finished without compiling it with warnings enabled.",
        ],
        "exercises": [
            (
                "Hello World practice: write a program that prints exactly one line: Hello, World!",
                '#include <stdio.h>\n\nint main(void) {\n    printf("Hello, World!\\n");\n    return 0;\n}',
                "The string ends with \\n, so the line is complete, and return 0 reports success.",
            ),
            (
                "Multiple lines practice: print your name, country, and goal on three separate lines.",
                '#include <stdio.h>\n\nint main(void) {\n    printf("Ada\\n");\n    printf("Myanmar\\n");\n    printf("Learn C\\n");\n    return 0;\n}',
                "Each printf call ends with a newline, so each value occupies its own line.",
            ),
            (
                "Comment practice: add one comment that explains the purpose of the program without repeating the printf text.",
                '/* Personal introduction: demonstrate printf, variables, and escapes. */',
                "The comment explains intent and remains useful even if the exact printed text changes.",
            ),
            (
                "Missing semicolon practice: repair printf(\"Hello\\n\") return 0;",
                '#include <stdio.h>\n\nint main(void) {\n    printf("Hello\\n");\n    return 0;\n}',
                "The semicolon terminates the printf statement before the return statement begins.",
            ),
            (
                "printf error practice: repair printf(\"%d\\n\", \"Ada\");",
                '#include <stdio.h>\n\nint main(void) {\n    printf("%s\\n", "Ada");\n    return 0;\n}',
                "A string argument requires %s; %d expects an int.",
            ),
            (
                "Escape-sequence practice: print a quoted title and a tab-separated pair of values.",
                '#include <stdio.h>\n\nint main(void) {\n    printf("\\\"Practice\\\"\\tComplete\\n");\n    return 0;\n}',
                "The escaped quotes are printed as characters, the tab separates the columns, and the newline ends the line.",
            ),
            (
                "Format-specifier practice: print name, age, and score with %s, %d, and %.1f.",
                '#include <stdio.h>\n\nint main(void) {\n    printf("%s\\t%d\\t%.1f\\n", "Ada", 20, 95.5);\n    return 0;\n}',
                "Each conversion matches the type of the corresponding argument in order.",
            ),
            (
                "Output prediction: what does printf(\"A\\tB\\nC\\n\"); display, and how many lines are visible?",
                '#include <stdio.h>\n\nint main(void) {\n    printf("A\\tB\\nC\\n");\n    return 0;\n}',
                "The output has two visible lines: A and B separated by a tab on the first line, then C on the second.",
            ),
            (
                "Error identification: classify the problem in printf(\"%d\\n\", 3.5);",
                'printf("%.1f\\n", 3.5);',
                "This is a compile-time format/type mismatch: %d expects an int but the argument is a double.",
            ),
        ],
        "summary": (
            "You completed the first full C module. You can read program structure, follow syntax rules, comment code, "
            "use printf and escape sequences, choose format specifiers, compile with strict warnings, diagnose common "
            "errors, and build a small personal introduction project."
        ),
        "next": "Module 04 begins with variables and data types, building on the programs you can now write and explain.",
        "mm": (
            "ဤသင်ခန်းစာသည် Module 3 ၏ လက်တွေ့အလုပ်ဖြစ်သည်။ Exercise တစ်ခုစီအတွက် output ကို အရင်ခန့်မှန်းပြီး "
            "compile လုပ်ကာ ရလဒ်နှင့် နှိုင်းယှဉ်ပါ။ ကွာခြားချက်ရှိပါက အသေးဆုံးလိုင်းကို ရှာပါ။ Mini project ဖြစ်သော "
            "Personal Introduction Program တွင် name၊ age၊ country နှင့် programming goal ကို `printf` ဖြင့် "
            "ပြရမည်။ `%s` ကို string အတွက်၊ `%d` ကို age အတွက် အသုံးပြုပြီး `\\n` နှင့် `\\t` ဖြင့် ဖတ်ရလွယ်အောင် "
            "စီစဉ်ပါ။ Variable များတွင် တန်ဖိုးများ သိမ်းထားခြင်းက ပြောင်းလဲရလွယ်စေသည်။ ပြီးဆုံးကြောင်း မကြေညာမီ "
            "warning များဖြင့် compile လုပ်ပြီး checklist ကို စစ်ပါ။ C keyword များနှင့် code ကို "
            "မပြောင်းလဲပါ။"
        ),
        "questions": [
            (
                "Which program correctly prints a line containing a tab between Name and Ada?",
                ['printf("Name:\\tAda\\n");', 'printf("Name:\\nAda\\n");', 'printf("Name: Ada");', 'printf("Name: \\q Ada\\n");'],
                'printf("Name:\\tAda\\n");',
                "\\t inserts a tab, and \\n ends the line.",
                "multiple_choice",
            ),
            (
                "What is the output of printf(\"%s is %d\\n\", \"Mya\", 20); ?",
                ["Mya is 20", "Mya is %d", "%s is 20", "Mya20"],
                "Mya is 20",
                "%s is replaced by Mya and %d by 20, in argument order.",
                "code_output",
            ),
            (
                "Which repair makes printf(\"%d\\n\", 4.5); type-compatible?",
                ['printf("%.1f\\n", 4.5);', 'printf("%d\\n", (int)4.5);', 'printf("%c\\n", 4.5);', "Remove the semicolon"],
                'printf("%.1f\\n", 4.5);',
                "The argument is a double, so a floating-point conversion avoids the mismatch.",
                "multiple_choice",
            ),
            (
                "How many visible lines does printf(\"A\\nB\\nC\\n\"); produce?",
                ["Three", "One", "Two", "Zero"],
                "Three",
                "Each newline ends one visible line, giving three lines.",
                "code_output",
            ),
            (
                "True or false: a mini project is complete as soon as the source file exists.",
                ["True", "False"],
                "False",
                "It must compile, run, meet the requirements, and pass the completion checklist.",
                "true_false",
            ),
            (
                "Which header is required when a program uses printf?",
                ["<stdio.h>", "<stdlib.h>", "<string.h>", "<ctype.h>"],
                "<stdio.h>",
                "printf is declared in the standard input/output header.",
                "multiple_choice",
            ),
        ],
    },
]

MODULE_THREE_SECTION_HEADINGS = [
    "Introduction",
    "Learning objectives",
    "Prerequisites",
    "Detailed theory",
    "Visual explanation",
    "Key definitions",
    "Syntax example",
    "Complete C program",
    "Expected output",
    "Line-by-line explanation",
    "Additional complete example",
    "Common mistakes",
    "Practice exercises",
    "Summary",
    "Next lesson",
]


def _question_type(options, explicit_type, prompt):
    if explicit_type:
        return explicit_type
    if options == ["True", "False"]:
        return "true_false"
    if "output" in prompt.lower():
        return "code_output"
    return "multiple_choice"


def seed_module_three(db, module):
    """Create or refresh Module 3 without deleting lesson IDs or student progress."""
    from .models import CodeExample, Lesson, LessonQuiz, QuizQuestion

    module.title = f"03 {MODULE_TITLE}"
    for position, item in enumerate(MODULE_THREE_LESSONS, 1):
        slug = f"03-{item['slug']}"
        lesson = db.scalar(
            select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == position)
        )
        if not lesson:
            lesson = Lesson(
                module_id=module.id,
                title=item["title"],
                slug=slug,
                description=item["intro"][:240],
                content_en="",
                order_index=position,
                duration_minutes=35,
                status="published",
                published=True,
            )
            db.add(lesson)
            db.flush()
        lesson.title = item["title"]
        lesson.slug = slug
        lesson.description = item["intro"][:240]
        lesson.content_en = build_content(item)
        lesson.content_mm = item["mm"]
        lesson.order_index = position
        lesson.duration_minutes = 35
        lesson.status = "published"
        lesson.published = True

        examples = [item] + item.get("extra_examples", [])
        existing_examples = {
            row.position: row
            for row in db.scalars(
                select(CodeExample).where(CodeExample.lesson_id == lesson.id)
            ).all()
        }
        for example_position, example_source in enumerate(examples, 1):
            if example_position == 1:
                title = f"{item['title']} — complete example"
                code = item["code"]
                output = item["output"]
                explanation = item["explanation"]
            else:
                title = f"{item['title']} — {example_source['title']}"
                code = example_source["code"]
                output = example_source["output"]
                explanation = example_source["explanation"]
            example = existing_examples.get(example_position)
            if not example:
                example = CodeExample(lesson_id=lesson.id, position=example_position)
                db.add(example)
            example.title = title
            example.language = "c"
            example.filename = "introduction.c" if position == 10 else "main.c"
            example.code = code.rstrip("\n") + "\n"
            example.description = (
                f"Expected output:\n{output}\n\n"
                f"Line-by-line explanation:\n{explanation}"
            )
        for stale_position, stale in existing_examples.items():
            if stale_position > len(examples):
                db.delete(stale)

        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(
                lesson_id=lesson.id,
                title=f"Module 3 review: {item['title']}",
                explanation="Review the theory and re-run the examples before retrying the quiz.",
                status="published",
            )
            db.add(quiz)
            db.flush()
        quiz.title = f"Module 3 review: {item['title']}"
        quiz.explanation = (
            "Read each answer explanation, revisit the relevant section, and compile the example again "
            "before retrying."
        )
        quiz.status = "published"

        existing_questions = {
            row.position: row
            for row in db.scalars(
                select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id)
            ).all()
        }
        for question_position, question_data in enumerate(item["questions"], 1):
            prompt, options, answer, explanation, explicit_type = question_data
            question = existing_questions.get(question_position)
            if not question:
                question = QuizQuestion(quiz_id=quiz.id, position=question_position)
                db.add(question)
            question.prompt = prompt
            question.options_json = json.dumps(options)
            question.correct_answer = answer
            question.explanation = explanation
            question.question_type = _question_type(options, explicit_type, prompt)
            question.position = question_position
        for stale_position, stale in existing_questions.items():
            if stale_position > len(item["questions"]):
                db.delete(stale)
