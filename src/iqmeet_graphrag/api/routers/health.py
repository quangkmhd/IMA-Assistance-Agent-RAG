from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends
from starlette.concurrency import run_in_threadpool

from iqmeet_graphrag.api.dependencies import get_runtime
from iqmeet_graphrag.api.models import SuccessEnvelope

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=SuccessEnvelope)
async def liveness() -> SuccessEnvelope:
    return SuccessEnvelope(data={"status": "ok"}, trace_id=f"trc_{uuid4().hex}")


@router.get("/ready", response_model=SuccessEnvelope)
async def readiness(runtime=Depends(get_runtime)) -> SuccessEnvelope:
    _ = await run_in_threadpool(lambda: runtime)
    return SuccessEnvelope(data={"status": "ready"}, trace_id=f"trc_{uuid4().hex}")
