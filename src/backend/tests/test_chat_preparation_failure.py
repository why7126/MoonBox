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


@pytest.mark.parametrize('code', [
    'direct_command_preparation_failed', 'direct_command_operation_missing',
    'direct_command_operation_invalid', 'direct_command_identity_mismatch',
    'direct_command_baseline_missing', 'direct_command_baseline_invalid',
])
def test_review_record_preflight_retains_reason_and_zero_model_usage(chat, capsys, code):
    client,factory=chat;token=claimed(client,factory)
    assert fail_preparation(factory,token,service.ChatError(2604,'记录异常',kind=code))
    with factory() as db:
        row=db.execute(select(turns).where(turns.c.id==token['turn_id'])).mappings().one()
        assert (row['status'],row['error_code'],row['executor_turn_id'])==('failed',code,None)
        assert db.scalar(select(reservations.c.actual_tokens).where(reservations.c.turn_id==row['id']))==0
        assert db.scalar(select(conversations.c.active_turn_id).where(conversations.c.id==token['conversation_id'])) is None
    assert code in capsys.readouterr().out


def test_preflight_failure_checkpoints_existing_operation_without_model(chat, monkeypatch):
    from types import SimpleNamespace
    from sqlalchemy import insert
    from app.chat.schema import governance_candidates as candidates
    from app.governance import durable_recovery as policy
    from app.governance.recovery_schema import operations
    client,factory=chat;token=claimed(client,factory)
    monkeypatch.setenv('MOONBOX_CHAT_RETENTION','{"executor_delete_seconds":86400,"backup_expiry_seconds":86400}')
    with factory() as db:
        parent=db.execute(select(conversations).where(conversations.c.id==token['conversation_id'])).mappings().one()
        candidate={**service.identity(),'actor_id':'alice','space_id':parent['space_id'],'repository_id':parent['repository_id'],
            'scope_key':'scope','conversation_id':parent['id'],'prepared_turn_id':token['turn_id'],
            'object_id':'REQ-9000-preflight','action':'req-review','binding_revision':'binding','baseline_hash':'baseline','state':'prepared'}
        db.execute(insert(candidates).values(**candidate))
        oid=policy.create(db,actor='alice',project=SimpleNamespace(key='scope',binding_revision='binding'),parent=parent,
            action='req-review',object_id=candidate['object_id'],request_key='preflight',request_hash='hash',source_hash='baseline',candidate_id=candidate['id'])
        db.execute(update(operations).where(operations.c.id==oid).values(origin_turn_id=token['turn_id'],stage='generation'));db.commit()
    assert fail_preparation(factory,token,service.ChatError(2605,'unavailable',kind='recovery_capability_unavailable'))
    with factory() as db:
        current=policy.row(db,oid)
        assert current['state']=='blocked' and current['execution_terminal']=='failed'
        assert current['reason_code']=='recovery_capability_unavailable' and current['recovery_expires_at']
        assert db.scalar(select(candidates.c.state).where(candidates.c.id==candidate['id']))=='rejected'
        assert db.scalar(select(turns.c.executor_turn_id).where(turns.c.id==token['turn_id'])) is None
        assert current['manual_count']==current['auto_retry_count']==0
