"""Action-scoped proof regression; unrelated edits are distinct from conflicts."""
import copy
import pytest
import yaml
from app.governance.direct_completion import manifest, verify, DirectProofError

OID = 'BUG-9001-sample'
BASE = f'issues/bugs/review/{OID}'
CHANGE = 'fix-sample'


def md(**data):
    return ('---\n' + yaml.safe_dump(data) + '---\n\n# 文档\n\n## 验证记录\n\n初始记录\n').encode()


def files():
    return {
        'issues/bugs/_registry.yaml': yaml.safe_dump({'entries':[{'id':OID,'path':BASE,'status':'in_sprint'}]}).encode(),
        'issues/requirements/_registry.yaml': b'entries: []',
        BASE+'/bug.md':md(status='in_sprint',title='测试'),
        BASE+'/trace.md':md(status='in_sprint',iteration='sprint-012',openspec_changes=[{'change_id':CHANGE}]),
        f'openspec/changes/{CHANGE}/trace.md':md(status='proposed',iteration='sprint-012'),
        f'openspec/changes/{CHANGE}/proposal.md':b'proposal',
        f'openspec/changes/{CHANGE}/design.md':b'design',
        f'openspec/changes/{CHANGE}/tasks.md':b'- [ ] task',
        'iterations/change/sprint-012/sprint.yaml':yaml.safe_dump(dict(sprint_id='sprint-012',status='planning',bugs=[OID],requirements=[],changes=[CHANGE],scope_estimates=[dict(id=OID,estimated_person_days=8)],capacity_person_days=30)).encode(),
        'rules/security.md':b'permission checks',
    }


def record(fs):
    return dict(schema_version=1,object_id=OID,action='bug-opsx',steps=[dict(sync_succeeded=True,completion_manifest=manifest(fs,OID,'bug-opsx'))])


def test_unrelated_concurrent_object_does_not_invalidate_proof():
    fs=files(); before=record(fs)
    fs['issues/bugs/plan/BUG-9002-other/bug.md']=b'unrelated'
    registry=yaml.safe_load(fs['issues/bugs/_registry.yaml']);registry['entries'].append(dict(id='BUG-9002-other',path='issues/bugs/plan/BUG-9002-other',status='draft'))
    fs['issues/bugs/_registry.yaml']=yaml.safe_dump(registry).encode()
    assert verify(before,fs,OID,'bug-opsx')


def test_trace_verification_appendix_can_finalize_without_resync():
    fs=files(); before=record(fs)
    fs[BASE+'/trace.md']+=b'additional validation log\n'
    assert verify(before,fs,OID,'bug-opsx')


@pytest.mark.parametrize('path', ['rules/security.md',f'openspec/changes/{CHANGE}/tasks.md',BASE+'/bug.md'])
def test_related_content_conflict_stays_blocked(path):
    fs=files(); before=record(fs);fs[path]+=b'changed'
    with pytest.raises(DirectProofError):verify(before,fs,OID,'bug-opsx')


def test_capacity_and_duplicate_global_identity_stay_gates():
    fs=files();before=record(fs)
    registry=yaml.safe_load(fs['issues/bugs/_registry.yaml']);registry['entries']*=2
    fs['issues/bugs/_registry.yaml']=yaml.safe_dump(registry).encode()
    with pytest.raises(DirectProofError):verify(before,fs,OID,'bug-opsx')
    fs=files();plan=yaml.safe_load(fs['iterations/change/sprint-012/sprint.yaml']);plan['scope_estimates'].append(dict(id='other',estimated_person_days=40))
    fs['iterations/change/sprint-012/sprint.yaml']=yaml.safe_dump(plan).encode()
    with pytest.raises(DirectProofError):verify(before,fs,OID,'bug-opsx')


@pytest.mark.parametrize('steps,reason', [([], 'direct_sync_missing'),([dict(sync_succeeded=True)],'direct_historical_evidence_missing'),([dict(sync_succeeded=True,completion_manifest={})],'direct_proof_invalid')])
def test_exit_zero_or_missing_manifest_is_not_proof(steps,reason):
    r=record(files());r['steps']=steps
    with pytest.raises(DirectProofError,match=reason):verify(r,files(),OID,'bug-opsx')


def test_proof_does_not_contain_source_content():
    proof=manifest(files(),OID,'bug-opsx')
    assert 'permission checks' not in str(proof)

from test_chat import chat
from test_governance_writer import writing


