"""Bridge authorized governance snapshots and the transactional object guard."""
import hashlib
import json
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from app.chat import service
from app.chat.workspace import WorkspaceError
from app.chat.schema import conversations, turns, relations, governance_candidates, governance_applications
from app.governance import execution_guard as guards, scope, store
from app.governance.snapshot import stable, cached_materialize, safe_load
from app.services import requirement_center as legacy


def fingerprint(prompt, materials, config):
    value = [prompt.strip(), service.material_fingerprint(materials or []), config['requested']]
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def replay(db, actor, parent, prompt, client_id, materials, config):
    from app.governance.preparation import _write_command
    from app.chat.relations import resolve_object
    command = _write_command(prompt)
    if not command:
        return None
    project = scope.authorize(db, actor, parent['space_id'], parent['repository_id'], write=True)
    oid = resolve_object(db, actor, parent['space_id'], parent['repository_id'], command[1])['id']
    row = guards.request(db, project.key, oid, actor, client_id)
    if not row:
        return None
    if row['request_fingerprint'] != fingerprint(prompt, materials, config):
        raise service.ChatError(2504, '同一请求标识不能用于不同输入')
    previous = service.turn(db, actor, row['operation_id'])
    result = service.public_turn(previous)
    result.update(service.material_counts(service.read_turn_materials(db, [previous['id']]).get(previous['id'], [])))
    return result


class IdentityIndex:
    """Pure identity lookup for one trusted snapshot; never an authorization cache."""

    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.registries = {}
        self.matches = {}

    def registry(self, folder, *, parsed=None):
        if folder not in self.registries:
            validated = getattr(self.snapshot, 'registries', None)
            data = (validated[folder] if validated is not None else parsed if parsed is not None
                    else safe_load(self.snapshot.files[f'issues/{folder}/_registry.yaml']))
            entries = data['entries']
            lookup = {}
            for entry in entries:
                full = entry['id']
                # A full ID can itself be a short ID. Preserve the original OR
                # predicate, including ambiguities, without counting it twice.
                for key in {full, '-'.join(full.split('-')[:2])}:
                    lookup.setdefault(key, []).append(full)
            self.matches[folder] = lookup
            self.registries[folder] = data
        return self.registries[folder]

    def resolve(self, oid):
        if not oid.startswith(('REQ-', 'BUG-')):
            return oid
        folder = 'requirements' if oid.startswith('REQ-') else 'bugs'
        self.registry(folder)
        matches = self.matches[folder].get(oid, [])
        if len(matches) != 1:
            raise service.ChatError(2604, '对象身份不唯一或已变化', 409, kind='governance_validation_failed')
        return matches[0]


def canonical_id(snapshot, oid, index=None):
    if index is not None:
        if index.snapshot is not snapshot:
            raise ValueError('identity snapshot mismatch')
        return index.resolve(oid)
    if oid.startswith(('REQ-', 'BUG-')):
        folder = 'requirements' if oid.startswith('REQ-') else 'bugs'
        matches = [entry['id'] for entry in safe_load(snapshot.files[f'issues/{folder}/_registry.yaml'])['entries']
                   if entry['id'] == oid or '-'.join(entry['id'].split('-')[:2]) == oid]
        if len(matches) != 1:
            raise service.ChatError(2604, '对象身份不唯一或已变化', 409, kind='governance_validation_failed')
        return matches[0]
    return oid


def stage_map(snapshot):
    identities = IdentityIndex(snapshot)
    with cached_materialize(snapshot, ('execution-guard', snapshot.revision)) as root:
        with legacy.using_governance_root(root, immutable=True, registry_index=identities):
            result = {canonical_id(snapshot, item.id, identities): item.stage for item in legacy.build_requirement_center_context().issues}
            import re
            for name, body in snapshot.files.items():
                match = re.fullmatch(r'iterations/(change|archive)/(sprint-\d{3})/sprint.yaml', name)
                if match:
                    plan = safe_load(body)
                    result[match[2]] = 'done' if match[1] == 'archive' and plan.get('status') in ('closed', 'completed', 'archived') else 'sprint-planning'
            return result


