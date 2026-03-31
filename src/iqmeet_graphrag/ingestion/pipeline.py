from __future__ import annotations

from dataclasses import dataclass

from langchain_core.documents import Document

from iqmeet_graphrag.contracts.events import EventRecord
from iqmeet_graphrag.ingestion.calibration import ConfidenceCalibrator
from iqmeet_graphrag.ingestion.extractor import EventExtractor, NullEventExtractor
from iqmeet_graphrag.ingestion.validator import EventValidatorChain, ValidationIssue


@dataclass
class IngestionResult:
    nodes: list[Document]
    accepted_events: list[EventRecord]
    validation_issues: list[ValidationIssue]
    extracted_count: int
    extraction_failures: list[str]


class MeetingIngestionPipeline:
    def __init__(self, event_extractor: EventExtractor | None = None) -> None:
        self._chunk_size = 1024
        self._chunk_overlap = 20
        self._event_extractor = event_extractor or NullEventExtractor()
        self._validator = EventValidatorChain()
        self._calibrator = ConfidenceCalibrator()

    def run(
        self, transcript_text: str, workspace_id: str, meeting_id: str
    ) -> IngestionResult:
        doc = Document(
            page_content=transcript_text,
            metadata={"workspace_id": workspace_id, "meeting_id": meeting_id},
        )
        chunks = self._split_documents([doc])
        for idx, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = idx
            chunk.metadata["block_id"] = f"{workspace_id}:{meeting_id}:blk_{idx:04d}"

        events: list[EventRecord] = []
        for chunk in chunks:
            events.extend(
                self._event_extractor.extract(
                    document=chunk, workspace_id=workspace_id, meeting_id=meeting_id
                )
            )

        calibrated = [self._calibrator.calibrate(event) for event in events]
        accepted, issues = self._validator.validate(calibrated)

        return IngestionResult(
            nodes=chunks,
            accepted_events=accepted,
            validation_issues=issues,
            extracted_count=len(events),
            extraction_failures=self._collect_extraction_failures(),
        )

    def _collect_extraction_failures(self) -> list[str]:
        failures = getattr(self._event_extractor, "failure_queue", [])
        return [f"{item.block_id}:{item.reason}" for item in failures]

    def _split_documents(self, documents: list[Document]) -> list[Document]:
        chunks: list[Document] = []
        step = max(1, self._chunk_size - self._chunk_overlap)

        for doc in documents:
            text = doc.page_content or ""
            if not text:
                chunks.append(Document(page_content="", metadata=dict(doc.metadata)))
                continue

            for start in range(0, len(text), step):
                end = min(len(text), start + self._chunk_size)
                chunk_text = text[start:end]
                chunks.append(
                    Document(page_content=chunk_text, metadata=dict(doc.metadata))
                )
                if end >= len(text):
                    break

        return chunks
