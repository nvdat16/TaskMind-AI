from types import SimpleNamespace
from uuid import uuid4

from app.api import deps
from app.api.v1 import chat as chat_api
from app.main import app


def test_chat_endpoint_returns_ai_response(client, monkeypatch) -> None:
    current_user = SimpleNamespace(id=uuid4())

    async def mock_process_chat_message(db, user, message, conversation_id=None):
        return SimpleNamespace(
            reply="Đã nhận tin nhắn.",
            intent="unknown",
            needs_confirmation=False,
            missing_fields=[],
            parsed_task=None,
        )

    app.dependency_overrides[deps.get_current_user] = lambda: current_user
    monkeypatch.setattr(chat_api.AIService, "process_chat_message", mock_process_chat_message)

    response = client.post(
        "/api/v1/chat",
        json={"message": "Xin chào", "conversation_id": "conv-1"},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["reply"] == "Đã nhận tin nhắn."
