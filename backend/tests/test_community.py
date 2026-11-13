from datetime import datetime, timezone
from sqlalchemy import select
from app.models import User
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
