import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base
class UUIDType(TypeDecorator):
    impl = CHAR(36); cache_ok = True
    def process_bind_param(self, value, dialect): return str(value) if value else None
    def process_result_value(self, value, dialect): return uuid.UUID(value) if value else None
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
class User(TimestampMixin, Base):
    __tablename__="users"; id: Mapped[uuid.UUID]=mapped_column(UUIDType,primary_key=True,default=uuid.uuid4); email: Mapped[str]=mapped_column(String(320),unique=True,index=True); password_hash: Mapped[str]=mapped_column(String(255)); display_name: Mapped[str]=mapped_column(String(120))
class ProgrammingLanguage(TimestampMixin, Base):
    __tablename__="programming_languages"; id: Mapped[uuid.UUID]=mapped_column(UUIDType,primary_key=True,default=uuid.uuid4); name: Mapped[str]=mapped_column(String(80),unique=True); slug: Mapped[str]=mapped_column(String(80),unique=True); color: Mapped[str]=mapped_column(String(20),default="#6366F1"); courses=relationship("Course",back_populates="language")
class CourseCategory(TimestampMixin, Base):
    __tablename__="course_categories"; id: Mapped[uuid.UUID]=mapped_column(UUIDType,primary_key=True,default=uuid.uuid4); name: Mapped[str]=mapped_column(String(100),unique=True); slug: Mapped[str]=mapped_column(String(100),unique=True); courses=relationship("Course",back_populates="category")
class Course(TimestampMixin, Base):
    __tablename__="courses"; __table_args__=(Index("ix_courses_published_level","published","level"),); id: Mapped[uuid.UUID]=mapped_column(UUIDType,primary_key=True,default=uuid.uuid4); language_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("programming_languages.id")); category_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("course_categories.id")); title: Mapped[str]=mapped_column(String(180)); slug: Mapped[str]=mapped_column(String(180),unique=True); description: Mapped[str]=mapped_column(Text); level: Mapped[str]=mapped_column(String(30)); duration_minutes: Mapped[int]=mapped_column(Integer); outcomes: Mapped[str]=mapped_column(Text,default=""); published: Mapped[bool]=mapped_column(Boolean,default=False,index=True); language=relationship("ProgrammingLanguage",back_populates="courses"); category=relationship("CourseCategory",back_populates="courses"); modules=relationship("CourseModule",back_populates="course",order_by="CourseModule.order_index")
class CourseModule(TimestampMixin, Base):
    __tablename__="course_modules"; __table_args__=(UniqueConstraint("course_id","order_index"),); id: Mapped[uuid.UUID]=mapped_column(UUIDType,primary_key=True,default=uuid.uuid4); course_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("courses.id",ondelete="CASCADE")); title: Mapped[str]=mapped_column(String(180)); order_index: Mapped[int]=mapped_column(Integer); course=relationship("Course",back_populates="modules"); lessons=relationship("Lesson",back_populates="module",order_by="Lesson.order_index")
class Lesson(TimestampMixin, Base):
    __tablename__="lessons"; __table_args__=(UniqueConstraint("module_id","order_index"),Index("ix_lessons_published","published")); id: Mapped[uuid.UUID]=mapped_column(UUIDType,primary_key=True,default=uuid.uuid4); module_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("course_modules.id",ondelete="CASCADE")); title: Mapped[str]=mapped_column(String(180)); slug: Mapped[str]=mapped_column(String(180)); content_en: Mapped[str]=mapped_column(Text); content_mm: Mapped[str|None]=mapped_column(Text,nullable=True); order_index: Mapped[int]=mapped_column(Integer); published: Mapped[bool]=mapped_column(Boolean,default=False); module=relationship("CourseModule",back_populates="lessons"); code_examples=relationship("CodeExample",back_populates="lesson")
class CodeExample(TimestampMixin, Base):
    __tablename__="code_examples"; id: Mapped[uuid.UUID]=mapped_column(UUIDType,primary_key=True,default=uuid.uuid4); lesson_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("lessons.id",ondelete="CASCADE")); title: Mapped[str]=mapped_column(String(180)); language: Mapped[str]=mapped_column(String(50)); code: Mapped[str]=mapped_column(Text); lesson=relationship("Lesson",back_populates="code_examples")
class Enrollment(TimestampMixin, Base):
    __tablename__="enrollments"; __table_args__=(UniqueConstraint("user_id","course_id"),); id: Mapped[uuid.UUID]=mapped_column(UUIDType,primary_key=True,default=uuid.uuid4); user_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("users.id")); course_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("courses.id"))
class LessonProgress(TimestampMixin, Base):
    __tablename__="lesson_progress"; __table_args__=(UniqueConstraint("user_id","lesson_id"),); id: Mapped[uuid.UUID]=mapped_column(UUIDType,primary_key=True,default=uuid.uuid4); user_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("users.id")); lesson_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("lessons.id")); completed: Mapped[bool]=mapped_column(Boolean,default=False)
class LearningPath(TimestampMixin, Base):
    __tablename__="learning_paths"; id: Mapped[uuid.UUID]=mapped_column(UUIDType,primary_key=True,default=uuid.uuid4); title: Mapped[str]=mapped_column(String(180)); slug: Mapped[str]=mapped_column(String(180),unique=True); description: Mapped[str]=mapped_column(Text); published: Mapped[bool]=mapped_column(Boolean,default=False)
class LearningPathCourse(Base):
    __tablename__="learning_path_courses"; __table_args__=(UniqueConstraint("path_id","course_id"),); path_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("learning_paths.id",ondelete="CASCADE"),primary_key=True); course_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("courses.id",ondelete="CASCADE"),primary_key=True); order_index: Mapped[int]=mapped_column(Integer)
