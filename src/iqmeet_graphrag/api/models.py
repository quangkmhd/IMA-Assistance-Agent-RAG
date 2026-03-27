from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from iqmeet_graphrag.contracts.answer import AnswerPayload
from iqmeet_graphrag.contracts.errors import ErrorContract
from iqmeet_graphrag.contracts.events import EventRecord
from iqmeet_graphrag.contracts.query import PlannerPayload, QueryIntent


class QueryAnswerRequest(BaseModel):
    query: str = Field(min_length=1)
    intent: QueryIntent
    acl_signature: str = "default"


class QueryPlanRequest(BaseModel):
    query: str = Field(min_length=1)
    intent: QueryIntent


class IngestMeetingRequest(BaseModel):
    workspace_id: str = Field(min_length=1)
    meeting_id: str = Field(min_length=1)
    transcript_text: str = Field(min_length=1)


class WorkspaceCacheInvalidateRequest(BaseModel):
    workspace_id: str = Field(min_length=1)


class EventSearchRequest(BaseModel):
    workspace_id: str = Field(min_length=1)
    meeting_id: str | None = None
    event_type: str | None = None
    entity_id: str | None = None
    attribute: str | None = None
    min_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    valid_at: datetime | None = None


class IngestionStats(BaseModel):
    accepted_events: int
    validation_issues: int
    extraction_failures: int
    indexed_nodes: int


class MeetingInfo(BaseModel):
    workspace_id: str
    meeting_id: str
    ingested_at: datetime
    accepted_events: int
    validation_issues: list[str]
    extraction_failures: list[str]
    indexed_nodes: int


class RuntimeInfo(BaseModel):
    app_name: str
    environment: str
    llm_model: str
    embedding_model: str
    qdrant_url: str
    neo4j_url: str
    input_context_budget: int
    reflection_max_iterations: int
    retrieval_top_k_vector: int
    retrieval_top_k_event: int
    retrieval_top_k_graph: int
    configured_workspaces: list[str]


class SuccessEnvelope(BaseModel):
    data: dict | list | str | int | float | bool | None
    trace_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorContract


class QueryAnswerEnvelope(BaseModel):
    data: AnswerPayload
    trace_id: str


class QueryPlanEnvelope(BaseModel):
    data: PlannerPayload
    trace_id: str


class EventListEnvelope(BaseModel):
    data: list[EventRecord]
    trace_id: str
