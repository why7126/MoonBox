"""Deployment-owned Capture readiness; no client can enable the writer."""
import hashlib
import json
import os
import stat
import time
from app.chat.service import ChatError
from app.chat.settings import repository_catalog, repository_binding
from app.governance import store


def continuous():
    return os.environ.get('MOONBOX_GOVERNANCE_CAPTURE_MODE') == 'continuous'


def publish():
    base = store.root()
    projects = {}
    for entry in repository_catalog():
        binding = repository_binding(entry['id'], entry['space_id'])
        if not binding: continue
        from pathlib import Path
        root = Path(binding['governance_root'])
        paths = [root/'issues'/kind for kind in ('requirements', 'bugs')]
        writable = all(path.is_dir() and os.access(path, os.W_OK | os.X_OK) and
                       os.access(path/'_registry.yaml', os.R_OK) for path in paths)
        key = hashlib.sha256(f"{entry['space_id']}\0{entry['id']}".encode()).hexdigest()
        projects[key] = {'revision': hashlib.sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest(), 'writable': writable}
    data = json.dumps({'time': time.time(), 'continuous': continuous(), 'projects': projects})
    fd = os.open(base/'controller-ready.tmp', os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as stream: stream.write(data); stream.flush(); os.fsync(stream.fileno())
    os.replace(base/'controller-ready.tmp', base/'controller-ready.json')


def require_controller(project=None):
    try:
        path = store.root()/'controller-ready.json'
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd) as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_size > 1024*1024: raise ValueError()
            value = json.load(stream)
        if not 0 <= time.time() - value['time'] < 30: raise ValueError()
        if project:
            row = value['projects'].get(project.key, {})
            if row.get('revision') != project.binding_revision or not row.get('writable'): raise ValueError()
            if continuous() and value.get('continuous') is not True: raise ValueError()
    except (OSError, ValueError, KeyError, TypeError):
        raise ChatError(2605, 'Capture写入服务未就绪，请联系管理员检查服务配置', 503) from None


def require_capture(project):
    if continuous():
        require_controller(project)
    else:
        from app.governance.writer import maintenance
        maintenance(project)
        require_controller(project)


def status(db, project):
    try:
        if project.readonly: raise ChatError(2601, '当前项目没有写入权限', 403)
        require_capture(project)
        require_controller(project)
        from app.governance.writer import assert_readable
        assert_readable(db, project)
        return {'ready': True, 'reason': '', 'mode': 'continuous' if continuous() else 'maintenance'}
    except ChatError as error:
        return {'ready': False, 'reason': error.message, 'mode': 'unavailable'}
