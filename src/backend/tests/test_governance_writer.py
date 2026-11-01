import json
import time
import pytest
from sqlalchemy import select,insert,update,func
from app.chat.schema import governance_applications,governance_candidates
from app.chat.service import ChatError
from app.governance import scope,store
from app.governance.snapshot import stable
from app.governance.writer import enqueue,process,assert_readable
from test_chat import chat
from test_governance_scope import bind
from test_governance_candidates import contents,bug_contents,OID,BASE,BUG_OID,BUG_BASE


@pytest.fixture
def writing(chat,tmp_path,monkeypatch):
    _,factory=chat;root=tmp_path/'repo';root.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    bind(monkeypatch,root);monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private))
    before,after=contents()
    for name,body in before.items():
        target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
    with factory() as db:project=scope.authorize(db,'alice','space','repo',write=True)
    permit=private/'maintenance.json';permit.write_text(json.dumps({'scope_key':project.key,'binding_revision':project.binding_revision,
      'registered_writers':['governance-controller'],'external_writers_paused':True,'expires_at':time.time()+600}));permit.chmod(0o600)
    from app.governance.readiness import publish
    publish()
    return factory,project,before,after,permit


def queue(writing,key='once',*,candidate_action='req-generate',object_id=OID,base_path=BASE):
    factory,project,before,after,_=writing
    # Exercise the same legacy multi-file spec editing path for atomicity/recovery.
    # For req-generate a candidate is required and independently revalidated.
    from app.chat import service
    from app.chat.schema import conversations,turns
    from app.governance.candidates import validate
    result=validate(before,after,object_id,base_path,candidate_action)
    with factory() as db:
        parent=service.create_conversation(db,'alice','space','repo','synthetic result')
        tid=service.identity();db.execute(insert(turns).values(**tid,conversation_id=parent['id'],client_request_id='test',prompt='synthetic',status='completed'))
        candidate={**service.identity(),'actor_id':'alice','space_id':'space','repository_id':'repo','scope_key':project.key,
          'conversation_id':parent['id'],'turn_id':tid['id'],'object_id':object_id,'action':candidate_action,'binding_revision':project.binding_revision,
          'baseline_hash':stable(project.root).revision,'manifest_hash':result['manifest_hash'],'revision':1,'state':'pending'}
        db.execute(insert(governance_candidates).values(**candidate));db.commit()
        record={'before':{p:b.decode() for p,b in before.items()},'after':{f['path']:after[f['path']].decode() if f['path'] in after else None for f in result['files']},'kind':candidate_action,'object_id':object_id,'base_path':base_path}
        request={'candidate_id':candidate['id']}
        operation=enqueue(db,'alice',project,key,request,record,candidate['id'])
        assert enqueue(db,'alice',project,key,request,record,candidate['id'])['id']==operation['id']
        with pytest.raises(ChatError):enqueue(db,'alice',project,key,{'other':1},record,candidate['id'])
    return operation['id']


def test_apply_and_idempotent_operation(writing):
    oid=queue(writing);factory,project,before,after,_=writing
    with factory() as db:
        assert process(db,oid)['state']=='applied'
        assert process(db,oid)['state']=='applied'
    assert stable(project.root).files==after


def test_candidate_apply_runs_workflow_sync_before_success(writing):
    oid=queue(writing);factory,project,_,_=writing[:4]
    script=project.root/'scripts'/'sync-workflow-status.py'
    script.parent.mkdir(parents=True)
    script.write_text("import json, pathlib, sys\npathlib.Path('workflow-sync-marker.json').write_text(json.dumps(sys.argv, ensure_ascii=False))\n")
    with factory() as db:
        assert process(db,oid)['state']=='applied'
        row=db.execute(select(governance_applications).where(governance_applications.c.id==oid)).mappings().one()
        assert row['phase']=='verified'
    assert (project.root/'workflow-sync-marker.json').exists()
    assert store.read(oid,'operation')['workflow_sync']['event']=='req.generate'


