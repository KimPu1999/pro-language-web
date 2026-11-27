from datetime import datetime, timezone

from app.auth import password_hasher
from app.models import PlatformSettingHistory, User


def admin_login(client):
    with client.session_factory() as db:
        db.add(User(email="settings-admin@example.com", email_normalized="settings-admin@example.com", password_hash=password_hasher.hash("admin-pass-123"), display_name="Settings Admin", role="platform_admin", account_status="active", email_verified_at=datetime.now(timezone.utc)))
        db.commit()
    assert client.post("/api/v1/admin/auth/login", json={"email": "settings-admin@example.com", "password": "admin-pass-123"}).status_code == 200
    return client.cookies.get("cm_csrf")


def test_platform_settings_persist_and_public_config_is_filtered(client):
    csrf = admin_login(client)
    loaded = client.get("/api/v1/admin/platform/settings")
    assert loaded.status_code == 200
    assert set(("general", "branding", "languages", "seo", "registration", "email", "media", "learning", "integrations", "system")) <= set(loaded.json()["groups"])
    assert loaded.json()["groups"]["general"]["version"] == 0

    saved = client.patch("/api/v1/admin/platform/settings/general", json={"expected_version": 0, "values": {"website_name": "Languages-Platform", "website_tagline": "Learn together.", "site_url": "https://learn.example"}, "change_reason": "Set public platform identity"}, headers={"X-CSRF-Token": csrf})
    assert saved.status_code == 200, saved.text
    assert saved.json()["version"] == 1
    assert saved.json()["values"]["website_name"] == "Languages-Platform"

    refreshed = client.get("/api/v1/admin/platform/settings/general")
    assert refreshed.json()["values"]["website_tagline"] == "Learn together."
    public = client.get("/api/v1/public/platform-config")
    assert public.status_code == 200
    assert public.json()["website"]["name"] == "Languages-Platform"
    assert "smtp_password" not in str(public.json())
    history = client.get("/api/v1/admin/platform/settings/history?group=general")
    assert history.status_code == 200 and history.json()["total"] == 1
    with client.session_factory() as db:
        assert db.query(PlatformSettingHistory).count() == 1


def test_platform_settings_reject_unknown_keys_and_stale_versions(client):
    csrf = admin_login(client)
    unknown = client.patch("/api/v1/admin/platform/settings/general", json={"expected_version": 0, "values": {"smtp_password": "do-not-store"}}, headers={"X-CSRF-Token": csrf})
    assert unknown.status_code == 422
    first = client.patch("/api/v1/admin/platform/settings/languages", json={"expected_version": 0, "values": {"default_locale": "my"}}, headers={"X-CSRF-Token": csrf})
    assert first.status_code == 200
    stale = client.patch("/api/v1/admin/platform/settings/languages", json={"expected_version": 0, "values": {"default_locale": "en"}}, headers={"X-CSRF-Token": csrf})
    assert stale.status_code == 409


def test_student_cannot_read_or_update_platform_settings(client):
    client.post("/api/v1/auth/register", json={"full_name": "Settings Student", "email": "settings-student@example.com", "password": "strong-pwd12", "confirm_password": "strong-pwd12", "accept_terms": True})
    csrf = client.cookies.get("cm_csrf")
    assert client.get("/api/v1/admin/platform/settings").status_code == 403
    assert client.patch("/api/v1/admin/platform/settings/general", json={"expected_version": 0, "values": {}}, headers={"X-CSRF-Token": csrf}).status_code == 403
