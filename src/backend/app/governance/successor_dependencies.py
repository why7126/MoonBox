"""Explicit, receipt-bound rule transition proof; never a directory exemption."""
import re
import hashlib
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app.governance.candidates import frontmatter


def verified_tasks(plan, files, before, after, guard, change):
    from app.governance.direct_completion import encoded, DirectProofError
    try:
        proofs = plan.get('successor_task_proofs', [])
        if not isinstance(proofs, list) or len(proofs) != 1:
            raise ValueError('declaration')
        proof = proofs[0]
        identities = lambda rows: [row.split()[0] for row in rows]
        if (not before or len(before) != len(after) or identities(before) != identities(after)
                or len(set(identities(before))) != len(before)
                or proof.get('schema_version') != 1 or proof['change_id'] != change
                or proof['operation_id'] != guard['operation_id']
                or proof['baseline_revision'] != guard['baseline_revision']
                or proof['before_sha256'] != hashlib.sha256(encoded(before)).hexdigest()
                or proof['after_sha256'] != hashlib.sha256(encoded(after)).hexdigest()):
            raise ValueError('binding')
        prefix = f'openspec/changes/{change}/'
        required = {prefix + name + '.md' for name in ('tasks', 'design', 'proposal')}
        required.update(name for name in files if name.startswith(prefix + 'specs/') and name.endswith('/spec.md'))
        ids = proof['check_ids']
        if not isinstance(ids, list) or not ids or len(ids) != len(set(ids)):
            raise ValueError('checks')
        checks = [check for check in plan['checks'] if check['id'] in ids]
        covered = {name for check in checks for name in check['inputs'] if name not in check.get('input_sections', {})}
        if len(checks) != len(ids) or not required <= covered or not required <= files.keys():
            raise ValueError('coverage')
        return dict(proof)
    except (KeyError, TypeError, ValueError, AttributeError, IndexError):
        raise DirectProofError('direct_successor_tasks_changed') from None


def verified_rules(plan, files, old, current, guard, began):
    from app.governance.direct_completion import DirectProofError
    result = {}
    try:
        declarations = plan.get('successor_dependency_proofs', [])
        if not isinstance(declarations, list) or len(declarations) > 20:
            raise ValueError('declarations')
        for proof in declarations:
            path, cid = proof['path'], proof['source_change']
            if (proof.get('schema_version') != 1 or began is None
                    or not isinstance(path, str) or not re.fullmatch(r'rules/[a-z0-9][a-z0-9_-]*\.md', path)
                    or not isinstance(cid, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', cid)
                    or path in result or path not in old['files'] or path not in current['files']
                    or old['files'][path] == current['files'][path]
                    or proof['operation_id'] != guard['operation_id']
                    or proof['baseline_revision'] != guard['baseline_revision']
                    or proof['before_sha256'] != old['files'][path]
                    or proof['after_sha256'] != current['files'][path]):
                raise ValueError('binding')
            prefixes = [name[:-len('/trace.md')] for name in files if re.fullmatch(
                rf'openspec/archive/\d{{4}}-\d{{2}}-\d{{2}}-{re.escape(cid)}/trace.md', name)]
            if len(prefixes) != 1 or any(name.startswith(f'openspec/changes/{cid}/') for name in files):
                raise ValueError('source_identity')
            prefix = prefixes[0]
            required = {path, *(prefix + '/' + name + '.md' for name in ('proposal', 'design', 'tasks', 'trace'))}
            check_ids = proof['check_ids']
            if not isinstance(check_ids, list) or not check_ids or len(set(check_ids)) != len(check_ids):
                raise ValueError('checks')
            checks = [check for check in plan['checks'] if check['id'] in check_ids]
            covered = {name for check in checks for name in check['inputs'] if name not in check.get('input_sections', {})}
            if len(checks) != len(check_ids) or not required <= covered or not required <= files.keys():
                raise ValueError('coverage')
            trace, _ = frontmatter(files[prefix + '/trace.md'])
            execution = trace['execution']
            def utc(value):
                time = datetime.fromisoformat(str(value))
                return (time.replace(tzinfo=ZoneInfo('Asia/Shanghai')) if time.tzinfo is None else time).astimezone(timezone.utc)
            start, end = utc(execution['started_at']), utc(execution['completed_at'])
            if (trace.get('change_id') != cid or trace.get('status') not in ('applied', 'archived')
                    or execution.get('schema_version') != 1
                    or execution.get('last_event') not in ('opsx.apply', 'opsx.accept', 'opsx.archive')
                    or not began <= end <= datetime.now(timezone.utc) or start > end):
                raise ValueError('completion')
            tasks = re.findall(r'^\s*- \[([ xX])\]\s+\S.*$', files[prefix + '/tasks.md'].decode(), re.M)
            if not tasks or any(value == ' ' for value in tasks):
                raise ValueError('tasks')
            result[path] = dict(proof)
        return result
    except (KeyError, TypeError, ValueError, AttributeError):
        raise DirectProofError('direct_successor_dependency_invalid') from None
