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
from sqlalchemy import select, update, or_
from app.chat import worker, service
from app.chat.accounting import pending, reconcile_usage
from app.chat.backup import LocalBackupStore
from app.chat.cleanup import process_copies
from app.chat.container_server import persistent_container_server, ContainerAppServer
from app.chat.execution import run_claim, mark_unknown, reconcile_unknown
from app.chat.platform import configured, fingerprint
from app.chat.schema import turns, conversations, cleanup_jobs
from app.chat.settings import backup_root, repository_catalog, repository_binding
from app.chat.workspace import trusted_directory, prepare_workspace, git
from app.db.session import get_session_factory


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
        if source==root or root in source.parents: raise RuntimeError('source_workspace_overlap')
        if source in root.parents: git(source,'check-ignore','-q',str(root))
        roots[(row['space_id'],row['id'])]=(source,root)
    subprocess.run(['docker','image','inspect',ContainerAppServer.IMAGE],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=20)
    store=LocalBackupStore(backup_root());store.create(database)
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
        source,root=roots[(parent['space_id'],parent['repository_id'])]
        return source,root/cid
    try:
        while running:
            if capture_job is None or not capture_job.is_alive():
                capture_job=threading.Thread(target=capture_tick,args=(factory,),daemon=True)
                capture_job.start()
            stamp=state/'worker-ready.tmp'
            stamp.write_text(json.dumps({'time':time.time(),'configuration':fingerprint()}));stamp.chmod(0o600);stamp.replace(state/'worker-ready.json')
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
                if time.monotonic()>=maintenance_at:
                    def purge(job):
                        _,path=workspace(job['conversation_id'])
                        with server(path) as adapter: return adapter.delete_thread(job['executor_thread_id'])
                    with factory() as db:
                        copies=list(db.scalars(select(cleanup_jobs.c.conversation_id).where(or_(cleanup_jobs.c.executor_status.in_(('pending','retry')),cleanup_jobs.c.backup_status.in_(('pending','retry'))))))
                        for cid in copies: process_copies(db,cid,purge,lambda job:store.copies_cleared(job['conversation_id']))
                    maintenance_at=time.monotonic()+30
                if time.monotonic()>=backup_at:
                    store.create(database);backup_at=time.monotonic()+86400
                with factory() as db: token=worker.claim(db,'platform-'+str(os.getpid()))
                if token:
                    try:
                        source,path=workspace(token['conversation_id'])
                        with factory() as db:
                            parent=db.execute(select(conversations).where(conversations.c.id==token['conversation_id'])).mappings().one()
                            service.conversation(db,parent['owner_id'],parent['id'])
                        if not path.exists(): prepare_workspace(source,path.parent,token['conversation_id'])
                        from app.governance.preparation import initialize_workspace
                        with factory() as db: initialize_workspace(db, parent, source, path)
                        trusted_directory(path)
                        job=threading.Thread(target=execute,args=(token,path));job.start()
                    except Exception: mark_unknown(factory,token,'platform_workspace_unavailable')
            time.sleep(.25)
    finally:
        (state/'worker-ready.json').unlink(missing_ok=True)
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
