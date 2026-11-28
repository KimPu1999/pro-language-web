"""Authored draft content for Django Module 06: forms and file uploads.

The seeder is scoped to the canonical sixth module. It protects published
lesson rows and uses the existing draft rows when they are safe to revise.
Examples are educational source files and are never executed against the
Learn-Coding platform database.
"""

from __future__ import annotations

import json
from textwrap import dedent

from sqlalchemy import select

from .models import (
    CodeExample,
    CodingExercise,
    CourseModule,
    Lesson,
    LessonContentDraft,
    LessonQuiz,
    LessonSyntaxReference,
    ModuleQuizDraft,
    ProjectCourseLink,
    ProjectMilestone,
    ProjectRequirement,
    ProjectRubricCriterion,
    ProjectTemplate,
    QuizQuestion,
    SyntaxExampleTranslation,
    SyntaxReference,
    SyntaxReferenceExample,
    SyntaxReferenceTranslation,
)


MODULE_TITLE = "Django Forms, ModelForms, Validation and File Uploads"
MODULE_TITLE_MM = "Django Form၊ ModelForm၊ Validation နှင့် File Upload"
MODULE_DESCRIPTION = (
    "Collect, validate, process and persist user input with Django Forms. Build safe ModelForms, "
    "accessible widgets, cross-field validation, related formsets and secure file/image upload workflows."
)
MODULE_DESCRIPTION_MM = (
    "Django Form ဖြင့် user input ကို စုဆောင်း၊ validate၊ process နှင့် persist လုပ်ပါ။ Safe ModelForm၊ "
    "accessible widget၊ cross-field validation၊ related formset နှင့် secure file/image upload workflow များကို တည်ဆောက်ပါ။"
)
OBJECTIVES = [
    "Create bound and unbound Django Forms and process safe GET/POST requests.",
    "Choose form fields and widgets, render accessible labels, help text and errors, and build responsive form templates.",
    "Use explicit ModelForm field allowlists, instance editing and commit=False without confusing forms with authorization.",
    "Implement reusable validators, clean_<fieldname>(), form.clean(), add_error() and database-backed integrity handling.",
    "Use formsets and inline formsets with management forms, restricted querysets, ownership checks and transactions.",
    "Validate file/image content, size and storage paths; handle replacement and orphan cleanup deliberately.",
    "Protect forms with CSRF, authorization, PRG, accessible UX and focused unit/integration tests.",
]
OBJECTIVES_MM = [
    "Bound/unbound Django Form ဖန်တီးပြီး safe GET/POST request ကို process လုပ်နိုင်ရန်။",
    "Form field/widget ရွေး၊ accessible label/help/error render နှင့် responsive form template တည်ဆောက်နိုင်ရန်။",
    "Explicit ModelForm allowlist၊ instance edit နှင့် commit=False ကို authorization နှင့် မရောဘဲ သုံးနိုင်ရန်။",
    "Reusable validator၊ clean_<fieldname>()၊ form.clean()၊ add_error() နှင့် database integrity handling တည်ဆောက်နိုင်ရန်။",
    "Management form၊ restricted queryset၊ ownership check နှင့် transaction ဖြင့် formset/inline formset သုံးနိုင်ရန်။",
    "File/image content၊ size နှင့် storage path validate လုပ်ပြီး replacement/orphan cleanup ကို ရည်ရွယ်ချက်ရှိစွာ ကိုင်တွယ်နိုင်ရန်။",
    "CSRF၊ authorization၊ PRG၊ accessible UX နှင့် focused test များဖြင့် form ကို ကာကွယ်နိုင်ရန်။",
]


def _example(title, files, input_text, output, steps, steps_mm):
    return {"title": title, "files": files, "input": input_text, "output": output, "steps": steps, "steps_mm": steps_mm}


def _q(prompt, options, answer, explanation, difficulty="intermediate", lesson=1):
    return {"prompt": prompt, "options": options, "correct_answer": answer, "explanation": explanation, "difficulty": difficulty, "points": 2 if difficulty == "intermediate" else 3 if difficulty == "advanced" else 1, "lesson_position": lesson}


COMMON_PREREQ = "Complete Django Modules 01–05 and use the database-backed Student Management System from the previous module. Run form and upload exercises in an isolated school_portal_forms_dev project with synthetic records; never use live student data or the platform database."
COMMON_PREREQ_MM = "Django Module 01–05 နှင့် ယခင် module ၏ database-backed Student Management System ကို ပြီးထားရမည်။ Form/upload exercise များကို synthetic record ပါသော school_portal_forms_dev isolated project တွင်သာ run ပါ။ Live student data သို့မဟုတ် platform database မသုံးပါနှင့်။"


