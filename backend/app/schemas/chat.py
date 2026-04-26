from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.schemas.common import AppBaseSchema
from app.schemas.task import TaskPriority

ChatRole = Literal["system", "user", "assistant"]
ChatIntent = Literal[
    "create_task",
    "update_task",
    "delete_task",
    "list_tasks",
    "plan_today",
    "daily_summary",
    "unknown",
]


class ParsedTaskData(AppBaseSchema):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    priority: TaskPriority | None = None
    due_at: datetime | None = None
    reminder_at: datetime | None = None


class ChatRequest(AppBaseSchema):
    message: str = Field(min_length=1)
    conversation_id: str | None = None


class ChatMessageResponse(AppBaseSchema):
    id: UUID
    user_id: UUID
    role: ChatRole
    message_text: str
    intent: ChatIntent | None = None
    structured_data: dict | None = None
    created_at: datetime


class ChatResponse(AppBaseSchema):
    reply: str
    intent: ChatIntent = "unknown"
    needs_confirmation: bool = False
    missing_fields: list[str] = []
    parsed_task: ParsedTaskData | None = None
