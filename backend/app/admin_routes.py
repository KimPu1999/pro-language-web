import json, math
from datetime import datetime, timezone
from uuid import UUID, uuid4
from fastapi import APIRouter, Cookie, Depends, File, HTTPException, Query, Request, Response, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from .auth import SESSION_COOKIE, check_rate_limit, clear_auth_cookies, create_session, current_user, hash_token, normalize_email, now, require_csrf, verify_password
from .db import get_db
from .models import AdminAuditLog, AuthSession, CareerRoadmap, Challenge, CodeExample, Course, CourseCategory, CourseFAQ, CourseInstructor, CourseModule, CourseRevision, Enrollment, Lesson, LessonProgress, LessonQuiz, LessonRevision, PlatformSetting, ProgrammingLanguage, ProjectTemplate, PublishingReview, QuizAttempt, QuizQuestion, User
from .rbac import CONTENT_ADMIN_ROLES, PLATFORM_ADMIN_ROLES, require_platform_admin
from .schemas import AdminCategoryIn, AdminCodeExampleIn, AdminCourseFAQIn, AdminCourseIn, AdminCourseOut, AdminLanguageIn, AdminLessonIn, AdminModuleIn, AdminPageOut, AdminQuizQuestionIn, BrandingSettings, CurriculumOrderIn, FooterSettings, HomepageAnnouncement, HomepageSectionsIn, HomepageSettings, LoginIn, NavigationSettings, PlatformPageIn, PlatformPageOut, PublishDecisionIn
from .footer_config import FOOTER_DRAFT_KEY, FOOTER_KEY, read_footer, validate_footer
from .media_storage import remove_file_if_safe, save_course_image
router=APIRouter(prefix="/api/v1/admin",tags=["admin"])
ADMIN=PLATFORM_ADMIN_ROLES
BRANDING_KEY="branding"
DEFAULT_BRANDING=BrandingSettings().model_dump()
HOMEPAGE_DRAFT_KEY="homepage:draft"
HOMEPAGE_PUBLISHED_KEY="homepage:published"
HOMEPAGE_REVISION_PREFIX="homepage:revision:"
DEFAULT_HOMEPAGE=HomepageSettings().model_dump(mode="json")
def admin_user(user: User=Depends(current_user)):
    if user.role not in CONTENT_ADMIN_ROLES: raise HTTPException(403,"Admin access required")
    return user
def full_admin(user: User=Depends(current_user)):
    return require_platform_admin(user)
def audit(db, actor, action, entity_type, entity_id=None): db.add(AdminAuditLog(actor_id=actor.id,action=action,entity_type=entity_type,entity_id=entity_id))
def cleanup_course_thumbnail(db, url: str|None, course_id: UUID):
    if url and not db.scalar(select(Course.id).where(Course.thumbnail==url, Course.id!=course_id)):
        remove_file_if_safe(url)
def branding_value(db):
    row=db.scalar(select(PlatformSetting).where(PlatformSetting.key==BRANDING_KEY))
    if not row: return DEFAULT_BRANDING.copy()
    try: return BrandingSettings(**{**DEFAULT_BRANDING, **json.loads(row.value_json or "{}")}).model_dump()
    except (TypeError, ValueError, json.JSONDecodeError): return DEFAULT_BRANDING.copy()
def homepage_value(db, key=HOMEPAGE_PUBLISHED_KEY):
    row=db.scalar(select(PlatformSetting).where(PlatformSetting.key==key))
    if not row: return HomepageSettings.model_validate(DEFAULT_HOMEPAGE)
    try: return normalize_homepage(HomepageSettings.model_validate({**DEFAULT_HOMEPAGE, **json.loads(row.value_json or "{}")}))
    except (TypeError, ValueError, json.JSONDecodeError): return HomepageSettings.model_validate(DEFAULT_HOMEPAGE)
def homepage_choices(db):
    courses=db.scalars(select(Course).where(Course.published.is_(True)).order_by(Course.title).limit(100)).all()
    lessons=db.execute(select(Lesson, CourseModule, Course).join(CourseModule, Lesson.module_id==CourseModule.id).join(Course, CourseModule.course_id==Course.id).where(Course.published.is_(True), Lesson.published.is_(True), Lesson.status!="archived").order_by(Course.title, CourseModule.order_index, Lesson.order_index).limit(200)).all()
    projects=db.scalars(select(ProjectTemplate).where(ProjectTemplate.published.is_(True)).order_by(ProjectTemplate.title).limit(100)).all()
    challenges=db.scalars(select(Challenge).where(Challenge.published.is_(True)).order_by(Challenge.title).limit(100)).all()
    paths=db.scalars(select(CareerRoadmap).where(CareerRoadmap.published.is_(True)).order_by(CareerRoadmap.title).limit(100)).all()
    return {"courses":[{"id":row.id,"title":row.title,"slug":row.slug} for row in courses],"lessons":[{"id":lesson.id,"title":lesson.title,"slug":lesson.slug,"course_id":course.id,"course_slug":course.slug,"course_title":course.title,"module_title":module.title,"duration_minutes":lesson.duration_minutes} for lesson,module,course in lessons],"projects":[{"id":row.id,"title":row.title,"slug":row.slug,"description":row.description_en,"estimated_hours":row.estimated_hours} for row in projects],"challenges":[{"id":row.id,"title":row.title,"slug":row.slug,"description":row.description_en,"difficulty":row.difficulty} for row in challenges],"paths":[{"id":row.id,"title":row.title,"slug":row.slug,"description":row.description_en,"estimated_hours":row.estimated_hours} for row in paths]}
def normalize_homepage(settings: HomepageSettings):
    values=settings.model_dump(mode="json")
    if values["announcement"] and not values["announcements"]:
        values["announcements"]=[{"id":"legacy-announcement","title":values["announcement"],"description":"","cta_label":"","cta_href":"/","visible":True,"display_priority":0,"status":"published"}]
    known={"hero":"hero","featured-courses":"featured_courses","new-courses":"new_courses","featured-lessons":"featured_lessons","learning-paths":"learning_paths","projects":"projects","challenges":"challenges","announcements":"announcement"}
    sections=[]
    for index, section in enumerate(values["sections"]):
        section["id"] = section.get("id") or section["key"]
        section["type"] = section.get("type") if section.get("type") and section.get("type") != "custom" else known.get(section["key"], "custom")
        section["display_order"] = index
        sections.append(section)
    values["sections"]=sections
    return HomepageSettings.model_validate(values)
