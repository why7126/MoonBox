import json
from sqlalchemy import text
from test_chat import chat
from test_managed_worktree_git import repo


def test_main_workspace_api_is_authorized_and_path_free(chat, repo, monkeypatch):
    client, factory = chat
    source, managed = repo
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS', json.dumps([dict(id='repo', space_id='space',
        governance_root=str(source.root), source_root=str(source.root), workspace_root=str(managed), workspace_mode='source')]))
    payload = {'space_id': 'space', 'repository_id': 'repo'}
    response = client.post('/api/v1/chat/workspaces/main', json=payload)
    assert response.status_code == 200, response.text
    identifier = response.json()['data']['id']
    assert str(source.root) not in response.text
    assert client.post('/api/v1/chat/workspaces/main', json=payload).json()['data']['id'] == identifier
    listed = client.get('/api/v1/chat/workspaces', params=payload)
    assert listed.status_code == 200
    assert listed.json()['data']['can_create_development'] is False
    assert listed.json()['data']['items'][0]['id'] == identifier
    from app.moonbox_exec import workspace_operation
    from app.chat.service import ChatError
    import pytest
    with factory() as db:
        assert workspace_operation(db, 'alice', 'workspace.list', **payload) == listed.json()['data']['items']
    with factory.begin() as db:
        db.execute(text("UPDATE admin_spaces SET status='FROZEN' WHERE id='space'"))
    assert client.post('/api/v1/chat/workspaces/main', json=payload).status_code == 403
    with factory() as db:
        with pytest.raises(ChatError) as denied:
            workspace_operation(db, 'alice', 'workspace.register_main', **payload)
        assert denied.value.status == 403
    assert client.get('/api/v1/chat/workspaces', params=payload).status_code == 200
    assert client.get('/api/v1/chat/workspaces', params={**payload, 'space_id': 'foreign'}).status_code == 403


def test_real_authority_development_reuse_and_shared_fact_protection(chat, repo, monkeypatch):
    from pathlib import Path
    from workspace_live_fixture import seed_project
    from test_managed_worktree_git import git
    from app.moonbox_exec_server import validation
    from app.moonbox_core.integration_schema import candidates
    from sqlalchemy import select
    client, factory = chat
    source, managed = repo
    seed_project(source.root)
    state = managed/'state'; state.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(state))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS', json.dumps([dict(id='repo', space_id='space',
        governance_root=str(source.root), source_root=str(source.root), workspace_root=str(managed), workspace_mode='source')]))
    class TestValidator:
        def capability(self): return {'available': True}
        def validate(self, **request):
            return dict(status='passed', candidate_id=request['candidate_id'], candidate_commit=request['candidate_commit'],
                environment_key='synthetic-api-test',runtime_digest='sha256:'+'a'*64,evidence_digest='b'*64)
    monkeypatch.setattr(validation, 'provider', TestValidator)
    payload = dict(space_id='space',repository_id='repo',change_id='example-change')
    response = client.post('/api/v1/chat/workspaces/development',json=payload)
    assert response.status_code == 200, response.text
    wid = response.json()['data']['id']
    assert client.post('/api/v1/chat/workspaces/development',json=payload).json()['data']['id'] == wid
    from app.moonbox_core.schema import workspaces
    with factory() as db:
        root = Path(db.scalar(select(workspaces.c.root_locator).where(workspaces.c.id == wid)))
    (root/'src/code.txt').write_text('API synthetic result')
    git(root,'add','src/code.txt'); git(root,'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','implementation')
    scope = dict(space_id='space',repository_id='repo')
    candidate = client.post('/api/v1/chat/workspaces/merge-candidates',json={**scope,'workspace_id':wid,'request_id':'prepare'},headers={'X-Chat-Client':'web','X-Request-ID':'untrusted-client-id'})
    assert candidate.status_code == 200, candidate.text
    value = candidate.json()['data']
    assert value['state'] == 'validated'
    from app.chat.schema import task_traces, usage_events
    with factory() as db:
        trace = db.execute(select(task_traces).where(task_traces.c.turn_id==value['id'])).mappings().one()
        assert trace['parent_request_id'] == candidate.headers['X-Request-ID']
        assert trace['parent_request_id'] != 'untrusted-client-id'
        event = db.execute(select(usage_events).where(usage_events.c.parent_request_id==trace['parent_request_id'])).mappings().one()
        assert json.loads(event['properties'])['operation_id']==value['id']
        assert event['event_name']=='workspace.action'
    denied = client.post('/api/v1/chat/workspaces/merge-candidates/'+value['id']+'/confirm',json={**scope,'fingerprint':'0'*64,'request_id':'wrong'})
    assert denied.status_code == 409
    confirmed = client.post('/api/v1/chat/workspaces/merge-candidates/'+value['id']+'/confirm',json={**scope,'fingerprint':value['fingerprint'],'request_id':'confirm'})
    assert confirmed.status_code == 200, confirmed.text
    assert confirmed.json()['data']['governance_state'] == 'completed'
    assert 'workspace_integration' in (source.root/'issues/requirements/_registry.yaml').read_text()
    assert source.head() == value['candidate_commit']
    # A second Change in the same REQ reuses the integrated tree after formal facts are committed.
    import yaml
    next_change = source.root/'openspec/changes/next-change'; next_change.mkdir()
    (next_change/'trace.md').write_text('---\n' + yaml.safe_dump(dict(status='in_progress',iteration='sprint-015',requirement_id='REQ-0042-example')) + '---\n')
    issue_trace = source.root/'issues/requirements/review/REQ-0042-example/trace.md'
    issue_trace.write_text('---\n' + yaml.safe_dump(dict(status='in_sprint',iteration='sprint-015',openspec_changes=['example-change','next-change'])) + '---\n')
    sprint = source.root/'iterations/change/sprint-015/sprint.yaml'
    sprint.write_text(yaml.safe_dump(dict(sprint_id='sprint-015',status='active',requirements=['REQ-0042-example'],changes=['example-change','next-change'])))
    git(source.root,'add','.'); git(source.root,'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','formal next change')
    reused = client.post('/api/v1/chat/workspaces/development',json={**payload,'change_id':'next-change'})
    assert reused.status_code == 200, reused.text
    assert reused.json()['data']['id'] == wid
    assert git(root,'rev-parse','HEAD') == source.head()
    busy = client.post('/api/v1/chat/workspaces/development',json=payload)
    assert busy.status_code == 409
