import copy
import json
from pathlib import Path
import pytest
import yaml
from sqlalchemy import func, insert, select, update
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import mysql
from app.chat import service, relations
from app.chat.schema import audit, conversations,governance_candidates,governance_applications,governance_project_locks,task_traces,turns,usage_events
from app.chat.workspace import git,prepare_workspace
from app.governance.candidates import validate
from app.governance.preparation import prepare, prepare_object_session, initialize_workspace, collect, check_send, execution_prompt_for_turn, prepare_command_snapshot
from app.governance import scope, store
from app.governance.snapshot import stable
from test_chat import chat
from test_governance_scope import bind,fixture_tree

OID='REQ-0099-local-check';BASE=f'issues/requirements/plan/{OID}'
BUG_OID='BUG-0099-local-check';BUG_BASE=f'issues/bugs/plan/{BUG_OID}'


def test_object_session_rejects_unknown_action_before_creating_conversation(chat):
    _, factory = chat
    with factory() as db:
        before = db.scalar(select(func.count()).select_from(conversations))
        with pytest.raises(service.ChatError) as error:
            prepare_object_session(db, 'alice', 'space', 'repo', OID, action='ac009-unknown-action')
        assert error.value.code == 2604
        assert db.scalar(select(func.count()).select_from(conversations)) == before


