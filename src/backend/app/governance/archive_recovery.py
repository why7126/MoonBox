"""Read-only archive recovery proof shared by product admission and the CLI.

An unrelated archive may advance the full spec fingerprint only through a
continuous chain of retained journals and unique, completed archive artifacts.
No repository code is executed here and no recovery journal is repaired on read.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

IDENTITY = re.compile(r'[a-z0-9][a-z0-9-]{0,100}')
HASH = re.compile(r'[a-f0-9]{64}')
MAX_JOURNAL_BYTES = 256 * 1024
MAX_CHAIN = 128


class RecoveryBlocked(ValueError):
    def __init__(self, code: str, message: str, *, diagnostics=None):
        super().__init__(message)
        self.code = code
        self.diagnostics = diagnostics or []


def delivery_input_hash(root: Path) -> str:
    """Versioned input projection; unknown files remain protected by default.

    Only generated acceptance reports and trace narrative/timestamps are outputs.
    Trace identity, status and initial execution facts remain protected. Evidence
    integrity is independently checked by acceptance_evidence before admission.
    """
    digest = hashlib.sha256(b'archive-delivery-input-v1\0')
    if root.is_symlink():
        raise ValueError('archive recovery rejects a symlink root')
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('archive recovery rejects a symlink')
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative.startswith('evidence/acceptance/'):
            continue
        content = path.read_bytes()
        if relative == 'trace.md':
            text = content.decode('utf-8')
            if not text.startswith('---\n') or '\n---' not in text[4:]:
                raise ValueError('archive trace frontmatter missing')
            try:
                metadata = yaml.safe_load(text.split('---', 2)[1])
            except yaml.YAMLError as error:
                raise ValueError('archive trace frontmatter invalid') from error
            if not isinstance(metadata, dict):
                raise ValueError('archive trace frontmatter invalid')
            metadata.pop('updated_at', None)
            content = json.dumps(metadata, sort_keys=True, default=str,
                                 ensure_ascii=False).encode()
        digest.update(relative.encode() + b'\0')
        digest.update(hashlib.sha256(content).digest())
    return digest.hexdigest()


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    if root.is_symlink():
        raise ValueError('archive recovery rejects a symlink root')
    if not root.exists():
        return digest.hexdigest()
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('archive recovery rejects a symlink')
        if path.is_file():
            digest.update(path.relative_to(root).as_posix().encode())
            digest.update(b'\0')
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def requirement_blocks(text: str) -> dict[str, str]:
    parts = re.split(r'(?m)^### Requirement: (.+)\n', text)
    result = {}
    for index in range(1, len(parts), 2):
        title = parts[index].strip()
        if title in result:
            raise ValueError('duplicate requirement title')
        result[title] = ' '.join(re.split(r'(?m)^## ', parts[index + 1])[0].split())
    return result


def verify_delta_effects(delta_root: Path, specs_root: Path) -> None:
    verify_chain_effects([delta_root.parent], specs_root)


def verify_chain_effects(archives: list[Path], specs_root: Path) -> None:
    """Later proven successors can supersede each other's independent titles."""
    expected = {}
    for archive in archives:
        for key, (kind, body) in delta_operations(archive).items():
            expected[key] = None if kind == 'REMOVED' else body
    for (capability, title), body in expected.items():
        path = specs_root / capability / 'spec.md'
        actual = requirement_blocks(path.read_text()) if path.exists() else {}
        if (title in actual if body is None else actual.get(title) != body):
            raise ValueError('archive chain final delta effect differs')


def journal_path(root: Path, change: str) -> Path:
    if not IDENTITY.fullmatch(change):
        raise ValueError('invalid change identity')
    return root / 'openspec/archive/.archive-recovery' / (change + '.json')


def read_record(path: Path) -> dict:
    if path.is_symlink() or path.parent.is_symlink() or path.stat().st_size > MAX_JOURNAL_BYTES:
        raise ValueError('unsafe archive recovery journal')
    record = json.loads(path.read_text())
    if not isinstance(record, dict) or record.get('change_id') != path.stem:
        raise ValueError('archive journal identity differs')
    if not HASH.fullmatch(str(record.get('expected_spec_hash', ''))):
        raise ValueError('invalid expected spec fingerprint')
    return record


