"""单机常驻执行门禁；API 仅读取配置摘要和 worker 心跳，不读取凭证。"""
import hashlib
import json
import os
from pathlib import Path
import stat
import time
from app.chat.settings import execution_limits, retention_limits, repository_catalog, repository_binding, backup_root, local_snapshot_limit


def fingerprint():
    names = ('MOONBOX_CHAT_EXECUTION_MODE','MOONBOX_CHAT_REPOSITORIES','MOONBOX_CHAT_REPOSITORY_BINDINGS',
             'MOONBOX_CHAT_LIMITS','MOONBOX_CHAT_RETENTION','MOONBOX_CHAT_BACKUP_ROOT','MOONBOX_CHAT_LOCAL_SNAPSHOT_LIMIT','DATABASE_URL')
    return hashlib.sha256(json.dumps({name:os.environ.get(name,'') for name in names},sort_keys=True).encode()).hexdigest()


def configured(db):
    if os.environ.get('MOONBOX_CHAT_EXECUTION_MODE') != 'local-codex': return False
    if not execution_limits() or not retention_limits() or not backup_root(): return False
    try: local_snapshot_limit()
    except ValueError: return False
    if db.get_bind().dialect.name != 'sqlite': return False
    catalog = repository_catalog()
    if not catalog or len({row['id'] for row in catalog}) != len(catalog): return False
    for row in catalog:
        binding=repository_binding(row['id'],row['space_id'])
        if not binding: return False
        for key in ('source_root','workspace_root','governance_root'):
            if not isinstance(binding.get(key),str) or not Path(binding[key]).is_absolute(): return False
    return True


READINESS_REASONS = {
    'ready': '仓库执行服务已就绪',
    'configuration_invalid': '执行服务配置不完整，请联系管理员检查部署配置',
    'worker_starting': '执行服务尚未就绪，正在自动重试；草稿已保留',
    'worker_heartbeat_expired': '执行服务心跳暂时中断，正在自动重试；草稿已保留',
    'worker_configuration_mismatch': '执行服务配置版本不一致，请更新 Worker 部署',
    'worker_heartbeat_invalid': '执行服务心跳不可校验，请联系管理员检查服务状态',
    'repository_unavailable': '当前空间未配置可执行仓库，请联系管理员',
}


def readiness(db, actor, space, repository=None):
    if not configured(db): return 'configuration_invalid'
    try:
        path=Path(os.environ['MOONBOX_CHAT_STATE_ROOT'])/'worker-ready.json'
        info=path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o022: return 'worker_heartbeat_invalid'
        beat=json.loads(path.read_text())
        if beat.get('configuration') != fingerprint(): return 'worker_configuration_mismatch'
        if not 0 <= time.time()-beat['time'] < 5: return 'worker_heartbeat_expired'
        from app.chat.service import authorize_space
        authorize_space(db,actor,space)
        return 'ready' if any(row['space_id']==space and (repository is None or row['id']==repository) for row in repository_catalog()) else 'repository_unavailable'
    except FileNotFoundError: return 'worker_starting'
    except (OSError,ValueError,KeyError,TypeError): return 'worker_heartbeat_invalid'


def allowed(db, actor, space, repository=None):
    return readiness(db, actor, space, repository) == 'ready'
