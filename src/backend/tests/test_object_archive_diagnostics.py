"""Public query contracts use the actual router, database and project reader."""
import json
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import insert, select, update, text
from test_chat import chat
from test_governance_scope import fixture_tree, bind
from app.governance.replacement_schema import archive_operations
from app.governance import scope
from app.chat.service import identity
from app.governance.archive_diagnostics import ArchiveDiagnosticError, safe_diagnostics


@pytest.fixture
def archive_view(chat, tmp_path, monkeypatch):
    client, factory = chat
    root = fixture_tree(tmp_path/'repo'); bind(monkeypatch, root)
    folder = root/'openspec/changes/fix-sample'; folder.mkdir(parents=True)
    (folder/'proposal.md').write_text('# 示例\n')
    (folder/'trace.md').write_text('---\nstatus: applied\n---\n')
    params = {'space_id': 'space', 'repository_id': 'repo', 'object_id': 'fix-sample'}
    return client, factory, root, params


def add_operation(factory, *, stage='synced', actor='alice'):
    with factory() as db:
        p = scope.authorize(db, 'alice', 'space', 'repo')
        db.execute(insert(archive_operations).values(**(identity() | {'id': 'original'}),
            scope_key=p.key, binding_revision=p.binding_revision, change_id='fix-sample', actor_id=actor,
            stage=stage, manifest='{}', fence=1, lease_until=(datetime.now(timezone.utc)-timedelta(minutes=1)).isoformat(), revision=1))
        db.commit()


def test_no_operation_is_readonly(archive_view):
    client, factory, root, params = archive_view
    before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
    response = client.get('/api/v1/chat/archive-operations', params=params)
    assert response.status_code == 200, response.text
    assert response.json()['data']['operations'] == []
    assert response.json()['data']['summary'] == 'not_started'
    with factory() as db: assert not db.execute(select(archive_operations)).first()
    assert before == {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}


def test_completed_history_does_not_hide_current_failure(archive_view):
    client, factory, _, params = archive_view; add_operation(factory, stage='completed')
    response = client.get('/api/v1/chat/archive-operations', params=params)
    assert response.status_code == 200, response.text
    data = response.json()['data']; op = data['operations'][0]
    assert op['stage'] == 'completed' and op['verification']['status'] == 'blocked'
    assert op['allowed_actions'] == ['refresh'] and data['summary'] != 'completed'
    assert 'manifest' not in op and 'fence' not in op
    denied = client.post('/api/v1/chat/archive-operations/resume', json=params | {'operation_id': 'original', 'confirmed': True})
    assert denied.status_code == 409
    with factory() as db: assert db.scalar(select(archive_operations.c.stage)) == 'completed'


def test_resume_requires_original_actor_and_explicit_confirmation(archive_view):
    client, factory, _, params = archive_view; add_operation(factory, actor='bob')
    response = client.get('/api/v1/chat/archive-operations', params=params)
    assert response.status_code == 200, response.text
    op = response.json()['data']['operations'][0]
    assert op['allowed_actions'] == ['refresh']
    for oid, confirmed in [('other', True), ('original', True), ('original', False)]:
        response = client.post('/api/v1/chat/archive-operations/resume', json=params | {'operation_id': oid, 'confirmed': confirmed})
        assert response.status_code == 409
    with factory() as db: assert db.scalar(select(archive_operations.c.revision)) == 1


def test_query_rejects_cross_project(archive_view):
    client, _, _, params = archive_view
    assert client.get('/api/v1/chat/archive-operations', params=params | {'space_id': 'other'}).status_code == 403


def test_error_diagnostics_survive_public_serializer(chat, monkeypatch):
    from app.governance import archive_dispatch
    def fail(*a, **k):
        raise ArchiveDiagnosticError('archive_finalization_blocked', {'operation_id': 'original',
            'findings': [{'file': 'issues/requirements/archive/REQ-0001-test/trace.md', 'kind': 'current-state', 'line': 9},
                         {'file': '/private/secret', 'kind': 'current-state'}]})
    monkeypatch.setattr(archive_dispatch, 'execute_object', fail)
    client, _ = chat
    r = client.post('/api/v1/chat/archive-commands', json={'space_id':'space','repository_id':'repo','object_id':'fix-sample','confirmed':True})
    assert r.status_code == 409
    data = r.json()['data']
    assert data['reason'] == 'archive_finalization_blocked' and data['operation_id'] == 'original'
    assert len(data['findings']) == 1 and '/private' not in r.text


def test_safe_diagnostics_never_passes_arbitrary_prose():
    result = safe_diagnostics({'operation_id': 'Bearer secret', 'findings': [
        {'file':'issues/../secret', 'kind':'broken-link'}, {'file':'/' + '/'.join(('Users', 'private')), 'kind':'broken-link'},
        {'file':'issues/ok.md','kind':'broken-link','message':'Bearer secret','line': True}]})
    assert 'secret' not in json.dumps(result)
    assert result['findings'][0]['line'] == 0


