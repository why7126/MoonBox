import pytest
import yaml
from app.chat.service import ChatError
from app.governance.change_priority import plan
from app.governance.reader import version
from test_change_visibility import change
from test_governance_scope import fixture_tree

def test_priority_atomic_audit_and_noop(tmp_path):
    root = fixture_tree(tmp_path)
    folder = change(root, 'standalone')
    text = (folder/'trace.md').read_text()
    changes = plan(root, 'standalone', 'P1', version(text), 'actor-test', '2026-10-31 22:00:00')
    assert len(changes) == 1
    body = next(iter(changes.values()))
    data = yaml.safe_load(body.split('---')[1])
    assert data['priority'] == 'P1'
    assert data['priority_history'][-1]['actor_id'] == 'actor-test'
    assert (folder/'trace.md').read_text() == text
    (folder/'trace.md').write_text(body)
    assert plan(root, 'standalone', 'P1', version(body), 'actor-test', '2026-10-31 22:01:00') == {}
    with pytest.raises(ChatError):
        plan(root, 'standalone', 'P2', version(text), 'actor-test', '2026-10-31 22:01:00')

def test_priority_rejects_archive_source_and_invalid(tmp_path):
    root = fixture_tree(tmp_path)
    folder = change(root, 'standalone')
    text = (folder/'trace.md').read_text()
    for value in ['P4', '', '../trace']:
        with pytest.raises(ChatError):
            plan(root, 'standalone', value, version(text), 'actor', 'time')
    target = root/'openspec/archive/2026-10-31-standalone'
    target.parent.mkdir(parents=True, exist_ok=True)
    folder.rename(target)
    with pytest.raises(ChatError):
        plan(root, 'standalone', 'P1', version(text), 'actor', 'time')

from test_governance_writer import writing
from test_chat import chat

def test_async_priority_controller_and_maintenance(writing):
    from app.governance.reader import ProjectReader
    from app.governance.change_priority import enqueue_priority
    from app.governance.writer import process
    factory, project, _, _, permit = writing
    folder = change(project.root, 'standalone')
    previous = (folder/'trace.md').read_text()
    with factory() as db:
        reader = ProjectReader(db, 'alice', project)
        reader.request_id = 'priority-test-request'
        result = enqueue_priority(reader, 'standalone', 'P0', version(previous), 'priority-once')
        assert result['state'] == 'pending'
        assert (folder/'trace.md').read_text() == previous
        assert process(db, result['id'])['state'] == 'applied'
    assert yaml.safe_load((folder/'trace.md').read_text().split('---')[1])['priority'] == 'P0'
    permit.unlink()
    with factory() as db:
        reader = ProjectReader(db, 'alice', project)
        reader.request_id = 'priority-test-request'
        with pytest.raises(ChatError):
            enqueue_priority(reader, 'standalone', 'P1', version((folder/'trace.md').read_text()), 'no-maintenance')

def test_async_source_change_conflicts_before_write(writing):
    from app.governance.reader import ProjectReader
    from app.governance.change_priority import enqueue_priority
    from app.governance.writer import process
    factory, project, _, _, _ = writing
    folder = change(project.root, 'standalone')
    previous = (folder/'trace.md').read_text()
    with factory() as db:
        reader = ProjectReader(db, 'alice', project)
        reader.request_id = 'test-request'
        result = enqueue_priority(reader, 'standalone', 'P1', version(previous), 'race')
        external = previous + '\n外部新内容\n'
        (folder/'trace.md').write_text(external)
        assert process(db, result['id'])['state'] == 'conflict'
    assert (folder/'trace.md').read_text() == external

def test_source_relation_rejects_priority(tmp_path):
    from test_change_visibility import issue
    root = fixture_tree(tmp_path)
    source = issue(root)
    folder = change(root, 'linked', requirement_id=source['id'])
    previous = (folder/'trace.md').read_text()
    with pytest.raises(ChatError):
        plan(root, 'linked', 'P0', version(previous), 'actor', 'time')

def test_projection_states_and_archive_readonly(tmp_path):
    from test_change_visibility import cards
    root = fixture_tree(tmp_path)
    for name, value in [('valid','P3'),('invalid','P9'),('missing',None)]:
        kwargs = {} if value is None else {'priority':value}
        change(root, name, **kwargs)
    rows = {row.id:row for row in cards(root).issues}
    assert rows['valid'].priority == 'P3'
    assert rows['valid'].priority_state == 'valid'
    assert rows['invalid'].priority == '' and rows['invalid'].priority_state == 'invalid'
    assert rows['missing'].priority_state == 'missing'
    assert not rows['valid'].can_edit_priority

