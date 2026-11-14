import json
import re
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .auth import current_user, require_csrf, verified_user, now
from .config import settings
from .db import get_db
from .models import LearningLab, LearningLabVersion, LearningLabWorkspace, LearningLabWorkspaceFile, LearningLabSnapshot, LearningLabRun, LearningLabProgress, LearningLabAuditLog, User
from .organization_routes import org_context
router=APIRouter(prefix="/api/v1",tags=["learning-labs"])
PATH=re.compile(r"^[A-Za-z0-9_./-]+$"); ROLES={"owner","admin","instructor"}
class LabIn(BaseModel): title:str=Field(min_length=2,max_length=180); slug:str=Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",max_length=180); description_en:str=Field(min_length=1,max_length=10000); description_mm:str|None=None; category:str="coding"; difficulty:str="beginner"; language:str="python"; estimated_minutes:int=Field(default=30,ge=1,le=1000)
class FileIn(BaseModel): path:str=Field(min_length=1,max_length=240); source_code:str=Field(max_length=100000); language:str=Field(max_length=40)
class RunIn(BaseModel): idempotency_key:str=Field(min_length=8,max_length=180); path:str|None=None
def audit(db,actor,action,rid=None,org_id=None):db.add(LearningLabAuditLog(organization_id=org_id,actor_id=actor.id if actor else None,action=action,resource_id=rid))
def visible_lab(db,lab_id,user=None):
    lab=db.get(LearningLab,lab_id)
    if not lab: raise HTTPException(404,"Lab not found")
    if not lab.published:
        if not user: raise HTTPException(404,"Lab not found")
        if lab.created_by!=user.id and user.role not in {"admin","super_admin","instructor"}: raise HTTPException(404,"Lab not found")
    return lab
def workspace_for(db,workspace_id,user):
    row=db.scalar(select(LearningLabWorkspace).where(LearningLabWorkspace.id==workspace_id,LearningLabWorkspace.user_id==user.id))
    if not row:raise HTTPException(404,"Workspace not found")
    return row
@router.get("/labs")
def catalog(search:str|None=None,language:str|None=None,difficulty:str|None=None,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=50),db:Session=Depends(get_db)):
    q=select(LearningLab).where(LearningLab.published.is_(True),LearningLab.organization_id.is_(None)); count=select(func.count()).select_from(LearningLab).where(LearningLab.published.is_(True),LearningLab.organization_id.is_(None))
    if search:q=q.where(LearningLab.title.ilike(f"%{search}%"));count=count.where(LearningLab.title.ilike(f"%{search}%"))
    if language:q=q.where(LearningLab.language==language);count=count.where(LearningLab.language==language)
    if difficulty:q=q.where(LearningLab.difficulty==difficulty);count=count.where(LearningLab.difficulty==difficulty)
    total=db.scalar(count) or 0; rows=db.scalars(q.order_by(LearningLab.title).offset((page-1)*page_size).limit(page_size)).all()
    return {"items":[{"id":x.id,"title":x.title,"slug":x.slug,"description_en":x.description_en,"description_mm":x.description_mm,"difficulty":x.difficulty,"language":x.language,"estimated_minutes":x.estimated_minutes} for x in rows],"page":page,"page_size":page_size,"total":total}
@router.get("/labs/{lab_id}")
def detail(lab_id:UUID,db:Session=Depends(get_db)):
    # Public detail intentionally exposes only published public labs.
    lab=visible_lab(db,lab_id,None);return {"id":lab.id,"title":lab.title,"slug":lab.slug,"description_en":lab.description_en,"description_mm":lab.description_mm,"difficulty":lab.difficulty,"language":lab.language,"estimated_minutes":lab.estimated_minutes,"execution_status":"available_only_when_runner_configured"}
