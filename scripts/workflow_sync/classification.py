"""Issue 分级：trace 优先解析及聚焦 Frontmatter 同步。"""
from __future__ import annotations

import re
from pathlib import Path

VALUES = {"req": {"P0", "P1", "P2", "P3"}, "bug": {"blocker", "critical", "high", "medium", "low"}}


def resolve_classification(path: Path, kind: str) -> tuple[str, str | None]:
    from .collect import parse_frontmatter_yaml
    key = "priority" if kind == "req" else "severity"
    main = "requirement.md" if kind == "req" else "bug.md"
    for name in ("trace.md", main, "capture.md"):
        file = path / name
        if not file.exists():
            continue
        fm = parse_frontmatter_yaml(file.read_text(encoding="utf-8"))
        for field in (key, key + "_hint"):
            if field in fm:
                value = str(fm[field]).strip()
                if value in VALUES[kind]:
                    return value, None
                return "", f"{path.name}/{name}: invalid {field}; confirm {key}"
    return "", f"{path.name}: missing {key}; confirm classification"


def sync_classification(issue, *, write: bool):
    from .patch import PatchResult, persist_markdown, ROOT
    key = "priority" if issue.kind == "req" else "severity"
    main = "requirement.md" if issue.kind == "req" else "bug.md"
    results = []
    for name in ("trace.md", main, "capture.md"):
        file = issue.path / name
        if not file.exists():
            continue
        original = file.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", original, re.S)
        body = match.group(1) if match else ""
        lines = body.splitlines()
        fields = {"priority", "severity", "priority_hint", "severity_hint"}
        lines = [line for line in lines if not any(line.startswith(f + ":") for f in fields)]
        lines.append(f"{key}: {issue.priority}")
        text = "---\n" + "\n".join(lines) + "\n---\n" + (original[match.end():] if match else original)
        changed = persist_markdown(file, text, original, write)
        results.append(PatchResult(str(file.relative_to(ROOT)), changed, "classification metadata"))
    return results
