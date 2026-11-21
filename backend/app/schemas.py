from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from .tool_registry import APPROVED_IMPLEMENTATION_KEYS
class LanguageOut(BaseModel):
    model_config=ConfigDict(from_attributes=True); id: UUID; name: str; slug: str; color: str
class CategoryOut(BaseModel):
    model_config=ConfigDict(from_attributes=True); id: UUID; name: str; slug: str
class ExampleOut(BaseModel):
    model_config=ConfigDict(from_attributes=True); id: UUID; title: str; language: str; code: str
class LessonOut(BaseModel):
    model_config=ConfigDict(from_attributes=True); id: UUID; title: str; slug: str; content_en: str; content_mm: str|None; order_index: int; code_examples: list[ExampleOut]=Field(default_factory=list)
class ModuleOut(BaseModel):
    model_config=ConfigDict(from_attributes=True); id: UUID; title: str; order_index: int; lessons: list[LessonOut]=Field(default_factory=list)
class LessonSummaryOut(BaseModel):
    model_config=ConfigDict(from_attributes=True); id: UUID; title: str; slug: str; order_index: int; duration_minutes: int
class LearningModuleOut(BaseModel):
    model_config=ConfigDict(from_attributes=True); id: UUID; title: str; order_index: int; lessons: list[LessonSummaryOut]=Field(default_factory=list)
class CourseOut(BaseModel):
    model_config=ConfigDict(from_attributes=True); id: UUID; title: str; slug: str; description: str; short_description: str = ""; thumbnail: str|None = None; level: str; duration_minutes: int; status: str; module_count: int = 0; lesson_count: int = 0; outcomes: list[str]=Field(default_factory=list); requirements: list[str]=Field(default_factory=list); language: LanguageOut; category: CategoryOut
    @field_validator("outcomes", mode="before")
    @classmethod
    def split_outcomes(cls, value): return value.split("|") if isinstance(value, str) else value
    @field_validator("requirements", mode="before")
    @classmethod
    def split_requirements(cls, value): return value.split("|") if isinstance(value, str) else value
class CourseDetailOut(CourseOut):
    target_audience: str = ""; technologies: list[str]=Field(default_factory=list); instructors: list[dict]=Field(default_factory=list); faqs: list[dict]=Field(default_factory=list); related_courses: list[dict]=Field(default_factory=list); modules: list[ModuleOut]=Field(default_factory=list)
class CourseLearningOut(CourseOut):
    modules: list[LearningModuleOut]=Field(default_factory=list)
class PageOut(BaseModel):
    items: list[CourseOut]; page: int; page_size: int; total: int; pages: int

class ToolCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID; name: str; slug: str; description: str = ""; icon_key: str = "wrench"; display_order: int = 0; is_active: bool = True

class DeveloperToolOut(BaseModel):
    id: UUID; name: str; slug: str; short_description: str; full_description: str = ""; icon_key: str; route_path: str; tags: list[str] = Field(default_factory=list); display_order: int; is_featured: bool; is_enabled: bool; category: ToolCategoryOut | None = None; implementation: str = ""; implementation_available: bool = True

class ToolCatalogPage(BaseModel):
    items: list[DeveloperToolOut]; page: int; page_size: int; total: int; pages: int

class AdminToolCategoryIn(BaseModel):
    name: str = Field(min_length=1, max_length=120); slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=120); description: str = Field(default="", max_length=4000); icon_key: str = Field(default="wrench", max_length=80); display_order: int = Field(default=0, ge=0); is_active: bool = True

