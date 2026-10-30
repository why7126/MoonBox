"""One claimed run, backed by persistent facts. API admission remains gated on deployment validation."""
from __future__ import annotations
import json
import hashlib
import re
import time
import logging
import os
from pathlib import Path
from sqlalchemy import func, insert, select, update
from app.chat import service, worker
from app.chat.assistant_output import persist_output
from app.chat.admission import settle
from app.chat.tool_record import tool_payload
from app.chat.app_server import ExecutorError
from app.chat.schema import conversations, turns, messages, diffs, workspace_baselines, reservations
from app.chat.workspace import snapshot, difference, WorkspaceError, trusted_directory


_PROFILE_BY_SCOPE = {'read_only': 'moonbox-read', 'governance_write': 'moonbox-governance',
    'implementation_write': 'moonbox-write', 'archive_write': 'moonbox-archive'}


def _retains_acknowledged_scope(permitted_scope: str, policy: dict) -> bool:
    if policy['write_scope'] == permitted_scope:
        return True
    # req-opsx / bug-opsx can make the same object implementation-ready.
    # Continue this turn with its original, narrower governance sandbox.
    return (permitted_scope == 'governance_write'
        and policy['write_scope'] == 'implementation_write'
        and policy['reason_code'] == 'implementation_change_in_sprint')


def _check_workspace_tool_dirs_outside_sandbox(workspace: Path):
    """Remove empty tool residue in project trees; preserve unsafe entries."""
    ignored_names = {'.git', '.venv', 'node_modules', 'dist', 'build', 'coverage',
                     '.pytest_cache', '.vite', '__pycache__', '.mintlify'}
    ignored_roots = {'logs', 'tmp', 'data/runtime', 'data/sqlite',
                     'data/uploads', 'data/processed', 'data/minio',
                     'data/s3', 'data/mysql', 'data/tmp', 'data/ai-usage',
                     'data/visual-evidence'}
    def fail(error):
        raise error

    for parent, directories, files in os.walk(workspace, followlinks=False, onerror=fail):
        base = Path(parent)
        kept = []
        for name in directories:
            path = base / name
            relative = path.relative_to(workspace).as_posix()
            if relative == '.agents' and not path.is_symlink():
                kept.append(name)
                continue
            if name in ('.agents', '.codex'):
                if path.is_symlink():
                    raise ExecutorError('workspace_forbidden_tool_dir')
                try:
                    path.rmdir()
                except OSError:
                    raise ExecutorError('workspace_forbidden_tool_dir') from None
                continue
            if name in ignored_names or relative in ignored_roots:
                continue
            kept.append(name)
        directories[:] = kept
        if any(name in ('.agents', '.codex') for name in files):
            raise ExecutorError('workspace_forbidden_tool_dir')


def _verify_permission_profile(server, scope):
    expected = _PROFILE_BY_SCOPE[scope]
    if hasattr(server, 'permission_profile'):
        if server.permission_profile != expected:
            raise ExecutorError('permission_profile_mismatch')
        if scope == 'implementation_write' and not server.write:
            raise ExecutorError('permission_profile_mismatch')
    return expected


def _permission_event(factory, token, decision, evidence, profile, phase, executor_turn_id=None):
    """Persist only bounded facts; failure is visible without exposing raw exceptions."""
    facts = {}
    for key, value in evidence.items():
        if key in ('entry_sha256', 'change_sha256', 'sprint_sha256'):
            if isinstance(value, str) and re.fullmatch(r'[a-f0-9]{64}', value):
                facts[key] = value
        elif key in ('object_id', 'change_id', 'sprint_id'):
            if isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,127}', value):
                facts[key] = value
    payload = {'permission_decision': {
        'turn_id': token['turn_id'], 'recorded_at': service.now(), 'phase': phase,
        'write_scope': decision['write_scope'], 'reason_code': decision['reason_code'],
        'selected_profile': profile, 'acknowledged_profile': profile if phase == 'acknowledged' else None,
        'verification': ('request_acknowledged' if phase == 'acknowledged' else
            'unknown' if phase == 'unknown' else 'selected_only'),
        'governance_versions': facts, 'executor_turn_id': executor_turn_id}}
    try:
        with factory() as db:
            recorded = worker.record_event(db, token, 'runner:permissions:' + phase,
                'execution.state', payload)
            if not recorded:
                logging.getLogger(__name__).warning('permission_observation_unavailable')
            return bool(recorded)
    except Exception:
        logging.getLogger(__name__).warning('permission_observation_unavailable')
        return False


def _workspace_identity(parent, workspace, db=None):
    if db is not None:
        from app.moonbox_core.sessions import execution_workspace
        binding = execution_workspace(db, parent)
        if binding:
            row, expected = binding
            if workspace != expected:
                raise ExecutorError('workspace_binding_mismatch')
            return row['id']
    from app.chat.settings import repository_binding
    binding = repository_binding(parent['repository_id'], parent['space_id']) or {}
    if binding.get('workspace_mode') == 'source':
        try:
            source = trusted_directory(binding['source_root'])
        except (KeyError, WorkspaceError):
            raise ExecutorError('workspace_binding_mismatch') from None
        if workspace == source:
            return 'source'
    if workspace.name != parent['id']:
        raise ExecutorError('workspace_binding_mismatch')
    return workspace.name


