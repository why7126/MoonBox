"""Durable, authorized three-way undo; file steps are individually recoverable."""
import hashlib
import json
import os
from dataclasses import asdict
from sqlalchemy import insert, select, update, func, delete
from app.chat import service as chat, content_store, snapshot_store
from app.chat.schema import conversations
from app.moonbox_core import service, workspaces
from app.moonbox_core.schema import session_bindings, write_locks
from app.moonbox_worktree import Repository, WorktreeConflict
from .schema import points, entries, operations, steps, references
from .recovery import Entry, preflight, fingerprint, validate_path
from .restore_io import apply_one, RestoreConflict
from . import catalog
from app.moonbox_core.observability import record


def _point(db, wid, pid):
    row = db.execute(select(points).where(points.c.workspace_id == wid, points.c.id == pid,
        points.c.state == 'complete')).mappings().first()
    if not row:
        raise WorktreeConflict('recovery_point_unavailable')
    return row


def _entries(db, pid, paths):
    keys = [hashlib.sha256(path.encode()).hexdigest() for path in paths]
    result = {}
    for row in db.execute(select(entries).where(entries.c.point_id == pid, entries.c.path_key.in_(keys))).mappings():
        if row['path'] not in paths:
            raise WorktreeConflict('manifest_path_mismatch')
        result[row['path']] = dict(row)
    return result


def _value(row):
    return Entry(**{k: row[k] for k in ('kind', 'digest', 'mode', 'byte_count')}) if row else None


def _current(root, paths):
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    values = {}
    try:
        for path in paths:
            try:
                values[path] = snapshot_store.read_file(None, None, fd, path, retain=False)
            except FileNotFoundError:
                pass
    finally:
        os.close(fd)
    return values


def preview(db, actor, space, repository, wid, before_id, after_id, paths):
    project, workspace, assignment = service.scoped(db, actor, space, repository, wid)
    if workspace['lifecycle'] != 'ready':
        raise WorktreeConflict('workspace_unavailable')
    if not paths or len(paths) > 256 or len(paths) != len(set(paths)):
        raise WorktreeConflict('invalid_restore_selection')
    for path in paths:
        validate_path(path)
        from app.moonbox_exec_server.scope import EXCLUDED, excluded
        if excluded(path) or any(path == value or path.startswith(value + '/') for value in EXCLUDED):
            raise WorktreeConflict('path_outside_recovery_scope')
        if assignment:
            from app.moonbox_core.delivery_policy import writable_roots
            if not any(path == value or path.startswith(value + '/') for value in writable_roots(assignment['change_id'])):
                raise WorktreeConflict('path_outside_recovery_scope')
    before, after = _point(db, wid, before_id), _point(db, wid, after_id)
    catalog.require_read(db, actor, project, before)
    catalog.require_read(db, actor, project, after)
    if before['policy_version'] != after['policy_version']:
        raise WorktreeConflict('recovery_policy_changed')
    left, right = _entries(db, before_id, paths), _entries(db, after_id, paths)
    if any(path not in left and path not in right for path in paths):
        raise WorktreeConflict('path_outside_recovery_scope')
    repo = Repository.open(workspace['root_locator'])
    if repo.identity != workspace['git_identity']:
        raise WorktreeConflict('repository_identity_mismatch')
    now = _current(repo.root, paths)
    result = preflight({k: _value(v) for k, v in left.items()}, {k: _value(v) for k, v in right.items()},
        {k: _value(v) for k, v in now.items()}, paths)
    current_digest = fingerprint({k: _value(v) for k, v in now.items()},
        policy_version=before['policy_version'], head_commit=repo.head())
    digest = hashlib.sha256(json.dumps([wid, workspace['revision'], before_id, after_id,
        before['manifest_hash'], after['manifest_hash'], paths, current_digest], separators=(',', ':')).encode()).hexdigest()
    return {'fingerprint': digest, 'current_digest': current_digest, 'items': result,
        'can_restore': not any(item['action'] in ('conflict', 'unsupported') for item in result)}, (workspace, left, right, now)