def validate_homepage(db, settings: HomepageSettings):
    settings=normalize_homepage(settings)
    for field in ("featured_course_ids","new_course_ids","featured_lesson_ids","featured_path_ids","featured_project_ids","featured_challenge_ids"):
        values=getattr(settings,field)
        if len(values) != len(set(values)): raise HTTPException(422,f"Duplicate references are not allowed in {field}")
    for field in ("hero_background_image","hero_illustration","social_image_url"):
        value=getattr(settings,field)
        if value and (not value.startswith("/") or value.startswith("//")): raise HTTPException(422,"Homepage media must use an internal path")
    if len({section.key for section in settings.sections}) != len(settings.sections): raise HTTPException(422,"Homepage section keys must be unique")
    for announcement in settings.announcements:
        if announcement.image_url and (not announcement.image_url.startswith("/") or announcement.image_url.startswith("//")): raise HTTPException(422,"Announcement images must use an internal path")
        if announcement.ends_at and announcement.starts_at and announcement.ends_at <= announcement.starts_at: raise HTTPException(422,"Announcement end date must be after its start date")
    checks=(("featured_course_ids",Course,"published"),("new_course_ids",Course,"published"),("featured_lesson_ids",Lesson,"published"),("featured_path_ids",CareerRoadmap,"published"),("featured_project_ids",ProjectTemplate,"published"),("featured_challenge_ids",Challenge,"published"))
    for field, model, publication_field in checks:
        ids=getattr(settings,field)
        if not ids: continue
        column=getattr(model,publication_field)
        found=set(db.scalars(select(model.id).where(model.id.in_(ids),column.is_(True))).all())
        if found != set(ids): raise HTTPException(422,f"All {field.replace('_',' ')} must reference published content")
    if settings.featured_lesson_ids:
        valid=set(db.scalars(select(Lesson.id).join(CourseModule).join(Course).where(Lesson.id.in_(settings.featured_lesson_ids),Lesson.published.is_(True),Course.published.is_(True))).all())
        if valid != set(settings.featured_lesson_ids): raise HTTPException(422,"Featured lessons must belong to published courses")
    return settings
def record_homepage_revision(db, user, settings, action):
    revision_id=uuid4()
    snapshot={"id":str(revision_id),"action":action,"created_at":datetime.now(timezone.utc).isoformat(),"snapshot":settings.model_dump(mode="json")}
    db.add(PlatformSetting(key=f"{HOMEPAGE_REVISION_PREFIX}{revision_id}",value_json=json.dumps(snapshot),updated_by=user.id))
    return revision_id
def homepage_revisions(db):
    rows=db.scalars(select(PlatformSetting).where(PlatformSetting.key.like(f"{HOMEPAGE_REVISION_PREFIX}%")).order_by(PlatformSetting.updated_at.desc()).limit(50)).all()
    revisions=[]
    for row in rows:
        try:
            value=json.loads(row.value_json or "{}")
            revisions.append({"id":value.get("id",row.key.removeprefix(HOMEPAGE_REVISION_PREFIX)),"action":value.get("action","draft_saved"),"created_at":value.get("created_at",row.updated_at),"status":value.get("snapshot",{}).get("status","draft")})
        except (TypeError,ValueError,json.JSONDecodeError): continue
    return revisions
def public_records(db, settings):
    def selected(model, ids):
        if not ids: return []
        rows=db.scalars(select(model).where(model.id.in_(ids))).all(); by_id={str(row.id):row for row in rows}; return [by_id[str(item)] for item in ids if str(item) in by_id]
    courses=selected(Course,settings.featured_course_ids)
    lessons=selected(Lesson,settings.featured_lesson_ids)
    paths=selected(CareerRoadmap,settings.featured_path_ids)
    projects=selected(ProjectTemplate,settings.featured_project_ids)
    challenges=selected(Challenge,settings.featured_challenge_ids)
    published_times=dict(db.execute(select(PublishingReview.course_id,func.max(PublishingReview.created_at)).where(PublishingReview.decision=="publish").group_by(PublishingReview.course_id)).all())
    new_candidates=db.scalars(select(Course).where(Course.published.is_(True))).all()
    if settings.new_courses_mode=="manual": new_courses=selected(Course,settings.new_course_ids)
    else: new_courses=sorted(new_candidates,key=lambda row: published_times.get(row.id) or row.updated_at,reverse=True)[:settings.new_courses_limit]
    def course_view(row): return {"id":row.id,"title":row.title,"slug":row.slug,"short_description":row.short_description or "","thumbnail":row.thumbnail,"level":row.level,"duration_minutes":row.duration_minutes}
    def lesson_view(row):
        module=db.get(CourseModule,row.module_id); course=db.get(Course,module.course_id) if module else None
        return {"id":row.id,"title":row.title,"slug":row.slug,"duration_minutes":row.duration_minutes,"course_slug":course.slug if course else None,"course_title":course.title if course else None,"module_title":module.title if module else None}
    now_value=datetime.now(timezone.utc)
    announcements=[]
    for item in settings.announcements:
        if not item.visible or item.status!="published": continue
        starts=item.starts_at.replace(tzinfo=timezone.utc) if item.starts_at and item.starts_at.tzinfo is None else item.starts_at
        ends=item.ends_at.replace(tzinfo=timezone.utc) if item.ends_at and item.ends_at.tzinfo is None else item.ends_at
        if starts and starts>now_value: continue
        if ends and ends<=now_value: continue
        announcements.append(item.model_dump(mode="json"))
    return {"featured_courses":[course_view(row) for row in courses if row.published],"new_courses":[course_view(row) for row in new_courses if row.published],"featured_lessons":[lesson_view(row) for row in lessons if row.published and db.scalar(select(Course.published).join(CourseModule,CourseModule.course_id==Course.id).where(CourseModule.id==row.module_id))],"featured_paths":[{"id":row.id,"title":row.title,"slug":row.slug,"description":row.description_en,"estimated_hours":row.estimated_hours} for row in paths if row.published],"featured_projects":[{"id":row.id,"title":row.title,"slug":row.slug,"description":row.description_en,"difficulty":row.difficulty,"estimated_hours":row.estimated_hours} for row in projects if row.published],"featured_challenges":[{"id":row.id,"title":row.title,"slug":row.slug,"description":row.description_en,"difficulty":row.difficulty} for row in challenges if row.published],"announcements":announcements}
