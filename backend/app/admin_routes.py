import json, math
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from .auth import current_user, require_csrf
from .db import get_db
from .models import AdminAuditLog, Course, CourseCategory, CourseInstructor, CourseModule, CourseRevision, Lesson, CodeExample, LessonQuiz, QuizQuestion, ProgrammingLanguage, PublishingReview, User
from .rbac import PLATFORM_ADMIN_ROLES, require_platform_admin
from .schemas import AdminCategoryIn, AdminCodeExampleIn, AdminCourseIn, AdminCourseOut, AdminLanguageIn, AdminLessonIn, AdminModuleIn, AdminPageOut, AdminQuizQuestionIn, PublishDecisionIn
router=APIRouter(prefix="/api/v1/admin",tags=["admin"])
ADMIN=PLATFORM_ADMIN_ROLES
def admin_user(user: User=Depends(current_user)):
    if user.role not in ADMIN and user.role!="instructor": raise HTTPException(403,"Admin access required")
    return user
def full_admin(user: User=Depends(current_user)):
    return require_platform_admin(user)
def audit(db, actor, action, entity_type, entity_id=None): db.add(AdminAuditLog(actor_id=actor.id,action=action,entity_type=entity_type,entity_id=entity_id))
def course_out(course): return {"id":course.id,"title":course.title,"slug":course.slug,"short_description":course.short_description or "","description":course.description,"language_id":course.language_id,"category_id":course.category_id,"level":course.level,"thumbnail":course.thumbnail,"estimated_duration":course.duration_minutes,"status":course.status or ("published" if course.published else "draft"),"published":course.published,"outcomes":course.outcomes,"requirements":course.requirements}
def load_course(db, course_id): return db.scalar(select(Course).options(selectinload(Course.modules).selectinload(CourseModule.lessons).selectinload(Lesson.code_examples)).where(Course.id==course_id))
def can_edit(course, user, db):
    if user.role in ADMIN: return True
    if user.role!="instructor": return False
    return course.created_by==user.id or db.scalar(select(CourseInstructor).where(CourseInstructor.course_id==course.id,CourseInstructor.user_id==user.id)) is not None
def require_edit(course_id, user, db):
    course=load_course(db,course_id)
    if not course: raise HTTPException(404,"Course not found")
    if not can_edit(course,user,db): raise HTTPException(403,"Course ownership required")
    return course
def quiz_question_out(row):
    return {"id": row.id, "prompt": row.prompt, "question_type": row.question_type, "options": json.loads(row.options_json or "[]"), "correct_answer": row.correct_answer, "explanation": row.explanation, "position": row.position}
def lesson_for_edit(lesson_id, user, db):
    lesson=db.get(Lesson, lesson_id)
    if not lesson: raise HTTPException(404,"Lesson not found")
    module=db.get(CourseModule, lesson.module_id)
    if not module: raise HTTPException(404,"Course module not found")
    require_edit(module.course_id, user, db)
    return lesson
@router.get("/dashboard")
def dashboard(user: User=Depends(full_admin), db: Session=Depends(get_db)):
    return {"total_courses":db.scalar(select(func.count(Course.id))) or 0,"published_courses":db.scalar(select(func.count(Course.id)).where(Course.published.is_(True))) or 0,"draft_courses":db.scalar(select(func.count(Course.id)).where(Course.status.in_(["draft","in_review"]))) or 0,"total_students":db.scalar(select(func.count(User.id)).where(User.role=="student")) or 0,"total_instructors":db.scalar(select(func.count(User.id)).where(User.role=="instructor")) or 0,"recent_courses":[course_out(x) for x in db.scalars(select(Course).order_by(Course.updated_at.desc()).limit(5)).all()],"pending_reviews":db.scalar(select(func.count(PublishingReview.id)).where(PublishingReview.decision=="pending")) or 0,"recent_activity":[]}
