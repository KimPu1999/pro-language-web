import io
import json
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .admin_routes import audit, full_admin
from .auth import check_rate_limit, current_user, require_csrf
from .certificate_service import COURSE_ACHIEVEMENT, certificate_payload
from .config import settings
from .db import get_db
from .models import CertificatePolicy, CertificateRevocation, CertificateTemplate, Course, IssuedCertificate, User

router = APIRouter(prefix="/api/v1", tags=["verified certificates"])


def _owned(db: Session, public_id: str, user: User) -> IssuedCertificate:
    row = db.scalar(select(IssuedCertificate).where(IssuedCertificate.public_id == public_id, IssuedCertificate.user_id == user.id))
    if not row:
        raise HTTPException(404, "Certificate not found")
    return row


@router.get("/me/certificates")
def my_certificates(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(IssuedCertificate).where(IssuedCertificate.user_id == user.id).order_by(IssuedCertificate.issued_at.desc())).all()
    return {"items": [certificate_payload(row, include_recipient=True) for row in rows]}


@router.get("/me/certificates/{public_id}")
def my_certificate(public_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = _owned(db, public_id, user)
    return {**certificate_payload(row, include_recipient=True), "evidence": json.loads(row.evidence_json or "{}")}


@router.get("/me/certificates/{public_id}/download")
def download_certificate(public_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = _owned(db, public_id, user)
    if row.revoked_at:
        raise HTTPException(410, "Revoked certificates cannot be downloaded")
    return _pdf_response(row)


def _pdf_response(row: IssuedCertificate) -> Response:
    try:
        from reportlab.graphics import renderPDF
        from reportlab.graphics.barcode.qr import QrCodeWidget
        from reportlab.graphics.shapes import Drawing
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.pdfgen import canvas
    except ModuleNotFoundError as exc:
        if exc.name == "reportlab":
            raise HTTPException(503, "Certificate PDF generation is not configured on this server") from exc
        raise

    buffer = io.BytesIO()
    page = landscape(A4)
    document = canvas.Canvas(buffer, pagesize=page)
    width, height = page
    accent = colors.HexColor("#6d5dfc")
    document.setFillColor(colors.HexColor("#0b1220")); document.rect(0, 0, width, height, fill=1, stroke=0)
    document.setStrokeColor(accent); document.setLineWidth(2); document.roundRect(28, 28, width - 56, height - 56, 18, fill=0, stroke=1)
    document.setFillColor(colors.white); document.setFont("Helvetica-Bold", 28); document.drawCentredString(width / 2, height - 120, "CERTIFICATE OF COMPLETION")
    document.setFont("Helvetica", 14); document.setFillColor(colors.HexColor("#c5cbd8")); document.drawCentredString(width / 2, height - 155, "Learn-Coding verified learning achievement")
    document.setFillColor(colors.white); document.setFont("Helvetica-Bold", 24); document.drawCentredString(width / 2, height - 235, _pdf_text(row.student_name))
    document.setFont("Helvetica", 14); document.setFillColor(colors.HexColor("#c5cbd8")); document.drawCentredString(width / 2, height - 270, "has successfully completed")
    document.setFillColor(colors.white); document.setFont("Helvetica-Bold", 20); document.drawCentredString(width / 2, height - 310, _pdf_text(row.title))
    document.setFont("Helvetica", 11); document.setFillColor(colors.HexColor("#c5cbd8")); document.drawCentredString(width / 2, 105, f"Completed: {(row.completion_at or row.issued_at).date().isoformat()}   •   Certificate ID: {row.public_id}")
    document.drawCentredString(width / 2, 84, f"Verify: {settings.app_base_url}/verify/certificate/{row.public_id}")
    try:
        qr = QrCodeWidget(f"{settings.app_base_url}/verify/certificate/{row.public_id}")
        x1, y1, x2, y2 = qr.getBounds(); size = 86
        drawing = Drawing(size, size, transform=[size / (x2 - x1), 0, 0, size / (y2 - y1), 0, 0]); drawing.add(qr)
        renderPDF.draw(drawing, document, width - 145, 62)
    except Exception:
        pass
    document.showPage(); document.save()
    return Response(buffer.getvalue(), media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="certificate-{row.public_id}.pdf"'})


def _pdf_text(value: str) -> str:
    try:
        value.encode("latin-1")
        return value
    except UnicodeEncodeError:
        return "Learn-Coding learner"


@router.get("/certificates/verify/{public_id}")
def verify_certificate(public_id: str, request: Request, db: Session = Depends(get_db)):
    check_rate_limit(f"certificate-verify:{request.client.host if request.client else 'unknown'}", 30, 60)
    row = db.scalar(select(IssuedCertificate).where(IssuedCertificate.public_id == public_id))
    if not row:
        return {"status": "not_found", "certificate_id": public_id}
    return certificate_payload(row)


class TemplateIn(BaseModel):
    slug: str = Field(min_length=3, max_length=120, pattern=r"^[a-z0-9-]+$")
    title: str = Field(min_length=2, max_length=180)
    issuer: str = Field(min_length=2, max_length=180)
    heading: str | None = Field(default=None, max_length=180)
    logo_url: str | None = Field(default=None, max_length=500)
    accent_color: str = Field(default="#6d5dfc", max_length=20)
    active: bool = True


class PolicyIn(BaseModel):
    template_id: UUID
    achievement_type: str = Field(default=COURSE_ACHIEVEMENT, pattern=r"^course_completion$")
    resource_id: UUID | None = None
    minimum_score: int | None = Field(default=70, ge=0, le=100)
    rules_json: str = "{\"lessons\":\"all_published\",\"quizzes\":\"published_quizzes_passed\"}"
    version: int = Field(default=1, ge=1)
    active: bool = True


@router.get("/admin/certificates")
def admin_certificates(search: str = Query("", max_length=100), status: str = Query("all", pattern="^(all|valid|revoked|expired)$"), page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100), user: User = Depends(full_admin), db: Session = Depends(get_db)):
    query = select(IssuedCertificate).order_by(IssuedCertificate.issued_at.desc())
    if search.strip():
        query = query.where(IssuedCertificate.title.ilike(f"%{search.strip()}%"))
    rows = db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
    items = [certificate_payload(row, include_recipient=True) for row in rows]
    if status != "all": items = [row for row in items if row["status"] == status]
    total = db.scalar(select(func.count(IssuedCertificate.id))) or 0
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.get("/admin/certificates/{public_id}")
def admin_certificate(public_id: str, user: User = Depends(full_admin), db: Session = Depends(get_db)):
    row = db.scalar(select(IssuedCertificate).where(IssuedCertificate.public_id == public_id))
    if not row: raise HTTPException(404, "Certificate not found")
    return {**certificate_payload(row, include_recipient=True), "student_name": row.student_name, "evidence": json.loads(row.evidence_json or "{}"), "revoked_at": row.revoked_at}


@router.get("/admin/certificate-templates")
def admin_templates(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return {"items": [{"id": str(row.id), "slug": row.slug, "title": row.title, "issuer": row.issuer, "heading": row.heading, "logo_url": row.logo_url, "accent_color": row.accent_color, "active": row.active} for row in db.scalars(select(CertificateTemplate).order_by(CertificateTemplate.created_at.desc())).all()]}


@router.post("/admin/certificate-templates", status_code=201)
def create_template(payload: TemplateIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if db.scalar(select(CertificateTemplate.id).where(CertificateTemplate.slug == payload.slug)): raise HTTPException(409, "Template slug already exists")
    row = CertificateTemplate(**payload.model_dump()); db.add(row); audit(db, user, "certificate_template_created", "certificate_template", row.id); db.commit(); return {"id": str(row.id), "slug": row.slug}


@router.patch("/admin/certificate-templates/{template_id}")
def update_template(template_id: UUID, payload: TemplateIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(CertificateTemplate, template_id)
    if not row: raise HTTPException(404, "Template not found")
    for key, value in payload.model_dump().items(): setattr(row, key, value)
    audit(db, user, "certificate_template_updated", "certificate_template", row.id); db.commit(); return {"id": str(row.id), "slug": row.slug}


@router.get("/admin/certificate-policies")
def admin_policies(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return {"items": [{"id": str(row.id), "template_id": str(row.template_id), "achievement_type": row.achievement_type, "resource_id": str(row.resource_id) if row.resource_id else None, "minimum_score": row.minimum_score, "version": row.version, "active": row.active, "rules_json": row.rules_json} for row in db.scalars(select(CertificatePolicy).order_by(CertificatePolicy.created_at.desc())).all()]}


@router.post("/admin/certificate-policies", status_code=201)
def create_policy(payload: PolicyIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if not db.get(CertificateTemplate, payload.template_id): raise HTTPException(404, "Template not found")
    row = CertificatePolicy(**payload.model_dump()); db.add(row); audit(db, user, "certificate_policy_created", "certificate_policy", row.id); db.commit(); return {"id": str(row.id), "version": row.version}


@router.post("/admin/certificates/{public_id}/revoke")
def revoke_certificate(public_id: str, reason: str = Query(..., min_length=3, max_length=500), user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(IssuedCertificate).where(IssuedCertificate.public_id == public_id))
    if not row: raise HTTPException(404, "Certificate not found")
    if not row.revoked_at:
        row.revoked_at = datetime.now(timezone.utc)
        db.add(CertificateRevocation(certificate_id=row.id, revoked_by=user.id, reason=reason.strip()))
        audit(db, user, "certificate_revoked", "issued_certificate", row.id)
        db.commit()
    return certificate_payload(row, include_recipient=True)
