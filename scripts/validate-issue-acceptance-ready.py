#!/usr/bin/env python3
"""Block Issue-linked Change archiving until its Issue acceptance is signed off."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("frontmatter_missing")
    _, raw, _ = text.split("---", 2)
    value = yaml.safe_load(raw)
    if not isinstance(value, dict):
        raise ValueError("frontmatter_invalid")
    return value


def readiness(root: Path, change: str) -> tuple[bool, str]:
    active = root / "openspec" / "changes" / change
    archive_roots = (root / "openspec" / "archive",
                     root / "openspec" / "changes" / "archive")
    archived = [path for archive_root in archive_roots
                for path in archive_root.glob(f"????-??-??-{change}")
                if path.is_dir() and not path.is_symlink()]
    if active.exists():
        if archived:
            return False, "change_identity_ambiguous"
        trace = active / "trace.md"
    else:
        if len(archived) > 1:
            return False, "change_identity_ambiguous"
        trace = archived[0] / "trace.md" if archived else active / "trace.md"
    if not trace.is_file():
        return False, "change_trace_missing"
    try:
        metadata = frontmatter(trace)
        issue = (metadata.get("bug") or metadata.get("requirement")
                 or metadata.get("bug_id") or metadata.get("requirement_id")
                 or metadata.get("source_bug") or metadata.get("source_requirement"))
    except (OSError, ValueError, yaml.YAMLError):
        return False, "change_trace_invalid"
    if not issue:
        return True, "standalone_change"
    if not isinstance(issue, str) or not re.fullmatch(r"(?:BUG|REQ)-\d{4}-[a-z0-9-]+", issue):
        return False, "issue_identity_invalid"
    domain = "bugs" if issue.startswith("BUG-") else "requirements"
    found = [root / "issues" / domain / stage / issue / "acceptance.md" for stage in ("plan", "review", "archive")]
    found = [path for path in found if path.is_file()]
    if len(found) != 1:
        return False, "issue_acceptance_missing_or_ambiguous"
    try:
        text = found[0].read_text(encoding="utf-8")
        status = frontmatter(found[0]).get("acceptance_status")
    except (OSError, ValueError, yaml.YAMLError):
        return False, "issue_acceptance_invalid"
    checks = re.findall(r"^- \[([ xX])\] AC-[A-Za-z0-9-]+\b", text, re.MULTILINE)
    if status != "passed" or not checks or any(mark == " " for mark in checks):
        return False, f"issue_acceptance_pending checked={sum(mark != ' ' for mark in checks)} total={len(checks)}"
    return True, "issue_acceptance_passed"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("change")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    ready, reason = readiness(args.root, args.change)
    print(("ACCEPTANCE_GATE_READY" if ready else "ACCEPTANCE_GATE_BLOCKED") + " " + reason)
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
