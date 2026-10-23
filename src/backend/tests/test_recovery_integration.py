"""Real writer recovery transactions; synthetic fixtures are not product observation."""
import pytest
from sqlalchemy import select, update, func
from app.chat import service
from app.chat.schema import conversations, turns, governance_candidates as candidates, governance_applications as applications
from app.governance import store, durable_recovery as policy
from app.governance.recovery_schema import operations, attempts
from app.governance.recovery_service import detail, request_recovery
from app.governance.recovery_controller import process_attempt
from app.governance.snapshot import stable
from test_chat import chat
from test_governance_writer import writing, queue
from test_governance_review import review_files


@pytest.mark.parametrize('bug', [False, True])
@pytest.mark.parametrize('failure', [None, 'binding', 'permission', 'artifact'])
def test_stopped_review_explicit_resume_reuses_application(writing, chat, monkeypatch, bug, failure):
    factory, project, _, _, permit = writing
    before, after, object_id, base = review_files(bug)
    for path in stable(project.root).files: (project.root/path).unlink()
    for path, body in before.items():
        target=project.root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
    app_id=queue((factory, project, before, after, permit),candidate_action='bug-review' if bug else 'req-review',object_id=object_id,base_path=base)
    monkeypatch.setenv('MOONBOX_CHAT_RETENTION','{"executor_delete_seconds":86400,"backup_expiry_seconds":86400}')
    from app.governance.recovery_capabilities import publish
    publish('worker'); publish('controller')
    with factory() as db:
        app=db.execute(select(applications).where(applications.c.id==app_id)).mappings().one()
        candidate=db.execute(select(candidates).where(candidates.c.id==app['candidate_id'])).mappings().one()
        parent=db.execute(select(conversations).where(conversations.c.id==candidate['conversation_id'])).mappings().one()
        db.execute(update(turns).where(turns.c.id==candidate['turn_id']).values(status='stopped'))
        store.write(candidate['id'],'baseline',{'binding_revision':project.binding_revision})
        store.write(candidate['id'],'result',{'manifest_hash':candidate['manifest_hash']})
        oid=policy.create(db,actor='alice',project=project,parent=parent,action=candidate['action'],object_id=object_id,
            request_key='original',request_hash='immutable',source_hash=stable(project.root).revision,candidate_id=candidate['id'])
        db.execute(update(operations).where(operations.c.id==oid).values(origin_turn_id=candidate['turn_id'],
            stage='validation',state='waiting',execution_terminal='stopped',manifest_hash=candidate['manifest_hash'],
            application_id=app_id,recovery_expires_at=policy.expiry(service.now(),{'executor_delete_seconds':86400,'backup_expiry_seconds':86400})))
        db.commit()
        result=detail(db,'alice',oid)
        assert 'resume' in result['allowed_actions']
        assert db.scalar(select(func.count()).select_from(attempts))==0
        db.execute(update(operations).where(operations.c.id==oid).values(manual_count=1))
        exhausted=detail(db,'alice',oid)
        assert 'resume' not in exhausted['allowed_actions'] and exhausted['reason_code']=='manual_attempt_exhausted'
        db.execute(update(operations).where(operations.c.id==oid).values(manual_count=0))
        db.commit()
        client = chat[0]
        response = client.get(f'/api/v1/chat/governance-operations/{oid}')
        assert response.status_code == 200 and response.json()['data']['execution_terminal'] == 'stopped'
        assert client.get('/api/v1/chat/governance-operations/unknown').status_code == 404
        payload = {'expected_version':1,'idempotency_key':'manual-one','confirmed':True}
        response = client.post(f'/api/v1/chat/governance-operations/{oid}/recoveries',json=payload)
        assert response.status_code == 202, response.text
        queued = response.json()['data']
        assert client.post(f'/api/v1/chat/governance-operations/{oid}/recoveries',json=payload).json()['data']['attempt_id'] == queued['attempt_id']
    if failure == 'binding':
        with factory() as db:
            db.execute(update(operations).where(operations.c.id==oid).values(binding_revision='changed'))
            db.commit()
    elif failure == 'permission':
        def denied(*args, **kwargs): raise service.ChatError(2601,'permission revoked',403)
        monkeypatch.setattr('app.governance.recovery_controller.authorize',denied)
    elif failure == 'artifact':
        store.write(candidate['id'],'result',{'manifest_hash':'changed'})
    with factory() as db:
        process_attempt(db,queued['attempt_id'])
    if failure:
        with factory() as db:
            current=policy.row(db,oid)
            assert current['state']=='blocked' and current['execution_terminal']=='stopped'
            assert current['lease_owner'] is None
        assert stable(project.root).files==before
        return
    with factory() as db:
        result=detail(db,'alice',oid)
        assert result['state']=='completed',result
        assert result['execution_terminal']=='stopped'
        assert db.scalar(select(func.count()).select_from(applications))==1
        assert db.scalar(select(func.count()).select_from(attempts))==1
        assert 'resume' not in result['allowed_actions']
        from app.chat.schema import usage_events, task_traces
        assert db.scalar(select(func.count()).select_from(usage_events).where(usage_events.c.event_name=='governance.recovery')) == 0
        recovery_trace=db.execute(select(task_traces).where(task_traces.c.turn_id=='governance:'+oid)).mappings().one()
        assert recovery_trace['status']=='applied' and recovery_trace['finished_at']
        # A crash after writer commit but before terminal projection must heal
        # from the existing turn, without changing that original terminal.
        db.execute(update(operations).where(operations.c.id==oid).values(execution_terminal=None,recovery_expires_at=None))
        from app.governance.recovery_service import checkpoint
        checkpoint(db,candidate['id'],'complete')
        healed=policy.row(db,oid)
        assert healed['state']=='completed' and healed['execution_terminal']=='stopped' and healed['recovery_expires_at']

    assert stable(project.root).files==after


