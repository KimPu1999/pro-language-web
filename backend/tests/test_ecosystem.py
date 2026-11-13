def register_and_login(client, email="ecosystem@example.com"):
    result=client.post("/api/v1/auth/register",json={"full_name":"Ecosystem Student","email":email,"password":"strong-pwd12","confirm_password":"strong-pwd12","accept_terms":True})
    assert result.status_code==201
    login=client.post("/api/v1/auth/login",json={"email":email,"password":"strong-pwd12"})
    assert login.status_code==200
    return client.cookies.get("cm_csrf")

def test_github_is_truthfully_unavailable_without_credentials(client):
    register_and_login(client)
    response=client.get("/api/v1/github/status")
    assert response.status_code==200
    body=response.json()
    assert body["enabled"] is False
    assert body["connected"] is False
    assert "Not Configured" in body["message"]

def test_public_ecosystem_lists_only_approved_records(client):
    assert client.get("/api/v1/open-source/projects").status_code==200
    assert client.get("/api/v1/open-source/opportunities").json()==[]

def test_webhook_requires_provider_configuration(client):
    response=client.post("/api/v1/github/webhooks",content=b"{}",headers={"X-GitHub-Delivery":"delivery-1","X-Hub-Signature-256":"sha256.invalid"})
    assert response.status_code==503

def test_webhook_signature_and_delivery_deduplication(client,monkeypatch):
    import hashlib,hmac
    from app.config import settings
    secret="phase19-test-secret"; monkeypatch.setattr(settings,"github_webhook_secret",secret)
    body=b'{"action":"opened"}'; signature="sha256="+hmac.new(secret.encode(),body,hashlib.sha256).hexdigest()
    headers={"X-GitHub-Delivery":"delivery-verified","X-GitHub-Event":"issues","X-Hub-Signature-256":signature}
    first=client.post("/api/v1/github/webhooks",content=body,headers=headers); second=client.post("/api/v1/github/webhooks",content=body,headers=headers)
    assert first.status_code==200 and first.json()["status"]=="accepted"
    assert second.status_code==200 and second.json()["status"]=="duplicate_acknowledged"

def test_private_profile_is_not_publicly_readable(client):
    register_and_login(client,"private-profile@example.com")
    response=client.get("/api/v1/developers/private-user")
    assert response.status_code==404
