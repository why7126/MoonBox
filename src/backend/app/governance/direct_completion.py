"""Action-scoped completion facts. Private manifests contain hashes, never bodies.

Normal completion requires a recorded successful sync with a matching dependency
manifest. Historical reconstruction is explicit and preserves the old journal.
"""
import hashlib
import json
import math
import re
import yaml
from datetime import datetime, timezone

from app.governance.candidates import frontmatter
from app.governance.snapshot import safe_load, digest, validate
from app.governance.execution_validation import validate_result

SCHEMA_VERSION = 1
ACTIONS = frozenset(('sprint-propose', 'req-generate', 'bug-generate',
    'req-complete', 'bug-complete', 'req-review', 'bug-review',
    'req-opsx', 'bug-opsx', 'opsx-apply', 'opsx-modify', 'opsx-archive', 'sprint-archive'))
# Only machine-state trace documents permit narrative verification appendices.
APPENDICES = frozenset(('验证记录', '验证摘要', '规划验证记录', '变更记录'))


class DirectProofError(ValueError):
    pass


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str,
                      separators=(',', ':')).encode()


def normalized(name, body):
    if name.endswith('.md') and body.startswith(b'---\n'):
        fm, _ = frontmatter(body)
        fm.pop('updated_at', None)
        content = body.decode().split('---', 2)[2]
        sections = re.split(r'(?=^## )', content, flags=re.M)
        if name.endswith('/trace.md'):
            content = ''.join(s for s in sections if not s.strip() or s.splitlines()[0].removeprefix('## ').strip() not in APPENDICES)
        return encoded(fm) + content.encode()
    return body


def projection(files, oid, action):
    if action not in ACTIONS:
        raise DirectProofError('direct_action_unsupported')
    try:
        validate(files)  # Includes both registries' global uniqueness.
        selected = {n: b for n, b in files.items() if n.startswith('rules/')}
        links = []
        sprint = None
        if action == 'sprint-archive':
            from app.governance.execution_validation import validate_result
            if not validate_result(files, oid, action):
                raise ValueError('sprint_result')
            # A Sprint closes its entire scope: all governance facts participate
            # in proof, so a later scope/result edit invalidates this proof.
            return {n: normalized(n, b) for n, b in files.items()
                    if n.startswith(('iterations/', 'issues/', 'openspec/', 'rules/'))}
        if oid.startswith(('REQ-', 'BUG-')):
            folder = 'requirements' if oid.startswith('REQ-') else 'bugs'
            registry = f'issues/{folder}/_registry.yaml'
            entries = [e for e in safe_load(files[registry])['entries'] if e['id'] == oid]
            if len(entries) != 1:
                raise ValueError('identity')
            entry = dict(entries[0]); base = entry['path'].rstrip('/')
            if not re.fullmatch(rf'issues/{folder}/(?:plan|review|archive)/{re.escape(oid)}', base):
                raise ValueError('path')
            entry.pop('updated_at', None)
            selected[registry] = encoded(entry)
            selected.update({n: normalized(n, b) for n, b in files.items() if n.startswith(base + '/')})
            trace, _ = frontmatter(files[base + '/trace.md'])
            from app.governance.archive_admission import linked_changes
            links = linked_changes({}, trace)
            sprint = trace.get('iteration')
            parent = trace.get('related_requirement')
            if parent and parent != oid:
                reg = 'issues/requirements/_registry.yaml'
                parents = [e for e in safe_load(files[reg])['entries'] if e['id'] == parent]
                if len(parents) != 1:
                    raise ValueError('parent')
                prefix = parents[0]['path'].rstrip('/') + '/'
                selected[reg + '#' + parent] = encoded(parents)
                selected.update({n: b for n, b in files.items() if n.startswith(prefix)})
        else:
            links = [oid]
        for cid in links:
            bases = [n[:-9] for n in files if n == f'openspec/changes/{cid}/trace.md'
                     or re.fullmatch(rf'openspec/archive/\d{{4}}-\d{{2}}-\d{{2}}-{re.escape(cid)}/trace.md', n)]
            if len(bases) != 1:
                raise ValueError('change_identity')
            base = bases[0]
            selected.update({n: normalized(n, b) for n, b in files.items() if n.startswith(base + '/')})
            ct, _ = frontmatter(files[base + '/trace.md'])
            sprint = sprint or ct.get('iteration')
            for n in files:
                if n.startswith(base + '/specs/') and n.endswith('/spec.md'):
                    capability = n[len(base + '/specs/'):].split('/')[0]
                    canonical = f'openspec/specs/{capability}/spec.md'
                    selected[canonical] = files.get(canonical, b'')
        if sprint:
            plans = [(n, safe_load(b)) for n, b in files.items() if n in (
                f'iterations/change/{sprint}/sprint.yaml', f'iterations/archive/{sprint}/sprint.yaml')]
            if len(plans) != 1:
                raise ValueError('sprint')
            name, plan = plans[0]
            capacity = float(plan.get('capacity_person_days', 30))
            estimates = plan.get('scope_estimates', [])
            values = [float(e.get('estimated_person_days', e.get('person_days'))) for e in estimates]
            if any(not math.isfinite(v) or v < 0 for v in values):
                raise ValueError('estimate')
            total = sum(values)
            if not math.isfinite(capacity) or capacity <= 0 or not math.isfinite(total) or total > capacity * 1.2:
                raise ValueError('capacity')
            for kind in ('requirements', 'bugs', 'changes'):
                members = plan.get(kind, [])
                if not isinstance(members, list) or len(members) != len(set(members)):
                    raise ValueError('members')
            selected[name] = encoded({
                'sprint_id': plan['sprint_id'], 'status': plan['status'],
                'capacity': capacity,
                'members': {k: sorted(x for x in plan.get(k, []) if x == oid or x in links)
                            for k in ('requirements', 'bugs', 'changes')},
                'estimates': [e for e in estimates if e.get('id') == oid or e.get('change') in links],
            })
        return selected
    except (KeyError, TypeError, AttributeError, ValueError, yaml.YAMLError) as error:
        if isinstance(error, DirectProofError):
            raise
        raise DirectProofError('direct_dependency_invalid') from None


