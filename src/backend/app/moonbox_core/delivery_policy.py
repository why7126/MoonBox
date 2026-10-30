"""A development checkout may change implementation and its own Change, never registries."""
from pathlib import PurePosixPath
from sqlalchemy import select
from app.chat import service
from .schema import delivery_sessions, assignments
from .sessions import execution_workspace
from .authority import delivery


def execution_context(db, actor, parent, prompt):
    binding = execution_workspace(db, parent)
    if not binding or binding[0]['purpose'] != 'development':
        return None
    linked = db.execute(select(delivery_sessions).where(
        delivery_sessions.c.conversation_id == parent['id'])).mappings().first()
    if not linked:
        raise service.ChatError(2606, '开发工作区缺少交付链路', 409)
    assigned = db.execute(select(assignments).where(assignments.c.workspace_id == binding[0]['id'])).mappings().first()
    if not assigned or assigned['change_id'] != linked['change_id'] or assigned['state'] != 'developing':
        raise service.ChatError(2606, '此会话的交付阶段已结束，请在当前工作区创建后继会话', 409)
    project, context = delivery(db, actor, parent['space_id'], parent['repository_id'], linked['change_id'])
    if context['delivery_root'] != linked['delivery_root']:
        raise service.ChatError(2606, '交付链路已变化', 409)
    # Formal ID/review/Sprint/create/archive writes are confined to main.
    command = prompt.strip().split(maxsplit=1)[0] if prompt.strip().startswith('/') else ''
    if command and command not in ('/opsx-apply', '/opsx-modify', '/opsx-accept'):
        raise service.ChatError(2606, '此治理操作需在主工作区执行', 409)
    return {**context, 'workspace_id': binding[0]['id']}


def writable_roots(change_id):
    if not change_id or PurePosixPath(change_id).name != change_id or change_id.startswith('.'):
        raise ValueError('invalid_change_identity')
    return ('src', 'tests', 'docs', 'scripts', 'openspec/changes/' + change_id)
