import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.v1.admin_auth import require_session_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.requirement_center import RequirementCenterContext, RequirementCenterDocumentUpdate
from app.services.requirement_center import (
    build_requirement_center_context,
    read_requirement_center_change_document,
    read_requirement_center_document,
    update_requirement_center_change_document,
    update_requirement_center_document as save_requirement_center_document,
)


router = APIRouter(prefix="/api/v1/requirement-center", tags=["requirement-center"])
logger = logging.getLogger("moonbox.requirement_center")


def _log_document_operation(
    *,
    event: str,
    object_id: str,
    document_name: str,
    operation: str,
    result: str,
    error_code: str = "",
    reason: str = "",
) -> None:
    logger.info(
        event,
        extra={
            "requirement_center_document_operation": {
                "object_id": object_id,
                "document_name": document_name,
                "operation": operation,
                "result": result,
                "error_code": error_code,
                "reason": reason,
            }
        },
    )


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
        _log_document_operation(event="requirement_center.document.reject", object_id=issue_id, document_name=document_name, operation="read", result="rejected", error_code="not_found", reason="文档不存在或已移动")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在或已移动") from exc
    except PermissionError as exc:
        _log_document_operation(event="requirement_center.document.reject", object_id=issue_id, document_name=document_name, operation="read", result="rejected", error_code="forbidden", reason="无权读取该文档")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权读取该文档") from exc
    except ValueError as exc:
        _log_document_operation(event="requirement_center.document.reject", object_id=issue_id, document_name=document_name, operation="read", result="rejected", error_code="unsupported_type", reason="仅支持 Markdown 或 HTML 文档")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 Markdown 或 HTML 文档") from exc
    if suffix != ".md":
        _log_document_operation(event="requirement_center.document.reject", object_id=issue_id, document_name=document_name, operation="read", result="rejected", error_code="unsupported_type", reason="该入口仅支持 Markdown 文档")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该入口仅支持 Markdown 文档")
    _log_document_operation(event="requirement_center.document.open", object_id=issue_id, document_name=document_name, operation="read", result="allowed")
    return ApiResponse(data={"name": document_name, "content": content})


@router.put(
    "/issues/{issue_id}/documents/{document_name}",
    response_model=ApiResponse[dict[str, str]],
    tags=["Requirement Center"],
    summary="保存需求中心 Markdown 文档",
)
def update_requirement_center_document(
    issue_id: str,
    document_name: str,
    payload: RequirementCenterDocumentUpdate,
    current_user: dict[str, Any] = Depends(require_session_user),
) -> ApiResponse[dict[str, str]]:
    try:
        content = save_requirement_center_document(issue_id, document_name, payload.content)
    except FileNotFoundError as exc:
        _log_document_operation(event="requirement_center.document.reject", object_id=issue_id, document_name=document_name, operation="save", result="rejected", error_code="not_found", reason="文档不存在或已移动")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在或已移动") from exc
    except PermissionError as exc:
        reason = str(exc) or "当前阶段不允许人工编辑该文档"
        _log_document_operation(event="requirement_center.document.reject", object_id=issue_id, document_name=document_name, operation="save", result="rejected", error_code="forbidden", reason=reason)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=reason) from exc
    except ValueError as exc:
        _log_document_operation(event="requirement_center.document.reject", object_id=issue_id, document_name=document_name, operation="save", result="rejected", error_code="unsupported_type", reason="仅支持 Markdown 文档")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 Markdown 文档") from exc
    except OSError as exc:
        _log_document_operation(event="requirement_center.document.reject", object_id=issue_id, document_name=document_name, operation="save", result="failed", error_code="filesystem_unavailable", reason="文档保存失败，治理目录暂不可写")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="文档保存失败，治理目录暂不可写") from exc
    _log_document_operation(event="requirement_center.document.save", object_id=issue_id, document_name=document_name, operation="save", result="allowed")
    return ApiResponse(data={"name": document_name, "content": content})


