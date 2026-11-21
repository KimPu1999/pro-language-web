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


def test_footer_draft_stays_private_until_publish(client):
    public_default = client.get("/api/v1/site/footer")
    assert public_default.status_code == 200
    assert public_default.json()["status"] == "published"
    csrf = admin_login(client)
    draft = {
        "tagline": "Build your next skill.",
        "description": "A managed footer.",
        "groups": [{"id": "learn", "title": "Learn", "position": 0, "enabled": True, "links": [{"id": "courses", "label": "Courses", "href": "/courses", "position": 0, "enabled": True}]}],
        "social_links": [{"id": "github", "platform": "GitHub", "url": "https://github.com/learn-coding", "icon_key": "github", "position": 0, "enabled": True}],
        "newsletter_enabled": False,
        "newsletter_note": "Unavailable.",
        "copyright_text": "© Learn-Coding",
        "status": "draft",
    }
    saved = client.patch("/api/v1/admin/settings/footer", json=draft, headers={"X-CSRF-Token": csrf})
    assert saved.status_code == 200
    assert client.get("/api/v1/admin/settings/footer").json()["status"] == "draft"
    assert client.get("/api/v1/site/footer").json()["tagline"] != "Build your next skill."
    assert client.post("/api/v1/admin/settings/footer/publish", headers={"X-CSRF-Token": csrf}).status_code == 200
    published = client.get("/api/v1/site/footer")
    assert published.status_code == 200
    assert published.json()["tagline"] == "Build your next skill."
    invalid = {**draft, "groups": [{**draft["groups"][0], "links": [{**draft["groups"][0]["links"][0], "href": "/not-a-real-route"}]}]}
    assert client.patch("/api/v1/admin/settings/footer", json=invalid, headers={"X-CSRF-Token": csrf}).status_code == 422


def test_admin_inventory_endpoints_use_existing_domain_records(client):
    admin_login(client)
    users = client.get("/api/v1/admin/users")
    projects = client.get("/api/v1/admin/projects")
    roadmaps = client.get("/api/v1/admin/roadmaps")
    assert users.status_code == 200
    assert users.json()["items"][0]["role"] == "platform_admin"
    assert projects.status_code == 200
    assert roadmaps.status_code == 200


def test_course_catalog_exposes_real_curriculum_counts(client):
    from app.models import CourseModule, Lesson

    with client.session_factory() as db:
        module = db.scalar(select(CourseModule))
        db.add(Lesson(module_id=module.id, title="Private draft", slug="private-draft", content_en="Do not expose", order_index=2, published=False, status="draft"))
        db.commit()
    response = client.get("/api/v1/courses?page_size=1")
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["module_count"] == 1
    assert item["lesson_count"] == 1
    detail = client.get(f"/api/v1/courses/{item['slug']}")
    assert detail.status_code == 200
    assert detail.json()["modules"][0]["lessons"][0]["title"] == "Hello"
    assert all(lesson["title"] != "Private draft" for module in detail.json()["modules"] for lesson in module["lessons"])


def test_admin_course_stats_use_shared_records(client):
    admin_login(client)
    course_id = client.get("/api/v1/admin/courses?page_size=1").json()["items"][0]["id"]
    response = client.get(f"/api/v1/admin/courses/{course_id}/stats")
    assert response.status_code == 200
    assert response.json()["module_count"] == 1
    assert response.json()["lesson_count"] == 1


def test_course_detail_faq_workflow_keeps_drafts_private(client):
    csrf = admin_login(client)
    course_id = client.get("/api/v1/admin/courses?page_size=1").json()["items"][0]["id"]
    created = client.post(
        f"/api/v1/admin/courses/{course_id}/faqs",
        json={"question": "Who is this for?", "answer": "Learners building a foundation.", "position": 0, "status": "published"},
        headers={"X-CSRF-Token": csrf},
    )
    assert created.status_code == 201
    public = client.get("/api/v1/courses/python-foundations")
    assert public.status_code == 200
    assert public.json()["faqs"][0]["question"] == "Who is this for?"
    updated = client.patch(
        f"/api/v1/admin/faqs/{created.json()['id']}",
        json={"question": "Who is this for?", "answer": "Private answer.", "position": 0, "status": "draft"},
        headers={"X-CSRF-Token": csrf},
    )
    assert updated.status_code == 200
    assert client.get("/api/v1/courses/python-foundations").json()["faqs"] == []