def prepare(db, actor, parent, prompt, client_id=None):
    """Resolve and authorize before admission starts its write transaction."""
    from app.governance.preparation import _write_command, _preflight_object_session
    from app.governance.reader import ProjectReader
    command = _write_command(prompt)
    if not command:
        return None
    action, oid = command
    project = scope.authorize(db, actor, parent['space_id'], parent['repository_id'], write=True)
    item = _preflight_object_session(db, actor, project, oid, action)
    if action == 'sprint-archive':
        from app.governance.sprint_object import require_final
        from .controlled_successor import authority
        with authority(db, project, actor):
            require_final(project.root, item['id'])
    reader = ProjectReader(db, actor, project)
    snapshot = reader.snapshot()
    oid = item['id']
    ids = [oid]
    if not oid.startswith(('REQ-', 'BUG-', 'sprint-')):
        ids += [entry['id'] for entry in reader.authorize_object(snapshot, oid, change=True, write=True)]
    stages = stage_map(snapshot)
    for key in sorted(set(ids)):
        reconcile_external(db, project, key, stages.get(key, 'unknown'), snapshot, actor=actor)
    db.commit()
    if client_id:
        from app.governance.direct_command_journal import prepare as prepare_journal
        prepare_journal(parent['id'], client_id, action, oid, snapshot.revision)
    return {'scope_key': project.key, 'action': action,
            'baseline_revision': snapshot.revision,
            'objects': [(key, stages.get(key, 'unknown')) for key in sorted(set(ids))]}


def acquire(db, context, tid, parent, actor, *, client_id=None, request_fingerprint=None):
    if context:
        for oid, stage in context['objects']:
            legacy_busy = db.scalar(select(conversations.c.id).join(
                relations, relations.c.conversation_id == conversations.c.id).where(
                    conversations.c.space_id == parent['space_id'],
                    conversations.c.repository_id == parent['repository_id'],
                    conversations.c.active_turn_id.is_not(None),
                    conversations.c.active_turn_id != tid,
                    relations.c.object_id == oid, relations.c.role == 'primary').limit(1))
            pending = db.scalar(select(governance_candidates.c.id).where(
                governance_candidates.c.scope_key == context['scope_key'],
                governance_candidates.c.object_id == oid,
                governance_candidates.c.state == 'pending').limit(1))
            if legacy_busy or pending:
                raise service.ChatError(2607, '该对象原执行尚未结束，请先核对', 409,
                                        kind='governance_object_busy')
            guards.acquire(db, scope_key=context['scope_key'], object_id=oid,
                           operation_id=tid, conversation_id=parent['id'], owner_id=actor,
                           action=context['action'], confirmed_stage=stage,
                           baseline_revision=context['baseline_revision'],
                           client_request_id=client_id, request_fingerprint=request_fingerprint)


def visible_state(db, actor, project, oid):
    row = guards.read(db, project.key, oid)
    result = guards.public_state(row, actor)
    if result['can_send']:
        legacy = db.execute(select(conversations).join(
            relations, relations.c.conversation_id == conversations.c.id).where(
                conversations.c.space_id == project.space_id,
                conversations.c.repository_id == project.repository_id,
                conversations.c.active_turn_id.is_not(None),
                relations.c.object_id == oid, relations.c.role == 'primary').order_by(
                    conversations.c.owner_id != actor, conversations.c.updated_at.desc()).limit(1)).mappings().first()
        if legacy:
            result = {'execution_state': 'running', 'can_send': False,
                      'reason_code': 'legacy_object_running',
                      'view_conversation_id': legacy['id'] if legacy['owner_id'] == actor else None}
    if result['can_send']:
        candidate = db.execute(select(governance_candidates).where(
            governance_candidates.c.scope_key == project.key,
            governance_candidates.c.object_id == oid,
            governance_candidates.c.state == 'pending').limit(1)).mappings().first()
        if candidate:
            result = {'execution_state': 'needs_review', 'can_send': False,
                      'reason_code': 'pending_governance_candidate',
                      'view_conversation_id': candidate['conversation_id'] if candidate['actor_id'] == actor else None}
    cid = result.get('view_conversation_id')
    if cid:
        try:
            parent = service.conversation(db, actor, cid)
            if parent['archived'] or parent['deleted_at']:
                result['view_conversation_id'] = None
        except service.ChatError:
            result['view_conversation_id'] = None
    return result