@pytest.fixture
def direct_scene(writing, chat):
    from app.chat import service
    from app.chat.schema import turns
    from sqlalchemy import insert
    from app.governance import store, execution_guard as guards
    from app.governance.direct_command_journal import prepare, observe, record_id, terminal
    from app.governance.snapshot import digest
    factory, project, _, _, _ = writing
    for p in project.root.rglob('*'):
        if p.is_file():p.unlink()
    fs=files()
    for n,b in fs.items():
        p=project.root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    with factory() as db:
        parent=service.create_conversation(db,'alice','space','repo','proof')
        turn=service.identity()
        db.execute(insert(turns).values(**turn,conversation_id=parent['id'],client_request_id='proof',prompt='/bug-opsx '+OID,status='completed'))
        row=guards.acquire(db,scope_key=project.key,object_id=OID,operation_id=turn['id'],conversation_id=parent['id'],owner_id='alice',action='bug-opsx',confirmed_stage='sprint-planning',baseline_revision=digest(fs))
        guards.terminal(db,turn['id'],'completed');db.commit()
    rid=record_id(parent['id'],'proof')
    store.write(rid,'baseline',dict(action='bug-opsx',object_id=OID,revision=digest(fs),binding_revision=project.binding_revision,files={n:b.decode() for n,b in fs.items()}))
    prepare(parent['id'],'proof','bug-opsx',OID,digest(fs))
    observe(parent['id'],'proof','sync','completed',project.root,sync=True,sync_succeeded=True)
    terminal(parent['id'],'proof','completed',project.root)
    return factory,project,turn['id'],rid,row['version']


def test_http_recovery_is_idempotent_and_keeps_history(direct_scene,chat):
    from app.governance import store
    factory,project,tid,rid,version=direct_scene;client,_=chat
    before=store.read(rid,'operation')['steps']
    url=f'/api/v1/chat/turns/{tid}/completion-verification'
    assert client.get(url).json()['data']['can_verify']
    for _ in range(2):
        response=client.post(url,json={'expected_version':version})
        assert response.status_code==200,response.text
        assert response.json()['data']['state']=='recovered_valid'
    assert store.read(rid,'operation')['steps']==before


@pytest.mark.parametrize('related_change', [False, True])
def test_history_remains_readable_after_current_guard_advances(direct_scene, chat, related_change):
    from sqlalchemy import update
    from app.governance import store, execution_guard as guards
    factory, project, tid, rid, version = direct_scene
    client, _ = chat
    url = f'/api/v1/chat/turns/{tid}/completion-verification'
    assert client.post(url, json={'expected_version': version}).status_code == 200
    original = store.read(rid, 'operation')
    with factory() as db:
        db.execute(update(guards.execution_guards).where(
            guards.execution_guards.c.operation_id == tid).values(
                operation_id=None, owner_id=None, conversation_id=None,
                action='external-sync', state='idle', version=version + 1))
        db.commit()
    if related_change:
        (project.root / f'openspec/changes/{CHANGE}/tasks.md').write_text('later delivery')
    response = client.get(url)
    assert response.status_code == 200, response.text
    result = response.json()['data']
    assert result['reason_code'] == ('direct_historical_record_preserved' if related_change else 'direct_historical_verified')
    assert not result['can_verify'] and result['version'] is None
    assert client.post(url, json={'expected_version': version}).status_code == 404
    assert store.read(rid, 'operation') == original
    with factory() as db:
        assert guards.read(db, project.key, OID)['state'] == 'idle'


@pytest.mark.parametrize('mode',['related','version','missing_sync','legacy','permission','race'])
def test_actual_verification_endpoint_safety(direct_scene,chat,monkeypatch,mode):
    from app.governance import store
    from sqlalchemy import text
    factory,project,tid,rid,version=direct_scene;client,_=chat
    if mode=='related':(project.root/f'openspec/changes/{CHANGE}/tasks.md').write_text('changed')
    if mode=='version':version+=1
    if mode in ('missing_sync','legacy'):
        r=store.read(rid,'operation')
        if mode=='missing_sync':r['steps']=[]
        else:
            for step in r['steps']:step.pop('completion_manifest',None)
        store.write(rid,'operation',r)
    if mode=='permission':
        with factory() as db:db.execute(text("UPDATE admin_spaces SET status='FROZEN'"));db.commit()
    if mode=='race':
        original=store.write
        def concurrent(rid,name,value):
            original(rid,name,value)
            if value.get('final_verification'):
                (project.root/f'openspec/changes/{CHANGE}/tasks.md').write_text('race')
        monkeypatch.setattr(store,'write',concurrent)
    response=client.post(f'/api/v1/chat/turns/{tid}/completion-verification',json={'expected_version':version})
    assert response.status_code==(200 if mode=='legacy' else 403 if mode=='permission' else 409),response.text
    if mode=='legacy':
        assert store.read(rid,'operation')['final_verification']['historical_attribution']=='unknown'
        assert all('completion_manifest' not in s for s in store.read(rid,'operation')['steps'])


