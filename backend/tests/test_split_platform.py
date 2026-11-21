import json
from datetime import datetime, timezone

from sqlalchemy import select

from app.auth import password_hasher
from app.models import User


def admin_login(client):
    with client.session_factory() as db:
        db.add(User(email="split-admin@example.com", email_normalized="split-admin@example.com", password_hash=password_hasher.hash("admin-pass-123"), display_name="Split Admin", role="platform_admin", account_status="active", email_verified_at=datetime.now(timezone.utc)))
        db.commit()
    response = client.post("/api/v1/admin/auth/login", json={"email": "split-admin@example.com", "password": "admin-pass-123"})
    assert response.status_code == 200
    return client.cookies.get("cm_csrf")


def test_public_branding_and_draft_page_visibility(client):
    assert client.get("/api/v1/site/branding").json()["website_name"] == "Learn-Coding"
    assert client.get("/api/v1/site/pages/about").status_code == 404


def test_admin_navigation_and_published_page_reach_public_api(client):
    csrf = admin_login(client)
    navigation = {"items": [{"label": "Courses", "href": "/courses", "enabled": True, "position": 0, "area": "header"}]}
    response = client.patch("/api/v1/admin/settings/navigation", json=navigation, headers={"X-CSRF-Token": csrf})
    assert response.status_code == 200
    assert client.get("/api/v1/site/navigation").json()["items"][0]["href"] == "/courses"
    page = {"slug": "about", "title": "About Learn-Coding", "body": "Our mission.", "status": "draft"}
    assert client.put("/api/v1/admin/pages/about", json=page, headers={"X-CSRF-Token": csrf}).status_code == 200
    assert client.get("/api/v1/site/pages/about").status_code == 404
    page["status"] = "published"
    assert client.put("/api/v1/admin/pages/about", json=page, headers={"X-CSRF-Token": csrf}).status_code == 200
    public = client.get("/api/v1/site/pages/about")
    assert public.status_code == 200
    assert public.json()["title"] == "About Learn-Coding"


def test_student_cannot_update_navigation(client):
    client.post("/api/v1/auth/register", json={"full_name": "Student", "email": "split-student@example.com", "password": "strong-pwd12", "confirm_password": "strong-pwd12", "accept_terms": True})
    csrf = client.cookies.get("cm_csrf")
    response = client.patch("/api/v1/admin/settings/navigation", json={"items": []}, headers={"X-CSRF-Token": csrf})
    assert response.status_code == 403


def test_admin_inventory_endpoints_use_existing_domain_records(client):
    admin_login(client)
    users = client.get("/api/v1/admin/users")
    projects = client.get("/api/v1/admin/projects")
    roadmaps = client.get("/api/v1/admin/roadmaps")
    assert users.status_code == 200
    assert users.json()["items"][0]["role"] == "platform_admin"
    assert projects.status_code == 200
    assert roadmaps.status_code == 200