def test_candidate_apply_blocks_success_when_workflow_sync_fails(writing):
    oid=queue(writing);factory,project,_,after,_=writing
    script=project.root/'scripts'/'sync-workflow-status.py'
    script.parent.mkdir(parents=True)
    script.write_text("import sys\nsys.exit(2)\n")
    with factory() as db:
        result=process(db,oid)
        assert result['state']=='recovery_blocked'
        assert result['error_code']=='workflow_sync_failed'
        row=db.execute(select(governance_candidates)).mappings().one()
        assert row['state']=='pending'
        with pytest.raises(ChatError):
            assert_readable(db,project)
    for name,body in after.items():
        assert (project.root/name).read_bytes()==body


def test_generate_apply_then_complete_without_git_commit(writing,monkeypatch):
    from app.chat.workspace import git,prepare_workspace,snapshot
    from app.governance.preparation import prepare_object_session,prepare_command_snapshot,initialize_workspace
    from app.chat import service
    from app.chat.schema import turns,conversations
    from sqlalchemy import update
    factory,project,_,after,_=writing
    skill=project.root/'.agents/skills/req-complete/SKILL.md';skill.parent.mkdir(parents=True);skill.write_text('complete skill')
    git(project.root,'init');git(project.root,'add','.')
    git(project.root,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','captured')
    operation=queue(writing)
    with factory() as db:
        candidate=db.execute(select(governance_candidates)).mappings().one()
        from app.chat.relations import set_relations
        set_relations(db,'alice',candidate['conversation_id'],OID,[])
        workspaces=project.root.parent/'workspaces';workspaces.mkdir()
        # Match the deployed read-only API mount: preparation may inspect but not commit.
        monkeypatch.setattr('app.governance.completion_recovery.repository_binding',
            lambda *_:{'workspace_root':str(workspaces)})
        workspace=prepare_workspace(project.root,workspaces,candidate['conversation_id'])['path']
        manifest={name:{k:v for k,v in item.items() if k in ('kind','sha256','executable')} for name,item in snapshot(workspace)['files'].items()}
        store.write(candidate['id'],'baseline',{'workspace_manifest':manifest})
        store.write(candidate['id'],'result',{'after':{name:body.decode() for name,body in after.items()}})
        for name,body in after.items():
            path=workspace/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
        assert process(db,operation)['state']=='applied'
        assert git(project.root,'status','--porcelain').strip()
        next_session=prepare_object_session(db,'alice','space','repo',OID,action='req-complete')
        parent=service.conversation(db,'alice',next_session['conversation_id'])
        # Reuse the generation session, including its already-applied dirty worktree.
        assert parent['id']==candidate['conversation_id']
        from app.governance import preparation
        original_git=preparation.git
        def readonly_git(path,*args):
            assert 'add' not in args and 'commit' not in args
            return original_git(path,*args)
        with monkeypatch.context() as guarded:
            guarded.setattr(preparation,'git',readonly_git)
            prepare_command_snapshot(db,'alice',parent,f'/req-complete {OID}','after-generate')
        assert git(workspace,'status','--porcelain').strip()
        turn=service.identity()
        db.execute(insert(turns).values(**turn,conversation_id=parent['id'],client_request_id='after-generate',prompt=f'/req-complete {OID}',status='connecting'))
        db.execute(update(conversations).where(conversations.c.id==parent['id']).values(active_turn_id=turn['id']));db.commit()
        initialize_workspace(db,service.conversation(db,'alice',parent['id']),project.root,workspace)
        assert stable(workspace).files==after
        assert not git(workspace,'status','--porcelain').strip()
    assert stable(project.root).files==after


def test_bug_generate_candidate_applies_bug_files(chat,tmp_path,monkeypatch):
    _,factory=chat;root=tmp_path/'repo';root.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    bind(monkeypatch,root);monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private))
    before,after=bug_contents()
    for name,body in before.items():
        target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
    with factory() as db:project=scope.authorize(db,'alice','space','repo',write=True)
    permit=private/'maintenance.json';permit.write_text(json.dumps({'scope_key':project.key,'binding_revision':project.binding_revision,
      'registered_writers':['governance-controller'],'external_writers_paused':True,'expires_at':time.time()+600}));permit.chmod(0o600)
    from app.governance.readiness import publish
    publish()
    oid=queue((factory,project,before,after,permit),'bug-once',candidate_action='bug-generate',object_id=BUG_OID,base_path=BUG_BASE)
    with factory() as db:
        assert process(db,oid)['state']=='applied'
        row=db.execute(select(governance_applications).where(governance_applications.c.id==oid)).mappings().one()
        assert row['candidate_id']
    assert stable(project.root).files==after


