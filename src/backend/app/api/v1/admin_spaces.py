from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.admin_auth import require_admin_user
from app.db.session import get_db
from app.repositories import admin_spaces
from app.schemas.admin_spaces import (
    AdminSpaceAction,
    AdminSpaceApplicationCreate,
    AdminSpaceApplicationDecision,
    AdminSpaceApplicationListParams,
    AdminSpaceApplicationRead,
    AdminSpaceAuditRead,
    AdminSpaceCreate,
    AdminSpaceListParams,
    AdminSpaceMemberAction,
    AdminSpaceMemberCreate,
    AdminSpaceMemberRead,
    AdminSpaceMemberUpdate,
    AdminSpaceQuotaUpdate,
    AdminSpaceRead,
    AdminSpaceRenew,
    AdminSpaceTransferOwner,
    AdminSpaceUpdate,
)
from app.schemas.common import ApiResponse, PageResponse

spaces_router = APIRouter(prefix="/api/v1/admin/spaces", tags=["Admin Spaces"])
applications_router = APIRouter(prefix="/api/v1/admin/space-applications", tags=["Admin Space Applications"])


def _handle_error(exc: Exception) -> None:
    if isinstance(exc, LookupError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, PermissionError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    raise exc


@spaces_router.get("", response_model=ApiResponse[PageResponse[AdminSpaceRead]], summary="查询空间列表")
def list_admin_spaces(
    q: str | None = Query(default=None, max_length=64),
    status_value: str | None = Query(default=None, alias="status"),
    source: str | None = Query(default=None),
    usage_status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[PageResponse[AdminSpaceRead]]:
    params = AdminSpaceListParams(q=q, status=status_value, source=source, usage_status=usage_status, page=page, page_size=page_size)  # type: ignore[arg-type]
    items, total = admin_spaces.list_spaces(db, params, actor=actor)
    return ApiResponse(data=PageResponse(items=[AdminSpaceRead(**item) for item in items], total=total, page=page, page_size=page_size))


@spaces_router.post("", response_model=ApiResponse[AdminSpaceRead], status_code=status.HTTP_201_CREATED, summary="创建空间")
def create_admin_space(
    payload: AdminSpaceCreate,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminSpaceRead]:
    try:
        created = admin_spaces.create_space(db, payload, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminSpaceRead(**created))


@spaces_router.get("/{space_id}", response_model=ApiResponse[AdminSpaceRead], summary="查询空间详情")
def get_admin_space(
    space_id: str,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminSpaceRead]:
    space = admin_spaces.get_space(db, space_id, actor=actor)
    if space is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="空间不存在。")
    return ApiResponse(data=AdminSpaceRead(**space))


@spaces_router.put("/{space_id}", response_model=ApiResponse[AdminSpaceRead], summary="编辑空间")
def update_admin_space(
    space_id: str,
    payload: AdminSpaceUpdate,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminSpaceRead]:
    try:
        updated = admin_spaces.update_space(db, space_id, payload, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminSpaceRead(**updated))


@spaces_router.post("/{space_id}/freeze", response_model=ApiResponse[AdminSpaceRead], summary="冻结空间")
def freeze_admin_space(
    space_id: str,
    payload: AdminSpaceAction,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminSpaceRead]:
    try:
        updated = admin_spaces.set_status(db, space_id, status="FROZEN", payload=payload, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminSpaceRead(**updated))


@spaces_router.post("/{space_id}/restore", response_model=ApiResponse[AdminSpaceRead], summary="恢复空间")
def restore_admin_space(
    space_id: str,
    payload: AdminSpaceAction,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminSpaceRead]:
    try:
        updated = admin_spaces.set_status(db, space_id, status="ACTIVE", payload=payload, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminSpaceRead(**updated))


@spaces_router.delete("/{space_id}", response_model=ApiResponse[AdminSpaceRead], summary="移入回收站")
def recycle_admin_space(
    space_id: str,
    payload: AdminSpaceAction,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminSpaceRead]:
    try:
        updated = admin_spaces.set_status(db, space_id, status="RECYCLE", payload=payload, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminSpaceRead(**updated))


@spaces_router.delete("/{space_id}/purge", response_model=ApiResponse[AdminSpaceRead], summary="彻底删除空间")
def purge_admin_space(
    space_id: str,
    payload: AdminSpaceAction,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminSpaceRead]:
    try:
        deleted = admin_spaces.purge_space(db, space_id, payload, actor=actor)
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminSpaceRead(**deleted))


@spaces_router.post("/{space_id}/quota", response_model=ApiResponse[AdminSpaceRead], summary="调整空间配额")
def update_admin_space_quota(
    space_id: str,
    payload: AdminSpaceQuotaUpdate,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminSpaceRead]:
    try:
        updated = admin_spaces.update_quota(db, space_id, payload, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminSpaceRead(**updated))