def public_homepage(db):
    settings=homepage_value(db,HOMEPAGE_PUBLISHED_KEY)
    return {**settings.model_dump(mode="json"),**public_records(db,settings)}
def course_out(course): return {"id":course.id,"title":course.title,"slug":course.slug,"short_description":course.short_description or "","description":course.description,"target_audience":course.target_audience or "","technologies":course.technologies or "","seo_title":course.seo_title or "","seo_description":course.seo_description or "","language_id":course.language_id,"category_id":course.category_id,"level":course.level,"thumbnail":course.thumbnail,"estimated_duration":course.duration_minutes,"status":course.status or ("published" if course.published else "draft"),"published":course.published,"outcomes":course.outcomes,"requirements":course.requirements}
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
def lesson_payload(lesson):
    return {"id":lesson.id,"module_id":lesson.module_id,"title":lesson.title,"slug":lesson.slug,"description":lesson.description or "","content_en":lesson.content_en or "","content_mm":lesson.content_mm,"position":lesson.order_index,"duration_minutes":lesson.duration_minutes,"status":lesson.status,"published":lesson.published,"content_version":lesson.content_version,"updated_at":lesson.updated_at}
def admin_lesson_payload(lesson, db):
    module=db.get(CourseModule,lesson.module_id)
    course=db.get(Course,module.course_id) if module else None
    language=db.get(ProgrammingLanguage,course.language_id) if course else None
    return {**lesson_payload(lesson),"module_title":module.title if module else None,"module_position":module.order_index if module else None,"course_id":course.id if course else None,"course_slug":course.slug if course else None,"course_title":course.title if course else None,"language_id":language.id if language else None,"language_name":language.name if language else None,"language_slug":language.slug if language else None}
def lesson_snapshot(lesson):
    return {"title":lesson.title,"slug":lesson.slug,"description":lesson.description or "","content_en":lesson.content_en or "","content_mm":lesson.content_mm,"position":lesson.order_index,"duration_minutes":lesson.duration_minutes,"status":lesson.status,"published":lesson.published}
def record_lesson_revision(db, lesson, user, summary=""):
    latest=db.scalar(select(func.max(LessonRevision.revision_number)).where(LessonRevision.lesson_id==lesson.id)) or 0
    revision=LessonRevision(lesson_id=lesson.id,changed_by=user.id,revision_number=latest+1,content_snapshot=json.dumps(lesson_snapshot(lesson),default=str),change_summary=summary)
    db.add(revision)
def require_lesson_version(lesson, expected_version):
    if expected_version is not None and lesson.content_version != expected_version: raise HTTPException(409,"This lesson was updated by another administrator. Reload it before saving.")
def curriculum_payload(course):
    return [{"id":m.id,"title":m.title,"position":m.order_index,"lessons":[lesson_payload(l) for l in m.lessons]} for m in course.modules]
def reorder_structure(course, payload, db):
    modules={module.id:module for module in course.modules}; requested={item.id for item in payload.modules}
    if requested != set(modules): raise HTTPException(422,"Curriculum must include every course module exactly once")
    lessons={lesson.id:lesson for module in course.modules for lesson in module.lessons}; requested_lessons=[lesson_id for item in payload.modules for lesson_id in item.lesson_ids]
    if len(requested_lessons) != len(lessons) or set(requested_lessons) != set(lessons): raise HTTPException(422,"Curriculum must include every course lesson exactly once")
    for module in course.modules: module.order_index += 100000
    for lesson in lessons.values(): lesson.order_index += 100000
    db.flush()
    for item in sorted(payload.modules,key=lambda value:value.position):
        module=modules[item.id]; module.order_index=item.position
        for position, lesson_id in enumerate(item.lesson_ids):
            lesson=lessons[lesson_id]; lesson.module_id=module.id; lesson.order_index=position
    db.flush()
def quiz_question_out(row):
    return {"id": row.id, "prompt": row.prompt, "question_type": row.question_type, "options": json.loads(row.options_json or "[]"), "correct_answer": row.correct_answer, "explanation": row.explanation, "position": row.position}
def lesson_for_edit(lesson_id, user, db):
    lesson=db.get(Lesson, lesson_id)
    if not lesson: raise HTTPException(404,"Lesson not found")
    module=db.get(CourseModule, lesson.module_id)
    if not module: raise HTTPException(404,"Course module not found")
    require_edit(module.course_id, user, db)
    return lesson
@router.post("/auth/login")
def admin_login(payload: LoginIn, request: Request, response: Response, db: Session=Depends(get_db)):
    check_rate_limit(f"admin-login:{request.client.host if request.client else 'unknown'}:{normalize_email(payload.email)}", 8)
    user=db.scalar(select(User).where(User.email_normalized==normalize_email(payload.email)))
    if not user or not verify_password(payload.password, user.password_hash) or user.account_status!="active":
        raise HTTPException(401,"Invalid email or password")
    if user.role not in CONTENT_ADMIN_ROLES or not user.email_verified_at:
        raise HTTPException(403,"Administrator access required")
    raw, csrf=create_session(db,user)
    user.last_login_at=now()
    audit(db,user,"admin_login","admin_session")
    db.commit()
    from .auth import set_auth_cookies
    set_auth_cookies(response,raw,csrf)
    return {"id":user.id,"email":user.email,"full_name":user.display_name,"role":user.role,"email_verified":True}
@router.get("/auth/me")
def admin_me(user: User=Depends(admin_user)):
    return {"id":user.id,"email":user.email,"full_name":user.display_name,"role":user.role,"email_verified":True}
@router.post("/auth/logout")
def admin_logout(response: Response, session_token: str|None=Cookie(default=None,alias=SESSION_COOKIE), user: User=Depends(full_admin), _:None=Depends(require_csrf), db: Session=Depends(get_db)):
    if session_token:
        session=db.scalar(select(AuthSession).where(AuthSession.token_hash==hash_token(session_token)))
        if session: session.revoked_at=now()
    audit(db,user,"admin_logout","admin_session")
    db.commit(); clear_auth_cookies(response)
    return {"status":"ok"}
