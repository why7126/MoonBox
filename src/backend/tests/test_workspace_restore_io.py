import hashlib
import pytest
from app.moonbox_rollout.recovery import Entry
from app.moonbox_rollout.restore_io import apply_one, RestoreConflict


def entry(value):
    return Entry('file', hashlib.sha256(value).hexdigest(), 0o644, len(value))


def test_restore_and_crash_reentry_are_idempotent(tmp_path):
    (tmp_path / 'file').write_bytes(b'after')
    args = dict(expected=entry(b'after'), desired=entry(b'before'), blocks=[b'before'])
    assert apply_one(tmp_path, 'file', **args) == 'restored'
    assert apply_one(tmp_path, 'file', **args) == 'already_restored'
    assert (tmp_path / 'file').read_bytes() == b'before'


def test_corrupt_content_and_external_edits_are_not_overwritten(tmp_path):
    (tmp_path / 'file').write_bytes(b'after')
    with pytest.raises(RestoreConflict, match='integrity'):
        apply_one(tmp_path, 'file', expected=entry(b'after'), desired=entry(b'before'), blocks=[b'bad'])
    assert (tmp_path / 'file').read_bytes() == b'after'
    assert list(tmp_path.glob('.moonbox-restore-*')) == []
    (tmp_path / 'file').write_bytes(b'new external edit')
    with pytest.raises(RestoreConflict, match='current_content_changed'):
        apply_one(tmp_path, 'file', expected=entry(b'after'), desired=None)
    assert (tmp_path / 'file').read_bytes() == b'new external edit'


def test_creation_deletion_and_symlink_escape(tmp_path):
    assert apply_one(tmp_path, 'file', expected=None, desired=entry(b'new'), blocks=[b'new']) == 'restored'
    assert apply_one(tmp_path, 'file', expected=entry(b'new'), desired=None) == 'restored'
    (tmp_path / 'linked').symlink_to(tmp_path.parent, target_is_directory=True)
    with pytest.raises(OSError):
        apply_one(tmp_path, 'linked/escape', expected=None, desired=entry(b'x'), blocks=[b'x'])
