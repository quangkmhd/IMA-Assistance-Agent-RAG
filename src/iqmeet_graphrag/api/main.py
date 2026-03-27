from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from iqmeet_graphrag.api.errors import register_exception_handlers
from iqmeet_graphrag.api.routers import (
    admin_router,
    cache_router,
    events_router,
    health_router,
    ingestion_router,
    meetings_router,
    query_router,
)
from iqmeet_graphrag.config import AppSettings


def create_app(
    settings: AppSettings | None = None,
    runtime: Any | None = None,
) -> FastAPI:
    app_settings = settings or AppSettings()

    @asynccontextmanager
    async def app_lifespan(app: FastAPI):
        app.state.settings = app_settings
        if runtime is not None:
            app.state.runtime = runtime
        else:
            from iqmeet_graphrag.runtime import build_runtime

            app.state.runtime = build_runtime(
                settings=app_settings,
                allowed_workspaces=app_settings.allowed_workspaces,
            )
        yield

    app = FastAPI(
        title="IQMeet Agentic Temporal GraphRAG API",
        description="Production-style API for meeting ingestion and agentic temporal GraphRAG querying.",
        version="1.0.0",
        lifespan=app_lifespan,
    )
    app.state.settings = app_settings
    if runtime is not None:
        app.state.runtime = runtime
    register_exception_handlers(app)

    app.include_router(health_router, prefix=app_settings.api_prefix)
    app.include_router(query_router, prefix=app_settings.api_prefix)
    app.include_router(ingestion_router, prefix=app_settings.api_prefix)
    app.include_router(meetings_router, prefix=app_settings.api_prefix)
    app.include_router(events_router, prefix=app_settings.api_prefix)
    app.include_router(cache_router, prefix=app_settings.api_prefix)
    app.include_router(admin_router, prefix=app_settings.api_prefix)
    return app


app = create_app()
