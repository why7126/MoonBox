"""Trusted writer orchestration; never calls an executor or regenerates output."""
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, update
from app.chat import service
from app.chat.schema import governance_applications as applications, governance_candidates as candidates
from app.governance import durable_recovery as policy
from app.governance.recovery_schema import operations, attempts
from app.governance.recovery_service import authorize, reason, checkpoint


def assert_fence(db, oid, attempt):
    current = policy.row(db, oid)
    if current['lease_owner'] != attempt['id'] or current['fencing_token'] != attempt['fencing_token']:
        raise service.ChatError(2607, '恢复执行权已失效', 409)


def finish(db, oid, attempt, *, state, reason=None):
    policy.release(db, oid, attempt, state=state, reason=reason)
    from app.governance.observability import trace
    current = policy.row(db, oid)
    trace(db, oid, 'applied' if state == 'completed' else 'failed', actor=current['actor_id'],
          request_id=attempt['request_id'], metadata={'operation_id':oid, 'attempt_id':attempt['id'],
              'application_id':current['application_id'], 'error_code':reason, 'result':state})


def process_attempt(db, aid):
    attempt = db.execute(select(attempts).where(attempts.c.id == aid)).mappings().one()
    if attempt['state'] != 'claimed':
        return
    operation = policy.row(db, attempt['operation_id'])
    try:
        operation, parent, project = authorize(db, operation['actor_id'], operation['id'], write=True)
        # Our persisted claim is the only busy marker ignored during revalidation.
        checked = dict(operation, lease_owner=None)
        blocked = reason(db, checked, parent, project)
        if blocked:
            finish(db, operation['id'], attempt, state='blocked', reason=blocked)
            db.commit()
            return
        assert_fence(db, operation['id'], attempt)
        candidate = db.execute(select(candidates).where(candidates.c.id == operation['candidate_id'])).mappings().one()
        from app.governance.writer import apply_candidate, process, project_lock
        app = db.execute(select(applications).where(applications.c.candidate_id == candidate['id'])).mappings().first()
        if app is None:
            result = apply_candidate(db, operation['actor_id'], candidate['id'], candidate['manifest_hash'],
                                     candidate['revision'], f"auto-{candidate['id']}", True)
            app_id = result['id']
        else:
            app_id = app['id']
            if app['state'] in ('conflict', 'recovery_blocked'):
                # Original journal verification remains in writer.process; no new input is accepted.
                with project_lock(project):
                    assert_fence(db, operation['id'], attempt)
                    db.execute(update(applications).where(applications.c.id == app_id,
                        applications.c.state == app['state']).values(state='recovering'))
                    db.commit()
        policy.advance(db, operation['id'], 'apply', application_id=app_id)
        db.commit()
        result = process(db, app_id, recovery_fence=(operation['id'], dict(attempt)))
        if result['state'] == 'applied':
            checkpoint(db, candidate['id'], 'complete')
            finish(db, operation['id'], attempt, state='completed')
        else:
            finish(db, operation['id'], attempt, state='blocked', reason=result.get('error_code') or 'application_unverified')
        db.commit()
    except BlockingIOError:
        # The existing claim is retained; no second budget charge on contention.
        db.rollback()
    except (service.ChatError, OSError, ValueError, KeyError):
        db.rollback()
        # Unknown commit outcomes are not classified as safe transient failures.
        if policy.row(db, operation['id'])['lease_owner'] == attempt['id']:
            finish(db, operation['id'], attempt, state='blocked', reason='recovery_verification_failed')
            db.commit()


def tick(factory):
    from app.chat.schema import turns
    from app.chat.preparation_failure import PREPARATION_CODES
    from app.governance.recovery_service import checkpoint_preparation_failure
    with factory() as db:
        failures = db.execute(select(turns.c.id, turns.c.error_code).join(operations,
            operations.c.origin_turn_id == turns.c.id).where(operations.c.state == 'active',
            turns.c.status == 'failed', turns.c.executor_turn_id.is_(None),
            turns.c.error_code.in_(PREPARATION_CODES))).all()
        for tid, code in failures:
            checkpoint_preparation_failure(db, tid, code)
        missing_terminal = db.execute(select(operations.c.candidate_id).join(turns,
            operations.c.origin_turn_id == turns.c.id).where(operations.c.state == 'completed',
            operations.c.execution_terminal.is_(None), turns.c.status.in_(('completed','failed','stopped')))).scalars().all()
        for candidate_id in missing_terminal:
            checkpoint(db, candidate_id, 'complete')
        db.commit()
    with factory() as db:
        ids = list(db.scalars(select(attempts.c.id).where(attempts.c.state == 'claimed')))
    for aid in ids:
        with factory() as db:
            process_attempt(db, aid)
    # Automatic attempts are only for a positively classified, uncommitted transient failure.
    with factory() as db:
        queued = list(db.scalars(select(operations.c.id).where(operations.c.state == 'blocked',
            operations.c.reason_code.in_(policy.TRANSIENT), operations.c.auto_retry_count < 3,
            operations.c.next_retry_at <= service.now(), operations.c.lease_owner.is_(None))))
    for oid in queued:
        with factory() as db:
            current = policy.row(db, oid)
            try:
                current, parent, project = authorize(db, current['actor_id'], oid, write=True)
                if reason(db, current, parent, project):
                    continue
                from app.governance.writer import project_lock
                with project_lock(project):
                    policy.claim(db, oid, current['version'], f"auto-{current['auto_retry_count'] + 1}", kind='auto')
                    db.commit()
            except (BlockingIOError, service.ChatError):
                db.rollback()