def test_whole_batch_conflict_and_no_maintenance(writing):
    oid=queue(writing);factory,project,before,after,permit=writing
    (project.root/f'{BASE}/capture.md').write_text('external newer input')
    with factory() as db:assert process(db,oid)['state']=='conflict'
    assert not (project.root/f'{BASE}/requirement.md').exists()
    permit.unlink()
    with factory() as db:
        with pytest.raises(ChatError):enqueue(db,'alice',project,'missing',{}, {})


@pytest.mark.parametrize('stale_field',['manifest','revision','binding'])
def test_candidate_application_rejects_stale_identity_before_new_operation(writing,stale_field):
    from app.governance.writer import apply_candidate
    oid=queue(writing);factory,project,before,_,_=writing
    with factory() as db:
        candidate=db.execute(select(governance_candidates)).mappings().one()
        count=db.scalar(select(func.count()).select_from(governance_applications))
        manifest=candidate['manifest_hash']
        revision=candidate['revision']
        if stale_field=='manifest':manifest='0'*64
        elif stale_field=='revision':revision+=1
        else:
            db.execute(update(governance_candidates).where(governance_candidates.c.id==candidate['id']).values(binding_revision='stale-binding'))
            db.commit()
        with pytest.raises(ChatError) as error:
            apply_candidate(db,'alice',candidate['id'],manifest,revision,'stale-application',True)
        assert error.value.code==2606
        assert db.scalar(select(func.count()).select_from(governance_applications))==count
    assert stable(project.root).files==before


def test_generate_candidate_uses_controller_readiness_without_maintenance(writing):
    factory, project, before, after, permit = writing
    permit.unlink()
    oid = queue((factory, project, before, after, permit), 'controller-generate')
    with factory() as db:
        assert process(db, oid)['state'] == 'applied'
        with pytest.raises(ChatError):
            enqueue(db, 'alice', project, 'document-still-blocked', {}, {'kind': 'document'})
    assert stable(project.root).files == after


def test_crash_recovery_rolls_forward_with_persistent_images(writing):
    oid=queue(writing);factory,project,_,after,_=writing
    def crash(*_):raise SystemExit('synthetic power loss after replace before log')
    with factory() as db:
        with pytest.raises(SystemExit):process(db,oid,after_write=crash)
        with pytest.raises(ChatError):assert_readable(db,project)
    with factory() as restarted:assert process(restarted,oid)['state']=='applied'
    assert stable(project.root).files==after


def test_external_change_during_recovery_is_never_overwritten(writing):
    oid=queue(writing);factory,project,_,_,_=writing
    changed=[]
    def crash(index,path):changed.append(path);raise SystemExit()
    with factory() as db:
        with pytest.raises(SystemExit):process(db,oid,after_write=crash)
    path=project.root/changed[0];path.write_text('external change must survive')
    with factory() as restarted:
        assert process(restarted,oid)['state']=='recovery_blocked'
        with pytest.raises(ChatError):assert_readable(restarted,project)
    assert path.read_text()=='external change must survive'
    assert store.read(oid,'operation')['before']


def test_registered_writer_lock_prevents_concurrent_takeover(writing):
    from app.governance.writer import project_lock
    oid=queue(writing);factory,project,before,_,_=writing
    with project_lock(project),factory() as db:
        with pytest.raises(BlockingIOError):process(db,oid)
    assert stable(project.root).files==before


