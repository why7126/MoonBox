"""Server-side, read-only archive reconciliation; never replay archive commands."""
import re
import os
from pathlib import Path
import subprocess
import sys

from app.governance import store
from app.governance.candidates import frontmatter
from app.governance.direct_command_journal import record_id, record_block_reason
from app.governance.execution_validation import validate_result
from app.governance.snapshot import digest, read_once, safe_load
from app.governance.writer import project_lock


class ArchiveProofError(ValueError):
    """Only bounded reason codes leave this verifier."""


def _require(condition, reason):
    if not condition:
        raise ArchiveProofError(reason)


def _requirements(body):
    result = {}
    for match in re.finditer(r'^### Requirement: ([^\n]+)\n[\s\S]*?(?=^### Requirement: |\Z)', body, re.M):
        title = match.group(1).strip()
        _require(title not in result, 'archive_duplicate_requirement')
        lines, fence = [], None
        for line in match.group(0).strip().splitlines():
            marker = re.match(r'^\s*(`{3,}|~{3,})', line)
            if marker:
                token = marker.group(1)
                if fence is None:
                    fence = token
                elif token[0] == fence[0] and len(token) >= len(fence):
                    fence = None
            # OpenSpec collapses repeated blank separators, not fenced examples.
            if fence is None and not line and lines and not lines[-1]:
                continue
            lines.append(line)
        result[title] = '\n'.join(lines)
    return result


def _archive(files, oid):
    if oid.startswith(('BUG-', 'REQ-')):
        folder = 'bugs' if oid.startswith('BUG-') else 'requirements'
        entries = safe_load(files[f'issues/{folder}/_registry.yaml'])['entries']
        matches = [e for e in entries if e.get('id') == oid]
        _require(len(matches) == 1, 'archive_identity_invalid')
        base = matches[0]['path'].rstrip('/')
        _require(base == f'issues/{folder}/archive/{oid}', 'archive_issue_not_promoted')
        trace, _ = frontmatter(files[f'{base}/trace.md'])
        _require(trace.get('status') == 'done', 'archive_issue_not_done')
        from app.governance.archive_admission import linked_changes
        links = linked_changes(matches[0], trace)
        _require(len(links) == 1, 'archive_change_ambiguous')
        cid = links[0]
    else:
        cid = oid
    _require(isinstance(cid, str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', cid), 'archive_identity_invalid')
    bases = [n[:-len('/trace.md')] for n in files if re.fullmatch(
        rf'openspec/archive/\d{{4}}-\d{{2}}-\d{{2}}-{re.escape(cid)}/trace.md', n)]
    _require(len(bases) == 1 and not any(n.startswith(f'openspec/changes/{cid}/') for n in files),
             'archive_location_invalid')
    return cid, bases[0]


def validate_merge(before, current, cid, archived):
    """Compare immutable pre-run deltas and all affected requirement bodies."""
    prefix = f'openspec/changes/{cid}/'
    _require(prefix + 'trace.md' in before, 'archive_baseline_missing')
    deltas = [n for n in before if n.startswith(prefix + 'specs/') and n.endswith('/spec.md')]
    for name in deltas:
        relative = name[len(prefix):]
        delta = before[name]
        _require(current.get(archived + '/' + relative) == delta, 'archive_delta_changed')
        cap = relative[len('specs/'):]
        actual = _requirements(current.get('openspec/specs/' + cap, b'').decode())
        original = _requirements(before.get('openspec/specs/' + cap, b'').decode())
        expected = dict(original)
        sections = re.split(r'^## (ADDED|MODIFIED|REMOVED|RENAMED) Requirements\s*$', delta.decode(), flags=re.M)
        _require(len(sections) > 1, 'archive_delta_invalid')
        for index in range(1, len(sections), 2):
            operation, body = sections[index:index + 2]
            _require(operation != 'RENAMED', 'archive_rename_requires_review')
            for title, requirement in _requirements(body).items():
                if operation == 'ADDED':
                    _require(title not in expected, 'archive_delta_invalid')
                    expected[title] = requirement
                elif operation == 'MODIFIED':
                    _require(title in expected, 'archive_delta_invalid')
                    expected[title] = requirement
                else:
                    _require(title in expected, 'archive_delta_invalid')
                    expected.pop(title)
        _require(actual == expected, 'archive_spec_merge_mismatch')
    # These artifacts define the approved change; later edits cannot be silently accepted.
    for name in ('proposal.md', 'design.md', 'tasks.md'):
        _require(before.get(prefix + name) == current.get(archived + '/' + name)
                 and bool(before.get(prefix + name)), 'archive_artifact_changed')


def _verify(project, guard, turn, operation, snapshot):
    """Return a proof only after independent current-source verification."""
    _require(guard['action'] == 'opsx-archive' and turn['status'] == 'completed', 'archive_terminal_invalid')
    _require(guard['operation_id'] == turn['id'] and guard['conversation_id'] == turn['conversation_id'],
             'archive_execution_mismatch')
    _require(guard['scope_key'] == project.key, 'archive_scope_mismatch')
    rid = record_id(turn['conversation_id'], turn['client_request_id'])
    _require(record_block_reason(turn['conversation_id'], turn['client_request_id'], action='opsx-archive',
                                object_id=guard['object_id'], revision=guard['baseline_revision']) is None,
             'archive_record_invalid')
    _require(operation.get('phase') == 'terminal' and operation.get('terminal_status') == 'completed',
             'archive_terminal_invalid')
    baseline = store.read(rid, 'baseline')
    _require(baseline.get('binding_revision') == project.binding_revision, 'archive_binding_changed')
    before = {n: b.encode() for n, b in baseline['files'].items()}
    _require(digest(before) == guard['baseline_revision'], 'archive_baseline_invalid')
    cid, archived = _archive(snapshot.files, guard['object_id'])
    validate_merge(before, snapshot.files, cid, archived)
    _require(validate_result(snapshot.files, guard['object_id'], 'opsx-archive'), 'archive_business_invalid')
    source = project.source_root or project.root
    script = source / 'scripts' / 'sync-workflow-status.py'
    with project_lock(project):
        _require(read_once(project.root) == snapshot.files and read_once(source) == snapshot.files,
                 'archive_source_changed')
        _require(script.is_file() and not script.is_symlink(), 'archive_checker_unavailable')
        try:
            result = subprocess.run([sys.executable, '-m', 'app.governance.archive_workflow_check', str(source), cid], cwd=source, capture_output=True, timeout=120,
                                     env={**os.environ, 'PYTHONPATH': str(Path(__file__).resolve().parents[2])})
        except (OSError, subprocess.TimeoutExpired):
            raise ArchiveProofError('archive_sync_check_failed') from None
        _require(result.returncode == 0, 'archive_sync_check_failed')
        _require(read_once(project.root) == snapshot.files and read_once(source) == snapshot.files,
                 'archive_source_changed')
    proof = dict(schema_version=1, scope_key=project.key, object_id=guard['object_id'], change_id=cid,
                 operation_id=turn['id'], action='opsx-archive', source_hash=snapshot.revision,
                 baseline_revision=guard['baseline_revision'], verification_source='archive_source_revalidation')
    # Preserve every original observation. This is a new server verification, not a forged tool step.
    operation = dict(operation, archive_verification=proof)
    store.write(rid, 'operation', operation)
    return proof


def verify(project, guard, turn, operation, snapshot):
    try:
        return _verify(project, guard, turn, operation, snapshot)
    except ArchiveProofError:
        raise
    except (KeyError, TypeError, AttributeError, UnicodeError):
        raise ArchiveProofError('archive_record_invalid') from None
