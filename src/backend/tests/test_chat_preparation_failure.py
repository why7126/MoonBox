import pytest
from sqlalchemy import select, update
from test_chat import chat, create
from app.chat import worker, service
from app.chat.admission import enqueue
from app.chat.schema import turns, conversations, reservations, events
from app.chat.preparation_failure import fail_preparation, recover_preparation_failures


def claimed(client, factory):
    cid = create(client)
    limits = dict(user_concurrency=1,space_concurrency=2,user_monthly_tokens=10000,space_monthly_tokens=20000,user_storage_bytes=1000000,space_storage_bytes=2000000,turn_reserved_tokens=1000,turn_reserved_bytes=100000)
    with factory() as db:
        enqueue(db,'alice',cid,'prepare','test',limits)
        return worker.claim(db,'test')


@pytest.mark.parametrize('toolchain_failure', [False, True])
def test_preparation_failure_releases_lock_and_settles_without_leaking(chat,capsys,toolchain_failure):
    client,factory=chat; token=claimed(client,factory)
    error=service.ChatError(2604,'secret=/private/work',kind='workspace_unapplied_changes')
    code='workspace_unapplied_changes'
    if toolchain_failure:
        from app.chat.app_server import ExecutorError
        code='container_toolchain_unavailable'
        error=ExecutorError(code)
    assert fail_preparation(factory,token,error)
    assert not fail_preparation(factory,token,error)
    with factory() as db:
        row=db.execute(select(turns).where(turns.c.id==token['turn_id'])).mappings().one()
        assert row['status']=='failed' and row['error_code']==code
        assert db.scalar(select(conversations.c.active_turn_id).where(conversations.c.id==token['conversation_id'])) is None
        assert db.scalar(select(reservations.c.actual_tokens).where(reservations.c.turn_id==row['id']))==0
        assert db.scalar(select(events.c.payload).where(events.c.turn_id==row['id']))
    output=capsys.readouterr().out
    assert code in output and '/private' not in output and 'secret' not in output


def test_stale_governance_preparation_keeps_actionable_error_code(chat,capsys):
    client,factory=chat;token=claimed(client,factory)
    error=service.ChatError(2606,'治理文件版本已变化',kind='workspace_fact_source_stale')
    assert fail_preparation(factory,token,error)
    with factory() as db:
        row=db.execute(select(turns.c.status,turns.c.error_code).where(turns.c.id==token['turn_id'])).one()
        assert row==('failed','workspace_fact_source_stale')
    assert 'workspace_fact_source_stale' in capsys.readouterr().out


@pytest.mark.parametrize('external,code,recovered',[(None,'platform_workspace_unavailable',True),('external','platform_workspace_unavailable',False),(None,'worker_heartbeat_lost',False)])
def test_recovery_only_proven_preparation_failures(chat,external,code,recovered):
    client,factory=chat; token=claimed(client,factory)
    with factory() as db:
        db.execute(update(turns).where(turns.c.id==token['turn_id']).values(status='unknown',error_code=code,executor_turn_id=external));db.commit()
    recover_preparation_failures(factory)
    with factory() as db:
        assert db.scalar(select(turns.c.status).where(turns.c.id==token['turn_id']))==('failed' if recovered else 'unknown')


def test_preparation_failure_fences_old_generation(chat):
    client,factory=chat; token=claimed(client,factory)
    assert not fail_preparation(factory,{**token,'generation':token['generation']-1},ValueError())


def test_unapplied_workspace_is_preserved(chat,tmp_path):
    from app.governance.preparation import _checkpoint_applied_workspace
    client,factory=chat; token=claimed(client,factory)
    document=tmp_path/'requirement.md';document.write_text('preserved result')
    with factory() as db, pytest.raises(service.ChatError) as caught:
        _checkpoint_applied_workspace(db,{'id':token['conversation_id']},tmp_path)
    assert caught.value.kind=='workspace_unapplied_changes'
    assert document.read_text()=='preserved result'


def test_claim_toolchain_failure_is_terminal_before_model(chat, tmp_path):
    from app.chat.app_server import ExecutorError
    from app.chat.execution import run_claim
    client, factory = chat
    token = claimed(client, factory)
    work = tmp_path / token['conversation_id']; work.mkdir()
    (work / 'existing.md').write_text('preserved')
    calls = []
    def server(path):
        calls.append(path)
        raise ExecutorError('container_toolchain_unavailable')
    assert run_claim(factory, token, work, server) == 'failed'
    assert calls == [work]
    assert (work / 'existing.md').read_text() == 'preserved'
    with factory() as db:
        row = db.execute(select(turns).where(turns.c.id == token['turn_id'])).mappings().one()
        assert row['status'] == 'failed'
        assert row['error_code'] == 'container_toolchain_unavailable'
        assert row['executor_turn_id'] is None
        assert db.scalar(select(reservations.c.actual_tokens).where(reservations.c.turn_id == row['id'])) == 0
        assert db.scalar(select(conversations.c.active_turn_id).where(conversations.c.id == token['conversation_id'])) is None
