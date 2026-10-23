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
from app.chat.workspace import WorkspaceError
from app.governance.snapshot import digest, read_once

DIRECT_ACTIONS = frozenset(('sprint-propose', 'req-generate', 'bug-generate',
    'req-complete', 'bug-complete', 'req-review', 'bug-review',
    'req-opsx', 'bug-opsx', 'opsx-apply', 'opsx-modify', 'opsx-archive', 'sprint-archive'))
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
        from app.governance.archive_recovery import read_record, tree_hash, transition_chain, archive_paths
        record = read_record(journal)
        actual = tree_hash(root / 'openspec/specs')
        if actual == record['expected_spec_hash']:
            return False
        active = root / 'openspec/changes' / object_id
        archives = archive_paths(root, object_id)
        if len(archives) + int(active.is_dir()) != 1:
            return True
        transition_chain(root, object_id, record['expected_spec_hash'], actual,
                         active if active.is_dir() else archives[0])
        return False
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
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


def record_block_reason(conversation_id, client_id, *, action=None, object_id=None, revision=None):
    """Validate immutable command inputs without repairing or overwriting evidence."""
    rid = record_id(conversation_id, client_id)
    if not (store.root() / rid).exists():
        return 'direct_command_operation_missing'
    try:
        operation = store.read(rid, 'operation')
    except FileNotFoundError:
        return 'direct_command_operation_missing'
    except (ValueError, OSError, WorkspaceError):
        return 'direct_command_operation_invalid'
    if (not isinstance(operation, dict) or type(operation.get('schema_version')) is not int or operation.get('schema_version') != 1
            or operation.get('action') not in DIRECT_ACTIONS
            or not isinstance(operation.get('object_id'), str)
            or not isinstance(operation.get('baseline_revision'), str)
            or not isinstance(operation.get('steps'), list)
            or operation.get('phase') not in ('prepared', 'write_observed', 'sync_observed', 'blocked_step_limit', 'terminal')):
        return 'direct_command_operation_invalid'
    if any(not isinstance(step, dict)
            or not isinstance(step.get('item_key'), str)
            or not isinstance(step.get('source_revision'), (str, type(None)))
            or type(step.get('workflow_sync')) is not bool
            or type(step.get('sync_succeeded')) is not bool
            for step in operation['steps']):
        return 'direct_command_operation_invalid'
    expected = {'action': action, 'object_id': object_id, 'baseline_revision': revision}
    if any(value is not None and operation.get(key) != value for key, value in expected.items()):
        return 'direct_command_identity_mismatch'
    try:
        baseline = store.read(rid, 'baseline')
    except FileNotFoundError:
        return None if action is None else 'direct_command_baseline_missing'
    except (ValueError, OSError, WorkspaceError):
        return 'direct_command_baseline_invalid'
    if not isinstance(baseline, dict):
        return 'direct_command_baseline_invalid'
    if any(baseline.get(key) != operation.get(target) for key, target in (
            ('action', 'action'), ('object_id', 'object_id'), ('revision', 'baseline_revision'))):
        return 'direct_command_identity_mismatch'
    return None


def completion_block_reason(conversation_id, client_id, workspace):
    """Reject a direct command's success when its source facts are invalid."""
    if not os.environ.get('MOONBOX_GOVERNANCE_STATE_ROOT'):
        return None
    rid = record_id(conversation_id, client_id)
    record_path = store.root() / rid
    if not record_path.exists() and not record_path.is_symlink():
        return None
    reason = record_block_reason(conversation_id, client_id)
    if reason:
        return reason
    operation = store.read(rid, 'operation')
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
    """Candidate recognition only; a successful structured result is also required."""
    import shlex
    if item.get('type') != 'commandExecution':
        return False
    command = item.get('command')
    if not isinstance(command, str):
        return False
    try:
        tokens = shlex.split(command)
        if len(tokens) >= 3 and Path(tokens[0]).name in ('sh', 'bash', 'zsh') and tokens[1] in ('-c', '-lc'):
            command = tokens[2]
        lexer = shlex.shlex(command, posix=True, punctuation_chars=';&|()<>')
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return False
    # Reject probes anywhere in compound commands; false negatives are safer than
    # crediting another subcommand's shell exit status.
    if any(t.split('=', 1)[0] in ('--dry-run', '--check') for t in tokens):
        return False
    return any(Path(t).name == 'sync-workflow-status.py' for t in tokens) and any(
        t == '--event' or t.startswith('--event=') for t in tokens)