class AdminToolIn(BaseModel):
    name: str = Field(min_length=1, max_length=160); slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=160); short_description: str = Field(default="", max_length=1000); full_description: str = Field(default="", max_length=10000); icon_key: str = Field(default="wrench", max_length=80); route_path: str = Field(pattern=r"^/tools/[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=240); implementation_key: str = Field(max_length=100); tags: list[str] = Field(default_factory=list, max_length=20); category_id: UUID | None = None; display_order: int = Field(default=0, ge=0); is_featured: bool = False; is_enabled: bool = True; status: str = Field(default="draft", pattern=r"^(draft|in_review|published|archived)$")
    @field_validator("implementation_key")
    @classmethod
    def approved_implementation(cls, value: str):
        if value not in APPROVED_IMPLEMENTATION_KEYS: raise ValueError("Implementation key is not registered")
        return value
    @field_validator("tags")
    @classmethod
    def clean_tags(cls, value: list[str]):
        cleaned = [item.strip().lower() for item in value if item.strip()]
        if len(cleaned) != len(set(cleaned)): raise ValueError("Tags must be unique")
        return cleaned

class AdminToolOut(AdminToolIn):
    id: UUID; published_at: datetime | None = None; created_at: datetime | None = None; updated_at: datetime | None = None; category: ToolCategoryOut | None = None
class QuizAnswerIn(BaseModel):
    answers: dict[str, str] = Field(default_factory=dict)
class QuizQuestionOut(BaseModel):
    id: UUID; prompt: str; question_type: str; options: list[str] = Field(default_factory=list); position: int
class QuizOut(BaseModel):
    id: UUID; lesson_id: UUID; title: str; explanation: str; questions: list[QuizQuestionOut] = Field(default_factory=list); latest_attempt: dict|None = None
class AdminQuizQuestionIn(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    options: list[str] = Field(default_factory=list, max_length=10)
    correct_answer: str = Field(min_length=1, max_length=255)
    explanation: str = Field(default="", max_length=4000)
    question_type: str = Field(default="multiple_choice", pattern=r"^(multiple_choice|true_false|code_output)$")
    position: int = Field(ge=1)
    @model_validator(mode="after")
    def valid_options(self):
        cleaned=[option.strip() for option in self.options if option.strip()]
        if len(cleaned) != len(self.options) or len(set(cleaned)) != len(cleaned): raise ValueError("Quiz options must be non-empty and unique")
        if self.correct_answer not in cleaned: raise ValueError("Correct answer must match one of the options")
        return self
class PathOut(BaseModel):
    model_config=ConfigDict(from_attributes=True); id: UUID; title: str; slug: str; description: str
class RegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120); email: str; password: str = Field(min_length=8, max_length=12); confirm_password: str = Field(min_length=8, max_length=12); accept_terms: bool
    @model_validator(mode="after")
    def valid(self):
        if "@" not in self.email: raise ValueError("Valid email required")
        if self.password != self.confirm_password: raise ValueError("Passwords do not match")
        if not self.accept_terms: raise ValueError("Terms must be accepted")
        return self
class LoginIn(BaseModel): email: str; password: str
class ForgotPasswordIn(BaseModel): email: str
class ResetPasswordIn(BaseModel):
    token: str = Field(min_length=20); password: str = Field(min_length=8, max_length=12); confirm_password: str = Field(min_length=8, max_length=12)
    @model_validator(mode="after")
    def valid(self):
        if self.password != self.confirm_password: raise ValueError("Passwords do not match")
        return self
class ChangePasswordIn(BaseModel):
    current_password: str; new_password: str = Field(min_length=8, max_length=12); confirm_password: str = Field(min_length=8, max_length=12)
    @model_validator(mode="after")
    def valid(self):
        if self.new_password != self.confirm_password: raise ValueError("Passwords do not match")
        return self
class ProfileIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120); bio: str|None = Field(default=None, max_length=1000); learning_interests: list[str] = Field(default_factory=list); preferred_language: str|None = Field(default=None, max_length=80); learning_level: str|None = Field(default=None, max_length=30); show_myanmar: bool=False
class UserOut(BaseModel):
    id: UUID; email: str; full_name: str; role: str; email_verified: bool; email_verified_at: datetime|None; profile: dict
class EnrollmentOut(BaseModel):
    id: UUID; course: CourseOut; completed_lessons: int; total_lessons: int; progress_percent: float; last_lesson_slug: str|None; next_lesson_slug: str|None = None
class ProgressIn(BaseModel): completed: bool
class DashboardOut(BaseModel):
    enrollments: list[EnrollmentOut]
    completed_lessons: int
    overall_progress: float
    recent_activity: list[dict]
    total_enrolled: int = 0
    in_progress_courses: int = 0
    completed_courses: int = 0
    quiz_attempts: int = 0
    quiz_average_score: float | None = None
    certificates_earned: int = 0
    current_streak: int = 0
    learning_time_minutes: int | None = None
