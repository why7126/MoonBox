"""Extract a protected recovery point into a separate, non-development Git worktree."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL
from sqlalchemy import insert, select, update
from app.chat import content_store
from app.chat.settings import repository_binding
from app.moonbox_core import service, workspaces
from app.moonbox_core.schema import workspaces as table, main_bindings
from app.moonbox_worktree import Repository, WorktreeConflict
from .schema import entries, points
from .restore import _point, _current, _value
from .restore_io import apply_one
from . import catalog


def create(db, actor, space_id, repository_id, workspace_id, point_id, request_id):
    project, source, _ = service.scoped(db, actor, space_id, repository_id, workspace_id, write=True)
    point = _point(db, workspace_id, point_id)
    catalog.require_read(db, actor, project, point)
    if not point['scope_json']:
        raise WorktreeConflict('recovery_scope_unknown')
    allowed = json.loads(point['scope_json'])
    identifier = str(uuid5(NAMESPACE_URL, '\0'.join(['moonbox-recovery', actor, workspace_id, request_id])))
    owner = hashlib.sha256((actor + '\0' + request_id).encode()).hexdigest()
    row = db.execute(select(table).where(table.c.id == identifier)).mappings().first()
    from .schema import references
    existing = db.execute(select(references).where(references.c.workspace_id == workspace_id,
        references.c.owner_type == 'recovery_tree', references.c.owner_id == identifier)).mappings().first()
    if existing and existing['point_id'] != point_id:
        raise WorktreeConflict('recovery_request_conflict')
    main_id = db.scalar(select(main_bindings.c.workspace_id).where(main_bindings.c.space_id == space_id,
        main_bindings.c.repository_id == repository_id))
    main = workspaces.get(db, space_id, repository_id, main_id)
    config = repository_binding(repository_id, space_id)
    if not config or not config.get('workspace_root'):
        raise WorktreeConflict('managed_root_unavailable')
    if not row:
        row = workspaces._row(identifier, space_id, repository_id, main['git_identity'], 'recovery',
            Path(config['workspace_root']) / identifier, point['head_commit'])
        row['lifecycle'] = 'preparing'
        db.execute(insert(table).values(**row))
    if row['lifecycle'] == 'ready':
        return workspaces.public(row)
    catalog.reference(db, workspace_id, point_id, 'recovery_tree', identifier, 'recovery_directory')
    workspaces.acquire(db, identifier, owner, 1)
    db.commit()
    repo = Repository.open(main['root_locator'])
    if repo.identity != source['git_identity'] or repo.identity != main['git_identity']:
        raise WorktreeConflict('repository_identity_mismatch')
    root = Path(row['root_locator'])
    if not root.exists():
        repo.create(root.parent, identifier, point['head_commit'])
    else:
        child = repo.verify(root)
        if child.head() != point['head_commit']:
            raise WorktreeConflict('recovery_baseline_changed')
    # The isolated checkout is not a development claim. Only supported files are
    # extracted; unsupported links remain explicitly visible in point metadata.
    cursor = ''
    unsupported = 0
    while True:
        batch = list(db.execute(select(entries).where(entries.c.point_id == point_id,
            entries.c.path_key > cursor).order_by(entries.c.path_key).limit(100)).mappings())
        if not batch:
            break
        for item in batch:
            if item['kind'] != 'file' or not item['object_id']:
                unsupported += 1
                continue
            desired = _value(item)
            current = _current(root, [item['path']]).get(item['path'])
            # Never overwrite edits in an interrupted recovery checkout. Its Git
            # baseline or already extracted point are the only accepted states.
            baseline = _baseline(root, point['head_commit'], item['path'])
            if current and _value(current) != desired and _value(current) != baseline:
                raise WorktreeConflict('recovery_directory_modified')
            apply_one(root, item['path'], expected=_value(current), desired=desired,
                blocks=content_store.blocks(db, item['object_id']))
        cursor = batch[-1]['path_key']
    from app.moonbox_exec_server.scope import names
    for path in names(root, allowed):
        key = hashlib.sha256(path.encode()).hexdigest()
        if db.scalar(select(entries.c.path_key).where(entries.c.point_id == point_id, entries.c.path_key == key)):
            continue
        current = _current(root, [path]).get(path)
        baseline = _baseline(root, point['head_commit'], path)
        if current and (_value(current).kind != 'file' or _value(current) != baseline):
            raise WorktreeConflict('recovery_directory_modified')
        apply_one(root, path, expected=_value(current), desired=None)
    db.execute(update(table).where(table.c.id == identifier).values(lifecycle='ready', updated_at=workspaces.stamp()))
    workspaces.release(db, identifier, owner, 1)
    db.commit()
    return workspaces.public(dict(row) | {'lifecycle': 'ready'}) | {'unsupported_files': unsupported}


def _baseline(root, head, path):
    from app.moonbox_worktree.git import _run
    from app.chat.workspace import git_env
    from .recovery import Entry
    record = _run(root, 'ls-tree', '-z', head, '--', path)
    if not record:
        return None
    mode, kind, oid = record.split(b'\t', 1)[0].decode().split()
    if kind != 'blob' or mode not in ('100644', '100755'):
        return None
    with tempfile.TemporaryFile() as output:
        result = subprocess.run(['git', '-C', str(root), 'cat-file', 'blob', oid],
            env=git_env(), stdout=output, stderr=subprocess.DEVNULL, timeout=60)
        if result.returncode:
            raise WorktreeConflict('recovery_baseline_unavailable')
        output.seek(0); digest = hashlib.sha256(); size = 0
        while chunk := output.read(65536):
            digest.update(chunk); size += len(chunk)
    return Entry('file', digest.hexdigest(), 0o755 if mode == '100755' else 0o644, size)
