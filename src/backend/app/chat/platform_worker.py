"""单机受信任控制器；一次领取一轮，其余持久排队，不施加用户并发配额。"""
import fcntl
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import threading
import time
from uuid import uuid4
from sqlalchemy import select, update, or_
from app.chat import worker, service
from app.chat.accounting import pending, reconcile_usage
from app.chat.backup import LocalBackupStore
from app.chat.snapshot_observability import record as record_snapshot
from app.chat.cleanup import process_copies
from app.chat.container_server import persistent_container_server, ContainerAppServer
from app.chat.execution import run_claim, mark_unknown, reconcile_unknown
from app.chat.platform import configured
from app.chat.heartbeat import worker_heartbeat
from app.chat.preparation_failure import fail_preparation, recover_preparation_failures
from app.chat.schema import turns, conversations, cleanup_jobs
from app.chat.settings import backup_root, local_snapshot_limit, repository_catalog, repository_binding
from app.chat.workspace import trusted_directory, prepare_workspace, git
from app.db.session import get_session_factory


def automatic_snapshot(factory, store, database, snapshot_limit):
    operation_id=uuid4().hex
    record_snapshot(factory,operation_id,'started')
    try:
        result=store.create_automatic(database,snapshot_limit)
    except Exception:
        record_snapshot(factory,operation_id,'failed',error_code='snapshot_operation_failed')
        raise
    record_snapshot(factory,operation_id,'rotated' if result['created'] else 'skipped',
                    expired=result['expired'],protected=result['protected'])
    return result


def selected_workspace_mode(binding):
    mode = binding.get('workspace_mode')
    if mode not in ('copy', 'source'): raise RuntimeError('workspace_mode_invalid')
    return mode


