"""REQ-0056 delivery projection must not mutate source or sibling facts."""
import yaml
from app.services import requirement_center as service
from test_change_visibility import cards, change, issue, context_database
from test_chat import chat
from test_governance_scope import fixture_tree
from test_governance_board import write


def sprint(root, sid, changes, estimates=()):
    folder = root / 'iterations/change' / sid
    write(folder / 'sprint.yaml', yaml.safe_dump(dict(sprint_id=sid, status='planning', changes=changes, scope_estimates=list(estimates))))
    write(folder / 'sprint.md', '# 迭代规划')


def test_siblings_keep_history_and_count_source_once(tmp_path):
    root = fixture_tree(tmp_path)
    source = issue(root)
    change(root, 'old-delivery', requirement_id=source['id'], iteration='sprint-001')
    old = root / 'openspec/changes/old-delivery'
    archived = root / 'openspec/archive/2026-10-01-old-delivery'
    archived.parent.mkdir(parents=True, exist_ok=True); old.rename(archived)
    new = change(root, 'new-delivery', requirement_id=source['id'], iteration='sprint-002')
    write(new / 'tasks.md', '## 实施任务\n- [ ] 1.1 新交付\n')
    sprint(root, 'sprint-001', ['old-delivery'])
    sprint(root, 'sprint-002', ['new-delivery'], [dict(id=source['id'], change='new-delivery', estimated_person_days=13)])
    before = (archived / 'trace.md').read_bytes()
    write(archived / 'evidence/record.md', '# 历史附件\n保持原交付证据。\n')
    history_before = {str(path.relative_to(archived)): path.read_bytes() for path in archived.rglob('*') if path.is_file()}
    context = cards(root)
    rows = {row.id: row for row in context.issues}
    assert set(rows) == {'old-delivery', 'new-delivery'}
    assert context.stats.requirements == 1 and context.stats.total == 2
    assert context.stats.standalone_changes == 0
    assert rows['old-delivery'].stage == 'done' and rows['old-delivery'].sprint_id == 'sprint-001'
    assert rows['new-delivery'].stage == 'ready-dev' and rows['new-delivery'].sprint_id == 'sprint-002'
    assert rows['new-delivery'].task_progress == (0, 1)
    assert rows['new-delivery'].estimated_person_days is None
    assert rows['old-delivery'].completion_hint
    assert rows['new-delivery'].action.disabled_reason is None
    assert source['id'] in rows['new-delivery'].action.command
    assert (archived / 'trace.md').read_bytes() == before
    assert {str(path.relative_to(archived)): path.read_bytes() for path in archived.rglob('*') if path.is_file()} == history_before
    for row in rows.values():
        assert row.target_change_id == row.id
        assert row.source_issues[0].id == source['id']
        assert all('/changes/' + row.id + '/' in d.url for d in row.document_entries)
        assert all('/issues/' in d.url for d in row.source_issues[0].document_entries)


def test_many_sources_one_card_and_hidden_relation_never_standalone(tmp_path):
    root = fixture_tree(tmp_path)
    a = issue(root, 'REQ-0098-first'); b = issue(root, 'BUG-0099-second')
    change(root, 'shared-delivery', source_issues=[a['id'], b['id']])
    context = cards(root)
    assert len(context.issues) == 1
    assert len(context.issues[0].source_issues) == 2
    assert context.stats.requirements == context.stats.bugs == 1
    hidden = cards(root, lambda oid: oid != b['id'])
    assert all(row.type != 'change' for row in hidden.issues)
    assert b['id'] not in hidden.model_dump_json()
    assert hidden.issues[0].change_warning


def test_explicit_change_estimate_and_missing_task_do_not_fall_back(tmp_path):
    root = fixture_tree(tmp_path); source = issue(root)
    first = change(root, 'first', requirement_id=source['id'], iteration='sprint-001')
    change(root, 'second', requirement_id=source['id'], iteration='sprint-001')
    (first / 'tasks.md').unlink()
    sprint(root, 'sprint-001', ['first', 'second'], [dict(id='first', requirement=source['id'], estimated_person_days=2.5)])
    rows = {row.id: row for row in cards(root).issues}
    assert rows['first'].estimated_person_days == 2.5
    assert rows['second'].estimate_status == 'missing'
    assert rows['first'].tasks is None and rows['second'].task_progress == (1, 1)


