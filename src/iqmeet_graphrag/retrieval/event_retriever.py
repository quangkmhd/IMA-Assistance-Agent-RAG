from __future__ import annotations

from datetime import datetime, timezone

from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import NodeWithScore, QueryBundle


class CurrentStateEventRetrieverWrapper(BaseRetriever):
    def __init__(
        self, base_retriever: BaseRetriever, query_time: datetime | None = None
    ) -> None:
        self._base_retriever = base_retriever
        self._query_time = query_time or datetime.now(timezone.utc)

    def _retrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        nodes = self._base_retriever.retrieve(query_bundle)
        filtered: list[NodeWithScore] = []
        for node in nodes:
            valid_from = node.node.metadata.get("valid_from")
            valid_to = node.node.metadata.get("valid_to")

            valid_from_dt = self._parse_time(valid_from)
            valid_to_dt = self._parse_time(valid_to)

            if valid_from_dt and valid_from_dt > self._query_time:
                continue
            if valid_to_dt and valid_to_dt < self._query_time:
                continue
            if node.node.metadata.get("status") == "superseded":
                continue

            filtered.append(node)

        return filtered

    def _parse_time(self, value: object) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None