@pytest.mark.parametrize('action,oid,source_name',[
    ('req-generate',OID,'contents'),
    ('bug-generate',BUG_OID,'bug_contents'),
])
def test_object_session_generate_requires_capture_stage(chat,tmp_path,monkeypatch,action,oid,source_name):
    _,factory=chat;root=tmp_path/'repo';root.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,root)
    captured,draft=globals()[source_name]()
    for name,body in draft.items():
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(root,'init');git(root,'add','.');git(root,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','draft')
    with factory() as db:
        with pytest.raises(service.ChatError) as error:
            prepare_object_session(db,'alice','space','repo',oid,action=action,idempotency_key='draft')
        assert error.value.code==2604
        assert db.scalar(select(func.count()).select_from(conversations))==0
    for name,body in captured.items():
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    with factory() as db:
        prepared=prepare_object_session(db,'alice','space','repo',oid,action=action,idempotency_key='captured')
        assert prepared['object_id']==oid

def front(data,body='\n需求说明正文，包含本地验证目标与验收条件。\n'):
    if 'requirement_id' in data:
        data={**data, 'title':'本地需求业务主题'}
        body='# 本地需求业务主题\n'+body
    if 'bug_id' in data:
        data={**data, 'title':'本地缺陷业务主题'}
        body='# 本地缺陷业务主题\n'+body
    return ('---\n'+yaml.safe_dump(data,allow_unicode=True)+'---\n'+body).encode()


def contents():
    meta={'requirement_id':OID,'status':'captured','iteration':None,'openspec_changes':[], 'lifecycle':{'captured':'2026-09-11'}}
    files={f'{BASE}/capture.md':b'captured input',f'{BASE}/trace.md':front(meta),
      'issues/requirements/_registry.yaml':yaml.safe_dump({'next_id':100,'entries':[{'id':OID,'title':'本地需求业务主题','status':'captured','path':BASE}]}).encode(),
      'issues/bugs/_registry.yaml':b'entries: []\n',
      'issues/requirements/CHANGELOG.md':front({'purpose':'index','updated_at':'2026-09-11'},f'| {OID} | captured | {BASE} |\n')}
    result=copy.deepcopy(files);result[f'{BASE}/requirement.md']=front({'requirement_id':OID,'status':'draft'})
    meta['status']='draft';meta['lifecycle']['generated']='2026-09-11';result[f'{BASE}/trace.md']=front(meta)
    result['issues/requirements/_registry.yaml']=files['issues/requirements/_registry.yaml'].replace(b'captured',b'draft')
    result['issues/requirements/CHANGELOG.md']=files['issues/requirements/CHANGELOG.md'].replace(b'captured',b'draft')
    return files,result


def bug_contents():
    meta={'bug_id':BUG_OID,'status':'captured','iteration':None,'openspec_changes':[], 'lifecycle':{'captured':'2026-09-11'}}
    files={f'{BUG_BASE}/capture.md':b'captured bug input',f'{BUG_BASE}/trace.md':front(meta),
      'issues/bugs/_registry.yaml':yaml.safe_dump({'next_id':100,'entries':[{'id':BUG_OID,'title':'本地缺陷业务主题','status':'captured','path':BUG_BASE}]}).encode(),
      'issues/requirements/_registry.yaml':b'entries: []\n',
      'issues/bugs/CHANGELOG.md':front({'purpose':'index','updated_at':'2026-09-11'},f'| {BUG_OID} | captured | {BUG_BASE} | /bug-generate {BUG_OID} |\n')}
    result=copy.deepcopy(files);result[f'{BUG_BASE}/bug.md']=front({'bug_id':BUG_OID,'status':'draft'})
    meta['status']='draft';meta['lifecycle']['generated']='2026-09-11';result[f'{BUG_BASE}/trace.md']=front(meta)
    result['issues/bugs/_registry.yaml']=files['issues/bugs/_registry.yaml'].replace(b'captured',b'draft')
    result['issues/bugs/CHANGELOG.md']=files['issues/bugs/CHANGELOG.md'].replace(b'captured',b'draft').replace(b'/bug-generate',b'/bug-complete')
    return files,result


def test_fixed_write_set_and_semantic_rejection():
    before,after=contents();result=validate(before,after,OID,BASE)
    assert len(result['files'])==4 and result['manifest_hash']
    for name,body in [('src/evil.py',b'code'),('openspec/specs/live/spec.md',b'live'),('issues/bugs/_registry.yaml',b'entries: [other]')]:
        bad={**after,name:body}
        with pytest.raises(service.ChatError): validate(before,bad,OID,BASE)
    bad=copy.deepcopy(after);bad[f'{BASE}/trace.md']=bad[f'{BASE}/trace.md'].replace(b'iteration: null',b'iteration: sprint-999')
    with pytest.raises(service.ChatError): validate(before,bad,OID,BASE)
    bad=copy.deepcopy(after);bad['issues/requirements/CHANGELOG.md']+=b'\nother row changed'
    with pytest.raises(service.ChatError): validate(before,bad,OID,BASE)


@pytest.mark.parametrize('action',['req-generate','bug-generate'])
def test_generate_noop_validates_existing_draft(action):
    bug=action.startswith('bug-')
    _,after=bug_contents() if bug else contents()
    oid,base=(BUG_OID,BUG_BASE) if bug else (OID,BASE)
    assert validate(after,after,oid,base,action)['files']==[]
    after[f'{base}/trace.md']=after[f'{base}/trace.md'].replace(b'draft',b'captured')
    with pytest.raises(service.ChatError):validate(after,after,oid,base,action)


def test_req_generate_accepts_exploring_source_and_preserves_only_generation_write_set():
    before, after = contents()
    for name in (f'{BASE}/trace.md', 'issues/requirements/_registry.yaml'):
        before[name] = before[name].replace(b'status: captured', b'status: exploring')
    before['issues/requirements/CHANGELOG.md'] = before['issues/requirements/CHANGELOG.md'].replace(b'| captured |', b'| exploring |')
    result = validate(before, after, OID, BASE, 'req-generate')
    assert {item['path'] for item in result['files']} == {
        f'{BASE}/requirement.md', f'{BASE}/trace.md',
        'issues/requirements/_registry.yaml', 'issues/requirements/CHANGELOG.md',
    }


def test_bug_generate_keeps_captured_only_stage_gate():
    before, after = bug_contents()
    for name in (f'{BUG_BASE}/trace.md', 'issues/bugs/_registry.yaml'):
        before[name] = before[name].replace(b'status: captured', b'status: exploring')
    before['issues/bugs/CHANGELOG.md'] = before['issues/bugs/CHANGELOG.md'].replace(b'| captured |', b'| exploring |')
    with pytest.raises(service.ChatError):
        validate(before, after, BUG_OID, BUG_BASE, 'bug-generate')


def test_bug_generate_write_set_and_next_step_rejection():
    before,after=bug_contents();result=validate(before,after,BUG_OID,BUG_BASE,'bug-generate')
    assert len(result['files'])==4 and result['manifest_hash']
    for name,body in [('src/evil.py',b'code'),('issues/requirements/_registry.yaml',b'entries: [other]'),(f'{BUG_BASE}/root-cause.md',b'extra')]:
        bad={**after,name:body}
        with pytest.raises(service.ChatError): validate(before,bad,BUG_OID,BUG_BASE,'bug-generate')
    bad=copy.deepcopy(after);bad['issues/bugs/CHANGELOG.md']=bad['issues/bugs/CHANGELOG.md'].replace(b'/bug-complete',b'/bug-generate')
    with pytest.raises(service.ChatError): validate(before,bad,BUG_OID,BUG_BASE,'bug-generate')


@pytest.mark.parametrize("terminal", ["completed", "failed", "stopped"])
def test_prepare_isolated_uncommitted_and_success_candidate(chat,tmp_path,monkeypatch,terminal):
    _,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    before,after=contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    for name in ['AGENTS.md','openspec/project.md','.agents/skills/req-generate/SKILL.md','.agents/skills/workflow-sync/SKILL.md','scripts/sync-workflow-status.py','scripts/ai_usage.py','scripts/validate-document-titles.py','src/backend/app/governance/titles.py']:
        target=source/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('# Synthetic control file\n')
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','baseline')
    (source/f'{BASE}/capture.md').write_text('latest uncommitted governance input')
    workspaces=tmp_path/'workspaces';workspaces.mkdir()
    with factory() as db:
        prepared=prepare(db,'alice','space','repo',OID)
        assert db.scalar(select(turns.c.id)) is None
        cid=prepared['conversation_id'];parent=service.conversation(db,'alice',cid)
        path=prepare_workspace(source,workspaces,cid)["path"]
        from app.chat.policy import write_allowed
        assert not write_allowed(db,'alice',parent)
        initialize_workspace(db,parent,source,path)
        assert write_allowed(db,'alice',parent)
        assert (path/f'{BASE}/capture.md').read_text()=='latest uncommitted governance input'
        for name,body in after.items():
            if name.endswith('capture.md'):continue
            target=path/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
        applications=[]
        def fake_apply(db,actor,candidate_id,expected_manifest_hash,candidate_revision,idempotency_key,confirmed,request_id=None):
            candidate=db.execute(select(governance_candidates).where(governance_candidates.c.id==candidate_id)).mappings().one()
            app={**service.identity(),'actor_id':actor,'space_id':candidate['space_id'],'repository_id':candidate['repository_id'],
                 'scope_key':candidate['scope_key'],'idempotency_key':idempotency_key,'request_hash':'synthetic',
                 'candidate_id':candidate_id,'state':'pending','phase':'queued'}
            db.execute(insert(governance_applications).values(**app));applications.append(app)
            return {'id':app['id'],'state':'pending','phase':'queued'}
        monkeypatch.setattr('app.governance.writer.apply_candidate',fake_apply)
        turn=service.identity();db.execute(insert(turns).values(**turn,conversation_id=cid,client_request_id='test',status=terminal,prompt='synthetic'));db.commit()
        collect(db,parent,turn['id'],path,terminal)
        row=db.execute(select(governance_candidates)).mappings().one()
        assert row['state']=='pending'
        assert db.scalar(select(turns.c.status).where(turns.c.id==turn['id']))==terminal
        assert not (source/f'{BASE}/requirement.md').exists()
        if row['state']=='pending':
            assert store.read(row['id'],'result')['manifest_hash']==row['manifest_hash']
            assert applications and applications[0]['idempotency_key']==f"auto-{row['id']}"
            stored_app=db.execute(select(governance_applications).where(governance_applications.c.candidate_id==row['id'])).mappings().one()
            assert stored_app['state']=='pending'
        initialize_workspace(db,parent,source,path)


def test_mysql_schema_compiles_with_durable_identity():
    for table in (governance_candidates,governance_applications,governance_project_locks):
        statement=str(CreateTable(table).compile(dialect=mysql.dialect()))
        assert table.name in statement
    assert 'uq_governance_application_request' in str(CreateTable(governance_applications).compile(dialect=mysql.dialect()))


@pytest.mark.parametrize('invalid', ['missing', 'english', 'h1', 'registry'])
def test_title_gate_rejects_candidate_without_mutating_source(invalid):
    before, after = contents()
    original = copy.deepcopy(before)
    path = f'{BASE}/requirement.md'
    if invalid == 'missing':
        after[path] = after[path].replace('title: 本地需求业务主题\n'.encode(), b'')
    elif invalid == 'english':
        after[path] = after[path].replace('title: 本地需求业务主题'.encode(), b'title: English')
    elif invalid == 'h1':
        after[path] = after[path].replace('# 本地需求业务主题'.encode(), '# 其他业务标题'.encode())
    else:
        data = yaml.safe_load(after['issues/requirements/_registry.yaml'])
        data['entries'][0]['title'] = '其他业务标题'
        after['issues/requirements/_registry.yaml'] = yaml.safe_dump(data, allow_unicode=True).encode()
    with pytest.raises(service.ChatError):
        validate(before, after, OID, BASE)
    assert before == original


def test_candidate_accepts_business_title_change_with_registry_sync():
    before, after = contents()
    for name in (f'{BASE}/requirement.md', f'{BASE}/trace.md'):
        after[name] = after[name].replace('本地需求业务主题'.encode(), '更新后的业务标题'.encode())
    data = yaml.safe_load(after['issues/requirements/_registry.yaml'])
    data['entries'][0]['title'] = '更新后的业务标题'
    after['issues/requirements/_registry.yaml'] = yaml.safe_dump(data, allow_unicode=True).encode()
    assert validate(before, after, OID, BASE)['manifest_hash']


def test_prepare_bug_generate_uses_bug_action_and_prompt(chat,tmp_path,monkeypatch):
    _,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    before,_=bug_contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    for name in ['AGENTS.md','openspec/project.md','.agents/skills/bug-generate/SKILL.md','.agents/skills/workflow-sync/SKILL.md','scripts/sync-workflow-status.py','scripts/ai_usage.py','scripts/validate-document-titles.py','src/backend/app/governance/titles.py']:
        target=source/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('# Synthetic control file\n')
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','baseline')
    with factory() as db:
        prepared=prepare(db,'alice','space','repo',BUG_OID,action='bug-generate')
        row=db.execute(select(governance_candidates)).mappings().one()
        assert row['action']=='bug-generate'
        assert prepared['object_id']==BUG_OID
        assert prepared['prompt']==f'/bug-generate {BUG_OID}'
        assert '所有生成Markdown' not in prepared['prompt']
        assert execution_prompt_for_turn(db,service.conversation(db,'alice',prepared['conversation_id']),prepared['prompt']).startswith(f'/bug-generate {BUG_OID}\n所有生成Markdown')
        edited_prompt=f'/bug-generate {BUG_OID} 用户编辑后的补充说明'
        assert execution_prompt_for_turn(db,service.conversation(db,'alice',prepared['conversation_id']),edited_prompt)==edited_prompt


def test_prepare_reuses_latest_object_conversation_and_creates_new_candidate(chat,tmp_path,monkeypatch):
    _,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    monkeypatch.setattr('app.chat.isolated.allowed',lambda *args,**kwargs:True)
    before,_=contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','baseline')
    with factory() as db:
        first=prepare(db,'alice','space','repo',OID,idempotency_key='first')
        second=prepare(db,'alice','space','repo',OID,idempotency_key='second')
        assert second['conversation_id']==first['conversation_id']
        assert second['preparation_id']!=first['preparation_id']
        assert second['reused_conversation'] is True
        assert db.scalar(select(governance_candidates.c.id).where(governance_candidates.c.id==second['preparation_id']))==second['preparation_id']
        assert len(list(db.execute(select(governance_candidates))))==2
        parent=service.conversation(db,'alice',first['conversation_id'])
        assert check_send(db,'alice',parent)['id']==second['preparation_id']
        assert execution_prompt_for_turn(db,parent,second['prompt']).startswith(f'/req-generate {OID}\n所有生成Markdown')
        repeat=prepare(db,'alice','space','repo',OID,idempotency_key='second')
        assert repeat['preparation_id']==second['preparation_id']
        assert len(list(db.execute(select(governance_candidates))))==2


def test_applied_candidate_does_not_reactivate_older_unbound_preparation(chat,tmp_path,monkeypatch):
    _,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    before,_=contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','baseline')
    with factory() as db:
        old=prepare(db,'alice','space','repo',OID,idempotency_key='old')
        current=prepare(db,'alice','space','repo',OID,idempotency_key='current')
        db.execute(update(governance_candidates).where(governance_candidates.c.id==current['preparation_id']).values(state='applied'))
        db.commit()
        (source/'docs'/'later.md').parent.mkdir(exist_ok=True)
        (source/'docs'/'later.md').write_text('changed after the old preparation')
        parent=service.conversation(db,'alice',old['conversation_id'])
        assert check_send(db,'alice',parent) is None
        assert execution_prompt_for_turn(db,parent,f'/req-generate {OID}')==f'/req-generate {OID}'


def test_prepare_skips_archived_but_returns_active_object_conversation(chat,tmp_path,monkeypatch):
    _,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    before,_=contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','baseline')
    with factory() as db:
        archived=service.create_conversation(db,'alice','space','repo','archived')
        relations.set_relations(db,'alice',archived['id'],OID,[])
        db.execute(update(conversations).where(conversations.c.id==archived['id']).values(archived=1));db.commit()
        active=service.create_conversation(db,'alice','space','repo','active')
        relations.set_relations(db,'alice',active['id'],OID,[])
        tid=service.identity()
        db.execute(insert(turns).values(**tid,conversation_id=active['id'],client_request_id='active',status='queued',prompt='synthetic'))
        db.execute(update(conversations).where(conversations.c.id==active['id']).values(active_turn_id=tid['id']));db.commit()
        prepared=prepare(db,'alice','space','repo',OID,idempotency_key='fresh')
        assert prepared['conversation_id'] == active['id']
        assert prepared['reused_conversation'] is True
        assert prepared['can_send'] is False
        assert prepared['preparation_id'] is None


def test_prepare_object_session_supports_change_reuse(chat,tmp_path,monkeypatch):
    _,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    change='add-local-governance'
    trace=front({'change_id':change,'title':'本地治理变更','status':'proposed'},'# 本地治理变更\n\n变更追溯。')
    for name,body in {f'openspec/changes/{change}/trace.md':trace,'issues/requirements/_registry.yaml':b'entries: []\n','issues/bugs/_registry.yaml':b'entries: []\n'}.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','baseline')
    with factory() as db:
        first=prepare_object_session(db,'alice','space','repo',change,action='opsx-apply',idempotency_key='open')
        second=prepare_object_session(db,'alice','space','repo',change,action='opsx-apply',idempotency_key='again')
        assert first['object_type']=='CHANGE'
        assert first['title']=='本地治理变更'
        assert second['conversation_id']==first['conversation_id']
        assert second['reused_conversation'] is True


def test_change_id_write_session_rejects_read_only_issue_association(chat,tmp_path,monkeypatch):
    _,factory=chat;root=tmp_path/'repo';root.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,root)
    _,files=contents();change='isolated-read-only-association'
    files[f'openspec/changes/{change}/trace.md']=front({
        'change_id':change,'requirement_id':OID,'status':'proposed',
    })
    for name,body in files.items():
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(root,'init');git(root,'add','.');git(root,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','read-only-link')
    with factory() as db:
        with pytest.raises(service.ChatError) as error:
            prepare_object_session(db,'alice','space','repo',change,action='opsx-apply',idempotency_key='read-only')
        assert error.value.code==2601
        assert db.scalar(select(func.count()).select_from(conversations))==0
    trace=root/f'{BASE}/trace.md'
    trace.write_bytes(trace.read_bytes().replace(b'openspec_changes: []',f'openspec_changes:\n- change_id: {change}'.encode()))
    with factory() as db:
        prepared=prepare_object_session(db,'alice','space','repo',change,action='opsx-apply',idempotency_key='linked')
        assert prepared['object_id']==change


def test_write_object_session_allows_generated_uncommitted_fact_source(chat,tmp_path,monkeypatch):
    _,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    before,after=contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','captured')
    for name,body in after.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    with factory() as db:
        prepared=prepare_object_session(db,'alice','space','repo',OID,action='req-complete',idempotency_key='dirty')
        assert prepared['object_id']==OID


def test_write_object_session_rejects_invalid_fact_source(chat,tmp_path,monkeypatch):
    _,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    with factory() as db:
        with pytest.raises(service.ChatError) as error:
            prepare_object_session(db,'alice','space','repo',OID,action='req-complete',idempotency_key='no-git')
        assert error.value.kind=='source_invalid'
        assert db.scalar(select(conversations.c.id)) is None


@pytest.mark.parametrize('invalid', ['registry_path', 'trace_status', 'required_document'])
def test_write_object_session_checks_current_issue_facts_before_conversation(chat,tmp_path,monkeypatch,invalid):
    _,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    _,draft=contents()
    if invalid=='registry_path':
        draft['issues/requirements/_registry.yaml']=draft['issues/requirements/_registry.yaml'].replace(BASE.encode(),b'issues/requirements/plan/REQ-0099-other')
    elif invalid=='trace_status':
        draft[f'{BASE}/trace.md']=draft[f'{BASE}/trace.md'].replace(b'status: draft',b'status: captured')
    else:
        del draft[f'{BASE}/requirement.md']
    for name,body in draft.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','invalid')
    with factory() as db:
        with pytest.raises(service.ChatError) as error:
            prepare_object_session(db,'alice','space','repo',OID,action='req-complete',idempotency_key=invalid)
        assert error.value.kind=='governance_validation_failed'
        assert db.scalar(select(func.count()).select_from(conversations))==0
        assert db.scalar(select(func.count()).select_from(turns))==0


def test_projected_governance_root_uses_source_root_git_snapshot(chat,tmp_path,monkeypatch):
    _,factory=chat
    source=tmp_path/'source-repo';source.mkdir()
    projected=tmp_path/'governance-projection';projected.mkdir()
    private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{
        'id':'repo','space_id':'space','governance_root':str(projected),'source_root':str(source)
    }]))
    _,after=contents()
    for root in (source,projected):
        for name,body in after.items():
            path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','draft')
    with factory() as db:
        prepared=prepare_object_session(db,'alice','space','repo',OID,action='req-complete',idempotency_key='projected-clean')
        assert prepared['object_id']==OID
        assert prepared['action']=='req-complete'