def test_early_source_and_explicit_source_detail(tmp_path):
    root = fixture_tree(tmp_path); source = issue(root)
    assert cards(root).issues[0].card_kind == 'issue'
    change(root, 'one', requirement_id=source['id'])
    with service.using_governance_root(root):
        detail = service.build_requirement_center_context(selected_object=source['id'])
    assert len(detail.issues) == 1 and detail.issues[0].card_kind == 'issue'
    assert detail.issues[0].status == 'in_sprint'


def test_delivery_acl_includes_own_identity(tmp_path):
    root = fixture_tree(tmp_path); source = issue(root)
    change(root, 'denied-delivery', requirement_id=source['id'])
    context = cards(root, lambda oid: oid != 'denied-delivery')
    assert [row.type for row in context.issues] == ['requirement']
    assert context.issues[0].change_warning


def test_delivery_http_documents_and_status_reject_hidden_source(context_database, tmp_path, monkeypatch):
    from test_governance_scope import bind
    from app.chat.schema import object_access
    from sqlalchemy import insert
    client, factory = context_database
    root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    source = issue(root)
    change(root, 'first', requirement_id=source['id'])
    change(root, 'second', requirement_id=source['id'])
    query = {'space_id':'space','repository_id':'repo'}
    result = client.get('/api/v1/requirement-center/context',params=query)
    assert result.status_code == 200
    rows = result.json()['data']['issues']
    assert {row['id'] for row in rows} == {'first','second'}
    assert all('repository_id=repo' in row['source_issues'][0]['document_entries'][0]['url'] for row in rows)
    assert all(row['source_issues'][0]['document_entries'][0]['url'].count('space_id=') == 1 for row in rows)
    task_url = '/api/v1/requirement-center/changes/first/documents/tasks.md'
    original = client.get(task_url, params=query).json()['data']
    with factory() as db:
        db.execute(insert(object_access).values(space_id='space',repository_id='repo',object_id=source['id'],user_id='bob',can_read=1));db.commit()
    assert client.get('/api/v1/requirement-center/changes/first/documents/tasks.md',params=query).status_code == 403
    assert client.get('/api/v1/requirement-center/status',params={**query,'object_ids':['first']}).status_code == 403
    before = (root / 'openspec/changes/first/tasks.md').read_bytes()
    assert client.put(task_url+'/tasks',params=query,json={'content':original['content'].replace('[x]','[ ]'),'expected_version':original['version'],'idempotency_key':'denied-target-write'}).status_code == 403
    assert (root / 'openspec/changes/first/tasks.md').read_bytes() == before


def test_source_only_action_never_picks_first_eligible_change(tmp_path):
    import pytest
    from app.chat.service import ChatError
    from app.governance.preparation import _require_issue_fact_source
    from app.governance.snapshot import stable
    root = fixture_tree(tmp_path); source = issue(root)
    write(root / source['path'] / 'trace.md', '---\nstatus: in_sprint\nopenspec_changes:\n  - change_id: first\n  - change_id: second\n---\n')
    change(root, 'first', requirement_id=source['id']);change(root,'second',requirement_id=source['id'])
    with pytest.raises(ChatError) as error:
        _require_issue_fact_source(stable(root),source['id'],'opsx-apply',root)
    assert error.value.kind == 'delivery_target_required'


def test_delivery_acceptance_never_borrows_parent_or_task_completion(tmp_path, monkeypatch):
    from app.governance.change_index import ChangeIndex
    root = fixture_tree(tmp_path); source = issue(root)
    folder = change(root, 'child', requirement_id=source['id'])
    index = ChangeIndex(root)
    record = index.records['child']
    with service.using_governance_root(root):
        assert index.delivery_acceptance_progress(record) is None
        write(folder / 'acceptance-plan.json', '{}')
        monkeypatch.setattr('app.governance.acceptance_evidence.read_plan', lambda _: {'checks':[{'id':'AC-001'}, {'id':'AC-002'}]})
        monkeypatch.setattr(index, 'acceptance_source_reason', lambda _: '证据过期')
        assert index.delivery_acceptance_progress(record) is None
        monkeypatch.setattr(index, 'acceptance_source_reason', lambda _: None)
        assert index.delivery_acceptance_progress(record) == (2, 2)


