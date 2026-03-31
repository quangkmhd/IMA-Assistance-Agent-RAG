from __future__ import annotations

from typing import Any

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from iqmeet_graphrag.config.settings import AppSettings
from iqmeet_graphrag.postprocessors import (
    EventDedupPostprocessor,
    TemporalLabelPostprocessor,
    TemporalRerankPostprocessor,
    TemporalWeights,
)
from iqmeet_graphrag.retrieval.fusion import build_fusion_retriever
from iqmeet_graphrag.retrieval.router import build_router_retriever


class QueryChain:
    """Wrapper for the LCEL RAG chain that supports source document tracking."""

    def __init__(self, chain: Any, retriever_fn: Any) -> None:
        self._chain = chain
        self._retriever_fn = retriever_fn
        self._last_source_docs: list[Document] = []

    def query(self, query: str) -> "QueryResult":
        """Execute the RAG chain and return result with source documents."""
        self._last_source_docs = self._retriever_fn(query)
        answer = self._chain.invoke(
            {
                "context_docs": self._last_source_docs,
                "question": query,
            }
        )
        return QueryResult(
            answer=answer,
            source_documents=self._last_source_docs,
        )


class QueryResult:
    """Encapsulates a query answer along with source documents."""

    def __init__(self, answer: str, source_documents: list[Document]) -> None:
        self.answer = answer
        self.source_documents = source_documents

    def __str__(self) -> str:
        return self.answer


def build_query_engine(
    settings: AppSettings,
    llm: Any,
    vector_retriever: BaseRetriever,
    event_retriever: BaseRetriever,
    graph_retriever: BaseRetriever,
) -> QueryChain:
    """Build an LCEL-based RAG chain."""

    # Build routing retriever
    router = build_router_retriever(
        settings=settings,
        llm=llm,
        vector_retriever=vector_retriever,
        event_retriever=event_retriever,
        graph_retriever=graph_retriever,
    )

    # Build fusion ensemble
    fusion = build_fusion_retriever([router, event_retriever])

    # Initialize postprocessors as classes
    deduper = EventDedupPostprocessor()
    labeler = TemporalLabelPostprocessor()
    reranker = TemporalRerankPostprocessor(
        weights=TemporalWeights(
            w_semantic=0.25,
            w_recency=0.25,
            w_validity=0.35,
            w_importance=0.10,
            w_diversity=0.05,
        )
    )

    def postprocess_pipeline(docs: list[Document]) -> list[Document]:
        docs = deduper.postprocess(docs)
        docs = labeler.postprocess(docs)
        docs = reranker.postprocess(docs)
        return docs

    def retrieve_and_process(query: str) -> list[Document]:
        docs = fusion.invoke(query)
        return postprocess_pipeline(docs)

    def format_docs(docs: list[Document]) -> str:
        formatted = []
        for doc in docs:
            label = doc.metadata.get("temporal_label", "")
            event_id = doc.metadata.get("event_id", "")
            block_id = doc.metadata.get("block_id", "")
            prefix = f"[{label}]" if label else ""
            citation = (
                f"(event_id={event_id}, block_id={block_id})"
                if event_id or block_id
                else ""
            )
            formatted.append(f"{prefix} {citation}\n{doc.page_content}")
        return "\n---\n".join(formatted)

    # Build prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a meeting intelligence assistant. "
                "Answer the question based on the provided context. "
                "Always cite event_id and block_id for factual claims. "
                "If evidence is insufficient, state low confidence.\n\n"
                "Context:\n{context}",
            ),
            ("human", "{question}"),
        ]
    )

    # Build LCEL chain
    chain = (
        {
            "context": RunnablePassthrough()
            | RunnableLambda(lambda x: x["context_docs"])
            | RunnableLambda(format_docs),
            "question": RunnablePassthrough() | RunnableLambda(lambda x: x["question"]),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return QueryChain(chain=chain, retriever_fn=retrieve_and_process)
