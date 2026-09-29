from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from functools import wraps
from copy import deepcopy
from contextlib import contextmanager
from datetime import datetime
import os
from pathlib import Path
import re
from typing import Any

from app.governance.lifecycle import change_state, aggregate_states
from sqlalchemy import text
from sqlalchemy.orm import Session
import yaml

from app.schemas.requirement_center import (
    RequirementCenterAction,
    RequirementCenterArchiveReadinessBlocker,
    RequirementCenterContext,
    RequirementCenterCurrentIterationArchiveReadiness,
    RequirementCenterCurrentIterationCapacity,
    RequirementCenterDocument,
    RequirementCenterDocumentCapability,
    RequirementCenterIssue,
    RequirementCenterSprintOption,
    RequirementCenterSprintMetrics,
    RequirementCenterStats,
    RequirementCenterTasks,
    RequirementCenterUser,
    RequirementCenterWorkspace,
)


def _resolve_governance_root(source_file: Path | None = None) -> Path:
    configured_root = os.environ.get("MOONBOX_GOVERNANCE_ROOT")
    if configured_root:
        return Path(configured_root).resolve()

    source_path = (source_file or Path(__file__)).resolve()
    for parent in source_path.parents:
        if (parent / "issues").exists() and (parent / "openspec").exists():
            return parent
    return Path.cwd().resolve()


GOVERNANCE_ROOT = _resolve_governance_root()
# Compatibility for offline governance tools/tests. HTTP callers always bind an
# authorized immutable snapshot; concurrent requests never mutate module state.
_SCOPED_ROOT: ContextVar[Path | None] = ContextVar("requirement_center_root", default=None)
_VALID_PRIORITIES = {"P0", "P1", "P2", "P3"}
_VALID_SEVERITIES = {"blocker", "critical", "high", "medium", "low"}
_TASK_ITEM_RE = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(.+?)\s*$")


@dataclass(frozen=True)
class _TaskProgressBucket:
    done: int = 0
    total: int = 0

    @property
    def progress(self) -> tuple[int, int] | None:
        return (self.done, self.total) if self.total else None


@dataclass(frozen=True)
class _ClassifiedTaskProgress:
    development: _TaskProgressBucket = _TaskProgressBucket()
    test: _TaskProgressBucket = _TaskProgressBucket()
    manual: _TaskProgressBucket = _TaskProgressBucket()

    @property
    def has_progress(self) -> bool:
        return bool(self.development.total or self.test.total or self.manual.total)

def _governance_root() -> Path:
    return _SCOPED_ROOT.get() or GOVERNANCE_ROOT

@contextmanager
def using_governance_root(root: Path, *, immutable: bool = False):
    token = _SCOPED_ROOT.set(root)
    memo_token = _READ_MEMO.set({} if immutable else None)
    try:
        yield
    finally:
        _SCOPED_ROOT.reset(token)
        _READ_MEMO.reset(memo_token)

# Request-local pure parsing only. Mutable legacy/writer contexts opt out.
_READ_MEMO: ContextVar[dict | None] = ContextVar("requirement_center_read_memo", default=None)


def _memoized_read(function):
    @wraps(function)
    def read(*args):
        memo = _READ_MEMO.get()
        if memo is None:
            return function(*args)
        key = (function.__name__, tuple(tuple(arg) if isinstance(arg, list) else arg for arg in args))
        if key not in memo:
            memo[key] = function(*args)
        return deepcopy(memo[key])
    return read

STAGES = {
    "captured": "capture",
    "draft": "planning",
    "enriching": "planning",
    "pending_review": "review-ready",
    "approved": "approved",
    "in_sprint": "sprint-planning",
    "proposed": "ready-dev",
    "in_progress": "development",
    "applied": "acceptance",
    "done": "done",
    "archived": "done",
}
SPRINT_VISIBLE_STAGES = {"sprint-planning", "ready-dev", "development", "acceptance", "done"}
CHANGE_DOCS = ("proposal.md", "spec.md", "design.md", "trace.md", "tasks.md")
TASK_MARKER_RE = re.compile(r"^(\s*[-*]\s+\[)( |x|X)(\]\s+.*)$")


def build_requirement_center_context(
    current_user: dict[str, Any] | None = None,
    db: Session | None = None,
    visibility=None,
) -> RequirementCenterContext:
    from app.governance.change_index import ChangeIndex
    issues = ChangeIndex(_governance_root()).cards(visibility or (lambda _: True))
    issues.sort(key=lambda item: item.updated_at, reverse=True)
    stats = RequirementCenterStats(
        total=len(issues),
        standalone_changes=sum(1 for item in issues if item.type == "change"),
        requirements=sum(1 for item in issues if item.type == "requirement"),
        bugs=sum(1 for item in issues if item.type == "bug"),
        blocked=sum(1 for item in issues if item.blocked),
        drift=sum(1 for item in issues if item.drift_warnings),
    )
    workspaces = _load_workspaces(issues, current_user, db)
    return RequirementCenterContext(
        issues=issues,
        workspaces=workspaces,
        current_user=_context_user(current_user),
        selected_workspace_id=workspaces[0].workspace_id if workspaces else "",
        current_iteration_capacity=_load_current_iteration_capacity(),
        sprint_metrics=_load_sprint_metrics(),
        sprint_options=_load_open_sprints(),
        sprint_option_details=_load_sprint_option_details(),
        stats=stats,
    )


def _load_issues(issue_type: str) -> list[RequirementCenterIssue]:
    registry_path = _governance_root() / "issues" / ("requirements" if issue_type == "requirement" else "bugs") / "_registry.yaml"
    if not registry_path.exists():
        raise FileNotFoundError(f"requirement center registry missing: {issue_type}")
    registry = _read_yaml(registry_path)
    entries = registry.get("entries", []) if isinstance(registry, dict) else []
    return [_build_issue(issue_type, entry) for entry in entries if isinstance(entry, dict)]


