import json
import time
import pytest
from test_chat import chat, create
from test_chat_unlimited import unlimited
from app.chat.platform import allowed, fingerprint, configured
from app.chat.heartbeat import worker_heartbeat


def test_platform_deployment_defaults_local_binding_to_source_mode(monkeypatch,tmp_path):
    host=tmp_path/'host';source=tmp_path/'source'
    host.mkdir();source.mkdir()
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_ID','repo')
    monkeypatch.setenv('MOONBOX_CHAT_SPACE_ID','space')
    monkeypatch.setenv('MOONBOX_CHAT_HOST_ROOT',str(host))
    monkeypatch.setenv('MOONBOX_CHAT_SOURCE_ROOT',str(source))
    from app.chat.platform_deployment import mapping
    assert mapping()=={
        'id':'repo','space_id':'space','source_root':str(source),
        'workspace_root':str(host/'workspaces'),'governance_root':'/app/governance',
        'workspace_mode':'source'
    }


def test_worker_requires_explicit_workspace_mode():
    from app.chat.platform_worker import selected_workspace_mode
    assert selected_workspace_mode({'workspace_mode': 'source'}) == 'source'
    assert selected_workspace_mode({'workspace_mode': 'copy'}) == 'copy'
    with pytest.raises(RuntimeError, match='workspace_mode_invalid'):
        selected_workspace_mode({})


def test_platform_deployment_rejects_private_root_inside_source(monkeypatch,tmp_path):
    import subprocess
    source=tmp_path/'source';source.mkdir()
    subprocess.run(['git','init','-q',str(source)],check=True)
    (source/'tracked.txt').write_text('base\n')
    subprocess.run(['git','-C',str(source),'add','tracked.txt'],check=True)
    subprocess.run(['git','-C',str(source),'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','fixture'],check=True)
    auth=tmp_path/'auth.json';auth.write_text('{"OPENAI_API_KEY":"synthetic"}');auth.chmod(0o600)
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_ID','repo')
    monkeypatch.setenv('MOONBOX_CHAT_SPACE_ID','space')
    monkeypatch.setenv('MOONBOX_CHAT_HOST_ROOT',str(source/'data/runtime/chat-platform'))
    monkeypatch.setenv('MOONBOX_CHAT_SOURCE_ROOT',str(source))
    monkeypatch.setenv('MOONBOX_CHAT_AUTH_SOURCE',str(auth))
    monkeypatch.setenv('MOONBOX_CHAT_LIMITS',json.dumps({'user_concurrency':'unlimited','space_concurrency':'unlimited',
        'user_monthly_tokens':'unlimited','space_monthly_tokens':'unlimited','user_storage_bytes':'unlimited',
        'space_storage_bytes':'unlimited','turn_reserved_tokens':'unlimited','turn_reserved_bytes':16777216}))
    monkeypatch.setenv('MOONBOX_CHAT_RETENTION',json.dumps({'executor_delete_seconds':'unlimited','backup_expiry_seconds':'unlimited'}))
    from app.chat.platform_deployment import check
    with pytest.raises(ValueError,match='执行数据目录不能位于源仓库内'):
        check()


def test_chat_platform_worker_source_mount_is_writable_for_source_mode():
    import yaml
    source = '${MOONBOX_CHAT_SOURCE_ROOT}:${MOONBOX_CHAT_SOURCE_ROOT}'
    document = yaml.safe_load(__import__('pathlib').Path('deploy/docker-compose.chat-platform.yml').read_text())
    assert source in document['services']['chat-worker']['volumes']
    assert source + ':ro' in document['services']['backend']['volumes']
    assert source + ':ro' in document['services']['verification-worker']['volumes']


def test_archive_permission_profile_is_separate_from_governance(tmp_path):
    from app.chat.container_server import write_profiles
    write_profiles(tmp_path)
    config=(tmp_path/'config.toml').read_text()
    governance=config.split('[permissions.moonbox-governance.filesystem]',1)[1].split('[permissions.moonbox-governance.network]',1)[0]
    archive=config.split('[permissions.moonbox-archive.filesystem]',1)[1].split('[permissions.moonbox-archive.network]',1)[0]
    assert '"/work/openspec/specs"' not in governance
    assert '"/work/openspec/archive"' not in governance
    assert '"/work/openspec/specs"="write"' in archive
    assert '"/work/openspec/archive"="write"' in archive


