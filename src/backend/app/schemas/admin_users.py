from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

AdminUserRole = Literal["后台管理员", "前台用户"]
AdminUserStatus = Literal["待激活", "正常", "已冻结", "已删除"]


class AdminUserRead(BaseModel):
    id: str
    username: str
    nickname: str | None = None
    avatar_url: str | None = None
    role: AdminUserRole
    status: AdminUserStatus
    status_before_freeze: AdminUserStatus | None = None
    workspace_count: int
    last_login_at: str | None = None
    is_system_superadmin: bool
    deleted_at: str | None = None
    session_invalidated_at: str | None = None
    created_at: str
    updated_at: str


class AdminUserCreate(BaseModel):
    username: str = Field(min_length=4, max_length=32, pattern=r"^[A-Za-z][A-Za-z0-9]{3,31}$")
    nickname: str | None = Field(default=None, max_length=128)
    avatar_url: str | None = Field(default=None, max_length=512)
    role: AdminUserRole


class AdminUserUpdate(BaseModel):
    nickname: str | None = Field(default=None, max_length=128)
    avatar_url: str | None = Field(default=None, max_length=512)
    role: AdminUserRole


class AdminUserAction(BaseModel):
    reason: str = Field(min_length=4, max_length=512)


class AdminPasswordResetResult(BaseModel):
    temporary_password: str
    message: str


class AdminUserCreateResult(BaseModel):
    user: AdminUserRead
    temporary_password: str
    message: str


class AdminAvatarUploadResult(BaseModel):
    url: str
    status: Literal["done"]


class AdminUserListParams(BaseModel):
    q: str | None = Field(default=None, max_length=64)
    role: AdminUserRole | None = None
    status: AdminUserStatus | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)

    @field_validator("q")
    @classmethod
    def clean_query(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None
