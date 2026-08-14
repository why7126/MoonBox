from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.admin_auth import require_session_user
from app.schemas.common import ApiResponse
from app.schemas.requirement_center import RequirementCenterContext
from app.services.requirement_center import build_requirement_center_context


router = APIRouter(prefix="/api/v1/requirement-center", tags=["requirement-center"])


@router.get("/context", response_model=ApiResponse[RequirementCenterContext], tags=["Requirement Center"], summary="读取需求中心上下文")
def get_requirement_center_context(
    current_user: dict[str, Any] = Depends(require_session_user),
) -> ApiResponse[RequirementCenterContext]:
    try:
        return ApiResponse(data=build_requirement_center_context(current_user=current_user))
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="需求中心数据源暂不可用",
        ) from exc
