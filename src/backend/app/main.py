from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.admin_auth import router as admin_auth_router
from app.api.v1.admin_users import router as admin_users_router
from app.core.config import settings
from app.api.v1.health import router as health_router
from app.db.seed import seed_admin_user
from app.db.session import init_database, validate_runtime_database
from app.db.session import get_session_factory


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    validate_runtime_database()
    init_database()
    session = get_session_factory()()
    try:
        seed_admin_user(session)
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
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["authorization", "content-type"],
)

app.include_router(health_router)
app.include_router(admin_auth_router)
app.include_router(admin_users_router)
