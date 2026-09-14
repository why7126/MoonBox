"""回环测试环境门禁；正常部署永远不因配置文件而开放执行。"""
import json
import os
from pathlib import Path
import stat
import time
from app.chat.settings import execution_limits, repository_binding
from app.chat.workspace import trusted_directory


def configuration(db=None, *, live=False):
    if os.environ.get('APP_ENV')!='isolated-test' or os.environ.get('CHAT_LIVE_ISOLATED_PROBE')!='1':return None
    try:
        file=Path(os.environ['MOONBOX_CHAT_LOCAL_CONFIG'])
        info=file.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid!=os.getuid() or info.st_mode & 0o077:return None
        value=json.loads(file.read_text());root=trusted_directory(value['root'])
        if value.get('executor','native') not in ('native','container'):return None
        if root.parent!=Path('/private/tmp') or not root.name.startswith('moonbox-chat-e2e-'):return None
        if file.parent!=root or root.stat().st_mode & 0o077:return None
        if not time.time()<value['expires_at']<=time.time()+7200:return None
        if not execution_limits():return None
        if db is not None:
            url=db.get_bind().url
            if url.get_backend_name()!='sqlite' or Path(url.database).resolve()!=root/'chat.db':return None
        if live:
            beat=json.loads((root/'worker-ready.json').read_text())
            if not 0<=time.time()-beat['time']<5:return None
        return value
    except (OSError,ValueError,KeyError,TypeError,RuntimeError):return None


def allowed(db, actor, space, repository=None):
    if os.environ.get('MOONBOX_CHAT_EXECUTION_MODE') == 'local-codex':
        from app.chat.platform import allowed as platform_allowed
        return platform_allowed(db, actor, space, repository)
    value=configuration(db,live=True)
    if not value or actor!=value['actor'] or space!=value['space']:return False
    if repository is not None and repository!=value['repository']:return False
    binding=repository_binding(value['repository'],space)
    return bool(binding and binding.get('workspace_root')==str(Path(value['root'])/'workspaces'))
