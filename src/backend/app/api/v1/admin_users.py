from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.v1.admin_auth import require_admin_user
from app.core.config import settings
from app.core.object_storage import ObjectStorage, ObjectStorageError, get_object_storage
from app.db.session import get_db
from app.repositories import admin_users
from app.schemas.admin_users import (
    AdminAvatarUploadResult,
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

ALLOWED_AVATAR_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_AVATAR_BYTES = 2 * 1024 * 1024


def _handle_error(exc: Exception) -> None:
    if isinstance(exc, LookupError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, PermissionError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    raise exc


def _avatar_key(filename: str) -> str:
    prefix = settings.object_storage_avatar_prefix.strip("/")
    return f"{prefix}/{filename}"


@router.get("", response_model=ApiResponse[PageResponse[AdminUserRead]])
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


@router.post("", response_model=ApiResponse[AdminUserCreateResult], status_code=status.HTTP_201_CREATED)
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


@router.put("/{user_id}", response_model=ApiResponse[AdminUserRead])
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


@router.post("/{user_id}/freeze", response_model=ApiResponse[AdminUserRead])
def freeze_admin_user(
    user_id: str,
    payload: AdminUserAction,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminUserRead]:
    try:
        updated = admin_users.set_status(db, user_id, status="已冻结", reason=payload.reason, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminUserRead(**updated))


@router.post("/{user_id}/unfreeze", response_model=ApiResponse[AdminUserRead])
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


@router.delete("/{user_id}", response_model=ApiResponse[AdminUserRead])
def delete_admin_user(
    user_id: str,
    payload: AdminUserAction,
    db: Session = Depends(get_db),
    actor: dict = Depends(require_admin_user),
) -> ApiResponse[AdminUserRead]:
    try:
        updated = admin_users.set_status(db, user_id, status="已删除", reason=payload.reason, actor=actor["id"])
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=AdminUserRead(**updated))


@router.post("/{user_id}/reset-password", response_model=ApiResponse[AdminPasswordResetResult])
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


@router.post("/avatar", response_model=ApiResponse[AdminAvatarUploadResult])
async def upload_admin_user_avatar(
    file: UploadFile = File(...),
    _actor: dict = Depends(require_admin_user),
    storage: ObjectStorage = Depends(get_object_storage),
) -> ApiResponse[AdminAvatarUploadResult]:
    suffix = ALLOWED_AVATAR_TYPES.get(file.content_type or "")
    if suffix is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 JPG、PNG、WEBP 头像。")

    content = await file.read()
    if len(content) > MAX_AVATAR_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="头像文件不得超过 2MB。")

    filename = f"{uuid4().hex}{suffix}"
    try:
        storage.put(_avatar_key(filename), content, file.content_type or "application/octet-stream")
    except ObjectStorageError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return ApiResponse(data=AdminAvatarUploadResult(url=f"/api/v1/admin/users/avatar/{filename}", status="done"))


@router.get("/avatar/{filename}")
def read_admin_user_avatar(
    filename: str,
    _actor: dict = Depends(require_admin_user),
    storage: ObjectStorage = Depends(get_object_storage),
) -> Response:
    if "/" in filename or "\\" in filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件名无效。")
    try:
        stored = storage.get(_avatar_key(filename))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="头像不存在。")
    except ObjectStorageError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return Response(content=stored.data, media_type=stored.content_type)
