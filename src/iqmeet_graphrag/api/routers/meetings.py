from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool

from iqmeet_graphrag.api.dependencies import (
    WorkspaceContext,
    get_runtime,
    get_workspace_context,
    require_api_key,
)
from iqmeet_graphrag.api.models import EventListEnvelope, MeetingInfo, SuccessEnvelope

router = APIRouter(
    prefix="/meetings",
    tags=["meetings"],
    dependencies=[Depends(require_api_key)],
)


@router.get("/{meeting_id}", response_model=SuccessEnvelope)
async def get_meeting(
    meeting_id: str,
    runtime=Depends(get_runtime),
    workspace: WorkspaceContext = Depends(get_workspace_context),
) -> SuccessEnvelope:
    snapshot = await run_in_threadpool(
        runtime.meeting_store.get, (workspace.workspace_id, meeting_id)
    )
    if snapshot is None:
        raise HTTPException(status_code=404, detail="meeting_not_found")

    payload = MeetingInfo(
        workspace_id=snapshot.workspace_id,
        meeting_id=snapshot.meeting_id,
        ingested_at=snapshot.ingested_at,
        accepted_events=len(snapshot.accepted_events),
        validation_issues=snapshot.validation_issues,
        extraction_failures=snapshot.extraction_failures,
        indexed_nodes=snapshot.indexed_nodes,
    )
    return SuccessEnvelope(
        data=payload.model_dump(mode="json"), trace_id=f"trc_{uuid4().hex}"
    )


@router.get("/{meeting_id}/events", response_model=EventListEnvelope)
async def list_meeting_events(
    meeting_id: str,
    event_type: str | None = None,
    min_confidence: float = 0.0,
    runtime=Depends(get_runtime),
    workspace: WorkspaceContext = Depends(get_workspace_context),
) -> EventListEnvelope:
    snapshot = await run_in_threadpool(
        runtime.meeting_store.get, (workspace.workspace_id, meeting_id)
    )
    if snapshot is None:
        raise HTTPException(status_code=404, detail="meeting_not_found")

    events = snapshot.accepted_events
    if event_type:
        events = [event for event in events if event.event_type.value == event_type]
    events = [event for event in events if event.confidence >= min_confidence]
    return EventListEnvelope(data=events, trace_id=f"trc_{uuid4().hex}")
