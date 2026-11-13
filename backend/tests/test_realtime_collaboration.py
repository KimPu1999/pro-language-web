from datetime import datetime, timezone
from sqlalchemy import select
from app.models import User

def login_verified(client, email):
    response = client.post("/api/v1/auth/register", json={"full_name":"Realtime User","email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True})
    assert response.status_code == 201
    with client.session_factory() as db:
        user = db.scalar(select(User).where(User.email == email)); user.email_verified_at = datetime.now(timezone.utc); db.commit()
    client.post("/api/v1/auth/login", json={"email":email,"password":"strong-pwd12"})
    return client.cookies.get("cm_csrf")

def test_room_membership_and_document_ownership(client):
    csrf = login_verified(client, "realtime@example.com")
    created = client.post("/api/v1/collaboration/rooms", json={"name":"Pair room"}, headers={"X-CSRF-Token":csrf})
    assert created.status_code == 201
    room_id = created.json()["id"]
    detail = client.get(f"/api/v1/collaboration/rooms/{room_id}")
    assert detail.status_code == 200
    document = client.post(f"/api/v1/collaboration/rooms/{room_id}/documents", json={"path":"main.py","language":"python"}, headers={"X-CSRF-Token":csrf})
    assert document.status_code == 201
    unsafe = client.post(f"/api/v1/collaboration/rooms/{room_id}/documents", json={"path":"../secret.py","language":"python"}, headers={"X-CSRF-Token":csrf})
    assert unsafe.status_code == 422

def test_realtime_and_runner_are_truthfully_unavailable(client):
    csrf = login_verified(client, "realtime-status@example.com")
    room = client.post("/api/v1/collaboration/rooms", json={"name":"Status room"}, headers={"X-CSRF-Token":csrf}).json()
    response = client.post(f"/api/v1/collaboration/rooms/{room['id']}/run", json={"idempotency_key":"run-status-1"}, headers={"X-CSRF-Token":csrf})
    assert response.status_code == 202
    assert response.json()["status"] == "runner_unavailable"