def visible_states(db, actor, project, object_ids):
    """Fresh request-local display projection; never used for send admission."""
    ids = list(dict.fromkeys(object_ids))
    result = {}
    # Bound SQL parameters and temporary rows. Permissions were checked by the
    # reader; actual send still uses the single-object transactional fence.
    for offset in range(0, len(ids), 256):
        batch = ids[offset:offset + 256]
        rows = {row['object_id']: row for row in db.execute(select(guards.execution_guards).where(
            guards.execution_guards.c.scope_key == project.key,
            guards.execution_guards.c.object_id.in_(batch))).mappings()}
        states = {oid: guards.public_state(rows.get(oid), actor) for oid in batch}
        idle = [oid for oid in batch if states[oid]['can_send']]
        if idle:
            busy = db.execute(select(conversations, relations.c.object_id.label('related_object_id')).join(
                relations, relations.c.conversation_id == conversations.c.id).where(
                    conversations.c.space_id == project.space_id,
                    conversations.c.repository_id == project.repository_id,
                    conversations.c.active_turn_id.is_not(None),
                    relations.c.object_id.in_(idle), relations.c.role == 'primary').order_by(
                        conversations.c.owner_id != actor, conversations.c.updated_at.desc())).mappings()
            for row in busy:
                oid = row['related_object_id']
                if states[oid]['can_send']:
                    states[oid] = {'execution_state': 'running', 'can_send': False,
                        'reason_code': 'legacy_object_running',
                        'view_conversation_id': row['id'] if row['owner_id'] == actor else None}
        idle = [oid for oid in batch if states[oid]['can_send']]
        if idle:
            for row in db.execute(select(governance_candidates).where(
                    governance_candidates.c.scope_key == project.key,
                    governance_candidates.c.object_id.in_(idle),
                    governance_candidates.c.state == 'pending')).mappings():
                oid = row['object_id']
                if states[oid]['can_send']:
                    states[oid] = {'execution_state': 'needs_review', 'can_send': False,
                        'reason_code': 'pending_governance_candidate',
                        'view_conversation_id': row['conversation_id'] if row['actor_id'] == actor else None}
        for oid, state in states.items():
            cid = state.get('view_conversation_id')
            if cid:
                try:
                    parent = service.conversation(db, actor, cid)
                    if parent['archived'] or parent['deleted_at']:
                        state['view_conversation_id'] = None
                except service.ChatError:
                    state['view_conversation_id'] = None
            result[oid] = (rows.get(oid), state)
    return result


def reconcile(db, actor, project, *, operation_id=None, snapshot=None):
    """Own the reconciliation boundary; never keep file work in a write transaction."""
    from app.governance.verification_transaction import VerificationPlan
    db.commit()
    from app.governance.writer import epoch
    before_epoch = epoch(db, project)
    query = select(guards.execution_guards).where(
        guards.execution_guards.c.scope_key == project.key,
        guards.execution_guards.c.owner_id == actor,
        guards.execution_guards.c.state.in_(('running', 'needs_review')))
    if operation_id:
        query = query.where(guards.execution_guards.c.operation_id == operation_id)
    rows = [dict(row) for row in db.execute(query).mappings()]
    db.rollback()
    for row in rows:
        plan = VerificationPlan(db)
        turn = plan.execute(select(turns).where(turns.c.id == row['operation_id'])).mappings().first()
        if not turn or turn['status'] not in ('completed', 'failed', 'stopped', 'unknown'):
            continue
        _reconcile_plan(plan, actor, project, operation_id=row['operation_id'], object_id=row['object_id'], snapshot=snapshot)
        if snapshot is not None and plan.statements and stable(project.root).revision != snapshot.revision:
            raise service.ChatError(2603, '项目文件已变化，请重新读取完整快照', 503)
        plan.apply(actor=actor, project=project,
                   expected={'object_id': row['object_id'], '_row': row}, turn=turn, expected_epoch=before_epoch)