def manifest(files, oid, action):
    selected = projection(files, oid, action)
    return {'schema_version': SCHEMA_VERSION, 'object_id': oid, 'action': action,
            'revision': digest(selected),
            'files': {n: hashlib.sha256(b).hexdigest() for n, b in sorted(selected.items())}}


def verify(record, files, oid, action):
    if (record.get('action') != action or record.get('object_id') != oid
            or record.get('schema_version') != 1):
        raise DirectProofError('direct_command_identity_mismatch')
    steps = [s for s in record.get('steps', []) if s.get('sync_succeeded')]
    if not steps:
        raise DirectProofError('direct_sync_missing')
    step = steps[-1]
    result = step.get('sync_result')
    if result is None and action in ('opsx-apply', 'opsx-modify'):
        # Old journals cannot distinguish a progress/dry-run observation from
        # delivery completion. Explicit successor verification supplies new proof.
        raise DirectProofError('direct_completion_event_missing')
    if result is not None:
        expected = {action.replace('-', '.', 1)}
        if action in ('opsx-apply', 'opsx-modify'):
            expected.add('opsx.accept')
        if result.get('event') not in expected or result.get('ok') is not True or result.get('mode') != 'write':
            raise DirectProofError('direct_completion_event_missing')
    proof = step.get('completion_manifest')
    if proof is None:
        raise DirectProofError('direct_historical_evidence_missing')
    if (not isinstance(proof, dict) or proof.get('schema_version') != SCHEMA_VERSION
            or proof.get('object_id') != oid or proof.get('action') != action
            or not isinstance(proof.get('files'), dict)):
        raise DirectProofError('direct_proof_invalid')
    current = manifest(files, oid, action)
    if proof != current:
        raise DirectProofError('direct_dependency_conflict')
    if ((action.startswith('req-') and not oid.startswith('REQ-'))
            or (action.startswith('bug-') and not oid.startswith('BUG-'))
            or not validate_result(files, oid, action)):
        raise DirectProofError('direct_result_invalid')
    return current


