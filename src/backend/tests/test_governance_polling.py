"""Maintenance cadence must not delay admission or hide stale publishers."""
import pytest
from test_chat import chat
from app.chat.polling import Periodic
from app.chat.service import ChatError
from app.governance import controller, recovery_capabilities


def test_retention_is_periodic_but_recovery_admission_keeps_polling(chat, monkeypatch):
    _, factory = chat
    from app.governance import recovery_controller, recovery_retention, completion_handoff
    clock = [0.0]
    calls = {'recovery': 0, 'retention': 0}
    def recovery(factory): calls['recovery'] += 1
    def retention(db): calls['retention'] += 1
    monkeypatch.setattr(recovery_controller, 'tick', recovery)
    monkeypatch.setattr(recovery_retention, 'sweep', retention)
    monkeypatch.setattr(completion_handoff, 'tick', lambda factory: None)
    monkeypatch.setattr(controller, '_completion_scan_at', 0)
    schedule = Periodic(30, lambda: clock[0])
    for n in range(121):
        clock[0] = n * .25
        controller.tick(factory, schedule)
    assert calls == {'recovery': 121, 'retention': 2}


def test_publication_cadence_keeps_original_expiry_and_stopped_peer_rejection(monkeypatch):
    clock = [0.0]
    records = {}
    writes = []
    monkeypatch.setattr(recovery_capabilities.time, 'time', lambda: clock[0])
    def write(key, kind, value):
        records[key] = value
        writes.append(key)
    monkeypatch.setattr(recovery_capabilities.store, 'write', write)
    monkeypatch.setattr(recovery_capabilities.store, 'read', lambda key, kind: records[key])
    worker = Periodic(5, lambda: clock[0])
    controller = Periodic(5, lambda: clock[0])
    for n in range(121):
        clock[0] = n * .25
        worker.run(recovery_capabilities.publish, 'worker')
        controller.run(recovery_capabilities.publish, 'controller')
        recovery_capabilities.require('bug-review')
    assert len(writes) == 14
    clock[0] = 60
    controller.run(recovery_capabilities.publish, 'controller')
    with pytest.raises(ChatError) as error:
        recovery_capabilities.require('bug-review')
    assert error.value.kind == 'recovery_capability_unavailable'


def test_slow_or_failed_maintenance_never_creates_catchup_burst():
    clock = [0.0]
    schedule = Periodic(5, lambda: clock[0])
    calls = []
    def slow():
        calls.append(clock[0]); clock[0] += 20
    schedule.run(slow)
    schedule.run(slow)
    assert calls == [0]
    clock[0] = 25
    def failed(): raise OSError('not published')
    with pytest.raises(OSError): schedule.run(failed)
    schedule.run(slow)
    assert calls == [0, 25]


def test_health_probe_keeps_checks_without_loading_database_models(tmp_path):
    import os, subprocess, sys, json, time
    root = tmp_path / 'state'; root.mkdir(mode=0o700)
    heartbeat = root / 'controller-ready.json'
    heartbeat.write_text(json.dumps({'time': time.time()})); heartbeat.chmod(0o600)
    code = "from app.governance.readiness import require_controller; require_controller(); import sys; assert 'sqlalchemy' not in sys.modules"
    env = dict(os.environ, MOONBOX_GOVERNANCE_STATE_ROOT=str(root))
    result = subprocess.run([sys.executable, '-c', code], env=env, capture_output=True)
    assert result.returncode == 0, result.stderr.decode()
    heartbeat.chmod(0o644)
    assert subprocess.run([sys.executable, '-c', code], env=env, capture_output=True).returncode != 0
    heartbeat.chmod(0o600); heartbeat.write_text(json.dumps({'time': time.time()-31}))
    assert subprocess.run([sys.executable, '-c', code], env=env, capture_output=True).returncode != 0
