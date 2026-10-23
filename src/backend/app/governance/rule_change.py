"""Narrow rule extension checked from exact content and acceptance evidence.

The two approved text hashes describe the narrow BUG-0063-shaped rule edit,
not an object-ID allowlist. Future edit kinds require reviewed code and tests.
Legacy signed proofs are verified by controlled_successor, never rewritten here.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
from pathlib import Path
from sqlalchemy import select, text
from .archive_recovery import archive_paths, completed_archive, delta_operations, requirement_blocks, tree_hash
from .compatible_successor import scenarios
from .replacement_proof import canonical, digest
from .rule_change_schema import confirmations

SUPPORTED = frozenset({(
    '0f6a2949f9be25c8c0a10356668193e3f7528566b77908fe1e6935bf2f5fb544',
    '13349404a22a8ca1bd656a5c5d6443c27aeb5fffc7464c05ec46b851bb38b0b0',
)})
MAX_PROOF_BYTES = 64 * 1024


def supported(before: str, after: str) -> bool:
    try:
        old_head, old_scenarios = scenarios(before)
        new_head, new_scenarios = scenarios(after)
    except ValueError:
        return False
    # The reviewed first sample narrows two existing rejection scenarios to
    # "unproved/destructive" edits, so their text legitimately changes.
    # Exact before/after hashes below bind that one semantic exception.
    if not old_head or not new_head or not set(old_scenarios) <= set(new_scenarios):
        return False
    return (hashlib.sha256(before.encode()).hexdigest(),
            hashlib.sha256(after.encode()).hexdigest()) in SUPPORTED


def history_hash(root: Path) -> str:
    archive = root/'openspec/archive'
    rows = []
    for folder in sorted(archive.glob('????-??-??-*')):
        if folder.is_symlink() or not folder.is_dir():
            raise ValueError('unsafe_archive_history')
        rows.append((folder.name, tree_hash(folder)))
    return digest(rows)


def conflicts(project, change: str) -> list[dict]:
    root = project.root
    folder = root/'openspec/changes'/change
    if not folder.is_dir() or folder.is_symlink() or archive_paths(root, change):
        raise ValueError('rule_change_candidate_missing_or_ambiguous')
    matches = []
    for key, (operation, after) in delta_operations(folder).items():
        cap, title = key
        source = root/'openspec/specs'/cap/'spec.md'
        if not source.is_file() or source.is_symlink():
            continue
        before = requirement_blocks(source.read_text()).get(title)
        if before is None:
            continue
        owners = []
        for archived in (root/'openspec/archive').glob('????-??-??-*'):
            if archived.is_symlink() or not archived.is_dir():
                raise ValueError('unsafe_archive_history')
            if not (archived/'specs'/cap).exists():
                continue
            if key in delta_operations(archived):
                cid = archived.name[11:]
                if not completed_archive(archived, cid) or len(archive_paths(root, cid)) != 1:
                    raise ValueError('incomplete_archive_history')
                owners.append(cid)
        if owners:
            matches.append({'key': key, 'operation': operation, 'before': before,
                            'after': after, 'protected_changes': sorted(owners)})
    return matches


def candidate(project, change: str) -> dict:
    root = project.root
    folder = root/'openspec/changes'/change
    matches = conflicts(project, change)
    if len(matches) != 1:
        raise ValueError('rule_change_scope_unsupported')
    match = matches[0]
    if not match['supported']:
        raise ValueError('rule_change_not_supported')
    (cap, title) = match['key']
    before, after, owners = match['before'], match['after'], match['protected_changes']
    plan = folder/'acceptance-plan.json'
    if not plan.is_file() or plan.is_symlink() or plan.stat().st_size > MAX_PROOF_BYTES:
        raise ValueError('rule_change_acceptance_plan_missing')
    plan_bytes = plan.read_bytes()
    plan_data = json.loads(plan_bytes)
    if not isinstance(plan_data, dict):
        raise ValueError('rule_change_acceptance_plan_invalid')
    issue_id = plan_data.get('issue_id')
    issue_digest = None
    if isinstance(issue_id, str) and re.fullmatch(r'(?:REQ|BUG)-[0-9]{4}-[a-z0-9-]+', issue_id):
        domain = 'requirements' if issue_id.startswith('REQ-') else 'bugs'
        docs = [root/'issues'/domain/stage/issue_id/'acceptance.md'
                for stage in ('plan', 'review', 'archive')]
        docs = [path for path in docs if path.exists()]
        if len(docs) != 1 or docs[0].is_symlink() or docs[0].stat().st_size > MAX_PROOF_BYTES:
            raise ValueError('rule_change_issue_acceptance_missing')
        issue_digest = hashlib.sha256(docs[0].read_bytes()).hexdigest()
    content = {
        'schema_version': 2, 'project_id': project.key,
        'binding_revision': project.binding_revision, 'change_id': change,
        'capability': cap, 'requirement': title, 'before': before, 'after': after,
        'protected_changes': owners, 'delta_sha256': tree_hash(folder/'specs'),
        'acceptance_plan_sha256': hashlib.sha256(plan_bytes).hexdigest(),
        'acceptance_evidence_sha256': tree_hash(folder/'evidence/acceptance'),
        'issue_acceptance_sha256': issue_digest,
        'history_sha256': history_hash(root),
    }
    return content


def proof_path(root: Path, change: str, key: tuple[str, str]) -> Path:
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,100}', change):
        raise ValueError('invalid_rule_change_id')
    filename = hashlib.sha256('\0'.join(key).encode()).hexdigest()+'.json'
    return root/'openspec/archive/.rule-confirmations'/change/filename


def _row(db, project, change: str, content: dict, *, current_owner: bool = False):
    row = db.execute(select(confirmations).where(
        confirmations.c.scope_key == project.key,
        confirmations.c.change_id == change,
        confirmations.c.content_digest == digest(content),
        confirmations.c.state == 'confirmed')).mappings().first()
    if row and current_owner:
        owner = db.scalar(text('SELECT owner_id FROM admin_spaces WHERE id=:space'),
                          {'space': row['space_id']})
        if owner != row['actor_id']:
            return None
    return row


def verify(root: Path, successor: str, folder: Path, key: tuple[str, str],
           before: str, after: str, *, source_root=None) -> dict:
    from .controlled_successor import _authority
    context = _authority.get()
    if context is None:
        raise ValueError('rule_change_authority_unavailable')
    db, project, _actor, _operation_id, _fence = context
    if root != project.root or not supported(before, after):
        raise ValueError('rule_change_unsupported')
    archived = folder.parent.name == 'archive'
    if archived:
        path = proof_path(root, successor, key)
        if (path.is_symlink() or path.parent.is_symlink() or path.parent.parent.is_symlink()
                or not path.is_file() or path.stat().st_size > MAX_PROOF_BYTES):
            raise ValueError('rule_change_proof_missing')
        raw = path.read_bytes()
        record = json.loads(raw)
        content = record.get('content')
        version = record.get('schema_version')
        if (version == 2 and set(record) != {'schema_version','content','confirmation_id'}) or (
            version == 3 and set(record) != {'schema_version','content'}) or version not in {2, 3}:
            raise ValueError('rule_change_proof_invalid')
        if not isinstance(content, dict):
            raise ValueError('rule_change_proof_invalid')
        if (content.get('change_id'), content.get('capability'), content.get('requirement'),
            content.get('before'), content.get('after'), content.get('delta_sha256')) != (
            successor, key[0], key[1], before, after, tree_hash(folder/'specs')):
            raise ValueError('rule_change_proof_changed')
        confirmation_id = None
        if version == 2:
            row = _row(db, project, successor, content)
            if not row or row['id'] != record['confirmation_id']:
                raise ValueError('rule_change_confirmation_missing')
            confirmation_id = row['id']
        return {'proof_path': path.relative_to(root).as_posix(),
                'proof_sha256': hashlib.sha256(raw).hexdigest(), 'dependencies': [],
                'rule_change': {'schema_version': version, 'confirmation_id': confirmation_id,
                                'digest': digest(content)}}
    content = candidate(project, successor)
    if (content['capability'], content['requirement'], content['before'], content['after']) != (
        key[0], key[1], before, after):
        raise ValueError('rule_change_candidate_changed')
    path = proof_path(root, successor, key)
    if path.is_symlink() or path.parent.is_symlink() or path.parent.parent.is_symlink():
        raise ValueError('unsafe_rule_change_proof')
    if path.exists():
        expected = canonical({'schema_version': 3, 'content': content})
        if path.is_symlink() or path.read_bytes() != expected:
            raise ValueError('rule_change_proof_changed')
    return {'proof_path': path.relative_to(root).as_posix(), 'virtual': True,
            'dependencies': [], 'rule_change': {'schema_version': 3,
                'digest': digest(content), 'content': content}}


def recheck(certificate: dict) -> None:
    from .controlled_successor import _authority
    context = _authority.get()
    if context is None:
        raise ValueError('rule_change_authority_unavailable')
    db, project, _actor, _operation_id, _fence = context
    data = certificate['rule_change']
    if data.get('schema_version') == 3:
        if certificate.get('virtual'):
            if candidate(project, data['content']['change_id']) != data['content']:
                raise ValueError('rule_change_candidate_changed')
            path = project.root/certificate['proof_path']
            if path.is_symlink() or path.parent.is_symlink() or path.parent.parent.is_symlink():
                raise ValueError('unsafe_rule_change_proof')
            if path.exists() and path.read_bytes() != canonical({'schema_version': 3, 'content': data['content']}):
                raise ValueError('rule_change_proof_changed')
        return
    row = db.execute(select(confirmations).where(confirmations.c.id == data['confirmation_id'],
        confirmations.c.scope_key == project.key,
        confirmations.c.content_digest == data['digest'],
        confirmations.c.state == 'confirmed')).mappings().first()
    if not row:
        raise ValueError('rule_change_confirmation_changed')
    if certificate.get('virtual'):
        owner = db.scalar(text('SELECT owner_id FROM admin_spaces WHERE id=:space'),
                          {'space': row['space_id']})
        if owner != row['actor_id']:
            raise ValueError('rule_change_confirmation_owner_changed')
        if candidate(project, json.loads(row['body'])['change_id']) != data['content']:
            raise ValueError('rule_change_candidate_changed')
        path = project.root/certificate['proof_path']
        if path.is_symlink() or path.parent.is_symlink() or path.parent.parent.is_symlink():
            raise ValueError('unsafe_rule_change_proof')
        if path.exists():
            expected = canonical({'schema_version': 2, 'content': data['content'],
                                  'confirmation_id': row['id']})
            if path.is_symlink() or path.read_bytes() != expected:
                raise ValueError('rule_change_proof_changed')


def publish(project, change: str, db) -> None:
    content = candidate(project, change)
    key = (content['capability'], content['requirement'])
    path = proof_path(project.root, change, key)
    if path.parent.parent.is_symlink() or path.parent.is_symlink():
        raise ValueError('unsafe_rule_change_proof')
    record = {'schema_version': 3, 'content': content}
    raw = canonical(record)
    if path.exists():
        if path.is_symlink() or path.read_bytes() != raw:
            raise ValueError('rule_change_proof_changed')
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink() or path.parent.parent.is_symlink():
        raise ValueError('unsafe_rule_change_proof')
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    except FileExistsError:
        if path.read_bytes() != raw:
            raise ValueError('rule_change_proof_changed')
        return
    with os.fdopen(fd, 'wb') as output:
        output.write(raw)
        output.flush()
        os.fsync(output.fileno())
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