def _build_issue(issue_type: str, entry: dict[str, Any], changes_override: list[str] | None = None, status_override: str | None = None) -> RequirementCenterIssue:
    issue_id = str(entry.get("id", "")).strip()
    issue_dir = _safe_issue_dir(entry.get("path"))
    trace = _frontmatter(issue_dir / "trace.md") if issue_dir else {}
    changes = _linked_changes(entry, trace) if changes_override is None else changes_override
    tasks = _change_tasks(changes)
    classified_tasks = _classified_change_tasks(changes)
    task_progress = (tasks.done, tasks.total) if tasks and tasks.total else None
    raw_sprint_id = entry.get("target_iteration") or entry.get("iteration") or trace.get("iteration")
    status = status_override or _issue_status(entry, trace, changes)
    documents = [name for name in _display_document_names(issue_dir, changes, status) if name != "sprint.md"]
    main_document = "requirement.md" if issue_type == "requirement" else "bug.md"
    documents = [name for name in documents if name not in {"requirement.md", "bug.md"}]
    if issue_dir and (issue_dir / main_document).is_file():
        documents.insert(0, main_document)
    if issue_type == "requirement":
        documents.extend(name for name in _prototype_documents(issue_dir) if name not in documents)
    sprint_document = _sprint_document(entry, trace)
    if sprint_document:
        documents.append("sprint.md")
    stage = _map_stage(str(status), documents, changes)
    test_progress = _test_progress(_document_names(issue_dir), stage)
    manual_acceptance_progress: tuple[int, int] | None = None
    if stage == "acceptance" and classified_tasks.has_progress:
        task_progress = classified_tasks.development.progress
        test_progress = classified_tasks.test.progress
        manual_acceptance_progress = classified_tasks.manual.progress
    sprint_id = raw_sprint_id if _should_show_sprint(stage) else None
    warnings = _drift_warnings(entry, trace, issue_dir, raw_sprint_id)
    priority, severity, level_warning = _classification_fields(issue_type, entry, trace)
    if level_warning:
        warnings.append(level_warning)
    validation_documents = sorted((set(_document_names(issue_dir)) - {"sprint.md"}) | set(documents))
    blocked = _blocked_reason(stage, issue_type, validation_documents, warnings, issue_dir)
    if stage == "sprint-planning":
        if not sprint_document:
            blocked = "缺少关联 Sprint 的 sprint.md"
        elif not sprint_document.read_text(encoding="utf-8").strip():
            blocked = "文档内容为空：sprint.md"
    detail_url = _detail_url(issue_id)
    return RequirementCenterIssue(
        id=_short_id(issue_id),
        type=issue_type,
        title=str(entry.get("title") or issue_id),
        priority=priority,
        severity=severity,
        owner=_owner_name(entry.get("owner") or entry.get("requester") or entry.get("reporter")),
        source=str(entry.get("lifecycle_stage") or entry.get("status") or "registry"),
        stage=stage,
        documents=documents,
        document_entries=_document_entries(issue_id, documents, stage, issue_type, changes),
        detail_url=detail_url,
        archive_url=detail_url if stage == "done" else None,
        action=_stage_action(issue_id, issue_type, stage, blocked),
        tasks=tasks,
        updated_at=_updated_at(trace.get("updated_at") or entry.get("created")),
        blocked=blocked,
        sprint_id=str(sprint_id) if sprint_id else None,
        task_progress=task_progress,
        test_progress=test_progress,
        manual_acceptance_progress=manual_acceptance_progress,
        manual_acceptance_count=0,
        drift_warnings=warnings,
    )


def _classification_fields(issue_type: str, entry: dict[str, Any], trace: dict[str, Any]) -> tuple[str, str, str | None]:
    if issue_type == "bug":
        raw = entry.get("severity") or trace.get("severity")
        severity = str(raw or "").strip().lower()
        if severity in _VALID_SEVERITIES:
            return "", severity, None
        issue_id = str(entry.get("id") or trace.get("bug_id") or "BUG").strip()
        reason = "缺少 severity" if not severity else f"非法 severity: {severity}"
        return "", "", f"{issue_id} 分级字段异常：{reason}"

    raw = entry.get("priority") or trace.get("priority") or "P2"
    priority = str(raw or "").strip().upper()
    if priority in _VALID_PRIORITIES:
        return priority, "", None
    issue_id = str(entry.get("id") or trace.get("requirement_id") or "REQ").strip()
    return "", "", f"{issue_id} 分级字段异常：非法 priority: {priority}"


def _should_show_sprint(stage: str) -> bool:
    return stage in SPRINT_VISIBLE_STAGES


def _prototype_documents(issue_dir: Path | None) -> list[str]:
    if not issue_dir or not issue_dir.is_dir():
        return []
    candidates = [issue_dir / "prototype.html"]
    folder = issue_dir / "prototype"
    if folder.is_dir() and not folder.is_symlink():
        candidates.extend(folder.rglob("*.html"))
    result = []
    for path in candidates:
        relative = path.relative_to(issue_dir)
        if any((issue_dir / Path(*relative.parts[:i])).is_symlink() for i in range(1, len(relative.parts) + 1)):
            continue
        if path.is_file() and path.resolve().is_relative_to(issue_dir.resolve()):
            result.append(relative.as_posix())
    return sorted(set(result))


def _document_names(issue_dir: Path | None) -> list[str]:
    if not issue_dir or not issue_dir.exists():
        return []
    names = [path.name for path in issue_dir.iterdir() if path.is_file() and path.suffix.lower() in {".md", ".html"}]
    return sorted(names)


def _display_document_names(issue_dir: Path | None, changes: list[str], status: Any) -> list[str]:
    stage = STAGES.get(str(status), "capture")
    if changes and stage in SPRINT_VISIBLE_STAGES:
        change_documents = _change_document_names(changes[0])
        if change_documents:
            # A Change trace never supplies the card's Issue trace existence.
            names = [name for name in change_documents if name != "trace.md"]
            if issue_dir and (issue_dir / "trace.md").is_file():
                names.append("trace.md")
            return names
    return _document_names(issue_dir)


@_memoized_read
def _change_document_names(change_id: str) -> list[str]:
    try:
        change_dir = _change_dir(change_id)
    except PermissionError:
        return []
    existing: set[str] = set()
    for name in ("proposal.md", "design.md", "trace.md", "tasks.md"):
        if (change_dir / name).exists():
            existing.add(name)
    if any((change_dir / "specs").glob("*/spec.md")):
        existing.add("spec.md")
    return [name for name in CHANGE_DOCS if name in existing]


def _document_entries(issue_id: str, documents: list[str], stage: str, issue_type: str, changes: list[str]) -> list[RequirementCenterDocument]:
    entries: list[RequirementCenterDocument] = []
    change_id = changes[0] if changes and stage in SPRINT_VISIBLE_STAGES else None
    trace_dir = _find_issue_dir(issue_id)
    for name in dict.fromkeys([*documents, "trace.md", *(["sprint.md"] if stage == "sprint-planning" else [])]):
        suffix = Path(name).suffix.lower()
        if suffix == ".md":
            path_category = "change" if change_id and name in CHANGE_DOCS and name != "trace.md" else "issue"
            capability = compute_document_capability(
                issue_type=issue_type,
                stage=stage,
                document_name=name,
                path_category=path_category,
                exists=bool(trace_dir and (trace_dir / name).is_file()) if name == "trace.md" else True,
            )
            if name == "sprint.md":
                capability = RequirementCenterDocumentCapability(
                    readable="sprint.md" in documents, reason="关联 Sprint 文档只读" if "sprint.md" in documents else "关联 Sprint 文档不存在或已移动")
            url = (
                f"/api/v1/requirement-center/changes/{change_id}/documents/{name}"
                if path_category == "change"
                else f"/api/v1/requirement-center/issues/{issue_id}/documents/{name}"
            )
            entries.append(
                RequirementCenterDocument(
                    name=name,
                    type="markdown",
                    open_mode="drawer",
                    label=name,
                    url=url,
                    editable=capability.human_editable,
                    capability=capability,
                )
            )
        elif suffix == ".html":
            entries.append(
                RequirementCenterDocument(
                    name=name,
                    type="html",
                    open_mode="new-tab",
                    label=name.removeprefix("prototype/"),
                    url=f"/api/v1/requirement-center/issues/{issue_id}/documents/{name}/preview",
                )
            )
    return entries


