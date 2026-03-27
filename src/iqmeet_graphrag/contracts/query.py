from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class QueryIntent(str, Enum):
    summary = "summary"
    current_state = "current_state"
    timeline = "timeline"
    relationship = "relationship"


class TimeRange(BaseModel):
    from_: datetime | None = Field(default=None, alias="from")
    to: datetime | None = None


class QueryRewritePayload(BaseModel):
    original_query: str
    rewritten_query: str
    intent: QueryIntent
    time_range: TimeRange | None = None
    entities: list[str] = Field(default_factory=list)
    workspace_id: str


class RetrievalPlan(BaseModel):
    plan_id: str
    tools: list[str]
    top_k: dict[str, int]
    query_payload: dict[str, str]


class PlannerPayload(BaseModel):
    rewrite: QueryRewritePayload
    retrieval_plan: RetrievalPlan
