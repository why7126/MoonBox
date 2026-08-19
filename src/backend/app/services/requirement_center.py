from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session
import yaml

from app.schemas.requirement_center import (
    RequirementCenterAction,
    RequirementCenterContext,
    RequirementCenterDocument,
    RequirementCenterIssue,
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


def build_requirement_center_context(
    current_user: dict[str, Any] | None = None,
    db: Session | None = None,
) -> RequirementCenterContext:
    issues = _load_issues("requirement") + _load_issues("bug")
    issues.sort(key=lambda item: item.updated_at, reverse=True)
    stats = RequirementCenterStats(
        total=len(issues),
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
        sprint_options=_load_open_sprints(),
        stats=stats,
    )


def _load_issues(issue_type: str) -> list[RequirementCenterIssue]:
    registry_path = GOVERNANCE_ROOT / "issues" / ("requirements" if issue_type == "requirement" else "bugs") / "_registry.yaml"
    if not registry_path.exists():
        raise FileNotFoundError(f"requirement center registry missing: {issue_type}")
    registry = _read_yaml(registry_path)
    entries = registry.get("entries", []) if isinstance(registry, dict) else []
    return [_build_issue(issue_type, entry) for entry in entries if isinstance(entry, dict)]


def _build_issue(issue_type: str, entry: dict[str, Any]) -> RequirementCenterIssue:
    issue_id = str(entry.get("id", "")).strip()
    issue_dir = _safe_issue_dir(entry.get("path"))
    trace = _frontmatter(issue_dir / "trace.md") if issue_dir else {}
    documents = _document_names(issue_dir)
    changes = _linked_changes(entry, trace)
    tasks = _change_tasks(changes)
    task_progress = (tasks.done, tasks.total) if tasks and tasks.total else None
    raw_sprint_id = entry.get("target_iteration") or entry.get("iteration") or trace.get("iteration")
    status = _change_status(changes) or trace.get("status") or entry.get("status") or "captured"
    stage = _map_stage(str(status), documents, changes)
    sprint_id = raw_sprint_id if _should_show_sprint(stage) else None
    warnings = _drift_warnings(entry, trace, issue_dir, raw_sprint_id)
    blocked = _blocked_reason(stage, issue_type, documents, warnings)
    detail_url = _detail_url(issue_id)
    return RequirementCenterIssue(
        id=_short_id(issue_id),
        type=issue_type,
        title=str(entry.get("title") or issue_id),
        priority=str(entry.get("priority") or "P2"),
        owner=_owner_name(entry.get("owner") or entry.get("requester") or entry.get("reporter")),
        source=str(entry.get("lifecycle_stage") or entry.get("status") or "registry"),
        stage=stage,
        documents=documents,
        document_entries=_document_entries(issue_id, documents, stage),
        detail_url=detail_url,
        archive_url=detail_url if stage == "done" else None,
        action=_stage_action(issue_id, issue_type, stage, blocked),
        tasks=tasks,
        updated_at=_updated_at(trace.get("updated_at") or entry.get("created")),
        blocked=blocked,
        sprint_id=str(sprint_id) if sprint_id else None,
        task_progress=task_progress,
        test_progress=_test_progress(documents, stage),
        manual_acceptance_count=0,
        drift_warnings=warnings,
    )


def _should_show_sprint(stage: str) -> bool:
    return stage in SPRINT_VISIBLE_STAGES


def _document_names(issue_dir: Path | None) -> list[str]:
    if not issue_dir or not issue_dir.exists():
        return []
    names = [path.name for path in issue_dir.iterdir() if path.is_file() and path.suffix.lower() in {".md", ".html"}]
    return sorted(names)


def _document_entries(issue_id: str, documents: list[str], stage: str) -> list[RequirementCenterDocument]:
    entries: list[RequirementCenterDocument] = []
    for name in documents:
        suffix = Path(name).suffix.lower()
        if suffix == ".md":
            entries.append(
                RequirementCenterDocument(
                    name=name,
                    type="markdown",
                    open_mode="drawer",
                    label=name,
                    url=f"/api/v1/requirement-center/issues/{issue_id}/documents/{name}",
                    editable=stage == "capture" and name == "capture.md",
                )
            )
        elif suffix == ".html":
            entries.append(
                RequirementCenterDocument(
                    name=name,
                    type="html",
                    open_mode="new-tab",
                    label=name,
                    url=f"/api/v1/requirement-center/issues/{issue_id}/documents/{name}/preview",
                )
            )
    return entries


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
    candidate = (GOVERNANCE_ROOT / str(raw_path)).resolve()
    try:
        candidate.relative_to(GOVERNANCE_ROOT)
    except ValueError:
        return None
    return candidate


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
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
    project = _read_yaml(GOVERNANCE_ROOT / "project.yaml").get("project", {})
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


def _frontmatter(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    data = yaml.safe_load(parts[1])
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


def _change_tasks(changes: list[str]) -> RequirementCenterTasks | None:
    total_done = 0
    total = 0
    blocked: list[str] = []
    source: str | None = None
    for change in changes:
        tasks_path = GOVERNANCE_ROOT / "openspec" / "changes" / change / "tasks.md"
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


def _change_task_progress(changes: list[str]) -> tuple[int, int] | None:
    tasks = _change_tasks(changes)
    return (tasks.done, tasks.total) if tasks else None


def _change_status(changes: list[str]) -> str | None:
    if not changes:
        return None
    statuses = []
    for change in changes:
        trace = _frontmatter(GOVERNANCE_ROOT / "openspec" / "changes" / change / "trace.md")
        if trace.get("status"):
            statuses.append(str(trace["status"]))
    if "in_progress" in statuses:
        return "in_progress"
    if "applied" in statuses:
        return "applied"
    return statuses[0] if statuses else "proposed"


def _map_stage(status: str, documents: list[str], changes: list[str]) -> str:
    if status == "in_sprint" and changes:
        return "ready-dev"
    if status in {"proposed", "in_sprint"} and changes:
        progress = _change_task_progress(changes)
        if progress and progress[1] > 0 and progress[0] == progress[1]:
            return "acceptance"
        return STAGES.get(status, "ready-dev")
    if status == "captured" and any(doc in documents for doc in ("requirement.md", "bug.md")):
        return "planning"
    return STAGES.get(status, "capture")


def _drift_warnings(entry: dict[str, Any], trace: dict[str, Any], issue_dir: Path | None, sprint_id: Any) -> list[str]:
    warnings: list[str] = []
    if issue_dir and not issue_dir.exists():
        warnings.append("issue_path_missing")
    if sprint_id and not _sprint_contains(str(sprint_id), str(entry.get("id", ""))):
        warnings.append("sprint_scope_mismatch")
    if trace.get("status") and entry.get("status") and trace.get("status") != entry.get("status"):
        warnings.append("registry_trace_status_mismatch")
    return warnings


def _sprint_contains(sprint_id: str, issue_id: str) -> bool:
    sprint = _read_yaml(GOVERNANCE_ROOT / "iterations" / "change" / sprint_id / "sprint.yaml")
    key = "requirements" if issue_id.startswith("REQ-") else "bugs"
    return issue_id in (sprint.get(key) or [])


def _load_open_sprints() -> list[str]:
    base = GOVERNANCE_ROOT / "iterations" / "change"
    if not base.exists():
        return []
    sprints: list[str] = []
    for path in sorted(base.glob("sprint-*")):
        sprint = _read_yaml(path / "sprint.yaml")
        status = str(sprint.get("status") or "").lower()
        if status not in {"closed", "archived", "done"}:
            sprints.append(path.name)
    return sprints


def read_requirement_center_document(issue_id: str, document_name: str) -> tuple[str, str]:
    if Path(document_name).name != document_name:
        raise PermissionError("invalid document name")
    suffix = Path(document_name).suffix.lower()
    if suffix not in {".md", ".html"}:
        raise ValueError("unsupported document type")
    issue_dir = _find_issue_dir(issue_id)
    if issue_dir is None:
        raise FileNotFoundError("issue not found")
    target = (issue_dir / document_name).resolve()
    try:
        target.relative_to(issue_dir.resolve())
    except ValueError as exc:
        raise PermissionError("invalid document path") from exc
    if not target.exists() or not target.is_file():
        raise FileNotFoundError("document not found")
    return target.read_text(encoding="utf-8"), suffix


def update_requirement_center_capture_document(issue_id: str, document_name: str, content: str) -> str:
    if document_name != "capture.md":
        raise PermissionError("only capture.md is editable")
    if Path(document_name).name != document_name:
        raise PermissionError("invalid document name")
    issue_dir = _find_issue_dir(issue_id)
    if issue_dir is None:
        raise FileNotFoundError("issue not found")
    documents = _document_names(issue_dir)
    if document_name not in documents:
        raise FileNotFoundError("document not found")
    stage = _issue_stage(issue_id, issue_dir, documents)
    if stage != "capture":
        raise PermissionError("document is read only outside capture stage")
    target = (issue_dir / document_name).resolve()
    try:
        target.relative_to(issue_dir.resolve())
    except ValueError as exc:
        raise PermissionError("invalid document path") from exc
    if not target.exists() or not target.is_file():
        raise FileNotFoundError("document not found")
    target.write_text(content, encoding="utf-8")
    return content


def _issue_stage(issue_id: str, issue_dir: Path, documents: list[str]) -> str:
    issue_type = "requirements" if issue_id.startswith("REQ-") else "bugs"
    registry = _read_yaml(GOVERNANCE_ROOT / "issues" / issue_type / "_registry.yaml")
    trace = _frontmatter(issue_dir / "trace.md")
    entry = next(
        (item for item in registry.get("entries", []) if isinstance(item, dict) and str(item.get("id")) == issue_id),
        {},
    )
    changes = _linked_changes(entry, trace) if isinstance(entry, dict) else []
    status = _change_status(changes) or trace.get("status") or (entry.get("status") if isinstance(entry, dict) else None) or "captured"
    return _map_stage(str(status), documents, changes)


def _find_issue_dir(issue_id: str) -> Path | None:
    issue_type = "requirements" if issue_id.startswith("REQ-") else "bugs"
    registry = _read_yaml(GOVERNANCE_ROOT / "issues" / issue_type / "_registry.yaml")
    for entry in registry.get("entries", []) if isinstance(registry, dict) else []:
        if isinstance(entry, dict) and str(entry.get("id")) == issue_id:
            return _safe_issue_dir(entry.get("path"))
    return None


def _blocked_reason(stage: str, issue_type: str, documents: list[str], warnings: list[str]) -> str | None:
    required = {
        "review-ready": ["acceptance.md", "trace.md"],
        "ready-dev": ["proposal.md", "tasks.md", "trace.md"],
        "acceptance": ["acceptance.md", "trace.md"],
    }.get(stage, [])
    if stage == "planning":
        required = ["requirement.md" if issue_type == "requirement" else "bug.md", "trace.md"]
    missing = [doc for doc in required if doc not in documents]
    if missing:
        return f"缺少 {', '.join(missing)}"
    if warnings:
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
        return value.strftime("%H:%M")
    if not value:
        return "--:--"
    text = str(value)
    return text[11:16] if len(text) >= 16 else text


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
