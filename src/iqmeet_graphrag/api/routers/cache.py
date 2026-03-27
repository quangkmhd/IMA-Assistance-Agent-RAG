from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends
from starlette.concurrency import run_in_threadpool

from iqmeet_graphrag.api.dependencies import get_runtime, require_api_key
from iqmeet_graphrag.api.models import SuccessEnvelope, WorkspaceCacheInvalidateRequest

router = APIRouter(
    prefix="/cache",
    tags=["cache"],
    dependencies=[Depends(require_api_key)],
)


@router.post("/invalidate-workspace", response_model=SuccessEnvelope)
async def invalidate_workspace_cache(
    payload: WorkspaceCacheInvalidateRequest,
    runtime=Depends(get_runtime),
) -> SuccessEnvelope:
    await run_in_threadpool(
        runtime.service.invalidate_workspace_cache, payload.workspace_id
    )
    return SuccessEnvelope(
        data={"workspace_id": payload.workspace_id, "invalidated": True},
        trace_id=f"trc_{uuid4().hex}",
    )
