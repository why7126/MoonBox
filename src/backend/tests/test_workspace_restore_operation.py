"""Real Git/files/chunk store; only external identity/catalog lookup is substituted."""
import hashlib
from types import SimpleNamespace
import pytest
from sqlalchemy import insert, select, update
from app.chat import service as chat_service, snapshot_store
from app.chat.schema import conversations, turns
from app.moonbox_core import service, workspaces
from app.moonbox_core.schema import session_bindings, write_locks
from app.moonbox_rollout import catalog, restore
from app.moonbox_rollout.schema import operations, steps, entries, points
from app.moonbox_worktree import WorktreeConflict
from test_chat import chat, create
from test_managed_worktree_git import repo


@pytest.fixture
def recovery(chat, repo, monkeypatch):
    client, factory = chat
    source, _ = repo
    cid = create(client)
    with factory.begin() as db:
        main = workspaces.register_main(db, 'space', 'repo', source.root)
        db.execute(insert(session_bindings).values(conversation_id=cid, workspace_id=main['id']))
        tid = chat_service.identity()
        db.execute(insert(turns).values(**tid, conversation_id=cid, client_request_id='snapshot', status='completed', prompt='synthetic snapshot'))
    def scoped(db, actor, space, repository, wid, **kwargs):
        assert actor == 'alice' and space == 'space' and repository == 'repo'
        return SimpleNamespace(), workspaces.get(db, space, repository, wid), None
    monkeypatch.setattr(service, 'scoped', scoped)
    def point(phase):
        snap = snapshot_store.capture(factory, cid, tid['id'], source.root, phase, policy_roots=('',))
        with factory.begin() as db:
            return catalog.publish(db, main['id'], snap['version_id'], policy_version='policy', head_commit=source.head(), changed=True)['id']
    before = point('before')
    (source.root/'file.txt').write_text('agent result')
    (source.root/'new.txt').write_text('agent addition')
    after = point('after')
    return factory, source.root, main['id'], cid, before, after


def test_restore_preflight_then_persisted_undo_and_replay(recovery):
    factory, root, wid, cid, before, after = recovery
    paths = ['file.txt', 'new.txt']
    with factory() as db:
        checked, _ = restore.preview(db, 'alice', 'space', 'repo', wid, before, after, paths)
        assert checked['can_restore']
        operation = restore.start(db, 'alice', 'space', 'repo', wid, cid, before, after, paths, checked['fingerprint'], 'restore-one')
    assert (root/'file.txt').read_text() == 'agent result'
    result = restore.run(factory, 'alice', 'space', 'repo', operation['id'])
    assert result['state'] == 'completed'
    assert (root/'file.txt').read_text() == 'baseline'
    assert not (root/'new.txt').exists()
    assert restore.run(factory, 'alice', 'space', 'repo', operation['id']) == result
    with factory() as db:
        assert db.scalar(select(write_locks.c.workspace_id)) is None
        assert restore.start(db, 'alice', 'space', 'repo', wid, cid, before, after, paths, checked['fingerprint'], 'restore-one')['id'] == operation['id']


def test_stale_preflight_and_external_edit_are_preserved(recovery):
    factory, root, wid, cid, before, after = recovery
    with factory() as db:
        checked, _ = restore.preview(db, 'alice', 'space', 'repo', wid, before, after, ['file.txt'])
    (root/'file.txt').write_text('human edit')
    with factory() as db, pytest.raises(WorktreeConflict, match='stale_or_conflicted'):
        restore.start(db, 'alice', 'space', 'repo', wid, cid, before, after, ['file.txt'], checked['fingerprint'], 'stale')
    assert (root/'file.txt').read_text() == 'human edit'


def test_crash_after_file_write_can_resume_without_overwriting_new_work(recovery, monkeypatch):
    factory, root, wid, cid, before, after = recovery
    with factory() as db:
        checked, _ = restore.preview(db, 'alice', 'space', 'repo', wid, before, after, ['file.txt', 'new.txt'])
        operation = restore.start(db, 'alice', 'space', 'repo', wid, cid, before, after, ['file.txt', 'new.txt'], checked['fingerprint'], 'crash')
    original = restore.apply_one
    def crash(*args, **kwargs):
        original(*args, **kwargs)
        raise OSError('synthetic process termination before journal commit')
    monkeypatch.setattr(restore, 'apply_one', crash)
    with pytest.raises(WorktreeConflict, match='requires_recheck'):
        restore.run(factory, 'alice', 'space', 'repo', operation['id'])
    assert (root/'file.txt').read_text() == 'baseline'
    with factory() as db:
        assert db.scalar(select(operations.c.state)) == 'blocked'
        assert db.scalar(select(write_locks.c.operation_id)) == operation['id']
    monkeypatch.setattr(restore, 'apply_one', original)
    assert restore.run(factory, 'alice', 'space', 'repo', operation['id'])['state'] == 'completed'


