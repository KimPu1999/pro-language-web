from datetime import datetime, timezone
from sqlalchemy import select
from app.config import settings
from app.models import AIConversation, Lesson, User
def verified_client(client,email):
    response=client.post("/api/v1/auth/register",json={"full_name":"AI Student","email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True});assert response.status_code==201
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

def test_ai_mock_stream_uses_myanmar_lesson_context(client):
    old_enabled, old_provider = settings.ai_enabled, settings.ai_provider
    settings.ai_enabled, settings.ai_provider = True, "mock"
    try:
        csrf = verified_client(client, "ai-mm@example.com")
        with client.session_factory() as db:
            lesson = db.query(Lesson).first()
            lesson_id = str(lesson.id)
        created = client.post("/api/v1/ai/conversations", json={"title": "MM tutor"}, headers={"X-CSRF-Token": csrf})
        response = client.post(f"/api/v1/ai/conversations/{created.json()['id']}/stream", json={"message": "ရှင်းပြပါ", "language": "mm", "context_type": "lesson", "context_id": lesson_id}, headers={"X-CSRF-Token": csrf})
        assert response.status_code == 200
        assert "Mock provider response" in response.text
        assert "event: complete" in response.text
        with client.session_factory() as db:
            row = db.query(Lesson).first()
            assert db.query(User).filter(User.email == "ai-mm@example.com").first()
            assert row.content_mm == "မြန်မာ"
            conversation = db.query(AIConversation).order_by(AIConversation.created_at.desc()).first()
            assert conversation.language == "mm"
            assert conversation.lesson_id == row.id
    finally:
        settings.ai_enabled, settings.ai_provider = old_enabled, old_provider
