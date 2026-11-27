from datetime import datetime, timezone

from app.auth import password_hasher
from app.models import NotificationMessage, NotificationOutbox, User


def add_user(client, email, role="student"):
    with client.session_factory() as db:
        row = User(email=email, email_normalized=email, password_hash=password_hasher.hash("notify-pass"), display_name=email.split("@")[0], role=role, account_status="active", email_verified_at=datetime.now(timezone.utc))
        db.add(row)
        db.commit()
        return row.id


def login(client, email):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "notify-pass"})
    assert response.status_code == 200, response.text
    return client.cookies.get("cm_csrf")


def test_announcement_approval_publishes_durable_inbox_records(client):
    add_user(client, "notify-admin@example.com", "platform_admin")
    add_user(client, "notify-student@example.com")
    csrf = login(client, "notify-admin@example.com")
    created = client.post("/api/v1/admin/notifications/announcements", json={"title_en": "Maintenance", "title_mm": "ပြုပြင်ထိန်းသိမ်းမှု", "body_en": "The platform will be updated.", "body_mm": "ပလက်ဖောင်းကို အပ်ဒိတ်လုပ်ပါမည်။", "channels": ["in_app", "email"]}, headers={"X-CSRF-Token": csrf})
    assert created.status_code == 200, created.text
    announcement_id = created.json()["id"]
    assert client.post(f"/api/v1/admin/notifications/announcements/{announcement_id}/submit", headers={"X-CSRF-Token": csrf}).status_code == 200
    assert client.post(f"/api/v1/admin/notifications/announcements/{announcement_id}/approve", headers={"X-CSRF-Token": csrf}).status_code == 200
    published = client.post(f"/api/v1/admin/notifications/announcements/{announcement_id}/publish", headers={"X-CSRF-Token": csrf})
    assert published.status_code == 200, published.text
    assert published.json()["messages_created"] == 2
    with client.session_factory() as db:
        assert db.query(NotificationMessage).count() == 2
        assert db.query(NotificationOutbox).count() == 2
        assert db.query(NotificationMessage).filter(NotificationMessage.channel == "email", NotificationMessage.status == "queued").count() == 1

    client.cookies.clear()
    login(client, "notify-student@example.com")
    inbox = client.get("/api/v1/me/notifications")
    assert inbox.status_code == 200 and inbox.json()["unread"] == 1
    message_id = inbox.json()["items"][0]["id"]
    csrf = client.cookies.get("cm_csrf")
    assert client.post(f"/api/v1/me/notifications/{message_id}/read", headers={"X-CSRF-Token": csrf}).status_code == 200
    assert client.get("/api/v1/me/notifications").json()["unread"] == 0


def test_notification_templates_reject_undeclared_variables(client):
    add_user(client, "template-admin@example.com", "platform_admin")
    csrf = login(client, "template-admin@example.com")
    response = client.post("/api/v1/admin/notifications/templates", json={"template_key": "course.update", "name": "Course update", "channel": "in_app", "locale": "en", "body": "Hello {{user_name}} {{secret}}", "variables": ["user_name"]}, headers={"X-CSRF-Token": csrf})
    assert response.status_code == 422


def test_notification_provider_does_not_claim_console_delivery(client):
    add_user(client, "provider-admin@example.com", "platform_admin")
    login(client, "provider-admin@example.com")
    response = client.get("/api/v1/admin/notifications/providers")
    assert response.status_code == 200
    email = next(item for item in response.json()["items"] if item["channel"] == "email")
    assert email["status"] == "not_configured"