def differences(before, after, *, limit=30):
    old, new = before.get('files', {}), after.get('files', {})
    return [{'path': name, 'kind': 'added' if name not in old else 'deleted' if name not in new else 'modified'}
            for name in sorted(old.keys() | new.keys()) if old.get(name) != new.get(name)][:limit]


def stamp():
    return datetime.now(timezone.utc).isoformat()


def successor_evidence(record):
    """Expose only confirmed, safe report identities, never private journal data."""
    from app.governance.workflow_receipt import safe_id
    final = record.get('final_verification', {})
    if final.get('pending_confirmation') or final.get('mode') != 'successor_revalidation':
        return {}
    runs = final.get('successor', {}).get('acceptance_runs', {})
    return {cid: run for cid, run in runs.items() if safe_id(cid) and safe_id(run)} if isinstance(runs, dict) else {}


def operation_context(db, actor, turn_id):
    from sqlalchemy import select
    from app.chat import service
    from app.governance import execution_guard as guards, scope, store
    from app.governance.direct_command_journal import record_id, record_block_reason
    turn = service.turn(db, actor, turn_id)
    parent = service.conversation(db, actor, turn['conversation_id'])
    project = scope.authorize(db, actor, parent['space_id'], parent['repository_id'], write=True)
    row = db.execute(select(guards.execution_guards).where(
        guards.execution_guards.c.scope_key == project.key,
        guards.execution_guards.c.operation_id == turn_id,
        guards.execution_guards.c.owner_id == actor)).mappings().first()
    if not row or not scope.visible(db, actor, project, row['object_id']):
        raise service.ChatError(2601, '原执行不存在或无权核验', 404)
    rid = record_id(row['conversation_id'], turn['client_request_id'])
    reason = record_block_reason(row['conversation_id'], turn['client_request_id'],
        action=row['action'], object_id=row['object_id'], revision=row['baseline_revision'])
    if reason:
        raise DirectProofError(reason)
    baseline = store.read(rid, 'baseline')
    if baseline.get('binding_revision') != project.binding_revision:
        raise DirectProofError('direct_binding_changed')
    record = store.read(rid, 'operation')
    if record.get('proof_schema_version') not in (None, SCHEMA_VERSION):
        raise DirectProofError('direct_proof_invalid')
    return turn, project, row, rid, baseline, record


def historical_status(db, actor, turn_id):
    """Read a prior signature after the mutable current guard has advanced.

    This is historical display only, never current admission or recovery authority.
    """
    from app.chat import service
    from app.governance import scope, store
    from app.governance.direct_command_journal import record_id, record_block_reason
    turn = service.turn(db, actor, turn_id)
    parent = service.conversation(db, actor, turn['conversation_id'])
    project = scope.authorize(db, actor, parent['space_id'], parent['repository_id'], write=True)
    reason = record_block_reason(parent['id'], turn['client_request_id'])
    if reason:
        raise service.ChatError(2601, '原执行不存在或无权核验', 404)
    rid = record_id(parent['id'], turn['client_request_id'])
    baseline = store.read(rid, 'baseline')
    record = store.read(rid, 'operation')
    final = record.get('final_verification', {})
    proof = final.get('manifest', {})
    if (baseline.get('binding_revision') != project.binding_revision
            or not scope.visible(db, actor, project, record['object_id'])
            or record.get('proof_schema_version') not in (None, SCHEMA_VERSION)
            or final.get('operation_id') != turn_id
            or not final.get('checked_at')
            or final.get('pending_confirmation')
            or proof.get('schema_version') != SCHEMA_VERSION
            or proof.get('object_id') != record['object_id']
            or proof.get('action') != record['action']
            or not isinstance(proof.get('files'), dict)
            or not (any(s.get('sync_succeeded') for s in record['steps'])
                    or (final.get('mode') == 'successor_revalidation'
                        and final.get('successor', {}).get('kind') == 'verified_successor'
                        and final.get('successor', {}).get('original_operation_id') == turn_id))):
        raise service.ChatError(2601, '原执行不存在或无权核验', 404)
    from app.governance.snapshot import stable
    current = stable(project.root)
    try:
        still_valid = (manifest(current.files, record['object_id'], record['action']) == proof
                       and validate_result(current.files, record['object_id'], record['action']))
    except (ValueError, OSError):
        still_valid = False
    return {'available': True, 'state': 'validated' if still_valid else 'historical', 'version': None,
            'reason_code': 'direct_historical_verified' if still_valid else 'direct_historical_record_preserved', 'can_verify': False,
            'last_checked_at': final['checked_at'], 'differences': [], 'successor_evidence': successor_evidence(record),
            'historical_evidence_missing': final.get('historical_attribution') == 'unknown'}


