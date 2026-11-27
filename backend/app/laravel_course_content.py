"""Authored Laravel vertical slice for the idempotent catalog seed."""
import json
import re

from sqlalchemy import select

from .models import CodingExercise, CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

PLANNED_MODULES = [
    "Introduction to Laravel", "Modern PHP Fundamentals", "Composer & PHP Environment", "Laravel Installation & Setup",
    "Laravel Project Structure", "Laravel MVC Architecture", "Routing Fundamentals", "Controllers & Request Handling",
    "Blade Template Engine", "Middleware & Request Lifecycle", "Forms & Validation", "Sessions, Cookies & CSRF",
    "Database Fundamentals", "Migrations, Seeders & Factories", "Eloquent ORM Fundamentals", "Eloquent Relationships",
    "Advanced Eloquent", "Authentication Fundamentals", "Authorization & Policies", "REST API Development",
    "Laravel Sanctum", "File Uploads & Storage", "Blade Components & Livewire", "Inertia.js & React Integration",
    "Email & Notifications", "Events & Listeners", "Queues & Background Jobs", "Task Scheduling", "Redis & Caching",
    "Broadcasting & Real-Time Features", "Laravel Testing Fundamentals", "Advanced API & Database Testing",
    "Laravel Security Best Practices", "Performance Optimization", "Application Architecture & Patterns",
    "Multi-Tenant SaaS Development", "Docker & Laravel Development", "CI/CD, Deployment & Monitoring",
    "Professional Laravel Projects", "Final Laravel Capstone",
]

MODULE_ONE = [
    ("What Laravel Provides", "MVC architecture, conventions, and productive web development", "php -v\ncomposer --version\nphp artisan --version", "terminal", "Laravel is a PHP framework that provides conventions and components for routing, controllers, views, validation, database access, queues, authentication, and testing. Framework automation is helpful only when its boundaries and configuration are understood.", "Laravel သည် routing၊ controller၊ view၊ validation၊ database၊ queue၊ authentication နှင့် testing အတွက် convention များကို ပေးသော PHP framework ဖြစ်သည်။", "Draw the boundary between PHP, Laravel, and the database in a request.", ("Laravel သည် ဘာကို ပေးသနည်း?", ["Conventions and components for web applications", "A replacement for PostgreSQL", "A secret storage vault"], "Conventions and components for web applications", "Laravel provides application structure and framework components.")),
    ("Modern PHP Foundations", "types, functions, arrays, and secure input boundaries", "php -v\nphp -r 'echo strtoupper(\"php\");'", "terminal", "Laravel applications are PHP programs. Understand variables, functions, arrays, classes, namespaces, exceptions, and strict input handling before relying on framework helpers. External request data is untrusted and must be validated.", "Laravel application သည် PHP program ဖြစ်သောကြောင့် variable၊ function၊ array၊ class၊ namespace နှင့် exception အခြေခံများကို နားလည်ရမည်။ Request data ကို validate လုပ်ရသည်။", "Identify which values in a fictional request must be validated before use.", ("Request input ကို ဘယ်လို ကိုင်တွယ်သင့်သနည်း?", ["Validate it at the application boundary", "Trust all browser values", "Put it in a secret file"], "Validate it at the application boundary", "Browser input is untrusted.")),
    ("Composer and Project Dependencies", "Composer packages, lockfiles, and reproducible installs", "composer create-project laravel/laravel example-app\ncd example-app\ncomposer install\nphp artisan about", "terminal", "Composer installs PHP dependencies and composer.lock records resolved versions. Use trusted packages, review updates, and keep secrets in environment configuration rather than committed files. The Academy examples do not install packages on its host.", "Composer သည် PHP dependency များကို install လုပ်ပြီး lockfile က resolved version များကို မှတ်တမ်းတင်သည်။ Trusted package နှင့် environment configuration ကို သုံးပါ။", "Explain why composer.lock should be reviewed and why .env should not be committed.", ("Dependency reproducibility အတွက် ဘာကို အသုံးပြုသနည်း?", ["composer.lock", "A random download URL", "A committed password"], "composer.lock", "The lockfile records resolved dependency versions.")),
    ("Create and Configure a Laravel App", "application keys, environment configuration, and safe setup", "composer create-project laravel/laravel example-app\ncd example-app\ncp .env.example .env\nphp artisan key:generate\nphp artisan serve", "terminal", "A Laravel project separates source, configuration, routes, views, and storage. APP_KEY and database settings belong in protected environment configuration. Never publish real credentials or production .env files.", "Laravel project သည် source၊ configuration၊ route၊ view နှင့် storage ကို ခွဲထားသည်။ APP_KEY နှင့် database setting ကို protected environment configuration ထဲထားရသည်။", "Create a setup checklist that distinguishes local .env values from committed example configuration.", ("Real credential ကို ဘယ်မှာ မထားသင့်သနည်း?", ["Committed source or public logs", "A protected secret manager", "A local protected environment"], "Committed source or public logs", "Credentials in source or logs can be exposed.")),
    ("Laravel Project Structure", "routes, app code, resources, database, and storage", "php artisan route:list\nphp artisan config:show app\nphp artisan about", "terminal", "The app directory contains application code, routes define entry points, resources hold views and frontend assets, database holds migrations and seeders, and storage holds runtime files. Learn the structure before adding behavior so responsibilities remain clear.", "app သည် application code၊ routes သည် entry point၊ resources သည် view/assets၊ database သည် migration/seeder နှင့် storage သည် runtime file များကို ထားသည်။", "Map a request from routes/web.php to a controller and Blade view.", ("Migration များကို ဘယ် folder တွင် ထားသနည်း?", ["database/migrations", "public/passwords", "storage/tokens"], "database/migrations", "Laravel convention keeps migration files in database/migrations.")),
    ("MVC Request Lifecycle", "routes, controllers, models, views, and responses", "php artisan route:list\n# Route -> controller -> model/service -> view or JSON response", "terminal", "Laravel MVC separates request matching, application behavior, persistence, and presentation. A controller should coordinate rather than contain every rule. Use policies, validation, services, and resources when the feature grows.", "Laravel MVC သည် request matching၊ business behavior၊ persistence နှင့် presentation ကို ခွဲထားသည်။ Controller ထဲတွင် rule အားလုံး မထည့်ဘဲ validation/policy/service ကို သုံးပါ။", "Trace a profile update from route to controller, validation, model, and response.", ("MVC တွင် controller ၏ တာဝန်က ဘာလဲ?", ["Coordinate request handling and application behavior", "Store every secret", "Replace the database"], "Coordinate request handling and application behavior", "Controllers coordinate the request rather than replacing every layer.")),
    ("Routes, Controllers, and Validation", "safe request handling and explicit route boundaries", "php artisan make:controller ProfileController\nphp artisan route:list\nphp artisan make:request UpdateProfileRequest", "terminal", "Routes should be explicit and protected where needed. Controllers receive validated requests and return a view, redirect, or JSON resource. Use route model binding carefully and authorize access before exposing or changing a record.", "Route သည် explicit ဖြစ်ပြီး လိုအပ်ပါက protected ဖြစ်ရမည်။ Controller သည် validated request ကို လက်ခံပြီး view/redirect/JSON ပြန်သည်။", "Design a protected update route with a form request and ownership policy.", ("Record update မလုပ်မီ ဘာကို စစ်သင့်သနည်း?", ["Validation and authorization", "Only a hidden browser field", "A client-supplied user id"], "Validation and authorization", "Both input validity and ownership must be enforced server-side.")),
    ("Blade Views and the First Tested Workflow", "templates, escaping, tests, and review", "php artisan make:view profile\nphp artisan test\nphp artisan route:list\nphp artisan config:clear", "terminal", "Blade provides escaped output, layouts, components, and control structures for server-rendered UI. A professional workflow creates a focused feature, validates input, tests it, inspects configuration, and reviews secrets before commit.", "Blade သည် escaped output၊ layout နှင့် component များကို ပေးသည်။ Feature တစ်ခုကို test၊ config review နှင့် secret review ပြုလုပ်ပြီးမှ commit လုပ်ပါ။", "Create a checklist for a profile page: route, validation, authorization, escaped view, feature test, and review.", ("Blade output အတွက် ဘာကို ဦးစားပေးသင့်သနည်း?", ["Escaped output and validated data", "Raw untrusted HTML everywhere", "Credentials in templates"], "Escaped output and validated data", "Escaping and validation reduce injection and data-handling risk.")),
]

