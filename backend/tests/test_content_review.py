from datetime import datetime, timezone

from app.auth import password_hasher
from app.models import User


def admin_login(client, email: str, display_name: str):
    with client.session_factory() as db:
        db.add(User(email=email, email_normalized=email, password_hash=password_hasher.hash("review-pass-123"), display_name=display_name, role="platform_admin", account_status="active", email_verified_at=datetime.now(timezone.utc)))
        db.commit()
    response = client.post("/api/v1/admin/auth/login", json={"email": email, "password": "review-pass-123"})
    assert response.status_code == 200, response.text
    return response.cookies.get("cm_csrf") or client.cookies.get("cm_csrf")


def test_platform_content_review_uses_global_scope_and_enforces_workflow(client):
    response = client.get("/api/v1/platform/content-review/dashboard")
    assert response.status_code == 401

    admin_csrf = admin_login(client, "content-review-admin@example.com", "Review Admin")
    course_id = client.get("/api/v1/admin/courses?page_size=1").json()["items"][0]["id"]

    submitted = client.post("/api/v1/platform/content-review/submit", json={"content_type": "course", "content_key": course_id}, headers={"X-CSRF-Token": admin_csrf})
    assert submitted.status_code == 201, submitted.text
    review = submitted.json()
    assert review["organization"] is None
    assert review["status"] == "submitted"

    queue = client.get("/api/v1/platform/content-review/queue?status=submitted")
    assert queue.status_code == 200
    assert any(item["id"] == review["id"] for item in queue.json()["items"])

    reviewer_csrf = admin_login(client, "content-review-reviewer@example.com", "Independent Reviewer")
    reviewers = client.get("/api/v1/platform/content-review/reviewers").json()
    reviewer_id = next(item["id"] for item in reviewers if item["email"] == "content-review-reviewer@example.com")
    assigned = client.patch(f"/api/v1/platform/content-review/{review['id']}/assignment", json={"reviewer_id": reviewer_id}, headers={"X-CSRF-Token": reviewer_csrf})
    assert assigned.status_code == 200, assigned.text

    started = client.post(f"/api/v1/platform/content-review/{review['id']}/transition", json={"status": "in_review"}, headers={"X-CSRF-Token": reviewer_csrf})
    assert started.status_code == 200, started.text
    needs_reason = client.post(f"/api/v1/platform/content-review/{review['id']}/transition", json={"status": "rejected"}, headers={"X-CSRF-Token": reviewer_csrf})
    assert needs_reason.status_code == 422
    approved = client.post(f"/api/v1/platform/content-review/{review['id']}/transition", json={"status": "approved"}, headers={"X-CSRF-Token": reviewer_csrf})
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "approved"

    published = client.post(f"/api/v1/platform/content-review/{review['id']}/publish", headers={"X-CSRF-Token": reviewer_csrf})
    assert published.status_code == 200, published.text
    assert published.json()["status"] == "published"

    detail = client.get(f"/api/v1/platform/content-review/{review['id']}")
    assert detail.status_code == 200
    assert detail.json()["preview"]["title"] == "Python Foundations"
    assert [event["to_status"] for event in detail.json()["history"]] == ["submitted", "in_review", "approved", "published"]
