"""Summary is a distinct read scope, never a completion proof."""
import os

import pytest
from sqlalchemy import insert

from app.chat.service import ChatError
from app.chat.schema import object_access
from app.governance import read_snapshot, snapshot
from test_chat import chat
from test_governance_scope import fixture_tree, bind


@pytest.fixture(autouse=True)
def directory_fixture(monkeypatch):
    # The Chat fixture has permission tables but no product-directory tables.
    from app.services import requirement_center
    monkeypatch.setattr(requirement_center, '_load_workspaces', lambda *args: [])


def tree(root):
    fixture_tree(root)
    issue = root / 'issues/bugs/review/BUG-0099-sample'
    issue.mkdir(parents=True)
    (root / 'issues/bugs/_registry.yaml').write_text(
        'entries:\n- id: BUG-0099-sample\n  path: issues/bugs/review/BUG-0099-sample\n'
        '  title: 示例\n  status: applied\n  severity: high\n')
    (issue / 'trace.md').write_text('---\nstatus: applied\n---\n')
    (issue / 'bug.md').write_text('# 示例\n')
    (issue / 'acceptance.md').write_text('# 验收\n')
    evidence = root / 'openspec/changes/sample/evidence'
    evidence.mkdir(parents=True)
    (evidence / 'large.md').write_text('irrelevant evidence')
    (root / 'docs').mkdir()
    (root / 'docs/guide.md').write_text('guide')
    return root


def test_profile_isolation_and_fresh_summary_bytes(tmp_path):
    root = tree(tmp_path / 'repo')
    read_snapshot.clear()
    full = read_snapshot.stable_read(root, 'binding')
    light = read_snapshot.stable_read(root, 'binding', profile='summary')
    assert 'docs/guide.md' in full.files and 'docs/guide.md' not in light.files
    assert 'openspec/changes/sample/evidence/large.md' not in light.files
    assert full.revision != light.revision
    path = root / 'issues/bugs/review/BUG-0099-sample/bug.md'
    before = path.stat()
    path.write_text('# 变化\n')
    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
    changed = read_snapshot.stable_read(root, 'binding', profile='summary')
    assert changed.revision != light.revision
    assert read_snapshot.stable_read(root, 'binding').files['docs/guide.md'] == b'guide'
    path.unlink()
    path.symlink_to(root / 'docs/guide.md')
    with pytest.raises(ChatError):
        read_snapshot.stable_read(root, 'binding', profile='summary')


def test_cold_summary_uses_bounded_parallel_safe_reads(tmp_path, monkeypatch):
    root = tree(tmp_path / 'repo')
    read_snapshot.clear()
    original = snapshot.read_once
    calls = []
    def observed(*args, **kwargs):
        calls.append(kwargs.get('workers', 1))
        return original(*args, **kwargs)
    monkeypatch.setattr(read_snapshot, 'read_workers', lambda: 2)
    monkeypatch.setattr(snapshot, 'read_once', observed)
    result = read_snapshot.stable_read(root, 'cold', profile='summary')
    assert calls == [2, 2]
    assert result.files == original(root, profile='summary', workers=1)


def test_equal_payload_reuse_still_reads_every_byte_and_rejects_links(tmp_path, monkeypatch):
    root = tree(tmp_path / 'repo')
    identities = {}
    first = snapshot.read_once(root, profile='summary', identities=identities)
    candidates = {name: (identities[name], body) for name, body in first.items()}
    reads = []
    original = snapshot.read_body
    def observed(fd, size):
        body = original(fd, size)
        reads.append(len(body))
        return body
    monkeypatch.setattr(snapshot, 'read_body', observed)
    second = snapshot.read_once(root, profile='summary', workers=2, byte_candidates=candidates)
    assert sum(reads) == sum(map(len, first.values()))
    assert len(reads) == len(first)
    assert all(second[name] is body for name, body in first.items())
    name = 'issues/bugs/review/BUG-0099-sample/bug.md'
    path = root / name
    before = path.stat()
    path.write_text('# 变化\n')
    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
    changed = snapshot.read_once(root, profile='summary', byte_candidates=candidates)
    assert changed[name] == '# 变化\n'.encode() and changed[name] != first[name]
    path.unlink()
    path.symlink_to(root / 'docs/guide.md')
    with pytest.raises((ValueError, OSError)):
        snapshot.read_once(root, profile='summary', byte_candidates=candidates)


