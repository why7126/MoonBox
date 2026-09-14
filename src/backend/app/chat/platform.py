"""单机常驻执行门禁；API 仅读取配置摘要和 worker 心跳，不读取凭证。"""
import hashlib
import json
import os
from pathlib import Path
import stat
import time
from app.chat.settings import execution_limits, retention_limits, repository_catalog, repository_binding, backup_root


def fingerprint():
    names = ('MOONBOX_CHAT_EXECUTION_MODE','MOONBOX_CHAT_REPOSITORIES','MOONBOX_CHAT_REPOSITORY_BINDINGS',
             'MOONBOX_CHAT_LIMITS','MOONBOX_CHAT_RETENTION','MOONBOX_CHAT_BACKUP_ROOT','DATABASE_URL')
    return hashlib.sha256(json.dumps({name:os.environ.get(name,'') for name in names},sort_keys=True).encode()).hexdigest()


def configured(db):
    if os.environ.get('MOONBOX_CHAT_EXECUTION_MODE') != 'local-codex': return False
    if not execution_limits() or not retention_limits() or not backup_root(): return False
    if db.get_bind().dialect.name != 'sqlite': return False
    catalog = repository_catalog()
    if not catalog or len({row['id'] for row in catalog}) != len(catalog): return False
    for row in catalog:
        binding=repository_binding(row['id'],row['space_id'])
        if not binding: return False
        for key in ('source_root','workspace_root','governance_root'):
            if not isinstance(binding.get(key),str) or not Path(binding[key]).is_absolute(): return False
    return True


def allowed(db, actor, space, repository=None):
    if not configured(db): return False
    try:
        path=Path(os.environ['MOONBOX_CHAT_STATE_ROOT'])/'worker-ready.json'
        info=path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o022: return False
        beat=json.loads(path.read_text())
        if beat.get('configuration') != fingerprint() or not 0 <= time.time()-beat['time'] < 5: return False
        from app.chat.service import authorize_space
        authorize_space(db,actor,space)
        return any(row['space_id']==space and (repository is None or row['id']==repository) for row in repository_catalog())
    except (OSError,ValueError,KeyError,TypeError): return False
