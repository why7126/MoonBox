"""One bounded background recovery slot; the normal claim loop never waits on Docker."""
import logging
import subprocess
import threading
import time
from sqlalchemy import select
from app.chat import recovery
from app.chat.execution import reconcile_unknown
from app.chat.recovery_runtime import scope
from app.chat.schema import turns


def execute(factory, lease, workspace, server, policy, docker=True):
    with factory() as db:
        if not recovery.fence(db, lease):
            db.rollback(); return
        db.commit()
    outcome = {'result': 'internal_error'}
    started = time.monotonic()
    with scope(lease['turn_id'], lease_token=lease['lease_token']) as runtime:
        try:
            # Recovery of an expired lease confirms old processes are gone first.
            if docker: runtime.cleanup(stale=True)
            if lease.get('cleanup_only'):
                outcome['result'] = 'budget_exhausted'
                return
            with factory() as db:
                cid = db.scalar(select(turns.c.conversation_id).where(turns.c.id == lease['turn_id']))
            _, path = workspace(cid)
            reconcile_unknown(factory, lease['turn_id'], path, server, recovery_lease=lease, outcome=outcome)
        except subprocess.TimeoutExpired:
            outcome['result'] = 'timeout'
        except Exception as error:
            outcome['result'] = recovery.classify(error)
        finally:
            try:
                if docker: runtime.cleanup()
            except Exception: outcome['result'] = 'cleanup_failed'
            try:
                if docker: runtime.collect_metrics()
            except Exception: pass
            runtime.metrics['duration_ms'] = int((time.monotonic()-started)*1000)
            with factory() as db:
                recovery.finish(db, lease, outcome['result'], policy, metrics=runtime.metrics)


class RecoverySlot:
    def __init__(self, factory, workspace, server, policy, docker=True):
        self.factory, self.workspace, self.server, self.policy = factory, workspace, server, policy
        self.docker = docker
        self.job = None
        self.next_scan = 0

    def tick(self):
        if self.job is not None and self.job.is_alive(): return
        if time.monotonic() < self.next_scan: return
        self.next_scan = time.monotonic()+1
        # Even the DB scan is off the normal task claim path.
        def work():
            try:
                with self.factory() as db: lease = recovery.claim(db, self.policy)
                if lease: execute(self.factory, lease, self.workspace, self.server, self.policy, self.docker)
            except Exception:
                logging.getLogger('moonbox.chat').warning('chat.recovery_worker_failed')
        self.job = threading.Thread(target=work, name='chat-recovery', daemon=True)
        self.job.start()

    def close(self):
        if self.job is not None: self.job.join(timeout=120)