def test_completed_step_does_not_overwrite_later_edit(recovery, monkeypatch):
    factory, root, wid, cid, before, after = recovery
    with factory() as db:
        checked, _ = restore.preview(db, 'alice', 'space', 'repo', wid, before, after, ['file.txt', 'new.txt'])
        operation = restore.start(db, 'alice', 'space', 'repo', wid, cid, before, after, ['file.txt', 'new.txt'], checked['fingerprint'], 'partial')
    original = restore.apply_one
    def fail_second(root, path, **kwargs):
        if path == 'new.txt':
            raise OSError('synthetic failure')
        return original(root, path, **kwargs)
    monkeypatch.setattr(restore, 'apply_one', fail_second)
    with pytest.raises(WorktreeConflict):
        restore.run(factory, 'alice', 'space', 'repo', operation['id'])
    (root/'file.txt').write_text('later human edit')
    monkeypatch.setattr(restore, 'apply_one', original)
    assert restore.run(factory, 'alice', 'space', 'repo', operation['id'])['state'] == 'completed'
    assert (root/'file.txt').read_text() == 'later human edit'


def test_recovery_directory_preserves_current_tree_and_does_not_claim_development(recovery, monkeypatch):
    from app.moonbox_rollout import recovery_tree
    from app.moonbox_core.schema import claims
    import json
    factory, root, wid, cid, before, after = recovery
    managed = root.parent/'recovery-managed'; managed.mkdir()
    monkeypatch.setattr(recovery_tree, 'repository_binding', lambda *_: {'workspace_root': str(managed)})
    with factory.begin() as db:
        db.execute(update(points).where(points.c.id == before).values(scope_json=json.dumps([''])))
    with factory() as db:
        result = recovery_tree.create(db, 'alice', 'space', 'repo', wid, before, 'recover-tree')
        recovered = workspaces.get(db, 'space', 'repo', result['id'])
        assert result['purpose'] == 'recovery'
        assert db.scalar(select(claims.c.workspace_id)) is None
    from pathlib import Path
    assert (Path(recovered['root_locator'])/'file.txt').read_text() == 'baseline'
    assert (root/'file.txt').read_text() == 'agent result'
    with factory() as db:
        assert recovery_tree.create(db, 'alice', 'space', 'repo', wid, before, 'recover-tree')['id'] == result['id']
        with pytest.raises(WorktreeConflict, match='request_conflict|scope_unknown'):
            recovery_tree.create(db, 'alice', 'space', 'repo', wid, after, 'recover-tree')


def test_history_deletion_keeps_shared_reference_and_point_content(recovery, chat):
    import json
    from app.chat import content_store, result_reader
    from app.chat.content_schema import entries as snapshot_entries
    from app.chat.schema import diffs
    client, _ = chat
    factory, root, wid, cid, before, after = recovery
    second = create(client)
    with factory.begin() as db:
        db.execute(insert(session_bindings).values(conversation_id=second, workspace_id=wid))
        tid = chat_service.identity()
        db.execute(insert(turns).values(**tid, conversation_id=second, client_request_id='second', status='completed', prompt='synthetic'))
    snap = snapshot_store.capture(factory, second, tid['id'], root, 'before', policy_roots=('',))
    with factory.begin() as db:
        key = hashlib.sha256(b'file.txt').hexdigest()
        old_oid = db.scalar(select(entries.c.object_id).where(entries.c.point_id == after, entries.c.path_key == key))
        new_oid = db.scalar(select(snapshot_entries.c.object_id).where(snapshot_entries.c.version_id == snap['version_id'], snapshot_entries.c.path_key == key))
        assert old_oid == new_oid
        db.execute(insert(diffs).values(**chat_service.identity(), turn_id=tid['id'], before_hash=snap['hash'], after_hash=snap['hash'],
            payload=json.dumps({'format_version':2,'before_version':snap['version_id'],'after_version':snap['version_id'],'initial_version':snap['version_id']})))
        content_store.purge_conversation(db, cid)
        db.execute(update(conversations).where(conversations.c.id == cid).values(deleted_at=chat_service.now()))
    with factory() as db:
        assert result_reader.content(db, 'alice', tid['id'], key, 'after')['text'] == 'agent result'
        assert b''.join(content_store.blocks(db, old_oid)) == b'agent result'
        assert restore._point(db, wid, after)['state'] == 'complete'


def test_rotation_releases_old_snapshot_manifests_but_keeps_history(recovery):
    from app.chat.content_schema import versions, entries as snapshot_entries
    from app.chat.service import ChatError
    factory, root, wid, cid, before, after = recovery
    with factory() as db:
        tid = db.scalar(select(turns.c.id).where(turns.c.conversation_id == cid))
        initial_version = db.scalar(select(points.c.version_id).where(points.c.id == before))
    for index in range(12):
        (root/'file.txt').write_text('change '+str(index))
        value = snapshot_store.capture(factory, cid, tid, root, 'after', policy_roots=('',))
        with factory.begin() as db:
            catalog.publish(db, wid, value['version_id'], policy_version='policy', head_commit='h', changed=True)
            catalog.rotate(db, wid)
    with factory() as db:
        assert db.scalar(select(versions.c.status).where(versions.c.id == initial_version)) == 'expired'
        assert db.scalar(select(snapshot_entries.c.path_key).where(snapshot_entries.c.version_id == initial_version).limit(1)) is None
        assert db.scalar(select(turns.c.id).where(turns.c.id == tid)) == tid
        with pytest.raises(ChatError) as failure:
            snapshot_store.diff_page(db, initial_version, initial_version)
        assert failure.value.status == 410
