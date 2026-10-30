"""Proof-bound additive metadata restoration; never mutate archived inputs."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile

from .archive_recovery import IDENTITY, archive_paths, delivery_input_hash, journal_path
from .acceptance_evidence import archived_readiness, latest_manifest


def safe_file(root: Path, path: Path) -> bytes:
    if not path.is_relative_to(root) or any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('unsafe metadata restoration path')
    return path.read_bytes()


def receipt_path(root: Path, change: str) -> Path:
    if not IDENTITY.fullmatch(change):
        raise ValueError('invalid change identity')
    return root / 'openspec/archive/.archive-recovery/metadata' / f'{change}.json'


def proof(root: Path, folder: Path) -> dict:
    """Bind the immutable source, original journal and complete passing manifest."""
    import yaml
    change = folder.name[11:]
    if not IDENTITY.fullmatch(change) or archive_paths(root, change) != [folder]:
        raise ValueError('ambiguous archive identity')
    source = safe_file(root, folder / 'acceptance.md')
    parts = source.decode('utf-8').split('---', 2)
    meta = yaml.safe_load(parts[1]) if len(parts) == 3 and not parts[0].strip() else {}
    if not isinstance(meta, dict) or meta.get('acceptance_status') != 'not_started':
        raise ValueError('only historical not_started acceptance metadata can be restored')
    journal = safe_file(root, journal_path(root, change))
    # The existing recovery/acceptance authority must independently pass.
    evidence = archived_readiness(root, folder)
    if evidence.get('status') != 'ready':
        raise ValueError('archive recovery and complete acceptance evidence must be ready')
    manifest = latest_manifest(folder)
    if not manifest or manifest.get('run_id') != evidence.get('run_id'):
        raise ValueError('acceptance manifest changed during restoration')
    digest = lambda raw: hashlib.sha256(raw).hexdigest()
    return {'schema_version': 1, 'change_id': change,
            'archive': folder.relative_to(root).as_posix(),
            'field': 'acceptance_status', 'from': 'not_started', 'to': 'passed',
            'source_sha256': digest(source), 'journal_sha256': digest(journal),
            'delivery_input_hash': delivery_input_hash(folder),
            'manifest_sha256': digest(json.dumps(manifest, sort_keys=True, ensure_ascii=False).encode()),
            'run_id': evidence['run_id']}


def restored_acceptance_status(root: Path, folder: Path) -> str | None:
    path = receipt_path(root, folder.name[11:])
    if not path.exists() and not path.is_symlink():
        return None
    raw = safe_file(root, path)
    if len(raw) > 16384:
        raise ValueError('oversized metadata restoration')
    record = json.loads(raw)
    expected = proof(root, folder)
    if not isinstance(record, dict) or record.get('proof') != expected or not record.get('restored_at'):
        raise ValueError('metadata restoration binding differs')
    if safe_file(root, path) != raw or proof(root, folder) != expected:
        raise ValueError('metadata restoration changed during validation')
    return expected['to']


def restore(root: Path, change: str, *, apply: bool = False) -> dict:
    root = root.resolve()
    path = receipt_path(root, change)
    folders = archive_paths(root, change)
    if len(folders) != 1:
        raise ValueError('exactly one archived Change is required')
    folder = folders[0]
    expected = proof(root, folder)
    if path.exists() or path.is_symlink():
        restored_acceptance_status(root, folder)
        return {'status': 'unchanged', 'receipt': path.relative_to(root).as_posix()}
    if not apply:
        return {'status': 'ready', 'proof': expected}
    if any(p.is_symlink() for p in (path.parent, *path.parent.parents)):
        raise ValueError('unsafe metadata restoration directory')
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {'proof': expected, 'restored_at': datetime.now(timezone.utc).isoformat()}
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(record, handle, ensure_ascii=False, sort_keys=True)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    try:
        if proof(root, folder) != expected:
            raise ValueError('metadata restoration inputs changed')
        # Publish complete bytes exclusively; no overwrite, including concurrent writers.
        os.link(temporary, path)
    finally:
        temporary.unlink()
    restored_acceptance_status(root, folder)
    return {'status': 'restored', 'receipt': path.relative_to(root).as_posix()}