def auto_verification(db, actor, turn_id, project, guard):
    from sqlalchemy import select
    from app.governance.completion_handoff import handoffs
    unavailable = {'state': 'unavailable', 'reason_code': None}
    if guard['owner_id'] != actor or guard['operation_id'] != turn_id or guard['scope_key'] != project.key:
        return unavailable
    job = db.execute(select(handoffs).where(handoffs.c.scope_key == project.key,
        handoffs.c.object_id == guard['object_id'], handoffs.c.guard_version == guard['version'],
        handoffs.c.operation_id == turn_id)).mappings().first()
    if not job or job['state'] not in ('pending', 'checking', 'confirmed', 'blocked'):
        return unavailable
    # Stable codes only, never return an exception or untrusted diagnostic text.
    import re
    reason = job['reason_code']
    return {'state': job['state'], 'reason_code': reason if isinstance(reason, str) and re.fullmatch(r'[a-z][a-z0-9_]{0,63}', reason) else None}


def status(db, actor, turn_id):
    from app.chat import service
    try:
        turn, project, row, rid, baseline, record = operation_context(db, actor, turn_id)
    except DirectProofError as error:
        return {'available': True, 'reason_code': str(error), 'can_verify': False,
                'state': 'needs_review', 'version': None, 'last_checked_at': None}
    except service.ChatError:
        return historical_status(db, actor, turn_id)
    terminal = turn['status'] in ('completed', 'failed', 'stopped')
    from app.governance.successor_completion import startup_proof, original_time
    successor_candidate = False
    successor_reason = None
    if terminal and row['state'] == 'needs_review' and row['action'] in ('opsx-apply', 'opsx-modify'):
        try:
            startup_proof(row, record, baseline)
            original_time(turn['created_at'])
            successor_candidate = True
        except DirectProofError as error:
            successor_reason = str(error)
    changes = []
    has_sync = any(step.get('sync_succeeded') for step in record['steps'])
    legacy_missing = record.get('proof_schema_version') != SCHEMA_VERSION and has_sync and not any(step.get('completion_manifest') for step in record['steps'])
    proofs = [step.get('completion_manifest') for step in record['steps'] if step.get('completion_manifest')]
    if row['state'] == 'needs_review' and proofs:
        from app.governance.snapshot import stable
        try:
            changes = differences(proofs[-1], manifest(stable(project.root).files, row['object_id'], row['action']))
        except (ValueError, OSError):
            pass

    return {'auto_verification': auto_verification(db, actor, turn_id, project, row),
            'available': True, 'state': row['state'], 'version': row['version'], 'differences': changes,
            'reason_code': ('direct_successor_verified' if row['state'] in ('validated', 'recovered_valid') and record.get('final_verification', {}).get('mode') == 'successor_revalidation' else 'direct_successor_available' if successor_candidate and not has_sync else successor_reason if not has_sync and successor_reason else 'direct_sync_missing' if row['state'] == 'needs_review' and not has_sync else 'direct_historical_evidence_missing' if row['state'] == 'needs_review' and legacy_missing else row['reason_code']),
            'last_checked_at': (None if record.get('final_verification', {}).get('pending_confirmation')
                                else record.get('final_verification', {}).get('checked_at')),
            'can_verify': terminal and (has_sync or successor_candidate) and row['state'] == 'needs_review' and row['action'] not in ('req-review','bug-review','opsx-archive'),
            'historical_evidence_missing': legacy_missing,
            'successor_evidence': successor_evidence(record)}


