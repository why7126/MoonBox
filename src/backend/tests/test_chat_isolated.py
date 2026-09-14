import json
import os
from pathlib import Path
import tempfile
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.chat.isolated import configuration,allowed
from test_chat_accounting import LIMITS


def test_gate_requires_private_live_scope_and_disposable_database(monkeypatch):
    with tempfile.TemporaryDirectory(prefix='moonbox-chat-e2e-',dir='/private/tmp') as folder:
        root=Path(folder);config=root/'config.json';beat=root/'worker-ready.json'
        values=dict(root=folder,actor='alice',space='space',repository='repo',expires_at=time.time()+600)
        config.write_text(json.dumps(values));config.chmod(0o600);beat.write_text(json.dumps({'time':time.time()}))
        monkeypatch.setenv('APP_ENV','isolated-test');monkeypatch.setenv('CHAT_LIVE_ISOLATED_PROBE','1')
        monkeypatch.setenv('MOONBOX_CHAT_LOCAL_CONFIG',str(config));monkeypatch.setenv('MOONBOX_CHAT_LIMITS',json.dumps(LIMITS))
        monkeypatch.setenv('MOONBOX_CHAT_REPOSITORIES','[{"id":"repo","space_id":"space"}]')
        monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([dict(id='repo',space_id='space',governance_root=folder,workspace_root=str(root/'workspaces'))]))
        engine=create_engine('sqlite:///'+str(root/'chat.db'))
        with Session(engine) as db:
            assert allowed(db,'alice','space','repo')
            values['executor']='container';config.write_text(json.dumps(values));assert allowed(db,'alice','space','repo')
            values['executor']='invalid';config.write_text(json.dumps(values));assert not allowed(db,'alice','space','repo')
            values['executor']='native';config.write_text(json.dumps(values))
            assert not allowed(db,'bob','space','repo')
            assert not allowed(db,'alice','space','other')
            monkeypatch.setenv('APP_ENV','production');assert not allowed(db,'alice','space')
            monkeypatch.setenv('APP_ENV','isolated-test')
            config.chmod(0o644);assert not allowed(db,'alice','space');config.chmod(0o600)
            beat.write_text(json.dumps({'time':time.time()-10}));assert not allowed(db,'alice','space')
            beat.write_text(json.dumps({'time':time.time()}));values['expires_at']=time.time()-1;config.write_text(json.dumps(values));assert not allowed(db,'alice','space')
        engine.dispose()