@router.get("/me/labs")
def dashboard(user:User=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.execute(select(LearningLabProgress,LearningLab).join(LearningLab,LearningLab.id==LearningLabProgress.lab_id).where(LearningLabProgress.user_id==user.id).order_by(LearningLabProgress.updated_at.desc()).limit(50)).all()
    return {"items":[{"lab_id":l.id,"title":l.title,"started":p.started,"completed":p.completed,"verified_steps":p.verified_steps} for p,l in rows],"data_source":"postgresql"}
@router.post("/labs/{lab_id}/workspace",status_code=201)
def create_workspace(lab_id:UUID,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    lab=visible_lab(db,lab_id,user);existing=db.scalar(select(LearningLabWorkspace).where(LearningLabWorkspace.lab_id==lab.id,LearningLabWorkspace.user_id==user.id))
    if existing:return {"id":existing.id,"status":existing.status,"idempotent":True}
    version=db.scalar(select(LearningLabVersion).where(LearningLabVersion.lab_id==lab.id,LearningLabVersion.status=="published").order_by(LearningLabVersion.version_number.desc()))
    if not version:raise HTTPException(409,"This lab has no published version")
    row=LearningLabWorkspace(lab_id=lab.id,user_id=user.id,version_id=version.id);db.add(row);db.flush();db.add(LearningLabProgress(lab_id=lab.id,user_id=user.id,started=True));audit(db,user,"workspace_created",row.id);db.commit();return {"id":row.id,"status":row.status}
@router.get("/lab-workspaces/{workspace_id}")
def workspace(workspace_id:UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=workspace_for(db,workspace_id,user);files=db.scalars(select(LearningLabWorkspaceFile).where(LearningLabWorkspaceFile.workspace_id==row.id).order_by(LearningLabWorkspaceFile.path)).all();return {"id":row.id,"lab_id":row.lab_id,"status":row.status,"files":[{"id":f.id,"path":f.path,"language":f.language,"source_code":f.source_code} for f in files],"runner_status":"configured" if settings.runner_enabled else "Not Configured"}
@router.put("/lab-workspaces/{workspace_id}/files")
def save_file(payload:FileIn,workspace_id:UUID,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=workspace_for(db,workspace_id,user)
    if not PATH.fullmatch(payload.path) or payload.path.startswith("/") or ".." in payload.path.split("/"):raise HTTPException(422,"Unsafe file path")
    file=db.scalar(select(LearningLabWorkspaceFile).where(LearningLabWorkspaceFile.workspace_id==row.id,LearningLabWorkspaceFile.path==payload.path))
    if not file:file=LearningLabWorkspaceFile(workspace_id=row.id,**payload.model_dump());db.add(file)
    else:file.source_code=payload.source_code;file.language=payload.language
    db.commit();return {"id":file.id,"path":file.path,"status":"saved"}
@router.post("/lab-workspaces/{workspace_id}/snapshots",status_code=201)
def snapshot(workspace_id:UUID,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=workspace_for(db,workspace_id,user);files=db.scalars(select(LearningLabWorkspaceFile).where(LearningLabWorkspaceFile.workspace_id==row.id)).all();snap=LearningLabSnapshot(workspace_id=row.id,created_by=user.id,files_json=json.dumps([{"path":f.path,"language":f.language,"source_code":f.source_code} for f in files]));db.add(snap);db.commit();return {"id":snap.id,"status":"saved"}
@router.post("/lab-workspaces/{workspace_id}/run",status_code=202)
def run(payload:RunIn,workspace_id:UUID,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=workspace_for(db,workspace_id,user);existing=db.scalar(select(LearningLabRun).where(LearningLabRun.user_id==user.id,LearningLabRun.idempotency_key==payload.idempotency_key));
    if existing:return {"id":existing.id,"status":existing.status,"idempotent":True}
    status="queued" if settings.runner_enabled else "runner_unavailable";reason=None if settings.runner_enabled else "Secure runner is not configured; no code was executed."
    job=LearningLabRun(lab_id=row.lab_id,workspace_id=row.id,user_id=user.id,idempotency_key=payload.idempotency_key,status=status,failure_reason=reason);db.add(job);db.commit();return {"id":job.id,"status":job.status,"message":reason or "Execution queued for the isolated runner."}
@router.get("/instructor/labs")
def instructor_labs(user:User=Depends(current_user),db:Session=Depends(get_db)):
    if user.role not in {"instructor","admin","super_admin"}:raise HTTPException(403,"Instructor permission required")
    rows=db.scalars(select(LearningLab).where(LearningLab.created_by==user.id).order_by(LearningLab.updated_at.desc())).all();return [{"id":x.id,"title":x.title,"status":x.status,"published":x.published} for x in rows]
@router.post("/instructor/labs",status_code=201)
def create_lab(payload:LabIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if user.role not in {"instructor","admin","super_admin"}:raise HTTPException(403,"Instructor permission required")
    if db.scalar(select(LearningLab).where(LearningLab.organization_id.is_(None),LearningLab.slug==payload.slug)):raise HTTPException(409,"Lab slug already exists")
    row=LearningLab(created_by=user.id,**payload.model_dump());db.add(row);db.flush();version=LearningLabVersion(lab_id=row.id,version_number=1,created_by=user.id,snapshot_json=json.dumps(payload.model_dump(),default=str));db.add(version);audit(db,user,"lab_created",row.id);db.commit();return {"id":row.id,"version_id":version.id,"status":row.status}
@router.post("/instructor/labs/{lab_id}/publish")
def publish(lab_id:UUID,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(LearningLab).where(LearningLab.id==lab_id,LearningLab.created_by==user.id))
    if not row and user.role not in {"admin","super_admin"}:raise HTTPException(403,"Lab ownership required")
    if not row:row=db.get(LearningLab,lab_id)
    version=db.scalar(select(LearningLabVersion).where(LearningLabVersion.lab_id==row.id).order_by(LearningLabVersion.version_number.desc()))
    if not version:raise HTTPException(409,"Lab version is required")
    version.status="published";row.status="published";row.published=True;audit(db,user,"lab_published",row.id);db.commit();return {"id":row.id,"status":row.status}
@router.get("/platform/labs")
def platform_labs(user:User=Depends(__import__("app.auth",fromlist=["require_role"]).require_role("admin","platform_admin","super_admin")),db:Session=Depends(get_db)):
    return {"metrics":{"labs":db.scalar(select(func.count()).select_from(LearningLab)) or 0,"runs":db.scalar(select(func.count()).select_from(LearningLabRun)) or 0,"failed_runs":db.scalar(select(func.count()).select_from(LearningLabRun).where(LearningLabRun.status.in_(["runner_unavailable","failed"]))) or 0},"runner_status":"configured" if settings.runner_enabled else "Not Configured","data_source":"postgresql"}