def recover(db, actor, turn_id, expected_version):
    from sqlalchemy import update
    from app.chat import service
    from app.governance import store, execution_guard as guards, scope
    from app.governance.snapshot import stable
    from app.governance.execution_context import stage_map
    turn, project, row, rid, baseline, record = operation_context(db, actor, turn_id)
    if row['version'] != expected_version:
        raise DirectProofError('direct_operation_superseded')
    if row['state'] in ('validated', 'recovered_valid'):
        # A crash after the database commit may leave only the pending journal
        # signature. The same committed guard version safely finishes that write.
        final = record.get('final_verification', {})
        if (final.get('pending_confirmation') and final.get('operation_id') == turn_id
                and final.get('guard_version') == expected_version):
            final['pending_confirmation'] = False
            store.write(rid, 'operation', record)
        return status(db, actor, turn_id)
    if turn['status'] not in ('completed', 'failed', 'stopped') or row['state'] != 'needs_review':
        raise DirectProofError('direct_execution_active')
    if row['action'] in ('req-review', 'bug-review', 'opsx-archive'):
        raise DirectProofError('direct_specialized_verification_required')
    snapshot = stable(project.root)
    successor = None
    legacy = not any('completion_manifest' in s for s in record['steps'])
    independent = row['action'] in ('opsx-apply', 'opsx-modify') and not any(
        step.get('sync_succeeded') and step.get('completion_manifest') for step in record['steps'])
    if independent:
        from app.governance.successor_completion import verify_successor
        proof, successor = verify_successor(project, row, record, snapshot, baseline, original_started_at=turn['created_at'])
    elif legacy:
        # Reconstruct CURRENT evidence, never pretend to recover a historic diff.
        # Specialized review/archive protocols are not replaced by this path.
        if row['action'] in ('req-review', 'bug-review', 'opsx-archive'):
            raise DirectProofError('direct_specialized_verification_required')
        if turn['status'] != 'completed' or not any(s.get('sync_succeeded') for s in record['steps']):
            raise DirectProofError('direct_sync_missing')
        original = {n: b.encode() for n, b in baseline['files'].items()}
        # Inputs outside the action's deliverables cannot be silently rebased.
        protected = {n for n in original.keys() | snapshot.files.keys() if n.startswith(('rules/', 'openspec/specs/'))}
        if any(original.get(n) != snapshot.files.get(n) for n in protected):
            raise DirectProofError('direct_dependency_conflict')
        if not validate_result(snapshot.files, row['object_id'], row['action']):
            raise DirectProofError('direct_result_invalid')
        proof = manifest(snapshot.files, row['object_id'], row['action'])
        # For historically generated Changes, all pre-existing Issue inputs stay
        # protected. Only trace status/links are the expected workflow outputs.
        if row['action'] in ('req-opsx', 'bug-opsx'):
            historical_opsx_inputs(original, snapshot.files, row['object_id'], row['action'])
    else:
        try:
            proof = verify(record, snapshot.files, row['object_id'], row['action'])
        except DirectProofError as error:
            if str(error) not in ('direct_dependency_conflict', 'direct_result_invalid', 'direct_completion_event_missing'):
                raise
            from app.governance.successor_completion import verify_successor
            proof, successor = verify_successor(project, row, record, snapshot, baseline)
    current = stable(project.root)
    if manifest(current.files, row['object_id'], row['action']) != proof:
        raise DirectProofError('direct_dependency_conflict')
    # Persist the new current verification separately; old sync steps are immutable.
    record['final_verification'] = {'manifest': proof, 'checked_at': stamp(),
        'operation_id': turn_id, 'guard_version': expected_version,
        'pending_confirmation': True,
        'mode': 'historical_current_revalidation' if legacy else 'scoped_revalidation',
        'historical_attribution': 'unknown' if legacy else 'manifest_available'}
    if successor is not None:
        record['final_verification']['successor'] = successor
        record['final_verification']['mode'] = 'successor_revalidation'
    store.write(rid, 'operation', record)
    latest = stable(project.root)
    if manifest(latest.files, row['object_id'], row['action']) != proof:
        raise DirectProofError('direct_dependency_conflict')
    if successor is not None:
        verify_successor(project, row, record, latest, baseline, original_started_at=turn['created_at'])
    authorized = scope.authorize(db, actor, project.space_id, project.repository_id, write=True)
    if authorized.binding_revision != project.binding_revision or not scope.visible(db, actor, authorized, row['object_id']):
        raise DirectProofError('direct_binding_changed')
    if not guards.confirm(db, scope_key=project.key, object_id=row['object_id'],
        operation_id=turn_id, version=expected_version, result_revision=current.revision,
        current_revision=current.revision, stage=stage_map(current).get(row['object_id'], row['confirmed_stage']),
        business_valid=True, sync_valid=True, execution_ended=True, recovery=True):
        raise DirectProofError('direct_operation_superseded')
    guards.observe(db, turn_id, 'direct_revalidated', object_id=row['object_id'], action=row['action'])
    db.commit()
    record['final_verification']['pending_confirmation'] = False
    store.write(rid, 'operation', record)
    return status(db, actor, turn_id)


