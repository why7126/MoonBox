"""Pure completion checks over an immutable governance snapshot.

The caller separately proves terminal execution, sync evidence and a stable hash.
No model text or client-supplied success flags are accepted as evidence.
"""
import re
import yaml
from app.governance.candidates import frontmatter
from app.governance.snapshot import safe_load


def validate_result(files, object_id, action, *, external=False):
    try:
        return _validate(files, object_id, action, external=external)
    except (KeyError, ValueError, TypeError, AttributeError, yaml.YAMLError):
        return False


def _validate(files, oid, action, *, external=False):
    if action == 'sprint-archive':
        if not re.fullmatch(r'sprint-\d{3}', oid):
            return False
        base = f'iterations/archive/{oid}'
        if any(n.startswith(f'iterations/change/{oid}/') for n in files):
            return False
        plan = safe_load(files[base + '/sprint.yaml'])
        if plan.get('sprint_id') != oid or plan.get('status') not in ('closed', 'archived', 'completed'):
            return False
        from app.governance.sprint_object import scope_ids
        members = scope_ids(plan)
        if not any(members.values()):
            return False
        if not all(files.get(base + '/' + name, b'').strip() for name in ('sprint.md', 'acceptance-report.md', 'release-note.md')):
            return False
        report_text = files[base + '/acceptance-report.md'].decode('utf-8')
        from app.services.requirement_center import _sprint_report_signed_off
        if not _sprint_report_signed_off(report_text):
            return False
        for key in ('requirements', 'bugs'):
            for member in members[key]:
                if not _validate(files, member, 'opsx-archive', external=external):
                    return False
        return all(_change(files, cid, 'opsx-archive', historical=True) for cid in members['changes'])
    if oid.startswith(('REQ-', 'BUG-')):
        folder = 'requirements' if oid.startswith('REQ-') else 'bugs'
        entries = safe_load(files[f'issues/{folder}/_registry.yaml'])['entries']
        matches = [e for e in entries if e.get('id') == oid]
        if len(matches) != 1:
            return False
        entry = matches[0]
        base = entry['path'].rstrip('/')
        if not re.fullmatch(rf'issues/{folder}/(?:plan|review|archive)/{re.escape(oid)}', base):
            return False
        trace, _ = frontmatter(files[f'{base}/trace.md'])
        if trace.get('status') != entry.get('status'):
            return False
        document = 'requirement.md' if folder == 'requirements' else 'bug.md'
        primary, _ = frontmatter(files[f'{base}/{document}'])
        if primary.get('status') != trace.get('status') or not primary.get('title'):
            return False
        if action.endswith('-generate'):
            return trace.get('status') in (('draft', 'enriching') if external else ('draft',))
        if action.endswith('-complete'):
            required = (['business-flow.md', 'user-stories.md', 'acceptance.md'] if folder == 'requirements'
                        else ['root-cause.md', 'workaround.md', 'acceptance.md'])
            return trace.get('status') == 'pending_review' and all(files.get(f'{base}/{name}', b'').strip() for name in required)
        if action.endswith('-review'):
            return trace.get('status') in ('approved', 'rejected', 'deferred', 'wont_fix') and bool(files.get(f'{base}/review.md', b'').strip())
        sprint = trace.get('iteration')
        if not isinstance(sprint, str) or not re.fullmatch(r'sprint-\d{3}', sprint):
            return False
        plans = [safe_load(body) for name, body in files.items()
                 if name in (f'iterations/change/{sprint}/sprint.yaml', f'iterations/archive/{sprint}/sprint.yaml')]
        if len(plans) != 1 or oid not in plans[0].get('requirements' if folder == 'requirements' else 'bugs', []):
            return False
        if action == 'sprint-propose':
            return trace.get('status') == 'in_sprint'
        from app.governance.archive_admission import linked_changes
        links = linked_changes({}, trace)
        if not links or any(x not in plans[0].get('changes', []) for x in links):
            return False
        if action != 'opsx-archive' and not any(f'openspec/changes/{cid}/trace.md' in files for cid in links):
            return False
        return all(_change(files, cid, action, external=external, historical=True) for cid in links)
    return _change(files, oid, action, external=external)


def _change(files, cid, action, *, external=False, historical=False):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', cid):
        return False
    bases = [name[:-len('/trace.md')] for name in files
             if name == f'openspec/changes/{cid}/trace.md'
             or re.fullmatch(rf'openspec/archive/\d{{4}}-\d{{2}}-\d{{2}}-{re.escape(cid)}/trace.md', name)]
    if len(bases) != 1:
        return False
    base = bases[0]
    archived = base.startswith('openspec/archive/')
    trace_body = files[f'{base}/trace.md']
    if archived and (external or historical) and trace_body.strip() and not trace_body.startswith(b'---'):
        trace = {}  # pre-frontmatter archive; location remains the lifecycle fact
    else:
        trace, _ = frontmatter(trace_body)
    # Existing archive folders are authoritative in the shared lifecycle reader.
    # Historical Changes may predate mandatory design.md and execution metadata.
    required = ('proposal.md', 'tasks.md') if archived and (external or historical) else ('proposal.md', 'design.md', 'tasks.md')
    if not all(files.get(f'{base}/{name}', b'').strip() for name in required):
        return False
    if action == 'opsx-archive':
        return archived
    if archived and historical:
        return True
    if action in ('req-opsx', 'bug-opsx'):
        return not archived and trace.get('status') == 'proposed'
    if action in ('opsx-apply', 'opsx-modify'):
        tasks = files[f'{base}/tasks.md'].decode()
        return (trace.get('status') == 'applied' and bool(re.search(r'^\s*- \[[xX]\]', tasks, re.M))
                and not re.search(r'^\s*- \[ \]', tasks, re.M)
                and bool(trace.get('execution', {}).get('completed_at')))
    return False


def validate_external(files, object_id, stage):
    """Validate external governance facts without inventing a product Chat turn."""
    if object_id.startswith('sprint-'):
        if stage == 'done':
            return validate_result(files, object_id, 'sprint-archive', external=True)
        if stage != 'sprint-planning' or not re.fullmatch(r'sprint-\d{3}', object_id):
            return False
        try:
            base = f'iterations/change/{object_id}'
            if any(name.startswith(f'iterations/archive/{object_id}/') for name in files):
                return False
            plan = safe_load(files[base + '/sprint.yaml'])
            from app.governance.sprint_object import scope_ids
            scope_ids(plan)
            return plan.get('sprint_id') == object_id and plan.get('status') in ('planning', 'active', 'in_progress')
        except (KeyError, ValueError, TypeError, AttributeError, yaml.YAMLError):
            return False
    action = {
        'planning': 'req-generate' if object_id.startswith('REQ-') else 'bug-generate',
        'review-ready': 'req-complete' if object_id.startswith('REQ-') else 'bug-complete',
        'approved': 'req-review' if object_id.startswith('REQ-') else 'bug-review',
        'sprint-planning': 'sprint-propose',
        'ready-dev': 'req-opsx' if object_id.startswith('REQ-') else 'bug-opsx',
        'acceptance': 'opsx-apply',
        'done': 'opsx-archive',
    }.get(stage)
    if action:
        return validate_result(files, object_id, action, external=True)
    # Capture and in-progress development are not completion claims.
    if stage in ('capture', 'development'):
        return True
    return False
