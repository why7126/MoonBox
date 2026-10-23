"""Portable standard-sync receipts. Stdlib only; no repository code execution on read."""
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from uuid import uuid4


def safe_id(value):
    return isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', value) is not None


def digest(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('receipt_input_invalid')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(root, change, event, issue):
    if event != 'opsx.accept' or not change:
        return
    if not safe_id(change):
        raise ValueError('receipt_identity_invalid')
    folder = root / 'openspec/changes' / change
    plan = json.loads((folder / 'acceptance-plan.json').read_text())
    # Bind the receipt to the exact accepted report and plan. Consumers still
    # independently check every current fingerprint, effect and artifact.
    base = folder / 'evidence/acceptance'
    manifests = sorted([*base.glob('*/manifest.json'), *base.glob('checkpoints/*/manifest.json')],
                       key=lambda p: p.stat().st_mtime_ns, reverse=True)
    report = None
    for path in manifests:
        if path.is_symlink() or path.parent.name.startswith('.'):
            continue
        try:
            candidate = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        if candidate.get('scope', 'complete') != 'complete' or any(
                row.get('reason') == 'not-selected' for row in candidate.get('checks', [])):
            continue
        # A newer failed complete report supersedes an older success.
        if candidate.get('status') == 'passed' and safe_id(path.parent.name):
            report = path
        break
    if report is None:
        return
    value = dict(schema_version=1, event=event, mode='write', ok=True,
                 change_id=change, object_id=issue or plan.get('issue_id'),
                 run_id=report.parent.name, plan_hash=digest(folder/'acceptance-plan.json'),
                 manifest_hash=digest(report), created_at=datetime.now(timezone.utc).isoformat())
    directory = folder / '.workflow-receipts'
    directory.mkdir(exist_ok=True)
    if directory.is_symlink():
        raise ValueError('receipt_directory_invalid')
    path = directory / (str(uuid4()) + '.json')
    with path.open('x') as out:
        json.dump(value, out, ensure_ascii=False)
        out.flush(); os.fsync(out.fileno())


def valid(folder, change, issue, run):
    if not safe_id(change) or not safe_id(run):
        return False
    plan = folder/'acceptance-plan.json'
    manifest = folder/'evidence/acceptance'/run/'manifest.json'
    directory = folder/'.workflow-receipts'
    if directory.is_symlink():
        return False
    for path in directory.glob('*.json'):
        if path.is_symlink() or path.stat().st_size > 8192:
            continue
        try:
            r = json.loads(path.read_text())
            if (r.get('schema_version') == 1 and r.get('event') == 'opsx.accept'
                    and r.get('mode') == 'write' and r.get('ok') is True
                    and r.get('object_id') == issue and r.get('change_id') == change
                    and r.get('run_id') == run and r.get('plan_hash') == digest(plan)
                    and r.get('manifest_hash') == digest(manifest)):
                return True
        except (ValueError, OSError):
            continue
    return False
