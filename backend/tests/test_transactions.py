from datetime import datetime, timezone

from app.auth import password_hasher
from app.models import User


def admin_login(client):
    with client.session_factory() as db:
        db.add(User(email="transactions-admin@example.com", email_normalized="transactions-admin@example.com", password_hash=password_hasher.hash("admin-pass-123"), display_name="Transactions Admin", role="platform_admin", account_status="active", email_verified_at=datetime.now(timezone.utc)))
        db.commit()
    assert client.post("/api/v1/admin/auth/login", json={"email": "transactions-admin@example.com", "password": "admin-pass-123"}).status_code == 200


def test_transactions_requires_authorization_and_reports_unconfigured_billing(client):
    assert client.get("/api/v1/admin/transactions").status_code in {401, 403}
    admin_login(client)
    response = client.get("/api/v1/admin/transactions?search=student&status=pending&page=2&page_size=10")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["configured"] is False
    assert payload["status"] == "not_configured"
    assert payload["data_source"] == "billing_provider_not_configured"
    assert payload["items"] == []
    assert payload["page"] == 2
    assert client.get("/api/v1/admin/transactions/00000000-0000-0000-0000-000000000000").status_code == 404
