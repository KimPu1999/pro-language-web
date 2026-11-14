import hashlib
import json
from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .auth import current_user, require_csrf, verified_user, now
from .config import settings
from .db import get_db
from .models import (
    AutomationAgentDefinition, AutomationAgentToolPermission, AutomationApprovalDecision,
    AutomationApprovalRequest, AutomationAuditLog, AutomationIdempotencyKey,
    AutomationRecommendation, AutomationSecurityEvent, AutomationStepRun,
    AutomationTemplate, AutomationTrigger, AutomationUsageRecord, AutomationWorkflow,
    AutomationWorkflowEdge, AutomationWorkflowNode, AutomationWorkflowRun,
    AutomationWorkflowVersion,
    Organization, OrganizationMembership, User,
)
from .organization_routes import check_role, org_context

router = APIRouter(prefix="/api/v1", tags=["automation"])
MANAGERS = {"owner", "admin"}
APPROVERS = {"owner", "admin"}
NODE_TYPES = {"trigger", "condition", "action", "approval", "end"}
SAFE_ACTIONS = {"notify", "create_recommendation", "propose_assignment", "request_approval", "record_event"}


class WorkflowIn(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=180)
    description: str = Field(default="", max_length=5000)


class GraphNode(BaseModel):
    node_key: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
    node_type: str
    config: dict = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source_key: str
    target_key: str


class GraphIn(BaseModel):
    nodes: list[GraphNode] = Field(min_length=1, max_length=50)
    edges: list[GraphEdge] = Field(default_factory=list, max_length=200)


class RunIn(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=180)


class DecisionIn(BaseModel):
    decision: str = Field(pattern=r"^(approved|rejected|cancelled)$")
    comment: str = Field(default="", max_length=2000)


class TriggerIn(BaseModel):
    trigger_type: str = Field(pattern=r"^(event|schedule|manual)$")
    config: dict = Field(default_factory=dict)
    enabled: bool = False


class EventIn(BaseModel):
    event_type: str = Field(pattern=r"^(assessment_completed|course_completed|training_assigned|membership_created|deadline_approaching|manual)$")
    event_id: str = Field(min_length=1, max_length=180)


def graph_errors(graph: GraphIn) -> list[str]:
    errors: list[str] = []
    keys = [n.node_key for n in graph.nodes]
    if len(set(keys)) != len(keys):
        errors.append("Node keys must be unique")
    nodes = {n.node_key: n for n in graph.nodes}
    if not any(n.node_type == "trigger" for n in graph.nodes):
        errors.append("A trigger node is required")
    if not any(n.node_type == "end" for n in graph.nodes):
        errors.append("An end node is required")
    for node in graph.nodes:
        if node.node_type not in NODE_TYPES:
            errors.append(f"Unsupported node type: {node.node_type}")
        if node.node_type == "action" and node.config.get("action") not in SAFE_ACTIONS:
            errors.append(f"Unsupported action on node {node.node_key}")
        if any(k in node.config for k in ("shell", "sql", "url", "command")):
            errors.append(f"Unsafe tool configuration on node {node.node_key}")
    adjacency: dict[str, list[str]] = {key: [] for key in keys}
    for edge in graph.edges:
        if edge.source_key not in nodes or edge.target_key not in nodes:
            errors.append("Edges must reference existing nodes")
        elif edge.source_key == edge.target_key:
            errors.append("Self-referential edges are not allowed")
        else:
            adjacency[edge.source_key].append(edge.target_key)
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(key: str) -> None:
        if key in visiting:
            errors.append("Workflow graph contains a cycle")
            return
        if key in visited:
            return
        visiting.add(key)
        for child in adjacency.get(key, []):
            visit(child)
        visiting.remove(key)
        visited.add(key)
    for key in keys:
        visit(key)
    return list(dict.fromkeys(errors))


def graph_payload(graph: GraphIn) -> dict:
    return {"nodes": [n.model_dump() for n in graph.nodes], "edges": [e.model_dump() for e in graph.edges]}


def graph_hash(graph: GraphIn) -> str:
    return hashlib.sha256(json.dumps(graph_payload(graph), sort_keys=True).encode()).hexdigest()


