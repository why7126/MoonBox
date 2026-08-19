from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.repositories.admin_users import normalize_avatar_url, utc_now
from app.schemas.admin_spaces import (
    AdminSpaceAction,
    AdminSpaceApplicationCreate,
    AdminSpaceApplicationDecision,
    AdminSpaceApplicationListParams,
    AdminSpaceCreate,
    AdminSpaceListParams,
    AdminSpaceMemberCreate,
    AdminSpaceMemberUpdate,
    AdminSpaceQuotaUpdate,
    AdminSpaceRenew,
    AdminSpaceTransferOwner,
    AdminSpaceUpdate,
)


def _row_to_dict(row) -> dict:  # type: ignore[no-untyped-def]
    data = dict(row._mapping)
    for key in ("protected",):
        if key in data:
            data[key] = bool(data[key])
    if "storage_used_gb" in data:
        data["storage_used_gb"] = float(data["storage_used_gb"] or 0)
    if "storage_quota_gb" in data:
        data["storage_quota_gb"] = float(data["storage_quota_gb"] or 0)
    for key in ("avatar_url", "owner_avatar_url"):
        if key in data:
            data[key] = normalize_avatar_url(data.get(key))
    return data


def _json(data: dict | None) -> str | None:
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def _allowed_actions(space: dict, *, actor: dict | None = None) -> list[str]:
    if space["status"] == "ACTIVE":
        actions = ["VIEW", "EDIT", "FREEZE", "DELETE", "QUOTA", "RENEW", "TRANSFER_OWNER"]
    elif space["status"] == "FROZEN":
        actions = ["VIEW", "RESTORE", "QUOTA", "RENEW"]
    else:
        actions = ["VIEW", "RESTORE", "PURGE"]
    if space.get("protected"):
        actions = [item for item in actions if item not in {"FREEZE", "DELETE", "PURGE"}]
    if actor and not actor.get("is_system_superadmin"):
        actions = [item for item in actions if item != "PURGE"]
    return actions


def _hydrate_space(row: dict, *, actor: dict | None = None) -> dict:
    row["allowed_actions"] = _allowed_actions(row, actor=actor)
    return row


def _space_select() -> str:
    return """
        SELECT s.id, s.name, s.code, s.description, s.owner_id,
               COALESCE(u.nickname, u.username) AS owner_name, u.role AS owner_role,
               u.avatar_url AS owner_avatar_url,
               s.status, s.source, s.member_count, s.member_quota,
               s.storage_used_gb, s.storage_quota_gb, s.ai_used_tokens, s.ai_quota_tokens,
               p.product_id, p.product_name,
               s.expiry_type, s.expires_at, s.protected, s.deleted_at,
               s.deleted_by, COALESCE(deleter.nickname, deleter.username) AS deleted_by_name,
               s.delete_reason, s.purge_at,
               s.created_at, s.updated_at
        FROM admin_spaces s
        JOIN admin_space_products p ON p.space_id = s.id
        LEFT JOIN admin_users u ON u.id = s.owner_id
        LEFT JOIN admin_users deleter ON deleter.id = s.deleted_by
    """


def _audit(
    db: Session,
    *,
    actor: str,
    space_id: str,
    action: str,
    before: dict | None,
    after: dict | None,
    reason: str,
    result: str = "success",
) -> None:
    db.execute(
        text(
            """
            INSERT INTO admin_space_audit_events (
                id, space_id, actor, action, before_value, after_value,
                reason, result, request_id, created_at
            ) VALUES (
                :id, :space_id, :actor, :action, :before_value, :after_value,
                :reason, :result, :request_id, :created_at
            )
            """
        ),
        {
            "id": f"space_audit_{uuid4().hex}",
            "space_id": space_id,
            "actor": actor,
            "action": action,
            "before_value": _json(before),
            "after_value": _json(after),
            "reason": reason,
            "result": result,
            "request_id": f"req_{uuid4().hex[:12]}",
            "created_at": utc_now(),
        },
    )


def _ensure_owner(db: Session, owner_id: str) -> dict:
    row = db.execute(
        text("SELECT id, username, nickname, role, status FROM admin_users WHERE id = :id AND status != '已删除'"),
        {"id": owner_id},
    ).first()
    if row is None:
        raise LookupError("空间负责人不存在。")
    return _row_to_dict(row)


def _ensure_normal_user(db: Session, user_id: str) -> dict:
    row = db.execute(
        text("SELECT id, username, nickname, avatar_url, role, status FROM admin_users WHERE id = :id AND status = '正常'"),
        {"id": user_id},
    ).first()
    if row is None:
        raise LookupError("成员用户不存在或状态非正常。")
    return _row_to_dict(row)


