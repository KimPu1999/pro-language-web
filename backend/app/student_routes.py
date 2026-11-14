import json
from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from .auth import SESSION_COOKIE, current_user, require_csrf, verified_user, hash_token, now
from .db import get_db
from .models import AuthSession, Course, CourseModule, Enrollment, Lesson, LessonBookmark, LessonProgress, LessonQuiz, QuizAttempt, QuizQuestion, User, UserProfile
from .schemas import DashboardOut, EnrollmentOut, ProfileIn, ProgressIn, QuizAnswerIn, QuizOut, UserOut
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
@router.post("/lessons/{lesson_id}/visit")
def visit_lesson(lesson_id, user: User=Depends(verified_user), __: None=Depends(require_csrf), db: Session=Depends(get_db)):
    """Record last-visited time without changing completion state."""
    lesson=db.scalar(select(Lesson).join(CourseModule).join(Course).where(Lesson.id==lesson_id,Lesson.published.is_(True),Course.published.is_(True)))
    if not lesson: raise HTTPException(404,"Published lesson not found")
    course_id=db.scalar(select(CourseModule.course_id).where(CourseModule.id==lesson.module_id)); enrollment=db.scalar(select(Enrollment).where(Enrollment.user_id==user.id,Enrollment.course_id==course_id))
    if not enrollment: raise HTTPException(403,"Enroll in this course first")
    progress=db.scalar(select(LessonProgress).where(LessonProgress.user_id==user.id,LessonProgress.lesson_id==lesson_id))
    if not progress: progress=LessonProgress(user_id=user.id,lesson_id=lesson_id,completed=False); db.add(progress)
    progress.last_visited_at=now(); db.commit()
    return {"lesson_id":lesson_id,"completed":progress.completed,"last_visited_at":progress.last_visited_at}
@router.get("/courses/{course_slug}/progress")
def course_progress(course_slug: str, user: User=Depends(current_user), db: Session=Depends(get_db)):
    course=db.scalar(course_base().where(Course.slug==course_slug))
    if not course: raise HTTPException(404,"Published course not found")
    rows=db.execute(select(Lesson.id,Lesson.title,Lesson.order_index,CourseModule.id,CourseModule.title,CourseModule.order_index).join(CourseModule,Lesson.module_id==CourseModule.id).where(CourseModule.course_id==course.id,Lesson.published.is_(True)).order_by(CourseModule.order_index,Lesson.order_index)).all()
    progress_rows=db.scalars(select(LessonProgress).where(LessonProgress.user_id==user.id,LessonProgress.lesson_id.in_([row[0] for row in rows]) if rows else False)).all() if rows else []
    progress_by_lesson={row.lesson_id: row for row in progress_rows}
    lessons=[{"lesson_id":str(lesson_id),"title":title,"position":lesson_position,"module_id":str(module_id),"module_title":module_title,"module_position":module_position,"completed":bool(progress_by_lesson.get(lesson_id) and progress_by_lesson[lesson_id].completed),"last_visited_at":progress_by_lesson[lesson_id].last_visited_at.isoformat() if progress_by_lesson.get(lesson_id) and progress_by_lesson[lesson_id].last_visited_at else None} for lesson_id,title,lesson_position,module_id,module_title,module_position in rows]
    completed=sum(1 for item in lessons if item["completed"]); total=len(lessons)
    module_rows={}
    for item in lessons:
        module=module_rows.setdefault(item["module_id"],{"module_id":item["module_id"],"title":item["module_title"],"position":item["module_position"],"total_lessons":0,"completed_lessons":0})
        module["total_lessons"]+=1; module["completed_lessons"]+=1 if item["completed"] else 0
    modules=[{**module,"progress_percent":round(module["completed_lessons"]/module["total_lessons"]*100,1) if module["total_lessons"] else 0} for module in sorted(module_rows.values(),key=lambda row:row["position"])]
    last_visited=max((item for item in lessons if item["last_visited_at"]),key=lambda item:item["last_visited_at"],default=None)
    return {"course_slug":course.slug,"course_title":course.title,"total_lessons":total,"completed_lessons":completed,"progress_percent":round(completed/total*100,1) if total else 0,"last_visited_lesson_id":last_visited["lesson_id"] if last_visited else None,"modules":modules,"lessons":lessons}
def quiz_for_lesson(lesson_id, db):
    lesson=db.scalar(select(Lesson).join(CourseModule).join(Course).where(Lesson.id==lesson_id,Lesson.published.is_(True),Course.published.is_(True)))
    if not lesson: raise HTTPException(404,"Published lesson not found")
    quiz=db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id==lesson.id,LessonQuiz.status=="published"))
    if not quiz: raise HTTPException(404,"Quiz not available for this lesson")
    questions=db.scalars(select(QuizQuestion).where(QuizQuestion.quiz_id==quiz.id).order_by(QuizQuestion.position)).all()
    return quiz, questions
@router.get("/lessons/{lesson_id}/quiz", response_model=QuizOut)
def lesson_quiz(lesson_id, user: User=Depends(current_user), db: Session=Depends(get_db)):
    quiz, questions=quiz_for_lesson(lesson_id,db)
    latest=db.scalar(select(QuizAttempt).where(QuizAttempt.quiz_id==quiz.id,QuizAttempt.user_id==user.id).order_by(QuizAttempt.created_at.desc()))
    return {"id":quiz.id,"lesson_id":quiz.lesson_id,"title":quiz.title,"explanation":quiz.explanation,"questions":[{"id":q.id,"prompt":q.prompt,"question_type":q.question_type,"options":json.loads(q.options_json),"position":q.position} for q in questions],"latest_attempt":{"score":latest.score,"total":latest.total,"created_at":latest.created_at} if latest else None}
@router.post("/lessons/{lesson_id}/quiz", response_model=dict)
def submit_lesson_quiz(lesson_id, payload: QuizAnswerIn, user: User=Depends(verified_user), __: None=Depends(require_csrf), db: Session=Depends(get_db)):
    quiz, questions=quiz_for_lesson(lesson_id,db)
    course_id=db.scalar(select(CourseModule.course_id).join(Lesson,Lesson.module_id==CourseModule.id).where(Lesson.id==lesson_id))
    if not db.scalar(select(Enrollment).where(Enrollment.user_id==user.id,Enrollment.course_id==course_id)): raise HTTPException(403,"Enroll in this course first")
    answers={str(key): str(value) for key,value in payload.answers.items()}; correct=sum(1 for q in questions if answers.get(str(q.id)) == q.correct_answer)
    attempt=QuizAttempt(quiz_id=quiz.id,user_id=user.id,answers_json=json.dumps(answers),score=correct,total=len(questions)); db.add(attempt); db.commit()
    return {"attempt_id":attempt.id,"score":correct,"total":len(questions),"passed":bool(questions) and correct==len(questions),"feedback":[{"question_id":q.id,"correct":answers.get(str(q.id))==q.correct_answer,"explanation":q.explanation} for q in questions]}
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
