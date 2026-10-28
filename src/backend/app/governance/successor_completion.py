"""Explicit current delivery verification; never rewrites an old execution."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import re
import json
from app.governance.candidates import frontmatter
from app.governance.acceptance_evidence import read_plan, readiness, latest_manifest
from app.governance.archive_admission import linked_changes, issue_acceptance, issue_identity


def startup_proof(guard, record, baseline):
    """Validate private startup content against the immutable operation digest."""
    from app.governance.direct_completion import manifest, DirectProofError
    from app.governance.snapshot import digest
    try:
        if (guard['action'] not in ('opsx-apply', 'opsx-modify')
                or record.get('schema_version') != 1
                or any(baseline.get(k) != guard[k] or record.get(k) != guard[k]
                       for k in ('object_id', 'action'))
                or baseline.get('revision') != guard['baseline_revision']
                or record.get('baseline_revision') != guard['baseline_revision']):
            raise ValueError('identity')
        files = baseline['files']
        if not files or not isinstance(files, dict) or any(
                not isinstance(k, str) or not isinstance(v, str) for k, v in files.items()):
            raise ValueError('files')
        original = {k: v.encode() for k, v in files.items()}
        if digest(original) != guard['baseline_revision']:
            raise ValueError('digest')
        return manifest(original, guard['object_id'], guard['action'])
    except (KeyError, TypeError, ValueError):
        raise DirectProofError('direct_successor_baseline_invalid') from None


def original_time(value):
    from app.governance.direct_completion import DirectProofError
    try:
        result = datetime.fromisoformat(value)
        if result.tzinfo is None:
            raise ValueError('timezone')
        return result.astimezone(timezone.utc)
    except (TypeError, ValueError):
        raise DirectProofError('direct_successor_time_invalid') from None


def verify_successor(project, guard, record, snapshot, baseline, *, original_started_at=None):
    from app.governance.direct_completion import manifest, differences, DirectProofError
    from app.governance.execution_validation import validate_result
    from app.governance.snapshot import safe_load
    # Specialized review/archive protocols must not be bypassed by this verifier.
    if guard['action'] not in ('opsx-apply', 'opsx-modify'):
        raise DirectProofError('direct_successor_unsupported')
    oid = guard['object_id']
    current = manifest(snapshot.files, oid, guard['action'])
    proofs = [s['completion_manifest'] for s in record.get('steps', []) if s.get('completion_manifest') and s.get('sync_succeeded')]
    independent = not proofs
    old = startup_proof(guard, record, baseline) if independent else proofs[-1]
    began = original_time(original_started_at) if independent else None
    if old.get('object_id') != oid or old.get('action') != guard['action']:
        raise DirectProofError('direct_command_identity_mismatch')
    # Display truncation must never truncate the authorization decision.
    changes = differences(old, current, limit=None)
    if any(d['path'].startswith(('openspec/specs/', 'iterations/')) for d in changes):
        raise DirectProofError('direct_dependency_conflict')
    try:
        domain = 'bugs' if oid.startswith('BUG-') else 'requirements'
        entries = safe_load(snapshot.files[f'issues/{domain}/_registry.yaml'])['entries']
        base = next(e['path'].rstrip('/') for e in entries if e['id'] == oid)
        trace, _ = frontmatter(snapshot.files[base + '/trace.md'])
        links = linked_changes({}, trace)
        if not links or not validate_result(snapshot.files, oid, guard['action']):
            raise DirectProofError('direct_result_invalid')
        covered, derived, runs, dependencies, task_proofs = set(), {base + '/trace.md'}, {}, {}, {}
        if not issue_acceptance(project.root, project.root / base, links,
                                source_root=getattr(project, 'source_root', None))['ready']:
            raise DirectProofError('direct_successor_evidence_invalid')
        for cid in links:
            prefix = f'openspec/changes/{cid}'
            folder = project.root / prefix
            ct, _ = frontmatter(snapshot.files[prefix + '/trace.md'])
            execution = ct.get('execution', {})
            if (issue_identity(ct) != oid or execution.get('schema_version') != 1
                    or execution.get('last_event') not in ('opsx.apply', 'opsx.accept', 'opsx.modify')):
                raise DirectProofError('direct_successor_completion_missing')
            started = datetime.fromisoformat(str(execution['started_at']))
            completed = datetime.fromisoformat(str(execution['completed_at']))
            if began is not None:
                # Governance documents use the project's explicit local timezone.
                local = ZoneInfo('Asia/Shanghai')
                start_utc = (started.replace(tzinfo=local) if started.tzinfo is None else started).astimezone(timezone.utc)
                end_utc = (completed.replace(tzinfo=local) if completed.tzinfo is None else completed).astimezone(timezone.utc)
                if end_utc < began or end_utc < start_utc or end_utc > datetime.now(timezone.utc):
                    raise DirectProofError('direct_successor_time_invalid')
            if completed < started:
                raise DirectProofError('direct_successor_completion_missing')
            tasks_path = prefix + '/tasks.md'
            old_tasks = baseline.get('files', {}).get(tasks_path)
            new_tasks = snapshot.files[tasks_path].decode()
            task_rows = lambda text: re.findall(r'^\s*- \[[ xX]\]\s+(.+)$', text, re.M)
            if not old_tasks:
                raise DirectProofError('direct_successor_tasks_changed')
            plan = read_plan(folder)
            state = readiness(project.root, cid, source_root=getattr(project, 'source_root', None))
            if state['status'] != 'ready' or plan.get('issue_id', oid) != oid:
                raise DirectProofError('direct_successor_evidence_invalid')
            from app.governance.workflow_receipt import valid
            if not valid(folder, cid, oid, state['run_id'], not_before=began):
                raise DirectProofError('direct_successor_completion_missing')
            if task_rows(old_tasks) != task_rows(new_tasks):
                from app.governance.successor_dependencies import verified_tasks
                task_proofs[cid] = verified_tasks(plan, snapshot.files, task_rows(old_tasks), task_rows(new_tasks), guard, cid)
            from app.governance.successor_dependencies import verified_rules
            dependencies.update(verified_rules(plan, snapshot.files, old, current, guard, began))
            runs[cid] = state['run_id']
            for check in plan['checks']:
                covered.update(x for x in check['inputs'] if x not in check.get('input_sections', {}))
            evidence = latest_manifest(folder)
            for row in evidence['checks']:
                for artifact in row.get('artifacts', []):
                    # artifacts_match has already checked these exact hashes.
                    if isinstance(artifact, dict) and isinstance(artifact.get('path'), str):
                        covered.add(artifact['path'])
            derived.update((prefix + '/trace.md', prefix + '/tasks.md'))
            # Newly appended historical reports are derived too. Their summaries
            # never establish current readiness, and existing history cannot change.
            for name in snapshot.files:
                if not name.startswith(prefix + '/evidence/acceptance/') or not name.endswith('/summary.md'):
                    continue
                relative = name.removeprefix(prefix + '/evidence/acceptance/').split('/')
                current_summary = (relative == [state['run_id'], 'summary.md'] or
                    (len(relative) == 3 and relative[0] == 'checkpoints'
                     and relative[1].startswith(state['run_id'] + '-checkpoint-')))
                if current_summary:
                    derived.add(name)
                elif name not in old['files']:
                    report_path = project.root / name.removesuffix('summary.md') / 'manifest.json'
                    if report_path.is_symlink() or not report_path.is_file():
                        continue
                    report = json.loads(report_path.read_text())
                    if (report.get('schema_version') == 1 and report.get('change_id') == cid
                            and report.get('run_id') == report_path.parent.name
                            and report.get('scope') in ('complete', 'diagnostic')
                            and report.get('status') in ('passed', 'failed', 'blocked')
                            and {r['id'] for r in report.get('checks', [])} <= {c['id'] for c in plan['checks']}):
                        derived.add(name)
        for delta in changes:
            if delta['path'].startswith('rules/') and delta['path'] not in dependencies:
                raise DirectProofError('direct_dependency_conflict')
            if delta['kind'] == 'deleted' or delta['path'] not in covered | derived:
                raise DirectProofError('direct_successor_input_uncovered')
        return current, {'schema_version': 1, 'kind': 'verified_successor',
                         'original_operation_id': guard['operation_id'],
                         'original_guard_version': guard['version'], 'acceptance_runs': runs,
                         'differences': changes, 'historical_attribution': 'partial',
                         'basis': 'startup_baseline' if independent else 'sync_manifest',
                         'baseline_revision': baseline.get('revision'), 'dependency_proofs': dependencies,
                         'task_proofs': task_proofs}
    except (KeyError, StopIteration, TypeError, ValueError, OSError) as error:
        if isinstance(error, DirectProofError):
            raise
        raise DirectProofError('direct_successor_evidence_invalid') from None
