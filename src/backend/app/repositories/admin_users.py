from __future__ import annotations

import json
import secrets
import string
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.admin_users import AdminUserCreate, AdminUserListParams, AdminUserUpdate

LEGACY_ADMIN_AVATAR_PREFIX = "/api/v1/admin/users/avatar/"
UNIFIED_AUTH_AVATAR_PREFIX = "/api/v1/auth/avatar/"


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_avatar_url(avatar_url: str | None) -> str | None:
    if not avatar_url:
        return avatar_url
    if avatar_url.startswith(LEGACY_ADMIN_AVATAR_PREFIX):
        return f"{UNIFIED_AUTH_AVATAR_PREFIX}{avatar_url.removeprefix(LEGACY_ADMIN_AVATAR_PREFIX)}"
    return avatar_url


def row_to_dict(row) -> dict:  # type: ignore[no-untyped-def]
    data = dict(row._mapping)
    data["is_system_superadmin"] = bool(data.get("is_system_superadmin"))
    data["avatar_url"] = normalize_avatar_url(data.get("avatar_url"))
    return data


def _json(data: dict | None) -> str | None:
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def audit(
    db: Session,
    *,
    actor: str,
    target_id: str,
    action: str,
    before: dict | None,
    after: dict | None,
    reason: str,
    result: str = "success",
    request_id: str | None = None,
) -> None:
    db.execute(
        text(
            """
            INSERT INTO admin_audit_events (
                id, actor, target_id, action, before_value, after_value,
                reason, result, request_id, created_at
            ) VALUES (
                :id, :actor, :target_id, :action, :before_value, :after_value,
                :reason, :result, :request_id, :created_at
            )
            """
        ),
        {
            "id": f"audit_{uuid4().hex}",
            "actor": actor,
            "target_id": target_id,
            "action": action,
            "before_value": _json(before),
            "after_value": _json(after),
            "reason": reason,
            "result": result,
            "request_id": request_id or f"req_{uuid4().hex[:12]}",
            "created_at": utc_now(),
        },
    )


def revoke_user_sessions(db: Session, user_id: str) -> None:
    now = utc_now()
    db.execute(
        text(
            """
            UPDATE admin_sessions
            SET revoked_at = COALESCE(revoked_at, :revoked_at), updated_at = :updated_at
            WHERE user_id = :user_id AND revoked_at IS NULL
            """
        ),
        {"user_id": user_id, "revoked_at": now, "updated_at": now},
    )


def list_users(db: Session, params: AdminUserListParams) -> tuple[list[dict], int]:
    filters: list[str] = []
    values: dict[str, object] = {"limit": params.page_size, "offset": (params.page - 1) * params.page_size}
    if params.q:
        filters.append("(LOWER(username) LIKE :query OR LOWER(COALESCE(nickname, '')) LIKE :query)")
        values["query"] = f"%{params.q.lower()}%"
    if params.role:
        filters.append("role = :role")
        values["role"] = params.role
    if params.status:
        filters.append("status = :status")
        values["status"] = params.status
    else:
        filters.append("status != '已删除'")

    where = f"WHERE {' AND '.join(filters)}" if filters else ""
    total = db.execute(text(f"SELECT COUNT(*) FROM admin_users {where}"), values).scalar_one()
    rows = db.execute(
        text(
            f"""
            SELECT id, username, nickname, avatar_url, role, status, workspace_count,
                   status_before_freeze, last_login_at, is_system_superadmin, deleted_at, session_invalidated_at,
                   created_at, updated_at
            FROM admin_users
            {where}
            ORDER BY is_system_superadmin DESC, created_at DESC
            LIMIT :limit OFFSET :offset
            """
        ),
        values,
    ).all()
    return [row_to_dict(row) for row in rows], int(total)


def get_user(db: Session, user_id: str) -> dict | None:
    row = db.execute(text("SELECT * FROM admin_users WHERE id = :id"), {"id": user_id}).first()
    return row_to_dict(row) if row else None


def username_exists(db: Session, username: str) -> bool:
    return bool(db.execute(text("SELECT 1 FROM admin_users WHERE username = :username"), {"username": username}).first())


def generate_temporary_password() -> str:
    alphabet = string.ascii_letters + string.digits
    return "Mb-" + "".join(secrets.choice(alphabet) for _ in range(18))