@router.get(
    "/changes/{change_id}/documents/{document_name}",
    response_model=ApiResponse[dict[str, str]],
    tags=["Requirement Center"],
    summary="读取需求中心 OpenSpec Change Markdown 文档",
)
def get_requirement_center_change_document(
    change_id: str,
    document_name: str,
    current_user: dict[str, Any] = Depends(require_session_user),
) -> ApiResponse[dict[str, str]]:
    try:
        content, suffix = read_requirement_center_change_document(change_id, document_name)
    except FileNotFoundError as exc:
        _log_document_operation(event="requirement_center.document.reject", object_id=change_id, document_name=document_name, operation="read", result="rejected", error_code="not_found", reason="文档不存在或已移动")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在或已移动") from exc
    except PermissionError as exc:
        reason = str(exc) or "无权读取该文档"
        _log_document_operation(event="requirement_center.document.reject", object_id=change_id, document_name=document_name, operation="read", result="rejected", error_code="forbidden", reason=reason)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=reason) from exc
    except ValueError as exc:
        _log_document_operation(event="requirement_center.document.reject", object_id=change_id, document_name=document_name, operation="read", result="rejected", error_code="unsupported_type", reason="仅支持 Markdown 文档")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 Markdown 文档") from exc
    if suffix != ".md":
        _log_document_operation(event="requirement_center.document.reject", object_id=change_id, document_name=document_name, operation="read", result="rejected", error_code="unsupported_type", reason="该入口仅支持 Markdown 文档")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该入口仅支持 Markdown 文档")
    _log_document_operation(event="requirement_center.document.open", object_id=change_id, document_name=document_name, operation="read", result="allowed")
    return ApiResponse(data={"name": document_name, "content": content})


@router.put(
    "/changes/{change_id}/documents/{document_name}",
    response_model=ApiResponse[dict[str, str]],
    tags=["Requirement Center"],
    summary="保存需求中心 OpenSpec Change Markdown 文档",
)
def put_requirement_center_change_document(
    change_id: str,
    document_name: str,
    payload: RequirementCenterDocumentUpdate,
    current_user: dict[str, Any] = Depends(require_session_user),
) -> ApiResponse[dict[str, str]]:
    try:
        content = update_requirement_center_change_document(change_id, document_name, payload.content)
    except FileNotFoundError as exc:
        _log_document_operation(event="requirement_center.document.reject", object_id=change_id, document_name=document_name, operation="save", result="rejected", error_code="not_found", reason="文档不存在或已移动")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在或已移动") from exc
    except PermissionError as exc:
        reason = str(exc) or "当前阶段不允许人工编辑该文档"
        _log_document_operation(event="requirement_center.document.reject", object_id=change_id, document_name=document_name, operation="save", result="rejected", error_code="forbidden", reason=reason)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=reason) from exc
    except OSError as exc:
        _log_document_operation(event="requirement_center.document.reject", object_id=change_id, document_name=document_name, operation="save", result="failed", error_code="filesystem_unavailable", reason="文档保存失败，治理目录暂不可写")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="文档保存失败，治理目录暂不可写") from exc
    _log_document_operation(event="requirement_center.document.save", object_id=change_id, document_name=document_name, operation="save", result="allowed")
    return ApiResponse(data={"name": document_name, "content": content})


@router.put(
    "/changes/{change_id}/documents/{document_name}/tasks",
    response_model=ApiResponse[dict[str, str]],
    tags=["Requirement Center"],
    summary="保存验收中 tasks.md 勾选状态",
)
def toggle_requirement_center_change_tasks(
    change_id: str,
    document_name: str,
    payload: RequirementCenterDocumentUpdate,
    current_user: dict[str, Any] = Depends(require_session_user),
) -> ApiResponse[dict[str, str]]:
    try:
        content = update_requirement_center_change_document(change_id, document_name, payload.content, task_toggle=True)
    except FileNotFoundError as exc:
        _log_document_operation(event="requirement_center.document.reject", object_id=change_id, document_name=document_name, operation="task_toggle", result="rejected", error_code="not_found", reason="文档不存在或已移动")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在或已移动") from exc
    except PermissionError as exc:
        reason = str(exc) or "验收中 tasks.md 仅允许切换任务勾选状态"
        _log_document_operation(event="requirement_center.document.reject", object_id=change_id, document_name=document_name, operation="task_toggle", result="rejected", error_code="forbidden", reason=reason)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=reason) from exc
    except OSError as exc:
        _log_document_operation(event="requirement_center.document.reject", object_id=change_id, document_name=document_name, operation="task_toggle", result="failed", error_code="filesystem_unavailable", reason="文档保存失败，治理目录暂不可写")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="文档保存失败，治理目录暂不可写") from exc
    _log_document_operation(event="requirement_center.document.task_toggle", object_id=change_id, document_name=document_name, operation="task_toggle", result="allowed")
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