def _ensure_code_available(db: Session, code: str, *, ignore_id: str | None = None) -> None:
    filters = "code = :code"
    values: dict[str, object] = {"code": code}
    if ignore_id:
        filters += " AND id != :ignore_id"
        values["ignore_id"] = ignore_id
    if db.execute(text(f"SELECT 1 FROM admin_spaces WHERE {filters}"), values).first():
        raise ValueError("空间编码已存在。")


def get_space(db: Session, space_id: str, *, actor: dict | None = None) -> dict | None:
    row = db.execute(text(f"{_space_select()} WHERE s.id = :id"), {"id": space_id}).first()
    return _hydrate_space(_row_to_dict(row), actor=actor) if row else None


def list_spaces(db: Session, params: AdminSpaceListParams, *, actor: dict | None = None) -> tuple[list[dict], int]:
    filters: list[str] = []
    values: dict[str, object] = {"limit": params.page_size, "offset": (params.page - 1) * params.page_size}
    if params.q:
        filters.append("(LOWER(s.name) LIKE :query OR LOWER(s.code) LIKE :query OR LOWER(COALESCE(u.nickname, u.username, '')) LIKE :query)")
        values["query"] = f"%{params.q.lower()}%"
    if params.status:
        filters.append("s.status = :status")
        values["status"] = params.status
    else:
        filters.append("s.status != 'RECYCLE'")
    if params.source:
        filters.append("s.source = :source")
        values["source"] = params.source
    if params.usage_status == "over_quota":
        filters.append("(s.member_count > s.member_quota OR s.storage_used_gb > s.storage_quota_gb OR s.ai_used_tokens > s.ai_quota_tokens)")
    elif params.usage_status == "normal":
        filters.append("(s.member_count <= s.member_quota AND s.storage_used_gb <= s.storage_quota_gb AND s.ai_used_tokens <= s.ai_quota_tokens)")
    where = f"WHERE {' AND '.join(filters)}" if filters else ""
    total = db.execute(
        text(
            f"""
            SELECT COUNT(*)
            FROM admin_spaces s
            JOIN admin_space_products p ON p.space_id = s.id
            LEFT JOIN admin_users u ON u.id = s.owner_id
            {where}
            """
        ),
        values,
    ).scalar_one()
    rows = db.execute(
        text(
            f"""
            {_space_select()}
            {where}
            ORDER BY s.created_at DESC
            LIMIT :limit OFFSET :offset
            """
        ),
        values,
    ).all()
    return [_hydrate_space(_row_to_dict(row), actor=actor) for row in rows], int(total)


def create_space(db: Session, payload: AdminSpaceCreate, *, actor: str, source: str = "后台创建") -> dict:
    _ensure_owner(db, payload.owner_id)
    _ensure_code_available(db, payload.code)
    now = utc_now()
    space_id = f"space_{uuid4().hex}"
    db.execute(
        text(
            """
            INSERT INTO admin_spaces (
                id, name, code, description, owner_id, status, source, member_count,
                member_quota, storage_used_gb, storage_quota_gb, ai_used_tokens, ai_quota_tokens,
                expiry_type, expires_at, protected, deleted_at, deleted_by, delete_reason, purge_at,
                created_at, updated_at
            ) VALUES (
                :id, :name, :code, :description, :owner_id, 'ACTIVE', :source, 1,
                :member_quota, 0, :storage_quota_gb, 0, :ai_quota_tokens,
                :expiry_type, :expires_at, 0, NULL, NULL, NULL, NULL,
                :created_at, :updated_at
            )
            """
        ),
        {
            "id": space_id,
            "name": payload.name,
            "code": payload.code,
            "description": payload.description,
            "owner_id": payload.owner_id,
            "source": source,
            "member_quota": payload.member_quota,
            "storage_quota_gb": payload.storage_quota_gb,
            "ai_quota_tokens": payload.ai_quota_tokens,
            "expiry_type": payload.expiry_type,
            "expires_at": payload.expires_at,
            "created_at": now,
            "updated_at": now,
        },
    )
    db.execute(
        text(
            """
            INSERT INTO admin_space_products (
                id, space_id, product_id, product_name, immutable_binding, created_at, updated_at
            ) VALUES (
                :id, :space_id, :product_id, :product_name, 1, :created_at, :updated_at
            )
            """
        ),
        {
            "id": f"space_product_{uuid4().hex}",
            "space_id": space_id,
            "product_id": payload.product_id,
            "product_name": payload.product_name,
            "created_at": now,
            "updated_at": now,
        },
    )
    after = get_space(db, space_id)
    _audit(db, actor=actor, space_id=space_id, action="create_space", before=None, after=after, reason="后台创建空间")
    db.commit()
    return after or {}


