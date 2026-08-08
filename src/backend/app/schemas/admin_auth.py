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
