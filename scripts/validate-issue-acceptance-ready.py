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
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/backend"))
    from app.governance.archive_admission import change_acceptance
    result = change_acceptance(root, change)
    if not result["ready"] and result.get("source") == "manual" and result.get("total"):
        return False, f"issue_acceptance_pending checked={result['done']} total={result['total']}"
    return result["ready"], result.get("reason") or "issue_acceptance_passed"


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
