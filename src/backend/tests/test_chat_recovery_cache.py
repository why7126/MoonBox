from pathlib import Path
from types import SimpleNamespace
import os
import pytest
from app.chat import container_server as cs
from app.chat.recovery_runtime import scope
from app.chat.app_server import ExecutorError


@pytest.fixture
def setup(tmp_path, monkeypatch):
    workspace=tmp_path/'work';workspace.mkdir();(workspace/'.git').mkdir()
    runtime=tmp_path/'runtime';runtime.mkdir(mode=0o700)
    auth=tmp_path/'auth.json';auth.write_text('{"OPENAI_API_KEY":"synthetic-test"}')
    calls=[]
    monkeypatch.setattr(cs,'verify_preflight',lambda *_:calls.append('preflight'))
    monkeypatch.setattr(cs,'ContainerAppServer',lambda *args,**kwargs: SimpleNamespace(write=kwargs.get('write')))
    monkeypatch.setattr(cs,'preflight_key',lambda *_:'key')
    cs._PREFLIGHT_CACHE.clear()
    return workspace,runtime,auth,calls


def test_success_reused_but_expiry_and_identity_invalidate(setup,monkeypatch):
    workspace,runtime,auth,calls=setup
    with scope('turn'):
        assert cs.persistent_container_server(workspace,runtime,auth).write is False
        cs.persistent_container_server(workspace,runtime,auth)
        assert len(calls)==1
        monkeypatch.setattr(cs,'preflight_key',lambda *_:'changed')
        cs.persistent_container_server(workspace,runtime,auth)
        assert len(calls)==2
        cs._PREFLIGHT_CACHE['changed']=0
        cs.persistent_container_server(workspace,runtime,auth)
        assert len(calls)==3


def test_failure_never_cached(setup,monkeypatch):
    workspace,runtime,auth,calls=setup
    def fail(*_): calls.append('failed');raise ExecutorError('container_sandbox_preflight_failed')
    monkeypatch.setattr(cs,'verify_preflight',fail)
    with scope('turn'):
        for _ in range(2):
            with pytest.raises(ExecutorError):cs.persistent_container_server(workspace,runtime,auth)
    assert calls==['failed','failed'] and not cs._PREFLIGHT_CACHE


def test_real_key_tracks_image_credentials_policy_and_directory(tmp_path,monkeypatch):
    workspace=tmp_path/'work';workspace.mkdir();(workspace/'.git').mkdir()
    runtime=tmp_path/'runtime';runtime.mkdir();cs.write_profiles(runtime)
    auth=tmp_path/'auth';auth.write_text('synthetic-one')
    image=['sha256:one']
    monkeypatch.setattr(cs.recovery_runtime,'run',lambda *a,**k:SimpleNamespace(returncode=0,stdout=image[0]))
    first=cs.preflight_key(workspace,runtime,auth)
    assert cs.preflight_key(workspace,runtime,auth)==first
    image[0]='sha256:two';second=cs.preflight_key(workspace,runtime,auth);assert second!=first
    auth.write_text('synthetic-two');third=cs.preflight_key(workspace,runtime,auth);assert third!=second
    (runtime/'config.toml').write_text('changed');fourth=cs.preflight_key(workspace,runtime,auth);assert fourth!=third
    (workspace/'.git').rename(workspace/'oldgit');(workspace/'.git').mkdir()
    assert cs.preflight_key(workspace,runtime,auth)!=fourth
    auth.unlink();auth.symlink_to(runtime/'config.toml')
    with pytest.raises(ExecutorError):cs.preflight_key(workspace,runtime,auth)


def test_deadline_prevents_new_container():
    with scope('turn',seconds=-1) as runtime:
        with pytest.raises(ExecutorError):runtime.labels()


def test_unchanged_hint_is_consumed_once_and_changes_force_read():
    from app.chat.recovery_hint import remember, unchanged
    remember('tid','same','same')
    assert unchanged('tid','same')
    assert not unchanged('tid','same')
    remember('tid','before','after')
    assert not unchanged('tid','after')
    remember('tid','old','old')
    assert not unchanged('tid','new')


def test_controller_context_not_loaded_from_isolated_home(monkeypatch):
    monkeypatch.delenv('DOCKER_HOST',raising=False)
    server=cs.ContainerAppServer.__new__(cs.ContainerAppServer);server.docker='docker'
    monkeypatch.setattr(cs.recovery_runtime,'run',lambda *a,**k:SimpleNamespace(returncode=0,stdout='unix:///synthetic/docker.sock\n'))
    assert server.transport_environment()=={'DOCKER_HOST':'unix:///synthetic/docker.sock'}
    monkeypatch.setenv('DOCKER_HOST','tcp://untrusted:2375')
    with pytest.raises(ExecutorError):server.transport_environment()
