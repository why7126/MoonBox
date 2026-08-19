from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

SpaceStatus = Literal["ACTIVE", "FROZEN", "RECYCLE"]
SpaceSource = Literal["后台创建", "申请审批"]
ExpiryType = Literal["fixed_date", "long_term"]
ApplicationStatus = Literal["待审批", "已通过", "已拒绝", "已撤回"]
ApplicationType = Literal["create", "join"]
AllowedAction = Literal["VIEW", "EDIT", "FREEZE", "RESTORE", "DELETE", "PURGE", "QUOTA", "RENEW", "TRANSFER_OWNER"]
SpaceMemberRole = Literal["管理员", "编辑者", "查看者"]


def validate_future_expiry(expiry_type: ExpiryType, expires_at: str | None) -> str | None:
    if expiry_type == "long_term":
        return None
    if not expires_at:
        raise ValueError("固定有效期空间必须设置到期时间。")
    normalized = expires_at.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError("到期时间格式不正确。") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    if parsed <= datetime.now(timezone.utc):
        raise ValueError("到期时间必须晚于当前时间。")
    return expires_at


class AdminSpaceRead(BaseModel):
    id: str
    name: str
    code: str
    description: str | None = None
    owner_id: str
    owner_name: str | None = None
    owner_role: str | None = None
    owner_avatar_url: str | None = None
    status: SpaceStatus
    source: SpaceSource
    member_count: int
    member_quota: int
    storage_used_gb: float
    storage_quota_gb: float
    ai_used_tokens: int
    ai_quota_tokens: int
    product_id: str
    product_name: str
    expiry_type: ExpiryType
    expires_at: str | None = None
    protected: bool
    deleted_at: str | None = None
    deleted_by: str | None = None
    deleted_by_name: str | None = None
    delete_reason: str | None = None
    purge_at: str | None = None
    allowed_actions: list[AllowedAction]
    created_at: str
    updated_at: str


class AdminSpaceListParams(BaseModel):
    q: str | None = Field(default=None, max_length=64)
    status: SpaceStatus | None = None
    source: SpaceSource | None = None
    usage_status: Literal["normal", "over_quota"] | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)

    @field_validator("q")
    @classmethod
    def clean_query(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class AdminSpaceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    code: str = Field(min_length=2, max_length=32, pattern=r"^[a-z][a-z0-9-]{1,31}$")
    description: str | None = Field(default=None, max_length=512)
    owner_id: str = Field(min_length=1, max_length=64)
    product_id: str = Field(min_length=2, max_length=64)
    product_name: str = Field(min_length=2, max_length=80)
    member_quota: int = Field(default=20, ge=1, le=100000)
    storage_quota_gb: float = Field(default=100.0, gt=0)
    ai_quota_tokens: int = Field(default=1000000, ge=0)
    expiry_type: ExpiryType = "fixed_date"
    expires_at: str | None = Field(default=None, max_length=40)

    @model_validator(mode="after")
    def validate_expiry(self) -> "AdminSpaceCreate":
        self.expires_at = validate_future_expiry(self.expiry_type, self.expires_at)
        return self


class AdminSpaceUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=512)
    expiry_type: ExpiryType
    expires_at: str | None = Field(default=None, max_length=40)

    @model_validator(mode="after")
    def validate_expiry(self) -> "AdminSpaceUpdate":
        self.expires_at = validate_future_expiry(self.expiry_type, self.expires_at)
        return self


class AdminSpaceAction(BaseModel):
    reason: str = Field(min_length=4, max_length=512)


class AdminSpaceQuotaUpdate(BaseModel):
    member_quota: int = Field(ge=1, le=100000)
    storage_quota_gb: float = Field(gt=0)
    ai_quota_tokens: int = Field(ge=0)
    reason: str = Field(min_length=4, max_length=512)


class AdminSpaceRenew(BaseModel):
    expiry_type: ExpiryType
    expires_at: str | None = Field(default=None, max_length=40)
    reason: str = Field(min_length=4, max_length=512)

    @model_validator(mode="after")
    def validate_expiry(self) -> "AdminSpaceRenew":
        self.expires_at = validate_future_expiry(self.expiry_type, self.expires_at)
        return self


class AdminSpaceTransferOwner(BaseModel):
    owner_id: str = Field(min_length=1, max_length=64)
    reason: str = Field(min_length=4, max_length=512)


class AdminSpaceMemberRead(BaseModel):
    id: str
    space_id: str
    user_id: str
    user_name: str | None = None
    username: str
    avatar_url: str | None = None
    role: SpaceMemberRole
    user_status: str
    joined_at: str
    updated_at: str


class AdminSpaceMemberCreate(BaseModel):
    user_id: str = Field(min_length=1, max_length=64)
    role: SpaceMemberRole


class AdminSpaceMemberUpdate(BaseModel):
    role: SpaceMemberRole


class AdminSpaceMemberAction(BaseModel):
    reason: str = Field(min_length=4, max_length=512)


class AdminSpaceApplicationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    code: str = Field(min_length=2, max_length=32, pattern=r"^[a-z][a-z0-9-]{1,31}$")
    applicant_id: str = Field(min_length=1, max_length=64)
    proposed_owner_id: str = Field(min_length=1, max_length=64)
    product_id: str = Field(min_length=2, max_length=64)
    product_name: str = Field(min_length=2, max_length=80)
    purpose: str = Field(min_length=4, max_length=512)
    expected_members: int = Field(default=10, ge=1, le=100000)
    requested_storage_gb: float = Field(default=100.0, gt=0)
    requested_ai_tokens: int = Field(default=1000000, ge=0)
    expires_at: str | None = Field(default=None, max_length=40)


class AdminSpaceApplicationRead(BaseModel):
    id: str
    application_type: ApplicationType = "create"
    target_space_id: str | None = None
    target_space_name: str | None = None
    name: str
    code: str
    applicant_id: str
    applicant_name: str | None = None
    proposed_owner_id: str
    proposed_owner_name: str | None = None
    product_id: str
    product_name: str
    purpose: str
    expected_members: int
    requested_storage_gb: float
    requested_ai_tokens: int
    expires_at: str | None = None
    status: ApplicationStatus
    decision_reason: str | None = None
    decision_by: str | None = None
    decision_at: str | None = None
    created_at: str
    updated_at: str


class AdminSpaceApplicationListParams(BaseModel):
    q: str | None = Field(default=None, max_length=64)
    status: ApplicationStatus | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)

    @field_validator("q")
    @classmethod
    def clean_query(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class AdminSpaceApplicationDecision(BaseModel):
    reason: str = Field(min_length=4, max_length=512)


class AdminSpaceAuditRead(BaseModel):
    id: str
    space_id: str
    actor: str
    actor_display_name: str | None = None
    action: str
    before_value: str | None = None
    after_value: str | None = None
    reason: str
    result: str
    request_id: str
    created_at: str
