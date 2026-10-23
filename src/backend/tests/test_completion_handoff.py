"""Transactional synthetic evidence; not a real product-run signoff."""
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import select, update
from app.chat.schema import conversations, turns, governance_candidates as candidates, governance_applications as applications
from app.governance import store, durable_recovery as policy
from app.governance.execution_guard import acquire, terminal, read
from app.governance.completion_handoff import handoffs, enqueue, tick
from app.governance.snapshot import digest
from test_chat import chat
from test_governance_writer import writing, queue
from test_governance_review import review_files


@pytest.mark.parametrize('bug',[False,True])
@pytest.mark.parametrize('mode',['normal','unrelated','conflict','restart','permission','transient','stale','concurrent'])
def test_verified_application_converges_without_reader(writing, chat, monkeypatch, bug, mode):
    factory, project, _, _, permit=writing
    before,after,oid,base=review_files(bug)
    for path in list(project.root.rglob('*')):
        if path.is_file(): path.unlink()
    for name,body in after.items():
        path=project.root/name; path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    aid=queue((factory,project,before,after,permit),candidate_action='bug-review' if bug else 'req-review',object_id=oid,base_path=base)
    with factory() as db:
        app=db.execute(select(applications).where(applications.c.id==aid)).mappings().one()
        candidate=db.execute(select(candidates).where(candidates.c.id==app['candidate_id'])).mappings().one()
        parent=db.execute(select(conversations).where(conversations.c.id==candidate['conversation_id'])).mappings().one()
        cid=candidate['id']; tid=candidate['turn_id']
        db.execute(update(turns).where(turns.c.id==tid).values(status='completed'))
        db.execute(update(applications).where(applications.c.id==aid).values(state='applied',phase='verified'))
        db.execute(update(candidates).where(candidates.c.id==cid).values(state='applied'))
        op=policy.create(db,actor='alice',project=project,parent=parent,action=candidate['action'],object_id=oid,
            request_key='complete',request_hash='input',source_hash=digest(before),candidate_id=cid)
        from app.governance.recovery_schema import operations
        db.execute(update(operations).where(operations.c.id==op).values(origin_turn_id=tid,application_id=aid,state='completed'))
        acquire(db,scope_key=project.key,object_id=oid,operation_id=tid,conversation_id=parent['id'],owner_id='alice',
                action=candidate['action'],confirmed_stage='review-ready',baseline_revision=digest(before))
        terminal(db,tid,'completed')
        store.write(cid,'baseline',{'workspace_mode':'source','files':{k:v.decode() for k,v in before.items()}})
        store.write(cid,'result',{'after':{k:after.get(k,b'').decode() if k in after else None for k in set(before)|set(after) if before.get(k)!=after.get(k)}})
        store.write(aid,'operation',{'workflow_sync':{'object_id':oid,'event':candidate['action'].replace('-','.'),'source_hash':digest(after)}})
        if mode!='restart': enqueue(db,cid)
        db.commit()
    if mode=='unrelated':
        (project.root/'docs').mkdir(exist_ok=True);(project.root/'docs/unrelated.md').write_text('# new')
    if mode=='conflict':
        path=next(project.root.glob(f'issues/*/review/{oid}/review.md'));path.write_text('# changed')
    if mode=='permission':
        from app.chat.service import ChatError
        def denied(*a,**kw): raise ChatError(2601,'denied',403)
        monkeypatch.setattr('app.governance.recovery_service.authorize',denied)
    if mode=='stale':
        from app.governance.execution_guard import execution_guards
        with factory() as db:
            db.execute(update(execution_guards).where(execution_guards.c.object_id==oid).values(version=2, operation_id='new-operation', state='running'))
            db.commit()
    if mode=='transient':
        def unavailable(*a,**kw): raise OSError('unavailable')
        monkeypatch.setattr('app.governance.execution_context.reconcile',unavailable)
    now=datetime.now(timezone.utc)+timedelta(seconds=1)
    if mode=='concurrent':
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=2) as workers:
            list(workers.map(lambda _: tick(factory,now), range(2)))
    else:
        tick(factory,now)
    tick(factory,now+timedelta(seconds=60));tick(factory,now+timedelta(seconds=120))
    with factory() as db:
        job=db.execute(select(handoffs)).mappings().one()
        guard=read(db,project.key,oid)
        if mode in ('conflict','permission','transient','stale'):
            assert job['state']=='blocked',dict(job)
            assert guard['state']==('running' if mode=='stale' else 'needs_review')
        else:
            assert job['state']=='confirmed',dict(job)
            assert guard['state']=='validated',dict(guard)
        assert job['attempt_count']==(3 if mode=='transient' else 1)
        if mode=='transient': assert job['reason_code']=='retry_exhausted'
        assert db.scalar(select(turns.c.status).where(turns.c.id==tid))=='completed'
    if mode=='conflict':
        response=chat[0].post(f'/api/v1/chat/governance-operations/{op}/verifications')
        assert response.status_code==200,response.text
        assert response.json()['data']['verification_differences']==['对象成果：修改 1 项']
    if mode=='normal':
        response=chat[0].post(f'/api/v1/chat/governance-operations/{op}/verifications')
        assert response.status_code==200,response.text
        assert response.json()['data']['admission_state']=='allowed'
        assert response.json()['data']['historical_result']=='verified'
        repeated=chat[0].post(f'/api/v1/chat/governance-operations/{op}/verifications')
        assert repeated.status_code==200
        assert repeated.json()['data']['admission_state']=='allowed'
        from app.governance.reader import ProjectReader
        with factory() as db:
            card=next(c for c in ProjectReader(db,'alice',project).call('build_requirement_center_context').issues if c.id==oid.split('-')[0]+'-'+oid.split('-')[1])
            assert card.view_turn_id==tid
            assert card.verification_operation_id==op
            assert card.historical_result=='verified'

        with factory() as db:
            assert len(db.execute(select(applications)).all())==1
            assert len(db.execute(select(turns)).all())==1
        path=next(project.root.glob(f'issues/*/review/{oid}/review.md'))
        original=path.read_bytes();path.write_bytes(original+b'\nrelated change\n')
        changed=chat[0].post(f'/api/v1/chat/governance-operations/{op}/verifications')
        assert changed.status_code==200
        assert changed.json()['data']['historical_result']=='verified'
        assert changed.json()['data']['admission_state']=='blocked'
        assert changed.json()['data']['verification_reason']=='dependency_conflict'
        assert changed.json()['data']['verification_differences']==['对象成果：修改 1 项']
        path.write_bytes(original)
        restored=chat[0].post(f'/api/v1/chat/governance-operations/{op}/verifications')
        assert restored.json()['data']['admission_state']=='allowed'
        with factory() as db:
            assert len(db.execute(select(applications)).all())==1
            assert len(db.execute(select(turns)).all())==1
        assert chat[0].post('/api/v1/chat/governance-operations/missing/verifications').status_code==404


def test_crashed_claim_exhaustion_is_durable(writing):
    from app.governance.completion_handoff import stamp
    from sqlalchemy import insert
    factory, *_ = writing
    now=datetime.now(timezone.utc)
    with factory() as db:
        db.execute(insert(handoffs).values(scope_key='s',object_id='REQ-9001-test',guard_version=1,
            operation_id='missing',application_id='missing',state='checking',attempt_count=3,
            next_attempt_at=stamp(now),created_at=stamp(now),lease_owner='dead',lease_until=stamp(now-timedelta(seconds=1))))
        db.commit()
    tick(factory,now);tick(factory,now+timedelta(seconds=60))
    with factory() as db:
        row=db.execute(select(handoffs)).mappings().one()
        assert row['state']=='blocked' and row['reason_code']=='retry_exhausted'
        assert row['attempt_count']==3
