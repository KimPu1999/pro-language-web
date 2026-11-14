from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
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
    model_config=ConfigDict(from_attributes=True); id: UUID; title: str; slug: str; description: str; level: str; duration_minutes: int; status: str; outcomes: list[str]=Field(default_factory=list); requirements: list[str]=Field(default_factory=list); language: LanguageOut; category: CategoryOut
    @field_validator("outcomes", mode="before")
    @classmethod
    def split_outcomes(cls, value): return value.split("|") if isinstance(value, str) else value
    @field_validator("requirements", mode="before")
    @classmethod
    def split_requirements(cls, value): return value.split("|") if isinstance(value, str) else value
class CourseDetailOut(CourseOut):
    modules: list[ModuleOut]=Field(default_factory=list)
class CourseLearningOut(CourseOut):
    modules: list[LearningModuleOut]=Field(default_factory=list)
class PageOut(BaseModel):
    items: list[CourseOut]; page: int; page_size: int; total: int; pages: int
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
    id: UUID; course: CourseOut; completed_lessons: int; total_lessons: int; progress_percent: float; last_lesson_slug: str|None
class ProgressIn(BaseModel): completed: bool
class DashboardOut(BaseModel): enrollments: list[EnrollmentOut]; completed_lessons: int; overall_progress: float; recent_activity: list[dict]
class AdminLanguageIn(BaseModel):
    name: str = Field(min_length=2,max_length=80); slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",max_length=80); description: str=""; icon: str|None=None; status: str="active"; display_order: int=0
class AdminCategoryIn(BaseModel):
    name: str = Field(min_length=2,max_length=100); slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",max_length=100); description: str=""; status: str="active"; display_order: int=0
class AdminCourseIn(BaseModel):
    title: str = Field(min_length=3,max_length=180); slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",max_length=180); short_description: str=""; description: str=""; language_id: UUID; category_id: UUID; level: str="beginner"; thumbnail: str|None=None; estimated_duration: int=Field(default=0,ge=0); status: str="draft"; outcomes: list[str]=Field(default_factory=list); requirements: list[str]=Field(default_factory=list)
class AdminModuleIn(BaseModel): title: str=Field(min_length=2,max_length=180); position: int=Field(ge=0); description: str=""
class AdminLessonIn(BaseModel): title: str=Field(min_length=2,max_length=180); slug: str=Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",max_length=180); description: str=""; content_en: str=""; content_mm: str|None=None; position: int=Field(ge=0); duration_minutes: int=Field(default=10,ge=0); status: str="draft"
class AdminCodeExampleIn(BaseModel): title: str=Field(min_length=1,max_length=180); language: str=Field(min_length=1,max_length=50); filename: str|None=None; source_code: str; description: str=""; position: int=Field(ge=0)
class PublishDecisionIn(BaseModel): decision: str; note: str=""
class AdminCourseOut(BaseModel):
    model_config=ConfigDict(from_attributes=True); id: UUID; title: str; slug: str; short_description: str; description: str; language_id: UUID; category_id: UUID; level: str; thumbnail: str|None; estimated_duration: int; status: str; published: bool; outcomes: list[str]=Field(default_factory=list); requirements: list[str]=Field(default_factory=list)
    @field_validator("outcomes","requirements",mode="before")
    @classmethod
    def split_values(cls,v): return v.split("|") if isinstance(v,str) and v else (v or [])
class AdminPageOut(BaseModel): items: list[AdminCourseOut]; page: int; page_size: int; total: int; pages: int
