"""Operator recovery of a completed, attributable review without rerunning the model."""
from pathlib import Path

from sqlalchemy import select, update

from app.chat import service
from app.chat.schema import conversations, turns, governance_candidates as candidates, governance_applications as applications
from app.chat.settings import repository_binding
from app.chat.workspace import snapshot, trusted_directory
from app.governance import scope, store
from app.governance.reader import ProjectReader
from app.governance.snapshot import stable


def recover(db, actor, turn_id):
    from app.governance.completion_recovery import prepare_completion
    from app.governance.preparation import _write_command, _candidate_id, bind_candidate_turn, collect
    turn = db.execute(select(turns).where(turns.c.id == turn_id)).mappings().one()
    parent = service.conversation(db, actor, turn['conversation_id'])
    command = _write_command(turn['prompt'])
    if not command or command[0] not in ('req-review', 'bug-review') or turn['status'] != 'completed':
        raise service.ChatError(2604, '仅可恢复已执行完成的评审轮次', 409)
    if parent['active_turn_id'] or parent['deleted_at']:
        raise service.ChatError(2604, '会话仍有执行中的轮次，暂不能恢复', 409)
    locked = db.execute(update(conversations).where(conversations.c.id == parent['id'],
        conversations.c.active_turn_id.is_(None), conversations.c.generation == parent['generation'])
        .values(updated_at=parent['updated_at'])).rowcount
    if not locked:
        raise service.ChatError(2606, '会话已变化，请重试', 409)
    action, oid = command
    project = scope.authorize(db, actor, parent['space_id'], parent['repository_id'], write=True)
    reader = ProjectReader(db, actor, project)
    cid = _candidate_id(actor, project.key, oid, action, turn['client_request_id'])['id']
    existing = db.execute(select(candidates).where(candidates.c.id == cid)).mappings().first()
    if existing and existing['error_code'] == 'source_recovery_blocked':
        # Only this attributable operator recovery may inspect a blocked source.
        if (existing['actor_id'] != actor or existing['scope_key'] != project.key
                or existing['prepared_turn_id'] != turn_id or
                db.scalar(select(applications.c.id).where(applications.c.scope_key == project.key,
                    applications.c.state.in_(('applying','recovering','recovery_blocked'))).limit(1))):
            raise service.ChatError(2606, '恢复归属或项目状态不可确认', 409)
        baseline = stable(project.root)
    else:
        baseline = reader.snapshot()
    reader.authorize_object(baseline, oid, write=True)
    binding = repository_binding(parent['repository_id'], parent['space_id'])
    if existing and existing['state'] != 'rejected':
        return {'candidate_id': cid, 'state': existing['state']}
    if db.scalar(select(candidates.c.id).where(candidates.c.conversation_id == parent['id'],
            candidates.c.state.in_(('prepared', 'running', 'pending'))).limit(1)):
        raise service.ChatError(2604, '会话已有未完成治理操作', 409)
    if binding.get('workspace_mode') == 'source':
        if (not existing or existing['prepared_turn_id'] != turn_id
                or existing['binding_revision'] != project.binding_revision
                or db.scalar(select(applications.c.id).where(applications.c.candidate_id == cid).limit(1))
                or db.scalar(select(turns.c.id).where(turns.c.conversation_id == parent['id'],
                    turns.c.id != turn_id, turns.c.created_at >= turn['created_at']).limit(1))):
            raise service.ChatError(2606, '原评审轮次基准或归属不可确认，保留成果', 409)
        record = store.read(cid, 'baseline')
        if record.get('workspace_mode') != 'source':
            raise service.ChatError(2606, '工作区模式已变化，保留成果', 409)
        workspace = trusted_directory(Path(binding['source_root']))
        db.execute(update(candidates).where(candidates.c.id == cid).values(state='running', error_code=None))
        collect(db, parent, turn_id, workspace, 'completed')
        return {'candidate_id': cid, 'state': db.scalar(select(candidates.c.state).where(candidates.c.id == cid))}
    if not binding.get('workspace_root'):
        raise service.ChatError(2604, '缺少原工作区，保留成果', 409)
    workspace = trusted_directory(Path(binding['workspace_root']) / parent['id'])
    if existing:
        return retry_rejected(db, parent, project, baseline, workspace, existing, turn)
    prepare_completion(db, actor, parent, project, {'id': oid}, baseline, turn['client_request_id'], action)
    record = store.read(cid, 'baseline')
    if not record.get('recovery_hash') or snapshot(workspace)['hash'] != record['recovery_hash']:
        raise service.ChatError(2606, '原工作区成果或恢复基准不可确认', 409)
    bind_candidate_turn(db, cid, turn_id)
    db.execute(update(candidates).where(candidates.c.id == cid).values(state='running'))
    collect(db, parent, turn_id, workspace, 'completed')
    return {'candidate_id': cid, 'state': db.scalar(select(candidates.c.state).where(candidates.c.id == cid))}