def test_projected_governance_root_dirty_source_root_allows_matching_manifest(chat,tmp_path,monkeypatch):
    _,factory=chat
    source=tmp_path/'source-repo';source.mkdir()
    projected=tmp_path/'governance-projection';projected.mkdir()
    private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{
        'id':'repo','space_id':'space','governance_root':str(projected),'source_root':str(source)
    }]))
    before,after=contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','captured')
    for root in (source,projected):
        for name,body in after.items():
            path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    with factory() as db:
        prepared=prepare_object_session(db,'alice','space','repo',OID,action='req-complete',idempotency_key='projected-dirty')
        assert prepared['object_id']==OID


@pytest.mark.parametrize('sync_exit,stale_revision,stale_binding',[
    (0,False,False),(2,False,False),(0,True,False),(0,False,True),
])
@pytest.mark.parametrize('terminal',['completed','failed','stopped','unknown'])
def test_source_workspace_mode_generate_writes_directly_without_second_apply(chat,tmp_path,monkeypatch,sync_exit,stale_revision,stale_binding,terminal):
    _,factory=chat
    source=tmp_path/'source-repo';source.mkdir()
    private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{
        'id':'repo','space_id':'space','governance_root':str(source),'source_root':str(source),
        'workspace_root':str(tmp_path/'workspaces'),'workspace_mode':'source'
    }]))
    before,after=contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    for name in ['AGENTS.md','openspec/project.md','.agents/skills/req-generate/SKILL.md',
                 '.agents/skills/workflow-sync/SKILL.md','scripts/sync-workflow-status.py',
                 'scripts/ai_usage.py','scripts/validate-document-titles.py','src/backend/app/governance/titles.py']:
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('# control\n')
    (source/'scripts/sync-workflow-status.py').write_text(f'import sys\nsys.exit({sync_exit})\n')
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','captured')
    with factory() as db:
        prepared=prepare(db,'alice','space','repo',OID,idempotency_key='source-mode')
        parent=service.conversation(db,'alice',prepared['conversation_id'])
        initialize_workspace(db,parent,source,source)
        row=db.execute(select(governance_candidates)).mappings().one()
        assert row['state']=='running'
        for name,body in after.items():
            path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
        turn=service.identity()
        db.execute(insert(turns).values(**turn,conversation_id=parent['id'],client_request_id='source-mode',
            prompt=f'/req-generate {OID}',status=terminal))
        if stale_revision:
            db.execute(update(governance_candidates).where(governance_candidates.c.id==row['id']).values(revision=2))
            db.commit()
        if stale_binding:
            db.execute(update(governance_candidates).where(governance_candidates.c.id==row['id']).values(binding_revision='stale-binding'))
            db.commit()
        if terminal=='unknown':
            for notification in ('unknown','completed'):
                collect(db,parent,turn['id'],source,notification)
                assert db.scalar(select(governance_candidates.c.state))=='running'
                assert db.scalar(select(governance_applications.c.id)) is None
                for name,body in after.items():
                    assert (source/name).read_bytes()==body
            # A later authoritative completion may collect the same files;
            # neither notification above rolled back or claimed success.
            db.execute(update(turns).where(turns.c.id==turn['id']).values(status='completed'))
            terminal='completed'
        collect(db,parent,turn['id'],source,terminal)
        assert db.scalar(select(turns.c.status).where(turns.c.id==turn['id']))==terminal
        candidate=db.execute(select(governance_candidates)).mappings().one()
        accepted=sync_exit==0 and not stale_revision and not stale_binding
        assert candidate['state']==('applied' if accepted else 'rejected')
        if stale_binding or stale_revision:
            assert candidate['error_code']=='source_recovery_blocked'
            from app.governance import writer
            with pytest.raises(service.ChatError) as blocked:
                writer.assert_readable(db,scope.authorize(db,'alice','space','repo'))
            assert blocked.value.status==503
        application=db.execute(select(governance_applications)).mappings().first()
        if accepted:
            assert application['state']=='applied'
            assert application['phase']=='verified'
            proof=store.read(application['id'],'operation')['workflow_sync']
            assert proof['object_id']==OID
            assert proof['source_hash']==stable(source).revision
            from app.governance.execution_context import recover_source_proof
            from types import SimpleNamespace
            project=scope.authorize(db,'alice','space','repo')
            guard={'action':'req-generate','object_id':OID}
            assert recover_source_proof(project,guard,application,SimpleNamespace(files={}))=={}
            recovered=recover_source_proof(project,guard,application,stable(source))
            assert recovered['workflow_sync']==proof
        else:
            assert application is None
    current=stable(source).files
    if not accepted and not (stale_binding or stale_revision):
        assert f'{BASE}/requirement.md' not in current
    for name,body in (after if accepted or stale_binding or stale_revision else before).items():
        assert current[name]==body


