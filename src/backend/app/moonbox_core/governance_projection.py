"""Main-only integration facts, separate from workflow phase and archive semantics."""
import json
import os
import re
import stat
import yaml
from sqlalchemy import select, update
from app.moonbox_worktree import Repository, WorktreeConflict
from app.governance.writer import project_lock
from .authority import delivery
from . import workspaces
from .integration_schema import operations, candidates


def _read(root, relative):
    from app.chat.snapshot_store import parent_fd
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    parent = None
    try:
        parent, name = parent_fd(fd, relative)
        handle = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        with os.fdopen(handle, 'rb') as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise WorktreeConflict('governance_projection_unsafe_file')
            value = stream.read(2*1024*1024+1)
        if len(value) > 2*1024*1024:
            raise WorktreeConflict('governance_projection_too_large')
        return value.decode('utf-8')
    finally:
        if parent is not None: os.close(parent)
        os.close(fd)


def _plan(root, candidate, operation):
    changes = []
    fact = {'state': 'integrated', 'change_id': candidate['change_id'], 'operation_id': operation['id'],
            'commit': candidate['candidate_commit']}
    if candidate['delivery_root'].startswith(('REQ-', 'BUG-')):
        kind = 'requirements' if candidate['delivery_root'].startswith('REQ-') else 'bugs'
        path = f'issues/{kind}/_registry.yaml'
        before = _read(root, path)
        data = yaml.safe_load(before)
        matches = [row for row in data.get('entries', []) if row.get('id') == candidate['delivery_root']]
        if len(matches) != 1:
            raise WorktreeConflict('governance_projection_identity_invalid')
        # Do not change review, Sprint or archive phase. These remain their own workflow facts.
        matches[0]['workspace_integration'] = fact
        changes.append({'path': path, 'before': before, 'after': yaml.safe_dump(data, allow_unicode=True, sort_keys=False)})
    sprint = candidate['sprint_id']
    if not re.fullmatch(r'sprint-[0-9]{3}', sprint):
        raise WorktreeConflict('governance_projection_identity_invalid')
    path = f'iterations/change/{sprint}/sprint.md'
    before = _read(root, path)
    start, end = '<!-- moonbox:workspace-integrations:start -->', '<!-- moonbox:workspace-integrations:end -->'
    line = f"- `{candidate['change_id']}`：已合入 `{candidate['candidate_commit']}`；操作 `{operation['id']}`。正式归档另行执行。"
    if start in before or end in before:
        if before.count(start) != 1 or before.count(end) != 1 or before.index(start) >= before.index(end):
            raise WorktreeConflict('governance_projection_marker_invalid')
        prefix, rest = before.split(start, 1); middle, suffix = rest.split(end, 1)
        lines = [row for row in middle.strip().splitlines() if f'操作 `{operation["id"]}`' not in row]
        after = prefix + start + '\n' + '\n'.join([*lines, line]) + '\n' + end + suffix
    else:
        after = before.rstrip() + '\n\n## 工作区成果合入\n\n' + start + '\n' + line + '\n' + end + '\n'
    changes.append({'path': path, 'before': before, 'after': after})
    return changes


def _replace(root, item):
    # Compare actual bytes immediately before atomic replacement; never overwrite drift.
    from app.chat.snapshot_store import parent_fd
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    parent = None
    temporary = '.moonbox-projection-' + os.urandom(12).hex()
    try:
        parent, name = parent_fd(fd, item['path'])
        if _read(root, item['path']) != item['before']:
            raise WorktreeConflict('governance_projection_changed')
        mode = os.stat(name, dir_fd=parent, follow_symlinks=False).st_mode & 0o777
        target = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, mode, dir_fd=parent)
        with os.fdopen(target, 'wb') as stream:
            stream.write(item['after'].encode()); stream.flush(); os.fsync(stream.fileno())
        if _read(root, item['path']) != item['before']:
            raise WorktreeConflict('governance_projection_changed')
        os.rename(temporary, name, src_dir_fd=parent, dst_dir_fd=parent)
        os.fsync(parent)
    finally:
        if parent is not None:
            try: os.unlink(temporary, dir_fd=parent)
            except FileNotFoundError: pass
            os.close(parent)
        os.close(fd)


def _authorize(db, operation, candidate):
    project, context = delivery(db, operation['actor_id'], candidate['space_id'], candidate['repository_id'], candidate['change_id'])
    if (context['delivery_root'], context['sprint_id'], str(project.binding_revision)) != (candidate['delivery_root'], candidate['sprint_id'], candidate['binding_revision']):
        raise WorktreeConflict('governance_projection_authority_changed')
    return project


def apply(factory, operation_id):
    """Only updates integration metadata; file drift and revoked authority stop new writes."""
    with factory() as db:
        operation = db.execute(select(operations).where(operations.c.id == operation_id)).mappings().one()
        if operation['state'] != 'completed' or operation['governance_state'] == 'completed':
            return
        candidate = db.execute(select(candidates).where(candidates.c.id == operation['candidate_id'])).mappings().one()
        project = _authorize(db, operation, candidate)
        main = workspaces.get(db, candidate['space_id'], candidate['repository_id'], candidate['main_workspace_id'])
        workspaces.acquire(db, main['id'], 'projection-' + operation_id, 1)
        db.commit()
        with project_lock(project):
            repo = Repository.open(main['root_locator'])
            from app.moonbox_worktree.git import _run
            if (repo.identity != main['git_identity'] or repo.head() != candidate['candidate_commit']
                    or project.root != repo.root
                    or _run(repo.root, 'symbolic-ref', '--quiet', 'HEAD').decode().strip() != candidate['target_ref']):
                raise WorktreeConflict('governance_projection_target_changed')
            plan = json.loads(operation['governance_plan']) if operation['governance_plan'] else None
            if plan is None:
                repo.require_clean()
                plan = _plan(repo.root, candidate, operation)
                db.execute(update(operations).where(operations.c.id == operation_id).values(
                    governance_state='applying', governance_plan=json.dumps(plan, ensure_ascii=False)))
                db.commit()
            for item in plan:
                db.commit()
                _authorize(db, operation, candidate)
                current = _read(repo.root, item['path'])
                if current == item['after']:
                    continue
                if current != item['before']:
                    raise WorktreeConflict('governance_projection_changed')
                _replace(repo.root, item)
            for item in plan:
                if _read(repo.root, item['path']) != item['after']:
                    raise WorktreeConflict('governance_projection_readback_failed')
            db.execute(update(operations).where(operations.c.id == operation_id).values(governance_state='completed'))
            workspaces.release(db, main['id'], 'projection-' + operation_id, 1)
            db.commit()


def try_apply(factory, operation_id):
    try:
        apply(factory, operation_id)
    except Exception:
        # The Git result stays completed. Only the independent projection is blocked.
        with factory.begin() as db:
            db.execute(update(operations).where(operations.c.id == operation_id,
                operations.c.governance_state != 'completed').values(governance_state='blocked'))