@router.get("/languages")
def list_languages(search: str|None=None, page: int=Query(1,ge=1), page_size: int=Query(20,ge=1,le=100), user: User=Depends(admin_user), db: Session=Depends(get_db)):
    q=select(ProgrammingLanguage); count=select(func.count()).select_from(ProgrammingLanguage)
    if search: q=q.where(ProgrammingLanguage.name.ilike(f"%{search}%")); count=count.where(ProgrammingLanguage.name.ilike(f"%{search}%"))
    total=db.scalar(count) or 0; return {"items":db.scalars(q.order_by(ProgrammingLanguage.display_order,ProgrammingLanguage.name).offset((page-1)*page_size).limit(page_size)).all(),"page":page,"page_size":page_size,"total":total,"pages":math.ceil(total/page_size) if total else 0}
@router.post("/languages",status_code=201)
def create_language(payload: AdminLanguageIn, user: User=Depends(full_admin), _:None=Depends(require_csrf), db: Session=Depends(get_db)):
    if db.scalar(select(ProgrammingLanguage).where(ProgrammingLanguage.slug==payload.slug)): raise HTTPException(409,"Slug already exists")
    row=ProgrammingLanguage(**payload.model_dump()); db.add(row); audit(db,user,"language_created","language",row.id); db.commit(); return row
