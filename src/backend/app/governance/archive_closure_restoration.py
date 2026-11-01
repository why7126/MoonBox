"""Additive, proof-bound projections for narrowly defined archive leftovers.

This never edits delivery bytes or grants archive authorization. Consumers must
still run their normal acceptance, recovery, ownership and completion gates.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import unquote, urlsplit

from .acceptance_evidence import archived_readiness, latest_manifest
from .archive_metadata import safe_file
from .archive_recovery import IDENTITY, archive_paths, delivery_input_hash, journal_path, completed_archive


def receipt_path(root: Path, change: str) -> Path:
    if not IDENTITY.fullmatch(change):
        raise ValueError('invalid closure restoration identity')
    return root / 'openspec/archive/.archive-recovery/finalization' / (change + '.json')


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def proof(root: Path, change: str) -> dict:
    from .archive_admission import issue_identity
    from .archive_finalization import metadata, navigation
    receipt_path(root, change)
    folders = archive_paths(root, change)
    active = root / 'openspec/changes' / change
    if len(folders) != 1 or folders[0].parent != root / 'openspec/archive' or active.exists() or active.is_symlink():
        raise ValueError('closure archive identity ambiguous')
    folder = folders[0]
    trace = folder / 'trace.md'
    safe_file(root, trace)
    if not completed_archive(folder, change):
        raise ValueError('closure archive not completed')
    evidence = archived_readiness(root, folder)
    manifest = latest_manifest(folder)
    if evidence.get('status') != 'ready' or not manifest or manifest.get('scope') != 'complete' or manifest.get('status') != 'passed' or manifest.get('run_id') != evidence.get('run_id'):
        raise ValueError('closure requires complete current archive evidence')
    sources, projections = {}, []

    def bind(path: Path) -> str:
        relative = path.relative_to(root).as_posix()
        sources[relative] = digest(safe_file(root, path))
        return relative

    proposal = folder / 'proposal.md'
    if proposal.is_file() and metadata(proposal).get('status') == 'proposed':
        projections.append({'file': bind(proposal), 'field': 'status', 'from': 'proposed', 'to': 'archived'})
    oid = issue_identity(metadata(trace))
    if oid:
        if not isinstance(oid, str) or not re.fullmatch(r'(REQ|BUG)-\d{4}-[a-z0-9-]+', oid):
            raise ValueError('closure source identity invalid')
        base = root / 'issues' / ('requirements' if oid.startswith('REQ-') else 'bugs')
        issue = base / 'archive' / oid
        existing = [p for p in [base / oid, *(base / stage / oid for stage in ('plan', 'review', 'archive'))] if p.exists() or p.is_symlink()]
        if existing != [issue]:
            raise ValueError('closure source is not uniquely archived')
        for name in ('trace.md', 'requirement.md' if oid.startswith('REQ-') else 'bug.md', 'acceptance.md'):
            bind(issue / name)
        im = metadata(issue / 'trace.md')
        principal = metadata(issue / ('requirement.md' if oid.startswith('REQ-') else 'bug.md'))
        acceptance = metadata(issue / 'acceptance.md')
        if im.get('status') != 'done' or im.get('lifecycle_stage') != 'archive' or principal.get('status') != 'done' or acceptance.get('acceptance_status') not in {'passed', 'accepted', 'approved', 'done', 'complete', 'completed'} or acceptance.get('manual_acceptance_status') in {'pending', 'failed', 'required'}:
            raise ValueError('closure source not complete')
        links = [v.get('change_id') if isinstance(v, dict) else v for v in im.get('openspec_changes', [])]
        links += im.get('related_changes') or []
        if im.get('related_change'):
            links.append(im['related_change'])
        if change not in links:
            raise ValueError('closure source ownership mismatch')
        for cid in links:
            if not isinstance(cid, str) or not IDENTITY.fullmatch(cid):
                raise ValueError('closure sibling identity invalid')
            siblings = archive_paths(root, cid)
            sibling_active = root / 'openspec/changes' / cid
            if len(siblings) != 1 or siblings[0].parent != root / 'openspec/archive' or sibling_active.exists() or sibling_active.is_symlink() or not completed_archive(siblings[0], cid):
                raise ValueError('closure sibling not complete')
            bind(siblings[0] / 'trace.md')
        prefix = f'openspec/changes/{change}/'
        for document in sorted(issue.glob('*.md')):
            raw = safe_file(root, document)
            for _, value in navigation(raw.decode('utf-8')):
                parts = urlsplit(value)
                path = unquote(parts.path)
                if parts.scheme or parts.netloc or not path.startswith(prefix):
                    continue
                tail = Path(path[len(prefix):])
                if not tail.parts or tail.is_absolute() or '..' in tail.parts:
                    raise ValueError('closure reference escapes archive')
                target = folder / tail
                if not target.is_file():
                    raise ValueError('closure reference destination missing')
                projections.append({'file': bind(document), 'from_path': path, 'to_path': bind(target)})
    # Preserve the original apply-stage assertion, with proof of the later closure.
    # An exact sentence only: neighbouring failures must never be suppressed.
    from .archive_finalization import paragraphs
    for line, paragraph, heading in paragraphs(safe_file(root, trace).decode('utf-8')):
        if heading.split(' / ')[-1] != '验收结论':
            continue
        for sentence in re.split(r'[。；;]', paragraph):
            if sentence.strip() == '无正式归档授权，本次未归档':
                projections.append({'file': bind(trace), 'line': line,
                                    'historical_sentence': sentence.strip()})
    # A quoted diagnosis in proposal background is not a present-state claim.
    # Full-sentence matching intentionally leaves unknown or appended claims open.
    quoted_diagnosis = re.compile(
        r'(?:BUG|REQ)-\d{4}归档同步后，验收结论保留'
        r'“无正式归档授权，本次未归档”，共享收尾校验误当当前状态')
    if proposal.is_file():
        for line, paragraph, heading in paragraphs(safe_file(root, proposal).decode('utf-8')):
            if heading.split(' / ')[-1] != '背景':
                continue
            for sentence in re.split(r'[。；;]', paragraph):
                if quoted_diagnosis.fullmatch(sentence.strip()):
                    projections.append({'file': bind(proposal), 'line': line,
                                        'historical_sentence': sentence.strip()})
    if not projections:
        raise ValueError('no supported closure restoration')
    return {'schema_version': 1, 'change_id': change, 'archive': folder.relative_to(root).as_posix(),
            'journal_sha256': digest(safe_file(root, journal_path(root, change))),
            'delivery_input_hash': delivery_input_hash(folder),
            'manifest_sha256': digest(json.dumps(manifest, sort_keys=True, ensure_ascii=False).encode()),
            'run_id': evidence['run_id'], 'sources': sources, 'projections': projections}


def verified(root: Path, change: str) -> dict | None:
    path = receipt_path(root, change)
    if not path.exists() and not path.is_symlink():
        return None
    raw = safe_file(root, path)
    if len(raw) > 256 * 1024:
        raise ValueError('oversized closure receipt')
    record = json.loads(raw)
    expected = proof(root, change)
    if not isinstance(record, dict) or not record.get('restored_at'):
        raise ValueError('closure restoration binding differs')
    if record.get('proof') != expected:
        from .archive_trace_supplement import verify
        verify(root, change, raw, expected)
    if safe_file(root, path) != raw or proof(root, change) != expected:
        raise ValueError('closure restoration changed during validation')
    return expected


def document_projection(root: Path, document: Path) -> list[dict]:
    """Only eligible archive documents or closed source Issues use a receipt."""
    from .archive_finalization import metadata
    parts = document.relative_to(root).parts
    changes = []
    if len(parts) == 4 and parts[:2] == ('openspec', 'archive') and parts[3] in {'proposal.md', 'trace.md'}:
        changes = [parts[2][11:]]
    elif len(parts) == 5 and parts[0] == 'issues' and parts[1] in {'requirements', 'bugs'} and parts[2] == 'archive':
        trace = document.parent / 'trace.md'
        if not trace.is_file():
            return []
        safe_file(root, trace)
        meta = metadata(trace)
        changes = [v.get('change_id') if isinstance(v, dict) else v for v in meta.get('openspec_changes', [])]
        changes += meta.get('related_changes') or []
        if meta.get('related_change'):
            changes.append(meta['related_change'])
    rows = []
    for change in dict.fromkeys(changes):
        if not isinstance(change, str) or not IDENTITY.fullmatch(change):
            raise ValueError('invalid closure source identity')
        value = verified(root, change)
        if value:
            rows.extend(row for row in value['projections'] if row['file'] == document.relative_to(root).as_posix())
    return rows


def restore(root: Path, change: str, *, apply: bool = False) -> dict:
    root = root.resolve()
    path = receipt_path(root, change)
    expected = proof(root, change)
    if path.exists() or path.is_symlink():
        verified(root, change)
        return {'status': 'unchanged', 'receipt': path.relative_to(root).as_posix()}
    if not apply:
        return {'status': 'ready', 'proof': expected}
    if any(p.is_symlink() for p in (path.parent, *path.parent.parents)):
        raise ValueError('unsafe closure receipt directory')
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {'proof': expected, 'restored_at': datetime.now(timezone.utc).isoformat()}
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(record, handle, sort_keys=True, ensure_ascii=False)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    try:
        if proof(root, change) != expected:
            raise ValueError('closure inputs changed before publication')
        os.link(temporary, path)
    finally:
        temporary.unlink()
    verified(root, change)
    return {'status': 'restored', 'receipt': path.relative_to(root).as_posix()}
