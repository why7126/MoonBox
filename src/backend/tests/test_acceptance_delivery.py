"""Real Chat admission transaction; executor availability and source probe are substituted."""
import pytest
from sqlalchemy import insert,select,update
from test_chat import chat
from test_acceptance_archive import settled
from app.chat.schema import turns,conversations
from app.moonbox_core.schema import execution_receipts
from app.verification.acceptance_schema import deliveries
from app.verification.acceptance_state import Conflict
from app.verification import acceptance_delivery as delivery


def prepared(chat,monkeypatch,tmp_path):
    state,item=settled(chat,monkeypatch,tmp_path);_,factory=chat
    with factory.begin() as db:
        from app.chat.schema import reservations
        from app.chat.service import identity
        db.execute(insert(reservations).values(**identity(),turn_id=item['source_turn_id'],owner_id='alice',
            space_id='space',period='2026-10',tokens=0,bytes=0,status='settled',actual_tokens=0))
        db.execute(update(turns).where(turns.c.id==item['source_turn_id']).values(status='failed'))
        db.execute(update(conversations).where(conversations.c.id==item['conversation_id']).values(active_turn_id=None))
        db.execute(insert(execution_receipts).values(turn_id=item['source_turn_id'],executor_closed=1,files_collected=1,scope_json='["src"]'))
    monkeypatch.setattr(delivery,'validate_inputs',lambda db,row:None)
    monkeypatch.setattr('app.chat.isolated.allowed',lambda *args:True)
    monkeypatch.setattr('app.moonbox_core.migration.ensure_binding',lambda *args:None)
    return state,item


def test_once_only_enqueue_preserves_original_terminal(chat,monkeypatch,tmp_path):
    state,item=prepared(chat,monkeypatch,tmp_path);_,factory=chat
    first=delivery.continue_once(factory,item['id'])
    assert first['state']=='queued'
    assert delivery.continue_once(factory,item['id'])==first
    with factory() as db:
        assert len(db.execute(select(deliveries)).all())==1
        assert db.scalar(select(turns.c.status).where(turns.c.id==item['source_turn_id']))=='failed'
        assert len(db.execute(select(turns)).all())==2
    assert state.get(item['id'])['resume_count']==1
    current=state.get(item['id']);state.cancel(item['id'],current['version'])
    with factory() as db,pytest.raises(Conflict,match='acceptance_continuation_stopped'):
        delivery.execution_guard(db,first['turn_id'],starting=True)


def test_stop_racing_admission_rolls_back_queue_and_budget(chat,monkeypatch,tmp_path):
    state,item=prepared(chat,monkeypatch,tmp_path);_,factory=chat
    from app.chat import service
    original=service.request_turn
    def stopped_before_admission(db,*args,**kwargs):
        db.rollback()
        current=state.get(item['id']);state.cancel(item['id'],current['version'])
        return original(db,*args,**kwargs)
    monkeypatch.setattr(service,'request_turn',stopped_before_admission)
    with pytest.raises(Conflict,match='cancelled'):delivery.continue_once(factory,item['id'])
    with factory() as db:
        assert len(db.execute(select(turns)).all())==1
        assert not db.execute(select(deliveries)).all()
        assert db.scalar(select(conversations.c.active_turn_id)) is None


@pytest.mark.parametrize('status,closed',[('unknown',0),('running',0),('stopped',1),('failed',0)])
def test_never_infers_termination_or_resumes_user_stop(chat,monkeypatch,tmp_path,status,closed):
    state,item=prepared(chat,monkeypatch,tmp_path);_,factory=chat
    with factory.begin() as db:
        db.execute(update(turns).where(turns.c.id==item['source_turn_id']).values(status=status))
        db.execute(update(execution_receipts).values(executor_closed=closed))
    with pytest.raises(Conflict,match='source_execution_unconfirmed'):delivery.continue_once(factory,item['id'])
    assert state.get(item['id'])['resume_count']==0


def test_uncertain_live_delivery_never_creates_second_consumer(chat,monkeypatch,tmp_path):
    state,item=prepared(chat,monkeypatch,tmp_path);_,factory=chat
    from app.chat.service import identity
    from app.verification.acceptance_schema import tool_waits
    with factory.begin() as db:
        db.execute(insert(tool_waits).values(**identity(),source_turn_id=item['source_turn_id'],
            operation_id=item['id'],call_id='call-test',generation=1,state='dispatching'))
    with pytest.raises(Conflict,match='delivery_unconfirmed'):delivery.continue_once(factory,item['id'])
    assert state.get(item['id'])['resume_count']==0


@pytest.mark.parametrize('used,reason',[(None,'source_budget_unconfirmed'),(100,'resume_budget_exhausted')])
def test_original_finite_budget_cannot_reset(chat,monkeypatch,tmp_path,used,reason):
    state,item=prepared(chat,monkeypatch,tmp_path);_,factory=chat
    from app.chat.schema import reservations
    with factory.begin() as db:db.execute(update(reservations).values(tokens=100,actual_tokens=used))
    with pytest.raises(Conflict,match=reason):delivery.continue_once(factory,item['id'])
    assert state.get(item['id'])['resume_count']==0


def test_continuation_keeps_only_original_remaining_tokens(chat,monkeypatch,tmp_path):
    state,item=prepared(chat,monkeypatch,tmp_path);_,factory=chat
    from app.chat.schema import reservations
    with factory.begin() as db:db.execute(update(reservations).values(tokens=100,actual_tokens=70))
    result=delivery.continue_once(factory,item['id'])
    with factory() as db:assert delivery.token_limit(db,result['turn_id'])==30


def test_linked_turn_cannot_reset_automatic_continuation_chain(chat,monkeypatch,tmp_path):
    state,item=prepared(chat,monkeypatch,tmp_path);_,factory=chat
    successor=delivery.continue_once(factory,item['id'])
    from app.verification.acceptance_service import create
    with factory() as db,pytest.raises(Conflict,match='resume_budget_exhausted'):
        create(db,factory,'alice',item['conversation_id'],successor['turn_id'],item['change_id'],'new-budget')
