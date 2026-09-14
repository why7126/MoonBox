"""REQ-0026 complete associations and fail-closed object access."""
import json
import shutil
import pytest
import yaml
from sqlalchemy import insert, text
from app.chat.schema import object_access
from app.services import requirement_center as service
from test_chat import chat
from test_governance_scope import fixture_tree, bind
from test_governance_board import write

QUERY = {'space_id': 'space', 'repository_id': 'repo'}
BASE = '/api/v1/requirement-center'

def issue(root, oid='REQ-0099-sample', **extra):
    folder = 'requirements' if oid.startswith('REQ') else 'bugs'
    registry = root / f'issues/{folder}/_registry.yaml'
    entry = dict(id=oid, path=f'issues/{folder}/review/{oid}', status='in_sprint', title='原需求标题', **extra)
    data = yaml.safe_load(registry.read_text()); data['entries'].append(entry)
    write(registry, yaml.safe_dump(data))
    write(root / entry['path'] / 'trace.md', '---\nstatus: in_sprint\n---\n')
    write(root / entry['path'] / ('requirement.md' if folder == 'requirements' else 'bug.md'), '# 原需求')
    return entry

def change(root, cid='sample-change', location='changes', **trace):
    directory = root / 'openspec' / location / cid
    write(directory / 'trace.md', '---\n' + yaml.safe_dump(dict(status='proposed', **trace), allow_unicode=True) + '---\n')
    write(directory / 'proposal.md', '# 业务能力调整\n')
    write(directory / 'tasks.md', '- [x] 完成一项\n')
    return directory

def cards(root, visible=lambda _: True):
    with service.using_governance_root(root):
        return service.build_requirement_center_context(visibility=visible)

def test_bidirectional_dedup_and_multi_current(tmp_path):
    root = fixture_tree(tmp_path); issue(root, related_change='one'); change(root, 'one', title='中文业务标题')
    first = cards(root)
    assert len(first.issues) == 1 and first.stats.standalone_changes == 0
    row = first.issues[0]
    assert row.id == 'REQ-0099' and row.title == '原需求标题'
    assert row.current_change.id == 'one' and row.current_change.title == '中文业务标题'
    assert row.stage == 'ready-dev' and row.task_progress == (1, 1)
    change(root, 'two', requirement='REQ-0099')
    row = cards(root).issues[0]
    assert row.current_change is None and len(row.related_changes) == 2
    assert row.change_warning == '多个 Change，当前项待核实'
    assert row.tasks is None and row.title == '原需求标题' and row.stage == 'ready-dev'

def test_hidden_sources_never_become_independent(tmp_path):
    root = fixture_tree(tmp_path); issue(root)
    change(root, 'private-change', requirement_id='REQ-0099-sample')
    change(root, 'dangling-change', source_requirement='REQ-8888-missing')
    change(root, 'public-change')
    context = cards(root, lambda oid: oid != 'REQ-0099-sample')
    assert [r.id for r in context.issues] == ['public-change']
    assert context.stats.total == context.stats.standalone_changes == 1
    issue(root, 'REQ-0099-other'); change(root, 'ambiguous-change', requirement='REQ-0099')
    assert 'ambiguous-change' not in [r.id for r in cards(root).issues]

def test_archive_active_precedence_unknown_and_missing_tasks(tmp_path):
    root = fixture_tree(tmp_path); old = change(root, '2026-09-01-sample', location='archive')
    assert cards(root).issues[0].stage == 'done'
    active = change(root, 'sample'); (active / 'tasks.md').unlink()
    assert cards(root).issues[0].task_progress is None
    with service.using_governance_root(root), pytest.raises(FileNotFoundError):
        service.read_requirement_center_change_document('sample', 'tasks.md')
    shutil.rmtree(active); change(root, '2026-09-02-sample', location='archive')
    row = cards(root).issues[0]
    assert row.stage == 'unknown' and row.document_entries == []
    shutil.rmtree(old); assert cards(root).issues[0].stage == 'done'
    active = change(root, 'bad-state'); write(active / 'trace.md', '---\nstatus: mystery\n---\n')
    assert next(r for r in cards(root).issues if r.id == 'bad-state').stage == 'unknown'

