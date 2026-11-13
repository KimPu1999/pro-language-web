from app.models import Challenge, ChallengeLanguageConfig, ChallengeTestCase
from datetime import datetime, timezone
from sqlalchemy import select
from app.models import User
def verified_client(client,email):
    response=client.post("/api/v1/auth/register",json={"full_name":"Challenge Student","email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True}); assert response.status_code==201
    with client.session_factory() as db:
        user=db.scalar(select(User).where(User.email==email)); user.email_verified_at=datetime.now(timezone.utc); db.commit()
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

def test_challenge_submission_rejects_invalid_language(client):
    challenge_id=make_challenge(client)
    response=client.post(f"/api/v1/challenges/{challenge_id}/submit",json={"language":"ruby","source_code":"puts 1"})
    assert response.status_code==401

def test_challenge_submission_uses_safe_runner_unavailable_state(client):
    challenge_id=make_challenge(client); csrf=verified_client(client,"challenge-student@example.com")
    response=client.post(f"/api/v1/challenges/{challenge_id}/submit",json={"language":"python","source_code":"print(3)"},headers={"X-CSRF-Token":csrf})
    assert response.status_code==202
    assert response.json()["status"]=="runner_unavailable"
