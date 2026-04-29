import asyncio

import pytest

from app.services import ai_service
from app.services.ai_service import AIService, AIServiceError


class MockResponse:
    def __init__(self, status_code: int, payload: dict, text: str = ""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self) -> dict:
        return self._payload


def test_parse_response_content_success() -> None:
    content = """
    {
      "reply": "Đã hiểu yêu cầu của bạn.",
      "intent": "create_task",
      "needs_confirmation": false,
      "missing_fields": [],
      "parsed_task": {
        "title": "lịch hẹn",
        "description": null,
        "category": "personal",
        "priority": "medium",
        "due_at": "2026-04-27T08:00:00+07:00",
        "reminder_at": null
      }
    }
    """

    result = AIService._parse_response_content(content)

    assert result.intent == "create_task"
    assert result.reply == "Đã hiểu yêu cầu của bạn."
    assert result.needs_confirmation is False
    assert result.parsed_task is not None
    assert result.parsed_task.title == "lịch hẹn"


def test_parse_response_content_invalid_json() -> None:
    with pytest.raises(AIServiceError, match="invalid JSON"):
        AIService._parse_response_content("not-json")


def test_build_headers_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ai_service.settings, "llm_api_key", "")

    with pytest.raises(AIServiceError, match="not configured"):
        AIService._build_headers()


def test_extract_task_from_message_success(monkeypatch: pytest.MonkeyPatch) -> None:
    async def mock_post(self, url, headers=None, json=None):
        assert url.endswith("/chat/completions")
        assert headers["Authorization"] == "Bearer test-key"
        assert json["model"] == ai_service.settings.llm_model
        return MockResponse(
            200,
            {
                "choices": [
                    {
                        "message": {
                            "content": """
                            {
                              "reply": "Tôi đã tạo nháp lịch hẹn cho bạn.",
                              "intent": "create_task",
                              "needs_confirmation": true,
                              "missing_fields": ["date"],
                              "parsed_task": {
                                "title": "lịch hẹn",
                                "description": null,
                                "category": "personal",
                                "priority": "medium",
                                "due_at": null,
                                "reminder_at": null
                              }
                            }
                            """
                        }
                    }
                ]
            },
        )

    monkeypatch.setattr(ai_service.settings, "llm_api_key", "test-key")
    monkeypatch.setattr(ai_service.httpx.AsyncClient, "post", mock_post)

    result = asyncio.run(AIService.extract_task_from_message("hãy tạo lịch hẹn vào 8h"))

    assert result.intent == "create_task"
    assert result.needs_confirmation is True
    assert result.missing_fields == ["date"]
    assert result.parsed_task is not None
    assert result.parsed_task.title == "lịch hẹn"


def test_extract_task_from_message_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    async def mock_post(self, url, headers=None, json=None):
        return MockResponse(401, {}, text="unauthorized")

    monkeypatch.setattr(ai_service.settings, "llm_api_key", "test-key")
    monkeypatch.setattr(ai_service.httpx.AsyncClient, "post", mock_post)

    with pytest.raises(AIServiceError, match="status 401"):
        asyncio.run(AIService.extract_task_from_message("test"))