def configure_platform(monkeypatch,tmp_path):
    root=tmp_path.resolve(); state=root/'state';state.mkdir()
    monkeypatch.setenv('MOONBOX_CHAT_EXECUTION_MODE','local-codex')
    monkeypatch.setenv('MOONBOX_CHAT_STATE_ROOT',str(state))
    monkeypatch.setenv('MOONBOX_CHAT_BACKUP_ROOT',str(root/'backups'))
    monkeypatch.setenv('MOONBOX_CHAT_RETENTION',json.dumps({'executor_delete_seconds':'unlimited','backup_expiry_seconds':'unlimited'}))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{'id':'repo','space_id':'space','source_root':str(root/'seed'),'workspace_root':str(root/'workspaces'),'governance_root':str(root/'governance')}]))
    unlimited(monkeypatch)
    return state


def beat(state,**overrides):
    path=state/'worker-ready.json';path.write_text(json.dumps({'time':time.time(),'configuration':fingerprint(),**overrides}));path.chmod(0o600)


def test_platform_gate_requires_fresh_matching_worker_and_scope(chat,monkeypatch,tmp_path):
    client,factory=chat;state=configure_platform(monkeypatch,tmp_path)
    with factory() as db:
        assert configured(db)
        assert not allowed(db,'alice','space','repo')
        beat(state); assert allowed(db,'alice','space','repo')
        assert not allowed(db,'alice','space','other')
        beat(state,time=time.time()-10); assert not allowed(db,'alice','space','repo')
        beat(state,configuration='stale'); assert not allowed(db,'alice','space','repo')
        beat(state);monkeypatch.setenv('MOONBOX_CHAT_RETENTION','{}');assert not allowed(db,'alice','space','repo')


def test_snapshot_limit_mismatch_rejects_worker_heartbeat(chat, monkeypatch, tmp_path):
    _, factory = chat
    state = configure_platform(monkeypatch, tmp_path)
    monkeypatch.setenv('MOONBOX_CHAT_LOCAL_SNAPSHOT_LIMIT', '2')
    beat(state)
    with factory() as db:
        assert allowed(db, 'alice', 'space', 'repo')
        monkeypatch.setenv('MOONBOX_CHAT_LOCAL_SNAPSHOT_LIMIT', '0')
        assert not allowed(db, 'alice', 'space', 'repo')


def test_platform_send_uses_existing_auth_and_fail_closed_switch(chat,monkeypatch,tmp_path):
    client,_=chat;state=configure_platform(monkeypatch,tmp_path);cid=create(client)
    payload={'client_request_id':'once','prompt':'hello'}
    assert client.post(f'/api/v1/chat/conversations/{cid}/turns',json=payload).status_code==503
    beat(state)
    assert client.post(f'/api/v1/chat/conversations/{cid}/turns',json=payload).json()['data']['status']=='queued'
    assert client.post(f'/api/v1/chat/conversations/{cid}/turns',json=payload).status_code==200
    assert client.post(f'/api/v1/chat/conversations/{cid}/turns',json={**payload,'client_request_id':'twice'}).status_code==409
    monkeypatch.delenv('MOONBOX_CHAT_EXECUTION_MODE')
    assert not client.get('/api/v1/chat/capabilities?space_id=space').json()['data']['execution_ready']


def test_symlink_or_world_writable_heartbeat_rejected(chat,monkeypatch,tmp_path):
    _,factory=chat;state=configure_platform(monkeypatch,tmp_path);beat(state);path=state/'worker-ready.json'
    with factory() as db:
        path.chmod(0o666);assert not allowed(db,'alice','space')
        path.chmod(0o600);path.rename(state/'other.json');path.symlink_to(state/'other.json');assert not allowed(db,'alice','space')


def test_heartbeat_updates_during_blocking_maintenance_and_stops(tmp_path):
    path=tmp_path/'worker-ready.json'
    with worker_heartbeat(tmp_path, interval=.02):
        first=json.loads(path.read_text())['time']
        time.sleep(.12)
        assert json.loads(path.read_text())['time']>first
        assert path.stat().st_mode & 0o777 == 0o600
    time.sleep(.06)
    assert not path.exists()


def test_capabilities_explains_outage_and_recovers(chat,monkeypatch,tmp_path):
    client,_=chat;state=configure_platform(monkeypatch,tmp_path)
    def code(): return client.get('/api/v1/chat/capabilities?space_id=space').json()['data']
    assert code()['reason_code']=='worker_starting'
    beat(state,time=time.time()-10)
    assert code()['reason_code']=='worker_heartbeat_expired'
    beat(state,configuration='old')
    assert code()['reason_code']=='worker_configuration_mismatch'
    beat(state)
    assert code()['execution_ready']
    cid=create(client)
    assert client.post(f'/api/v1/chat/conversations/{cid}/turns',json={'client_request_id':'recovered','prompt':'hello'}).json()['data']['status']=='queued'
