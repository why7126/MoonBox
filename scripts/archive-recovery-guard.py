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
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/backend'))
from app.governance.archive_recovery import (tree_hash, requirement_blocks, verify_delta_effects,
    recovery_state, transition_chain, read_record, archive_paths, MAX_JOURNAL_BYTES,
    delivery_input_hash)


def expected_spec_hash(root: Path, change_id: str) -> str:
    before = tree_hash(root / "openspec/specs")
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
        output = command.stdout + "\n" + command.stderr
        if re.search(r"(?im)^(?:Aborted\.|.*(?:MODIFIED|ADDED|REMOVED|RENAMED) failed\b|Error:)", output):
            raise ValueError("preview OpenSpec reported an aborted or failed merge")
        active = target / "changes" / change_id
        archives = [p for base in (target / "archive", target / "changes/archive")
                    for p in base.glob(f"????-??-??-{change_id}") if p.is_dir()]
        if active.exists() or len(archives) != 1:
            raise ValueError("preview did not produce exactly one archive and remove active Change")
        if tree_hash(archives[0]) != tree_hash(source / "changes" / change_id):
            raise ValueError("preview archive contents differ from source Change")
        verify_delta_effects(source / "changes" / change_id / "specs", target / "specs")
        if tree_hash(source / "specs") != before:
            raise ValueError("preview source specs changed during validation")
        return tree_hash(target / "specs")


def classify(root: Path, change_id: str, archive_date: str) -> str:
    state = recovery_state(root, change_id, archive_date)
    if state['mode'] == 'merge' and state['chain']:
        # Admission is read-only. At the actual merge boundary, rebase the
        # expected result onto the proven disjoint baseline, retaining history.
        # Otherwise S+B cannot prove the real result S+A+B after A archived.
        reprepare(root, change_id)
        return recovery_state(root, change_id, archive_date)['mode']
    if state['mode'] == 'archived':
        # The preparation day is not the migration identity. Only a unique,
        # fully proven archive may establish the actual date after a restart.
        journal = root / 'openspec/archive/.archive-recovery' / f'{change_id}.json'
        if journal.exists():
            original = journal.read_bytes()
            record = read_record(journal)
            actual_date = archive_paths(root, change_id)[0].name[:10]
            if record.get('archive_date') != actual_date:
                record['prepared_archive_date'] = record.get('prepared_archive_date', record.get('archive_date'))
                record['archive_date'] = actual_date
                with tempfile.NamedTemporaryFile(mode='w', dir=journal.parent, delete=False) as handle:
                    temporary = Path(handle.name)
                    handle.write(json.dumps(record, sort_keys=True) + '\n')
                    handle.flush()
                    os.fsync(handle.fileno())
                if journal.read_bytes() != original:
                    temporary.unlink()
                    raise ValueError('archive recovery journal changed concurrently')
                os.replace(temporary, journal)
    if state['mode'] != 'unprepared':
        return state['mode']
    active = root / 'openspec/changes' / change_id
    specs = root / 'openspec/specs'
    journal = root / 'openspec/archive/.archive-recovery' / f'{change_id}.json'
    baseline, active_hash = tree_hash(specs), tree_hash(active)
    input_hash = delivery_input_hash(active)
    expected = expected_spec_hash(root, change_id)
    if tree_hash(specs) != baseline or tree_hash(active) != active_hash:
        raise ValueError('archive preparation inputs changed')
    record = {'schema_version': 4, 'input_projection': 1,
              'delivery_input_hash': input_hash,
              'change_id': change_id, 'archive_date': archive_date,
              'active_change_hash': active_hash, 'delta_hash': tree_hash(active / 'specs'),
              'baseline_spec_hash': baseline, 'expected_spec_hash': expected}
    journal.parent.mkdir(parents=True, exist_ok=True)
    # Never replace a concurrently created recovery record.
    with tempfile.NamedTemporaryFile(mode='w', dir=journal.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(json.dumps(record, sort_keys=True) + '\n')
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.link(temporary, journal)
    finally:
        temporary.unlink()
    return 'merge'


def reprepare(root: Path, change_id: str) -> None:
    """Refresh an active attempt only after proving no own merge was applied."""
    journal = root / 'openspec/archive/.archive-recovery' / f'{change_id}.json'
    original = journal.read_bytes()
    record = read_record(journal)
    active = root / 'openspec/changes' / change_id
    if not active.is_dir() or archive_paths(root, change_id):
        raise ValueError('reprepare requires a unique active Change and no archive')
    baseline, active_hash = tree_hash(root / 'openspec/specs'), tree_hash(active)
    input_hash = delivery_input_hash(active)
    chain = transition_chain(root, change_id, record.get('baseline_spec_hash'), baseline, active)
    expected = expected_spec_hash(root, change_id)
    if (tree_hash(root / 'openspec/specs') != baseline or tree_hash(active) != active_hash
            or journal.read_bytes() != original):
        raise ValueError('reprepare inputs changed during validation')
    replacement = {**record, 'schema_version': 4, 'input_projection': 1,
                   'delivery_input_hash': input_hash, 'previous_record': record,
                   'baseline_spec_hash': baseline, 'baseline_transition': chain,
                   'active_change_hash': active_hash, 'delta_hash': tree_hash(active / 'specs'),
                   'expected_spec_hash': expected}
    body = json.dumps(replacement, sort_keys=True) + '\n'
    if len(body.encode()) > MAX_JOURNAL_BYTES:
        raise ValueError('archive recovery history capacity exceeded')
    if transition_chain(root, change_id, record.get('baseline_spec_hash'), baseline, active) != chain:
        raise ValueError('archive recovery proof changed during validation')
    temporary = journal.with_suffix('.tmp')
    temporary.write_text(body)
    os.replace(temporary, journal)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("change_id")
    parser.add_argument("archive_date", nargs="?")
    parser.add_argument("--preview", action="store_true", help="Validate spec merge in temporary copy; no archive or journal writes")
    parser.add_argument("--reprepare", action="store_true", help="Refresh active journal after verifying the baseline or a disjoint completed archive chain; retain history")
    args = parser.parse_args()
    try:
        if not __import__("re").fullmatch(r"[a-z0-9][a-z0-9-]{0,100}", args.change_id):
            raise ValueError("invalid change identity")
        if args.reprepare:
            if args.preview:
                raise ValueError("preview and reprepare are mutually exclusive")
            reprepare(Path.cwd(), args.change_id)
            print("archive journal reprepared; previous record retained")
        elif args.preview:
            print(json.dumps({"status": "passed", "check": "archive-preview", "expected_spec_hash": expected_spec_hash(Path.cwd(), args.change_id)}))
        else:
            if not args.archive_date:
                raise ValueError("archive_date required without --preview")
            print(classify(Path.cwd(), args.change_id, args.archive_date))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"ARCHIVE_RECOVERY_BLOCKED {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