def test_missing_title_and_execution_fact(tmp_path):
    root = fixture_tree(tmp_path)
    directory = change(root, execution={'schema_version': 1, 'started_at': '2026-09-12'})
    write(directory / 'proposal.md', '# 变更提案\n## 为什么\n')
    row = cards(root).issues[0]
    assert row.title == 'sample-change' and row.stage == 'development'
    write(directory / 'trace.md', '---\nexecution: {schema_version: 99}\n---\n')
    assert cards(root).issues[0].stage == 'unknown'

@pytest.fixture
def context_database(chat):
    client, factory = chat
    with factory() as db:
        for column, definition in [('code', 'TEXT'), ('description', 'TEXT'), ('member_count', 'INTEGER'), ('created_at', 'TEXT')]:
            db.execute(text(f'ALTER TABLE admin_spaces ADD COLUMN {column} {definition}'))
        db.execute(text('ALTER TABLE admin_users ADD COLUMN username TEXT'))
        db.execute(text('ALTER TABLE admin_users ADD COLUMN nickname TEXT'))
        db.execute(text('CREATE TABLE admin_space_products (space_id TEXT)'))
        db.execute(text("INSERT INTO admin_space_products VALUES ('space')")); db.commit()
    return client, factory

def test_http_permissions_readonly_sprint_and_refresh(context_database, tmp_path, monkeypatch):
    client, factory = context_database; root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    change(root, iteration='sprint-005'); sprint = root / 'iterations/change/sprint-005'
    write(sprint / 'sprint.yaml', 'changes: [sample-change]\n'); write(sprint / 'sprint.md', '# 本次迭代')
    route = BASE + '/changes/sample-change/documents/'
    assert client.get(route + 'sprint.md', params=QUERY).json()['data']['content'] == '# 本次迭代'
    response = client.get(BASE + '/context', params=QUERY)
    assert response.status_code == 200, response.text
    data = response.json()['data']; row = data['issues'][0]
    assert data['stats']['standalone_changes'] == 1 and row['action']['label'] == '开始开发' and row['action']['disabled_reason'] is None and row['priority'] == ''
    assert all(not d['editable'] and not d['capability']['task_toggle_only'] for d in row['document_entries'])
    assert all('repository_id=repo' in d['url'] for d in row['document_entries'])
    document = client.get(route + 'tasks.md', params=QUERY).json()['data']
    body = dict(content='- [ ] 更改任务', expected_version=document['version'], idempotency_key='standalone-reject')
    assert client.put(route + 'tasks.md', params=QUERY, json=body).status_code == 403
    assert client.put(route + 'tasks.md/tasks', params=QUERY, json=body).status_code == 403
    with factory() as db:
        db.execute(insert(object_access).values(space_id='space',repository_id='repo',object_id='sample-change',user_id='bob',can_read=1)); db.commit()
    assert client.get(route + 'tasks.md', params=QUERY).status_code == 403
    assert client.get(BASE + '/context', params=QUERY).json()['data']['stats']['total'] == 0
    with factory() as db:
        db.execute(text('DELETE FROM chat_object_access'))
        db.execute(text("UPDATE admin_spaces SET status='FROZEN'")); db.commit()
    assert client.get(route + 'tasks.md', params=QUERY).status_code == 200
    frozen = client.get(BASE + '/context', params=QUERY).json()['data']['issues'][0]
    assert '只读' in frozen['action']['disabled_reason']
    write(sprint / 'sprint.yaml', 'changes: []\n')
    assert client.get(route + 'sprint.md', params=QUERY).status_code == 404
    issue(root, related_change='sample-change')
    with factory() as db:
        db.execute(insert(object_access).values(space_id='space',repository_id='repo',object_id='REQ-0099-sample',user_id='bob',can_read=1)); db.commit()
    assert client.get(route + 'tasks.md', params=QUERY).status_code == 403
    assert client.get(BASE + '/context', params=QUERY).json()['data']['stats']['total'] == 0

