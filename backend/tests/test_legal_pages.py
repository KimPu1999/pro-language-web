from datetime import datetime, timezone
from app.auth import password_hasher
from app.models import User

def login(client):
    with client.session_factory() as db:
        db.add(User(email="legal-admin@example.com", email_normalized="legal-admin@example.com", password_hash=password_hasher.hash("legal-pass-123"), display_name="Legal Admin", role="platform_admin", account_status="active", email_verified_at=datetime.now(timezone.utc)))
        db.commit()
    assert client.post("/api/v1/admin/auth/login", json={"email":"legal-admin@example.com", "password":"legal-pass-123"}).status_code == 200
    return client.cookies.get("cm_csrf")

def test_legal_review_publish_and_revision_keeps_public_version(client):
    csrf = login(client)
    draft = {"title":"Privacy Policy", "content":"# Effective date\n\nFirst reviewed policy.", "version":"1.0", "effective_date":"2026-01-01T00:00:00Z"}
    saved = client.put("/api/v1/admin/legal/privacy", json=draft, headers={"X-CSRF-Token":csrf})
    assert saved.status_code == 200 and saved.json()["review_status"] == "draft"
    assert client.get("/api/v1/site/legal/privacy").status_code == 404
    assert client.post("/api/v1/admin/legal/privacy/submit-review", headers={"X-CSRF-Token":csrf}).status_code == 200
    assert client.post("/api/v1/admin/legal/privacy/approve", headers={"X-CSRF-Token":csrf}).status_code == 200
    published = client.post("/api/v1/admin/legal/privacy/publish", headers={"X-CSRF-Token":csrf})
    assert published.status_code == 200
    assert client.get("/api/v1/site/legal/privacy").json()["content"] == draft["content"]
    revised = {**draft, "content":"# Effective date\n\nSecond reviewed policy.", "version":"2.0"}
    assert client.put("/api/v1/admin/legal/privacy", json=revised, headers={"X-CSRF-Token":csrf}).status_code == 200
    assert client.get("/api/v1/site/legal/privacy").json()["content"] == draft["content"]
    assert client.post("/api/v1/admin/legal/privacy/submit-review", headers={"X-CSRF-Token":csrf}).status_code == 200
    rejected = client.post("/api/v1/admin/legal/privacy/reject", json={"reason":"Add the missing retention section."}, headers={"X-CSRF-Token":csrf})
    assert rejected.status_code == 200 and rejected.json()["review_status"] == "rejected"
    history = client.get("/api/v1/admin/legal/privacy", headers={"X-CSRF-Token":csrf})
    assert history.status_code == 200 and len(history.json()["versions"]) == 2

def test_legal_requires_explicit_approval_and_authentication(client):
    assert client.get("/api/v1/admin/legal").status_code == 401
    csrf = login(client)
    draft = {"title":"Terms", "content":"Reviewed terms.", "version":"1.0"}
    assert client.put("/api/v1/admin/legal/terms", json=draft, headers={"X-CSRF-Token":csrf}).status_code == 200
    assert client.post("/api/v1/admin/legal/terms/publish", headers={"X-CSRF-Token":csrf}).status_code == 409
