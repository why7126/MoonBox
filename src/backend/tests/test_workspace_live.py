"""Opt-in, bounded real model round in a disposable main workspace, never production."""
import json
import os
from pathlib import Path
import pytest
from sqlalchemy import select
from test_chat import chat, governance, create, allow_governed_write
from test_chat_local_execution import LIMITS
from test_managed_worktree_git import git
from app.chat import worker
from app.chat.admission import enqueue
from app.chat.execution import run_claim
from app.chat.container_server import persistent_container_server, ContainerAppServer
from app.chat.schema import turns, reservations
from app.moonbox_core.schema import runtime_bindings, execution_receipts, write_locks
from app.moonbox_rollout.schema import points


@pytest.mark.skipif(os.environ.get('MOONBOX_WORKSPACE_LIVE_PROBE') != '1', reason='Explicit isolated real-model sample only')
def test_managed_main_real_model_write_and_recovery_capture(chat, governance, tmp_path, monkeypatch):
    run_id = os.environ['MOONBOX_TEMP_RUN']
    expires = os.environ['MOONBOX_TEMP_EXPIRES']
    original_labels = ContainerAppServer.recovery_labels
    monkeypatch.setattr(ContainerAppServer, 'recovery_labels', lambda self: original_labels(self) + [
        '--label','moonbox.temp.managed=true','--label','moonbox.temp.run='+run_id,'--label','moonbox.temp.expires='+expires])
    client, factory = chat
    source, _ = governance
    cid = create(client)
    allow_governed_write(client, cid, governance)
    (source/'counter.txt').write_text('0\n')
    git(source, 'init', '-q', '-b', 'main'); git(source, 'add', '.')
    git(source, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'synthetic baseline')
    managed = tmp_path.resolve()/'managed'; managed.mkdir()
    runtime = tmp_path.resolve()/'runtime'; runtime.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS', json.dumps([dict(id='repo',space_id='space',
        source_root=str(source),governance_root=str(source),workspace_root=str(managed),workspace_mode='source')]))
    with factory() as db:
        row = enqueue(db, 'alice', cid, 'managed-live-one',
            'Set counter.txt to exactly 1 followed by newline. Modify no other files. Do not commit. Reply done.', LIMITS)
        claim = worker.claim(db, 'managed-isolated-test')
    def server(path):
        return persistent_container_server(path, runtime, Path.home()/'.codex/auth.json')
    result = run_claim(factory, claim, source, server, max_seconds=180)
    with factory() as db:
        state = db.execute(select(turns).where(turns.c.id == row['id'])).mappings().one()
        pin = db.execute(select(runtime_bindings).where(runtime_bindings.c.turn_id == row['id'])).mappings().first()
        receipt = db.execute(select(execution_receipts).where(execution_receipts.c.turn_id == row['id'])).mappings().first()
        usage = db.execute(select(reservations).where(reservations.c.turn_id == row['id'])).mappings().one()
        versions = list(db.execute(select(points.c.state, points.c.manifest_hash)).mappings())
        report = dict(sample='isolated-real-model-synthetic-identity', deployed_product_verified=False,
            turn_id=row['id'], status=state['status'], error_code=state['error_code'],
            file_changed=(source/'counter.txt').read_text() == '1\n',
            immutable_runtime=bool(pin and pin['image_digest'].startswith('sha256:')),
            tool_version=pin['tool_version'] if pin else None,
            executor_closed=bool(receipt and receipt['executor_closed']),
            files_collected=bool(receipt and receipt['files_collected']),
            complete_points=sum(point['state']=='complete' for point in versions),
            lease_released=db.scalar(select(write_locks.c.workspace_id)) is None,
            accounting_status=usage['status'],actual_tokens=usage['actual_tokens'])
    output = os.environ.get('MOONBOX_WORKSPACE_LIVE_REPORT')
    if output: Path(output).write_text(json.dumps(report, indent=2))
    assert result == 'completed', report
    assert report['file_changed'] and report['immutable_runtime']
    assert report['executor_closed'] and report['files_collected'] and report['lease_released']
    assert report['complete_points'] == 2
