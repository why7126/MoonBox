"""Pin the actual immutable image and permission contract before starting a model turn."""
import hashlib
import re
from pathlib import Path
from sqlalchemy import insert, select
from app.chat.app_server import ExecutorError
from app.moonbox_core.schema import runtime_bindings, execution_receipts
from app.moonbox_core.workspaces import stamp


def pin(db, turn_id, workspace_id, server):
    digest = getattr(server, 'IMAGE', '')
    if not re.fullmatch(r'sha256:[0-9a-f]{64}', digest):
        raise ExecutorError('immutable_runtime_required')
    policy = Path(server.codex_home) / 'config.toml'
    if policy.is_symlink():
        raise ExecutorError('runtime_policy_invalid')
    policy_digest = hashlib.sha256(policy.read_bytes()).hexdigest()
    row = dict(turn_id=turn_id, workspace_id=workspace_id, image_digest=digest,
        tool_version=server.VERSION, policy_digest=policy_digest)
    previous = db.execute(select(runtime_bindings).where(runtime_bindings.c.turn_id == turn_id)).mappings().first()
    if previous:
        if any(previous[k] != v for k, v in row.items()):
            raise ExecutorError('runtime_resume_incompatible')
    else:
        db.execute(insert(runtime_bindings).values(**row, created_at=stamp()))
        db.execute(insert(execution_receipts).values(turn_id=turn_id,
            executor_id=getattr(server, 'container_name', None), executor_closed=0, files_collected=0))
    return row


def saved(db, turn_id):
    return db.execute(select(runtime_bindings).where(runtime_bindings.c.turn_id == turn_id)).mappings().first()