def archive_paths(root: Path, change: str) -> list[Path]:
    return [p for base in ('openspec/archive', 'openspec/changes/archive')
            for p in (root / base).glob('????-??-??-' + change) if p.is_dir()]


def delta_operations(folder: Path) -> dict[tuple[str, str], tuple[str, str]]:
    """Parse only supported Requirement operations; unknown content fails closed."""
    base = folder / 'specs'
    tree_hash(base)
    files = sorted(p for p in base.rglob('*') if p.is_file())
    if not files or any(len(p.relative_to(base).parts) != 2 or p.name != 'spec.md' for p in files):
        raise ValueError('archive delta files unsupported or missing')
    result = {}
    for path in files:
        text = path.read_text()
        if text.startswith('---\n'):
            parts = text.split('---', 2)
            if len(parts) != 3:
                raise ValueError('archive delta metadata invalid')
            text = parts[2]
        sections = re.split(r'(?m)^## (.+?)\s*$', text)
        if len(sections) == 1:
            raise ValueError('archive delta operations missing')
        # A document title is presentation only. Other preamble is not a delta.
        if any(line.strip() and not re.fullmatch(r'# [^#]+', line) for line in sections[0].splitlines()):
            raise ValueError('archive delta preamble unsupported')
        for index in range(1, len(sections), 2):
            heading, content = sections[index:index + 2]
            if heading not in {'ADDED Requirements', 'MODIFIED Requirements', 'REMOVED Requirements'}:
                raise ValueError('archive delta operation unsupported')
            before = content.split('### Requirement:', 1)[0]
            blocks = requirement_blocks(content)
            if before.strip() or not blocks or len(re.findall(r'(?m)^### ', content)) != len(blocks):
                raise ValueError('archive delta requirement syntax invalid')
            for title, body in blocks.items():
                key = (path.parent.name, title)
                if not title or not body or key in result:
                    raise ValueError('archive delta requirement duplicate or empty')
                result[key] = (heading.split()[0], body)
    return result


def delta_scope(folder: Path) -> set[tuple[str, str]]:
    return set(delta_operations(folder))


def completed_archive(archive: Path, change: str) -> bool:
    """Canonical archives preserve the first apply execution metadata in this project."""
    trace = archive / 'trace.md'
    if trace.is_symlink():
        return False
    try:
        parts = trace.read_text().split('---', 2)
        meta = yaml.safe_load(parts[1]) if len(parts) == 3 and not parts[0].strip() else None
    except yaml.YAMLError:
        return False
    if not isinstance(meta, dict) or meta.get('change_id', change) != change:
        return False
    if meta.get('status') == 'archived':
        return True
    execution = meta.get('execution')
    tasks = archive / 'tasks.md'
    if (meta.get('status') != 'applied' or not isinstance(execution, dict)
            or not execution.get('completed_at') or tasks.is_symlink() or not tasks.is_file()):
        return False
    text = tasks.read_text()
    return bool(re.search(r'(?m)^\s*[-*] \[[xX]\]', text)) and not re.search(r'(?m)^\s*[-*] \[ \]', text)


