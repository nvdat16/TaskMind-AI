from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.schemas.common import AppBaseSchema

TaskPriority = Literal["low", "medium", "high", "urgent"]
TaskStatus = Literal["todo", "doing", "done", "snoozed", "cancelled"]
TaskSourceType = Literal["manual", "ai_chat", "import"]


class TaskBase(AppBaseSchema):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category: str = Field(default="general", min_length=1, max_length=50)
    priority: TaskPriority = "medium"
    status: TaskStatus = "todo"
    due_at: datetime | None = None
    estimated_minutes: int | None = Field(default=None, ge=1)
    reminder_at: datetime | None = None
    source_type: TaskSourceType = "manual"
    ai_metadata: dict | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(AppBaseSchema):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(default=None, min_length=1, max_length=50)
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    due_at: datetime | None = None
    estimated_minutes: int | None = Field(default=None, ge=1)
    reminder_at: datetime | None = None
    source_type: TaskSourceType | None = None
    ai_metadata: dict | None = None


class TaskResponse(TaskBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class TaskListResponse(AppBaseSchema):
    items: list[TaskResponse]
    total: int
