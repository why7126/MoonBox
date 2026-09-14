"""BUG-0016: 内容失效、安全错误分类和读写缓存隔离。"""
import os
import pytest
from app.chat.service import ChatError
from app.governance import snapshot as module
from test_governance_scope import fixture_tree, bind
from test_chat import chat


def test_stable_invalid_is_classified_once_and_recovers(tmp_path, monkeypatch):
    root = fixture_tree(tmp_path / 'repo')
    registry = root / 'issues/requirements/_registry.yaml'
    registry.write_text('entries: [private-invalid-body')
    original = module.read_once
    calls = []
    def read(path):
        calls.append(path)
        return original(path)
    monkeypatch.setattr(module, 'read_once', read)
    with pytest.raises(ChatError) as failure:
        module.stable(root)
    assert failure.value.kind == 'source_invalid'
    assert len(calls) == 2
    assert 'private-invalid-body' not in failure.value.message
    registry.write_text('entries: []\n')
    assert module.stable(root).revision


def test_cache_checks_actual_bytes_and_add_delete_rename(tmp_path):
    root = fixture_tree(tmp_path / 'repo')
    doc = root / 'issues/notes.md'
    doc.write_text('first')
    first = module.stable(root)
    with module.cached_materialize(first, ('project', 'binding')) as tree:
        initial = tree
        assert (tree / 'issues/notes.md').read_text() == 'first'
    stamp = doc.stat()
    doc.write_text('other')
    os.utime(doc, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    second = module.stable(root)
    assert second.revision != first.revision
    with module.cached_materialize(second, ('project', 'binding')) as tree:
        assert tree != initial
        assert (tree / 'issues/notes.md').read_text() == 'other'
    doc.rename(root / 'issues/renamed.md')
    renamed = module.stable(root)
    assert renamed.revision != second.revision
    (root / 'issues/renamed.md').unlink()
    assert module.stable(root).revision not in [first.revision, second.revision, renamed.revision]


def test_cache_namespace_bounds_and_writer_isolation(tmp_path, monkeypatch):
    snapshot = module.stable(fixture_tree(tmp_path / 'repo'))
    monkeypatch.setattr(module, 'CACHE_ENTRIES', 2)
    with module.cached_materialize(snapshot, ('one', 'binding')) as one:
        with module.materialize(snapshot) as writer:
            (writer / 'issues/requirements/_registry.yaml').write_text('bad')
        assert (one / 'issues/requirements/_registry.yaml').read_text() == 'entries: []\n'
    with module.cached_materialize(snapshot, ('one', 'binding')) as reused:
        assert reused == one
    with module.cached_materialize(snapshot, ('one', 'new-binding')) as other:
        assert other != one
    with module.cached_materialize(snapshot, ('two', 'binding')) as other:
        assert other != one
    assert not one.exists()
    assert len(module._trees) <= 2


def test_unsafe_tree_and_changing_tree_have_distinct_safe_errors(tmp_path, monkeypatch):
    root = fixture_tree(tmp_path / 'repo')
    (root / 'issues/link.md').symlink_to('/unavailable-private-source')
    with pytest.raises(ChatError) as failure:
        module.stable(root)
    assert failure.value.kind == 'source_unavailable'
    sequence = iter([{'a': b'1'}, {'a': b'2'}] * 3)
    monkeypatch.setattr(module, 'read_once', lambda _: next(sequence))
    with pytest.raises(ChatError) as failure:
        module.stable(root)
    assert failure.value.kind == 'source_changing'


def test_error_envelope_request_correlation_and_no_source_leak(chat, tmp_path, monkeypatch):
    client, _ = chat
    root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    (root / 'issues/requirements/_registry.yaml').write_text('entries: [private-secret')
    response = client.get('/api/v1/requirement-center/context', params={'space_id':'space','repository_id':'repo'})
    assert response.status_code == 503
    body = response.json()
    assert body['code'] == 2603
    assert body['data'] == {'kind':'source_invalid','request_id':response.headers['x-request-id']}
    assert 'private-secret' not in response.text and str(root) not in response.text
    assert response.headers['cache-control'] == 'no-store'


def test_existing_candidate_guard_rejects_invalid_registry_without_mutation():
    from copy import deepcopy
    from test_governance_candidates import contents, OID, BASE
    from app.governance.candidates import validate
    before, candidate = contents()
    unchanged = deepcopy(before)
    candidate['issues/requirements/_registry.yaml'] = b'entries: [invalid'
    with pytest.raises(ChatError) as failure:
        validate(before, candidate, OID, BASE)
    assert failure.value.code == 2604
    assert before == unchanged


@pytest.mark.parametrize('limit,value', [('LIMIT_FILE', 4), ('LIMIT_TOTAL', 4), ('LIMIT_COUNT', 1)])
def test_warm_validation_never_bypasses_snapshot_limits(tmp_path, monkeypatch, limit, value):
    root = fixture_tree(tmp_path / 'repo')
    module.stable(root)
    monkeypatch.setattr(module, limit, value)
    with pytest.raises(ChatError) as failure:
        module.stable(root)
    assert failure.value.kind == 'source_unavailable'


def test_binding_change_still_rejected_with_warm_tree(chat, tmp_path, monkeypatch):
    from dataclasses import replace
    from app.governance import scope, reader
    _, factory = chat
    root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    snap = module.stable(root)
    with factory() as db:
        initial = scope.authorize(db, 'alice', 'space', 'repo')
        with module.cached_materialize(snap, (str(root), initial.binding_revision)):
            pass
        monkeypatch.setattr(scope, 'authorize', lambda *args: replace(initial, binding_revision='changed'))
        with pytest.raises(ChatError) as failure:
            reader.ProjectReader(db, 'alice', initial).snapshot()
        assert failure.value.code == 2606