def list_members(db: Session, space_id: str) -> list[dict]:
    space = get_space(db, space_id)
    if space is None:
        raise LookupError("空间不存在。")
    rows = db.execute(
        text(
            """
            SELECT m.id, m.space_id, m.user_id,
                   COALESCE(u.nickname, u.username) AS user_name,
                   u.username, u.avatar_url, m.role, u.status AS user_status,
                   m.created_at AS joined_at, m.updated_at
            FROM admin_space_members m
            JOIN admin_users u ON u.id = m.user_id
            JOIN admin_spaces s ON s.id = m.space_id
            WHERE m.space_id = :space_id AND m.user_id != s.owner_id
            ORDER BY CASE m.role
                WHEN '管理员' THEN 1
                WHEN '编辑者' THEN 2
                WHEN '查看者' THEN 3
                ELSE 9
            END, m.created_at DESC
            """
        ),
        {"space_id": space_id},
    ).all()
    return [_row_to_dict(row) for row in rows]


def add_member(db: Session, space_id: str, payload: AdminSpaceMemberCreate, *, actor: str) -> dict:
    space = get_space(db, space_id)
    if space is None:
        raise LookupError("空间不存在。")
    if space["status"] == "RECYCLE":
        raise PermissionError("回收站空间不可添加成员。")
    if payload.user_id == space["owner_id"]:
        raise PermissionError("负责人不在成员列表中维护。")
    _ensure_normal_user(db, payload.user_id)
    if space["member_count"] >= space["member_quota"]:
        raise PermissionError("成员数量已达到上限。")
    now = utc_now()
    member_id = f"space_member_{uuid4().hex}"
    try:
        db.execute(
            text(
                """
                INSERT INTO admin_space_members (
                    id, space_id, user_id, role, created_at, updated_at
                ) VALUES (
                    :id, :space_id, :user_id, :role, :created_at, :updated_at
                )
                """
            ),
            {
                "id": member_id,
                "space_id": space_id,
                "user_id": payload.user_id,
                "role": payload.role,
                "created_at": now,
                "updated_at": now,
            },
        )
    except Exception as exc:
        raise ValueError("用户已是空间成员。") from exc
    db.execute(text("UPDATE admin_spaces SET member_count = member_count + 1, updated_at = :updated_at WHERE id = :id"), {"id": space_id, "updated_at": now})
    after = [item for item in list_members(db, space_id) if item["id"] == member_id][0]
    _audit(db, actor=actor, space_id=space_id, action="add_member", before=None, after=after, reason="后台添加空间成员")
    db.commit()
    return after


def update_member(db: Session, space_id: str, member_id: str, payload: AdminSpaceMemberUpdate, *, actor: str) -> dict:
    before_row = db.execute(text("SELECT * FROM admin_space_members WHERE id = :id AND space_id = :space_id"), {"id": member_id, "space_id": space_id}).first()
    if before_row is None:
        raise LookupError("空间成员不存在。")
    before = _row_to_dict(before_row)
    space = get_space(db, space_id)
    if space is None:
        raise LookupError("空间不存在。")
    if before["user_id"] == space["owner_id"]:
        raise PermissionError("负责人角色需通过负责人变更流程维护。")
    db.execute(
        text("UPDATE admin_space_members SET role = :role, updated_at = :updated_at WHERE id = :id"),
        {"id": member_id, "role": payload.role, "updated_at": utc_now()},
    )
    after = [item for item in list_members(db, space_id) if item["id"] == member_id][0]
    _audit(db, actor=actor, space_id=space_id, action="update_member_role", before=before, after=after, reason="后台编辑空间成员角色")
    db.commit()
    return after


