import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status, Query, Request
from sqlalchemy.orm import Session

from app.api.v1.admin_auth import require_session_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.requirement_center import RequirementCenterContext, RequirementCenterDocumentUpdate, RequirementCenterCaptureCreate, RequirementCenterReadError
from app.chat.api import ChatRoute
from app.governance.scope import authorize, projects
from app.governance.reader import ProjectReader, version
from app.services import requirement_center as legacy


def get_reader(
    request: Request,
    space_id: str = Query(min_length=1, max_length=64),
    repository_id: str = Query(min_length=1, max_length=64),
    current_user: dict[str, Any] = Depends(require_session_user),
    db: Session = Depends(get_db),
):
    actor = str(current_user["id"])
    request.state.chat_actor = actor
    scope = authorize(db, actor, space_id, repository_id, write=request.method != "GET")
    reader = ProjectReader(db, actor, scope)
    reader.request_id = request.state.chat_request_id
    request.state.governance_reader = reader
    return reader



router = APIRouter(prefix="/api/v1/requirement-center", tags=["requirement-center"], route_class=ChatRoute, responses={503: {"model": RequirementCenterReadError}})
logger = logging.getLogger("moonbox.requirement_center")


@router.get("/projects", response_model=ApiResponse[dict[str, Any]], summary="读取授权项目与账号目录")
def get_projects(request: Request, current_user: dict[str, Any] = Depends(require_session_user), db: Session = Depends(get_db)):
    request.state.chat_actor = str(current_user["id"])
    return ApiResponse(data={"projects": projects(db, str(current_user["id"])),
        "current_user": legacy._context_user(current_user),
        "workspaces": legacy._load_workspaces([], current_user, db)})


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
    reader: ProjectReader = Depends(get_reader),
    current_user: dict[str, Any] = Depends(require_session_user),
    db: Session = Depends(get_db),
) -> ApiResponse[RequirementCenterContext]:
    try:
        return ApiResponse(data=reader.call("build_requirement_center_context", current_user=current_user, db=db))
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
    reader: ProjectReader = Depends(get_reader),
    current_user: dict[str, Any] = Depends(require_session_user),
) -> ApiResponse[dict[str, str]]:
    try:
        content, suffix = reader.call("read_requirement_center_document", issue_id, document_name)
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
    return ApiResponse(data={"name": document_name, "content": content, "version": version(content)})


@router.put(
    "/issues/{issue_id}/documents/{document_name}",
    response_model=ApiResponse[dict],
    status_code=202,
    tags=["Requirement Center"],
    summary="保存需求中心 Markdown 文档",
)
def update_requirement_center_document(
    issue_id: str,
    document_name: str,
    payload: RequirementCenterDocumentUpdate,
    reader: ProjectReader = Depends(get_reader),
    current_user: dict[str, Any] = Depends(require_session_user),
) -> ApiResponse[dict[str, str]]:
    from app.governance.writer import enqueue_document
    result = enqueue_document(reader, "update_requirement_center_document", issue_id, document_name,
        payload.content, payload.expected_version, payload.idempotency_key, task_toggle=False, request_id=reader.request_id)
    return ApiResponse(data=result)


@router.get(
    "/changes/{change_id}/documents/{document_name}",
    response_model=ApiResponse[dict[str, str]],
    tags=["Requirement Center"],
    summary="读取需求中心 OpenSpec Change Markdown 文档",
)
def get_requirement_center_change_document(
    change_id: str,
    document_name: str,
    reader: ProjectReader = Depends(get_reader),
    current_user: dict[str, Any] = Depends(require_session_user),
) -> ApiResponse[dict[str, str]]:
    try:
        content, suffix = reader.call("read_requirement_center_change_document", change_id, document_name)
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
    return ApiResponse(data={"name": document_name, "content": content, "version": version(content)})


@router.put(
    "/changes/{change_id}/documents/{document_name}",
    response_model=ApiResponse[dict],
    status_code=202,
    tags=["Requirement Center"],
    summary="保存需求中心 OpenSpec Change Markdown 文档",
)
def put_requirement_center_change_document(
    change_id: str,
    document_name: str,
    payload: RequirementCenterDocumentUpdate,
    reader: ProjectReader = Depends(get_reader),
    current_user: dict[str, Any] = Depends(require_session_user),
) -> ApiResponse[dict[str, str]]:
    from app.governance.writer import enqueue_document
    result = enqueue_document(reader, "update_requirement_center_change_document", change_id, document_name,
        payload.content, payload.expected_version, payload.idempotency_key, task_toggle=False, request_id=reader.request_id)
    return ApiResponse(data=result)


@router.put(
    "/changes/{change_id}/documents/{document_name}/tasks",
    response_model=ApiResponse[dict],
    status_code=202,
    tags=["Requirement Center"],
    summary="保存验收中 tasks.md 勾选状态",
)
def toggle_requirement_center_change_tasks(
    change_id: str,
    document_name: str,
    payload: RequirementCenterDocumentUpdate,
    reader: ProjectReader = Depends(get_reader),
    current_user: dict[str, Any] = Depends(require_session_user),
) -> ApiResponse[dict[str, str]]:
    from app.governance.writer import enqueue_document
    result = enqueue_document(reader, "update_requirement_center_change_document", change_id, document_name,
        payload.content, payload.expected_version, payload.idempotency_key, task_toggle=True, request_id=reader.request_id)
    return ApiResponse(data=result)


@router.get(
    "/issues/{issue_id}/documents/{document_name:path}/preview",
    response_model=None,
    tags=["Requirement Center"],
    summary="预览需求中心 HTML 文档",
)
def preview_requirement_center_document(
    issue_id: str,
    document_name: str,
    reader: ProjectReader = Depends(get_reader),
    current_user: dict[str, Any] = Depends(require_session_user),
) -> Response:
    try:
        content, suffix = reader.call("read_requirement_center_document", issue_id, document_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在或已移动") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权读取该文档") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 Markdown 或 HTML 文档") from exc
    if suffix != ".html":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该入口仅支持 HTML 文档")
    return Response(content=content, media_type="text/html; charset=utf-8")




@router.post("/captures", response_model=ApiResponse[dict[str, Any]], status_code=202, summary="创建持久化 Capture")
def create_capture(payload: RequirementCenterCaptureCreate, request: Request, reader: ProjectReader = Depends(get_reader)):
    from app.governance.writer import enqueue
    values = payload.model_dump(exclude={"idempotency_key"})
    record = {"kind": "capture", "payload": values, "before": {}, "after": {}}
    return ApiResponse(data=enqueue(reader.db, reader.actor, reader.scope, payload.idempotency_key,
                                   {"kind": "capture", **values}, record, request_id=request.state.chat_request_id))


@router.get("/capture-readiness", response_model=ApiResponse[dict[str, Any]], summary="读取Capture写入就绪状态")
def capture_readiness(reader: ProjectReader = Depends(get_reader)):
    from app.governance.readiness import status
    return ApiResponse(data=status(reader.db, reader.scope))