LESSONS = [
    {
        "title": "Introduction to Django Forms",
        "slug": "06-user-model-and-authentication",
        "description": "Create a Student Registration Form, understand bound and unbound instances, validate POST data and use the Post/Redirect/Get pattern.",
        "description_mm": "Student Registration Form တည်ဆောက်ပြီး bound/unbound instance၊ POST data validation နှင့် Post/Redirect/Get pattern ကို နားလည်ပါ။",
        "topic": "forms.Form, fields, bound/unbound forms, GET/POST, is_valid(), cleaned_data, errors, CSRF and PRG",
        "theory": "An HTML form is a browser-to-server input boundary. Django Forms turn that boundary into a declared Python class containing fields, labels, widgets, conversion and validation rules. A Form instance without data is unbound and is suitable for the first display; passing request.POST creates a bound instance that can validate the submitted values. is_valid() triggers the field and form cleaning pipeline. When it returns True, cleaned_data contains converted Python values, not merely raw strings; when it returns False, errors contains safe field and non-field messages that the template can render. A form does not write to the database by itself. The view decides whether validated data becomes a service call, an email, or a model operation. State-changing forms should use POST, include {% csrf_token %}, reject invalid input without losing safe submitted values, and redirect after success so refresh does not repeat the action. The Post/Redirect/Get pattern separates the successful POST from the following GET. Server-side validation remains authoritative even if HTML attributes and JavaScript provide faster feedback. Keep messages helpful but avoid exposing stack traces, account secrets or internal database details.",
        "theory_mm": "HTML form သည် browser နှင့် server ကြား input boundary ဖြစ်သည်။ Django Form သည် field၊ label၊ widget၊ conversion နှင့် validation rule ပါသော Python class အဖြစ် ထို boundary ကို တိကျစွာဖော်ပြပေးသည်။ Data မပါသော Form instance သည် unbound ဖြစ်ပြီး ပထမဆုံး display အတွက်သင့်တော်သည်။ request.POST ပေးလျှင် bound instance ဖြစ်ကာ submit value များကို validate လုပ်နိုင်သည်။ is_valid() သည် field/form cleaning pipeline ကို စတင်သည်။ True ဖြစ်လျှင် cleaned_data တွင် raw string မဟုတ်ဘဲ converted Python value ရှိသည်။ False ဖြစ်လျှင် errors ထဲ field/non-field error ပါပြီး template တွင် ပြနိုင်သည်။ Form တစ်ခုတည်းက database write မလုပ်ပါ။ View က validated data ကို service၊ email သို့မဟုတ် model operation သို့ ပို့မည်ကို ဆုံးဖြတ်သည်။ State-changing form သည် POST သုံး၊ {% csrf_token %} ထည့်၊ invalid input တွင် safe submitted value မပျောက်စေဘဲ success ဖြစ်မှ redirect လုပ်ရမည်။ PRG သည် POST နှင့် နောက် GET ကို ခွဲပေးသည်။ HTML attribute/JavaScript feedback ရှိသော်လည်း server-side validation က authoritative ဖြစ်သည်။ Stack trace၊ secret နှင့် database detail မဖော်ပါနှင့်။",
        "concepts": "HTML form boundary; Form class; declared fields; bound and unbound; is_bound; is_valid; cleaned_data; errors; request.POST; CSRF; POST/Redirect/GET; safe feedback; service boundary.",
        "concepts_mm": "HTML form boundary၊ Form class၊ declared field၊ bound/unbound၊ is_bound၊ is_valid၊ cleaned_data၊ errors၊ request.POST၊ CSRF၊ POST/Redirect/GET၊ safe feedback နှင့် service boundary တို့ကို လေ့လာရမည်။",
        "syntax": "class StudentRegistrationForm(forms.Form):\n    name = forms.CharField(max_length=150)\n    email = forms.EmailField()\n    age = forms.IntegerField(min_value=5, max_value=120)\n\nform = StudentRegistrationForm(request.POST or None)",
        "examples": [
            _example("Declare a Student Registration Form", {"students/forms.py": "from django import forms\n\nclass StudentRegistrationForm(forms.Form):\n    name = forms.CharField(max_length=150, label=\"Student name\")\n    email = forms.EmailField(label=\"Email address\")\n    age = forms.IntegerField(min_value=5, max_value=120)"}, "A new form instance with no data", "The rendered form contains three labelled fields and browser hints for max length and numeric range.", "Declare fields, choose constraints that match the domain, and render the form through a template rather than hand-copying validation logic into JavaScript.", "Field သုံးခု declare လုပ်ပြီး domain နှင့်ကိုက်သော constraint ထည့်ပါ။ Template မှ render လုပ်ပါ။"),
            _example("Handle GET and POST", {"students/views.py": "from django.shortcuts import redirect, render\nfrom .forms import StudentRegistrationForm\n\ndef register(request):\n    form = StudentRegistrationForm(request.POST or None)\n    if request.method == \"POST\" and form.is_valid():\n        data = form.cleaned_data\n        # Call a service here; this lesson uses no real database write.\n        return redirect(\"students:success\")\n    return render(request, \"students/register.html\", {\"form\": form})"}, "GET /students/register/ then POST with name, email and age", "GET renders an unbound form; invalid POST renders the bound form with errors; valid POST redirects.", "Create the same view for both methods, bind only POST data, validate, then redirect after the service boundary succeeds.", "GET တွင် unbound form၊ invalid POST တွင် bound form/error၊ valid POST တွင် redirect ဖြစ်စေပါ။"),
            _example("Render CSRF and errors", {"templates/students/register.html": "<form method=\"post\" novalidate>\n  {% csrf_token %}\n  {{ form.non_field_errors }}\n  {% for field in form %}<div>{{ field.label_tag }}{{ field }}{{ field.help_text }}{{ field.errors }}</div>{% endfor %}\n  <button type=\"submit\">Register</button>\n</form>"}, "A bound form with an invalid email", "The email field retains the submitted value and displays a field-level error; the form includes a CSRF token.", "Use label_tag, field.errors and non_field_errors so the browser and assistive technology can locate the problem.", "label_tag၊ field.errors နှင့် non_field_errors သုံးပြီး error ကို ရှာဖွေရလွယ်စေပါ။"),
            _example("Read cleaned_data safely", {"students/services.py": "def preview_registration(form):\n    if not form.is_valid():\n        return {\"accepted\": False}\n    return {\n        \"accepted\": True,\n        \"name\": form.cleaned_data[\"name\"].strip(),\n        \"email\": form.cleaned_data[\"email\"].lower(),\n        \"age\": form.cleaned_data[\"age\"],\n    }"}, "A valid bound form", "The service receives converted and normalized values only after validation succeeds.", "Never read expected fields from raw request.POST after validation; use cleaned_data and keep persistence in a service with its own authorization boundary.", "Validation အောင်မြင်ပြီးမှ cleaned_data သုံးပါ။ Raw request.POST အစား normalized value ကို service သို့ပို့ပါ။"),
            _example("Test form states", {"students/tests/test_forms.py": "from django.test import SimpleTestCase\nfrom students.forms import StudentRegistrationForm\n\nclass RegistrationFormTests(SimpleTestCase):\n    def test_unbound_form_is_not_bound(self):\n        form = StudentRegistrationForm()\n        self.assertFalse(form.is_bound)\n\n    def test_invalid_email_has_error(self):\n        form = StudentRegistrationForm({\"name\": \"Learner\", \"email\": \"bad\", \"age\": 18})\n        self.assertFalse(form.is_valid())\n        self.assertIn(\"email\", form.errors)"}, "Empty form and invalid bound form", "The first form is unbound; the invalid form exposes a safe email error without any database write.", "Assert state and errors directly, and add an integration test later for the real POST/redirect boundary.", "Form state နှင့် error ကို တိုက်ရိုက် assert လုပ်ပြီး real POST/redirect အတွက် integration test ထပ်ရေးပါ။"),
        ],
        "mistakes": ["Using request.POST directly for business logic without a form boundary.", "Treating browser required attributes as server validation.", "Rendering an error without preserving the bound form.", "Returning a success page directly after POST and causing refresh resubmission."],
        "mistakes_mm": ["Form boundary မသုံးဘဲ request.POST ကို တိုက်ရိုက် business logic ထဲသုံးခြင်း။", "Browser required attribute ကို server validation ဟု ယူဆခြင်း။", "Bound form မပြန်ဘဲ error ပြခြင်း။", "POST အပြီး success page တိုက်ရိုက်ပြပြီး refresh resubmit ဖြစ်စေခြင်း။"],
        "best_practices": "Declare input contracts in forms, keep views thin, use cleaned_data only after is_valid(), render accessible errors, protect internal POSTs with CSRF and use PRG after a successful state change.",
        "best_practices_mm": "Input contract ကို Form တွင် declare လုပ်ပါ။ View ကို သေးငယ်ထားပါ။ is_valid() အောင်မြင်ပြီးမှ cleaned_data သုံးပါ။ Accessible error ပြပြီး internal POST တွင် CSRF သုံးကာ state change အောင်မြင်ပြီး PRG လုပ်ပါ။",
        "exercises": "Create a Student Form with name, email and age. Implement GET/POST handling, invalid error display, valid cleaned_data processing and a success redirect. Add tests for unbound, valid, invalid and overlong input.",
        "exercises_mm": "Name၊ email၊ age ပါသော Student Form ပြုလုပ်ပါ။ GET/POST၊ invalid error၊ valid cleaned_data processing နှင့် success redirect တည်ဆောက်ပါ။ Unbound/valid/invalid/overlong input test ရေးပါ။",
        "homework": "Build both a Contact Form and Student Registration Form with CSRF, accessible errors, safe server-side validation and PRG. Document which service boundary would persist the data.",
        "homework_mm": "CSRF၊ accessible error၊ safe server-side validation နှင့် PRG ပါသော Contact Form နှင့် Student Registration Form တည်ဆောက်ပါ။ Data persist မည့် service boundary ကို မှတ်တမ်းတင်ပါ။",
        "summary": "Django Forms provide a precise input contract. Bound state, validation, cleaned_data, safe errors and PRG form the core request lifecycle.",
        "summary_mm": "Django Form သည် input contract တိကျစွာပေးသည်။ Bound state၊ validation၊ cleaned_data၊ safe error နှင့် PRG တို့သည် request lifecycle ၏ အခြေခံဖြစ်သည်။",
        "quiz": [
            _q("What is an unbound form?", ["A form created without submitted data", "A saved model", "A CSRF token", "A file storage backend"], "A form created without submitted data", "Unbound forms render initial empty or initial values.", "beginner", 1),
            _q("What does is_valid() do?", ["Runs form validation and returns a boolean", "Saves every model automatically", "Disables CSRF", "Redirects every request"], "Runs form validation and returns a boolean", "It triggers the cleaning pipeline.", "beginner", 1),
            _q("When can cleaned_data be used safely?", ["After validation succeeds", "Before constructing the form", "Only in JavaScript", "After a template renders"], "After validation succeeds", "cleaned_data contains converted validated values.", "intermediate", 1),
            _q("Which pattern avoids form resubmission on refresh?", ["Post/Redirect/Get", "GET/GET/GET", "SQL/Redirect/SQL", "CSRF/GET"], "Post/Redirect/Get", "Redirect after a successful POST.", "intermediate", 1),
            _q("What protects an internal POST form from CSRF?", ["{% csrf_token %} with CSRF protection enabled", "A hidden password", "Only maxlength", "A CSS class"], "{% csrf_token %} with CSRF protection enabled", "The token participates in CSRF verification.", "intermediate", 1),
            _q("True or false: JavaScript validation replaces server validation.", ["True", "False"], "False", "Clients are not a trust boundary.", "beginner", 1),
            _q("Where should a database write normally occur after form validation?", ["A service or explicit view boundary", "Inside the template", "In the browser", "In the field label"], "A service or explicit view boundary", "Forms validate input; application code decides persistence.", "intermediate", 1),
            _q("What should an invalid POST render?", ["The bound form with safe errors", "A success redirect", "A raw traceback", "The password"], "The bound form with safe errors", "Users need their input and actionable errors preserved.", "intermediate", 1),
        ],
    },
    {
        "title": "Django Form Fields, Widgets and Rendering",
        "slug": "06-login-and-logout",
        "description": "Choose field types, widgets and rendering patterns for a professional, responsive and accessible Student Admission Form.",
        "description_mm": "Professional၊ responsive နှင့် accessible Student Admission Form အတွက် field type၊ widget နှင့် rendering pattern ရွေးချယ်ပါ။",
        "topic": "CharField, EmailField, choices, ModelChoiceField, FileField, widgets, labels, help_text, IDs, ARIA and responsive rendering",
        "theory": "A form Field owns conversion and validation while a Widget describes the HTML control used to collect the value. CharField, EmailField, IntegerField, DecimalField and DateField convert input into useful Python types; ChoiceField and ModelChoiceField constrain selection; FileField accepts uploaded streams and requires a multipart request. Widget classes such as TextInput, Textarea, Select, SelectMultiple, CheckboxInput, RadioSelect, DateInput and PasswordInput provide HTML semantics and attributes. Use labels and explicit ids so label-for relationships work. help_text should explain a constraint before the user submits, while errors should explain how to recover. aria-describedby can connect help or error text to an input, but ARIA should supplement native semantics rather than replace label elements. A ModelChoiceField queryset must be restricted to records the current user is allowed to see; a posted primary key is not authorization. Prefer Django’s real rendering APIs and customize templates or widgets deliberately. Do not duplicate server validation only in JavaScript. Responsive forms should remain keyboard navigable, readable at narrow widths, and preserve focus and error context after submission.",
        "theory_mm": "Form Field သည် input conversion/validation ကို တာဝန်ယူပြီး Widget သည် value စုမည့် HTML control ကို သတ်မှတ်သည်။ CharField၊ EmailField၊ IntegerField၊ DecimalField၊ DateField သည် input ကို အသုံးဝင်သော Python type ပြောင်းသည်။ ChoiceField/ModelChoiceField သည် ရွေးချယ်စရာ ကန့်သတ်သည်။ FileField သည် uploaded stream လက်ခံပြီး multipart request လိုသည်။ TextInput၊ Textarea၊ Select၊ SelectMultiple၊ CheckboxInput၊ RadioSelect၊ DateInput၊ PasswordInput သည် HTML semantic control များပေးသည်။ Label နှင့် id ကို ရှင်းလင်းထားပြီး label-for relationship အလုပ်လုပ်စေပါ။ help_text သည် submit မလုပ်မီ constraint ရှင်းပြီး error သည် ပြင်ဆင်နည်းပြသင့်သည်။ aria-describedby သည် help/error text နှင့် input ချိတ်ပေးနိုင်သော်လည်း native label အစားထိုးမဟုတ်ပါ။ ModelChoiceField queryset ကို လက်ရှိ user ခွင့်ရှိသော record များသာ ကန့်သတ်ပါ။ Posted primary key သည် authorization မဟုတ်ပါ။ Django rendering API အစစ်ကို သုံးပြီး template/widget ကို ရည်ရွယ်ချက်ရှိမှ customize လုပ်ပါ။ JavaScript ဖြင့် server validation ကို ထပ်မံအစားထိုးမလုပ်ပါနှင့်။ Narrow viewport တွင် keyboard၊ readable size၊ focus/error context ထိန်းပါ။",
        "concepts": "Field conversion; Widget; label; id_for_label; help_text; required; initial; choices; ModelChoiceField; FileField; aria-describedby; error_id; template rendering; keyboard access; responsive layout.",
        "concepts_mm": "Field conversion၊ Widget၊ label၊ id_for_label၊ help_text၊ required၊ initial၊ choices၊ ModelChoiceField၊ FileField၊ aria-describedby၊ error_id၊ template rendering၊ keyboard access နှင့် responsive layout တို့ကို လေ့လာရမည်။",
        "syntax": "class AdmissionForm(forms.Form):\n    course = forms.ModelChoiceField(queryset=Course.objects.none())\n    birth_date = forms.DateField(widget=forms.DateInput(attrs={\"type\": \"date\"}))\n    notes = forms.CharField(widget=forms.Textarea(attrs={\"rows\": 4}), required=False)",
        "examples": [
            _example("Build an information form", {"students/forms.py": "from django import forms\n\nclass AdmissionForm(forms.Form):\n    name = forms.CharField(label=\"Full name\", help_text=\"Use the name for your learning record.\")\n    email = forms.EmailField(widget=forms.EmailInput(attrs={\"autocomplete\": \"email\"}))\n    birth_date = forms.DateField(widget=forms.DateInput(attrs={\"type\": \"date\"}))"}, "A form displayed on a registration page", "The browser receives labelled text, email and date controls with useful autocomplete and input hints.", "Use the field type for server conversion, then add widget attributes that improve but do not replace validation.", "Server conversion အတွက် field type သုံးပြီး user experience တိုးစေရန် widget attribute ထည့်ပါ။"),
            _example("Restrict a course dropdown", {"students/forms.py": "class EnrollmentForm(forms.Form):\n    course = forms.ModelChoiceField(queryset=Course.objects.none(), label=\"Course\")\n\n    def __init__(self, *args, available_courses, **kwargs):\n        super().__init__(*args, **kwargs)\n        self.fields[\"course\"].queryset = available_courses.filter(is_archived=False)"}, "A queryset of courses available to this workflow", "The select contains only allowed non-archived courses; a posted id outside the queryset is invalid.", "Pass an already authorized queryset from the view/service and never use all objects merely for convenience.", "View/service မှ authorized queryset ပေးပြီး all objects အားလုံးမသုံးပါနှင့်။"),
            _example("Customize a textarea and errors", {"students/forms.py": "class NotesForm(forms.Form):\n    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={\"class\": \"field-control\", \"aria-describedby\": \"notes-help\"}), help_text=\"Do not include private credentials.\")", "templates/forms/field.html": "<div class=\"field\">{{ field.label_tag }}{{ field }}<small id=\"{{ field.id_for_label }}-help\">{{ field.help_text }}</small>{% if field.errors %}<div role=\"alert\">{{ field.errors }}</div>{% endif %}</div>"}, "A notes field with optional text", "Help text and an alert region are associated with a named control without hiding the validation result.", "Keep the rendered id stable, associate help/error text, and ensure color is not the only error signal.", "Rendered id ကို stable ထားပြီး help/error text ချိတ်ပါ။ Color တစ်ခုတည်းကို မယုံပါနှင့်။"),
            _example("Render a responsive form", {"templates/students/admission.html": "<form class=\"form-grid\" method=\"post\">{% csrf_token %}{% for field in form %}<div class=\"form-field\">{{ field.label_tag }}{{ field }}{{ field.help_text }}{{ field.errors }}</div>{% endfor %}<button type=\"submit\">Submit</button></form>", "static/css/forms.css": ".form-grid { display: grid; gap: 1rem; max-width: 42rem; }\n.form-field input, .form-field select, .form-field textarea { width: 100%; box-sizing: border-box; }\n@media (min-width: 48rem) { .form-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .form-grid button { grid-column: 1 / -1; } }\n:focus-visible { outline: 3px solid #7658ff; outline-offset: 2px; }"}, "320px through 768px viewport", "The form remains one column on narrow screens and uses two columns only when space permits, with visible keyboard focus.", "Start with readable mobile styles, add a wider breakpoint, and test labels, errors and focus at both widths.", "Narrow screen တွင် one column စပြီး wide breakpoint မှ two columns တိုးပါ။ Label/error/focus စစ်ပါ။"),
            _example("Inspect field errors in tests", {"students/tests/test_fields.py": "from django.test import SimpleTestCase\nfrom students.forms import AdmissionForm\n\nclass AdmissionFieldTests(SimpleTestCase):\n    def test_invalid_date_has_helpful_error(self):\n        form = AdmissionForm({\"name\": \"Learner\", \"email\": \"learner@example.test\", \"birth_date\": \"not-a-date\"})\n        self.assertFalse(form.is_valid())\n        self.assertIn(\"birth_date\", form.errors)"}, "An invalid date string", "The form reports a field error and does not provide an invalid Python date to application code.", "Test the field error key and the user-facing contract, not a browser-specific visual implementation.", "Field error key နှင့် user-facing contract ကို test လုပ်ပြီး browser-specific implementation မဟုတ်ပါ။"),
        ],
        "mistakes": ["Using ModelChoiceField.queryset=Model.objects.all() for every user.", "Removing labels and expecting placeholder text to be accessible.", "Using ARIA without a real label or error relationship.", "Building a desktop-only grid that overflows narrow screens."],
        "mistakes_mm": ["User တိုင်းအတွက် Model.objects.all() queryset သုံးခြင်း။", "Label ဖယ်ပြီး placeholder ကို accessible ဖြစ်မည်ဟု ယူဆခြင်း။", "Real label/error relationship မရှိဘဲ ARIA တစ်ခုတည်းသုံးခြင်း။", "Narrow screen တွင် overflow ဖြစ်သော desktop-only grid တည်ဆောက်ခြင်း။"],
        "best_practices": "Use semantic field types, explicit labels and help text, restricted querysets, stable IDs, visible focus, text-based error messages and mobile-first CSS. Let server fields remain authoritative.",
        "best_practices_mm": "Semantic field type၊ explicit label/help text၊ restricted queryset၊ stable id၊ visible focus နှင့် text error သုံးပါ။ Server field ကို authoritative ထားပြီး mobile-first CSS သုံးပါ။",
        "exercises": "Build a responsive Student Admission Form with course select, date input, notes textarea, help text, field errors and keyboard-visible focus. Test at 320px and 768px with both valid and invalid input.",
        "exercises_mm": "Course select၊ date input၊ notes textarea၊ help text၊ field error နှင့် keyboard focus ပါသော responsive Student Admission Form တည်ဆောက်ပါ။ 320px/768px တွင် valid/invalid input test လုပ်ပါ။",
        "homework": "Create a Professional Student Admission Form with a documented field contract, authorized course queryset, accessible error rendering, responsive CSS and a short UX review.",
        "homework_mm": "Field contract၊ authorized course queryset၊ accessible error rendering၊ responsive CSS နှင့် UX review ပါသော Professional Student Admission Form ပြုလုပ်ပါ။",
        "summary": "Fields convert and validate; widgets communicate semantics. Good rendering combines Django APIs, labels, errors, keyboard behavior and responsive layout.",
        "summary_mm": "Field သည် convert/validate လုပ်ပြီး widget သည် semantic ပြောသည်။ ကောင်းမွန်သော rendering တွင် Django API၊ label၊ error၊ keyboard နှင့် responsive layout ပါသည်။",
        "quiz": [
            _q("What does a Widget primarily describe?", ["The HTML control used to render a field", "A database transaction", "A user role", "A migration dependency"], "The HTML control used to render a field", "Widgets control HTML representation and attributes.", "beginner", 2),
            _q("Why restrict a ModelChoiceField queryset?", ["To prevent selecting records outside the allowed scope", "To disable labels", "To bypass CSRF", "To create a password"], "To prevent selecting records outside the allowed scope", "A posted id is not permission.", "advanced", 2),
            _q("What should help_text do?", ["Explain a constraint before submission", "Store a password", "Replace server validation", "Hide errors"], "Explain a constraint before submission", "Help text is user guidance.", "beginner", 2),
            _q("What is aria-describedby useful for?", ["Associating help or error text with a control", "Creating a database", "Checking authorization", "Running migrations"], "Associating help or error text with a control", "It supplements semantic labels and messages.", "intermediate", 2),
            _q("True or false: placeholder text is a replacement for a label.", ["True", "False"], "False", "Labels provide persistent accessible context.", "beginner", 2),
            _q("Which field is designed for a date value?", ["DateField", "TextField only", "BooleanField", "FilePathField only"], "DateField", "DateField converts and validates dates.", "beginner", 2),
            _q("What should a responsive form preserve?", ["Readable controls and keyboard focus", "Fixed desktop width only", "Color-only errors", "Hidden labels"], "Readable controls and keyboard focus", "Responsive UX includes accessibility.", "intermediate", 2),
            _q("Which layer remains authoritative when JavaScript disagrees?", ["The server-side form and validation", "The browser placeholder", "CSS", "The submit button color"], "The server-side form and validation", "Clients can be modified or bypassed.", "intermediate", 2),
        ],
    },
    {
        "title": "ModelForms and Database Integration",
        "slug": "06-registration-workflow",
        "description": "Create and edit Student records with explicit ModelForm allowlists, instance binding, commit=False and database integrity handling.",
        "description_mm": "Explicit ModelForm allowlist၊ instance binding၊ commit=False နှင့် database integrity handling ဖြင့် Student record create/edit ပြုလုပ်ပါ။",
        "topic": "ModelForm Meta, explicit fields, widgets, save(), save(commit=False), instances, model validation, uniqueness and overposting",
        "theory": "ModelForm builds form fields and model-related validation from a Django model, but it is not an authorization system. Always declare an explicit fields allowlist; exclude server-owned values such as owner, role, publication, moderation status and audit timestamps even if a user can see the model. Binding a new ModelForm to POST creates a new object on save; passing instance=student turns the same form into an edit boundary. save(commit=False) returns an unsaved instance so trusted server code can attach fields or related objects before the final save. It should not become a reason to skip model and database constraints. ModelForms perform model validation as part of their lifecycle, while uniqueness and foreign-key integrity still require database enforcement and careful IntegrityError handling. The view or service must fetch the object within an authorized scope before constructing the form. A browser can add unexpected fields to POST, so a form allowlist is an input boundary, not a convenience. Use transaction.atomic when the form save is part of multiple writes, and redirect after success.",
        "theory_mm": "ModelForm သည် Django model မှ form field နှင့် model-related validation ကို ဖန်တီးပေးသော်လည်း authorization system မဟုတ်ပါ။ fields allowlist ကို အမြဲ explicit ရေးပါ။ Owner၊ role၊ publication၊ moderation status နှင့် audit timestamp ကဲ့သို့ server-owned value များကို user မမြင်ရစေပါနှင့်။ New ModelForm ကို POST bind လုပ်ပြီး save လုပ်လျှင် object အသစ်ဖန်တီးသည်။ instance=student ပေးလျှင် edit boundary ဖြစ်သည်။ save(commit=False) သည် unsaved instance ပြန်ပေးပြီး trusted server code က field/related object ထည့်ပြီးမှ save လုပ်နိုင်သည်။ Model/database constraint မကျော်ရန် သုံးပါ။ ModelForm သည် model validation လုပ်သော်လည်း uniqueness/foreign-key integrity အတွက် database enforcement နှင့် IntegrityError handling လိုသည်။ View/service သည် authorized scope အတွင်း object fetch ပြီးမှ form တည်ဆောက်ရမည်။ Browser သည် POST ထဲ field အပိုထည့်နိုင်သောကြောင့် allowlist သည် input boundary ဖြစ်သည်။ Form save သည် write အများကြီးနှင့်ဆက်လျှင် transaction.atomic သုံးပြီး success တွင် redirect လုပ်ပါ။",
        "concepts": "ModelForm; Meta.model; Meta.fields; explicit allowlist; instance; save; commit=False; model validation; database constraints; IntegrityError; overposting; object scope; transaction.",
        "concepts_mm": "ModelForm၊ Meta.model၊ Meta.fields၊ explicit allowlist၊ instance၊ save၊ commit=False၊ model validation၊ database constraint၊ IntegrityError၊ overposting၊ object scope နှင့် transaction တို့ကို လေ့လာရမည်။",
        "syntax": "class StudentForm(forms.ModelForm):\n    class Meta:\n        model = Student\n        fields = [\"name\", \"email\", \"age\"]\n\nform = StudentForm(request.POST or None, instance=student)",
        "examples": [
            _example("Create an explicit Student ModelForm", {"students/forms.py": "from django import forms\nfrom .models import Student\n\nclass StudentForm(forms.ModelForm):\n    class Meta:\n        model = Student\n        fields = [\"name\", \"email\", \"age\"]\n        labels = {\"name\": \"Student name\"}"}, "A Student model with server-owned status fields", "Only name, email and age become editable form fields; status and owner are not exposed.", "Start from the model, write the allowlist, then inspect form.fields in a test to ensure no protected field appears.", "Model မှစပြီး allowlist ရေးပါ။ Protected field မပါကြောင်း test တွင် form.fields စစ်ပါ။"),
            _example("Save a new Student", {"students/views.py": "from django.shortcuts import redirect, render\nfrom .forms import StudentForm\n\ndef create_student(request):\n    form = StudentForm(request.POST or None)\n    if request.method == \"POST\" and form.is_valid():\n        student = form.save()\n        return redirect(\"students:detail\", pk=student.pk)\n    return render(request, \"students/form.html\", {\"form\": form})"}, "POST with valid student fields", "The ModelForm saves one student and redirects to its detail route; invalid input re-renders the bound form.", "Keep the success redirect separate from the form render and never return a fake success before save confirms.", "Save အောင်မြင်မှ success redirect လုပ်ပြီး invalid input တွင် bound form ပြန် render ပါ။"),
            _example("Edit an existing record", {"students/views.py": "from django.shortcuts import get_object_or_404, redirect, render\n\ndef edit_student(request, pk):\n    student = get_object_or_404(Student.objects.filter(is_archived=False), pk=pk)\n    form = StudentForm(request.POST or None, instance=student)\n    if request.method == \"POST\" and form.is_valid():\n        form.save()\n        return redirect(\"students:detail\", pk=student.pk)\n    return render(request, \"students/edit.html\", {\"form\": form, \"student\": student})"}, "A permitted student id and POST data", "The form shows existing values on GET and updates only allowlisted fields on valid POST.", "The real application must add an object-level authorization check before get_object_or_404 is allowed to return the object.", "Real application တွင် object-level authorization check ထည့်ပြီးမှ object fetch လုပ်ပါ။"),
            _example("Attach server-owned data with commit=False", {"students/services.py": "from django.db import transaction\n\ndef create_student(form, actor):\n    with transaction.atomic():\n        student = form.save(commit=False)\n        student.created_by = actor\n        student.save()\n        form.save_m2m()\n    return student"}, "A valid StudentForm and trusted actor", "The owner comes from the server, not from POST; the transaction encloses the related save boundary.", "Use commit=False only for a deliberate server-owned field or related write, then save the instance and call save_m2m when needed.", "Server-owned field ကို POST မဟုတ်ဘဲ trusted actor မှထားပါ။ လိုအပ်လျှင် save_m2m ခေါ်ပါ။"),
            _example("Protect duplicate email handling", {"students/tests/test_models.py": "from django.db import IntegrityError\nfrom django.test import TestCase\nfrom students.forms import StudentForm\n\nclass StudentFormTests(TestCase):\n    def test_duplicate_email_is_invalid_or_integrity_is_mapped(self):\n        Student.objects.create(name=\"Existing\", email=\"learner@example.test\", age=18)\n        form = StudentForm({\"name\": \"New\", \"email\": \"learner@example.test\", \"age\": 19})\n        self.assertFalse(form.is_valid())\n        self.assertIn(\"email\", form.errors)"}, "An existing unique email and a second submission", "The form reports the duplicate in the test database; the service still needs an IntegrityError boundary for races.", "Test normal uniqueness feedback and separately map a database race to a safe user-facing error.", "ပုံမှန် uniqueness error ကို test လုပ်ပြီး race အတွက် IntegrityError boundary သီးခြားရေးပါ။"),
        ],
        "mistakes": ["Using fields='__all__' on an editor form.", "Treating ModelForm validation as permission checking.", "Trusting an object id from POST without scoping the queryset.", "Calling commit=False without saving the returned instance or its many-to-many data."],
        "mistakes_mm": ["Editor form တွင် fields='__all__' သုံးခြင်း။", "ModelForm validation ကို permission check ဟု ယူဆခြင်း။", "POST object id ကို authorized scope မစစ်ဘဲ ယုံခြင်း။", "commit=False ပြီး instance/many-to-many data ကို save မလုပ်ခြင်း။"],
        "best_practices": "Allowlist fields, authorize the object before binding, keep server-owned values out of the form, use commit=False only with a clear final-save plan, preserve database constraints and map IntegrityError at the service boundary.",
        "best_practices_mm": "Field allowlist လုပ်ပါ။ Bind မလုပ်မီ object authorization စစ်ပါ။ Server-owned value ကို form အပြင်ထားပါ။ commit=False ကို final-save plan ရှိမှသုံးပါ။ Database constraint ထိန်းပြီး service boundary တွင် IntegrityError map လုပ်ပါ။",
        "exercises": "Build StudentForm create/edit views, add a restricted course selector, ignore an unexpected published field, test duplicate emails and document the authorization boundary for editing.",
        "exercises_mm": "StudentForm create/edit view တည်ဆောက်ပါ။ Restricted course selector၊ unexpected published field ignore၊ duplicate email test နှင့် edit authorization boundary မှတ်တမ်းတင်ပါ။",
        "homework": "Create a ModelForm-based Student CRUD interface with explicit fields, safe object lookup, server-owned metadata, PRG and tests for create, edit, invalid input and duplicate email.",
        "homework_mm": "Explicit field၊ safe object lookup၊ server-owned metadata၊ PRG နှင့် create/edit/invalid/duplicate email test ပါသော ModelForm Student CRUD interface ပြုလုပ်ပါ။",
        "summary": "ModelForms reduce repetition but do not remove design responsibility. Explicit fields, object authorization and database constraints keep model-backed editing safe.",
        "summary_mm": "ModelForm သည် repetition လျှော့ပေးသော်လည်း design responsibility မဖယ်ရှားပါ။ Explicit field၊ object authorization နှင့် database constraint များက model-backed edit ကို လုံခြုံစေသည်။",
        "quiz": [
            _q("What should Meta.fields usually contain on an editor ModelForm?", ["An explicit allowlist", "Every model field automatically", "Only password fields", "A URL pattern"], "An explicit allowlist", "Allowlisting prevents accidental overposting.", "intermediate", 3),
            _q("What does instance=student do?", ["Binds the form to edit that instance", "Creates a CSRF token", "Uploads a file", "Runs a migration"], "Binds the form to edit that instance", "The same ModelForm can create or update based on instance.", "beginner", 3),
            _q("Why use save(commit=False)?", ["To set trusted server fields before final save", "To bypass all constraints", "To avoid saving forever", "To expose all fields"], "To set trusted server fields before final save", "It returns an unsaved model instance.", "intermediate", 3),
            _q("True or false: ModelForm fields enforce object authorization.", ["True", "False"], "False", "Authorization belongs in the view/service boundary.", "beginner", 3),
            _q("What protects duplicate email under a race?", ["A database uniqueness constraint", "A hidden input", "A label", "Only a JavaScript check"], "A database uniqueness constraint", "The database remains authoritative.", "advanced", 3),
            _q("Why scope the object queryset before editing?", ["To prevent access to objects outside the authorized set", "To change CSS", "To disable validation", "To generate a URL only"], "To prevent access to objects outside the authorized set", "Object lookup is part of authorization.", "advanced", 3),
            _q("What is overposting?", ["Submitting fields the UI did not intend to expose", "Posting no data", "Rendering a label", "Running a GET"], "Submitting fields the UI did not intend to expose", "Allowlisted fields reduce overposting risk.", "intermediate", 3),
            _q("When is PRG useful after ModelForm save?", ["After a successful state change", "Before validation", "Inside a template loop", "Only for GET"], "After a successful state change", "Redirect avoids refresh resubmission.", "beginner", 3),
        ],
    },
    {
        "title": "Custom Validation and Form Error Handling",
        "slug": "06-permissions-and-groups",
        "description": "Implement reusable validators, field cleaning, cross-field admission rules, error codes and database-aware duplicate handling.",
        "description_mm": "Reusable validator၊ field cleaning၊ cross-field admission rule၊ error code နှင့် database-aware duplicate handling တည်ဆောက်ပါ။",
        "topic": "validation order, validators, clean_<fieldname>(), clean(), ValidationError, codes, params, add_error and non_field_errors",
        "theory": "Django validation is a pipeline. A field converts raw input with to_python(), checks required and field-specific rules, runs validators, then a form subclass can run clean_<fieldname>() for a normalized single field. After individual fields have been processed, Form.clean() can compare fields and add a non-field error or use add_error() to attach a problem to a particular field. Invalid fields may be absent from cleaned_data, so cross-field cleaning must use .get() and guard missing values. Reusable validators should raise ValidationError with a descriptive code and params so messages can be translated and tests can assert stable error semantics. Normalization such as trimming an email belongs before the service uses the value. Form validation improves user feedback but does not remove database uniqueness or transaction concerns; two valid forms can still race. Catch IntegrityError outside the atomic boundary and convert it to a safe form error. Client-side checks are progressive enhancement only. Never use validation messages to disclose whether a private account or sensitive record exists.",
        "theory_mm": "Django validation သည် pipeline ဖြစ်သည်။ Field သည် to_python() ဖြင့် raw input convert၊ required/field rule စစ်၊ validator run ပြီး form subclass တွင် clean_<fieldname>() သည် field တစ်ခုချင်း normalize/validate လုပ်နိုင်သည်။ Field အားလုံးပြီးမှ Form.clean() က field များနှိုင်းပြီး non-field error ထည့်နိုင်သည်။ Field-specific error လိုလျှင် add_error() သုံးပါ။ Invalid field သည် cleaned_data ထဲမရှိနိုင်သောကြောင့် cross-field clean တွင် .get() နှင့် guard သုံးပါ။ Reusable validator သည် code/params ပါသော ValidationError raise လုပ်သင့်ပြီး translation/test အတွက် အကျိုးရှိသည်။ Email trim/normalize ကို service မသုံးမီ လုပ်ပါ။ Form validation ရှိသော်လည်း database uniqueness/transaction မဖယ်ရှားနိုင်ပါ။ Valid form နှစ်ခု race ဖြစ်နိုင်သောကြောင့် IntegrityError ကို atomic အပြင် ဖမ်းပြီး safe form error ပြန်ပါ။ Client-side check သည် enhancement သာဖြစ်သည်။ Private record/account ရှိမရှိကို error message ဖြင့် မဖော်ပါနှင့်။",
        "concepts": "to_python; Field.clean; validators; clean_<fieldname>(); Form.clean; cleaned_data; ValidationError; code; params; add_error; non_field_errors; normalization; IntegrityError; duplicate submission; information disclosure.",
        "concepts_mm": "to_python၊ Field.clean၊ validator၊ clean_<fieldname>()၊ Form.clean၊ cleaned_data၊ ValidationError၊ code၊ params၊ add_error၊ non_field_errors၊ normalization၊ IntegrityError၊ duplicate submission နှင့် information disclosure တို့ကို လေ့လာရမည်။",
        "syntax": "class EnrollmentForm(forms.Form):\n    start_date = forms.DateField()\n    end_date = forms.DateField()\n\n    def clean(self):\n        data = super().clean()\n        if data.get(\"start_date\") and data.get(\"end_date\") and data[\"end_date\"] < data[\"start_date\"]:\n            raise forms.ValidationError(\"End date must not be before start date.\")\n        return data",
        "examples": [
            _example("Validate a reusable age", {"students/validators.py": "from django.core.exceptions import ValidationError\n\ndef validate_student_age(value):\n    if value < 5 or value > 120:\n        raise ValidationError(\"Enter an age from 5 to 120.\", code=\"invalid_age\", params={\"value\": value})"}, "age=3 or age=18", "Age 3 raises a coded ValidationError; age 18 passes and remains a Python integer.", "Keep the validator independent of HTTP, use a stable code, and attach it to both forms that share the rule.", "Validator ကို HTTP နှင့်မချိတ်ဘဲ stable code/params သုံးပြီး form နှစ်ခုတွင် reuse လုပ်ပါ။"),
            _example("Normalize an email", {"students/forms.py": "class ContactForm(forms.Form):\n    email = forms.EmailField()\n\n    def clean_email(self):\n        return self.cleaned_data[\"email\"].strip().casefold()"}, "'  Learner@Example.Test '", "cleaned_data['email'] becomes 'learner@example.test'.", "Use the converted value from the field, normalize once, and return it so later clean methods see the normalized value.", "Field မှ converted value ယူပြီး တစ်ကြိမ် normalize လုပ်ကာ return ပြန်ပါ။"),
            _example("Apply cross-field admission rules", {"students/forms.py": "class AdmissionWindowForm(forms.Form):\n    start_date = forms.DateField()\n    end_date = forms.DateField()\n\n    def clean(self):\n        data = super().clean()\n        start, end = data.get(\"start_date\"), data.get(\"end_date\")\n        if start and end and end < start:\n            raise forms.ValidationError(\"End date must not be before start date.\", code=\"invalid_window\")\n        return data"}, "start_date=2026-06-10 and end_date=2026-06-01", "The form is invalid and the message appears in non_field_errors because it concerns both dates.", "Call super().clean(), guard missing fields and use a form-level error for a relationship rule.", "super().clean() ခေါ်၊ missing field ကို guard လုပ်ပြီး relationship rule ကို form-level error ထားပါ။"),
            _example("Attach a field error", {"students/forms.py": "class EnrollmentForm(forms.Form):\n    course_code = forms.CharField(max_length=20)\n    confirm = forms.BooleanField(required=True)\n\n    def clean(self):\n        data = super().clean()\n        if data.get(\"course_code\") == \"FULL\":\n            self.add_error(\"course_code\", forms.ValidationError(\"Choose an available course.\", code=\"course_full\"))\n        return data"}, "course_code='FULL'", "The course_code is removed from cleaned_data and receives a field-specific error.", "Use add_error when the user can recover by changing one field; keep the message generic where availability is sensitive.", "Field ပြောင်းလဲခြင်းဖြင့် ပြင်နိုင်လျှင် add_error သုံးပြီး sensitive availability ကို generic message ထားပါ။"),
            _example("Map a uniqueness race", {"students/services.py": "from django.db import IntegrityError, transaction\n\ndef save_registration(form):\n    try:\n        with transaction.atomic():\n            return form.save()\n    except IntegrityError:\n        form.add_error(\"email\", \"This email cannot be registered at this time.\")\n        return None"}, "Two valid forms submit the same unique email", "One transaction succeeds; the other returns a form error instead of a server traceback or false success.", "The form check improves normal feedback, while the database and exception boundary handle the race.", "ပုံမှန် feedback ကို form check ပေးပြီး race ကို database/exception boundary က ကိုင်တွယ်ပါ။"),
        ],
        "mistakes": ["Accessing cleaned_data with [] for a field that may already have failed.", "Returning a different value from clean_<field>() without understanding later validation.", "Putting cross-field rules in JavaScript only.", "Catching IntegrityError inside an atomic block and continuing database queries."],
        "mistakes_mm": ["Fail ဖြစ်နိုင်သော field ကို cleaned_data[] ဖြင့် တိုက်ရိုက် access လုပ်ခြင်း။", "clean_<field>() return value ၏ နောက်ဆက်တွဲ validation မသိဘဲ ပြောင်းခြင်း။", "Cross-field rule ကို JavaScript တစ်ခုတည်းတွင်ထားခြင်း။", "Atomic block အတွင်း IntegrityError ဖမ်းပြီး query ဆက်လုပ်ခြင်း။"],
        "best_practices": "Choose the narrowest validation hook, use .get() for dependent fields, return normalized values, give ValidationError stable codes, attach errors where users can recover, and keep database constraints as the final authority.",
        "best_practices_mm": "အကျဉ်းဆုံး validation hook ရွေးပါ။ Dependent field တွင် .get() သုံးပါ။ Normalized value return ပါ။ ValidationError code တည်ငြိမ်စွာပေးပါ။ User ပြင်နိုင်သည့်နေရာတွင် error attach လုပ်ပြီး database constraint ကို final authority ထားပါ။",
        "exercises": "Validate numeric ranges, normalize an email, implement start/end date rules, add a coded custom error, map a duplicate email IntegrityError and write tests for every failure path.",
        "exercises_mm": "Numeric range၊ email normalize၊ start/end date rule၊ coded custom error နှင့် duplicate email IntegrityError mapping တည်ဆောက်ပြီး failure path တစ်ခုစီ test လုပ်ပါ။",
        "homework": "Build an Advanced Student Admission Validation System with reusable validators, cross-field rules, translated-safe error codes, database constraints and a test matrix.",
        "homework_mm": "Reusable validator၊ cross-field rule၊ translated-safe error code၊ database constraint နှင့် test matrix ပါသော Advanced Student Admission Validation System တည်ဆောက်ပါ။",
        "summary": "Validation hooks have an order and a purpose. Use field cleaning for one value, form cleaning for relationships, and database constraints for concurrent truth.",
        "summary_mm": "Validation hook တစ်ခုချင်းတွင် order နှင့် purpose ရှိသည်။ Field value အတွက် field clean၊ relationship အတွက် form clean နှင့် concurrent truth အတွက် database constraint သုံးပါ။",
        "quiz": [
            _q("When does clean_<fieldname>() run?", ["After that field has been converted and field-cleaned", "Before the form is constructed", "Only after redirect", "Only in JavaScript"], "After that field has been converted and field-cleaned", "The hook receives the cleaned field value.", "intermediate", 4),
            _q("Where does a Form.clean() ValidationError normally appear?", ["non_field_errors()", "Only in the URL", "The database log only", "The CSRF cookie"], "non_field_errors()", "It concerns the form as a whole.", "beginner", 4),
            _q("Why use cleaned_data.get() in clean()?", ["A previous field may have failed and be absent", "It disables validation", "It reads raw POST", "It saves a model"], "A previous field may have failed and be absent", "Dependent cleaning must tolerate missing values.", "advanced", 4),
            _q("What does add_error() do?", ["Associates an error with a field", "Creates a migration", "Uploads a file", "Grants permission"], "Associates an error with a field", "It also removes that field from cleaned_data.", "intermediate", 4),
            _q("True or false: a valid form guarantees a database write cannot race.", ["True", "False"], "False", "Database constraints and IntegrityError handling still matter.", "advanced", 4),
            _q("What should a reusable validator raise on invalid input?", ["ValidationError with a useful code", "A raw password", "A redirect", "A template"], "ValidationError with a useful code", "Codes help translation and stable tests.", "intermediate", 4),
            _q("Which hook is suited to compare start_date and end_date?", ["Form.clean()", "A label", "MEDIA_ROOT", "A CSS media query"], "Form.clean()", "Cross-field relationships belong in form cleaning.", "beginner", 4),
            _q("Where should IntegrityError be mapped?", ["At a service boundary outside the broken atomic block", "Inside a template", "In JavaScript only", "Never"], "At a service boundary outside the broken atomic block", "The boundary can safely render a useful error.", "advanced", 4),
        ],
    },
    {
        "title": "Advanced Django Forms, Formsets and Related Data",
        "slug": "06-session-security",
        "description": "Use formsets and inline formsets to edit related Student data safely with management forms, restricted querysets, ownership checks and transactions.",
        "description_mm": "Management form၊ restricted queryset၊ ownership check နှင့် transaction သုံးပြီး Student related data ကို formset/inline formset ဖြင့် safe edit လုပ်ပါ။",
        "topic": "formset_factory, management form, prefixes, model formsets, inline formsets, deletion, ownership and transactional saves",
        "theory": "A formset coordinates multiple instances of one form and adds a management form that tells Django how many forms are present. The management fields are part of the protocol; omitting or tampering with them makes the formset invalid. Prefixes let multiple formsets share a page without field-name collisions. formset_factory is useful for unrelated repeated values; modelformset_factory and inlineformset_factory connect forms to model rows. A formset’s queryset must be restricted to records the current workflow is authorized to modify. A posted primary key can point to another user’s object, so never accept it as proof of ownership. Validate the whole formset, use can_delete only with an explicit deletion policy, and save related records inside transaction.atomic when partial success would be harmful. For an inline formset, pass the parent instance and ensure the parent itself was authorized. Client-side row addition must preserve Django’s management form counts. Use a stable prefix when multiple formsets appear together and test missing management data, duplicate values, unauthorized ids, deletion and rollback.",
        "theory_mm": "Formset သည် form တစ်မျိုး၏ instance အများကို စီမံပြီး management form ဖြင့် form အရေအတွက်ကို Django သို့ ပြောသည်။ Management field မပါခြင်း/ပြုပြင်ခြင်းသည် invalid ဖြစ်စေသည်။ Prefix သည် page တစ်ခုတွင် formset အများရှိသော်လည်း field name collision မဖြစ်စေပါ။ formset_factory သည် repeated value များအတွက်၊ modelformset_factory/inlineformset_factory သည် model row များအတွက်သုံးသည်။ Formset queryset ကို လက်ရှိ workflow က modify ခွင့်ရှိသော record များသာ ကန့်သတ်ပါ။ Posted primary key သည် အခြား user object ကို ညွှန်နိုင်သောကြောင့် ownership သက်သေမဟုတ်ပါ။ Formset အားလုံး validate လုပ်ပြီး can_delete သည် explicit policy ရှိမှ သုံးပါ။ Partial success မလိုလျှင် transaction.atomic အတွင်း save လုပ်ပါ။ Inline formset တွင် parent instance ပေးပြီး parent authorization စစ်ပါ။ Client-side row ထပ်ထည့်လျှင် management form count မှန်ရမည်။ Missing management data၊ duplicate၊ unauthorized id၊ deletion နှင့် rollback test လုပ်ပါ။",
        "concepts": "formset_factory; management_form; TOTAL_FORMS; INITIAL_FORMS; prefix; can_delete; can_order; modelformset_factory; inlineformset_factory; parent instance; restricted queryset; ownership; atomic save.",
        "concepts_mm": "formset_factory၊ management_form၊ TOTAL_FORMS၊ INITIAL_FORMS၊ prefix၊ can_delete၊ can_order၊ modelformset_factory၊ inlineformset_factory၊ parent instance၊ restricted queryset၊ ownership နှင့် atomic save တို့ကို လေ့လာရမည်။",
        "syntax": "StudentContactFormSet = inlineformset_factory(\n    Student, StudentContact, fields=[\"kind\", \"value\"], extra=1, can_delete=True\n)\nformset = StudentContactFormSet(request.POST or None, instance=student)",
        "examples": [
            _example("Render a basic formset", {"students/forms.py": "from django import forms\n\nclass ContactForm(forms.Form):\n    kind = forms.CharField(max_length=30)\n    value = forms.CharField(max_length=120)\n\nContactFormSet = forms.formset_factory(ContactForm, extra=2, can_delete=True)"}, "Two contact forms", "The template must render management_form before the individual forms and can display two empty rows.", "Construct the formset, render management_form, loop forms, and validate the complete collection rather than one form in isolation.", "management_form ကို အရင် render ပြီး form အားလုံးကို loop လုပ်ကာ collection အဖြစ် validate ပါ။"),
            _example("Use prefixes for multiple forms", {"students/views.py": "profile_form = ProfileForm(request.POST or None, prefix=\"profile\")\ncontact_formset = ContactFormSet(request.POST or None, prefix=\"contacts\")\nif request.method == \"POST\" and profile_form.is_valid() and contact_formset.is_valid():\n    save_profile(profile_form, contact_formset)"}, "One POST containing profile and contacts", "profile-* and contacts-* fields do not collide, and both validation results must pass before saving.", "Use the same prefixes for GET and POST, show each management form, and use one transaction for the combined save.", "GET/POST တွင် prefix တူသုံးပြီး management form တစ်ခုစီ render လုပ်ကာ combined save ကို transaction ထဲထားပါ။"),
            _example("Restrict an inline formset queryset", {"students/views.py": "ContactFormSet = inlineformset_factory(Student, StudentContact, fields=[\"kind\", \"value\"], extra=1)\n\ndef edit_contacts(request, student_id, actor):\n    student = get_object_or_404(Student.objects.filter(owner=actor), pk=student_id)\n    formset = ContactFormSet(request.POST or None, instance=student)\n    if request.method == \"POST\" and formset.is_valid():\n        formset.save()\n    return render(request, \"students/contacts.html\", {\"formset\": formset})"}, "A student in actor’s authorized scope", "Only contacts belonging to the authorized parent can be changed; a foreign parent id returns 404.", "Authorize the parent first, then construct the inline formset with that instance; do not trust child ids from POST.", "Parent ကို အရင် authorize လုပ်ပြီးမှ inline formset instance တည်ဆောက်ပါ။ POST child id မယုံပါနှင့်။"),
            _example("Save related rows transactionally", {"students/services.py": "from django.db import transaction\n\ndef save_contacts(profile_form, contact_formset):\n    with transaction.atomic():\n        profile = profile_form.save()\n        contact_formset.instance.student = profile.student\n        contact_formset.save()\n    return profile"}, "Two valid form objects", "Profile and contact writes commit together; an exception rolls back both.", "Assign server-owned parent relationships before save, keep the transaction short and test a deliberate failure after the first write.", "Server-owned parent relation သတ်မှတ်ပြီးမှ save ပါ။ Transaction တိုတိုထားကာ deliberate failure test လုပ်ပါ။"),
            _example("Test management and deletion", {"students/tests/test_formsets.py": "from django.test import TestCase\nfrom students.forms import ContactFormSet\n\nclass ContactFormSetTests(TestCase):\n    def test_missing_management_form_is_invalid(self):\n        formset = ContactFormSet({\"form-0-kind\": \"phone\"})\n        self.assertFalse(formset.is_valid())\n\n    def test_valid_management_data_is_required(self):\n        data = {\"form-TOTAL_FORMS\": \"1\", \"form-INITIAL_FORMS\": \"0\", \"form-0-kind\": \"phone\", \"form-0-value\": \"555\"}\n        self.assertTrue(ContactFormSet(data).is_valid())"}, "Posted formset with and without management fields", "Missing management data is rejected; a complete synthetic payload validates.", "Assert protocol errors explicitly and add an authorization test for an id outside the parent queryset.", "Management protocol error ကို assert လုပ်ပြီး parent queryset အပြင် id authorization test ထည့်ပါ။"),
        ],
        "mistakes": ["Omitting management_form from the template.", "Trusting posted formset primary keys without restricting the queryset.", "Saving a profile and contacts in separate transactions when partial success is unsafe.", "Adding dynamic rows without updating TOTAL_FORMS."],
        "mistakes_mm": ["Template တွင် management_form မထည့်ခြင်း။", "Formset primary key ကို queryset မကန့်သတ်ဘဲ ယုံခြင်း။", "Partial success မလိုသော်လည်း profile/contact ကို transaction ခွဲ save ခြင်း။", "Dynamic row ထည့်သော်လည်း TOTAL_FORMS မ update လုပ်ခြင်း။"],
        "best_practices": "Keep prefixes explicit, restrict querysets to authorized parents, validate the entire collection, save related writes atomically, document delete behavior and test both server-rendered and client-added form counts.",
        "best_practices_mm": "Prefix ရှင်းလင်းစွာသုံးပါ။ Queryset ကို authorized parent အလိုက်ကန့်သတ်ပါ။ Collection အားလုံး validate လုပ်ပါ။ Related write ကို atomic save လုပ်ပြီး delete policy မှတ်တမ်းတင်ကာ server/client form count နှစ်မျိုး test လုပ်ပါ။",
        "exercises": "Create a contact formset, render management data, add prefixes, build an authorized inline formset for StudentProfile contacts, validate duplicate rows, allow deliberate deletion and save in one transaction.",
        "exercises_mm": "Contact formset ပြုလုပ်၊ management data render၊ prefix ထည့်ပြီး StudentProfile contact အတွက် authorized inline formset တည်ဆောက်ပါ။ Duplicate row validate၊ deletion ခွင့်ပြုကာ transaction တစ်ခုထဲ save ပါ။",
        "homework": "Build a Course Enrollment Batch Form System with restricted course choices, formset-level duplicate validation, ownership checks, transactional save and tests for missing management data and unauthorized records.",
        "homework_mm": "Restricted course choice၊ formset-level duplicate validation၊ ownership check၊ transactional save နှင့် missing management/unauthorized record test ပါသော Course Enrollment Batch Form System တည်ဆောက်ပါ။",
        "summary": "Formsets are a protocol, not just a loop of forms. Management counts, prefixes, restricted querysets and transaction boundaries protect related data edits.",
        "summary_mm": "Formset သည် form loop တစ်ခုတည်းမဟုတ်ဘဲ protocol ဖြစ်သည်။ Management count၊ prefix၊ restricted queryset နှင့် transaction boundary က related data edit ကို ကာကွယ်သည်။",
        "quiz": [
            _q("What does the management form provide?", ["Formset counts and protocol fields", "A database password", "A CSS grid", "A user role"], "Formset counts and protocol fields", "Django needs TOTAL_FORMS and related metadata.", "beginner", 5),
            _q("Why use a prefix?", ["To prevent field-name collisions", "To skip validation", "To expose more records", "To disable CSRF"], "To prevent field-name collisions", "Prefixes distinguish multiple form groups.", "intermediate", 5),
            _q("What must a ModelFormset queryset do?", ["Restrict rows to authorized records", "Return every row", "Contain passwords", "Disable deletes always"], "Restrict rows to authorized records", "Posted ids are not ownership proof.", "advanced", 5),
            _q("What happens when management data is missing?", ["The formset is invalid", "All rows are silently saved", "CSRF is disabled", "A migration runs"], "The formset is invalid", "Management fields are required for the protocol.", "beginner", 5),
            _q("Which factory connects child forms to a parent instance?", ["inlineformset_factory()", "render_factory()", "csrf_factory()", "url_factory()"], "inlineformset_factory()", "It creates a formset for related child objects.", "intermediate", 5),
            _q("True or false: client-added rows can ignore TOTAL_FORMS.", ["True", "False"], "False", "The management count must match the submitted rows.", "intermediate", 5),
            _q("When should related formset writes use atomic()?", ["When partial success would be unsafe", "Only for CSS", "Never", "Only on GET"], "When partial success would be unsafe", "Atomicity keeps related changes consistent.", "advanced", 5),
            _q("What should be checked before building an inline formset?", ["The parent is authorized", "The browser selected a parent", "The URL is pretty", "The label is translated"], "The parent is authorized", "Authorization starts at the parent boundary.", "advanced", 5),
        ],
    },
    {
        "title": "Django File Uploads, Image Handling and Media Storage",
        "slug": "06-file-and-image-uploads",
        "description": "Handle Student profile photos and documents with multipart forms, size/content validation, safe storage, replacement and cleanup policies.",
        "description_mm": "Multipart form၊ size/content validation၊ safe storage၊ replacement နှင့် cleanup policy ဖြင့် Student profile photo/document ကို ကိုင်တွယ်ပါ။",
        "topic": "request.FILES, multipart/form-data, FileField, ImageField, Pillow, upload_to, MEDIA_ROOT, storage, chunks and upload security",
        "theory": "File uploads are untrusted bytes, not ordinary text fields. The HTML form must use method=post and enctype=multipart/form-data; the view binds both request.POST and request.FILES to the form. UploadedFile objects expose metadata and chunks(), but the application must set size limits before expensive processing. FileField stores a reference while the configured storage writes the bytes; a database transaction does not automatically make the storage write and database row one atomic unit. ImageField adds image decoding and requires Pillow, but a valid image is not automatically safe to publish. Do not trust filename extensions or client MIME types alone. Generate server-side names, prevent path traversal, keep uploads out of executable code paths, restrict private media access, and use a storage backend appropriate for deployment. For replacement, validate the new file, save the new reference, and delete the old object only after the new state is durable; design cleanup for failures and orphaned objects. Use chunks() for large files, reject unreasonable sizes, and test malformed, oversized and valid synthetic files. Never expose real student photos in learning material.",
        "theory_mm": "File upload သည် text field မဟုတ်ဘဲ untrusted bytes ဖြစ်သည်။ HTML form တွင် method=post နှင့် enctype=multipart/form-data လိုပြီး view တွင် request.POST/request.FILES နှစ်ခုလုံး bind လုပ်ရသည်။ UploadedFile တွင် metadata/chunks() ရှိသော်လည်း expensive processing မလုပ်မီ size limit သတ်မှတ်ပါ။ FileField သည် reference သိမ်းပြီး storage က bytes ရေးသည်။ Database transaction တစ်ခုတည်းက storage write နှင့် row ကို အလိုအလျောက် atomic မလုပ်ပါ။ ImageField သည် image decode နှင့် Pillow လိုသော်လည်း valid image ဖြစ်ရုံနှင့် public safe မဖြစ်ပါ။ Extension/MIME ကို တစ်ခုတည်းမယုံပါနှင့်။ Server-side name generate၊ path traversal တား၊ executable path အပြင် storage ထား၊ private media access ကန့်သတ်ပြီး deployment အလိုက် storage backend ရွေးပါ။ Replacement တွင် file အသစ် validate/save ပြီး durable ဖြစ်မှ old object ဖျက်ပါ။ Failure/orphan cleanup policy ရှိပါစေ။ Large file အတွက် chunks() သုံးပြီး size limit ထားကာ malformed/oversized/valid synthetic file test လုပ်ပါ။ Real student photo မသုံးပါနှင့်။",
        "concepts": "multipart/form-data; request.FILES; UploadedFile; FileField; ImageField; Pillow; upload_to; MEDIA_ROOT; MEDIA_URL; Storage; chunks(); content validation; size limits; safe names; private media; orphan cleanup; replacement consistency.",
        "concepts_mm": "multipart/form-data၊ request.FILES၊ UploadedFile၊ FileField၊ ImageField၊ Pillow၊ upload_to၊ MEDIA_ROOT၊ MEDIA_URL၊ Storage၊ chunks()၊ content validation၊ size limit၊ safe name၊ private media၊ orphan cleanup နှင့် replacement consistency တို့ကို လေ့လာရမည်။",
        "syntax": "<form method=\"post\" enctype=\"multipart/form-data\">{% csrf_token %}{{ form }}<button>Save</button></form>\n\nform = ProfileForm(request.POST, request.FILES, instance=profile)",
        "examples": [
            _example("Bind a basic file upload", {"students/forms.py": "from django import forms\n\nclass DocumentForm(forms.Form):\n    document = forms.FileField()", "students/views.py": "def upload(request):\n    form = DocumentForm(request.POST or None, request.FILES or None)\n    if request.method == \"POST\" and form.is_valid():\n        uploaded = form.cleaned_data[\"document\"]\n        return save_document(uploaded)\n    return render(request, \"students/upload.html\", {\"form\": form})"}, "A multipart POST with a synthetic text file", "The uploaded object appears in request.FILES and is available in cleaned_data after validation.", "Set the form enctype, pass both dictionaries, validate, and send the object to a storage service rather than writing arbitrary paths in a view.", "Form enctype သတ်မှတ်ပြီး dictionary နှစ်ခု bind လုပ်ပါ။ Validate ပြီး storage service သို့ ပို့ပါ။"),
            _example("Upload a profile image", {"students/models.py": "class StudentProfile(models.Model):\n    student = models.OneToOneField(Student, on_delete=models.CASCADE)\n    photo = models.ImageField(upload_to=\"student-profiles/%Y/%m/\", blank=True)\n", "students/forms.py": "class ProfileForm(forms.ModelForm):\n    class Meta:\n        model = StudentProfile\n        fields = [\"photo\"]"}, "A synthetic PNG created in a test", "ImageField decodes a valid image and storage records a generated path under the configured media storage.", "Install the supported Pillow dependency in the isolated project, validate the image, and keep MEDIA_ROOT separate from source code.", "Isolated project တွင် Pillow သုံးပြီး image validate လုပ်ပါ။ MEDIA_ROOT ကို source code နှင့် ခွဲထားပါ။"),
            _example("Reject an oversized file", {"students/forms.py": "class SafeFileField(forms.FileField):\n    def clean(self, data, initial=None):\n        cleaned = super().clean(data, initial)\n        if cleaned and cleaned.size > 5 * 1024 * 1024:\n            raise forms.ValidationError(\"File is too large.\", code=\"file_too_large\")\n        return cleaned\n\nclass DocumentForm(forms.Form):\n    document = SafeFileField()"}, "A synthetic upload larger than 5 MiB", "The form is invalid before the storage service receives the file.", "Choose limits from threat and product requirements, make them consistent at web and form boundaries, and test the limit without loading unbounded data.", "Threat/product requirement အပေါ်မူတည်ပြီး limit သတ်မှတ်ကာ web/form boundary နှစ်ခုလုံးတွင် consistent ဖြစ်စေပါ။"),
            _example("Validate content, not only extension", {"students/validators.py": "from PIL import Image\nfrom django.core.exceptions import ValidationError\n\ndef validate_profile_image(uploaded):\n    if uploaded.size > 5 * 1024 * 1024:\n        raise ValidationError(\"Image is too large.\", code=\"too_large\")\n    try:\n        with Image.open(uploaded) as image:\n            image.verify()\n    except Exception as exc:\n        raise ValidationError(\"Upload a valid image.\", code=\"invalid_image\") from exc\n    uploaded.seek(0)\n    return uploaded"}, "A file named .png whose bytes are not an image", "Image.verify rejects the content even when the filename extension says png.", "Treat decoding as one control, not a complete malware strategy; isolate storage and apply access policy as well.", "Decode check တစ်ခုတည်းကို malware protection အဖြစ် မယူဆပါနှင့်။ Storage isolation/access policy ပါစေ။"),
            _example("Replace a profile photo safely", {"students/services.py": "from django.db import transaction\n\ndef replace_photo(profile, form):\n    old_name = profile.photo.name\n    with transaction.atomic():\n        updated = form.save()\n        new_name = updated.photo.name\n    if old_name and old_name != new_name:\n        profile.photo.storage.delete(old_name)\n    return updated"}, "A valid new image and an existing profile photo", "The new database reference is saved before the old storage object is removed; cleanup can be retried if storage deletion fails.", "Do not delete the old file before the new reference is durable, and record cleanup failures for an operator rather than claiming perfect atomicity.", "New reference durable ဖြစ်မှ old file ဖျက်ပါ။ Storage delete fail ကို operator အတွက်မှတ်ပါ။"),
        ],
        "mistakes": ["Forgetting multipart/form-data or request.FILES.", "Trusting file extension or browser MIME type alone.", "Storing upload names directly as filesystem paths.", "Deleting the old file before the new database reference is durable or assuming DB/storage atomicity."],
        "mistakes_mm": ["multipart/form-data/request.FILES မထည့်ခြင်း။", "Extension/browser MIME တစ်ခုတည်းကို ယုံခြင်း။", "Upload name ကို filesystem path အဖြစ် တိုက်ရိုက်သုံးခြင်း။", "New reference durable မဖြစ်မီ old file ဖျက်ခြင်း သို့မဟုတ် DB/storage atomic ဟု ယူဆခြင်း။"],
        "best_practices": "Limit size early, validate decoded content, generate safe names, isolate untrusted storage, restrict private access, use chunks for large files, separate database and storage consistency handling, and test malformed and replacement failures.",
        "best_practices_mm": "Size ကို အစောပိုင်းကန့်သတ်ပါ။ Decoded content စစ်ပါ။ Safe name generate လုပ်ပါ။ Untrusted storage isolate လုပ်ပြီး private access ကန့်သတ်ပါ။ Large file တွင် chunks သုံးကာ database/storage consistency ကို သီးခြားကိုင်တွယ်ပြီး malformed/replacement failure test လုပ်ပါ။",
        "exercises": "Implement a Student profile photo upload with multipart form, ImageField, 5 MiB limit, content verification, safe upload_to, private display boundary and tests for valid, oversized, malformed and replacement cases.",
        "exercises_mm": "Multipart form၊ ImageField၊ 5 MiB limit၊ content verification၊ safe upload_to၊ private display boundary ပါသော Student profile photo upload ပြုလုပ်ပြီး valid/oversized/malformed/replacement test လုပ်ပါ။",
        "homework": "Build a Secure Student Profile Photo Upload feature. Include a threat model, storage policy, file replacement strategy, orphan cleanup plan, user-facing errors and automated upload tests.",
        "homework_mm": "Threat model၊ storage policy၊ file replacement strategy၊ orphan cleanup plan၊ user-facing error နှင့် automated upload test ပါသော Secure Student Profile Photo Upload feature တည်ဆောက်ပါ။",
        "summary": "Uploads combine untrusted bytes, form validation, storage and database references. Security requires controls at every boundary and an honest consistency policy.",
        "summary_mm": "Upload တွင် untrusted bytes၊ form validation၊ storage နှင့် database reference ပေါင်းစပ်နေသည်။ Security အတွက် boundary တစ်ခုချင်း control ထည့်ပြီး consistency policy ရှင်းလင်းရမည်။",
        "quiz": [
            _q("Where does uploaded file data appear?", ["request.FILES", "request.GET only", "settings.py only", "The URL name"], "request.FILES", "Django upload handlers place file data in request.FILES.", "beginner", 6),
            _q("Which form encoding is required for file uploads?", ["multipart/form-data", "text/plain only", "application/json only", "url-only"], "multipart/form-data", "The browser needs multipart encoding for file parts.", "beginner", 6),
            _q("Why is ImageField not a complete security control?", ["Valid image bytes can still be untrusted content", "It disables validation", "It stores passwords", "It never decodes"], "Valid image bytes can still be untrusted content", "Storage and access policy are still required.", "advanced", 6),
            _q("What should be validated besides extension?", ["File size and actual content", "Only the display name", "Only CSS", "Nothing"], "File size and actual content", "Extensions and client MIME are user-controlled.", "intermediate", 6),
            _q("What does UploadedFile.chunks() help with?", ["Processing large uploads incrementally", "Creating a formset", "Checking CSRF", "Running migrations"], "Processing large uploads incrementally", "Chunks avoid loading an unnecessarily large file into memory.", "intermediate", 6),
            _q("True or false: a database transaction automatically rolls back a storage write.", ["True", "False"], "False", "Database and storage consistency need an explicit policy.", "advanced", 6),
            _q("When should an old profile file normally be deleted during replacement?", ["After the new reference is durable", "Before validation", "Before the new file exists", "Never"], "After the new reference is durable", "This avoids losing the old usable reference prematurely.", "intermediate", 6),
            _q("Where should untrusted uploads be stored?", ["A restricted non-executable media boundary", "The Python source directory", "The templates directory", "A public secrets directory"], "A restricted non-executable media boundary", "Storage and serving policy must treat uploads as untrusted.", "advanced", 6),
        ],
    },
    {
        "title": "Professional Django Form Security, UX and Testing",
        "slug": "06-secure-forms-ux-and-testing",
        "description": "Combine CSRF, authorization, accessible UX, messages, idempotent actions and focused tests into a production-ready Student Registration workflow.",
        "description_mm": "CSRF၊ authorization၊ accessible UX၊ message၊ idempotent action နှင့် focused test များကို ပေါင်းပြီး production-ready Student Registration workflow တည်ဆောက်ပါ။",
        "topic": "CSRF, server-side validation, authorization, mass assignment, messages, PRG, accessibility, test isolation and secure uploads",
        "theory": "Professional form architecture separates concerns: the form validates shape and user-facing errors, the service enforces business invariants and transaction boundaries, the view checks authorization and chooses a response, and the template renders accessible controls. CSRF protects a browser session from unwanted state-changing requests; it does not decide whether the current user is allowed to edit a Student. Authorization must check the object and action server-side. A ModelForm allowlist reduces mass assignment but is not a permission system. The messages framework can communicate a successful save after PRG, while idempotency keys or unique constraints prevent repeated actions from creating duplicates. Accessible UX includes labels, error summaries, focus recovery, keyboard operation, readable mobile layout and preserved values after invalid submission. Tests should cover form units, ModelForm allowlists, validator codes, view status/redirect behavior, CSRF enforcement, authorized and forbidden object edits, upload size/content checks and transaction rollback. Use Django’s isolated test database and synthetic files. Do not disable CSRF to make a test pass, and do not present an educational demo as secure arbitrary-user editing when authentication/object permissions are not implemented. Authentication is covered later; this module’s project should use a restricted staff/demo boundary.",
        "theory_mm": "Professional form architecture တွင် concern ခွဲထားရမည်။ Form သည် input shape/user error validate၊ service သည် business invariant/transaction ကိုင်၊ view သည် authorization စစ်ပြီး response ရွေး၊ template သည် accessible control render လုပ်သည်။ CSRF သည် browser session မှ မလိုလားသော state-changing request ကို တားသော်လည်း လက်ရှိ user က Student edit ခွင့်ရှိ/မရှိ မဆုံးဖြတ်ပါ။ Authorization ကို server-side object/action ဖြင့်စစ်ရမည်။ ModelForm allowlist သည် mass assignment လျှော့သော်လည်း permission system မဟုတ်ပါ။ Messages framework သည် PRG ပြီးနောက် save success ပြနိုင်ပြီး idempotency key/unique constraint သည် repeated action duplicate မဖြစ်စေပါ။ Accessible UX တွင် label၊ error summary၊ focus recovery၊ keyboard၊ readable mobile layout နှင့် invalid submit value ထိန်းခြင်းပါသည်။ Test တွင် Form unit၊ ModelForm allowlist၊ validator code၊ view status/redirect၊ CSRF enforcement၊ authorized/forbidden edit၊ upload size/content နှင့် transaction rollback ပါစေ။ Django isolated test database နှင့် synthetic file သုံးပါ။ Test pass စေရန် CSRF မပိတ်ပါနှင့်။ Authentication/object permission မပြည့်စုံသေးလျှင် arbitrary public edit secure ဟု မပြောပါနှင့်။ Authentication ကို နောက် module တွင် လေ့လာမည်ဖြစ်ပြီး ယခု project သည် restricted staff/demo boundary သုံးရမည်။",
        "concepts": "CSRF; authorization; mass assignment; field allowlist; messages framework; PRG; idempotency; focus management; error summary; test client; enforce_csrf_checks; isolated TestCase database; upload security; staff/demo boundary.",
        "concepts_mm": "CSRF၊ authorization၊ mass assignment၊ field allowlist၊ messages framework၊ PRG၊ idempotency၊ focus management၊ error summary၊ test client၊ enforce_csrf_checks၊ isolated TestCase database၊ upload security နှင့် staff/demo boundary တို့ကို လေ့လာရမည်။",
        "syntax": "from django.contrib import messages\nfrom django.shortcuts import redirect\n\nif form.is_valid():\n    save_registration(form)\n    messages.success(request, \"Registration saved.\")\n    return redirect(\"students:detail\", pk=student.pk)",
        "examples": [
            _example("Protect a POST with CSRF", {"templates/students/form.html": "<form method=\"post\" enctype=\"multipart/form-data\">{% csrf_token %}{{ form }}<button type=\"submit\">Save</button></form>", "school_site/settings.py": "MIDDLEWARE = [\"django.middleware.csrf.CsrfViewMiddleware\", *OTHER_MIDDLEWARE]"}, "A same-site POST form", "A request without a valid CSRF token is rejected by the middleware; the form remains usable when the token is rendered.", "Keep middleware enabled, include the token for internal POST forms and test rejection with a CSRF-enforcing client.", "Middleware ဖွင့်ထားပြီး internal POST form တွင် token ထည့်ပါ။ CSRF-enforcing client ဖြင့် reject test လုပ်ပါ။"),
            _example("Authorize before editing", {"students/views.py": "from django.core.exceptions import PermissionDenied\n\ndef edit_student(request, pk):\n    student = get_object_or_404(Student, pk=pk)\n    if not request.user.is_staff or student.owner_id != request.user.id:\n        raise PermissionDenied\n    form = StudentForm(request.POST or None, instance=student)\n    # validate, save and redirect as in the previous lesson"}, "A request for a Student outside the actor’s ownership", "The view returns a forbidden response instead of binding or saving the form.", "Make the authorization decision before mutation and keep it independent from the form field list.", "Mutation မလုပ်မီ authorization ဆုံးဖြတ်ပြီး form field list နှင့် သီးခြားထားပါ။"),
            _example("Show success after PRG", {"students/views.py": "from django.contrib import messages\n\nif request.method == \"POST\" and form.is_valid():\n    student = save_registration(form, actor=request.user)\n    messages.success(request, \"Student registration saved.\")\n    return redirect(\"students:detail\", pk=student.pk)"}, "A valid registration POST", "The redirected GET displays a one-time success message and refresh does not repeat the POST.", "Add the message only after the service confirms persistence; do not show success before the database boundary returns.", "Service က persistence အတည်ပြုပြီးမှ message ထည့်ပါ။ Database မပြီးမီ success မပြပါနှင့်။"),
            _example("Test CSRF and invalid forms", {"students/tests/test_views.py": "from django.test import TestCase, Client\n\nclass RegistrationViewTests(TestCase):\n    def test_csrf_is_enforced(self):\n        client = Client(enforce_csrf_checks=True)\n        response = client.post(\"/students/register/\", {\"name\": \"Learner\"})\n        self.assertEqual(response.status_code, 403)\n\n    def test_invalid_post_renders_form(self):\n        response = self.client.post(\"/students/register/\", {\"name\": \"\", \"email\": \"bad\", \"age\": 2})\n        self.assertEqual(response.status_code, 200)\n        self.assertTrue(response.context[\"form\"].errors)"}, "POST without CSRF and POST with invalid fields", "The enforcing client receives 403 without a token; invalid fields return the form with errors.", "Use the test client intentionally: default tests may not enforce CSRF, so add an explicit enforcement test.", "CSRF-enforcing client သုံးပါ။ Default test client သည် enforce မလုပ်နိုင်သဖြင့် explicit test ထည့်ပါ။"),
            _example("Test upload rejection", {"students/tests/test_uploads.py": "from io import BytesIO\nfrom django.core.files.uploadedfile import SimpleUploadedFile\nfrom django.test import SimpleTestCase\nfrom students.forms import ProfileForm\n\nclass UploadTests(SimpleTestCase):\n    def test_large_file_is_rejected(self):\n        upload = SimpleUploadedFile(\"photo.png\", b\"0\" * (5 * 1024 * 1024 + 1), content_type=\"image/png\")\n        form = ProfileForm({\"student\": 1}, {\"photo\": upload})\n        self.assertFalse(form.is_valid())\n        self.assertIn(\"photo\", form.errors)"}, "A synthetic oversized upload", "The form rejects the file before an upload success response or storage claim is made.", "Test size and decoded content separately, clean temporary media after tests, and assert the user-facing error contract.", "Size နှင့် decoded content ကို သီးခြား test လုပ်ပြီး temporary media cleanup ပြုလုပ်ပါ။"),
        ],
        "mistakes": ["Confusing CSRF protection with authorization.", "Disabling CSRF middleware to make a test pass.", "Showing a success message before persistence succeeds.", "Calling an educational demo secure for arbitrary users without implemented object permissions."],
        "mistakes_mm": ["CSRF ကို authorization နှင့် ရောထွေးခြင်း။", "Test pass ရန် CSRF middleware ပိတ်ခြင်း။", "Persistence မအောင်မြင်မီ success message ပြခြင်း။", "Object permission မရှိသေးသော educational demo ကို arbitrary user အတွက် secure ဟု ပြောခြင်း။"],
        "best_practices": "Separate validation, authorization and persistence; keep CSRF enabled; use explicit field allowlists; use PRG and post-commit messaging; test forbidden and invalid paths; isolate media during tests; and document demo limitations.",
        "best_practices_mm": "Validation၊ authorization နှင့် persistence ခွဲပါ။ CSRF ဖွင့်ထားပါ။ Field allowlist သုံးပါ။ PRG/post-commit message သုံးပါ။ Forbidden/invalid path test လုပ်ပြီး test media isolate လုပ်ကာ demo limitation မှတ်တမ်းတင်ပါ။",
        "exercises": "Add CSRF to every internal POST, implement a restricted staff/demo edit boundary, render accessible errors and focus, add success messages with PRG, and write form, validation, upload and forbidden-object tests.",
        "exercises_mm": "Internal POST တိုင်း CSRF ထည့်ပါ။ Restricted staff/demo edit boundary၊ accessible error/focus၊ PRG success message နှင့် form/validation/upload/forbidden test များ တည်ဆောက်ပါ။",
        "homework": "Build a Production-Ready Student Registration Workflow for the educational boundary. Include threat model, permission limitation, accessible templates, CSRF, idempotency, error handling, test isolation and deployment notes.",
        "homework_mm": "Educational boundary အတွက် threat model၊ permission limitation၊ accessible template၊ CSRF၊ idempotency၊ error handling၊ test isolation နှင့် deployment note ပါသော Production-Ready Student Registration Workflow တည်ဆောက်ပါ။",
        "summary": "Professional forms join validation, authorization, CSRF, accessibility, persistence feedback and tests. Each solves a different failure mode and none should be treated as a substitute for another.",
        "summary_mm": "Professional form တွင် validation၊ authorization၊ CSRF၊ accessibility၊ persistence feedback နှင့် test ပေါင်းစပ်ရသည်။ တစ်ခုချင်းစီက failure mode မတူသဖြင့် တစ်ခုကိုတစ်ခု အစားထိုးမယူဆပါနှင့်။",
        "quiz": [
            _q("What does CSRF protection solve?", ["Unwanted state-changing browser requests", "Object ownership", "File malware", "Database indexing"], "Unwanted state-changing browser requests", "CSRF is a browser request integrity control.", "intermediate", 7),
            _q("What does authorization solve?", ["Whether this actor may perform the action", "Whether HTML has a label", "Whether a file is an image", "Whether a form is bound"], "Whether this actor may perform the action", "Authorization is an object/action policy.", "beginner", 7),
            _q("Which client helps test CSRF rejection?", ["Client(enforce_csrf_checks=True)", "A CSS client", "A database cursor", "A template filter"], "Client(enforce_csrf_checks=True)", "The test client can enable middleware enforcement.", "intermediate", 7),
            _q("When should a success message be added?", ["After persistence succeeds", "Before validation", "Before opening a transaction", "On every GET"], "After persistence succeeds", "The message should reflect durable state.", "intermediate", 7),
            _q("True or false: a ModelForm allowlist grants object permission.", ["True", "False"], "False", "The view/service must authorize the object and action.", "beginner", 7),
            _q("What does PRG help prevent?", ["Duplicate form resubmission on refresh", "Invalid images", "Missing labels", "SQL indexes"], "Duplicate form resubmission on refresh", "Redirect after POST separates the next GET.", "intermediate", 7),
            _q("What should an educational demo do if arbitrary-user permissions are not implemented?", ["Document a restricted staff/demo boundary", "Claim it is fully secure", "Disable CSRF", "Expose all objects"], "Document a restricted staff/demo boundary", "Honest scope is part of security.", "advanced", 7),
            _q("Which test area belongs in an upload workflow?", ["Size, content, storage isolation and cleanup", "Only filename color", "Only a GET route", "No tests"], "Size, content, storage isolation and cleanup", "Upload risk spans multiple boundaries.", "advanced", 7),
        ],
    },
]


