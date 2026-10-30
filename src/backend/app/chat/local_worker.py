"""独立本机测试worker；只在隔离配置有效时领取任务。"""
import fcntl
import json
import os
from pathlib import Path
import signal
import threading
import time
from sqlalchemy import select, update, or_
from app.chat import worker, service
from app.chat.accounting import pending, reconcile_usage
from app.chat.execution import run_claim, mark_unknown
from app.chat.recovery_worker import RecoverySlot
from app.chat.settings import recovery_policy
from app.chat.isolated import configuration
from app.chat.local_probe import persistent_local_server
from app.chat.schema import conversations, turns, cleanup_jobs
from app.chat.workspace import prepare_workspace, trusted_directory
from app.db.session import get_session_factory


def main():
    factory=get_session_factory()
    with factory() as db:config=configuration(db)
    if not config:raise SystemExit('isolated configuration unavailable')
    root=Path(config['root']);running=True;job=None;token=None;maintenance_at=0
    lock=(root/'worker.lock').open('w')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    def stop(*_):
        nonlocal running
        running=False
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    def server(path):
        if config.get('executor')=='container':
            from app.chat.container_server import persistent_container_server
            return persistent_container_server(path,root/'runtime',root/'auth.json')
        return persistent_local_server(path,root/'runtime',root/'auth.json',config['executable'])
    def execute(claim,path):
        try:run_claim(factory,claim,path,server,max_seconds=180)
        except Exception:mark_unknown(factory,claim,'local_worker_setup_failed')
    def workspace(cid):
        with factory() as db:
            parent = db.execute(select(conversations).where(conversations.c.id == cid)).mappings().one()
            from app.moonbox_core.sessions import execution_workspace
            managed = execution_workspace(db, parent)
            if managed:
                return None, managed[1]
        return None, root/'workspaces'/cid
    recovery_slot = RecoverySlot(factory, workspace, server, recovery_policy(), docker=config.get('executor')=='container')
    try:
        while running:
            from app.governance.recovery_capabilities import publish as publish_capabilities
            publish_capabilities("worker")
            with factory() as db:
                if not configuration(db):break
            stamp=root/'worker-ready.tmp';stamp.write_text(json.dumps({'time':time.time()}));stamp.replace(root/'worker-ready.json')
            if job is None or not job.is_alive():
                job=None
                with factory() as db:
                    worker.mark_stale_unknown(db,stale_seconds=10)
                    for row in pending(db):reconcile_usage(db,row['id'])
                from app.governance.candidate_recovery import reconcile_terminal_candidates
                reconcile_terminal_candidates(factory, workspace)
                from app.governance.direct_command_journal import reconcile_terminal_commands
                reconcile_terminal_commands(factory, workspace)
                if time.monotonic()>=maintenance_at:
                    from app.chat.cleanup import process_copies
                    def purge(job):
                        path=trusted_directory(workspace(job['conversation_id'])[1])
                        with server(path) as adapter:return adapter.delete_thread(job['executor_thread_id'])
                    def backup(job):
                        from app.chat.settings import backup_root
                        from app.chat.backup import LocalBackupStore
                        return bool(backup_root()) and LocalBackupStore(backup_root()).copies_cleared(job['conversation_id'])
                    with factory() as db:
                        copies=list(db.scalars(select(cleanup_jobs.c.conversation_id).where(cleanup_jobs.c.owner_id==config['actor'],or_(cleanup_jobs.c.executor_status.in_(('pending','retry')),cleanup_jobs.c.backup_status.in_(('pending','retry'))))))
                        for cid in copies:process_copies(db,cid,purge,backup)
                    maintenance_at=time.monotonic()+30
                with factory() as db:token=worker.claim(db,'local-'+str(os.getpid()))
                if token:
                    path=workspace(token['conversation_id'])[1]
                    try:
                        with factory() as db:
                            parent=service.conversation(db,config['actor'],token['conversation_id'])
                            if parent['space_id']!=config['space'] or parent['repository_id']!=config['repository']:raise ValueError('scope')
                        if not path.exists():prepare_workspace(root/'seed',root/'workspaces',token['conversation_id'])
                        trusted_directory(path)
                        job=threading.Thread(target=execute,args=(token,path));job.start()
                    except Exception:mark_unknown(factory,token,'local_workspace_unavailable')
            recovery_slot.tick()
            time.sleep(.25)
    finally:
        recovery_slot.close()
        (root/'worker-ready.json').unlink(missing_ok=True)
        if job and job.is_alive():
            with factory() as db:
                db.execute(update(turns).where(turns.c.id==token['turn_id'],turns.c.worker_id==token['worker_id'],turns.c.generation==token['generation'],turns.c.status.in_(('connecting','running'))).values(status='stopping'));db.commit()
            job.join(timeout=60)
        lock.close()

if __name__=='__main__':main()
