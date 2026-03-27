from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import Depends, Header, HTTPException, Request, status

from iqmeet_graphrag.config import AppSettings


@dataclass(frozen=True)
class WorkspaceContext:
    workspace_id: str


async def get_settings(request: Request) -> AppSettings:
    settings = getattr(request.app.state, "settings", None)
    if settings is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="settings_unavailable",
        )
    return settings


async def get_runtime(request: Request) -> Any:
    runtime = getattr(request.app.state, "runtime", None)
    if runtime is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="runtime_unavailable",
        )
    return runtime


async def require_api_key(
    x_api_key: str = Header(default="", alias="X-API-Key"),
    settings: AppSettings = Depends(get_settings),
) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_api_key",
        )


async def get_workspace_context(
    x_workspace_id: str = Header(default="", alias="X-Workspace-Id"),
) -> WorkspaceContext:
    if not x_workspace_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="missing_workspace_header",
        )
    return WorkspaceContext(workspace_id=x_workspace_id)