def test_revision_change_makes_query_stale(archive_view, monkeypatch):
    from app.governance import archive_query
    client, factory, _, params = archive_view; add_operation(factory, stage='completed')
    original = archive_query.build_report
    def change_version(*args):
        result = original(*args)
        with factory() as db:
            db.execute(update(archive_operations).values(revision=2)); db.commit()
        return result
    monkeypatch.setattr(archive_query, 'build_report', change_version)
    data = client.get('/api/v1/chat/archive-operations', params=params).json()['data']
    assert data['summary'] == 'stale'
    assert data['operations'][0]['verification']['status'] == 'stale'
    assert data['operations'][0]['allowed_actions'] == ['refresh']


def test_multiple_changes_keep_missing_and_completed_separate(archive_view):
    client, factory, root, params = archive_view; add_operation(factory, stage='completed')
    issue = root/'issues/requirements/review/REQ-0001-example'; issue.mkdir(parents=True)
    (root/'issues/requirements/_registry.yaml').write_text('entries:\n- id: REQ-0001-example\n  path: issues/requirements/review/REQ-0001-example\n  status: in_sprint\n')
    (issue/'trace.md').write_text('---\nstatus: in_sprint\nopenspec_changes:\n- change_id: fix-sample\n- change_id: fix-second\n---\n')
    second = root/'openspec/changes/fix-second'; second.mkdir()
    (second/'proposal.md').write_text('# 第二项\n')
    r = client.get('/api/v1/chat/archive-operations', params=params | {'object_id': 'REQ-0001-example'})
    assert r.status_code == 200, r.text
    data = r.json()['data']
    assert len(data['operations']) == 1 and data['summary'] == 'needs_attention'
    assert data['not_started_targets'] == ['fix-second']


def test_ambiguous_controlled_identity_never_picks_latest(archive_view):
    from app.governance.replacement_schema import proposals
    client, factory, _, params = archive_view
    with factory() as db:
        p = scope.authorize(db, 'alice', 'space', 'repo')
        for i in range(2):
            db.execute(insert(proposals).values(**identity(),scope_key=p.key,space_id='space',repository_id='repo',
                binding_revision=p.binding_revision,change_id='fix-sample',digest=str(i)*64,body='{}',prepared_by='alice',revision=1,state='claimed'))
        db.commit()
    r = client.get('/api/v1/chat/archive-operations', params=params)
    assert r.status_code == 409 and r.json()['data']['reason'] == 'replacement_candidate_ambiguous'


def test_unknown_executor_occupancy_never_enables_resume(archive_view, monkeypatch):
    from app.governance import archive_query
    client, factory, _, params = archive_view; add_operation(factory)
    monkeypatch.setattr(archive_query, 'executor_idle', lambda project: False)
    data = client.get('/api/v1/chat/archive-operations', params=params).json()['data']
    assert data['operations'][0]['allowed_actions'] == ['refresh']


def test_safe_findings_wrong_shape_is_ignored():
    assert safe_diagnostics({'findings': {'secret': 'value'}}) == {}


def test_controlled_query_uses_exact_proposal_operation(archive_view):
    from app.governance.replacement_schema import proposals, commits
    client, factory, _, params = archive_view
    with factory() as db:
        p = scope.authorize(db, 'alice', 'space', 'repo')
        db.execute(insert(proposals).values(**(identity() | {'id':'proposal'}),scope_key=p.key,space_id='space',repository_id='repo',
            binding_revision=p.binding_revision,change_id='fix-sample',digest='a'*64,body='{}',prepared_by='alice',revision=1,state='claimed',operation_id='controlled-original'))
        db.execute(insert(commits).values(**(identity() | {'id':'controlled-original'}),scope_key=p.key,proposal_id='proposal',actor_id='alice',
            stage='move_verified',fence=1,lease_until='2026-01-01',input_hash='i',expected_hash='e',revision=2));db.commit()
    response=client.get('/api/v1/chat/archive-operations',params=params)
    assert response.status_code==200,response.text
    op=response.json()['data']['operations'][0]
    assert (op['operation_id'],op['operation_kind'],op['revision'])==('controlled-original','controlled',2)
    with factory() as db:
        db.execute(update(proposals).values(operation_id='different'));db.commit()
    assert client.get('/api/v1/chat/archive-operations',params=params).status_code==409


def test_sprint_query_keeps_own_and_child_operations_separate(archive_view):
    client,factory,root,params=archive_view;add_operation(factory,stage='completed')
    folder=root/'iterations/change/sprint-001';folder.mkdir(parents=True)
    (folder/'sprint.yaml').write_text('sprint_id: sprint-001\nstatus: active\nchanges: [fix-sample]\n')
    with factory() as db:
        p=scope.authorize(db,'alice','space','repo')
        db.execute(insert(archive_operations).values(**(identity() | {'id':'sprint-original'}),scope_key=p.key,binding_revision=p.binding_revision,
            change_id='sprint-001',actor_id='alice',stage='claimed',manifest='{}',fence=1,lease_until='2026-01-01',revision=1));db.commit()
    response=client.get('/api/v1/chat/archive-operations',params=params | {'object_id':'sprint-001'})
    assert response.status_code==200,response.text
    rows=response.json()['data']['operations']
    assert [(r['target_id'],r['operation_kind']) for r in rows]==[('sprint-001','sprint'),('fix-sample','ordinary')]
    assert response.json()['data']['summary']=='needs_attention'
