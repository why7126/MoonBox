"""Persistent acceptance control: synthetic execution, real SQL transactions."""
import pytest
import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.verification.acceptance_schema import TABLES, operations, attempts
from app.verification.acceptance_state import AcceptanceState, Conflict

@pytest.fixture
def state(tmp_path):
    url=os.getenv('ACCEPTANCE_TEST_DATABASE_URL',f'sqlite:///{tmp_path}/state.db')
    if not url.startswith('sqlite:') and not url.rsplit('/',1)[-1].startswith('acceptance_test_'):
        raise ValueError('disposable_test_database_required')
    engine = create_engine(url)
    for table in TABLES: table.create(engine)
    clock = [1000]
    result = AcceptanceState(sessionmaker(engine), clock=lambda:clock[0])
    result.clock_value = clock
    yield result
    for table in reversed(TABLES):table.drop(engine)
    engine.dispose()

def create(state, key='request', fingerprint='a'*64):
    return state.create(actor='alice', space='space', repository='repo', conversation='conversation',
        turn='turn', change='add-test', request_key=key, binding='b'*64,
        input_digest=fingerprint, plan={'checks':[{'id':'AC-001','dependencies':[],'inputs':['src/app.py']}]})

def test_idempotent_same_key_rejects_changed_input(state):
    first = create(state)
    assert create(state)['id'] == first['id']
    with pytest.raises(Conflict, match='input_conflict'): create(state, fingerprint='c'*64)
    with state.factory() as db:
        assert len(db.execute(select(operations)).all()) == 1

def test_stop_fences_late_worker_and_never_resumes(state):
    item = create(state)
    token = state.claim(item['id'], 'worker')
    stopped = state.cancel(item['id'], expected_version=token['version'])
    with pytest.raises(Conflict): state.advance(token, 'running')
    with pytest.raises(Conflict, match='cancelled'): state.resume(item['id'], stopped['version'])
    assert state.get(item['id'])['cancel_requested']

def test_recovery_does_not_reset_deadline_or_claim_live_worker(state):
    item=create(state); token=state.claim(item['id'],'worker')
    with pytest.raises(Conflict, match='execution_busy'):state.claim(item['id'],'other')
    state.clock_value[0] += 301
    with pytest.raises(Conflict, match='termination_unconfirmed'):state.claim(item['id'],'other')
    fresh=state.recover(item['id'], token['epoch'], terminated=True)
    assert fresh['expires_at']==token['expires_at']
    assert fresh['epoch']>token['epoch']
    with pytest.raises(Conflict):state.advance(token,'running')

def test_cleanup_failure_keeps_test_result_separate(state):
    item=create(state); token=state.claim(item['id'],'worker')
    state.result(token,'AC-001','passed', evidence={'kind':'command','digest':'d'*64})
    state.advance(token,'ready');state.advance(token,'running');state.advance(token,'passed')
    state.cleanup(item['id'], released=False)
    view=state.get(item['id'])
    assert view['checks'][0]['status']=='passed'
    assert view['cleanup_state']=='cleanup_failed'
    assert not view['ready']
    state.cleanup(item['id'], released=True)
    assert state.get(item['id'])['ready']

def test_partial_dependency_failure_keeps_independent_work(state):
    plan={'checks':[{'id':'AC-001','dependencies':[],'inputs':['src/a.py']},
        {'id':'AC-002','dependencies':['AC-001'],'inputs':['src/a.py']},
        {'id':'AC-003','dependencies':[],'inputs':['src/b.py']}]}
    item=state.create(actor='alice',space='space',repository='repo',conversation='c',turn='t',
        change='add-test',request_key='key',binding='b'*64,input_digest='a'*64,plan=plan)
    token=state.claim(item['id'],'worker');state.result(token,'AC-001','failed',evidence={})
    assert state.runnable(item['id'])==['AC-003']
    assert state.invalidate(item['id'],['src/a.py'])==['AC-001','AC-002']

def test_resume_counter_and_delivery_are_durable(state):
    item=create(state);token=state.claim(item['id'],'worker')
    assert state.deliver(token, 'result-1', terminated=False) == 'deliver'
    assert state.deliver(token, 'result-1', terminated=False) == 'delivery_pending'
    state.acknowledge_delivery(token,'result-1')
    assert state.deliver(token, 'result-1', terminated=False) == 'already_delivered'
    assert state.deliver(token, 'result-2', terminated=True, authorized=True) == 'resume'
    with pytest.raises(Conflict, match='resume_budget_exhausted'):
        state.deliver(token,'result-3',terminated=True,authorized=True)

