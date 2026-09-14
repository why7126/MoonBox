"""Capture acceptance uses disposable projects and the real durable controller."""
import json
import pytest
import yaml
from sqlalchemy import text, select
from app.chat.schema import task_traces, task_trace_spans, usage_events, audit
from app.chat.service import ChatError
from app.governance import writer, store
from app.governance.snapshot import stable
from app.schemas.requirement_center import RequirementCenterCaptureCreate
from test_chat import chat
from test_governance_writer import writing

QUERY = {'space_id': 'space', 'repository_id': 'repo'}


@pytest.fixture(autouse=True)
def capture_controller_heartbeat(writing):
    from app.governance.readiness import publish
    publish()



def payload(kind='requirement', key='capture-1'):
    return {'type': kind, 'title': '采集测试 | 中文', 'description': '第一行\n第二行',
            **({'priority': 'P3'} if kind == 'requirement' else {'severity': 'high'}), 'owner': '研发团队', 'source': 'user-feedback', 'idempotency_key': key}


def queue(factory, project, kind='requirement', key='capture-1'):
    data = RequirementCenterCaptureCreate(**payload(kind, key)).model_dump(exclude={'idempotency_key'})
    with factory() as db:
        return writer.enqueue(db, 'alice', project, key, {'kind': 'capture', **data},
                              {'kind': 'capture', 'payload': data, 'before': {}, 'after': {}}, request_id='capture-request')


@pytest.mark.parametrize('kind,prefix,folder', [('requirement', 'REQ', 'requirements'), ('bug', 'BUG', 'bugs')])
def test_real_capture_api_and_reload(chat, writing, kind, prefix, folder, monkeypatch):
    client, _ = chat
    # Minimal chat fixture omits workspace presentation tables; keep real scope and file reader.
    monkeypatch.setattr("app.services.requirement_center._load_workspaces", lambda *args: [])
    factory, project, before, _, _ = writing
    response = client.post('/api/v1/requirement-center/captures', params=QUERY, json=payload(kind), headers={'X-Chat-Client': 'web'})
    assert response.status_code == 202, response.text
    oid = response.json()['data']['id']
    assert stable(project.root).files == before  # acceptance is not completion
    with factory() as db:
        assert writer.process(db, oid)['state'] == 'applied'
        record = writer.operation(db, 'alice', oid)
    full_id = record['object_id']
    assert full_id.startswith(prefix + '-') and len(full_id.split('-')) >= 3
    registry = yaml.safe_load((project.root / f'issues/{folder}/_registry.yaml').read_text())
    entry = next(e for e in registry['entries'] if e['id'] == full_id)
    path = project.root / entry['path']
    assert '第一行\n第二行' in (path / 'capture.md').read_text()
    trace = yaml.safe_load((path / 'trace.md').read_text().split('---', 2)[1])
    level_key = 'priority' if kind == 'requirement' else 'severity'
    other = 'severity' if kind == 'requirement' else 'priority'
    capture_meta = yaml.safe_load((path / 'capture.md').read_text().split('---', 2)[1])
    for metadata in [trace, capture_meta, entry]:
        assert metadata[level_key] == payload(kind)[level_key]
        assert other not in metadata and 'severity_hint' not in metadata
    assert trace['status'] == 'captured' and trace['iteration'] is None and not trace['openspec_changes']
    assert full_id in (project.root / f'issues/{folder}/CHANGELOG.md').read_text()
    assert registry['next_id'] > int(full_id.split('-')[1])
    context = client.get('/api/v1/requirement-center/context', params=QUERY)
    assert context.status_code == 200, context.text
    assert any(i['id'] == '-'.join(full_id.split('-')[:2]) and full_id in i['detail_url']
               for i in context.json()['data']['issues'])
    doc = client.get(f'/api/v1/requirement-center/issues/{full_id}/documents/capture.md', params=QUERY)
    assert doc.status_code == 200 and '第二行' in doc.json()['data']['content']
    assert client.post('/api/v1/requirement-center/captures', params=QUERY, json=payload(kind)).json()['data']['id'] == oid
    changed = payload(kind); changed['description'] = 'different'
    assert client.post('/api/v1/requirement-center/captures', params=QUERY, json=changed).status_code == 409
    with factory() as db:
        rows = list(db.execute(select(task_traces).where(task_traces.c.turn_id == 'governance:' + oid)).mappings())
        assert len(rows) == 1 and rows[0]['parent_request_id']
        assert list(db.scalars(select(task_trace_spans.c.id).where(task_trace_spans.c.task_trace_id == rows[0]['task_trace_id'])))
        assert '第一行' not in rows[0]['metadata']
        events = list(db.execute(select(usage_events).where(usage_events.c.event_name == 'governance.capture')).mappings())
        assert len(events) == 1  # direct API retries above do not fabricate UI behavior
        assert json.loads(events[0]['properties']) == {'operation_id': oid}
        assert events[0]['parent_request_id'] == response.headers['X-Request-ID']
        assert db.scalar(select(audit.c.id).where(audit.c.request_id == events[0]['parent_request_id']))


def test_two_queued_creates_allocate_under_lock(writing):
    factory, project, *_ = writing
    one = queue(factory, project, key='one'); two = queue(factory, project, key='two')
    with factory() as db:
        assert writer.process(db, one['id'])['state'] == 'applied'
        assert writer.process(db, two['id'])['state'] == 'applied'
        assert writer.operation(db, 'alice', one['id'])['object_id'] != writer.operation(db, 'alice', two['id'])['object_id']
    registry = yaml.safe_load((project.root / 'issues/requirements/_registry.yaml').read_text())
    assert len({e['id'] for e in registry['entries']}) == len(registry['entries'])