def test_terminal_candidate_recovery_collects_once_without_restarting_turn(chat,tmp_path,monkeypatch):
    from app.governance.candidate_recovery import reconcile_terminal_candidates
    _,factory=chat
    source=tmp_path/'source-repo';source.mkdir()
    private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{
        'id':'repo','space_id':'space','governance_root':str(source),'source_root':str(source),
        'workspace_root':str(tmp_path/'workspaces'),'workspace_mode':'source'
    }]))
    before,after=contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    for name in ['AGENTS.md','openspec/project.md','.agents/skills/req-generate/SKILL.md',
                 '.agents/skills/workflow-sync/SKILL.md','scripts/sync-workflow-status.py',
                 'scripts/ai_usage.py','scripts/validate-document-titles.py','src/backend/app/governance/titles.py']:
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('# control\n')
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','captured')
    with factory() as db:
        prepared=prepare(db,'alice','space','repo',OID,idempotency_key='recovery-mode')
        parent=service.conversation(db,'alice',prepared['conversation_id'])
        initialize_workspace(db,parent,source,source)
        for name,body in after.items():
            path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
        turn=service.identity()
        db.execute(insert(turns).values(**turn,conversation_id=parent['id'],client_request_id='recovery-mode',
            prompt=f'/req-generate {OID}',status='completed'))
        db.execute(update(governance_candidates).where(governance_candidates.c.conversation_id==parent['id'])
            .values(prepared_turn_id=turn['id']))
        db.commit()
    resolve=lambda cid: (source,source)
    reconcile_terminal_candidates(factory,resolve)
    reconcile_terminal_candidates(factory,resolve)
    with factory() as db:
        assert db.scalar(select(governance_candidates.c.state))=='applied'
        assert db.scalar(select(func.count()).select_from(governance_applications))==1


