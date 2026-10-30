"""Resolve immutable turn-owned source, never infer ownership from a dirty checkout."""
import hashlib
import json

from sqlalchemy import select
from app.chat import service as chat
from app.chat.relations import _read_file
from app.moonbox_core.authority import delivery
from app.moonbox_core.schema import delivery_sessions, execution_receipts
from app.moonbox_core.sessions import execution_workspace
from app.moonbox_rollout.schema import references, points, entries
from app.verification.acceptance_snapshot import capture
from app.verification.acceptance_state import Conflict, validate_plan


def resolve(db, actor, conversation_id, turn_id, change_id, *, source_point_id=None):
    parent = chat.conversation(db, actor, conversation_id)
    turn = chat.turn(db, actor, turn_id)
    if turn['conversation_id'] != conversation_id:
        raise Conflict('source_turn_mismatch')
    project, context = delivery(db, actor, parent['space_id'], parent['repository_id'], change_id)
    linked = db.execute(select(delivery_sessions).where(
        delivery_sessions.c.conversation_id == conversation_id)).mappings().first()
    if not linked or linked['change_id'] != change_id or linked['delivery_root'] != context['delivery_root']:
        raise Conflict('delivery_binding_mismatch')
    managed = execution_workspace(db, parent)
    if not managed:
        raise Conflict('source_workspace_unbound')
    receipt = db.execute(select(execution_receipts).where(execution_receipts.c.turn_id == turn_id)).mappings().first()
    live_point=None
    if source_point_id:
        from app.verification.acceptance_schema import tool_waits
        live_point=db.scalar(select(tool_waits.c.point_id).where(tool_waits.c.source_turn_id==turn_id,
            tool_waits.c.point_id==source_point_id,tool_waits.c.state.in_(['waiting','dispatching','delivered'])))
        if not live_point:raise Conflict('source_checkpoint_missing')
    if not receipt or (not live_point and (not receipt['executor_closed'] or not receipt['files_collected'])):
        # A missing heartbeat or a terminal row alone never proves executor death.
        raise Conflict('source_execution_unconfirmed')
    point = db.execute(select(points).join(references, references.c.point_id == points.c.id).where(
        references.c.workspace_id == managed[0]['id'], references.c.owner_id == turn_id,
        references.c.owner_type == ('acceptance' if live_point else 'turn_after'), points.c.state == 'complete',
        *([points.c.id==live_point] if live_point else []),
    )).mappings().first()
    if not point:
        raise Conflict('source_checkpoint_missing')
    if not point['scope_json'] or json.loads(point['scope_json']) != json.loads(receipt['scope_json'] or '[]'):
        raise Conflict('source_scope_changed')
    recorded = list(db.execute(select(entries).where(entries.c.point_id == point['id'])).mappings())
    if any(entry['kind'] != 'file' for entry in recorded):
        raise Conflict('source_file_unsafe')
    try:
        raw = _read_file(project.root, 'openspec/changes/' + change_id + '/acceptance-plan.json')
        if len(raw.encode()) > 2 * 1024 * 1024: raise ValueError()
        plan = json.loads(raw)
        validate_plan(plan)
        if plan.get('change_id') != change_id: raise ValueError()
    except (ValueError, TypeError):
        raise Conflict('plan_invalid') from None
    source_ref = {'workspace_id': managed[0]['id'], 'point_id': point['id'],
                  'head_commit': point['head_commit'], 'manifest_hash': point['manifest_hash'],
                  'plan_digest': hashlib.sha256(raw.encode()).hexdigest()}
    if live_point:source_ref['kind']='tool_checkpoint'
    return parent, project, managed, point, recorded, plan, source_ref


