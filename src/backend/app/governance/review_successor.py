"""Recognize verified later lifecycle facts without replaying a historical review."""
from sqlalchemy import select
from app.chat.schema import governance_applications as applications, governance_candidates as candidates
from app.governance import store
from app.governance.candidates import frontmatter
from app.governance.completion_proof import historical_result
from app.governance.execution_validation import validate_external
from app.governance.snapshot import safe_load
from app.governance.archive_admission import change_acceptance, linked_changes, issue_identity
from app.governance.acceptance_evidence import read_plan


def verify_successor(db, project, guard, stage, snapshot):
    if stage not in ('sprint-planning', 'ready-dev', 'acceptance'):
        return False
    if guard['terminal_status'] != 'completed' or (
            guard['state'] == 'validated' and guard['confirmed_stage'] == stage
            and guard['result_revision'] == snapshot.revision):
        return False
    try:
        app = db.execute(select(applications).join(candidates, candidates.c.id == applications.c.candidate_id).where(
            candidates.c.turn_id == guard['operation_id'],
            candidates.c.object_id == guard['object_id'],
            candidates.c.scope_key == project.key,
            applications.c.scope_key == project.key,
            applications.c.state == 'applied', applications.c.phase == 'verified')).mappings().first()
        if not app:
            return False
        oid = guard['object_id']
        old = historical_result(store.read(app['candidate_id'], 'baseline'),
                                store.read(app['candidate_id'], 'result'),
                                store.read(app['id'], 'operation').get('workflow_sync', {}),
                                oid, guard['action'])
        current = snapshot.files
        domain = 'requirements' if oid.startswith('REQ-') else 'bugs'
        def base(files):
            entries = safe_load(files[f'issues/{domain}/_registry.yaml'])['entries']
            matches = [e['path'] for e in entries if e.get('id') == oid]
            if len(matches) != 1:
                raise ValueError('ambiguous')
            return matches[0].rstrip('/')
        before, after = base(old), base(current)
        # A changed review decision or governance rules is never just progression.
        review_changed = old.get(before + '/review.md') != current.get(after + '/review.md')
        if review_changed and stage != 'acceptance':
            return False
        if {k:v for k,v in old.items() if k.startswith('rules/')} != {k:v for k,v in current.items() if k.startswith('rules/')}:
            return False
        if not validate_external(current, oid, stage):
            return False
        trace, _ = frontmatter(current[after + '/trace.md'])
        if stage == 'acceptance':
            links = linked_changes({}, trace)
            if not links or not all(change_acceptance(project.root, cid, source_root=getattr(project, "source_root", None))['ready'] for cid in links):
                return False
            covered = set()
            for cid in links:
                folder = project.root / 'openspec/changes' / cid
                if (folder / 'acceptance-plan.json').is_file():
                    for check in read_plan(folder)['checks']:
                        covered.update(p for p in check['inputs'] if p not in check.get('input_sections', {}))
            if review_changed:
                # A later approved review is admissible only when the complete
                # current file participates in current verified delivery evidence.
                previous_review, _ = frontmatter(old[before + '/review.md'])
                current_review, _ = frontmatter(current[after + '/review.md'])
                if (after + '/review.md' not in covered
                        or previous_review.get('result') != 'approved'
                        or current_review.get('result') != 'approved'
                        or issue_identity(previous_review) != oid
                        or issue_identity(current_review) != oid):
                    return False
            if any(path.startswith(before + '/') and after + path[len(before):] not in current for path in old):
                return False
            for path, body in current.items():
                if not path.startswith(after + '/'):
                    continue
                name = path[len(after) + 1:]
                if name in ('trace.md', 'acceptance.md', 'capture.md', 'review.md'):
                    continue
                previous = old.get(before + '/' + name)
                if previous == body:
                    continue
                # Status/timestamps alone do not alter scope. Changed substantive
                # content must be covered by current, fingerprint-checked evidence.
                try:
                    om, ob = frontmatter(previous)
                    nm, nb = frontmatter(body)
                    ignored = {'status', 'updated_at', 'iteration', 'lifecycle_stage'}
                    unchanged = ob == nb and {k:v for k,v in om.items() if k not in ignored} == {k:v for k,v in nm.items() if k not in ignored}
                except (ValueError, AttributeError, TypeError):
                    unchanged = False
                if not unchanged and path not in covered:
                    return False
        else:
            # Planning may only advance bookkeeping; substantive scope edits need
            # newly verified delivery evidence, not a timestamp/status exemption.
            primary = '/requirement.md' if oid.startswith('REQ-') else '/bug.md'
            for path, body in old.items():
                if path.startswith(before + '/') and path not in {before + '/trace.md', before + '/acceptance.md', before + primary}:
                    if current.get(after + path[len(before):]) != body:
                        return False
            old_meta, old_body = frontmatter(old[before + primary])
            new_meta, new_body = frontmatter(current[after + primary])
            ignored = {'status', 'updated_at', 'iteration', 'lifecycle_stage'}
            if old_body != new_body or {k:v for k,v in old_meta.items() if k not in ignored} != {k:v for k,v in new_meta.items() if k not in ignored}:
                return False
        return True
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return False