def _reconcile_plan(db, actor, project, *, operation_id=None, object_id=None, snapshot=None):
    """Recheck terminal outcomes; never execute/retry a governance command here."""
    from app.governance.execution_validation import validate_result
    from app.governance.direct_command_journal import record_id
    rows = list(db.execute(select(guards.execution_guards).where(
        guards.execution_guards.c.scope_key == project.key,
        guards.execution_guards.c.owner_id == actor,
        guards.execution_guards.c.state.in_(('running', 'needs_review')))).mappings())
    if not rows:
        return
    stages = None
    for row in rows:
        if operation_id and row['operation_id'] != operation_id:
            continue
        if object_id and row['object_id'] != object_id:
            continue
        turn = db.execute(select(turns).where(turns.c.id == row['operation_id'])).mappings().first()
        if not turn or turn['status'] not in ('completed', 'failed', 'stopped', 'unknown'):
            continue
        if row['state'] == 'running' or row['terminal_status'] != turn['status']:
            guards.terminal(db, row['operation_id'], turn['status'])
        if turn['status'] == 'unknown':
            continue
        try:
            snapshot = snapshot or stable(project.root)
            rejected = db.execute(select(governance_candidates).where(
                governance_candidates.c.turn_id == row['operation_id'],
                governance_candidates.c.object_id == row['object_id'],
                governance_candidates.c.scope_key == project.key,
                governance_candidates.c.state == 'rejected',
                governance_candidates.c.error_code != 'source_recovery_blocked')).mappings().first()
            if (rejected and rejected['baseline_hash'] == snapshot.revision
                    and row['baseline_revision'] == snapshot.revision):
                # Existing source recovery restored the exact pre-run snapshot.
                # This only permits retry at the old stage, never advancement.
                guards.restore_without_write(db, scope_key=project.key, object_id=row['object_id'],
                    operation_id=row['operation_id'], version=row['version'], current_revision=snapshot.revision)
                continue
            try:
                record = store.read(record_id(row['conversation_id'], turn['client_request_id']), 'operation')
            except (FileNotFoundError, WorkspaceError):
                record = {}
            snapshot = snapshot or stable(project.root)
            if (turn['status'] in ('completed', 'failed', 'stopped') and record.get('phase') == 'terminal'
                    and record.get('classification') == 'no_governance_write'
                    and record.get('final_revision') == snapshot.revision):
                if guards.restore_without_write(db, scope_key=project.key, object_id=row['object_id'],
                        operation_id=row['operation_id'], version=row['version'], current_revision=snapshot.revision):
                    guards.observe(db, row['operation_id'], 'no_governance_write', object_id=row['object_id'], action=row['action'])
                continue
            if (row['action'] == 'opsx-archive' and record.get('action') == row['action']
                    and record.get('object_id') == row['object_id'] and record.get('phase') == 'terminal'
                    and record.get('classification') == 'no_governance_write'
                    and record.get('terminal_status') == turn['status']
                    and record.get('baseline_revision') == record.get('final_revision') == row['baseline_revision']):
                # No output from this ended attempt can be lost. Recheck the new
                # delivery before allowing a fresh archive attempt at its current revision.
                from app.governance.archive_admission import noop_archive_retry_ready
                if noop_archive_retry_ready(project.root, row['object_id'], snapshot, source_root=getattr(project, "source_root", None)):
                    if guards.restore_without_write(db, scope_key=project.key, object_id=row['object_id'],
                            operation_id=row['operation_id'], version=row['version'], current_revision=snapshot.revision,
                            verified_baseline_revision=row['baseline_revision']):
                        guards.observe(db, row['operation_id'], 'no_governance_write', object_id=row['object_id'], action=row['action'])
                    continue
            direct_manifest = None
            if (row['action'] not in ('req-review', 'bug-review', 'opsx-archive') and record
                    and (record.get('proof_schema_version') == 1 or any('completion_manifest' in step for step in record.get('steps', [])))):
                from app.governance.direct_completion import verify as verify_direct, DirectProofError
                try:
                    authorized = scope.authorize(db, actor, project.space_id, project.repository_id, write=True)
                    baseline = store.read(record_id(row['conversation_id'], turn['client_request_id']), 'baseline')
                    service.conversation(db, actor, row['conversation_id'])
                    if (baseline.get('binding_revision') != authorized.binding_revision
                            or not scope.visible(db, actor, authorized, row['object_id'])
                            or baseline.get('revision') != row['baseline_revision']):
                        raise DirectProofError('direct_binding_changed')
                    direct_manifest = verify_direct(record, snapshot.files, row['object_id'], row['action'])
                except DirectProofError as error:
                    if row['reason_code'] == str(error):
                        continue
                    g = guards.execution_guards.c
                    db.execute(update(guards.execution_guards).where(
                        g.operation_id == row['operation_id'], g.version == row['version'],
                        g.state == 'needs_review').values(reason_code=str(error)))
                    continue
            synced = any(isinstance(step, dict) and step.get('sync_succeeded') and step.get('source_revision') == snapshot.revision
                         for step in record.get('steps', []))
            synced = bool(direct_manifest) or synced
            if not synced:
                application = db.execute(select(governance_applications).join(governance_candidates,
                    governance_applications.c.candidate_id == governance_candidates.c.id).where(
                        governance_candidates.c.turn_id == row['operation_id'],
                        governance_candidates.c.object_id == row['object_id'],
                        governance_applications.c.scope_key == project.key,
                        governance_applications.c.state == 'applied',
                        governance_applications.c.phase == 'verified').limit(1)).mappings().first()
                if application:
                    try:
                        applied_record = store.read(application['id'], 'operation')
                    except (FileNotFoundError, WorkspaceError):
                        applied_record = recover_source_proof(project, row, application, snapshot)
                    proof = applied_record.get('workflow_sync', {}) if isinstance(applied_record, dict) else {}
                    if not isinstance(proof, dict):
                        proof = {}
                    synced = (proof.get('object_id') == row['object_id']
                              and proof.get('source_hash') == snapshot.revision)
                    if row['action'] in ('req-review', 'bug-review'):
                        from app.governance.completion_proof import verify, ProofError
                        candidate = db.execute(select(governance_candidates).where(
                            governance_candidates.c.id == application['candidate_id'])).mappings().one()
                        try:
                            authorized = scope.authorize(db, actor, project.space_id, project.repository_id, write=True)
                            if (candidate['actor_id'] != actor or candidate['scope_key'] != project.key
                                    or candidate['binding_revision'] != authorized.binding_revision
                                    or not scope.visible(db, actor, authorized, row['object_id'])):
                                raise ProofError('permission_denied')
                            synced = verify(store.read(candidate['id'], 'baseline'),
                                            store.read(candidate['id'], 'result'), proof,
                                            snapshot.files, row['object_id'], row['action'])
                        except ProofError as error:
                            if row['reason_code'] == str(error):
                                continue
                            g = guards.execution_guards.c
                            db.execute(update(guards.execution_guards).where(
                                g.scope_key == project.key, g.object_id == row['object_id'],
                                g.operation_id == row['operation_id'], g.version == row['version'],
                                g.state == 'needs_review').values(reason_code=str(error)))
                            continue
            if not synced and row['action'] == 'opsx-archive' and turn['status'] == 'completed':
                from app.governance.archive_proof import verify, ArchiveProofError
                try:
                    verify(project, row, turn, record, snapshot)
                    synced = True
                except ArchiveProofError as error:
                    if row['reason_code'] == str(error):
                        continue
                    # Preserve the lifecycle and expose a bounded verification failure.
                    g = guards.execution_guards.c
                    db.execute(update(guards.execution_guards).where(
                        g.scope_key == project.key, g.object_id == row['object_id'],
                        g.operation_id == row['operation_id'], g.version == row['version'],
                        g.state == 'needs_review').values(reason_code=str(error)))
                    continue
            if not synced or not validate_result(snapshot.files, row['object_id'], row['action']):
                continue
            # A final read fences files that changed while validation ran.
            current = stable(project.root)
            stages = stages or stage_map(snapshot)
            if direct_manifest:
                from app.governance.direct_completion import manifest, stamp
                if manifest(current.files, row['object_id'], row['action']) != direct_manifest:
                    continue
                rid = record_id(row['conversation_id'], turn['client_request_id'])
                record['final_verification'] = {'manifest': direct_manifest, 'checked_at': stamp(),
                    'operation_id': row['operation_id'], 'guard_version': row['version']}
                store.write(rid, 'operation', record)
                if manifest(stable(project.root).files, row['object_id'], row['action']) != direct_manifest:
                    continue
            confirmed = guards.confirm(db, scope_key=project.key, object_id=row['object_id'],
                           operation_id=row['operation_id'], version=row['version'],
                           result_revision=snapshot.revision, current_revision=snapshot.revision if direct_manifest else current.revision,
                           stage=stages.get(row['object_id'], row['confirmed_stage']),
                           business_valid=True, sync_valid=True, execution_ended=True,
                           recovery=turn['status'] in ('failed', 'stopped'))
            if confirmed:
                guards.observe(db, row['operation_id'], 'recovered_valid' if turn['status'] != 'completed' else 'validated',
                               object_id=row['object_id'], action=row['action'])
        except (FileNotFoundError, ValueError, OSError, WorkspaceError, service.ChatError):
            # Missing verifier evidence keeps the guard closed; the reader remains usable.
            continue