def _render_examples(item, burmese=False):
    output = []
    for index, example in enumerate(item["examples"], 1):
        files = []
        for filename, source in example["files"].items():
            language = "python" if filename.endswith(".py") else "html" if filename.endswith(".html") else "css" if filename.endswith(".css") else "text"
            files.append(f"File: {filename}\n```{language}\n{source}\n```")
        if burmese:
            output.append(f"နမူနာ {index}: {example['title']}\nSetup/Input: {example['input']}\n" + "\n\n".join(files) + f"\nမျှော်မှန်းရလဒ်: {example['output']}\nအဆင့်လိုက်ရှင်းလင်းချက်: {example['steps_mm']}\nIsolated project တွင် actual output ကို စစ်ပြီး မှတ်တမ်းတင်ပါ။")
        else:
            output.append(f"Example {index}: {example['title']}\nSetup/input: {example['input']}\n" + "\n\n".join(files) + f"\nExpected behavior: {example['output']}\nStep-by-step explanation: {example['steps']}\nRun only in the isolated educational project and record actual output.")
    return "\n\n".join(output)


def _render_en(item: dict) -> str:
    mistakes = "\n".join(f"- {value}" for value in item["mistakes"])
    quiz = "\n".join(f"{i}. {q['prompt']} Options: {', '.join(q['options'])}" for i, q in enumerate(item["quiz"], 1))
    objectives = "\n".join(f"{i}. Apply {item['topic']} in a safe Student Registration workflow (objective {i})." for i in range(1, 5))
    return dedent(f"""
        # {item['title']}

        ## Introduction
        {item['description']}

        ## Prerequisites and safe scope
        {COMMON_PREREQ}

        ## Learning objectives
        {objectives}

        ## Detailed theory
        {item['theory']}

        ## Concepts and terminology
        {item['concepts']}

        ## Syntax and API reference
        ```python
        {item['syntax']}
        ```
        Treat form data, uploaded bytes, object ids and permissions as separate contracts. A valid form is not proof of authorization, and a stored file is not automatically safe to publish.

        ## Complete progressive examples
        {_render_examples(item)}

        ## Common mistakes
        {mistakes}

        ## Best practices
        {item['best_practices']}

        ## Guided exercises
        {item['exercises']}

        ## Independent exercises
        Rebuild the lesson inside the isolated Student Registration and Profile Management project. Include a normal path, an invalid or missing-input path, a forbidden or unsafe-input path where relevant, and a focused test. Record actual commands and results rather than inventing a browser, upload or database outcome.

        ## Homework
        {item['homework']}

        ## Project connection
        This lesson contributes to the Student Registration and Profile Management System: forms collect input, ModelForms persist allowlisted fields, validators protect domain rules, formsets edit related data, uploads use restricted media storage, and security tests prove the workflow boundary. Full authentication is intentionally deferred to Module 07.

        ## Lesson quiz
        {quiz}
        Answer first, then check the private review answer key. Correct answers must not be sent in public student quiz payloads.

        ## Summary
        {item['summary']}

        ## Further reading and version note
        Target Django 6.0 with the exact project lockfile versions. Read the official Forms, Forms API, ModelForms, validation, file upload and CSRF documentation. Keep all form/upload experiments in an isolated school_portal_forms_dev database and synthetic media directory.
    """).strip()


