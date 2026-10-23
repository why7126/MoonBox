"""BUG-0047: exercise actual private store and preparation boundaries."""
import pytest
from app.governance import store
from app.governance.direct_command_journal import (
    DIRECT_ACTIONS, prepare, record_id, record_block_reason, completion_block_reason,
)
from app.governance.preparation import _check_command_record, collect_error_code
from app.chat.service import ChatError


@pytest.fixture
def record(tmp_path, monkeypatch):
    private = tmp_path / 'private'
    private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(private))
    return 'isolated-conversation', 'isolated-request', private


@pytest.mark.parametrize('action', sorted(DIRECT_ACTIONS))
def test_supported_action_producer_consumer_contract(record, action):
    cid, key, _ = record
    store.write(record_id(cid,key), 'baseline', {
        'action': action, 'object_id': 'REQ-9000-isolated', 'revision': 'baseline',
    })
    prepare(cid,key,action,'REQ-9000-isolated','baseline')
    _check_command_record(cid,key,action,'REQ-9000-isolated','baseline')
    assert record_block_reason(cid,key) is None


@pytest.mark.parametrize('damage,expected', [
    ('missing','direct_command_operation_missing'),
    ('invalid','direct_command_operation_invalid'),
    ('identity','direct_command_identity_mismatch'),
])
def test_incomplete_record_fails_before_execution_and_preserves_baseline(record,damage,expected):
    cid,key,private=record;rid=record_id(cid,key)
    baseline={'action':'req-review','object_id':'REQ-9000-isolated','revision':'original'}
    store.write(rid,'baseline',baseline)
    if damage=='invalid': store.write(rid,'operation',[])
    if damage=='identity': prepare(cid,key,'bug-review','BUG-9000-other','other')
    with pytest.raises(ChatError) as error:
        _check_command_record(cid,key,'req-review','REQ-9000-isolated','original')
    assert error.value.kind==expected
    assert error.value.details=={'phase':'preparation'}
    assert store.read(rid,'baseline')==baseline
    assert completion_block_reason(cid,key,private)==expected


def test_ordinary_chat_has_no_command_gate(record):
    cid,key,private=record
    assert completion_block_reason(cid,key,private) is None


@pytest.mark.parametrize('reason', [
    'direct_command_recovery_blocked', 'direct_command_operation_missing',
    'direct_command_operation_invalid', 'direct_command_identity_mismatch',
])
def test_candidate_diagnostic_preserves_terminal_record_failure(reason):
    class Database:
        def scalar(self, statement): return reason
    assert collect_error_code(Database(),'isolated-turn','failed')==reason


def test_prepare_retry_preserves_terminal_evidence(record):
    cid,key,_=record;rid=record_id(cid,key)
    store.write(rid,'baseline',{'action':'req-review','object_id':'REQ-9000-isolated','revision':'original'})
    prepare(cid,key,'req-review','REQ-9000-isolated','original')
    operation=store.read(rid,'operation');operation.update(phase='terminal',terminal_status='failed')
    store.write(rid,'operation',operation)
    prepare(cid,key,'req-review','REQ-9000-isolated','original')
    assert store.read(rid,'operation')==operation
    with pytest.raises(ValueError,match='identity_mismatch'):
        prepare(cid,key,'req-review','REQ-9000-isolated','changed')
    assert store.read(rid,'operation')==operation


def test_worker_preflight_rejects_lost_directory_before_candidate_or_executor(record):
    from app.governance.preparation import initialize_workspace
    cid,key,private=record
    class Result:
        def mappings(self): return self
        def first(self): return {'prompt':'/req-review REQ-9000-isolated','client_request_id':key}
    class Database:
        def execute(self, statement): return Result()
    with pytest.raises(ChatError) as error:
        initialize_workspace(Database(),{'id':cid,'active_turn_id':'turn'},private,private)
    assert error.value.kind=='direct_command_operation_missing'


def test_corrupt_record_does_not_break_terminal_accounting(record):
    from app.governance.direct_command_journal import terminal, observe
    cid,key,private=record
    store.write(record_id(cid,key),'operation',[])
    assert observe(cid,key,'tool','completed',private) is None
    assert terminal(cid,key,'failed',private) is None
    assert store.read(record_id(cid,key),'operation')==[]


