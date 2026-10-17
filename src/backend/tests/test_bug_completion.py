import copy
import pytest
from sqlalchemy import insert, select, update

from app.chat import service
from app.chat.policy import write_policy
from app.chat.schema import conversations, turns, governance_candidates, governance_applications
from app.chat.workspace import git, prepare_workspace, snapshot
from app.governance import store
from app.governance.candidates import frontmatter, validate
from app.governance.preparation import (prepare_object_session, prepare_command_snapshot,
    bind_prepared_turn, initialize_workspace, collect, execution_prompt_for_turn)
from app.governance.snapshot import stable
from app.governance.writer import process
from test_chat import chat
from test_governance_candidates import bug_contents, front, BUG_OID as OID, BUG_BASE as BASE
from test_governance_writer import writing, queue


def completed(root_status='hypothesis'):
    before=bug_contents()[1];after=copy.deepcopy(before)
    stage='pending_review' if root_status=='confirmed' else 'enriching'
    for name in ('bug.md','workaround.md','acceptance.md'):
        after[f'{BASE}/{name}']=front({'bug_id':OID,'status':stage})
    after[f'{BASE}/root-cause.md']=front({'bug_id':OID,'status':root_status},
        '\n## 根因状态\nstatus: '+root_status+'\n\n## 证据链\n| E1 | code_path | src/login.ts:12 | 未处理失效跳转 |\n')
    meta,_=frontmatter(before[f'{BASE}/trace.md']);meta['status']=stage
    if stage=='pending_review':meta['lifecycle']['completed']='2026-09-30'
    after[f'{BASE}/trace.md']=front(meta)
    for p in ('issues/bugs/_registry.yaml','issues/bugs/CHANGELOG.md'):
        after[p]=after[p].replace(b'draft',stage.encode())
    return before,after


@pytest.mark.parametrize('root_status',['unknown','hypothesis','probable','confirmed'])
def test_root_cause_controls_persisted_stage(root_status):
    before,after=completed(root_status)
    assert len(validate(before,after,OID,BASE,'bug-complete')['files'])==7


@pytest.mark.parametrize('failure',['missing','outside','status_conflict','evidence','premature','timestamp'])
def test_bug_completion_rejects_unsafe_results(failure):
    before,after=completed('confirmed' if failure in ('status_conflict','evidence') else 'hypothesis')
    if failure=='missing':del after[f'{BASE}/acceptance.md']
    elif failure=='outside':after['src/login.ts']=b'changed'
    elif failure=='status_conflict':after[f'{BASE}/root-cause.md']=after[f'{BASE}/root-cause.md'].replace(b'status: confirmed\n\n',b'status: hypothesis\n\n')
    elif failure=='evidence':after[f'{BASE}/root-cause.md']=after[f'{BASE}/root-cause.md'].split('## 证据链'.encode())[0]
    elif failure=='premature':after[f'{BASE}/trace.md']=after[f'{BASE}/trace.md'].replace(b'enriching',b'pending_review')
    else:
        meta,body=frontmatter(after[f'{BASE}/trace.md']);meta['lifecycle']['completed']='2026-09-30'
        after[f'{BASE}/trace.md']=front(meta)
    with pytest.raises(service.ChatError):validate(before,after,OID,BASE,'bug-complete')