def reconcile_external(db, project, oid, stage, snapshot, *, actor=None):
    if actor is None:
        # Legacy callers retain their transaction contract; readers supply actor.
        return _reconcile_external_plan(db, project, oid, stage, snapshot)
    from app.governance.verification_transaction import VerificationPlan
    db.commit()
    from app.governance.writer import epoch
    before_epoch = epoch(db, project)
    db.rollback()
    plan = VerificationPlan(db)
    row = guards.read(plan, project.key, oid)
    _reconcile_external_plan(plan, project, oid, stage, snapshot)
    try:
        plan.apply(actor=actor, project=project,
                   expected={'object_id': oid, '_row': dict(row) if row else None}, expected_epoch=before_epoch)
    except IntegrityError:
        db.rollback()  # Concurrent admission wins; do not overwrite it.


def reconcile_external_batch(db, project, items, snapshot, *, actor):
    """Skip proven no-op projections in one read, never cache admission decisions.

    Plain external projections share bounded commits, retaining every object's
    fresh authorization and compare-and-swap. Historical operations keep their
    original verification path. Callers read current admission again afterwards.
    """
    db.commit()
    rows = {row['object_id']: row for row in db.execute(select(guards.execution_guards).where(
        guards.execution_guards.c.scope_key == project.key)).mappings()}
    db.rollback()
    ordinary = []
    for oid, stage in items:
        row = rows.get(oid)
        review = row and row['action'] in ('req-review', 'bug-review')
        if row and not review:
            if row['operation_id'] and row['state'] in ('running', 'needs_review'):
                continue
            if row['result_revision'] == snapshot.revision and row['state'] in ('idle', 'validated', 'recovered_valid'):
                continue
        if not row or (not row['operation_id'] and row['action'] == 'external-sync'):
            ordinary.append((oid, stage))
        else:
            reconcile_external(db, project, oid, stage, snapshot, actor=actor)
    if not ordinary:
        return
    from app.governance.verification_transaction import VerificationPlan
    from app.governance.writer import epoch
    before_epoch = epoch(db, project)
    db.rollback()
    batches = []
    for offset in range(0, len(ordinary), 64):
        plan, expected = VerificationPlan(db), []
        for oid, stage in ordinary[offset:offset + 64]:
            row = guards.read(plan, project.key, oid)
            # A newly acquired or reclassified guard belongs to its original
            # verifier, never this external-only batch.
            if row and (row['operation_id'] or row['action'] != 'external-sync'):
                continue
            expected.append({'object_id': oid, '_row': dict(row) if row else None})
            _reconcile_external_plan(plan, project, oid, stage, snapshot)
        if plan.statements:
            batches.append((plan, expected))
    if batches and stable(project.root).revision != snapshot.revision:
        raise service.ChatError(2603, '项目文件已变化，请重新读取完整快照', 503)
    for plan, expected in batches:
        try:
            plan.apply(actor=actor, project=project, expected=expected[0],
                       expected_batch=expected, expected_epoch=before_epoch)
        except IntegrityError:
            db.rollback()  # Concurrent insertion wins; never overwrite it.