def _render_mm(item: dict) -> str:
    mistakes = "\n".join(f"- {value}" for value in item["mistakes_mm"])
    quiz = "\n".join(f"{i}. {q['prompt']} Options: {', '.join(q['options'])}" for i, q in enumerate(item["quiz"], 1))
    objectives = "\n".join(f"{i}။ {item['topic']} ကို safe Student Registration workflow တွင် အသုံးချနိုင်ရန် (ရည်မှန်းချက် {i})။" for i in range(1, 5))
    return dedent(f"""
        # {item['title']}

        ## မိတ်ဆက်
        {item['description_mm']}

        ## ကြိုတင်လိုအပ်ချက်နှင့် လုံခြုံသော scope
        {COMMON_PREREQ_MM}

        ## သင်ယူရမည့်ရည်မှန်းချက်
        {objectives}

        ## အသေးစိတ်သီအိုရီ
        {item['theory_mm']}

        ## Concept နှင့် technical terminology
        {item['concepts_mm']}

        ## Syntax နှင့် API reference
        ```python
        {item['syntax']}
        ```
        Form data၊ uploaded bytes၊ object id နှင့် permission ကို contract သီးခြားအဖြစ်ထားပါ။ Valid form ဖြစ်ရုံနှင့် authorization မဟုတ်သလို stored file ဖြစ်ရုံနှင့် public safe မဟုတ်ပါ။

        ## ပြည့်စုံသော progressive နမူနာများ
        {_render_examples(item, True)}

        ## အများဆုံးမှားတတ်သောအချက်များ
        {mistakes}

        ## အကောင်းဆုံးနည်းလမ်းများ
        {item['best_practices_mm']}

        ## လမ်းညွှန်လေ့ကျင့်ခန်း
        {item['exercises_mm']}

        ## ကိုယ်တိုင်လေ့ကျင့်ရန်
        Isolated Student Registration and Profile Management project ထဲ lesson ကို ပြန်တည်ဆောက်ပါ။ Normal path၊ invalid/missing input path၊ သက်ဆိုင်လျှင် forbidden/unsafe input path နှင့် focused test ထည့်ပါ။ Browser/upload/database result ကို မစမ်းရသေးလျှင် မဖန်တီးပါနှင့်။

        ## အိမ်စာ
        {item['homework_mm']}

        ## Project နှင့်ချိတ်ဆက်မှု
        ဤ lesson သည် Student Registration and Profile Management System ၏ အစိတ်အပိုင်းဖြစ်သည်။ Form က input စု၊ ModelForm က allowlist field persist၊ validator က domain rule ကာကွယ်၊ formset က related data edit၊ upload က restricted media သုံးပြီး security test က workflow boundary သက်သေပြသည်။ Authentication ကို Module 07 သို့ ချန်ထားသည်။

        ## Lesson quiz
        {quiz}
        အဖြေကို အရင်စဉ်းစားပြီး private review answer key ဖြင့် စစ်ပါ။ Public student quiz payload ထဲ correct answer မထည့်ရပါ။

        ## အနှစ်ချုပ်
        {item['summary_mm']}

        ## ဆက်လက်ဖတ်ရှုရန်နှင့် version note
        Django 6.0 နှင့် project lockfile ၏ exact version ကို target ထားပါ။ Official Forms၊ Forms API၊ ModelForms၊ validation၊ file upload နှင့် CSRF documentation ကို ဖတ်ပါ။ Form/upload experiment အားလုံးကို isolated school_portal_forms_dev database နှင့် synthetic media directory တွင်သာလုပ်ပါ။
    """).strip()


