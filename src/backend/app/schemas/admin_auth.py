from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.admin_users import AdminUserRead


class AdminLoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)
    remember_me: bool = False


class AdminLoginResult(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: str
    user: AdminUserRead


class AdminSessionUser(BaseModel):
    user: AdminUserRead


class AdminProfileUpdateRequest(BaseModel):
    nickname: str | None = Field(default=None, max_length=128)
    avatar_url: str | None = Field(default=None, max_length=512)


class AdminPasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=8, max_length=256)
    confirm_password: str = Field(min_length=8, max_length=256)


class AdminPasswordChangeResult(BaseModel):
    status: str = "done"
    message: str
