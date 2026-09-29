"""Concrete contracts; unknown fields (including formal Issue IDs) are rejected."""
from typing import Literal, Annotated
from pydantic import BaseModel, ConfigDict, Field, model_validator

class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid')

class Candidate(StrictModel):
    id: str | None = Field(default=None, max_length=64)
    type: Literal['requirement', 'bug']
    title: str = Field(min_length=1, max_length=60)
    description: str = Field(min_length=1, max_length=10000)
    priority: Literal['P0','P1','P2','P3'] | None = None
    severity: Literal['blocker','critical','high','medium','low'] | None = None
    source_refs: list[Annotated[str, Field(min_length=1, max_length=64)]] = Field(min_length=1, max_length=11)
    parents: list[Annotated[str, Field(min_length=1, max_length=64)]] = Field(default_factory=list, max_length=50)
    classification_reason: str = Field(default='', max_length=2000)
    clarifications: list[Annotated[str, Field(max_length=2000)]] = Field(default_factory=list, max_length=50)

    @model_validator(mode='after')
    def valid_type(self):
        from app.governance.titles import business_title
        if not business_title(self.title) or not self.description.strip():
            raise ValueError('标题须为有效中文业务标题，描述不能为空')
        if self.type == 'requirement' and (not self.priority or self.severity is not None):
            raise ValueError('需求只能使用 priority')
        if self.type == 'bug' and (not self.severity or self.priority is not None):
            raise ValueError('缺陷只能使用 severity')
        return self

class DraftContent(StrictModel):
    text: str = Field(default='', max_length=20000)
    media_ids: list[str] = Field(default_factory=list, max_length=10)
    candidates: list[Candidate] = Field(default_factory=list, max_length=50)

class DraftUpdate(DraftContent):
    expected_revision: int = Field(ge=1)

class VersionInput(StrictModel):
    expected_revision: int = Field(ge=1)

class ConfirmInput(VersionInput):
    idempotency_key: str = Field(min_length=1, max_length=128)

class DraftResult(StrictModel):
    id: str
    revision: int
    state: str
    content: DraftContent
    updated_at: str
    confirmed_task_id: str | None = None

class DraftList(StrictModel):
    items: list[DraftResult]
    total: int
    page: int
    page_size: int

class IssueLink(StrictModel):
    candidate_id: str
    issue_id: str

class ConfirmationResult(StrictModel):
    id: str
    revision: int
    state: str
    phase: str
    issue_links: list[IssueLink]

class MaterialResult(StrictModel):
    media_id: str
    mime_type: str
    size: int
    width: int
    height: int
    state: str
    preview_url: str

class DeleteResult(StrictModel):
    id: str
    state: str
    cleanup: str

class OrganizePayload(StrictModel):
    candidates: list[Candidate]
    rules_version: str

class OrganizeResult(StrictModel):
    id: str
    revision: int
    state: str
    result: OrganizePayload | None
    error_code: str | None

class CaptureLimits(StrictModel):
    max_images:int
    max_image_bytes:int
    max_total_image_bytes:int
    max_pixels:int
    max_text_codepoints:int
    max_candidates:int
    max_title_codepoints:int
    max_description_codepoints:int
    max_drafts:int
    max_material_bytes:int
    image_types:list[str]

class CapabilitiesResult(StrictModel):
    limits:CaptureLimits
    organize_ready:bool
    organize_reason:str
    write_ready:bool
    write_reason:str

class CandidateOrigin(StrictModel):
    candidate:Candidate
    text:str

class SourceContent(DraftContent):
    history:dict[str,Candidate]
    origins:dict[str,CandidateOrigin]=Field(default_factory=dict)

class SourceResult(StrictModel):
    task_id:str
    candidate_id:str
    revision:int
    content:SourceContent

class CaptureErrorDetails(StrictModel):
    kind: str = Field(max_length=64)
    request_id: str = Field(max_length=64)

class CaptureErrorResponse(StrictModel):
    code: int
    message: str
    data: CaptureErrorDetails | None = None
