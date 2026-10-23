"""Runtime compatibility intersection; absent or stale peers fail closed."""
import time
from uuid import uuid5, NAMESPACE_URL
from app.chat import service
from app.chat.workspace import WorkspaceError
from app.governance import store
from app.governance.durable_recovery import compatible

DECLARATION = {'schema_min': 1, 'schema_max': 1, 'actions': ['req-review', 'bug-review']}


def publish(role):
    if role not in ('worker', 'controller'):
        raise ValueError('invalid_capability_role')
    store.write(str(uuid5(NAMESPACE_URL, 'moonbox-recovery-runtime:' + role)), 'operation', {'time': time.time(), **DECLARATION})


def require(action):
    if action not in DECLARATION['actions']:
        return
    try:
        peers = [store.read(str(uuid5(NAMESPACE_URL, 'moonbox-recovery-runtime:' + role)), 'operation') for role in ('worker', 'controller')]
        if any(not 0 <= time.time() - peer['time'] < 30 for peer in peers):
            raise ValueError()
        if not compatible([DECLARATION, *peers], action):
            raise ValueError()
    except (OSError, KeyError, TypeError, ValueError, service.ChatError, WorkspaceError):
        raise service.ChatError(2605, '治理恢复服务版本或心跳不可确认，生成未开始', 503,
                                kind='recovery_capability_unavailable') from None