def test_stopped_source_candidate_restores_partial_file_after_restart(chat,tmp_path,monkeypatch):
    from app.governance.candidate_recovery import reconcile_terminal_candidates
    _,factory=chat
    source=tmp_path/'source-repo';source.mkdir()
    private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{
        'id':'repo','space_id':'space','governance_root':str(source),'source_root':str(source),
        'workspace_root':str(tmp_path/'workspaces'),'workspace_mode':'source'
    }]))
    before,after=contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    for name in ['AGENTS.md','openspec/project.md','.agents/skills/req-generate/SKILL.md',
                 '.agents/skills/workflow-sync/SKILL.md','scripts/sync-workflow-status.py',
                 'scripts/ai_usage.py','scripts/validate-document-titles.py','src/backend/app/governance/titles.py']:
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('# control\n')
    baseline_files=stable(source).files
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','captured')
    with factory() as db:
        prepared=prepare(db,'alice','space','repo',OID,idempotency_key='partial-recovery')
        parent=service.conversation(db,'alice',prepared['conversation_id'])
        initialize_workspace(db,parent,source,source)
        turn=service.identity()
        db.execute(insert(turns).values(**turn,conversation_id=parent['id'],client_request_id='partial-recovery',
            prompt=f'/req-generate {OID}',status='stopped'))
        db.execute(update(governance_candidates).where(governance_candidates.c.conversation_id==parent['id'])
            .values(prepared_turn_id=turn['id']))
        db.commit()
    target=source/f'{BASE}/requirement.md';target.write_bytes(after[f'{BASE}/requirement.md'])
    reconcile_terminal_candidates(factory,lambda cid:(source,source))
    with factory() as db:
        assert db.scalar(select(governance_candidates.c.state))=='rejected'
        assert db.scalar(select(func.count()).select_from(governance_applications))==0
    assert not target.exists()
    assert stable(source).files==baseline_files


def test_source_workspace_rejected_candidate_restores_governance_facts(chat,tmp_path,monkeypatch):
    _,factory=chat
    source=tmp_path/'source-repo';source.mkdir()
    private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{
        'id':'repo','space_id':'space','governance_root':str(source),'source_root':str(source),
        'workspace_root':str(tmp_path/'workspaces'),'workspace_mode':'source'
    }]))
    before,after=contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','captured')
    with factory() as db:
        prepared=prepare(db,'alice','space','repo',OID,idempotency_key='source-reject')
        parent=service.conversation(db,'alice',prepared['conversation_id'])
        initialize_workspace(db,parent,source,source)
        for name,body in after.items():
            path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
        trace=source/f'{BASE}/trace.md'
        trace.write_bytes(trace.read_bytes().replace(b'status: draft',b'status: draft\nreadiness: invalid'))
        turn=service.identity()
        db.execute(insert(turns).values(**turn,conversation_id=parent['id'],client_request_id='source-reject',
            prompt=f'/req-generate {OID}',status='completed'))
        collect(db,parent,turn['id'],source,'completed')
        candidate=db.execute(select(governance_candidates)).mappings().one()
        assert candidate['state']=='rejected'
        assert candidate['error_code']=='governance_validation_failed'
        assert db.execute(select(governance_applications)).first() is None
    assert stable(source).files==before


def test_stopped_candidate_does_not_prepare_a_later_command(chat,tmp_path,monkeypatch):
    _,factory=chat
    source=tmp_path/'source';source.mkdir()
    private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{
        'id':'repo','space_id':'space','governance_root':str(source),'source_root':str(source),
        'workspace_root':str(tmp_path/'workspaces'),'workspace_mode':'source'
    }]))
    before,approved=contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','baseline')
    with factory() as db:
        prepared=prepare(db,'alice','space','repo',OID)
        parent=service.conversation(db,'alice',prepared['conversation_id'])
        old_turn=service.identity()
        db.execute(insert(turns).values(**old_turn,conversation_id=parent['id'],client_request_id='old',
            prompt=f'/req-generate {OID}',status='stopped'))
        db.execute(update(governance_candidates).where(governance_candidates.c.conversation_id==parent['id'])
            .values(state='running',prepared_turn_id=old_turn['id']))
        for name,body in approved.items():
            path=source/name;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(body.replace(b'draft',b'approved'))
        new_turn=service.identity()
        db.execute(insert(turns).values(**new_turn,conversation_id=parent['id'],client_request_id='new',
            prompt=f'/sprint-propose --req {OID}',status='connecting'))
        db.execute(update(conversations).where(conversations.c.id==parent['id']).values(active_turn_id=new_turn['id']))
        db.commit()
        parent=service.conversation(db,'alice',parent['id'])
        prepare_command_snapshot(db,'alice',parent,f'/sprint-propose --req {OID}','new')
        before_prepare=stable(source).revision
        initialize_workspace(db,parent,source,source)
        assert stable(source).revision==before_prepare
        assert db.scalar(select(governance_candidates.c.state))=='running'
        collect(db,parent,new_turn['id'],source,'failed')
        assert db.scalar(select(governance_candidates.c.state))=='running'