class DashboardStudentOut(BaseModel):
    id: UUID
    display_name: str
    avatar_url: str | None = None
class DashboardStatisticsOut(BaseModel):
    enrolled_courses: int
    courses_in_progress: int
    completed_courses: int
    completed_lessons: int
    learning_seconds: int | None = None
    certificates_earned: int
    quiz_average_score: float | None = None
    quiz_attempts: int = 0
    current_learning_streak: int
class DashboardLessonRefOut(BaseModel):
    id: UUID
    title: str
    slug: str
    visited_at: datetime | None = None
class DashboardCourseOut(BaseModel):
    course_id: UUID
    course_slug: str
    course_title: str
    course_thumbnail: str | None = None
    completed_lessons: int
    total_lessons: int
    progress_percentage: float
    last_visited_lesson: DashboardLessonRefOut | None = None
    next_incomplete_lesson: DashboardLessonRefOut | None = None
    last_activity_at: datetime | None = None
class DashboardOverviewOut(BaseModel):
    student: DashboardStudentOut
    statistics: DashboardStatisticsOut
    courses: list[DashboardCourseOut] = Field(default_factory=list)
class DashboardActivityOut(BaseModel):
    event_type: str
    title: str
    course_title: str
    course_slug: str
    lesson_title: str | None = None
    timestamp: datetime
class WeeklyActivityDayOut(BaseModel):
    date: datetime | str
    completed_lessons: int
    recorded_learning_minutes: int | None = None
    quiz_attempts: int
class WeeklyActivityOut(BaseModel):
    days: list[WeeklyActivityDayOut]
    learning_time_available: bool
class AnalyticsActivityDayOut(BaseModel):
    date: str
    completed_lessons: int
    quiz_attempts: int
    learning_minutes: int | None = None
class AnalyticsCourseProgressOut(BaseModel):
    course_slug: str
    course_title: str
    progress_percentage: float
    completed_lessons: int
    total_lessons: int
class DashboardAnalyticsOut(BaseModel):
    range_start: str
    range_end: str
    activity: list[AnalyticsActivityDayOut]
    completed_lessons: int
    quiz_attempts: int
    quiz_average_score: float | None = None
    current_learning_streak: int
    learning_seconds: int | None = None
    learning_time_available: bool
    course_progress: list[AnalyticsCourseProgressOut]
class AdminLanguageIn(BaseModel):
    name: str = Field(min_length=2,max_length=80); slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",max_length=80); description: str=""; icon: str|None=None; status: str="active"; display_order: int=0
class AdminCategoryIn(BaseModel):
    name: str = Field(min_length=2,max_length=100); slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",max_length=100); description: str=""; status: str="active"; display_order: int=0
class AdminCourseIn(BaseModel):
    title: str = Field(min_length=3,max_length=180); slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",max_length=180); short_description: str=""; description: str=""; target_audience: str=""; technologies: list[str]=Field(default_factory=list); seo_title: str=""; seo_description: str=""; language_id: UUID; category_id: UUID; level: str="beginner"; thumbnail: str|None=None; estimated_duration: int=Field(default=0,ge=0); status: str="draft"; outcomes: list[str]=Field(default_factory=list); requirements: list[str]=Field(default_factory=list)
class AdminCourseFAQIn(BaseModel):
    question: str = Field(min_length=3, max_length=500); answer: str = Field(min_length=1, max_length=10000); position: int = Field(default=0, ge=0); status: str = Field(default="published", pattern=r"^(draft|published|archived)$")
