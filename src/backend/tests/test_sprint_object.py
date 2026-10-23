import pytest
import yaml
from app.chat.service import ChatError
from app.governance.sprint_object import resolve, preparation_reason
from app.services import requirement_center as center


def write(root, name, value):
    p = root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value)


def plan(root, **extra):
    value = dict(sprint_id='sprint-099', status='active', requirements=[], bugs=[], changes=['sample'])
    value.update(extra)
    write(root, 'iterations/change/sprint-099/sprint.yaml', yaml.safe_dump(value))
    for name in ('trace.md', 'proposal.md', 'tasks.md'):
        write(root, 'openspec/archive/2026-10-21-sample/' + name, '---\nstatus: archived\n---\n# Sample\n')
    return value


def test_identity_active_archive_and_no_fallback(tmp_path):
    p = plan(tmp_path)
    assert resolve(tmp_path, 'sprint-099')['plan'] == p
    source = tmp_path / 'iterations/change/sprint-099'
    target = tmp_path / 'iterations/archive/sprint-099'
    target.parent.mkdir(parents=True)
    source.rename(target)
    assert resolve(tmp_path, 'sprint-099')['path'].startswith('iterations/archive/')
    write(tmp_path, 'iterations/change/sprint-099/sprint.yaml', 'broken: true')
    with pytest.raises(ChatError): resolve(tmp_path, 'sprint-099')


def test_identity_rejects_links_and_mismatches(tmp_path):
    plan(tmp_path, sprint_id='sprint-098')
    with pytest.raises(ChatError): resolve(tmp_path, 'sprint-099')
    p = tmp_path / 'iterations/change/sprint-099/sprint.yaml'
    p.unlink(); p.symlink_to(tmp_path / 'secret')
    with pytest.raises(ChatError): resolve(tmp_path, 'sprint-099')
    with pytest.raises(ChatError): resolve(tmp_path, '../sprint-099')


@pytest.mark.parametrize('used,status', [(0,'normal'),(None,'unknown'),(30,'over_limit')])
def test_preparation_ignores_capacity_and_signoff(tmp_path, used, status):
    p = plan(tmp_path)
    with center.using_governance_root(tmp_path):
        result = center._sprint_archive_readiness('sprint-099', p, used, status)
    assert result.can_enter_confirmation


@pytest.mark.parametrize('changes,reason', [([], 'empty_scope'),(None,'scope_unknown'),(['missing'],'scope_unknown'),(['../sample'],'scope_unknown')])
def test_scope_fails_closed(tmp_path, changes, reason):
    p = plan(tmp_path, changes=changes)
    assert preparation_reason(tmp_path, 'sprint-099', p) == reason


def test_hidden_associated_change_blocks_completed_issue(tmp_path):
    oid = 'REQ-0099-sample'; base = 'issues/requirements/archive/' + oid
    p = plan(tmp_path, requirements=[oid])
    write(tmp_path, 'issues/requirements/_registry.yaml', yaml.safe_dump({'entries':[{'id':oid,'path':base,'status':'done'}]}))
    write(tmp_path, base + '/trace.md', '---\nstatus: done\nopenspec_changes:\n- change_id: unfinished\n---\n# Trace\n')
    write(tmp_path, 'openspec/changes/unfinished/trace.md', '---\nstatus: applied\n---\n# Trace\n')
    assert preparation_reason(tmp_path, 'sprint-099', p) == 'unarchived_scope'


def test_send_requires_signoff_and_command_is_strict(tmp_path, monkeypatch):
    from app.governance.sprint_object import require_final
    from app.governance.preparation import _write_command
    plan(tmp_path)
    monkeypatch.setattr('app.governance.sprint_archive_admission.change_close_readiness', lambda *a, **kw: {'ready':True})
    with pytest.raises(ChatError): require_final(tmp_path, 'sprint-099')
    write(tmp_path, 'iterations/change/sprint-099/acceptance-report.md', '---\nsigned_off: true\n---\n# Signed\n')
    assert require_final(tmp_path, 'sprint-099')['id'] == 'sprint-099'
    assert _write_command('/sprint-archive sprint-099') == ('sprint-archive','sprint-099')
    for command in ('/sprint-archive sprint-99','/sprint-archive sprint-099 extra','/sprint-archive'):
        with pytest.raises(ChatError): _write_command(command)


