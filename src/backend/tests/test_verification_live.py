"""Opt-in real executor round with disposable identities, DB and auth runtime."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
import time
import pytest
from sqlalchemy import select
from test_chat import chat, create
from test_governance_writer import writing
from test_direct_completion import direct_scene
from app.governance import execution_context, store
from app.chat import worker, settings
from app.chat.admission import enqueue
from app.chat.execution import run_claim
from app.chat.local_probe import local_executor
from app.chat.schema import turns


@pytest.mark.skipif(os.environ.get('CHAT_LIVE_ISOLATED_PROBE') != '1', reason='explicit isolated live probe')
def test_real_round_during_context_verification(direct_scene, chat, tmp_path, monkeypatch):
    client, factory = chat
    _, project, _, rid, _ = direct_scene
    record = store.read(rid, 'operation'); record['steps'] = []; store.write(rid, 'operation', record)
    monkeypatch.setattr('app.chat.isolated.allowed', lambda *a: True)
    cid = create(client)
    work = tmp_path.resolve()/cid; work.mkdir()
    subprocess.run(['git', 'init', '-q', str(work)], check=True)
    with factory() as db:
        row = enqueue(db, 'alice', cid, 'lock-live',
                      'Reply exactly: database lock probe complete. Do not use tools or modify files.',
                      settings.execution_limits())
        token = worker.claim(db, 'isolated-lock-probe')
    stop = threading.Event(); samples = []; failures = []
    def poll():
        while not stop.is_set():
            try:
                with factory() as db: execution_context.reconcile(db, 'alice', project)
                samples.append(1)
            except Exception as error:
                failures.append(type(error).__name__)
            stop.wait(.1)
    thread = threading.Thread(target=poll); thread.start()
    try:
        with local_executor([work], executable=os.environ.get('BUG0068_CODEX_BIN') or shutil.which('codex'),
                            auth_source=Path.home()/'.codex/auth.json') as (server, auth_home):
            status = run_claim(factory, token, work, server, max_seconds=120)
        assert not auth_home.exists()
    finally:
        stop.set(); thread.join(timeout=10)
    with factory() as db:
        error = db.scalar(select(turns.c.error_code).where(turns.c.id == row['id']))
    result = {'status':status, 'error_code':error, 'concurrent_checks':len(samples),
              'check_failures':failures, 'temporary_auth_removed':not auth_home.exists(),
              'real_executor':True, 'identity':'synthetic isolated actor', 'existing_services_restarted':False}
    if status == 'completed':
        route = f'/api/v1/chat/turns/{row["id"]}/results'
        first = client.get(route, params={'stream_id':'final'}).json()['data']
        second = client.get(route, params={'stream_id':'final'}).json()['data']
        result['reread_matches'] = first['items'] == second['items']
        result['has_final'] = first['has_final']
        assert result['reread_matches'] and result['has_final']
    destination = os.environ.get('BUG0068_LIVE_EVIDENCE')
    if destination: Path(destination).write_text(json.dumps(result, indent=2)+'\n')
    assert status == 'completed', error
    assert samples and not failures
