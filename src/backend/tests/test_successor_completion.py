"""Prove failed observations cannot masquerade as formal completion."""
import json
import pytest
from app.governance.direct_command_journal import is_formal_workflow_sync, workflow_sync_result

@pytest.mark.parametrize('suffix', ['--dry-run;', '--check;', '--dry-run\n', '--dry-run=true;', '--check &&'])
def test_compound_probes_never_count(suffix):
    assert not is_formal_workflow_sync(dict(type='commandExecution', command='python scripts/sync-workflow-status.py --event opsx.apply '+suffix+' true'))


def test_quoted_reference_not_command():
    assert not is_formal_workflow_sync(dict(type='commandExecution',command="echo 'python scripts/sync-workflow-status.py --event opsx.apply'"))

@pytest.mark.parametrize('ok,mode,expected', [(False,'write',False),(True,'dry-run',False),(True,'check',False),(True,'write',True)])
def test_shell_success_does_not_override_structured_result(ok,mode,expected):
    row=dict(schema_version=1,event='opsx.apply',ok=ok,mode=mode)
    item=dict(type='commandExecution',command='python scripts/sync-workflow-status.py --event opsx.apply; true',exitCode=0,status='completed',aggregatedOutput='MOONBOX_WORKFLOW_RESULT:'+json.dumps(row))
    assert bool(workflow_sync_result(item)) == expected
    item['aggregatedOutput']='arbitrary success text'
    assert workflow_sync_result(item) is None


def test_progress_is_not_completion_proof():
    from test_direct_completion import files, record, OID
    from app.governance.direct_completion import verify, DirectProofError
    fs=files();r=record(fs);r['steps'][-1]['sync_result']=dict(event='opsx.progress',ok=True,mode='write')
    with pytest.raises(DirectProofError,match='direct_completion_event_missing'):
        verify(r,fs,OID,'bug-opsx')

from test_chat import chat
from test_governance_writer import writing
from test_direct_completion import direct_scene, OID, BASE, CHANGE, md

@pytest.fixture
def successor_scene(direct_scene):
    from sqlalchemy import update
    from app.governance import store, execution_guard as guards
    from app.governance.direct_completion import manifest
    from app.governance.snapshot import stable
    from app.governance.acceptance_evidence import fingerprint
    from app.governance.workflow_receipt import emit
    factory,project,tid,rid,version=direct_scene
    record=store.read(rid,'operation');baseline=store.read(rid,'baseline')
    record['action']=baseline['action']='opsx-apply'
    record['steps'][-1]['completion_manifest']=manifest(stable(project.root).files,OID,'opsx-apply')
    record['steps'][-1]['sync_result']=dict(event='opsx.progress',mode='write',ok=True)
    store.write(rid,'operation',record);store.write(rid,'baseline',baseline)
    with factory() as db:
        db.execute(update(guards.execution_guards).where(guards.execution_guards.c.operation_id==tid).values(action='opsx-apply'));db.commit()
    prefix=f'openspec/changes/{CHANGE}'
    (project.root/prefix/'tasks.md').write_text('- [x] task')
    (project.root/prefix/'trace.md').write_bytes(md(status='applied',bug_id=OID,iteration='sprint-012',execution=dict(schema_version=1,started_at='2026-10-21 14:00:00',completed_at='2026-10-21 15:00:00',last_event='opsx.apply')))
    (project.root/BASE/'acceptance.md').write_bytes(md(acceptance_status='passed')+b'\n- [x] AC-001 sample\n')
    check=dict(id='AC-001',kind='command',inputs=[BASE+'/acceptance.md',prefix+'/design.md'],argv=['unused'])
    folder=project.root/prefix
    (folder/'acceptance-plan.json').write_text(json.dumps(dict(schema_version=1,change_id=CHANGE,issue_id=OID,checks=[check])))
    report=folder/'evidence/acceptance/run';report.mkdir(parents=True)
    (report/'manifest.json').write_text(json.dumps(dict(run_id='run',scope='complete',status='passed',checks=[dict(id='AC-001',status='passed',fingerprint=fingerprint(project.root,check),artifacts=[])])))
    emit(project.root,CHANGE,'opsx.accept',OID)
    from app.governance.archive_admission import issue_acceptance
    assert issue_acceptance(project.root,project.root/BASE,[CHANGE])['ready'], issue_acceptance(project.root,project.root/BASE,[CHANGE])
    return direct_scene