def test_sprint_completion_requires_closed_source_and_signed_report(tmp_path):
    from app.governance.execution_validation import validate_result
    plan(tmp_path)
    files = {str(p.relative_to(tmp_path)):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    assert not validate_result(files, 'sprint-099', 'sprint-archive')
    old = 'iterations/change/sprint-099/sprint.yaml'
    files['iterations/archive/sprint-099/sprint.yaml'] = files.pop(old).replace(b'active',b'closed')
    for name in ('sprint.md','release-note.md','acceptance-report.md'):
        files['iterations/archive/sprint-099/' + name] = b'---\nsigned_off: true\n---\n# Done\n'
    assert validate_result(files, 'sprint-099', 'sprint-archive')
    files['iterations/archive/sprint-099/acceptance-report.md'] = b'---\nsigned_off: false\n---\n# Done\n'
    assert not validate_result(files, 'sprint-099', 'sprint-archive')

from test_chat import chat


def session_fixture(tmp_path, monkeypatch):
    from test_governance_scope import bind, fixture_tree
    from app.chat.workspace import git
    root = fixture_tree(tmp_path / 'repo')
    plan(root)
    private = tmp_path / 'private'; private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(private))
    bind(monkeypatch, root)
    git(root, 'init'); git(root, 'add', '.')
    git(root, '-c','user.name=Test','-c','user.email=test@invalid','commit','-m','fixture')
    return root


def test_api_prepares_and_reuses_without_turn(chat,tmp_path,monkeypatch):
    from sqlalchemy import select,func
    from app.chat.schema import conversations,turns,governance_candidates,relations
    client,factory = chat
    session_fixture(tmp_path,monkeypatch)
    body=dict(space_id='space',repository_id='repo',object_id='sprint-099',action='sprint-archive')
    first=client.post('/api/v1/chat/object-sessions',json={**body,'idempotency_key':'first'})
    assert first.status_code == 200, first.text
    one=first.json()['data']
    assert one['object_type']=='SPRINT' and one['can_send']
    second=client.post('/api/v1/chat/object-sessions',json={**body,'idempotency_key':'second'})
    assert second.status_code==200,second.text
    assert second.json()['data']['conversation_id']==one['conversation_id']
    assert second.json()['data']['reused_conversation']
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(conversations))==1
        assert db.scalar(select(func.count()).select_from(relations))==1
        assert db.scalar(select(func.count()).select_from(turns))==0
        assert db.scalar(select(func.count()).select_from(governance_candidates))==0
    bad=client.post('/api/v1/chat/object-sessions',json={**body,'repository_id':'other'})
    assert bad.status_code != 200


def test_preparation_permission_and_busy_do_not_create(chat,tmp_path,monkeypatch):
    from app.governance.preparation import prepare_object_session
    from test_chat import queued
    from sqlalchemy import text
    client,factory=chat
    session_fixture(tmp_path,monkeypatch)
    with factory() as db:
        first=prepare_object_session(db,'alice','space','repo','sprint-099',action='sprint-archive')
        with pytest.raises(ChatError): prepare_object_session(db,'bob','space','repo','sprint-099',action='sprint-archive')
    queued(factory,first['conversation_id'])
    with factory() as db:
        result=prepare_object_session(db,'alice','space','repo','sprint-099',action='sprint-archive')
        assert not result['can_send']
        assert result['view_conversation_id']==first['conversation_id']
        db.execute(text("INSERT INTO admin_space_members(id,space_id,user_id,role) VALUES('viewer','space','bob','查看者')"));db.commit()
        with pytest.raises(ChatError): prepare_object_session(db,'bob','space','repo','sprint-099',action='sprint-archive')


