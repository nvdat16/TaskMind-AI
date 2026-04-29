from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.api.v1 import auth as auth_api
from app.schemas.user import TokenResponse


def test_register_returns_created_user(client, monkeypatch) -> None:
    user = SimpleNamespace(
        id=uuid4(),
        email="user@example.com",
        full_name="Test User",
        timezone="Asia/Ho_Chi_Minh",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    monkeypatch.setattr(auth_api.AuthService, "register_user", lambda db, payload: user)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "password123",
            "full_name": "Test User",
            "timezone": "Asia/Ho_Chi_Minh",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "user@example.com"
    assert body["full_name"] == "Test User"
    assert "password_hash" not in body


def test_login_returns_access_token(client, monkeypatch) -> None:
    monkeypatch.setattr(
        auth_api.AuthService,
        "login",
        lambda db, payload: TokenResponse(access_token="test-token"),
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json() == {"access_token": "test-token", "token_type": "bearer"}
