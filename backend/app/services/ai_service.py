from __future__ import annotations

import json
from typing import Any

import httpx

from app.core.config import get_settings
from app.schemas.chat import ChatResponse, ParsedTaskData

settings = get_settings()


class AIServiceError(Exception):
    pass


class AIService:
    @staticmethod
    def _build_headers() -> dict[str, str]:
        if not settings.llm_api_key:
            raise AIServiceError("LLM_API_KEY is not configured")

        return {
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _build_task_extraction_prompt(message: str) -> str:
        return f"""
You are an AI assistant for a personal task manager.
Extract the user's intent and task details from the message.
Return valid JSON only with this exact shape:
{{
  "reply": "short Vietnamese reply",
  "intent": "create_task|update_task|delete_task|list_tasks|plan_today|daily_summary|unknown",
  "needs_confirmation": true,
  "missing_fields": ["field_name"],
  "parsed_task": {{
    "title": "string or null",
    "description": "string or null",
    "category": "string or null",
    "priority": "low|medium|high|urgent|null",
    "due_at": "ISO datetime string or null",
    "reminder_at": "ISO datetime string or null"
  }}
}}

Rules:
- Reply in Vietnamese.
- If time/date is ambiguous, set needs_confirmation=true.
- If no task can be extracted, set intent="unknown".
- Do not include markdown fences.

User message: {message}
""".strip()

    @classmethod
    def _parse_response_content(cls, content: str) -> ChatResponse:
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise AIServiceError("LLM returned invalid JSON") from exc

        parsed_task_raw = payload.get("parsed_task")
        parsed_task = (
            ParsedTaskData.model_validate(parsed_task_raw) if parsed_task_raw else None
        )

        return ChatResponse(
            reply=payload.get("reply", "Tôi chưa hiểu yêu cầu của bạn."),
            intent=payload.get("intent", "unknown"),
            needs_confirmation=payload.get("needs_confirmation", False),
            missing_fields=payload.get("missing_fields", []),
            parsed_task=parsed_task,
        )

    @classmethod
    async def extract_task_from_message(cls, message: str) -> ChatResponse:
        prompt = cls._build_task_extraction_prompt(message)
        request_body: dict[str, Any] = {
            "model": settings.llm_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a precise information extraction assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }

        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            response = await client.post(
                f"{settings.llm_base_url}/chat/completions",
                headers=cls._build_headers(),
                json=request_body,
            )

        if response.status_code >= 400:
            raise AIServiceError(
                f"LLM request failed with status {response.status_code}: {response.text}"
            )

        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIServiceError("Unexpected LLM response structure") from exc

        return cls._parse_response_content(content)