# Five focused lessons per remaining module keep the catalog substantive while
# preserving the eight already published Module 1 lesson records and slugs.
MODULE_LESSON_TOPICS = {
    "Modern PHP Fundamentals": ["PHP type system and strict contracts", "Functions, arrays, and iterators", "Exceptions and failure boundaries", "Interfaces, traits, and value objects", "Modern PHP security review"],
    "Composer & PHP Environment": ["Composer package constraints", "PSR-4 autoloading", "Environment configuration", "Dependency updates and audits", "Reusable PHP package lab"],
    "Laravel Installation & Setup": ["Laravel version compatibility", "Application keys and configuration", "Artisan workflow", "Local database setup", "First Laravel health check"],
    "Laravel Project Structure": ["Application directories", "Configuration and service providers", "Routes and resources", "Storage and public assets", "Structure review lab"],
    "Laravel MVC Architecture": ["Request lifecycle", "Controllers and services", "Models and persistence", "Views and presenters", "Architecture boundary lab"],
    "Routing Fundamentals": ["Named routes", "Route parameters", "Route groups", "Route model binding", "Routing verification lab"],
    "Controllers & Request Handling": ["Controller responsibilities", "Form request objects", "Response types", "Dependency injection", "Request handling lab"],
    "Blade Template Engine": ["Blade expressions", "Layouts and components", "Escaped output", "Conditionals and loops", "Blade page lab"],
    "Middleware & Request Lifecycle": ["Middleware concepts", "Authentication middleware", "Custom middleware", "Middleware ordering", "Request pipeline lab"],
    "Forms & Validation": ["Validation rules", "Form request authorization", "Error messages", "Nested input validation", "Secure form lab"],
    "Sessions, Cookies & CSRF": ["Session storage", "Secure cookie flags", "CSRF tokens", "Flash messages", "Stateful form lab"],
    "Database Fundamentals": ["Relational schema design", "Keys and constraints", "Query builder basics", "Transactions", "Database boundary lab"],
    "Migrations, Seeders & Factories": ["Migration design", "Seed data", "Model factories", "Safe rollback", "Database setup lab"],
    "Eloquent ORM Fundamentals": ["Models and casts", "Mass assignment", "Query scopes", "Pagination", "Eloquent read lab"],
    "Eloquent Relationships": ["One-to-one relationships", "One-to-many relationships", "Many-to-many relationships", "Eager loading", "Relationship integrity lab"],
    "Advanced Eloquent": ["Aggregates and subqueries", "Observers and events", "Custom casts", "Query performance", "Eloquent review lab"],
    "Authentication Fundamentals": ["Authentication flow", "Password hashing", "Email verification", "Session invalidation", "Login security lab"],
    "Authorization & Policies": ["Gates and policies", "Ownership checks", "Role permissions", "Authorization responses", "Policy testing lab"],
    "REST API Development": ["Resource routes", "HTTP status codes", "API request validation", "Pagination and filters", "Laravel API lab"],
    "Laravel Sanctum": ["Token authentication", "Sanctum abilities", "SPA cookies", "CSRF and CORS", "Protected API lab"],
    "File Uploads & Storage": ["Upload validation", "Local disks", "Public and private files", "Signed URLs", "Safe upload lab"],
    "Blade Components & Livewire": ["Blade components", "Component properties", "Livewire state", "Livewire validation", "Interactive UI lab"],
    "Inertia.js & React Integration": ["Inertia page data", "React TypeScript props", "Form submissions", "Client navigation", "Inertia feature lab"],
    "Email & Notifications": ["Mailables", "Notification channels", "Queued notifications", "Templates and localization", "Notification lab"],
    "Events & Listeners": ["Domain events", "Listeners", "Synchronous versus queued work", "Event testing", "Event workflow lab"],
    "Queues & Background Jobs": ["Job contracts", "Queue connections", "Retries and backoff", "Failed jobs", "Queue worker lab"],
    "Task Scheduling": ["Scheduled commands", "Task frequency", "Overlapping jobs", "Scheduler monitoring", "Scheduled workflow lab"],
    "Redis & Caching": ["Cache keys and TTL", "Redis data structures", "Cache invalidation", "Locks and atomicity", "Caching lab"],
    "Broadcasting & Real-Time Features": ["Broadcast events", "WebSocket channels", "Private channel authorization", "Realtime client state", "Realtime feature lab"],
    "Laravel Testing Fundamentals": ["Feature tests", "Unit tests", "HTTP assertions", "Factories in tests", "Testing workflow lab"],
    "Advanced API & Database Testing": ["API contract tests", "Database isolation", "Authorization tests", "Queue and notification fakes", "Integration test lab"],
    "Laravel Security Best Practices": ["SQL injection defenses", "XSS and output escaping", "CSRF and session security", "Rate limiting", "Security review lab"],
    "Performance Optimization": ["Query profiling", "N plus one queries", "Config and route cache", "Response caching", "Performance lab"],
    "Application Architecture & Patterns": ["Service boundaries", "Repositories and query objects", "Domain actions", "Dependency inversion", "Architecture review lab"],
    "Multi-Tenant SaaS Development": ["Tenant identification", "Tenant scoped queries", "Tenant provisioning", "Tenant isolation tests", "Multi-tenant lab"],
    "Docker & Laravel Development": ["PHP container image", "Docker Compose services", "Database containers", "Development volumes", "Containerized Laravel lab"],
    "CI/CD, Deployment & Monitoring": ["CI quality gates", "Environment promotion", "Safe migrations", "Health checks and logs", "Deployment lab"],
    "Professional Laravel Projects": ["Project discovery", "Architecture decision records", "API and UI delivery", "Review and release", "Professional project lab"],
    "Final Laravel Capstone": ["Capstone scope", "Data and security design", "Full-stack implementation", "Testing and operations", "Capstone assessment"],
}

