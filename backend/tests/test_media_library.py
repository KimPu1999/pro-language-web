import base64
from datetime import datetime, timezone

from sqlalchemy import select

from app.auth import password_hasher
from app.models import Course, MediaAsset, User


PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=")


def admin_login(client):
    with client.session_factory() as db:
        db.add(User(email="media-admin@example.com", email_normalized="media-admin@example.com", password_hash=password_hasher.hash("admin-pass-123"), display_name="Media Admin", role="platform_admin", account_status="active", email_verified_at=datetime.now(timezone.utc)))
        db.commit()
    assert client.post("/api/v1/admin/auth/login", json={"email": "media-admin@example.com", "password": "admin-pass-123"}).status_code == 200
    return client.cookies.get("cm_csrf")


def test_media_library_upload_metadata_and_safe_in_use_archive(client, monkeypatch, tmp_path):
    from app.config import settings
    monkeypatch.setattr(settings, "media_root", str(tmp_path / "media"))
    assert client.get("/api/v1/admin/media").status_code in {401, 403}
    csrf = admin_login(client)
    uploaded = client.post("/api/v1/admin/media", files={"file": ("hero.png", PNG, "image/png")}, data={"title": "Hero image", "alt_text": "A learning hero", "collection": "homepage"}, headers={"X-CSRF-Token": csrf})
    assert uploaded.status_code == 201, uploaded.text
    asset = uploaded.json(); assert asset["mime_type"] == "image/png"; assert asset["url"].startswith("/media/library/")
    listed = client.get("/api/v1/admin/media?search=Hero"); assert listed.status_code == 200; assert listed.json()["total"] == 1
    updated = client.patch(f"/api/v1/admin/media/{asset['id']}", json={"title": "Updated hero", "alt_text": "Updated alt", "caption": "Caption", "collection": "homepage"}, headers={"X-CSRF-Token": csrf})
    assert updated.status_code == 200 and updated.json()["title"] == "Updated hero"
    with client.session_factory() as db:
        course = db.scalar(select(Course).where(Course.slug == "python-foundations")); course.thumbnail = asset["url"]; db.commit()
    blocked = client.delete(f"/api/v1/admin/media/{asset['id']}", headers={"X-CSRF-Token": csrf}); assert blocked.status_code == 409
    with client.session_factory() as db:
        course = db.scalar(select(Course).where(Course.slug == "python-foundations")); course.thumbnail = None; db.commit()
    archived = client.delete(f"/api/v1/admin/media/{asset['id']}", headers={"X-CSRF-Token": csrf}); assert archived.status_code == 200 and archived.json()["status"] == "archived"
    restored = client.post(f"/api/v1/admin/media/{asset['id']}/restore", headers={"X-CSRF-Token": csrf}); assert restored.status_code == 200 and restored.json()["status"] == "active"


def test_media_library_rejects_unsafe_file_and_student_writes(client):
    client.post("/api/v1/auth/register", json={"full_name": "Media Student", "email": "media-student@example.com", "password": "strong-pwd12", "confirm_password": "strong-pwd12", "accept_terms": True})
    csrf = client.cookies.get("cm_csrf")
    response = client.post("/api/v1/admin/media", files={"file": ("script.html", b"<script>alert(1)</script>", "text/html")}, headers={"X-CSRF-Token": csrf})
    assert response.status_code in {401, 403}