def test_http_permission_and_observability(writing, chat):
    from app.main import app
    from app.api.v1.admin_auth import require_session_user
    from app.chat.schema import usage_events
    from sqlalchemy import select, func
    client, _ = chat
    factory, project, _, _, _ = writing
    folder = change(project.root, 'standalone')
    payload = {'priority':'P1','expected_version':version((folder/'trace.md').read_text()),'idempotency_key':'http-priority'}
    url = '/api/v1/requirement-center/changes/standalone/priority?space_id=space&repository_id=repo'
    app.dependency_overrides[require_session_user] = lambda: {'id':'bob'}
    assert client.put(url,json=payload).status_code == 403
    app.dependency_overrides[require_session_user] = lambda: {'id':'alice'}
    assert client.put(url,json=payload).status_code == 202
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(usage_events).where(usage_events.c.event_name=='requirement_center.priority_save')) == 0
    payload['idempotency_key'] = 'http-priority-ui'
    assert client.put(url,json=payload,headers={'X-Chat-Client':'web','X-Behavior-Event-ID':'event-priority','X-Behavior-Trace-ID':'trace-priority'}).status_code == 202
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(usage_events).where(usage_events.c.event_name=='requirement_center.priority_save')) == 1

def test_telemetry_failure_does_not_block_priority(writing, chat, monkeypatch):
    import app.governance.acceptance_observability as observation
    from app.governance.writer import process
    client,_ = chat
    factory, project, _, _, _ = writing
    folder=change(project.root,'standalone')
    monkeypatch.setattr(observation, 'insert', lambda *args: (_ for _ in ()).throw(RuntimeError('synthetic telemetry failure')))
    response=client.put('/api/v1/requirement-center/changes/standalone/priority?space_id=space&repository_id=repo',
        json={'priority':'P3','expected_version':version((folder/'trace.md').read_text()),'idempotency_key':'telemetry-failure'},
        headers={'X-Chat-Client':'web','X-Behavior-Event-ID':'event-priority','X-Behavior-Trace-ID':'trace-priority'})
    assert response.status_code==202
    with factory() as db: assert process(db,response.json()['data']['id'])['state']=='applied'
    assert yaml.safe_load((folder/'trace.md').read_text().split('---')[1])['priority']=='P3'

def test_two_queued_writers_preserve_first_result(writing):
    from app.governance.reader import ProjectReader
    from app.governance.change_priority import enqueue_priority
    from app.governance.writer import process
    factory,project,_,_,_=writing
    folder=change(project.root,'standalone'); old=(folder/'trace.md').read_text()
    with factory() as db:
        reader=ProjectReader(db,'alice',project);reader.request_id='test'
        a=enqueue_priority(reader,'standalone','P1',version(old),'first')
        b=enqueue_priority(reader,'standalone','P0',version(old),'second')
        assert process(db,a['id'])['state']=='applied'
        assert process(db,b['id'])['state']=='conflict'
    assert yaml.safe_load((folder/'trace.md').read_text().split('---')[1])['priority']=='P1'

def test_fix_http_rejected_before_enqueue(writing, chat, monkeypatch):
    import app.governance.writer as writer
    client, _ = chat
    _, project, _, _, _ = writing
    folder = change(project.root, 'fix-sample', severity='high')
    previous = (folder/'trace.md').read_text()
    monkeypatch.setattr(writer, 'enqueue', lambda *a, **kw: pytest.fail('fix must not enqueue'))
    response = client.put('/api/v1/requirement-center/changes/fix-sample/priority?space_id=space&repository_id=repo',
        json={'priority':'P1','expected_version':version(previous),'idempotency_key':'fix-rejected'})
    assert response.status_code == 409
    assert (folder/'trace.md').read_text() == previous

def test_queued_priority_rechecks_type(writing):
    from app.governance.reader import ProjectReader
    from app.governance.change_priority import enqueue_priority
    from app.governance.writer import process
    factory, project, _, _, _ = writing
    folder = change(project.root, 'standalone')
    previous = (folder/'trace.md').read_text()
    with factory() as db:
        reader = ProjectReader(db, 'alice', project)
        reader.request_id = 'type-race'
        result = enqueue_priority(reader, 'standalone', 'P1', version(previous), 'type-race')
        changed = previous.replace('---\n', '---\nchange_type: fix\n', 1)
        (folder/'trace.md').write_text(changed)
        assert process(db, result['id'])['state'] != 'applied'
    assert (folder/'trace.md').read_text() == changed