def create_version(db: Session, workflow: AutomationWorkflow, graph: GraphIn, user: User, status: str = "draft"):
    errors = graph_errors(graph)
    if errors:
        raise HTTPException(422, detail={"message": "Invalid workflow graph", "errors": errors})
    current = db.scalar(select(func.max(AutomationWorkflowVersion.version_number)).where(AutomationWorkflowVersion.workflow_id == workflow.id)) or 0
    version = AutomationWorkflowVersion(workflow_id=workflow.id, version_number=current + 1, graph_hash=graph_hash(graph), status=status, created_by=user.id)
    db.add(version)
    db.flush()
    for node in graph.nodes:
        db.add(AutomationWorkflowNode(version_id=version.id, node_key=node.node_key, node_type=node.node_type, config_json=json.dumps(node.config, sort_keys=True)))
    for edge in graph.edges:
        db.add(AutomationWorkflowEdge(version_id=version.id, source_key=edge.source_key, target_key=edge.target_key))
    return version


def audit(db: Session, org, user: User, action: str, resource_type: str, resource_id=None, outcome="success"):
    db.add(AutomationAuditLog(organization_id=org.id, actor_id=user.id, action=action, resource_type=resource_type, resource_id=resource_id, outcome=outcome))


def workflow_for(ctx, workflow_id: UUID):
    org, member, user, db = ctx
    workflow = db.scalar(select(AutomationWorkflow).where(AutomationWorkflow.id == workflow_id, AutomationWorkflow.organization_id == org.id))
    if not workflow:
        raise HTTPException(404, "Workflow not found")
    return org, member, user, db, workflow


@router.get("/organizations/{slug}/automation")
def automation_dashboard(ctx=Depends(org_context)):
    org, _, _, db = ctx
    counts = {
        "workflows": db.scalar(select(func.count()).select_from(AutomationWorkflow).where(AutomationWorkflow.organization_id == org.id)) or 0,
        "active_workflows": db.scalar(select(func.count()).select_from(AutomationWorkflow).where(AutomationWorkflow.organization_id == org.id, AutomationWorkflow.enabled.is_(True))) or 0,
        "queued_runs": db.scalar(select(func.count()).select_from(AutomationWorkflowRun).where(AutomationWorkflowRun.organization_id == org.id, AutomationWorkflowRun.status.in_(["queued", "running"]))) or 0,
        "failed_runs": db.scalar(select(func.count()).select_from(AutomationWorkflowRun).where(AutomationWorkflowRun.organization_id == org.id, AutomationWorkflowRun.status == "failed")) or 0,
        "pending_approvals": db.scalar(select(func.count()).select_from(AutomationApprovalRequest).where(AutomationApprovalRequest.organization_id == org.id, AutomationApprovalRequest.status == "pending")) or 0,
    }
    return {"metrics": counts, "execution": {"status": "queued_only", "detail": "No automation worker is configured; runs remain durably queued."}, "ai": {"status": "configured" if settings.ai_enabled and settings.ai_provider != "disabled" else "Not Configured"}, "data_source": "postgresql"}