@router.patch("/languages/{language_id}")
def update_language(language_id: UUID,payload: AdminLanguageIn,user: User=Depends(full_admin),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(ProgrammingLanguage,language_id)
    if not row: raise HTTPException(404,"Language not found")
    duplicate=db.scalar(select(ProgrammingLanguage).where(ProgrammingLanguage.slug==payload.slug,ProgrammingLanguage.id!=language_id))
    if duplicate: raise HTTPException(409,"Slug already exists")
    for key,value in payload.model_dump().items(): setattr(row,key,value)
    audit(db,user,"language_updated","language",row.id); db.commit(); return row
@router.post("/languages/{language_id}/deactivate")
def deactivate_language(language_id:UUID,user:User=Depends(full_admin),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(ProgrammingLanguage,language_id)
    if not row: raise HTTPException(404,"Language not found")
    row.status="inactive"; audit(db,user,"language_deactivated","language",row.id); db.commit(); return row
@router.get("/categories")
def list_categories(search: str|None=None, page: int=Query(1,ge=1), page_size: int=Query(20,ge=1,le=100), user: User=Depends(admin_user), db: Session=Depends(get_db)):
    q=select(CourseCategory); count=select(func.count()).select_from(CourseCategory)
    if search: q=q.where(CourseCategory.name.ilike(f"%{search}%")); count=count.where(CourseCategory.name.ilike(f"%{search}%"))
    total=db.scalar(count) or 0; return {"items":db.scalars(q.order_by(CourseCategory.display_order,CourseCategory.name).offset((page-1)*page_size).limit(page_size)).all(),"page":page,"page_size":page_size,"total":total,"pages":math.ceil(total/page_size) if total else 0}
@router.post("/categories",status_code=201)
def create_category(payload: AdminCategoryIn,user: User=Depends(full_admin),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if db.scalar(select(CourseCategory).where(CourseCategory.slug==payload.slug)): raise HTTPException(409,"Slug already exists")
    row=CourseCategory(**payload.model_dump()); db.add(row); audit(db,user,"category_created","category",row.id); db.commit(); return row
@router.patch("/categories/{category_id}")
def update_category(category_id:UUID,payload:AdminCategoryIn,user:User=Depends(full_admin),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(CourseCategory,category_id)
    if not row: raise HTTPException(404,"Category not found")
    duplicate=db.scalar(select(CourseCategory).where(CourseCategory.slug==payload.slug,CourseCategory.id!=category_id))
    if duplicate: raise HTTPException(409,"Slug already exists")
    for key,value in payload.model_dump().items(): setattr(row,key,value)
    audit(db,user,"category_updated","category",row.id); db.commit(); return row
@router.post("/categories/{category_id}/archive")
def archive_category(category_id:UUID,user:User=Depends(full_admin),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(CourseCategory,category_id)
    if not row: raise HTTPException(404,"Category not found")
    row.status="archived"; audit(db,user,"category_archived","category",row.id); db.commit(); return row
@router.get("/courses",response_model=AdminPageOut)
def list_courses(search:str|None=None,language_id:UUID|None=None,level:str|None=None,status:str|None=None,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),user:User=Depends(admin_user),db:Session=Depends(get_db)):
    q=select(Course); count=select(func.count()).select_from(Course)
    for stmt in [q,count]:
        if search: stmt=stmt.where(Course.title.ilike(f"%{search}%"))
    if search: q=q.where(Course.title.ilike(f"%{search}%")); count=count.where(Course.title.ilike(f"%{search}%"))
    if language_id: q=q.where(Course.language_id==language_id); count=count.where(Course.language_id==language_id)
    if level: q=q.where(Course.level==level); count=count.where(Course.level==level)
    if status: q=q.where(Course.status==status); count=count.where(Course.status==status)
    total=db.scalar(count) or 0; rows=db.scalars(q.order_by(Course.updated_at.desc()).offset((page-1)*page_size).limit(page_size)).all(); return {"items":[course_out(x) for x in rows],"page":page,"page_size":page_size,"total":total,"pages":math.ceil(total/page_size) if total else 0}
@router.post("/courses",response_model=AdminCourseOut,status_code=201)
def create_course(payload:AdminCourseIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if db.scalar(select(Course).where(Course.slug==payload.slug)): raise HTTPException(409,"Slug already exists")
    if not db.get(ProgrammingLanguage,payload.language_id) or not db.get(CourseCategory,payload.category_id): raise HTTPException(422,"Language and category are required")
    row=Course(title=payload.title,slug=payload.slug,short_description=payload.short_description,description=payload.description,language_id=payload.language_id,category_id=payload.category_id,level=payload.level,thumbnail=payload.thumbnail,duration_minutes=payload.estimated_duration,status="draft",published=False,outcomes="|".join(payload.outcomes),requirements="|".join(payload.requirements),created_by=user.id,updated_by=user.id); db.add(row); db.flush(); audit(db,user,"course_created","course",row.id); db.commit(); return course_out(row)
@router.get("/courses/{course_id}/builder",response_model=AdminCourseOut)
def builder(course_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)): return course_out(require_edit(course_id,user,db))
@router.patch("/courses/{course_id}",response_model=AdminCourseOut)
def update_course(course_id:UUID,payload:AdminCourseIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=require_edit(course_id,user,db); duplicate=db.scalar(select(Course).where(Course.slug==payload.slug,Course.id!=course_id))
    if duplicate: raise HTTPException(409,"Slug already exists")
    for key,value in payload.model_dump().items(): setattr(row,key,value if key not in {"outcomes","requirements","estimated_duration"} else value)
    row.duration_minutes=payload.estimated_duration; row.outcomes="|".join(payload.outcomes); row.requirements="|".join(payload.requirements); row.updated_by=user.id; db.add(CourseRevision(course_id=row.id,changed_by=user.id,status=row.status,snapshot_json=json.dumps(course_out(row),default=str))); audit(db,user,"course_updated","course",row.id); db.commit(); return course_out(row)
@router.post("/courses/{course_id}/duplicate",response_model=AdminCourseOut,status_code=201)
def duplicate_course(course_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    source=require_edit(course_id,user,db); row=Course(title=f"{source.title} Copy",slug=f"{source.slug}-copy",short_description=source.short_description,description=source.description,language_id=source.language_id,category_id=source.category_id,level=source.level,duration_minutes=source.duration_minutes,status="draft",published=False,outcomes=source.outcomes,requirements=source.requirements,created_by=user.id,updated_by=user.id); db.add(row); db.flush(); audit(db,user,"course_duplicated","course",row.id); db.commit(); return course_out(row)
@router.post("/courses/{course_id}/archive",response_model=AdminCourseOut)
def archive_course(course_id:UUID,user:User=Depends(full_admin),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=require_edit(course_id,user,db); row.status="archived"; row.published=False; row.updated_by=user.id; audit(db,user,"course_archived","course",row.id); db.commit(); return course_out(row)
@router.get("/courses/{course_id}/curriculum")
def curriculum(course_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)):
    row=require_edit(course_id,user,db); return [{"id":m.id,"title":m.title,"position":m.order_index,"lessons":[{"id":l.id,"title":l.title,"slug":l.slug,"description":l.description,"position":l.order_index,"status":l.status,"content_en":l.content_en,"content_mm":l.content_mm,"duration_minutes":l.duration_minutes} for l in m.lessons]} for m in row.modules]
@router.post("/courses/{course_id}/modules",status_code=201)
def create_module(course_id:UUID,payload:AdminModuleIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    course=require_edit(course_id,user,db); row=CourseModule(course_id=course.id,title=payload.title,order_index=payload.position); db.add(row); audit(db,user,"module_created","course_module",row.id); db.commit(); return {"id":row.id,"title":row.title,"position":row.order_index}
@router.post("/modules/{module_id}/lessons",status_code=201)
def create_lesson(module_id:UUID,payload:AdminLessonIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    module=db.get(CourseModule,module_id)
    if not module: raise HTTPException(404,"Module not found")
    require_edit(module.course_id,user,db); row=Lesson(module_id=module.id,title=payload.title,slug=payload.slug,description=payload.description,content_en=payload.content_en,content_mm=payload.content_mm,order_index=payload.position,duration_minutes=payload.duration_minutes,status=payload.status,published=payload.status=="published"); db.add(row); db.commit(); return {"id":row.id,"title":row.title,"slug":row.slug}
@router.patch("/lessons/{lesson_id}")
def update_lesson(lesson_id:UUID,payload:AdminLessonIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(Lesson,lesson_id)
    if not row: raise HTTPException(404,"Lesson not found")
    module=db.get(CourseModule,row.module_id); require_edit(module.course_id,user,db)
    row.title=payload.title; row.slug=payload.slug; row.description=payload.description; row.content_en=payload.content_en; row.content_mm=payload.content_mm; row.order_index=payload.position; row.duration_minutes=payload.duration_minutes; row.status=payload.status; row.published=payload.status=="published"; db.commit(); return {"id":row.id,"title":row.title,"status":row.status}
@router.post("/lessons/{lesson_id}/examples",status_code=201)
def create_example(lesson_id:UUID,payload:AdminCodeExampleIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    lesson=db.get(Lesson,lesson_id)
    if not lesson: raise HTTPException(404,"Lesson not found")
    module=db.get(CourseModule,lesson.module_id); require_edit(module.course_id,user,db); row=CodeExample(lesson_id=lesson.id,title=payload.title,language=payload.language,filename=payload.filename,code=payload.source_code,description=payload.description,position=payload.position); db.add(row); db.commit(); return {"id":row.id,"title":row.title}
@router.get("/lessons/{lesson_id}/examples")
def admin_examples(lesson_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)):
    lesson=lesson_for_edit(lesson_id,user,db)
    return [{"id":str(row.id),"title":row.title,"language":row.language,"filename":row.filename,"source_code":row.code,"description":row.description,"position":row.position} for row in db.scalars(select(CodeExample).where(CodeExample.lesson_id==lesson.id).order_by(CodeExample.position)).all()]
@router.patch("/examples/{example_id}")
def update_example(example_id:UUID,payload:AdminCodeExampleIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(CodeExample,example_id)
    if not row: raise HTTPException(404,"Example not found")
    lesson_for_edit(row.lesson_id,user,db)
    row.title=payload.title; row.language=payload.language; row.filename=payload.filename; row.code=payload.source_code; row.description=payload.description; row.position=payload.position
    audit(db,user,"example_updated","code_example",row.id); db.commit(); return {"id":row.id,"title":row.title,"position":row.position}
@router.get("/lessons/{lesson_id}/quiz")
def admin_quiz(lesson_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)):
    lesson=lesson_for_edit(lesson_id,user,db)
    quiz=db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id==lesson.id))
    if not quiz: return {"id":None,"lesson_id":lesson.id,"title":f"{lesson.title} quiz","explanation":"","questions":[]}
    questions=db.scalars(select(QuizQuestion).where(QuizQuestion.quiz_id==quiz.id).order_by(QuizQuestion.position)).all()
    return {"id":quiz.id,"lesson_id":lesson.id,"title":quiz.title,"explanation":quiz.explanation,"questions":[quiz_question_out(q) for q in questions]}
@router.post("/lessons/{lesson_id}/quiz/questions",status_code=201)
def create_quiz_question(lesson_id:UUID,payload:AdminQuizQuestionIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    lesson=lesson_for_edit(lesson_id,user,db)
    quiz=db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id==lesson.id))
    if not quiz:
        quiz=LessonQuiz(lesson_id=lesson.id,title=f"{lesson.title} quiz",explanation="",status="published"); db.add(quiz); db.flush()
    if db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id==quiz.id,QuizQuestion.position==payload.position)):
        raise HTTPException(409,"A question already exists at that position")
    row=QuizQuestion(quiz_id=quiz.id,prompt=payload.prompt,question_type=payload.question_type,options_json=json.dumps(payload.options),correct_answer=payload.correct_answer,explanation=payload.explanation,position=payload.position)
    db.add(row); audit(db,user,"quiz_question_created","quiz_question",row.id); db.commit(); return quiz_question_out(row)
@router.patch("/quiz/questions/{question_id}")
def update_quiz_question(question_id:UUID,payload:AdminQuizQuestionIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(QuizQuestion,question_id)
    if not row: raise HTTPException(404,"Quiz question not found")
    quiz=db.get(LessonQuiz,row.quiz_id)
    if not quiz: raise HTTPException(404,"Quiz not found")
    lesson_for_edit(quiz.lesson_id,user,db)
    duplicate=db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id==quiz.id,QuizQuestion.position==payload.position,QuizQuestion.id!=row.id))
    if duplicate: raise HTTPException(409,"A question already exists at that position")
    row.prompt=payload.prompt; row.question_type=payload.question_type; row.options_json=json.dumps(payload.options); row.correct_answer=payload.correct_answer; row.explanation=payload.explanation; row.position=payload.position
    audit(db,user,"quiz_question_updated","quiz_question",row.id); db.commit(); return quiz_question_out(row)
@router.post("/courses/{course_id}/publish")
def publish(course_id:UUID,payload:PublishDecisionIn,user:User=Depends(full_admin),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=require_edit(course_id,user,db); published_lessons=db.scalar(select(func.count(Lesson.id)).join(CourseModule).where(CourseModule.course_id==row.id,Lesson.published.is_(True),func.length(func.trim(Lesson.content_en))>0)) or 0; modules=db.scalar(select(func.count(CourseModule.id)).where(CourseModule.course_id==row.id)) or 0
    if payload.decision=="publish" and (not row.title.strip() or not row.slug.strip() or not row.language_id or modules<1 or published_lessons<1): raise HTTPException(422,"Course needs a title, language, module, and published English lesson")
    row.status="published" if payload.decision=="publish" else ("draft" if payload.decision=="return" else "in_review"); row.published=row.status=="published"; row.updated_by=user.id; db.add(PublishingReview(course_id=row.id,reviewer_id=user.id,decision=payload.decision,note=payload.note)); audit(db,user,f"course_{row.status}","course",row.id); db.commit(); return course_out(row)