def verify_files(managed, point, recorded, binding):
    from app.moonbox_worktree import Repository
    from app.moonbox_exec_server.scope import names
    root = managed[1]
    if Repository.open(root).head() != point['head_commit']:
        raise Conflict('source_head_changed')
    allowed = json.loads(point['scope_json'])
    if set(names(root, allowed)) != {entry['path'] for entry in recorded}:
        raise Conflict('source_inputs_changed')
    captured = capture(root, [entry['path'] for entry in recorded], binding=binding, head_commit=point['head_commit'])
    actual = {path: (digest, mode) for path, digest, mode in captured['manifest']}
    if any(actual[entry['path']] != (entry['digest'], 0o755 if entry['mode'] & 0o111 else 0o644) for entry in recorded):
        raise Conflict('source_inputs_changed')
    return captured['digest']


def export_checkpoint(factory, source_ref, destination, template):
    """Overlay only the authorized immutable checkpoint onto its exact Git baseline."""
    import os
    import shutil
    import subprocess
    from pathlib import Path
    from app.chat import content_store
    from app.chat.workspace import git_env
    from app.moonbox_core.schema import workspaces
    from app.verification.candidate import export_candidate
    from app.verification.acceptance_snapshot import source_path, LIMIT_FILE, LIMIT_TOTAL
    destination=Path(destination)
    if destination.exists():raise Conflict('snapshot_destination_exists')
    destination.mkdir(mode=0o700,parents=True)
    with factory() as db:
        point=db.execute(select(points).where(points.c.id==source_ref['point_id'],points.c.state=='complete')).mappings().one()
        workspace=db.execute(select(workspaces).where(workspaces.c.id==source_ref['workspace_id'])).mappings().one()
        if (point['workspace_id']!=workspace['id'] or point['manifest_hash']!=source_ref['manifest_hash']
                or point['head_commit']!=source_ref['head_commit']):raise Conflict('source_checkpoint_changed')
        path=source_path(template['lock_path'])
        baseline=subprocess.run(['git','-C',workspace['root_locator'],'show',point['head_commit']+':'+path],
                                env=git_env(),capture_output=True,timeout=30)
        if baseline.returncode or len(baseline.stdout)>LIMIT_FILE:raise Conflict('baseline_lock_unavailable')
        export_candidate(workspace['root_locator'],point['head_commit'],destination,path,hashlib.sha256(baseline.stdout).hexdigest())
        allowed=json.loads(point['scope_json'])
        if not allowed or '' in allowed:raise Conflict('source_scope_not_isolated')
        for relative in allowed:
            source_path(relative)
            target=destination/relative
            if target.is_dir():shutil.rmtree(target)
            elif target.exists():target.unlink()
        total=0
        for entry in db.execute(select(entries).where(entries.c.point_id==point['id'])).mappings():
            relative=source_path(entry['path'])
            if not any(relative==prefix or relative.startswith(prefix+'/') for prefix in allowed):
                raise Conflict('source_entry_outside_scope')
            if entry['kind']!='file' or entry['byte_count']>LIMIT_FILE:raise Conflict('source_file_unsafe')
            total+=entry['byte_count']
            if total>LIMIT_TOTAL:raise Conflict('snapshot_total_limit')
            target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True)
            digest=hashlib.sha256();size=0
            with target.open('xb') as stream:
                for block in content_store.blocks(db,entry['object_id']):
                    size+=len(block)
                    if size>entry['byte_count']:raise Conflict('snapshot_integrity_failed')
                    digest.update(block);stream.write(block)
            if size!=entry['byte_count'] or digest.hexdigest()!=entry['digest']:raise Conflict('snapshot_integrity_failed')
            target.chmod(0o755 if entry['mode']&0o111 else 0o644)
    if hashlib.sha256((destination/path).read_bytes()).hexdigest()!=template['lock_digest']:
        raise Conflict('snapshot_dependencies_unapproved')
    total=0
    for file in destination.rglob('*'):
        if file.is_file():
            source_path(file.relative_to(destination).as_posix())
            total+=file.stat().st_size
    if total>LIMIT_TOTAL:raise Conflict('snapshot_total_limit')
    destination.chmod(0o755)
