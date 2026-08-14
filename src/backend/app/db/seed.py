from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.admin_spaces import create_application
from app.repositories.admin_auth import hash_password
from app.schemas.admin_spaces import AdminSpaceApplicationCreate


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


DEMO_SPACE_APPLICATION_USERS = [
    {
        "id": "user_demo_space_applicant",
        "username": "demo_space_applicant",
        "nickname": "演示申请人",
        "avatar_url": None,
    },
    {
        "id": "user_demo_space_owner",
        "username": "demo_space_owner",
        "nickname": "演示负责人",
        "avatar_url": None,
    },
    {
        "id": "user_demo_delivery_owner",
        "username": "demo_delivery_owner",
        "nickname": "交付负责人",
        "avatar_url": None,
    },
]

DEMO_SPACE_APPLICATIONS = [
    {
        "name": "AI 原生软件工厂试点空间",
        "code": "ai-factory-demo",
        "applicant_id": "user_demo_space_applicant",
        "proposed_owner_id": "user_demo_space_owner",
        "product_id": "ai-factory-demo",
        "product_name": "AI 原生软件工厂试点空间",
        "purpose": "用于验证空间申请审批、配额核定和产品绑定流程。",
        "expected_members": 12,
        "requested_storage_gb": 80,
        "requested_ai_tokens": 900000,
        "expires_at": None,
    },
    {
        "name": "增长实验空间",
        "code": "growth-lab-demo",
        "applicant_id": "user_demo_space_applicant",
        "proposed_owner_id": "user_demo_space_owner",
        "product_id": "growth-lab-demo",
        "product_name": "增长实验空间",
        "purpose": "用于演示申请审批通过后自动创建空间和产品绑定。",
        "expected_members": 20,
        "requested_storage_gb": 120,
        "requested_ai_tokens": 1500000,
        "expires_at": "2026-12-31T23:59:59Z",
    },
    {
        "name": "客户交付空间",
        "code": "delivery-space-demo",
        "applicant_id": "user_demo_space_applicant",
        "proposed_owner_id": "user_demo_delivery_owner",
        "product_id": "delivery-space-demo",
        "product_name": "客户交付空间",
        "purpose": "用于验收拒绝申请、审批原因和待审批列表刷新。",
        "expected_members": 8,
        "requested_storage_gb": 60,
        "requested_ai_tokens": 600000,
        "expires_at": None,
    },
]


def _seed_demo_user(session: Session, user: dict[str, str | None]) -> None:
    now = _now()
    exists = session.execute(text("SELECT 1 FROM admin_users WHERE id = :id"), {"id": user["id"]}).first()
    if exists:
        session.execute(
            text(
                """
                UPDATE admin_users
                SET nickname = :nickname, avatar_url = :avatar_url, status = '正常', updated_at = :updated_at
                WHERE id = :id
                """
            ),
            {**user, "updated_at": now},
        )
        return

    session.execute(
        text(
            """
            INSERT INTO admin_users (
                id, username, nickname, avatar_url, role, status, workspace_count,
                status_before_freeze, last_login_at, password_hash, is_system_superadmin, deleted_at, session_invalidated_at,
                created_at, updated_at
            ) VALUES (
                :id, :username, :nickname, :avatar_url, '前台用户', '正常', 0,
                NULL, NULL, NULL, 0, NULL, NULL, :created_at, :updated_at
            )
            """
        ),
        {**user, "created_at": now, "updated_at": now},
    )


def _has_space_or_application(session: Session, code: str) -> bool:
    existing = session.execute(
        text(
            """
            SELECT 1 FROM admin_spaces WHERE code = :code
            UNION ALL
            SELECT 1 FROM admin_space_applications WHERE code = :code
            LIMIT 1
            """
        ),
        {"code": code},
    ).first()
    return existing is not None


def _seed_actor_id(session: Session) -> str:
    row = session.execute(
        text("SELECT id FROM admin_users WHERE is_system_superadmin = 1 ORDER BY created_at ASC LIMIT 1")
    ).first()
    if row:
        return str(row._mapping["id"])
    return "system_demo_seed"


def seed_demo_space_applications(session: Session, *, force: bool = False) -> int:
    """Seed pending space applications for local admin approval demos."""

    if not force and (settings.is_production or not settings.admin_space_application_demo_seed):
        return 0

    for user in DEMO_SPACE_APPLICATION_USERS:
        _seed_demo_user(session, user)
    session.commit()

    actor = _seed_actor_id(session)
    created_count = 0
    for item in DEMO_SPACE_APPLICATIONS:
        if _has_space_or_application(session, str(item["code"])):
            continue
        create_application(session, AdminSpaceApplicationCreate(**item), actor=actor)
        created_count += 1
    return created_count
