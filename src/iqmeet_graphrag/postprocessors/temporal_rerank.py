from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from llama_index.core import QueryBundle
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore


class TemporalRerankPostprocessor(BaseNodePostprocessor):
    def __init__(
        self,
        w_semantic: float,
        w_recency: float,
        w_validity: float,
        w_importance: float,
        w_diversity: float,
    ) -> None:
        self.w_semantic = w_semantic
        self.w_recency = w_recency
        self.w_validity = w_validity
        self.w_importance = w_importance
        self.w_diversity = w_diversity

    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> list[NodeWithScore]:
        scored: list[NodeWithScore] = []
        for node in nodes:
            semantic_score = float(node.score or 0.0)
            recency_score = self._compute_recency(node)
            validity_score = self._compute_validity(node)
            importance = float(node.node.metadata.get("importance", 0.0))
            diversity = float(node.node.metadata.get("diversity", 0.0))

            final_score = (
                semantic_score * self.w_semantic
                + recency_score * self.w_recency
                + validity_score * self.w_validity
                + importance * self.w_importance
                + diversity * self.w_diversity
            )
            node.score = final_score
            scored.append(node)

        return sorted(scored, key=lambda item: float(item.score or 0.0), reverse=True)

    def _compute_recency(self, node: NodeWithScore) -> float:
        occurred_at_raw = node.node.metadata.get("occurred_at")
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

    def _compute_validity(self, node: NodeWithScore) -> float:
        valid_from_raw = node.node.metadata.get("valid_from")
        valid_to_raw = node.node.metadata.get("valid_to")
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
