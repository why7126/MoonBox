"""授权验证任务的幂等状态与脱敏链路事实。"""
from __future__ import annotations

import json
import hashlib
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
from uuid import uuid4

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError

from app.chat import service as chat_service
from app.chat.schema import verification_tasks, task_traces, task_trace_spans
from app.chat.settings import repository_binding
from app.governance import scope
from app.verification.service import inspect_authorized
from app.chat.workspace import trusted_directory, WorkspaceError

TERMINAL = {"passed", "failed", "blocked", "cancelled", "timed_out"}


def _public(row) -> dict:
    result = json.loads(row["result"] or "{}")
    return {"id": row["id"], "space_id": row["space_id"], "repository_id": row["repository_id"],
            "browser": row["browser"], "environment_key": row["environment_key"],
            "status": row["status"], "error_code": row["error_code"], "result": result,
            "created_at": row["created_at"], "started_at": row["started_at"],
            "completed_at": row["completed_at"]}


def _trace(db, row: dict, status: str, error_code: str | None = None,
           request_id: str | None = None) -> None:
    try:
        with db.begin_nested():
            previous = db.execute(select(task_traces).where(task_traces.c.turn_id == row["id"])).mappings().first()
            metadata = json.dumps({"browser": row["browser"], "environment_key": row.get("environment_key"),
                                   "error_code": error_code}, sort_keys=True)
            if previous:
                trace_id = previous["task_trace_id"]
                db.execute(update(task_traces).where(task_traces.c.id == previous["id"]).values(
                    status=status, finished_at=chat_service.now() if status in TERMINAL else None,
                    updated_at=chat_service.now(), metadata=metadata))
            else:
                trace_id = str(uuid4())
                db.execute(insert(task_traces).values(**chat_service.identity(), task_trace_id=trace_id,
                    turn_id=row["id"], parent_request_id=request_id, task_type="project_verification",
                    task_name="verification.browser", actor_user_id=row["actor_id"], status=status,
                    metadata=metadata))
            db.execute(insert(task_trace_spans).values(**chat_service.identity(), task_trace_id=trace_id,
                span_name="verification." + status, status=status, metadata=metadata))
    except Exception:
        # Observability never changes the task outcome.
        pass


def create_task(db, actor: str, space_id: str, repository_id: str,
                client_request_id: str, browser: str, request_id: str | None = None) -> dict:
    scope.authorize(db, actor, space_id, repository_id, write=True)
    request_hash = hashlib.sha256(client_request_id.encode("ascii")).hexdigest()
    previous = db.execute(select(verification_tasks).where(
        verification_tasks.c.actor_id == actor, verification_tasks.c.space_id == space_id,
        verification_tasks.c.repository_id == repository_id,
        verification_tasks.c.client_request_id == request_hash)).mappings().first()
    if previous:
        if previous["browser"] != browser:
            raise chat_service.ChatError(2702, "幂等请求与原验证任务不一致", 409)
        return _public(previous)
    if browser not in ("firefox", "chromium"):
        raise chat_service.ChatError(2700, "浏览器类型无效", 422)
    readiness = inspect_authorized(db, actor, space_id, repository_id)
    if readiness["status"] == "unavailable":
        raise chat_service.ChatError(2701, "验证环境不可用", 503,
                                     kind="verification_unavailable",
                                     details={"reason": readiness["reason_code"]})
    row = {**chat_service.identity(), "actor_id": actor, "space_id": space_id,
           "repository_id": repository_id, "client_request_id": request_hash,
           "browser": browser, "environment_key": readiness["environment_key"],
           "image_digest": None, "status": "queued", "error_code": None, "result": "{}",
           "started_at": None, "completed_at": None}
    try:
        db.execute(insert(verification_tasks).values(**row))
        _trace(db, row, "queued", request_id=request_id)
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.execute(select(verification_tasks).where(
            verification_tasks.c.actor_id == actor, verification_tasks.c.space_id == space_id,
            verification_tasks.c.repository_id == repository_id,
            verification_tasks.c.client_request_id == request_hash)).mappings().first()
        if not existing or existing["browser"] != browser:
            raise chat_service.ChatError(2702, "幂等请求与原验证任务不一致", 409)
        return _public(existing)
    return _public(row)


def get_task(db, actor: str, task_id: str) -> dict:
    row = db.execute(select(verification_tasks).where(verification_tasks.c.id == task_id,
        verification_tasks.c.actor_id == actor)).mappings().first()
    if not row:
        raise chat_service.ChatError(2703, "验证任务不存在或无权访问", 404)
    chat_service.authorize_space(db, actor, row["space_id"])
    if not repository_binding(row["repository_id"], row["space_id"]):
        raise chat_service.ChatError(2703, "项目绑定已撤销", 403)
    return _public(row)


def cancel_task(db, actor: str, task_id: str) -> dict:
    get_task(db, actor, task_id)
    row = db.execute(select(verification_tasks).where(verification_tasks.c.id == task_id)).mappings().one()
    if row["status"] in TERMINAL:
        return _public(row)
    target = "cancelled" if row["status"] == "queued" else "cancelling"
    db.execute(update(verification_tasks).where(verification_tasks.c.id == task_id,
        verification_tasks.c.status == row["status"]).values(status=target,
        completed_at=chat_service.now() if target == "cancelled" else None,
        updated_at=chat_service.now()))
    changed = dict(row, status=target)
    _trace(db, changed, target)
    db.commit()
    return _public(changed)


def evidence_path(db, actor: str, task_id: str, filename: str) -> Path:
    item = get_task(db, actor, task_id)
    if item["status"] != "passed" or not re.fullmatch(r"(firefox|chromium)-[0-9]{3,4}x[0-9]{3,4}\.png", filename):
        raise chat_service.ChatError(2704, "验证证据不可用", 404)
    if filename not in {row.get("screenshot") for row in item["result"].get("viewports", []) if isinstance(row, dict)}:
        raise chat_service.ChatError(2704, "验证证据不可用", 404)
    completed = item["completed_at"]
    try:
        timestamp = datetime.fromisoformat(completed.replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - timestamp > timedelta(days=7):
            raise chat_service.ChatError(2705, "验证证据已过保留期", 410)
    except (AttributeError, ValueError):
        raise chat_service.ChatError(2704, "验证证据不可用", 404)
    try:
        root = trusted_directory(os.environ["MOONBOX_VERIFICATION_EVIDENCE_ROOT"])
        project_key = hashlib.sha256(f"{item['space_id']}\0{item['repository_id']}".encode()).hexdigest()
        folder = trusted_directory(root / project_key / task_id)
        path = folder / filename
        if path.is_symlink() or not path.is_file():
            raise WorkspaceError("missing")
    except (KeyError, WorkspaceError):
        raise chat_service.ChatError(2704, "验证证据不可用", 404)
    return path
