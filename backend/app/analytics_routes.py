import csv, io, json, math
from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import func, or_, select, union
from sqlalchemy.orm import Session
from .auth import check_rate_limit, current_user, require_csrf
from .db import get_db
from .models import (AnalyticsAuditLog, AnalyticsReportExport, Challenge, ChallengeSubmission, CommunityAnswer,
    CommunityPost, Course, CourseInstructor, CourseModule, CourseRevision, Enrollment, IssuedCertificate,
    Lesson, LessonProgress, LessonRevision, ProjectCourseLink, ProjectReview, ProjectSubmission, ProjectTemplate,
    StudentAchievement, StudentProject, User)
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
    new_registrations = db.scalar(select(func.count(User.id)).where(User.role == "student", User.created_at >= start, User.created_at < end)) or 0
    return {"range":{"start":start_day.isoformat(),"end":end_day.isoformat()},"kpis":{"total_students":total_students,"new_registrations":new_registrations,"active_students":active_student_count(db,start,end,user),"total_instructors":total_instructors,"published_courses":published_courses,"total_enrollments":enrollments,"completed_courses":completed,"coding_submissions":submissions,"challenge_submissions":submissions,"certificates_issued":certificates},"trends":[{"date":(start_day+timedelta(days=i)).isoformat(),"enrollments":db.scalar(select(func.count(Enrollment.id)).where(Enrollment.created_at >= start+timedelta(days=i),Enrollment.created_at < start+timedelta(days=i+1))) or 0,"lesson_completions":db.scalar(select(func.count(LessonProgress.id)).where(LessonProgress.updated_at >= start+timedelta(days=i),LessonProgress.updated_at < start+timedelta(days=i+1),LessonProgress.completed.is_(True))) or 0} for i in range(min((end_day-start_day).days+1,90))],"completion_rate":round(completed/eligible*100,1) if eligible else 0,"definitions":definition_payload()}

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
    items.sort(key=lambda item: (-item["enrollments"], item["title"].lower()))
    return {"range":{"start":sd.isoformat(),"end":ed.isoformat()},"items":items,"definitions":definition_payload()}

@router.get("/analytics/instructors")
def instructors(start_date: date|None = Query(None), end_date: date|None = Query(None), user: User = Depends(analytics_user), db: Session = Depends(get_db)):
    start,end,sd,ed=bounds(start_date,end_date); ids=[user.id] if user.role=="instructor" else [x for x in db.scalars(select(User.id).where(User.role=="instructor")).all()]; items=[]
    for uid in ids:
        cq=select(Course.id).where(Course.created_by==uid); assigned=select(CourseInstructor.course_id).where(CourseInstructor.user_id==uid); cids=[*db.scalars(cq).all(),*db.scalars(assigned).all()]; cids=list(set(cids)); enrollments=db.scalar(select(func.count(Enrollment.id)).where(Enrollment.course_id.in_(cids),Enrollment.created_at>=start,Enrollment.created_at<end)) if cids else 0; items.append({"id":uid,"published_courses":db.scalar(select(func.count(Course.id)).where(Course.id.in_(cids),Course.published.is_(True))) if cids else 0,"enrollments":enrollments or 0})
    return {"range":{"start":sd.isoformat(),"end":ed.isoformat()},"items":items,"definitions":definition_payload()}


# Instructor intelligence uses a separate contract from the legacy platform
# overview above.  The legacy endpoint remains available for compatibility,
# while these endpoints expose one shared UTC window and one attribution rule.
def instructor_bounds(
    start_date: date|None,
    end_date: date|None,
    start_utc: datetime|None,
    end_utc: datetime|None,
):
    if (start_utc is None) != (end_utc is None):
        raise HTTPException(422, "start_utc and end_utc must be supplied together")
    if start_utc is not None and end_utc is not None:
        if start_utc.tzinfo is None or end_utc.tzinfo is None:
            raise HTTPException(422, "UTC reporting timestamps must include a timezone")
        start, end = start_utc.astimezone(timezone.utc), end_utc.astimezone(timezone.utc)
        if end <= start:
            raise HTTPException(422, "end_utc must be after start_utc")
        start_day, end_day = start.date(), (end - timedelta(microseconds=1)).date()
    else:
        start, end, start_day, end_day = bounds(start_date, end_date)
    if end - start > timedelta(days=366):
        raise HTTPException(422, "The reporting range cannot exceed 366 days")
    return start, end, start_day, end_day


def normalize_utc(value: datetime|None) -> datetime|None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def instructor_ids(db: Session, user: User, instructor_id: UUID|None = None) -> list[UUID]:
    if user.role == "instructor" and instructor_id and instructor_id != user.id:
        raise HTTPException(403, "Instructors may only view their own analytics")
    q = select(User.id).where(User.role == "instructor")
    if user.role == "instructor":
        q = q.where(User.id == user.id)
    if instructor_id:
        q = q.where(User.id == instructor_id)
    ids = list(db.scalars(q).all())
    if instructor_id and not ids:
        raise HTTPException(404, "Instructor not found")
    return ids


