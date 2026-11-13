from datetime import datetime, timezone
from app.auth import password_hasher
from app.models import User

def admin_login(client):
    with client.session_factory() as db:
        db.add(User(email="analytics-admin@example.com", email_normalized="analytics-admin@example.com", password_hash=password_hasher.hash("admin-pass-123"), display_name="Analytics Admin", role="admin", account_status="active", email_verified_at=datetime.now(timezone.utc)))
        db.commit()
    response = client.post("/api/v1/auth/login", json={"email":"analytics-admin@example.com", "password":"admin-pass-123"})
    assert response.status_code == 200
    return client.cookies.get("cm_csrf")

def test_analytics_requires_platform_admin(client):
    assert client.get("/api/v1/platform/analytics/overview").status_code == 401

def test_analytics_overview_uses_real_empty_dataset(client):
    admin_login(client)
    response = client.get("/api/v1/platform/analytics/overview")
    assert response.status_code == 200
    body = response.json()
    assert body["kpis"]["published_courses"] == 1
    assert body["kpis"]["total_students"] == 0
    assert "definitions" in body

def test_invalid_analytics_date_range_is_rejected(client):
    admin_login(client)
    response = client.get("/api/v1/platform/analytics/overview?start_date=2026-02-01&end_date=2026-01-01")
    assert response.status_code == 422

def test_report_export_requires_csrf_and_admin(client):
    assert client.post("/api/v1/platform/reports/export").status_code == 401
    csrf = admin_login(client)
    response = client.post("/api/v1/platform/reports/export", headers={"X-CSRF-Token": csrf})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
