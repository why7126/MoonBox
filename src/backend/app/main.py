from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.admin_auth import router as admin_auth_router
from app.api.v1.admin_spaces import applications_router as admin_space_applications_router
from app.api.v1.admin_spaces import spaces_router as admin_spaces_router
from app.api.v1.admin_users import router as admin_users_router
from app.api.v1.catalog_space_applications import router as catalog_space_applications_router
from app.api.v1.catalog_space_applications import search_router as catalog_workspaces_router
from app.core.config import settings
from app.api.v1.health import router as health_router
from app.api.v1.requirement_center import router as requirement_center_router
from app.db.seed import seed_admin_user, seed_demo_space_applications
from app.db.session import init_database, validate_runtime_database
from app.db.session import get_session_factory


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    validate_runtime_database()
    init_database()
    session = get_session_factory()()
    try:
        seed_admin_user(session)
        seed_demo_space_applications(session)
    finally:
        session.close()
    yield


app = FastAPI(
    title="MoonBox API",
    version="0.1.0",
    description="MoonBox REST API service.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["authorization", "content-type"],
)

app.include_router(health_router)
app.include_router(admin_auth_router)
app.include_router(admin_users_router)
app.include_router(admin_spaces_router)
app.include_router(admin_space_applications_router)
app.include_router(requirement_center_router)
app.include_router(catalog_workspaces_router)
app.include_router(catalog_space_applications_router)
