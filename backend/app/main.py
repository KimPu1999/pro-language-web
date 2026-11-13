import logging, math, uuid
from uuid import UUID
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from .config import settings
from .db import get_db
from .models import Course, CourseCategory, CourseModule, LearningPath, Lesson, ProgrammingLanguage
from .schemas import CategoryOut, CourseDetailOut, LanguageOut, ModuleOut, PageOut, PathOut
from .auth_routes import router as auth_router
from .student_routes import router as student_router
from .admin_routes import router as admin_router
from .runner_routes import router as runner_router
from .challenge_routes import router as challenge_router
from .roadmap_routes import router as roadmap_router
from .project_routes import router as project_router
from .ai_routes import router as ai_router
from .gamification_routes import router as gamification_router
from .community_routes import router as community_router
from .live_class_routes import router as live_class_router
from .analytics_routes import router as analytics_router
from .operations_routes import router as operations_router
from .learning_intelligence_routes import router as learning_intelligence_router
from .career_routes import router as career_router
from .collaboration_routes import router as collaboration_router
from .ecosystem_routes import router as ecosystem_router
from .organization_routes import router as organization_router
from .security_routes import router as security_router
from .automation_routes import router as automation_router
from .content_studio_routes import router as content_studio_router
from .lab_routes import router as lab_router
from .realtime_collaboration_routes import router as realtime_collaboration_router
logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger=logging.getLogger("codemaster.api")
app=FastAPI(title="CodeMaster Academy API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"], allow_headers=["Content-Type","X-CSRF-Token"])
@app.middleware("http")
async def request_context(request, call_next):
    request_id=request.headers.get("X-Request-ID") or str(uuid.uuid4())
    response=await call_next(request)
    response.headers["X-Request-ID"]=request_id
    response.headers["X-Content-Type-Options"]="nosniff"
    response.headers["Referrer-Policy"]="strict-origin-when-cross-origin"
    return response
app.include_router(auth_router); app.include_router(student_router); app.include_router(admin_router); app.include_router(runner_router); app.include_router(challenge_router); app.include_router(roadmap_router); app.include_router(project_router); app.include_router(ai_router); app.include_router(gamification_router); app.include_router(community_router); app.include_router(live_class_router)
app.include_router(analytics_router); app.include_router(operations_router)
app.include_router(learning_intelligence_router)
app.include_router(career_router)
app.include_router(collaboration_router)
app.include_router(ecosystem_router)
app.include_router(organization_router)
app.include_router(security_router)
app.include_router(automation_router)
app.include_router(content_studio_router)
app.include_router(lab_router)
app.include_router(realtime_collaboration_router)
@app.get("/api/v1/health")
def health(db: Session=Depends(get_db)): db.execute(select(1)); return {"status":"ok","service":"codemaster-api"}
@app.get("/api/v1/ready")
def readiness(db: Session=Depends(get_db)):
    try:
        db.execute(select(1))
    except Exception as exc:
        logger.warning("readiness database check failed: %s", type(exc).__name__)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Database is not ready") from exc
    return {"status": "ready", "database": "ok", "service": "codemaster-api"}
@app.get("/api/v1/languages",response_model=list[LanguageOut])
def languages(db: Session=Depends(get_db)): return db.scalars(select(ProgrammingLanguage).order_by(ProgrammingLanguage.name)).all()
@app.get("/api/v1/categories",response_model=list[CategoryOut])
def categories(db: Session=Depends(get_db)): return db.scalars(select(CourseCategory).order_by(CourseCategory.name)).all()
def course_query(): return select(Course).options(selectinload(Course.language),selectinload(Course.category)).where(Course.published.is_(True))
@app.get("/api/v1/courses",response_model=PageOut)
def courses(search: str|None=None, language: str|None=None, level: str|None=None, category: str|None=None, page: int=Query(1,ge=1), page_size: int=Query(12,ge=1,le=50), db: Session=Depends(get_db)):
    query=course_query(); count_query=select(func.count()).select_from(Course).where(Course.published.is_(True))
    if search: query=query.where(Course.title.ilike(f"%{search}%")); count_query=count_query.where(Course.title.ilike(f"%{search}%"))
    if language: query=query.join(Course.language).where(ProgrammingLanguage.slug==language); count_query=count_query.join(Course.language).where(ProgrammingLanguage.slug==language)
    if level: query=query.where(Course.level==level); count_query=count_query.where(Course.level==level)
    if category: query=query.join(Course.category).where(CourseCategory.slug==category); count_query=count_query.join(Course.category).where(CourseCategory.slug==category)
    total=db.scalar(count_query) or 0; rows=db.scalars(query.order_by(Course.title).offset((page-1)*page_size).limit(page_size)).all()
    return {"items":rows,"page":page,"page_size":page_size,"total":total,"pages":math.ceil(total/page_size) if total else 0}
@app.get("/api/v1/courses/{slug}",response_model=CourseDetailOut)
def course(slug: str, db: Session=Depends(get_db)):
    row=db.scalar(course_query().options(selectinload(Course.modules).selectinload(CourseModule.lessons).selectinload(Lesson.code_examples)).where(Course.slug==slug))
    if not row: raise HTTPException(404,"Published course not found")
    return row
@app.get("/api/v1/courses/{slug}/modules",response_model=list[ModuleOut])
def modules(slug: str, db: Session=Depends(get_db)):
    row=db.scalar(course_query().where(Course.slug==slug).options(selectinload(Course.modules).selectinload(CourseModule.lessons)))
    if not row: raise HTTPException(404,"Published course not found")
    return row.modules
@app.get("/api/v1/lessons/{lesson_id}",response_model=dict)
def lesson(lesson_id: UUID, db: Session=Depends(get_db)):
    row=db.scalar(select(Lesson).options(selectinload(Lesson.code_examples)).where(Lesson.id==lesson_id,Lesson.published.is_(True)))
    if not row: raise HTTPException(404,"Published lesson not found")
    return row
@app.get("/api/v1/paths",response_model=list[PathOut])
def paths(db: Session=Depends(get_db)): return db.scalars(select(LearningPath).where(LearningPath.published.is_(True)).order_by(LearningPath.title)).all()
