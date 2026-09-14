import json
import time
import pytest
from test_chat import chat, create
from test_chat_unlimited import unlimited
from app.chat.platform import allowed, fingerprint, configured


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