def test_delivery_observability_links_authorized_target_without_raw_content(context_database, tmp_path, monkeypatch):
    import json
    from sqlalchemy import select, func
    from app.chat.schema import audit, usage_events
    from test_governance_scope import bind
    client, factory = context_database
    root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    source = issue(root); change(root, 'observed-child', requirement_id=source['id'])
    url = '/api/v1/requirement-center/changes/observed-child/documents/tasks.md'
    params = {'space_id':'space','repository_id':'repo'}
    direct = client.get(url, params=params)
    assert direct.status_code == 200
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(usage_events)) == 0
        log = db.execute(select(audit).where(audit.c.request_id == direct.headers['X-Request-ID'])).mappings().one()
        assert json.loads(log['metadata']) == {'target_change_id':'observed-child','source_issue_ids':[source['id']]}
    response = client.get(url, params=params, headers={'X-Chat-Client':'web','X-Delivery-Action':'document-open'})
    assert response.status_code == 200
    with factory() as db:
        event = db.execute(select(usage_events).where(usage_events.c.event_name == 'governance.document_open')).mappings().one()
        props = json.loads(event['properties'])
        assert props['target_change_id'] == 'observed-child'
        assert props['source_issue_ids'] == [source['id']]
        assert 'content' not in props and 'prompt' not in props
        assert event['parent_request_id'] == response.headers['X-Request-ID']
    monkeypatch.setattr('app.chat.observability.behavior', lambda *a, **kw: (_ for _ in ()).throw(RuntimeError('synthetic telemetry failure')))
    assert client.get(url,params=params,headers={'X-Chat-Client':'web','X-Delivery-Action':'document-open'}).status_code == 200


def test_delivery_projection_keeps_source_identity_in_execution_guards(tmp_path):
    from app.governance.execution_context import stage_map
    from app.governance.snapshot import stable
    root = fixture_tree(tmp_path); source = issue(root)
    change(root, 'guarded-child', requirement_id=source['id'])
    stages = stage_map(stable(root))
    assert source['id'] in stages and 'guarded-child' in stages


def test_bound_source_command_keeps_explicit_delivery_and_rejects_sibling(context_database, tmp_path, monkeypatch):
    import pytest
    from app.chat import service as chat_service, relations
    from app.governance import scope, preparation
    from app.governance.reader import ProjectReader
    from app.governance.snapshot import stable
    from test_governance_scope import bind
    _, factory = context_database
    root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    source = issue(root, related_change='first')
    write(root / source['path'] / 'trace.md', '---\nstatus: in_sprint\nopenspec_changes:\n  - change_id: first\n  - change_id: second\n---\n')
    change(root, 'first', requirement_id=source['id']); change(root, 'second', requirement_id=source['id'])
    monkeypatch.setattr(preparation, '_object_session_snapshot', lambda db, actor, project: (ProjectReader(db,actor,project), stable(root)))
    with factory() as db:
        parent = chat_service.create_conversation(db,'alice','space','repo','交付目标验证')
        relations.set_relations(db,'alice',parent['id'],'first',[])
        assert preparation.bound_write_command(db,'alice',parent,'/opsx-apply '+source['id']) == ('opsx-apply','first')
        with pytest.raises(chat_service.ChatError) as error:
            preparation.bound_write_command(db,'alice',parent,'/opsx-apply second')
        assert error.value.kind == 'delivery_target_mismatch'
        with pytest.raises(chat_service.ChatError):
            preparation.bound_write_command(db,'alice',parent,'/opsx-apply REQ-0001-unrelated')