@router.get("/organizations/{slug}/automation/workflows")
def workflows(ctx=Depends(org_context), page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100)):
    org, _, _, db = ctx
    total = db.scalar(select(func.count()).select_from(AutomationWorkflow).where(AutomationWorkflow.organization_id == org.id)) or 0
    rows = db.scalars(select(AutomationWorkflow).where(AutomationWorkflow.organization_id == org.id).order_by(AutomationWorkflow.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [{"id": r.id, "name": r.name, "slug": r.slug, "status": r.status, "enabled": r.enabled} for r in rows], "page": page, "page_size": page_size, "total": total}


@router.post("/organizations/{slug}/automation/workflows", status_code=201)
def create_workflow(payload: WorkflowIn, ctx=Depends(org_context), _: None = Depends(require_csrf)):
    org, member, user, db = ctx
    check_role(ctx, MANAGERS)
    if db.scalar(select(AutomationWorkflow).where(AutomationWorkflow.organization_id == org.id, AutomationWorkflow.slug == payload.slug)):
        raise HTTPException(409, "Workflow slug is already in use")
    row = AutomationWorkflow(organization_id=org.id, created_by=user.id, **payload.model_dump())
    db.add(row); db.flush(); audit(db, org, user, "workflow_created", "workflow", row.id); db.commit()
    return {"id": row.id, "status": row.status}


@router.post("/organizations/{slug}/automation/workflows/{workflow_id}/validate")
def validate_workflow(payload: GraphIn, workflow_id: UUID, ctx=Depends(org_context)):
    _, _, _, _, _ = workflow_for(ctx, workflow_id)
    errors = graph_errors(payload)
    return {"valid": not errors, "errors": errors}


@router.post("/organizations/{slug}/automation/workflows/{workflow_id}/versions", status_code=201)
def add_version(payload: GraphIn, workflow_id: UUID, ctx=Depends(org_context), _: None = Depends(require_csrf)):
    org, member, user, db, workflow = workflow_for(ctx, workflow_id); check_role(ctx, MANAGERS)
    version = create_version(db, workflow, payload, user); audit(db, org, user, "workflow_version_created", "workflow_version", version.id); db.commit()
    return {"id": version.id, "version": version.version_number, "status": version.status, "graph_hash": version.graph_hash}


@router.get("/organizations/{slug}/automation/workflows/{workflow_id}/versions")
def versions(workflow_id: UUID, ctx=Depends(org_context)):
    _, _, _, db, workflow = workflow_for(ctx, workflow_id)
    rows = db.scalars(select(AutomationWorkflowVersion).where(AutomationWorkflowVersion.workflow_id == workflow.id).order_by(AutomationWorkflowVersion.version_number.desc())).all()
    return [{"id": r.id, "version": r.version_number, "status": r.status, "graph_hash": r.graph_hash, "published_at": r.published_at} for r in rows]


@router.post("/organizations/{slug}/automation/workflows/{workflow_id}/triggers", status_code=201)
def add_trigger(payload: TriggerIn, workflow_id: UUID, ctx=Depends(org_context), _: None = Depends(require_csrf)):
    org, _, user, db, workflow = workflow_for(ctx, workflow_id); check_role(ctx, MANAGERS)
    row = AutomationTrigger(organization_id=org.id, workflow_id=workflow.id, trigger_type=payload.trigger_type, config_json=json.dumps(payload.config, sort_keys=True), enabled=payload.enabled)
    db.add(row); audit(db, org, user, "automation_trigger_created", "trigger", row.id); db.commit()
    return {"id": row.id, "trigger_type": row.trigger_type, "enabled": row.enabled}


@router.post("/organizations/{slug}/automation/events", status_code=202)
def receive_event(payload: EventIn, ctx=Depends(org_context), _: None = Depends(require_csrf)):
    org, _, user, db = ctx
    key_value = f"event:{payload.event_type}:{payload.event_id}"
    existing = db.scalar(select(AutomationIdempotencyKey).where(AutomationIdempotencyKey.organization_id == org.id, AutomationIdempotencyKey.idempotency_key == key_value))
    if existing:
        return {"status": "deduplicated", "run_id": existing.run_id}
    triggers = db.scalars(select(AutomationTrigger).where(AutomationTrigger.organization_id == org.id, AutomationTrigger.trigger_type == "event", AutomationTrigger.enabled.is_(True))).all()
    created = 0
    for trigger in triggers:
        version = db.scalar(select(AutomationWorkflowVersion).where(AutomationWorkflowVersion.workflow_id == trigger.workflow_id, AutomationWorkflowVersion.status == "published").order_by(AutomationWorkflowVersion.version_number.desc()))
        if not version: continue
        run = AutomationWorkflowRun(organization_id=org.id, workflow_id=trigger.workflow_id, version_id=version.id, triggered_by=user.id, correlation_id=f"event-{payload.event_id}-{trigger.id}")
        db.add(run); db.flush();
        for node in db.scalars(select(AutomationWorkflowNode).where(AutomationWorkflowNode.version_id == version.id)).all(): db.add(AutomationStepRun(run_id=run.id, node_key=node.node_key))
        if created == 0: db.add(AutomationIdempotencyKey(organization_id=org.id, idempotency_key=key_value, run_id=run.id))
        created += 1
    if created == 0: db.add(AutomationIdempotencyKey(organization_id=org.id, idempotency_key=key_value))
    audit(db, org, user, "automation_event_received", "event", outcome="accepted"); db.commit()
    return {"status": "accepted", "runs_queued": created, "execution": "worker_not_configured"}


@router.post("/organizations/{slug}/automation/workflows/{workflow_id}/versions/{version_id}/publish")
def publish_version(workflow_id: UUID, version_id: UUID, ctx=Depends(org_context), _: None = Depends(require_csrf)):
    org, _, user, db, workflow = workflow_for(ctx, workflow_id); check_role(ctx, MANAGERS)
    version = db.scalar(select(AutomationWorkflowVersion).where(AutomationWorkflowVersion.id == version_id, AutomationWorkflowVersion.workflow_id == workflow.id))
    if not version: raise HTTPException(404, "Workflow version not found")
    if version.status == "published": return {"id": version.id, "status": version.status}
    version.status = "published"; version.published_at = now(); workflow.status = "published"; workflow.enabled = True
    audit(db, org, user, "workflow_version_published", "workflow_version", version.id); db.commit()
    return {"id": version.id, "status": version.status, "execution": "worker_not_configured"}


@router.post("/organizations/{slug}/automation/workflows/{workflow_id}/runs", status_code=202)
def run_workflow(payload: RunIn, workflow_id: UUID, ctx=Depends(org_context), _: None = Depends(require_csrf)):
    org, member, user, db, workflow = workflow_for(ctx, workflow_id)
    version = db.scalar(select(__import__("app.models", fromlist=["AutomationWorkflowVersion"]).AutomationWorkflowVersion).where(__import__("app.models", fromlist=["AutomationWorkflowVersion"]).AutomationWorkflowVersion.workflow_id == workflow.id, __import__("app.models", fromlist=["AutomationWorkflowVersion"]).AutomationWorkflowVersion.status == "published").order_by(__import__("app.models", fromlist=["AutomationWorkflowVersion"]).AutomationWorkflowVersion.version_number.desc()))
    if not version: raise HTTPException(409, "A published workflow version is required")
    key = db.scalar(select(AutomationIdempotencyKey).where(AutomationIdempotencyKey.organization_id == org.id, AutomationIdempotencyKey.idempotency_key == payload.idempotency_key))
    if key and key.run_id: return {"id": key.run_id, "status": "queued", "idempotent": True, "execution": "worker_not_configured"}
    run = AutomationWorkflowRun(organization_id=org.id, workflow_id=workflow.id, version_id=version.id, triggered_by=user.id, correlation_id=f"automation-{UUID(int=__import__('uuid').uuid4().int)}")
    db.add(run); db.flush(); db.add(AutomationIdempotencyKey(organization_id=org.id, idempotency_key=payload.idempotency_key, run_id=run.id))
    for node in db.scalars(select(AutomationWorkflowNode).where(AutomationWorkflowNode.version_id == version.id)).all(): db.add(AutomationStepRun(run_id=run.id, node_key=node.node_key))
    audit(db, org, user, "workflow_run_queued", "workflow_run", run.id); db.commit()
    return {"id": run.id, "status": run.status, "execution": "worker_not_configured", "correlation_id": run.correlation_id}


@router.get("/organizations/{slug}/automation/runs")
def runs(ctx=Depends(org_context), page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100)):
    org, _, _, db = ctx; q = select(AutomationWorkflowRun).where(AutomationWorkflowRun.organization_id == org.id).order_by(AutomationWorkflowRun.created_at.desc())
    rows = db.scalars(q.offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [{"id": r.id, "workflow_id": r.workflow_id, "version_id": r.version_id, "status": r.status, "correlation_id": r.correlation_id, "failure_reason": r.failure_reason} for r in rows], "page": page, "page_size": page_size}


