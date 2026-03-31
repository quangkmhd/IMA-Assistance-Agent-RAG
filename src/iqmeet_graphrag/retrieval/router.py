from __future__ import annotations

import logging
from typing import Any

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field

from iqmeet_graphrag.config.settings import AppSettings

logger = logging.getLogger(__name__)

from iqmeet_graphrag.config.settings import AppSettings


class _RouteDecision(BaseModel):
    """LLM-structured output for selecting which retrievers to invoke."""

    retrievers: list[str] = Field(
        description="List of retrievers to use. Choose from: 'vector', 'event', 'graph'"
    )


def build_router_retriever(
    settings: AppSettings,
    llm: Any,
    vector_retriever: BaseRetriever,
    event_retriever: BaseRetriever,
    graph_retriever: BaseRetriever,
) -> RunnableLambda:
    """Build an LLM-based routing retriever.

    Uses with_structured_output to have the LLM decide which retrievers
    to invoke for a given query.
    """
    route_llm = llm.with_structured_output(_RouteDecision)

    retriever_map: dict[str, BaseRetriever] = {
        "vector": vector_retriever,
        "event": event_retriever,
        "graph": graph_retriever,
    }

    retriever_descriptions = (
        "Choose which retrievers to use for the given query:\n"
        "- 'vector': Best for semantic summaries and high-level meeting overviews.\n"
        "- 'event': Best for factual current state, timeline updates, and event-centric questions.\n"
        "- 'graph': Best for entity relationships, multi-hop reasoning, and causality.\n"
    )

    def route_and_retrieve(query: str) -> list[Document]:
        routing_prompt = (
            f"{retriever_descriptions}\nQuery: {query}\n"
            "Return the list of retrievers to use."
        )
        try:
            decision = route_llm.invoke(routing_prompt)
            selected = decision.retrievers if decision.retrievers else ["vector", "event"]
        except Exception:
            # Fallback: use vector + event if routing fails
            selected = ["vector", "event"]

        all_docs: list[Document] = []
        for name in selected:
            retriever = retriever_map.get(name)
            if retriever is not None:
                try:
                    all_docs.extend(retriever.invoke(query))
                except Exception:
                    pass  # graceful degradation per architecture spec
        return all_docs

    return RunnableLambda(route_and_retrieve)
