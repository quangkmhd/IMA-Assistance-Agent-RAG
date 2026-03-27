from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from iqmeet_graphrag.config.settings import AppSettings
from iqmeet_graphrag.contracts.answer import AnswerPayload, Citation


@dataclass
class WorkflowState:
    query: str
    evidence_ids: set[str]
    iteration: int = 0


class AgenticQueryWorkflow:
    def __init__(self, settings: AppSettings, query_engine: Any) -> None:
        self._settings = settings
        self._query_engine = query_engine

    def run(self, query: str, trace_id: str) -> AnswerPayload:
        state = WorkflowState(query=query, evidence_ids=set())
        final_answer = ""
        warnings: list[str] = []
        confidence = 0.0
        citations: list[Citation] = []

        while state.iteration < self._settings.reflection_max_iterations:
            response = self._query_engine.query(state.query)
            answer_text = str(response)

            iteration_citations = self._extract_citations(response)
            new_evidence_ids = {
                f"{c.event_id}:{c.block_id}" for c in iteration_citations
            }

            if new_evidence_ids and new_evidence_ids == state.evidence_ids:
                warnings.append("reflection_stopped_redundant_evidence")
                final_answer = answer_text
                citations = iteration_citations
                confidence = self._compute_confidence(iteration_citations, warnings)
                break

            state.evidence_ids = new_evidence_ids or state.evidence_ids
            final_answer = answer_text
            citations = iteration_citations
            confidence = self._compute_confidence(iteration_citations, warnings)

            if confidence >= 0.75:
                break

            state.iteration += 1

        if confidence < 0.55:
            warnings.append("low_confidence")

        return AnswerPayload(
            answer=final_answer,
            confidence=confidence,
            citations=citations,
            warnings=warnings,
            trace_id=trace_id,
        )

    def set_query_engine(self, query_engine: Any) -> None:
        self._query_engine = query_engine

    def _extract_citations(self, response: Any) -> list[Citation]:
        source_nodes = getattr(response, "source_nodes", [])
        citations: list[Citation] = []
        for source in source_nodes:
            source_metadata = getattr(source, "metadata", None)
            source_node = getattr(source, "node", None)
            node_metadata = getattr(source_node, "metadata", None)

            metadata: dict[str, Any]
            if isinstance(source_metadata, dict):
                metadata = source_metadata
            elif isinstance(node_metadata, dict):
                metadata = node_metadata
            else:
                metadata = {}
            if not isinstance(metadata, dict):
                metadata = {}
            citations.append(
                Citation(
                    event_id=metadata.get("event_id"),
                    block_id=metadata.get("block_id"),
                    reason="retrieved_evidence",
                )
            )
        return citations

    def _compute_confidence(
        self, citations: list[Citation], warnings: list[str]
    ) -> float:
        if not citations:
            return 0.4
        score = 0.6 + min(0.3, len(citations) * 0.05)
        if warnings:
            score -= 0.1
        return max(0.0, min(1.0, score))
