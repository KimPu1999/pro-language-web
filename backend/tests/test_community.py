from datetime import datetime, timezone
from sqlalchemy import select
from app.models import CommunityCategory, Course, User
def verified(client,email):
    r=client.post("/api/v1/auth/register",json={"full_name":"Community Student","email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True});assert r.status_code==201
    with client.session_factory() as db: u=db.scalar(select(User).where(User.email==email));u.email_verified_at=datetime.now(timezone.utc);db.commit()
    return client.cookies.get("cm_csrf")
def test_post_answer_accept_and_self_vote_rejected(client):
    token=verified(client,"community-owner@example.com");p=client.post("/api/v1/community/posts",json={"title":"How do loops work?","body":"Please explain loops.","post_type":"question"},headers={"X-CSRF-Token":token});assert p.status_code==201
    post=p.json();a=client.post(f"/api/v1/community/posts/{post['id']}/answers",json={"body":"They repeat a block."},headers={"X-CSRF-Token":token});assert a.status_code==201
    assert client.post(f"/api/v1/community/posts/{post['id']}/accept/{a.json()['id']}",headers={"X-CSRF-Token":token}).status_code==200
    assert client.post(f"/api/v1/community/posts/{post['id']}/vote",headers={"X-CSRF-Token":token}).status_code==409
def test_public_feed_search_returns_only_published_public(client):
    token=verified(client,"community-search@example.com");client.post("/api/v1/community/posts",json={"title":"SQL joins","body":"A public explanation","post_type":"discussion"},headers={"X-CSRF-Token":token});r=client.get("/api/v1/community/feed?search=SQL");assert r.status_code==200;assert len(r.json()["items"])==1

def test_duplicate_titles_get_unique_slugs_and_context_is_returned(client):
    token=verified(client,"community-context@example.com")
    with client.session_factory() as db:
        category=CommunityCategory(name="Python",slug="python-community",description="Python discussions");db.add(category);db.commit();category_id=str(category.id)
        course=db.query(Course).filter_by(slug="python-foundations").one();module=course.modules[0];lesson=module.lessons[0];course_id,module_id,lesson_id=map(str,(course.id,module.id,lesson.id))
    body={"title":"Context question","body":"A complete question","post_type":"question","category_id":category_id,"course_id":course_id,"module_id":module_id,"lesson_id":lesson_id,"expected_behavior":"It should work","actual_behavior":"It does not"}
    first=client.post("/api/v1/community/posts",json=body,headers={"X-CSRF-Token":token});second=client.post("/api/v1/community/posts",json=body,headers={"X-CSRF-Token":token})
    assert first.status_code==201 and second.status_code==201 and first.json()["slug"]!=second.json()["slug"]
    assert first.json()["context"]["lesson_id"]==lesson_id and first.json()["category"]["slug"]=="python-community"
    revisions=client.get(f"/api/v1/community/posts/{first.json()['id']}/revisions")
    assert revisions.status_code==200 and revisions.json()[0]["revision_number"]==1
    filtered=client.get(f"/api/v1/community/posts?course_id={course_id}&status=unanswered")
    assert filtered.status_code==200 and filtered.json()["total"]==2

def test_report_review_hides_content_and_records_resolution(client):
    token=verified(client,"community-moderation@example.com")
    created=client.post("/api/v1/community/posts",json={"title":"Reportable post","body":"Please review this.","post_type":"discussion"},headers={"X-CSRF-Token":token});assert created.status_code==201
    post=created.json();report=client.post("/api/v1/community/reports",params={"target_type":"post","target_id":post["id"],"reason":"Unsafe link"},headers={"X-CSRF-Token":token});assert report.status_code==200
    with client.session_factory() as db:
        actor=db.query(User).filter_by(email="community-moderation@example.com").one();actor.role="platform_admin";db.commit()
    report_id=client.get("/api/v1/community/admin/reports?status=open").json()["items"][0]["id"]
    decision=client.patch(f"/api/v1/community/admin/reports/{report_id}",json={"status":"resolved","action":"hide","note":"Confirmed by review."},headers={"X-CSRF-Token":token});assert decision.status_code==200
    assert client.get(f"/api/v1/community/posts/{post['slug']}").status_code==404
