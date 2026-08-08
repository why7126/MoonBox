from fastapi import APIRouter

from app.schemas.common import ApiResponse

router = APIRouter(tags=["System"])


@router.get(
    "/health",
    response_model=ApiResponse[dict[str, str]],
    tags=["System"],
    summary="Health check",
)
async def health_check() -> ApiResponse[dict[str, str]]:
    return ApiResponse(data={"status": "ok"})
