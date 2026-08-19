from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.admin_auth import require_session_user
from app.db.session import get_db
from app.repositories import admin_spaces
from app.schemas.catalog_space_applications import (
    CatalogSpaceCreateApplication,
    CatalogSpaceCreateResult,
)
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/api/v1/catalog/workspace-applications", tags=["Catalog Workspace Applications"])
search_router = APIRouter(prefix="/api/v1/catalog/workspaces", tags=["Catalog Workspaces"])


def _handle_error(exc: Exception) -> None:
    if isinstance(exc, LookupError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, PermissionError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    raise exc


@router.post("/create", response_model=ApiResponse[CatalogSpaceCreateResult], status_code=status.HTTP_201_CREATED, summary="创建空间")
def create_workspace_application(
    payload: CatalogSpaceCreateApplication,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_session_user),
) -> ApiResponse[CatalogSpaceCreateResult]:
    try:
        created = admin_spaces.create_catalog_space_application(db, payload, actor=current_user)
    except Exception as exc:
        _handle_error(exc)
    return ApiResponse(data=CatalogSpaceCreateResult(application=created))
