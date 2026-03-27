from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from llama_index.core import QueryBundle
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore


class TemporalLabelPostprocessor(BaseNodePostprocessor):
    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> list[NodeWithScore]:
        now = datetime.now(timezone.utc)
        for node in nodes:
            status = node.node.metadata.get("status", "open")
            valid_to = node.node.metadata.get("valid_to")

            if status == "superseded":
                node.node.metadata["temporal_label"] = "SUPERSEDED"
                continue

            if valid_to:
                try:
                    valid_to_dt = datetime.fromisoformat(
                        str(valid_to).replace("Z", "+00:00")
                    )
                    if valid_to_dt < now:
                        node.node.metadata["temporal_label"] = "HISTORICAL"
                        continue
                except ValueError:
                    node.node.metadata["temporal_label"] = "HISTORICAL"
                    continue

            node.node.metadata["temporal_label"] = "LATEST"

        return nodes
