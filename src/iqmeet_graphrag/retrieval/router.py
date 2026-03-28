from __future__ import annotations

from llama_index.core import Settings
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.retrievers import RouterRetriever
from llama_index.core.selectors import PydanticMultiSelector
from llama_index.core.tools import RetrieverTool

from iqmeet_graphrag.config.settings import AppSettings


def build_router_retriever(
    settings: AppSettings,
    vector_retriever: BaseRetriever,
    event_retriever: BaseRetriever,
    graph_retriever: BaseRetriever,
) -> RouterRetriever:
    llm = Settings.llm

    tools = [
        RetrieverTool.from_defaults(
            retriever=vector_retriever,
            description="Best for semantic summaries and high-level meeting overviews.",
            name="vector",
        ),
        RetrieverTool.from_defaults(
            retriever=event_retriever,
            description="Best for factual current state, timeline updates, and event-centric questions.",
            name="event",
        ),
        RetrieverTool.from_defaults(
            retriever=graph_retriever,
            description="Best for entity relationships, multi-hop reasoning, and causality.",
            name="graph",
        ),
    ]

    return RouterRetriever(
        selector=PydanticMultiSelector.from_defaults(llm=llm),
        retriever_tools=tools,
    )