def compute_document_capability(
    *,
    issue_type: str,
    stage: str,
    document_name: str,
    path_category: str,
    exists: bool,
) -> RequirementCenterDocumentCapability:
    if not exists:
        return RequirementCenterDocumentCapability(readable=False, reason="文档不存在或已移动")
    if document_name == "sprint.md":
        return RequirementCenterDocumentCapability(reason="关联 Sprint 文档只读")
    if document_name == "trace.md":
        return RequirementCenterDocumentCapability(ai_mutable=True, reason="trace.md 仅允许系统治理链路更新，人工始终只读")
    if path_category == "effective_spec":
        return RequirementCenterDocumentCapability(reason="已生效规格只能通过 OpenSpec Change 和 archive 合并流程修改")
    if path_category == "change":
        if stage == "ready-dev" and document_name in {"proposal.md", "spec.md", "design.md", "tasks.md"}:
            return RequirementCenterDocumentCapability(human_editable=True, ai_mutable=True, reason="待开发阶段允许编辑当前 OpenSpec Change 计划类文档")
        if stage == "acceptance" and document_name == "tasks.md":
            return RequirementCenterDocumentCapability(ai_mutable=True, task_toggle_only=True, reason="验收中 tasks.md 仅允许勾选或取消勾选任务")
        return RequirementCenterDocumentCapability(ai_mutable=True, reason="当前 Change 阶段不允许人工全文编辑")
    if stage == "capture" and document_name == "capture.md":
        return RequirementCenterDocumentCapability(human_editable=True, ai_mutable=True, reason="采集池阶段允许编辑 capture.md")
    if stage == "planning":
        allowed = "requirement.md" if issue_type == "requirement" else "bug.md"
        if document_name == allowed:
            return RequirementCenterDocumentCapability(human_editable=True, ai_mutable=True, reason="规划中阶段允许编辑主文档")
    if stage == "review-ready":
        allowed_docs = {"acceptance.md"}
        allowed_docs.update({"requirement.md", "business-flow.md", "user-stories.md"} if issue_type == "requirement" else {"bug.md", "root-cause.md", "workaround.md"})
        if document_name in allowed_docs:
            return RequirementCenterDocumentCapability(human_editable=True, ai_mutable=True, reason="待评审阶段允许完善类文档编辑")
    if stage == "approved":
        allowed_docs = {"acceptance.md", "review.md"}
        allowed_docs.update({"requirement.md", "business-flow.md", "user-stories.md"} if issue_type == "requirement" else {"bug.md", "root-cause.md", "workaround.md"})
        if document_name in allowed_docs:
            return RequirementCenterDocumentCapability(human_editable=True, ai_mutable=True, reason="已评审阶段允许已评审材料编辑")
    return RequirementCenterDocumentCapability(ai_mutable=True, reason="当前治理阶段不允许人工编辑")


def _detail_url(issue_id: str) -> str:
    return f"/requirements/{issue_id}"


def _stage_action(issue_id: str, issue_type: str, stage: str, blocked: str | None) -> RequirementCenterAction:
    commands: dict[str, dict[str, str]] = {
        "capture": {"requirement": "/req-generate", "bug": "/bug-generate"},
        "planning": {"requirement": "/req-complete", "bug": "/bug-complete"},
        "review-ready": {"requirement": "/req-review", "bug": "/bug-review"},
        "approved": {"requirement": "/sprint-propose", "bug": "/sprint-propose"},
        "sprint-planning": {"requirement": "/req-opsx", "bug": "/bug-opsx"},
        "ready-dev": {"requirement": "/opsx-apply", "bug": "/opsx-apply"},
        "development": {"requirement": "/opsx-apply", "bug": "/opsx-apply"},
        "acceptance": {"requirement": "/opsx-archive", "bug": "/opsx-archive"},
        "done": {"requirement": "只读", "bug": "只读"},
    }
    labels: dict[str, dict[str, str]] = {
        "capture": {"requirement": "生成需求", "bug": "生成 Bug"},
        "planning": {"requirement": "完善需求", "bug": "完善 Bug"},
        "review-ready": {"requirement": "发起评审", "bug": "确认修复"},
        "approved": {"requirement": "加入迭代", "bug": "加入迭代"},
        "sprint-planning": {"requirement": "生成 Opsx", "bug": "生成 Opsx"},
        "ready-dev": {"requirement": "开始开发", "bug": "开始修复"},
        "development": {"requirement": "查看进度", "bug": "查看进度"},
        "acceptance": {"requirement": "完成 / 归档", "bug": "完成 / 归档"},
        "done": {"requirement": "查看归档", "bug": "查看归档"},
    }
    choice = None
    if stage == "capture":
        choice = "generation"
    elif stage == "planning":
        choice = "completion"
    elif stage == "approved":
        choice = "sprint"
    return RequirementCenterAction(
        command=f"{commands.get(stage, {}).get(issue_type, '只读')} {issue_id}".strip(),
        label=labels.get(stage, {}).get(issue_type, "只读"),
        requires_choice=choice,
        disabled_reason=blocked,
    )


def _safe_issue_dir(raw_path: Any) -> Path | None:
    if not raw_path:
        return None
    candidate = (_governance_root() / str(raw_path)).resolve()
    try:
        candidate.relative_to(_governance_root())
    except ValueError:
        return None
    return candidate


@_memoized_read
def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))
    except (OSError, yaml.YAMLError):
        return {}
    return data if isinstance(data, dict) else {}


def _load_workspaces(
    issues: list[RequirementCenterIssue],
    current_user: dict[str, Any] | None,
    db: Session | None,
) -> list[RequirementCenterWorkspace]:
    if db is not None and current_user and current_user.get("id"):
        workspaces = _load_joined_admin_spaces(db, str(current_user["id"]))
        if workspaces:
            return workspaces
    if db is not None:
        return []
    return _load_project_workspace(issues, current_user)


def _load_joined_admin_spaces(db: Session, user_id: str) -> list[RequirementCenterWorkspace]:
    rows = db.execute(
        text(
            """
            SELECT s.id, s.name, s.code, s.description, s.status, s.member_count,
                   s.owner_id, COALESCE(owner.nickname, owner.username, 'MoonBox 产品团队') AS owner_name,
                   m.role AS member_role
            FROM admin_spaces s
            JOIN admin_space_products p ON p.space_id = s.id
            LEFT JOIN admin_users owner ON owner.id = s.owner_id
            LEFT JOIN admin_space_members m ON m.space_id = s.id AND m.user_id = :user_id
            WHERE s.status != 'RECYCLE'
              AND (s.owner_id = :user_id OR m.user_id IS NOT NULL)
            ORDER BY s.created_at DESC, s.name ASC
            """
        ),
        {"user_id": user_id},
    ).all()
    workspaces: list[RequirementCenterWorkspace] = []
    for row in rows:
        data = dict(row._mapping)
        status = str(data.get("status") or "ACTIVE")
        role = "拥有者" if str(data.get("owner_id")) == user_id else str(data.get("member_role") or "成员")
        workspaces.append(
            RequirementCenterWorkspace(
                organization_name=str(data.get("owner_name") or "MoonBox 产品团队"),
                workspace_id=str(data["id"]),
                name=str(data.get("name") or data.get("code") or "未命名空间"),
                slug=str(data.get("code") or data["id"]),
                description=str(data.get("description") or ""),
                timezone=os.environ.get("TZ", "Asia/Shanghai"),
                member_count=int(data.get("member_count") or 1),
                role=role,
                status=status,
                readonly=status == "FROZEN",
            )
        )
    return workspaces


