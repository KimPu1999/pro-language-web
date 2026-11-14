from datetime import datetime, timezone
from app.auth import password_hasher
from app.models import Challenge, GamificationXPLedger, StudentChallengeProgress, User

def student(client,email="gamification-student@example.com"):
    r=client.post("/api/v1/auth/register",json={"full_name":"Gamification Student","email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True});assert r.status_code in {201,400}
    with client.session_factory() as db:
        u=db.query(User).filter(User.email_normalized==email).one();u.email_verified_at=datetime.now(timezone.utc);db.commit()
    client.post("/api/v1/auth/login",json={"email":email,"password":"strong-pwd12"});return client.cookies.get("cm_csrf")
def admin(client,email="gamification-admin@example.com"):
    with client.session_factory() as db:db.add(User(email=email,email_normalized=email,password_hash=password_hasher.hash("Admin-pass12"),display_name="Gamification Admin",role="platform_admin",account_status="active",email_verified_at=datetime.now(timezone.utc)));db.commit()
    client.post("/api/v1/auth/login",json={"email":email,"password":"Admin-pass12"});return client.cookies.get("cm_csrf")
def test_quest_requires_verified_evidence_and_awards_once(client):
    admin_csrf=admin(client);student_email="quest-owner@example.com";client.post("/api/v1/auth/logout");student_csrf=student(client,student_email)
    with client.session_factory() as db:
        owner=db.query(User).filter(User.email_normalized==student_email).one();challenge=Challenge(title="Verified Challenge",slug="verified-challenge",description_en="Solve",difficulty="easy",published=True,status="published");db.add(challenge);db.flush();challenge_id=challenge.id;owner_id=owner.id
    client.post("/api/v1/auth/logout");admin_csrf=admin(client,"gamification-admin-2@example.com")
    quest=client.post("/api/v1/gamification-network/admin/quests",json={"slug":"solve-verified","title":"Solve verified","description":"Solve one","quest_type":"daily","rule_type":"challenge_solved","rule":{"challenge_id":str(challenge_id)},"xp_reward":25},headers={"X-CSRF-Token":admin_csrf});assert quest.status_code==201
    assigned=client.post(f"/api/v1/gamification-network/admin/quests/{quest.json()['id']}/assign/{owner_id}",headers={"X-CSRF-Token":admin_csrf});assert assigned.status_code==201
    client.post("/api/v1/auth/logout");student_csrf=student(client,student_email)
    assignment_id=assigned.json()["id"];assert client.post(f"/api/v1/gamification-network/quests/{assignment_id}/complete",headers={"X-CSRF-Token":student_csrf}).status_code==409
    with client.session_factory() as db:db.add(StudentChallengeProgress(user_id=owner_id,challenge_id=challenge_id,solved=True,solved_at=datetime.now(timezone.utc)));db.commit()
    first=client.post(f"/api/v1/gamification-network/quests/{assignment_id}/complete",headers={"X-CSRF-Token":student_csrf});second=client.post(f"/api/v1/gamification-network/quests/{assignment_id}/complete",headers={"X-CSRF-Token":student_csrf});assert first.status_code==200 and first.json()["xp_awarded"]==25;assert second.status_code==200 and second.json()["status"]=="already_completed"
    with client.session_factory() as db:assert db.query(GamificationXPLedger).filter(GamificationXPLedger.user_id==owner_id).count()==1
def test_leaderboard_requires_opt_in_and_platform_analytics_is_protected(client):
    student(client,"leaderboard-private@example.com");assert client.get("/api/v1/gamification-network/platform/analytics").status_code==403
    assert client.get("/api/v1/gamification-network/leaderboards").status_code==200 and client.get("/api/v1/gamification-network/leaderboards").json()["items"]==[]