@router.get("/dashboard")
def dashboard(user: User=Depends(full_admin), db: Session=Depends(get_db)):
    lesson_counts=select(CourseModule.course_id.label("course_id"),func.count(Lesson.id).label("total")).join(Lesson,Lesson.module_id==CourseModule.id).where(Lesson.published.is_(True)).group_by(CourseModule.course_id).subquery()
    completed_counts=select(LessonProgress.user_id.label("user_id"),CourseModule.course_id.label("course_id"),func.count(LessonProgress.id).label("completed")).select_from(LessonProgress).join(Lesson,LessonProgress.lesson_id==Lesson.id).join(CourseModule,CourseModule.id==Lesson.module_id).where(LessonProgress.completed.is_(True)).group_by(LessonProgress.user_id,CourseModule.course_id).subquery()
    completed_courses=db.scalar(select(func.count()).select_from(Enrollment).join(lesson_counts,lesson_counts.c.course_id==Enrollment.course_id).join(completed_counts,(completed_counts.c.course_id==Enrollment.course_id)&(completed_counts.c.user_id==Enrollment.user_id),isouter=True).where(lesson_counts.c.total>0,func.coalesce(completed_counts.c.completed,0)>=lesson_counts.c.total)) or 0
    popularity=db.execute(select(Course.title,func.count(Enrollment.id).label("enrollments")).join(Enrollment,Enrollment.course_id==Course.id).group_by(Course.id).order_by(func.count(Enrollment.id).desc()).limit(5)).all()
    activity=db.scalars(select(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()).limit(8)).all()
    return {"total_courses":db.scalar(select(func.count(Course.id))) or 0,"published_courses":db.scalar(select(func.count(Course.id)).where(Course.published.is_(True))) or 0,"draft_courses":db.scalar(select(func.count(Course.id)).where(Course.status.in_(["draft","in_review"]))) or 0,"total_lessons":db.scalar(select(func.count(Lesson.id))) or 0,"total_students":db.scalar(select(func.count(User.id)).where(User.role=="student")) or 0,"active_enrollments":db.scalar(select(func.count(Enrollment.id))) or 0,"completed_courses":completed_courses,"quiz_attempts":db.scalar(select(func.count(QuizAttempt.id))) or 0,"total_instructors":db.scalar(select(func.count(User.id)).where(User.role=="instructor")) or 0,"recent_courses":[course_out(x) for x in db.scalars(select(Course).order_by(Course.updated_at.desc()).limit(5)).all()],"pending_reviews":db.scalar(select(func.count(PublishingReview.id)).where(PublishingReview.decision=="pending")) or 0,"recent_activity":[{"action":x.action,"entity_type":x.entity_type,"created_at":x.created_at} for x in activity],"course_popularity":[{"title":title,"enrollments":enrollments} for title,enrollments in popularity]}
@router.get("/users")
def list_users(search: str|None=None, page: int=Query(1,ge=1), page_size: int=Query(20,ge=1,le=100), user: User=Depends(full_admin), db: Session=Depends(get_db)):
    query=select(User); count=select(func.count()).select_from(User)
    if search:
        pattern=f"%{search}%"
        condition=User.email.ilike(pattern)|User.display_name.ilike(pattern)|User.role.ilike(pattern)
        query=query.where(condition); count=count.where(condition)
    total=db.scalar(count) or 0
    rows=db.scalars(query.order_by(User.created_at.desc()).offset((page-1)*page_size).limit(page_size)).all()
    return {"items":[{"id":row.id,"email":row.email,"display_name":row.display_name,"role":row.role,"account_status":row.account_status,"email_verified":row.email_verified_at is not None,"created_at":row.created_at} for row in rows],"page":page,"page_size":page_size,"total":total,"pages":math.ceil(total/page_size) if total else 0}
@router.get("/settings/branding", response_model=BrandingSettings)
def get_branding_settings(user: User=Depends(full_admin), db: Session=Depends(get_db)):
    return branding_value(db)
@router.patch("/settings/branding", response_model=BrandingSettings)
def update_branding_settings(payload: BrandingSettings, user: User=Depends(full_admin), _: None=Depends(require_csrf), db: Session=Depends(get_db)):
    values=payload.model_dump()
    for key in ("logo_url", "mobile_logo_url", "favicon_url"):
        if not (values[key].startswith("/") and not values[key].startswith("//")):
            raise HTTPException(422, "Branding assets must use an internal path")
    row=db.scalar(select(PlatformSetting).where(PlatformSetting.key==BRANDING_KEY))
    if row: row.value_json=json.dumps(values); row.updated_by=user.id
    else: db.add(PlatformSetting(key=BRANDING_KEY,value_json=json.dumps(values),updated_by=user.id))
    audit(db,user,"branding_updated","platform_setting")
    db.commit()
    return values
@router.get("/settings/navigation", response_model=NavigationSettings)
def get_navigation_settings(user: User=Depends(admin_user), db: Session=Depends(get_db)):
    row=db.scalar(select(PlatformSetting).where(PlatformSetting.key=="navigation"))
    if not row: return NavigationSettings(items=[])
    try: return NavigationSettings.model_validate(json.loads(row.value_json or "{}"))
    except (TypeError, ValueError, json.JSONDecodeError): return NavigationSettings(items=[])
@router.patch("/settings/navigation", response_model=NavigationSettings)
def update_navigation_settings(payload: NavigationSettings, user: User=Depends(full_admin), _: None=Depends(require_csrf), db: Session=Depends(get_db)):
    values=payload.model_dump()
    row=db.scalar(select(PlatformSetting).where(PlatformSetting.key=="navigation"))
    if row: row.value_json=json.dumps(values); row.updated_by=user.id
    else: db.add(PlatformSetting(key="navigation",value_json=json.dumps(values),updated_by=user.id))
    audit(db,user,"navigation_updated","platform_setting"); db.commit(); return values
@router.get("/settings/homepage")
def get_homepage_settings(user: User=Depends(admin_user), db: Session=Depends(get_db)):
    draft_exists=db.scalar(select(PlatformSetting).where(PlatformSetting.key==HOMEPAGE_DRAFT_KEY)) is not None
    settings=homepage_value(db, HOMEPAGE_DRAFT_KEY if draft_exists else HOMEPAGE_PUBLISHED_KEY)
    return {"settings": settings.model_dump(mode="json"), **homepage_choices(db), "revisions": homepage_revisions(db)}
@router.get("/settings/homepage/preview")
def preview_homepage_settings(user: User=Depends(admin_user), db: Session=Depends(get_db)):
    settings=homepage_value(db,HOMEPAGE_DRAFT_KEY)
    return {**settings.model_dump(mode="json"),**public_records(db,settings),"preview":True}