def _load_project_workspace(
    issues: list[RequirementCenterIssue],
    current_user: dict[str, Any] | None,
) -> list[RequirementCenterWorkspace]:
    project = _read_yaml(_governance_root() / "project.yaml").get("project", {})
    if not isinstance(project, dict):
        project = {}
    name = str(project.get("name") or project.get("code") or "MoonBox").strip()
    code = str(project.get("code") or name).strip()
    owner = str(project.get("owner") or "MoonBox 产品团队").strip()
    description = str(project.get("description") or "当前项目治理工作空间").strip()
    workspace_id = _workspace_id(code)
    return [
        RequirementCenterWorkspace(
            organization_name=owner,
            workspace_id=workspace_id,
            name=name,
            slug=workspace_id,
            description=description,
            timezone=os.environ.get("TZ", "Asia/Shanghai"),
            member_count=_workspace_member_count(issues, current_user),
            role=_workspace_role(current_user),
        )
    ]


def _workspace_id(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")
    return slug or "moonbox"


def _workspace_member_count(issues: list[RequirementCenterIssue], current_user: dict[str, Any] | None) -> int:
    members = {issue.owner for issue in issues if issue.owner and issue.owner != "未分配"}
    if current_user:
        display_name = str(current_user.get("nickname") or current_user.get("username") or "").strip()
        if display_name:
            members.add(display_name)
    return max(1, len(members))


def _workspace_role(user: dict[str, Any] | None) -> str:
    if not user:
        return "只读"
    if bool(user.get("is_system_superadmin")):
        return "拥有者"
    if str(user.get("role")) == "后台管理员":
        return "管理员"
    return "只读"


@_memoized_read
def _frontmatter(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    data = yaml.load(parts[1], Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))
    return data if isinstance(data, dict) else {}


def _linked_changes(entry: dict[str, Any], trace: dict[str, Any]) -> list[str]:
    changes: list[str] = []
    for key in ("related_changes", "related_change"):
        value = entry.get(key)
        if isinstance(value, list):
            changes.extend(str(item) for item in value if item)
        elif value:
            changes.append(str(value))
    for item in trace.get("openspec_changes", []) or []:
        if isinstance(item, dict) and item.get("change_id"):
            changes.append(str(item["change_id"]))
    return sorted(set(changes))


@_memoized_read
def _change_tasks(changes: list[str]) -> RequirementCenterTasks | None:
    total_done = 0
    total = 0
    blocked: list[str] = []
    source: str | None = None
    for change in changes:
        tasks_path = _change_dir(change) / "tasks.md"
        if not tasks_path.exists():
            continue
        source = change
        for line in tasks_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped.startswith("- ["):
                continue
            total += 1
            if stripped.startswith("- [x]"):
                total_done += 1
            if "阻塞" in stripped or "blocked" in stripped.lower():
                blocked.append(stripped[:160])
    return RequirementCenterTasks(done=total_done, total=total, blocked=blocked, source=source) if total else None


@_memoized_read
def _classified_change_tasks(changes: list[str]) -> _ClassifiedTaskProgress:
    counters = {
        "development": [0, 0],
        "test": [0, 0],
        "manual": [0, 0],
    }
    for change in changes:
        tasks_path = _change_dir(change) / "tasks.md"
        if not tasks_path.exists():
            continue
        current_category = "development"
        for line in tasks_path.read_text(encoding="utf-8").splitlines():
            heading = _task_heading_category(line)
            if heading:
                current_category = heading
                continue
            match = _TASK_ITEM_RE.match(line)
            if not match:
                continue
            category = _task_item_category(match.group(2), current_category)
            counters[category][1] += 1
            if match.group(1).lower() == "x":
                counters[category][0] += 1
    return _ClassifiedTaskProgress(
        development=_TaskProgressBucket(counters["development"][0], counters["development"][1]),
        test=_TaskProgressBucket(counters["test"][0], counters["test"][1]),
        manual=_TaskProgressBucket(counters["manual"][0], counters["manual"][1]),
    )


def _task_heading_category(line: str) -> str | None:
    text = line.strip().lstrip("#").strip()
    if not text or text == line.strip():
        return None
    lowered = text.lower()
    if "验收返修" in lowered or "opsx-modify" in lowered:
        return "repair"
    if any(keyword in lowered for keyword in ("人工验收", "人工复验", "人工确认", "sign-off", "manual acceptance")):
        return "manual"
    if any(keyword in lowered for keyword in ("回归验证", "自动化测试", "测试任务", "测试", "验证", "视觉证据", "validation")):
        return "test"
    if any(keyword in lowered for keyword in ("实施", "研发", "开发", "修复", "文档同步", "准备", "implementation")):
        return "development"
    return None


def _task_item_category(text: str, current_category: str) -> str:
    lowered = text.lower()
    if current_category in {"development", "test", "manual"}:
        return current_category
    if "纳入对应分类" in text or "分类解析" in text or "进度字段" in text:
        return "development"
    if any(keyword in lowered for keyword in ("人工验收", "人工复验", "人工确认", "人工签收", "sign-off", "manual acceptance")):
        return "manual"
    if any(keyword in lowered for keyword in ("回归", "测试", "验证", "校验", "视觉证据", "截图", "validation", "test")):
        return "test"
    return "development" if current_category == "repair" else current_category


def _change_task_progress(changes: list[str]) -> tuple[int, int] | None:
    tasks = _change_tasks(changes)
    return (tasks.done, tasks.total) if tasks else None


def _change_status(changes: list[str]) -> str | None:
    if not changes:
        return None
    statuses = []
    for change in changes:
        directory = _change_dir(change)
        if directory.parent == (_governance_root() / "openspec" / "archive").resolve():
            statuses.append("archived")
            continue
        if not directory.is_dir():
            continue
        trace = _frontmatter(directory / "trace.md")
        progress = _change_tasks([change])
        statuses.append(change_state(trace, progress.done if progress else 0, progress.total if progress else 0))
    return aggregate_states(statuses)


def _issue_status(entry: dict[str, Any], trace: dict[str, Any], changes: list[str]) -> str:
    status = str(trace.get("status") or entry.get("status") or "captured")
    # Closed issues cannot be reopened by a historical Change status.
    if status in {"done", "archived"}:
        return status
    return _change_status(changes) or status


def _map_stage(status: str, documents: list[str], changes: list[str]) -> str:
    if status == "in_sprint" and changes:
        return "ready-dev"
    if status == "captured" and any(doc in documents for doc in ("requirement.md", "bug.md")):
        return "planning"
    return "unknown" if status == "unknown" else STAGES.get(status, "capture")


def _drift_warnings(entry: dict[str, Any], trace: dict[str, Any], issue_dir: Path | None, sprint_id: Any) -> list[str]:
    warnings: list[str] = []
    if issue_dir and not issue_dir.exists():
        warnings.append("issue_path_missing")
    if sprint_id and not _sprint_contains(str(sprint_id), str(entry.get("id", ""))):
        warnings.append("sprint_scope_mismatch")
    if trace.get("status") and entry.get("status") and trace.get("status") != entry.get("status"):
        warnings.append("registry_trace_status_mismatch")
    return warnings


def _sprint_document(entry: dict[str, Any], trace: dict[str, Any]) -> Path | None:
    """Resolve exactly the associated Sprint; never use an Issue or stale copy."""
    sprint_id = entry.get("target_iteration") or entry.get("iteration") or trace.get("iteration")
    if not isinstance(sprint_id, str) or not re.fullmatch(r"sprint-\d{3,}", sprint_id):
        return None
    root = _governance_root().resolve()
    directory = root / "iterations/change" / sprint_id
    if not directory.exists():
        directory = root / "iterations/archive" / sprint_id
    directory = directory.resolve()
    try:
        directory.relative_to(root / "iterations")
        target = (directory / "sprint.md").resolve()
        target.relative_to(directory)
    except ValueError:
        return None
    sprint = _read_yaml(directory / "sprint.yaml")
    key = "requirements" if str(entry.get("id", "")).startswith("REQ-") else "bugs"
    if entry.get("id") not in (sprint.get(key) or []):
        return None
    return target if target.is_file() else None


def _issue_sprint_document(issue_id: str, issue_dir: Path) -> Path | None:
    folder = "requirements" if issue_id.startswith("REQ-") else "bugs"
    registry = _read_yaml(_governance_root() / "issues" / folder / "_registry.yaml")
    entry = next((item for item in registry.get("entries", []) if item.get("id") == issue_id), {})
    return _sprint_document(entry, _frontmatter(issue_dir / "trace.md"))


def _sprint_contains(sprint_id: str, issue_id: str) -> bool:
    if Path(sprint_id).name != sprint_id:
        return False
    sprint = _read_yaml(_governance_root() / "iterations" / "change" / sprint_id / "sprint.yaml")
    if not sprint:
        sprint = _read_yaml(_governance_root() / "iterations" / "archive" / sprint_id / "sprint.yaml")
    key = "requirements" if issue_id.startswith("REQ-") else "bugs"
    return issue_id in (sprint.get(key) or [])


def _load_open_sprints() -> list[str]:
    base = _governance_root() / "iterations" / "change"
    if not base.exists():
        return []
    sprints: list[str] = []
    for path in sorted(base.glob("sprint-*")):
        sprint = _read_yaml(path / "sprint.yaml")
        status = str(sprint.get("status") or "").lower()
        if status not in {"closed", "archived", "done"}:
            sprints.append(path.name)
    return sprints


def _sprint_status_label(status: str, lifecycle: str) -> tuple[str, str, str | None]:
    if lifecycle == "archive":
        return "archived", "已归档", None
    if status == "planning":
        return "planning", "规划中", None
    if status == "in_progress":
        return "in_progress", "进行中", None
    if status in {"completed", "done", "closed", "archived"}:
        return "completed", "已完成", None
    return "unknown", "状态待核实", "sprint_status_unknown"


def _load_sprint_option_details() -> list[RequirementCenterSprintOption]:
    root = _governance_root()
    records: dict[str, RequirementCenterSprintOption] = {}
    conflicts: set[str] = set()
    for lifecycle, base in (("change", root / "iterations" / "change"), ("archive", root / "iterations" / "archive")):
        if not base.exists():
            continue
        for path in sorted(base.glob("sprint-*")):
            if not re.fullmatch(r"sprint-\d{3,}", path.name):
                continue
            data = _read_yaml(path / "sprint.yaml")
            raw_status = str(data.get("status") or "").lower()
            status, label, warning = _sprint_status_label(raw_status, lifecycle)
            if path.name in records:
                conflicts.add(path.name)
                continue
            records[path.name] = RequirementCenterSprintOption(
                sprint_id=path.name,
                label=path.name,
                lifecycle_stage=lifecycle,  # type: ignore[arg-type]
                status=status,  # type: ignore[arg-type]
                status_label=label,
                warning=warning,
            )
    for sprint_id in conflicts:
        records[sprint_id] = records[sprint_id].model_copy(
            update={
                "lifecycle_stage": "unknown",
                "status": "unknown",
                "status_label": "状态待核实",
                "warning": "sprint_lifecycle_conflict",
            }
        )
    return [records[key] for key in sorted(records.keys(), reverse=True)]


def _load_sprint_metrics() -> RequirementCenterSprintMetrics:
    root = _governance_root()
    seen: set[str] = set()
    completed: set[str] = set()
    warning = None
    for lifecycle, base in (("change", root / "iterations" / "change"), ("archive", root / "iterations" / "archive")):
        if not base.exists():
            continue
        for path in sorted(base.glob("sprint-*")):
            sprint_id = path.name
            if not re.fullmatch(r"sprint-\d{3,}", sprint_id):
                continue
            seen.add(sprint_id)
            data: dict[str, Any] = {}
            if (path / "sprint.yaml").exists():
                try:
                    loaded = yaml.load((path / "sprint.yaml").read_text(encoding="utf-8"), Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))
                    data = loaded if isinstance(loaded, dict) else {}
                except (OSError, yaml.YAMLError):
                    warning = "sprint_metrics_partial"
                    data = {}
            status = str(data.get("status") or "").lower()
            if lifecycle == "archive" or status in {"completed", "done", "archived", "closed"}:
                completed.add(sprint_id)
    return RequirementCenterSprintMetrics(
        completed_count=len(completed),
        total_count=len(seen),
        warning=warning,
    )