def test_multiple_source_permission_and_conflict_api(context_database,tmp_path,monkeypatch):
    client, factory = context_database; root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    issue(root, related_change='shared'); issue(root, 'BUG-0099-sample', related_change='shared'); change(root, 'shared')
    with factory() as db:
        db.execute(insert(object_access).values(space_id='space',repository_id='repo',object_id='BUG-0099-sample',user_id='bob',can_read=1)); db.commit()
    data = client.get(BASE + '/context',params=QUERY).json()['data']
    assert data['stats']['total'] == 1 and data['issues'][0]['related_changes'] == []
    assert 'shared' not in json.dumps(data)
    assert client.get(BASE+'/changes/shared/documents/tasks.md',params=QUERY).status_code == 403
    change(root,'2026-09-01-conflict',location='archive'); change(root,'2026-09-02-conflict',location='archive')
    assert client.get(BASE+'/changes/conflict/documents/tasks.md',params=QUERY).status_code == 404
    (root/'issues/requirements/_registry.yaml').write_text('entries: [')
    assert client.get(BASE+'/context',params=QUERY).status_code == 503


def test_document_audit_and_collection_failure(context_database,tmp_path,monkeypatch):
    from sqlalchemy import select
    from app.chat.schema import audit
    from app.chat import api
    client,factory=context_database; root=fixture_tree(tmp_path/'repo');bind(monkeypatch,root)
    change(root)
    route=BASE+'/changes/sample-change/documents/tasks.md'
    response=client.get(route,params=QUERY,headers={'X-Request-ID':'forged','X-Chat-Client':'untrusted'})
    assert response.status_code==200 and response.headers['X-Request-ID']!='forged'
    with factory() as db:
        row=db.execute(select(audit).where(audit.c.request_id==response.headers['X-Request-ID'])).mappings().one()
        assert row['actor_id']=='alice' and row['status_code']==200
        assert '完成一项' not in json.dumps(dict(row))
        db.execute(insert(object_access).values(space_id='space',repository_id='repo',object_id='sample-change',user_id='bob',can_read=1));db.commit()
    response=client.get(route,params=QUERY)
    assert response.status_code==403
    with factory() as db:
        row=db.execute(select(audit).where(audit.c.request_id==response.headers['X-Request-ID'])).mappings().one()
        assert row['status_code']==403
        db.execute(text('DELETE FROM chat_object_access'));db.commit()
    # Only the audit session fails; source and authorized document reads still run.
    monkeypatch.setattr(api,'get_session_factory',lambda: (_ for _ in ()).throw(RuntimeError('instrumentation unavailable')))
    assert client.get(route,params=QUERY).status_code==200


def test_reverse_source_does_not_expand_write_access(context_database,tmp_path,monkeypatch):
    client,_=context_database;root=fixture_tree(tmp_path/'repo');bind(monkeypatch,root)
    issue(root); change(root,requirement='REQ-0099-sample')
    route=BASE+'/changes/sample-change/documents/tasks.md'
    assert client.get(route,params=QUERY).status_code==200
    assert client.put(route,params=QUERY,json={'content':'- [ ] 修改','expected_version':'a'*64,'idempotency_key':'reverse-source'}).status_code==403
    write(root/'openspec/changes/sample-change/trace.md','---\nchange_id: other-identity\nstatus: proposed\n---\n')
    assert client.get(route,params=QUERY).status_code==403

