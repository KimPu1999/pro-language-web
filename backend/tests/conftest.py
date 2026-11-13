import os
os.environ["DATABASE_URL"]="sqlite:///./test.db"
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db
from app.auth import _rate_buckets
from app.main import app
from app.models import Course, CourseCategory, CourseModule, Lesson, ProgrammingLanguage
@pytest.fixture()
def client(tmp_path):
    _rate_buckets.clear()
    engine=create_engine(f"sqlite:///{tmp_path}/test.db",connect_args={"check_same_thread":False})
    Base.metadata.create_all(engine); Session=sessionmaker(bind=engine)
    with Session() as db:
        lang=ProgrammingLanguage(name="Python",slug="python",color="#3776AB"); cat=CourseCategory(name="Fundamentals",slug="fundamentals"); db.add_all([lang,cat]); db.flush()
        course=Course(language_id=lang.id,category_id=cat.id,title="Python Foundations",slug="python-foundations",description="Learn Python",level="Beginner",duration_minutes=60,outcomes="Syntax|Practice",published=True); db.add(course); db.flush(); module=CourseModule(course_id=course.id,title="Basics",order_index=1); db.add(module); db.flush(); db.add(Lesson(module_id=module.id,title="Hello",slug="hello",content_en="Hello lesson",content_mm="မြန်မာ",order_index=1,published=True)); db.commit()
    def override():
        with Session() as db: yield db
    app.dependency_overrides[get_db]=override
    test_client=TestClient(app); test_client.session_factory=Session
    yield test_client
    app.dependency_overrides.clear()