def _load_current_iteration_capacity() -> list[RequirementCenterCurrentIterationCapacity]:
    base = _governance_root() / "iterations" / "change"
    if not base.exists():
        return []
    sprint_paths = [
        path for path in sorted(base.glob("sprint-*"))
        if re.fullmatch(r"sprint-\d{3,}", path.name)
    ]
    active: list[tuple[str, dict[str, Any]]] = []
    for path in sprint_paths:
        sprint = _read_yaml(path / "sprint.yaml")
        if not isinstance(sprint, dict):
            continue
        status = str(sprint.get("status") or "").lower()
        if status not in {"closed", "archived", "done"}:
            active.append((path.name, sprint))
    multiple_warning = len(active) > 2
    return [_sprint_capacity_summary(sprint_id, sprint, multiple_warning=multiple_warning) for sprint_id, sprint in active]


def _sprint_capacity_summary(
    sprint_id: str,
    sprint: dict[str, Any],
    *,
    multiple_warning: bool = False,
) -> RequirementCenterCurrentIterationCapacity:
    source: str = "unknown"
    total: float | None = None
    raw_total = sprint.get("capacity_person_days")
    if isinstance(raw_total, (int, float)) and raw_total > 0:
        total = float(raw_total)
        source = "explicit"
    elif raw_total is None:
        total = 30.0
        source = "default"

    used = _sum_scope_estimates(sprint.get("scope_estimates"))
    status = _capacity_status(used, total)
    messages: list[str] = []
    if source == "default":
        messages.append("使用默认容量")
    if status == "near_limit":
        messages.append("接近容量上限")
    elif status == "over_limit":
        messages.append("已超出规划容量")
    elif status == "unknown":
        messages.append("容量待核实")
    if multiple_warning:
        status = "unknown"
        messages.append("当前迭代超过 2 个，请核实范围")

    return RequirementCenterCurrentIterationCapacity(
        sprint_id=sprint_id,
        used_capacity=used,
        total_capacity=total,
        capacity_source=source,  # type: ignore[arg-type]
        status=status,  # type: ignore[arg-type]
        message="；".join(messages) or None,
        archive_readiness=_sprint_archive_readiness(sprint_id, sprint, used, status),
    )


