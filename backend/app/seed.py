from sqlalchemy import select
from .db import SessionLocal
from .models import CodeExample, Course, CourseCategory, CourseModule, LearningPath, Lesson, ProgrammingLanguage
DATA=[("Python","python","#3776AB"),("JavaScript","javascript","#F7DF1E"),("TypeScript","typescript","#3178C6"),("Java","java","#ED8B00"),("C++","cpp","#00599C"),("PHP","php","#777BB4"),("HTML","html","#E34F26"),("CSS","css","#1572B6"),("SQL","sql","#22C55E")]
def main():
    with SessionLocal() as db:
        category=db.scalar(select(CourseCategory).where(CourseCategory.slug=="programming-fundamentals"))
        if not category: category=CourseCategory(name="Programming Fundamentals",slug="programming-fundamentals"); db.add(category); db.flush()
        for name,slug,color in DATA:
            lang=db.scalar(select(ProgrammingLanguage).where(ProgrammingLanguage.slug==slug))
            if not lang: lang=ProgrammingLanguage(name=name,slug=slug,color=color); db.add(lang); db.flush()
            course=db.scalar(select(Course).where(Course.slug==f"{slug}-foundations"))
            if course: continue
            course=Course(language_id=lang.id,category_id=category.id,title=f"{name} Foundations",slug=f"{slug}-foundations",description=f"Build a practical foundation in {name} with focused lessons and examples.",level="Beginner",duration_minutes=240,outcomes="Understand core syntax|Build small programs|Read documentation",published=True); db.add(course); db.flush()
            module=CourseModule(course_id=course.id,title="Core concepts",order_index=1); db.add(module); db.flush()
            lesson=Lesson(module_id=module.id,title=f"Your first {name} program",slug="first-program",content_en=f"Start with the essentials of {name}. This lesson introduces the language, the core workflow, and a small program you can understand line by line.",content_mm="ဒီသင်ခန်းစာတွင် အခြေခံအကြောင်းအရာများကို လေ့လာမည်ဖြစ်သည်။",order_index=1,published=True); db.add(lesson); db.flush()
            code="print('Hello, CodeMaster!')" if slug=="python" else "// Your first step\nconsole.log('Hello, CodeMaster!');"
            db.add(CodeExample(lesson_id=lesson.id,title="A small first step",language=slug,code=code))
        path=db.scalar(select(LearningPath).where(LearningPath.slug=="developer-foundations"))
        if not path: db.add(LearningPath(title="Developer Foundations",slug="developer-foundations",description="A guided start for new developers.",published=True))
        db.commit()
if __name__=="__main__": main()
