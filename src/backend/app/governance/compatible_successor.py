"""Versioned, read-only compatible-append proofs; never trust a title alone.

Certificates are separate from immutable archive journals. A reviewed statement
and passing regression artifact are content-bound, as are both delta bodies and
all successor acceptance artifacts. Reading never runs repository commands.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

MAX_BYTES = 256 * 1024


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def scenarios(body: str) -> tuple[str, dict[str, str]]:
    parts = re.split(r'#### Scenario: ', body)
    requirement = parts[0].strip()
    if not requirement or 'SHALL' not in requirement or '###' in requirement:
        raise ValueError('unsupported requirement')
    result = {}
    for part in parts[1:]:
        match = re.fullmatch(r'(.+?) - \*\*WHEN\*\* (.+?) - \*\*THEN\*\* (.+)', part.strip())
        if not match or '###' in part:
            raise ValueError('unsupported scenario')
        title = match[1].strip()
        if title in result:
            raise ValueError('duplicate scenario')
        result[title] = part.strip()
    if not result:
        raise ValueError('missing scenarios')
    return requirement, result


def append_only(before: str, after: str) -> list[str]:
    old_head, old = scenarios(before)
    new_head, new = scenarios(after)
    if old_head != new_head or any(new.get(key) != value for key, value in old.items()):
        raise ValueError('protected requirement changed')
    additions = sorted(new.keys() - old.keys())
    if not additions:
        raise ValueError('no additive scenarios')
    return additions


def proof_path(root: Path, successor: str, key: tuple[str, str]) -> Path:
    from .archive_recovery import IDENTITY
    if not IDENTITY.fullmatch(successor):
        raise ValueError('invalid successor')
    return root / 'openspec/archive/.compatible-successors' / successor / (digest('\0'.join(key)) + '.json')


def evidence_file(root: Path, item: dict) -> bytes:
    """Relative, symlink-free, hash-bound proof assets only."""
    rel = item['path']
    if not isinstance(rel, str) or '\\' in rel or Path(rel).is_absolute() or '..' in Path(rel).parts:
        raise ValueError('unsafe evidence path')
    original = root / rel
    if any(p.is_symlink() for p in [original, *original.parents] if p != root.parent):
        raise ValueError('unsafe evidence path')
    from .acceptance_evidence import artifact_path
    path = artifact_path(root, rel)
    if not rel.startswith('openspec/') or any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
        raise ValueError('unsafe evidence path')
    if path.stat().st_size > MAX_BYTES:
        raise ValueError('oversized evidence')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != item['sha256']:
        raise ValueError('evidence changed')
    return raw


def acceptance_binding(root: Path, folder: Path, *, source_root: Path | None = None) -> str:
    """Evidence-only validation: deliberately no recursive recovery admission."""
    from .acceptance_evidence import read_plan, latest_manifest, artifacts_match, readiness
    from .archive_recovery import tree_hash
    before = tree_hash(folder)
    plan = read_plan(folder)
    if folder.parent == root / 'openspec/changes' and readiness(root, folder.name, source_root=source_root)['status'] != 'ready':
        raise ValueError('candidate acceptance stale')
    manifest = latest_manifest(folder)
    if not manifest or manifest.get('status') != 'passed':
        raise ValueError('successor acceptance not passed')
    checks = {row['id']: row for row in plan['checks']}
    rows = manifest.get('checks', [])
    if len(rows) != len(checks) or {row['id'] for row in rows} != set(checks):
        raise ValueError('successor acceptance incomplete')
    for row in rows:
        if (row.get('status') != 'passed'
                or {a['path'] for a in row.get('artifacts', [])} != set(checks[row['id']].get('artifacts', []))
                or not artifacts_match(root, row, archive_dir=folder)):
            raise ValueError('successor evidence invalid')
    if before != tree_hash(folder):
        raise ValueError('successor changed')
    return digest(json.dumps(manifest, sort_keys=True, ensure_ascii=False))


def verify_append(root: Path, successor: str, folder: Path, key: tuple[str, str], before: str, after: str, *, source_root: Path | None = None) -> dict:
    additions = append_only(before, after)
    path = proof_path(root, successor, key)
    if any(p.is_symlink() for p in (path, path.parent, path.parent.parent)) or path.stat().st_size > MAX_BYTES:
        raise ValueError('unsafe compatibility proof')
    raw = path.read_bytes()
    record = json.loads(raw)
    expected = {'schema_version': 1, 'successor': successor, 'capability': key[0],
                'requirement': key[1], 'before_sha256': digest(before), 'after_sha256': digest(after),
                'added_scenarios': additions, 'classification': 'compatible_append'}
    if any(record.get(k) != v for k, v in expected.items()):
        raise ValueError('compatibility proof identity mismatch')
    from .archive_recovery import tree_hash
    if record.get('delta_sha256') != tree_hash(folder / 'specs'):
        raise ValueError('compatibility delta changed')
    if record.get('acceptance_sha256') != acceptance_binding(root, folder, source_root=source_root):
        raise ValueError('compatibility acceptance changed')
    review = json.loads(evidence_file(root, record['review']))
    regression = json.loads(evidence_file(root, record['regression']))
    for evidence in (review, regression):
        if any(evidence.get(k) != v for k, v in expected.items()) or evidence.get('status') != 'passed':
            raise ValueError('compatibility evidence identity mismatch')
    if not review.get('reviewer') or not review.get('rationale') or review.get('contradictions') != []:
        raise ValueError('compatibility review incomplete')
    required = {'original_contract', 'added_scenarios', 'destructive_changes', 'broken_chain', 'concurrent_change'}
    if not required <= set(regression.get('checks', [])):
        raise ValueError('compatibility regression incomplete')
    if path.read_bytes() != raw:
        raise ValueError('compatibility proof changed')
    dependencies = [record['review'], record['regression']]
    for item in dependencies:
        evidence_file(root, item)
    return {'proof_sha256': hashlib.sha256(raw).hexdigest(), 'proof_path': path.relative_to(root).as_posix(),
            'dependencies': dependencies}


def verify(root: Path, successor: str, folder: Path, key: tuple[str, str], before: str, after: str, *, source_root: Path | None = None) -> dict:
    try:
        append_only(before, after)
    except ValueError:
        from .rule_change import supported, verify as verify_rule_change
        if supported(before, after):
            return verify_rule_change(root, successor, folder, key, before, after, source_root=source_root)
        from .controlled_successor import verify as verify_replacement
        return verify_replacement(root, successor, folder, key, before, after, source_root=source_root)
    # An invalid append certificate cannot fall back to a replacement waiver.
    return verify_append(root, successor, folder, key, before, after, source_root=source_root)


def recheck(root: Path, certificate: dict) -> None:
    if certificate.get('rule_change'):
        from .rule_change import recheck as recheck_rule_change
        recheck_rule_change(certificate)
        if not certificate.get('virtual'):
            evidence_file(root, {'path': certificate['proof_path'], 'sha256': certificate['proof_sha256']})
        return
    if certificate.get('virtual'):
        if not certificate.get('controlled') or (root/certificate['proof_path']).exists():
            raise ValueError('replacement_proof_changed')
    else:
        evidence_file(root, {'path': certificate['proof_path'], 'sha256': certificate['proof_sha256']})
    for item in certificate.get('dependencies', []):
        evidence_file(root, item)
    if certificate.get('controlled'):
        from .controlled_successor import recheck_authority
        recheck_authority(certificate['controlled'])
    if certificate.get('bootstrap'):
        from .controlled_successor import recheck_bootstrap
        recheck_bootstrap(certificate['bootstrap'])


def preflight(root: Path, successor: str, *, source_root: Path | None = None) -> list[dict]:
    """Legacy read-only entry; current candidates use normal acceptance, not a second proof."""
    from .archive_recovery import delta_operations, archive_paths, completed_archive
    folder = root / 'openspec/changes' / successor
    if not folder.is_dir():
        return []
    archives = [p for p in (root / 'openspec/archive').glob('????-??-??-*')
                if p.is_dir() and completed_archive(p, p.name[11:])]
    if not archives:
        return []
    operations = delta_operations(folder)
    from .archive_recovery import tree_hash
    def inputs():
        relevant = []
        for candidate in (root / 'openspec/archive').glob('????-??-??-*'):
            if any((candidate / 'specs' / cap).exists() for cap, _ in operations):
                relevant.append((candidate.name, tree_hash(candidate / 'specs'),
                                 (candidate / 'trace.md').read_bytes() if (candidate / 'trace.md').exists() else None))
        return (tree_hash(root / 'openspec/specs'), tree_hash(folder), tuple(sorted(relevant)),
                tree_hash(root / 'openspec/archive/.compatible-successors'),
                tree_hash(root / 'openspec/archive/.controlled-successors'),
                tree_hash(root / 'openspec/archive/.rule-confirmations'))
    initial = inputs()
    affected = {}
    for archive in archives:
        cid = archive.name[11:]
        if not archive.is_dir() or not completed_archive(archive, cid):
            continue
        if not any((archive / 'specs' / cap).exists() for cap, _ in operations):
            continue
        if len(archive_paths(root, cid)) != 1:
            raise ValueError('ambiguous protected archive')
        for key in delta_operations(archive).keys() & operations.keys():
            affected.setdefault(key, []).append(cid)
    failures = []
    if affected:
        try:
            acceptance_binding(root, folder, source_root=source_root)
        except (OSError, ValueError, KeyError, TypeError):
            for key, owners in sorted(affected.items()):
                failures.append({'change_id': successor, 'capability': key[0], 'requirement': key[1],
                                 'protected_changes': sorted(owners), 'reason': '当前对象的正常验收或证据未就绪'})
    if inputs() != initial:
        raise ValueError('candidate protection inputs changed')
    return failures
