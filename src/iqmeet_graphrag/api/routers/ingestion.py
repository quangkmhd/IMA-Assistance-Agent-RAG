from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from starlette.concurrency import run_in_threadpool

from iqmeet_graphrag.api.dependencies import get_runtime, require_api_key
from iqmeet_graphrag.api.models import (
    IngestMeetingRequest,
    IngestionStats,
    SuccessEnvelope,
)

router = APIRouter(
    prefix="/ingestion",
    tags=["ingestion"],
    dependencies=[Depends(require_api_key)],
)


@router.post(
    "/meetings", response_model=SuccessEnvelope, status_code=status.HTTP_201_CREATED
)
async def ingest_meeting(
    payload: IngestMeetingRequest,
    runtime=Depends(get_runtime),
) -> SuccessEnvelope:
    from iqmeet_graphrag.runtime import ingest_and_index_meeting

    is_allowed = await run_in_threadpool(
        runtime.service.is_workspace_allowed, payload.workspace_id
    )
    if not is_allowed:
        raise HTTPException(status_code=403, detail="workspace_not_allowed")
    stats = await run_in_threadpool(
        ingest_and_index_meeting,
        runtime,
        runtime.service.settings,
        payload.transcript_text,
        payload.workspace_id,
        payload.meeting_id,
    )
    typed_stats = IngestionStats(**stats)
    return SuccessEnvelope(data=typed_stats.model_dump(), trace_id=f"trc_{uuid4().hex}")
