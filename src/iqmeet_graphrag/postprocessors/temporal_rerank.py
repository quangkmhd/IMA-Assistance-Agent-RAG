from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from langchain_core.documents import Document


@dataclass
class TemporalWeights:
    w_semantic: float = 0.25
    w_recency: float = 0.25
    w_validity: float = 0.35
    w_importance: float = 0.10
    w_diversity: float = 0.05


class TemporalRerankPostprocessor:
    """Postprocessor to rerank documents using temporal hybrid scoring."""

    def __init__(self, weights: TemporalWeights | None = None) -> None:
        self.weights = weights or TemporalWeights()

    def postprocess(self, docs: list[Document]) -> list[Document]:
        scored: list[Document] = []
        for doc in docs:
            semantic_score = float(doc.metadata.get("_score", 0.0))
            recency_score = self._compute_recency(doc)
            validity_score = self._compute_validity(doc)
            importance = float(doc.metadata.get("importance", 0.0))
            diversity = float(doc.metadata.get("diversity", 0.0))

            final_score = (
                semantic_score * self.weights.w_semantic
                + recency_score * self.weights.w_recency
                + validity_score * self.weights.w_validity
                + importance * self.weights.w_importance
                + diversity * self.weights.w_diversity
            )
            doc.metadata["_score"] = final_score
            scored.append(doc)

        return sorted(scored, key=lambda d: float(d.metadata.get("_score", 0.0)), reverse=True)

    def _compute_recency(self, doc: Document) -> float:
        occurred_at_raw = doc.metadata.get("occurred_at")
        if not occurred_at_raw:
            return 0.0
        try:
            occurred_at = datetime.fromisoformat(
                str(occurred_at_raw).replace("Z", "+00:00")
            )
        except ValueError:
            return 0.0

        now = datetime.now(timezone.utc)
        age_hours = max(1.0, (now - occurred_at).total_seconds() / 3600.0)
        return min(1.0, 1.0 / age_hours)

    def _compute_validity(self, doc: Document) -> float:
        valid_from_raw = doc.metadata.get("valid_from")
        valid_to_raw = doc.metadata.get("valid_to")
        now = datetime.now(timezone.utc)

        if not valid_from_raw:
            return 0.0

        try:
            valid_from = datetime.fromisoformat(
                str(valid_from_raw).replace("Z", "+00:00")
            )
        except ValueError:
            return 0.0

        if valid_from > now:
            return 0.0

        if not valid_to_raw:
            return 1.0

        try:
            valid_to = datetime.fromisoformat(str(valid_to_raw).replace("Z", "+00:00"))
        except ValueError:
            return 0.0

        return 1.0 if valid_to >= now else 0.0
