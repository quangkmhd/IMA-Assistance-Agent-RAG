from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

from langchain_core.documents import Document
from pydantic import BaseModel, Field

from iqmeet_graphrag.config.settings import AppSettings
from iqmeet_graphrag.contracts.events import EventRecord


class EventExtractor(ABC):
    @abstractmethod
    def extract(
        self, document: Document, workspace_id: str, meeting_id: str
    ) -> list[EventRecord]:
        raise NotImplementedError


class NullEventExtractor(EventExtractor):
    def extract(
        self, document: Document, workspace_id: str, meeting_id: str
    ) -> list[EventRecord]:
        return []


@dataclass
class ExtractionFailure:
    block_id: str
    reason: str


class _ExtractedArgument(BaseModel):
    role: str
    entity_id: str


class _ExtractedSourceSpan(BaseModel):
    utterance_id: str = "unknown"
    char_start: int = 0
    char_end: int = 0


class _ExtractedEvent(BaseModel):
    event_type: str
    tags: list[str] = Field(default_factory=list)
    entity_id: str | None = None
    attribute: str | None = None
    value: str | None = None
    arguments: list[_ExtractedArgument] = Field(default_factory=list)
    occurred_at: str | None = None
    valid_from: str | None = None
    valid_to: str | None = None
    status: str = "open"
    priority: str = "medium"
    confidence: float = 0.7
    importance: float = 0.5
    source_span: _ExtractedSourceSpan = Field(default_factory=_ExtractedSourceSpan)


class _ExtractedEventPayload(BaseModel):
    events: list[_ExtractedEvent] = Field(default_factory=list)


class StructuredEventExtractor(EventExtractor):
    def __init__(self, settings: AppSettings, llm: Any) -> None:
        self._settings = settings
        self._llm = llm
        self._structured_llm = self._llm.with_structured_output(_ExtractedEventPayload)
        self._failure_queue: list[ExtractionFailure] = []

    @property
    def failure_queue(self) -> list[ExtractionFailure]:
        return self._failure_queue

    def extract(
        self, document: Document, workspace_id: str, meeting_id: str
    ) -> list[EventRecord]:
        block_id = str(document.metadata.get("block_id") or document.metadata.get("id", "unknown"))
        prompt = self._build_prompt(node_text=document.page_content, block_id=block_id)

        last_error = "unknown_extraction_error"
        for _attempt in range(self._settings.extraction_max_retries + 1):
            try:
                response = self._structured_llm.invoke(prompt)
                payload = self._coerce_payload(response)
                return [
                    self._to_event_record(
                        item=item,
                        workspace_id=workspace_id,
                        meeting_id=meeting_id,
                        block_id=block_id,
                    )
                    for item in payload.events
                ]
            except (
                Exception
            ) as exc:  # pragma: no cover - runtime model-specific behavior
                last_error = str(exc)

        self._failure_queue.append(
            ExtractionFailure(block_id=block_id, reason=last_error)
        )
        return []

    def _coerce_payload(self, response: Any) -> _ExtractedEventPayload:
        if isinstance(response, _ExtractedEventPayload):
            return response
        if isinstance(response, dict):
            return _ExtractedEventPayload.model_validate(response)
        if hasattr(response, "content") and isinstance(response.content, str):
            return _ExtractedEventPayload.model_validate_json(response.content)
        return _ExtractedEventPayload.model_validate(response)

    def _to_event_record(
        self,
        item: _ExtractedEvent,
        workspace_id: str,
        meeting_id: str,
        block_id: str,
    ) -> EventRecord:
        now = datetime.now(timezone.utc)
        occurred_at = self._to_datetime(item.occurred_at) or now
        valid_from = self._to_datetime(item.valid_from) or occurred_at
        valid_to = self._to_datetime(item.valid_to)

        event_id_raw = f"{block_id}:{item.event_type}:{item.value}:{occurred_at.isoformat()}"
        event_id_hash = sha256(event_id_raw.encode("utf-8")).hexdigest()[:16]

        return EventRecord(
            event_id=f"evt_{event_id_hash}",
            workspace_id=workspace_id,
            meeting_id=meeting_id,
            block_id=block_id,
            event_type=item.event_type,
            tags=item.tags,
            entity_id=item.entity_id,
            attribute=item.attribute,
            value=item.value,
            arguments=[arg.model_dump() for arg in item.arguments],
            occurred_at=occurred_at,
            valid_from=valid_from,
            valid_to=valid_to,
            status=item.status,
            priority=item.priority,
            confidence=item.confidence,
            importance=item.importance,
            source_span=item.source_span.model_dump(),
            extraction_version=self._settings.extraction_version,
            created_at=now,
        )

    def _to_datetime(self, value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _build_prompt(self, node_text: str, block_id: str) -> str:
        return (
            "Extract meeting events as strict JSON with schema fields: "
            "event_type,tags,entity_id,attribute,value,arguments,occurred_at,"
            "valid_from,valid_to,status,priority,confidence,importance,source_span. "
            f"Block ID: {block_id}. Transcript:\n{node_text}"
        )
