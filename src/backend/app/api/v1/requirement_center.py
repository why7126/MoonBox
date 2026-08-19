from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.v1.admin_auth import require_session_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.requirement_center import RequirementCenterContext, RequirementCenterDocumentUpdate
from app.services.requirement_center import (
    build_requirement_center_context,
    read_requirement_center_document,
    update_requirement_center_capture_document,
)


router = APIRouter(prefix="/api/v1/requirement-center", tags=["requirement-center"])


@router.get("/context", response_model=ApiResponse[RequirementCenterContext], tags=["Requirement Center"], summary="读取需求中心上下文")
def get_requirement_center_context(
    current_user: dict[str, Any] = Depends(require_session_user),
    db: Session = Depends(get_db),
) -> ApiResponse[RequirementCenterContext]:
    try:
        return ApiResponse(data=build_requirement_center_context(current_user=current_user, db=db))
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="需求中心数据源暂不可用",
        ) from exc


@router.get(
    "/issues/{issue_id}/documents/{document_name}",
    response_model=ApiResponse[dict[str, str]],
    tags=["Requirement Center"],
    summary="读取需求中心 Markdown 文档",
)
def get_requirement_center_document(
    issue_id: str,
    document_name: str,
    current_user: dict[str, Any] = Depends(require_session_user),
) -> ApiResponse[dict[str, str]]:
    try:
        content, suffix = read_requirement_center_document(issue_id, document_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在或已移动") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权读取该文档") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 Markdown 或 HTML 文档") from exc
    if suffix != ".md":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该入口仅支持 Markdown 文档")
    return ApiResponse(data={"name": document_name, "content": content})


@router.put(
    "/issues/{issue_id}/documents/{document_name}",
    response_model=ApiResponse[dict[str, str]],
    tags=["Requirement Center"],
    summary="保存采集池 capture.md 文档",
)
def update_requirement_center_document(
    issue_id: str,
    document_name: str,
    payload: RequirementCenterDocumentUpdate,
    current_user: dict[str, Any] = Depends(require_session_user),
) -> ApiResponse[dict[str, str]]:
    try:
        content = update_requirement_center_capture_document(issue_id, document_name, payload.content)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在或已移动") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅采集池 capture.md 支持编辑") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 Markdown 文档") from exc
    return ApiResponse(data={"name": document_name, "content": content})


@router.get(
    "/issues/{issue_id}/documents/{document_name}/preview",
    response_model=None,
    tags=["Requirement Center"],
    summary="预览需求中心 HTML 文档",
)
def preview_requirement_center_document(
    issue_id: str,
    document_name: str,
    current_user: dict[str, Any] = Depends(require_session_user),
) -> Response:
    try:
        content, suffix = read_requirement_center_document(issue_id, document_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在或已移动") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权读取该文档") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 Markdown 或 HTML 文档") from exc
    if suffix != ".html":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该入口仅支持 HTML 文档")
    return Response(content=content, media_type="text/html; charset=utf-8")
