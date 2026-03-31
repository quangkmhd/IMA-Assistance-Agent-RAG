from __future__ import annotations

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever


class _FusionRetriever(BaseRetriever):
    """Simple weighted fusion retriever without langchain-classic dependency."""

    retrievers: list[BaseRetriever]

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        merged: list[Document] = []
        seen_keys: set[str] = set()

        for retriever in self.retrievers:
            docs = retriever.invoke(query)
            for doc in docs:
                key = str(
                    doc.metadata.get("event_id")
                    or doc.metadata.get("block_id")
                    or hash(doc.page_content)
                )
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                merged.append(doc)
        return merged


def build_fusion_retriever(
    retrievers: list[BaseRetriever],
    weights: list[float] | None = None,
) -> BaseRetriever:
    """Build a lightweight fusion retriever from multiple retrievers."""
    if weights is None:
        weights = [1.0 / len(retrievers)] * len(retrievers)
    _ = weights
    return _FusionRetriever(retrievers=retrievers)
