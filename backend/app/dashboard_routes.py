from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from .auth import current_user
from .db import get_db
from .models import (
    Course,
    CourseModule,
    Enrollment,
    IssuedCertificate,
    Lesson,
    LessonProgress,
    LessonQuiz,
    LearningStreak,
    ProjectSubmission,
    QuizAttempt,
    StudentProject,
    User,
    UserProfile,
)
from .schemas import (
    DashboardActivityOut,
    DashboardCourseOut,
    DashboardOverviewOut,
    DashboardAnalyticsOut,
    DashboardStatisticsOut,
    DashboardStudentOut,
    WeeklyActivityDayOut,
    WeeklyActivityOut,
)

router = APIRouter(prefix="/api/v1/dashboard", tags=["student-dashboard"])


def _published_courses(db: Session, user_id: UUID):
    return db.scalars(
        select(Course)
        .join(Enrollment, Enrollment.course_id == Course.id)
        .options(selectinload(Course.language), selectinload(Course.category))
        .where(Enrollment.user_id == user_id, Course.published.is_(True))
        .order_by(Enrollment.created_at.desc())
    ).all()


def _course_rows(db: Session, user_id: UUID):
    courses = _published_courses(db, user_id)
    if not courses:
        return []
    course_ids = [course.id for course in courses]
    lessons = db.execute(
        select(Lesson, CourseModule.course_id)
        .join(CourseModule, Lesson.module_id == CourseModule.id)
        .where(CourseModule.course_id.in_(course_ids), Lesson.published.is_(True))
        .order_by(CourseModule.order_index, Lesson.order_index)
    ).all()
    lesson_ids = [lesson.id for lesson, _ in lessons]
    progress_rows = (
        db.scalars(
            select(LessonProgress).where(
                LessonProgress.user_id == user_id,
                LessonProgress.lesson_id.in_(lesson_ids),
            )
        ).all()
        if lesson_ids
        else []
    )
    progress = {row.lesson_id: row for row in progress_rows}
    by_course: dict[UUID, list[Lesson]] = {course_id: [] for course_id in course_ids}
    for lesson, course_id in lessons:
        by_course[course_id].append(lesson)

    rows = []
    for course in courses:
        course_lessons = by_course[course.id]
        completed = sum(1 for lesson in course_lessons if progress.get(lesson.id) and progress[lesson.id].completed)
        visited = [
            (lesson, progress[lesson.id])
            for lesson in course_lessons
            if lesson.id in progress and progress[lesson.id].last_visited_at
        ]
        last_lesson, last_progress = max(visited, key=lambda item: item[1].last_visited_at, default=(None, None))
        next_lesson = next(
            (lesson for lesson in course_lessons if not (progress.get(lesson.id) and progress[lesson.id].completed)),
            None,
        )
        rows.append(
            {
                "course": course,
                "completed_lessons": completed,
                "total_lessons": len(course_lessons),
                "progress_percentage": round(completed / len(course_lessons) * 100, 1) if course_lessons else 0,
                "last_visited_lesson": {
                    "id": last_lesson.id,
                    "title": last_lesson.title,
                    "slug": last_lesson.slug,
                    "visited_at": last_progress.last_visited_at,
                }
                if last_lesson
                else None,
                "next_incomplete_lesson": {
                    "id": next_lesson.id,
                    "title": next_lesson.title,
                    "slug": next_lesson.slug,
                }
                if next_lesson
                else None,
                "last_activity_at": last_progress.last_visited_at if last_progress else None,
            }
        )
    # SQLite test databases may return naive datetimes while PostgreSQL returns
    # timezone-aware values; using a naive sentinel avoids mixed-type sorting.
    return sorted(rows, key=lambda row: row["last_activity_at"] or datetime.min, reverse=True)