def instructor_course_pairs():
    authored = (
        select(Course.created_by.label("instructor_id"), Course.id.label("course_id"))
        .join(User, User.id == Course.created_by)
        .where(User.role == "instructor", Course.created_by.is_not(None))
    )
    assigned = (
        select(CourseInstructor.user_id.label("instructor_id"), CourseInstructor.course_id.label("course_id"))
        .join(User, User.id == CourseInstructor.user_id)
        .where(User.role == "instructor")
    )
    return union(authored, assigned).subquery("instructor_course_pairs")


def instructor_sources() -> dict[str, str]:
    return {
        "instructors": "available",
        "courses": "available",
        "course_instructors": "available",
        "enrollments": "available",
        "lesson_progress": "available",
        "lesson_revisions": "available",
        "project_reviews": "available",
    }


def instructor_definitions() -> dict[str, str]:
    return {
        "total_instructors": "Distinct active users with role instructor, counted as of the reporting window end.",
        "active_instructors": "Instructors with a recorded lesson revision, published course revision, course assignment, or finalized project review during the UTC window.",
        "published_courses": "Distinct currently published courses associated with the selected instructor scope. Historical publication timestamps are unavailable on Course, so this is labeled as current state.",
        "new_enrollments": "Valid enrollment records created with created_at >= start_utc and created_at < end_utc.",
        "active_learners": "Distinct students with a completed or visited lesson-progress record in the selected associated courses during the UTC window.",
        "course_completions": "Distinct enrolled student-course pairs whose published lessons were all completed and whose last completion update fell inside the UTC window.",
        "lessons_published": "Lesson revision records created in the window for lessons that are currently published; the schema has no separate published_at field.",
        "project_reviews_completed": "ProjectReview records created by an instructor in the window. ProjectReview.created_at is the finalized review event available in this schema.",
        "review_turnaround": "Median duration from ProjectSubmission.submitted_at to ProjectReview.created_at for valid finalized reviews in the window.",
    }


def _grouped_count(db: Session, query) -> dict[str, int]:
    return {str(key): int(value or 0) for key, value in db.execute(query).all()}


def completion_counts_for_courses(db: Session, course_ids: set[UUID], start: datetime, end: datetime) -> dict[UUID, int]:
    if not course_ids:
        return {}
    totals = dict(db.execute(
        select(CourseModule.course_id, func.count(Lesson.id))
        .join(Lesson, Lesson.module_id == CourseModule.id)
        .where(CourseModule.course_id.in_(course_ids), Lesson.published.is_(True))
        .group_by(CourseModule.course_id)
    ).all())
    rows = db.execute(
        select(
            CourseModule.course_id,
            LessonProgress.user_id,
            func.count(func.distinct(LessonProgress.lesson_id)),
            func.max(LessonProgress.updated_at),
        )
        .join(Lesson, Lesson.module_id == CourseModule.id)
        .join(LessonProgress, LessonProgress.lesson_id == Lesson.id)
        .join(Enrollment, (Enrollment.course_id == CourseModule.course_id) & (Enrollment.user_id == LessonProgress.user_id))
        .where(
            CourseModule.course_id.in_(course_ids),
            Lesson.published.is_(True),
            LessonProgress.completed.is_(True),
            Enrollment.created_at < end,
        )
        .group_by(CourseModule.course_id, LessonProgress.user_id)
    ).all()
    result: dict[UUID, int] = {course_id: 0 for course_id in course_ids}
    for course_id, _user_id, completed_lessons, latest in rows:
        latest_utc = normalize_utc(latest)
        if totals.get(course_id, 0) and completed_lessons >= totals[course_id] and latest_utc and start <= latest_utc < end:
            result[course_id] += 1
    return result