@router.get("/organizations/{slug}/automation/approvals")
def approvals(ctx=Depends(org_context)):
    org, _, _, db = ctx; rows = db.scalars(select(AutomationApprovalRequest).where(AutomationApprovalRequest.organization_id == org.id).order_by(AutomationApprovalRequest.created_at.desc())).all()
    return [{"id": r.id, "run_id": r.workflow_run_id, "status": r.status, "action_type": r.action_type, "expires_at": r.expires_at} for r in rows]


@router.post("/organizations/{slug}/automation/approvals/{request_id}/decision")
def decide_approval(payload: DecisionIn, request_id: UUID, ctx=Depends(org_context), _: None = Depends(require_csrf)):
    org, member, user, db = ctx; check_role(ctx, APPROVERS)
    row = db.scalar(select(AutomationApprovalRequest).where(AutomationApprovalRequest.id == request_id, AutomationApprovalRequest.organization_id == org.id))
    if not row: raise HTTPException(404, "Approval request not found")
    if row.requested_by == user.id: raise HTTPException(403, "Separation of duties prevents self-approval")
    if row.status != "pending": raise HTTPException(409, "Approval request already decided")
    if row.expires_at <= now(): row.status = "expired"; db.commit(); raise HTTPException(409, "Approval request expired")
    row.status = payload.decision; db.add(AutomationApprovalDecision(request_id=row.id, decided_by=user.id, decision=payload.decision, comment=payload.comment)); audit(db, org, user, "approval_decided", "approval", row.id); db.commit()
    return {"id": row.id, "status": row.status, "execution": "revalidation_required"}