def test_invalid_plan_cycle_is_rejected(state):
    with pytest.raises(Conflict, match='plan_invalid'):
        state.create(actor='a',space='s',repository='r',conversation='c',turn='t',change='x',
            request_key='key',binding='b'*64,input_digest='a'*64,
            plan={'checks':[{'id':'AC-001','dependencies':['AC-001'],'inputs':['src/a']} ]})

def test_changed_template_invalidates_retained_results_before_runtime(state):
    item=create(state);token=state.claim(item['id'],'worker')
    state.bind_template(token,'d'*64)
    state.result(token,'AC-001','passed',evidence={'kind':'command','digest':'e'*64})
    state.recover(item['id'],token['epoch'],terminated=True)
    current=state.cleanup(item['id'],released=True)
    resumed=state.resume(item['id'],current['version'])
    assert resumed['template_digest']=='d'*64
    assert resumed['checks'][0]['status']=='passed'
    next_token=state.claim(item['id'],'second-worker')
    with pytest.raises(Conflict,match='template_changed'):
        state.bind_template(next_token,'f'*64)
    current=state.get(item['id'])
    assert current['status']=='blocked' and current['checks'][0]['status']=='stale'
    assert current['checks'][0]['evidence_json']!='{}'
    with pytest.raises(Conflict,match='epoch_conflict'):state.heartbeat(next_token)

def test_public_projection_excludes_private_control_facts(state):
    from app.verification.acceptance_service import public
    item=create(state)
    view=public(item)
    assert view['id']==item['id']
    assert not {'actor_id','request_hash','plan_json','binding_revision','epoch','lease_until'} & view.keys()
    assert view['checks']==[{'ac_id':'AC-001','status':'pending','reason_code':None,'evidence_available':False}]

@pytest.mark.parametrize('evidence,reason', [
    ({'kind':'command','digest':'not-a-digest'},None),
    ({'kind':'command','digest':'d'*64},'secret=value'),
    (None,None),
])
def test_result_metadata_rejects_unbounded_or_secret_payloads(state,evidence,reason):
    token=state.claim(create(state)['id'],'worker')
    with pytest.raises(Conflict):state.result(token,'AC-001','passed',evidence=evidence,reason=reason)

def test_late_heartbeat_and_result_cannot_follow_stop(state):
    token=state.claim(create(state)['id'],'worker')
    state.cancel(token['id'],token['version'])
    with pytest.raises(Conflict,match='cancelled'):state.heartbeat(token)
    with pytest.raises(Conflict,match='cancelled'):
        state.result(token,'AC-001','passed',evidence={'kind':'command','digest':'d'*64})
    assert state.get(token['id'])['checks'][0]['status']=='pending'


def test_resource_reservations_do_not_expire_into_free_capacity(state):
    from app.verification.acceptance_resources import reserve,release,GIB
    limits=dict(available_cpu=16,available_memory=32*GIB,available_disk=100*GIB,hard_disk_limit=True)
    first=dict(id='one',space_id='space-one',expires_at=1)
    reserve(state.factory,first,**limits)
    with pytest.raises(Conflict,match='environment_concurrency_limit'):
        reserve(state.factory,dict(id='two',space_id='space-one',expires_at=1),**limits)
    reserve(state.factory,dict(id='two',space_id='space-two',expires_at=1),**limits)
    with pytest.raises(Conflict,match='environment_concurrency_limit'):
        reserve(state.factory,dict(id='three',space_id='space-three',expires_at=1),**limits)
    with pytest.raises(Conflict,match='cleanup_unconfirmed'):
        release(state.factory,'one',resources_confirmed_absent=False)
    assert release(state.factory,'one',resources_confirmed_absent=True)==1
    reserve(state.factory,dict(id='three',space_id='space-three',expires_at=1),**limits)


def test_controller_runs_independent_checks_and_keeps_cleanup_failure(state):
    from app.verification.acceptance_controller import Controller
    calls=[]
    class Runtime:
        def prepare(self,token):calls.append('prepare')
        def execute(self,ac):
            calls.append(ac)
            return {'status':'passed','evidence':{'kind':'command','digest':'d'*64}}
        def interrupt(self):calls.append('interrupt')
        def cleanup(self):calls.append('cleanup');return False
        def terminated(self):return True
    item=create(state)
    result=Controller(state,Runtime(),lambda oid:None).run(item['id'],'worker')
    assert calls==['prepare','AC-001','cleanup']
    assert result['status']=='passed' and result['cleanup_state']=='cleanup_failed' and not result['ready']
    assert result['lease_until']==0


