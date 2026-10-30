"""Publish and pin immutable recovery points under the workspace row lock."""
import json
import os
from sqlalchemy import insert, select, update, func, delete
from app.chat import service
from app.chat.content_schema import versions
from app.moonbox_core.schema import workspaces, session_bindings
from .schema import points, references, entries, snapshot_points
from .recovery import rotation_candidates


def _lock(db, workspace_id):
    if db.execute(update(workspaces).where(workspaces.c.id == workspace_id,
            workspaces.c.lifecycle == 'ready').values(updated_at=workspaces.c.updated_at)).rowcount != 1:
        raise ValueError('workspace_unavailable')


def publish(db, workspace_id, version_id, *, policy_version, head_commit, changed, scope=None):
    _lock(db, workspace_id)
    version = db.execute(select(versions).join(session_bindings,
        versions.c.conversation_id == session_bindings.c.conversation_id).where(
        versions.c.id == version_id, session_bindings.c.workspace_id == workspace_id,
        versions.c.status == 'complete')).mappings().first()
    if not version or not version['manifest_hash']:
        raise ValueError('snapshot_unavailable_or_outside_workspace')
    from app.moonbox_core.schema import assignments
    change_id = db.scalar(select(assignments.c.change_id).where(assignments.c.workspace_id == workspace_id))
    previous = db.execute(select(points).where(points.c.workspace_id == workspace_id,
        points.c.state == 'complete').order_by(points.c.sequence.desc()).limit(1)).mappings().first()
    if previous and previous['change_id'] == change_id and (previous['manifest_hash'], previous['policy_version'], previous['head_commit']) == (
            version['manifest_hash'], policy_version, head_commit):
        _associate(db, version_id, previous['id'])
        return dict(previous)
    sequence = (db.scalar(select(func.max(points.c.sequence)).where(points.c.workspace_id == workspace_id)) or 0) + 1
    row = dict(**service.identity(), workspace_id=workspace_id, version_id=version_id,
        sequence=sequence, manifest_hash=version['manifest_hash'], policy_version=policy_version,
        head_commit=head_commit, changed=int(changed), state='complete',
        scope_json=json.dumps(scope) if scope is not None else None, change_id=change_id)
    db.execute(insert(points).values(**row))
    from app.chat.snapshot_store import page
    cursor = ''
    while batch := page(db, version_id, cursor, 256):
        db.execute(insert(entries), [{k: item[k] for k in ('path_key','path','kind','mode','digest','byte_count','object_id')}
            | {'point_id': row['id']} for item in batch])
        cursor = batch[-1]['path_key']
    _associate(db, version_id, row['id'])
    return row


def _associate(db, version_id, point_id):
    old = db.scalar(select(snapshot_points.c.point_id).where(snapshot_points.c.version_id == version_id))
    if old and old != point_id:
        raise ValueError('snapshot_point_identity_conflict')
    if not old:
        db.execute(insert(snapshot_points).values(version_id=version_id, point_id=point_id))


def reference(db, workspace_id, point_id, owner_type, owner_id, protection_reason=None):
    _lock(db, workspace_id)
    point = db.execute(select(points).where(points.c.workspace_id == workspace_id,
        points.c.id == point_id, points.c.state == 'complete')).mappings().first()
    if not point:
        raise ValueError('recovery_point_unavailable')
    key = (references.c.workspace_id == workspace_id, references.c.owner_type == owner_type,
           references.c.owner_id == owner_id)
    existing = db.execute(select(references).where(*key)).mappings().first()
    if existing:
        if (existing['point_id'], existing['protection_reason']) != (point_id, protection_reason):
            raise ValueError('recovery_reference_identity_conflict')
        return
    db.execute(insert(references).values(workspace_id=workspace_id, point_id=point_id,
        owner_type=owner_type, owner_id=owner_id, protection_reason=protection_reason))


def unprotect_manual(db, workspace_id, point_id, actor):
    _lock(db, workspace_id)
    # System pins are never released via this entry point.
    return db.execute(delete(references).where(references.c.workspace_id == workspace_id,
        references.c.point_id == point_id, references.c.owner_type == 'manual',
        references.c.owner_id == actor)).rowcount


def retention_count():
    raw = os.environ.get('MOONBOX_WORKSPACE_RECOVERY_KEEP', '10')
    if not raw.isascii() or not raw.isdigit() or int(raw) < 1:
        raise ValueError('invalid_retention_count')
    return int(raw)


def rotate(db, workspace_id):
    _lock(db, workspace_id)
    rows = db.execute(select(points).where(points.c.workspace_id == workspace_id)).mappings().all()
    protected = set(db.scalars(select(references.c.point_id).where(
        references.c.workspace_id == workspace_id, references.c.protection_reason.is_not(None))))
    candidates = rotation_candidates(rows, protected, keep=retention_count())
    if candidates:
        db.execute(delete(entries).where(entries.c.point_id.in_(candidates)))
        from app.chat.content_schema import entries as snapshot_entries
        expired_versions = select(snapshot_points.c.version_id).where(snapshot_points.c.point_id.in_(candidates))
        db.execute(delete(snapshot_entries).where(snapshot_entries.c.version_id.in_(expired_versions)))
        db.execute(update(versions).where(versions.c.id.in_(expired_versions)).values(status='expired'))
        db.execute(update(points).where(points.c.id.in_(candidates)).values(state='expired'))
    # Content reclamation is separate: this never deletes conversation history or chunks.
    return candidates


def can_read(db, actor, project, point):
    if not point['change_id']:
        return True
    from app.governance.scope import visible
    return visible(db, actor, project, point['change_id'])


def require_read(db, actor, project, point):
    if not can_read(db, actor, project, point):
        raise service.ChatError(2601, '无权访问恢复点所属变更', 403)