@pytest.mark.parametrize('failure',[None,'rules','tasks','uncovered','stale','receipt','version'])
def test_successor_actual_http_verifier(successor_scene,chat,failure):
    from app.governance import store
    factory,project,tid,rid,version=successor_scene;client,_=chat
    before=store.read(rid,'operation')['steps']
    prefix=project.root/f'openspec/changes/{CHANGE}'
    if failure=='rules':(project.root/'rules/security.md').write_text('changed')
    if failure=='tasks':(prefix/'tasks.md').write_text('- [x] different scope')
    if failure=='uncovered':(prefix/'proposal.md').write_text('new scope')
    if failure=='stale':(prefix/'design.md').write_text('stale input')
    if failure=='receipt':
        for f in (prefix/'.workflow-receipts').glob('*'):f.unlink()
    if failure=='version':version+=1
    url=f'/api/v1/chat/turns/{tid}/completion-verification'
    response=client.post(url,json={'expected_version':version})
    assert response.status_code==(200 if failure is None else 409),response.text
    if failure is None:
        assert response.json()['data']['state']=='recovered_valid'
        assert client.post(url,json={'expected_version':version}).status_code==200
        assert store.read(rid,'operation')['final_verification']['mode']=='successor_revalidation'
    assert store.read(rid,'operation')['steps']==before

@pytest.mark.parametrize('mode', ['unrelated', 'source_race', 'guard_race', 'permission', 'interrupted'])
def test_successor_recovery_fences(successor_scene, chat, monkeypatch, mode):
    from app.governance import store, execution_guard as guards
    from sqlalchemy import update, text
    factory, project, tid, rid, version = successor_scene
    client, _ = chat
    before = store.read(rid, 'operation')['steps']
    if mode == 'permission':
        with factory() as db:
            db.execute(text("UPDATE admin_spaces SET status='FROZEN'")); db.commit()
    original = store.write
    def write(record_id, name, value):
        original(record_id, name, value)
        if name != 'operation' or not value.get('final_verification'):
            return
        if mode == 'unrelated':
            path = project.root/'docs/another-object.md'; path.parent.mkdir(exist_ok=True); path.write_text('unrelated')
        elif mode == 'source_race':
            (project.root/f'openspec/changes/{CHANGE}/design.md').write_text('changed during verification')
        elif mode == 'guard_race':
            with factory() as db:
                db.execute(update(guards.execution_guards).where(guards.execution_guards.c.operation_id == tid).values(version=version+1)); db.commit()
        elif mode == 'interrupted':
            raise OSError('simulated interruption')
    monkeypatch.setattr(store, 'write', write)
    url = f'/api/v1/chat/turns/{tid}/completion-verification'
    if mode == 'interrupted':
        with pytest.raises(OSError): client.post(url, json={'expected_version':version})
        monkeypatch.setattr(store, 'write', original)
        response = client.post(url, json={'expected_version':version})
    else:
        response = client.post(url, json={'expected_version':version})
    assert response.status_code == (200 if mode in ('unrelated','interrupted') else 403 if mode == 'permission' else 409), response.text
    with factory() as db:
        assert (guards.read(db, project.key, OID)['state'] == 'recovered_valid') == (mode in ('unrelated','interrupted'))
    assert store.read(rid, 'operation')['steps'] == before


def test_receipt_rejects_path_escape(successor_scene):
    from app.governance.workflow_receipt import valid
    _, project, *_ = successor_scene
    assert not valid(project.root/f'openspec/changes/{CHANGE}', CHANGE, OID, '../run')


def test_new_failed_report_cannot_reissue_success_receipt(successor_scene):
    import os
    from app.governance.workflow_receipt import emit
    _, project, *_ = successor_scene
    folder = project.root/f'openspec/changes/{CHANGE}'
    before = list((folder/'.workflow-receipts').glob('*'))
    report = folder/'evidence/acceptance/failed/manifest.json'; report.parent.mkdir()
    report.write_text(json.dumps(dict(scope='complete',status='failed',checks=[])))
    os.utime(report, (2000000000,2000000000))
    emit(project.root, CHANGE, 'opsx.accept', OID)
    assert list((folder/'.workflow-receipts').glob('*')) == before


