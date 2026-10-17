#!/usr/bin/env python3
"""Classify a retry around OpenSpec's spec-merge/Change-move boundary.

The local journal contains hashes only. A preview archive runs in a temporary
copy so a crash after the real spec merge can be recognized without guessing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    if not root.exists():
        return digest.hexdigest()
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"archive recovery rejects a symlink: {path.relative_to(root)}")
        if not path.is_file():
            continue
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def expected_spec_hash(root: Path, change_id: str) -> str:
    with tempfile.TemporaryDirectory(prefix="moonbox-archive-preview-") as temporary:
        preview = Path(temporary)
        source = root / "openspec"
        target = preview / "openspec"
        (target / "changes").mkdir(parents=True)
        shutil.copytree(source / "specs", target / "specs") if (source / "specs").exists() else (target / "specs").mkdir()
        shutil.copytree(source / "changes" / change_id, target / "changes" / change_id)
        for name in ("config.yaml", "project.md"):
            if (source / name).is_file():
                shutil.copy2(source / name, target / name)
        command = subprocess.run(
            ["openspec", "archive", change_id, "-y"], cwd=preview,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        if command.returncode:
            raise ValueError(f"preview OpenSpec archive failed (exit {command.returncode})")
        return tree_hash(target / "specs")


def classify(root: Path, change_id: str, archive_date: str) -> str:
    active = root / "openspec/changes" / change_id
    specs = root / "openspec/specs"
    journal = root / "openspec/archive/.archive-recovery" / f"{change_id}.json"
    if not active.is_dir():
        if journal.is_file():
            record = json.loads(journal.read_text())
            if tree_hash(specs) != record["expected_spec_hash"]:
                raise ValueError("archive recovery blocked: archived spec differs from prepared result")
        return "archived"
    if journal.is_file():
        record = json.loads(journal.read_text())
        if record.get("change_id") != change_id or record.get("archive_date") != archive_date:
            raise ValueError("archive recovery blocked: journal identity differs")
        if tree_hash(active) != record["active_change_hash"]:
            raise ValueError("archive recovery blocked: active Change changed after preparation")
    else:
        record = {
            "schema_version": 1,
            "change_id": change_id,
            "archive_date": archive_date,
            "active_change_hash": tree_hash(active),
            "baseline_spec_hash": tree_hash(specs),
            "expected_spec_hash": expected_spec_hash(root, change_id),
        }
        journal.parent.mkdir(parents=True, exist_ok=True)
        temporary = journal.with_suffix(".tmp")
        temporary.write_text(json.dumps(record, sort_keys=True) + "\n")
        os.replace(temporary, journal)
    actual = tree_hash(specs)
    if actual == record["baseline_spec_hash"]:
        return "merge"
    if actual == record["expected_spec_hash"]:
        return "move-only"
    raise ValueError("archive recovery blocked: unknown spec modification; journal and files retained")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("change_id")
    parser.add_argument("archive_date")
    args = parser.parse_args()
    try:
        print(classify(Path.cwd(), args.change_id, args.archive_date))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"ARCHIVE_RECOVERY_BLOCKED {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