def _generated_code(title: str) -> str:
    lower = title.lower()
    if "route" in lower or "routing" in lower:
        return "Route::get('/profiles/{profile}', [ProfileController::class, 'show'])->name('profiles.show');"
    if "validation" in lower or "form" in lower:
        return "$validated = $request->validate(['name' => ['required', 'string', 'max:120']]);"
    if "eloquent" in lower or "query" in lower or "relationship" in lower:
        return "$profiles = Profile::query()->with('user')->latest()->paginate(15);"
    if "migration" in lower or "schema" in lower:
        return "Schema::create('profiles', function (Blueprint $table) { $table->id(); $table->string('name'); $table->timestamps(); });"
    if "queue" in lower or "job" in lower:
        return "ProcessProfile::dispatch($profile->id)->onQueue('default');"
    if "cache" in lower or "redis" in lower:
        return "$profile = Cache::remember('profile:' . $id, 300, fn () => Profile::findOrFail($id));"
    if "test" in lower:
        return "$this->get(route('profiles.index'))->assertOk()->assertSee('Profiles');"
    if "react" in lower or "inertia" in lower:
        return "const response = await fetch('/api/profiles', { headers: { Accept: 'application/json' } });"
    if "security" in lower or "csrf" in lower or "auth" in lower or "policy" in lower:
        return "$this->authorize('update', $profile);"
    return "php artisan about\nphp artisan route:list\nphp artisan test";