def remove_member(db: Session, space_id: str, member_id: str, *, reason: str, actor: str) -> dict:
    before_row = db.execute(text("SELECT * FROM admin_space_members WHERE id = :id AND space_id = :space_id"), {"id": member_id, "space_id": space_id}).first()
    if before_row is None:
        raise LookupError("空间成员不存在。")
    before = _row_to_dict(before_row)
    space = get_space(db, space_id)
    if space is None:
        raise LookupError("空间不存在。")
    if before["user_id"] == space["owner_id"]:
        raise PermissionError("负责人不可在成员列表中移除。")
    removed = [item for item in list_members(db, space_id) if item["id"] == member_id][0]
    db.execute(text("DELETE FROM admin_space_members WHERE id = :id"), {"id": member_id})
    db.execute(
        text("UPDATE admin_spaces SET member_count = 1 + (SELECT COUNT(*) FROM admin_space_members WHERE space_id = :id), updated_at = :updated_at WHERE id = :id"),
        {"id": space_id, "updated_at": utc_now()},
    )
    _audit(db, actor=actor, space_id=space_id, action="remove_member", before=before, after=None, reason=reason)
    db.commit()
    return removed


def update_space(db: Session, space_id: str, payload: AdminSpaceUpdate, *, actor: str) -> dict:
    before = get_space(db, space_id)
    if before is None:
        raise LookupError("空间不存在。")
    if before["status"] == "RECYCLE":
        raise PermissionError("回收站空间不可编辑。")
    now = utc_now()
    db.execute(
        text(
            """
            UPDATE admin_spaces
            SET name = :name, description = :description, expiry_type = :expiry_type,
                expires_at = :expires_at, updated_at = :updated_at
            WHERE id = :id
            """
        ),
        {
            "id": space_id,
            "name": payload.name,
            "description": payload.description,
            "expiry_type": payload.expiry_type,
            "expires_at": payload.expires_at,
            "updated_at": now,
        },
    )
    after = get_space(db, space_id)
    _audit(db, actor=actor, space_id=space_id, action="update_space", before=before, after=after, reason="后台编辑空间")
    db.commit()
    return after or {}


