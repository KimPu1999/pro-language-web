from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from .auth import SESSION_COOKIE, current_user, require_csrf, verified_user, hash_token, now
from .db import get_db
from .models import AuthSession, Course, CourseModule, Enrollment, Lesson, LessonBookmark, LessonProgress, User, UserProfile
from .schemas import DashboardOut, EnrollmentOut, ProfileIn, ProgressIn, UserOut
router=APIRouter(prefix="/api/v1/me", tags=["student"])
def course_base(): return select(Course).options(selectinload(Course.language),selectinload(Course.category)).where(Course.published.is_(True))
def profile_payload(user, profile): return {"id":user.id,"email":user.email,"full_name":user.display_name,"role":user.role,"email_verified":bool(user.email_verified_at),"email_verified_at":user.email_verified_at,"profile":{"bio":profile.bio if profile else None,"learning_interests":profile.learning_interests.split("|") if profile and profile.learning_interests else [],"preferred_language":profile.preferred_language if profile else None,"learning_level":profile.learning_level if profile else None,"show_myanmar":profile.show_myanmar if profile else False,"avatar_url":profile.avatar_url if profile else None}}
def enrollment_payload(db, enrollment):
    course=db.scalar(course_base().where(Course.id==enrollment.course_id)); lesson_ids=db.scalars(select(Lesson.id).join(CourseModule).where(CourseModule.course_id==course.id,Lesson.published.is_(True))).all(); completed=db.scalar(select(func.count(LessonProgress.id)).where(LessonProgress.user_id==enrollment.user_id,LessonProgress.lesson_id.in_(lesson_ids),LessonProgress.completed.is_(True))) if lesson_ids else 0; last=db.scalar(select(Lesson.slug).join(LessonProgress,LessonProgress.lesson_id==Lesson.id).join(CourseModule).where(LessonProgress.user_id==enrollment.user_id,CourseModule.course_id==course.id).order_by(LessonProgress.last_visited_at.desc()).limit(1)); total=len(lesson_ids); return {"id":enrollment.id,"course":course,"completed_lessons":completed or 0,"total_lessons":total,"progress_percent":round(((completed or 0)/total)*100,1) if total else 0,"last_lesson_slug":last}
@router.get("/profile", response_model=UserOut)
def get_profile(user: User=Depends(current_user), db: Session=Depends(get_db)): return profile_payload(user,db.scalar(select(UserProfile).where(UserProfile.user_id==user.id)))
@router.patch("/profile", response_model=UserOut)
def update_profile(payload: ProfileIn, user: User=Depends(current_user), _: None=Depends(require_csrf), db: Session=Depends(get_db)):
    user.display_name=payload.full_name.strip(); profile=db.scalar(select(UserProfile).where(UserProfile.user_id==user.id)) or UserProfile(user_id=user.id); profile.bio=payload.bio; profile.learning_interests="|".join(payload.learning_interests); profile.preferred_language=payload.preferred_language; profile.learning_level=payload.learning_level; profile.show_myanmar=payload.show_myanmar; db.add(profile); db.commit(); return profile_payload(user,profile)
@router.post("/enrollments/{course_slug}",response_model=EnrollmentOut,status_code=201)
def enroll(course_slug: str, user: User=Depends(verified_user), __: None=Depends(require_csrf), db: Session=Depends(get_db)):
    course=db.scalar(course_base().where(Course.slug==course_slug))
    if not course: raise HTTPException(404,"Published course not found")
    if db.scalar(select(Enrollment).where(Enrollment.user_id==user.id,Enrollment.course_id==course.id)): raise HTTPException(409,"Already enrolled")
    enrollment=Enrollment(user_id=user.id,course_id=course.id); db.add(enrollment); db.commit(); return enrollment_payload(db,enrollment)
@router.get("/enrollments",response_model=list[EnrollmentOut])
def enrollments(user: User=Depends(current_user), db: Session=Depends(get_db)):
    return [enrollment_payload(db,e) for e in db.scalars(select(Enrollment).where(Enrollment.user_id==user.id).order_by(Enrollment.created_at.desc())).all()]
@router.get("/dashboard",response_model=DashboardOut)
def dashboard(user: User=Depends(current_user), db: Session=Depends(get_db)):
    rows=[enrollment_payload(db,e) for e in db.scalars(select(Enrollment).where(Enrollment.user_id==user.id).order_by(Enrollment.created_at.desc())).all()]; total=sum(x["total_lessons"] for x in rows); complete=sum(x["completed_lessons"] for x in rows); activity=[{"course_slug":x["course"].slug,"lesson_slug":x["last_lesson_slug"],"progress_percent":x["progress_percent"]} for x in rows if x["last_lesson_slug"]]; return {"enrollments":rows,"completed_lessons":complete,"overall_progress":round(complete/total*100,1) if total else 0,"recent_activity":activity}
@router.post("/lessons/{lesson_id}/progress")
def update_progress(lesson_id, payload: ProgressIn, user: User=Depends(verified_user), __: None=Depends(require_csrf), db: Session=Depends(get_db)):
    lesson=db.scalar(select(Lesson).join(CourseModule).join(Course).where(Lesson.id==lesson_id,Lesson.published.is_(True),Course.published.is_(True)))
    if not lesson: raise HTTPException(404,"Published lesson not found")
    course_id=db.scalar(select(CourseModule.course_id).where(CourseModule.id==lesson.module_id)); enrollment=db.scalar(select(Enrollment).where(Enrollment.user_id==user.id,Enrollment.course_id==course_id))
    if not enrollment: raise HTTPException(403,"Enroll in this course first")
    progress=db.scalar(select(LessonProgress).where(LessonProgress.user_id==user.id,LessonProgress.lesson_id==lesson_id)) or LessonProgress(user_id=user.id,lesson_id=lesson_id); progress.completed=payload.completed; progress.last_visited_at=now(); db.add(progress); db.commit(); return {"lesson_id":lesson_id,"completed":progress.completed}
@router.post("/lessons/{lesson_id}/bookmark")
def toggle_bookmark(lesson_id, user: User=Depends(verified_user), __: None=Depends(require_csrf), db: Session=Depends(get_db)):
    lesson=db.scalar(select(Lesson).join(CourseModule).join(Course).where(Lesson.id==lesson_id,Lesson.published.is_(True),Course.published.is_(True)))
    if not lesson: raise HTTPException(404,"Published lesson not found")
    row=db.scalar(select(LessonBookmark).where(LessonBookmark.user_id==user.id,LessonBookmark.lesson_id==lesson_id))
    if row: db.delete(row); bookmarked=False
    else: db.add(LessonBookmark(user_id=user.id,lesson_id=lesson_id)); bookmarked=True
    db.commit(); return {"lesson_id": lesson_id, "bookmarked": bookmarked}
@router.post("/sessions/revoke-others")
def revoke_other_sessions(response: Response, session_token: str|None=Cookie(default=None,alias=SESSION_COOKIE), user: User=Depends(current_user), _: None=Depends(require_csrf), db: Session=Depends(get_db)):
    current_hash=hash_token(session_token) if session_token else ""; db.query(AuthSession).filter(AuthSession.user_id==user.id,AuthSession.token_hash!=current_hash,AuthSession.revoked_at.is_(None)).update({"revoked_at":now()}); db.commit(); return {"status":"revoked"}
