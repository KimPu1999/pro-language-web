from datetime import datetime, timezone

from app.auth import password_hasher
from app.models import User


def login(client, email: str, name: str):
    with client.session_factory() as db:
        db.add(User(email=email, email_normalized=email, password_hash=password_hasher.hash("draft-pass-123"), display_name=name, role="platform_admin", account_status="active", email_verified_at=datetime.now(timezone.utc)))
        db.commit()
    response = client.post("/api/v1/admin/auth/login", json={"email": email, "password": "draft-pass-123"})
    assert response.status_code == 200, response.text
    return response.cookies.get("cm_csrf") or client.cookies.get("cm_csrf")


def test_published_lesson_uses_separate_draft_until_review_publish(client):
    csrf = login(client, "draft-author@example.com", "Draft Author")
    course = client.get("/api/v1/admin/courses?page_size=1").json()["items"][0]
    curriculum = client.get(f"/api/v1/admin/courses/{course['id']}/curriculum")
    assert curriculum.status_code == 200
    lesson = curriculum.json()[0]["lessons"][0]
    original = client.get(f"/api/v1/admin/lessons/{lesson['id']}").json()

    empty = client.get(f"/api/v1/admin/lessons/{lesson['id']}/draft")
    assert empty.status_code == 200
    assert empty.json()["draft"] is None

    saved = client.put(
        f"/api/v1/admin/lessons/{lesson['id']}/draft",
        headers={"X-CSRF-Token": csrf},
        json={
            "title": original["title"],
            "slug": original["slug"],
            "description": original["description"],
            "content_en": "# reviewed draft\n\n## Exercises\nA bounded exercise.",
            "content_mm": "# ပြန်လည်စစ်ဆေးရန် draft\n\n## လေ့ကျင့်ခန်း\nလုံခြုံသော လေ့ကျင့်ခန်း။",
            "duration_minutes": original["duration_minutes"],
            "status": "draft",
        },
    )
    assert saved.status_code == 200, saved.text
    assert saved.json()["draft"]["status"] == "draft"
    assert saved.json()["published"]["content_en"] == original["content_en"]

    unchanged = client.get(f"/api/v1/admin/lessons/{lesson['id']}").json()
    assert unchanged["content_en"] == original["content_en"]
    assert unchanged["published"] is True

    submitted = client.post(f"/api/v1/admin/lessons/{lesson['id']}/draft/submit", headers={"X-CSRF-Token": csrf}, json={})
    assert submitted.status_code == 201, submitted.text
    review_id = submitted.json()["review_id"]

    reviewer_csrf = login(client, "draft-reviewer@example.com", "Draft Reviewer")
    started = client.post(f"/api/v1/platform/content-review/{review_id}/transition", headers={"X-CSRF-Token": reviewer_csrf}, json={"status": "in_review"})
    assert started.status_code == 200, started.text
    approved = client.post(f"/api/v1/platform/content-review/{review_id}/transition", headers={"X-CSRF-Token": reviewer_csrf}, json={"status": "approved"})
    assert approved.status_code == 200, approved.text
    published = client.post(f"/api/v1/platform/content-review/{review_id}/publish", headers={"X-CSRF-Token": reviewer_csrf})
    assert published.status_code == 200, published.text

    after = client.get(f"/api/v1/admin/lessons/{lesson['id']}").json()
    assert after["content_en"].startswith("# reviewed draft")
    assert after["published"] is True
