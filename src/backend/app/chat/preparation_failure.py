"""Terminal failures only for stages that cannot have started an executor turn."""
import json
from sqlalchemy import func, insert, select, update
from app.chat import service
from app.chat.app_server import ExecutorError
from app.chat.schema import conversations, events, snapshots, turns

PREPARATION_CODES = frozenset({
    'operating_quota_exceeded', 'container_memory_exhausted', 'container_terminated',
    'workspace_resource_exhausted', 'result_persistence_failed', 'protocol_resource_limit',
    'recovery_capability_unavailable', 'recovery_operation_incomplete',
    'direct_command_preparation_failed', 'direct_command_operation_missing',
    'direct_command_operation_invalid', 'direct_command_identity_mismatch',
    'direct_command_baseline_missing', 'direct_command_baseline_invalid',
    'workspace_unapplied_changes', 'workspace_fact_source_stale',
    'governance_validation_failed', 'workspace_prepare_failed',
    'workspace_binding_mismatch', 'usage_reservation_missing',
    'result_reservation_too_small', 'execution_access_or_workspace_error',
    'execution_internal_error', 'container_runtime_unavailable',
    'container_credential_directory_invalid', 'container_mount_overlap',
    'container_auth_path_invalid', 'container_sandbox_preflight_failed',
    'container_readonly_preflight_failed', 'container_governance_lock_unavailable',
    'container_auth_source_invalid', 'container_toolchain_unavailable', 'unsupported_executor_version',
    'executor_disconnected', 'executor_rpc_rejected', 'executor_invalid_result',
    'executor_timeout_initialize',
})


def fail_preparation(factory, token, error, *, recovering=False):
    kind = error.code if isinstance(error, ExecutorError) else getattr(error, 'kind', None)
    code = kind if kind in PREPARATION_CODES else 'workspace_prepare_failed'
    with factory() as db:
        if db.scalar(select(events.c.id).where(events.c.turn_id == token['turn_id'],
            events.c.source_id == 'runner:start-requested')):
            return False
        filters = [turns.c.id == token['turn_id'], turns.c.worker_id == token['worker_id'],
                   turns.c.generation == token['generation'], turns.c.executor_turn_id.is_(None)]
        if recovering:
            filters += [turns.c.status == 'unknown', turns.c.error_code == 'platform_workspace_unavailable']
        else:
            filters += [turns.c.status == 'connecting']
        parent = db.execute(select(conversations.c.id).where(
            conversations.c.id == token['conversation_id'],
            conversations.c.active_turn_id == token['turn_id'],
            conversations.c.generation == token['generation'])).first()
        if not parent:
            return False
        won = db.execute(update(turns).where(*filters).values(
            status='failed', error_code=code, updated_at=service.now())).rowcount
        if won != 1:
            db.rollback()
            return False
        tid = token['turn_id']
        sequence = (db.scalar(select(func.max(events.c.sequence)).where(events.c.turn_id == tid)) or 0) + 1
        payload = {'status': 'failed', 'error_code': code, 'stage': 'workspace_prepare'}
        db.execute(insert(events).values(**service.identity(), turn_id=tid, sequence=sequence,
            source_id='workspace-prepare-failed' if not db.scalar(select(events.c.id).where(events.c.turn_id == tid,
                events.c.source_id == 'workspace-prepare-failed')) else f"workspace-prepare-failed:{token['generation']}",
            event_type='execution.state', payload=json.dumps(payload)))
        from app.chat.content_schema import prepare_attempts
        db.execute(update(prepare_attempts).where(prepare_attempts.c.turn_id == tid,
            prepare_attempts.c.state.in_(('queued', 'connecting'))).values(state='failed', updated_at=service.now()))
        db.execute(update(conversations).where(conversations.c.id == token['conversation_id'],
            conversations.c.active_turn_id == tid, conversations.c.generation == token['generation'])
            .values(active_turn_id=None, updated_at=service.now()))
        from app.chat.observability import trace
        trace(db, tid, 'failed')
        prompt = db.scalar(select(turns.c.prompt).where(turns.c.id == tid))
        size = len(prompt.encode()) + sum(len(s.encode()) for s in db.scalars(
            select(snapshots.c.content).where(snapshots.c.turn_id == tid)))
        if not db.scalar(select(turns.c.reserved_bytes).where(turns.c.id == tid)):
            from app.chat.accounting import stored_metadata_bytes
            size = stored_metadata_bytes(db, tid)
        from app.chat.admission import settle
        # Zero model usage is justified here: this stage never calls start_turn.
        settle(db, tid, 0, size)
        from app.moonbox_core.sessions import bound
        from app.moonbox_core.workspaces import release
        workspace_id = bound(db, token['conversation_id'])
        if workspace_id:
            from sqlalchemy import delete
            from app.moonbox_rollout.schema import references
            db.execute(delete(references).where(references.c.workspace_id == workspace_id,
                references.c.owner_type == 'active_turn', references.c.owner_id == tid))
            release(db, workspace_id, tid, token['generation'])
        from app.governance.recovery_service import checkpoint_preparation_failure
        checkpoint_preparation_failure(db, tid, code)
        db.commit()
    print(json.dumps({'event': 'chat.workspace_prepare_failed', 'turn_id': tid,
        'error_code': code, 'stage': 'workspace_prepare', 'recovered': recovering,
        'exception_type': type(error).__name__ if error is not None else 'legacy_unavailable',
        'cause_type': getattr(error, 'cause_type', None) if error is not None else None,
        'api_code': error.code if isinstance(error, service.ChatError) else None}), flush=True)
    return True


def recover_preparation_failures(factory):
    with factory() as db:
        rows = list(db.execute(select(turns).where(turns.c.status == 'unknown',
            turns.c.error_code == 'platform_workspace_unavailable',
            turns.c.executor_turn_id.is_(None))).mappings())
    for row in rows:
        token = {'turn_id': row['id'], 'conversation_id': row['conversation_id'],
                 'worker_id': row['worker_id'], 'generation': row['generation']}
        fail_preparation(factory, token, None, recovering=True)
