from datetime import datetime, timezone
from sqlalchemy import select
from app.config import settings
from app.models import User
def verified_client(client,email):
    response=client.post("/api/v1/auth/register",json={"full_name":"AI Student","email":email,"password":"strong-pass-123","confirm_password":"strong-pass-123","accept_terms":True});assert response.status_code==201
    with client.session_factory() as db:
        user=db.scalar(select(User).where(User.email==email));user.email_verified_at=datetime.now(timezone.utc);db.commit()
    return client.cookies.get("cm_csrf")
def test_ai_conversation_ownership_and_unavailable_stream(client):
    csrf=verified_client(client,"ai-one@example.com");created=client.post("/api/v1/ai/conversations",json={"title":"Python help"},headers={"X-CSRF-Token":csrf});assert created.status_code==201;conversation_id=created.json()["id"]
    response=client.post(f"/api/v1/ai/conversations/{conversation_id}/stream",json={"message":"Explain loops"},headers={"X-CSRF-Token":csrf});assert response.status_code==200;assert "AI tutor is unavailable" in response.text
    client.post("/api/v1/auth/logout",headers={"X-CSRF-Token":csrf});other=verified_client(client,"ai-two@example.com");assert client.get(f"/api/v1/ai/conversations/{conversation_id}").status_code==404;assert other
def test_ai_quota_is_server_enforced(client):
    old=settings.ai_daily_request_limit;settings.ai_daily_request_limit=0
    try:
        csrf=verified_client(client,"ai-quota@example.com");created=client.post("/api/v1/ai/conversations",json={},headers={"X-CSRF-Token":csrf});response=client.post(f"/api/v1/ai/conversations/{created.json()['id']}/stream",json={"message":"hello"},headers={"X-CSRF-Token":csrf});assert response.status_code==429
    finally: settings.ai_daily_request_limit=old
