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
    updated_at: str
    blocked: str | None = None
    sprint_id: str | None = None
    task_progress: tuple[int, int] | None = None
    test_progress: tuple[int, int] | None = None
    manual_acceptance_count: int = 0
    drift_warnings: list[str] = Field(default_factory=list)


class RequirementCenterWorkspace(BaseModel):
    organization_name: str
    workspace_id: str
    name: str
    slug: str
    description: str
    timezone: str
    member_count: int
    role: str


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