def _protect_current(db, workspace, cid, selected, now, operation_id):
    """Persist the exact write set before first mutation, independent of turn history."""
    if not db.scalar(select(conversations.c.id).join(session_bindings,
            conversations.c.id == session_bindings.c.conversation_id).where(conversations.c.id == cid,
            conversations.c.deleted_at.is_(None), session_bindings.c.workspace_id == workspace['id'])):
        raise WorktreeConflict('restore_session_unavailable')
    catalog._lock(db, workspace['id'])
    identifier = chat.identity()
    sequence = (db.scalar(select(func.max(points.c.sequence)).where(points.c.workspace_id == workspace['id'])) or 0) + 1
    policy = hashlib.sha256(json.dumps(['restore-write-set-v1', selected]).encode()).hexdigest()
    head = Repository.open(workspace['root_locator']).head()
    digest = fingerprint({k: _value(v) for k, v in now.items()}, policy_version=policy, head_commit=head)
    from app.moonbox_core.schema import assignments
    change_id = db.scalar(select(assignments.c.change_id).where(assignments.c.workspace_id == workspace['id']))
    db.execute(insert(points).values(**identifier, workspace_id=workspace['id'], sequence=sequence,
        version_id=identifier['id'], manifest_hash=digest, policy_version=policy, head_commit=head,
        changed=1, state='building', scope_json=json.dumps(selected), change_id=change_id))
    fd = os.open(workspace['root_locator'], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for path in selected:
            if path not in now:
                continue
            value = snapshot_store.read_file(db, cid, fd, path, retain=True)
            if _value(value) != _value(now[path]):
                raise RestoreConflict('restore_checkpoint_changed')
            db.execute(insert(entries).values(point_id=identifier['id'], path_key=hashlib.sha256(path.encode()).hexdigest(), path=path, **value))
    finally:
        os.close(fd)
    db.execute(update(points).where(points.c.id == identifier['id']).values(state='complete'))
    catalog.reference(db, workspace['id'], identifier['id'], 'restore_safety', operation_id, 'before_restore')
    return identifier['id']


def start(db, actor, space, repository, wid, cid, before_id, after_id, paths, expected_fingerprint, request_id):
    request_digest = hashlib.sha256(json.dumps([cid, before_id, after_id, paths, expected_fingerprint], separators=(',', ':')).encode()).hexdigest()
    service.scoped(db, actor, space, repository, wid, write=True)
    existing = db.execute(select(operations).where(operations.c.workspace_id == wid,
        operations.c.actor_id == actor, operations.c.request_id == request_id)).mappings().first()
    if existing:
        if existing['request_digest'] != request_digest:
            raise WorktreeConflict('restore_request_conflict')
        return dict(existing)
    row = chat.identity()
    workspaces.acquire(db, wid, row['id'], 1)
    checked, (workspace, left, right, now) = preview(db, actor, space, repository, wid, before_id, after_id, paths)
    if checked['fingerprint'] != expected_fingerprint or not checked['can_restore']:
        raise WorktreeConflict('restore_preflight_stale_or_conflicted')
    parent = chat.conversation(db, actor, cid)
    if (parent['space_id'], parent['repository_id']) != (space, repository):
        raise WorktreeConflict('restore_session_scope_mismatch')
    safety = _protect_current(db, workspace, cid, paths, now, row['id'])
    mutations = {item['path'] for item in checked['items'] if item['action'] in ('restore', 'delete')}
    plan = [{'path': path, 'expected': asdict(_value(now[path])) if path in now else None,
        'desired': asdict(_value(left[path])) if path in left else None,
        'object_id': left.get(path, {}).get('object_id')} for path in paths if path in mutations]
    row.update(workspace_id=wid, actor_id=actor, request_id=request_id, request_digest=request_digest,
        before_id=before_id, after_id=after_id, current_digest=checked['current_digest'],
        state='pending', plan=json.dumps({'files': plan, 'safety_point': safety,
            'head_commit': Repository.open(workspace['root_locator']).head()}), error_code=None)
    db.execute(insert(operations).values(**row))
    record(db, row['id'], actor, 'restore', 'queued', workspace_id=wid)
    for path in paths:
        db.execute(insert(steps).values(operation_id=row['id'], path_key=hashlib.sha256(path.encode()).hexdigest(), state='pending'))
    for role, pid in [('restore_before', before_id), ('restore_after', after_id)]:
        catalog.reference(db, wid, pid, role, row['id'], 'restore_in_flight')
    db.commit()  # Operation + pins + safety point exist durably before any filesystem write.
    return row


def _authorize_operation(db, actor, space, repository, operation):
    project, workspace, _ = service.scoped(db, actor, space, repository, operation['workspace_id'], write=True)
    for pid in (operation['before_id'], operation['after_id']):
        point = db.execute(select(points).where(points.c.id == pid, points.c.workspace_id == workspace['id'])).mappings().one()
        catalog.require_read(db, actor, project, point)
    return workspace


def run(factory, actor, space, repository, operation_id):
    with factory() as db:
        operation = db.execute(select(operations).where(operations.c.id == operation_id,
            operations.c.actor_id == actor)).mappings().first()
        if not operation:
            raise WorktreeConflict('restore_operation_unavailable')
        workspace = _authorize_operation(db, actor, space, repository, operation)
        if operation['state'] == 'completed':
            return public(operation)
        workspaces.acquire(db, workspace['id'], operation_id, 1)
        db.commit()
        plan = json.loads(operation['plan'])
    for item in plan['files']:
        key = hashlib.sha256(item['path'].encode()).hexdigest()
        try:
            with factory() as db:
                _authorize_operation(db, actor, space, repository, operation)
                db.execute(update(write_locks).where(write_locks.c.workspace_id == workspace['id']).values(generation=write_locks.c.generation))
                lock = db.execute(select(write_locks).where(write_locks.c.workspace_id == workspace['id']).with_for_update()).mappings().one()
                if (lock['operation_id'], lock['generation']) != (operation_id, 1):
                    raise WorktreeConflict('restore_operation_fenced')
                repo = Repository.open(workspace['root_locator'])
                if repo.identity != workspace['git_identity'] or repo.head() != plan['head_commit']:
                    raise WorktreeConflict('restore_baseline_changed')
                if db.scalar(select(steps.c.state).where(steps.c.operation_id == operation_id, steps.c.path_key == key)) == 'completed':
                    continue
                desired = Entry(**item['desired']) if item['desired'] else None
                expected = Entry(**item['expected']) if item['expected'] else None
                # Rechecks content immediately before replacement and validates streamed bytes.
                apply_one(workspace['root_locator'], item['path'], expected=expected, desired=desired,
                    blocks=content_store.blocks(db, item['object_id']) if desired and item['object_id'] else ())
                db.execute(update(steps).where(steps.c.operation_id == operation_id, steps.c.path_key == key).values(state='completed'))
                db.execute(update(operations).where(operations.c.id == operation_id).values(state='running', error_code=None, updated_at=chat.now()))
                db.commit()
        except (RestoreConflict, WorktreeConflict, OSError, ValueError, chat.ChatError):
            with factory() as db:
                db.execute(update(operations).where(operations.c.id == operation_id).values(state='blocked', error_code='restore_step_requires_recheck', updated_at=chat.now()))
                record(db, operation_id, actor, 'restore', 'blocked', workspace_id=workspace['id'], error_code='restore_step_requires_recheck')
                db.commit()
            raise WorktreeConflict('restore_step_requires_recheck') from None
    with factory() as db:
        service.scoped(db, actor, space, repository, workspace['id'], write=True)
        db.execute(update(operations).where(operations.c.id == operation_id).values(state='completed', updated_at=chat.now(), error_code=None))
        db.execute(delete(references).where(references.c.owner_id == operation_id,
            references.c.owner_type.in_(('restore_before', 'restore_after'))))
        workspaces.release(db, workspace['id'], operation_id, 1)
        record(db, operation_id, actor, 'restore', 'completed', workspace_id=workspace['id'])
        db.commit()
        return public(db.execute(select(operations).where(operations.c.id == operation_id)).mappings().one())


def public(row):
    return {key: row[key] for key in ('id', 'workspace_id', 'state', 'error_code', 'created_at', 'updated_at')}
