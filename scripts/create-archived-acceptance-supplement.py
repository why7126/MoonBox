#!/usr/bin/env python3
"""Recheck one archived command AC and record a bounded artifact supplement."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

from opsx_acceptance import (
    ROOT,
    artifacts_match,
    fingerprint,
    latest_manifest,
    read_plan,
    run_command,
    stamp,
    within,
)


def build_supplement(root: Path, change: str, check_id: str) -> tuple[Path, dict]:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", change) or not re.fullmatch(r"AC-[A-Za-z0-9-]+", check_id):
        raise ValueError("invalid Change or AC ID")
    archives = list((root / "openspec" / "archive").glob(f"????-??-??-{change}"))
    if len(archives) != 1:
        raise ValueError("archived Change missing or ambiguous")
    archive = archives[0]
    plan = read_plan(archive)
    manifest = latest_manifest(archive)
    if not manifest or manifest.get("status") != "passed":
        raise ValueError("complete passed manifest required")
    check = next((item for item in plan["checks"] if item["id"] == check_id), None)
    row = next((item for item in manifest.get("checks", []) if item.get("id") == check_id), None)
    if not check or check.get("kind") != "command" or not row or row.get("status") != "passed":
        raise ValueError("target must be a passed command AC")
    if any(not artifacts_match(root, item, archive_dir=archive) for item in manifest["checks"] if item.get("id") != check_id):
        raise ValueError("another AC artifact is stale")
    changed = []
    for artifact in row.get("artifacts", []):
        parts = Path(artifact["path"]).parts
        path = within(root, artifact["path"])
        if len(parts) >= 4 and parts[:3] == ("openspec", "changes", change):
            path = within(archive, str(Path(*parts[3:])))
        if not path.is_file():
            raise ValueError("target artifact missing")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != artifact["sha256"]:
            changed.append({"path": artifact["path"], "previous_sha256": artifact["sha256"], "current_sha256": actual})
    if not changed:
        raise ValueError("no target artifact changed")
    result = run_command(check, root)
    if result.get("status") != "passed" or result.get("exit_code") != 0:
        raise ValueError("original AC command did not pass")
    supplement = {
        "schema_version": 1,
        "change_id": change,
        "source_run_id": manifest["run_id"],
        "check_id": check_id,
        "verified_at": stamp(),
        "input_fingerprint": fingerprint(root, check),
        "argv": check["argv"],
        "exit_code": 0,
        "artifacts": changed,
    }
    return archive / "evidence" / "acceptance" / "supplements" / f"{check_id}.json", supplement


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--change", required=True)
    parser.add_argument("--check", required=True)
    args = parser.parse_args()
    try:
        path, supplement = build_supplement(ROOT, args.change, args.check)
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".supplement-", suffix=".json", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(supplement, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ARCHIVED_ACCEPTANCE_SUPPLEMENT_BLOCKED {exc}")
        return 1
    print(f"ARCHIVED_ACCEPTANCE_SUPPLEMENT_PASSED {args.change} {args.check} artifacts={len(supplement['artifacts'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