@pytest.mark.parametrize('crash_index', range(4))
def test_restart_after_each_file_rolls_forward(writing, crash_index):
    factory, project, *_ = writing
    oid = queue(factory, project)['id']
    def crash(index, path):
        if index == crash_index:
            raise SystemExit('synthetic crash')
    with factory() as db:
        with pytest.raises(SystemExit):
            writer.process(db, oid, after_write=crash)
        with pytest.raises(ChatError):
            writer.assert_readable(db, project)
    with factory() as db:
        assert writer.process(db, oid)['state'] == 'applied'
        full_id = writer.operation(db, 'alice', oid)['object_id']
    assert full_id in (project.root / 'issues/requirements/CHANGELOG.md').read_text()


def test_external_recovery_conflict_preserves_newer_file(writing):
    factory, project, *_ = writing
    oid = queue(factory, project)['id']; changed = []
    def crash(index, path):
        changed.append(path); raise SystemExit()
    with factory() as db:
        with pytest.raises(SystemExit): writer.process(db, oid, after_write=crash)
    target = project.root / changed[0]; target.write_text('external newer content')
    with factory() as db:
        assert writer.process(db, oid)['state'] == 'recovery_blocked'
        with pytest.raises(ChatError): writer.assert_readable(db, project)
    assert target.read_text() == 'external newer content'


def test_input_and_permission_gates(chat, writing):
    client, _ = chat; factory, project, before, _, permit = writing
    for change in [{'title': '  '}, {'title': 'a' * 61}, {'type': 'other'}, {'priority': 'P8'},
                   {'description': 'a' * 201}, {'path': '../../private'}, {'owner': 'other'}, {'idempotency_key': '../bad'}]:
        assert client.post('/api/v1/requirement-center/captures', params=QUERY, json={**payload(), **change}).status_code == 422
    assert client.post('/api/v1/requirement-center/captures', params={**QUERY, 'repository_id': 'other'}, json=payload()).status_code == 503
    with factory() as db:
        db.execute(text("UPDATE admin_spaces SET status='FROZEN'")); db.commit()
    assert client.post('/api/v1/requirement-center/captures', params=QUERY, json=payload()).status_code == 403
    with factory() as db:
        db.execute(text("UPDATE admin_spaces SET status='ACTIVE'")); db.commit()
    permit.unlink()
    assert client.post('/api/v1/requirement-center/captures', params=QUERY, json=payload()).status_code == 503
    assert stable(project.root).files == before


def test_directory_symlink_is_never_followed(writing, tmp_path):
    factory, project, *_ = writing
    target = tmp_path / 'outside'; target.mkdir()
    (project.root / 'issues/bugs/plan').symlink_to(target, target_is_directory=True)
    oid = queue(factory, project, kind='bug')['id']
    with factory() as db: assert writer.process(db, oid)['state'] == 'conflict'
    assert list(target.iterdir()) == []


def test_contending_controller_does_not_allocate_outside_lock(writing):
    factory, project, before, *_ = writing
    oid = queue(factory, project)['id']
    with writer.project_lock(project), factory() as db:
        with pytest.raises(BlockingIOError): writer.process(db, oid)
    assert stable(project.root).files == before
    with factory() as db: assert writer.process(db, oid)['state'] == 'applied'


def test_directory_write_failure_is_not_success_and_preserves_snapshot(writing, monkeypatch):
    factory, project, before, *_ = writing
    oid = queue(factory, project)['id']
    original = writer.os.mkdir
    def fail(*args, **kwargs):
        if kwargs.get('dir_fd') is not None: raise PermissionError('synthetic directory refusal')
        return original(*args, **kwargs)
    monkeypatch.setattr(writer.os, 'mkdir', fail)
    with factory() as db:
        assert writer.process(db, oid)['state'] == 'recovery_blocked'
        with pytest.raises(ChatError): writer.assert_readable(db, project)
    record = store.read(oid, 'operation')
    assert record['planned'] and record['before'] and record['after']
    for name, content in before.items():
        if '/plan/' in name: assert (project.root / name).read_bytes() == content


def test_continuous_capture_uses_live_controller_not_expiring_maintenance(chat, writing, monkeypatch):
    from app.governance.readiness import publish, status
    factory, project, _, _, permit = writing
    monkeypatch.setenv('MOONBOX_GOVERNANCE_CAPTURE_MODE', 'continuous')
    permit.unlink()
    with factory() as db: assert status(db, project)['ready'] is False
    publish()
    with factory() as db: assert status(db, project)['ready'] is True
    oid = queue(factory, project)['id']
    with factory() as db: assert writer.process(db, oid)['state'] == 'applied'
    # Legacy document operations are not granted continuous permissions.
    with pytest.raises(ChatError): writer.write_permission(project, 'document')
    path = store.root()/'controller-ready.json'
    data = json.loads(path.read_text());data['time'] -= 31;path.write_text(json.dumps(data))
    with factory() as db: assert status(db, project)['ready'] is False
    with pytest.raises(ChatError): queue(factory, project, key='offline')
    publish()
    with factory() as db: assert status(db, project)['ready'] is True
    data = json.loads(path.read_text());data['projects'][project.key]['revision'] = 'stale';path.write_text(json.dumps(data))
    with factory() as db: assert status(db, project)['ready'] is False

@pytest.mark.parametrize('kind,fields', [
    ('bug', {'priority': 'P1'}), ('bug', {'severity': 'high', 'priority': None}),
    ('bug', {'severity': 'P1'}), ('bug', {}),
    ('requirement', {'severity': 'high'}), ('requirement', {'priority': 'P4'}),
    ('requirement', {}),
])
def test_capture_rejects_invalid_type_grading(kind, fields):
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        RequirementCenterCaptureCreate(type=kind, title='test', idempotency_key='grading', **fields)
