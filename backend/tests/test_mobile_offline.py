from datetime import datetime, timezone

from sqlalchemy import select

from app.auth import password_hasher
from app.models import Course, Lesson, User


def login(client, email="mobile@example.com", role="student"):
    with client.session_factory() as db:
        user = User(email=email, email_normalized=email, password_hash=password_hasher.hash("mobile-pass"), display_name="Mobile", role=role, account_status="active", email_verified_at=datetime.now(timezone.utc))
        db.add(user); db.commit()
    assert client.post("/api/v1/auth/login", json={"email": email, "password": "mobile-pass"}).status_code == 200
    return client.cookies.get("cm_csrf")


def course_id(client):
    with client.session_factory() as db:
        course = db.scalar(select(Course)); course.published = True; db.commit(); return str(course.id)


def test_manifest_and_content_are_authenticated_and_account_scoped(client):
    assert client.get("/api/v1/mobile/dashboard").status_code == 401
    csrf = login(client); created = client.post("/api/v1/mobile/manifests", json={"course_id": course_id(client)}, headers={"X-CSRF-Token": csrf})
    assert created.status_code == 201
    content = client.get(f"/api/v1/mobile/manifests/{created.json()['id']}/content")
    assert content.status_code == 200 and content.json()["verified_offline"] is False
    client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf})
    login(client, "mobile-other@example.com")
    assert client.get(f"/api/v1/mobile/manifests/{created.json()['id']}/content").status_code == 404


def test_sync_is_idempotent_and_conflicts_are_explicit(client):
    csrf = login(client, "sync@example.com"); with_db = client.session_factory()
    with with_db as db:
        lesson = db.scalar(select(Lesson)); lesson.published = True; db.commit(); lesson_id = str(lesson.id)
    event = {"event_id": "offline-event-001", "event_type": "lesson_progress", "lesson_id": lesson_id, "content_version": "stale-version", "payload": {"completed": True}}
    first = client.post("/api/v1/mobile/sync", json={"events": [event]}, headers={"X-CSRF-Token": csrf})
    assert first.status_code == 200 and first.json()["items"][0]["status"] == "conflict"
    second = client.post("/api/v1/mobile/sync", json={"events": [event]}, headers={"X-CSRF-Token": csrf})
    assert second.status_code == 200 and second.json()["items"][0]["status"] == "conflict"


def test_push_preferences_and_platform_operations_preserve_rbac(client):
    csrf = login(client, "push@example.com")
    assert client.put("/api/v1/mobile/notifications", json={"enabled": True, "categories": ["reminders"]}, headers={"X-CSRF-Token": csrf}).status_code == 200
    push = client.post("/api/v1/mobile/push-subscriptions", json={"endpoint": "https://push.example.test/subscription", "keys": {"p256dh": "public-key", "auth": "auth-key"}}, headers={"X-CSRF-Token": csrf})
    assert push.status_code == 201 and push.json()["provider"] == "not_configured"
    assert client.get("/api/v1/mobile/platform/operations").status_code == 403
    client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf})
    login(client, "mobile-admin@example.com", role="platform_admin")
    assert client.get("/api/v1/mobile/platform/operations").status_code == 200