def _sprint_archive_readiness(
    sprint_id: str,
    sprint: dict[str, Any],
    used_capacity: float | None,
    capacity_status: str,
) -> RequirementCenterCurrentIterationArchiveReadiness:
    if used_capacity is None or capacity_status == "unknown":
        return RequirementCenterCurrentIterationArchiveReadiness(
            display_mode="hidden",
            reason_code="capacity_unknown",
            safe_summary="当前迭代容量待核实，归档入口暂不展示。",
        )
    if used_capacity <= 0:
        return RequirementCenterCurrentIterationArchiveReadiness(
            display_mode="hidden",
            reason_code="capacity_zero",
            safe_summary="当前迭代尚未消耗容量，归档入口暂不展示。",
        )

    blockers = _sprint_archive_blockers(sprint_id, sprint)
    if blockers:
        reason = "missing_signoff" if all(blocker.type == "acceptance_report" for blocker in blockers) else "unarchived_scope"
        return RequirementCenterCurrentIterationArchiveReadiness(
            display_mode="disabled",
            reason_code=reason,  # type: ignore[arg-type]
            safe_summary=_archive_safe_summary(blockers),
            blockers=blockers,
        )

    return RequirementCenterCurrentIterationArchiveReadiness(
        can_enter_confirmation=True,
        display_mode="enabled",
        reason_code="ready",
        safe_summary="范围内 REQ、BUG 与独立 Change 均已归档闭环，验收 sign-off、权限与 Workflow Sync 将在 Sprint archive 确认流程中继续复核。",
    )


def _sprint_archive_blockers(sprint_id: str, sprint: dict[str, Any]) -> list[RequirementCenterArchiveReadinessBlocker]:
    blockers: list[RequirementCenterArchiveReadinessBlocker] = []
    for issue_id in _sprint_scope_ids(sprint.get("requirements")):
        status = _governance_issue_status("requirement", issue_id)
        if status not in {"archived", "done", "closed"}:
            blockers.append(
                RequirementCenterArchiveReadinessBlocker(
                    type="requirement",
                    id=issue_id,
                    status=status or "unknown",
                    message="范围内需求尚未归档闭环",
                    action_hint=f"/req-review {issue_id}",
                )
            )
    for issue_id in _sprint_scope_ids(sprint.get("bugs")):
        status = _governance_issue_status("bug", issue_id)
        if status not in {"archived", "done", "closed"}:
            blockers.append(
                RequirementCenterArchiveReadinessBlocker(
                    type="bug",
                    id=issue_id,
                    status=status or "unknown",
                    message="范围内 BUG 尚未归档闭环",
                    action_hint=f"/bug-review {issue_id}",
                )
            )
    for change_id in _sprint_scope_ids(sprint.get("changes")):
        status = _change_status([change_id]) or "unknown"
        if status != "archived":
            blockers.append(
                RequirementCenterArchiveReadinessBlocker(
                    type="change",
                    id=change_id,
                    status=status,
                    message="范围内 Change 尚未归档闭环",
                    action_hint=f"/opsx-archive {change_id}",
                )
            )
    if not _sprint_acceptance_signed_off(sprint_id):
        blockers.append(
            RequirementCenterArchiveReadinessBlocker(
                type="acceptance_report",
                id=sprint_id,
                status="missing_signoff",
                message="验收报告尚未完成 sign-off",
                action_hint=f"/sprint-archive {sprint_id}",
            )
        )
    return blockers


