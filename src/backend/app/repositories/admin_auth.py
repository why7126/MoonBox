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


def can_access_admin(user: dict) -> bool:
    return user.get("role") == "后台管理员"


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


def activate_pending_user(db: Session, user: dict) -> dict:
    now = utc_now()
    before = {key: user.get(key) for key in ("id", "username", "role", "status", "status_before_freeze")}
    db.execute(
        text(
            """
            UPDATE admin_users
            SET status = '正常', status_before_freeze = NULL, updated_at = :updated_at
            WHERE id = :id AND status = '待激活'
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
        reason="用户首次登录激活",
    )
    return after


def authenticate(db: Session, *, username: str, password: str, remember_me: bool = False) -> tuple[dict, dict]:
    user = get_user_by_username(db, username)
    if user is None or not verify_password(password, user.get("password_hash")):
        raise PermissionError("用户名或密码错误。")
    if user["status"] == "待激活":
        user = activate_pending_user(db, user)
    elif user["status"] != "正常":
        raise PermissionError("账号不可用。")
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


def validate_new_password(new_password: str, *, current_password: str) -> None:
    normalized = new_password.strip()
    weak_values = {
        "",
        "password",
        "admin",
        "admin123",
        "123456",
        "change-me-on-first-run",
        "example-test-password",
    }
    if normalized.lower() in weak_values or len(new_password) < 12:
        raise ValueError("新密码不符合安全规则。")
    if new_password == current_password:
        raise ValueError("新密码不能与当前密码相同。")
    has_letter = any(char.isalpha() for char in new_password)
    has_digit = any(char.isdigit() for char in new_password)
    has_symbol = any(not char.isalnum() for char in new_password)
    if not (has_letter and has_digit and has_symbol):
        raise ValueError("新密码需包含字母、数字和符号。")


def change_own_password(db: Session, user_id: str, *, current_password: str, new_password: str, actor: str) -> None:
    user = get_user_by_id(db, user_id)
    if user is None or user.get("status") != "正常":
        raise PermissionError("账号不可用。")
    if not verify_password(current_password, user.get("password_hash")):
        raise PermissionError("当前密码错误。")
    validate_new_password(new_password, current_password=current_password)
    now = utc_now()
    before = {"id": user_id, "username": user.get("username"), "password_changed": False}
    db.execute(
        text("UPDATE admin_users SET password_hash = :password_hash, updated_at = :updated_at WHERE id = :id"),
        {"id": user_id, "password_hash": hash_password(new_password), "updated_at": now},
    )
    audit(
        db,
        actor=actor,
        target_id=user_id,
        action="change_own_password",
        before=before,
        after={"id": user_id, "username": user.get("username"), "password_changed": True, "sessions_revoked": "all"},
        reason="后台用户自助修改密码",
    )
    revoke_user_sessions(db, user_id)
    db.commit()


def update_own_profile(db: Session, user_id: str, *, nickname: str | None, avatar_url: str | None, actor: str) -> dict:
    user = get_user_by_id(db, user_id)
    if user is None or user.get("status") != "正常":
        raise PermissionError("账号不可用。")

    cleaned_nickname = nickname.strip() if nickname is not None else None
    if cleaned_nickname == "":
        cleaned_nickname = None
    if cleaned_nickname is not None and len(cleaned_nickname) > 128:
        raise ValueError("昵称不得超过 128 个字符。")
    if avatar_url is not None:
        cleaned_avatar_url = avatar_url.strip()
        if cleaned_avatar_url == "":
            cleaned_avatar_url = None
    else:
        cleaned_avatar_url = None
    if cleaned_avatar_url is not None and cleaned_avatar_url.lower().startswith("blob:"):
        raise ValueError("头像地址必须为持久可访问 URL。")
    if cleaned_avatar_url is not None and len(cleaned_avatar_url) > 512:
        raise ValueError("头像地址过长。")

    now = utc_now()
    before = {key: user.get(key) for key in ("id", "username", "nickname", "avatar_url")}
    db.execute(
        text(
            """
            UPDATE admin_users
            SET nickname = :nickname, avatar_url = :avatar_url, updated_at = :updated_at
            WHERE id = :id
            """
        ),
        {"id": user_id, "nickname": cleaned_nickname, "avatar_url": cleaned_avatar_url, "updated_at": now},
    )
    updated = get_user_by_id(db, user_id)
    audit(
        db,
        actor=actor,
        target_id=user_id,
        action="update_own_profile",
        before=before,
        after={key: (updated or {}).get(key) for key in ("id", "username", "nickname", "avatar_url")},
        reason="当前用户自助修改个人资料",
    )
    db.commit()
    return updated or {}


def resolve_token(db: Session, token: str, *, require_admin: bool = False) -> dict:
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
    if require_admin and not can_access_admin(data):
        raise PermissionError("需要后台管理员权限。")
    db.execute(
        text("UPDATE admin_sessions SET last_used_at = :last_used_at, updated_at = :updated_at WHERE id = :id"),
        {"id": data["session_id"], "last_used_at": utc_now(), "updated_at": utc_now()},
    )
    db.commit()
    return data
