from __future__ import annotations

import json
import re
from typing import Any

from pydantic import ValidationError

from app.schemas.chat import ChatResponse, ParsedTaskData
from app.services.ai_errors import AIServiceError


def _extract_json_candidate(content: str) -> str:
    stripped = content.strip()

    fenced_match = re.search(r"```(?:json)?\s*(.*?)\s*```", stripped, re.DOTALL | re.IGNORECASE)
    if fenced_match:
        return fenced_match.group(1).strip()

    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        return stripped[start : end + 1]

    return stripped


def parse_chat_response(content: str) -> ChatResponse:
    candidate = _extract_json_candidate(content)

    try:
        payload: dict[str, Any] = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise AIServiceError("LLM returned invalid JSON") from exc

    parsed_task_raw = payload.get("parsed_task")
    parsed_task: ParsedTaskData | None = None
    if parsed_task_raw:
        try:
            parsed_task = ParsedTaskData.model_validate(parsed_task_raw)
        except ValidationError as exc:
            raise AIServiceError("LLM returned invalid parsed_task payload") from exc

    missing_fields = payload.get("missing_fields") or []
    if not isinstance(missing_fields, list):
        missing_fields = [str(missing_fields)]

    return ChatResponse(
        reply=payload.get("reply", "Tôi chưa hiểu yêu cầu của bạn."),
        intent=payload.get("intent", "unknown"),
        needs_confirmation=bool(payload.get("needs_confirmation", False)),
        missing_fields=[str(field) for field in missing_fields],
        parsed_task=parsed_task,
    )