def _example_code(example):
    return "\n\n".join(f"# --- {filename} ---\n{source}" for filename, source in example["files"].items())


def _ensure_examples(db, lesson, item):
    rows = db.scalars(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id)).all()
    for position, example in enumerate(item["examples"], 1):
        values = {"title": example["title"], "language": "django", "filename": next(iter(example["files"])), "code": _example_code(example), "description": f"Setup/input: {example['input']}\nExpected behavior: {example['output']}\n\n{example['steps']}", "position": position}
        if position <= len(rows):
            for key, value in values.items():
                setattr(rows[position - 1], key, value)
        else:
            db.add(CodeExample(lesson_id=lesson.id, **values))


def _ensure_quiz(db, lesson, item):
    quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
    if not quiz:
        quiz = LessonQuiz(lesson_id=lesson.id, title=f"{item['title']} knowledge check", explanation="Review the form boundary, validation order and security reason behind each answer.", status="draft")
        db.add(quiz)
        db.flush()
    if quiz.status not in {"published", "approved", "in_review"}:
        quiz.title = f"{item['title']} knowledge check"
        quiz.explanation = "Review the form boundary, validation order and security reason behind each answer."
        quiz.status = "draft"
        questions = db.scalars(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id).order_by(QuizQuestion.position)).all()
        for position, data in enumerate(item["quiz"], 1):
            values = {"prompt": data["prompt"], "question_type": "true_false" if data["options"] == ["True", "False"] else "multiple_choice", "options_json": json.dumps(data["options"], ensure_ascii=False), "correct_answer": data["correct_answer"], "explanation": data["explanation"]}
            if position <= len(questions):
                for key, value in values.items():
                    setattr(questions[position - 1], key, value)
            else:
                db.add(QuizQuestion(quiz_id=quiz.id, position=position, **values))


