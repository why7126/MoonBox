"""Private, bounded source facts for direct governance command recovery.

This journal is observational. A terminal Chat turn is never replayed from it.
"""
import hashlib
import json
import os
import re
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5
import yaml

from app.governance import store
from app.governance.snapshot import digest, read_once

DIRECT_ACTIONS = frozenset(('sprint-propose', 'req-opsx', 'opsx-apply', 'opsx-archive'))
MAX_STEPS = 256


def archive_spec_drift(object_id, workspace):
    """Return true when a prepared archive's merged specs changed later in the turn."""
    if not isinstance(object_id, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,100}', object_id):
        return False
    root = Path(workspace)
    journal = root / 'openspec' / 'archive' / '.archive-recovery' / f'{object_id}.json'
    if not journal.exists():
        return False
    try:
        if journal.is_symlink() or journal.stat().st_size > 8192:
            return True
        record = json.loads(journal.read_text())
        if record.get('change_id') != object_id or not re.fullmatch(r'[a-f0-9]{64}', record.get('expected_spec_hash', '')):
            return True
        value = hashlib.sha256()
        specs = root / 'openspec' / 'specs'
        if specs.exists():
            for path in sorted(specs.rglob('*')):
                if path.is_symlink():
                    return True
                if path.is_file():
                    value.update(path.relative_to(specs).as_posix().encode())
                    value.update(b'\0')
                    value.update(hashlib.sha256(path.read_bytes()).digest())
        return value.hexdigest() != record['expected_spec_hash']
    except (OSError, ValueError, TypeError, KeyError):
        return True


def archive_completion_blocked(conversation_id, client_id, workspace):
    """Check archive source facts before a Chat success is committed."""
    if not os.environ.get('MOONBOX_GOVERNANCE_STATE_ROOT'):
        return False
    record_path = store.root() / record_id(conversation_id, client_id)
    if not record_path.exists() and not record_path.is_symlink():
        return False
    try:
        operation = store.read(record_id(conversation_id, client_id), 'operation')
    except (FileNotFoundError, ValueError, OSError):
        return False
    return operation.get('action') == 'opsx-archive' and archive_spec_drift(
        operation.get('object_id'), workspace)


def completion_block_reason(conversation_id, client_id, workspace):
    """Reject a direct command's success when its source facts are invalid."""
    if not os.environ.get('MOONBOX_GOVERNANCE_STATE_ROOT'):
        return None
    rid = record_id(conversation_id, client_id)
    record_path = store.root() / rid
    if not record_path.exists() and not record_path.is_symlink():
        return None
    try:
        operation = store.read(rid, 'operation')
    except (FileNotFoundError, ValueError, OSError):
        return 'direct_command_recovery_blocked'
    if operation.get('action') == 'opsx-archive':
        return 'archive_recovery_blocked' if archive_spec_drift(
            operation.get('object_id'), workspace) else None
    if operation.get('action') != 'sprint-propose':
        return None
    try:
        files = read_once(workspace)
        paths = [name for name in files if re.fullmatch(
            r'iterations/(?:change|archive)/sprint-\d{3}/sprint\.yaml', name)]
        if not paths:
            return 'sprint_source_invalid'
        member_found = False
        for name in paths:
            parsed = yaml.safe_load(files[name])
            if not isinstance(parsed, dict) or parsed.get('sprint_id') != Path(name).parent.name:
                return 'sprint_source_invalid'
            if not isinstance(parsed.get('requirements', []), list) or not isinstance(parsed.get('bugs', []), list):
                return 'sprint_source_invalid'
            member_found = member_found or operation.get('object_id') in (
                parsed.get('requirements') or []) or operation.get('object_id') in (
                parsed.get('bugs') or [])
        if not member_found:
            return 'sprint_source_invalid'
    except (OSError, ValueError, UnicodeError, yaml.YAMLError):
        return 'sprint_source_invalid'
    return None


def is_formal_workflow_sync(item):
    """Exclude dry-run/check probes from persistent sync success observations."""
    if item.get('type') != 'commandExecution':
        return False
    command = item.get('command')
    if not isinstance(command, str) or 'sync-workflow-status.py' not in command:
        return False
    if not re.search(r'(?<!\S)--event(?:\s|=)', command):
        return False
    return not re.search(r'(?<!\S)--(?:dry-run|check)(?=\s|$|["\'])', command)


def record_id(conversation_id, client_id):
    return str(uuid5(NAMESPACE_URL,
        f'moonbox.command-baseline.v1:{conversation_id}:{client_id}'))