def _sprint_scope_ids(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    ids: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            ids.append(item.strip())
        elif isinstance(item, dict):
            raw = item.get("id") or item.get("change") or item.get("change_id")
            if raw:
                ids.append(str(raw).strip())
    return [item for item in ids if item]


def _governance_issue_status(issue_type: str, issue_id: str) -> str | None:
    folder = "requirements" if issue_type == "requirement" else "bugs"
    registry = _read_yaml(_governance_root() / "issues" / folder / "_registry.yaml")
    entries = registry.get("entries", []) if isinstance(registry, dict) else []
    for entry in entries:
        if not isinstance(entry, dict) or str(entry.get("id") or "") != issue_id:
            continue
        issue_dir = _safe_issue_dir(entry.get("path"))
        trace = _frontmatter(issue_dir / "trace.md") if issue_dir else {}
        return str(trace.get("status") or entry.get("status") or "unknown")
    return None


def _sprint_acceptance_signed_off(sprint_id: str) -> bool:
    report_path = _governance_root() / "iterations" / "change" / sprint_id / "acceptance-report.md"
    if not report_path.exists():
        return False
    frontmatter = _frontmatter(report_path)
    for key in ("signed_off", "signoff", "sign_off", "acceptance_signed_off"):
        value = frontmatter.get(key)
        if value is True or str(value).strip().lower() in {"true", "yes", "passed", "approved", "signed"}:
            return True
    try:
        text = report_path.read_text(encoding="utf-8").lower()
    except OSError:
        return False
    if re.search(r"(signed[_ -]?off|sign[_ -]?off|验收\s*签署|人工\s*sign-off)\s*[:：]\s*(true|yes|passed|approved|signed|已完成|通过)", text):
        return True
    return False


def _archive_safe_summary(blockers: list[RequirementCenterArchiveReadinessBlocker]) -> str:
    counts: dict[str, int] = {}
    for blocker in blockers:
        counts[blocker.type] = counts.get(blocker.type, 0) + 1
    parts = []
    labels = {
        "requirement": "REQ",
        "bug": "BUG",
        "change": "Change",
        "acceptance_report": "验收 sign-off",
        "permission": "权限",
        "workflow_sync": "Workflow Sync",
        "capacity": "容量",
    }
    for kind in ("requirement", "bug", "change", "acceptance_report", "permission", "workflow_sync", "capacity"):
        if counts.get(kind):
            parts.append(f"{labels[kind]} {counts[kind]} 项")
    return "Sprint archive readiness 未通过：" + "、".join(parts) + " 未闭环。"


def _sum_scope_estimates(value: Any) -> float | None:
    if not isinstance(value, list):
        return None
    total = 0.0
    for item in value:
        if not isinstance(item, dict):
            return None
        raw = item.get("estimated_person_days")
        if not isinstance(raw, (int, float)) or raw < 0:
            return None
        total += float(raw)
    return total


def _capacity_status(used: float | None, total: float | None) -> str:
    if used is None or total is None or total <= 0:
        return "unknown"
    ratio = used / total
    if ratio > 1:
        return "over_limit"
    if ratio >= 0.8:
        return "near_limit"
    return "normal"


def read_requirement_center_document(issue_id: str, document_name: str) -> tuple[str, str]:
    nested_prototype = document_name.startswith("prototype/") and document_name.endswith(".html")
    if Path(document_name).name != document_name and not nested_prototype:
        raise PermissionError("invalid document name")
    suffix = Path(document_name).suffix.lower()
    if suffix not in {".md", ".html"}:
        raise ValueError("unsupported document type")
    issue_dir = _find_issue_dir(issue_id)
    if issue_dir is None:
        raise FileNotFoundError("issue not found")
    if nested_prototype and (not issue_id.startswith("REQ-") or document_name not in _prototype_documents(issue_dir)):
        raise FileNotFoundError("prototype not found")
    if document_name == "sprint.md":
        target = _issue_sprint_document(issue_id, issue_dir)
        if target is None:
            raise FileNotFoundError("associated sprint document not found")
        return target.read_text(encoding="utf-8"), suffix
    target = (issue_dir / document_name).resolve()
    try:
        target.relative_to(issue_dir.resolve())
    except ValueError as exc:
        raise PermissionError("invalid document path") from exc
    if not target.exists() or not target.is_file():
        raise FileNotFoundError("document not found")
    return target.read_text(encoding="utf-8"), suffix


def read_requirement_center_change_document(change_id: str, document_name: str) -> tuple[str, str]:
    if Path(document_name).name != document_name:
        raise PermissionError("invalid document name")
    if Path(document_name).suffix.lower() != ".md":
        raise ValueError("unsupported document type")
    if document_name == "sprint.md":
        from app.governance.change_index import ChangeIndex
        index = ChangeIndex(_governance_root())
        record = index.records.get(change_id)
        target = index.sprint_document(record) if record else None
        if target is None:
            raise FileNotFoundError("associated sprint document not found")
        return target.read_text(encoding="utf-8"), ".md"
    if document_name == "spec.md":
        spec_paths = _change_spec_paths(change_id)
        if not spec_paths:
            raise FileNotFoundError("spec document not found")
        if len(spec_paths) > 1:
            sections = [
                f"<!-- source: {path.parent.name}/spec.md -->\n{path.read_text(encoding='utf-8').strip()}"
                for path in spec_paths
            ]
            return "\n\n---\n\n".join(sections), ".md"
    target = _change_document_path(change_id, document_name)
    if not target.exists() or not target.is_file():
        raise FileNotFoundError("document not found")
    return target.read_text(encoding="utf-8"), ".md"


def update_requirement_center_document(issue_id: str, document_name: str, content: str) -> str:
    if Path(document_name).name != document_name:
        raise PermissionError("invalid document name")
    issue_dir = _find_issue_dir(issue_id)
    if issue_dir is None:
        raise FileNotFoundError("issue not found")
    documents = _document_names(issue_dir)
    if document_name not in documents:
        raise FileNotFoundError("document not found")
    stage = _issue_stage(issue_id, issue_dir, documents)
    issue_type = "requirement" if issue_id.startswith("REQ-") else "bug"
    capability = compute_document_capability(
        issue_type=issue_type,
        stage=stage,
        document_name=document_name,
        path_category="issue",
        exists=True,
    )
    if not capability.human_editable:
        raise PermissionError(capability.reason)
    if stage != "capture":
        allowed = compute_document_capability(
            issue_type=issue_type,
            stage=stage,
            document_name=document_name,
            path_category="issue",
            exists=True,
        )
        if not allowed.human_editable:
            raise PermissionError(allowed.reason)
    target = (issue_dir / document_name).resolve()
    try:
        target.relative_to(issue_dir.resolve())
    except ValueError as exc:
        raise PermissionError("invalid document path") from exc
    if not target.exists() or not target.is_file():
        raise FileNotFoundError("document not found")
    target.write_text(content, encoding="utf-8")
    return content


def update_requirement_center_change_document(change_id: str, document_name: str, content: str, *, task_toggle: bool = False) -> str:
    if Path(document_name).name != document_name:
        raise PermissionError("invalid document name")
    stage = _change_stage(change_id)
    capability = compute_document_capability(
        issue_type=_change_issue_type(change_id),
        stage=stage,
        document_name=document_name,
        path_category="change",
        exists=True,
    )
    if task_toggle:
        if not capability.task_toggle_only:
            raise PermissionError(capability.reason)
        target = _change_document_path(change_id, document_name)
        if not target.exists() or not target.is_file():
            raise FileNotFoundError("document not found")
        current = target.read_text(encoding="utf-8")
        if not _is_task_toggle_only_change(current, content):
            raise PermissionError("验收中 tasks.md 仅允许切换任务勾选状态")
    elif not capability.human_editable:
        raise PermissionError(capability.reason)
    if document_name == "spec.md":
        return _write_change_spec_document(change_id, content)
    target = _change_document_path(change_id, document_name)
    if not target.exists() or not target.is_file():
        raise FileNotFoundError("document not found")
    target.write_text(content, encoding="utf-8")
    return content


def _change_document_path(change_id: str, document_name: str) -> Path:
    change_dir = _change_dir(change_id)
    if document_name == "spec.md":
        spec_paths = _change_spec_paths(change_id)
        if len(spec_paths) != 1:
            if spec_paths:
                raise PermissionError("多个 delta spec 需通过治理命令或具体文件入口修改")
            raise FileNotFoundError("spec document not found")
        return spec_paths[0].resolve()
    target = (change_dir / document_name).resolve()
    try:
        target.relative_to(change_dir)
    except ValueError as exc:
        raise PermissionError("invalid document path") from exc
    return target


@_memoized_read
def _change_spec_paths(change_id: str) -> list[Path]:
    change_dir = _change_dir(change_id)
    return sorted((change_dir / "specs").glob("*/spec.md"))


def _write_change_spec_document(change_id: str, content: str) -> str:
    spec_paths = _change_spec_paths(change_id)
    if not spec_paths:
        raise FileNotFoundError("spec document not found")
    if len(spec_paths) == 1:
        spec_paths[0].write_text(content, encoding="utf-8")
        return content
    sections = content.split("\n\n---\n\n")
    if len(sections) != len(spec_paths):
        raise PermissionError("多个 delta spec 保存必须保留 source 标记和分隔线")
    for section, path in zip(sections, spec_paths):
        marker = f"<!-- source: {path.parent.name}/spec.md -->"
        lines = section.splitlines()
        if not lines or lines[0].strip() != marker:
            raise PermissionError("多个 delta spec 保存必须保留 source 标记")
        body = "\n".join(lines[1:]).strip()
        path.write_text(f"{body}\n", encoding="utf-8")
    return content


def _change_stage(change_id: str) -> str:
    status = _change_status([change_id]) or "proposed"
    return STAGES.get(str(status), "ready-dev")


def _change_issue_type(change_id: str) -> str:
    trace = _frontmatter(_change_dir(change_id) / "trace.md")
    source = str(trace.get("requirement") or trace.get("bug") or trace.get("source_requirement") or trace.get("source_bug") or "")
    return "bug" if source.startswith("BUG-") else "requirement"


@_memoized_read
def _change_dir(change_id: str) -> Path:
    change_root = (_governance_root() / "openspec" / "changes").resolve()
    change_dir = (change_root / change_id).resolve()
    try:
        change_dir.relative_to(change_root)
    except ValueError as exc:
        raise PermissionError("invalid change path") from exc
    if change_dir.is_dir():
        return change_dir
    archive_root = (_governance_root() / "openspec" / "archive").resolve()
    # Full dated folder suffix, never a fuzzy or short-ID match.
    matches = [path.resolve() for path in archive_root.glob("*")
               if path.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}-" + re.escape(change_id), path.name)
               and path.resolve().parent == archive_root]
    return matches[0] if len(matches) == 1 else change_dir