def _course_out(row: dict) -> dict:
    course = row["course"]
    return {
        "course_id": course.id,
        "course_slug": course.slug,
        "course_title": course.title,
        "course_thumbnail": course.thumbnail,
        "completed_lessons": row["completed_lessons"],
        "total_lessons": row["total_lessons"],
        "progress_percentage": row["progress_percentage"],
        "last_visited_lesson": row["last_visited_lesson"],
        "next_incomplete_lesson": row["next_incomplete_lesson"],
        "last_activity_at": row["last_activity_at"],
    }


def _statistics(db: Session, user_id: UUID, rows: list[dict]) -> dict:
    attempts = db.scalars(select(QuizAttempt).where(QuizAttempt.user_id == user_id)).all()
    graded = [attempt for attempt in attempts if attempt.score is not None and attempt.total and attempt.total > 0]
    certificate_count = db.scalar(
        select(func.count(IssuedCertificate.id)).where(
            IssuedCertificate.user_id == user_id,
            IssuedCertificate.revoked_at.is_(None),
        )
    ) or 0
    streak = db.scalar(select(LearningStreak.current_streak).where(LearningStreak.user_id == user_id)) or 0
    return {
        "enrolled_courses": len(rows),
        "courses_in_progress": sum(0 < row["progress_percentage"] < 100 for row in rows),
        "completed_courses": sum(row["total_lessons"] > 0 and row["completed_lessons"] == row["total_lessons"] for row in rows),
        "completed_lessons": sum(row["completed_lessons"] for row in rows),
        "learning_seconds": None,
        "certificates_earned": int(certificate_count),
        "quiz_average_score": round(sum(attempt.score / attempt.total * 100 for attempt in graded) / len(graded), 1)
        if graded
        else None,
        "quiz_attempts": len(attempts),
        "current_learning_streak": int(streak),
    }


