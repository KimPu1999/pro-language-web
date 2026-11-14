from datetime import timedelta
import logging
import time
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Cookie
from sqlalchemy import select
from sqlalchemy.orm import Session
from .auth import SESSION_COOKIE, check_rate_limit, clear_auth_cookies, create_session, current_user, hash_token, new_token, normalize_email, now, password_hasher, require_csrf, set_auth_cookies, validate_password, verify_password
from .config import settings
from .db import get_db
from .mailer import mailer
from .models import AuthSession, EmailVerificationToken, PasswordResetToken, SecurityAuditLog, User, UserProfile
from .schemas import ChangePasswordIn, ForgotPasswordIn, LoginIn, RegisterIn, ResetPasswordIn, UserOut
router=APIRouter(prefix="/api/v1/auth", tags=["auth"])
logger = logging.getLogger("codemaster.auth")
def profile_payload(user: User, db: Session):
    profile=db.scalar(select(UserProfile).where(UserProfile.user_id==user.id))
    return {"id":user.id,"email":user.email,"full_name":user.display_name,"role":user.role,"email_verified":bool(user.email_verified_at),"email_verified_at":user.email_verified_at,"profile":{"bio":profile.bio if profile else None,"learning_interests":profile.learning_interests.split("|") if profile and profile.learning_interests else [],"preferred_language":profile.preferred_language if profile else None,"learning_level":profile.learning_level if profile else None,"show_myanmar":profile.show_myanmar if profile else False,"avatar_url":profile.avatar_url if profile else None}}
def log_event(db, event, user_id=None, request=None): db.add(SecurityAuditLog(user_id=user_id,event=event,ip_address=request.client.host if request and request.client else None))
def send_verification(db, user, request):
    raw=new_token(); db.add(EmailVerificationToken(user_id=user.id,token_hash=hash_token(raw),expires_at=now()+timedelta(hours=settings.verification_ttl_hours))); mailer.send(user.email,"Verify your CodeMaster Academy email",f"Open {settings.app_base_url}/verify-email?token={raw}"); log_event(db,"verification_requested",user.id,request)
@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: RegisterIn, request: Request, response: Response, db: Session=Depends(get_db)):
    check_rate_limit(f"register:{request.client.host if request.client else 'unknown'}", 5)
    validate_password(payload.password); email=normalize_email(payload.email)
    if db.scalar(select(User).where(User.email_normalized==email)): raise HTTPException(400,"Unable to create account with those details")
    user=User(email=email,email_normalized=email,password_hash=password_hasher.hash(payload.password),display_name=payload.full_name.strip(),role="student",account_status="active",password_changed_at=now()); db.add(user); db.flush(); db.add(UserProfile(user_id=user.id)); send_verification(db,user,request); raw,csrf=create_session(db,user); user.last_login_at=now(); db.commit(); set_auth_cookies(response,raw,csrf); return profile_payload(user,db)
@router.post("/login", response_model=UserOut)
def login(payload: LoginIn, response: Response, request: Request, db: Session=Depends(get_db)):
    started = time.perf_counter()
    check_rate_limit(f"login:{request.client.host if request.client else 'unknown'}:{normalize_email(payload.email)}", 10)
    lookup_started = time.perf_counter()
    user=db.scalar(select(User).where(User.email_normalized==normalize_email(payload.email)))
    lookup_ms = (time.perf_counter() - lookup_started) * 1000
    verify_started = time.perf_counter()
    valid = bool(user and verify_password(payload.password,user.password_hash))
    verify_ms = (time.perf_counter() - verify_started) * 1000
    # Keep password verification before the account-status check so inactive
    # accounts do not become an account-enumeration oracle.
    if not valid or user.account_status != "active":
        logger.info("login_failed request_id=%s lookup_ms=%.1f password_verify_ms=%.1f total_ms=%.1f error_category=invalid_credentials", getattr(request.state, "request_id", "-"), lookup_ms, verify_ms, (time.perf_counter() - started) * 1000)
        raise HTTPException(401,"Invalid email or password")
    session_started = time.perf_counter()
    raw,csrf=create_session(db,user); user.last_login_at=now(); log_event(db,"login_success",user.id,request); db.commit(); set_auth_cookies(response,raw,csrf)
    payload_out = profile_payload(user,db)
    logger.info("login_success request_id=%s lookup_ms=%.1f password_verify_ms=%.1f session_commit_ms=%.1f total_ms=%.1f error_category=success", getattr(request.state, "request_id", "-"), lookup_ms, verify_ms, (time.perf_counter() - session_started) * 1000, (time.perf_counter() - started) * 1000)
    return payload_out