class AdminModuleIn(BaseModel): title: str=Field(min_length=2,max_length=180); position: int=Field(ge=0); description: str=""
class AdminLessonIn(BaseModel): title: str=Field(min_length=2,max_length=180); slug: str=Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",max_length=180); description: str=""; content_en: str=""; content_mm: str|None=None; position: int=Field(ge=0); duration_minutes: int=Field(default=10,ge=0); status: str="draft"
class AdminCodeExampleIn(BaseModel): title: str=Field(min_length=1,max_length=180); language: str=Field(min_length=1,max_length=50); filename: str|None=None; source_code: str; description: str=""; position: int=Field(ge=0)
class PublishDecisionIn(BaseModel): decision: str; note: str=""
class AdminCourseOut(BaseModel):
    model_config=ConfigDict(from_attributes=True); id: UUID; title: str; slug: str; short_description: str; description: str; target_audience: str = ""; technologies: list[str]=Field(default_factory=list); seo_title: str = ""; seo_description: str = ""; language_id: UUID; category_id: UUID; level: str; thumbnail: str|None; estimated_duration: int; status: str; published: bool; outcomes: list[str]=Field(default_factory=list); requirements: list[str]=Field(default_factory=list)
    @field_validator("outcomes","requirements","technologies",mode="before")
    @classmethod
    def split_values(cls,v): return v.split("|") if isinstance(v,str) and v else (v or [])
class AdminPageOut(BaseModel): items: list[AdminCourseOut]; page: int; page_size: int; total: int; pages: int
class BrandingSettings(BaseModel):
    website_name: str = Field(default="Learn-Coding", min_length=2, max_length=120)
    tagline: str = Field(default="Learn to code. Build your future.", max_length=240)
    logo_url: str = Field(default="/branding/tkp.png", max_length=500)
    mobile_logo_url: str = Field(default="/branding/tkp.png", max_length=500)
    favicon_url: str = Field(default="/branding/tkp.png", max_length=500)
    primary_color: str = Field(default="#6366F1", pattern=r"^#[0-9A-Fa-f]{6}$")
    active_navigation_color: str = Field(default="#6366F1", pattern=r"^#[0-9A-Fa-f]{6}$")
    header_background: str = Field(default="#0B1020", pattern=r"^#[0-9A-Fa-f]{6}$")
    footer_branding: str = Field(default="Learn-Coding", max_length=120)

class NavigationItem(BaseModel):
    label: str = Field(min_length=1, max_length=80)
    href: str = Field(pattern=r"^/[A-Za-z0-9/_?=&.-]*$", max_length=240)
    enabled: bool = True
    position: int = Field(ge=0, le=200)
    area: str = Field(default="header", pattern=r"^(header|footer)$")

class NavigationSettings(BaseModel):
    items: list[NavigationItem] = Field(default_factory=list, max_length=100)

class FooterLink(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=80)
    label: str = Field(min_length=1, max_length=100)
    href: str = Field(pattern=r"^(?:/[A-Za-z0-9/_?=&.%-]*|https://[^\s]+)$", max_length=500)
    position: int = Field(default=0, ge=0, le=200)
    enabled: bool = True

class FooterLinkGroup(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=80)
    title: str = Field(min_length=1, max_length=80)
    position: int = Field(default=0, ge=0, le=50)
    enabled: bool = True
    links: list[FooterLink] = Field(default_factory=list, max_length=30)

class FooterSocialLink(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=80)
    platform: str = Field(min_length=1, max_length=40)
    url: str = Field(pattern=r"^https://[^\s]+$", max_length=500)
    icon_key: str = Field(default="globe", pattern=r"^[a-z0-9_-]+$", max_length=40)
    position: int = Field(default=0, ge=0, le=50)
    enabled: bool = True

class FooterSettings(BaseModel):
    tagline: str = Field(default="Learn to code. Build your future.", max_length=240)
    description: str = Field(default="Practical coding education, projects, and tools for your next step.", max_length=600)
    groups: list[FooterLinkGroup] = Field(default_factory=list, max_length=12)
    social_links: list[FooterSocialLink] = Field(default_factory=list, max_length=12)
    newsletter_enabled: bool = False
    newsletter_note: str = Field(default="Newsletter sign-ups are not available yet.", max_length=240)
    copyright_text: str = Field(default="© 2026 Learn-Coding. All rights reserved.", max_length=240)
    status: str = Field(default="published", pattern=r"^(draft|published)$")

class PlatformPageIn(BaseModel):
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=120)
    title: str = Field(min_length=2, max_length=180)
    body: str = Field(default="", max_length=100000)
    status: str = Field(default="draft", pattern=r"^(draft|in_review|published|archived)$")

class PlatformPageOut(PlatformPageIn):
    updated_at: datetime | None = None