def test_concurrent_creation_uses_object_epoch(chat,tmp_path,monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from app.governance.preparation import _create_sprint_conversation
    from app.governance.scope import authorize
    from sqlalchemy import select,func
    from app.chat.schema import conversations,relations
    _,factory=chat
    root=session_fixture(tmp_path,monkeypatch)
    item=resolve(root,'sprint-099')
    gate=Barrier(2)
    def create():
        with factory() as db:
            project=authorize(db,'alice','space','repo',write=True)
            gate.wait()
            return _create_sprint_conversation(db,'alice',project,item)['id']
    with ThreadPoolExecutor(max_workers=2) as pool:
        ids=list(pool.map(lambda _:create(),range(2)))
    assert ids[0]==ids[1]
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(conversations))==1
        assert db.scalar(select(func.count()).select_from(relations))==1


def test_final_completion_proof_requires_sync_and_unchanged_scope(tmp_path):
    from app.governance.direct_completion import manifest, verify, DirectProofError
    plan(tmp_path)
    for folder in ('requirements','bugs'):
        write(tmp_path,f'issues/{folder}/_registry.yaml','entries: []\n')
    src=tmp_path/'iterations/change/sprint-099';dest=tmp_path/'iterations/archive/sprint-099'
    dest.parent.mkdir(parents=True);src.rename(dest)
    p=dest/'sprint.yaml';p.write_text(p.read_text().replace('status: active','status: completed'))
    for name in ('sprint.md','release-note.md','acceptance-report.md'):
        write(tmp_path,'iterations/archive/sprint-099/'+name,'---\nsigned_off: true\n---\n# Result\n')
    files={str(p.relative_to(tmp_path)):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    proof=manifest(files,'sprint-099','sprint-archive')
    record=dict(schema_version=1,action='sprint-archive',object_id='sprint-099',steps=[])
    with pytest.raises(DirectProofError): verify(record,files,'sprint-099','sprint-archive')
    record['steps']=[{'sync_succeeded':True,'sync_result':{'event':'sprint.archive','ok':True,'mode':'write'},'completion_manifest':proof}]
    assert verify(record,files,'sprint-099','sprint-archive')==proof
    files['iterations/archive/sprint-099/release-note.md']+=b'changed result'
    with pytest.raises(DirectProofError): verify(record,files,'sprint-099','sprint-archive')


def test_send_snapshot_guard_and_permission_share_sprint_identity(chat,tmp_path,monkeypatch):
    from app.governance.preparation import prepare_object_session,prepare_command_snapshot
    from app.governance.execution_context import prepare, acquire
    from app.chat import service,policy
    from app.chat.schema import turns,conversations
    from sqlalchemy import insert,update
    _,factory=chat
    root=session_fixture(tmp_path,monkeypatch)
    monkeypatch.setattr('app.governance.sprint_archive_admission.change_close_readiness',lambda *a,**kw:{'ready':True})
    with factory() as db:
        session=prepare_object_session(db,'alice','space','repo','sprint-099',action='sprint-archive')
        parent=service.conversation(db,'alice',session['conversation_id'])
        assert policy.write_policy(db,'alice',parent)['write_scope']=='read_only'
        with pytest.raises(ChatError): prepare_command_snapshot(db,'alice',parent,'/sprint-archive sprint-099','send')
        write(root,'iterations/change/sprint-099/acceptance-report.md','---\nsigned_off: true\n---\n# Signed\n')
        prepare_command_snapshot(db,'alice',parent,'/sprint-archive sprint-099','send')
        guard=prepare(db,'alice',parent,'/sprint-archive sprint-099','send')
        assert guard['objects']==[('sprint-099','sprint-planning')]
        tid=service.identity()
        db.execute(insert(turns).values(**tid,conversation_id=parent['id'],client_request_id='send',prompt='/sprint-archive sprint-099',status='connecting'))
        acquire(db,guard,tid['id'],parent,'alice',client_id='send',request_fingerprint='test-send')
        db.execute(update(conversations).where(conversations.c.id==parent['id']).values(active_turn_id=tid['id']));db.commit()
        parent=service.conversation(db,'alice',parent['id'])
        assert policy.write_policy(db,'alice',parent)['write_scope']=='archive_write'
        write(root,'iterations/change/sprint-099/acceptance-report.md','---\nsigned_off: false\n---\n# Unsigned\n')
        assert policy.write_policy(db,'alice',parent)['write_scope']=='read_only'


def test_multiple_sessions_exclude_archived_deleted_and_order_turns(chat,tmp_path,monkeypatch):
    from app.governance.preparation import prepare_object_session
    from app.chat import service,relations as rel
    from app.chat.schema import turns,conversations
    from sqlalchemy import insert,update
    _,factory=chat;session_fixture(tmp_path,monkeypatch)
    with factory() as db:
        rows=[]
        for i in range(4):
            row=service.create_conversation(db,'alice','space','repo',f'session {i}')
            rel.set_relations(db,'alice',row['id'],'sprint-099',[]);rows.append(row)
            token=service.identity();token['updated_at']=f'2026-10-21T12:0{i}:00Z'
            db.execute(insert(turns).values(**token,conversation_id=row['id'],client_request_id=f'turn{i}',prompt='fixture',status='completed'))
            db.commit()
        db.execute(update(conversations).where(conversations.c.id==rows[3]['id']).values(deleted_at=service.now()))
        db.execute(update(conversations).where(conversations.c.id==rows[2]['id']).values(archived=1));db.commit()
        result=prepare_object_session(db,'alice','space','repo','sprint-099',action='sprint-archive')
        assert result['conversation_id']==rows[1]['id']


def test_unknown_sprint_state_and_duplicate_change_fail_closed(tmp_path):
    p=plan(tmp_path,status='unrecognized')
    assert preparation_reason(tmp_path,'sprint-099',p)=='scope_unknown'
    p['status']='active'
    write(tmp_path,'openspec/archive/2026-10-20-sample/trace.md','# duplicate')
    assert preparation_reason(tmp_path,'sprint-099',p)=='scope_unknown'


def test_registry_trailing_slash_and_signed_archive_transition(tmp_path, monkeypatch):
    from app.governance.sprint_object import require_final
    oid = 'REQ-0099-sample'; base = 'issues/requirements/archive/' + oid
    p = plan(tmp_path, requirements=[oid])
    write(tmp_path, 'issues/requirements/_registry.yaml', yaml.safe_dump({'entries':[{'id':oid,'path':base+'/', 'status':'done'}]}))
    write(tmp_path, base+'/trace.md', '---\nstatus: done\n---\n')
    assert preparation_reason(tmp_path, 'sprint-099', p) is None
    monkeypatch.setattr('app.governance.sprint_archive_admission.change_close_readiness', lambda *a, **kw: {'ready':True})
    write(tmp_path, 'iterations/change/sprint-099/acceptance-report.md', '# 签署\n验收签署：通过\n')
    source=tmp_path/'iterations/change/sprint-099'; target=tmp_path/'iterations/archive/sprint-099';target.parent.mkdir(parents=True)
    p['status']='completed';write(tmp_path,'iterations/change/sprint-099/sprint.yaml',yaml.safe_dump(p));source.rename(target)
    with pytest.raises(ChatError): require_final(tmp_path, 'sprint-099')
    assert require_final(tmp_path, 'sprint-099', allow_closing=True)['id'] == 'sprint-099'
    (target/'acceptance-report.md').write_text('# 未签署\n')
    with pytest.raises(ChatError): require_final(tmp_path, 'sprint-099', allow_closing=True)
