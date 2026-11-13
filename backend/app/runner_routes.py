from datetime import timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from .auth import current_user, require_csrf, verified_user, now
from .config import settings
from .db import get_db
from .models import CodeExecutionJob, CodeExecutionResult, CodeSubmission, CodingExercise, ExerciseTestCase, StudentEditorPreference, User
from .runner_queue import queue
from .runner_registry import RUNTIMES, get_runtime
from pydantic import BaseModel, Field
router=APIRouter(prefix="/api/v1/runner",tags=["runner"])
class ExecuteIn(BaseModel): language: str; source_code: str=Field(min_length=1); exercise_id: UUID|None=None; idempotency_key: str|None=Field(default=None,max_length=128)
class PreferenceIn(BaseModel): font_size:int=Field(default=14,ge=10,le=32); theme:str="vs-dark"; word_wrap:bool=True; tab_size:int=Field(default=2,ge=1,le=8); minimap:bool=False; auto_save:bool=True
def job_view(job, result=None): return {"id":job.id,"language":job.language,"status":job.status,"queued_at":job.queued_at,"started_at":job.started_at,"finished_at":job.finished_at,"expires_at":job.expires_at,"result":None if not result else {"stdout":result.stdout,"stderr":result.stderr,"exit_code":result.exit_code,"execution_time_ms":result.execution_time_ms,"truncated":result.truncated,"error_code":result.error_code}}
@router.get("/languages")
def languages(user:User=Depends(current_user)): return [{"identifier":x.identifier,"version":x.version,"filename":x.filename} for x in RUNTIMES.values()]
@router.post("/execute",status_code=202)
def execute(payload:ExecuteIn,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    try: get_runtime(payload.language)
    except ValueError: raise HTTPException(422,"Unsupported language")
    if len(payload.source_code.encode())>settings.max_source_code_bytes: raise HTTPException(413,"Source code is too large")
    if payload.exercise_id and not db.get(CodingExercise,payload.exercise_id): raise HTTPException(404,"Exercise not found")
    if payload.idempotency_key:
        existing=db.scalar(select(CodeExecutionJob).where(CodeExecutionJob.idempotency_key==payload.idempotency_key,CodeExecutionJob.user_id==user.id))
        if existing: return job_view(existing,db.scalar(select(CodeExecutionResult).where(CodeExecutionResult.job_id==existing.id)))
    job=CodeExecutionJob(user_id=user.id,exercise_id=payload.exercise_id,language=payload.language,source_code=payload.source_code,status="queued",idempotency_key=payload.idempotency_key,expires_at=now()+timedelta(minutes=10)); db.add(job); db.flush()
    if not queue.enqueue(str(job.id)):
        job.status="runner_unavailable"; job.finished_at=now(); db.add(CodeExecutionResult(job_id=job.id,stderr="The secure execution runner is unavailable.",error_code="RUNNER_UNAVAILABLE"))
    db.commit(); return job_view(job,db.scalar(select(CodeExecutionResult).where(CodeExecutionResult.job_id==job.id)))
@router.get("/jobs/{job_id}")
def get_job(job_id:UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):
    job=db.scalar(select(CodeExecutionJob).where(CodeExecutionJob.id==job_id,CodeExecutionJob.user_id==user.id))
    if not job: raise HTTPException(404,"Job not found")
    return job_view(job,db.scalar(select(CodeExecutionResult).where(CodeExecutionResult.job_id==job.id)))
@router.post("/jobs/{job_id}/cancel")
def cancel_job(job_id:UUID,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    job=db.scalar(select(CodeExecutionJob).where(CodeExecutionJob.id==job_id,CodeExecutionJob.user_id==user.id))
    if not job: raise HTTPException(404,"Job not found")
    if job.status in {"queued","running"}: job.status="cancelled"; job.finished_at=now(); db.commit()
    return job_view(job,db.scalar(select(CodeExecutionResult).where(CodeExecutionResult.job_id==job.id)))
@router.get("/exercises/{slug}")
def exercise(slug:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.scalar(select(CodingExercise).where(CodingExercise.slug==slug,CodingExercise.status=="published"))
    if not row: raise HTTPException(404,"Exercise not found")
    tests=db.scalars(select(ExerciseTestCase).where(ExerciseTestCase.exercise_id==row.id,ExerciseTestCase.is_hidden.is_(False)).order_by(ExerciseTestCase.position)).all()
    return {"id":row.id,"title":row.title,"slug":row.slug,"description_en":row.description_en,"description_mm":row.description_mm,"difficulty":row.difficulty,"language":row.language,"starter_code":row.starter_code,"public_tests":[{"input":t.input_data,"expected_output":t.expected_output,"points":t.points} for t in tests]}
@router.post("/exercises/{exercise_id}/submit",status_code=202)
def submit(exercise_id:UUID,payload:ExecuteIn,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    exercise=db.scalar(select(CodingExercise).where(CodingExercise.id==exercise_id,CodingExercise.status=="published"))
    if not exercise: raise HTTPException(404,"Exercise not found")
    if payload.language!=exercise.language: raise HTTPException(422,"Submission language does not match exercise")
    execution=execute(payload.model_copy(update={"exercise_id":exercise_id}),user,_,db)
    job_id=execution["id"]; submission=CodeSubmission(user_id=user.id,exercise_id=exercise_id,job_id=job_id,language=payload.language,source_code=payload.source_code,status=execution["status"]); db.add(submission); db.commit(); return {"submission_id":submission.id,"job":execution}
@router.get("/submissions")
def submissions(user:User=Depends(current_user),exercise_id:UUID|None=None,db:Session=Depends(get_db)):
    q=select(CodeSubmission).where(CodeSubmission.user_id==user.id).order_by(CodeSubmission.created_at.desc()).limit(50)
    if exercise_id:q=q.where(CodeSubmission.exercise_id==exercise_id)
    return db.scalars(q).all()
@router.get("/preferences")
def preferences(user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.scalar(select(StudentEditorPreference).where(StudentEditorPreference.user_id==user.id)); return row or {"font_size":14,"theme":"vs-dark","word_wrap":True,"tab_size":2,"minimap":False,"auto_save":True}
@router.put("/preferences")
def update_preferences(payload:PreferenceIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(StudentEditorPreference).where(StudentEditorPreference.user_id==user.id)) or StudentEditorPreference(user_id=user.id); [setattr(row,k,v) for k,v in payload.model_dump().items()]; db.add(row); db.commit(); return row