@spaces_router.post("/{space_id}/renew", response_model=ApiResponse[AdminSpaceRead], summary="续期空间")
def renew_admin_space(
    space_id: str,
    payload: AdminSpaceRenew,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminSpaceRead]:
    try:
        updated = admin_spaces.renew_space(db, space_id, payload, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminSpaceRead(**updated))


@spaces_router.post("/{space_id}/transfer-owner", response_model=ApiResponse[AdminSpaceRead], summary="转移空间负责人")
def transfer_admin_space_owner(
    space_id: str,
    payload: AdminSpaceTransferOwner,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminSpaceRead]:
    try:
        updated = admin_spaces.transfer_owner(db, space_id, payload, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminSpaceRead(**updated))


@spaces_router.get("/{space_id}/members", response_model=ApiResponse[list[AdminSpaceMemberRead]], summary="查询空间成员")
def list_admin_space_members(
    space_id: str,
    db: Session = Depends(get_db),
    _actor: dict = Depends(require_admin_user),
) -> ApiResponse[list[AdminSpaceMemberRead]]:
    try:
        items = admin_spaces.list_members(db, space_id)
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=[AdminSpaceMemberRead(**item) for item in items])


@spaces_router.post("/{space_id}/members", response_model=ApiResponse[AdminSpaceMemberRead], status_code=status.HTTP_201_CREATED, summary="添加空间成员")
def add_admin_space_member(
    space_id: str,
    payload: AdminSpaceMemberCreate,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminSpaceMemberRead]:
    try:
        created = admin_spaces.add_member(db, space_id, payload, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminSpaceMemberRead(**created))


@spaces_router.put("/{space_id}/members/{member_id}", response_model=ApiResponse[AdminSpaceMemberRead], summary="编辑空间成员角色")
def update_admin_space_member(
    space_id: str,
    member_id: str,
    payload: AdminSpaceMemberUpdate,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminSpaceMemberRead]:
    try:
        updated = admin_spaces.update_member(db, space_id, member_id, payload, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminSpaceMemberRead(**updated))


@spaces_router.delete("/{space_id}/members/{member_id}", response_model=ApiResponse[AdminSpaceMemberRead], summary="移除空间成员")
def remove_admin_space_member(
    space_id: str,
    member_id: str,
    payload: AdminSpaceMemberAction,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminSpaceMemberRead]:
    try:
        removed = admin_spaces.remove_member(db, space_id, member_id, reason=payload.reason, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminSpaceMemberRead(**removed))


@spaces_router.get("/{space_id}/audit-events", response_model=ApiResponse[PageResponse[AdminSpaceAuditRead]], summary="查询空间审计日志")
def list_admin_space_audit_events(
    space_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _actor: dict = Depends(require_admin_user),
) -> ApiResponse[PageResponse[AdminSpaceAuditRead]]:
    items, total = admin_spaces.list_audit_events(db, space_id, page=page, page_size=page_size)
    return ApiResponse(data=PageResponse(items=[AdminSpaceAuditRead(**item) for item in items], total=total, page=page, page_size=page_size))


@applications_router.get("", response_model=ApiResponse[PageResponse[AdminSpaceApplicationRead]], summary="查询空间申请")
def list_admin_space_applications(
    q: str | None = Query(default=None, max_length=64),
    status_value: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _actor: dict = Depends(require_admin_user),
) -> ApiResponse[PageResponse[AdminSpaceApplicationRead]]:
    params = AdminSpaceApplicationListParams(q=q, status=status_value, page=page, page_size=page_size)  # type: ignore[arg-type]
    items, total = admin_spaces.list_applications(db, params)
    return ApiResponse(data=PageResponse(items=[AdminSpaceApplicationRead(**item) for item in items], total=total, page=page, page_size=page_size))


@applications_router.post("", response_model=ApiResponse[AdminSpaceApplicationRead], status_code=status.HTTP_201_CREATED, summary="创建空间申请")
def create_admin_space_application(
    payload: AdminSpaceApplicationCreate,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminSpaceApplicationRead]:
    try:
        created = admin_spaces.create_application(db, payload, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminSpaceApplicationRead(**created))


@applications_router.post("/{application_id}/approve", response_model=ApiResponse[AdminSpaceApplicationRead], summary="通过空间申请")
def approve_admin_space_application(
    application_id: str,
    payload: AdminSpaceApplicationDecision,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminSpaceApplicationRead]:
    try:
        decided = admin_spaces.decide_application(db, application_id, payload, actor=actor["id"], approve=True)
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminSpaceApplicationRead(**decided))


@applications_router.post("/{application_id}/reject", response_model=ApiResponse[AdminSpaceApplicationRead], summary="拒绝空间申请")
def reject_admin_space_application(
    application_id: str,
    payload: AdminSpaceApplicationDecision,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminSpaceApplicationRead]:
    try:
        decided = admin_spaces.decide_application(db, application_id, payload, actor=actor["id"], approve=False)
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminSpaceApplicationRead(**decided))
