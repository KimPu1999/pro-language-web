"""Idempotent, authored C++20 curriculum for the public C++ course.

The seed deliberately uses the existing course tables.  It updates only rows
owned by ``cpp-programming`` and never touches C-course lessons or progress.
"""
import json
import re
from sqlalchemy import select

from .models import CourseModule, Lesson, LessonQuiz, QuizQuestion, CodeExample


MODULES = [
    "Introduction to C++ Programming", "C++ Environment Setup", "First C++ Program",
    "Variables & Data Types", "Input & Output", "Operators & Expressions",
    "Conditional Statements", "Loops & Iteration", "Functions",
    "Arrays, Strings & Vectors", "References & Pointers", "Scope, Lifetime & Memory",
    "Structures & Enumerations", "Object-Oriented Programming", "Constructors & Destructors",
    "Inheritance & Polymorphism", "Operator Overloading", "Templates & Generic Programming",
    "Standard Template Library", "Files & Error Handling", "Modern C++ Features",
    "Debugging, Testing & Build Tools", "Guided Mini Projects", "Final Capstone & Assessment",
]

LESSONS = [
    (1, "What C++ Is and How Programs Run", "program structure", '#include <iostream>\n\nint main() {\n    std::cout << "C++ is ready\\n";\n}', "C++ source is translated, linked, and then executed. The standard library provides reusable facilities, while main is the program entry point.", "C++ source -> compiler -> executable -> runtime output.", "C++ program ၏ source code ကို compiler က executable အဖြစ် ပြောင်းပြီး runtime တွင် run သည်။"),
    (1, "Names, Statements, and Comments", "tokens and comments", '#include <iostream>\n\nint main() {\n    int lessons = 2; // a named value\n    std::cout << "Lessons: " << lessons << "\\n";\n}', "A statement is an instruction ending in a semicolon. Identifiers name values and functions; comments explain intent to humans and are ignored by the compiler.", "identifier; statement; comment; block.", "Statement တစ်ခုသည် များသောအားဖြင့် semicolon ဖြင့်ဆုံးသည်။ Comment များသည် code ဖတ်သူအတွက်သာ ဖြစ်သည်။"),
    (2, "Installing a C++20 Toolchain", "compiler setup", '#include <iostream>\nint main() { std::cout << "Toolchain check\\n"; }', "Use GCC 11+, Clang 13+, or MSVC with C++20 support. Confirm with a version command, then compile using -std=c++20 -Wall -Wextra -Wpedantic.", "c++ -std=c++20 -Wall -Wextra -Wpedantic main.cpp -o main", "Compiler setup အပြီးတွင် version ကို စစ်ပြီး C++20 flags ဖြင့် compile လုပ်ပါ။"),
    (2, "Build, Run, and Diagnose", "build commands", '#include <iostream>\nint main() { std::cout << "Build succeeded\\n"; }', "A build command turns source into an executable. Read the first diagnostic, fix one cause at a time, and keep warnings enabled.", "compile -> link -> execute; stderr contains diagnostics.", "Build error ဖြစ်လျှင် ပထမဆုံး diagnostic ကိုဖတ်ပြီး တစ်ကြိမ်တွင် အမှားတစ်ခုစီကို ပြင်ပါ။"),
    (3, "Your First C++20 Program", "main and output", '#include <iostream>\n\nint main() {\n    std::cout << "Hello, learner!\\n";\n    return 0;\n}', "Every hosted C++ program starts execution in main. iostream declares the stream objects used for console output.", "int main() { statements }", "main သည် program ၏ entry point ဖြစ်ပြီး std::cout သည် console output အတွက် အသုံးပြုသည်။"),
    (3, "Formatting Console Output", "stream insertion", '#include <iostream>\n#include <iomanip>\n\nint main() {\n    std::cout << std::fixed << std::setprecision(2) << 12.5 << "\\n";\n}', "The insertion operator sends values to a stream. Manipulators such as fixed and setprecision control presentation without changing the stored value.", "std::cout << value; std::fixed << std::setprecision(2)", "std::cout နှင့် manipulators များသည် output ပုံစံကို ထိန်းချုပ်သည်။"),
    (4, "Variables and Initialization", "declarations", '#include <iostream>\n\nint main() {\n    const int weeks = 4;\n    int lessons = weeks * 3;\n    std::cout << lessons << "\\n";\n}', "A variable has a type, name, and lifetime. Prefer initialization at declaration and const when a value should not change.", "type name{initial_value}; const type name{value};", "Variable ကို declaration နေရာမှာ initialize လုပ်ပြီး မပြောင်းရမည့် value ကို const သုံးပါ။"),
    (4, "Numeric, Character, and Boolean Types", "types", '#include <iostream>\n\nint main() {\n    int count{7}; double price{2.5}; char grade{65}; bool ready{true};\n    std::cout << count << " " << price << " " << grade << " " << std::boolalpha << ready << "\\n";\n}', "int stores whole numbers, double stores fractional values, char stores a character, and bool represents true or false. Choose a type that expresses intent.", "int; double; char; bool; std::string", "Type တစ်ခုစီသည် သိမ်းဆည်းမည့် data ၏ အဓိပ္ပါယ်ကို ဖော်ပြသည်။"),
    (5, "Reading Input Safely", "std::cin", '#include <iostream>\n#include <string>\n\nint main() {\n    std::string name;\n    std::cin >> name;\n    std::cout << "Hello, " << name << "\\n";\n}', "std::cin extracts formatted input and reports failure through its stream state. Validate input before using it in important work.", "std::cin >> value; if (!std::cin) { /* handle error */ }", "std::cin ဖြင့် input ဖတ်ပြီး stream state ကို စစ်ဆေးသင့်သည်။"),
    (5, "Whole Lines with getline", "std::getline", '#include <iostream>\n#include <string>\n\nint main() {\n    std::string line;\n    std::getline(std::cin, line);\n    std::cout << "You typed: " << line << "\\n";\n}', "operator>> stops at whitespace; getline reads the rest of a line. Mixing them requires consuming the pending newline first.", "std::getline(std::cin, text);", "Space ပါသော စာကြောင်းကို ဖတ်ရန် std::getline ကို အသုံးပြုပါ။"),
    (6, "Arithmetic and Assignment", "operators", '#include <iostream>\n\nint main() {\n    int total{17};\n    total += 5;\n    std::cout << total / 2 << " " << total % 2 << "\\n";\n}', "Arithmetic operators have precedence and integer division discards a fractional part. Use parentheses when they make intent clearer.", "+ - * / %; += -= *= /=", "Integer division သည် fractional part ကို ဖြုတ်သည်။ ရှင်းလင်းရန် parentheses သုံးပါ။"),
    (6, "Comparisons and Logical Expressions", "boolean expressions", '#include <iostream>\n\nint main() {\n    int score{82};\n    bool passed = score >= 50 && score <= 100;\n    std::cout << std::boolalpha << passed << "\\n";\n}', "Comparisons produce bool values. &&, ||, and ! combine conditions; short-circuit evaluation can avoid unnecessary work.", "a == b; a != b; a < b; condition && condition", "Comparison များသည် bool ထုတ်ပေးပြီး logical operators ဖြင့် ပေါင်းစပ်နိုင်သည်။"),
    (7, "if, else if, and else", "branching", '#include <iostream>\n\nint main() {\n    int score{82};\n    if (score >= 80) std::cout << "Excellent\\n";\n    else if (score >= 50) std::cout << "Pass\\n";\n    else std::cout << "Try again\\n";\n}', "Conditional statements select a path at runtime. Put braces around multi-line branches and order mutually exclusive ranges carefully.", "if (condition) { ... } else { ... }", "if/else သည် condition အပေါ်မူတည်၍ code path ရွေးသည်။"),
    (7, "switch and Enumerated Choices", "switch", '#include <iostream>\n\nint main() {\n    int option{2};\n    switch (option) {\n        case 1: std::cout << "Start\\n"; break;\n        case 2: std::cout << "Pause\\n"; break;\n        default: std::cout << "Unknown\\n";\n    }\n}', "switch is useful for discrete choices. break prevents accidental fall-through; default documents unexpected values.", "switch (value) { case constant: statement; break; default: statement; }", "ရွေးချယ်စရာတန်ဖိုးများအတွက် switch ကို သုံးပြီး break မမေ့ပါနှင့်။"),
    (8, "for Loops", "for iteration", '#include <iostream>\n\nint main() {\n    for (int number{1}; number <= 3; ++number) {\n        std::cout << number << "\\n";\n    }\n}', "A for loop groups initialization, continuation, and update. Choose inclusive or exclusive bounds deliberately.", "for (init; condition; update) { body }", "for loop တွင် initialization၊ condition နှင့် update သုံးပိုင်းပါသည်။"),
    (8, "while and Range-Based for", "loop choices", '#include <iostream>\n#include <array>\n\nint main() {\n    std::array<int, 3> values{2, 4, 6};\n    for (int value : values) std::cout << value << " ";\n    std::cout << "\\n";\n}', "while suits a condition-controlled loop; range-based for suits each element in a range. Prefer clear loop invariants over clever control flow.", "while (condition) { ... }; for (const auto& item : range) { ... }", "Range-based for သည် container ထဲက element တစ်ခုချင်းကို ရှင်းလင်းစွာ iterate လုပ်သည်။"),
    (9, "Defining and Calling Functions", "functions", '#include <iostream>\n\nint square(int value) { return value * value; }\n\nint main() { std::cout << square(5) << "\\n"; }', "Functions give a name to a reusable operation. Keep each function focused and make inputs and outputs explicit.", "return_type name(parameters) { statements }", "Function သည် ပြန်သုံးနိုင်သော operation ကို အမည်ပေးသည်။"),
    (9, "Parameters, const, and Return Values", "function interfaces", '#include <iostream>\n#include <string>\n\nvoid greet(const std::string& name) { std::cout << "Hi " << name << "\\n"; }\nint main() { greet("Mya"); }', "Pass small values by value and larger read-only objects by const reference. A function interface should state what it needs and returns.", "void f(const Type& value);", "ပြောင်းလဲရန်မလိုသော object များကို const reference ဖြင့် လက်ခံနိုင်သည်။"),
    (10, "std::array and Indexing", "fixed-size sequences", '#include <array>\n#include <iostream>\n\nint main() {\n    std::array<int, 3> marks{70, 85, 90};\n    std::cout << marks.at(1) << "\\n";\n}', "std::array has a fixed size known at compile time. at checks bounds and operator[] is useful when bounds are already proven.", "std::array<Type, N> values{...}; values.at(index)", "အရွယ်အစားမပြောင်းသော sequence အတွက် std::array ကို သုံးပါ။"),
    (10, "std::string and std::vector", "dynamic collections", '#include <iostream>\n#include <string>\n#include <vector>\n\nint main() {\n    std::vector<std::string> names{"Ada", "Lin"};\n    names.push_back("Mya");\n    std::cout << names.size() << " " << names.front() << "\\n";\n}', "std::string manages text and std::vector manages a resizable contiguous sequence. Their member functions express intent and manage memory safely.", "std::vector<Type> values; values.push_back(value);", "std::vector သည် size ပြောင်းနိုင်သော sequence ကို အလိုအလျောက် manage လုပ်သည်။"),
    (11, "References for Aliases", "references", '#include <iostream>\n\nvoid add_one(int& value) { ++value; }\nint main() { int count{4}; add_one(count); std::cout << count << "\\n"; }', "A reference is an alias to an existing object and cannot be reseated. Use const references for read-only access and non-const references only when mutation is intentional.", "Type& name = object; const Type& read_only = object;", "Reference သည် ရှိပြီးသား object ကို alias လုပ်သည်။ မလိုအပ်ဘဲ mutation မလုပ်ပါနှင့်။"),
    (11, "Pointers and nullptr", "pointers", '#include <iostream>\n\nint main() {\n    int value{9};\n    int* pointer{&value};\n    if (pointer != nullptr) std::cout << *pointer << "\\n";\n}', "A pointer stores an address and may be null. Dereference only a valid, live object; prefer references, containers, and smart pointers when ownership is involved.", "Type* pointer{nullptr}; pointer = &object; *pointer", "Pointer ကို dereference မလုပ်မီ nullptr နှင့် lifetime ကို စစ်ပါ။"),
    (12, "Scope and Lifetime", "scope", '#include <iostream>\n\nint main() {\n    int outside{1};\n    { int inside{2}; std::cout << outside + inside << "\\n"; }\n    std::cout << outside << "\\n";\n}', "Scope describes where a name is visible; lifetime describes how long an object exists. Local objects normally end at the closing brace.", "{ local scope } and automatic lifetime", "Scope သည် name မြင်နိုင်ရာနေရာ၊ lifetime သည် object ရှိနေချိန် ဖြစ်သည်။"),
    (12, "RAII and Smart Ownership", "RAII", '#include <iostream>\n#include <memory>\n\nint main() {\n    auto value = std::make_unique<int>(42);\n    std::cout << *value << "\\n";\n}', "RAII ties resource ownership to object lifetime. std::unique_ptr expresses single ownership and releases its resource automatically.", "auto owner = std::make_unique<Type>(args);", "RAII သည် resource lifetime ကို object lifetime နှင့် ချိတ်ပြီး cleanup ကို အလိုအလျောက်လုပ်သည်။"),
    (13, "struct for Related Data", "structures", '#include <iostream>\n#include <string>\n\nstruct Student { std::string name; int score; };\nint main() { Student student{"Mya", 88}; std::cout << student.name << " " << student.score << "\\n"; }', "A struct groups related fields under one meaningful type. Give fields sensible names and initialize the whole object.", "struct Name { Type field; }; Name value{...};", "struct သည် ဆက်စပ်သော data များကို type တစ်ခုအဖြစ် စုစည်းသည်။"),
    (13, "enum class for Named States", "enumerations", '#include <iostream>\n\nenum class Status { draft, published };\nint main() { Status status{Status::published}; if (status == Status::published) std::cout << "Live\\n"; }', "enum class provides scoped named values and avoids accidental implicit conversion to integers.", "enum class Name { first, second }; Name::first", "enum class သည် named states များကို type-safe ဖြစ်စေသည်။"),
    (14, "Classes and Encapsulation", "classes", '#include <iostream>\n\nclass Counter { int value{0}; public: void increment() { ++value; } int get() const { return value; } };\nint main() { Counter counter; counter.increment(); std::cout << counter.get() << "\\n"; }', "A class bundles state and behavior. private data protects invariants; public member functions form the safe interface.", "class Name { private: fields; public: methods; };", "class သည် state နှင့် behavior ကို encapsulate လုပ်ပြီး public interface ဖြင့် အသုံးပြုစေသည်။"),
    (14, "Member Functions and const", "object behavior", '#include <iostream>\n\nclass Rectangle { public: Rectangle(int width, int height): width_{width}, height_{height} {} int area() const { return width_ * height_; } private: int width_; int height_; };\nint main() { const Rectangle box{3, 4}; std::cout << box.area() << "\\n"; }', "A const member function promises not to modify the object, allowing it to be called on const instances.", "ReturnType method() const { ... }", "const member function သည် object state မပြောင်းကြောင်း promise ပေးသည်။"),
    (15, "Constructors Establish Invariants", "constructors", '#include <iostream>\n\nclass Timer { public: explicit Timer(int seconds): seconds_{seconds} {} int seconds() const { return seconds_; } private: int seconds_; };\nint main() { Timer timer{30}; std::cout << timer.seconds() << "\\n"; }', "A constructor runs when an object is created. Use member initializer lists and validate inputs so a newly created object is usable.", "Class(Type value) : member{value} {}", "Constructor သည် object ဖန်တီးချိန်တွင် run ပြီး valid initial state တည်ဆောက်သည်။"),
    (15, "Destructors and Resource Cleanup", "destructors", '#include <iostream>\n\nclass Notice { public: ~Notice() { std::cout << "cleanup\\n"; } };\nint main() { { Notice notice; std::cout << "work\\n"; } }', "A destructor runs when an object lifetime ends. Prefer standard RAII types so custom destructors are rarely needed for ordinary memory.", "~ClassName() { release owned resources; }", "Destructor သည် lifetime အဆုံးတွင် cleanup လုပ်သည်။ Standard RAII type များကို ဦးစားပေးပါ။"),
    (16, "Inheritance and Base Interfaces", "inheritance", '#include <iostream>\n\nstruct Animal { void breathe() const { std::cout << "breathing\\n"; } };\nstruct Cat : Animal { void meow() const { std::cout << "meow\\n"; } };\nint main() { Cat cat; cat.breathe(); cat.meow(); }', "Inheritance models an is-a relationship and reuses a base interface. Favor composition unless substitutability is clear.", "struct Derived : Base { ... };", "Inheritance သည် is-a relationship ကို model လုပ်ရန် အသုံးပြုသည်။"),
    (16, "Virtual Functions and Polymorphism", "polymorphism", '#include <iostream>\n\nstruct Shape { virtual int sides() const { return 0; } virtual ~Shape() = default; };\nstruct Triangle : Shape { int sides() const override { return 3; } };\nint main() { Triangle triangle; Shape& shape{triangle}; std::cout << shape.sides() << "\\n"; }', "A virtual function enables dynamic dispatch through a base interface. Use override so the compiler checks your intention and virtual destructors for polymorphic ownership.", "virtual ReturnType method() const; override", "virtual function သည် base interface မှ dynamic dispatch ပေးသည်။"),
    (17, "Operators as Readable Interfaces", "operator overloading", '#include <iostream>\n\nstruct Point { int x; int y; };\nPoint operator+(const Point& left, const Point& right) { return {left.x + right.x, left.y + right.y}; }\nint main() { Point result = Point{1, 2} + Point{3, 4}; std::cout << result.x << " " << result.y << "\\n"; }', "Operator overloading should preserve familiar meaning. Keep it small, unsurprising, and consistent with the type's value semantics.", "ReturnType operator+(const Type& a, const Type& b)", "Operator overload သည် သဘာဝကျပြီး မရှုပ်ထွေးသော meaning ရှိရမည်။"),
    (17, "Comparisons and Stream Output", "custom operators", '#include <iostream>\n\nstruct Score { int value; };\nbool operator==(Score a, Score b) { return a.value == b.value; }\nstd::ostream& operator<<(std::ostream& out, Score score) { return out << score.value; }\nint main() { std::cout << (Score{8} == Score{8}) << " " << Score{8} << "\\n"; }', "Value types benefit from predictable equality and output operations. Return the stream by reference so chaining remains possible.", "std::ostream& operator<<(std::ostream&, const Type&)", "Value type များအတွက် equality နှင့် stream output ကို predictable ဖြစ်အောင်ရေးပါ။"),
    (18, "Function Templates", "templates", '#include <iostream>\n\ntemplate <typename T> T maximum(T left, T right) { return left > right ? left : right; }\nint main() { std::cout << maximum(4, 9) << "\\n"; }', "A function template describes an algorithm for a family of types. The compiler creates a type-specific version when it is used.", "template <typename T> Return name(T value)", "Template သည် type များစွာအတွက် algorithm တစ်ခုကို ရေးနိုင်စေသည်။"),
    (18, "Generic Constraints and Good Interfaces", "generic programming", '#include <iostream>\n#include <string>\n\ntemplate <typename T> void show(const T& value) { std::cout << value << "\\n"; }\nint main() { show(42); show(std::string{"ready"}); }', "Generic code should state its assumptions through a simple interface and should work for types that support the operations it uses.", "template <typename T> void show(const T& value)", "Generic code သည် အသုံးပြုမည့် operation များကို ရှင်းလင်းစွာထားရမည်။"),
    (19, "Algorithms and Iterators", "standard algorithms", '#include <algorithm>\n#include <array>\n#include <iostream>\n\nint main() { std::array<int, 4> values{4, 1, 3, 2}; std::sort(values.begin(), values.end()); for (int value : values) std::cout << value << " "; }', "The standard library provides tested algorithms. Iterators describe positions in a range; containers own the data.", "std::sort(begin, end); std::find(begin, end, value)", "Standard algorithm များသည် tested ဖြစ်ပြီး container data ကို ပြန်သုံးနိုင်သည်။"),
    (19, "Maps, Sets, and Choosing Containers", "containers", '#include <iostream>\n#include <map>\n#include <string>\n\nint main() { std::map<std::string, int> scores{{"Mya", 90}}; std::cout << scores.at("Mya") << "\\n"; }', "Choose vector for ordered sequences, map for key/value lookup, and set for unique ordered values. Let access patterns guide the choice.", "std::map<Key, Value>; map.at(key);", "Container ရွေးချယ်ရာတွင် data access pattern ကို အခြေခံပါ။"),
    (20, "Writing and Reading Text Files", "fstream", '#include <fstream>\n#include <iostream>\n\nint main() { std::ofstream file{"note.txt"}; file << "C++20\\n"; file.close(); std::cout << "saved\\n"; }', "File streams report failure through their state. Check the stream, write a clear format, and close through RAII when possible.", "std::ofstream out{path}; std::ifstream in{path};", "File stream ဖွင့်ပြီး success state ကို စစ်ဆေးပါ။"),
    (20, "Exceptions and Error Boundaries", "exceptions", '#include <iostream>\n#include <stdexcept>\n\nint divide(int a, int b) { if (b == 0) throw std::invalid_argument{"zero divisor"}; return a / b; }\nint main() { try { std::cout << divide(8, 2) << "\\n"; } catch (const std::exception& error) { std::cout << error.what() << "\\n"; } }', "Exceptions communicate failure across a call boundary. Catch specific failures at a layer that can recover or report them meaningfully.", "throw ExceptionType{message}; catch (const std::exception& e)", "Recover လုပ်နိုင်သော boundary တွင် exception ကို catch လုပ်ပြီး အဓိပ္ပါယ်ရှိစွာ report လုပ်ပါ။"),
    (21, "auto, constexpr, and Structured Bindings", "modern syntax", '#include <iostream>\n#include <utility>\n\nconstexpr int twice(int value) { return value * 2; }\nint main() { auto [left, right] = std::pair{2, 3}; std::cout << twice(left + right) << "\\n"; }', "C++20 lets the compiler infer obvious types with auto, evaluate pure expressions with constexpr, and unpack tuple-like values with structured bindings.", "auto name = expression; constexpr function; auto [a, b] = pair", "C++20 တွင် auto၊ constexpr နှင့် structured binding များက code ကို ရှင်းလင်းစေသည်။"),
    (21, "Ranges, Concepts, and Safer Modern Code", "C++20 features", '#include <concepts>\n#include <iostream>\n\ntemplate <std::integral T> T increment(T value) { return value + 1; }\nint main() { std::cout << increment(4) << "\\n"; }', "Concepts document template requirements at the interface and produce clearer diagnostics. Adopt new features when they improve correctness and readability.", "template <std::integral T> T function(T value)", "Concepts သည် template requirement များကို interface မှာ ဖော်ပြသည်။"),
    (22, "Warnings, Debuggers, and Assertions", "debugging", '#include <cassert>\n#include <iostream>\n\nint main() { int total{3}; assert(total > 0); std::cout << "checked\\n"; }', "Compile with strict warnings, use a debugger to inspect state, and use assertions for programmer assumptions that must hold during development.", "-Wall -Wextra -Wpedantic -g; assert(condition);", "Warning များကို ဖွင့်ထားပြီး debugger နှင့် assert ဖြင့် assumption များကို စစ်ပါ။"),
    (22, "Testing and CMake Foundations", "build tools", '#include <iostream>\n\nint add(int a, int b) { return a + b; }\nint main() { std::cout << add(2, 3) << "\\n"; }', "A small testable function separates behavior from I/O. CMake describes a portable build and can enforce the C++20 standard for a project.", "add_executable(app main.cpp); target_compile_features(app PRIVATE cxx_std_20)", "Testable function နှင့် CMake build configuration သည် project ကို maintain လုပ်လွယ်စေသည်။"),
]