def test_retention_protects_partial_application_and_requires_admin(writing):
    from app.governance.recovery_retention import classify, sweep, dispose
    factory, project, before, after, permit = writing
    app_id = queue(writing)
    with factory() as db:
        app=db.execute(select(applications).where(applications.c.id==app_id)).mappings().one()
        candidate=db.execute(select(candidates).where(candidates.c.id==app['candidate_id'])).mappings().one()
        parent=db.execute(select(conversations).where(conversations.c.id==candidate['conversation_id'])).mappings().one()
        oid=policy.create(db,actor='alice',project=project,parent=parent,action='req-review',object_id=candidate['object_id'],
            request_key='retention',request_hash='hash',source_hash=stable(project.root).revision)
        db.execute(update(operations).where(operations.c.id==oid).values(application_id=app_id,
            origin_turn_id=candidate['turn_id'],recovery_expires_at='2000-01-01T00:00:00+00:00'))
        db.execute(update(applications).where(applications.c.id==app_id).values(state='recovery_blocked'))
        db.commit()
        assert classify(db,policy.row(db,oid))=='cleanup_blocked'
        sweep(db)
        current=policy.row(db,oid)
        with pytest.raises(service.ChatError): dispose(db,'alice',oid,current['version'],'recheck')
        dispose(db,'alice',oid,current['version'],'retain_7_days')
        assert policy.row(db,oid)['recovery_expires_at']=='2000-01-01T00:00:00+00:00'
        assert policy.row(db,oid)['retention_until'] is not None
        with pytest.raises(service.ChatError): dispose(db,'bob',oid,current['version'],'retain_7_days')


