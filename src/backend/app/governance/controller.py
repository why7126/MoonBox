"""Run in the separately mounted trusted writer service, without model credentials."""
import logging
import time
from sqlalchemy import select, or_, and_
from app.chat.schema import governance_applications
from app.chat.service import ChatError
from app.db.session import get_session_factory
from app.governance.writer import process
from app.governance import store

logger=logging.getLogger('moonbox.governance')
_completion_scan_at = 0.0


def tick(factory, retention=None):
    from app.governance.recovery_controller import tick as recover
    recover(factory)
    from app.governance.completion_handoff import tick as reconcile_completion
    global _completion_scan_at
    if time.monotonic() >= _completion_scan_at:
        reconcile_completion(factory)
        _completion_scan_at = time.monotonic() + 10.0
    from app.governance.recovery_retention import sweep
    def maintain():
        with factory() as db:
            sweep(db)
    if retention is None:
        maintain()
    else:
        retention.run(maintain)
    from app.governance.recovery_schema import operations
    with factory() as db:
        rows=db.execute(select(governance_applications.c.id).outerjoin(operations,
            operations.c.candidate_id == governance_applications.c.candidate_id).where(
            governance_applications.c.state.in_(('pending','applying','recovering')),
            or_(operations.c.id.is_(None), and_(operations.c.lease_owner.is_(None),
                or_(operations.c.state == 'active', and_(operations.c.state == 'waiting',
                    governance_applications.c.state.in_(('applying','recovering')))))))
            .order_by(governance_applications.c.created_at,governance_applications.c.id)).all()
    for row in rows:
        try:
            with factory() as db:
                process(db,row.id)
        except BlockingIOError: continue
        except (OSError,ChatError) as error:
            from app.governance.recovery_schema import operations
            from app.governance.writer import set_state
            with factory() as db:
                app = db.execute(select(governance_applications).where(governance_applications.c.id == row.id)).mappings().one()
                governed = db.scalar(select(operations.c.id).where(operations.c.candidate_id == app['candidate_id']))
                if governed and app['state'] in ('pending', 'applying', 'recovering'):
                    safe_transient = app['state'] == 'pending' and isinstance(error, OSError) and not isinstance(error, PermissionError)
                    code = 'storage_unavailable' if safe_transient else 'authorization_or_commit_unknown'
                    set_state(db, row.id, 'conflict' if app['state'] == 'pending' else 'recovery_blocked', 'preflight_blocked', code)
            logger.warning('governance.controller.operation_unavailable',extra={'operation_id':row.id})


def main():
    store.root();factory=get_session_factory()
    from app.chat.polling import Periodic
    heartbeat, retention = Periodic(5), Periodic(30)
    while True:
        from app.governance.readiness import publish
        heartbeat.run(publish);tick(factory, retention);time.sleep(.25)


if __name__=='__main__':main()
