"""Phase 35 student success, support, privacy, and evidence APIs."""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .auth import check_rate_limit, require_csrf, verified_user, current_user
from .db import get_db
from .models import (
    Course, CourseInstructor, Enrollment, LessonProgress, StudentFeedback,
    StudentLearningSignal, StudentLearningSignalEvidence, StudentSupportEscalation,
    StudentSupportKnowledgeArticle, StudentSupportKnowledgeVersion,
    StudentSupportPlan, StudentSupportPlanItem, StudentSupportTicket,
    StudentSupportTicketEvent, StudentSupportTicketMessage,
    StudentSuccessAuditLog, StudentSuccessPrivacyPreference, User,
)

router = APIRouter(prefix="/api/v1/student-success", tags=["student-success"])
STAFF = {"support_staff", "admin", "platform_admin", "super_admin", "moderator"}
PLATFORM = {"admin", "platform_admin", "super_admin"}


def staff_user(user: User = Depends(current_user)) -> User:
    if user.role not in STAFF:
        raise HTTPException(403, "Support staff access required")
    return user


def platform_user(user: User = Depends(current_user)) -> User:
    if user.role not in PLATFORM:
        raise HTTPException(403, "Platform permission required")
    return user


def row_data(row):
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


def audit(db, actor, action, entity_type, entity_id=None):
    db.add(StudentSuccessAuditLog(actor_id=actor.id, action=action, entity_type=entity_type, entity_id=entity_id))


class TicketIn(BaseModel):
    category: str = Field(min_length=2, max_length=50)
    subject: str = Field(min_length=3, max_length=180)
    description: str = Field(min_length=10, max_length=20000)
    priority: str = Field(default="normal", pattern="^(low|normal|high)$")
    course_id: UUID | None = None


class MessageIn(BaseModel):
    body: str = Field(min_length=2, max_length=10000)


class TransitionIn(BaseModel):
    status: str = Field(pattern="^(triaged|in_progress|waiting_for_student|resolved|reopened|closed)$")
    note: str = Field(default="", max_length=5000)


