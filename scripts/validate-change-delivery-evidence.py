#!/usr/bin/env python3
"""Validate active applied Changes keep Requirement Center-readable delivery evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND_SRC = ROOT / "src" / "backend"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from app.governance.change_index import ChangeIndex  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--change",
        action="append",
        dest="changes",
        help="Limit validation to one Change ID. Repeat for multiple Changes.",
    )
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser


def validate(root: Path, changes: list[str] | None = None) -> dict:
    index = ChangeIndex(root)
    selected = changes or sorted(index.records)
    checked: list[dict] = []
    missing: list[dict] = []
    skipped: list[dict] = []

    for change_id in selected:
        record = index.records.get(change_id)
        if record is None:
            missing.append({"change_id": change_id, "reason": "Change not found"})
            continue
        if record.source_kind != "active":
            skipped.append(
                {
                    "change_id": change_id,
                    "stage": record.stage,
                    "source_kind": record.source_kind,
                    "reason": "not an active Change",
                }
            )
            continue
        if record.stage != "acceptance":
            skipped.append(
                {
                    "change_id": change_id,
                    "stage": record.stage,
                    "source_kind": record.source_kind,
                    "reason": "not an applied Change",
                }
            )
            continue
        reason = index.acceptance_source_reason(record)
        row = {
            "change_id": change_id,
            "stage": record.stage,
            "sprint": index.sprint_id(record),
            "reason": reason,
        }
        checked.append(row)
        if reason:
            missing.append(row)

    return {
        "status": "pass" if not missing else "blocked",
        "checked_count": len(checked),
        "missing_count": len(missing),
        "skipped_count": len(skipped),
        "checked": checked,
        "missing": missing,
        "skipped": skipped,
    }


def print_text(report: dict) -> None:
    print("Change Delivery Evidence Report")
    print(f"Status: {report['status']}")
    print(f"Checked: {report['checked_count']}")
    print(f"Missing: {report['missing_count']}")
    print(f"Skipped: {report['skipped_count']}")
    if report["missing"]:
        print("\nMissing delivery evidence:")
        for row in report["missing"]:
            print(f"- {row['change_id']}: {row['reason']}")
    else:
        print("\nAll checked applied Changes have readable delivery evidence.")
    if report["skipped"]:
        print("\nSkipped:")
        for row in report["skipped"]:
            print(f"- {row['change_id']}: {row['reason']}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = validate(args.root.resolve(), args.changes)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text(report)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
