"""Durable AC scheduler; runtime adapters own bounded external effects and proofs."""
import hashlib
import json
import threading
import re
from sqlalchemy import insert, select, update
from app.chat.service import identity, now
from app.verification.acceptance_schema import steps
from app.verification.acceptance_state import Conflict


class Controller:
    def __init__(self, state, runtime, authorize):
        self.state, self.runtime, self.authorize = state, runtime, authorize

    def checkpoint(self, token, key, status, facts=None):
        with self.state.factory.begin() as db:
            row, attempt = self.state._fenced(db, token)
            self.state._cas(db, row)
            previous = db.scalar(select(steps.c.id).where(steps.c.attempt_id == attempt['id'], steps.c.step_key == key))
            values = dict(epoch=attempt['epoch'], status=status, facts_json=json.dumps(facts or {}), updated_at=now())
            if previous:
                db.execute(update(steps).where(steps.c.id == previous).values(**values))
            else:
                db.execute(insert(steps).values(**{**identity(), **values}, attempt_id=attempt['id'], step_key=key))

    def run(self, operation_id, worker_id):
        self.authorize(operation_id)
        token = self.state.claim(operation_id, worker_id)
        stop = threading.Event()
        lease_lost = threading.Event()
        def renew():
            while not stop.wait(30):
                try:
                    self.authorize(operation_id)
                    self.state.heartbeat(token)
                except Exception:
                    lease_lost.set()
                    # Adapter interrupts only its own subprocesses/resources.
                    self.runtime.interrupt()
                    return
        thread = threading.Thread(target=renew, daemon=True)
        thread.start()
        outcome = 'blocked'
        reason = None
        try:
            self.checkpoint(token, 'prepare', 'intent')
            self.runtime.prepare(token)
            self.checkpoint(token, 'prepare', 'complete')
            self.state.advance(token, 'ready')
            self.state.advance(token, 'running')
            while not lease_lost.is_set():
                pending = self.state.runnable(operation_id)
                if not pending: break
                for ac in pending:
                    self.authorize(operation_id)
                    self.state.heartbeat(token)
                    self.checkpoint(token, 'ac:'+ac, 'intent')
                    try:
                        result = self.runtime.execute(ac)
                    except Conflict as error:
                        result = {'status':'blocked','reason':str(error),'evidence':{}}
                    self.state.result(token, ac, result['status'], evidence=result.get('evidence',{}), reason=result.get('reason'))
                    self.checkpoint(token, 'ac:'+ac, 'complete')
            current = self.state.get(operation_id)
            if current['cancel_requested']: raise Conflict('cancelled')
            statuses = {item['status'] for item in current['checks']}
            outcome = 'passed' if statuses == {'passed'} else 'failed' if 'failed' in statuses else 'blocked'
            self.state.advance(token, outcome)
        except Conflict as error:
            outcome = 'blocked'
            reason = str(error) if re.fullmatch(r'[a-z][a-z0-9_]{0,79}',str(error)) else 'runtime_refused'
        except Exception:
            outcome = 'blocked'
            reason = 'runtime_unavailable'
        finally:
            stop.set(); thread.join(timeout=35)
            # Cleanup and resource release remain independent from AC success.
            try:
                clean = self.runtime.cleanup()
            except Exception:
                clean = False
            from app.verification.acceptance_cleanup import record
            record(self.state,operation_id,clean)
            # The local adapter must prove execution stopped, not infer from lease age.
            if self.runtime.terminated():
                self.finish_owner(token, outcome, reason)
        return self.state.get(operation_id)

    def finish_owner(self, token, outcome, reason=None):
        from app.verification.acceptance_schema import attempts
        with self.state.factory.begin() as db:
            row = self.state._row(db, token['id'])
            attempt = db.execute(select(attempts).where(attempts.c.id == token['attempt_id'])).mappings().one()
            # Cancellation increments the fence; it still permits releasing this known owner.
            if row['attempt_id'] != token['attempt_id'] or attempt['epoch'] not in {token['epoch'],token['epoch']+1}:
                raise Conflict('epoch_conflict')
            self.state._cas(db,row,status='cancelled' if row['cancel_requested'] else outcome,
                            reason_code='user_stopped' if row['cancel_requested'] else reason)
            db.execute(update(attempts).where(attempts.c.id == attempt['id']).values(
                worker_id=None, lease_until=0, state='cancelled' if row['cancel_requested'] else outcome))
