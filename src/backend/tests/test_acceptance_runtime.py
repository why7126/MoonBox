"""Fault injection for runtime isolation; real Docker has a separate opt-in matrix."""
from types import SimpleNamespace
import pytest
from app.verification.acceptance_runtime import DockerRuntime
from app.verification.acceptance_state import Conflict
from test_acceptance_orchestration import state


def runtime(state,tmp_path):
    template=SimpleNamespace(data={'checks':{'AC-001':{'database':'mysql'},'AC-002':{'database':'sqlite'}}})
    return DockerRuntime(state,template,tmp_path/'private',identity_adapter=SimpleNamespace(revoke_all=lambda:True))


def test_failed_database_does_not_block_independent_backend_or_replay(state,tmp_path,monkeypatch):
    adapter=runtime(state,tmp_path);calls=[]
    def start(backend):
        calls.append(backend)
        if backend=='mysql':raise Conflict('migration_failed')
    monkeypatch.setattr(adapter,'start_database',start)
    monkeypatch.setattr(adapter,'reset_database',lambda:calls.append('discard-unknown-db'))
    adapter.prepare_databases()
    assert calls==['mysql','discard-unknown-db','sqlite']
    with pytest.raises(Conflict,match='migration_failed'):adapter.execute('AC-001')
    assert calls==['mysql','discard-unknown-db','sqlite']


def test_failed_cleanup_prevents_reusing_unknown_environment(state,tmp_path,monkeypatch):
    adapter=runtime(state,tmp_path)
    adapter.engine=SimpleNamespace(cleanup=lambda:False)
    monkeypatch.setattr(adapter,'start_database',lambda _: (_ for _ in ()).throw(Conflict('migration_failed')))
    with pytest.raises(Conflict,match='database_cleanup_unconfirmed'):adapter.prepare_databases()


def test_runtime_disables_unbounded_daemon_logs_and_honors_stop(state,tmp_path):
    adapter=runtime(state,tmp_path);calls=[]
    adapter.engine=SimpleNamespace(command=lambda args,**kwargs:calls.append(args) or 'ok')
    assert adapter.command(['run','--rm','approved-image'])=='ok'
    assert calls==[['run','--log-driver','none','--rm','approved-image']]
    adapter.stopped.set()
    with pytest.raises(Conflict,match='cancelled'):adapter.command(['exec','owned','command'])
    assert len(calls)==1


@pytest.mark.parametrize('subnet',['127.0.0.0/24','0.0.0.0/24','8.8.8.0/24','10.0.0.1/24','10.0.0.0/16','10.0.0.0/30','::1/128'])
def test_network_rejects_non_private_or_unsafe_subnet(state,tmp_path,monkeypatch,subnet):
    adapter=runtime(state,tmp_path)
    monkeypatch.setenv('MOONBOX_ACCEPTANCE_SUBNET',subnet)
    with pytest.raises(Conflict,match='acceptance_subnet_invalid'):adapter.create_network()


def test_network_override_remains_internal_and_owned(state,tmp_path,monkeypatch):
    adapter=runtime(state,tmp_path);calls=[]
    adapter.engine=SimpleNamespace(label_args=lambda:['--label','owned=true'],network='owned-network')
    monkeypatch.setenv('MOONBOX_ACCEPTANCE_SUBNET','10.248.48.0/28')
    monkeypatch.setattr(adapter,'command',lambda args:calls.append(args))
    adapter.create_network()
    assert calls==[['network','create','--internal','--subnet','10.248.48.0/28','--label','owned=true','owned-network']]
