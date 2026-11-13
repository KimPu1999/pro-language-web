def login_student(client,email="security@example.com"):
    result=client.post("/api/v1/auth/register",json={"full_name":"Security Student","email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True})
    assert result.status_code==201
    from datetime import datetime, timezone
    from app.models import User
    with client.session_factory() as db:
        db.get(User,result.json()["id"]).email_verified_at=datetime.now(timezone.utc);db.commit()
    client.post("/api/v1/auth/login",json={"email":email,"password":"strong-pwd12"})
    return client.cookies.get("cm_csrf")

def test_security_dashboard_reports_unconfigured_providers(client):
    login_student(client)
    status=client.get("/api/v1/settings/security/mfa")
    assert status.status_code==200 and status.json()["status"]=="Not Configured"
    assert client.get("/api/v1/organizations/example/security").status_code==403

def test_mfa_does_not_generate_secrets_when_unconfigured(client):
    csrf=login_student(client,"mfa@example.com")
    response=client.post("/api/v1/settings/security/mfa/enroll",headers={"X-CSRF-Token":csrf})
    assert response.status_code==503
    assert "Not Configured" in response.json()["detail"]

def test_scim_is_unavailable_without_configuration(client):
    response=client.get("/api/v1/scim/v2/organizations/00000000-0000-0000-0000-000000000000/Users",headers={"Authorization":"Bearer test-token"})
    assert response.status_code==503

def test_privacy_requests_are_authenticated_and_owned(client):
    assert client.get("/api/v1/privacy/requests").status_code==401
    csrf=login_student(client,"privacy@example.com")
    response=client.post("/api/v1/privacy/requests",json={"request_type":"export"},headers={"X-CSRF-Token":csrf})
    assert response.status_code==201
    assert client.get("/api/v1/privacy/requests").json()[0]["request_type"]=="export"

def test_compliance_is_platform_admin_only(client):
    assert client.get("/api/v1/platform/compliance").status_code==401
    login_student(client,"compliance@example.com")
    assert client.get("/api/v1/platform/compliance").status_code==403