def test_bound_delivery_baseline_is_durable_and_cannot_retarget(context_database, tmp_path, monkeypatch):
    import pytest
    from app.chat import service as chat_service, relations
    from app.governance import preparation, store
    from app.governance.reader import ProjectReader
    from app.governance.snapshot import stable
    from test_governance_scope import bind
    _, factory = context_database
    root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    state = tmp_path / 'private'; state.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(state))
    source = issue(root, related_change='first')
    write(root / source['path'] / 'trace.md', '---\nstatus: in_sprint\nopenspec_changes:\n  - change_id: first\n  - change_id: second\n---\n')
    change(root,'first',requirement_id=source['id']);change(root,'second',requirement_id=source['id'])
    snapshot=stable(root)
    monkeypatch.setattr(preparation,'_object_session_snapshot',lambda db,actor,project:(ProjectReader(db,actor,project),snapshot))
    def baseline(db,actor,parent,oid,action):
        project=preparation.scope.authorize(db,actor,'space','repo',write=True)
        return project,{'id':oid},ProjectReader(db,actor,project),snapshot
    monkeypatch.setattr(preparation,'_send_baseline',baseline)
    with factory() as db:
        parent=chat_service.create_conversation(db,'alice','space','repo','固定交付测试')
        relations.set_relations(db,'alice',parent['id'],'first',[])
        prompt='/opsx-apply '+source['id']
        preparation.prepare_command_snapshot(db,'alice',parent,prompt,'fixed-request')
        saved=store.read(preparation._command_baseline_id(parent['id'],'fixed-request'),'baseline')
        assert saved['object_id']=='first' and saved['source_issue_id']==source['id']
        relations.set_relations(db,'alice',parent['id'],'second',[])
        with pytest.raises(chat_service.ChatError) as replay_error:
            preparation.assert_delivery_replay_identity(db,parent,{'prompt':prompt,'client_request_id':'fixed-request'})
        assert replay_error.value.kind == 'delivery_target_mismatch'
        with pytest.raises(chat_service.ChatError):
            preparation.prepare_command_snapshot(db,'alice',parent,prompt,'fixed-request')
        assert store.read(preparation._command_baseline_id(parent['id'],'fixed-request'),'baseline')==saved


def test_delivery_execution_permission_uses_bound_target_and_current_sprint(context_database, tmp_path, monkeypatch):
    from sqlalchemy import insert
    from app.chat import service as chat_service, relations, policy
    from app.chat.schema import turns
    from app.governance import preparation, store
    from test_governance_scope import bind
    _, factory = context_database
    root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    state=tmp_path/'state';state.mkdir(mode=0o700);monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(state))
    source=issue(root,related_change='first')
    write(root/source['path']/'trace.md','---\nstatus: in_sprint\nopenspec_changes:\n- change_id: first\n- change_id: second\n---\n')
    change(root,'first',requirement_id=source['id'],iteration='sprint-001')
    change(root,'second',requirement_id=source['id'],iteration='sprint-001')
    plan=dict(sprint_id='sprint-001',status='active',changes=['first','second'],requirements=[source['id']],bugs=[])
    write(root/'iterations/change/sprint-001/sprint.yaml',yaml.safe_dump(plan))
    with factory() as db:
        parent=chat_service.create_conversation(db,'alice','space','repo','权限验证')
        relations.set_relations(db,'alice',parent['id'],'first',[])
        prompt='/opsx-apply '+source['id'];tid=chat_service.identity()
        db.execute(insert(turns).values(**tid,conversation_id=parent['id'],client_request_id='permission-probe',status='queued',prompt=prompt,generation=0));db.commit()
        parent={**parent,'active_turn_id':tid['id']}
        store.write(preparation._command_baseline_id(parent['id'],'permission-probe'),'baseline',dict(action='opsx-apply',object_id='first',source_issue_id=source['id']))
        assert policy.write_policy(db,'alice',parent)['write_scope']=='implementation_write'
        assert policy.write_policy(db,'bob',parent)['write_scope']=='read_only'
        relations.set_relations(db,'alice',parent['id'],'second',[])
        assert policy.write_policy(db,'alice',parent)['write_scope']=='read_only'
        relations.set_relations(db,'alice',parent['id'],'first',[])
        plan['requirements']=[];write(root/'iterations/change/sprint-001/sprint.yaml',yaml.safe_dump(plan))
        assert policy.write_policy(db,'alice',parent)['write_scope']=='read_only'