def transition_chain(root: Path, change: str, start: str, current: str, folder: Path) -> list[dict]:
    """Prove a full-hash advance using only disjoint completed archives.

    Legacy v1/v2 journals are useful evidence: their before/after hashes retain
    exactly the same meaning. Missing edges, partial merges and overlapping
    capability updates cannot be inferred or silently rebaselined.
    """
    if current == start:
        return []
    if not HASH.fullmatch(str(start)):
        raise ValueError('archive recovery baseline missing')
    protected = delta_scope(folder)
    if not protected:
        raise ValueError('archive recovery scope missing')
    edges = {}
    for path in journal_path(root, change).parent.glob('*.json'):
        if path.stem == change:
            continue
        try:
            journal_bytes = path.read_bytes()
            record = read_record(path)
            if path.read_bytes() != journal_bytes:
                continue
            before, after = record.get('baseline_spec_hash'), record['expected_spec_hash']
            if HASH.fullmatch(str(before)) and before != after:
                edges.setdefault(before, []).append((record, path, hashlib.sha256(journal_bytes).hexdigest()))
        except (OSError, ValueError, TypeError):
            continue  # An invalid unrelated journal is not usable evidence.
    queue = [(start, [], frozenset((start,)), delta_operations(folder))]
    from .spec_normalization import transitions, recheck as recheck_normalization
    normalizations = transitions(root)
    examined = 0
    conflicts = []
    while queue and examined < MAX_CHAIN:
        node, chain, seen, protected_view = queue.pop(0)
        examined += 1
        for edge in normalizations:
            target = edge['expected_spec_hash']
            if edge['baseline_spec_hash'] == node and target not in seen:
                queue.append((target, chain + [edge], seen | {target}, protected_view))
        for record, path, journal_hash in edges.get(node, []):
            after = record['expected_spec_hash']
            if after in seen:
                continue
            cid = record['change_id']
            if not IDENTITY.fullmatch(cid):
                continue
            archives = archive_paths(root, cid)
            if len(archives) != 1 or (root / 'openspec/changes' / cid).exists():
                continue
            archive = archives[0]
            if archive.is_symlink():
                continue
            try:
                archive_hash = tree_hash(archive)
                if not completed_archive(archive, cid):
                    continue
                operations = delta_operations(archive)
                overlap = set(operations) & protected
                compatibility = []
                next_view = dict(protected_view)
                if overlap:
                    # Completed successors are governed by normal acceptance and
                    # immutable journal/delta checks, not a separate certificate.
                    from .compatible_successor import acceptance_binding
                    try:
                        acceptance_binding(root, archive)
                    except (OSError, ValueError):
                        conflicts.extend({'change_id': cid, 'capability': cap, 'requirement': title}
                                         for cap, title in sorted(overlap))
                        continue
                    for key in overlap:
                        next_view[key] = operations[key]
                if record.get('schema_version') == 4 and (record.get('input_projection') != 1
                        or delivery_input_hash(archive) != record.get('delivery_input_hash')):
                    continue
                if record.get('delta_hash') and tree_hash(archive / 'specs') != record['delta_hash']:
                    continue
            except (OSError, ValueError):
                continue
            evidence = {'change_id': cid, 'baseline_spec_hash': node, 'expected_spec_hash': after,
                        'journal_hash': journal_hash,
                        'archive_delta_hash': tree_hash(archive / 'specs'),
                        'archive_hash': archive_hash, 'compatibility': compatibility}
            next_chain = chain + [evidence]
            if after == current:
                try:
                    verify_chain_effects([archive_paths(root, edge['change_id'])[0] for edge in next_chain if 'change_id' in edge], root / 'openspec/specs')
                except (OSError, ValueError, IndexError):
                    conflicts.extend({'change_id': cid, 'capability': cap, 'requirement': title}
                                     for cap, title in sorted(overlap))
                    continue
                if tree_hash(root / 'openspec/specs') != current:
                    raise ValueError('archive recovery specs changed during proof')
                for edge in next_chain:
                    if 'normalization' in edge:
                        recheck_normalization(root, edge)
                        continue
                    raw = journal_path(root, edge['change_id']).read_bytes()
                    matches = archive_paths(root, edge['change_id'])
                    if (len(matches) != 1 or (root / 'openspec/changes' / edge['change_id']).exists()
                            or tree_hash(matches[0]) != edge['archive_hash']):
                        raise ValueError('archive recovery delivery changed during proof')
                    for certificate in edge.get('compatibility', []):
                        from .compatible_successor import recheck
                        recheck(root, certificate)
                    if hashlib.sha256(raw).hexdigest() != edge['journal_hash']:
                        raise ValueError('archive recovery journal changed during proof')
                return next_chain
            queue.append((after, next_chain, seen | {after}, next_view))
    if conflicts:
        raise RecoveryBlocked('archive_requirement_conflict', '归档后继触及受保护条文', diagnostics=conflicts)
    raise ValueError('archive recovery blocked: unproven spec transition')