def _generated_content(module_title: str, title: str, position: int, previous: str, next_title: str) -> str:
    code = _generated_code(title)
    return f"""Introduction
{title} is part of the {module_title} module and develops a production-oriented Laravel skill.

Learning objectives
- Explain the purpose and boundary of {title}.
- Implement the workflow with explicit validation, authorization, and failure handling.
- Verify the behavior with a focused test and document its operational risks.

Prerequisites
{previous}

Introduction to the workflow
Laravel features become reliable when the request boundary, application rule, persistence boundary, and response format are explicit. Start with a small reproducible case, identify trusted and untrusted values, and define the success and failure result before writing code.

Detailed theory
{title} requires more than memorizing a command. Decide which layer owns the rule, which data may cross the boundary, how invalid input is rejected, and how a reviewer can verify the result. Keep controllers and UI components small, use dependency injection for collaborators, and keep database changes inside migrations and transactions where consistency requires it. For a full-stack feature, expose a documented JSON contract and keep authentication and authorization on the Laravel server.

Syntax and progressive examples
Example 1 — inspect the smallest framework boundary:
{code}

Example 2 — isolate the application operation:
final class ProfileAction {{
    public function handle(int $profileId): string {{ return 'profile:' . $profileId; }}
}}

Example 3 — reject invalid input:
$validated = $request->validate(['name' => ['required', 'string', 'max:120']]);

Example 4 — verify the result:
$this->assertDatabaseHas('profiles', ['id' => $profileId]);

Example 5 — preserve the security boundary:
$this->authorize('view', $profile);

Run the examples in a disposable Laravel project with the documented PHP and Laravel versions. Replace placeholder identifiers only after checking the real schema and route names.

Expected output
The expected result is a successful response or assertion for valid input and a clear validation, authorization, or domain error for invalid input. Verify status codes, database state, emitted events, queue behavior, and logs instead of relying on a browser message alone.

Code explanation
The first example shows the entry point for the feature. The action or service owns the focused behavior, validation prevents malformed data from entering the application, and the assertion proves the result at the right boundary. Authorization is server-side and must not depend on hidden fields or client-side route guards.

Practical lab
Build a disposable feature for {title}. Create the route or command, add the smallest service or controller boundary, validate input, authorize the operation, persist only the required data, and add a feature test. Record the command, request, response, database result, and cleanup step.

Error handling
Return a useful 4xx response for invalid input or unauthorized access, catch only exceptions that the layer can handle, and let unexpected failures reach structured logging and the framework error boundary. Do not expose stack traces, SQL, tokens, or environment values.

Debugging
Check php -v, composer show, php artisan about, route:list, configuration cache, database connectivity, logs, and the first failing assertion. Reproduce with one request and one fixture before changing multiple layers.

Security best practices
Use prepared queries or Eloquent bindings, escaped Blade output, CSRF protection for state-changing browser requests, password hashing, authorization policies, rate limits, safe upload validation, secret management, and tenant-scoped queries where applicable.

Exercises
- Easy: reproduce Example 1 and explain each input and output.
- Medium: add validation and a test for one invalid request.
- Advanced: add authorization, failure logging, and a regression test for an unauthorized user.

Homework
Extend the lab with a README containing the architecture, database changes, API contract, threat model, test command, expected results, and rollback or cleanup procedure.

Quiz
1. Which boundary should validate external request data? The server-side request boundary.
2. True or false: a hidden form field is an authorization control. False.
3. Which practice proves a database write? A focused database assertion or verified read.
4. What should a production error response avoid? Secrets, stack traces, and internal SQL details.

Summary
You can now apply {title} through explicit boundaries, progressive examples, practical verification, and secure Laravel conventions.

Next lesson
{next_title}

Myanmar explanation
ဤသင်ခန်းစာတွင် {title} ကို Laravel application ၏ request၊ validation၊ authorization၊ database နှင့် testing boundary များနှင့် ဆက်စပ်ပြီး လေ့လာမည်။ External input ကို အတည်ပြုပြီးမှ အသုံးပြုပါ၊ state ပြောင်းလဲမှုတိုင်းတွင် permission စစ်ပါ၊ code ပြီးတိုင်း test ဖြင့် ရလဒ်ကို အတည်ပြုပါ။

Safety note
ဥပမာများကို disposable local Laravel project တွင်သာ run ပါ။ Production credential၊ database နှင့် Learn-Coding backend ကို မချိတ်ဆက်ပါနှင့်။
"""

