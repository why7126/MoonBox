from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.schemas.admin_spaces import AdminSpaceApplicationRead, ExpiryType, validate_future_expiry


class CatalogSpaceCreateApplication(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    code: str = Field(min_length=2, max_length=32, pattern=r"^[a-z][a-z0-9-]{1,31}$")
    description: str | None = Field(default=None, max_length=512)
    member_quota: int = Field(default=20, ge=1, le=100000)
    storage_quota_gb: float = Field(default=100.0, gt=0)
    ai_quota_tokens: int = Field(default=1000000, ge=0)
    expiry_type: ExpiryType = "fixed_date"
    expires_at: str | None = Field(default=None, max_length=40)

    @model_validator(mode="after")
    def validate_expiry(self) -> "CatalogSpaceCreateApplication":
        self.expires_at = validate_future_expiry(self.expiry_type, self.expires_at)
        return self


class CatalogSpaceCreateResult(BaseModel):
    application: AdminSpaceApplicationRead