def create_user(db: Session, payload: AdminUserCreate, *, actor: str) -> tuple[dict, str]:
    if username_exists(db, payload.username):
        raise ValueError("用户名已存在。")
    from app.repositories.admin_auth import hash_password

    now = utc_now()
    user_id = f"user_{uuid4().hex}"
    temporary_password = generate_temporary_password()
    data = {
        "id": user_id,
        "username": payload.username,
        "nickname": payload.nickname,
        "avatar_url": payload.avatar_url,
        "role": payload.role,
        "status": "待激活",
        "workspace_count": 0,
        "password_hash": hash_password(temporary_password),
        "created_at": now,
        "updated_at": now,
    }
    db.execute(
        text(
            """
            INSERT INTO admin_users (
                id, username, nickname, avatar_url, role, status, workspace_count,
                status_before_freeze, last_login_at, password_hash, is_system_superadmin, deleted_at, session_invalidated_at,
                created_at, updated_at
            ) VALUES (
                :id, :username, :nickname, :avatar_url, :role, :status, :workspace_count,
                NULL, NULL, :password_hash, 0, NULL, NULL, :created_at, :updated_at
            )
            """
        ),
        data,
    )
    created = get_user(db, user_id)
    audit(db, actor=actor, target_id=user_id, action="create_user", before=None, after=created, reason="后台创建用户")
    db.commit()
    return created or {}, temporary_password


def ensure_mutable(user: dict) -> None:
    if user["is_system_superadmin"]:
        raise PermissionError("系统内置超级管理员不可操作。")


def update_user(db: Session, user_id: str, payload: AdminUserUpdate, *, actor: str) -> dict:
    before = get_user(db, user_id)
    if before is None:
        raise LookupError("用户不存在。")
    ensure_mutable(before)
    db.execute(
        text(
            """
            UPDATE admin_users
            SET nickname = :nickname, avatar_url = :avatar_url, role = :role, updated_at = :updated_at
            WHERE id = :id
            """
        ),
        {
            "id": user_id,
            "nickname": payload.nickname,
            "avatar_url": payload.avatar_url,
            "role": payload.role,
            "updated_at": utc_now(),
        },
    )
    after = get_user(db, user_id)
    audit(db, actor=actor, target_id=user_id, action="update_user", before=before, after=after, reason="后台编辑用户")
    db.commit()
    return after or {}


def set_status(db: Session, user_id: str, *, status: str, reason: str, actor: str) -> dict:
    before = get_user(db, user_id)
    if before is None:
        raise LookupError("用户不存在。")
    ensure_mutable(before)
    if before["status"] == "已删除" or status == "正常" and before["status"] != "已冻结":
        raise PermissionError("已删除用户不可恢复，非冻结用户不可解冻。")
    now = utc_now()
    session_invalidated_at = None
    deleted_at = before.get("deleted_at")
    status_before_freeze = before.get("status_before_freeze")
    if status == "已冻结":
        if before["status"] == "已冻结":
            status_before_freeze = before.get("status_before_freeze")
        elif before["status"] in {"待激活", "正常"}:
            status_before_freeze = before["status"]
        else:
            raise PermissionError("当前状态不可冻结。")
        session_invalidated_at = (datetime.now(UTC) + timedelta(seconds=10)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        revoke_user_sessions(db, user_id)
    if status == "正常" and before["status"] == "已冻结":
        if before.get("status_before_freeze") not in {"待激活", "正常"}:
            raise ValueError("缺少冻结前状态，无法安全解冻。")
        status = before["status_before_freeze"]
        status_before_freeze = None
        session_invalidated_at = None
    if status == "已删除":
        deleted_at = now
        status_before_freeze = None
        revoke_user_sessions(db, user_id)
    db.execute(
        text(
            """
            UPDATE admin_users
            SET status = :status, status_before_freeze = :status_before_freeze, deleted_at = :deleted_at,
                session_invalidated_at = :session_invalidated_at, updated_at = :updated_at
            WHERE id = :id
            """
        ),
        {
            "id": user_id,
            "status": status,
            "status_before_freeze": status_before_freeze,
            "deleted_at": deleted_at,
            "session_invalidated_at": session_invalidated_at,
            "updated_at": now,
        },
    )
    after = get_user(db, user_id)
    audit(db, actor=actor, target_id=user_id, action=f"set_status:{status}", before=before, after=after, reason=reason)
    db.commit()
    return after or {}


def reset_password(db: Session, user_id: str, *, reason: str, actor: str) -> str:
    before = get_user(db, user_id)
    if before is None:
        raise LookupError("用户不存在。")
    ensure_mutable(before)
    from app.repositories.admin_auth import hash_password

    temporary_password = generate_temporary_password()
    now = utc_now()
    db.execute(
        text("UPDATE admin_users SET password_hash = :password_hash, updated_at = :updated_at WHERE id = :id"),
        {"id": user_id, "password_hash": hash_password(temporary_password), "updated_at": now},
    )
    audit(
        db,
        actor=actor,
        target_id=user_id,
        action="reset_password",
        before={"id": user_id, "status": before["status"]},
        after={"id": user_id, "password_reset": "issued_once"},
        reason=reason,
    )
    revoke_user_sessions(db, user_id)
    db.commit()
    return temporary_password
