from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever


class CurrentStateEventRetrieverWrapper(BaseRetriever):
    """Wraps a base retriever to filter documents by temporal validity (current state)."""

    base_retriever: Any
    query_time: datetime | None = None

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        effective_time = self.query_time or datetime.now(timezone.utc)
        docs = self.base_retriever.invoke(query)

        filtered: list[Document] = []
        for doc in docs:
            valid_from = doc.metadata.get("valid_from")
            valid_to = doc.metadata.get("valid_to")

            valid_from_dt = self._parse_time(valid_from)
            valid_to_dt = self._parse_time(valid_to)

            if valid_from_dt and valid_from_dt > effective_time:
                continue
            if valid_to_dt and valid_to_dt < effective_time:
                continue
            if doc.metadata.get("status") == "superseded":
                continue

            filtered.append(doc)

        return filtered

    @staticmethod
    def _parse_time(value: object) -> datetime | None:
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
