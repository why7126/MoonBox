"""Atomic shared environment reservations. Expiry never proves resource absence."""
from sqlalchemy import delete, insert, inspect, select
from sqlalchemy.exc import IntegrityError
from app.verification.acceptance_schema import reservations
from app.verification.acceptance_state import Conflict

GIB = 1024 ** 3
BUDGET = {'cpu_millis': 4000, 'memory_bytes': 8 * GIB, 'disk_bytes': 20 * GIB, 'evidence_bytes': 2 * GIB}


def capacity(*, available_cpu, available_memory, available_disk, hard_disk_limit):
    if not hard_disk_limit:raise Conflict('hard_disk_quota_unavailable')
    count=min(2,int(available_cpu//4),int(available_memory//(8*GIB)),int(available_disk//(22*GIB)))
    if count<1:raise Conflict('environment_capacity_unavailable')
    return count


def reserve_in_transaction(db, operation, count):
    existing=db.execute(select(reservations).where(reservations.c.operation_id==operation['id'])).mappings().first()
    if existing:
        if existing['space_id']!=operation['space_id']:raise Conflict('reservation_scope_conflict')
        return dict(existing)
    if len(db.execute(select(reservations.c.slot)).all())>=count:
        raise Conflict('environment_concurrency_limit')
    # Pre-upgrade resources have no reservation. Reconcile them before admission;
    # do not infer release from age or silently omit them from the shared budget.
    if inspect(db.connection()).has_table('verification_candidate_environments'):
        from app.verification.candidate_schema import environments
        legacy=db.scalar(select(environments.c.id).outerjoin(reservations,
            reservations.c.operation_id==environments.c.id).where(
            environments.c.cleanup_state!='clean',reservations.c.operation_id.is_(None),
            environments.c.id!=operation['id']).limit(1))
        if legacy:raise Conflict('legacy_environment_cleanup_required')
    for slot in range(count):
        try:
            with db.begin_nested():
                row=dict(slot=slot,operation_id=operation['id'],space_id=operation['space_id'],
                         expires_at=operation['expires_at'],**BUDGET)
                db.execute(insert(reservations).values(**row))
            return row
        except IntegrityError:
            continue
    raise Conflict('environment_concurrency_limit')


def reserve(factory, operation, **limits):
    count=capacity(**limits)
    with factory.begin() as db:return reserve_in_transaction(db,operation,count)


def release_in_transaction(db, operation_id):
    return db.execute(delete(reservations).where(reservations.c.operation_id==operation_id)).rowcount


def release(factory, operation_id, *, resources_confirmed_absent):
    if not resources_confirmed_absent:raise Conflict('cleanup_unconfirmed')
    with factory.begin() as db:return release_in_transaction(db,operation_id)