def set_status(db: Session, space_id: str, *, status: str, payload: AdminSpaceAction, actor: str) -> dict:
    before = get_space(db, space_id)
    if before is None:
        raise LookupError("空间不存在。")
    if before.get("protected"):
        raise PermissionError("受保护空间不可执行该操作。")
    now = utc_now()
    values: dict[str, object] = {"id": space_id, "status": status, "updated_at": now}
    if status == "FROZEN":
        if before["status"] != "ACTIVE":
            raise PermissionError("仅正常空间可冻结。")
        statement = "UPDATE admin_spaces SET status = :status, freeze_reason = :reason, updated_at = :updated_at WHERE id = :id"
        values["reason"] = payload.reason
    elif status == "ACTIVE":
        if before["status"] not in {"FROZEN", "RECYCLE"}:
            raise PermissionError("当前状态不可恢复。")
        statement = """
            UPDATE admin_spaces
            SET status = :status, freeze_reason = NULL, deleted_at = NULL, deleted_by = NULL,
                delete_reason = NULL, purge_at = NULL, updated_at = :updated_at
            WHERE id = :id
        """
    elif status == "RECYCLE":
        if before["status"] != "ACTIVE":
            raise PermissionError("仅正常空间可移入回收站。")
        blockers = list_runtime_blockers(db, space_id)
        if blockers:
            raise PermissionError("空间存在运行中的任务，暂不可删除。")
        purge_at = (datetime.now(UTC) + timedelta(days=30)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        statement = """
            UPDATE admin_spaces
            SET status = :status, deleted_at = :deleted_at, deleted_by = :deleted_by,
                delete_reason = :reason, purge_at = :purge_at, updated_at = :updated_at
            WHERE id = :id
        """
        values.update({"deleted_at": now, "deleted_by": actor, "reason": payload.reason, "purge_at": purge_at})
    else:
        raise ValueError("不支持的空间状态。")
    db.execute(text(statement), values)
    after = get_space(db, space_id)
    _audit(db, actor=actor, space_id=space_id, action=f"set_status:{status}", before=before, after=after, reason=payload.reason)
    db.commit()
    return after or {}


def list_runtime_blockers(_db: Session, _space_id: str) -> list[str]:
    return []


def update_quota(db: Session, space_id: str, payload: AdminSpaceQuotaUpdate, *, actor: str) -> dict:
    before = get_space(db, space_id)
    if before is None:
        raise LookupError("空间不存在。")
    db.execute(
        text(
            """
            UPDATE admin_spaces
            SET member_quota = :member_quota, storage_quota_gb = :storage_quota_gb,
                ai_quota_tokens = :ai_quota_tokens, updated_at = :updated_at
            WHERE id = :id
            """
        ),
        {
            "id": space_id,
            "member_quota": payload.member_quota,
            "storage_quota_gb": payload.storage_quota_gb,
            "ai_quota_tokens": payload.ai_quota_tokens,
            "updated_at": utc_now(),
        },
    )
    after = get_space(db, space_id)
    _audit(db, actor=actor, space_id=space_id, action="update_quota", before=before, after=after, reason=payload.reason)
    db.commit()
    return after or {}


def renew_space(db: Session, space_id: str, payload: AdminSpaceRenew, *, actor: str) -> dict:
    before = get_space(db, space_id)
    if before is None:
        raise LookupError("空间不存在。")
    db.execute(
        text(
            """
            UPDATE admin_spaces
            SET expiry_type = :expiry_type, expires_at = :expires_at, updated_at = :updated_at
            WHERE id = :id
            """
        ),
        {"id": space_id, "expiry_type": payload.expiry_type, "expires_at": payload.expires_at, "updated_at": utc_now()},
    )
    after = get_space(db, space_id)
    _audit(db, actor=actor, space_id=space_id, action="renew_space", before=before, after=after, reason=payload.reason)
    db.commit()
    return after or {}


def transfer_owner(db: Session, space_id: str, payload: AdminSpaceTransferOwner, *, actor: str) -> dict:
    before = get_space(db, space_id)
    if before is None:
        raise LookupError("空间不存在。")
    _ensure_owner(db, payload.owner_id)
    db.execute(text("DELETE FROM admin_space_members WHERE space_id = :space_id AND user_id = :user_id"), {"space_id": space_id, "user_id": payload.owner_id})
    db.execute(
        text("UPDATE admin_spaces SET member_count = 1 + (SELECT COUNT(*) FROM admin_space_members WHERE space_id = :space_id) WHERE id = :space_id"),
        {"space_id": space_id},
    )
    db.execute(
        text("UPDATE admin_spaces SET owner_id = :owner_id, updated_at = :updated_at WHERE id = :id"),
        {"id": space_id, "owner_id": payload.owner_id, "updated_at": utc_now()},
    )
    after = get_space(db, space_id)
    _audit(db, actor=actor, space_id=space_id, action="transfer_owner", before=before, after=after, reason=payload.reason)
    db.commit()
    return after or {}


def purge_space(db: Session, space_id: str, payload: AdminSpaceAction, *, actor: dict) -> dict:
    before = get_space(db, space_id, actor=actor)
    if before is None:
        raise LookupError("空间不存在。")
    if not actor.get("is_system_superadmin"):
        raise PermissionError("仅系统超级管理员可彻底删除空间。")
    if before["status"] != "RECYCLE":
        raise PermissionError("仅回收站空间可彻底删除。")
    if before.get("protected"):
        raise PermissionError("受保护空间不可彻底删除。")
    _audit(db, actor=actor["id"], space_id=space_id, action="purge_space", before=before, after={"id": space_id, "purged": True}, reason=payload.reason)
    db.execute(text("DELETE FROM admin_space_members WHERE space_id = :id"), {"id": space_id})
    db.execute(text("DELETE FROM admin_space_products WHERE space_id = :id"), {"id": space_id})
    db.execute(text("DELETE FROM admin_spaces WHERE id = :id"), {"id": space_id})
    db.commit()
    return before


def list_applications(db: Session, params: AdminSpaceApplicationListParams) -> tuple[list[dict], int]:
    filters: list[str] = []
    values: dict[str, object] = {"limit": params.page_size, "offset": (params.page - 1) * params.page_size}
    if params.q:
        filters.append("(LOWER(a.name) LIKE :query OR LOWER(a.code) LIKE :query OR LOWER(COALESCE(applicant.nickname, applicant.username, '')) LIKE :query)")
        values["query"] = f"%{params.q.lower()}%"
    if params.status:
        filters.append("a.status = :status")
        values["status"] = params.status
    else:
        filters.append("a.status = '待审批'")
    where = f"WHERE {' AND '.join(filters)}" if filters else ""
    total = db.execute(text(f"SELECT COUNT(*) FROM admin_space_applications a LEFT JOIN admin_users applicant ON applicant.id = a.applicant_id {where}"), values).scalar_one()
    rows = db.execute(
        text(
            f"""
            SELECT a.*, COALESCE(applicant.nickname, applicant.username) AS applicant_name,
                   COALESCE(owner.nickname, owner.username) AS proposed_owner_name,
                   target.name AS target_space_name
            FROM admin_space_applications a
            LEFT JOIN admin_users applicant ON applicant.id = a.applicant_id
            LEFT JOIN admin_users owner ON owner.id = a.proposed_owner_id
            LEFT JOIN admin_spaces target ON target.id = a.target_space_id
            {where}
            ORDER BY a.created_at DESC
            LIMIT :limit OFFSET :offset
            """
        ),
        values,
    ).all()
    return [_row_to_dict(row) for row in rows], int(total)


def create_application(db: Session, payload: AdminSpaceApplicationCreate, *, actor: str) -> dict:
    _ensure_owner(db, payload.applicant_id)
    _ensure_owner(db, payload.proposed_owner_id)
    _ensure_code_available(db, payload.code)
    now = utc_now()
    application_id = f"space_app_{uuid4().hex}"
    db.execute(
        text(
            """
            INSERT INTO admin_space_applications (
                id, application_type, target_space_id, name, code, applicant_id, proposed_owner_id, product_id, product_name,
                purpose, expected_members, requested_storage_gb, requested_ai_tokens, expires_at,
                status, decision_reason, decision_by, decision_at, created_at, updated_at
            ) VALUES (
                :id, 'create', NULL, :name, :code, :applicant_id, :proposed_owner_id, :product_id, :product_name,
                :purpose, :expected_members, :requested_storage_gb, :requested_ai_tokens, :expires_at,
                '待审批', NULL, NULL, NULL, :created_at, :updated_at
            )
            """
        ),
        {
            "id": application_id,
            **payload.model_dump(),
            "created_at": now,
            "updated_at": now,
        },
    )
    _audit(db, actor=actor, space_id=application_id, action="create_application", before=None, after=payload.model_dump(), reason="提交空间申请")
    db.commit()
    return get_application(db, application_id) or {}


def get_application(db: Session, application_id: str) -> dict | None:
    row = db.execute(
        text(
            """
            SELECT a.*, COALESCE(applicant.nickname, applicant.username) AS applicant_name,
                   COALESCE(owner.nickname, owner.username) AS proposed_owner_name,
                   target.name AS target_space_name
            FROM admin_space_applications a
            LEFT JOIN admin_users applicant ON applicant.id = a.applicant_id
            LEFT JOIN admin_users owner ON owner.id = a.proposed_owner_id
            LEFT JOIN admin_spaces target ON target.id = a.target_space_id
            WHERE a.id = :id
            """
        ),
        {"id": application_id},
    ).first()
    return _row_to_dict(row) if row else None


def exact_search_workspace(db: Session, query: str, *, user_id: str) -> dict | None:
    value = query.strip()
    row = db.execute(
        text(
            f"""
            {_space_select()}
            WHERE s.code = :query OR s.name = :query
            ORDER BY CASE WHEN s.code = :query THEN 0 ELSE 1 END, s.created_at DESC
            LIMIT 2
            """
        ),
        {"query": value},
    ).all()
    if len(row) != 1:
        return None
    workspace = _hydrate_space(_row_to_dict(row[0]))
    membership = db.execute(
        text("SELECT id FROM admin_space_members WHERE space_id = :space_id AND user_id = :user_id"),
        {"space_id": workspace["id"], "user_id": user_id},
    ).first()
    is_owner = workspace["owner_id"] == user_id
    workspace["can_apply"] = workspace["status"] == "ACTIVE" and not membership and not is_owner and workspace["member_count"] < workspace["member_quota"]
    if workspace["status"] != "ACTIVE":
        workspace["apply_block_reason"] = "空间当前不可加入。"
    elif membership or is_owner:
        workspace["apply_block_reason"] = "你已在该空间中。"
    elif workspace["member_count"] >= workspace["member_quota"]:
        workspace["apply_block_reason"] = "空间成员已满。"
    else:
        workspace["apply_block_reason"] = None
    return workspace


def create_catalog_application(db: Session, payload, *, actor: dict) -> dict:  # type: ignore[no-untyped-def]
    admin_payload = AdminSpaceApplicationCreate(
        name=payload.name,
        code=payload.code,
        applicant_id=actor["id"],
        proposed_owner_id=actor["id"],
        product_id=payload.code,
        product_name=payload.name,
        purpose=payload.purpose,
        expected_members=payload.expected_members,
        requested_storage_gb=payload.requested_storage_gb,
        requested_ai_tokens=payload.requested_ai_tokens,
        expires_at=None,
    )
    return create_application(db, admin_payload, actor=actor["id"])


def create_catalog_space(db: Session, payload, *, actor: dict) -> dict:  # type: ignore[no-untyped-def]
    create_payload = AdminSpaceCreate(
        name=payload.name,
        code=payload.code,
        description=payload.description,
        owner_id=actor["id"],
        product_id=payload.code,
        product_name=payload.name,
        member_quota=payload.member_quota,
        storage_quota_gb=payload.storage_quota_gb,
        ai_quota_tokens=payload.ai_quota_tokens,
        expiry_type=payload.expiry_type,
        expires_at=payload.expires_at,
    )
    return create_space(db, create_payload, actor=actor["id"], source="后台创建")


def create_catalog_space_application(db: Session, payload, *, actor: dict) -> dict:  # type: ignore[no-untyped-def]
    application_payload = AdminSpaceApplicationCreate(
        name=payload.name,
        code=payload.code,
        applicant_id=actor["id"],
        proposed_owner_id=actor["id"],
        product_id=payload.code,
        product_name=payload.name,
        purpose=payload.description or f"申请创建空间：{payload.name}",
        expected_members=payload.member_quota,
        requested_storage_gb=payload.storage_quota_gb,
        requested_ai_tokens=payload.ai_quota_tokens,
        expires_at=payload.expires_at,
    )
    return create_application(db, application_payload, actor=actor["id"])


def join_catalog_application(db: Session, payload, *, actor: dict) -> dict:  # type: ignore[no-untyped-def]
    space = get_space(db, payload.workspace_id)
    if space is None:
        raise LookupError("空间不存在。")
    searched = exact_search_workspace(db, space["code"], user_id=actor["id"])
    if not searched or not searched["can_apply"]:
        raise PermissionError(searched.get("apply_block_reason") if searched else "空间当前不可加入。")
    existing = db.execute(
        text(
            """
            SELECT id FROM admin_space_applications
            WHERE applicant_id = :applicant_id AND target_space_id = :target_space_id AND status = '待审批'
            """
        ),
        {"applicant_id": actor["id"], "target_space_id": payload.workspace_id},
    ).first()
    if existing:
        raise ValueError("你已有待审批的加入申请。")
    now = utc_now()
    application_id = f"space_app_{uuid4().hex}"
    db.execute(
        text(
            """
            INSERT INTO admin_space_applications (
                id, application_type, target_space_id, name, code, applicant_id, proposed_owner_id,
                product_id, product_name, purpose, expected_members, requested_storage_gb,
                requested_ai_tokens, expires_at, status, decision_reason, decision_by, decision_at,
                created_at, updated_at
            ) VALUES (
                :id, 'join', :target_space_id, :name, :code, :applicant_id, :proposed_owner_id,
                :product_id, :product_name, :purpose, :expected_members, :requested_storage_gb,
                :requested_ai_tokens, NULL, '待审批', NULL, NULL, NULL, :created_at, :updated_at
            )
            """
        ),
        {
            "id": application_id,
            "target_space_id": payload.workspace_id,
            "name": space["name"],
            "code": space["code"],
            "applicant_id": actor["id"],
            "proposed_owner_id": space["owner_id"],
            "product_id": space["product_id"],
            "product_name": space["product_name"],
            "purpose": payload.reason,
            "expected_members": space["member_count"] + 1,
            "requested_storage_gb": space["storage_quota_gb"],
            "requested_ai_tokens": space["ai_quota_tokens"],
            "created_at": now,
            "updated_at": now,
        },
    )
    _audit(db, actor=actor["id"], space_id=application_id, action="join_application", before=None, after={"target_space_id": payload.workspace_id}, reason=payload.reason)
    db.commit()
    return get_application(db, application_id) or {}


def list_my_applications(db: Session, *, actor: dict) -> list[dict]:
    rows = db.execute(
        text(
            """
            SELECT a.*, target.name AS target_space_name
            FROM admin_space_applications a
            LEFT JOIN admin_spaces target ON target.id = a.target_space_id
            WHERE a.applicant_id = :applicant_id
            ORDER BY a.created_at DESC
            """
        ),
        {"applicant_id": actor["id"]},
    ).all()
    return [_row_to_dict(row) for row in rows]


def withdraw_my_application(db: Session, application_id: str, *, actor: dict, reason: str | None = None) -> dict:
    before = get_application(db, application_id)
    if before is None or before["applicant_id"] != actor["id"]:
        raise LookupError("空间申请不存在。")
    if before["status"] != "待审批":
        raise PermissionError("仅待审批申请可撤回。")
    now = utc_now()
    db.execute(
        text("UPDATE admin_space_applications SET status = '已撤回', decision_reason = :reason, updated_at = :updated_at WHERE id = :id"),
        {"id": application_id, "reason": reason or "申请人撤回", "updated_at": now},
    )
    after = get_application(db, application_id)
    _audit(db, actor=actor["id"], space_id=application_id, action="withdraw_application", before=before, after=after, reason=reason or "申请人撤回")
    db.commit()
    return after or {}


def resubmit_my_application(db: Session, application_id: str, *, actor: dict) -> dict:
    before = get_application(db, application_id)
    if before is None or before["applicant_id"] != actor["id"]:
        raise LookupError("空间申请不存在。")
    if before["status"] not in {"已拒绝", "已撤回"}:
        raise PermissionError("仅已拒绝或已撤回申请可重新提交。")
    if before.get("application_type") == "join":
        class Payload:
            workspace_id = before["target_space_id"]
            reason = before["purpose"]

        return join_catalog_application(db, Payload(), actor=actor)
    payload = AdminSpaceApplicationCreate(
        name=before["name"],
        code=before["code"],
        applicant_id=actor["id"],
        proposed_owner_id=actor["id"],
        product_id=before["product_id"],
        product_name=before["product_name"],
        purpose=before["purpose"],
        expected_members=before["expected_members"],
        requested_storage_gb=before["requested_storage_gb"],
        requested_ai_tokens=before["requested_ai_tokens"],
        expires_at=before.get("expires_at"),
    )
    return create_application(db, payload, actor=actor["id"])


def decide_application(db: Session, application_id: str, payload: AdminSpaceApplicationDecision, *, actor: str, approve: bool) -> dict:
    before = get_application(db, application_id)
    if before is None:
        raise LookupError("空间申请不存在。")
    if before["status"] != "待审批":
        raise PermissionError("仅待审批申请可处理。")
    now = utc_now()
    new_status = "已通过" if approve else "已拒绝"
    db.execute(
        text(
            """
            UPDATE admin_space_applications
            SET status = :status, decision_reason = :reason, decision_by = :decision_by,
                decision_at = :decision_at, updated_at = :updated_at
            WHERE id = :id
            """
        ),
        {"id": application_id, "status": new_status, "reason": payload.reason, "decision_by": actor, "decision_at": now, "updated_at": now},
    )
    if approve and before.get("application_type", "create") == "join":
        add_member(
            db,
            before["target_space_id"],
            AdminSpaceMemberCreate(user_id=before["applicant_id"], role="查看者"),
            actor=actor,
        )
        target = get_space(db, before["target_space_id"])
        _audit(
            db,
            actor=actor,
            space_id=before["target_space_id"],
            action="application_approved_join_space",
            before=before,
            after=target,
            reason=payload.reason,
        )
    elif approve:
        create_payload = AdminSpaceCreate(
            name=before["name"],
            code=before["code"],
            description=before["purpose"],
            owner_id=before["proposed_owner_id"],
            product_id=before["product_id"],
            product_name=before["product_name"],
            member_quota=before["expected_members"],
            storage_quota_gb=before["requested_storage_gb"],
            ai_quota_tokens=before["requested_ai_tokens"],
            expiry_type="long_term" if before.get("expires_at") is None else "fixed_date",
            expires_at=before.get("expires_at"),
        )
        created_space = create_space(db, create_payload, actor=actor, source="申请审批")
        _audit(
            db,
            actor=actor,
            space_id=created_space["id"],
            action="application_approved_create_space",
            before=before,
            after=created_space,
            reason=payload.reason,
        )
    after = get_application(db, application_id)
    _audit(db, actor=actor, space_id=application_id, action=f"application:{new_status}", before=before, after=after, reason=payload.reason)
    db.commit()
    return after or {}


def list_audit_events(db: Session, space_id: str, *, page: int = 1, page_size: int = 10) -> tuple[list[dict], int]:
    total = db.execute(
        text("SELECT COUNT(*) FROM admin_space_audit_events WHERE space_id = :space_id"),
        {"space_id": space_id},
    ).scalar_one()
    offset = (page - 1) * page_size
    rows = db.execute(
        text(
            """
            SELECT e.id, e.space_id, e.actor,
                   COALESCE(u.nickname, u.username, e.actor) AS actor_display_name,
                   e.action, e.before_value, e.after_value,
                   e.reason, e.result, e.request_id, e.created_at
            FROM admin_space_audit_events e
            LEFT JOIN admin_users u ON u.id = e.actor
            WHERE e.space_id = :space_id
            ORDER BY e.created_at DESC
            LIMIT :limit OFFSET :offset
            """
        ),
        {"space_id": space_id, "limit": page_size, "offset": offset},
    ).all()
    return [_row_to_dict(row) for row in rows], total