def prepare(conversation_id, client_id, action, object_id, revision):
    if action not in DIRECT_ACTIONS:
        return
    store.write(record_id(conversation_id, client_id), 'operation', {
        'schema_version': 1, 'action': action, 'object_id': object_id,
        'baseline_revision': revision, 'steps': [], 'phase': 'prepared',
    })


def observe(conversation_id, client_id, item_id, phase, workspace, *, sync=False,
            sync_succeeded=False):
    """Record an exact filesystem hash at a tool boundary; never store content."""
    if not os.environ.get('MOONBOX_GOVERNANCE_STATE_ROOT'):
        return None
    rid = record_id(conversation_id, client_id)
    record_path = store.root() / rid
    if not record_path.exists() and not record_path.is_symlink():
        return None
    try:
        operation = store.read(rid, 'operation')
    except FileNotFoundError:
        return None
    if operation['phase'] == 'terminal':
        return operation
    steps = operation['steps']
    key = hashlib.sha256(f'{item_id}:{phase}'.encode()).hexdigest()
    if any(step['item_key'] == key for step in steps):
        return operation
    if len(steps) >= MAX_STEPS:
        operation['phase'] = 'blocked_step_limit'
        store.write(rid, 'operation', operation)
        return operation
    try:
        revision = digest(read_once(workspace))
        state = 'observed'
    except (OSError, ValueError, UnicodeError):
        revision = None
        state = 'source_unreadable'
    steps.append({'item_key': key, 'phase': phase, 'source_revision': revision,
                  'state': state, 'workflow_sync': bool(sync),
                  'sync_succeeded': bool(sync and phase == 'completed' and sync_succeeded)})
    operation['phase'] = 'sync_observed' if sync else 'write_observed'
    store.write(rid, 'operation', operation)
    return operation


def terminal(conversation_id, client_id, status, workspace):
    """Classify the stop point conservatively; never infer command success."""
    if not os.environ.get('MOONBOX_GOVERNANCE_STATE_ROOT'):
        return None
    rid = record_id(conversation_id, client_id)
    record_path = store.root() / rid
    if not record_path.exists() and not record_path.is_symlink():
        return None
    try:
        operation = store.read(rid, 'operation')
    except FileNotFoundError:
        return None
    if operation['phase'] == 'terminal':
        return operation
    try:
        current = digest(read_once(workspace))
    except (OSError, ValueError, UnicodeError):
        current = None
    steps = operation['steps']
    observed = {step['source_revision'] for step in steps if step['source_revision']}
    if operation.get('action') == 'opsx-archive' and archive_spec_drift(operation.get('object_id'), workspace):
        classification = 'blocked_archive_spec_drift'
    elif (operation.get('action') == 'sprint-propose' and status == 'failed'
          and any(step['sync_succeeded'] for step in steps)
          and completion_block_reason(conversation_id, client_id, workspace) == 'sprint_source_invalid'):
        classification = 'blocked_invalid_sprint_source'
    elif current is None or (current != operation['baseline_revision'] and current not in observed):
        classification = 'blocked_unobserved_source_change'
    elif current == operation['baseline_revision']:
        classification = 'no_governance_write'
    elif any(step['sync_succeeded']
             and step['source_revision'] == current for step in steps):
        classification = 'sync_completed_unverified'
    elif any(step['workflow_sync'] for step in steps):
        classification = 'sync_incomplete'
    else:
        classification = 'partial_write'
    operation.update(phase='terminal', terminal_status=status,
                     final_revision=current, classification=classification)
    store.write(rid, 'operation', operation)
    return operation


def reconcile_terminal_commands(factory, resolve_workspace):
    """Finish journals for already terminal turns after a worker restart."""
    from sqlalchemy import or_, select
    from app.chat.schema import turns
    with factory() as db:
        rows = list(db.execute(select(turns.c.conversation_id,
            turns.c.client_request_id, turns.c.status).where(
                turns.c.status.in_(('completed', 'failed', 'stopped')),
                or_(*(turns.c.prompt.like('/' + action + ' %')
                      for action in DIRECT_ACTIONS)))
            .order_by(turns.c.updated_at.desc()).limit(200)).all())
    for conversation_id, client_id, status in rows:
        try:
            _, workspace = resolve_workspace(conversation_id)
            if workspace.is_dir():
                terminal(conversation_id, client_id, status, workspace)
        except (OSError, ValueError):
            continue