def save_homepage_draft(db, user, payload: HomepageSettings, action="draft_saved"):
    settings=validate_homepage(db,payload).model_copy(update={"status":"draft"})
    values=settings.model_dump(mode="json")
    row=db.scalar(select(PlatformSetting).where(PlatformSetting.key==HOMEPAGE_DRAFT_KEY))
    if row: row.value_json=json.dumps(values); row.updated_by=user.id
    else: db.add(PlatformSetting(key=HOMEPAGE_DRAFT_KEY,value_json=json.dumps(values),updated_by=user.id))
    record_homepage_revision(db,user,settings,action); audit(db,user,"homepage_draft_saved","platform_setting"); db.commit(); return settings
@router.patch("/settings/homepage", response_model=HomepageSettings)
def update_homepage_settings(payload: HomepageSettings, user: User=Depends(full_admin), _: None=Depends(require_csrf), db: Session=Depends(get_db)):
    return save_homepage_draft(db,user,payload)
@router.patch("/settings/homepage/sections", response_model=HomepageSettings)
def reorder_homepage_sections(payload: HomepageSectionsIn, user: User=Depends(full_admin), _: None=Depends(require_csrf), db: Session=Depends(get_db)):
    current=homepage_value(db,HOMEPAGE_DRAFT_KEY); return save_homepage_draft(db,user,current.model_copy(update={"sections":payload.sections}),"sections_reordered")
@router.post("/settings/homepage/announcements", response_model=HomepageSettings)
def create_homepage_announcement(payload: HomepageAnnouncement, user: User=Depends(full_admin), _: None=Depends(require_csrf), db: Session=Depends(get_db)):
    current=homepage_value(db,HOMEPAGE_DRAFT_KEY); announcement=payload.model_copy(update={"id":payload.id or str(uuid4())}); return save_homepage_draft(db,user,current.model_copy(update={"announcements":[*current.announcements,announcement]}),"announcement_created")
@router.patch("/settings/homepage/announcements/{announcement_id}", response_model=HomepageSettings)
def update_homepage_announcement(announcement_id: str, payload: HomepageAnnouncement, user: User=Depends(full_admin), _: None=Depends(require_csrf), db: Session=Depends(get_db)):
    current=homepage_value(db,HOMEPAGE_DRAFT_KEY); if_not_found=next((item for item in current.announcements if item.id==announcement_id),None)
    if not if_not_found: raise HTTPException(404,"Homepage announcement not found")
    announcements=[payload.model_copy(update={"id":announcement_id}) if item.id==announcement_id else item for item in current.announcements]
    return save_homepage_draft(db,user,current.model_copy(update={"announcements":announcements}),"announcement_updated")
@router.delete("/settings/homepage/announcements/{announcement_id}", response_model=HomepageSettings)
def delete_homepage_announcement(announcement_id: str, user: User=Depends(full_admin), _: None=Depends(require_csrf), db: Session=Depends(get_db)):
    current=homepage_value(db,HOMEPAGE_DRAFT_KEY); announcements=[item for item in current.announcements if item.id!=announcement_id]
    if len(announcements)==len(current.announcements): raise HTTPException(404,"Homepage announcement not found")
    return save_homepage_draft(db,user,current.model_copy(update={"announcements":announcements}),"announcement_deleted")
@router.get("/settings/homepage/revisions")
def list_homepage_revisions(user: User=Depends(admin_user), db: Session=Depends(get_db)):
    return homepage_revisions(db)
@router.post("/settings/homepage/revisions/{revision_id}/restore", response_model=HomepageSettings)
def restore_homepage_revision(revision_id: UUID, user: User=Depends(full_admin), _: None=Depends(require_csrf), db: Session=Depends(get_db)):
    row=db.scalar(select(PlatformSetting).where(PlatformSetting.key==f"{HOMEPAGE_REVISION_PREFIX}{revision_id}"))
    if not row: raise HTTPException(404,"Homepage revision not found")
    try: snapshot=json.loads(row.value_json or "{}")["snapshot"]; settings=HomepageSettings.model_validate(snapshot)
    except (KeyError,TypeError,ValueError,json.JSONDecodeError): raise HTTPException(422,"Homepage revision is invalid")
    return save_homepage_draft(db,user,settings,"revision_restored")
@router.post("/settings/homepage/publish", response_model=HomepageSettings)
def publish_homepage_settings(user: User=Depends(full_admin), _: None=Depends(require_csrf), db: Session=Depends(get_db)):
    settings=validate_homepage(db,homepage_value(db,HOMEPAGE_DRAFT_KEY))
    values=settings.model_copy(update={"status":"published"}).model_dump(mode="json")
    row=db.scalar(select(PlatformSetting).where(PlatformSetting.key==HOMEPAGE_PUBLISHED_KEY))
    if row: row.value_json=json.dumps(values); row.updated_by=user.id
    else: db.add(PlatformSetting(key=HOMEPAGE_PUBLISHED_KEY,value_json=json.dumps(values),updated_by=user.id))
    draft=db.scalar(select(PlatformSetting).where(PlatformSetting.key==HOMEPAGE_DRAFT_KEY))
    if draft: draft.value_json=json.dumps(values); draft.updated_by=user.id
    record_homepage_revision(db,user,HomepageSettings.model_validate(values),"published"); audit(db,user,"homepage_published","platform_setting"); db.commit(); return HomepageSettings.model_validate(values)
@router.get("/settings/footer", response_model=FooterSettings)
def get_footer_settings(user: User=Depends(admin_user), db: Session=Depends(get_db)):
    return read_footer(db, FOOTER_DRAFT_KEY) if db.scalar(select(PlatformSetting).where(PlatformSetting.key == FOOTER_DRAFT_KEY)) else read_footer(db)
@router.patch("/settings/footer", response_model=FooterSettings)
def update_footer_settings(payload: FooterSettings, user: User=Depends(full_admin), _: None=Depends(require_csrf), db: Session=Depends(get_db)):
    values = validate_footer(payload).model_copy(update={"status": "draft"}).model_dump(mode="json")
    row = db.scalar(select(PlatformSetting).where(PlatformSetting.key == FOOTER_DRAFT_KEY))
    if row: row.value_json = json.dumps(values); row.updated_by = user.id
    else: db.add(PlatformSetting(key=FOOTER_DRAFT_KEY, value_json=json.dumps(values), updated_by=user.id))
    audit(db, user, "footer_saved_draft", "platform_setting"); db.commit(); return values
