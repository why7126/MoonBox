from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.object_storage import ObjectStorage, ObjectStorageError, get_object_storage
from app.db.session import get_db
from app.repositories import admin_auth
from app.schemas.admin_auth import AdminLoginRequest, AdminLoginResult, AdminPasswordChangeRequest, AdminPasswordChangeResult, AdminProfileUpdateRequest, AdminSessionUser
from app.schemas.admin_users import AdminAvatarUploadResult, AdminUserRead
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

ALLOWED_AVATAR_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_AVATAR_BYTES = 2 * 1024 * 1024


def _bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录或凭证缺失。")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录或凭证缺失。")
    return token


def require_session_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict:
    token = _bearer_token(authorization)
    try:
        return admin_auth.resolve_token(db, token)
    except PermissionError as exc:
        message = str(exc)
        code = status.HTTP_403_FORBIDDEN if "权限" in message or "不可用" in message else status.HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=code, detail=message) from exc


def require_admin_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict:
    token = _bearer_token(authorization)
    try:
        return admin_auth.resolve_token(db, token, require_admin=True)
    except PermissionError as exc:
        message = str(exc)
        code = status.HTTP_403_FORBIDDEN if "权限" in message or "不可用" in message else status.HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=code, detail=message) from exc


def _avatar_key(filename: str) -> str:
    prefix = settings.object_storage_avatar_prefix.strip("/")
    return f"{prefix}/{filename}"


@router.post("/login", response_model=ApiResponse[AdminLoginResult], tags=["Auth"], summary="统一账号登录")
def login(
    payload: AdminLoginRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[AdminLoginResult]:
    try:
        user, session_data = admin_auth.authenticate(
            db,
            username=payload.username,
            password=payload.password,
            remember_me=payload.remember_me,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return ApiResponse(
        data=AdminLoginResult(
            access_token=session_data["access_token"],
            expires_at=session_data["expires_at"],
            user=AdminUserRead(**user),
        )
    )


@router.post("/logout", response_model=ApiResponse[dict[str, str]], tags=["Auth"], summary="退出登录并撤销当前会话")
def logout(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_session_user),
) -> ApiResponse[dict[str, str]]:
    token = _bearer_token(authorization)
    admin_auth.revoke_session(db, token)
    return ApiResponse(data={"status": "done"})


@router.get("/me", response_model=ApiResponse[AdminSessionUser], tags=["Auth"], summary="读取当前登录用户")
def read_current_user(
    current_user: dict = Depends(require_session_user),
) -> ApiResponse[AdminSessionUser]:
    return ApiResponse(data=AdminSessionUser(user=AdminUserRead(**current_user)))


@router.patch("/me", response_model=ApiResponse[AdminSessionUser], tags=["Auth"], summary="更新当前登录用户个人资料")
def update_current_user_profile(
    payload: AdminProfileUpdateRequest,
    current_user: dict = Depends(require_session_user),
    db: Session = Depends(get_db),
) -> ApiResponse[AdminSessionUser]:
    try:
        updated = admin_auth.update_own_profile(
            db,
            current_user["id"],
            nickname=payload.nickname,
            avatar_url=payload.avatar_url,
            actor=current_user["id"],
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ApiResponse(data=AdminSessionUser(user=AdminUserRead(**updated)))


@router.post("/change-password", response_model=ApiResponse[AdminPasswordChangeResult], tags=["Auth"], summary="当前登录用户修改密码")
def change_current_user_password(
    payload: AdminPasswordChangeRequest,
    current_user: dict = Depends(require_session_user),
    db: Session = Depends(get_db),
) -> ApiResponse[AdminPasswordChangeResult]:
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="两次输入的新密码不一致。")
    try:
        admin_auth.change_own_password(
            db,
            current_user["id"],
            current_password=payload.current_password,
            new_password=payload.new_password,
            actor=current_user["id"],
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ApiResponse(data=AdminPasswordChangeResult(message="密码已更新，请重新登录。"))


@router.post("/avatar", response_model=ApiResponse[AdminAvatarUploadResult], tags=["Auth"], summary="当前登录用户上传头像")
async def upload_current_user_avatar(
    file: UploadFile = File(...),
    _current_user: dict = Depends(require_session_user),
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
    return ApiResponse(data=AdminAvatarUploadResult(url=f"/api/v1/auth/avatar/{filename}", status="done"))


@router.get("/avatar/{filename}", response_model=None, tags=["Auth"], summary="当前登录用户读取头像")
def read_current_user_avatar(
    filename: str,
    _current_user: dict = Depends(require_session_user),
    storage: ObjectStorage = Depends(get_object_storage),
) -> Response:
    if "/" in filename or "\\" in filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件名无效。")
    try:
        stored = storage.get(_avatar_key(filename))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="头像不存在。") from exc
    except ObjectStorageError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return Response(content=stored.data, media_type=stored.content_type)