def workflow_sync_result(item):
    """Use the standard CLI's own result, not the containing shell's exit code."""
    if not is_formal_workflow_sync(item) or item.get('exitCode') != 0 or item.get('status') != 'completed':
        return None
    output = item.get('aggregatedOutput', '')
    if not isinstance(output, str):
        return None
    results = []
    for line in output.splitlines():
        if line.startswith('MOONBOX_WORKFLOW_RESULT:'):
            try:
                results.append(json.loads(line.split(':', 1)[1]))
            except ValueError:
                return None
    if not results or any(not isinstance(r, dict) or r.get('schema_version') != 1
                          or r.get('mode') != 'write' or r.get('ok') is not True for r in results):
        return None
    return results[-1]


def record_id(conversation_id, client_id):
    return str(uuid5(NAMESPACE_URL,
        f'moonbox.command-baseline.v1:{conversation_id}:{client_id}'))


def prepare(conversation_id, client_id, action, object_id, revision):
    if action not in DIRECT_ACTIONS:
        return
    rid = record_id(conversation_id, client_id)
    if (store.root() / rid / 'operation.json').exists():
        reason = record_block_reason(conversation_id, client_id, action=action,
                                     object_id=object_id, revision=revision)
        if reason:
            raise ValueError(reason)
        return
    store.write(rid, 'operation', {
        'schema_version': 1, 'proof_schema_version': 1, 'action': action, 'object_id': object_id,
        'baseline_revision': revision, 'steps': [], 'phase': 'prepared',
    })


def observe(conversation_id, client_id, item_id, phase, workspace, *, sync=False,
            sync_succeeded=False, sync_result=None):
    """Record an exact filesystem hash at a tool boundary; never store content."""
    if not os.environ.get('MOONBOX_GOVERNANCE_STATE_ROOT'):
        return None
    rid = record_id(conversation_id, client_id)
    record_path = store.root() / rid
    if not record_path.exists() and not record_path.is_symlink():
        return None
    if record_block_reason(conversation_id, client_id):
        return None
    operation = store.read(rid, 'operation')
    if operation['phase'] == 'terminal':
        return operation
    if sync_result is not None and sync_result.get('object_id') != operation['object_id']:
        sync_succeeded = False
    steps = operation['steps']
    key = hashlib.sha256(f'{item_id}:{phase}'.encode()).hexdigest()
    if any(step['item_key'] == key for step in steps):
        return operation
    if len(steps) >= MAX_STEPS:
        operation['phase'] = 'blocked_step_limit'
        store.write(rid, 'operation', operation)
        return operation
    try:
        files = read_once(workspace)
        revision = digest(files)
        state = 'observed'
    except (OSError, ValueError, UnicodeError):
        revision = None
        state = 'source_unreadable'
    steps.append({'item_key': key, 'phase': phase, 'source_revision': revision,
                  'state': state, 'workflow_sync': bool(sync),
                  'sync_succeeded': bool(sync and phase == 'completed' and sync_succeeded)})
    if sync_result is not None:
        steps[-1]['sync_result'] = sync_result
    if sync and phase == 'completed' and sync_succeeded and revision:
        from app.governance.direct_completion import manifest, DirectProofError
        try:
            steps[-1]['completion_manifest'] = manifest(files, operation['object_id'], operation['action'])
        except DirectProofError as error:
            steps[-1]['completion_reason'] = str(error)
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
    if record_block_reason(conversation_id, client_id):
        return None
    operation = store.read(rid, 'operation')
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