@router.get("/me", response_model=UserOut)
def me(user: User=Depends(current_user), db: Session=Depends(get_db)): return profile_payload(user,db)
@router.post("/logout")
def logout(response: Response, request: Request, session_token: str|None=Cookie(default=None,alias=SESSION_COOKIE), user: User=Depends(current_user), _: None=Depends(require_csrf), db: Session=Depends(get_db)):
    if session_token:
        session=db.scalar(select(AuthSession).where(AuthSession.token_hash==hash_token(session_token))); 
        if session: session.revoked_at=now()
    log_event(db,"logout",user.id,request); db.commit(); clear_auth_cookies(response); return {"status":"ok"}
@router.get("/verify-email")
def verify_email(token: str, db: Session=Depends(get_db)):
    record=db.scalar(select(EmailVerificationToken).where(EmailVerificationToken.token_hash==hash_token(token),EmailVerificationToken.used_at.is_(None),EmailVerificationToken.expires_at>now()))
    if not record: raise HTTPException(400,"Verification link is invalid or expired")
    user=db.get(User,record.user_id); record.used_at=now(); user.email_verified_at=now(); db.commit(); return {"status":"verified"}
@router.post("/resend-verification")
def resend_verification(payload: ForgotPasswordIn, request: Request, db: Session=Depends(get_db)):
    check_rate_limit(f"verify:{request.client.host if request.client else 'unknown'}", 5)
    user=db.scalar(select(User).where(User.email_normalized==normalize_email(payload.email)))
    if user and not user.email_verified_at: send_verification(db,user,request); db.commit()
    return {"message":"If an account needs verification, an email will be sent."}
@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordIn, request: Request, db: Session=Depends(get_db)):
    check_rate_limit(f"forgot:{request.client.host if request.client else 'unknown'}", 5)
    user=db.scalar(select(User).where(User.email_normalized==normalize_email(payload.email)))
    if user:
        raw=new_token(); db.add(PasswordResetToken(user_id=user.id,token_hash=hash_token(raw),expires_at=now()+timedelta(minutes=settings.reset_ttl_minutes))); db.commit(); mailer.send(user.email,"Reset your CodeMaster Academy password",f"Open {settings.app_base_url}/reset-password?token={raw}"); log_event(db,"password_reset_requested",user.id,request); db.commit()
    return {"message":"If an account exists, password reset instructions will be sent."}
@router.post("/reset-password")
def reset_password(payload: ResetPasswordIn, response: Response, db: Session=Depends(get_db)):
    validate_password(payload.password); record=db.scalar(select(PasswordResetToken).where(PasswordResetToken.token_hash==hash_token(payload.token),PasswordResetToken.used_at.is_(None),PasswordResetToken.expires_at>now()))
    if not record: raise HTTPException(400,"Reset link is invalid or expired")
    user=db.get(User,record.user_id); user.password_hash=password_hasher.hash(payload.password); user.password_changed_at=now(); record.used_at=now(); db.query(AuthSession).filter(AuthSession.user_id==user.id).update({"revoked_at":now()}); db.commit(); clear_auth_cookies(response); return {"status":"reset"}
@router.post("/change-password")
def change_password(payload: ChangePasswordIn, response: Response, user: User=Depends(current_user), _: None=Depends(require_csrf), db: Session=Depends(get_db)):
    if not verify_password(payload.current_password,user.password_hash): raise HTTPException(400,"Current password is incorrect")
    validate_password(payload.new_password); user.password_hash=password_hasher.hash(payload.new_password); user.password_changed_at=now(); db.query(AuthSession).filter(AuthSession.user_id==user.id).update({"revoked_at":now()}); raw,csrf=create_session(db,user); db.commit(); set_auth_cookies(response,raw,csrf); return {"status":"changed"}