MODULE_ONE_LESSONS = [
    ("What Is Programming?", "programming as a sequence of instructions", '#include <iostream>\n\nint main() {\n    std::cout << "A program follows steps.\\n";\n    std::cout << "The result is repeatable.\\n";\n}', "Programming is the process of describing data, decisions, and actions precisely enough for a computer to perform them. A program has inputs, processing steps, and observable outputs. The same source and input should produce a predictable result.", "input -> process -> output; statements execute in order", "Programming ဆိုသည်မှာ computer နားလည်နိုင်အောင် data၊ decision နှင့် action များကို အစီအစဉ်တကျ ဖော်ပြခြင်းဖြစ်သည်။"),
    ("Introduction to C++", "the C++ language and standard library", '#include <iostream>\n\nint main() {\n    std::cout << "Modern C++20\\n";\n}', "C++ is a compiled, general-purpose language used for applications, games, embedded systems, browsers, and high-performance services. C++20 adds modern language and library features while keeping control over performance and resources.", "#include <iostream>; int main(); std::cout << expression", "C++ သည် application၊ game၊ embedded system နှင့် performance လိုအပ်သော software များတွင် အသုံးများသော compiled language ဖြစ်သည်။"),
    ("C++ vs C", "language relationship and differences", '#include <iostream>\n#include <string>\n\nint main() {\n    std::string message{"C++ adds expressive abstractions"};\n    std::cout << message << "\\n";\n}', "C and C++ share many low-level ideas and both can produce fast native programs, but C++ adds classes, references, templates, the standard library, and RAII. C++ code should not be treated as automatically safe; correctness still depends on clear ownership and validation.", "C uses stdio-style APIs; C++ commonly uses iostream, std::string, containers, and classes", "C နှင့် C++ တွင် အခြေခံအယူအဆတူသော်လည်း C++ တွင် class၊ reference၊ template၊ standard library နှင့် RAII များ ပါဝင်သည်။"),
    ("How C++ Programs Work", "source, compiler, linker, and runtime", '#include <iostream>\n\nint main() {\n    std::cout << "Source -> compiler -> executable -> output\\n";\n}', "A C++ program begins as source text. The preprocessor handles directives, the compiler translates source into object code, the linker combines object code and libraries, and the operating system starts the executable.", "preprocess -> compile -> link -> run", "C++ program သည် source text မှ preprocess၊ compile၊ link အဆင့်များဖြတ်ပြီး executable ဖြစ်လာသည်။"),
    ("C++ Programming Tools", "compiler, editor, debugger, and build tool", '#include <iostream>\n\nint main() {\n    std::cout << "Tools make feedback faster.\\n";\n}', "A compiler translates code and reports diagnostics. An editor helps write source, a debugger helps inspect state, and a build tool records repeatable commands. Use strict warnings during learning.", "c++ -std=c++20 -Wall -Wextra -Wpedantic main.cpp -o main", "Compiler၊ editor၊ debugger နှင့် build tool များသည် code ရေးခြင်းနှင့် error ရှာခြင်းကို မြန်ဆန်စေသည်။"),
    ("Your First C++ Program", "main, headers, and console output", '#include <iostream>\n\nint main() {\n    std::cout << "Hello, C++ learner!\\n";\n    return 0;\n}', "The first complete program demonstrates a header, the main entry point, stream output, and a successful return status. Save it as hello.cpp and compile it with the C++20 standard.", "int main() { ... }; std::cout << \"text\"; return 0;", "ပထမဆုံး C++ program တွင် header၊ main၊ std::cout နှင့် return status ပါဝင်သည်။"),
    ("Programming Concepts & Assessment", "variables, decisions, repetition, and review", '#include <iostream>\n\nint main() {\n    int lessons{7};\n    if (lessons >= 5) std::cout << "Foundation ready\\n";\n}', "Programs combine sequence, selection, and repetition. Variables hold values, conditions select paths, and loops repeat work. This assessment reviews the vocabulary and the edit-compile-run workflow before Module 2.", "type name{value}; if (condition) { ... }; for (...) { ... }", "Program များသည် sequence၊ selection နှင့် repetition ကို ပေါင်းစပ်အသုံးပြုသည်။ Module 2 မတိုင်မီ အခြေခံ vocabulary နှင့် workflow ကို ပြန်လည်စစ်ဆေးပါ။"),
]