class PlanIn(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    barriers: str = Field(default="", max_length=5000)
    items: list[str] = Field(default_factory=list, max_length=20)


class PlanStatusIn(BaseModel):
    status: str = Field(pattern="^(active|paused|dismissed|completed)$")


class EscalationIn(BaseModel):
    topic: str = Field(min_length=3, max_length=180)
    description: str = Field(min_length=10, max_length=10000)
    consented: bool


class PrivacyIn(BaseModel):
    show_signals: bool = True
    allow_personalization: bool = True
    allow_mentor_sharing: bool = False
    retention_days: int = Field(default=365, ge=30, le=3650)


def can_view_ticket(ticket, user):
    return ticket.user_id == user.id or user.role in STAFF


@router.get("/dashboard")
def dashboard(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    enrolled = db.scalar(select(func.count(Enrollment.id)).where(Enrollment.user_id == user.id)) or 0
    completed = db.scalar(select(func.count(LessonProgress.id)).where(LessonProgress.user_id == user.id, LessonProgress.completed.is_(True))) or 0
    open_tickets = db.scalar(select(func.count(StudentSupportTicket.id)).where(StudentSupportTicket.user_id == user.id, StudentSupportTicket.status.not_in({"resolved", "closed"}))) or 0
    plans = db.scalar(select(func.count(StudentSupportPlan.id)).where(StudentSupportPlan.user_id == user.id, StudentSupportPlan.status == "active")) or 0
    return {"enrolled_courses": enrolled, "completed_lessons": completed, "open_support_tickets": open_tickets, "active_support_plans": plans, "data_source": "persisted_learning_and_support_records"}


@router.get("/tickets")
def tickets(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    query = select(StudentSupportTicket).order_by(StudentSupportTicket.updated_at.desc()).limit(100)
    if user.role not in STAFF:
        query = query.where(StudentSupportTicket.user_id == user.id)
    return [row_data(row) for row in db.scalars(query).all()]


@router.post("/tickets", status_code=201)
def create_ticket(payload: TicketIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    check_rate_limit(f"student-support-ticket:{user.id}", limit=10, window_seconds=3600)
    if payload.course_id and not db.scalar(select(Course.id).where(Course.id == payload.course_id, Course.published.is_(True))):
        raise HTTPException(404, "Published course not found")
    ticket = StudentSupportTicket(user_id=user.id, **payload.model_dump())
    db.add(ticket); db.flush()
    db.add(StudentSupportTicketEvent(ticket_id=ticket.id, actor_id=user.id, to_status="submitted", note="Ticket created"))
    audit(db, user, "ticket_created", "student_support_ticket", ticket.id)
    db.commit(); db.refresh(ticket)
    return row_data(ticket)


@router.get("/tickets/{ticket_id}")
def ticket_detail(ticket_id: UUID, user: User = Depends(verified_user), db: Session = Depends(get_db)):
    ticket = db.get(StudentSupportTicket, ticket_id)
    if not ticket or not can_view_ticket(ticket, user):
        raise HTTPException(404, "Support ticket not found")
    messages = select(StudentSupportTicketMessage).where(StudentSupportTicketMessage.ticket_id == ticket.id)
    if user.role not in STAFF:
        messages = messages.where(StudentSupportTicketMessage.visibility == "student")
    return {"ticket": row_data(ticket), "messages": [row_data(row) for row in db.scalars(messages.order_by(StudentSupportTicketMessage.created_at)).all()]}


@router.post("/tickets/{ticket_id}/messages", status_code=201)
def add_ticket_message(ticket_id: UUID, payload: MessageIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    check_rate_limit(f"student-support-message:{user.id}", limit=30, window_seconds=3600)
    ticket = db.get(StudentSupportTicket, ticket_id)
    if not ticket or not can_view_ticket(ticket, user):
        raise HTTPException(404, "Support ticket not found")
    visibility = "staff" if user.role in STAFF and ticket.user_id != user.id else "student"
    row = StudentSupportTicketMessage(ticket_id=ticket.id, author_id=user.id, body=payload.body, visibility=visibility)
    db.add(row); audit(db, user, "ticket_message_added", "student_support_ticket", ticket.id); db.commit(); db.refresh(row)
    return row_data(row)


@router.post("/tickets/{ticket_id}/transition")
def transition_ticket(ticket_id: UUID, payload: TransitionIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    ticket = db.get(StudentSupportTicket, ticket_id)
    if not ticket or not can_view_ticket(ticket, user):
        raise HTTPException(404, "Support ticket not found")
    if user.role not in STAFF and payload.status not in {"reopened", "closed"}:
        raise HTTPException(403, "Only support staff can advance a ticket")
    allowed = {"submitted": {"triaged"}, "triaged": {"in_progress"}, "in_progress": {"waiting_for_student", "resolved"}, "waiting_for_student": {"in_progress"}, "resolved": {"reopened", "closed"}, "reopened": {"in_progress"}, "closed": set()}
    if payload.status not in allowed.get(ticket.status, set()):
        raise HTTPException(409, "Invalid ticket status transition")
    old = ticket.status; ticket.status = payload.status
    if payload.status == "closed": ticket.closed_at = datetime.now(timezone.utc)
    db.add(StudentSupportTicketEvent(ticket_id=ticket.id, actor_id=user.id, from_status=old, to_status=payload.status, note=payload.note))
    audit(db, user, "ticket_transitioned", "student_support_ticket", ticket.id); db.commit(); db.refresh(ticket)
    return row_data(ticket)


@router.get("/learning-signals")
def learning_signals(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    pref = db.scalar(select(StudentSuccessPrivacyPreference).where(StudentSuccessPrivacyPreference.user_id == user.id))
    if pref and not pref.show_signals:
        return {"visible": False, "items": [], "reason": "Student has disabled learning signal visibility."}
    rows = db.scalars(select(StudentLearningSignal).where(StudentLearningSignal.user_id == user.id, StudentLearningSignal.visible_to_student.is_(True)).order_by(StudentLearningSignal.created_at.desc())).all()
    result = []
    for row in rows:
        evidence = db.scalars(select(StudentLearningSignalEvidence).where(StudentLearningSignalEvidence.signal_id == row.id)).all()
        result.append({**row_data(row), "evidence": [row_data(item) for item in evidence]})
    return {"visible": True, "items": result, "note": "Signals describe observable learning activity only; they are not grades or character assessments."}


@router.post("/learning-signals/{signal_id}/dismiss")
def dismiss_signal(signal_id: UUID, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(StudentLearningSignal, signal_id)
    if not row or row.user_id != user.id: raise HTTPException(404, "Learning signal not found")
    row.status = "dismissed"; audit(db, user, "learning_signal_dismissed", "student_learning_signal", row.id); db.commit()
    return row_data(row)


@router.get("/support-plans")
def support_plans(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(StudentSupportPlan).where(StudentSupportPlan.user_id == user.id).order_by(StudentSupportPlan.updated_at.desc())).all()
    return [{**row_data(row), "items": [row_data(item) for item in db.scalars(select(StudentSupportPlanItem).where(StudentSupportPlanItem.plan_id == row.id).order_by(StudentSupportPlanItem.position)).all()]} for row in rows]


@router.post("/support-plans", status_code=201)
def create_support_plan(payload: PlanIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    plan = StudentSupportPlan(user_id=user.id, created_by=user.id, title=payload.title, barriers=payload.barriers, consented=False)
    db.add(plan); db.flush()
    for position, description in enumerate(payload.items): db.add(StudentSupportPlanItem(plan_id=plan.id, item_type="guidance", description=description, position=position))
    audit(db, user, "support_plan_created", "student_support_plan", plan.id); db.commit(); db.refresh(plan)
    return row_data(plan)


@router.patch("/support-plans/{plan_id}")
def update_support_plan(plan_id: UUID, payload: PlanStatusIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    plan = db.get(StudentSupportPlan, plan_id)
    if not plan or plan.user_id != user.id: raise HTTPException(404, "Support plan not found")
    plan.status = payload.status; plan.consented = payload.status == "active"; audit(db, user, "support_plan_updated", "student_support_plan", plan.id); db.commit(); return row_data(plan)


@router.post("/mentorship/escalations", status_code=201)
def request_mentor(payload: EscalationIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    pref = db.scalar(select(StudentSuccessPrivacyPreference).where(StudentSuccessPrivacyPreference.user_id == user.id))
    if not payload.consented or (pref and not pref.allow_mentor_sharing):
        raise HTTPException(403, "Mentor sharing consent is required")
    row = StudentSupportEscalation(student_id=user.id, topic=payload.topic, description=payload.description, consented=True)
    db.add(row); audit(db, user, "mentor_escalation_requested", "student_support_escalation", row.id); db.commit(); db.refresh(row); return row_data(row)


@router.get("/guidance")
def guidance(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    courses = db.scalars(select(Course).where(Course.published.is_(True)).order_by(Course.updated_at.desc()).limit(10)).all()
    return {"items": [{"id": row.id, "title": row.title, "slug": row.slug, "level": row.level, "reason": "Published course available in the catalog."} for row in courses], "personalized": False, "data_source": "published_course_catalog"}


@router.get("/help")
def help_articles(search: str | None = Query(None, max_length=120), db: Session = Depends(get_db)):
    query = select(StudentSupportKnowledgeArticle).where(StudentSupportKnowledgeArticle.status == "published")
    if search: query = query.where(or_(StudentSupportKnowledgeArticle.title.ilike(f"%{search}%"), StudentSupportKnowledgeArticle.category.ilike(f"%{search}%")))
    articles = db.scalars(query.order_by(StudentSupportKnowledgeArticle.title).limit(50)).all()
    result = []
    for article in articles:
        version = db.scalar(select(StudentSupportKnowledgeVersion).where(StudentSupportKnowledgeVersion.article_id == article.id, StudentSupportKnowledgeVersion.status == "published").order_by(StudentSupportKnowledgeVersion.version.desc()))
        result.append({**row_data(article), "body": version.body if version else "", "version": version.version if version else None})
    return result


@router.get("/feedback")
def feedback_history(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    return [row_data(row) for row in db.scalars(select(StudentFeedback).where(StudentFeedback.user_id == user.id).order_by(StudentFeedback.created_at.desc()).limit(100)).all()]


@router.get("/outcomes")
def outcomes(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    lessons = db.scalar(select(func.count(LessonProgress.id)).where(LessonProgress.user_id == user.id, LessonProgress.completed.is_(True))) or 0
    return {"completed_lessons": lessons, "verified_assessments": 0, "skill_evidence": 0, "source": "persisted_lesson_progress_only", "note": "No unverified AI estimates are included."}


@router.get("/privacy")
def privacy(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    row = db.scalar(select(StudentSuccessPrivacyPreference).where(StudentSuccessPrivacyPreference.user_id == user.id))
    if not row: row = StudentSuccessPrivacyPreference(user_id=user.id); db.add(row); db.commit(); db.refresh(row)
    return row_data(row)


@router.put("/privacy")
def update_privacy(payload: PrivacyIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(StudentSuccessPrivacyPreference).where(StudentSuccessPrivacyPreference.user_id == user.id))
    if not row: row = StudentSuccessPrivacyPreference(user_id=user.id); db.add(row)
    for key, value in payload.model_dump().items(): setattr(row, key, value)
    audit(db, user, "privacy_preferences_updated", "student_success_privacy_preferences", row.id); db.commit(); db.refresh(row); return row_data(row)


@router.get("/staff/tickets")
def staff_tickets(user: User = Depends(staff_user), db: Session = Depends(get_db)):
    return [row_data(row) for row in db.scalars(select(StudentSupportTicket).order_by(StudentSupportTicket.updated_at.desc()).limit(200)).all()]


@router.post("/staff/tickets/{ticket_id}/assign")
def assign_ticket(ticket_id: UUID, staff_id: UUID, user: User = Depends(staff_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    ticket = db.get(StudentSupportTicket, ticket_id); target = db.get(User, staff_id)
    if not ticket or not target or target.role not in STAFF: raise HTTPException(404, "Ticket or support staff not found")
    ticket.assigned_to = target.id; audit(db, user, "ticket_assigned", "student_support_ticket", ticket.id); db.commit(); return row_data(ticket)


@router.get("/instructor/tickets")
def instructor_tickets(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role not in STAFF | {"instructor"}: raise HTTPException(403, "Instructor support access required")
    query = select(StudentSupportTicket).join(Course, StudentSupportTicket.course_id == Course.id).outerjoin(CourseInstructor, CourseInstructor.course_id == Course.id).where(or_(Course.created_by == user.id, CourseInstructor.user_id == user.id)).limit(100)
    return [row_data(row) for row in db.scalars(query).all()]


@router.get("/platform/overview")
def platform_overview(user: User = Depends(platform_user), db: Session = Depends(get_db)):
    total = db.scalar(select(func.count(StudentSupportTicket.id))) or 0
    open_count = db.scalar(select(func.count(StudentSupportTicket.id)).where(StudentSupportTicket.status.not_in({"resolved", "closed"}))) or 0
    return {"support_tickets": total, "open_tickets": open_count, "learning_signals": db.scalar(select(func.count(StudentLearningSignal.id))) or 0, "mentor_escalations": db.scalar(select(func.count(StudentSupportEscalation.id))) or 0, "minimum_group_size": 5, "small_groups_suppressed": True}
