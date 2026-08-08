from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import admin_auth
from app.schemas.admin_auth import AdminLoginRequest, AdminLoginResult, AdminSessionUser
from app.schemas.admin_users import AdminUserRead
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/api/v1/admin/auth", tags=["Admin Auth"])


def _bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录或凭证缺失。")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录或凭证缺失。")
    return token


def require_admin_user(
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


@router.post("/login", response_model=ApiResponse[AdminLoginResult])
def login_admin(
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


@router.post("/logout", response_model=ApiResponse[dict[str, str]])
def logout_admin(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_admin_user),
) -> ApiResponse[dict[str, str]]:
    token = _bearer_token(authorization)
    admin_auth.revoke_session(db, token)
    return ApiResponse(data={"status": "done"})


@router.get("/me", response_model=ApiResponse[AdminSessionUser])
def read_current_admin(
    current_user: dict = Depends(require_admin_user),
) -> ApiResponse[AdminSessionUser]:
    return ApiResponse(data=AdminSessionUser(user=AdminUserRead(**current_user)))