def retry_rejected(db, parent, project, baseline, workspace, candidate, turn):
    """Revalidate retained bytes, then rebase only unrelated source changes."""
    from app.governance.candidates import validate
    from app.governance.review import allowed_paths
    from app.governance.preparation import collect
    cid = candidate['id']
    if candidate['prepared_turn_id'] != turn['id'] or db.scalar(select(applications.c.id).where(applications.c.candidate_id == cid).limit(1)):
        raise service.ChatError(2604, '已有应用记录或轮次不匹配，不能重置候选', 409)
    later = db.scalar(select(turns.c.id).where(turns.c.conversation_id == parent['id'],
        turns.c.id != turn['id'], turns.c.created_at >= turn['created_at']).limit(1))
    if later:
        raise service.ChatError(2606, '会话已有后续轮次，不能将当前成果归属于旧轮次', 409)
    record = store.read(cid, 'baseline')
    original = {p: b.encode() for p, b in record['files'].items()}
    if project.binding_revision != candidate['binding_revision']:
        raise service.ChatError(2606, '项目绑定已变化，不能恢复', 409)
    for path in allowed_paths(record['base_path'], original):
        if original.get(path) != baseline.files.get(path):
            raise service.ChatError(2606, '目标事实源已变化，保留成果并阻断恢复', 409)
    current = snapshot(workspace, text_bytes=1024*1024, max_text_bytes=32*1024*1024)
    old = record['workspace_manifest']
    changed = {p for p in old.keys() | current['files'].keys() if old.get(p) != {
        k: v for k, v in current['files'].get(p, {}).items() if k in ('kind', 'sha256', 'executable')}}
    after = dict(baseline.files)
    for path in changed:
        item = current['files'].get(path)
        if item is None:
            after.pop(path, None)
        elif item['kind'] != 'file' or item['text'] is None:
            raise service.ChatError(2604, '成果包含不可应用文件，已保留', 409)
        else:
            after[path] = item['text'].encode()
    from app.governance.review_finalization import finalize_review
    finalized = finalize_review(baseline.files, after, candidate['object_id'], record['base_path'], candidate['action'])
    repaired = {p for p in finalized if finalized[p] != after.get(p)}
    checked = validate(baseline.files, finalized, candidate['object_id'], record['base_path'], candidate['action'])
    if changed | repaired != {f['path'] for f in checked['files']} or snapshot(workspace)['hash'] != current['hash']:
        raise service.ChatError(2606, '工作区变化或存在越界成果，不能恢复', 409)
    if not record.get('recovery_origin_saved'):
        store.write(cid, 'recovery-origin', record)
        record['recovery_origin_saved'] = True
    record['files'] = {p: b.decode() for p, b in baseline.files.items()}
    store.write(cid, 'baseline', record)
    db.execute(update(candidates).where(candidates.c.id == cid, candidates.c.state == 'rejected').values(
        state='running', baseline_hash=baseline.revision, error_code=None, updated_at=service.now()))
    collect(db, parent, turn['id'], workspace, 'completed')
    return {'candidate_id': cid, 'state': db.scalar(select(candidates.c.state).where(candidates.c.id == cid))}