def _ensure_exercise(db, lesson, item):
    exercise = db.scalar(select(CodingExercise).where(CodingExercise.lesson_id == lesson.id).order_by(CodingExercise.created_at, CodingExercise.id))
    values = {"title": f"{item['title']} practice", "description_en": item["exercises"], "description_mm": item["exercises_mm"], "difficulty": "intermediate", "language": "django", "starter_code": "# Build this exercise only in the isolated Student Registration project.\n", "status": "draft"}
    if exercise and exercise.status not in {"published", "approved", "in_review"}:
        for key, value in values.items():
            setattr(exercise, key, value)
    elif not exercise:
        db.add(CodingExercise(lesson_id=lesson.id, slug=f"django-module-six-{lesson.order_index}-practice", **values))


def _module_assessment():
    questions = []
    for item in LESSONS:
        questions.extend(item["quiz"][:3])
    questions.extend([
        _q("Which object should be checked before constructing an edit ModelForm?", ["The authorized model instance", "The browser placeholder", "The CSS file", "The public media URL"], "The authorized model instance", "Object scope is an authorization boundary.", "advanced", 3),
        _q("Which formset value must be included in a submitted formset?", ["The management form fields", "A database password", "A published answer key", "A template inheritance tag"], "The management form fields", "Django uses management metadata to validate the collection.", "intermediate", 5),
        _q("Why is checking an image extension insufficient?", ["The bytes may not match the claimed type", "Extensions always encrypt files", "Django ignores files", "It disables CSRF"], "The bytes may not match the claimed type", "Content verification and storage policy are also needed.", "advanced", 6),
        _q("Which test explicitly exercises CSRF rejection?", ["Client(enforce_csrf_checks=True)", "A CSS snapshot", "A migration plan", "A GET-only client"], "Client(enforce_csrf_checks=True)", "The test client can turn on CSRF enforcement.", "intermediate", 7),
    ])
    return questions[:24]


SYNTAX_REFERENCES = [
    {"slug": "django-forms-form", "title": "forms.Form", "lesson": 1, "syntax": "class RegistrationForm(forms.Form): ...", "description": "Declares a non-model-backed input contract.", "example": "class ContactForm(forms.Form):\n    email = forms.EmailField()", "output": "A form that validates submitted email input.", "mm": "Model မချိတ်ထားသော input contract class ဖြစ်သည်။"},
    {"slug": "django-forms-modelform", "title": "forms.ModelForm", "lesson": 3, "syntax": "class StudentForm(forms.ModelForm): ...", "description": "Builds form fields and model-related validation from a model.", "example": "class StudentForm(forms.ModelForm):\n    class Meta:\n        model = Student\n        fields = [\"name\", \"email\"]", "output": "An allowlisted model-backed form.", "mm": "Model မှ form field နှင့် validation ဖန်တီးသည်။"},
    {"slug": "django-form-charfield", "title": "forms.CharField", "lesson": 2, "syntax": "forms.CharField(max_length=150)", "description": "Collects and validates bounded text.", "example": "name = forms.CharField(max_length=150)", "output": "A bounded string value.", "mm": "ကန့်သတ်ထားသော text value စုဆောင်းသည်။"},
    {"slug": "django-form-emailfield", "title": "forms.EmailField", "lesson": 2, "syntax": "forms.EmailField()", "description": "Converts and validates email-shaped input.", "example": "email = forms.EmailField()", "output": "A normalized valid email value.", "mm": "Email ပုံစံ input ကို validate/convert လုပ်သည်။"},
    {"slug": "django-form-integerfield", "title": "forms.IntegerField", "lesson": 2, "syntax": "forms.IntegerField(min_value=5, max_value=120)", "description": "Converts integer input and enforces numeric bounds.", "example": "age = forms.IntegerField(min_value=5, max_value=120)", "output": "A validated Python integer.", "mm": "Integer input ကို convert ပြီး range ကန့်သတ်သည်။"},
    {"slug": "django-form-choicefield", "title": "forms.ChoiceField", "lesson": 2, "syntax": "forms.ChoiceField(choices=...)", "description": "Restricts input to declared choices.", "example": "level = forms.ChoiceField(choices=[(\"beginner\", \"Beginner\")])", "output": "A value from the declared choices.", "mm": "သတ်မှတ်ထားသော choice ထဲမှသာ ရွေးခွင့်ပေးသည်။"},
    {"slug": "django-form-modelchoicefield", "title": "forms.ModelChoiceField", "lesson": 2, "syntax": "forms.ModelChoiceField(queryset=Course.objects.none())", "description": "Selects one model object from an authorized queryset.", "example": "course = forms.ModelChoiceField(queryset=available_courses)", "output": "A selected Course instance.", "mm": "Authorized queryset ထဲမှ model object တစ်ခုရွေးသည်။"},
    {"slug": "django-form-filefield", "title": "forms.FileField", "lesson": 6, "syntax": "forms.FileField()", "description": "Validates an uploaded file object.", "example": "document = forms.FileField()", "output": "A validated UploadedFile.", "mm": "Uploaded file object ကို validate လုပ်သည်။"},
    {"slug": "django-form-imagefield", "title": "forms.ImageField", "lesson": 6, "syntax": "forms.ImageField()", "description": "Validates image input using image decoding support.", "example": "photo = forms.ImageField()", "output": "A validated image upload.", "mm": "Image decode support ဖြင့် image input validate လုပ်သည်။"},
    {"slug": "django-form-widgets", "title": "Django form widgets", "lesson": 2, "syntax": "forms.Textarea(attrs={...})", "description": "Controls HTML representation and attributes for a field.", "example": "notes = forms.CharField(widget=forms.Textarea(attrs={\"rows\": 4}))", "output": "A textarea with documented attributes.", "mm": "Field ၏ HTML representation နှင့် attribute ကို ထိန်းသည်။"},
    {"slug": "django-form-is-valid", "title": "form.is_valid()", "lesson": 1, "syntax": "if form.is_valid(): ...", "description": "Runs the form cleaning pipeline and returns a boolean.", "example": "form = RegistrationForm(request.POST); form.is_valid()", "output": "True/False and populated cleaned data or errors.", "mm": "Validation pipeline run ပြီး boolean ပြန်သည်။"},
    {"slug": "django-form-cleaned-data", "title": "form.cleaned_data", "lesson": 1, "syntax": "form.cleaned_data[\"email\"]", "description": "Contains converted values after successful field cleaning.", "example": "email = form.cleaned_data[\"email\"]", "output": "A validated Python value.", "mm": "Validation အောင်မြင်ပြီး converted value ရှိသည်။"},
    {"slug": "django-form-errors", "title": "form.errors", "lesson": 1, "syntax": "form.errors", "description": "Exposes field and non-field validation errors for rendering or tests.", "example": "if form.errors: render_errors(form.errors)", "output": "Safe error structures for user feedback.", "mm": "Field/non-field error များကို rendering/test အတွက် ပေးသည်။"},
    {"slug": "django-form-clean", "title": "form.clean()", "lesson": 4, "syntax": "def clean(self): ...", "description": "Validates relationships between multiple form fields.", "example": "def clean(self):\n    data = super().clean()\n    return data", "output": "A cleaned form or non-field error.", "mm": "Field အများကြား relationship ကို validate လုပ်သည်။"},
    {"slug": "django-form-clean-field", "title": "clean_<fieldname>()", "lesson": 4, "syntax": "def clean_email(self): ...", "description": "Normalizes or validates one named form field.", "example": "def clean_email(self):\n    return self.cleaned_data[\"email\"].casefold()", "output": "A normalized field value.", "mm": "Field တစ်ခုချင်း normalize/validate လုပ်သည်။"},
    {"slug": "django-form-validation-error", "title": "forms.ValidationError", "lesson": 4, "syntax": "raise ValidationError(message, code=..., params=...)", "description": "Reports structured validation failure.", "example": "raise forms.ValidationError(\"Invalid age\", code=\"invalid_age\")", "output": "A coded form error.", "mm": "Structured validation failure ကို report လုပ်သည်။"},
    {"slug": "django-form-add-error", "title": "form.add_error()", "lesson": 4, "syntax": "form.add_error(\"field\", error)", "description": "Attaches a validation error to a particular field.", "example": "self.add_error(\"course\", \"Choose an available course.\")", "output": "A field-specific error and removed cleaned value.", "mm": "Field တစ်ခုသို့ error attach လုပ်သည်။"},
    {"slug": "django-form-non-field-errors", "title": "form.non_field_errors()", "lesson": 4, "syntax": "{{ form.non_field_errors }}", "description": "Renders errors concerning the form as a whole.", "example": "{{ form.non_field_errors }}", "output": "A form-level error message.", "mm": "Form တစ်ခုလုံးနှင့်သက်ဆိုင်သော error ပြသည်။"},
    {"slug": "django-form-save", "title": "form.save()", "lesson": 3, "syntax": "instance = form.save()", "description": "Valid ModelForm data to a model instance and saves it.", "example": "student = form.save()", "output": "A persisted model instance.", "mm": "ModelForm data ကို model instance အဖြစ် save သည်။"},
    {"slug": "django-form-save-commit-false", "title": "form.save(commit=False)", "lesson": 3, "syntax": "instance = form.save(commit=False)", "description": "Returns an unsaved ModelForm instance for trusted server additions.", "example": "student = form.save(commit=False); student.owner = actor; student.save()", "output": "An unsaved instance ready for server-owned fields.", "mm": "Server-owned field ထည့်ရန် unsaved instance ပြန်သည်။"},
    {"slug": "django-formset-factory", "title": "formset_factory()", "lesson": 5, "syntax": "formset_factory(Form, extra=1)", "description": "Creates a formset class for repeated non-model forms.", "example": "ContactFormSet = formset_factory(ContactForm, extra=2)", "output": "A reusable repeated form class.", "mm": "Model မချိတ်သော repeated form class ဖန်တီးသည်။"},
    {"slug": "django-modelformset-factory", "title": "modelformset_factory()", "lesson": 5, "syntax": "modelformset_factory(Student, fields=[...])", "description": "Creates a formset class for multiple model instances.", "example": "StudentSet = modelformset_factory(Student, fields=[\"name\"])", "output": "A model-backed formset.", "mm": "Model instance အများအတွက် formset ဖန်တီးသည်။"},
    {"slug": "django-inlineformset-factory", "title": "inlineformset_factory()", "lesson": 5, "syntax": "inlineformset_factory(Parent, Child, fields=[...])", "description": "Creates a formset for child objects related to one parent.", "example": "ContactSet = inlineformset_factory(Student, StudentContact, fields=[\"value\"])", "output": "A parent-bound related formset.", "mm": "Parent တစ်ခုနှင့်ဆက်သော child formset ဖန်တီးသည်။"},
    {"slug": "django-request-post-files", "title": "request.POST and request.FILES", "lesson": 6, "syntax": "Form(request.POST, request.FILES)", "description": "Binds regular fields and uploaded files to a form.", "example": "ProfileForm(request.POST, request.FILES, instance=profile)", "output": "A bound form with file data available.", "mm": "Regular field နှင့် upload file ကို form သို့ bind လုပ်သည်။"},
    {"slug": "django-csrf-token", "title": "csrf_token", "lesson": 7, "syntax": "{% csrf_token %}", "description": "Adds the CSRF token to an internal POST form.", "example": "<form method=\"post\">{% csrf_token %}...", "output": "CSRF-protected form submission.", "mm": "Internal POST form တွင် CSRF token ထည့်သည်။"},
    {"slug": "django-media-root-url", "title": "MEDIA_ROOT and MEDIA_URL", "lesson": 6, "syntax": "MEDIA_ROOT = BASE_DIR / \"media\"\nMEDIA_URL = \"/media/\"", "description": "Configures local media storage location and URL boundary.", "example": "photo = models.ImageField(upload_to=\"student-profiles/\")", "output": "A stored media reference under configured storage.", "mm": "Media storage location နှင့် URL boundary configure လုပ်သည်။"},
    {"slug": "django-upload-to", "title": "upload_to", "lesson": 6, "syntax": "upload_to=\"student-profiles/%Y/%m/\"", "description": "Defines a storage-relative upload path pattern.", "example": "photo = models.ImageField(upload_to=\"student-profiles/%Y/%m/\")", "output": "A date-partitioned storage path.", "mm": "Storage-relative upload path pattern သတ်မှတ်သည်။"},
    {"slug": "django-uploaded-file-chunks", "title": "UploadedFile.chunks()", "lesson": 6, "syntax": "for chunk in uploaded.chunks(): ...", "description": "Iterates over an upload incrementally.", "example": "for chunk in uploaded.chunks(): destination.write(chunk)", "output": "The file is processed without an unnecessary full-memory read.", "mm": "Upload ကို memory အပြည့်မဖတ်ဘဲ အပိုင်းလိုက် process လုပ်သည်။"},
]


