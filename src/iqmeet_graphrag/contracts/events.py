from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EventType(str, Enum):
    decision = "decision"
    action_item = "action_item"
    deadline = "deadline"
    status_update = "status_update"
    risk_blocker = "risk_blocker"
    approval_rejection = "approval_rejection"
    question = "question"
    claim_fact = "claim_fact"
    discussion_note = "discussion_note"
    information = "information"


class EventArgument(BaseModel):
    role: str
    entity_id: str


class SourceSpan(BaseModel):
    utterance_id: str
    char_start: int
    char_end: int


class EventRecord(BaseModel):
    event_id: str
    workspace_id: str
    meeting_id: str
    block_id: str
    event_type: EventType
    tags: list[str] = Field(default_factory=list)
    entity_id: Optional[str] = None
    attribute: Optional[str] = None
    value: Optional[str] = None
    arguments: list[EventArgument] = Field(default_factory=list)
    occurred_at: datetime
    valid_from: datetime
    valid_to: Optional[datetime] = None
    status: str = "open"
    priority: str = "medium"
    confidence: float = 0.0
    importance: float = 0.0
    source_span: SourceSpan
    extraction_version: str
    updated_by_event_id: Optional[str] = None
    created_at: datetime


class EventExtractionBatch(BaseModel):
    block_id: str
    events: list[EventRecord] = Field(default_factory=list)
    rejected_candidates: list[dict[str, str]] = Field(default_factory=list)