def historical_opsx_inputs(original, current, oid, action):
    """Permit only generated Change links and explicit workflow bookkeeping.

    These are current validation rules, not reconstructed historical evidence.
    """
    from app.governance.archive_admission import linked_changes
    traces = [n for n in current if '/' + oid + '/' in n and n.endswith('/trace.md')]
    if len(traces) != 1 or traces[0] not in original:
        raise DirectProofError('direct_dependency_conflict')
    before_trace, _ = frontmatter(original[traces[0]])
    after_trace, _ = frontmatter(current[traces[0]])
    links = linked_changes({}, after_trace)
    if len(links) != 1:
        raise DirectProofError('direct_dependency_conflict')
    cid = links[0]
    mutable = {'updated_at', 'related_change', 'openspec_changes'}
    if {k:v for k,v in before_trace.items() if k not in mutable} != {k:v for k,v in after_trace.items() if k not in mutable}:
        raise DirectProofError('direct_dependency_conflict')
    for n, body in original.items():
        if '/' + oid + '/' not in n or n.endswith('/trace.md'):
            continue
        actual = current.get(n)
        if actual is None:
            raise DirectProofError('direct_dependency_conflict')
        def canonical(b):
            fm, _ = frontmatter(b)
            fm.pop('updated_at', None)
            if fm.get('related_change') in (None, cid):
                fm.pop('related_change', None)
            content = b.decode().split('---', 2)[2]
            content = content.replace('已创建 '+cid+'（proposed）', '尚未创建 Change')
            if n.endswith('/acceptance.md'):
                content = re.sub(r'^source_change: (?:null|'+re.escape(cid)+r')$', 'source_change: null', content, flags=re.M)
                content = re.sub(r'^source_event: (?:sprint\.propose|'+re.escape(action.replace('-', '.'))+r')$', 'source_event: sprint.propose', content, flags=re.M)
            return encoded(fm) + content.encode()
        if canonical(body) != canonical(actual):
            raise DirectProofError('direct_dependency_conflict')