def _workspace_id_allowed(parent, workspace_id, db=None):
    if parent['workspace_id'] in (None, workspace_id):
        return True
    if db is not None:
        from app.moonbox_core.schema import migrations
        migration = db.execute(select(migrations).where(migrations.c.conversation_id == parent['id'],
            migrations.c.workspace_id == workspace_id)).mappings().first()
        if migration and migration['previous_workspace_id'] == parent['workspace_id']:
            return True
    # Existing object conversations may have been initialized before a repository
    # binding switched from copy mode to source mode. Allow one safe migration only
    # after the current workspace has already been verified as the bound source root.
    return workspace_id == 'source' and parent['workspace_id'] == parent['id']


def _baseline_workspace_id(parent, workspace_id):
    # Source mode shares one repository root across many object conversations;
    # baselines remain per conversation to satisfy the historical unique key.
    return parent['id'] if workspace_id == 'source' else workspace_id


def safe_text(value):
    # Conservative credential-shaped string filtering; no raw protocol errors/config/paths are logged.
    value = re.sub(r'\b(?:sk-[A-Za-z0-9_-]{12,}|eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)\b', '[已脱敏]', str(value))
    return re.sub(r'(?i)\b(authorization|api[_-]?key|password|secret|access[_-]?token)\s*[:=]\s*[^\s,;]+', r'\1=[已脱敏]', value)


from app.chat.final_answer import source as final_source


def save_result(factory, token, text, source, stream='output'):
    from app.chat import content_store
    from app.chat.final_answer import mark
    if stream == 'final':
        with factory() as db:
            row, _ = owned(db, token)
            mark(db, row['id'], source, 'begin')
            db.commit()
    # Split by characters below the byte ceiling, preserving UTF-8 boundaries.
    offset = 0
    for start in range(0, len(text), 12000):
        part = text[start:start + 12000]; data = part.encode()
        with factory() as db:
            row, parent = owned(db, token)
            sequence = content_store.result(db, parent['id'], row['id'], stream, source, offset, data)
            if sequence == 1 or sequence % 128 == 0:
                from app.chat.observability import storage_span
                storage_span(db, row['id'], 'result_commit', metadata={'storage_mode': 'chunks_v2'})
            db.commit()
        with factory() as db:
            owned(db, token)
            worker.record_event(db, token, 'content:' + str(sequence), 'execution.output',
                {'text': part[:1024], 'content_ref': {'sequence': sequence, 'stream_id': stream},
                 'truncated': len(part) > 1024, 'format_version': 2})
        offset += len(data)

    if stream == 'final':
        with factory() as db:
            row, _ = owned(db, token)
            mark(db, row['id'], source, 'complete')
            db.commit()


def owned(db, token):
    from app.chat.resource_guard import lock_budget
    lock_budget(db)
    row = db.execute(select(turns).where(turns.c.id == token['turn_id'], turns.c.worker_id == token['worker_id'],
        turns.c.generation == token['generation'], turns.c.status.in_(('connecting','running','stopping')))).mappings().first()
    parent = db.execute(select(conversations).where(conversations.c.id == token['conversation_id'],
        conversations.c.generation == token['generation'], conversations.c.active_turn_id == token['turn_id'],
        conversations.c.deleted_at.is_(None))).mappings().first()
    if not row or not parent: raise ExecutorError('worker_fenced')
    service.conversation(db,parent['owner_id'],parent['id'])
    from app.verification.acceptance_delivery import execution_guard
    from app.verification.acceptance_state import Conflict
    try:execution_guard(db,token['turn_id'])
    except Conflict as error:raise ExecutorError(str(error)) from None
    from app.chat.relations import authorize_history
    authorize_history(db, parent['owner_id'], dict(parent))
    db.execute(update(turns).where(turns.c.id == row['id'], turns.c.generation == token['generation'])
        .values(heartbeat_at=service.now(), updated_at=service.now()))
    return dict(row), dict(parent)


def mark_unknown(factory, token, code):
    logging.getLogger(__name__).warning('chat_execution_unknown reason_code=%s', code)
    with factory() as db:
        changed=db.execute(update(turns).where(turns.c.id == token['turn_id'], turns.c.worker_id == token['worker_id'],
            turns.c.generation == token['generation'], turns.c.status.in_(('connecting','running','stopping')))
            .values(status='unknown', error_code=code, updated_at=service.now())).rowcount
        from app.chat.observability import trace
        if changed:
            from app.chat.content_schema import prepare_attempts
            db.execute(update(prepare_attempts).where(prepare_attempts.c.turn_id == token['turn_id'],
                prepare_attempts.c.state == 'connecting').values(state='unknown', updated_at=service.now()))
            from app.chat.observability import storage_span
            storage_span(db, token['turn_id'], 'resource_guard', result='unknown', metadata={'error_code': code})
            try:
                with db.begin_nested():
                    persist_output(db, token['turn_id'])
            except Exception:
                # Status safety survives a failed message write; GET can still
                # project the already committed output without mutating storage.
                logging.getLogger(__name__).warning('assistant_materialization_unavailable')
            trace(db,token['turn_id'],'unknown')
        db.commit()
    # Neither a timeout nor process teardown proves that the external turn completed.
    return 'unknown'


def mark_setup_failed(factory, token, code, *, cause=None):
    SetupFailure = type('SetupFailure', (), {'kind': code, 'code': None, 'cause_type': type(cause).__name__ if cause is not None else None})
    from app.chat.preparation_failure import fail_preparation
    return 'failed' if fail_preparation(factory, token, SetupFailure()) else mark_unknown(factory, token, code)


