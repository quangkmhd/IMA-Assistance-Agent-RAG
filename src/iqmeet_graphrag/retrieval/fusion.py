from __future__ import annotations

from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.retrievers import QueryFusionRetriever


def build_fusion_retriever(
    retrievers: list[BaseRetriever],
    similarity_top_k: int = 20,
) -> QueryFusionRetriever:
    return QueryFusionRetriever(
        retrievers=retrievers,
        similarity_top_k=similarity_top_k,
        mode="reciprocal_rerank",
        num_queries=1,
        use_async=False,
        verbose=False,
    )