@pytest.mark.parametrize('root_status',['hypothesis','confirmed'])
@pytest.mark.parametrize('source_changed',[False,True])
def test_same_conversation_generate_complete_auto_applies(writing,monkeypatch,root_status,source_changed):
    factory,project,_,_,permit=writing
    skill=project.root/'.agents/skills/bug-complete/SKILL.md'
    skill.parent.mkdir(parents=True);skill.write_text('complete skill')
    captured,generated=bug_contents();_,result=completed(root_status)
    # Keep the fixture's unrelated requirement facts intact through both operations.
    existing=stable(project.root).files
    captured={**existing,**captured};generated={**existing,**generated};result={**existing,**result}
    for p,b in captured.items():
        dest=project.root/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
    git(project.root,'init');git(project.root,'add','.')
    git(project.root,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','captured')
    operation=queue((factory,project,captured,generated,permit),candidate_action='bug-generate',object_id=OID,base_path=BASE)
    with factory() as db:
        old=db.execute(select(governance_candidates)).mappings().one()
        from app.chat.relations import set_relations
        set_relations(db,'alice',old['conversation_id'],OID,[])
        workspaces=project.root.parent/'workspaces';workspaces.mkdir()
        monkeypatch.setattr('app.governance.completion_recovery.repository_binding',lambda *_:{'workspace_root':str(workspaces)})
        workspace=prepare_workspace(project.root,workspaces,old['conversation_id'])['path']
        manifest={p:{k:v for k,v in item.items() if k in ('kind','sha256','executable')} for p,item in snapshot(workspace)['files'].items()}
        store.write(old['id'],'baseline',{'workspace_manifest':manifest})
        store.write(old['id'],'result',{'after':{p:b.decode() for p,b in generated.items()}})
        for p,b in generated.items():
            dest=workspace/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
        assert process(db,operation)['state']=='applied'
        db.execute(update(governance_candidates).where(governance_candidates.c.id==old['id']).values(updated_at='2026-01-01T00:00:00+00:00'));db.commit()
        next_session=prepare_object_session(db,'alice','space','repo',OID,action='bug-complete')
        assert next_session['conversation_id']==old['conversation_id']
        parent=service.conversation(db,'alice',old['conversation_id'])
        assert write_policy(db,'alice',parent)['reason_code']!='governance_candidate_invalid'
        prepare_command_snapshot(db,'alice',parent,f'/bug-complete {OID}','complete')
        turn=service.identity()
        db.execute(insert(turns).values(**turn,conversation_id=parent['id'],client_request_id='complete',prompt=f'/bug-complete {OID}',status='completed'))
        bind_prepared_turn(db,parent['id'],turn['id'])
        db.execute(update(conversations).where(conversations.c.id==parent['id']).values(active_turn_id=turn['id']));db.commit()
        parent=service.conversation(db,'alice',parent['id'])
        initialize_workspace(db,parent,project.root,workspace)
        assert write_policy(db,'alice',parent)['reason_code']=='governance_candidate_running'
        assert 'enriching' in execution_prompt_for_turn(db,parent,f'/bug-complete {OID}')
        for p,b in result.items():
            dest=workspace/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
        collect(db,parent,turn['id'],workspace,'completed')
        candidate=db.execute(select(governance_candidates).where(governance_candidates.c.turn_id==turn['id'])).mappings().one()
        assert candidate['action']=='bug-complete' and candidate['state']=='pending'
        application=db.execute(select(governance_applications).where(governance_applications.c.candidate_id==candidate['id'])).mappings().one()
        assert process(db,application['id'])['state']=='applied'
        assert stable(project.root).files==result
        assert db.scalar(select(turns.c.prompt).where(turns.c.id==turn['id']))==f'/bug-complete {OID}'
        if root_status=='confirmed':return  # Further completion is not admitted after review readiness.
        db.execute(update(conversations).where(conversations.c.id==parent['id']).values(active_turn_id=None));db.commit()
        parent=service.conversation(db,'alice',parent['id'])
        prepare_command_snapshot(db,'alice',parent,f'/bug-complete {OID}','repeat')
        repeat=service.identity()
        db.execute(insert(turns).values(**repeat,conversation_id=parent['id'],client_request_id='repeat',prompt=f'/bug-complete {OID}',status='completed'))
        bind_prepared_turn(db,parent['id'],repeat['id'])
        db.execute(update(conversations).where(conversations.c.id==parent['id']).values(active_turn_id=repeat['id']));db.commit()
        parent=service.conversation(db,'alice',parent['id'])
        initialize_workspace(db,parent,project.root,workspace)
        initial=snapshot(workspace)['hash']
        if source_changed:
            (project.root/f'{BASE}/capture.md').write_bytes(b'newer source')
        source_before=stable(project.root).revision
        collect(db,parent,repeat['id'],workspace,'completed')
        latest=db.execute(select(governance_candidates).where(governance_candidates.c.turn_id==repeat['id'])).mappings().one()
        assert latest['state']==('rejected' if source_changed else 'unchanged')
        assert not db.scalar(select(governance_applications.c.id).where(governance_applications.c.candidate_id==latest['id']))
        assert snapshot(workspace)['hash']==initial
        assert stable(project.root).revision==source_before


@pytest.mark.parametrize('root_status',['hypothesis','confirmed'])
def test_complete_noop_still_validates_documents(root_status):
    _,after=completed(root_status)
    assert validate(after,after,OID,BASE,'bug-complete')['files']==[]
    del after[f'{BASE}/acceptance.md']
    with pytest.raises(service.ChatError):validate(after,after,OID,BASE,'bug-complete')