def test_automatic_reconcile_after_unrelated_edit(direct_scene):
    from app.governance.execution_context import reconcile
    from app.governance.execution_guard import read
    from app.governance import store
    factory,project,tid,rid,version=direct_scene
    # Simulate a changed write set before sync; avoid the legacy no-write path.
    record=store.read(rid,'operation');record['classification']='sync_completed_unverified';store.write(rid,'operation',record)
    p=project.root/'docs/unrelated.md';p.parent.mkdir(exist_ok=True);p.write_text('other task')
    with factory() as db:
        reconcile(db,'alice',project,operation_id=tid)
        assert read(db,project.key,OID)['state']=='validated'
        db.commit()


@pytest.mark.parametrize('action',['req-generate','bug-generate','req-complete','bug-complete','req-review','bug-review','sprint-propose','req-opsx','bug-opsx','opsx-apply','opsx-modify','opsx-archive'])
def test_action_contract_requires_business_result_not_just_sync(action):
    fs=files();r=record(fs);r['action']=action
    r['steps'][0]['sync_result']=dict(event=action.replace('-', '.', 1),mode='write',ok=True,object_id=OID)
    r['steps'][0]['completion_manifest']=manifest(fs,OID,action)
    if action in ('bug-opsx','sprint-propose'):
        assert verify(r,fs,OID,action)
    else:
        with pytest.raises(DirectProofError,match='direct_result_invalid'):verify(r,fs,OID,action)


@pytest.mark.parametrize('action',['req-generate','bug-generate','req-complete','bug-complete','req-review','bug-review','sprint-propose','req-opsx','bug-opsx','opsx-apply','opsx-modify','opsx-archive'])
def test_each_supported_action_has_valid_and_invalid_output(action):
    fs=files();oid=OID;base=BASE
    if action.startswith('req-'):
        oid=OID.replace('BUG-','REQ-');base=BASE.replace('/bugs/','/requirements/').replace(OID,oid)
        fs={n.replace('/bugs/','/requirements/').replace(OID,oid):b.replace(OID.encode(),oid.encode()).replace(b'issues/bugs/',b'issues/requirements/') for n,b in fs.items() if not n.startswith('issues/requirements/')}
        fs[base+'/requirement.md']=fs.pop(base+'/bug.md')
        fs['issues/bugs/_registry.yaml']=b'entries: []'
        pn='iterations/change/sprint-012/sprint.yaml';plan=yaml.safe_load(fs[pn]);plan['requirements']=plan.pop('bugs');plan['bugs']=[];fs[pn]=yaml.safe_dump(plan).encode()
    state='draft' if action.endswith('generate') else 'pending_review' if action.endswith('complete') else 'approved' if action.endswith('review') else 'done' if action=='opsx-archive' else 'in_sprint'
    registry='issues/requirements/_registry.yaml' if oid.startswith('REQ') else 'issues/bugs/_registry.yaml'
    reg=yaml.safe_load(fs[registry]);reg['entries'][0]['status']=state
    for n in (base+'/trace.md',base+('/requirement.md' if oid.startswith('REQ') else '/bug.md')):
        parts=fs[n].decode().split('---',2);fm=yaml.safe_load(parts[1]);fm['status']=state
        if action.endswith(('generate','complete','review')):fm['openspec_changes']=[];fm['iteration']=None
        fs[n]=('---\n'+yaml.safe_dump(fm)+'---'+parts[2]).encode()
    for n in ['business-flow.md','user-stories.md','root-cause.md','workaround.md','acceptance.md','review.md']:fs[base+'/'+n]=b'valid required document'
    if action in ('opsx-apply','opsx-modify'):
        fs[f'openspec/changes/{CHANGE}/trace.md']=md(status='applied',iteration='sprint-012',execution={'completed_at':'2026-10-21T01:00:00Z'})
        fs[f'openspec/changes/{CHANGE}/tasks.md']=b'- [x] done'
    if action=='opsx-archive':
        fs={n.replace('openspec/changes/'+CHANGE,'openspec/archive/2026-10-21-'+CHANGE):b for n,b in fs.items()}
    fs[registry]=yaml.safe_dump(reg).encode()
    r=dict(schema_version=1,action=action,object_id=oid,steps=[dict(sync_succeeded=True,completion_manifest=manifest(fs,oid,action))])
    r['steps'][0]['sync_result']=dict(event=action.replace('-', '.', 1),mode='write',ok=True,object_id=oid)
    assert verify(r,fs,oid,action)
    del fs[base+('/requirement.md' if oid.startswith('REQ') else '/bug.md')]
    with pytest.raises(DirectProofError):verify(r,fs,oid,action)


