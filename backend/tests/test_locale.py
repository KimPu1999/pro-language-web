from sqlalchemy import select

from app.models import User, UserProfile


def _register(client):
    return client.post("/api/v1/auth/register", json={"full_name": "Locale Student", "email": "locale@example.com", "password": "strong-pwd12", "confirm_password": "strong-pwd12", "accept_terms": True})


def test_locale_requires_authentication_and_supported_values(client):
    assert client.patch("/api/v1/me/locale", json={"language": "mm"}, headers={"X-CSRF-Token": ""}).status_code == 401
    _register(client)
    csrf = client.cookies.get("cm_csrf")
    assert client.patch("/api/v1/me/locale", json={"language": "fr"}, headers={"X-CSRF-Token": csrf}).status_code == 422


def test_locale_persists_without_replacing_profile_data(client):
    _register(client)
    csrf = client.cookies.get("cm_csrf")
    response = client.patch("/api/v1/me/locale", json={"language": "mm"}, headers={"X-CSRF-Token": csrf})
    assert response.status_code == 200
    assert response.json() == {"language": "my"}
    with client.session_factory() as db:
        user = db.scalar(select(User).where(User.email == "locale@example.com"))
        profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
        assert profile.preferred_language == "my"
        assert profile.show_myanmar is True
    assert client.get("/api/v1/me/profile").json()["profile"]["preferred_language"] == "my"
