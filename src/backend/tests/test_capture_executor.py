from pathlib import Path
from app.governance.capture_executor import CaptureServer


def test_model_adapter_mounts_and_tools():
    server=object.__new__(CaptureServer)
    server.docker='docker';server.container_name='synthetic';server.workspace=Path('/fixture');server.runtime=Path('/runtime')
    server.mounts=['--mount','type=bind,src=/fixture,dst=/work','--mount','type=bind,src=/fixture/.git,dst=/work/.git,readonly']
    options=server.options()
    assert 'type=bind,src=/fixture,dst=/work,readonly' in options
    command=server.launch_command('docker')
    for name in ('shell_tool','unified_exec','multi_agent','apps','image_generation'):
        assert f'features.{name}=false' in command
    assert 'web_search="disabled"' in command


def test_native_image_input_and_readonly_permissions():
    server=object.__new__(CaptureServer);server.workspace=Path('/fixture')
    calls=[];server.connect=lambda:'thread'
    def rpc(method,params):calls.append((method,params));return {'turn':{'id':'turn'}}
    server.rpc=rpc
    events=iter([{'method':'item/completed','params':{'turnId':'turn','item':{'type':'agentMessage','text':'{"candidates":[]}'}}},
                 {'method':'turn/completed','params':{'turn':{'id':'turn','status':'completed'}}}])
    server.event=lambda _:next(events)
    assert server.organize('synthetic',['image.png'])=='{"candidates":[]}'
    request=calls[0][1]
    assert request['permissions']=='moonbox-read' and request['approvalPolicy']=='never'
    assert request['input'][1]=={'type':'localImage','path':'/work/image.png'}


def test_recovery_only_removes_owned_capture_copies(tmp_path,monkeypatch):
    from app.governance import capture_executor as executor
    from types import SimpleNamespace
    import os
    root=tmp_path/'runtime';root.mkdir(mode=0o700)
    own=root/'capture-owned';own.mkdir();(own/'.capture-owned').write_text('1');(own/'material.png').write_bytes(b'synthetic')
    other=root/'capture-unmarked';other.mkdir();(other/'keep').write_text('keep')
    peer=tmp_path/'peer';peer.mkdir();(peer/'.capture-owned').write_text('1')
    (root/'capture-link').symlink_to(peer,target_is_directory=True)
    monkeypatch.setenv('MOONBOX_CHAT_RUNTIME_ROOT',str(root));monkeypatch.setattr(executor.shutil,'which',lambda _:'docker')
    calls=[]
    def run(command,**kwargs):calls.append(command);return SimpleNamespace(stdout='owned-container\n')
    monkeypatch.setattr(executor.subprocess,'run',run)
    executor.recover_copies()
    assert not own.exists() and other.exists() and peer.exists()
    assert calls[0][-1]=='label=moonbox.capture.runtime='+executor.runtime_label()
    assert calls[1]==['docker','rm','-f','owned-container']


def test_stop_prevents_new_model_turn():
    import pytest
    from app.governance.capture_executor import STOP
    from app.chat.app_server import ExecutorError
    server=object.__new__(CaptureServer)
    STOP.set()
    try:
        with pytest.raises(ExecutorError):server.organize('synthetic',[])
    finally:STOP.clear()


def test_compose_worker_has_storage_configuration():
    import yaml
    compose=Path(__file__).resolve().parents[3]/'deploy/docker-compose.chat-platform.yml'
    worker=yaml.safe_load(compose.read_text())['services']['chat-worker']
    assert worker['networks']==['app-network']
    environment=worker['environment']
    assert environment['OBJECT_STORAGE_ENDPOINT']=='${MINIO_ENDPOINT:-minio:9000}'
    assert all(name in environment for name in ('MINIO_ACCESS_KEY','MINIO_SECRET_KEY','MINIO_BUCKET','MINIO_SECURE'))
