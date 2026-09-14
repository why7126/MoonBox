from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class RequirementCenterReadFailureDetails(BaseModel):
    kind: Literal["source_invalid", "source_changing", "source_unavailable"] = Field(description="脱敏读取失败分类；旧2603可能没有此字段，不能推断为格式错误")
    request_id: str = Field(description="与X-Request-ID一致的服务端请求编号，不包含文件路径或原文")


class RequirementCenterReadError(BaseModel):
    code: int
    message: str
    data: RequirementCenterReadFailureDetails | None = None


class RequirementCenterDocumentCapability(BaseModel):
    readable: bool = True
    human_editable: bool = False
    ai_mutable: bool = False
    task_toggle_only: bool = False
    reason: str = "当前阶段只读"


class RequirementCenterChangeSummary(BaseModel):
    warnings: list[str] = Field(default_factory=list)
    id: str
    title: str | None = None
    stage: str
    source_kind: str
    task_progress: tuple[int, int] | None = None
    document_entries: list[RequirementCenterDocument] = Field(default_factory=list)


class RequirementCenterIssue(BaseModel):
    current_change: RequirementCenterChangeSummary | None = None
    related_changes: list[RequirementCenterChangeSummary] = Field(default_factory=list)
    change_warning: str | None = None
    id: str
    type: str
    title: str
    priority: str = "P2"
    owner: str
    source: str
    stage: str
    documents: list[str] = Field(default_factory=list)
    document_entries: list[RequirementCenterDocument] = Field(default_factory=list)
    detail_url: str
    archive_url: str | None = None
    action: RequirementCenterAction | None = None
    tasks: RequirementCenterTasks | None = None
    updated_at: str
    blocked: str | None = None
    sprint_id: str | None = None
    task_progress: tuple[int, int] | None = None
    test_progress: tuple[int, int] | None = None
    manual_acceptance_count: int = 0
    drift_warnings: list[str] = Field(default_factory=list)


class RequirementCenterDocument(BaseModel):
    name: str
    type: str
    open_mode: str
    status: str = "available"
    label: str
    url: str | None = None
    editable: bool = False
    capability: RequirementCenterDocumentCapability = Field(default_factory=RequirementCenterDocumentCapability)


class RequirementCenterDocumentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=200_000)
    expected_version: str = Field(pattern=r"^[a-f0-9]{64}$")
    idempotency_key: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")


class RequirementCenterAction(BaseModel):
    command: str
    label: str
    requires_choice: str | None = None
    disabled_reason: str | None = None


class RequirementCenterTasks(BaseModel):
    done: int = 0
    total: int = 0
    blocked: list[str] = Field(default_factory=list)
    source: str | None = None


class RequirementCenterWorkspace(BaseModel):
    organization_name: str
    workspace_id: str
    name: str
    slug: str
    description: str
    timezone: str
    member_count: int
    role: str
    status: str = "ACTIVE"
    readonly: bool = False


class RequirementCenterUser(BaseModel):
    name: str
    avatar_initial: str
    avatar_url: str | None = None
    can_access_admin: bool
    permissions: list[str] = Field(default_factory=list)


class RequirementCenterStats(BaseModel):
    standalone_changes: int = 0
    total: int
    requirements: int
    bugs: int
    blocked: int
    drift: int


class RequirementCenterContext(BaseModel):
    repository_id: str = ""
    snapshot_revision: str = ""
    sync_status: str = "ready"
    issues: list[RequirementCenterIssue]
    workspaces: list[RequirementCenterWorkspace]
    current_user: RequirementCenterUser
    selected_workspace_id: str
    stats: RequirementCenterStats
    sprint_options: list[str] = Field(default_factory=list)


class RequirementCenterCaptureCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["requirement", "bug"]
    title: str = Field(min_length=1, max_length=60)
    description: str = Field(default="", max_length=200)
    priority: Literal["P0", "P1", "P2", "P3"] | None = None
    severity: Literal["blocker", "critical", "high", "medium", "low"] | None = None
    owner: Literal["产品团队", "研发团队", "设计团队", "未分配"] = "未分配"
    source: Literal["explore", "user-feedback", "internal", "incident"] = "explore"
    idempotency_key: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")

    @model_validator(mode="after")
    def type_level(self):
        field = "priority" if self.type == "requirement" else "severity"
        other = "severity" if self.type == "requirement" else "priority"
        if getattr(self, field) is None or other in self.model_fields_set:
            raise ValueError("Invalid grading field for Capture type")
        return self

    @field_validator("title")
    @classmethod
    def nonempty_title(cls, value: str) -> str:
        value = value.strip()
        if not value or any(ord(char) < 32 for char in value):
            raise ValueError("标题不能为空或包含控制字符")
        return value
