"""Verify immutable review evidence separately from current admission dependencies."""
import json
from app.governance.snapshot import digest, safe_load
from app.governance.execution_validation import validate_result
from app.governance.candidates import frontmatter


class ProofError(ValueError):
    pass


def reconstruct(baseline, result):
    if not isinstance(baseline, dict) or not isinstance(result, dict):
        raise ProofError('proof_invalid')
    if baseline.get('workspace_mode') != 'source':
        raise ProofError('unsupported_proof')
    try:
        files = {name: body.encode() for name, body in baseline['files'].items()}
        for name, body in result['after'].items():
            if body is None:
                files.pop(name, None)
            else:
                files[name] = body.encode()
        return files
    except (KeyError, TypeError, AttributeError):
        raise ProofError('proof_invalid') from None


def dependencies(files, oid, changed=()):
    """Review validator reads the object registry entry and its complete document set.

    Rules and every file written by the operation remain dependencies. Other
    registry entries and unrelated docs are not completion inputs.
    """
    folder = 'requirements' if oid.startswith('REQ-') else 'bugs'
    registry = f'issues/{folder}/_registry.yaml'
    try:
        entries = [e for e in safe_load(files[registry])['entries'] if e.get('id') == oid]
        if len(entries) != 1:
            raise ProofError('dependency_unknown')
        base = entries[0]['path'].rstrip('/')
        if not base.startswith(f'issues/{folder}/') or base.split('/')[-1] != oid:
            raise ProofError('dependency_unknown')
        selected = {name: body for name, body in files.items()
                    if name.startswith(base + '/') or name.startswith('rules/') or name in changed}
        selected[registry] = json.dumps(entries, sort_keys=True, default=str).encode()
        changelog = f'issues/{folder}/CHANGELOG.md'
        if changelog in selected:
            lines = [line for line in selected[changelog].splitlines() if oid.encode() in line]
            if not lines:
                raise ProofError('dependency_unknown')
            selected[changelog] = b'\n'.join(lines)
        trace, _ = frontmatter(files[f'{base}/trace.md'])
        parent = trace.get('related_requirement')
        if parent and parent != oid:
            parent_registry = 'issues/requirements/_registry.yaml'
            matches = [entry for entry in safe_load(files[parent_registry])['entries'] if entry.get('id') == parent]
            if len(matches) != 1:
                raise ProofError('dependency_unknown')
            parent_base = matches[0]['path'].rstrip('/')
            if not parent_base.startswith('issues/requirements/') or parent_base.split('/')[-1] != parent:
                raise ProofError('dependency_unknown')
            selected[parent_registry + '#' + parent] = json.dumps(matches, sort_keys=True, default=str).encode()
            for name in ('trace.md', 'requirement.md'):
                selected[parent_base + '/' + name] = files[parent_base + '/' + name]
        return selected
    except (KeyError, TypeError, AttributeError):
        raise ProofError('dependency_unknown') from None


def historical_result(baseline, result, proof, oid, action):
    if action not in ('req-review', 'bug-review'):
        raise ProofError('unsupported_proof')
    historical = reconstruct(baseline, result)
    if not isinstance(proof, dict):
        raise ProofError('proof_invalid')
    if (proof.get('object_id') != oid or proof.get('event') != action.replace('-', '.')
            or proof.get('source_hash') != digest(historical)
            or not validate_result(historical, oid, action)):
        raise ProofError('proof_invalid')
    return historical


def verify(baseline, result, proof, current, oid, action):
    historical = historical_result(baseline, result, proof, oid, action)
    # Retain every operation write as a dependency, including deletions.
    changed = set(result['after'])
    registry = 'issues/requirements/_registry.yaml' if oid.startswith('REQ-') else 'issues/bugs/_registry.yaml'
    changed.discard(registry)
    if dependencies(historical, oid, changed) != dependencies(current, oid, changed):
        raise ProofError('dependency_conflict')
    if not validate_result(current, oid, action):
        raise ProofError('dependency_conflict')
    return True


def differences(baseline, result, proof, current, oid, action):
    """Bounded semantic categories only; never expose source bodies or private paths."""
    historical = historical_result(baseline, result, proof, oid, action)
    changed = set(result['after'])
    before = dependencies(historical, oid, changed)
    after = dependencies(current, oid, changed)
    counts = {}
    for name in sorted(set(before) | set(after)):
        if before.get(name) == after.get(name):
            continue
        category = ('治理规范' if name.startswith('rules/') else
                    '对象索引' if '_registry.yaml' in name or name.endswith('CHANGELOG.md') else
                    '对象成果' if '/' + oid + '/' in name else '关联依赖')
        change = '新增' if name not in before else '删除' if name not in after else '修改'
        counts[(category, change)] = counts.get((category, change), 0) + 1
    return [f'{category}：{change} {count} 项' for (category, change), count in sorted(counts.items())]