def _is_task_toggle_only_change(original: str, updated: str) -> bool:
    original_lines = original.splitlines(keepends=True)
    updated_lines = updated.splitlines(keepends=True)
    if len(original_lines) != len(updated_lines):
        return False
    changed = False
    for before, after in zip(original_lines, updated_lines):
        if before == after:
            continue
        before_body = before.rstrip("\r\n")
        after_body = after.rstrip("\r\n")
        before_match = TASK_MARKER_RE.match(before_body)
        after_match = TASK_MARKER_RE.match(after_body)
        if not before_match or not after_match:
            return False
        if before_match.group(1) != after_match.group(1) or before_match.group(3) != after_match.group(3):
            return False
        if before[len(before_body) :] != after[len(after_body) :]:
            return False
        changed = True
    return changed


def _issue_stage(issue_id: str, issue_dir: Path, documents: list[str]) -> str:
    issue_type = "requirements" if issue_id.startswith("REQ-") else "bugs"
    registry = _read_yaml(_governance_root() / "issues" / issue_type / "_registry.yaml")
    trace = _frontmatter(issue_dir / "trace.md")
    entry = next(
        (item for item in registry.get("entries", []) if isinstance(item, dict) and str(item.get("id")) == issue_id),
        {},
    )
    changes = _linked_changes(entry, trace) if isinstance(entry, dict) else []
    status = _issue_status(entry, trace, changes)
    return _map_stage(str(status), documents, changes)


def _find_issue_dir(issue_id: str) -> Path | None:
    issue_type = "requirements" if issue_id.startswith("REQ-") else "bugs"
    registry = _read_yaml(_governance_root() / "issues" / issue_type / "_registry.yaml")
    for entry in registry.get("entries", []) if isinstance(registry, dict) else []:
        if isinstance(entry, dict) and str(entry.get("id")) == issue_id:
            return _safe_issue_dir(entry.get("path"))
    return None


def _required_action_documents(stage: str, issue_type: str) -> list[str]:
    requirement_documents = ["capture.md", "trace.md", "requirement.md", "acceptance.md", "business-flow.md", "user-stories.md"]
    bug_documents = ["capture.md", "trace.md", "bug.md", "root-cause.md", "workaround.md", "acceptance.md"]
    if stage == "capture":
        return ["trace.md", "capture.md"]
    if stage == "planning":
        return ["trace.md", "capture.md", "requirement.md" if issue_type == "requirement" else "bug.md"]
    return {
        "review-ready": requirement_documents if issue_type == "requirement" else bug_documents,
        "approved": [*requirement_documents, "review.md"] if issue_type == "requirement" else [*bug_documents, "review.md"],
        "ready-dev": ["proposal.md", "tasks.md", "trace.md"],
        "acceptance": ["acceptance.md", "trace.md"],
    }.get(stage, [])


def _empty_documents(issue_dir: Path | None, required: list[str]) -> list[str]:
    if not issue_dir:
        return required
    empty: list[str] = []
    for name in required:
        target = (issue_dir / name).resolve()
        try:
            target.relative_to(issue_dir.resolve())
        except ValueError:
            empty.append(name)
            continue
        if not target.exists() or not target.is_file():
            continue
        if not target.read_text(encoding="utf-8").strip():
            empty.append(name)
    return empty


def _blocked_reason(stage: str, issue_type: str, documents: list[str], warnings: list[str], issue_dir: Path | None) -> str | None:
    required = _required_action_documents(stage, issue_type)
    missing = [doc for doc in required if doc not in documents]
    if missing:
        return f"缺少 {', '.join(missing)}"
    empty = _empty_documents(issue_dir, required)
    if empty:
        return f"文档内容为空：{', '.join(empty)}"
    if warnings and stage != "done":
        return "存在数据漂移"
    return None


def _test_progress(documents: list[str], stage: str) -> tuple[int, int] | None:
    if stage != "acceptance":
        return None
    done = sum(1 for doc in ("acceptance.md", "review.md", "trace.md") if doc in documents)
    return (done, 3)


def _owner_name(value: Any) -> str:
    mapping = {
        "product": "产品团队",
        "user": "用户反馈",
        "null": "未分配",
        "None": "未分配",
    }
    return mapping.get(str(value), str(value or "未分配"))


def _updated_at(value: Any) -> str:
    if isinstance(value, datetime):
        return value.strftime("%y/%m/%d %H:%M")
    if not isinstance(value, str) or not re.match(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}", value.strip()):
        return "更新时间未知"
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return "更新时间未知"
    return parsed.strftime("%y/%m/%d %H:%M")


def _short_id(issue_id: str) -> str:
    parts = issue_id.split("-")
    return "-".join(parts[:2]) if len(parts) >= 2 else issue_id


def _context_user(user: dict[str, Any] | None) -> RequirementCenterUser:
    if not user:
        return RequirementCenterUser(
            name="未登录",
            avatar_initial="未",
            avatar_url=None,
            can_access_admin=False,
            permissions=["requirement:read"],
        )
    display_name = str(user.get("nickname") or user.get("username") or "MoonBox 用户")
    can_access_admin = str(user.get("role")) == "后台管理员" or bool(user.get("is_system_superadmin"))
    return RequirementCenterUser(
        name=display_name,
        avatar_initial=display_name[:1].upper(),
        avatar_url=user.get("avatar_url"),
        can_access_admin=can_access_admin,
        permissions=["requirement:read", "bug:read", "sprint:read", "openspec:read", *([] if not can_access_admin else ["admin:access"])],
    )
