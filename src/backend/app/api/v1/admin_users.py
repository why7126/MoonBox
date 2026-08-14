from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.admin_auth import require_admin_user
from app.db.session import get_db
from app.repositories import admin_users
from app.schemas.admin_users import (
    AdminPasswordResetResult,
    AdminUserAction,
    AdminUserCreate,
    AdminUserCreateResult,
    AdminUserListParams,
    AdminUserRead,
    AdminUserUpdate,
)
from app.schemas.common import ApiResponse, PageResponse

router = APIRouter(prefix="/api/v1/admin/users", tags=["Admin Users"])


def _handle_error(exc: Exception) -> None:
    if isinstance(exc, LookupError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, PermissionError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    raise exc


def _ensure_not_self_target(user_id: str, actor: dict, action: str) -> None:
    if actor["id"] == user_id:
        raise PermissionError(f"不能{action}当前登录账号。")


@router.get("", response_model=ApiResponse[PageResponse[AdminUserRead]], tags=["Admin Users"], summary="查询后台用户列表")
def list_admin_users(
    q: str | None = Query(default=None, max_length=64),
    role: str | None = Query(default=None),
    status_value: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _actor: dict = Depends(require_admin_user),
) -> ApiResponse[PageResponse[AdminUserRead]]:
    params = AdminUserListParams(q=q, role=role, status=status_value, page=page, page_size=page_size)  # type: ignore[arg-type]
    items, total = admin_users.list_users(db, params)
    return ApiResponse(data=PageResponse(items=[AdminUserRead(**item) for item in items], total=total, page=page, page_size=page_size))


@router.post("", response_model=ApiResponse[AdminUserCreateResult], status_code=status.HTTP_201_CREATED, tags=["Admin Users"], summary="创建后台用户")
def create_admin_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminUserCreateResult]:
    try:
        created, temporary_password = admin_users.create_user(db, payload, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminUserCreateResult(user=AdminUserRead(**created), temporary_password=temporary_password, message="临时密码仅展示一次。"))


@router.put("/{user_id}", response_model=ApiResponse[AdminUserRead], tags=["Admin Users"], summary="更新后台用户")
def update_admin_user(
    user_id: str,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminUserRead]:
    try:
        updated = admin_users.update_user(db, user_id, payload, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminUserRead(**updated))


@router.post("/{user_id}/freeze", response_model=ApiResponse[AdminUserRead], tags=["Admin Users"], summary="冻结后台用户")
def freeze_admin_user(
    user_id: str,
    payload: AdminUserAction,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminUserRead]:
    try:
        _ensure_not_self_target(user_id, actor, "冻结")
        updated = admin_users.set_status(db, user_id, status="已冻结", reason=payload.reason, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminUserRead(**updated))


@router.post("/{user_id}/unfreeze", response_model=ApiResponse[AdminUserRead], tags=["Admin Users"], summary="解冻后台用户")
def unfreeze_admin_user(
    user_id: str,
    payload: AdminUserAction,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminUserRead]:
    try:
        updated = admin_users.set_status(db, user_id, status="正常", reason=payload.reason, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminUserRead(**updated))


@router.delete("/{user_id}", response_model=ApiResponse[AdminUserRead], tags=["Admin Users"], summary="删除后台用户")
def delete_admin_user(
    user_id: str,
    payload: AdminUserAction,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminUserRead]:
    try:
        _ensure_not_self_target(user_id, actor, "删除")
        updated = admin_users.set_status(db, user_id, status="已删除", reason=payload.reason, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminUserRead(**updated))


@router.post("/{user_id}/reset-password", response_model=ApiResponse[AdminPasswordResetResult], tags=["Admin Users"], summary="重置后台用户密码")
def reset_admin_user_password(
    user_id: str,
    payload: AdminUserAction,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminPasswordResetResult]:
    try:
        temporary_password = admin_users.reset_password(db, user_id, reason=payload.reason, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminPasswordResetResult(temporary_password=temporary_password, message="临时密码仅展示一次。"))
