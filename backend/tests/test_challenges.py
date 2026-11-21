from app.models import Challenge, ChallengeLanguageConfig, ChallengeTestCase
from datetime import datetime, timezone
from sqlalchemy import select
from app.models import User
from app.auth import password_hasher
def verified_client(client,email):
    response=client.post("/api/v1/auth/register",json={"full_name":"Challenge Student","email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True}); assert response.status_code==201
    with client.session_factory() as db:
        user=db.scalar(select(User).where(User.email==email)); user.email_verified_at=datetime.now(timezone.utc); db.commit()
    return client.cookies.get("cm_csrf")

def admin_client(client, email="challenge-admin@example.com", role="admin"):
    with client.session_factory() as db:
        db.add(User(email=email,email_normalized=email,password_hash=password_hasher.hash("admin-pass-123"),display_name="Challenge Admin",role=role,account_status="active",email_verified_at=datetime.now(timezone.utc))); db.commit()
    response=client.post("/api/v1/auth/login",json={"email":email,"password":"admin-pass-123"}); assert response.status_code==200
    return client.cookies.get("cm_csrf")

def make_challenge(client):
    with client.session_factory() as db:
        challenge=Challenge(title="Two Sum",slug="two-sum",description_en="Find two values.",difficulty="beginner",status="published",published=True)
        db.add(challenge); db.flush(); db.add(ChallengeLanguageConfig(challenge_id=challenge.id,language="python",starter_code="")); db.add(ChallengeTestCase(challenge_id=challenge.id,input_data="1 2",expected_output="3",is_hidden=False)); db.add(ChallengeTestCase(challenge_id=challenge.id,input_data="9 9",expected_output="18",is_hidden=True)); db.commit(); return challenge.id

def test_published_challenge_hides_hidden_tests_and_lists(client):
    challenge_id=make_challenge(client)
    assert client.get("/api/v1/challenges").json()["total"]==1
    detail=client.get("/api/v1/challenges/two-sum").json()
    assert len(detail["public_tests"])==1
    assert "9 9" not in str(detail)
    assert str(challenge_id) == detail["id"]

def test_catalog_filters_and_static_routes_are_reachable(client):
    make_challenge(client)
    assert client.get("/api/v1/challenge-categories").status_code == 200
    filtered=client.get("/api/v1/challenges?language=python&difficulty=beginner").json()
    assert filtered["total"] == 1
    assert client.get("/api/v1/challenges/submissions/history").status_code == 401
    assert client.get("/api/v1/challenges/skills/me").status_code == 401
    assert client.get("/api/v1/me/challenge-progress").status_code == 401

def test_challenge_submission_rejects_invalid_language(client):
    challenge_id=make_challenge(client)
    response=client.post(f"/api/v1/challenges/{challenge_id}/submit",json={"language":"ruby","source_code":"puts 1"})
    assert response.status_code==401

def test_challenge_submission_uses_safe_runner_unavailable_state(client):
    challenge_id=make_challenge(client); csrf=verified_client(client,"challenge-student@example.com")
    response=client.post(f"/api/v1/challenges/{challenge_id}/submit",json={"language":"python","source_code":"print(3)"},headers={"X-CSRF-Token":csrf})
    assert response.status_code==202
    assert response.json()["status"]=="runner_unavailable"

def test_admin_challenge_wizard_crud_publish_and_public_answer_contract(client):
    csrf=admin_client(client)
    create=client.post("/api/v1/challenges/admin",json={"title":"HTTP Status Quiz","slug":"http-status-quiz","description_en":"Choose the successful response.","challenge_type":"quiz","quiz_mode":"single","quiz_options":["200","404"],"quiz_correct_answer":"200","quiz_explanation":"200 means success."},headers={"X-CSRF-Token":csrf})
    assert create.status_code==201, create.text; challenge_id=create.json()["id"]
    assert client.get(f"/api/v1/challenges/admin/{challenge_id}").status_code==200
    patch=client.patch(f"/api/v1/challenges/admin/{challenge_id}",json={"description_en":"Updated question."},headers={"X-CSRF-Token":csrf}); assert patch.status_code==200
    assert client.get(f"/api/v1/challenges/{challenge_id}").status_code==404
    published=client.post(f"/api/v1/challenges/admin/{challenge_id}/publish",headers={"X-CSRF-Token":csrf}); assert published.status_code==200, published.text
    public=client.get("/api/v1/challenges/http-status-quiz"); assert public.status_code==200; body=public.json(); assert body["quiz_options"]==["200","404"]; assert "quiz_correct_answer" not in body; assert "quiz_explanation" not in body
    answer=client.post(f"/api/v1/challenges/{challenge_id}/answer",json={"answer":"200"},headers={"X-CSRF-Token":csrf}); assert answer.status_code==201; assert answer.json()["score"]==100

def test_admin_can_save_an_incomplete_blank_challenge_draft(client):
    csrf=admin_client(client,"blank-challenge-admin@example.com")
    response=client.post("/api/v1/challenges/admin",json={"title":"","slug":None,"challenge_type":"coding"},headers={"X-CSRF-Token":csrf})
    assert response.status_code==201, response.text
    assert response.json()["status"]=="draft" and response.json()["published"] is False

def test_admin_reorder_is_persisted(client):
    csrf=admin_client(client,"reorder-admin@example.com")
    first=client.post("/api/v1/challenges/admin",json={"title":"Order one","slug":"order-one"},headers={"X-CSRF-Token":csrf}).json()["id"]
    second=client.post("/api/v1/challenges/admin",json={"title":"Order two","slug":"order-two"},headers={"X-CSRF-Token":csrf}).json()["id"]
    reordered=client.post("/api/v1/challenges/admin/reorder",json={"ids":[second,first]},headers={"X-CSRF-Token":csrf}); assert reordered.status_code==200
    positions={str(item["id"]):item["position"] for item in client.get("/api/v1/challenges/admin/reorder").json()}; assert positions[second]==0 and positions[first]==1

def test_admin_coding_challenge_draft_validation_and_hidden_test_privacy(client):
    csrf=admin_client(client,"coding-admin@example.com")
    create=client.post("/api/v1/challenges/admin",json={"title":"Draft Coding","slug":"draft-coding","description_en":"Add two numbers.","challenge_type":"coding"},headers={"X-CSRF-Token":csrf}); assert create.status_code==201, create.text; challenge_id=create.json()["id"]
    language=client.post(f"/api/v1/challenges/admin/{challenge_id}/languages",json={"language":"python","starter_code":""},headers={"X-CSRF-Token":csrf}); assert language.status_code==201
    test=client.post(f"/api/v1/challenges/admin/{challenge_id}/tests",json={"input_data":"1 2","expected_output":"3","is_hidden":True},headers={"X-CSRF-Token":csrf}); assert test.status_code==201
    blocked=client.post(f"/api/v1/challenges/admin/{challenge_id}/publish",headers={"X-CSRF-Token":csrf}); assert blocked.status_code==200, blocked.text
    assert client.get("/api/v1/challenges/draft-coding").status_code==200
    detail=client.get("/api/v1/challenges/draft-coding").json(); assert detail["public_tests"]==[]; assert "reference_solution" not in detail
    assert client.get(f"/api/v1/challenges/admin/{challenge_id}/submissions").status_code==404
    assert client.get(f"/api/v1/challenges/admin/{challenge_id}").json()["tests"][0]["is_hidden"] is True