@router.get("/overview", response_model=DashboardOverviewOut)
def dashboard_overview(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = _course_rows(db, user.id)
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    return {
        "student": {"id": user.id, "display_name": user.display_name, "avatar_url": profile.avatar_url if profile else None},
        "statistics": _statistics(db, user.id, rows),
        "courses": [_course_out(row) for row in rows],
    }


@router.get("/courses", response_model=list[DashboardCourseOut])
def dashboard_courses(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [_course_out(row) for row in _course_rows(db, user.id)]


@router.get("/recent-activity", response_model=list[DashboardActivityOut])
def recent_activity(
    limit: int = Query(default=20, ge=1, le=50),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    events: list[dict] = []
    lesson_rows = db.execute(
        select(LessonProgress, Lesson, Course)
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .join(CourseModule, CourseModule.id == Lesson.module_id)
        .join(Course, Course.id == CourseModule.course_id)
        .where(LessonProgress.user_id == user.id, LessonProgress.completed.is_(True), Lesson.published.is_(True), Course.published.is_(True))
        .order_by(LessonProgress.last_visited_at.desc())
        .limit(limit)
    ).all()
    events.extend({"event_type": "lesson_completed", "title": "Lesson completed", "course_title": course.title, "course_slug": course.slug, "lesson_title": lesson.title, "timestamp": progress.last_visited_at} for progress, lesson, course in lesson_rows)
    quiz_rows = db.execute(
        select(QuizAttempt, Lesson, Course)
        .join(LessonQuiz, LessonQuiz.id == QuizAttempt.quiz_id)
        .join(Lesson, Lesson.id == LessonQuiz.lesson_id)
        .join(CourseModule, CourseModule.id == Lesson.module_id)
        .join(Course, Course.id == CourseModule.course_id)
        .where(QuizAttempt.user_id == user.id, Course.published.is_(True))
        .order_by(QuizAttempt.created_at.desc())
        .limit(limit)
    ).all()
    events.extend({"event_type": "quiz_submitted", "title": "Quiz submitted", "course_title": course.title, "course_slug": course.slug, "lesson_title": lesson.title, "timestamp": attempt.created_at} for attempt, lesson, course in quiz_rows)
    return sorted(events, key=lambda event: event["timestamp"] or datetime.min, reverse=True)[:limit]


@router.get("/weekly-activity", response_model=WeeklyActivityOut)
def weekly_activity(user: User = Depends(current_user), db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=6)
    days = {start + timedelta(days=index): {"date": start + timedelta(days=index), "completed_lessons": 0, "recorded_learning_minutes": None, "quiz_attempts": 0} for index in range(7)}
    progress_rows = db.scalars(select(LessonProgress).where(LessonProgress.user_id == user.id, LessonProgress.completed.is_(True))).all()
    for row in progress_rows:
        day = row.last_visited_at.date() if row.last_visited_at else None
        if day in days:
            days[day]["completed_lessons"] += 1
    attempt_rows = db.scalars(select(QuizAttempt).where(QuizAttempt.user_id == user.id, QuizAttempt.created_at >= datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc))).all()
    for row in attempt_rows:
        day = row.created_at.date() if row.created_at else None
        if day in days:
            days[day]["quiz_attempts"] += 1
    return {"days": list(days.values()), "learning_time_available": False}


@router.get("/analytics", response_model=DashboardAnalyticsOut)
def dashboard_analytics(
    days: int = Query(default=30, ge=7, le=90),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    """Return verified, student-scoped learning activity for dashboard charts.

    Only completed lessons and submitted quizzes are counted. There is no
    authoritative duration record in the current schema, so time remains null.
    """
    today = datetime.now(timezone.utc).date()
    range_end = end_date or today
    range_start = start_date or (range_end - timedelta(days=days - 1))
    if range_start > range_end:
        range_start, range_end = range_end, range_start
    if (range_end - range_start).days > 90:
        range_start = range_end - timedelta(days=89)
    start_dt = datetime.combine(range_start, datetime.min.time(), tzinfo=timezone.utc)
    end_dt = datetime.combine(range_end + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)
    points = {
        day: {"date": day.isoformat(), "completed_lessons": 0, "quiz_attempts": 0, "learning_minutes": None}
        for day in (range_start + timedelta(days=index) for index in range((range_end - range_start).days + 1))
    }
    progress_rows = db.scalars(
        select(LessonProgress).where(
            LessonProgress.user_id == user.id,
            LessonProgress.completed.is_(True),
            LessonProgress.last_visited_at >= start_dt,
            LessonProgress.last_visited_at < end_dt,
        )
    ).all()
    for row in progress_rows:
        if row.last_visited_at:
            day = row.last_visited_at.date()
            if day in points:
                points[day]["completed_lessons"] += 1
    attempts = db.scalars(
        select(QuizAttempt).where(
            QuizAttempt.user_id == user.id,
            QuizAttempt.created_at >= start_dt,
            QuizAttempt.created_at < end_dt,
        )
    ).all()
    for attempt in attempts:
        if attempt.created_at:
            day = attempt.created_at.date()
            if day in points:
                points[day]["quiz_attempts"] += 1
    graded = [attempt for attempt in attempts if attempt.score is not None and attempt.total and attempt.total > 0]
    rows = _course_rows(db, user.id)
    streak = db.scalar(select(LearningStreak.current_streak).where(LearningStreak.user_id == user.id)) or 0
    return {
        "range_start": range_start.isoformat(),
        "range_end": range_end.isoformat(),
        "activity": list(points.values()),
        "completed_lessons": sum(item["completed_lessons"] for item in points.values()),
        "quiz_attempts": len(attempts),
        "quiz_average_score": round(sum(attempt.score / attempt.total * 100 for attempt in graded) / len(graded), 1) if graded else None,
        "current_learning_streak": int(streak),
        "learning_seconds": None,
        "learning_time_available": False,
        "course_progress": [
            {
                "course_slug": row["course"].slug,
                "course_title": row["course"].title,
                "progress_percentage": row["progress_percentage"],
                "completed_lessons": row["completed_lessons"],
                "total_lessons": row["total_lessons"],
            }
            for row in rows
        ],
    }