def main():
    factory=get_session_factory()
    with factory() as db:
        if not configured(db): raise RuntimeError('platform_configuration_unavailable')
        database=Path(db.get_bind().url.database)
    if os.getuid()==0: raise RuntimeError('nonroot_controller_required')
    state=trusted_directory(os.environ['MOONBOX_CHAT_STATE_ROOT'])
    runtime=trusted_directory(os.environ['MOONBOX_CHAT_RUNTIME_ROOT'])
    auth=Path(os.environ['MOONBOX_CHAT_AUTH_FILE'])
    if auth.is_symlink() or not auth.is_file(): raise RuntimeError('credential_source_unavailable')
    # Validate shape only; never print credential values or copy personal config.
    credential=json.loads(auth.read_text())
    if not isinstance(credential,dict) or not (credential.get('tokens') or credential.get('OPENAI_API_KEY')):
        raise RuntimeError('credential_source_invalid')
    del credential
    lock=(state/'worker.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    roots={}
    for row in repository_catalog():
        binding=repository_binding(row['id'],row['space_id'])
        source=trusted_directory(binding['source_root']);git(source,'rev-parse','--verify','HEAD')
        root=trusted_directory(binding['workspace_root'])
        mode=selected_workspace_mode(binding)
        if mode=='copy':
            if source==root or root in source.parents: raise RuntimeError('source_workspace_overlap')
            if source in root.parents: git(source,'check-ignore','-q',str(root))
        roots[(row['space_id'],row['id'])]=(source,root,mode)
    subprocess.run(['docker','image','inspect',ContainerAppServer.IMAGE],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=120)
    store=LocalBackupStore(backup_root())
    snapshot_limit=local_snapshot_limit()
    automatic_snapshot(factory,store,database,snapshot_limit)
    # Verify nested sandbox with a disposable workspace before publishing readiness.
    import tempfile
    with tempfile.TemporaryDirectory(prefix='preflight-',dir=runtime) as folder:
        probe=Path(folder);(probe/'.git').mkdir()
        with persistent_container_server(probe,runtime,auth): pass
        import hashlib
        shutil.rmtree(runtime/hashlib.sha256(str(probe).encode()).hexdigest())
    from app.governance.capture_worker import recover_interrupted, tick as capture_tick
    from app.governance.capture_executor import STOP as capture_stop, recover_copies
    recover_copies()
    recover_interrupted(factory)
    recover_preparation_failures(factory)
    running=True;job=None;token=None;maintenance_at=0;backup_at=time.monotonic()+86400
    capture_job=None
    def stop(*_):
        nonlocal running
        running=False
        capture_stop.set()
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    def server(path): return persistent_container_server(path,runtime,auth)
    def execute(claim,path):
        try: run_claim(factory,claim,path,server)
        except Exception: mark_unknown(factory,claim,'platform_execution_setup_failed')
    def workspace(cid):
        with factory() as db: parent=db.execute(select(conversations).where(conversations.c.id==cid)).mappings().one()
        source,root,mode=roots[(parent['space_id'],parent['repository_id'])]
        return source,source if mode=='source' else root/cid
    heartbeat=worker_heartbeat(state)
    heartbeat.__enter__()
    try:
        while running:
            from app.governance.recovery_capabilities import publish as publish_capabilities
            publish_capabilities("worker")
            if capture_job is None or not capture_job.is_alive():
                capture_job=threading.Thread(target=capture_tick,args=(factory,),daemon=True)
                capture_job.start()
            if job is None or not job.is_alive():
                job=None
                with factory() as db:
                    worker.mark_stale_unknown(db,stale_seconds=10)
                    for row in pending(db): reconcile_usage(db,row['id'])
                    unknown=list(db.execute(select(turns.c.id,turns.c.conversation_id).where(turns.c.status=='unknown')).all())
                for tid,cid in unknown:
                    try:
                        _,path=workspace(cid)
                        if path.is_dir(): reconcile_unknown(factory,tid,path,server)
                    except (KeyError,ValueError): continue
                from app.governance.candidate_recovery import reconcile_terminal_candidates
                reconcile_terminal_candidates(factory, workspace)
                from app.governance.direct_command_journal import reconcile_terminal_commands
                reconcile_terminal_commands(factory, workspace)
                if time.monotonic()>=maintenance_at:
                    from app.governance.completion_recovery import checkpoint_applied_completions
                    checkpoint_applied_completions(factory,workspace)
                    def purge(job):
                        _,path=workspace(job['conversation_id'])
                        with server(path) as adapter: return adapter.delete_thread(job['executor_thread_id'])
                    with factory() as db:
                        copies=list(db.scalars(select(cleanup_jobs.c.conversation_id).where(or_(cleanup_jobs.c.executor_status.in_(('pending','retry')),cleanup_jobs.c.backup_status.in_(('pending','retry'))))))
                        for cid in copies: process_copies(db,cid,purge,lambda job:store.copies_cleared(job['conversation_id']))
                    maintenance_at=time.monotonic()+30
                if time.monotonic()>=backup_at:
                    try:
                        automatic_snapshot(factory,store,database,snapshot_limit)
                    except Exception:
                        import logging
                        logging.getLogger('moonbox.chat').warning('local_snapshot.operation_failed')
                        backup_at=time.monotonic()+300
                    else:
                        backup_at=time.monotonic()+86400
                with factory() as db: token=worker.claim(db,'platform-'+str(os.getpid()))
                if token:
                    try:
                        source,path=workspace(token['conversation_id'])
                        with factory() as db:
                            parent=db.execute(select(conversations).where(conversations.c.id==token['conversation_id'])).mappings().one()
                            service.conversation(db,parent['owner_id'],parent['id'])
                        if path != source and not path.exists(): prepare_workspace(source,path.parent,token['conversation_id'])
                        # Copying a workspace can exceed the heartbeat TTL. This live
                        # worker refreshes only its own declaration before preflight.
                        publish_capabilities("worker")
                        from app.governance.preparation import initialize_workspace
                        with factory() as db: initialize_workspace(db, parent, source, path)
                        trusted_directory(path)
                        job=threading.Thread(target=execute,args=(token,path));job.start()
                    except Exception as error: fail_preparation(factory,token,error)
            time.sleep(.25)
    finally:
        heartbeat.__exit__(None,None,None)
        capture_stop.set()
        if capture_job and capture_job.is_alive():capture_job.join(timeout=25)
        if job and job.is_alive():
            with factory() as db:
                db.execute(update(turns).where(turns.c.id==token['turn_id'],turns.c.worker_id==token['worker_id'],turns.c.generation==token['generation'],turns.c.status.in_(('connecting','running'))).values(status='stopping'));db.commit()
            job.join(timeout=60)
        lock.close()

if __name__=='__main__':
    try: main()
    except Exception as error:
        import traceback
        frames=traceback.extract_tb(error.__traceback__)
        print(json.dumps({'event':'chat.worker.unavailable','error_type':type(error).__name__,
            'locations':[frame.name+':'+str(frame.lineno) for frame in frames[-4:]]}),flush=True)
        raise SystemExit('Chat worker unavailable; check private configuration, credentials, database and Docker dependencies') from None
