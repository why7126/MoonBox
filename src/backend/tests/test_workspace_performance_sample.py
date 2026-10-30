"""Measured small-file recovery sample; reports observations, never an invented SLA."""
import json
import os
import time
from pathlib import Path
from sqlalchemy import insert
from test_chat import chat, create
from test_managed_worktree_git import repo
from app.chat import service as chat_service, snapshot_store
from app.chat.schema import turns
from app.moonbox_core import workspaces
from app.moonbox_core.schema import session_bindings
from app.moonbox_exec_server.scope import names
from app.moonbox_rollout import catalog, restore
from test_workspace_restore_operation import recovery


def test_measured_scan_capture_publication_and_restore(recovery):
    factory, root, wid, cid, _, _ = recovery
    directory = root/'src'; directory.mkdir()
    paths = [f'src/sample-{n:03}.txt' for n in range(100)]
    for n, path in enumerate(paths): (root/path).write_text(str(n).zfill(4) + 'a'*4092)
    with factory.begin() as db:
        turn = chat_service.identity()
        db.execute(insert(turns).values(**turn,conversation_id=cid,client_request_id='performance',status='completed',prompt='synthetic benchmark'))
    timing = {}
    started = time.perf_counter(); scanned = list(names(root, ('src',)))
    timing['enumeration_seconds'] = time.perf_counter()-started
    points = []
    for phase in ('before','after'):
        if phase == 'after':
            for n,path in enumerate(paths): (root/path).write_text(str(n).zfill(4) + 'b'*4092)
        started = time.perf_counter()
        snapshot = snapshot_store.capture(factory,cid,turn['id'],root,phase,policy_roots=('src',))
        timing[phase+'_capture_and_content_persistence_seconds'] = time.perf_counter()-started
        started = time.perf_counter()
        with factory.begin() as db:
            points.append(catalog.publish(db,wid,snapshot['version_id'],policy_version='performance-sample',head_commit='sample',changed=True,scope=['src'])['id'])
        timing[phase+'_catalog_persistence_seconds'] = time.perf_counter()-started
    started = time.perf_counter()
    with factory() as db:
        checked,_ = restore.preview(db,'alice','space','repo',wid,*points,paths)
        operation = restore.start(db,'alice','space','repo',wid,cid,*points,paths,checked['fingerprint'],'performance-restore')
    timing['preflight_and_operation_persistence_seconds'] = time.perf_counter()-started
    started=time.perf_counter(); result=restore.run(factory,'alice','space','repo',operation['id'])
    timing['restore_seconds']=time.perf_counter()-started
    assert result['state']=='completed' and len(scanned)==100
    assert all((root/path).read_text()==str(n).zfill(4)+'a'*4092 for n,path in enumerate(paths))
    report=dict(sample='synthetic-real-files-and-sqlite',files=100,bytes_per_phase=409600,
        database='sqlite',repetitions=1,concurrent_load='other local verification may be running',
        thresholds=None,measurements=timing,restored_files=100)
    target=os.getenv('MOONBOX_WORKSPACE_PERFORMANCE_REPORT')
    if target: Path(target).write_text(json.dumps(report,indent=2))
