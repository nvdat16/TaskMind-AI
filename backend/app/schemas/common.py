from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class AppBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(AppBaseSchema):
    created_at: datetime
    updated_at: datetime | None = None


class MessageResponse(AppBaseSchema):
    message: str


class PaginatedResponse(AppBaseSchema, Generic[T]):
    items: list[T]
    total: int