def test_resume_journal_after_guard_commit(successor_scene, chat, monkeypatch):
    from app.governance import store, execution_guard as guards
    factory, project, tid, rid, version = successor_scene
    client, _ = chat
    original = store.write
    def write(record_id, name, value):
        if name == 'operation' and value.get('final_verification', {}).get('pending_confirmation') is False:
            raise OSError('journal interrupted after guard commit')
        return original(record_id, name, value)
    monkeypatch.setattr(store, 'write', write)
    url = f'/api/v1/chat/turns/{tid}/completion-verification'
    with pytest.raises(OSError):client.post(url, json={'expected_version':version})
    with factory() as db:assert guards.read(db, project.key, OID)['state'] == 'recovered_valid'
    assert store.read(rid, 'operation')['final_verification']['pending_confirmation']
    monkeypatch.setattr(store, 'write', original)
    assert client.post(url, json={'expected_version':version}).status_code == 200
    assert not store.read(rid, 'operation')['final_verification']['pending_confirmation']


def test_current_card_stage_does_not_roll_back_while_guard_blocks(successor_scene):
    from app.governance.reader import ProjectReader
    factory, project, *_ = successor_scene
    with factory() as db:
        cards = ProjectReader(db, 'alice', project).call('build_requirement_center_context').issues
        card = next(c for c in cards if c.id in (OID, 'BUG-9001'))
        assert card.stage == 'acceptance'
        assert card.execution_state == 'needs_review'
        assert not card.can_send
        assert card.action.disabled_reason

@pytest.mark.parametrize('valid_report',[True,False])
def test_append_only_prior_acceptance_summary(successor_scene,chat,valid_report):
    _,project,tid,_,version=successor_scene;client,_=chat
    folder=project.root/f'openspec/changes/{CHANGE}/evidence/acceptance/earlier'
    folder.mkdir();(folder/'summary.md').write_text('Earlier failed run, not current acceptance authority')
    (folder/'manifest.json').write_text(json.dumps(dict(schema_version=1,change_id=CHANGE if valid_report else 'another-change',run_id='earlier',scope='diagnostic',status='blocked',checks=[dict(id='AC-001')])) )
    response=client.post(f'/api/v1/chat/turns/{tid}/completion-verification',json={'expected_version':version})
    assert response.status_code==(200 if valid_report else 409),response.text


def test_legacy_apply_observation_is_not_upgraded_to_completion():
    from test_direct_completion import files, record, OID
    from app.governance.direct_completion import verify, DirectProofError, manifest
    fs=files();r=record(fs);r['action']='opsx-apply'
    r['steps'][0]['completion_manifest']=manifest(fs,OID,'opsx-apply')
    with pytest.raises(DirectProofError,match='direct_completion_event_missing'):
        verify(r,fs,OID,'opsx-apply')


def test_binding_change_after_signature_keeps_guard(successor_scene,chat,monkeypatch):
    from dataclasses import replace
    from app.governance import store,scope,execution_guard as guards
    factory,project,tid,_,version=successor_scene;client,_=chat
    original=store.write;authorize=scope.authorize
    def write(rid,name,value):
        original(rid,name,value)
        if value.get('final_verification'):
            monkeypatch.setattr(scope,'authorize',lambda *a,**kw:replace(authorize(*a,**kw),binding_revision='changed'))
    monkeypatch.setattr(store,'write',write)
    response=client.post(f'/api/v1/chat/turns/{tid}/completion-verification',json={'expected_version':version})
    assert response.status_code==409
    assert response.json()['data']['kind']=='direct_binding_changed'
    with factory() as db:assert guards.read(db,project.key,OID)['state']=='needs_review'


def test_unverified_external_result_keeps_canonical_stage(successor_scene):
    from sqlalchemy import update
    from app.governance import execution_guard as guards
    from app.governance.reader import ProjectReader
    factory, project, *_ = successor_scene
    (project.root / f'openspec/changes/{CHANGE}/tasks.md').write_text('- [x] implemented\n- [ ] product evidence pending\n')
    with factory() as db:
        db.execute(update(guards.execution_guards).where(guards.execution_guards.c.object_id == OID).values(
            action='external-sync', confirmed_stage='unknown', operation_id=None,
            conversation_id=None, state='needs_review', reason_code='external_result_unverified'))
        db.commit()
        card = next(c for c in ProjectReader(db, 'alice', project).call('build_requirement_center_context').issues if c.id in (OID, 'BUG-9001'))
        assert card.stage == 'acceptance'
        assert card.execution_state == 'needs_review'
        assert not card.can_send
        assert card.action.disabled_reason
