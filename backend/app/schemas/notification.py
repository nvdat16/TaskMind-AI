from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.schemas.common import AppBaseSchema

NotificationChannel = Literal["in_app", "email", "telegram"]
NotificationType = Literal["reminder", "summary", "weekly_review"]
NotificationStatus = Literal["pending", "sent", "failed", "cancelled"]


class NotificationBase(AppBaseSchema):
    channel: NotificationChannel = "in_app"
    notification_type: NotificationType
    scheduled_at: datetime
    sent_at: datetime | None = None
    status: NotificationStatus = "pending"
    payload: dict | None = None


class NotificationCreate(NotificationBase):
    task_id: UUID | None = None


class NotificationResponse(NotificationBase):
    id: UUID
    user_id: UUID
    task_id: UUID | None = None
    created_at: datetime
