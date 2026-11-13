from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
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
class CourseOut(BaseModel):
    model_config=ConfigDict(from_attributes=True); id: UUID; title: str; slug: str; description: str; level: str; duration_minutes: int; outcomes: list[str]=Field(default_factory=list); language: LanguageOut; category: CategoryOut
    @field_validator("outcomes", mode="before")
    @classmethod
    def split_outcomes(cls, value): return value.split("|") if isinstance(value, str) else value
class CourseDetailOut(CourseOut):
    modules: list[ModuleOut]=Field(default_factory=list)
class PageOut(BaseModel):
    items: list[CourseOut]; page: int; page_size: int; total: int; pages: int
class PathOut(BaseModel):
    model_config=ConfigDict(from_attributes=True); id: UUID; title: str; slug: str; description: str
