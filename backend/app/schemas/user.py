from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.common import AppBaseSchema


class UserBase(AppBaseSchema):
	email: EmailStr
	full_name: str = Field(min_length=1, max_length=255)
	timezone: str = Field(default="Asia/Ho_Chi_Minh", min_length=1, max_length=100)


class UserCreate(UserBase):
	password: str = Field(min_length=8, max_length=255)


class UserLogin(AppBaseSchema):
	email: EmailStr
	password: str = Field(min_length=8, max_length=255)


class UserUpdate(AppBaseSchema):
	full_name: str | None = Field(default=None, min_length=1, max_length=255)
	timezone: str | None = Field(default=None, min_length=1, max_length=100)


class UserResponse(UserBase):
	id: UUID
	created_at: datetime
	updated_at: datetime


class TokenResponse(AppBaseSchema):
	access_token: str
	token_type: str = "bearer"
