"""Durable, bounded verification queue; never replays governance side effects."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlalchemy import Column, Integer, String, Table, Index, insert, select, update, or_
from sqlalchemy.exc import IntegrityError
from app.chat.schema import metadata, governance_applications as applications, governance_candidates as candidates, turns
from app.governance.execution_guard import execution_guards as guards
from app.chat import service

handoffs = Table('governance_completion_handoffs', metadata,
    Column('scope_key', String(64), primary_key=True),
    Column('object_id', String(128), primary_key=True),
    Column('guard_version', Integer, primary_key=True),
    Column('operation_id', String(64), nullable=False),
    Column('application_id', String(64), nullable=False),
    Column('state', String(24), nullable=False),
    Column('attempt_count', Integer, nullable=False, default=0),
    Column('next_attempt_at', String(32), nullable=False),
    Column('lease_owner', String(64)), Column('lease_until', String(32)),
    Column('last_checked_at', String(32)), Column('reason_code', String(64)),
    Column('created_at', String(32), nullable=False))
Index('ix_completion_handoff_due', handoffs.c.state, handoffs.c.next_attempt_at)
BACKOFF = (5, 15, 30)


def stamp(now):
    return now.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def enqueue(db, candidate_id, now=None):
    now = now or datetime.now(timezone.utc)
    candidate = db.execute(select(candidates).where(candidates.c.id == candidate_id)).mappings().first()
    if not candidate or candidate['action'] not in ('req-review', 'bug-review'):
        return
    app = db.execute(select(applications).where(applications.c.candidate_id == candidate_id,
        applications.c.state == 'applied', applications.c.phase == 'verified')).mappings().first()
    guard = db.execute(select(guards).where(guards.c.scope_key == candidate['scope_key'],
        guards.c.object_id == candidate['object_id'], guards.c.operation_id == candidate['turn_id'],
        guards.c.state.in_(('running', 'needs_review')))).mappings().first()
    if not app or not guard:
        return
    try:
        with db.begin_nested():
            db.execute(insert(handoffs).values(scope_key=guard['scope_key'], object_id=guard['object_id'],
                guard_version=guard['version'], operation_id=guard['operation_id'], application_id=app['id'],
                state='pending', attempt_count=0, next_attempt_at=stamp(now), created_at=stamp(now)))
    except IntegrityError:
        pass


def key(row):
    return (handoffs.c.scope_key == row['scope_key'], handoffs.c.object_id == row['object_id'],
            handoffs.c.guard_version == row['guard_version'])


def tick(factory, now=None):
    from app.governance.recovery_service import authorize
    from app.governance.recovery_schema import operations
    from app.governance.execution_context import reconcile
    now = now or datetime.now(timezone.utc)
    # Startup/restart repair: verified applications are durable handoff intents.
    with factory() as db:
        ids = db.scalars(select(candidates.c.id).join(applications, applications.c.candidate_id == candidates.c.id)
            .join(turns, turns.c.id == candidates.c.turn_id)
            .join(guards, (guards.c.operation_id == candidates.c.turn_id) & (guards.c.object_id == candidates.c.object_id)
                  & (guards.c.scope_key == candidates.c.scope_key))
            .outerjoin(handoffs, (handoffs.c.scope_key == guards.c.scope_key) & (handoffs.c.object_id == guards.c.object_id) & (handoffs.c.guard_version == guards.c.version))
            .where(handoffs.c.scope_key.is_(None), applications.c.state == 'applied', applications.c.phase == 'verified',
                   candidates.c.action.in_(('req-review','bug-review')), turns.c.status.in_(('completed','failed','stopped')), guards.c.state.in_(('running','needs_review')))
            .order_by(applications.c.created_at).limit(100)).all()
        for cid in ids:
            enqueue(db, cid, now)
        # Direct commands have durable terminal turns and guards, even without
        # candidate applications. Reuse the same bounded CAS queue on restart.
        from app.governance.direct_command_journal import DIRECT_ACTIONS
        direct_rows = db.execute(select(guards).join(turns, turns.c.id == guards.c.operation_id)
            .outerjoin(handoffs, (handoffs.c.scope_key == guards.c.scope_key) &
                (handoffs.c.object_id == guards.c.object_id) & (handoffs.c.guard_version == guards.c.version))
            .where(handoffs.c.scope_key.is_(None), guards.c.action.in_(DIRECT_ACTIONS),
                guards.c.state.in_(('running','needs_review')),
                turns.c.status.in_(('completed','failed','stopped'))).limit(100)).mappings().all()
        for guard in direct_rows:
            try:
                with db.begin_nested():
                    db.execute(insert(handoffs).values(scope_key=guard['scope_key'], object_id=guard['object_id'],
                        guard_version=guard['version'], operation_id=guard['operation_id'],
                        application_id='direct:'+guard['operation_id'], state='pending', attempt_count=0,
                        next_attempt_at=stamp(now), created_at=stamp(now)))
            except IntegrityError:
                pass
        db.commit()
        queue = db.execute(select(handoffs).outerjoin(turns, turns.c.id == handoffs.c.operation_id).where(
            or_(turns.c.status.in_(('completed','failed','stopped')), handoffs.c.attempt_count >= 3), handoffs.c.state.in_(('pending','checking')),
            handoffs.c.next_attempt_at <= stamp(now),
            or_(handoffs.c.lease_until.is_(None), handoffs.c.lease_until <= stamp(now)))
            .order_by(handoffs.c.next_attempt_at).limit(100)).mappings().all()
    for row in queue:
        if row['attempt_count'] >= 3:
            with factory() as db:
                db.execute(update(handoffs).where(*key(row), handoffs.c.state.in_(('pending','checking')),
                    or_(handoffs.c.lease_until.is_(None), handoffs.c.lease_until <= stamp(now))).values(
                        state='blocked', reason_code='retry_exhausted', lease_owner=None, lease_until=None))
                db.commit()
            continue
        token = str(uuid4())
        with factory() as db:
            claimed = db.execute(update(handoffs).where(*key(row), handoffs.c.state.in_(('pending','checking')),
                handoffs.c.attempt_count == row['attempt_count'],
                or_(handoffs.c.lease_until.is_(None), handoffs.c.lease_until <= stamp(now)))
                .values(state='checking', attempt_count=row['attempt_count'] + 1, lease_owner=token, lease_until=stamp(now+timedelta(seconds=30))))
            db.commit()
            if claimed.rowcount != 1:
                continue
            reason = None
            try:
                if row['application_id'].startswith('direct:'):
                    from app.governance.direct_completion import operation_context
                    guard = db.execute(select(guards).where(guards.c.scope_key == row['scope_key'],
                        guards.c.object_id == row['object_id'])).mappings().first()
                    if not guard or guard['version'] != row['guard_version'] or guard['operation_id'] != row['operation_id']:
                        reason = 'stale_operation'
                    else:
                        actor = guard['owner_id']
                        _, project, _, _, _, _ = operation_context(db, actor, row['operation_id'])
                else:
                    op = db.execute(select(operations).where(operations.c.origin_turn_id == row['operation_id'])).mappings().first()
                    if not op:
                        reason = 'proof_missing'
                    else:
                        actor = op['actor_id']
                        _, _, project = authorize(db, actor, op['id'], write=True)
                        if project.binding_revision != op['binding_revision']:
                            reason = 'dependency_conflict'
                if reason is None:
                    reconcile(db, actor, project, operation_id=row['operation_id'])
                    guard = db.execute(select(guards).where(guards.c.scope_key == row['scope_key'],
                        guards.c.object_id == row['object_id'])).mappings().first()
                    if not guard or guard['version'] != row['guard_version'] or guard['operation_id'] != row['operation_id']:
                        reason = 'stale_operation'
                    elif guard['state'] not in ('validated','recovered_valid'):
                        reason = guard['reason_code'] or 'temporarily_unavailable'
            except service.ChatError as error:
                db.rollback()
                reason = 'permission_denied' if error.status in (403,404) else 'temporarily_unavailable'
            except (OSError, ValueError):
                db.rollback()
                reason = 'temporarily_unavailable'
            count = row['attempt_count'] + 1
            transient = reason in ('temporarily_unavailable','result_unverified','object_running')
            state = 'confirmed' if reason is None else ('pending' if transient and count < 3 else 'blocked')
            if transient and count >= 3:
                reason = 'retry_exhausted'
            db.execute(update(handoffs).where(*key(row), handoffs.c.lease_owner == token).values(
                state=state, attempt_count=count, reason_code=reason, last_checked_at=stamp(now),
                next_attempt_at=stamp(now+timedelta(seconds=BACKOFF[min(count-1,2)])), lease_owner=None, lease_until=None))
            from app.governance.execution_guard import observe
            observe(db, row['operation_id'], 'completion_' + state, object_id=row['object_id'])
            db.commit()


def status(db, actor, project, guard):
    """Read-only historical fact; current admission is always checked separately."""
    from app.governance import store, scope
    from app.governance.completion_proof import historical_result, ProofError
    from app.chat.workspace import WorkspaceError
    result = {'historical_result': 'unverified', 'last_checked_at': None,
              'verification_reason': None, 'verification_actions': [], 'verification_differences': []}
    if not guard or guard['owner_id'] != actor or not scope.visible(db, actor, project, guard['object_id']):
        return result
    job = db.execute(select(handoffs).where(handoffs.c.scope_key == guard['scope_key'],
        handoffs.c.object_id == guard['object_id'], handoffs.c.guard_version == guard['version'])).mappings().first()
    if job:
        result.update(last_checked_at=job['last_checked_at'], verification_reason=job['reason_code'])
    app = db.execute(select(applications).join(candidates, candidates.c.id == applications.c.candidate_id).where(
        candidates.c.turn_id == guard['operation_id'], candidates.c.object_id == guard['object_id'],
        candidates.c.scope_key == project.key, candidates.c.actor_id == actor,
        applications.c.scope_key == project.key, applications.c.state == 'applied', applications.c.phase == 'verified')).mappings().first()
    if not app or guard['action'] not in ('req-review','bug-review'):
        return result
    try:
        historical_result(store.read(app['candidate_id'], 'baseline'), store.read(app['candidate_id'], 'result'),
                          store.read(app['id'], 'operation').get('workflow_sync', {}), guard['object_id'], guard['action'])
        result['historical_result'] = 'verified'
        if result['verification_reason'] == 'dependency_conflict':
            from app.governance.completion_proof import differences
            from app.governance.snapshot import stable
            result['verification_differences'] = differences(
                store.read(app['candidate_id'], 'baseline'), store.read(app['candidate_id'], 'result'),
                store.read(app['id'], 'operation').get('workflow_sync', {}), stable(project.root).files,
                guard['object_id'], guard['action'])
        result['verification_actions'] = ['evidence', 'verify'] if not project.readonly else ['evidence']
    except (ProofError, FileNotFoundError, WorkspaceError, service.ChatError, ValueError, AttributeError, TypeError):
        result['verification_reason'] = result['verification_reason'] or 'proof_invalid'
    return result


def verify_operation(db, actor, operation_id):
    """Explicit authorized recheck: no regeneration, business writes or budget reset."""
    from app.governance.recovery_service import authorize
    from app.governance.execution_context import reconcile
    operation, _, project = authorize(db, actor, operation_id, write=True)
    from app.governance.writer import project_lock
    if project.binding_revision != operation['binding_revision']:
        raise service.ChatError(2606, '项目绑定已变化，无法核验原操作', 409)
    with project_lock(project):
        # Explicit verification rechecks even a previously confirmed proof. Fence the
        # original operation/version; never reopen a newer operation or replay work.
        current = db.execute(select(guards).where(guards.c.scope_key == project.key,
            guards.c.object_id == operation['object_id'])).mappings().first()
        if current and current['operation_id'] == operation['origin_turn_id'] and current['state'] in ('validated', 'recovered_valid'):
            db.execute(update(guards).where(guards.c.scope_key == project.key,
                guards.c.object_id == operation['object_id'], guards.c.version == current['version'],
                guards.c.operation_id == operation['origin_turn_id'], guards.c.state == current['state']).values(
                    state='needs_review', reason_code='result_unverified'))
        reconcile(db, actor, project, operation_id=operation['origin_turn_id'])
        from app.governance.execution_context import reconcile_external, stage_map
        from app.governance.snapshot import stable
        snapshot = stable(project.root)
        reconcile_external(db, project, operation['object_id'],
                           stage_map(snapshot).get(operation['object_id'], 'unknown'), snapshot)
        db.commit()
    guard = db.execute(select(guards).where(guards.c.scope_key == project.key,
        guards.c.object_id == operation['object_id'])).mappings().first()
    if not guard or guard['operation_id'] != operation['origin_turn_id']:
        return {'historical_result': 'unverified', 'admission_state': 'blocked', 'reason_code': 'stale_operation'}
    now = stamp(datetime.now(timezone.utc))
    db.execute(update(handoffs).where(handoffs.c.scope_key == guard['scope_key'],
        handoffs.c.object_id == guard['object_id'], handoffs.c.guard_version == guard['version'],
        handoffs.c.operation_id == guard['operation_id']).values(last_checked_at=now, reason_code=guard['reason_code'],
            state='confirmed' if guard['state'] in ('validated','recovered_valid') else 'blocked'))
    db.commit()
    result = status(db, actor, project, guard)
    result['last_checked_at'] = now
    result.update(admission_state='allowed' if guard['state'] in ('validated','recovered_valid','idle') else 'blocked',
                  reason_code=guard['reason_code'])
    return result