def test_direct_handoff_resumes_without_browser_and_is_idempotent(direct_scene):
    from app.governance import store
    from app.governance.completion_handoff import tick, handoffs
    from app.governance.execution_guard import read
    from sqlalchemy import select
    factory,project,tid,rid,version=direct_scene
    record=store.read(rid,'operation');record['classification']='sync_completed_unverified';store.write(rid,'operation',record)
    p=project.root/'docs/unrelated.md';p.parent.mkdir(exist_ok=True);p.write_text('other task')
    tick(factory)
    tick(factory)
    with factory() as db:
        assert read(db,project.key,OID)['state']=='validated'
        jobs=db.execute(select(handoffs).where(handoffs.c.operation_id==tid)).mappings().all()
        assert len(jobs)==1
        assert jobs[0]['state']=='confirmed'
        assert jobs[0]['attempt_count']==1


def test_historical_recovery_blocks_new_protected_input(direct_scene,chat):
    from app.governance import store
    factory,project,tid,rid,version=direct_scene;client,_=chat
    record=store.read(rid,'operation')
    for step in record['steps']:step.pop('completion_manifest',None)
    store.write(rid,'operation',record)
    (project.root/'rules/new-policy.md').write_text('new mandatory constraint')
    response=client.post(f'/api/v1/chat/turns/{tid}/completion-verification',json={'expected_version':version})
    assert response.status_code==409
    assert response.json()['data']['kind']=='direct_dependency_conflict'


@pytest.mark.parametrize('action', ['req-review','bug-review','opsx-archive'])
def test_generic_recovery_never_replaces_specialized_gates(direct_scene,chat,action):
    from app.governance import store
    from app.governance.execution_guard import execution_guards
    from sqlalchemy import update
    factory,project,tid,rid,version=direct_scene;client,_=chat
    record=store.read(rid,'operation');record['action']=action
    baseline=store.read(rid,'baseline');baseline['action']=action
    store.write(rid,'operation',record);store.write(rid,'baseline',baseline)
    with factory() as db:
        db.execute(update(execution_guards).where(execution_guards.c.operation_id==tid).values(action=action));db.commit()
    response=client.post(f'/api/v1/chat/turns/{tid}/completion-verification',json={'expected_version':version})
    assert response.status_code==409
    assert response.json()['data']['kind']=='direct_specialized_verification_required'


def test_file_difference_classification_contains_no_bodies():
    from app.governance.direct_completion import differences
    result=differences({'files':{'keep':'1','remove':'2','edit':'3'}},{'files':{'keep':'1','add':'4','edit':'5'}})
    assert result==[{'path':'add','kind':'added'},{'path':'edit','kind':'modified'},{'path':'remove','kind':'deleted'}]


def test_failed_sync_is_not_mislabeled_as_historical_missing(direct_scene,chat):
    from app.governance import store
    _,_,tid,rid,_=direct_scene;client,_=chat
    record=store.read(rid,'operation');record['steps']=[];store.write(rid,'operation',record)
    data=client.get(f'/api/v1/chat/turns/{tid}/completion-verification').json()['data']
    assert data['reason_code']=='direct_sync_missing'
    assert not data['historical_evidence_missing']
    assert not data['can_verify']


def test_unknown_operation_proof_version_fails_closed(direct_scene,chat):
    from app.governance import store
    _,_,tid,rid,version=direct_scene;client,_=chat
    record=store.read(rid,'operation');record['proof_schema_version']=2;store.write(rid,'operation',record)
    response=client.post(f'/api/v1/chat/turns/{tid}/completion-verification',json={'expected_version':version})
    assert response.status_code==409
    assert response.json()['data']['kind']=='direct_proof_invalid'
