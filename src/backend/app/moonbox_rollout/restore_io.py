"""One fenced restore step. Caller owns workspace lock, ACL and durable operation journal."""
import hashlib
import os
import stat
from uuid import uuid4
from app.chat.snapshot_store import parent_fd
from app.chat.workspace import trusted_directory
from .recovery import Entry, validate_path


class RestoreConflict(ValueError):
    pass


def _read(directory, name):
    try:
        info = os.stat(name, dir_fd=directory, follow_symlinks=False)
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise RestoreConflict('unsupported_or_linked_file')
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise RestoreConflict('unsupported_or_linked_file')
        digest = hashlib.sha256()
        size = 0
        while block := os.read(fd, 65536):
            digest.update(block)
            size += len(block)
        after = os.fstat(fd)
        current = os.stat(name, dir_fd=directory, follow_symlinks=False)
        fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns', 'st_mode', 'st_nlink')
        if any(getattr(before, k) != getattr(after, k) or getattr(after, k) != getattr(current, k) for k in fields):
            raise RestoreConflict('file_changed_during_preflight')
        return Entry('file', digest.hexdigest(), stat.S_IMODE(after.st_mode), size)
    finally:
        os.close(fd)


def apply_one(root, path, *, expected, desired, blocks=()):
    """Return a verifiable step result; never treat multiple files as atomic.

    Application writers must honor the workspace lease. External filesystem writers
    cannot be fenced by a database lease; two content checks narrow that race but do
    not establish an OS-level compare-and-swap guarantee.
    """
    validate_path(path)
    if any(value is not None and value.kind != 'file' for value in (expected, desired)):
        raise RestoreConflict('unsupported_restore_kind')
    root_fd = os.open(trusted_directory(root), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    directory = None
    temporary = None
    try:
        try:
            directory, name = parent_fd(root_fd, path)
        except FileNotFoundError:
            if desired is None:
                return 'already_restored'
            if expected is not None:
                raise RestoreConflict('current_content_changed') from None
            # Recreate deleted directories without following parent links.
            directory = os.dup(root_fd)
            for part in path.split('/')[:-1]:
                try:
                    os.mkdir(part, mode=0o755, dir_fd=directory)
                except FileExistsError:
                    pass
                nested = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                os.close(directory)
                directory = nested
            name = path.split('/')[-1]
        current = _read(directory, name)
        if current == desired:
            return 'already_restored'
        if current != expected:
            raise RestoreConflict('current_content_changed')
        if desired is None:
            # The workspace lease serializes MoonBox writers, not arbitrary OS processes.
            if _read(directory, name) != expected:
                raise RestoreConflict('current_content_changed')
            os.unlink(name, dir_fd=directory)
        else:
            temporary = '.moonbox-restore-' + uuid4().hex
            fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600, dir_fd=directory)
            try:
                digest = hashlib.sha256(); size = 0
                for block in blocks:
                    digest.update(block); size += len(block)
                    if size > desired.byte_count:
                        raise RestoreConflict('recovery_content_integrity')
                    view = memoryview(block)
                    while view:
                        written = os.write(fd, view)
                        view = view[written:]
                if size != desired.byte_count or digest.hexdigest() != desired.digest:
                    raise RestoreConflict('recovery_content_integrity')
                os.fchmod(fd, desired.mode)
                os.fsync(fd)
            finally:
                os.close(fd)
            if _read(directory, name) != expected:
                raise RestoreConflict('current_content_changed')
            os.replace(temporary, name, src_dir_fd=directory, dst_dir_fd=directory)
            temporary = None
        os.fsync(directory)
        if _read(directory, name) != desired:
            raise RestoreConflict('restore_outcome_changed')
        return 'restored'
    finally:
        if temporary is not None and directory is not None:
            os.unlink(temporary, dir_fd=directory)
        if directory is not None:
            os.close(directory)
        os.close(root_fd)
