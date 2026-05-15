from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import get_settings
from app.models.chat_message import ChatMessage
from app.models.user import User
from app.schemas.chat import ChatResponse
from app.services.ai_action_mapper import AIActionMapper
from app.services.ai_errors import AIServiceError
from app.services.ai_parser import parse_chat_response
from app.services.ai_prompts import AIPromptTemplates

settings = get_settings()
logger = logging.getLogger(__name__)


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
    def _build_task_extraction_messages(message: str) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": AIPromptTemplates.task_extraction_system_prompt(),
            },
            {
                "role": "user",
                "content": AIPromptTemplates.task_extraction_user_prompt(message),
            },
        ]

    @classmethod
    def _parse_response_content(cls, content: str) -> ChatResponse:
        return parse_chat_response(content)

    @classmethod
    async def extract_task_from_message(cls, message: str) -> ChatResponse:
        messages = cls._build_task_extraction_messages(message)
        request_body: dict[str, Any] = {
            "model": settings.llm_model,
            "messages": messages,
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

    @classmethod
    async def process_chat_message(
        cls,
        db,
        user: User,
        message: str,
        conversation_id: str | None = None,
    ) -> ChatResponse:
        user_message = ChatMessage(
            user_id=user.id,
            role="user",
            message_text=message,
            intent=None,
            structured_data={"conversation_id": conversation_id},
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)

        extracted = await cls.extract_task_from_message(message)
        action_result = AIActionMapper.execute(db=db, user=user, response=extracted)

        assistant_message = ChatMessage(
            user_id=user.id,
            role="assistant",
            message_text=action_result.response.reply,
            intent=action_result.response.intent,
            structured_data={
                "conversation_id": conversation_id,
                "extracted": extracted.model_dump(mode="json"),
                "action_name": action_result.action_name,
                "action_metadata": action_result.metadata,
                "task_id": str(action_result.task.id) if action_result.task else None,
            },
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)

        logger.info(
            "AI chat processed user_id=%s intent=%s action=%s task_id=%s",
            user.id,
            extracted.intent,
            action_result.action_name,
            action_result.task.id if action_result.task else None,
        )

        return action_result.response
