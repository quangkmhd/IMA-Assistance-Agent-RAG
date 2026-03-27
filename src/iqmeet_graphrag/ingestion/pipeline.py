from __future__ import annotations

from dataclasses import dataclass

from llama_index.core import Document
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import BaseNode

from iqmeet_graphrag.contracts.events import EventRecord
from iqmeet_graphrag.ingestion.calibration import ConfidenceCalibrator
from iqmeet_graphrag.ingestion.extractor import EventExtractor, NullEventExtractor
from iqmeet_graphrag.ingestion.validator import EventValidatorChain, ValidationIssue


@dataclass
class IngestionResult:
    nodes: list[BaseNode]
    accepted_events: list[EventRecord]
    validation_issues: list[ValidationIssue]
    extracted_count: int
    extraction_failures: list[str]


class MeetingIngestionPipeline:
    def __init__(self, event_extractor: EventExtractor | None = None) -> None:
        self._pipeline = IngestionPipeline(
            transformations=[
                SentenceSplitter(chunk_size=1024, chunk_overlap=20),
                TitleExtractor(),
            ]
        )
        self._event_extractor = event_extractor or NullEventExtractor()
        self._validator = EventValidatorChain()
        self._calibrator = ConfidenceCalibrator()

    def run(
        self, transcript_text: str, workspace_id: str, meeting_id: str
    ) -> IngestionResult:
        docs = [
            Document(
                text=transcript_text,
                metadata={"workspace_id": workspace_id, "meeting_id": meeting_id},
            )
        ]
        nodes = self._pipeline.run(documents=docs)

        events: list[EventRecord] = []
        for node in nodes:
            events.extend(
                self._event_extractor.extract(
                    node=node, workspace_id=workspace_id, meeting_id=meeting_id
                )
            )

        calibrated = [self._calibrator.calibrate(event) for event in events]
        accepted, issues = self._validator.validate(calibrated)

        return IngestionResult(
            nodes=nodes,
            accepted_events=accepted,
            validation_issues=issues,
            extracted_count=len(events),
            extraction_failures=self._collect_extraction_failures(),
        )

    def _collect_extraction_failures(self) -> list[str]:
        failures = getattr(self._event_extractor, "failure_queue", [])
        return [f"{item.block_id}:{item.reason}" for item in failures]
