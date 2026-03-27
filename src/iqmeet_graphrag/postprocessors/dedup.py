from __future__ import annotations

from typing import Optional

from llama_index.core import QueryBundle
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore


class EventDedupPostprocessor(BaseNodePostprocessor):
    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> list[NodeWithScore]:
        seen: set[str] = set()
        result: list[NodeWithScore] = []
        for node in nodes:
            event_id = (
                node.node.metadata.get("event_id")
                or node.node.metadata.get("block_id")
                or node.node.node_id
            )
            if event_id in seen:
                continue
            seen.add(event_id)
            result.append(node)
        return result
