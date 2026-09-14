import json
import time
import pytest
from sqlalchemy import select,insert
from app.chat.schema import governance_applications,governance_candidates
from app.chat.service import ChatError
from app.governance import scope,store
from app.governance.snapshot import stable
from app.governance.writer import enqueue,process,assert_readable
from test_chat import chat
from test_governance_scope import bind
from test_governance_candidates import contents,OID,BASE


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
    return factory,project,before,after,permit


def queue(writing,key='once'):
    factory,project,before,after,_=writing
    # Exercise the same legacy multi-file spec editing path for atomicity/recovery.
    # For req-generate a candidate is required and independently revalidated.
    from app.chat import service
    from app.chat.schema import conversations,turns
    from app.governance.candidates import validate
    result=validate(before,after,OID,BASE)
    with factory() as db:
        parent=service.create_conversation(db,'alice','space','repo','synthetic result')
        tid=service.identity();db.execute(insert(turns).values(**tid,conversation_id=parent['id'],client_request_id='test',prompt='synthetic',status='completed'))
        candidate={**service.identity(),'actor_id':'alice','space_id':'space','repository_id':'repo','scope_key':project.key,
          'conversation_id':parent['id'],'turn_id':tid['id'],'object_id':OID,'action':'req-generate','binding_revision':project.binding_revision,
          'baseline_hash':stable(project.root).revision,'manifest_hash':result['manifest_hash'],'revision':1,'state':'pending'}
        db.execute(insert(governance_candidates).values(**candidate));db.commit()
        record={'before':{p:b.decode() for p,b in before.items()},'after':{f['path']:after[f['path']].decode() for f in result['files']},'kind':'req-generate','object_id':OID,'base_path':BASE}
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


def test_whole_batch_conflict_and_no_maintenance(writing):
    oid=queue(writing);factory,project,before,after,permit=writing
    (project.root/f'{BASE}/capture.md').write_text('external newer input')
    with factory() as db:assert process(db,oid)['state']=='conflict'
    assert not (project.root/f'{BASE}/requirement.md').exists()
    permit.unlink()
    with factory() as db:
        with pytest.raises(ChatError):enqueue(db,'alice',project,'missing',{}, {})


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
    def concurrent_snapshot(root):
        with factory() as worker:assert process(worker,oid)['state']=='applied'
        return Snapshot(partial,digest(partial))
    monkeypatch.setattr('app.governance.reader.stable',concurrent_snapshot)
    with factory() as reader:
        with pytest.raises(ChatError):ProjectReader(reader,'alice',project).snapshot()


def test_stale_database_session_does_not_reapply_finished_operation(writing):
    oid=queue(writing);factory,project,_,after,_=writing
    with factory() as stale:
        assert stale.scalar(select(governance_applications.c.state).where(governance_applications.c.id==oid))=='pending'
        with factory() as worker:assert process(worker,oid)['state']=='applied'
        assert process(stale,oid)['state']=='applied'
    assert stable(project.root).files==after