def instructor_report_rows(
    db: Session,
    user: User,
    ids: list[UUID],
    start: datetime,
    end: datetime,
    course_id: UUID|None = None,
):
    if not ids:
        return [], {"active_ids": set(), "course_ids": set()}
    pair = instructor_course_pairs()
    pair_rows = db.execute(
        select(pair.c.instructor_id, pair.c.course_id)
        .where(pair.c.instructor_id.in_(ids), *( [pair.c.course_id == course_id] if course_id else [] ))
    ).all()
    courses_by_instructor: dict[UUID, set[UUID]] = {instructor_id: set() for instructor_id in ids}
    instructors_by_course: dict[UUID, set[UUID]] = {}
    for instructor_id, linked_course_id in pair_rows:
        courses_by_instructor[instructor_id].add(linked_course_id)
        instructors_by_course.setdefault(linked_course_id, set()).add(instructor_id)
    course_ids = set(instructors_by_course)
    published_courses = _grouped_count(db, select(pair.c.instructor_id, func.count(func.distinct(Course.id))).join(Course, Course.id == pair.c.course_id).where(pair.c.instructor_id.in_(ids), Course.published.is_(True), *( [pair.c.course_id == course_id] if course_id else [] )).group_by(pair.c.instructor_id))
    published_lessons = _grouped_count(db, select(pair.c.instructor_id, func.count(func.distinct(Lesson.id))).join(Course, Course.id == pair.c.course_id).join(CourseModule, CourseModule.course_id == Course.id).join(Lesson, Lesson.module_id == CourseModule.id).where(pair.c.instructor_id.in_(ids), Lesson.published.is_(True), *( [pair.c.course_id == course_id] if course_id else [] )).group_by(pair.c.instructor_id))
    enrolled_learners = _grouped_count(db, select(pair.c.instructor_id, func.count(func.distinct(Enrollment.user_id))).join(Enrollment, Enrollment.course_id == pair.c.course_id).where(pair.c.instructor_id.in_(ids), Enrollment.created_at < end, *( [pair.c.course_id == course_id] if course_id else [] )).group_by(pair.c.instructor_id))
    active_learners = _grouped_count(db, select(pair.c.instructor_id, func.count(func.distinct(LessonProgress.user_id))).join(CourseModule, CourseModule.course_id == pair.c.course_id).join(Lesson, Lesson.module_id == CourseModule.id).join(LessonProgress, LessonProgress.lesson_id == Lesson.id).where(pair.c.instructor_id.in_(ids), LessonProgress.updated_at >= start, LessonProgress.updated_at < end, *( [pair.c.course_id == course_id] if course_id else [] )).group_by(pair.c.instructor_id))
    new_enrollments = _grouped_count(db, select(pair.c.instructor_id, func.count(func.distinct(Enrollment.id))).join(Enrollment, Enrollment.course_id == pair.c.course_id).where(pair.c.instructor_id.in_(ids), Enrollment.created_at >= start, Enrollment.created_at < end, *( [pair.c.course_id == course_id] if course_id else [] )).group_by(pair.c.instructor_id))
    completion_by_course = completion_counts_for_courses(db, course_ids, start, end)
    completions = {instructor_id: sum(completion_by_course.get(linked_course_id, 0) for linked_course_id in linked_courses) for instructor_id, linked_courses in courses_by_instructor.items()}
    review_counts = _grouped_count(db, select(ProjectReview.reviewer_id, func.count(ProjectReview.id)).where(ProjectReview.reviewer_id.in_(ids), ProjectReview.created_at >= start, ProjectReview.created_at < end).group_by(ProjectReview.reviewer_id))
    lesson_revision_counts = _grouped_count(db, select(LessonRevision.changed_by, func.count(LessonRevision.id)).join(Lesson, Lesson.id == LessonRevision.lesson_id).join(CourseModule, CourseModule.id == Lesson.module_id).where(LessonRevision.changed_by.in_(ids), LessonRevision.created_at >= start, LessonRevision.created_at < end, Lesson.published.is_(True), *( [CourseModule.course_id == course_id] if course_id else [] )).group_by(LessonRevision.changed_by))
    course_revision_counts = _grouped_count(db, select(CourseRevision.changed_by, func.count(CourseRevision.id)).where(CourseRevision.changed_by.in_(ids), CourseRevision.created_at >= start, CourseRevision.created_at < end, CourseRevision.status == "published", *( [CourseRevision.course_id == course_id] if course_id else [] )).group_by(CourseRevision.changed_by))
    assignment_counts = _grouped_count(db, select(CourseInstructor.user_id, func.count()).where(CourseInstructor.user_id.in_(ids), CourseInstructor.assigned_at >= start, CourseInstructor.assigned_at < end, *( [CourseInstructor.course_id == course_id] if course_id else [] )).group_by(CourseInstructor.user_id))
    active_ids = {UUID(key) for key in set(review_counts) | set(lesson_revision_counts) | set(course_revision_counts) | set(assignment_counts)}
    turnaround_rows = db.execute(
        select(ProjectReview.reviewer_id, ProjectSubmission.submitted_at, ProjectReview.created_at)
        .join(ProjectSubmission, ProjectSubmission.id == ProjectReview.submission_id)
        .where(ProjectReview.reviewer_id.in_(ids), ProjectReview.created_at >= start, ProjectReview.created_at < end, ProjectSubmission.submitted_at.is_not(None))
    ).all()
    turnaround: dict[UUID, list[float]] = {instructor_id: [] for instructor_id in ids}
    for reviewer_id, submitted_at, reviewed_at in turnaround_rows:
        if reviewed_at and submitted_at and reviewed_at >= submitted_at:
            turnaround[reviewer_id].append((reviewed_at - submitted_at).total_seconds() / 3600)
    last_activity: dict[UUID, datetime|None] = {instructor_id: None for instructor_id in ids}
    for instructor_id, linked_courses in courses_by_instructor.items():
        if linked_courses:
            last_activity[instructor_id] = db.scalar(select(func.max(Course.updated_at)).where(Course.id.in_(linked_courses)))
    for instructor_id, value in db.execute(select(LessonRevision.changed_by, func.max(LessonRevision.created_at)).where(LessonRevision.changed_by.in_(ids)).group_by(LessonRevision.changed_by)).all():
        if value and (not last_activity[instructor_id] or value > last_activity[instructor_id]): last_activity[instructor_id] = value
    for instructor_id, value in db.execute(select(ProjectReview.reviewer_id, func.max(ProjectReview.created_at)).where(ProjectReview.reviewer_id.in_(ids)).group_by(ProjectReview.reviewer_id)).all():
        if value and (not last_activity[instructor_id] or value > last_activity[instructor_id]): last_activity[instructor_id] = value
    users = {row.id: row for row in db.scalars(select(User).where(User.id.in_(ids))).all()}
    rows = []
    for instructor_id in ids:
        person = users[instructor_id]
        hours = sorted(turnaround[instructor_id])
        rows.append({
            "id": instructor_id,
            "display_name": person.display_name,
            "email": person.email if user.role in ADMIN else None,
            "associated_courses": len(courses_by_instructor[instructor_id]),
            "published_courses": published_courses.get(str(instructor_id), 0),
            "published_lessons": published_lessons.get(str(instructor_id), 0),
            "published_lesson_revisions": lesson_revision_counts.get(str(instructor_id), 0),
            "enrolled_learners": enrolled_learners.get(str(instructor_id), 0),
            "active_learners": active_learners.get(str(instructor_id), 0),
            "course_completions": completions[instructor_id],
            "completed_reviews": review_counts.get(str(instructor_id), 0),
            "review_turnaround_hours": round(sorted(hours)[len(hours) // 2], 2) if hours else None,
            "last_recorded_activity": last_activity[instructor_id],
            "activity_state": "available" if instructor_id in active_ids else "no_activity_recorded",
        })
    return rows, {"active_ids": active_ids, "course_ids": course_ids, "courses_by_instructor": courses_by_instructor, "instructors_by_course": instructors_by_course}


def instructor_window_params():
    return {
        "start_date": Query(None), "end_date": Query(None),
        "start_utc": Query(None), "end_utc": Query(None),
    }


@router.get("/analytics/instructors/overview")
def instructor_overview(
    start_date: date|None = Query(None), end_date: date|None = Query(None),
    start_utc: datetime|None = Query(None), end_utc: datetime|None = Query(None),
    instructor_id: UUID|None = None, course_id: UUID|None = None,
    compare_start_utc: datetime|None = Query(None), compare_end_utc: datetime|None = Query(None),
    user: User = Depends(analytics_user), db: Session = Depends(get_db),
):
    start, end, start_day, end_day = instructor_bounds(start_date, end_date, start_utc, end_utc)
    ids = instructor_ids(db, user, instructor_id)
    rows, metadata = instructor_report_rows(db, user, ids, start, end, course_id)
    pair = instructor_course_pairs()
    scoped_course_ids = metadata["course_ids"]
    if course_id:
        filtered_instructors = {row[0] for row in db.execute(select(pair.c.instructor_id).where(pair.c.course_id == course_id, pair.c.instructor_id.in_(ids))).all()}
        total_instructors = len(filtered_instructors)
    else:
        total_instructors = db.scalar(select(func.count(User.id)).where(User.role == "instructor", User.created_at < end, *( [User.id == instructor_id] if instructor_id else [] ))) or 0
        if user.role == "instructor": total_instructors = 1
    published_courses = db.scalar(select(func.count(func.distinct(Course.id))).where(Course.id.in_(scoped_course_ids), Course.published.is_(True))) if scoped_course_ids else 0
    new_enrollments = db.scalar(select(func.count(Enrollment.id)).where(Enrollment.course_id.in_(scoped_course_ids), Enrollment.created_at >= start, Enrollment.created_at < end)) if scoped_course_ids else 0
    active_learners = db.scalar(select(func.count(func.distinct(LessonProgress.user_id))).join(Lesson, Lesson.id == LessonProgress.lesson_id).join(CourseModule, CourseModule.id == Lesson.module_id).where(CourseModule.course_id.in_(scoped_course_ids), LessonProgress.updated_at >= start, LessonProgress.updated_at < end)) if scoped_course_ids else 0
    completion_by_course = completion_counts_for_courses(db, scoped_course_ids, start, end)
    course_completions = sum(completion_by_course.values())
    lessons_published = db.scalar(select(func.count(LessonRevision.id)).join(Lesson, Lesson.id == LessonRevision.lesson_id).join(CourseModule, CourseModule.id == Lesson.module_id).where(CourseModule.course_id.in_(scoped_course_ids), LessonRevision.created_at >= start, LessonRevision.created_at < end, Lesson.published.is_(True))) if scoped_course_ids else 0
    review_query = select(func.count(ProjectReview.id)).join(User, User.id == ProjectReview.reviewer_id).where(User.role == "instructor", ProjectReview.created_at >= start, ProjectReview.created_at < end, *( [ProjectReview.reviewer_id == instructor_id] if instructor_id else [] ))
    if course_id:
        review_query = review_query.join(ProjectSubmission, ProjectSubmission.id == ProjectReview.submission_id).join(StudentProject, StudentProject.id == ProjectSubmission.student_project_id).join(ProjectCourseLink, ProjectCourseLink.project_id == StudentProject.project_id).where(ProjectCourseLink.course_id == course_id)
    project_reviews_completed = db.scalar(review_query) or 0
    pending_query = select(func.count(ProjectSubmission.id)).where(ProjectSubmission.status.in_(["submitted", "in_review", "changes_requested"]), *( [ProjectSubmission.reviewer_id == instructor_id] if instructor_id else [] ))
    pending_reviews = db.scalar(pending_query) or 0
    active_instructors = len(metadata["active_ids"])
    current = {"total_instructors": total_instructors, "active_instructors": active_instructors, "published_courses": published_courses or 0, "new_enrollments": new_enrollments or 0, "active_learners": active_learners or 0, "course_completions": course_completions, "lessons_published": lessons_published or 0, "project_reviews_completed": project_reviews_completed, "pending_project_reviews": pending_reviews}
    comparison = None
    if (compare_start_utc is None) != (compare_end_utc is None):
        raise HTTPException(422, "compare_start_utc and compare_end_utc must be supplied together")
    if compare_start_utc and compare_end_utc:
        previous_start, previous_end, _, _ = instructor_bounds(None, None, compare_start_utc, compare_end_utc)
    else:
        previous_end = start
        previous_start = start - (end - start)
    if previous_start and previous_end:
        previous_rows, previous_meta = instructor_report_rows(db, user, ids, previous_start, previous_end, course_id)
        previous_courses = previous_meta["course_ids"]
        previous = {"new_enrollments": db.scalar(select(func.count(Enrollment.id)).where(Enrollment.course_id.in_(previous_courses), Enrollment.created_at >= previous_start, Enrollment.created_at < previous_end)) if previous_courses else 0, "active_learners": db.scalar(select(func.count(func.distinct(LessonProgress.user_id))).join(Lesson, Lesson.id == LessonProgress.lesson_id).join(CourseModule, CourseModule.id == Lesson.module_id).where(CourseModule.course_id.in_(previous_courses), LessonProgress.updated_at >= previous_start, LessonProgress.updated_at < previous_end)) if previous_courses else 0, "course_completions": sum(completion_counts_for_courses(db, previous_courses, previous_start, previous_end).values()), "project_reviews_completed": sum(row["completed_reviews"] for row in previous_rows)}
        comparison = {key: {"current": current[key], "previous": previous[key], "difference": current[key] - previous[key], "percentage": round((current[key] - previous[key]) / previous[key] * 100, 1) if previous[key] else None} for key in previous}
    return {"range": {"start": start.isoformat(), "end": end.isoformat(), "start_date": start_day.isoformat(), "end_date": end_day.isoformat()}, "kpis": current, "comparison": comparison, "sources": instructor_sources(), "definitions": instructor_definitions(), "data_state": "available" if ids else "no_activity_recorded", "updated_at": datetime.now(timezone.utc)}


@router.get("/analytics/instructors/list")
def instructor_list(
    start_date: date|None = Query(None), end_date: date|None = Query(None),
    start_utc: datetime|None = Query(None), end_utc: datetime|None = Query(None),
    instructor_id: UUID|None = None, course_id: UUID|None = None,
    search: str|None = Query(None, max_length=120), status: str|None = Query(None, pattern="^(active|inactive)$"),
    sort: str = Query("activity_desc", pattern="^(activity_desc|name_asc|learners_desc|completions_desc|reviews_desc)$"),
    page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=50),
    user: User = Depends(analytics_user), db: Session = Depends(get_db),
):
    start, end, start_day, end_day = instructor_bounds(start_date, end_date, start_utc, end_utc)
    ids = instructor_ids(db, user, instructor_id)
    rows, metadata = instructor_report_rows(db, user, ids, start, end, course_id)
    if search:
        needle = search.strip().lower(); rows = [row for row in rows if needle in row["display_name"].lower() or (row["email"] and needle in row["email"].lower())]
    if status: rows = [row for row in rows if (row["activity_state"] == "available") == (status == "active")]
    if sort == "name_asc": rows.sort(key=lambda row: row["display_name"].lower())
    elif sort == "learners_desc": rows.sort(key=lambda row: (-row["active_learners"], row["display_name"].lower()))
    elif sort == "completions_desc": rows.sort(key=lambda row: (-row["course_completions"], row["display_name"].lower()))
    elif sort == "reviews_desc": rows.sort(key=lambda row: (-row["completed_reviews"], row["display_name"].lower()))
    else: rows.sort(key=lambda row: (row["last_recorded_activity"] is None, -(row["last_recorded_activity"].timestamp() if row["last_recorded_activity"] else 0)))
    total = len(rows); offset = (page - 1) * page_size
    return {"range": {"start": start.isoformat(), "end": end.isoformat(), "start_date": start_day.isoformat(), "end_date": end_day.isoformat()}, "items": rows[offset:offset + page_size], "page": page, "page_size": page_size, "total": total, "pages": math.ceil(total / page_size) if total else 0, "sources": instructor_sources(), "definitions": instructor_definitions(), "data_state": "available" if total else "no_activity_recorded"}


@router.get("/analytics/instructors/trends")
def instructor_trends(
    start_date: date|None = Query(None), end_date: date|None = Query(None),
    start_utc: datetime|None = Query(None), end_utc: datetime|None = Query(None),
    instructor_id: UUID|None = None, course_id: UUID|None = None,
    bucket: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    user: User = Depends(analytics_user), db: Session = Depends(get_db),
):
    start, end, start_day, end_day = instructor_bounds(start_date, end_date, start_utc, end_utc)
    ids = instructor_ids(db, user, instructor_id)
    _rows, metadata = instructor_report_rows(db, user, ids, start, end, course_id)
    course_ids = metadata["course_ids"]
    span = max(1, (end_day - start_day).days + 1)
    if bucket == "daily": step, count = timedelta(days=1), span
    elif bucket == "weekly": step, count = timedelta(days=7), math.ceil(span / 7)
    else:
        count = (end_day.year - start_day.year) * 12 + end_day.month - start_day.month + 1; step = None
    dates = []
    for index in range(count):
        point = start + (step * index if step else timedelta(0))
        if bucket == "monthly": point = datetime(point.year, point.month, 1, tzinfo=timezone.utc)
        dates.append(point)
    def bucket_index(value: datetime):
        value = normalize_utc(value)
        if bucket == "daily": return (value.date() - start_day).days
        if bucket == "weekly": return (value.date() - start_day).days // 7
        return (value.year - start_day.year) * 12 + value.month - start_day.month
    trend = [{"date": point.date().isoformat() if bucket != "monthly" else point.strftime("%Y-%m"), "activity": 0, "new_enrollments": 0, "active_learners": 0, "course_completions": 0, "project_reviews": 0, "lessons_published": 0, "_learners": set()} for point in dates]
    if course_ids:
        for created_at, in db.execute(select(Enrollment.created_at).where(Enrollment.course_id.in_(course_ids), Enrollment.created_at >= start, Enrollment.created_at < end)).all():
            index = bucket_index(created_at); trend[index]["new_enrollments"] += 1 if 0 <= index < count else 0
        for updated_at, student_id in db.execute(select(LessonProgress.updated_at, LessonProgress.user_id).join(Lesson, Lesson.id == LessonProgress.lesson_id).join(CourseModule, CourseModule.id == Lesson.module_id).where(CourseModule.course_id.in_(course_ids), LessonProgress.updated_at >= start, LessonProgress.updated_at < end)).all():
            index = bucket_index(updated_at)
            if 0 <= index < count: trend[index]["_learners"].add(student_id)
        for created_at, in db.execute(select(LessonRevision.created_at).join(Lesson, Lesson.id == LessonRevision.lesson_id).join(CourseModule, CourseModule.id == Lesson.module_id).where(CourseModule.course_id.in_(course_ids), LessonRevision.created_at >= start, LessonRevision.created_at < end, Lesson.published.is_(True))).all():
            index = bucket_index(created_at)
            if 0 <= index < count: trend[index]["lessons_published"] += 1
        for updated_at, in db.execute(select(LessonProgress.updated_at).join(Lesson, Lesson.id == LessonProgress.lesson_id).join(CourseModule, CourseModule.id == Lesson.module_id).where(CourseModule.course_id.in_(course_ids), LessonProgress.updated_at >= start, LessonProgress.updated_at < end, LessonProgress.completed.is_(True))).all():
            index = bucket_index(updated_at)
            if 0 <= index < count: trend[index]["course_completions"] += 1
    review_filter = [ProjectReview.reviewer_id.in_(ids), ProjectReview.created_at >= start, ProjectReview.created_at < end]
    for created_at, in db.execute(select(ProjectReview.created_at).where(*review_filter)).all():
        index = bucket_index(created_at)
        if 0 <= index < count: trend[index]["project_reviews"] += 1
    for item in trend:
        item["active_learners"] = len(item.pop("_learners")); item["activity"] = item["lessons_published"] + item["project_reviews"] + item["new_enrollments"]
    return {"range": {"start": start.isoformat(), "end": end.isoformat(), "start_date": start_day.isoformat(), "end_date": end_day.isoformat()}, "bucket": bucket, "items": trend, "sources": instructor_sources(), "definitions": instructor_definitions(), "data_state": "available" if any(item["activity"] for item in trend) else "no_activity_recorded"}


@router.get("/analytics/instructors/courses")
def instructor_courses(
    start_date: date|None = Query(None), end_date: date|None = Query(None),
    start_utc: datetime|None = Query(None), end_utc: datetime|None = Query(None),
    instructor_id: UUID|None = None, course_id: UUID|None = None,
    page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=50),
    user: User = Depends(analytics_user), db: Session = Depends(get_db),
):
    start, end, start_day, end_day = instructor_bounds(start_date, end_date, start_utc, end_utc)
    ids = instructor_ids(db, user, instructor_id)
    _rows, metadata = instructor_report_rows(db, user, ids, start, end, course_id)
    course_ids = metadata["course_ids"]
    if not course_ids: return {"range": {"start": start.isoformat(), "end": end.isoformat()}, "items": [], "page": page, "page_size": page_size, "total": 0, "pages": 0, "sources": instructor_sources(), "definitions": instructor_definitions(), "data_state": "no_activity_recorded"}
    courses = db.scalars(select(Course).where(Course.id.in_(course_ids)).order_by(Course.title)).all()
    pair = instructor_course_pairs()
    instructor_count = _grouped_count(db, select(pair.c.course_id, func.count(func.distinct(pair.c.instructor_id))).where(pair.c.course_id.in_(course_ids)).group_by(pair.c.course_id))
    items = []
    completion_counts = completion_counts_for_courses(db, course_ids, start, end)
    for course in courses:
        published_lessons = db.scalar(select(func.count(Lesson.id)).join(CourseModule, CourseModule.id == Lesson.module_id).where(CourseModule.course_id == course.id, Lesson.published.is_(True))) or 0
        enrollments = db.scalar(select(func.count(Enrollment.id)).where(Enrollment.course_id == course.id, Enrollment.created_at < end)) or 0
        new_enrollments = db.scalar(select(func.count(Enrollment.id)).where(Enrollment.course_id == course.id, Enrollment.created_at >= start, Enrollment.created_at < end)) or 0
        active_students = db.scalar(select(func.count(func.distinct(LessonProgress.user_id))).join(Lesson, Lesson.id == LessonProgress.lesson_id).join(CourseModule, CourseModule.id == Lesson.module_id).where(CourseModule.course_id == course.id, LessonProgress.updated_at >= start, LessonProgress.updated_at < end)) or 0
        items.append({"id": course.id, "title": course.title, "slug": course.slug, "published": course.published, "instructor_count": instructor_count.get(str(course.id), 0), "published_lessons": published_lessons, "enrolled_learners": enrollments, "new_enrollments": new_enrollments, "active_learners": active_students, "course_completions": completion_counts.get(course.id, 0)})
    total = len(items); offset = (page - 1) * page_size
    return {"range": {"start": start.isoformat(), "end": end.isoformat(), "start_date": start_day.isoformat(), "end_date": end_day.isoformat()}, "items": items[offset:offset + page_size], "page": page, "page_size": page_size, "total": total, "pages": math.ceil(total / page_size) if total else 0, "sources": instructor_sources(), "definitions": instructor_definitions(), "data_state": "available" if items else "no_activity_recorded"}