def test_controller_stop_inside_check_rejects_result_and_continues_cleanup(state):
    from app.verification.acceptance_controller import Controller
    class Runtime:
        def prepare(self,token):self.token=token
        def execute(self,ac):
            current=state.get(self.token['id']);state.cancel(current['id'],current['version'])
            return {'status':'passed','evidence':{'kind':'command','digest':'d'*64}}
        def interrupt(self):pass
        def cleanup(self):return True
        def terminated(self):return True
    item=create(state)
    result=Controller(state,Runtime(),lambda oid:None).run(item['id'],'worker')
    assert result['status']=='cancelled' and result['cleanup_state']=='released'
    assert result['checks'][0]['status']=='pending' and not result['ready']


def test_cleanup_retries_preserve_backoff_and_stop_after_three(state):
    from app.verification.acceptance_cleanup import record,due
    item=create(state)
    record(state,item['id'],False)
    assert not due(state,state.get(item['id']))
    state.clock_value[0]+=30
    assert due(state,state.get(item['id']))
    record(state,item['id'],False)
    state.clock_value[0]+=119
    assert not due(state,state.get(item['id']))
    state.clock_value[0]+=1
    assert due(state,state.get(item['id']))
    record(state,item['id'],False)
    state.clock_value[0]+=600
    assert not due(state,state.get(item['id']))


def test_resume_preserves_history_and_original_budgets(state):
    item=create(state);token=state.claim(item['id'],'worker')
    state.advance(token,'ready');state.advance(token,'running')
    state.result(token,'AC-001','blocked',evidence={},reason='temporary_unavailable')
    state.recover(item['id'],token['epoch'],terminated=True)
    state.cleanup(item['id'],released=True)
    previous=state.get(item['id'])
    resumed=state.resume(item['id'],previous['version'])
    assert resumed['attempt_id']!=previous['attempt_id']
    assert resumed['expires_at']==previous['expires_at']
    assert resumed['checks_deadline']==previous['checks_deadline']
    assert resumed['checks'][0]['status']=='pending'
    with state.factory() as db:
        assert len(db.execute(select(attempts)).all())==2


def test_identity_secret_not_in_database_and_cancellation_rejects_issue(state,tmp_path):
    from app.verification.acceptance_identity import IdentityLease
    from app.verification.acceptance_schema import identities
    token=state.claim(create(state)['id'],'worker')
    lease=IdentityLease(state,tmp_path/'private',clock=state.clock)
    issued=lease.issue(token,'reader',approved_roles=['reader'])
    assert 'password' not in issued
    path=tmp_path/'private'/issued['identity_ref']
    assert path.stat().st_mode&0o777==0o600
    with state.factory() as db:
        assert 'password' not in str(dict(db.execute(select(identities)).mappings().one()))
    current=state.get(token['id']);state.cancel(current['id'],current['version'])
    with pytest.raises(Conflict):lease.issue(token,'reader',approved_roles=['reader'])
    assert len(list((tmp_path/'private').iterdir()))==1
    isolated=[]
    assert not lease.revoke(token['attempt_id'],revoke_application=lambda ref:False,isolate_network=lambda:isolated.append(True))
    assert isolated==[True] and not path.exists()


def test_identity_revoke_exceptions_remove_private_media_and_keep_failure(state,tmp_path):
    from app.verification.acceptance_identity import IdentityLease
    from app.verification.acceptance_schema import identities
    token=state.claim(create(state)['id'],'worker')
    lease=IdentityLease(state,tmp_path/'private',clock=state.clock)
    issued=lease.issue(token,'reader',approved_roles=['reader'])
    def fail(*args):raise RuntimeError('private failure')
    assert not lease.revoke(token['attempt_id'],revoke_application=fail,isolate_network=fail)
    assert not (tmp_path/'private'/issued['identity_ref']).exists()
    with state.factory() as db:
        assert db.scalar(select(identities.c.revocation_state))=='revocation_failed'


def test_host_capacity_limits_eligible_slots(state):
    from app.verification.acceptance_resources import reserve,GIB
    budget=dict(available_cpu=4,available_memory=8*GIB,available_disk=22*GIB,hard_disk_limit=True)
    first=state.claim(create(state)['id'],'worker')
    reserve(state.factory,first,**budget)
    second={**first,'id':'another','space_id':'another-space'}
    with pytest.raises(Conflict,match='environment_concurrency_limit'):
        reserve(state.factory,second,**budget)


def test_resume_action_requires_released_resources_and_remaining_time(state):
    from app.verification.acceptance_service import public
    item=create(state)
    view={**item,'status':'blocked','lease_until':0,'expires_at':None,'cleanup_state':'cleanup_failed'}
    assert 'resume' not in public(view,writable=True)['allowed_actions']
    view['cleanup_state']='released'
    assert 'resume' in public(view,writable=True)['allowed_actions']
    view['expires_at']=1
    assert 'resume' not in public(view,writable=True)['allowed_actions']
