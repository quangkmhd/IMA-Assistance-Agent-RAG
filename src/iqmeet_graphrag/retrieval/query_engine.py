from __future__ import annotations

from llama_index.core import get_response_synthesizer, Settings
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

from iqmeet_graphrag.config.settings import AppSettings
from iqmeet_graphrag.postprocessors import (
    EventDedupPostprocessor,
    TemporalLabelPostprocessor,
    TemporalRerankPostprocessor,
)
from iqmeet_graphrag.retrieval.fusion import build_fusion_retriever
from iqmeet_graphrag.retrieval.router import build_router_retriever


def build_query_engine(
    settings: AppSettings,
    vector_retriever: BaseRetriever,
    event_retriever: BaseRetriever,
    graph_retriever: BaseRetriever,
) -> RetrieverQueryEngine:
    router = build_router_retriever(
        settings=settings,
        vector_retriever=vector_retriever,
        event_retriever=event_retriever,
        graph_retriever=graph_retriever,
    )
    fusion = build_fusion_retriever([router, event_retriever])

    llm = Settings.llm
    response_synthesizer = get_response_synthesizer(llm=llm, use_async=False)

    temporal_rerank = TemporalRerankPostprocessor(
        w_semantic=0.25,
        w_recency=0.25,
        w_validity=0.35,
        w_importance=0.10,
        w_diversity=0.05,
    )

    return RetrieverQueryEngine(
        retriever=fusion,
        response_synthesizer=response_synthesizer,
        node_postprocessors=[
            EventDedupPostprocessor(),
            TemporalLabelPostprocessor(),
            temporal_rerank,
        ],
    )