@router.post("/settings/footer/publish", response_model=FooterSettings)
def publish_footer_settings(user: User=Depends(full_admin), _: None=Depends(require_csrf), db: Session=Depends(get_db)):
    draft_row = db.scalar(select(PlatformSetting).where(PlatformSetting.key == FOOTER_DRAFT_KEY))
    payload = read_footer(db, FOOTER_DRAFT_KEY) if draft_row else read_footer(db)
    values = validate_footer(payload).model_copy(update={"status": "published"}).model_dump(mode="json")
    row = db.scalar(select(PlatformSetting).where(PlatformSetting.key == FOOTER_KEY))
    if row: row.value_json = json.dumps(values); row.updated_by = user.id
    else: db.add(PlatformSetting(key=FOOTER_KEY, value_json=json.dumps(values), updated_by=user.id))
    if draft_row: draft_row.value_json = json.dumps(values); draft_row.updated_by = user.id
    else: db.add(PlatformSetting(key=FOOTER_DRAFT_KEY, value_json=json.dumps(values), updated_by=user.id))
    audit(db, user, "footer_published", "platform_setting"); db.commit(); return values
@router.get("/pages")
def list_platform_pages(user: User=Depends(admin_user), db: Session=Depends(get_db)):
    rows=db.scalars(select(PlatformSetting).where(PlatformSetting.key.like("page:%")).order_by(PlatformSetting.key)).all()
    pages=[]
    for row in rows:
        try: pages.append(PlatformPageOut.model_validate(json.loads(row.value_json or "{}")))
        except (TypeError, ValueError, json.JSONDecodeError): continue
    return pages
@router.put("/pages/{slug}", response_model=PlatformPageOut)
def upsert_platform_page(slug: str, payload: PlatformPageIn, user: User=Depends(full_admin), _: None=Depends(require_csrf), db: Session=Depends(get_db)):
    if slug != payload.slug: raise HTTPException(422, "Page slug does not match path")
    values=payload.model_dump()
    row=db.scalar(select(PlatformSetting).where(PlatformSetting.key==f"page:{slug}"))
    if row: row.value_json=json.dumps(values); row.updated_by=user.id
    else: db.add(PlatformSetting(key=f"page:{slug}",value_json=json.dumps(values),updated_by=user.id))
    audit(db,user,f"page_{payload.status}","platform_page"); db.commit(); return values
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
@router.get("/lessons")
def list_lessons(search: str|None=None, status: str|None=None, page: int=Query(1,ge=1), page_size: int=Query(20,ge=1,le=100), user: User=Depends(admin_user), db: Session=Depends(get_db)):
    query=select(Lesson, CourseModule, Course).join(CourseModule, Lesson.module_id==CourseModule.id).join(Course, CourseModule.course_id==Course.id)
    count=select(func.count(Lesson.id)).select_from(Lesson).join(CourseModule, Lesson.module_id==CourseModule.id).join(Course, CourseModule.course_id==Course.id)
    if search:
        condition=Lesson.title.ilike(f"%{search}%")|Course.title.ilike(f"%{search}%")
        query=query.where(condition); count=count.where(condition)
    if status:
        query=query.where(Lesson.status==status); count=count.where(Lesson.status==status)
    total=db.scalar(count) or 0
    rows=db.execute(query.order_by(Course.title, CourseModule.order_index, Lesson.order_index).offset((page-1)*page_size).limit(page_size)).all()
    items=[{**lesson_payload(lesson),"course_id":course.id,"course_title":course.title,"module_title":module.title} for lesson,module,course in rows]
    return {"items":items,"page":page,"page_size":page_size,"total":total,"pages":math.ceil(total/page_size) if total else 0}
@router.post("/courses",response_model=AdminCourseOut,status_code=201)
def create_course(payload:AdminCourseIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if db.scalar(select(Course).where(Course.slug==payload.slug)): raise HTTPException(409,"Slug already exists")
    if not db.get(ProgrammingLanguage,payload.language_id) or not db.get(CourseCategory,payload.category_id): raise HTTPException(422,"Language and category are required")
    row=Course(title=payload.title,slug=payload.slug,short_description=payload.short_description,description=payload.description,target_audience=payload.target_audience,technologies="|".join(payload.technologies),seo_title=payload.seo_title,seo_description=payload.seo_description,language_id=payload.language_id,category_id=payload.category_id,level=payload.level,thumbnail=payload.thumbnail,duration_minutes=payload.estimated_duration,status="draft",published=False,outcomes="|".join(payload.outcomes),requirements="|".join(payload.requirements),created_by=user.id,updated_by=user.id); db.add(row); db.flush(); audit(db,user,"course_created","course",row.id); db.commit(); return course_out(row)
@router.get("/courses/{course_id}/builder",response_model=AdminCourseOut)
def builder(course_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)): return course_out(require_edit(course_id,user,db))
@router.get("/courses/{course_id}/stats")
def course_stats(course_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)):
    course=require_edit(course_id,user,db)
    module_count=db.scalar(select(func.count(CourseModule.id)).where(CourseModule.course_id==course.id)) or 0
    lesson_count=db.scalar(select(func.count(Lesson.id)).join(CourseModule).where(CourseModule.course_id==course.id)) or 0
    published_lesson_count=db.scalar(select(func.count(Lesson.id)).join(CourseModule).where(CourseModule.course_id==course.id,Lesson.published.is_(True))) or 0
    enrollment_count=db.scalar(select(func.count(Enrollment.id)).where(Enrollment.course_id==course.id)) or 0
    return {"course_id":course.id,"module_count":module_count,"lesson_count":lesson_count,"published_lesson_count":published_lesson_count,"enrollment_count":enrollment_count,"status":course.status,"published":course.published}
