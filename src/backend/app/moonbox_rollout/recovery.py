"""Pure recovery decisions; filesystem mutation requires a separately fenced operation."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import PurePosixPath


@dataclass(frozen=True)
class Entry:
    kind: str
    digest: str
    mode: int
    byte_count: int

    def __post_init__(self):
        if self.kind not in ('file', 'symlink') or self.byte_count < 0:
            raise ValueError('invalid_manifest_entry')
        if len(self.digest) != 64 or any(c not in '0123456789abcdef' for c in self.digest):
            raise ValueError('invalid_manifest_digest')
        if type(self.mode) is not int or not 0 <= self.mode <= 0o777:
            raise ValueError('invalid_manifest_mode')


def validate_path(path):
    if not isinstance(path, str) or '\x00' in path or '\\' in path:
        raise ValueError('invalid_manifest_path')
    parts = path.split('/')
    if not path or PurePosixPath(path).is_absolute() or any(p in ('', '.', '..', '.git') for p in parts):
        raise ValueError('invalid_manifest_path')
    return path


def fingerprint(manifest, *, policy_version, head_commit):
    """Permission policy and Git baseline are part of the trusted manifest identity."""
    values = []
    for path, entry in sorted(manifest.items()):
        validate_path(path)
        values.append([path, entry.kind, entry.digest, entry.mode, entry.byte_count])
    encoded = json.dumps([policy_version, head_commit, values], ensure_ascii=False,
                         separators=(',', ':')).encode()
    return hashlib.sha256(encoded).hexdigest()


def preflight(before, after, current, selected):
    """Undo only this operation's changes; preserve any later divergent content."""
    if len(set(selected)) != len(selected):
        raise ValueError('duplicate_restore_path')
    result = []
    for path in selected:
        validate_path(path)
        old, end, now = before.get(path), after.get(path), current.get(path)
        if old == end:
            action = 'unchanged'
        elif old == now:
            action = 'already_restored'
        elif now != end:
            action = 'conflict'
        elif (old and old.kind != 'file') or (end and end.kind != 'file'):
            action = 'unsupported'
        elif old is None:
            action = 'delete'
        else:
            action = 'restore'
        result.append({'path': path, 'action': action})
    return result


def rotation_candidates(points, protected_ids, *, keep=10):
    """Keep latest ten complete unprotected change points; pins are additional."""
    if type(keep) is not int or keep < 1:
        raise ValueError('invalid_retention_count')
    eligible = [p for p in points if p['state'] == 'complete'
                and p['id'] not in protected_ids and p['changed']]
    sequences = [p['sequence'] for p in eligible]
    if len(set(sequences)) != len(sequences):
        raise ValueError('ambiguous_point_order')
    eligible.sort(key=lambda p: p['sequence'], reverse=True)
    return [p['id'] for p in eligible[keep:]]