@pytest.mark.parametrize('action', [
    'req-complete','bug-complete','req-review','bug-review','sprint-propose','req-opsx','bug-opsx','opsx-apply','opsx-modify','opsx-archive',
])
def test_all_write_object_session_actions_allow_dirty_matching_facts(chat,tmp_path,monkeypatch,action):
    _,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    before,after=bug_contents() if action.startswith('bug-') else contents()
    oid=BUG_OID if action.startswith('bug-') else OID
    status=('draft' if action.endswith('complete') else 'pending_review' if action.endswith('review')
            else 'approved' if action=='sprint-propose' else 'in_sprint')
    after={name:body.replace(b'draft',status.encode()) for name,body in after.items()}
    if action in {'req-opsx','bug-opsx'}:
        after[f'{BUG_BASE if action.startswith("bug-") else BASE}/trace.md']=after[f'{BUG_BASE if action.startswith("bug-") else BASE}/trace.md'].replace(b'iteration: null',b'iteration: sprint-001')
        after['iterations/change/sprint-001/sprint.yaml']=yaml.safe_dump({
            'sprint_id':'sprint-001','status':'planning',
            'requirements':[OID] if action=='req-opsx' else [],
            'bugs':[BUG_OID] if action=='bug-opsx' else [],
        }).encode()
    if action in {'opsx-apply','opsx-modify','opsx-archive'}:
        change='isolated-governance-change'
        stage='proposed' if action=='opsx-apply' else 'applied'
        after[f'{BASE}/trace.md']=after[f'{BASE}/trace.md'].replace(
            b'openspec_changes: []',f'openspec_changes:\n- change_id: {change}\n  status: {stage}'.encode())
        after[f'openspec/changes/{change}/trace.md']=front({
            'change_id':change,'requirement_id':OID,'status':stage,
        })
        if action == 'opsx-archive':
            after[f'{BASE}/acceptance.md'] = front(
                {'acceptance_status': 'passed', 'manual_acceptance_status': 'accepted'},
                '\n- [x] AC-01 隔离测试夹具已验收\n')
            after[f'openspec/changes/{change}/verification.md'] = b'Isolated fixture verification passed.\n'
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','captured')
    for name,body in after.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    control=source/f'.agents/skills/{action}/SKILL.md';control.parent.mkdir(parents=True);control.write_text('current skill')
    review_controls = ['scripts/promote-issue-stage.py', 'scripts/sync-workflow-status.py',
        '.agents/skills/workflow-sync/SKILL.md', 'scripts/validate-document-titles.py',
        'src/backend/app/governance/titles.py', 'src/backend/app/governance/lifecycle.py',
        'scripts/workflow_sync/__init__.py'] if action.endswith('review') else []
    for name in review_controls:
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('current uncommitted control')
    document=source/'docs/unrelated.md';document.parent.mkdir();document.write_text('uncommitted unrelated document')
    (source/'.env').write_text('SYNTHETIC_NOT_FOR_EXECUTOR=1')
    workspaces=tmp_path/'workspaces';workspaces.mkdir()
    if action.endswith('review'):
        from app.governance.recovery_capabilities import publish
        publish('worker'); publish('controller')
    with factory() as db:
        prepared=prepare_object_session(db,'alice','space','repo',oid,action=action,idempotency_key=action)
        assert prepared['object_id']==oid
        parent=service.conversation(db,'alice',prepared['conversation_id'])
        prompt=f'/{action} '+('--req ' if action=='sprint-propose' else '')+oid
        prepare_command_snapshot(db,'alice',parent,prompt,'command')
        tid=service.identity()
        db.execute(insert(turns).values(**tid,conversation_id=parent['id'],client_request_id='command',prompt=prompt,status='connecting'))
        if action.endswith('review'):
            from app.governance.preparation import bind_prepared_turn
            bind_prepared_turn(db, parent['id'], tid['id'])
        db.execute(update(conversations).where(conversations.c.id==parent['id']).values(active_turn_id=tid['id']));db.commit()
        parent=service.conversation(db,'alice',parent['id'])
        workspace=prepare_workspace(source,workspaces,parent['id'])['path']
        initialize_workspace(db,parent,source,workspace)
        from app.governance.snapshot import stable
        assert stable(workspace).files==stable(source).files
        assert (workspace/f'.agents/skills/{action}/SKILL.md').read_text()=='current skill'
        for name in review_controls:
            assert (workspace/name).read_text() == 'current uncommitted control'
        assert not (workspace/'.env').exists()
        assert not git(workspace,'status','--porcelain').strip()


@pytest.mark.parametrize('conflict',['revision','workspace'])
def test_command_sync_preserves_conflicting_workspace(chat,tmp_path,monkeypatch,conflict):
    _,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    _,after=contents()
    for name,body in after.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    control=source/'.agents/skills/req-complete/SKILL.md';control.parent.mkdir(parents=True);control.write_text('skill')
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','baseline')
    workspaces=tmp_path/'workspaces';workspaces.mkdir()
    with factory() as db:
        prepared=prepare_object_session(db,'alice','space','repo',OID,action='req-complete')
        parent=service.conversation(db,'alice',prepared['conversation_id']);prompt=f'/req-complete {OID}'
        prepare_command_snapshot(db,'alice',parent,prompt,'conflict')
        tid=service.identity();db.execute(insert(turns).values(**tid,conversation_id=parent['id'],client_request_id='conflict',prompt=prompt,status='connecting'))
        db.execute(update(conversations).where(conversations.c.id==parent['id']).values(active_turn_id=tid['id']));db.commit()
        parent=service.conversation(db,'alice',parent['id'])
        workspace=prepare_workspace(source,workspaces,parent['id'])['path']
        target=(source if conflict=='revision' else workspace)/f'{BASE}/requirement.md'
        target.write_text('newer content')
        old=(workspace/f'{BASE}/requirement.md').read_bytes()
        with pytest.raises(service.ChatError): initialize_workspace(db,parent,source,workspace)
        assert (workspace/f'{BASE}/requirement.md').read_bytes()==old