@router.get("/organizations/{slug}/automation/agents")
def agents(ctx=Depends(org_context)):
    org, _, _, db = ctx; rows = db.scalars(select(AutomationAgentDefinition).where((AutomationAgentDefinition.organization_id == org.id) | (AutomationAgentDefinition.organization_id.is_(None)))).all()
    return [{"id": r.id, "key": r.agent_key, "name": r.name, "status": r.status if settings.ai_enabled else "Not Configured", "tools": [p.tool_key for p in db.scalars(select(AutomationAgentToolPermission).where(AutomationAgentToolPermission.agent_id == r.id, AutomationAgentToolPermission.enabled.is_(True))).all()]} for r in rows]


@router.get("/organizations/{slug}/automation/recommendations")
def recommendations(ctx=Depends(org_context), page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100)):
    org, _, user, db = ctx; rows = db.scalars(select(AutomationRecommendation).where(AutomationRecommendation.organization_id == org.id, AutomationRecommendation.user_id == user.id).order_by(AutomationRecommendation.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [{"id": r.id, "course_id": r.course_id, "explanation": r.explanation, "status": r.status} for r in rows], "page": page, "page_size": page_size}


@router.get("/organizations/{slug}/automation/templates")
def templates(ctx=Depends(org_context)):
    org, _, _, db = ctx; rows = db.scalars(select(AutomationTemplate).where((AutomationTemplate.organization_id == org.id) | (AutomationTemplate.organization_id.is_(None)))).all()
    return [{"id": r.id, "key": r.template_key, "name": r.name, "status": r.status} for r in rows]


@router.get("/organizations/{slug}/automation/usage")
def usage(ctx=Depends(org_context)):
    org, _, _, db = ctx; rows = db.scalars(select(AutomationUsageRecord).where(AutomationUsageRecord.organization_id == org.id).order_by(AutomationUsageRecord.created_at.desc()).limit(100)).all()
    return {"provider_status": "configured" if settings.ai_enabled and settings.ai_provider != "disabled" else "Not Configured", "items": [{"provider": r.provider, "requests": r.request_count, "input_tokens": r.input_tokens, "output_tokens": r.output_tokens, "estimated_cost": r.estimated_cost} for r in rows]}


@router.get("/platform/automation")
def platform_automation(user: User = Depends(__import__("app.auth", fromlist=["require_role"]).require_role("admin", "platform_admin", "super_admin")), db: Session = Depends(get_db)):
    return {"metrics": {"workflows": db.scalar(select(func.count()).select_from(AutomationWorkflow)) or 0, "queued_runs": db.scalar(select(func.count()).select_from(AutomationWorkflowRun).where(AutomationWorkflowRun.status.in_(["queued", "running"]))) or 0, "failed_runs": db.scalar(select(func.count()).select_from(AutomationWorkflowRun).where(AutomationWorkflowRun.status == "failed")) or 0}, "ai_status": "configured" if settings.ai_enabled and settings.ai_provider != "disabled" else "Not Configured", "data_source": "postgresql"}
