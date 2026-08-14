from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
from typing import Any

import yaml

from app.schemas.requirement_center import (
    RequirementCenterContext,
    RequirementCenterIssue,
    RequirementCenterStats,
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


def build_requirement_center_context(current_user: dict[str, Any] | None = None) -> RequirementCenterContext:
    issues = _load_issues("requirement") + _load_issues("bug")
    issues.sort(key=lambda item: item.updated_at, reverse=True)
    stats = RequirementCenterStats(
        total=len(issues),
        requirements=sum(1 for item in issues if item.type == "requirement"),
        bugs=sum(1 for item in issues if item.type == "bug"),
        blocked=sum(1 for item in issues if item.blocked),
        drift=sum(1 for item in issues if item.drift_warnings),
    )
    workspaces = _load_workspaces(issues, current_user)
    return RequirementCenterContext(
        issues=issues,
        workspaces=workspaces,
        current_user=_context_user(current_user),
        selected_workspace_id=workspaces[0].workspace_id,
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
    documents = sorted(path.name for path in issue_dir.glob("*.md")) if issue_dir and issue_dir.exists() else []
    changes = _linked_changes(entry, trace)
    task_progress = _change_task_progress(changes)
    sprint_id = entry.get("target_iteration") or entry.get("iteration") or trace.get("iteration")
    status = _change_status(changes) or trace.get("status") or entry.get("status") or "captured"
    stage = _map_stage(str(status), documents, changes)
    warnings = _drift_warnings(entry, trace, issue_dir, sprint_id)
    blocked = _blocked_reason(stage, issue_type, documents, warnings)
    return RequirementCenterIssue(
        id=_short_id(issue_id),
        type=issue_type,
        title=str(entry.get("title") or issue_id),
        priority=str(entry.get("priority") or "P2"),
        owner=_owner_name(entry.get("owner") or entry.get("requester") or entry.get("reporter")),
        source=str(entry.get("lifecycle_stage") or entry.get("status") or "registry"),
        stage=stage,
        documents=documents,
        updated_at=_updated_at(trace.get("updated_at") or entry.get("created")),
        blocked=blocked,
        sprint_id=str(sprint_id) if sprint_id else None,
        task_progress=task_progress,
        test_progress=_test_progress(documents, stage),
        manual_acceptance_count=0,
        drift_warnings=warnings,
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


def _load_workspaces(issues: list[RequirementCenterIssue], current_user: dict[str, Any] | None) -> list[RequirementCenterWorkspace]:
    project = _read_yaml(GOVERNANCE_ROOT / "project.yaml").get("project", {})
    if not isinstance(project, dict):
        project = {}
    name = str(project.get("name") or project.get("code") or "MoonBox").strip()
    code = str(project.get("code") or name).strip()
    owner = str(project.get("owner") or "MoonBox 产品团队").strip()
    description = str(project.get("description") or "当前项目治理工作空间").strip()
    workspace_id = _workspace_id(code)
    member_count = _workspace_member_count(issues, current_user)
    role = _workspace_role(current_user)
    return [
        RequirementCenterWorkspace(
            organization_name=owner,
            workspace_id=workspace_id,
            name=name,
            slug=workspace_id,
            description=description,
            timezone=os.environ.get("TZ", "Asia/Shanghai"),
            member_count=member_count,
            role=role,
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


def _change_task_progress(changes: list[str]) -> tuple[int, int] | None:
    total_done = 0
    total = 0
    for change in changes:
        tasks_path = GOVERNANCE_ROOT / "openspec" / "changes" / change / "tasks.md"
        if not tasks_path.exists():
            continue
        for line in tasks_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped.startswith("- ["):
                continue
            total += 1
            if stripped.startswith("- [x]"):
                total_done += 1
    return (total_done, total) if total else None


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