@router.patch("/courses/{course_id}",response_model=AdminCourseOut)
def update_course(course_id:UUID,payload:AdminCourseIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=require_edit(course_id,user,db); duplicate=db.scalar(select(Course).where(Course.slug==payload.slug,Course.id!=course_id))
    if duplicate: raise HTTPException(409,"Slug already exists")
    for key,value in payload.model_dump().items():
        if key in {"estimated_duration","outcomes","requirements"}: continue
        setattr(row,key,value)
    row.duration_minutes=payload.estimated_duration; row.target_audience=payload.target_audience; row.technologies="|".join(payload.technologies); row.seo_title=payload.seo_title; row.seo_description=payload.seo_description; row.outcomes="|".join(payload.outcomes); row.requirements="|".join(payload.requirements); row.updated_by=user.id; db.add(CourseRevision(course_id=row.id,changed_by=user.id,status=row.status,snapshot_json=json.dumps(course_out(row),default=str))); audit(db,user,"course_updated","course",row.id); db.commit(); return course_out(row)
@router.post("/courses/{course_id}/thumbnail",response_model=AdminCourseOut)
async def upload_course_thumbnail(course_id:UUID,image:UploadFile=File(...),user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=require_edit(course_id,user,db); previous=row.thumbnail
    public_url, _, _ = await save_course_image(image)
    row.thumbnail=public_url; row.updated_by=user.id
    audit(db,user,"course_thumbnail_uploaded","course",row.id)
    try:
        db.commit()
    except Exception:
        db.rollback(); remove_file_if_safe(public_url); raise
    if previous and previous != public_url:
        cleanup_course_thumbnail(db,previous,row.id)
    return course_out(row)
@router.delete("/courses/{course_id}/thumbnail",response_model=AdminCourseOut)
def remove_course_thumbnail(course_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=require_edit(course_id,user,db); previous=row.thumbnail
    row.thumbnail=None; row.updated_by=user.id
    audit(db,user,"course_thumbnail_removed","course",row.id); db.commit()
    if previous:
        cleanup_course_thumbnail(db,previous,row.id)
    return course_out(row)
@router.post("/courses/{course_id}/duplicate",response_model=AdminCourseOut,status_code=201)
def duplicate_course(course_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    source=require_edit(course_id,user,db); slug=f"{source.slug}-copy"; suffix=2
    while db.scalar(select(Course).where(Course.slug==slug)):
        slug=f"{source.slug}-copy-{suffix}"; suffix += 1
    row=Course(title=f"{source.title} Copy",slug=slug,short_description=source.short_description,description=source.description,target_audience=source.target_audience,technologies=source.technologies,seo_title=source.seo_title,seo_description=source.seo_description,language_id=source.language_id,category_id=source.category_id,level=source.level,duration_minutes=source.duration_minutes,status="draft",published=False,outcomes=source.outcomes,requirements=source.requirements,thumbnail=source.thumbnail,created_by=user.id,updated_by=user.id); db.add(row); db.flush()
    for module in source.modules:
        copied_module=CourseModule(course_id=row.id,title=module.title,order_index=module.order_index); db.add(copied_module); db.flush()
        for lesson in module.lessons:
            copied_lesson=Lesson(module_id=copied_module.id,title=lesson.title,slug=lesson.slug,description=lesson.description,content_en=lesson.content_en,content_mm=lesson.content_mm,order_index=lesson.order_index,duration_minutes=lesson.duration_minutes,status="draft",published=False,content_version=1); db.add(copied_lesson); db.flush()
            for example in lesson.code_examples: db.add(CodeExample(lesson_id=copied_lesson.id,title=example.title,language=example.language,code=example.code,filename=example.filename,description=example.description,position=example.position))
            source_quiz=db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id==lesson.id))
            if source_quiz:
                copied_quiz=LessonQuiz(lesson_id=copied_lesson.id,title=source_quiz.title,explanation=source_quiz.explanation,status="draft"); db.add(copied_quiz); db.flush()
                for question in db.scalars(select(QuizQuestion).where(QuizQuestion.quiz_id==source_quiz.id).order_by(QuizQuestion.position)).all():
                    db.add(QuizQuestion(quiz_id=copied_quiz.id,prompt=question.prompt,question_type=question.question_type,options_json=question.options_json,correct_answer=question.correct_answer,explanation=question.explanation,position=question.position))
    for faq in source.faqs:
        db.add(CourseFAQ(course_id=row.id,question=faq.question,answer=faq.answer,position=faq.position,status="draft"))
    for instructor in db.scalars(select(CourseInstructor).where(CourseInstructor.course_id==source.id)).all():
        db.add(CourseInstructor(course_id=row.id,user_id=instructor.user_id))
    audit(db,user,"course_duplicated","course",row.id); db.commit(); return course_out(row)
@router.post("/courses/{course_id}/archive",response_model=AdminCourseOut)
def archive_course(course_id:UUID,user:User=Depends(full_admin),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=require_edit(course_id,user,db); row.status="archived"; row.published=False; row.updated_by=user.id; audit(db,user,"course_archived","course",row.id); db.commit(); return course_out(row)
@router.get("/courses/{course_id}/curriculum")
def curriculum(course_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)):
    return curriculum_payload(require_edit(course_id,user,db))
@router.post("/courses/{course_id}/curriculum/reorder")
def reorder_curriculum(course_id:UUID,payload:CurriculumOrderIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    course=require_edit(course_id,user,db); reorder_structure(course,payload,db); audit(db,user,"curriculum_reordered","course",course.id); db.commit(); return curriculum_payload(load_course(db,course.id))
@router.get("/courses/{course_id}/faqs")
def list_course_faqs(course_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)):
    course=require_edit(course_id,user,db)
    return [{"id":faq.id,"question":faq.question,"answer":faq.answer,"position":faq.position,"status":faq.status} for faq in db.scalars(select(CourseFAQ).where(CourseFAQ.course_id==course.id).order_by(CourseFAQ.position,CourseFAQ.created_at)).all()]
@router.post("/courses/{course_id}/faqs",status_code=201)
def create_course_faq(course_id:UUID,payload:AdminCourseFAQIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    course=require_edit(course_id,user,db); row=CourseFAQ(course_id=course.id,**payload.model_dump()); db.add(row); audit(db,user,"course_faq_created","course_faq",row.id); db.commit(); return {"id":row.id,"question":row.question,"answer":row.answer,"position":row.position,"status":row.status}
@router.patch("/faqs/{faq_id}")
def update_course_faq(faq_id:UUID,payload:AdminCourseFAQIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(CourseFAQ,faq_id)
    if not row: raise HTTPException(404,"FAQ not found")
    require_edit(row.course_id,user,db)
    for key,value in payload.model_dump().items(): setattr(row,key,value)
    audit(db,user,"course_faq_updated","course_faq",row.id); db.commit(); return {"id":row.id,"question":row.question,"answer":row.answer,"position":row.position,"status":row.status}
@router.delete("/faqs/{faq_id}",status_code=204)
def delete_course_faq(faq_id:UUID,user:User=Depends(full_admin),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(CourseFAQ,faq_id)
    if not row: raise HTTPException(404,"FAQ not found")
    require_edit(row.course_id,user,db); audit(db,user,"course_faq_deleted","course_faq",row.id); db.delete(row); db.commit()
@router.post("/courses/{course_id}/modules",status_code=201)
def create_module(course_id:UUID,payload:AdminModuleIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    course=require_edit(course_id,user,db); position=max([module.order_index for module in course.modules],default=-1)+1; row=CourseModule(course_id=course.id,title=payload.title,order_index=position); db.add(row); audit(db,user,"module_created","course_module",row.id); db.commit(); return {"id":row.id,"title":row.title,"position":row.order_index}
@router.patch("/modules/{module_id}")
def update_module(module_id:UUID,payload:AdminModuleIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(CourseModule,module_id)
    if not row: raise HTTPException(404,"Module not found")
    course=require_edit(row.course_id,user,db); row.title=payload.title; audit(db,user,"module_updated","course_module",row.id); db.commit(); return {"id":row.id,"title":row.title,"position":row.order_index}
@router.post("/modules/{module_id}/lessons",status_code=201)
def create_lesson(module_id:UUID,payload:AdminLessonIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    module=db.get(CourseModule,module_id)
    if not module: raise HTTPException(404,"Module not found")
    course=require_edit(module.course_id,user,db)
    if db.scalar(select(Lesson).join(CourseModule).where(CourseModule.course_id==course.id,Lesson.slug==payload.slug)): raise HTTPException(409,"Lesson slug already exists in this course")
    position=max([lesson.order_index for lesson in module.lessons],default=-1)+1; row=Lesson(module_id=module.id,title=payload.title,slug=payload.slug,description=payload.description,content_en=payload.content_en,content_mm=payload.content_mm,order_index=position,duration_minutes=payload.duration_minutes,status=payload.status,published=payload.status=="published",content_version=1); db.add(row); db.flush(); record_lesson_revision(db,row,user,"Initial lesson draft"); audit(db,user,"lesson_created","lesson",row.id); db.commit(); return lesson_payload(row)
@router.get("/lessons/{lesson_id}")
def admin_lesson(lesson_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)):
    lesson=lesson_for_edit(lesson_id,user,db); return admin_lesson_payload(lesson,db)
@router.patch("/lessons/{lesson_id}")
def update_lesson(lesson_id:UUID,payload:AdminLessonIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(Lesson,lesson_id)
    if not row: raise HTTPException(404,"Lesson not found")
    module=db.get(CourseModule,row.module_id); course=require_edit(module.course_id,user,db); require_lesson_version(row,payload.expected_version)
    duplicate=db.scalar(select(Lesson).join(CourseModule).where(CourseModule.course_id==course.id,Lesson.slug==payload.slug,Lesson.id!=row.id))
    if duplicate: raise HTTPException(409,"Lesson slug already exists in this course")
    record_lesson_revision(db,row,user,payload.change_summary or "Before lesson update")
    row.title=payload.title; row.slug=payload.slug; row.description=payload.description; row.content_en=payload.content_en; row.content_mm=payload.content_mm; row.order_index=payload.position; row.duration_minutes=payload.duration_minutes; row.status=payload.status; row.published=payload.status=="published"; row.content_version += 1; audit(db,user,"lesson_updated","lesson",row.id); db.commit(); return lesson_payload(row)
@router.post("/lessons/{lesson_id}/duplicate")
def duplicate_lesson(lesson_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    source=lesson_for_edit(lesson_id,user,db); module=db.get(CourseModule,source.module_id); base=f"{source.slug}-copy"; slug=base; suffix=2
    while db.scalar(select(Lesson).join(CourseModule).where(CourseModule.course_id==module.course_id,Lesson.slug==slug)):
        slug=f"{base}-{suffix}"; suffix += 1
    position=max([lesson.order_index for lesson in module.lessons],default=-1)+1; row=Lesson(module_id=module.id,title=f"{source.title} Copy",slug=slug,description=source.description,content_en=source.content_en,content_mm=source.content_mm,order_index=position,duration_minutes=source.duration_minutes,status="draft",published=False,content_version=1); db.add(row); db.flush()
    for example in source.code_examples: db.add(CodeExample(lesson_id=row.id,title=example.title,language=example.language,code=example.code,filename=example.filename,description=example.description,position=example.position))
    record_lesson_revision(db,row,user,"Duplicated lesson draft"); audit(db,user,"lesson_duplicated","lesson",row.id); db.commit(); return lesson_payload(row)
@router.post("/lessons/{lesson_id}/archive")
def archive_lesson(lesson_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=lesson_for_edit(lesson_id,user,db); record_lesson_revision(db,row,user,"Before lesson archive"); row.status="archived"; row.published=False; row.content_version += 1; audit(db,user,"lesson_archived","lesson",row.id); db.commit(); return lesson_payload(row)
@router.get("/lessons/{lesson_id}/revisions")
def lesson_revisions(lesson_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)):
    lesson=lesson_for_edit(lesson_id,user,db); return [{"id":revision.id,"revision_number":revision.revision_number,"changed_by":revision.changed_by,"content_snapshot":json.loads(revision.content_snapshot),"change_summary":revision.change_summary,"created_at":revision.created_at} for revision in db.scalars(select(LessonRevision).where(LessonRevision.lesson_id==lesson.id).order_by(LessonRevision.revision_number.desc())).all()]
@router.post("/lessons/{lesson_id}/revisions/{revision_id}/restore")
def restore_lesson_revision(lesson_id:UUID,revision_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    lesson=lesson_for_edit(lesson_id,user,db); revision=db.scalar(select(LessonRevision).where(LessonRevision.id==revision_id,LessonRevision.lesson_id==lesson.id))
    if not revision: raise HTTPException(404,"Lesson revision not found")
    snapshot=json.loads(revision.content_snapshot); record_lesson_revision(db,lesson,user,f"Before restoring revision {revision.revision_number}")
    lesson.title=snapshot["title"]; lesson.slug=snapshot["slug"]; lesson.description=snapshot.get("description",""); lesson.content_en=snapshot.get("content_en",""); lesson.content_mm=snapshot.get("content_mm"); lesson.duration_minutes=snapshot.get("duration_minutes",10); lesson.status=snapshot.get("status","draft"); lesson.published=bool(snapshot.get("published",False)); lesson.content_version += 1; audit(db,user,"lesson_revision_restored","lesson",lesson.id); db.commit(); return lesson_payload(lesson)
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