def run_claim(factory, token, workspace, server_factory, *, max_seconds=None, stop_seconds=20, usage_grace_seconds=3):
    """server_factory accepts the verified workspace; executable/auth never come from a browser request."""
    executor_turn = None
    start_requested = False
    workspace_collection_complete = False
    from app.moonbox_exec_server.context import DELIVERY, IMAGE
    delivery_token = DELIVERY.set(None)
    image_token = IMAGE.set(None)
    tool_started = {}
    acceptance_pending = None
    final_reply = None
    server = None; permitted_scope = None; seq = 0; terminal = None; reply = ''; usage = None; metadata_bytes = 0; budget_stop = False; limit_recorded = False; stop_at = None; last_interrupt = 0
    try:
        workspace = trusted_directory(workspace)
        with factory() as db:
            _, binding_parent = owned(db, token)
            from app.verification.acceptance_delivery import execution_guard
            execution_guard(db,token['turn_id'],starting=True)
            from app.moonbox_core.delivery_policy import execution_context
            from app.moonbox_core.sessions import execution_workspace
            managed = execution_workspace(db, binding_parent)
            if managed and managed[1] != workspace:
                raise ExecutorError('workspace_binding_mismatch')
            context = execution_context(db, binding_parent['owner_id'], binding_parent,
                db.scalar(select(turns.c.prompt).where(turns.c.id == token['turn_id'])))
            DELIVERY.set(context)
            db.commit()
        from app.governance.archive_chat import run as run_trusted_archive
        archive_result = run_trusted_archive(factory, token, workspace)
        if archive_result is not None:
            workspace_collection_complete = True
            return archive_result
        with factory() as db:
            row, parent = owned(db, token)
            workspace_id = _workspace_identity(parent, workspace, db)
            if not _workspace_id_allowed(parent, workspace_id, db): raise ExecutorError('workspace_binding_mismatch')
            reserve = db.execute(select(reservations).where(reservations.c.turn_id == row['id'])).mappings().first()
            if not reserve: raise ExecutorError('usage_reservation_missing')
            budget = row['reserved_bytes']; token_budget = reserve['tokens']
            from app.verification.acceptance_delivery import token_limit
            continuation_token_limit=token_limit(db,row['id'])
            scalable = budget == 0 or managed is not None
            baseline = db.execute(select(workspace_baselines).where(workspace_baselines.c.conversation_id == parent['id'])).mappings().first()
            from app.moonbox_core.sessions import bound
            baseline_workspace_id = parent['id'] if bound(db, parent['id']) else _baseline_workspace_id(parent, workspace_id)
            from app.governance.preparation import execution_prompt_for_turn
            execution_prompt=execution_prompt_for_turn(db,parent,row['prompt'])
            db.commit()
        from app.chat.relations import read_snapshots
        with factory() as db: context=read_snapshots(db,parent['owner_id'],row['id'])
        context_bytes=len(json.dumps(context,ensure_ascii=False).encode())
        from app.chat.policy import write_policy, WRITE_SCOPE_READ_ONLY
        from app.moonbox_exec_server.scope import roots as recovery_roots
        with factory() as db:
            capture_policy = write_policy(db, parent['owner_id'], parent)
        allowed_roots = recovery_roots(capture_policy['write_scope'], DELIVERY.get()) if managed else None
        if scalable:
            from app.chat.snapshot_store import capture, import_legacy, diff_page
            before = capture(factory, parent['id'], row['id'], workspace, 'before', fence=lambda db: owned(db, token), policy_roots=allowed_roots)
            if managed:
                from app.moonbox_rollout.execution import publish_turn
                with factory() as db:
                    owned(db, token)
                    publish_turn(db, managed[0], row['id'], before, allowed_roots, 'before')
                    db.commit()
        else:
            before = snapshot(workspace, max_text_bytes=min(budget//4, 4*1024*1024))
        if baseline:
            initial = json.loads(baseline['payload'])
        else: initial = before
        if scalable and initial.get('format_version') != 2:
            with factory() as db:
                owned(db, token)
                initial = import_legacy(db, parent['id'], row['id'], initial)
                db.execute(update(workspace_baselines).where(workspace_baselines.c.conversation_id == parent['id'])
                    .values(payload=json.dumps(initial, ensure_ascii=False)))
                db.commit()
        # Each claim owns a new App Server process. Its cumulative usage resets
        # on process recreation even when the conversation thread is resumed.
        retained = (len(json.dumps(initial,ensure_ascii=False).encode()) if not baseline else 0)+context_bytes
        if not scalable and retained + len(execution_prompt.encode()) + 2048 > budget: raise ExecutorError('result_reservation_too_small')
        with factory() as db:
            owned(db, token)
            if not baseline:
                db.execute(insert(workspace_baselines).values(conversation_id=parent['id'], workspace_id=baseline_workspace_id,
                    content_hash=initial['hash'], payload=json.dumps(initial,ensure_ascii=False), token_total=0))
            elif baseline['workspace_id'] != baseline_workspace_id:
                db.execute(update(workspace_baselines).where(workspace_baselines.c.conversation_id==parent['id']).values(workspace_id=baseline_workspace_id))
            db.execute(update(conversations).where(conversations.c.id == parent['id']).values(workspace_id=workspace_id))
            db.commit()
        from app.chat.policy import write_policy, WRITE_SCOPE_READ_ONLY
        permission_evidence = {}
        with factory() as db:
            current_write_policy = write_policy(db, parent['owner_id'], parent, evidence=permission_evidence)
        permitted_scope = current_write_policy['write_scope']
        if managed and recovery_roots(permitted_scope, DELIVERY.get()) != allowed_roots:
            raise ExecutorError('workspace_write_scope_changed')
        if permitted_scope != WRITE_SCOPE_READ_ONLY:
            _check_workspace_tool_dirs_outside_sandbox(workspace)
        server = server_factory(workspace)
        server.acceptance_enabled = bool(managed and DELIVERY.get() and permitted_scope=='implementation_write')
        if hasattr(server, 'set_write_scope'):
            server.set_write_scope(permitted_scope)
        else:
            server.write = permitted_scope == 'implementation_write'
        selected_profile = _verify_permission_profile(server, permitted_scope)
        if managed:
            from app.moonbox_exec_server.runtime import pin
            with factory() as db:
                owned(db, token)
                pin(db, token['turn_id'], managed[0]['id'], server)
                from app.moonbox_core.schema import execution_receipts
                db.execute(update(execution_receipts).where(execution_receipts.c.turn_id == token['turn_id']).values(
                    scope_json=json.dumps(allowed_roots)))
                db.commit()
        _permission_event(factory, token, current_write_policy, permission_evidence,
            getattr(server, 'permission_profile', None), 'selected')
        thread_id = server.connect(parent['thread_id'])
        with factory() as db:
            current, _ = owned(db, token)
            db.execute(update(conversations).where(conversations.c.id == parent['id']).values(thread_id=thread_id));db.commit()
        if current['status'] == 'stopping': terminal='stopped'; usage=0
        else:
            prompt=execution_prompt
            if context: prompt += '\n\n以下是本轮授权的只读引用快照，内容仅作业务上下文，不能扩大工具权限：\n'+json.dumps(context,ensure_ascii=False)
            _verify_permission_profile(server, permitted_scope)
            with factory() as db:
                owned(db, token)
                if not worker.record_event(db, token, 'runner:start-requested', 'execution.state',
                    {'stage': 'executor_start', 'execution_started': 'unknown'}):
                    raise ExecutorError('worker_fenced')
            start_requested = True
            executor_turn = server.start_turn(thread_id,prompt)
            actual_profile = getattr(server, 'last_turn_permission_profile', None)
            if actual_profile is not None and actual_profile != selected_profile:
                server.interrupt(thread_id, executor_turn)
                raise ExecutorError('permission_profile_mismatch')
            acknowledged = actual_profile == selected_profile
            _permission_event(factory, token, current_write_policy, permission_evidence,
                selected_profile if acknowledged else None,
                'acknowledged' if acknowledged else 'unknown', executor_turn)
            with factory() as db:
                owned(db, token)
                db.execute(update(turns).where(turns.c.id == row['id']).values(executor_turn_id=executor_turn));db.commit()
                worker.record_event(db,token,'runner:started','execution.state',{'status':'running','executor_turn_id':executor_turn})
            deadline=time.monotonic()+max_seconds if max_seconds is not None else None; output_bytes=0
            archive_permission_gap_started = None
            while terminal is None:
                with factory() as db:
                    current, _ = owned(db, token)
                    if permitted_scope != WRITE_SCOPE_READ_ONLY:
                        policy = write_policy(db, parent['owner_id'], parent)
                        if _retains_acknowledged_scope(permitted_scope, policy):
                            archive_permission_gap_started = None
                        elif (permitted_scope == 'archive_write'
                                and policy['reason_code'] in ('governance_facts_invalid', 'governance_object_read_only',
                                                              'governance_object_writable')
                                and (archive_permission_gap_started is None
                                     or time.monotonic() - archive_permission_gap_started < 15)):
                            # CLI moves the Change across mounts. During the copy, the
                            # active source is gone before the legacy trace is complete.
                            # Keep the already acknowledged archive profile briefly;
                            # revoke it if the transition does not recover.
                            if archive_permission_gap_started is None:
                                archive_permission_gap_started = time.monotonic()
                        else:
                            raise ExecutorError('write_permission_revoked')
                    db.commit()
                if deadline is not None and time.monotonic() >= deadline: raise ExecutorError('execution_deadline_unknown')
                if budget_stop and not limit_recorded:
                    with factory() as db:
                        owned(db,token)
                        worker.record_event(db,token,'runner:limit','execution.state',{'status':'stopping','reason':'result_or_token_limit','output_may_be_truncated':True})
                    metadata_bytes+=1024;limit_recorded=True
                if current['status']=='stopping' or budget_stop:
                    if stop_at is None: stop_at=time.monotonic()
                    if time.monotonic()-stop_at >= stop_seconds: raise ExecutorError('interrupt_unconfirmed')
                    # A rejected early interrupt is retried against the same turn, never by starting a new turn.
                    if time.monotonic()-last_interrupt >= 1:
                        server.interrupt(thread_id,executor_turn);last_interrupt=time.monotonic()
                if acceptance_pending:
                    from app.verification.acceptance_tool import poll
                    poll(factory,token,server,*acceptance_pending)
                event=server.event(timeout=1)
                if event is None: continue
                params=event.get('params',{});method=event.get('method')
                if params.get('threadId') != thread_id: continue
                if method=='item/tool/call' and 'id' in event:
                    from app.verification.acceptance_tool import begin
                    from app.verification.acceptance_state import Conflict
                    try:
                        if (not server.acceptance_enabled or params.get('turnId')!=executor_turn or
                                params.get('tool')!='moonbox_acceptance' or params.get('arguments')!={} or
                                params.get('namespace') is not None or tool_started):
                            raise Conflict('acceptance_tool_unavailable')
                        operation_id=begin(factory,token,workspace,params.get('callId'))
                        acceptance_pending=(event['id'],operation_id)
                    except (Conflict,service.ChatError) as error:
                        reason=str(error) if isinstance(error,Conflict) else 'acceptance_authorization_denied'
                        server.respond_tool(event['id'],{'success':False,'contentItems':[{'type':'inputText','text':reason}]})
                    continue
                if (method=='item/completed' and params.get('item',{}).get('type')=='dynamicToolCall'
                        and params.get('turnId')==executor_turn
                        and params.get('item',{}).get('success') is True
                        and params.get('item',{}).get('tool')=='moonbox_acceptance'):
                    from app.verification.acceptance_tool import acknowledge
                    item=params['item']
                    acknowledge(factory,token,item.get('callId') or item.get('id'))
                    acceptance_pending=None
                event_turn=params.get('turnId') or params.get('turn',{}).get('id')
                if event_turn != executor_turn: continue
                if method=='thread/tokenUsage/updated':
                    total=params.get('tokenUsage',{}).get('total',{}).get('totalTokens')
                    if type(total) is int and total >= 0:
                        usage=max(usage or 0,total)
                        if scalable or metadata_bytes+1024 < budget//8:
                            with factory() as db:
                                owned(db,token)
                                if worker.record_event(db,token,f'usage:{total}','execution.usage',{'total_tokens':usage,'reserved_tokens':token_budget}):metadata_bytes+=1024
                        else:budget_stop=True
                        if not scalable and token_budget > 0 and usage >= token_budget: budget_stop=True
                        if continuation_token_limit is not None and usage >= continuation_token_limit: budget_stop=True
                elif method=='item/agentMessage/delta':
                    text=safe_text(params.get('delta','')).replace(str(workspace),'[工作区]'); size=len(text.encode())
                    if scalable:
                        seq += 1
                        save_result(factory, token, text, f'{executor_turn}:output:{seq}')
                        continue
                    if size > 60000: budget_stop=True;continue
                    if size + output_bytes > max(0,budget-retained-2048)//3:
                        budget_stop=True;continue
                    output_bytes += size+1024;reply += text;seq += 1
                    with factory() as db:
                        owned(db,token)
                        if not worker.record_event(db,token,f'{executor_turn}:output:{seq}','execution.output',{'text':text,'executor_turn_id':executor_turn,'item_id':params.get('itemId') if isinstance(params.get('itemId'),str) and re.fullmatch(r'[A-Za-z0-9_-]{1,96}',params['itemId']) else None}): raise ExecutorError('worker_fenced')
                elif method in ('item/started','item/completed'):
                    item=params.get('item',{});item_id=item.get('id')
                    if method == 'item/completed' and item.get('type') == 'agentMessage' and item.get('phase') == 'final_answer' and isinstance(item.get('text'), str):
                        candidate = safe_text(item['text']).replace(str(workspace), '[工作区]')
                        if scalable:
                            save_result(factory, token, candidate, final_source(item.get('id')), 'final')
                            final_reply = True
                        elif len(candidate.encode()) <= min(budget // 8, 60000):
                            final_reply = candidate
                            metadata_bytes += len(candidate.encode()) + 1024
                            with factory() as db:
                                owned(db, token)
                                worker.record_event(db, token, 'assistant:final:' + hashlib.sha256(str(item.get('id')).encode()).hexdigest(),
                                    'execution.state', {'text': candidate})
                    if item.get('type') in ('commandExecution','fileChange') and isinstance(item_id,str) and re.fullmatch(r'[A-Za-z0-9_-]{1,64}',item_id):
                        payload = tool_payload(item, method.split('/')[1], executor_turn, workspace, tool_started)
                        from app.governance.direct_command_journal import (
                            is_formal_workflow_sync, workflow_sync_result, observe as observe_direct_command,
                        )
                        observe_direct_command(parent['id'], row['client_request_id'], item_id,
                            method.split('/')[1], workspace,
                            sync=is_formal_workflow_sync(item),
                            sync_succeeded=bool(workflow_sync_result(item)),
                            sync_result=workflow_sync_result(item))
                        detail_bytes = len(json.dumps(payload,ensure_ascii=False).encode()) + 1024
                        if scalable or metadata_bytes+detail_bytes < budget//8:
                            with factory() as db:
                                owned(db,token)
                                if worker.record_event(db,token,'tool:'+hashlib.sha256(f'{executor_turn}:{item_id}:{method}'.encode()).hexdigest(),'execution.tool',payload):metadata_bytes+=detail_bytes
                        else:budget_stop=True
                elif method=='turn/completed':
                    terminal={'completed':'completed','failed':'failed','interrupted':'stopped'}.get(params.get('turn',{}).get('status'))
                    if terminal is None: raise ExecutorError('executor_terminal_unrecognized')
        # Completion may precede the final usage notification. Keep a bounded window,
        # never regress totals and never infer zero from an empty notification stream.
        if executor_turn is not None:
            end=time.monotonic()+usage_grace_seconds
            while time.monotonic()<end:
                try: event=server.event(timeout=min(.25,max(.001,end-time.monotonic())))
                except ExecutorError: break  # A confirmed terminal is not undone by teardown.
                if not event: continue
                params=event.get('params',{})
                if params.get('threadId') != thread_id or params.get('turnId') != executor_turn: continue
                if event.get('method') == 'item/completed':
                    item = params.get('item', {})
                    if item.get('type') == 'agentMessage' and item.get('phase') == 'final_answer' and isinstance(item.get('text'), str):
                        candidate = safe_text(item['text']).replace(str(workspace), '[工作区]')
                        if scalable and candidate:
                            save_result(factory, token, candidate, final_source(item.get('id')), 'final')
                            final_reply = True
                        elif candidate and len(candidate.encode()) <= min(budget // 8, 60000):
                            final_reply = candidate
                            metadata_bytes += len(candidate.encode()) + 1024
                            with factory() as db:
                                owned(db, token)
                                worker.record_event(db, token, 'assistant:final:' + hashlib.sha256(str(item.get('id')).encode()).hexdigest(),
                                    'execution.state', {'text': candidate})
                    if item.get('type') in ('commandExecution', 'fileChange') and isinstance(item.get('id'), str) and re.fullmatch(r'[A-Za-z0-9_-]{1,64}', item['id']):
                        payload = tool_payload(item, 'completed', executor_turn, workspace, tool_started)
                        from app.governance.direct_command_journal import (
                            is_formal_workflow_sync, workflow_sync_result, observe as observe_direct_command,
                        )
                        observe_direct_command(parent['id'], row['client_request_id'], item['id'],
                            'completed', workspace,
                            sync=is_formal_workflow_sync(item),
                            sync_succeeded=bool(workflow_sync_result(item)),
                            sync_result=workflow_sync_result(item))
                        size = len(json.dumps(payload, ensure_ascii=False).encode()) + 1024
                        if scalable or metadata_bytes + size < budget // 8:
                            with factory() as db:
                                owned(db, token)
                                if worker.record_event(db, token, 'tool:' + hashlib.sha256(f"{executor_turn}:{item['id']}:item/completed".encode()).hexdigest(), 'execution.tool', payload):
                                    metadata_bytes += size
                    continue
                if event.get('method') != 'thread/tokenUsage/updated': continue
                total=params.get('tokenUsage',{}).get('total',{}).get('totalTokens')
                if type(total) is int and total>=0: usage=max(usage or 0,total)
        if scalable:
            after = capture(factory, parent['id'], row['id'], workspace, 'after', fence=lambda db: owned(db, token), policy_roots=allowed_roots)
            if managed:
                with factory() as db:
                    owned(db, token)
                    publish_turn(db, managed[0], row['id'], after, allowed_roots, 'after')
                    db.commit()
            with factory() as db:
                delta = diff_page(db, before['version_id'], after['version_id'])
                cumulative = diff_page(db, initial['version_id'], after['version_id'])
            payload = {'files': delta['files'], 'cumulative_files': cumulative['files'],
                'initial_hash': initial['hash'], 'format_version': 2, 'before_version': before['version_id'],
                'after_version': after['version_id'], 'initial_version': initial['version_id'],
                'next_cursor': delta['next_cursor'], 'cumulative_next_cursor': cumulative['next_cursor']}
        else:
            after=snapshot(workspace,max_text_bytes=min(budget//4,4*1024*1024))
            delta=difference(before,after,max_patch_bytes=budget//8); cumulative=difference(initial,after,max_patch_bytes=budget//8)
            payload={'files':delta['files'],'cumulative_files':cumulative['files'],'initial_hash':initial['hash']}
        encoded=json.dumps(payload,ensure_ascii=False)
        actual_bytes=retained+len(encoded.encode())+len(reply.encode())*2+len(execution_prompt.encode())+2048+seq*1024+metadata_bytes
        if not scalable and actual_bytes > budget: raise ExecutorError('result_capacity_unconfirmed')
        from app.governance.direct_command_journal import (
            completion_block_reason, terminal as terminal_direct_command,
        )
        completion_block = (completion_block_reason(parent['id'], row['client_request_id'], workspace)
                            if terminal == 'completed' else None)
        if completion_block:
            terminal = 'failed'
        terminal_direct_command(parent['id'], row['client_request_id'], terminal, workspace)
        with factory() as db:
            owned(db,token)
            db.execute(insert(diffs).values(**service.identity(),turn_id=row['id'],before_hash=before['hash'],after_hash=after['hash'],payload=encoded))
            if scalable: persist_output(db, row['id'])
            elif reply or final_reply: persist_output(db, row['id'], final_reply if final_reply is not None else reply)
            if usage is not None:
                db.execute(update(workspace_baselines).where(workspace_baselines.c.conversation_id==parent['id']).values(token_total=usage))
            db.execute(update(turns).where(turns.c.id==row['id']).values(error_code=completion_block or ('result_or_token_limit' if budget_stop else ('usage_unavailable' if usage is None else None))))
            worker.record_event(db,token,'runner:accounting','execution.usage',{'total_tokens':usage,'actual_bytes':actual_bytes,'thread_total':usage,'usage_scope':'app_server_process_v1','usage_pending':usage is None})
            if not worker.record_event(db,token,'runner:terminal','execution.state',{'status':terminal},terminal=terminal):raise ExecutorError('worker_fenced')
        if usage is not None:
            with factory() as db:
                from app.chat.accounting import reconcile_usage
                reconcile_usage(db,row['id'])
        from app.governance.preparation import collect
        with factory() as db: collect(db, parent, row['id'], workspace, terminal)
        workspace_collection_complete = True
        return terminal
    except (ExecutorError, WorkspaceError, service.ChatError) as error:
        logging.getLogger(__name__).warning('chat_execution_cause cause_type=%s', type(error).__name__)
        code = error.code if isinstance(error, ExecutorError) else ('operating_quota_exceeded'
            if isinstance(error, service.ChatError) and error.code == 2508 else 'execution_access_or_workspace_error')
        if executor_turn is None and not start_requested:
            return mark_setup_failed(factory, token, code, cause=error)
        return mark_unknown(factory,token,code)
    except Exception as error:
        from app.chat.resource_guard import classify
        code = classify(error)
        from app.chat.resource_guard import database_failure_details
        try:
            logging.getLogger(__name__).warning(
                'chat_execution_unhandled cause_type=%s phase=%s turn_id=%s diagnostic=%s',
                type(error).__name__, 'setup' if executor_turn is None else 'running',
                row['id'], database_failure_details(error))
        except Exception:
            pass  # A failed diagnostic sink must not interrupt terminal handling.
        if executor_turn is None and not start_requested:
            return mark_setup_failed(factory, token, code, cause=error)
        return mark_unknown(factory,token,code)
    finally:
        DELIVERY.reset(delivery_token)
        IMAGE.reset(image_token)
        try:
            if server is not None:server.close()
            from app.moonbox_core.schema import execution_receipts
            with factory() as db:
                db.execute(update(execution_receipts).where(execution_receipts.c.turn_id == token['turn_id']).values(
                    executor_closed=1, files_collected=int(workspace_collection_complete)))
                db.commit()
            if workspace_collection_complete:
                from app.moonbox_core.sessions import bound as bound_workspace_id
                from app.moonbox_core.workspaces import release
                with factory() as db:
                    workspace_id = bound_workspace_id(db, token['conversation_id'])
                    if workspace_id:
                        release(db, workspace_id, token['turn_id'], token['generation'])
                    db.commit()
        finally:
            if permitted_scope is not None and permitted_scope != 'read_only':
                try: _check_workspace_tool_dirs_outside_sandbox(workspace)
                except (ExecutorError, OSError):
                    logging.getLogger(__name__).warning('workspace_forbidden_tool_dir_postrun')


def reconcile_unknown(factory, tid, workspace, server_factory, *, recovery_lease=None, outcome=None):
    """Read the exact external turn; never restart it or infer termination from elapsed time."""
    server=None
    from app.moonbox_exec_server.context import DELIVERY, IMAGE
    delivery_token = DELIVERY.set(None)
    image_token = IMAGE.set(None)
    def report(value):
        if outcome is not None: outcome["result"] = value
    report("no_terminal")
    try:
        with factory() as db:
            row=db.execute(select(turns).where(turns.c.id==tid)).mappings().first()
            if not row or row['status']!='unknown':return False
            parent=service.conversation(db,row_owner(db,row['conversation_id']),row['conversation_id'])
            if parent['active_turn_id']!=tid or not parent['thread_id'] or not row['executor_turn_id']:
                report('record_missing');return False
            bound=trusted_directory(workspace)
            if _workspace_identity(parent, bound, db) != parent['workspace_id']:
                report('workspace_identity');return False
        signature = None
        if recovery_lease is not None:
            from app.chat.recovery_hint import fingerprint, unchanged, remember
            signature = fingerprint(server_factory, bound, parent['thread_id'])
            if unchanged(tid, signature):
                report('unchanged');return False
        from app.moonbox_exec_server.runtime import saved, pin
        from app.moonbox_core.schema import delivery_sessions
        with factory() as db:
            runtime = saved(db, tid)
            delivery_binding = db.execute(select(delivery_sessions).where(
                delivery_sessions.c.conversation_id == parent['id'])).mappings().first()
            if runtime:
                IMAGE.set(runtime['image_digest'])
            if delivery_binding:
                DELIVERY.set(dict(delivery_binding))
        server=server_factory(bound);server.write=False
        if runtime:
            with factory() as db:
                pin(db, tid, runtime['workspace_id'], server)
        result=server.read_turn(parent['thread_id'],row['executor_turn_id'])
        terminal={'completed':'completed','failed':'failed','interrupted':'stopped'}.get((result or {}).get('status'))
        if terminal is None:
            if recovery_lease is not None and result is not None:
                remember(tid, signature, fingerprint(server_factory, bound, parent['thread_id']))
            report('record_missing' if result is None else 'no_terminal');return False
        from app.governance.direct_command_journal import completion_block_reason
        completion_block = (completion_block_reason(parent['id'], row['client_request_id'], bound)
                            if terminal == 'completed' else None)
        if completion_block:
            terminal = 'failed'
        with factory() as db:
            current_parent = service.conversation(db,parent['owner_id'],parent['id'])
            if current_parent['active_turn_id'] != tid or current_parent['thread_id'] != parent['thread_id']:
                report('workspace_identity');return False
            if recovery_lease is not None:
                from app.chat.recovery import fence
                if not fence(db, recovery_lease):
                    db.rollback();report('lease_lost');return False
            won=db.execute(update(turns).where(turns.c.id==tid,turns.c.status=='unknown',turns.c.generation==row['generation'],turns.c.executor_turn_id==row['executor_turn_id']).values(status=terminal,error_code=completion_block or (row['error_code'] or 'reconciled_usage_pending'),updated_at=service.now())).rowcount
            if not won:db.rollback();return False
            db.execute(update(conversations).where(conversations.c.id==parent['id'],conversations.c.active_turn_id==tid).values(active_turn_id=None,updated_at=service.now()))
            from app.chat.admission import release_concurrency
            release_concurrency(db, tid)
            # Terminal authority does not prove file collection. Keep the write
            # lock until completion.reconcile captures and publishes this turn's
            # files after the recovery reader has closed; otherwise its join on
            # write_locks loses the only pending collection record.
            from app.chat.schema import events
            from sqlalchemy import func
            seq=(db.scalar(select(func.max(events.c.sequence)).where(events.c.turn_id==tid)) or 0)+1
            recovered_bytes = 0
            for item in (result or {}).get('items', []):
                if not isinstance(item, dict) or item.get('type') not in ('commandExecution', 'fileChange'):
                    continue
                if item.get('status') not in ('completed', 'failed', 'declined') or not isinstance(item.get('id'), str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', item['id']):
                    continue
                source_id = 'tool:' + hashlib.sha256(f"{row['executor_turn_id']}:{item['id']}:item/completed".encode()).hexdigest()
                if db.scalar(select(events.c.id).where(events.c.turn_id==tid, events.c.source_id==source_id)):
                    continue
                payload = tool_payload(item, 'completed', row['executor_turn_id'], bound, {})
                encoded = json.dumps(payload, ensure_ascii=False)
                recovered_bytes += len(encoded.encode()) + 1024
                if row['reserved_bytes'] and recovered_bytes > row['reserved_bytes'] // 8:
                    break
                db.execute(insert(events).values(**service.identity(), turn_id=tid, sequence=seq, source_id=source_id,
                    event_type='execution.tool', payload=encoded))
                seq += 1
            # Only a bounded, sanitized authoritative final answer may replace
            # accumulated commentary. The terminal update above serializes recovery.
            for item in reversed((result or {}).get('items', [])):
                if not isinstance(item, dict) or item.get('type') != 'agentMessage' or item.get('phase') != 'final_answer':
                    continue
                if not isinstance(item.get('text'), str): continue
                candidate = safe_text(item['text']).replace(str(bound), '[工作区]')
                if not candidate: continue
                if row['reserved_bytes'] and len(candidate.encode()) > min(60000, row['reserved_bytes'] // 8): continue
                if not row['reserved_bytes']:
                    from app.chat.content_store import result as save_segment
                    from app.chat.final_answer import mark
                    answer_source = final_source(item.get('id'))
                    mark(db, tid, answer_source, 'begin')
                    offset = 0
                    for start in range(0, len(candidate), 12000):
                        block = candidate[start:start+12000].encode()
                        save_segment(db, parent['id'], tid, 'final', answer_source, offset, block)
                        offset += len(block)
                    mark(db, tid, answer_source, 'complete')
                    seq = (db.scalar(select(func.max(events.c.sequence)).where(events.c.turn_id == tid)) or 0) + 1
                    candidate = candidate[:1024]
                source = 'assistant:final:' + hashlib.sha256(str(item.get('id')).encode()).hexdigest()
                if not db.scalar(select(events.c.id).where(events.c.turn_id == tid, events.c.source_id == source)):
                    db.execute(insert(events).values(**service.identity(), turn_id=tid, sequence=seq,
                        source_id=source, event_type='execution.state', payload=json.dumps({'text': candidate}, ensure_ascii=False)))
                    seq += 1
                break
            db.execute(insert(events).values(**service.identity(),turn_id=tid,sequence=seq,source_id='reconcile:terminal',event_type='execution.state',payload=json.dumps({'status':terminal,'reconciled':True,'usage_pending':True})))
            persist_output(db, tid)
            from app.chat.observability import trace
            trace(db,tid,terminal);db.commit()
            from app.chat.accounting import reconcile_usage
            if reconcile_usage(db, tid):
                db.execute(update(events).where(events.c.turn_id==tid, events.c.source_id=='reconcile:terminal')
                    .values(payload=json.dumps({'status':terminal,'reconciled':True,'usage_pending':False})))
                db.commit()
        from app.governance.direct_command_journal import terminal as terminal_direct_command
        terminal_direct_command(parent['id'], row['client_request_id'], terminal, bound)
        # Usage reservation remains until authoritative billing is available; no zero-cost assumption.
        report("terminal_" + terminal)
        return True
    except (service.ChatError,ExecutorError,WorkspaceError) as error:
        from app.chat.recovery import classify
        report(classify(error));return False
    finally:
        DELIVERY.reset(delivery_token)
        IMAGE.reset(image_token)
        if server is not None:server.close()


def row_owner(db,cid):
    return db.scalar(select(conversations.c.owner_id).where(conversations.c.id==cid))