def _recovery_state(root: Path, change: str, archive_date: str | None = None) -> dict:
    path = journal_path(root, change)
    active = root / 'openspec/changes' / change
    archives = archive_paths(root, change)
    if len(archives) + int(active.is_dir()) != 1:
        raise RecoveryBlocked('archive_identity_ambiguous', '归档对象身份不唯一，请核验活动与归档目录')
    if not path.exists() and not path.is_symlink():
        return {'mode': 'unprepared' if active.is_dir() else 'archived', 'chain': []}
    record = read_record(path)
    folder = active if active.is_dir() else archives[0]
    actual = tree_hash(root / 'openspec/specs')
    if not active.is_dir():
        if record.get('delta_hash') and tree_hash(folder / 'specs') != record['delta_hash']:
            raise RecoveryBlocked('archive_delivery_inputs_changed', '归档增量规格与恢复记录不一致')
        if record.get('schema_version') == 4 and delivery_input_hash(folder) != record.get('delivery_input_hash'):
            raise RecoveryBlocked('archive_delivery_inputs_changed', '归档交付输入与恢复记录不一致')
    merge_error = None
    if active.is_dir():
        if record.get('schema_version') == 4:
            if (record.get('input_projection') != 1
                    or delivery_input_hash(active) != record.get('delivery_input_hash')):
                raise RecoveryBlocked('archive_delivery_inputs_changed',
                                      '归档交付输入已变化，请重新核验并更新恢复记录')
        elif tree_hash(active) != record.get('active_change_hash'):
            raise RecoveryBlocked('archive_legacy_record_stale',
                                  '旧版归档恢复记录已过期，请核验并迁移恢复记录')
        try:
            chain = transition_chain(root, change, record.get('baseline_spec_hash'), actual, folder)
            return {'mode': 'merge', 'chain': chain}
        except ValueError as error:
            merge_error = error
    try:
        chain = transition_chain(root, change, record['expected_spec_hash'], actual, folder)
    except RecoveryBlocked:
        raise
    except ValueError as error:
        if isinstance(merge_error, RecoveryBlocked):
            raise merge_error
        raise RecoveryBlocked('archive_spec_baseline_changed',
                              '归档规格基线变化缺少完整证明，请核验关联归档记录') from error
    verify_chain_effects([folder] + [archive_paths(root, edge['change_id'])[0] for edge in chain if 'change_id' in edge], root / 'openspec/specs')
    return {'mode': 'move-only' if active.is_dir() else 'archived', 'chain': chain}


def recovery_state(root: Path, change: str, archive_date: str | None = None) -> dict:
    """Reject changed inputs instead of returning a stale successful proof."""
    def snapshot():
        paths = [root / 'openspec/changes' / change, *archive_paths(root, change)]
        journal = journal_path(root, change)
        if journal.exists() and (journal.is_symlink() or journal.stat().st_size > MAX_JOURNAL_BYTES):
            raise ValueError('unsafe archive recovery journal')
        return (tree_hash(root / 'openspec/specs'),
                tuple((str(p), tree_hash(p)) for p in paths),
                journal.read_bytes() if journal.exists() else None,
                tree_hash(root / 'openspec/archive/.compatible-successors'),
                tree_hash(root / 'openspec/archive/.controlled-successors'),
                tree_hash(root / 'openspec/archive/.rule-confirmations'),
                tree_hash(root / 'openspec/archive/.spec-normalizations'),
                tree_hash(root / 'openspec/archive/.archive-recovery'))
    before = snapshot()
    result = _recovery_state(root, change, archive_date)
    from .compatible_successor import recheck
    for edge in result.get('chain', []):
        if 'normalization' in edge:
            from .spec_normalization import recheck as recheck_normalization
            recheck_normalization(root, edge)
        for certificate in edge.get('compatibility', []):
            recheck(root, certificate)
    if snapshot() != before:
        raise RecoveryBlocked('archive_proof_inputs_changed', '归档证明期间输入变化，请重新核验')
    return result


def recovery_admission(root: Path, change: str, *, source_root: Path | None = None) -> dict:
    try:
        state = recovery_state(root, change)
        return {'ready': True, 'mode': state['mode'], 'chain': state['chain']}
    except RecoveryBlocked as error:
        return {'ready': False, 'reason': str(error), 'recovery_reason': error.code, 'diagnostics': error.diagnostics}
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        return {'ready': False, 'reason': '归档恢复记录损坏或无法安全读取，请核验恢复记录',
                'recovery_reason': 'archive_recovery_record_invalid'}
