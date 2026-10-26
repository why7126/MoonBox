from sqlalchemy import select
from test_chat import chat, create
from app.chat import worker, settings
from app.chat.admission import enqueue
from app.chat.preparation_failure import fail_preparation
from app.chat.content_schema import prepare_attempts
from app.chat.schema import turns, events
from app.governance.prepare_recovery import request


def test_proven_preparation_resume_keeps_turn_and_history_and_deduplicates(chat, monkeypatch):
    client, factory = chat; cid = create(client)
    monkeypatch.setattr('app.chat.isolated.allowed', lambda *args: True)
    with factory() as db:
        turn = enqueue(db, 'alice', cid, 'one', 'synthetic', settings.execution_limits())
        token = worker.claim(db, 'worker')
    assert fail_preparation(factory, token, RuntimeError('synthetic'))
    with factory() as db:
        assert request(db, 'alice', turn['id'], 'check', 'check')['eligibility']
        first = request(db, 'alice', turn['id'], 'resume_prepare', 'resume')
        second = request(db, 'alice', turn['id'], 'resume_prepare', 'resume')
        assert first['attempt_id'] == second['attempt_id']
        assert first['turn_id'] == turn['id']
        assert db.scalar(select(turns.c.status).where(turns.c.id == turn['id'])) == 'queued'
        attempt = db.execute(select(prepare_attempts)).mappings().one()
        assert attempt['prior_status'] == 'failed'
        token2 = worker.claim(db, 'worker2')
    assert fail_preparation(factory, token2, RuntimeError('synthetic second failure'))
    with factory() as db:
        failures = list(db.scalars(select(events.c.id).where(events.c.source_id.startswith('workspace-prepare-failed'))))
        assert len(failures) == 2
        assert db.scalar(select(prepare_attempts.c.state)) == 'failed'


def test_start_request_without_ack_is_not_safe_to_resume(chat):
    client, factory = chat; cid = create(client)
    with factory() as db:
        turn = enqueue(db, 'alice', cid, 'one', 'synthetic', settings.execution_limits())
        token = worker.claim(db, 'worker')
        worker.record_event(db, token, 'runner:start-requested', 'execution.state', {'stage': 'executor_start'})
    assert not fail_preparation(factory, token, RuntimeError('synthetic'))
    with factory() as db:
        result = request(db, 'alice', turn['id'], 'check', 'check')
        assert not result['eligibility']
        assert result['reason'] == 'execution_state_unknown'


def test_repeated_prepare_does_not_charge_same_saved_prompt_twice(chat,monkeypatch):
    from app.chat.schema import usage_accounts
    client,factory=chat;cid=create(client)
    monkeypatch.setattr('app.chat.isolated.allowed',lambda *args:True)
    with factory() as db:
        turn=enqueue(db,'alice',cid,'one','same persisted prompt',settings.execution_limits())
        token=worker.claim(db,'first')
    assert fail_preparation(factory,token,RuntimeError('synthetic'))
    with factory() as db:
        charged=db.scalar(select(usage_accounts.c.used_bytes).where(usage_accounts.c.id=='user:alice'))
        request(db,'alice',turn['id'],'resume_prepare','second')
        token=worker.claim(db,'second')
    assert fail_preparation(factory,token,RuntimeError('synthetic'))
    with factory() as db:
        assert db.scalar(select(usage_accounts.c.used_bytes).where(usage_accounts.c.id=='user:alice'))==charged
