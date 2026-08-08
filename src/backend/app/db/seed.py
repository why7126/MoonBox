from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.admin_auth import hash_password


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def seed_admin_user(session: Session) -> None:
    """Seed the deployment-level superadmin used by admin user management."""

    settings.validate_admin_initial_password()
    exists = session.execute(
        text("SELECT id, password_hash FROM admin_users WHERE is_system_superadmin = 1 LIMIT 1")
    ).first()
    if exists:
        row = dict(exists._mapping)
        if not row.get("password_hash"):
            session.execute(
                text("UPDATE admin_users SET password_hash = :password_hash, updated_at = :updated_at WHERE id = :id"),
                {"id": row["id"], "password_hash": hash_password(settings.admin_initial_password), "updated_at": _now()},
            )
            session.commit()
        return

    now = _now()
    username = settings.admin_username
    password_hash = hash_password(settings.admin_initial_password)
    session.execute(
        text(
            """
            INSERT INTO admin_users (
                id, username, nickname, avatar_url, role, status, workspace_count,
                status_before_freeze, last_login_at, password_hash, is_system_superadmin, deleted_at, session_invalidated_at,
                created_at, updated_at
            ) VALUES (
                :id, :username, '平台超级管理员', NULL, '后台管理员', '正常', 0,
                NULL, NULL, :password_hash, 1, NULL, NULL, :created_at, :updated_at
            )
            """
        ),
        {"id": f"user_{uuid4().hex}", "username": username, "password_hash": password_hash, "created_at": now, "updated_at": now},
    )
    session.commit()
