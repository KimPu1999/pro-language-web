from datetime import datetime, timezone
from sqlalchemy import select
from app.models import User
def verified_client(client,email="runner@example.com"):
    response=client.post("/api/v1/auth/register",json={"full_name":"Runner Student","email":email,"password":"strong-pass-123","confirm_password":"strong-pass-123","accept_terms":True}); assert response.status_code==201
    with client.session_factory() as db:
        user=db.scalar(select(User).where(User.email==email)); user.email_verified_at=datetime.now(timezone.utc); db.commit()
    return client.cookies.get("cm_csrf")
def test_runner_rejects_unsupported_and_oversized_source(client):
    csrf=verified_client(client)
    assert client.post("/api/v1/runner/execute",json={"language":"ruby","source_code":"puts 1"},headers={"X-CSRF-Token":csrf}).status_code==422
    assert client.post("/api/v1/runner/execute",json={"language":"python","source_code":"x"*100001},headers={"X-CSRF-Token":csrf}).status_code==413
def test_runner_creates_unavailable_job_without_execution(client):
    csrf=verified_client(client); response=client.post("/api/v1/runner/execute",json={"language":"python","source_code":"print(1)","idempotency_key":"job-1"},headers={"X-CSRF-Token":csrf}); assert response.status_code==202; body=response.json(); assert body["status"]=="runner_unavailable"; assert body["result"]["error_code"]=="RUNNER_UNAVAILABLE"; assert client.get(f"/api/v1/runner/jobs/{body['id']}").status_code==200
def test_runner_job_ownership_is_enforced(client):
    csrf=verified_client(client); response=client.post("/api/v1/runner/execute",json={"language":"python","source_code":"print(1)"},headers={"X-CSRF-Token":csrf}); job_id=response.json()["id"]
    client.post("/api/v1/auth/logout",headers={"X-CSRF-Token":csrf}); other_csrf=verified_client(client,"other-runner@example.com"); assert client.get(f"/api/v1/runner/jobs/{job_id}").status_code==404; assert other_csrf
