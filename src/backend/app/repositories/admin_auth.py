from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.admin_users import audit, row_to_dict, utc_now

HASH_ITERATIONS = 120_000


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def hash_password(password: str, *, salt: str | None = None) -> str:
    salt_value = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_value.encode("utf-8"), HASH_ITERATIONS)
    return f"pbkdf2_sha256${HASH_ITERATIONS}${salt_value}${digest.hex()}"


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    try:
        algorithm, iterations_text, salt, expected = password_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), int(iterations_text))
    return hmac.compare_digest(digest.hex(), expected)


def token_hash(token: str) -> str:
    return hmac.new(settings.app_secret_key.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).hexdigest()


def get_user_by_username(db: Session, username: str) -> dict | None:
    row = db.execute(text("SELECT * FROM admin_users WHERE username = :username"), {"username": username}).first()
    return row_to_dict(row) if row else None


def get_user_by_id(db: Session, user_id: str) -> dict | None:
    row = db.execute(text("SELECT * FROM admin_users WHERE id = :id"), {"id": user_id}).first()
    return row_to_dict(row) if row else None


def create_session(db: Session, user: dict, *, remember_me: bool = False) -> dict:
    now = utc_now()
    expires_at = (
        datetime.now(UTC)
        + (timedelta(days=settings.jwt_remember_me_expire_days) if remember_me else timedelta(minutes=settings.jwt_access_token_expire_minutes))
    ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    token = secrets.token_urlsafe(32)
    session_id = f"sess_{uuid4().hex}"
    db.execute(
        text(
            """
            INSERT INTO admin_sessions (
                id, user_id, token_hash, expires_at, revoked_at, last_used_at, created_at, updated_at
            ) VALUES (
                :id, :user_id, :token_hash, :expires_at, NULL, :last_used_at, :created_at, :updated_at
            )
            """
        ),
        {
            "id": session_id,
            "user_id": user["id"],
            "token_hash": token_hash(token),
            "expires_at": expires_at,
            "last_used_at": now,
            "created_at": now,
            "updated_at": now,
        },
    )
    db.execute(
        text("UPDATE admin_users SET last_login_at = :last_login_at, updated_at = :updated_at WHERE id = :id"),
        {"id": user["id"], "last_login_at": now, "updated_at": now},
    )
    db.commit()
    return {"access_token": token, "expires_at": expires_at, "session_id": session_id}


def activate_pending_admin_user(db: Session, user: dict) -> dict:
    now = utc_now()
    before = {key: user.get(key) for key in ("id", "username", "role", "status", "status_before_freeze")}
    db.execute(
        text(
            """
            UPDATE admin_users
            SET status = '正常', status_before_freeze = NULL, updated_at = :updated_at
            WHERE id = :id AND status = '待激活' AND role = '后台管理员'
            """
        ),
        {"id": user["id"], "updated_at": now},
    )
    after = get_user_by_id(db, user["id"]) or user
    audit(
        db,
        actor=user["id"],
        target_id=user["id"],
        action="first_login_activate",
        before=before,
        after={key: after.get(key) for key in ("id", "username", "role", "status", "status_before_freeze")},
        reason="后台管理员首次登录激活",
    )
    return after


def authenticate(db: Session, *, username: str, password: str, remember_me: bool = False) -> tuple[dict, dict]:
    user = get_user_by_username(db, username)
    if user is None or not verify_password(password, user.get("password_hash")):
        raise PermissionError("用户名或密码错误。")
    if user["role"] != "后台管理员":
        raise PermissionError("账号不可用或无后台权限。")
    if user["status"] == "待激活":
        user = activate_pending_admin_user(db, user)
    elif user["status"] != "正常":
        raise PermissionError("账号不可用或无后台权限。")
    session_data = create_session(db, user, remember_me=remember_me)
    refreshed = get_user_by_id(db, user["id"]) or user
    return refreshed, session_data


def revoke_session(db: Session, token: str) -> None:
    now = utc_now()
    db.execute(
        text("UPDATE admin_sessions SET revoked_at = :revoked_at, updated_at = :updated_at WHERE token_hash = :token_hash"),
        {"revoked_at": now, "updated_at": now, "token_hash": token_hash(token)},
    )
    db.commit()


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


def resolve_token(db: Session, token: str) -> dict:
    now = datetime.now(UTC).replace(microsecond=0)
    row = db.execute(
        text(
            """
            SELECT s.id AS session_id, s.expires_at, s.revoked_at,
                   u.id, u.username, u.nickname, u.avatar_url, u.role, u.status,
                   u.status_before_freeze, u.workspace_count, u.last_login_at, u.is_system_superadmin,
                   u.deleted_at, u.session_invalidated_at, u.created_at, u.updated_at
            FROM admin_sessions s
            JOIN admin_users u ON u.id = s.user_id
            WHERE s.token_hash = :token_hash
            """
        ),
        {"token_hash": token_hash(token)},
    ).first()
    if row is None:
        raise PermissionError("未认证或凭证无效。")
    data = row_to_dict(row)
    if data["revoked_at"] or _parse_time(data["expires_at"]) <= now:
        raise PermissionError("登录态已失效。")
    if data["status"] != "正常":
        raise PermissionError("账号不可用。")
    if data["role"] != "后台管理员":
        raise PermissionError("需要后台管理员权限。")
    db.execute(
        text("UPDATE admin_sessions SET last_used_at = :last_used_at, updated_at = :updated_at WHERE id = :id"),
        {"id": data["session_id"], "last_used_at": utc_now(), "updated_at": utc_now()},
    )
    db.commit()
    return data
