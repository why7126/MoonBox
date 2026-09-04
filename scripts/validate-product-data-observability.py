#!/usr/bin/env python3
"""
校验 MoonBox 产品数据采集与链路观测治理门禁。

默认检查标准文档、入口规则和技能是否接入门禁；传入 --change、--sprint
或 --diff 时，额外检查命中触发范围的目标文档是否包含固定声明。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STANDARD = "docs/standards/product-data-collection-observability.md"
TASK_TRACE = "docs/standards/task-trace-coverage.md"
DECLARATION = "product_data_collection_observability"

ENTRY_FILES = [
    "AGENTS.md",
    "docs/standards/api-governance.md",
    "rules/api.md",
    "rules/database.md",
    "rules/testing.md",
    "rules/requirement-management.md",
    "rules/iterations-lifecycle.md",
]

SKILL_FILES = [
    ".agents/skills/req-complete/SKILL.md",
    ".agents/skills/req-review/SKILL.md",
    ".agents/skills/req-opsx/SKILL.md",
    ".agents/skills/opsx-apply/SKILL.md",
    ".agents/skills/opsx-propose/SKILL.md",
    ".agents/skills/opsx-archive/SKILL.md",
    ".agents/skills/sprint-propose/SKILL.md",
    ".agents/skills/sprint-apply/SKILL.md",
    ".agents/skills/sprint-archive/SKILL.md",
]

STANDARD_TERMS = [
    "usage_events",
    "request_logs",
    "task_traces",
    "task_trace_spans",
    "behavior_trace_id",
    "behavior_event_id",
    "parent_behavior_event_id",
    "request_id",
    "client_request_id",
    "Task Trace 分级覆盖",
    "保留周期",
    "Authorization",
    "Cookie",
    "Token",
    "完整请求体",
    "完整响应体",
    "本机绝对路径",
    "真实客户敏感数据",
]

ENTRY_TERM_GROUPS = [
    [STANDARD],
    [DECLARATION],
    ["affected_layers", "适用层级"],
    ["reason", "原因"],
    ["validation", "验证", "验收"],
    ["N/A", "not_applicable", "不适用"],
]

PATH_TRIGGERS = [
    "src/backend/app/api/",
    "src/backend/app/schemas/",
    "src/backend/app/repositories/",
    "src/backend/app/services/",
    "src/backend/app/db/",
    "src/web/src/services/",
    "src/web/src/api/",
    "src/web/src/shared/api/",
    "request",
    "usage",
    "trace",
    "audit",
    "observability",
]

TEXT_TRIGGERS = [
    "API",
    "DB",
    "数据库",
    "日志审计",
    "行为埋点",
    "请求封装",
    "链路 ID",
    "Task Trace",
    "request_logs",
    "usage_events",
    "task_traces",
    "task_trace_spans",
    "behavior_trace_id",
    "behavior_event_id",
    "client_request_id",
    "request_id",
    "保留周期",
    "脱敏",
    "OpenAPI",
    "Orval",
]

BAD_NA_REASONS = {"无", "不涉及", "none", "n/a", "na", "N/A"}


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def markdown_files(base: Path) -> list[Path]:
    if not base.exists():
        return []
    return sorted(path for path in base.rglob("*.md") if "__pycache__" not in path.parts)


def validate_standard() -> list[str]:
    errors: list[str] = []
    for item in (STANDARD, TASK_TRACE):
        if not (ROOT / item).exists():
            errors.append(f"缺少标准文件: {item}")
    if (ROOT / STANDARD).exists():
        text = read(ROOT / STANDARD)
        for term in STANDARD_TERMS:
            if term not in text:
                errors.append(f"{STANDARD} 缺少关键内容: {term}")
    if (ROOT / TASK_TRACE).exists() and STANDARD not in read(ROOT / TASK_TRACE):
        errors.append(f"{TASK_TRACE} 缺少对 {STANDARD} 的引用")
    return errors


def validate_entry_files() -> list[str]:
    errors: list[str] = []
    for item in ENTRY_FILES + SKILL_FILES:
        path = ROOT / item
        if not path.exists():
            errors.append(f"{item}: 缺少门禁入口文件")
            continue
        text = read(path)
        missing = ["/".join(group) for group in ENTRY_TERM_GROUPS if not any(term in text for term in group)]
        if missing:
            errors.append(f"{item}: 缺少采集门禁关键内容: {', '.join(missing)}")
    return errors


def collect_change(change_id: str) -> tuple[str, list[Path]]:
    return f"change:{change_id}", markdown_files(ROOT / "openspec" / "changes" / change_id)


def collect_sprint(sprint_id: str) -> tuple[str, list[Path]]:
    files: list[Path] = []
    linked_changes: set[str] = set()
    for stage in ("change", "archive"):
        base = ROOT / "iterations" / stage / sprint_id
        files.extend(markdown_files(base))
        yaml_path = base / "sprint.yaml"
        if yaml_path.exists():
            files.append(yaml_path)
            for line in read(yaml_path).splitlines():
                stripped = line.strip()
                if stripped.startswith("- ") and not stripped.startswith("- REQ-") and not stripped.startswith("- BUG-"):
                    item = stripped[2:].strip()
                    if item and "/" not in item and " " not in item:
                        linked_changes.add(item)
    for change_id in sorted(linked_changes):
        files.extend(markdown_files(ROOT / "openspec" / "changes" / change_id))
    return f"sprint:{sprint_id}", sorted(set(files))


def collect_diff() -> tuple[str, list[Path]]:
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    files: list[Path] = []
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            path = ROOT / line.strip()
            if path.exists() and path.is_file() and path.suffix in {".md", ".py", ".ts", ".tsx", ".js", ".json", ".yaml", ".yml"}:
                files.append(path)
    return "diff:working-tree", sorted(files)


def validate_target(label: str, files: list[Path]) -> list[str]:
    errors: list[str] = []
    if not files:
        errors.append(f"{label}: 未找到可校验目标文件")
        return errors

    text_chunks: list[str] = []
    trigger_hits: list[str] = []
    for path in files:
        relative = rel(path)
        path_hits = [trigger for trigger in PATH_TRIGGERS if trigger in relative]
        if path_hits:
            trigger_hits.append(f"{relative}:path:{'|'.join(path_hits)}")
        text = read(path)
        text_chunks.append(text)
        for trigger in TEXT_TRIGGERS:
            if trigger in text:
                trigger_hits.append(f"{relative}:text:{trigger}")

    if not trigger_hits:
        return errors

    combined = "\n".join(text_chunks)
    if DECLARATION not in combined:
        errors.append(f"{label}: 命中采集规范触发范围但缺少 `{DECLARATION}` 声明")
        return errors
    for term in ("affected_layers", "reason", "validation"):
        if term not in combined:
            errors.append(f"{label}: `{DECLARATION}` 声明缺少 `{term}`")
    errors.extend(validate_na_reason(label, combined))
    return errors


def validate_na_reason(label: str, text: str) -> list[str]:
    errors: list[str] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if "status:" not in stripped or "not_applicable" not in stripped:
            continue
        reason = ""
        for follow in lines[index + 1 : index + 8]:
            if follow.strip().startswith("reason:"):
                reason = follow.split(":", 1)[1].strip().strip("\"'")
                break
        if not reason or reason in BAD_NA_REASONS or len(reason) < 8:
            errors.append(f"{label}: N/A 声明缺少可审计 reason")
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="校验产品数据采集与链路观测治理门禁")
    parser.add_argument("--change", help="聚焦校验 active OpenSpec Change")
    parser.add_argument("--sprint", help="聚焦校验 Sprint 四件套")
    parser.add_argument("--diff", action="store_true", help="聚焦校验当前 working tree diff 涉及文件")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    errors = validate_standard()
    errors.extend(validate_entry_files())

    targets: list[tuple[str, list[Path]]] = []
    if args.change:
        targets.append(collect_change(args.change))
    if args.sprint:
        targets.append(collect_sprint(args.sprint))
    if args.diff:
        targets.append(collect_diff())

    for label, files in targets:
        errors.extend(validate_target(label, files))

    if errors:
        print("产品数据采集与链路观测门禁校验失败：")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("产品数据采集与链路观测门禁校验通过。")
    print(f"- entry_files: {len(ENTRY_FILES)}")
    print(f"- skill_files: {len(SKILL_FILES)}")
    print(f"- focused_targets: {len(targets)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