PROJECTS = [
    ("Simple Calculator", "Read two numbers, validate the operator, and calculate a result.", '#include <iostream>\nint main() { double a{12}, b{4}; char op{42}; if (op == 42) std::cout << a * b << "\\n"; }'),
    ("Number Guessing Game", "Compare a deterministic guess with a target and report the result.", '#include <iostream>\nint main() { const int target{7}; int guess{7}; std::cout << (guess == target ? "Correct\\n" : "Try again\\n"); }'),
    ("Multiplication Table", "Use a loop to print a clear table.", '#include <iostream>\nint main() { for (int i{1}; i <= 5; ++i) std::cout << "3 x " << i << " = " << 3 * i << "\\n"; }'),
    ("Student Grade Calculator", "Store marks, compute an average, and classify it.", '#include <iostream>\nint main() { int a{80}, b{90}; double average{(a + b) / 2.0}; std::cout << average << "\\n"; }'),
    ("Quiz Game", "Represent a question and evaluate an answer.", '#include <iostream>\nint main() { const int answer{2}; int selected{2}; std::cout << (answer == selected ? "Correct\\n" : "Incorrect\\n"); }'),
    ("Contact Book", "Use a vector of structs for contact records.", '#include <iostream>\n#include <string>\n#include <vector>\nstruct Contact { std::string name; std::string phone; };\nint main() { std::vector<Contact> book{{"Mya", "555-0100"}}; std::cout << book.front().name << "\\n"; }'),
    ("To-Do List", "Track tasks and completion state.", '#include <iostream>\n#include <string>\n#include <vector>\nstruct Task { std::string text; bool done; };\nint main() { std::vector<Task> tasks{{"Study C++", false}}; tasks[0].done = true; std::cout << tasks[0].text << " done\\n"; }'),
    ("Bank Account Simulator", "Encapsulate a balance and safe deposit operation.", '#include <iostream>\nclass Account { double balance_{0}; public: void deposit(double amount) { if (amount > 0) balance_ += amount; } double balance() const { return balance_; } };\nint main() { Account account; account.deposit(25); std::cout << account.balance() << "\\n"; }'),
    ("Expense Tracker", "Aggregate a small vector of expenses.", '#include <iostream>\n#include <vector>\nint main() { std::vector<double> expenses{4.5, 8.0, 2.5}; double total{0}; for (double value : expenses) total += value; std::cout << total << "\\n"; }'),
    ("Student Management", "Find a student by id in a vector.", '#include <iostream>\n#include <vector>\nstruct Student { int id; };\nint main() { std::vector<Student> students{{1}, {2}}; for (const auto& student : students) if (student.id == 2) std::cout << "found\\n"; }'),
    ("Inventory Manager", "Update stock quantities with a map.", '#include <iostream>\n#include <map>\nint main() { std::map<int, int> stock{{101, 3}}; stock[101] += 2; std::cout << stock.at(101) << "\\n"; }'),
    ("Library Management Capstone", "Combine structs, vectors, searching, and clear output.", '#include <iostream>\n#include <string>\n#include <vector>\nstruct Book { std::string title; bool borrowed; };\nint main() { std::vector<Book> books{{"C++20", false}}; books[0].borrowed = true; std::cout << books[0].title << " borrowed\\n"; }'),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content(title: str, topic: str, code: str, theory: str, syntax: str, mm: str, previous: str, next_title: str, project: bool = False) -> str:
    practice = f"Build a small {topic} example, change one input, predict the output, and compile it with -std=c++20 -Wall -Wextra -Wpedantic. Then explain why the result is correct."
    if project:
        practice = f"Implement the requirements for {title}, split the work into small functions or types, test normal and invalid inputs, and document one extension."
    return f"""Introduction\n{title} introduces {topic} through a complete, deterministic C++20 example.\n\nLearning objectives\n- Explain the purpose of {topic}.\n- Read and modify a complete C++20 program.\n- Predict behavior before compiling and test the result safely.\n\nPrerequisites\n{previous or 'A C++20 compiler and the previous lesson in this course.'}\n\nDetailed theory\n{theory} In real software, this idea helps developers make behavior explicit, testable, and easier to maintain.\n\nSyntax and best practices\n{syntax} Prefer standard library types, const correctness, RAII, meaningful names, and compiler warnings.\n\nReal-world example\nThe example models a small, deterministic piece of a learning or application workflow so its output can be checked without relying on a particular machine.\n\nComplete C++20 example\n```cpp\n{code}\n```\n\nExpected output\n```text\n{_output(code)}\n```\n\nLine-by-line explanation\nThe include lines provide the declarations used by the program. main owns the execution flow. Each declaration creates or names data, each expression performs one deliberate operation, and the output statement makes the result observable. Compile it, compare the output, and inspect the line that produced each value.\n\nCommon beginner mistakes\n- Confusing assignment with comparison or forgetting a semicolon.\n- Ignoring compiler warnings or assuming that compilation proves the logic is correct.\n- Using a dangling pointer, unchecked input, or an out-of-range index.\n- Copying a solution without first predicting and testing its behavior.\n\nModern C++ best practices\n- Prefer std::string, std::vector, const, references, algorithms, and RAII.\n- Keep ownership explicit and avoid manual new/delete in beginner application code.\n- Keep functions focused and validate input at a clear boundary.\n\nPractice exercises\n1. {practice}\n2. Add one validation or edge-case test and record the expected output.\n3. Explain one design choice to a study partner.\n\nSummary\nYou can now explain {topic}, read its C++20 syntax, and verify a complete program.\n\nNext lesson\n{next_title}\n\nMyanmar explanation\n{mm}\n"""


def _output(code: str) -> str:
    if "A program follows steps" in code: return "A program follows steps.\nThe result is repeatable."
    if "Modern C++20" in code: return "Modern C++20"
    if "C++ adds expressive abstractions" in code: return "C++ adds expressive abstractions"
    if "Source -> compiler" in code: return "Source -> compiler -> executable -> output"
    if "Tools make feedback faster" in code: return "Tools make feedback faster."
    if "Hello, C++ learner!" in code: return "Hello, C++ learner!"
    if "Foundation ready" in code: return "Foundation ready"
    if "C++ is ready" in code: return "C++ is ready"
    if "Hello, learner!" in code: return "Hello, learner!"
    if "Lessons: " in code: return "Lessons: 2"
    if "Build succeeded" in code: return "Build succeeded"
    if "Toolchain check" in code: return "Toolchain check"
    if "setprecision" in code: return "12.50"
    if "int lessons = weeks" in code: return "12"
    if "char grade" in code: return "7 2.5 A true"
    if "std::cin >> name" in code: return "Input: Ada\nHello, Ada"
    if "std::getline(std::cin" in code: return "Input: C++20\nYou typed: C++20"
    if "total / 2" in code: return "11 0"
    if "Excellent" in code: return "Excellent"
    if "Pause" in code: return "Pause"
    if "number <= 3" in code: return "1\n2\n3"
    if "std::sort" in code: return "1 2 3 4"
    if "value : values" in code: return "2 4 6"
    if "square(5)" in code: return "25"
    if "greet(" in code: return "Hi Mya"
    if "marks.at(1)" in code: return "85"
    if "names.size()" in code: return "3 Ada"
    if "add_one(count)" in code: return "5"
    if "*pointer" in code: return "9"
    if "outside + inside" in code: return "3\n1"
    if "make_unique" in code: return "42"
    if "counter.get()" in code: return "1"
    if "box.area()" in code: return "12"
    if "timer.seconds()" in code: return "30"
    if "Notice notice" in code: return "work\ncleanup"
    if "saved" in code: return "saved"
    if "cleanup" in code: return "work\ncleanup"
    if "breathing" in code: return "breathing\nmeow"
    if "shape.sides()" in code: return "3"
    if "Point result" in code: return "4 6"
    if "Score{8}" in code: return "1 8"
    if "maximum(4, 9)" in code: return "9"
    if "show(42)" in code: return "42\nready"
    if "scores.at" in code: return "90"
    if "divide(8, 2)" in code: return "4"
    if "twice(left + right)" in code: return "10"
    if "increment(4)" in code: return "5"
    if "assert(total" in code: return "checked"
    if "add(2, 3)" in code: return "5"
    if "a * b" in code: return "48"
    if "average" in code: return "85"
    if "book.front().name" in code: return "Mya"
    if "account.balance()" in code: return "25"
    if "total += value" in code: return "15"
    if "stock.at" in code: return "5"
    if "Capstone plan" in code: return "Capstone plan"
    if "accumulate" in code: return "12"
    if "Live" in code: return "Live"
    if "Correct" in code: return "Correct"
    if "found" in code: return "found"
    if "borrowed" in code: return "C++20 borrowed"
    if "done" in code: return "Study C++ done"
    if "Mya" in code and "Contact" not in code: return "Mya 88"
    if "std::boolalpha" in code: return "true"
    if "std::cout <<" in code and "3 * i" in code: return "3 x 1 = 3\n3 x 2 = 6\n3 x 3 = 9\n3 x 4 = 12\n3 x 5 = 15"
    return "The program prints the deterministic result described in the example."


def _questions(title: str, topic: str):
    return [
        (f"What is the main idea of {topic}?", [f"Use {topic} deliberately", "Ignore all types", "Skip compilation"], f"Use {topic} deliberately", "The lesson defines the concept and demonstrates it in a complete program."),
        ("Which command enables the course's C++20 warning flags?", ["c++ -std=c++20 -Wall -Wextra -Wpedantic", "run-cpp-now", "c++ --delete"], "c++ -std=c++20 -Wall -Wextra -Wpedantic", "The standard and warning flags make the compiler check the intended language and common mistakes."),
        (f"True or false: {title} should be tested with more than one input or state.", ["True", "False"], "True", "Testing an additional case helps reveal assumptions and boundary mistakes."),
    ]


def _module_one_questions(title: str):
    question_bank = {
        "What Is Programming?": [
            ("Which sequence best describes a simple program?", ["Input, process, output", "Output, delete, guess", "Compile, sleep, repeat"], "Input, process, output", "A useful model is to identify inputs, processing, and observable outputs."),
            ("True or false: A program should have predictable behavior for the same input.", ["True", "False"], "True", "Predictability makes software easier to test and explain."),
            ("Which is a programming mistake?", ["Changing code without testing the result", "Naming a value clearly", "Writing a small test"], "Changing code without testing the result", "Untested changes can hide logic errors."),
        ],
        "Introduction to C++": [
            ("Which library provides std::cout?", ["<iostream>", "<vector>", "<memory>"], "<iostream>", "iostream declares the standard stream objects used for console I/O."),
            ("True or false: C++20 is a language standard version.", ["True", "False"], "True", "C++20 names a published version of the C++ language and library standard."),
            ("What does std::cout usually do?", ["Writes formatted output", "Allocates a database", "Starts a debugger"], "Writes formatted output", "std::cout is the standard output stream."),
        ],
        "C++ vs C": [
            ("Which feature is commonly associated with modern C++?", ["RAII and classes", "Only preprocessor macros", "No standard library"], "RAII and classes", "C++ adds abstractions such as classes, references, templates, and RAII."),
            ("True or false: C++ code is automatically safe just because it uses a newer language.", ["True", "False"], "False", "Safety still requires correct ownership, validation, and careful design."),
            ("Which type manages text in the example?", ["std::string", "int", "bool"], "std::string", "std::string is the standard library text type used in the example."),
        ],
        "How C++ Programs Work": [
            ("Which stage combines object code and libraries?", ["Linking", "Typing", "Scrolling"], "Linking", "The linker combines compiled pieces into an executable."),
            ("True or false: The operating system runs C++ source text directly in the normal compiled workflow.", ["True", "False"], "False", "The usual workflow produces an executable before runtime."),
            ("What is the first artifact a developer edits?", ["Source code", "A CPU register", "A hidden binary"], "Source code", "The developer starts with human-readable source text."),
        ],
        "C++ Programming Tools": [
            ("Which tool reports compiler diagnostics?", ["Compiler", "Calculator", "Image viewer"], "Compiler", "The compiler translates source and reports syntax and type diagnostics."),
            ("True or false: -Wall -Wextra -Wpedantic are useful learning flags.", ["True", "False"], "True", "Warnings help identify suspicious or non-portable code early."),
            ("What is a debugger used for?", ["Inspecting program state", "Replacing all tests", "Formatting a hard drive"], "Inspecting program state", "A debugger can pause execution and inspect values and call paths."),
        ],
        "Your First C++ Program": [
            ("Where does a hosted C++ program begin?", ["main", "std::vector", "README"], "main", "The main function is the program entry point."),
            ("True or false: #include <iostream> supplies declarations for stream I/O.", ["True", "False"], "True", "The header declares facilities used by std::cout."),
            ("What does return 0 from main communicate?", ["Successful completion", "A loop", "A compiler installation"], "Successful completion", "Zero is the conventional successful process status."),
        ],
        "Programming Concepts & Assessment": [
            ("Which construct selects between paths?", ["if", "std::string", "#include"], "if", "A condition selects a branch at runtime."),
            ("True or false: Opening a lesson automatically proves its concepts were mastered.", ["True", "False"], "False", "Completion should come from an explicit lesson action and quiz/progress evidence."),
            ("What should you do before changing a working example?", ["Predict and record the expected result", "Delete all tests", "Disable warnings"], "Predict and record the expected result", "Prediction makes the change observable and testable."),
        ],
    }
    return question_bank.get(title, _questions(title, "the lesson topic"))


def seed_cpp_course(db, course):
    course.title = "C++ Programming — From Zero to Modern C++"
    course.short_description = "A free, theory-first C++20 foundation with practical programs, projects, quizzes, and safe modern practices."
    course.description = "Learn Modern C++20 from first principles through console programs, standard library techniques, object-oriented design, debugging, and guided projects."
    course.level = "beginner"
    course.outcomes = "Explain C++20 syntax and types|Build and test portable console programs|Use STL containers and algorithms|Apply RAII and safe modern C++ practices|Complete guided projects and a capstone"
    course.requirements = "Basic computer literacy; no previous programming experience is required; access to a C++20 compiler is recommended."
    course.status = "published"
    course.published = True

    authored = []
    for module_index, module_title in enumerate(MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_index))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_index)
            db.add(module); db.flush()
        else:
            module.title = module_title
        if module_index == 1:
            specs = MODULE_ONE_LESSONS
        elif module_index == 23:
            specs = [(name, "guided project", code, requirements, "Break the project into requirements, implementation, tests, and an extension.", "Project တစ်ခုချင်းစီကို requirements၊ implementation၊ test နှင့် extension အဖြစ် ခွဲလုပ်ပါ။") for name, requirements, code in PROJECTS]
        elif module_index == 24:
            specs = [("Capstone Requirements and Architecture", "capstone planning", '#include <iostream>\nint main() { std::cout << "Capstone plan\\n"; }', "Choose a useful problem, write requirements, define types and functions, and plan tests before implementation.", "Requirements -> design -> implementation -> tests", "Capstone ကို code မရေးမီ requirements နှင့် tests ကို အရင်ရေးပါ။"), ("Final C++20 Assessment", "final assessment", '#include <iostream>\n#include <vector>\n#include <numeric>\nint main() { std::vector<int> values{2, 4, 6}; std::cout << std::accumulate(values.begin(), values.end(), 0) << "\\n"; }', "The final assessment combines types, functions, containers, algorithms, error handling, and explanation. A score is earned through the existing quiz and progress systems, not by opening the page.", "combine verified concepts; explain trade-offs; test edge cases", "Final assessment တွင် concept များကို ပေါင်းစပ်ပြီး edge case များကို test လုပ်ပါ။")]
        else:
            first = LESSONS[(module_index - 1) * 2]
            second = LESSONS[(module_index - 1) * 2 + 1]
            specs = [(first[1], first[2], first[3], first[4], first[5], first[6]), (second[1], second[2], second[3], second[4], second[5], second[6])]
        for lesson_index, (title, topic, code, theory, syntax, mm) in enumerate(specs, 1):
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm="")
                db.add(lesson); db.flush()
            lesson.title, lesson.slug = title, slug
            previous = f"Complete the earlier lessons in Module {module_index - 1}." if module_index > 1 else "No programming experience is required."
            next_title = "Continue to the next module." if module_index == 24 else "Continue with the next lesson in the curriculum."
            lesson.content_en = _content(title, topic, code, theory, syntax, mm, previous, next_title, module_index == 23)
            lesson.content_mm = f"{title} အကြောင်းကို English theory နှင့်အတူ ပြန်လည်လေ့လာနိုင်ပါသည်။\n\n{mm}"
            lesson.description = theory
            lesson.duration_minutes, lesson.status, lesson.published = (35 if module_index == 23 else 25), "published", True
            authored.append(lesson)
            example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id, CodeExample.position == 1))
            if not example:
                example = CodeExample(lesson_id=lesson.id, position=1, title=f"{title} — complete C++20 example", language="cpp", code=code)
                db.add(example)
            else:
                example.title, example.language, example.code = f"{title} — complete C++20 example", "cpp", code
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz:
                quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Answer all questions, review the explanations, and retry after studying any missed concept.", status="published")
                db.add(quiz); db.flush()
            questions = _module_one_questions(title) if module_index == 1 else _questions(title, topic)
            for position, (prompt, options, answer, explanation) in enumerate(questions, 1):
                question = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == position))
                question_type = "true_false" if options == ["True", "False"] else "multiple_choice"
                values = dict(prompt=prompt, question_type=question_type, options_json=json.dumps(options), correct_answer=answer, explanation=explanation)
                if not question: db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))
                else:
                    for key, value in values.items(): setattr(question, key, value)
    course.duration_minutes = sum((lesson.duration_minutes or 25) for lesson in authored)
    db.flush()