def test_bug_generate_stale_preparation_is_diagnostic_and_new_candidate_can_resume(chat,tmp_path,monkeypatch):
    _,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    before,_=bug_contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','captured')
    with factory() as db:
        first=prepare(db,'alice','space','repo',BUG_OID,action='bug-generate',idempotency_key='first')
        parent=service.conversation(db,'alice',first['conversation_id'])
        unrelated=source/'docs/unrelated.md';unrelated.parent.mkdir();unrelated.write_text('changed after preparation')
        with pytest.raises(service.ChatError) as send_error:
            check_send(db,'alice',parent)
        assert send_error.value.code==2606 and send_error.value.kind=='workspace_fact_source_stale'
        with pytest.raises(service.ChatError) as error:
            initialize_workspace(db,parent,source,source)
        assert error.value.code==2606 and error.value.kind=='workspace_fact_source_stale'
        assert not (source/f'{BUG_BASE}/bug.md').exists()
        second=prepare(db,'alice','space','repo',BUG_OID,action='bug-generate',idempotency_key='second')
        assert second['preparation_id']!=first['preparation_id']
        initialize_workspace(db,parent,source,source)
        rows=db.execute(select(governance_candidates.c.id,governance_candidates.c.state)).all()
        assert dict(rows)[first['preparation_id']]=='prepared'
        assert dict(rows)[second['preparation_id']]=='running'


def test_read_only_object_session_allows_dirty_fact_source(chat,tmp_path,monkeypatch):
    _,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    before,after=contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','captured')
    for name,body in after.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    with factory() as db:
        prepared=prepare_object_session(db,'alice','space','repo',OID,action='req-explore',idempotency_key='explore')
        assert prepared['object_id']==OID
        assert prepared['action']=='req-explore'
        assert db.scalar(select(conversations.c.id))==prepared['conversation_id']


def test_write_object_session_rejects_missing_primary_document(chat,tmp_path,monkeypatch):
    _,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    _,after=contents()
    after.pop(f'{BASE}/requirement.md')
    for name,body in after.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','draft-without-document')
    with factory() as db:
        with pytest.raises(service.ChatError) as error:
            prepare_object_session(db,'alice','space','repo',OID,action='req-complete',idempotency_key='missing-doc')
        assert error.value.kind=='governance_validation_failed'
        assert 'requirement.md' in error.value.message


@pytest.mark.parametrize('action,oid,base,source',[
    ('req-opsx',OID,BASE,contents),
    ('bug-opsx',BUG_OID,BUG_BASE,bug_contents),
])
def test_opsx_session_requires_formal_sprint_scope(chat,tmp_path,monkeypatch,action,oid,base,source):
    _,factory=chat;root=tmp_path/'repo';root.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,root)
    _,files=source()
    files[f'{base}/trace.md']=files[f'{base}/trace.md'].replace(b'status: draft',b'status: in_sprint').replace(b'iteration: null',b'iteration: sprint-001')
    registry='issues/bugs/_registry.yaml' if action=='bug-opsx' else 'issues/requirements/_registry.yaml'
    files[registry]=files[registry].replace(b'status: draft',b'status: in_sprint')
    files['iterations/change/sprint-001/sprint.yaml']=yaml.safe_dump({
        'sprint_id':'sprint-001','requirements':[],'bugs':[],
    }).encode()
    for name,body in files.items():
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(root,'init');git(root,'add','.');git(root,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','scope')
    with factory() as db:
        with pytest.raises(service.ChatError) as error:
            prepare_object_session(db,'alice','space','repo',oid,action=action,idempotency_key='out-of-scope')
        assert error.value.code==2604 and error.value.kind=='governance_validation_failed'
        assert db.scalar(select(func.count()).select_from(conversations))==0
    scope_key='bugs' if action=='bug-opsx' else 'requirements'
    path=root/'iterations/change/sprint-001/sprint.yaml'
    path.write_text(yaml.safe_dump({'sprint_id':'sprint-001',scope_key:oid}))
    with factory() as db:
        with pytest.raises(service.ChatError):
            prepare_object_session(db,'alice','space','repo',oid,action=action,idempotency_key='malformed-scope')
    path.write_text(yaml.safe_dump({'sprint_id':'sprint-001','status':'closed',scope_key:[oid]}))
    with factory() as db:
        with pytest.raises(service.ChatError):
            prepare_object_session(db,'alice','space','repo',oid,action=action,idempotency_key='closed-sprint')
    path.write_text(yaml.safe_dump({'sprint_id':'sprint-001',scope_key:[oid]}))
    with factory() as db:
        prepared=prepare_object_session(db,'alice','space','repo',oid,action=action,idempotency_key='in-scope')
        assert prepared['object_id']==oid


def test_opsx_object_session_requires_linked_change_at_action_stage(chat,tmp_path,monkeypatch):
    _,factory=chat;root=tmp_path/'repo';root.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,root)
    _,files=contents()
    files[f'{BASE}/trace.md']=files[f'{BASE}/trace.md'].replace(b'status: draft',b'status: in_sprint')
    files['issues/requirements/_registry.yaml']=files['issues/requirements/_registry.yaml'].replace(b'status: draft',b'status: in_sprint')
    for name,body in files.items():
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(root,'init');git(root,'add','.');git(root,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','scope')
    with factory() as db:
        for action in ('opsx-apply','opsx-modify','opsx-archive'):
            with pytest.raises(service.ChatError) as error:
                prepare_object_session(db,'alice','space','repo',OID,action=action,idempotency_key='unlinked-'+action)
            assert error.value.code==2604
        assert db.scalar(select(func.count()).select_from(conversations))==0
    change='isolated-linked-change'
    trace=root/f'{BASE}/trace.md'
    trace.write_bytes(trace.read_bytes().replace(b'openspec_changes: []',f'openspec_changes:\n- change_id: {change}'.encode()))
    target=root/f'openspec/changes/{change}/trace.md';target.parent.mkdir(parents=True)
    target.write_bytes(front({'change_id':change,'requirement_id':OID,'status':'proposed'}))
    with factory() as db:
        with pytest.raises(service.ChatError) as error:
            prepare_object_session(db,'alice','space','repo',OID,action='opsx-archive',idempotency_key='unapplied')
        assert error.value.code==2604
        prepared=prepare_object_session(db,'alice','space','repo',OID,action='opsx-apply',idempotency_key='start')
        assert prepared['object_id']==OID
    target.write_bytes(front({'change_id':change,'requirement_id':OID,'status':'applied'}))
    # Applied alone is insufficient: retain the current archive evidence gate.
    with factory() as db:
        with pytest.raises(service.ChatError) as error:
            prepare_object_session(db,'alice','space','repo',OID,action='opsx-archive',idempotency_key='missing-evidence')
        assert error.value.code == 2604
    (root / BASE / 'acceptance.md').write_bytes(front(
        {'acceptance_status': 'passed', 'manual_acceptance_status': 'accepted'},
        '\n- [x] AC-01 隔离测试夹具已验收\n'))
    (target.parent / 'verification.md').write_text('Isolated fixture verification passed.\n')
    with factory() as db:
        prepared=prepare_object_session(db,'alice','space','repo',OID,action='opsx-archive',idempotency_key='archive-ready-stage')
        assert prepared['object_id']==OID


def test_write_object_session_accepts_clean_current_fact_source(chat,tmp_path,monkeypatch):
    _,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    _,after=contents()
    for name,body in after.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','draft')
    with factory() as db:
        prepared=prepare_object_session(db,'alice','space','repo',OID,action='req-complete',idempotency_key='clean')
        assert prepared['object_id']==OID
        assert prepared['object_type']=='REQ'
        assert prepared['action']=='req-complete'


def test_object_session_records_sanitized_observability(chat,tmp_path,monkeypatch):
    client,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    before,_=contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','baseline')
    response=client.post('/api/v1/chat/object-sessions',headers={'X-Chat-Client':'web'},json={
        'space_id':'space','repository_id':'repo','object_id':OID,'action':'req-explore','idempotency_key':'observe'})
    assert response.status_code==200,response.text
    data=response.json()['data']
    with factory() as db:
        event=db.execute(select(usage_events).where(usage_events.c.event_name=='governance.prepare')).mappings().one()
        props=json.loads(event['properties'])
        assert props['object_id']==OID
        assert props['object_type']=='REQ'
        assert props['action_type']=='req-explore'
        assert props['conversation_id']==data['conversation_id']
        assert 'prompt' not in props and 'content' not in props
        request_log=db.execute(select(audit).where(audit.c.route_template=='/api/v1/chat/object-sessions')).mappings().one()
        assert request_log['status_code']==200
        assert OID not in request_log['metadata']
        trace=db.execute(select(task_traces).where(task_traces.c.turn_id==f"governance:{data['conversation_id']}")).mappings().one()
        trace_meta=json.loads(trace['metadata'])
        assert trace_meta['object_id']==OID
        assert trace_meta['action_type']=='req-explore'


@pytest.mark.parametrize('kind', ['req', 'bug'])
def test_all_object_entries_share_busy_guard_and_trace(chat,tmp_path,monkeypatch,kind):
    client,factory=chat;source=tmp_path/'repo';source.mkdir()
    private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    before,_=contents() if kind=='req' else bug_contents()
    oid=OID if kind=='req' else BUG_OID
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','baseline')
    with factory() as db:
        parent=service.create_conversation(db,'alice','space','repo','busy fixture')
        relations.set_relations(db,'alice',parent['id'],oid,[])
        turn=service.identity()
        db.execute(insert(turns).values(**turn,conversation_id=parent['id'],client_request_id='busy',status='running',prompt='synthetic'))
        db.execute(update(conversations).where(conversations.c.id==parent['id']).values(active_turn_id=turn['id']))
        db.commit()
    actions=[f'{kind}-{name}' for name in ['explore','generate','complete','review','opsx']]+['sprint-propose','opsx-apply','opsx-modify','opsx-archive','open-chat']
    for action in actions:
        response=client.post('/api/v1/chat/object-sessions',json={'space_id':'space','repository_id':'repo','object_id':oid,'action':action,'idempotency_key':action})
        assert response.status_code==200,response.text
        data=response.json()['data']
        assert data['conversation_id']==parent['id'] and data['can_send'] is False
        assert data['execution_state']=='running'
        with factory() as db:
            trace=db.execute(select(task_traces).where(task_traces.c.parent_request_id==response.headers['X-Request-ID'])).mappings().one()
            meta=json.loads(trace['metadata'])
            assert meta['object_id']==oid and meta['action_type']==action
            assert meta['result']=='legacy_object_running'
            assert db.scalar(select(func.count()).select_from(turns))==1
            assert db.scalar(select(func.count()).select_from(usage_events))==0


def test_direct_api_has_no_web_behavior_and_pure_reads_add_no_task_trace(chat,tmp_path,monkeypatch):
    client,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    before,_=contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','baseline')
    with factory() as db:
        event_count=db.scalar(select(func.count()).select_from(usage_events))
        trace_count=db.scalar(select(func.count()).select_from(task_traces))
    response=client.post('/api/v1/chat/object-sessions',headers={'X-Request-ID':'client-forged-request-id'},json={
        'space_id':'space','repository_id':'repo','object_id':OID,'action':'req-explore',
        'idempotency_key':'direct-api-observation'})
    assert response.status_code==200,response.text
    assert response.headers['X-Request-ID']!='client-forged-request-id'
    conversation_id=response.json()['data']['conversation_id']
    with factory() as db:
        assert db.scalar(select(audit.c.id).where(audit.c.request_id==response.headers['X-Request-ID'])) is not None
        assert db.scalar(select(func.count()).select_from(usage_events))==event_count
        prepared_trace_count=db.scalar(select(func.count()).select_from(task_traces))
        assert prepared_trace_count==trace_count+1
    for _ in range(2):
        response=client.get(f'/api/v1/chat/conversations/{conversation_id}')
        assert response.status_code==200,response.text
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(usage_events))==event_count
        assert db.scalar(select(func.count()).select_from(task_traces))==prepared_trace_count


