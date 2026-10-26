"""Verify lossless EOF-LF transitions without changing historical journals."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath


def inventory_hash(files: dict[str, str]) -> str:
    from .archive_recovery import HASH
    digest = hashlib.sha256()
    if not isinstance(files, dict) or not files or len(files) > 10000:
        raise ValueError('invalid normalization inventory')
    for name in sorted(files, key=PurePosixPath):
        value = files[name]
        path = PurePosixPath(name)
        if (path.is_absolute() or '..' in path.parts or str(path) != name
                or '\\' in name or '\0' in name or not HASH.fullmatch(value)):
            raise ValueError('invalid normalization member')
        digest.update(name.encode() + b'\0' + bytes.fromhex(value))
    return digest.hexdigest()


def verify(root: Path, path: Path) -> dict:
    from .archive_recovery import (read_record, journal_path, archive_paths,
                                  completed_archive, tree_hash, delivery_input_hash)
    if path.is_symlink() or path.parent.is_symlink() or path.stat().st_size > 2 * 1024 * 1024:
        raise ValueError('unsafe normalization proof')
    raw = path.read_bytes()
    proof = json.loads(raw)
    if (not isinstance(proof, dict) or proof.get('schema_version') != 1
            or set(proof) != {'schema_version', 'source_change', 'successor_change',
                              'before', 'after', 'texts'}):
        raise ValueError('unsupported normalization proof')
    before, after = proof['before'], proof['after']
    if not all(isinstance(value, dict) for value in (before, after, proof['texts'])):
        raise ValueError('invalid normalization mapping')
    if set(before) != set(after):
        raise ValueError('normalization file set changed')
    changed = {key for key in before if before[key] != after[key]}
    if not changed or changed != set(proof['texts']):
        raise ValueError('normalization changed members differ')
    for name in changed:
        if len(PurePosixPath(name).parts) != 2 or not name.endswith('/spec.md'):
            raise ValueError('normalization requires capability spec')
        if not isinstance(proof['texts'][name], dict) or set(proof['texts'][name]) != {'before', 'after'}:
            raise ValueError('invalid normalization text pair')
        old, new = proof['texts'][name]['before'], proof['texts'][name]['after']
        if (not isinstance(old, str) or not isinstance(new, str)
                or not old.endswith('\n') or not new.endswith('\n') or not old.rstrip('\n')
                or old.rstrip('\n') != new.rstrip('\n')):
            raise ValueError('normalization changes spec content')
        if any(hashlib.sha256(body.encode()).hexdigest() != inventory[name]
               for body, inventory in ((old, before), (new, after))):
            raise ValueError('normalization content hash differs')
    start, end = inventory_hash(before), inventory_hash(after)
    for field, digest, key in (('source_change', start, 'expected_spec_hash'),
                               ('successor_change', end, 'baseline_spec_hash')):
        cid = proof[field]
        record = read_record(journal_path(root, cid))
        archives = archive_paths(root, cid)
        if (record.get(key) != digest or len(archives) != 1
                or (root / 'openspec/changes' / cid).exists()
                or not completed_archive(archives[0], cid)
                or tree_hash(archives[0] / 'specs') != record.get('delta_hash')
                or (record.get('schema_version') == 4
                    and delivery_input_hash(archives[0]) != record.get('delivery_input_hash'))):
            raise ValueError('normalization anchor invalid')
    if path.read_bytes() != raw:
        raise ValueError('normalization proof changed')
    return {'normalization': path.relative_to(root).as_posix(),
            'baseline_spec_hash': start, 'expected_spec_hash': end,
            'proof_hash': hashlib.sha256(raw).hexdigest()}


def transitions(root: Path) -> list[dict]:
    directory = root / 'openspec/archive/.spec-normalizations'
    if directory.is_symlink():
        raise ValueError('unsafe normalization directory')
    return [verify(root, p) for p in sorted(directory.glob('*.json'))]


def recheck(root: Path, edge: dict) -> None:
    if verify(root, root / edge['normalization']) != edge:
        raise ValueError('normalization changed during proof')