@pytest.mark.parametrize('location', ['change', 'archive'])
@pytest.mark.parametrize('iteration', [None, ''])
def test_completed_change_unique_sprint_membership(tmp_path, location, iteration):
    root = fixture_tree(tmp_path)
    change(root, '2026-09-01-sample', location='archive', iteration=iteration)
    sprint = root / f'iterations/{location}/sprint-005'
    write(sprint / 'sprint.yaml', 'changes: [sample]\n')
    row = cards(root).issues[0]
    assert row.stage == 'done' and row.sprint_id == 'sprint-005'
    assert 'sprint.md' not in row.documents
    with service.using_governance_root(root), pytest.raises(FileNotFoundError):
        service.read_requirement_center_change_document('sample', 'sprint.md')
    write(sprint / 'sprint.md', '# 唯一所属迭代\n')
    assert 'sprint.md' in cards(root).issues[0].documents
    with service.using_governance_root(root):
        assert '唯一所属迭代' in str(service.read_requirement_center_change_document('sample', 'sprint.md'))
    assert cards(root, lambda _: False).issues == []


def test_sprint_membership_ambiguity_and_explicit_priority(tmp_path):
    root = fixture_tree(tmp_path); directory = change(root, 'sample')
    for sid in ('sprint-004', 'sprint-005'):
        write(root / f'iterations/archive/{sid}/sprint.yaml', 'changes: [sample]\n')
        write(root / f'iterations/archive/{sid}/sprint.md', '# 迭代\n')
    row = cards(root).issues[0]
    assert row.sprint_id is None and 'sprint.md' not in row.documents
    assert any('多个 Sprint' in w for w in row.drift_warnings)
    for explicit, expected in [('sprint-005', 'sprint-005'), ('sprint-099', None), ('../sprint-005', None), ([], None)]:
        write(directory / 'trace.md', '---\n' + yaml.safe_dump({'iteration': explicit}) + '---\n')
        assert cards(root).issues[0].sprint_id == expected


def test_active_sprint_precedes_archive_without_backfill(tmp_path):
    root = fixture_tree(tmp_path); change(root, 'sample')
    archived = root / 'iterations/archive/sprint-005'; active = root / 'iterations/change/sprint-005'
    write(archived / 'sprint.yaml', 'changes: [sample]\n'); write(archived / 'sprint.md', '# 旧迭代\n')
    write(active / 'sprint.yaml', 'changes: [sample]\n')
    row = cards(root).issues[0]
    assert row.sprint_id == 'sprint-005' and 'sprint.md' not in row.documents
    (active / 'sprint.yaml').unlink()
    assert cards(root).issues[0].sprint_id is None


def test_invalid_sprint_metadata_does_not_break_change_cards(tmp_path):
    root = fixture_tree(tmp_path); change(root, 'sample')
    write(root / 'iterations/change/sprint-005/sprint.yaml', 'changes: [invalid\n')
    from app.governance.change_index import ChangeIndex
    with service.using_governance_root(root):
        index = ChangeIndex(root)
        assert index.sprint_id(index.records['sample']) is None


def test_completed_sprint_reverse_lookup_http(context_database, tmp_path, monkeypatch):
    client, factory = context_database
    root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    change(root, '2026-09-01-sample', location='archive')
    sprint = root / 'iterations/archive/sprint-005'
    write(sprint / 'sprint.yaml', 'changes: [sample]\n')
    route = BASE + '/changes/sample/documents/sprint.md'
    row = client.get(BASE + '/context', params=QUERY).json()['data']['issues'][0]
    assert row['stage'] == 'done' and row['sprint_id'] == 'sprint-005'
    assert client.get(route, params=QUERY).status_code == 404
    write(sprint / 'sprint.md', '# 历史迭代\n')
    assert client.get(route, params=QUERY).status_code == 200
    with factory() as db:
        db.execute(insert(object_access).values(space_id='space', repository_id='repo', object_id='sample', user_id='bob', can_read=1)); db.commit()
    assert client.get(route, params=QUERY).status_code == 403
    assert client.get(BASE + '/context', params=QUERY).json()['data']['issues'] == []