def test_prepare_write_interruption_is_explicit_and_does_not_launch_candidate(record, monkeypatch):
    from types import SimpleNamespace
    from app.governance import preparation
    cid,key,_=record
    monkeypatch.setattr('app.governance.recovery_service.prepare_explicit_regeneration',lambda *a:None)
    monkeypatch.setattr(preparation,'_current_prepared_candidate',lambda *a:None)
    monkeypatch.setattr(preparation.scope,'authorize',lambda *a,**k:SimpleNamespace(binding_revision='binding'))
    monkeypatch.setattr(preparation,'_preflight_object_session',lambda *a:{'id':'REQ-9000-isolated','version':'original'})
    class Reader:
        def __init__(self,*a):pass
        def snapshot(self):return SimpleNamespace(revision='original',files={})
        def entries(self,*a):return []
    monkeypatch.setattr(preparation,'ProjectReader',Reader)
    original=store.write
    def interrupted(rid,name,value):
        if name=='operation':raise OSError('injected write interruption')
        return original(rid,name,value)
    monkeypatch.setattr(store,'write',interrupted)
    with pytest.raises(ChatError) as error:
        preparation.prepare_command_snapshot(None,'actor',{'id':cid,'space_id':'space','repository_id':'repo'},'/req-review REQ-9000-isolated',key)
    assert error.value.kind=='direct_command_preparation_failed'
    assert store.read(record_id(cid,key),'baseline')['revision']=='original'
    assert not (record[2]/record_id(cid,key)/'operation.json').exists()
    monkeypatch.setattr(store,'write',original)
    with pytest.raises(ChatError) as retry:
        preparation.prepare_command_snapshot(None,'actor',{'id':cid,'space_id':'space','repository_id':'repo'},'/req-review REQ-9000-isolated',key)
    assert retry.value.kind=='direct_command_operation_missing'
    assert store.read(record_id(cid,key),'baseline')['revision']=='original'
    assert not (record[2]/record_id(cid,key)/'operation.json').exists()


def test_malformed_observation_step_is_diagnosed_not_executed(record):
    from app.governance.direct_command_journal import terminal
    cid,key,private=record;rid=record_id(cid,key)
    prepare(cid,key,'req-review','REQ-9000-isolated','revision')
    operation=store.read(rid,'operation')
    operation['steps']=[{'item_key':'key','source_revision':{},'workflow_sync':False,'sync_succeeded':False}]
    store.write(rid,'operation',operation)
    assert completion_block_reason(cid,key,private)=='direct_command_operation_invalid'
    assert terminal(cid,key,'failed',private) is None
    assert store.read(rid,'operation')==operation


def test_existing_candidate_still_prepares_each_new_request(record, monkeypatch):
    from types import SimpleNamespace
    from app.governance import preparation, completion_recovery, durable_recovery
    monkeypatch.setattr(durable_recovery, 'create', lambda *args, **kwargs: None)
    monkeypatch.setattr('app.governance.recovery_service.prepare_explicit_regeneration', lambda *args: None)
    cid,key,_=record
    monkeypatch.setattr(preparation,'_current_prepared_candidate',lambda *a:{'id':'retained-candidate'})
    monkeypatch.setattr(preparation.scope,'authorize',lambda *a,**k:SimpleNamespace(binding_revision='binding'))
    monkeypatch.setattr(preparation,'_preflight_object_session',lambda *a:{'id':'REQ-9000-isolated','version':'original'})
    class Reader:
        def __init__(self,*a):pass
        def snapshot(self):return SimpleNamespace(revision='original',files={})
        def entries(self,*a):return []
    monkeypatch.setattr(preparation,'ProjectReader',Reader)
    def forbidden(*a,**k):raise AssertionError('existing candidate must not be replaced')
    monkeypatch.setattr(completion_recovery,'prepare_completion',forbidden)
    preparation.prepare_command_snapshot(None,'actor',{'id':cid,'space_id':'space','repository_id':'repo'},'/req-review REQ-9000-isolated',key)
    assert record_block_reason(cid,key,action='req-review',object_id='REQ-9000-isolated',revision='original') is None


def test_worker_preflight_requires_durable_operation_before_model(record, monkeypatch):
    from app.governance import preparation
    cid, key, private = record
    store.write(record_id(cid,key),'baseline',{'action':'req-review','object_id':'REQ-9000-isolated','revision':'original'})
    prepare(cid,key,'req-review','REQ-9000-isolated','original')
    monkeypatch.setattr('app.governance.recovery_capabilities.require',lambda action:None)
    class Result:
        def __init__(self,value):self.value=value
        def mappings(self):return self
        def first(self):return self.value
    class Database:
        def __init__(self):self.calls=0
        def execute(self,statement):
            self.calls+=1
            return Result({'prompt':'/req-review REQ-9000-isolated','client_request_id':key} if self.calls==1 else None)
    with pytest.raises(ChatError) as error:
        preparation.initialize_workspace(Database(),{'id':cid,'active_turn_id':'turn'},private,private)
    assert error.value.kind=='recovery_operation_incomplete'