@router.get("/analytics/instructors/reviews")
def instructor_reviews(
    start_date: date|None = Query(None), end_date: date|None = Query(None),
    start_utc: datetime|None = Query(None), end_utc: datetime|None = Query(None),
    instructor_id: UUID|None = None,
    user: User = Depends(analytics_user), db: Session = Depends(get_db),
):
    start, end, start_day, end_day = instructor_bounds(start_date, end_date, start_utc, end_utc)
    ids = instructor_ids(db, user, instructor_id)
    review_rows = db.execute(select(ProjectReview.reviewer_id, ProjectReview.created_at, ProjectSubmission.submitted_at, ProjectReview.decision, ProjectReview.comments).join(ProjectSubmission, ProjectSubmission.id == ProjectReview.submission_id).where(ProjectReview.reviewer_id.in_(ids), ProjectReview.created_at >= start, ProjectReview.created_at < end)).all()
    durations = [(reviewed - submitted).total_seconds() / 3600 for _reviewer, reviewed, submitted, _decision, _comments in review_rows if reviewed and submitted and reviewed >= submitted]
    pending = db.scalar(select(func.count(ProjectSubmission.id)).where(ProjectSubmission.status.in_(["submitted", "in_review", "changes_requested"]), *( [ProjectSubmission.reviewer_id == instructor_id] if instructor_id else [] ))) or 0
    resubmissions = db.scalar(select(func.count()).select_from(select(ProjectSubmission.student_project_id).where(ProjectSubmission.created_at >= start, ProjectSubmission.created_at < end).group_by(ProjectSubmission.student_project_id).having(func.count(ProjectSubmission.id) > 1).subquery())) or 0
    completed = len(review_rows); feedback = sum(bool(comments.strip()) for _reviewer, _reviewed, _submitted, _decision, comments in review_rows)
    return {"range": {"start": start.isoformat(), "end": end.isoformat(), "start_date": start_day.isoformat(), "end_date": end_day.isoformat()}, "submitted_projects": db.scalar(select(func.count(ProjectSubmission.id)).where(ProjectSubmission.created_at >= start, ProjectSubmission.created_at < end)) or 0, "reviews_completed": completed, "pending_reviews": pending, "resubmissions": resubmissions, "feedback_completed": feedback, "median_turnaround_hours": round(sorted(durations)[len(durations) // 2], 2) if durations else None, "sources": instructor_sources(), "definitions": instructor_definitions(), "data_state": "available" if ids else "no_activity_recorded"}


def csv_safe(value) -> str:
    text = "" if value is None else str(value)
    return "'" + text if text[:1] in {"=", "+", "-", "@"} else text


@router.get("/analytics/instructors/export")
def export_instructor_analytics(
    start_date: date|None = Query(None), end_date: date|None = Query(None),
    start_utc: datetime|None = Query(None), end_utc: datetime|None = Query(None),
    instructor_id: UUID|None = None, course_id: UUID|None = None,
    search: str|None = Query(None, max_length=120),
    user: User = Depends(full_admin), db: Session = Depends(get_db),
):
    check_rate_limit(f"instructor-analytics-export:{user.id}", limit=10, window_seconds=60)
    start, end, start_day, end_day = instructor_bounds(start_date, end_date, start_utc, end_utc)
    ids = instructor_ids(db, user, instructor_id)
    rows, _metadata = instructor_report_rows(db, user, ids, start, end, course_id)
    if search:
        needle = search.strip().lower(); rows = [row for row in rows if needle in row["display_name"].lower() or (row["email"] and needle in row["email"].lower())]
    output = io.StringIO(); writer = csv.writer(output)
    writer.writerow(["instructor", "associated_courses", "published_courses", "published_lessons", "active_learners", "course_completions", "completed_reviews", "review_turnaround_hours", "last_recorded_activity"])
    for row in rows:
        writer.writerow([csv_safe(row[key]) for key in ("display_name", "associated_courses", "published_courses", "published_lessons", "active_learners", "course_completions", "completed_reviews", "review_turnaround_hours", "last_recorded_activity")])
    db.add(AnalyticsReportExport(requested_by=user.id, report_type="instructor_summary", filters_json=json.dumps({"start_utc": start.isoformat(), "end_utc": end.isoformat(), "instructor_id": str(instructor_id) if instructor_id else None, "course_id": str(course_id) if course_id else None}), row_count=len(rows)))
    db.add(AnalyticsAuditLog(actor_id=user.id, action="instructor_analytics_export", report_type="instructor_summary", filters_json=json.dumps({"start_utc": start.isoformat(), "end_utc": end.isoformat()})))
    db.commit()
    return Response(output.getvalue(), media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="instructors-{start_day.isoformat()}-{end_day.isoformat()}.csv"'})


@router.get("/analytics/instructors/{instructor_id}")
def instructor_detail(
    instructor_id: UUID,
    start_date: date|None = Query(None), end_date: date|None = Query(None),
    start_utc: datetime|None = Query(None), end_utc: datetime|None = Query(None),
    user: User = Depends(analytics_user), db: Session = Depends(get_db),
):
    start, end, start_day, end_day = instructor_bounds(start_date, end_date, start_utc, end_utc)
    ids = instructor_ids(db, user, instructor_id)
    rows, metadata = instructor_report_rows(db, user, ids, start, end)
    course_ids = metadata["courses_by_instructor"].get(instructor_id, set())
    course_items = db.execute(select(Course.id, Course.title, Course.slug, Course.published).where(Course.id.in_(course_ids)).order_by(Course.title)).all() if course_ids else []
    return {"range": {"start": start.isoformat(), "end": end.isoformat(), "start_date": start_day.isoformat(), "end_date": end_day.isoformat()}, "instructor": rows[0] if rows else None, "courses": [{"id": row[0], "title": row[1], "slug": row[2], "published": row[3]} for row in course_items], "sources": instructor_sources(), "definitions": instructor_definitions(), "data_state": rows[0]["activity_state"] if rows else "no_activity_recorded"}

@router.get("/analytics/challenges")
def challenges(start_date: date|None = Query(None), end_date: date|None = Query(None), user: User = Depends(full_admin), db: Session = Depends(get_db)):
    start,end,sd,ed=bounds(start_date,end_date); base=select(ChallengeSubmission).where(ChallengeSubmission.created_at>=start,ChallengeSubmission.created_at<end); rows=db.scalars(base).all(); evaluated=[r for r in rows if r.status not in {"queued","running","internal_error"}]; accepted=sum(r.status=="accepted" for r in evaluated); challenge_difficulty=dict(db.execute(select(Challenge.id,Challenge.difficulty).where(Challenge.id.in_({row.challenge_id for row in rows}))).all()) if rows else {}; difficulty={}
    for row in rows:
        name=challenge_difficulty.get(row.challenge_id,"unknown"); bucket=difficulty.setdefault(name,{"difficulty":name,"attempts":0,"accepted":0}); bucket["attempts"]+=1; bucket["accepted"]+=int(row.status=="accepted")
    for bucket in difficulty.values(): bucket["acceptance_rate"]=round(bucket["accepted"]/bucket["attempts"]*100,1) if bucket["attempts"] else 0
    return {"range":{"start":sd.isoformat(),"end":ed.isoformat()},"attempts":len(rows),"accepted":accepted,"failed":len(evaluated)-accepted,"success_rate":round(accepted/len(evaluated)*100,1) if evaluated else 0,"statuses":{s:sum(r.status==s for r in rows) for s in sorted({r.status for r in rows})},"languages":{s:sum(r.language==s for r in rows) for s in sorted({r.language for r in rows})},"difficulty_performance":sorted(difficulty.values(),key=lambda item:item["difficulty"]),"definitions":definition_payload()}

@router.get("/analytics/projects")
def projects(start_date: date|None = Query(None), end_date: date|None = Query(None), user: User = Depends(full_admin), db: Session = Depends(get_db)):
    """Return real project submission/review counts for the selected UTC period."""
    start,end,sd,ed=bounds(start_date,end_date)
    submissions=db.scalars(select(ProjectSubmission).where(ProjectSubmission.created_at>=start,ProjectSubmission.created_at<end)).all()
    status_counts={status:sum(row.status==status for row in submissions) for status in {row.status for row in submissions}}
    published_projects=db.scalar(select(func.count(ProjectTemplate.id)).where(ProjectTemplate.published.is_(True))) or 0
    started_projects=db.scalar(select(func.count(StudentProject.id)).where(StudentProject.created_at>=start,StudentProject.created_at<end)) or 0
    return {"range":{"start":sd.isoformat(),"end":ed.isoformat()},"submitted":len(submissions),"pending_reviews":sum(status_counts.get(status,0) for status in ("submitted","in_review")),"approved":status_counts.get("approved",0),"revision_requests":status_counts.get("changes_requested",0),"rejected":status_counts.get("rejected",0),"published_projects":published_projects,"started_projects":started_projects,"statuses":status_counts,"definitions":{"submitted":"Project submissions created during the selected UTC period.","pending_reviews":"Submissions currently in submitted or in_review state.","approved":"Submissions marked approved during the selected UTC period.","revision_requests":"Submissions currently marked changes_requested."}}

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