def test_explicit_regeneration_cannot_take_over_commit_but_can_replace_expired_generation(writing):
    from sqlalchemy import delete
    from app.governance import execution_guard as guards
    from app.governance.recovery_service import prepare_explicit_regeneration
    factory, project, _, _, _=writing
    app_id=queue(writing)
    with factory() as db:
        app=db.execute(select(applications).where(applications.c.id==app_id)).mappings().one()
        candidate=db.execute(select(candidates).where(candidates.c.id==app['candidate_id'])).mappings().one()
        parent=db.execute(select(conversations).where(conversations.c.id==candidate['conversation_id'])).mappings().one()
        oid=policy.create(db,actor='alice',project=project,parent=parent,action='req-review',object_id=candidate['object_id'],
            request_key='old',request_hash='old',source_hash=stable(project.root).revision,candidate_id=candidate['id'])
        db.execute(update(operations).where(operations.c.id==oid).values(origin_turn_id=candidate['turn_id'],state='blocked',
            execution_terminal='stopped',recovery_expires_at='2000-01-01T00:00:00+00:00'))
        guards.acquire(db,scope_key=project.key,object_id=candidate['object_id'],operation_id=candidate['turn_id'],
            conversation_id=parent['id'],owner_id='alice',action='req-review',confirmed_stage='plan',baseline_revision='baseline')
        guards.terminal(db,candidate['turn_id'],'stopped')
        prepare_explicit_regeneration(db,'alice',parent,project,'req-review',candidate['object_id'],'new')
        assert guards.read(db,project.key,candidate['object_id'])['state']=='needs_review'
        # Independent fixture represents an expired generation that never queued an application.
        db.execute(delete(applications).where(applications.c.id==app_id))
        prepare_explicit_regeneration(db,'alice',parent,project,'req-review',candidate['object_id'],'new')
        assert guards.read(db,project.key,candidate['object_id'])['state']=='idle'
        assert policy.row(db,oid)['execution_terminal']=='stopped'
        assert db.scalar(select(candidates.c.state).where(candidates.c.id==candidate['id']))=='rejected'


def test_expired_unfinished_and_unknown_execution_keep_cleanup_protection(writing):
    from app.governance.recovery_retention import classify
    from app.chat.schema import turns
    factory, project, _, _, _=writing
    aid=queue(writing)
    with factory() as db:
        app=db.execute(select(applications).where(applications.c.id==aid)).mappings().one()
        candidate=db.execute(select(candidates).where(candidates.c.id==app['candidate_id'])).mappings().one()
        parent=db.execute(select(conversations).where(conversations.c.id==candidate['conversation_id'])).mappings().one()
        oid=policy.create(db,actor='alice',project=project,parent=parent,action='req-review',object_id=candidate['object_id'],request_key='expired',request_hash='h',source_hash='h')
        db.execute(update(operations).where(operations.c.id==oid).values(origin_turn_id=candidate['turn_id'],state='blocked',recovery_expires_at='2000-01-01T00:00:00+00:00'))
        assert classify(db,policy.row(db,oid))=='cleanup_blocked'
        db.execute(update(turns).where(turns.c.id==candidate['turn_id']).values(status='unknown'))
        assert classify(db,policy.row(db,oid))=='active_protected'


@pytest.mark.parametrize('state,lease', [('active','claim'),('blocked',None),('waiting',None)])
def test_ordinary_controller_cannot_bypass_recovery_claim_or_block(writing,monkeypatch,state,lease):
    from app.governance import controller, recovery_controller, recovery_retention
    factory,project,before,_,_=writing;aid=queue(writing)
    with factory() as db:
        app=db.execute(select(applications).where(applications.c.id==aid)).mappings().one()
        candidate=db.execute(select(candidates).where(candidates.c.id==app['candidate_id'])).mappings().one()
        parent=db.execute(select(conversations).where(conversations.c.id==candidate['conversation_id'])).mappings().one()
        oid=policy.create(db,actor='alice',project=project,parent=parent,action='req-review',object_id=candidate['object_id'],request_key='claimed',request_hash='hash',source_hash='source',candidate_id=candidate['id'])
        db.execute(update(operations).where(operations.c.id==oid).values(state=state,lease_owner=lease))
        db.commit()
    monkeypatch.setattr(recovery_controller,'tick',lambda factory:None)
    monkeypatch.setattr(recovery_retention,'sweep',lambda db:None)
    controller.tick(factory)
    assert stable(project.root).files==before
    with factory() as db:assert db.scalar(select(applications.c.state).where(applications.c.id==aid))=='pending'