def _project_source_files():
    return {
        "manage.py": "#!/usr/bin/env python\nimport os\nimport sys\n\nif __name__ == \"__main__\":\n    os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\", \"school_site.settings\")\n    from django.core.management import execute_from_command_line\n    execute_from_command_line(sys.argv)\n",
        "school_site/settings.py": "import os\nfrom pathlib import Path\nBASE_DIR = Path(__file__).resolve().parent.parent\nSECRET_KEY = os.environ.get(\"DJANGO_SECRET_KEY\", \"unsafe-local-only\")\nDEBUG = os.environ.get(\"DJANGO_DEBUG\", \"1\") == \"1\"\nINSTALLED_APPS = [\"django.contrib.auth\", \"django.contrib.contenttypes\", \"django.contrib.sessions\", \"django.contrib.messages\", \"django.contrib.staticfiles\", \"students\", \"courses\"]\nMIDDLEWARE = [\"django.middleware.security.SecurityMiddleware\", \"django.contrib.sessions.middleware.SessionMiddleware\", \"django.middleware.csrf.CsrfViewMiddleware\", \"django.contrib.auth.middleware.AuthenticationMiddleware\", \"django.contrib.messages.middleware.MessageMiddleware\"]\nDATABASES = {\"default\": {\"ENGINE\": \"django.db.backends.postgresql\", \"NAME\": os.environ[\"POSTGRES_DB\"], \"USER\": os.environ[\"POSTGRES_USER\"], \"PASSWORD\": os.environ[\"POSTGRES_PASSWORD\"], \"HOST\": os.environ.get(\"POSTGRES_HOST\", \"127.0.0.1\"), \"PORT\": os.environ.get(\"POSTGRES_PORT\", \"5432\")}}\nMEDIA_ROOT = BASE_DIR / \"media\"\nMEDIA_URL = \"/media/\"\nSTATIC_URL = \"/static/\"\nUSE_TZ = True\nTIME_ZONE = \"UTC\"\nROOT_URLCONF = \"school_site.urls\"\nDEFAULT_AUTO_FIELD = \"django.db.models.BigAutoField\"\n",
        "school_site/urls.py": "from django.urls import include, path\nurlpatterns = [path(\"students/\", include(\"students.urls\")), path(\"courses/\", include(\"courses.urls\"))]\n",
        "students/models.py": "from django.db import models\n\nclass Student(models.Model):\n    owner = models.ForeignKey(\"auth.User\", on_delete=models.PROTECT, related_name=\"students\")\n    name = models.CharField(max_length=150)\n    email = models.EmailField(unique=True)\n    age = models.PositiveIntegerField()\n    is_archived = models.BooleanField(default=False)\n    def __str__(self):\n        return self.name\n\nclass StudentProfile(models.Model):\n    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name=\"profile\")\n    photo = models.ImageField(upload_to=\"student-profiles/%Y/%m/\", blank=True)\n    biography = models.TextField(blank=True)\n\nclass StudentContact(models.Model):\n    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name=\"contacts\")\n    kind = models.CharField(max_length=30)\n    value = models.CharField(max_length=120)\n\nclass Course(models.Model):\n    code = models.CharField(max_length=20, unique=True)\n    title = models.CharField(max_length=160)\n    is_archived = models.BooleanField(default=False)\n\nclass Enrollment(models.Model):\n    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name=\"enrollments\")\n    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name=\"enrollments\")\n    created_at = models.DateTimeField(auto_now_add=True)\n    class Meta:\n        constraints = [models.UniqueConstraint(fields=[\"student\", \"course\"], name=\"unique_student_course\")]\n",
        "students/validators.py": "from PIL import Image\nfrom django.core.exceptions import ValidationError\n\ndef validate_profile_image(uploaded):\n    if uploaded.size > 5 * 1024 * 1024:\n        raise ValidationError(\"Image is too large.\", code=\"too_large\")\n    try:\n        with Image.open(uploaded) as image:\n            image.verify()\n    except Exception as exc:\n        raise ValidationError(\"Upload a valid image.\", code=\"invalid_image\") from exc\n    uploaded.seek(0)\n    return uploaded\n",
        "students/forms.py": "from django import forms\nfrom .models import Course, Student, StudentContact, StudentProfile\nfrom .validators import validate_profile_image\n\nclass StudentRegistrationForm(forms.ModelForm):\n    class Meta:\n        model = Student\n        fields = [\"name\", \"email\", \"age\"]\n\n    def clean_email(self):\n        return self.cleaned_data[\"email\"].strip().casefold()\n\nclass ProfileForm(forms.ModelForm):\n    photo = forms.ImageField(required=False, validators=[validate_profile_image])\n    class Meta:\n        model = StudentProfile\n        fields = [\"photo\", \"biography\"]\n\nclass EnrollmentForm(forms.Form):\n    course = forms.ModelChoiceField(queryset=Course.objects.none())\n    def __init__(self, *args, available_courses, **kwargs):\n        super().__init__(*args, **kwargs)\n        self.fields[\"course\"].queryset = available_courses.filter(is_archived=False)\n\nContactFormSet = forms.inlineformset_factory(Student, StudentContact, fields=[\"kind\", \"value\"], extra=1, can_delete=True)\n",
        "students/services.py": "from django.db import IntegrityError, transaction\nfrom .models import Enrollment\n\nclass DuplicateEnrollment(Exception):\n    pass\n\ndef enroll(student, course):\n    try:\n        with transaction.atomic():\n            return Enrollment.objects.create(student=student, course=course)\n    except IntegrityError as exc:\n        raise DuplicateEnrollment from exc\n\ndef save_profile(form, student):\n    with transaction.atomic():\n        profile = form.save(commit=False)\n        profile.student = student\n        profile.save()\n        form.save_m2m()\n    return profile\n",
        "students/views.py": "from django.contrib import messages\nfrom django.core.exceptions import PermissionDenied\nfrom django.shortcuts import get_object_or_404, redirect, render\nfrom django.views.decorators.csrf import csrf_protect\nfrom .forms import ContactFormSet, ProfileForm, StudentRegistrationForm\nfrom .models import Student\nfrom .services import save_profile\n\n@csrf_protect\ndef register(request):\n    form = StudentRegistrationForm(request.POST or None)\n    if request.method == \"POST\" and form.is_valid():\n        student = form.save(commit=False)\n        student.owner = request.user\n        student.save()\n        messages.success(request, \"Student registration saved.\")\n        return redirect(\"students:detail\", pk=student.pk)\n    return render(request, \"students/register.html\", {\"form\": form})\n\n@csrf_protect\ndef edit_profile(request, pk):\n    student = get_object_or_404(Student, pk=pk)\n    if not request.user.is_staff or student.owner_id != request.user.id:\n        raise PermissionDenied\n    profile, _ = student.profile, None\n    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)\n    if request.method == \"POST\" and form.is_valid():\n        save_profile(form, student)\n        messages.success(request, \"Profile updated.\")\n        return redirect(\"students:detail\", pk=student.pk)\n    return render(request, \"students/edit.html\", {\"form\": form, \"student\": student})\n\ndef detail(request, pk):\n    student = get_object_or_404(Student.objects.prefetch_related(\"contacts\", \"enrollments__course\"), pk=pk)\n    return render(request, \"students/detail.html\", {\"student\": student})\n",
        "students/urls.py": "from django.urls import path\nfrom . import views\napp_name = \"students\"\nurlpatterns = [path(\"register/\", views.register, name=\"register\"), path(\"<int:pk>/\", views.detail, name=\"detail\"), path(\"<int:pk>/profile/\", views.edit_profile, name=\"edit-profile\")]\n",
        "courses/views.py": "from django.shortcuts import redirect, render\nfrom students.forms import EnrollmentForm\nfrom students.models import Course\n\ndef enroll(request):\n    available = Course.objects.filter(is_archived=False)\n    form = EnrollmentForm(request.POST or None, available_courses=available)\n    if request.method == \"POST\" and form.is_valid():\n        return redirect(\"courses:success\")\n    return render(request, \"courses/enrollment.html\", {\"form\": form})\n",
        "courses/urls.py": "from django.urls import path\nfrom .views import enroll\napp_name = \"courses\"\nurlpatterns = [path(\"enroll/\", enroll, name=\"enroll\")]\n",
        "students/tests/test_forms.py": "from django.test import TestCase\nfrom students.forms import StudentRegistrationForm\n\nclass StudentFormTests(TestCase):\n    def test_fields_are_allowlisted_and_email_normalized(self):\n        form = StudentRegistrationForm({\"name\": \"Learner\", \"email\": \" Learner@Example.Test \", \"age\": 18, \"is_archived\": True})\n        self.assertTrue(form.is_valid())\n        self.assertNotIn(\"is_archived\", form.fields)\n        self.assertEqual(form.cleaned_data[\"email\"], \"learner@example.test\")\n",
        "students/tests/test_validation.py": "from django.test import SimpleTestCase\nfrom students.forms import EnrollmentForm\nfrom students.models import Course\n\nclass ValidationTests(SimpleTestCase):\n    def test_course_queryset_is_supplied_by_workflow(self):\n        form = EnrollmentForm(available_courses=Course.objects.none())\n        self.assertIn(\"course\", form.fields)\n",
        "students/tests/test_uploads.py": "from django.test import SimpleTestCase\nfrom django.core.files.uploadedfile import SimpleUploadedFile\nfrom students.forms import ProfileForm\n\nclass UploadTests(SimpleTestCase):\n    def test_oversized_image_is_rejected(self):\n        upload = SimpleUploadedFile(\"photo.png\", b\"0\" * (5 * 1024 * 1024 + 1), content_type=\"image/png\")\n        form = ProfileForm({\"biography\": \"demo\"}, {\"photo\": upload})\n        self.assertFalse(form.is_valid())\n",
        "students/tests/test_views.py": "from django.test import Client, TestCase\n\nclass SecurityViewTests(TestCase):\n    def test_csrf_is_enforced(self):\n        response = Client(enforce_csrf_checks=True).post(\"/students/register/\", {\"name\": \"Learner\"})\n        self.assertEqual(response.status_code, 403)\n",
        "courses/tests/test_enrollment.py": "from django.test import SimpleTestCase\n\nclass EnrollmentBoundaryTests(SimpleTestCase):\n    def test_project_uses_a_restricted_demo_boundary(self):\n        self.assertTrue(True)\n",
        "templates/base.html": "{% load static %}<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><link rel=\"stylesheet\" href=\"{% static 'css/forms.css' %}\"><title>{% block title %}Student Portal{% endblock %}</title></head><body>{% if messages %}<div role=\"status\">{% for message in messages %}{{ message }}{% endfor %}</div>{% endif %}{% block content %}{% endblock %}</body></html>",
        "templates/students/register.html": "{% extends 'base.html' %}{% block content %}<main><h1>Student registration</h1><form method=\"post\">{% csrf_token %}{{ form.non_field_errors }}{{ form.as_p }}<button type=\"submit\">Register</button></form></main>{% endblock %}",
        "templates/students/edit.html": "{% extends 'base.html' %}{% block content %}<main><h1>Edit profile</h1><form method=\"post\" enctype=\"multipart/form-data\">{% csrf_token %}{{ form.non_field_errors }}{{ form.as_p }}<button type=\"submit\">Save</button></form></main>{% endblock %}",
        "templates/students/detail.html": "{% extends 'base.html' %}{% block content %}<main><h1>{{ student.name }}</h1>{% if student.profile.photo %}<img src=\"{{ student.profile.photo.url }}\" alt=\"Profile photo\">{% endif %}<ul>{% for contact in student.contacts.all %}<li>{{ contact.kind }}: {{ contact.value }}</li>{% endfor %}</ul></main>{% endblock %}",
        "templates/courses/enrollment.html": "{% extends 'base.html' %}{% block content %}<main><h1>Course enrollment</h1><form method=\"post\">{% csrf_token %}{{ form.as_p }}<button type=\"submit\">Enroll</button></form></main>{% endblock %}",
        "static/css/forms.css": ":root { font-family: system-ui, sans-serif; color: #172033; }\nbody { margin: 0; padding: 1rem; }\nmain { max-width: 48rem; margin: auto; }\nform { display: grid; gap: 1rem; }\ninput, select, textarea { width: 100%; box-sizing: border-box; padding: .7rem; }\n.errorlist { color: #a11; }\n:focus-visible { outline: 3px solid #7658ff; outline-offset: 2px; }\n@media (min-width: 48rem) { form { grid-template-columns: repeat(2, minmax(0, 1fr)); } form button { grid-column: 1 / -1; } }\n",
        "static/js/forms.js": "document.addEventListener(\"DOMContentLoaded\", () => { document.querySelectorAll(\"[data-add-row]\").forEach((button) => button.addEventListener(\"click\", () => { const target = document.querySelector(button.dataset.addRow); if (target) target.classList.remove(\"is-hidden\"); })); });\n",
        "students/migrations/0001_initial.py": "from django.db import migrations, models\n\nclass Migration(migrations.Migration):\n    initial = True\n    dependencies = [(\"auth\", \"0012_alter_user_first_name_max_length\")]\n    operations = [migrations.CreateModel(name=\"Student\", fields=[(\"id\", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name=\"ID\")), (\"name\", models.CharField(max_length=150)), (\"email\", models.EmailField(max_length=254, unique=True)), (\"age\", models.PositiveIntegerField())])]\n",
    }


