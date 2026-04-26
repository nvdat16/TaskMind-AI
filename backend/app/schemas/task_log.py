from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.common import AppBaseSchema


class TaskLogResponse(AppBaseSchema):
    id: UUID
    task_id: UUID
    action_type: str = Field(min_length=1, max_length=50)
    old_value: dict | None = None
    new_value: dict | None = None
    created_at: datetime