def test_standalone_stage_actions_are_capability_gated(tmp_path):
    root = fixture_tree(tmp_path); directory = change(root)
    for state, label, command in [('proposed', '开始开发', '/opsx-apply'), ('in_progress', '查看进度', '查看进度'), ('applied', '完成 / 归档', '/opsx-archive')]:
        write(directory / 'trace.md', '---\nstatus: ' + state + '\n---\n')
        action = cards(root).issues[0].action
        assert action.label == label and action.command == command + ' sample-change'
        assert bool(action.disabled_reason) == (state != 'in_progress')
    write(directory / 'trace.md', '---\nstatus: unknown\n---\n')
    assert cards(root).issues[0].action is None


def test_standalone_action_uses_actual_document_gates(tmp_path):
    root = fixture_tree(tmp_path); directory = change(root, iteration='sprint-005')
    write(root / 'iterations/change/sprint-005/sprint.yaml', 'changes: [sample-change]\n')
    assert cards(root).issues[0].action.disabled_reason is None
    write(directory / 'trace.md', '---\nstatus: applied\niteration: sprint-005\n---\n')
    assert '验收来源待核实' in cards(root).issues[0].action.disabled_reason
    write(directory / 'acceptance.md', '')
    assert '文档内容为空' in cards(root).issues[0].action.disabled_reason
    write(directory / 'acceptance.md', '# 验收\n- [x] 已核对\n')
    assert cards(root).issues[0].action.disabled_reason is None


def test_change_delivery_sources_and_explicit_reference_boundaries(tmp_path):
    root = fixture_tree(tmp_path); directory = change(root, iteration='sprint-005')
    write(root / 'iterations/change/sprint-005/sprint.yaml', 'changes: [sample-change]\n')
    trace = '---\nstatus: applied\niteration: sprint-005\n---\n'
    write(directory / 'trace.md', trace + '# 交付\n## 验证记录\n5项容量回归通过。\n')
    assert cards(root).issues[0].action.disabled_reason is None
    write(directory / 'trace.md', trace)
    assert '验收来源待核实' in cards(root).issues[0].action.disabled_reason
    write(directory / 'verification.md', '# 验证结果\n已完成检查')
    assert cards(root).issues[0].action.disabled_reason is None
    for ref in ['missing.md', '../outside.md', '/tmp/outside.md']:
        write(directory / 'trace.md', trace.replace('status: applied', 'status: applied\nacceptance_refs: [' + ref + ']'))
        assert '验收来源待核实' in cards(root).issues[0].action.disabled_reason
    write(directory / 'evidence/check.md', '# 验证报告\n记录')
    write(directory / 'trace.md', trace.replace('status: applied', 'status: applied\nacceptance_refs: [evidence/check.md]'))
    assert cards(root).issues[0].action.disabled_reason is None


def test_trace_business_heading_is_last_title_fallback(tmp_path):
    from app.governance.change_index import chinese_title
    (tmp_path / 'trace.md').write_text('# Issue 分级元数据统一\n', encoding='utf-8')
    assert chinese_title(tmp_path, {}) == 'Issue 分级元数据统一'
    assert chinese_title(tmp_path, {'title': '显式业务标题'}) == '显式业务标题'
    (tmp_path / 'proposal.md').write_text('# 提案：已有业务标题\n', encoding='utf-8')
    assert chinese_title(tmp_path, {}) == '已有业务标题'


@pytest.mark.parametrize('heading', ['追溯', 'Change 追溯', '变更追溯', '验证记录', '验收记录', '验收结果', '验证结果', '背景', '任务清单', '背景与动机', '设计决策'])
def test_trace_generic_heading_is_not_a_business_title(tmp_path, heading):
    from app.governance.change_index import chinese_title
    (tmp_path / 'trace.md').write_text(f'# {heading}\n## 中文内容章节\n', encoding='utf-8')
    assert chinese_title(tmp_path, {}) is None
