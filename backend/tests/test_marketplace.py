from datetime import datetime, timezone

from app.auth import password_hasher
from app.models import User


def login(client, email: str, role: str):
    with client.session_factory() as db:
        db.add(User(email=email, email_normalized=email, password_hash=password_hasher.hash("Market-pass"), display_name=email.split("@")[0], role=role, account_status="active", email_verified_at=datetime.now(timezone.utc)))
        db.commit()
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "Market-pass"})
    assert response.status_code == 200
    return client.cookies.get("cm_csrf")


def resource_payload():
    return {"title": "Safe Python Guide", "summary": "A reviewed guide", "content_markdown": "# Safe Python\nUse validation.", "resource_type": "tutorial", "license_code": "CC-BY-4.0", "attribution": "Original work", "tags": ["python"]}


def test_public_marketplace_excludes_drafts(client):
    response = client.get("/api/v1/marketplace")
    assert response.status_code == 200
    assert response.json()["resources"] == []
    search = client.get("/api/v1/marketplace/search?q=secret")
    assert search.status_code == 200
    assert search.json()["items"] == []


def test_contributor_can_create_but_not_publish(client):
    csrf = login(client, "contributor@example.com", "instructor")
    created = client.post("/api/v1/marketplace/resources", json=resource_payload(), headers={"X-CSRF-Token": csrf})
    assert created.status_code == 201
    assert created.json()["status"] == "draft"
    assert client.get(f"/api/v1/marketplace/resources/{created.json()['slug']}").status_code == 404


def test_moderator_review_publishes_resource(client):
    csrf = login(client, "author@example.com", "instructor")
    created = client.post("/api/v1/marketplace/resources", json=resource_payload(), headers={"X-CSRF-Token": csrf}).json()
    submitted = client.post(f"/api/v1/marketplace/resources/{created['id']}/submit", headers={"X-CSRF-Token": csrf})
    assert submitted.status_code == 202
    admin_csrf = login(client, "moderator@example.com", "platform_admin")
    queue = client.get("/api/v1/marketplace/moderation/queue")
    assert queue.status_code == 200
    request_id = queue.json()["reviews"][0]["id"]
    decision = client.post(f"/api/v1/marketplace/moderation/reviews/{request_id}", json={"decision": "approved", "note": "Reviewed"}, headers={"X-CSRF-Token": admin_csrf})
    assert decision.status_code == 200
    assert client.get(f"/api/v1/marketplace/resources/{created['slug']}").status_code == 200


def test_student_cannot_contribute_or_moderate(client):
    csrf = login(client, "student-market@example.com", "student")
    assert client.post("/api/v1/marketplace/resources", json=resource_payload(), headers={"X-CSRF-Token": csrf}).status_code == 403
    assert client.get("/api/v1/marketplace/moderation/queue").status_code == 403


def test_review_requires_published_resource_and_self_review_is_blocked(client):
    csrf = login(client, "review-student@example.com", "student")
    assert client.post("/api/v1/marketplace/resources/00000000-0000-0000-0000-000000000000/reviews", json={"rating": 5}, headers={"X-CSRF-Token": csrf}).status_code == 404
