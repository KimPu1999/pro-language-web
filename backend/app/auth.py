import hashlib, secrets, time
from datetime import datetime, timedelta, timezone
from fastapi import Cookie, Depends, Header, HTTPException, Request, status
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .models import AuthSession, User

password_hasher = PasswordHasher()
_rate_buckets: dict[str, list[float]] = {}
SESSION_COOKIE = "cm_session"
CSRF_COOKIE = "cm_csrf"
def now() -> datetime: return datetime.now(timezone.utc)
def normalize_email(value: str) -> str: return value.strip().lower()
def check_rate_limit(key: str, limit: int = 10, window_seconds: int = 60) -> None:
    current=time.time(); bucket=[stamp for stamp in _rate_buckets.get(key,[]) if current-stamp < window_seconds]
    if len(bucket) >= limit: raise HTTPException(429,"Too many requests. Try again later.")
    bucket.append(current); _rate_buckets[key]=bucket
def validate_password(value: str) -> None:
    if len(value) < 8 or len(value) > 12: raise HTTPException(422, "Password must be between 8 and 12 characters")
def hash_token(raw: str) -> str: return hashlib.sha256(raw.encode()).hexdigest()
def new_token() -> str: return secrets.token_urlsafe(32)
def verify_password(password: str, password_hash: str) -> bool:
    try: return password_hasher.verify(password_hash, password)
    except VerifyMismatchError: return False
def create_session(db: Session, user: User) -> tuple[str, str]:
    raw = new_token(); csrf = new_token(); expires = now() + timedelta(hours=settings.session_ttl_hours)
    db.add(AuthSession(user_id=user.id, token_hash=hash_token(raw), expires_at=expires)); return raw, csrf
def set_auth_cookies(response, raw: str, csrf: str) -> None:
    response.set_cookie(SESSION_COOKIE, raw, httponly=True, secure=settings.cookie_secure, samesite=settings.cookie_samesite, max_age=settings.session_ttl_hours*3600, path="/")
    response.set_cookie(CSRF_COOKIE, csrf, httponly=False, secure=settings.cookie_secure, samesite=settings.cookie_samesite, max_age=settings.session_ttl_hours*3600, path="/")
def clear_auth_cookies(response) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/"); response.delete_cookie(CSRF_COOKIE, path="/")
def current_user(db: Session = Depends(get_db), session_token: str|None = Cookie(default=None, alias=SESSION_COOKIE)) -> User:
    if not session_token: raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required")
    session = db.scalar(select(AuthSession).where(AuthSession.token_hash==hash_token(session_token), AuthSession.revoked_at.is_(None), AuthSession.expires_at > now()))
    if not session: raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required")
    user = db.get(User, session.user_id)
    if not user or user.account_status != "active": raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required")
    return user
def require_csrf(request: Request, csrf_cookie: str|None=Cookie(default=None, alias=CSRF_COOKIE), csrf_header: str|None=Header(default=None, alias="X-CSRF-Token")) -> None:
    if request.method in {"POST","PUT","PATCH","DELETE"} and (not csrf_cookie or not csrf_header or not secrets.compare_digest(csrf_cookie, csrf_header)):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "CSRF validation failed")
def require_verified(user: User) -> User:
    if not user.email_verified_at: raise HTTPException(status.HTTP_403_FORBIDDEN, "Email verification required")
    return user
def verified_user(user: User = Depends(current_user)) -> User: return require_verified(user)
def require_role(*roles: str):
    def dependency(user: User = Depends(current_user)):
        if user.role not in roles: raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user
    return dependency
