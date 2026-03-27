from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool

from iqmeet_graphrag.api.dependencies import get_runtime, require_api_key
from iqmeet_graphrag.api.models import (
    EventListEnvelope,
    EventSearchRequest,
    SuccessEnvelope,
)

router = APIRouter(
    prefix="/events",
    tags=["events"],
    dependencies=[Depends(require_api_key)],
)


@router.get("/{event_id}", response_model=SuccessEnvelope)
async def get_event(event_id: str, runtime=Depends(get_runtime)) -> SuccessEnvelope:
    event = await run_in_threadpool(runtime.event_store.get, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="event_not_found")
    return SuccessEnvelope(
        data=event.model_dump(mode="json"), trace_id=f"trc_{uuid4().hex}"
    )


@router.post("/search", response_model=EventListEnvelope)
async def search_events(
    payload: EventSearchRequest,
    runtime=Depends(get_runtime),
) -> EventListEnvelope:
    effective_time = payload.valid_at or datetime.now(timezone.utc)

    raw_events = await run_in_threadpool(lambda: list(runtime.event_store.values()))
    events = [
        event for event in raw_events if event.workspace_id == payload.workspace_id
    ]
    if payload.meeting_id:
        events = [event for event in events if event.meeting_id == payload.meeting_id]
    if payload.event_type:
        events = [
            event for event in events if event.event_type.value == payload.event_type
        ]
    if payload.entity_id:
        events = [event for event in events if event.entity_id == payload.entity_id]
    if payload.attribute:
        events = [event for event in events if event.attribute == payload.attribute]
    events = [event for event in events if event.confidence >= payload.min_confidence]
    events = [
        event
        for event in events
        if event.valid_from <= effective_time
        and (event.valid_to is None or event.valid_to >= effective_time)
    ]
    return EventListEnvelope(data=events, trace_id=f"trc_{uuid4().hex}")