def _generated_content_mm(
    module_title: str,
    title: str,
    code: str,
    previous: str,
    next_title: str,
    existing_mm: str = "",
    existing_exercise: str = "",
    question_data: tuple | None = None,
) -> str:
    """Build a complete Burmese lesson while keeping executable examples unchanged."""
    existing_question = question_data[0] if question_data else f"{title} ကို လေ့လာရာတွင် အရေးကြီးဆုံးအချက်က ဘာလဲ?"
    existing_options = question_data[1] if question_data else ["Server-side boundary နှင့် test ကို သတ်မှတ်ခြင်း", "Browser value ကို အမြဲယုံခြင်း", "Secret ကို source code ထဲထည့်ခြင်း"]
    existing_answer = question_data[2] if question_data else existing_options[0]
    existing_explanation = question_data[3] if question_data else "Server-side validation၊ authorization နှင့် test များက feature ၏ အပြုအမူကို စစ်ဆေးနိုင်စေသည်။"
    short_context = existing_mm or f"{title} သည် {module_title} ၏ အဓိကအကြောင်းအရာကို လက်တွေ့လေ့လာစေသော သင်ခန်းစာဖြစ်သည်။"
    exercise = existing_exercise or f"{title} အတွက် disposable Laravel project တစ်ခုတွင် valid case နှင့် invalid case နှစ်မျိုးကို တည်ဆောက်ပြီး result ကို test ဖြင့် စစ်ဆေးပါ။"
    return f"""သင်ခန်းစာခေါင်းစဉ် — {title}

နိဒါန်း
{short_context}

သင်ယူရမည့်ရည်ရွယ်ချက်များ
- {title} ၏ အဓိပ္ပာယ်၊ အသုံးပြုပုံနှင့် application boundary ကို ကိုယ်တိုင်ရှင်းပြနိုင်ရန်။
- Request၊ validation၊ authorization၊ persistence နှင့် response အဆင့်များကို အစဉ်လိုက် တည်ဆောက်နိုင်ရန်။
- အောင်မြင်သောအခြေအနေနှင့် မအောင်မြင်သောအခြေအနေ နှစ်မျိုးလုံးကို test ဖြင့် အတည်ပြုနိုင်ရန်။
- Secret၊ permission၊ input နှင့် database state များကို လုံခြုံစွာ ကိုင်တွယ်နိုင်ရန်။

လိုအပ်သောအခြေခံများ
{previous}
PHP syntax၊ command line နှင့် HTTP request/response အခြေခံကို သိထားပါ။ မသေချာသည့် version၊ package သို့မဟုတ် configuration ကို လက်တွေ့အသုံးမပြုမီ official documentation နှင့် project ၏ lockfile ကို စစ်ပါ။

Workflow အကြောင်းမိတ်ဆက်
Laravel feature တစ်ခုကို route သို့မဟုတ် request boundary မှ စတင်ပြီး middleware၊ controller သို့မဟုတ် service၊ model/database နှင့် Blade သို့မဟုတ် JSON response အထိ ခွဲခြမ်းစဉ်းစားရသည်။ Browser မှလာသော data ကို အယုံအကြည်မရှိသော input အဖြစ် သတ်မှတ်ပါ။ Valid input ကိုသာ application rule ထဲသို့ ပို့ပြီး state ပြောင်းလဲမှုတိုင်းတွင် authorization ကို server ဘက်မှ စစ်ဆေးပါ။

အသေးစိတ်သီအိုရီ
{title} ကို command တစ်ခုမှတ်ထားရုံဖြင့် မလုံလောက်ပါ။ Rule ကို ဘယ် layer က ပိုင်ဆိုင်သလဲ၊ ဘယ် data ကို boundary ကျော်ခွင့်ပြုသလဲ၊ မမှန်ကန်သော input ကို ဘယ်လိုငြင်းပယ်မလဲ၊ အခြား developer က ဘယ်လိုပြန်စစ်နိုင်မလဲဆိုသည်ကို အရင်သတ်မှတ်ပါ။ Controller နှင့် UI component များကို သေးငယ်အောင်ထားပြီး dependency injection ဖြင့် collaborator များကို ထည့်ပါ။ Database ပြောင်းလဲမှုများကို migration ထဲတွင် ထိန်းသိမ်းပြီး consistency လိုအပ်သော state changes များကို transaction ဖြင့် ကာကွယ်ပါ။

Full-stack feature တစ်ခုတွင် Laravel server သည် authentication၊ authorization၊ validation နှင့် data ownership ကို အဓိကပိုင်ဆိုင်ရမည်။ React၊ Blade သို့မဟုတ် အခြား client သည် user interface နှင့် request ပြုလုပ်မှုကို ကိုင်တွယ်နိုင်သော်လည်း client-side guard တစ်ခုတည်းကို လုံခြုံရေးအဖြစ် မယူဆပါနှင့်။ API response တွင် လိုအပ်သည့် field များသာ ထည့်ပြီး internal error၊ token နှင့် secret များကို မထုတ်ပြပါနှင့်။

Syntax နှင့် အဆင့်လိုက်ဥပမာများ
ဥပမာ ၁ — အနည်းဆုံး framework boundary ကို ကြည့်ခြင်း
{code}

ဥပမာ ၂ — Application operation ကို သီးခြားခွဲခြင်း
final class ProfileAction {{
    public function handle(int $profileId): string {{ return 'profile:' . $profileId; }}
}}

ဥပမာ ၃ — မမှန်ကန်သော input ကို ပယ်ချခြင်း
$validated = $request->validate(['name' => ['required', 'string', 'max:120']]);

ဥပမာ ၄ — ရလဒ်ကို အတည်ပြုခြင်း
$this->assertDatabaseHas('profiles', ['id' => $profileId]);

ဥပမာ ၅ — Security boundary ကို ထိန်းသိမ်းခြင်း
$this->authorize('view', $profile);

အထက်ပါ code များကို version ကိုက်ညီသော disposable Laravel project ထဲတွင်သာ run ပါ။ Placeholder identifier များကို သင့် project ၏ route name၊ schema နှင့် model အမှန်များကို စစ်ပြီးမှ ပြောင်းပါ။ Code fence မပါသော snippet ကို စာသားအဖြစ် ဖတ်ရှုနိုင်သော်လည်း executable source အဖြစ် copy မလုပ်မီ context ကို အတည်ပြုပါ။

မျှော်မှန်းရလဒ်
Valid input အတွက် အောင်မြင်သော response သို့မဟုတ် assertion ရရမည်။ Invalid input အတွက် validation error၊ authorization error သို့မဟုတ် domain error ကို ရှင်းလင်းစွာ ပြရမည်။ Browser message တစ်ခုတည်းကို မယုံဘဲ status code၊ database state၊ event၊ queue result နှင့် application log တို့ကိုလည်း စစ်ပါ။

Code ရှင်းလင်းချက်
ပထမဥပမာသည် feature ၏ entry point ကို ပြသည်။ Action သို့မဟုတ် service သည် အဓိကလုပ်ဆောင်ချက်ကို ပိုင်ဆိုင်ပြီး validation သည် ပုံစံမမှန်သော data များ application ထဲ မဝင်စေရန် ကာကွယ်သည်။ Database assertion သည် state ပြောင်းလဲမှု အမှန်ဖြစ်ကြောင်း သက်သေပြသည်။ Authorization သည် server-side ဖြစ်ရပြီး hidden field သို့မဟုတ် client-side route guard ပေါ် မူတည်ရမည်မဟုတ်ပါ။

လက်တွေ့လေ့ကျင့်ခန်း
{exercise}
Route သို့မဟုတ် command ကို ဖန်တီးပါ။ အနည်းဆုံး controller/service boundary တစ်ခု ထည့်ပါ။ Input ကို validate လုပ်ပါ။ လုပ်ဆောင်ခွင့်ကို authorize လုပ်ပါ။ လိုအပ်သည့် data ကိုသာ သိမ်းပါ။ Valid request၊ invalid request နှင့် unauthorized request အတွက် feature test များ ရေးပါ။ အသုံးပြုခဲ့သော command၊ request၊ response၊ database result နှင့် cleanup အဆင့်ကို မှတ်တမ်းတင်ပါ။

အမှားကိုင်တွယ်ခြင်း
Invalid input သို့မဟုတ် unauthorized access အတွက် သင့်တော်သော 4xx response ပြန်ပါ။ Layer တစ်ခုက ကိုင်တွယ်နိုင်သော exception ကိုသာ catch လုပ်ပါ။ မမျှော်လင့်ထားသော failure များကို structured logging နှင့် framework error boundary သို့ ပို့ပါ။ Stack trace၊ SQL၊ token၊ APP_KEY သို့မဟုတ် environment value များကို user response ထဲ မထည့်ပါနှင့်။

Debugging လမ်းညွှန်
php -v၊ composer show၊ php artisan about၊ route:list၊ configuration cache၊ database connection၊ log နှင့် ပထမဆုံး fail ဖြစ်သော assertion ကို စစ်ပါ။ ပြဿနာကို request တစ်ခုနှင့် fixture တစ်ခုဖြင့် ပြန်လည်ဖန်တီးပြီးမှ layer အများကြီးကို တပြိုင်နက် မပြောင်းပါနှင့်။ Error context ကို မဖျက်မီ မှတ်သားပါ။

လုံခြုံရေးအကောင်းဆုံးနည်းလမ်းများ
Prepared query သို့မဟုတ် Eloquent binding ကို သုံးပါ။ Blade output ကို escape လုပ်ပါ။ Browser မှ state ပြောင်းလဲသော request များတွင် CSRF protection သုံးပါ။ Password ကို hashing ဖြင့် သိမ်းပါ။ Resource ownership ကို policy ဖြင့် စစ်ပါ။ Rate limit၊ safe upload validation၊ secret manager နှင့် tenant-scoped query များကို သင့် feature လိုအပ်သလို ထည့်ပါ။

လေ့ကျင့်ခန်းများ
- လွယ်ကူသောအဆင့်: ဥပမာ ၁ ကို ပြန်လုပ်ပြီး input တစ်ခုစီနှင့် output တစ်ခုစီ၏ အဓိပ္ပာယ်ကို ရှင်းပြပါ။
- အလယ်အလတ်အဆင့်: Invalid request တစ်ခုအတွက် validation rule နှင့် test တစ်ခု ထည့်ပါ။
- အဆင့်မြင့်: Authorization၊ failure logging နှင့် ခွင့်မရှိသော user အတွက် regression test ထည့်ပါ။

အိမ်စာ
လက်တွေ့ lab ကို ဆက်လက်တိုးချဲ့ပြီး architecture၊ database change၊ API contract၊ threat model၊ test command၊ expected result နှင့် rollback သို့မဟုတ် cleanup procedure ပါသော README တစ်ခု ရေးပါ။ ထို README တွင် မည်သည့် data ကို ယုံကြည်နိုင်သလဲ၊ မည်သည့် data ကို မယုံကြည်ရသလဲဆိုသည်ကိုလည်း ရှင်းပြပါ။

Quiz
၁။ {existing_question}
ရွေးချယ်စရာများ: {"၊ ".join(existing_options)}
မှန်ကန်သောအဖြေ: {existing_answer}
ရှင်းလင်းချက်: {existing_explanation}

၂။ Academy သည် arbitrary PHP သို့မဟုတ် Laravel code ကို application host ပေါ်တွင် execute လုပ်သလား။ မလုပ်ပါ။
၃။ Application ကို ကာကွယ်ရန် ဘယ်နည်းလမ်းက မှန်ကန်သနည်း။ Input validation၊ authorization၊ escaped output နှင့် secret hygiene ကို server-side တွင် ထိန်းသိမ်းခြင်း ဖြစ်သည်။
၄။ State ပြောင်းလဲသော feature အလုပ်လုပ်ကြောင်း ဘာက သက်သေပြသနည်း။ Focused test နှင့် အတည်ပြုထားသော persisted result ဖြစ်သည်။

အနှစ်ချုပ်
ယခု {title} ကို request၊ validation၊ authorization၊ persistence နှင့် response boundary များဖြင့် စနစ်တကျ အသုံးချနိုင်ပြီဖြစ်သည်။ Code တစ်ခုရေးပြီးတိုင်း valid case၊ invalid case နှင့် permission case ကို စစ်ပါ။ Production data နှင့် credential များကို လေ့ကျင့်ခန်းတွင် မသုံးပါနှင့်။

နောက်သင်ခန်းစာ
{next_title}

လုံခြုံစွာလေ့လာရန် မှတ်ချက်
ဥပမာများကို disposable local Laravel project ထဲတွင်သာ run ပါ။ Production credential၊ အမှန်တကယ် database နှင့် Learn-Coding backend ကို မချိတ်ဆက်ပါနှင့်။ Dependency version၊ migration နှင့် deployment ပြောင်းလဲမှုတိုင်းကို review ပြီးမှ အသုံးပြုပါ။
"""

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(position: int, item: tuple) -> str:
    title, topic, commands, filename, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    previous = "No Laravel experience is required; basic PHP is helpful." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: complete the first Laravel application lab and review the Module 1 assessment."
    return f"""Introduction
{title} introduces {topic} through a safe Laravel workflow.

Learning objectives
- Explain {topic} in your own words.
- Trace a request through Laravel's layers.
- Identify validation, authorization, configuration, and secret boundaries.

Prerequisites
{previous}

Laravel architecture explanation
HTTP request -> route -> middleware -> controller/service -> model/database -> Blade or JSON response

Detailed theory
{theory}

Step-by-step PHP and Artisan examples
{commands}

File paths and folder structure
project/
  app/
  routes/web.php
  resources/views/
  database/migrations/
  tests/
  .env

Expected output
Exact output depends on the Laravel/PHP versions and local configuration. Verify the state with the relevant Artisan command instead of copying unverified output.

Code explanation
Read each route, class, command, and configuration boundary. Keep examples in a disposable project and distinguish local settings from committed source.

Common errors
- Using incompatible PHP, Composer, or Laravel versions.
- Trusting request fields without validation or authorization.
- Committing .env, APP_KEY, or database credentials.
- Putting business rules and queries into a single controller.

Troubleshooting
Check php -v, composer diagnose, php artisan about, route:list, configuration cache, and the first application error. Preserve error context before changing multiple files.

Best practices
- Validate at request boundaries, authorize resource ownership, and use escaped Blade output.
- Keep controllers focused and test the behavior you publish.
- Use parameterized Eloquent/query-builder operations and review dependencies.

Security considerations
Do not expose APP_KEY, passwords, tokens, private uploads, or debug details. Protect CSRF, sessions, policies, file validation, and tenant boundaries server-side.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Create a disposable Laravel profile feature with a route, validated request, authorization check, escaped Blade view, and feature test. Use placeholder data only.

Summary
You can now reason about {topic} as a sequence of protected Laravel request and response boundaries.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
The Academy displays PHP/Laravel examples and does not execute untrusted code on its application host.
"""