def test_summary_defers_proofs_but_keeps_permissions(chat, tmp_path, monkeypatch):
    from app.governance import execution_context, archive_admission, completion_handoff
    from app.governance.change_index import ChangeIndex
    client, factory = chat
    bind(monkeypatch, tree(tmp_path / 'repo'))
    builds = []
    original_init = ChangeIndex.__init__
    def counted(self, *args, **kwargs):
        builds.append(1)
        original_init(self, *args, **kwargs)
    monkeypatch.setattr(ChangeIndex, '__init__', counted)
    def forbidden(*args, **kwargs):
        raise AssertionError('summary must not invoke deep proof checks')
    monkeypatch.setattr(execution_context, 'reconcile', forbidden)
    monkeypatch.setattr(execution_context, 'reconcile_external_batch', forbidden)
    monkeypatch.setattr(archive_admission, 'issue_acceptance', forbidden)
    monkeypatch.setattr(completion_handoff, 'status', forbidden)
    params = {'space_id': 'space', 'repository_id': 'repo', 'view': 'summary'}
    response = client.get('/api/v1/requirement-center/context', params=params)
    assert response.status_code == 200, response.text
    card = next(c for c in response.json()['data']['issues'] if c['id'] == 'BUG-0099')
    assert card['checks_deferred'] is True
    assert card['manual_acceptance_progress'] is None
    assert card['acceptance_blocked_reason'] == '验收待检查'
    assert card['action']['disabled_reason'] == '验收待检查'
    with factory() as db:
        db.execute(insert(object_access).values(space_id='space', repository_id='repo',
            object_id='BUG-0099-sample', user_id='bob', can_read=1))
        db.commit()
    response = client.get('/api/v1/requirement-center/context', params=params)
    assert response.status_code == 200
    assert not any(c['id'] == 'BUG-0099' for c in response.json()['data']['issues'])
    assert len(builds) == 1  # Pure relationships reused; revoked ACL was not.
    params['object_id'] = 'BUG-0099'
    assert client.get('/api/v1/requirement-center/context', params=params).status_code == 403


def test_selected_object_cannot_return_other_cards(chat, tmp_path, monkeypatch):
    client, _ = chat
    bind(monkeypatch, tree(tmp_path / 'repo'))
    response = client.get('/api/v1/requirement-center/context', params={
        'space_id': 'space', 'repository_id': 'repo', 'object_id': 'BUG-0099'})
    assert response.status_code == 200, response.text
    assert [c['id'] for c in response.json()['data']['issues']] == ['BUG-0099']
    assert response.json()['data']['issues'][0]['checks_deferred'] is False


def test_summary_execution_link_does_not_lookup_deferred_verification(chat, tmp_path, monkeypatch):
    from sqlalchemy.orm import Session
    from app.governance import execution_context
    from app.governance.recovery_schema import operations
    client, _ = chat
    bind(monkeypatch, tree(tmp_path / 'repo'))
    original_states = execution_context.visible_states
    original_scalar = Session.scalar
    def states(*args, **kwargs):
        result = original_states(*args, **kwargs)
        _, state = result['BUG-0099-sample']
        result['BUG-0099-sample'] = ({'operation_id': 'old-turn'}, {
            **state, 'can_send': True, 'view_conversation_id': 'old-chat'})
        return result
    def scalar(self, statement, *args, **kwargs):
        assert operations.name not in str(statement)
        return original_scalar(self, statement, *args, **kwargs)
    monkeypatch.setattr(execution_context, 'visible_states', states)
    monkeypatch.setattr(Session, 'scalar', scalar)
    response = client.get('/api/v1/requirement-center/context', params={
        'space_id': 'space', 'repository_id': 'repo', 'view': 'summary'})
    assert response.status_code == 200, response.text
    card = next(c for c in response.json()['data']['issues'] if c['id'] == 'BUG-0099')
    assert card['view_turn_id'] == 'old-turn'
    assert card['verification_operation_id'] is None
    assert card['verification_actions'] == []


def test_status_reads_no_files_and_rechecks_access(chat, tmp_path, monkeypatch):
    client, factory = chat
    bind(monkeypatch, tree(tmp_path / 'repo'))
    monkeypatch.setattr(snapshot, 'read_once', lambda *a, **k: pytest.fail('status must not scan files'))
    params = {'space_id': 'space', 'repository_id': 'repo', 'object_ids': ['BUG-0099-sample']}
    response = client.get('/api/v1/requirement-center/status', params=params)
    assert response.status_code == 200, response.text
    assert response.json()['data']['items'][0]['object_id'] == 'BUG-0099-sample'
    with factory() as db:
        db.execute(insert(object_access).values(space_id='space', repository_id='repo',
            object_id='BUG-0099-sample', user_id='bob', can_read=1))
        db.commit()
    assert client.get('/api/v1/requirement-center/status', params=params).status_code == 403
    params['object_ids'] = ['../private']
    assert client.get('/api/v1/requirement-center/status', params=params).status_code == 403


def test_explicit_check_behavior_is_optional_and_correlated(chat, tmp_path, monkeypatch):
    from sqlalchemy import select
    from app.chat.schema import usage_events
    client, factory = chat
    bind(monkeypatch, tree(tmp_path / 'repo'))
    params = {'space_id': 'space', 'repository_id': 'repo', 'object_id': 'BUG-0099'}
    headers = {'X-Chat-Client': 'web', 'X-Behavior-Event-ID': 'check-event', 'X-Behavior-Trace-ID': 'check-chain'}
    response = client.get('/api/v1/requirement-center/context', params=params, headers=headers)
    assert response.status_code == 200
    with factory() as db:
        row = db.execute(select(usage_events).where(usage_events.c.behavior_event_id == 'check-event')).mappings().one()
        assert row['event_name'] == 'requirement_center.acceptance_check'
        assert row['parent_request_id']
        assert row['properties'] == '{"behavior_trace_id": "check-chain"}'
    # Duplicate telemetry cannot turn a successful read into a failure.
    assert client.get('/api/v1/requirement-center/context', params=params, headers=headers).status_code == 200