def test_object_session_stale_error_returns_safe_reason_details(chat,tmp_path,monkeypatch):
    client,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    before,after=contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','captured')
    for name,body in after.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    projected=tmp_path/'projection';projected.mkdir()
    for name,body in before.items():
        path=projected/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{
        'id':'repo','space_id':'space','governance_root':str(projected),'source_root':str(source)}]))
    response=client.post('/api/v1/chat/object-sessions',headers={'X-Chat-Client':'web'},json={
        'space_id':'space','repository_id':'repo','object_id':OID,'action':'req-complete','idempotency_key':'dirty-api'})
    assert response.status_code==409,response.text
    payload=response.json()
    assert payload['data']['kind']=='workspace_fact_source_stale'
    assert payload['data']['reason']=='manifest_mismatch'
    assert str(source) not in response.text
    assert OID not in response.text
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(conversations)) == 0
        assert db.scalar(select(func.count()).select_from(turns)) == 0
        request_log=db.execute(select(audit).where(audit.c.route_template=='/api/v1/chat/object-sessions')).mappings().one()
        assert request_log['status_code']==409
        assert OID not in request_log['metadata']


def test_preflight_marks_executor_unavailable_before_send(chat,tmp_path,monkeypatch):
    _,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    before,_=contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','baseline')
    monkeypatch.setattr('app.chat.isolated.allowed',lambda *args,**kwargs:False)
    with factory() as db:
        prepared=prepare(db,'alice','space','repo',OID)
        parent=service.conversation(db,'alice',prepared['conversation_id'])
        with pytest.raises(service.ChatError) as error:
            check_send(db,'alice',parent)
        assert error.value.kind=='executor_unavailable'
        row=db.execute(select(governance_candidates)).mappings().one()
        assert row['error_code']=='executor_unavailable'


def test_completion_rejection_exposes_only_fixed_rule_identifier():
    from app.governance.requirement_completion import validate_completion
    with pytest.raises(service.ChatError) as error:
        validate_completion({}, {}, OID, 'issues/requirements/plan/wrong')
    assert error.value.details == {'reason': 'identity'}
    assert error.value.kind == 'governance_validation_failed'