def seed_laravel_course(db, course):
    course.title = "Laravel & PHP Full-Stack Development — From Zero to Professional"
    course.short_description = "A free, practical path from PHP and Laravel fundamentals to secure APIs, database applications, and deployment."
    course.description = "Learn PHP, Composer, Laravel MVC, routing, Blade, validation, Eloquent, authentication, APIs, queues, caching, testing, security, Docker, and professional full-stack workflows through safe examples."
    # Newly generated curriculum must go through the admin review workflow.
    # Existing live rows are not touched unless this seed is explicitly run.
    course.level, course.status, course.published = "beginner", "draft", False
    course.duration_minutes = 0
    course.outcomes = "Build structured Laravel applications with routing, controllers, Blade, validation, and Eloquent|Create secure APIs with authentication, authorization, and resource ownership|Use migrations, queues, caching, testing, and deployment practices|Apply Laravel security, dependency, file, session, and tenant-isolation principles"
    course.requirements = "A text editor and basic command-line familiarity; no previous Laravel experience is required."
    for module_index, module_title in enumerate(PLANNED_MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_index))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_index)
            db.add(module)
            db.flush()
        module.title = module_title
        if module_index == 1:
            specs = MODULE_ONE
        else:
            specs = []
            for lesson_title in MODULE_LESSON_TOPICS[module_title]:
                topic = lesson_title.lower()
                code = _generated_code(lesson_title)
                filename = "routes/web.php" if "route" in topic else "app/Services/ProfileAction.php"
                specs.append((lesson_title, topic, code, filename, f"{lesson_title} requires a clear Laravel boundary, a verified happy path, and a deliberate failure path. Keep the rule close to its owner, validate external input, authorize state changes, and cover the behavior with a focused test.", f"{lesson_title} သည် Laravel boundary၊ validation၊ authorization နှင့် testing ကို ပေါင်းစပ်လေ့လာရန် အရေးကြီးသည်။", f"Build a disposable {lesson_title} feature, record the valid and invalid results, and add a focused test.", ("Which practice supports this lesson?", ["Explicit boundaries, validation, authorization, and tests", "Trust every browser value", "Commit production secrets"], "Explicit boundaries, validation, authorization, and tests", "Server-side boundaries make behavior reviewable and safer.")))
        for lesson_index, item in enumerate(specs, 1):
            title = item[0]
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == lesson_index))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=lesson_index, content_en="", content_mm="")
                db.add(lesson)
                db.flush()
            previous = "No Laravel experience is required; basic PHP is helpful." if module_index == 1 and lesson_index == 1 else f"Complete the previous lesson in this module before starting {title}."
            next_title = "Continue to the next lesson." if lesson_index < len(specs) else (f"Continue to Module {module_index + 1}." if module_index < len(PLANNED_MODULES) else "Complete the final capstone assessment.")
            previous_mm = "Laravel အတွေ့အကြုံ မလိုအပ်ပါ။ PHP အခြေခံကို သိထားပါက အထောက်အကူဖြစ်သည်။" if module_index == 1 and lesson_index == 1 else f"{title} မစတင်မီ ယခင်သင်ခန်းစာကို ပြီးအောင်လေ့လာပါ။"
            lesson.title, lesson.slug = title, slug
            lesson.description = item[1]
            lesson.content_en = _content(lesson_index, item) if module_index == 1 else _generated_content(module_title, title, lesson_index, previous, next_title)
            lesson.content_mm = _generated_content_mm(
                module_title,
                title,
                item[2],
                previous_mm,
                next_title,
                existing_mm=item[5] if module_index == 1 else "",
                existing_exercise=f"{title} ကို disposable Laravel project တစ်ခုတွင် လေ့ကျင့်ပြီး result ကို test ဖြင့် စစ်ဆေးပါ။",
                question_data=item[7] if module_index == 1 else None,
            )
            lesson.duration_minutes, lesson.status, lesson.published = 45, "draft", False
            course.duration_minutes += lesson.duration_minutes
            example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
            values = {"title": f"{title} example", "language": "php" if module_index > 1 or item[3] == "php" else "bash", "filename": item[3], "code": item[2], "description": "Read-only PHP/Laravel example. Run locally in an isolated workspace; the Academy does not execute code on its host.", "position": 1}
            if not example:
                db.add(CodeExample(lesson_id=lesson.id, **values))
            else:
                for key, value in values.items():
                    setattr(example, key, value)
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz:
                quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review the Laravel request boundary and security boundary before retrying.", status="draft")
                db.add(quiz)
                db.flush()
            first_question = (item[7][0], item[7][1], item[7][2], item[7][3])
            questions = [first_question, ("True or false: the Academy executes arbitrary PHP or Laravel code on its application host.", ["True", "False"], "False", "Examples are displayed as read-only learning content."), ("Which practice protects a Laravel application?", ["Validate input, authorize access, escape output, and keep secrets out of source", "Trust hidden form fields", "Commit .env and APP_KEY"], "Validate input, authorize access, escape output, and keep secrets out of source", "Server-side validation, authorization, output escaping, and secret hygiene reduce risk."), ("What proves a state-changing feature works?", ["A focused test and verified persisted result", "A hidden browser field", "A screenshot without a request"], "A focused test and verified persisted result", "Behavior needs a reproducible check at the correct boundary.")]
            for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
                row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
                values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
                if not row:
                    db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
                else:
                    for key, value in values.items():
                        setattr(row, key, value)
            for difficulty, label in (("beginner", "Easy"), ("intermediate", "Medium"), ("advanced", "Advanced")):
                exercise_slug = f"{slug}-{difficulty}"
                exercise = db.scalar(select(CodingExercise).where(CodingExercise.slug == exercise_slug))
                values = {"lesson_id": lesson.id, "title": f"{title} — {label} exercise", "slug": exercise_slug, "description_en": f"{label} exercise: implement and verify {title} in an isolated Laravel project.", "description_mm": f"{title} ကို သီးခြား Laravel project ထဲတွင် {label} အဆင့်ဖြင့် implement လုပ်ပြီး result ကို စစ်ဆေးပါ။", "difficulty": difficulty, "language": "php", "starter_code": "<?php\ndeclare(strict_types=1);\n", "status": "draft"}
                if not exercise:
                    db.add(CodingExercise(**values))
                else:
                    for key, value in values.items():
                        setattr(exercise, key, value)
    db.flush()
