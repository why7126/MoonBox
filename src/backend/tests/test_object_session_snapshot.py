"""Preparation uses fresh complete bytes while retaining reader fences."""
from dataclasses import replace
import os
import pytest
from app.chat.service import ChatError
from app.governance import preparation, read_snapshot, snapshot, scope, writer
from test_chat import chat
from test_governance_scope import bind, fixture_tree
from test_governance_writer import writing
from test_direct_completion import direct_scene


@pytest.fixture(autouse=True)
def clear_cache():
    read_snapshot.clear()
    yield
    read_snapshot.clear()


def test_same_root_reads_fresh_bytes_without_duplicate_replica(chat, tmp_path, monkeypatch):
    _, factory = chat
    root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    doc = root / 'issues/note.md'; doc.write_text('first')
    calls = []
    original = snapshot.read_once
    def read(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)
    monkeypatch.setattr(snapshot, 'read_once', read)
    with factory() as db:
        project = scope.authorize(db, 'alice', 'space', 'repo', write=True)
        _, before = preparation._object_session_snapshot(db, 'alice', project)
        assert len(calls) == 2
        calls.clear()
        _, warm = preparation._object_session_snapshot(db, 'alice', project)
        assert warm.revision == before.revision and len(calls) == 1
        stamp = doc.stat(); doc.write_text('other')
        os.utime(doc, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        _, changed = preparation._object_session_snapshot(db, 'alice', project)
        assert changed.files['issues/note.md'] == b'other'
        assert changed.revision != before.revision


def test_projection_mismatch_and_missing_source_fail_closed(chat, tmp_path, monkeypatch):
    _, factory = chat
    root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    source = fixture_tree(tmp_path / 'source')
    with factory() as db:
        project = scope.authorize(db, 'alice', 'space', 'repo', write=True)
        project = replace(project, source_root=source)
        preparation._object_session_snapshot(db, 'alice', project)
        (source / 'issues/extra.md').write_text('changed')
        with pytest.raises(ChatError) as error:
            preparation._object_session_snapshot(db, 'alice', project)
        assert error.value.kind == 'workspace_fact_source_stale'
        with pytest.raises(ChatError):
            preparation._object_session_snapshot(db, 'alice', replace(project, source_root_unavailable=True))


def test_reader_epoch_fence_surrounds_source_checks(chat, tmp_path, monkeypatch):
    _, factory = chat
    root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    with factory() as db:
        project = scope.authorize(db, 'alice', 'space', 'repo', write=True)
        epochs = iter([1, 2]); monkeypatch.setattr(writer, 'epoch', lambda *_: next(epochs))
        with pytest.raises(ChatError) as error:
            preparation._object_session_snapshot(db, 'alice', project)
        assert error.value.code == 2603


def test_reader_reauthorizes_binding_after_load(chat, tmp_path, monkeypatch):
    _, factory = chat
    root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    with factory() as db:
        project = scope.authorize(db, 'alice', 'space', 'repo', write=True)
        monkeypatch.setattr(scope, 'authorize', lambda *_args, **_kwargs: replace(project, binding_revision='changed'))
        with pytest.raises(ChatError) as error:
            preparation._object_session_snapshot(db, 'alice', project)
        assert error.value.code == 2606


def test_preflight_observes_mutation_during_reconcile(chat, tmp_path, monkeypatch):
    from app.governance import execution_context
    from test_governance_candidates import contents, OID
    from app.chat.schema import conversations
    from sqlalchemy import select, func
    _, factory = chat
    root = tmp_path / 'repo'; root.mkdir(); bind(monkeypatch, root)
    captured, draft = contents()
    def write(files):
        for name, body in files.items():
            path = root / name; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
    write(captured)
    def reconcile(*args, **kwargs):
        write(draft)
    monkeypatch.setattr(execution_context, 'reconcile', reconcile)
    with factory() as db:
        with pytest.raises(ChatError) as error:
            preparation.prepare_object_session(db, 'alice', 'space', 'repo', OID, 'req-generate')
        assert error.value.code == 2604
        assert db.scalar(select(func.count()).select_from(conversations)) == 0


def test_projection_catches_up_with_bounded_fresh_read(chat, tmp_path, monkeypatch):
    _, factory = chat
    root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    source = fixture_tree(tmp_path / 'source')
    (source / 'issues/new.md').write_text('new')
    original = read_snapshot.stable_read
    reads = []
    def read(path, *args, **kwargs):
        result = original(path, *args, **kwargs)
        reads.append(path)
        if path == source:
            (root / 'issues/new.md').write_text('new')
        return result
    monkeypatch.setattr(read_snapshot, 'stable_read', read)
    with factory() as db:
        project = replace(scope.authorize(db, 'alice', 'space', 'repo', write=True), source_root=source)
        _, result = preparation._object_session_snapshot(db, 'alice', project)
        assert result.files['issues/new.md'] == b'new'
        assert reads == [root, source, root]


def test_permission_revoked_during_load_fails_closed(chat, tmp_path, monkeypatch):
    _, factory = chat
    root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    with factory() as db:
        project = scope.authorize(db, 'alice', 'space', 'repo', write=True)
        def denied(*args, **kwargs):
            raise ChatError(2601, 'revoked', 403)
        monkeypatch.setattr(scope, 'authorize', denied)
        with pytest.raises(ChatError) as error:
            preparation._object_session_snapshot(db, 'alice', project)
        assert error.value.code == 2601


def test_parallel_replica_reads_retain_mismatch_rejection(chat, tmp_path, monkeypatch):
    from threading import Barrier, Lock
    _, factory = chat
    root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    source = fixture_tree(tmp_path / 'source')
    (source / 'issues/new.md').write_text('new')
    original = read_snapshot.stable_read
    barrier = Barrier(2); lock = Lock(); calls = []
    def read(path, *args, **kwargs):
        with lock:
            calls.append(path); initial = len(calls) <= 2
        if initial:
            barrier.wait(timeout=5)
        return original(path, *args, **kwargs)
    monkeypatch.setattr(read_snapshot, 'read_workers', lambda **_:  2)
    monkeypatch.setattr(read_snapshot, 'stable_read', read)
    with factory() as db:
        project = replace(scope.authorize(db, 'alice', 'space', 'repo', write=True), source_root=source)
        with pytest.raises(ChatError) as error:
            preparation._object_session_snapshot(db, 'alice', project)
        assert error.value.kind == 'workspace_fact_source_stale'


def test_reconcile_fresh_loader_keeps_transaction_fence(direct_scene):
    from sqlalchemy import update
    from app.governance import execution_context, execution_guard as guards
    from test_direct_completion import OID
    factory, project, tid, _, version = direct_scene
    reads = []
    def load():
        with factory() as other:
            other.execute(update(guards.execution_guards).where(
                guards.execution_guards.c.operation_id == tid).values(version=version+1))
            other.commit()
        reads.append(True)
        return read_snapshot.stable_read(project.root, project.binding_revision)
    with factory() as db:
        execution_context.reconcile(db, 'alice', project, snapshot_loader=load)
        row = guards.read(db, project.key, OID)
        assert row['version'] == version+1
        assert row['state'] == 'needs_review'
    assert reads


def test_different_names_for_same_directory_read_bytes_once(chat, tmp_path, monkeypatch):
    _, factory = chat
    root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    alias = root / '..' / root.name
    assert alias != root and os.path.samefile(root, alias)
    original = snapshot.read_once
    calls = []
    def read(*args, **kwargs):
        calls.append(kwargs.get('root_fd'))
        return original(*args, **kwargs)
    monkeypatch.setattr(snapshot, 'read_once', read)
    with factory() as db:
        project = replace(scope.authorize(db, 'alice', 'space', 'repo', write=True), source_root=alias)
        preparation._object_session_snapshot(db, 'alice', project)
        calls.clear()
        preparation._object_session_snapshot(db, 'alice', project)
        assert len(calls) == 1 and calls[0] is not None
        with pytest.raises(OSError):
            os.fstat(calls[0])  # descriptors do not outlive this request stage
        note = root / 'issues/note.md'; note.write_text('first')
        preparation._object_session_snapshot(db, 'alice', project)
        stamp = note.stat(); note.write_text('other')
        os.utime(note, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        _, result = preparation._object_session_snapshot(db, 'alice', project)
        assert result.files['issues/note.md'] == b'other'


@pytest.mark.parametrize('replacement', ['directory', 'symlink'])
def test_alias_root_replaced_during_read_fails_closed(tmp_path, monkeypatch, replacement):
    root = fixture_tree(tmp_path / 'repo')
    alias = root / '..' / root.name
    original = read_snapshot.stable_read
    def read(*args, **kwargs):
        result = original(*args, **kwargs)
        root.rename(tmp_path / 'original')
        if replacement == 'directory':
            fixture_tree(root)
        else:
            root.symlink_to(tmp_path / 'original', target_is_directory=True)
        return result
    monkeypatch.setattr(read_snapshot, 'stable_read', read)
    with pytest.raises(ChatError) as error:
        read_snapshot.stable_alias_read(root, alias, 'binding')
    assert error.value.kind == 'source_changing'


def test_object_session_cold_parallel_reads_still_verify_two_passes_and_retry(tmp_path, monkeypatch):
    root = fixture_tree(tmp_path / 'repo')
    doc = root / 'issues/note.md'; doc.write_text('before')
    original = snapshot.read_once
    calls = []
    monkeypatch.setattr(read_snapshot, 'read_workers', lambda **_:  2)
    def changing_read(*args, **kwargs):
        calls.append(kwargs.get('workers', 1))
        result = original(*args, **kwargs)
        if len(calls) == 1:
            stamp = doc.stat(); doc.write_text('after!')
            os.utime(doc, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        return result
    monkeypatch.setattr(snapshot, 'read_once', changing_read)
    result = read_snapshot.stable_read(root, 'binding', parallel_cold=True)
    assert calls == [2, 2, 1, 1]
    assert result.files['issues/note.md'] == b'after!'


@pytest.mark.parametrize('quota,cpus,expected', [('max 100000',10,4),('800000 100000',10,4),('600000 100000',10,2),('200000 100000',10,1),('max 100000',4,2),('bad',10,1)])
def test_cold_read_parallelism_keeps_cpu_headroom(monkeypatch, quota, cpus, expected):
    monkeypatch.setattr(os, 'sched_getaffinity', lambda _: set(range(cpus)), raising=False)
    monkeypatch.setattr(read_snapshot.Path, 'read_text', lambda _: quota)
    assert read_snapshot.read_workers(cold=True) == expected