def _reconcile_external_plan(db, project, oid, stage, snapshot):
    """External facts use structural governance validation, never a fake Chat turn."""
    from app.governance.execution_validation import validate_external
    g = guards.execution_guards.c
    row = guards.read(db, project.key, oid)
    if row and row['action'] in ('req-review', 'bug-review') and row['state'] in ('needs_review', 'validated', 'recovered_valid'):
        from app.governance.review_successor import verify_successor
        if verify_successor(db, project, row, stage, snapshot) and stable(project.root).revision == snapshot.revision:
            # Preserve the immutable original operation. Fence late callbacks with
            # a new version; a later action acquires its own operation identity.
            db.execute(update(guards.execution_guards).where(
                g.scope_key == project.key, g.object_id == oid,
                g.version == row['version'], g.operation_id == row['operation_id'],
                g.state == row['state']).values(
                    state='validated', confirmed_stage=stage,
                    result_revision=snapshot.revision, reason_code=None,
                    version=g.version + 1, updated_at=service.now()))
            return
    if row and row['operation_id'] and (row['state'] in ('running', 'needs_review') or
            (row['state'] in ('validated', 'recovered_valid') and row['action'] in ('req-review', 'bug-review'))):
        # Keep the historical operation addressable for explicit verification.
        return
    if row and row['result_revision'] == snapshot.revision and row['state'] in ('idle', 'validated', 'recovered_valid'):
        return
    valid = validate_external(snapshot.files, oid, stage)
    confirmed = stage if valid else (row['confirmed_stage'] if row else 'unknown')
    values = dict(state='idle' if valid else 'needs_review', confirmed_stage=confirmed,
                  result_revision=snapshot.revision if valid else None,
                  operation_id=None, conversation_id=None, owner_id=None,
                  client_request_id=None, request_fingerprint=None,
                  action='external-sync', reason_code=None if valid else 'external_result_unverified',
                  updated_at=service.now())
    if row and all(row[key] == value for key, value in values.items() if key != 'updated_at'):
        return  # Invalid external facts were rechecked; unchanged state needs no write.
    if row:
        db.execute(update(guards.execution_guards).where(g.scope_key==project.key, g.object_id==oid,
            g.version==row['version'], g.state==row['state'], g.operation_id==row['operation_id']).values(
                **values, version=g.version+1))
    else:
        try:
            with db.begin_nested():
                db.execute(insert(guards.execution_guards).values(scope_key=project.key, object_id=oid, version=0, **values))
        except IntegrityError:
            pass  # Concurrent admission wins; the subsequent read uses its guard.


def recover_source_proof(project, guard, application, snapshot):
    """Revalidate legacy source-mode completion; never trust an applied flag alone."""
    from app.governance.preparation import _verify_source_workflow_sync
    cid = application['candidate_id']
    baseline = store.read(cid, 'baseline')
    if baseline.get('workspace_mode') != 'source':
        return {}
    result = store.read(cid, 'result')
    expected = {name: body.encode() for name, body in baseline['files'].items()}
    for name, body in result['after'].items():
        if body is None:
            expected.pop(name, None)
        else:
            expected[name] = body.encode()
    if expected != snapshot.files:
        return {}
    proof = _verify_source_workflow_sync(project, guard['action'], guard['object_id'], expected)
    record = {'workflow_sync': proof, 'workspace_mode': 'source'}
    store.write(application['id'], 'operation', record)
    return record
