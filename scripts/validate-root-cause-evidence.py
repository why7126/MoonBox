#!/usr/bin/env python3
"""Validate root-cause evidence gates for BUGs and BUG-sourced Changes."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUG_ROOTS = [
    ROOT / "issues" / "bugs" / "plan",
    ROOT / "issues" / "bugs" / "review",
    ROOT / "issues" / "bugs" / "archive",
    ROOT / "issues" / "bugs",
]
CHANGE_ROOT = ROOT / "openspec" / "changes"

VALID_STATUSES = {"unknown", "hypothesis", "probable", "confirmed"}
EVIDENCE_TYPES = {
    "reproduction",
    "test_failure",
    "runtime_log",
    "browser_console",
    "network_request",
    "screenshot",
    "computed_style",
    "data_sample",
    "config_diff",
    "code_path",
}


@dataclass
class CheckResult:
    target: str
    status: str
    path: str | None = None
    root_cause_status: str | None = None
    evidence_count: int = 0
    messages: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "target": self.target,
            "status": self.status,
            "path": self.path,
            "root_cause_status": self.root_cause_status,
            "evidence_count": self.evidence_count,
            "messages": self.messages,
        }


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_bug_dir(bug_id: str) -> Path | None:
    for root in BUG_ROOTS:
        candidate = root / bug_id
        if candidate.is_dir():
            return candidate
    matches = []
    for root in BUG_ROOTS:
        if not root.is_dir():
            continue
        matches.extend(path for path in root.glob(f"{bug_id}*") if path.is_dir())
    return sorted(matches)[0] if matches else None


def extract_heading_section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    next_match = re.search(r"^##\s+", text[match.end() :], re.MULTILINE)
    end = match.end() + next_match.start() if next_match else len(text)
    return text[match.end() : end].strip()


def extract_status(text: str) -> str | None:
    section = extract_heading_section(text, "根因状态")
    candidates = [section, text]
    for candidate in candidates:
        match = re.search(r"(?im)^\s*(?:status|root_cause_status|状态)\s*[:：]\s*`?([a-z_]+)`?", candidate)
        if match:
            return match.group(1).strip().lower()
    return None


def count_evidence(text: str) -> int:
    section = extract_heading_section(text, "证据链")
    if not section:
        return 0
    count = 0
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip(" `") for cell in stripped.strip("|").split("|")]
        if len(cells) < 4:
            continue
        if cells[0].lower() in {"id", ""}:
            continue
        if any(cell in EVIDENCE_TYPES for cell in cells):
            count += 1
        elif re.match(r"^E\d+", cells[0], re.IGNORECASE):
            count += 1
    bullets = re.findall(r"(?im)^\s*[-*]\s+(E\d+|证据|evidence)\b", section)
    return count + len(bullets)


def validate_bug(bug_id: str) -> CheckResult:
    bug_dir = find_bug_dir(bug_id)
    if not bug_dir:
        return CheckResult(
            target=bug_id,
            status="blocked",
            messages=[f"未找到 BUG 目录: {bug_id}"],
        )

    root_cause_path = bug_dir / "root-cause.md"
    result = CheckResult(target=bug_id, status="pass", path=str(root_cause_path.relative_to(ROOT)))
    if not root_cause_path.exists():
        result.status = "blocked"
        result.messages.append("缺少 root-cause.md")
        return result

    text = read_text(root_cause_path)
    result.root_cause_status = extract_status(text)
    result.evidence_count = count_evidence(text)

    if result.root_cause_status not in VALID_STATUSES:
        result.status = "blocked"
        result.messages.append("根因状态缺失或非法，必须是 unknown/hypothesis/probable/confirmed")
        return result

    if result.root_cause_status != "confirmed":
        result.status = "blocked"
        result.messages.append(
            f"根因状态为 {result.root_cause_status}，未达到 confirmed；需要补证后再进入修复门禁"
        )
        return result

    if result.evidence_count <= 0:
        result.status = "blocked"
        result.messages.append("status: confirmed 但 ## 证据链 缺少有效证据项")
        return result

    result.messages.append("root-cause evidence gate passed")
    return result


def find_bug_ids_in_change(change_id: str) -> list[str]:
    change_dir = CHANGE_ROOT / change_id
    if not change_dir.is_dir():
        return []
    text_parts = []
    for name in ("trace.md", "proposal.md", "design.md", "tasks.md", "README.md"):
        path = change_dir / name
        if path.exists():
            text_parts.append(read_text(path))
    joined = "\n".join(text_parts)
    return sorted(set(re.findall(r"\bBUG-\d{4}-[A-Za-z0-9-]+\b", joined)))


def validate_change(change_id: str) -> list[CheckResult]:
    change_dir = CHANGE_ROOT / change_id
    if not change_dir.is_dir():
        return [
            CheckResult(
                target=change_id,
                status="blocked",
                messages=[f"未找到 active Change: {change_id}"],
            )
        ]
    bug_ids = find_bug_ids_in_change(change_id)
    if not bug_ids:
        return [
            CheckResult(
                target=change_id,
                status="na",
                path=str(change_dir.relative_to(ROOT)),
                messages=["未识别 BUG 来源，root-cause evidence gate 不适用"],
            )
        ]
    return [validate_bug(bug_id) for bug_id in bug_ids]


def active_bug_ids() -> list[str]:
    ids: set[str] = set()
    for root in BUG_ROOTS[:2]:
        if not root.is_dir():
            continue
        for path in root.iterdir():
            if path.is_dir() and re.match(r"^BUG-\d{4}-", path.name):
                ids.add(path.name)
    return sorted(ids)


def active_change_ids() -> list[str]:
    if not CHANGE_ROOT.is_dir():
        return []
    return sorted(path.name for path in CHANGE_ROOT.iterdir() if path.is_dir() and path.name != "archive")


def print_results(results: list[CheckResult], as_json: bool) -> None:
    if as_json:
        print(json.dumps([result.as_dict() for result in results], ensure_ascii=False, indent=2))
        return
    for result in results:
        path = f" path={result.path}" if result.path else ""
        root_status = f" root_cause_status={result.root_cause_status}" if result.root_cause_status else ""
        print(
            f"[{result.status}] {result.target}{path}{root_status} evidence_count={result.evidence_count}"
        )
        for message in result.messages:
            print(f"  - {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--bug", help="Full BUG id, e.g. BUG-0001-example")
    group.add_argument("--change", help="Active OpenSpec change id")
    group.add_argument("--all-active", action="store_true", help="Scan active BUGs and active Changes")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    results: list[CheckResult] = []
    if args.bug:
        results = [validate_bug(args.bug)]
    elif args.change:
        results = validate_change(args.change)
    elif args.all_active:
        for bug_id in active_bug_ids():
            results.append(validate_bug(bug_id))
        for change_id in active_change_ids():
            results.extend(validate_change(change_id))

    print_results(results, args.json)
    return 1 if any(result.status == "blocked" for result in results) else 0


if __name__ == "__main__":
    sys.exit(main())
