"""Versioned, reviewed legal documents. No legal text is generated here."""
import json
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .admin_routes import full_admin
from .auth import require_csrf
from .db import get_db
from .models import AdminAuditLog, LegalDocument, LegalDocumentVersion, PlatformSetting, User

router = APIRouter(tags=["legal"])
LEGAL_TYPES = {"privacy", "terms"}
class LegalDraftIn(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    content: str = Field(min_length=1, max_length=200000)
    effective_date: datetime | None = None
    version: str = Field(min_length=1, max_length=40)
class RejectIn(BaseModel):
    reason: str = Field(min_length=3, max_length=2000)
def ensure_type(document_type: str):
    if document_type not in LEGAL_TYPES: raise HTTPException(404, "Legal document not found")
def legacy(db, document_type):
    row = db.scalar(select(PlatformSetting).where(PlatformSetting.key == f"page:{document_type}"))
    if not row: return None
    try: return json.loads(row.value_json or "{}")
    except (TypeError, ValueError, json.JSONDecodeError): return None
def doc_for(db, document_type): return db.scalar(select(LegalDocument).where(LegalDocument.document_type == document_type))
def versions(db, document_id): return db.scalars(select(LegalDocumentVersion).where(LegalDocumentVersion.document_id == document_id).order_by(LegalDocumentVersion.created_at.desc())).all()
def out(version, document_type):
    return {"id": version.id, "document_type": document_type, "version": version.version, "title": version.title, "content": version.content, "effective_date": version.effective_date, "review_status": version.review_status, "publication_status": version.publication_status, "rejection_reason": version.rejection_reason, "submitted_by": version.submitted_by, "reviewed_by": version.reviewed_by, "reviewed_at": version.reviewed_at, "published_by": version.published_by, "published_at": version.published_at, "created_at": version.created_at, "updated_at": version.updated_at}
def legacy_out(db, document_type):
    page = legacy(db, document_type)
    if not page: return None
    return {"id": None, "document_type": document_type, "version": "legacy", "title": page.get("title", document_type.title()), "content": page.get("body", ""), "effective_date": None, "review_status": "approved" if page.get("status") == "published" else "draft", "publication_status": "published" if page.get("status") == "published" else "unpublished", "rejection_reason": "", "published_at": page.get("published_at")}
@router.get("/api/v1/site/legal/{document_type}")
def public_legal(document_type: str, db: Session = Depends(get_db)):
    ensure_type(document_type); document = doc_for(db, document_type)
    if document:
        version = db.scalar(select(LegalDocumentVersion).where(LegalDocumentVersion.document_id == document.id, LegalDocumentVersion.publication_status == "published").order_by(LegalDocumentVersion.published_at.desc()))
        if version: return out(version, document_type)
    old = legacy_out(db, document_type)
    if old and old["publication_status"] == "published": return old
    raise HTTPException(404, "Published legal document not found")
@router.get("/api/v1/site/legal/{document_type}/availability")
def public_legal_availability(document_type: str, db: Session = Depends(get_db)):
    ensure_type(document_type); document = doc_for(db, document_type)
    if not document:
        old = legacy_out(db, document_type)
        return {"document_type": document_type, "state": "published" if old and old["publication_status"] == "published" else "no_document"}
    rows = versions(db, document.id)
    if any(row.publication_status == "published" for row in rows): state = "published"
    elif any(row.review_status == "approved" for row in rows): state = "approved_unpublished"
    elif any(row.review_status == "in_review" for row in rows): state = "pending_review"
    elif rows: state = "draft_only"
    else: state = "no_document"
    return {"document_type": document_type, "state": state}
@router.get("/api/v1/admin/legal")
def list_legal(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    result = []
    for document_type in sorted(LEGAL_TYPES):
        document = doc_for(db, document_type)
        result.append({"document_type": document_type, "versions": [out(row, document_type) for row in versions(db, document.id)] if document else [], "legacy": legacy_out(db, document_type) if not document else None})
    return result
@router.get("/api/v1/admin/legal/{document_type}")
def get_legal(document_type: str, user: User = Depends(full_admin), db: Session = Depends(get_db)):
    ensure_type(document_type); document = doc_for(db, document_type)
    return {"document_type": document_type, "versions": [out(row, document_type) for row in versions(db, document.id)] if document else [], "legacy": legacy_out(db, document_type) if not document else None}
@router.put("/api/v1/admin/legal/{document_type}")
def save_legal_draft(document_type: str, payload: LegalDraftIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    ensure_type(document_type); document = doc_for(db, document_type)
    if not document: document = LegalDocument(document_type=document_type); db.add(document); db.flush()
    draft = db.scalar(select(LegalDocumentVersion).where(LegalDocumentVersion.document_id == document.id, LegalDocumentVersion.review_status.in_(["draft", "rejected"]), LegalDocumentVersion.publication_status != "published").order_by(LegalDocumentVersion.created_at.desc()))
    if draft: draft.title, draft.content, draft.effective_date, draft.version, draft.review_status, draft.rejection_reason = payload.title, payload.content, payload.effective_date, payload.version, "draft", ""
    else: draft = LegalDocumentVersion(document_id=document.id, **payload.model_dump()); db.add(draft)
    db.add(AdminAuditLog(actor_id=user.id, action="legal_draft_saved", entity_type="legal_document", entity_id=document.id)); db.commit(); db.refresh(draft)
    return out(draft, document_type)
def current_draft(document_type, db):
    document = doc_for(db, document_type)
    if not document: raise HTTPException(404, "No legal draft exists")
    draft = db.scalar(select(LegalDocumentVersion).where(LegalDocumentVersion.document_id == document.id, LegalDocumentVersion.publication_status != "published", LegalDocumentVersion.review_status.in_(["draft", "rejected", "in_review", "approved"])).order_by(LegalDocumentVersion.created_at.desc()))
    if not draft: raise HTTPException(404, "No legal draft exists")
    return document, draft
@router.post("/api/v1/admin/legal/{document_type}/submit-review")
def submit_review(document_type: str, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    ensure_type(document_type); document, draft = current_draft(document_type, db)
    if draft.review_status not in {"draft", "rejected"}: raise HTTPException(409, "Only a draft can be submitted for review")
    draft.review_status = "in_review"; draft.submitted_by = user.id; draft.rejection_reason = ""; db.add(AdminAuditLog(actor_id=user.id, action="legal_submitted_for_review", entity_type="legal_document", entity_id=document.id)); db.commit(); return out(draft, document_type)
@router.post("/api/v1/admin/legal/{document_type}/approve")
def approve_legal(document_type: str, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    ensure_type(document_type); document, draft = current_draft(document_type, db)
    if draft.review_status != "in_review": raise HTTPException(409, "Only content in review can be approved")
    draft.review_status, draft.reviewed_by, draft.reviewed_at = "approved", user.id, datetime.now(timezone.utc); db.add(AdminAuditLog(actor_id=user.id, action="legal_approved", entity_type="legal_document", entity_id=document.id)); db.commit(); return out(draft, document_type)
@router.post("/api/v1/admin/legal/{document_type}/reject")
def reject_legal(document_type: str, payload: RejectIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    ensure_type(document_type); document, draft = current_draft(document_type, db)
    if draft.review_status != "in_review": raise HTTPException(409, "Only content in review can be rejected")
    draft.review_status, draft.rejection_reason, draft.reviewed_by, draft.reviewed_at = "rejected", payload.reason, user.id, datetime.now(timezone.utc); db.add(AdminAuditLog(actor_id=user.id, action="legal_rejected", entity_type="legal_document", entity_id=document.id)); db.commit(); return out(draft, document_type)
@router.post("/api/v1/admin/legal/{document_type}/publish")
def publish_legal(document_type: str, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    ensure_type(document_type); document, draft = current_draft(document_type, db)
    if draft.review_status != "approved": raise HTTPException(409, "Only an approved legal version can be published")
    for old in db.scalars(select(LegalDocumentVersion).where(LegalDocumentVersion.document_id == document.id, LegalDocumentVersion.publication_status == "published")).all(): old.publication_status = "unpublished"
    draft.publication_status, draft.published_by, draft.published_at = "published", user.id, datetime.now(timezone.utc); document.current_version_id = draft.id; db.add(AdminAuditLog(actor_id=user.id, action="legal_published", entity_type="legal_document", entity_id=document.id)); db.commit(); return out(draft, document_type)
@router.post("/api/v1/admin/legal/{document_type}/unpublish")
def unpublish_legal(document_type: str, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    ensure_type(document_type); document, draft = current_draft(document_type, db)
    published = db.scalar(select(LegalDocumentVersion).where(LegalDocumentVersion.document_id == document.id, LegalDocumentVersion.publication_status == "published"))
    if not published: raise HTTPException(409, "No published legal version exists")
    published.publication_status, published.published_at, published.published_by = "unpublished", None, None; document.current_version_id = None; db.add(AdminAuditLog(actor_id=user.id, action="legal_unpublished", entity_type="legal_document", entity_id=document.id)); db.commit(); return out(published, document_type)
@router.post("/api/v1/admin/legal/{document_type}/restore/{version_id}")
def restore_legal(document_type: str, version_id: UUID, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    ensure_type(document_type); document = doc_for(db, document_type); source = db.scalar(select(LegalDocumentVersion).where(LegalDocumentVersion.id == version_id, LegalDocumentVersion.document_id == document.id if document else False))
    if not source: raise HTTPException(404, "Legal version not found")
    draft = LegalDocumentVersion(document_id=document.id, version=f"{source.version}-draft", title=source.title, content=source.content, effective_date=source.effective_date, review_status="draft", publication_status="unpublished"); db.add(draft); db.add(AdminAuditLog(actor_id=user.id, action="legal_version_restored", entity_type="legal_document", entity_id=document.id)); db.commit(); db.refresh(draft); return out(draft, document_type)
