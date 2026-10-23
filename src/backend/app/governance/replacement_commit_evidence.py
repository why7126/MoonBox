"""Bind immutable completion receipts to the original archive journal."""
import hashlib
from .archive_recovery import journal_path, read_record


def bindings(root, change):
    path = journal_path(root, change)
    if path.is_symlink() or any(p.is_symlink() for p in (path.parent, path.parent.parent)):
        raise ValueError('unsafe_commit_journal')
    record = read_record(path)
    if record.get('change_id') != change:
        raise ValueError('commit_journal_identity_changed')
    return {'journal_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'baseline_spec_hash': record['baseline_spec_hash'],
            'expected_spec_hash': record['expected_spec_hash']}