def test_telemetry_failure_does_not_replace_success(writing,monkeypatch):
    from app.governance import observability
    oid=queue(writing);factory,project,_,after,_=writing
    # The instrumentation helper owns its own failure boundary.
    with factory() as db:
        original=db.begin_nested
        monkeypatch.setattr(db,'begin_nested',lambda:(_ for _ in ()).throw(RuntimeError('synthetic telemetry failure')))
        observability.trace(db,oid,'pending')
        monkeypatch.setattr(db,'begin_nested',original)
        assert process(db,oid)['state']=='applied'
    assert stable(project.root).files==after


def test_governance_observation_rejects_untrusted_metadata_and_keeps_recovery_trace(writing):
    import json
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import select, update
    from app.chat.schema import task_traces, task_trace_spans
    from app.governance.observability import trace, prune

    factory, _, *_ = writing
    old = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat(timespec='seconds')
    with factory() as db:
        trace(db, 'pending-opaque', 'recovering', metadata={
            'object_id': 'REQ-0001-safe', 'candidate_id': '/' + 'Users/private/local-path',
            'error_code': 'secret value', 'prompt': 'synthetic private prompt',
        })
        trace(db, 'finished-opaque', 'applied', metadata={'object_id': 'REQ-0002-safe'})
        db.commit()
        rows = db.execute(select(task_traces)).mappings().all()
        assert len(rows) == 2
        pending = next(row for row in rows if row['turn_id'] == 'governance:pending-opaque')
        assert json.loads(pending['metadata']) == {'object_id': 'REQ-0001-safe'}
        db.execute(update(task_traces).where(task_traces.c.task_trace_id == pending['task_trace_id']).values(created_at=old))
        db.execute(update(task_traces).where(task_traces.c.turn_id == 'governance:finished-opaque').values(finished_at=old))
        db.commit()
        prune(db)
        kept = db.execute(select(task_traces)).mappings().all()
        assert [row['turn_id'] for row in kept] == ['governance:pending-opaque']
        assert db.scalar(select(task_trace_spans.c.id).where(task_trace_spans.c.task_trace_id == pending['task_trace_id'])) is not None


def test_document_save_uses_same_queue_and_version_check(writing):
    from app.governance.reader import ProjectReader,version
    from app.governance.writer import enqueue_document
    factory,project,before,_,_=writing
    with factory() as db:
        reader=ProjectReader(db,'alice',project)
        record=enqueue_document(reader,'update_requirement_center_document',OID,'capture.md','updated capture',version('captured input'),'save-1')
        assert record['state']=='pending'
        assert (project.root/f'{BASE}/capture.md').read_bytes()==before[f'{BASE}/capture.md']
        assert process(db,record['id'])['state']=='applied'
        assert (project.root/f'{BASE}/capture.md').read_text()=='updated capture'
        with pytest.raises(ChatError):enqueue_document(reader,'update_requirement_center_document',OID,'capture.md','stale draft',version('captured input'),'save-2')


def test_reader_rejects_snapshot_if_writer_finishes_during_read(writing,monkeypatch):
    from app.governance.reader import ProjectReader
    from app.governance.snapshot import Snapshot,digest
    oid=queue(writing);factory,project,before,after,_=writing
    partial={**before,'issues/requirements/_registry.yaml':after['issues/requirements/_registry.yaml']}
    def concurrent_snapshot(root, *_args, **_kwargs):
        with factory() as worker:assert process(worker,oid)['state']=='applied'
        return Snapshot(partial,digest(partial))
    monkeypatch.setattr('app.governance.read_snapshot.stable_read',concurrent_snapshot)
    with factory() as reader:
        with pytest.raises(ChatError):ProjectReader(reader,'alice',project).snapshot()


def test_stale_database_session_does_not_reapply_finished_operation(writing):
    oid=queue(writing);factory,project,_,after,_=writing
    with factory() as stale:
        assert stale.scalar(select(governance_applications.c.state).where(governance_applications.c.id==oid))=='pending'
        with factory() as worker:assert process(worker,oid)['state']=='applied'
        assert process(stale,oid)['state']=='applied'
    assert stable(project.root).files==after
