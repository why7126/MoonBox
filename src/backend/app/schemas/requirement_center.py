from __future__ import annotations

from pydantic import BaseModel, Field


class RequirementCenterIssue(BaseModel):
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


class RequirementCenterDocumentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=200_000)


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
    total: int
    requirements: int
    bugs: int
    blocked: int
    drift: int


class RequirementCenterContext(BaseModel):
    issues: list[RequirementCenterIssue]
    workspaces: list[RequirementCenterWorkspace]
    current_user: RequirementCenterUser
    selected_workspace_id: str
    stats: RequirementCenterStats
    sprint_options: list[str] = Field(default_factory=list)