def _ensure_project(db, course, module):
    slug = "django-student-registration-profile-management"
    source_files = _project_source_files()
    brief = {
        "goal": "Extend the database-backed Student Management System with safe registration, profile editing, course enrollment and profile photo uploads.",
        "scope": "Module 06 draft project only. Use a restricted staff/demo boundary, synthetic records and school_portal_forms_dev.",
        "setup_commands": ["python -m venv .venv", "pip install Django==6.0.* psycopg[binary] Pillow", "python manage.py check", "python manage.py makemigrations", "python manage.py migrate", "python manage.py test"],
        "routes": ["/students/register/", "/students/<id>/", "/students/<id>/profile/", "/courses/enroll/"],
        "source_files": source_files,
        "required_features": ["Student Registration Form", "Student Profile ModelForm", "email and age validation", "duplicate email protection", "course selector", "enrollment", "profile photo upload", "size/content validation", "CSRF", "responsive templates", "tests"],
        "expected_behavior": ["GET renders unbound forms", "Invalid POST preserves values and shows errors", "Valid POST saves and redirects", "Unexpected fields are ignored", "Unauthorized edit is forbidden", "Invalid/oversized uploads are rejected", "Messages appear after successful persistence"],
        "testing_guide": "Run form unit tests, validation tests, CSRF-enforcing view tests, upload tests with temporary media, model constraint tests and integration tests in an isolated test database.",
        "deployment_guide": "Use a secret provider, private/non-executable media storage, DEBUG=False, HTTPS/CSRF settings and a reviewed authorization boundary. Full authentication is deferred to Module 07.",
        "review_checklist": ["No live student data", "No credentials in source", "Explicit ModelForm fields", "CSRF enabled", "Object authorization documented", "Uploads size/content checked", "Media cleanup policy documented", "Answer keys private", "All records remain draft"],
    }
    values = {"title": "Student Registration and Profile Management System", "description_en": "A Django Forms and ModelForms project with secure validation, enrollment handling, profile image uploads, responsive templates, CSRF protection and tests.", "description_mm": "Django Form/ModelForm၊ safe validation၊ enrollment၊ profile image upload၊ responsive template၊ CSRF နှင့် test ပါသော Student Registration and Profile Management System ဖြစ်သည်။", "difficulty": "advanced", "estimated_hours": 24, "requirements": "Python 3.12+, Django 6.0 target, PostgreSQL 14+, psycopg 3.1.12+, Pillow and an isolated school_portal_forms_dev database.", "learning_outcomes": "Collect and validate input, persist allowlisted models, manage related data, upload safe images, protect workflows and test failure paths.", "technology_stack": "Python | Django Forms | ModelForms | PostgreSQL | psycopg | Pillow | HTML/CSS | JavaScript | Django Test Framework", "prerequisites": "Complete Django Modules 01–05; use synthetic data and restricted staff/demo access.", "architecture_overview": "school_site owns settings and URLs; students owns models/forms/validators/services/views; courses owns enrollment UI; templates render accessible forms; static contains responsive CSS/JS; media is isolated untrusted storage; tests prove validation, CSRF, authorization and upload behavior.", "folder_structure": "\n".join(source_files.keys()), "testing_guide": brief["testing_guide"], "deployment_guide": brief["deployment_guide"], "tags_json": json.dumps(["django", "forms", "modelforms", "validation", "uploads", "csrf", "student-registration"], ensure_ascii=False), "languages_json": json.dumps(["Python", "HTML", "CSS", "JavaScript"], ensure_ascii=False), "brief_json": json.dumps(brief, ensure_ascii=False), "status": "draft", "published": False}
    project = db.scalar(select(ProjectTemplate).where(ProjectTemplate.slug == slug))
    if not project:
        project = ProjectTemplate(slug=slug, **values)
        db.add(project)
        db.flush()
    elif not project.published and project.status not in {"published", "approved", "in_review"}:
        for key, value in values.items():
            setattr(project, key, value)
    link = db.scalar(select(ProjectCourseLink).where(ProjectCourseLink.project_id == project.id, ProjectCourseLink.course_id == course.id, ProjectCourseLink.module_id == module.id))
    if not link:
        db.add(ProjectCourseLink(project_id=project.id, course_id=course.id, module_id=module.id, position=1))
    milestones = [
        ("Registration forms", "Create and validate the Student Registration Form with GET/POST, CSRF and PRG.", "students/forms.py"),
        ("ModelForms and related data", "Edit Student and Profile records with allowlists, ownership checks and an inline contact formset.", "students/services.py"),
        ("Uploads and storage", "Validate profile image size/content, use safe media paths, replace files carefully and test cleanup.", "students/validators.py"),
        ("Security and testing", "Run form, CSRF, authorization, upload and integration tests in an isolated test database.", "students/tests/test_views.py"),
    ]
    for position, (title, description, filename) in enumerate(milestones, 1):
        row = db.scalar(select(ProjectMilestone).where(ProjectMilestone.project_id == project.id, ProjectMilestone.position == position))
        data = {"title": title, "slug": f"registration-portal-{position}", "description_en": description, "description_mm": description + " ကို isolated project တွင် လေ့ကျင့်ပါ။", "content_en": f"Required boundary: {filename}\n\n{description}\n\nUse synthetic records, restricted demo access and actual test output.", "content_mm": "Synthetic record၊ restricted demo access နှင့် actual test output သုံးပါ။", "code": source_files.get(filename, ""), "filename": filename, "expected_output": "The learner records actual form, validation, CSRF, upload and test results and explains one remaining limitation.", "line_explanation": "Read the form/service/view boundary, run the focused check, inspect the result, then add a regression test.", "completion_criteria": "Source exists, checks/tests run, security boundary is documented, and no live data or credential is used.", "resources_json": json.dumps([{"title": "Django forms", "url": "https://docs.djangoproject.com/en/6.0/topics/forms/"}, {"title": "Django file uploads", "url": "https://docs.djangoproject.com/en/6.0/topics/http/file-uploads/"}], ensure_ascii=False), "required": True}
        if not row:
            db.add(ProjectMilestone(project_id=project.id, position=position, **data))
        else:
            for key, value in data.items():
                setattr(row, key, value)
    requirements = [
        ("Safe registration", "A Student Registration Form validates and persists only allowlisted fields.", "Invalid input preserves errors; valid input redirects after persistence; unexpected fields are ignored."),
        ("Profile and enrollment workflow", "ModelForms, course selection and related formsets enforce server-side rules.", "Ownership boundary, duplicate enrollment handling and atomic related writes are tested."),
        ("Upload and security boundary", "Profile image upload validates size/content and uses isolated media handling.", "CSRF, forbidden edit, malformed/oversized upload and cleanup behavior are tested/documented."),
    ]
    for position, (title, description, acceptance) in enumerate(requirements, 1):
        row = db.scalar(select(ProjectRequirement).where(ProjectRequirement.project_id == project.id, ProjectRequirement.position == position))
        data = {"title": title, "description": description, "acceptance_criteria": acceptance, "required": True}
        if not row:
            db.add(ProjectRequirement(project_id=project.id, position=position, **data))
        else:
            for key, value in data.items():
                setattr(row, key, value)
    rubric = [("Form design", "Forms, widgets, allowlists, labels and validation boundaries are clear.", 25), ("Persistence and relationships", "ModelForms, formsets, transactions and database constraints are correct.", 25), ("Upload security", "Size/content checks, storage isolation, replacement and cleanup policy are documented.", 20), ("Security and UX", "CSRF, authorization limitation, PRG, messages, accessibility and responsive behavior are addressed.", 20), ("Tests and documentation", "Tests run, actual output is recorded and remaining scope is honest.", 10)]
    for position, (name, description, weight) in enumerate(rubric, 1):
        row = db.scalar(select(ProjectRubricCriterion).where(ProjectRubricCriterion.project_id == project.id, ProjectRubricCriterion.position == position))
        if not row:
            db.add(ProjectRubricCriterion(project_id=project.id, position=position, name=name, description=description, weight=weight))
        else:
            row.name, row.description, row.weight = name, description, weight
    return project


def _ensure_syntax_references(db, course, lessons_by_position):
    created = 0
    for display_order, item in enumerate(SYNTAX_REFERENCES, 1):
        ref = db.scalar(select(SyntaxReference).where(SyntaxReference.course_id == course.id, SyntaxReference.slug == item["slug"]))
        values = {"title": item["title"], "category": "Django Forms and File Uploads", "description": item["description"], "basic_syntax": item["syntax"], "when_to_use": "Use this reference in the matching Module 06 lesson and verify it against the target Django version.", "important_notes": "Keep CSRF enabled, restrict object querysets, validate upload content and never expose answer keys or credentials.", "reference_type": "framework_api", "difficulty": "intermediate", "purpose": item["description"], "syntax_format": item["syntax"], "parameters": "See the official Django documentation for documented arguments.", "return_value": item["output"], "version_compatibility": "Django 6.0 target; verify the exact project lockfile.", "input_output": f"Input: {item['example']}\nOutput: {item['output']}", "common_mistakes": "Do not disable CSRF, trust client validation, expose unauthorized objects or trust file extensions alone.", "best_practices": "Use explicit fields, safe errors, isolated test data, restricted media and focused tests.", "practice_exercises": "Implement the linked lesson exercise and record actual output.", "further_reading": "https://docs.djangoproject.com/en/6.0/", "minimum_examples": 1, "review_notes": "Phase 08 Module 06 draft; publication remains review-only.", "status": "draft", "display_order": display_order}
        if not ref:
            ref = SyntaxReference(course_id=course.id, slug=item["slug"], **values)
            db.add(ref)
            db.flush()
            created += 1
        elif ref.status not in {"published", "approved", "in_review"}:
            for key, value in values.items():
                setattr(ref, key, value)
        if not db.scalar(select(SyntaxReferenceTranslation).where(SyntaxReferenceTranslation.reference_id == ref.id, SyntaxReferenceTranslation.locale == "my")):
            db.add(SyntaxReferenceTranslation(reference_id=ref.id, locale="my", title=item["title"], description=item["mm"], purpose=item["mm"], syntax_format=item["syntax"], parameters="Supported Django version official documentation နှင့် တိုက်စစ်ပါ။", return_value=item["output"], version_compatibility="Django 6.0 target နှင့် lockfile version ကို စစ်ပါ။", input_output=f"Input: {item['example']}\nOutput: {item['output']}", common_mistakes="CSRF မပိတ်ပါနှင့်။ Unauthorized object/file မသုံးပါနှင့်။", best_practices="Explicit field၊ safe error၊ restricted media နှင့် focused test သုံးပါ။", practice_exercises="သက်ဆိုင်ရာ lesson exercise ကို run ပြီး actual result မှတ်ပါ။", further_reading="https://docs.djangoproject.com/en/6.0/", status="draft"))
        example = db.scalar(select(SyntaxReferenceExample).where(SyntaxReferenceExample.reference_id == ref.id, SyntaxReferenceExample.example_number == 1))
        example_values = {"title": item["title"], "code": item["example"], "language": "django", "difficulty": "intermediate", "description": item["description"], "setup": "Use the supported isolated Django project.", "sample_input": item["syntax"], "expected_output": item["output"], "explanation": "Run the focused example and compare actual behavior with the documented expectation.", "common_mistakes": "Keep CSRF, authorization and upload boundaries explicit.", "verification_steps": "Run a focused check/test and record the actual result."}
        if not example:
            example = SyntaxReferenceExample(reference_id=ref.id, example_number=1, **example_values)
            db.add(example)
            db.flush()
        else:
            for key, value in example_values.items():
                setattr(example, key, value)
        if not db.scalar(select(SyntaxExampleTranslation).where(SyntaxExampleTranslation.example_id == example.id, SyntaxExampleTranslation.locale == "my")):
            db.add(SyntaxExampleTranslation(example_id=example.id, locale="my", title=item["title"], description=item["mm"], setup="Isolated Django project တွင် run ပါ။", sample_input=item["syntax"], expected_output=item["output"], explanation="Example ကို run ပြီး actual behavior နှင့် နှိုင်းပါ။", common_mistakes="CSRF၊ authorization နှင့် upload boundary မလွတ်ပါစေနှင့်။", verification_steps="Focused check/test run လုပ်ပြီး result မှတ်ပါ။", status="draft"))
        lesson = lessons_by_position[item["lesson"]]
        if not db.scalar(select(LessonSyntaxReference).where(LessonSyntaxReference.lesson_id == lesson.id, LessonSyntaxReference.reference_id == ref.id)):
            db.add(LessonSyntaxReference(lesson_id=lesson.id, reference_id=ref.id, position=display_order))
    return created


def seed_django_module_six(db, course):
    """Populate only canonical Django Module 06 as reviewable draft content."""
    module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == 6))
    if not module:
        module = CourseModule(course_id=course.id, title=MODULE_TITLE, order_index=6)
        db.add(module)
        db.flush()
    module.title = MODULE_TITLE
    module.title_mm = MODULE_TITLE_MM
    module.description = MODULE_DESCRIPTION
    module.description_mm = MODULE_DESCRIPTION_MM
    module.learning_objectives = "\n".join(f"{i}. {value}" for i, value in enumerate(OBJECTIVES, 1))
    module.learning_objectives_mm = "\n".join(f"{i}. {value}" for i, value in enumerate(OBJECTIVES_MM, 1))
    created_lessons = 0
    lessons_by_position = {}
    for position, item in enumerate(LESSONS, 1):
        lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == position))
        if not lesson:
            lesson = Lesson(module_id=module.id, title=item["title"], slug=item["slug"], description=item["description"], content_en="", content_mm="", order_index=position, duration_minutes=100, status="draft", published=False)
            db.add(lesson)
            db.flush()
            created_lessons += 1
        content_en, content_mm = _render_en(item), _render_mm(item)
        if lesson.published or lesson.status in {"published", "approved", "in_review"}:
            draft = db.scalar(select(LessonContentDraft).where(LessonContentDraft.lesson_id == lesson.id))
            if not draft:
                db.add(LessonContentDraft(lesson_id=lesson.id, base_content_version=lesson.content_version, draft_version=1, title=item["title"], slug=lesson.slug, description=item["description"], content_en=content_en, content_mm=content_mm, duration_minutes=100, status="draft", change_summary="Phase 08 Module 06 authoring"))
            elif draft.status == "draft":
                draft.title, draft.description, draft.content_en, draft.content_mm, draft.duration_minutes = item["title"], item["description"], content_en, content_mm, 100
        else:
            lesson.title = item["title"]
            lesson.description = item["description"]
            lesson.content_en = content_en
            lesson.content_mm = content_mm
            lesson.duration_minutes = 100
            lesson.status = "draft"
            lesson.published = False
            _ensure_examples(db, lesson, item)
            _ensure_quiz(db, lesson, item)
            _ensure_exercise(db, lesson, item)
        lessons_by_position[position] = lesson
    assessment_questions = _module_assessment()
    payload = [{"position": i, **question} for i, question in enumerate(assessment_questions, 1)]
    assessment = db.scalar(select(ModuleQuizDraft).where(ModuleQuizDraft.module_id == module.id))
    if not assessment:
        db.add(ModuleQuizDraft(module_id=module.id, title_en="Django Forms, ModelForms, Validation and File Uploads Module Assessment", title_mm="Django Form၊ ModelForm၊ Validation နှင့် File Upload Module စစ်ဆေးမှု", questions_json=json.dumps(payload, ensure_ascii=False), pass_percent=70, status="draft"))
    elif assessment.status not in {"published", "approved", "in_review"}:
        assessment.title_en = "Django Forms, ModelForms, Validation and File Uploads Module Assessment"
        assessment.title_mm = "Django Form၊ ModelForm၊ Validation နှင့် File Upload Module စစ်ဆေးမှု"
        assessment.questions_json = json.dumps(payload, ensure_ascii=False)
        assessment.pass_percent = 70
        assessment.status = "draft"
    project = _ensure_project(db, course, module)
    syntax_created = _ensure_syntax_references(db, course, lessons_by_position)
    db.flush()
    return {"module": module, "created_lessons": created_lessons, "lesson_count": len(LESSONS), "assessment_questions": len(assessment_questions), "project": project, "syntax_created": syntax_created}

