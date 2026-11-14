import csv, io, json, math
from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select, union
from sqlalchemy.orm import Session
from .auth import current_user, require_csrf
from .db import get_db
from .models import (AnalyticsAuditLog, AnalyticsReportExport, ChallengeSubmission, CommunityAnswer,
    CommunityPost, Course, CourseInstructor, CourseModule, Enrollment, IssuedCertificate, Lesson, LessonProgress,
    StudentAchievement, User)
from .config import settings
from .rbac import PLATFORM_ADMIN_ROLES, require_platform_admin

router = APIRouter(prefix="/api/v1/platform", tags=["platform analytics"])
ADMIN = PLATFORM_ADMIN_ROLES

def analytics_user(user: User = Depends(current_user)):
    if user.role not in ADMIN and user.role != "instructor": raise HTTPException(403, "Analytics access required")
    return user

def full_admin(user: User = Depends(current_user)):
    return require_platform_admin(user)

@router.get("/quality")
def quality_status(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    """Expose observed configuration and dependency status without inventing health data."""
    checks = [{"name": "api", "status": "healthy", "detail": "The API served this request."}]
    try:
        db.execute(select(1))
        checks.append({"name": "database", "status": "healthy", "detail": "Database connectivity is available."})
    except Exception:
        checks.append({"name": "database", "status": "error", "detail": "Database connectivity could not be verified."})
    checks.extend([
        {"name": "secure_runner", "status": "configured" if settings.runner_enabled else "not_configured", "detail": "Sandbox execution is enabled." if settings.runner_enabled else "Runner is disabled; submissions fail closed."},
        {"name": "ai_provider", "status": "configured" if settings.ai_enabled and settings.ai_provider != "disabled" else "not_configured", "detail": "AI provider is enabled." if settings.ai_enabled and settings.ai_provider != "disabled" else "AI provider is disabled or not configured."},
        {"name": "video_provider", "status": "configured" if settings.video_enabled and settings.video_provider != "disabled" else "not_configured", "detail": "Video provider is enabled." if settings.video_enabled and settings.video_provider != "disabled" else "Video provider is disabled or not configured."},
        {"name": "ci", "status": "not_configured", "detail": "CI status integration is not connected to this deployment."},
        {"name": "observability", "status": "partial", "detail": "Request correlation IDs are enabled; external telemetry is not configured."},
    ])
    return {"checks": checks, "generated_at": datetime.now(timezone.utc)}

def bounds(start: date|None, end: date|None):
    end = end or datetime.now(timezone.utc).date(); start = start or end - timedelta(days=29)
    if end < start: raise HTTPException(422, "end_date must be on or after start_date")
    return datetime.combine(start, time.min, timezone.utc), datetime.combine(end + timedelta(days=1), time.min, timezone.utc), start, end

def course_scope(db: Session, user: User):
    if user.role in ADMIN: return None
    return select(Course.id).where(or_(Course.created_by == user.id, Course.id.in_(select(CourseInstructor.course_id).where(CourseInstructor.user_id == user.id))))

def scoped_course_filter(query, db: Session, user: User, course_id: UUID|None = None, instructor_id: UUID|None = None):
    scope = course_scope(db, user)
    if scope is not None: query = query.where(Course.id.in_(scope))
    if course_id: query = query.where(Course.id == course_id)
    if instructor_id: query = query.where(or_(Course.created_by == instructor_id, Course.id.in_(select(CourseInstructor.course_id).where(CourseInstructor.user_id == instructor_id))))
    return query

def active_student_count(db: Session, start, end, user: User):
    queries = [select(Enrollment.user_id.label("user_id")).where(Enrollment.created_at >= start, Enrollment.created_at < end),
        select(LessonProgress.user_id.label("user_id")).where(LessonProgress.updated_at >= start, LessonProgress.updated_at < end),
        select(ChallengeSubmission.user_id.label("user_id")).where(ChallengeSubmission.created_at >= start, ChallengeSubmission.created_at < end)]
    if user.role not in ADMIN:
        scope = course_scope(db, user)
        queries[0] = queries[0].join(Course, Course.id == Enrollment.course_id).where(Course.id.in_(scope))
    activity = union(*queries).subquery()
    return db.scalar(select(func.count()).select_from(activity).join(User, User.id == activity.c.user_id).where(User.role == "student")) or 0

def completion_rows(db: Session, start, end, user: User, course_id: UUID|None = None):
    q = select(Enrollment.id, Enrollment.course_id, Enrollment.user_id).join(Course, Course.id == Enrollment.course_id).where(Enrollment.created_at < end)
    q = scoped_course_filter(q, db, user, course_id)
    enrollments = db.execute(q).all()
    if not enrollments:
        return []
    course_ids = {cid for _, cid, _ in enrollments}
    user_ids = {uid for _, _, uid in enrollments}
    totals = dict(db.execute(
        select(CourseModule.course_id, func.count(Lesson.id))
        .join(Lesson, Lesson.module_id == CourseModule.id)
        .where(CourseModule.course_id.in_(course_ids), Lesson.published.is_(True))
        .group_by(CourseModule.course_id)
    ).all())
    completed = {
        (cid, uid): count
        for cid, uid, count in db.execute(
            select(CourseModule.course_id, LessonProgress.user_id, func.count(LessonProgress.id))
            .join(Lesson, Lesson.module_id == CourseModule.id)
            .join(LessonProgress, LessonProgress.lesson_id == Lesson.id)
            .where(
                CourseModule.course_id.in_(course_ids),
                LessonProgress.user_id.in_(user_ids),
                Lesson.published.is_(True),
                LessonProgress.completed.is_(True),
            )
            .group_by(CourseModule.course_id, LessonProgress.user_id)
        ).all()
    }
    return [(enrollment_id, cid, totals.get(cid, 0), min(completed.get((cid, uid), 0), totals.get(cid, 0))) for enrollment_id, cid, uid in enrollments]

def definition_payload():
    return {"active_students": "Distinct students with enrollment, lesson progress, or challenge activity in the selected UTC period.", "completion_rate": "Enrollments with all published lessons completed divided by eligible enrollments; courses with zero published lessons are excluded.", "challenge_success_rate": "Accepted evaluated submissions divided by evaluated submissions; queued and infrastructure failures are excluded."}

@router.get("/analytics/overview")
def overview(start_date: date|None = Query(None), end_date: date|None = Query(None), course_id: UUID|None = None, instructor_id: UUID|None = None, user: User = Depends(full_admin), db: Session = Depends(get_db)):
    start, end, start_day, end_day = bounds(start_date, end_date)
    courses_q = scoped_course_filter(select(Course), db, user, course_id, instructor_id)
    courses_q = courses_q.where(Course.published.is_(True))
    published_courses = db.scalar(select(func.count()).select_from(courses_q.subquery())) or 0
    total_students = db.scalar(select(func.count(User.id)).where(User.role == "student")) or 0
    total_instructors = db.scalar(select(func.count(User.id)).where(User.role == "instructor")) or 0
    enroll_q = select(func.count(Enrollment.id)).join(Course, Course.id == Enrollment.course_id).where(Enrollment.created_at >= start, Enrollment.created_at < end)
    enroll_q = scoped_course_filter(enroll_q, db, user, course_id, instructor_id)
    enrollments = db.scalar(enroll_q) or 0
    submissions = db.scalar(select(func.count(ChallengeSubmission.id)).where(ChallengeSubmission.created_at >= start, ChallengeSubmission.created_at < end)) or 0
    certificates = db.scalar(select(func.count(IssuedCertificate.id)).where(IssuedCertificate.issued_at >= start, IssuedCertificate.issued_at < end, IssuedCertificate.revoked_at.is_(None))) or 0
    completion_data = completion_rows(db,start,end,user,course_id)
    completed = sum(total > 0 and done == total for _,_,total,done in completion_data)
    eligible = sum(total > 0 for _,_,total,_ in completion_data)
    return {"range":{"start":start_day.isoformat(),"end":end_day.isoformat()},"kpis":{"total_students":total_students,"active_students":active_student_count(db,start,end,user),"total_instructors":total_instructors,"published_courses":published_courses,"total_enrollments":enrollments,"completed_courses":completed,"coding_submissions":submissions,"certificates_issued":certificates},"trends":[{"date":(start_day+timedelta(days=i)).isoformat(),"enrollments":db.scalar(select(func.count(Enrollment.id)).where(Enrollment.created_at >= start+timedelta(days=i),Enrollment.created_at < start+timedelta(days=i+1))) or 0,"lesson_completions":db.scalar(select(func.count(LessonProgress.id)).where(LessonProgress.updated_at >= start+timedelta(days=i),LessonProgress.updated_at < start+timedelta(days=i+1),LessonProgress.completed.is_(True))) or 0} for i in range(min((end_day-start_day).days+1,90))],"completion_rate":round(completed/eligible*100,1) if eligible else 0,"definitions":definition_payload()}

@router.get("/analytics/students")
def students(start_date: date|None = Query(None), end_date: date|None = Query(None), page: int = Query(1,ge=1), page_size: int = Query(20,ge=1,le=100), user: User = Depends(full_admin), db: Session = Depends(get_db)):
    start,end,sd,ed=bounds(start_date,end_date); q=select(User).where(User.role=="student",User.created_at>=start,User.created_at<end).order_by(User.created_at.desc()); total=db.scalar(select(func.count()).select_from(q.subquery())) or 0; rows=db.scalars(q.offset((page-1)*page_size).limit(page_size)).all()
    return {"range":{"start":sd.isoformat(),"end":ed.isoformat()},"new_registrations":total,"active_students":active_student_count(db,start,end,user),"items":[{"id":r.id,"name":r.display_name,"joined_at":r.created_at} for r in rows],"page":page,"page_size":page_size,"total":total,"pages":math.ceil(total/page_size) if total else 0,"definitions":definition_payload()}

@router.get("/analytics/courses")
def courses(start_date: date|None = Query(None), end_date: date|None = Query(None), course_id: UUID|None = None, instructor_id: UUID|None = None, user: User = Depends(analytics_user), db: Session = Depends(get_db)):
    start,end,sd,ed=bounds(start_date,end_date); q=scoped_course_filter(select(Course).where(Course.published.is_(True)),db,user,course_id,instructor_id); rows=db.scalars(q.order_by(Course.title)).all(); items=[]
    for course in rows:
        enrollments=db.scalar(select(func.count(Enrollment.id)).where(Enrollment.course_id==course.id,Enrollment.created_at>=start,Enrollment.created_at<end)) or 0
        completions=[x for x in completion_rows(db,start,end,user,course.id) if x[2]>0]; completed=sum(x[3]==x[2] for x in completions); eligible=len(completions)
        lessons=db.scalar(select(func.count(Lesson.id)).join(CourseModule,CourseModule.id==Lesson.module_id).where(CourseModule.course_id==course.id,Lesson.published.is_(True))) or 0
        activity=db.scalar(select(func.count(LessonProgress.id)).join(Lesson,Lesson.id==LessonProgress.lesson_id).join(CourseModule,CourseModule.id==Lesson.module_id).where(CourseModule.course_id==course.id,LessonProgress.updated_at>=start,LessonProgress.updated_at<end)) or 0
        items.append({"id":course.id,"title":course.title,"enrollments":enrollments,"published_lessons":lessons,"lesson_activity":activity,"completion_rate":round(completed/eligible*100,1) if eligible else 0})
    return {"range":{"start":sd.isoformat(),"end":ed.isoformat()},"items":items,"definitions":definition_payload()}

@router.get("/analytics/instructors")
def instructors(start_date: date|None = Query(None), end_date: date|None = Query(None), user: User = Depends(analytics_user), db: Session = Depends(get_db)):
    start,end,sd,ed=bounds(start_date,end_date); ids=[user.id] if user.role=="instructor" else [x for x in db.scalars(select(User.id).where(User.role=="instructor")).all()]; items=[]
    for uid in ids:
        cq=select(Course.id).where(Course.created_by==uid); assigned=select(CourseInstructor.course_id).where(CourseInstructor.user_id==uid); cids=[*db.scalars(cq).all(),*db.scalars(assigned).all()]; cids=list(set(cids)); enrollments=db.scalar(select(func.count(Enrollment.id)).where(Enrollment.course_id.in_(cids),Enrollment.created_at>=start,Enrollment.created_at<end)) if cids else 0; items.append({"id":uid,"published_courses":db.scalar(select(func.count(Course.id)).where(Course.id.in_(cids),Course.published.is_(True))) if cids else 0,"enrollments":enrollments or 0})
    return {"range":{"start":sd.isoformat(),"end":ed.isoformat()},"items":items,"definitions":definition_payload()}

@router.get("/analytics/challenges")
def challenges(start_date: date|None = Query(None), end_date: date|None = Query(None), user: User = Depends(full_admin), db: Session = Depends(get_db)):
    start,end,sd,ed=bounds(start_date,end_date); base=select(ChallengeSubmission).where(ChallengeSubmission.created_at>=start,ChallengeSubmission.created_at<end); rows=db.scalars(base).all(); evaluated=[r for r in rows if r.status not in {"queued","running","internal_error"}]; accepted=sum(r.status=="accepted" for r in evaluated); return {"range":{"start":sd.isoformat(),"end":ed.isoformat()},"attempts":len(rows),"accepted":accepted,"failed":len(evaluated)-accepted,"success_rate":round(accepted/len(evaluated)*100,1) if evaluated else 0,"statuses":{s:sum(r.status==s for r in rows) for s in sorted({r.status for r in rows})},"languages":{s:sum(r.language==s for r in rows) for s in sorted({r.language for r in rows})},"definitions":definition_payload()}

@router.get("/analytics/learning")
def learning(start_date: date|None = Query(None), end_date: date|None = Query(None), user: User = Depends(full_admin), db: Session = Depends(get_db)):
    start,end,sd,ed=bounds(start_date,end_date); lessons=db.scalar(select(func.count(LessonProgress.id)).where(LessonProgress.updated_at>=start,LessonProgress.updated_at<end,LessonProgress.completed.is_(True))) or 0; achievements=db.scalar(select(func.count(StudentAchievement.id)).where(StudentAchievement.awarded_at>=start,StudentAchievement.awarded_at<end)) or 0
    return {"range":{"start":sd.isoformat(),"end":ed.isoformat()},"lesson_completions":lessons,"verified_milestones":achievements,"weekly_activity":[{"week":(sd+timedelta(days=i)).isoformat(),"completions":db.scalar(select(func.count(LessonProgress.id)).where(LessonProgress.updated_at>=start+timedelta(days=i),LessonProgress.updated_at<start+timedelta(days=i+7),LessonProgress.completed.is_(True))) or 0} for i in range(0,min((ed-sd).days+1,84),7)],"definitions":definition_payload()}

@router.get("/analytics/certificates")
def certificates(start_date: date|None = Query(None), end_date: date|None = Query(None), user: User = Depends(full_admin), db: Session = Depends(get_db)):
    start,end,sd,ed=bounds(start_date,end_date); issued=db.scalar(select(func.count(IssuedCertificate.id)).where(IssuedCertificate.issued_at>=start,IssuedCertificate.issued_at<end)) or 0; active=db.scalar(select(func.count(IssuedCertificate.id)).where(IssuedCertificate.issued_at<end,IssuedCertificate.revoked_at.is_(None))) or 0; revoked=db.scalar(select(func.count(IssuedCertificate.id)).where(IssuedCertificate.issued_at>=start,IssuedCertificate.issued_at<end,IssuedCertificate.revoked_at.is_not(None))) or 0; return {"range":{"start":sd.isoformat(),"end":ed.isoformat()},"issued":issued,"active":active,"revoked":revoked,"definitions":definition_payload()}

@router.get("/analytics/community")
def community(start_date: date|None = Query(None), end_date: date|None = Query(None), user: User = Depends(full_admin), db: Session = Depends(get_db)):
    start,end,sd,ed=bounds(start_date,end_date); posts=db.scalar(select(func.count(CommunityPost.id)).where(CommunityPost.created_at>=start,CommunityPost.created_at<end,CommunityPost.status=="published")) or 0; answers=db.scalar(select(func.count(CommunityAnswer.id)).where(CommunityAnswer.created_at>=start,CommunityAnswer.created_at<end,CommunityAnswer.status=="published")) or 0; accepted=db.scalar(select(func.count(CommunityPost.id)).where(CommunityPost.created_at>=start,CommunityPost.created_at<end,CommunityPost.accepted_answer_id.is_not(None))) or 0; return {"range":{"start":sd.isoformat(),"end":ed.isoformat()},"posts":posts,"answers":answers,"accepted_answers":accepted,"definitions":definition_payload()}

@router.get("/reports")
def report_history(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),user:User=Depends(full_admin),db:Session=Depends(get_db)):
    q=select(AnalyticsReportExport).order_by(AnalyticsReportExport.created_at.desc()); total=db.scalar(select(func.count()).select_from(AnalyticsReportExport)) or 0; return {"exports":[{"id":x.id,"report_type":x.report_type,"row_count":x.row_count,"status":x.status,"created_at":x.created_at} for x in db.scalars(q.offset((page-1)*page_size).limit(page_size)).all()],"page":page,"page_size":page_size,"total":total,"pages":math.ceil(total/page_size) if total else 0}

@router.post("/reports/export")
def export_report(report_type:str=Query("overview"),start_date:date|None=Query(None),end_date:date|None=Query(None),user:User=Depends(full_admin),db:Session=Depends(get_db),_:None=Depends(require_csrf)):
    start,end,sd,ed=bounds(start_date,end_date); ifilter={"start_date":sd.isoformat(),"end_date":ed.isoformat()}; overview_data=overview(sd,ed,None,None,user,db); output=io.StringIO(); writer=csv.writer(output); writer.writerow(["metric","value"]); writer.writerows([[key,value] for key,value in overview_data["kpis"].items()]); row_count=len(overview_data["kpis"]); db.add(AnalyticsReportExport(requested_by=user.id,report_type=report_type,filters_json=json.dumps(ifilter),row_count=row_count)); db.add(AnalyticsAuditLog(actor_id=user.id,action="analytics_export",report_type=report_type,filters_json=json.dumps(ifilter))); db.commit(); from fastapi.responses import Response; return Response(output.getvalue(),media_type="text/csv",headers={"Content-Disposition":f'attachment; filename="codemaster-{report_type}-{sd.isoformat()}.csv"'})
