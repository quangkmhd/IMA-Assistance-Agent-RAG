from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from llama_index.core import Document
from llama_index.core.base.base_retriever import BaseRetriever

from iqmeet_graphrag.config import AppSettings
from iqmeet_graphrag.contracts.events import EventRecord
from iqmeet_graphrag.indexing import GraphIndexManager, VectorIndexManager
from iqmeet_graphrag.ingestion.pipeline import MeetingIngestionPipeline
from iqmeet_graphrag.ingestion.extractor import StructuredEventExtractor
from iqmeet_graphrag.retrieval import build_query_engine
from iqmeet_graphrag.retrieval.event_retriever import CurrentStateEventRetrieverWrapper
from iqmeet_graphrag.service import IQMeetGraphRAGService


@dataclass
class MeetingSnapshot:
    workspace_id: str
    meeting_id: str
    transcript_text: str
    ingested_at: datetime
    accepted_events: list[EventRecord]
    validation_issues: list[str]
    extraction_failures: list[str]
    indexed_nodes: int


@dataclass
class RuntimeComponents:
    service: IQMeetGraphRAGService
    ingestion: MeetingIngestionPipeline
    vector_manager: VectorIndexManager
    graph_manager: GraphIndexManager
    meeting_store: dict[tuple[str, str], MeetingSnapshot] = field(default_factory=dict)
    event_store: dict[str, EventRecord] = field(default_factory=dict)


from iqmeet_graphrag.config.llm_initializer import setup_llm_and_embedding

def build_runtime(
    settings: AppSettings, allowed_workspaces: set[str]
) -> RuntimeComponents:
    # Cấu hình AI Provider toàn cục cho LlamaIndex (Sử dụng cấu trúc LiteLLM)
    setup_llm_and_embedding(settings)
    
    ingestion = MeetingIngestionPipeline(
        event_extractor=StructuredEventExtractor(settings=settings)
    )

    vector_manager = VectorIndexManager(settings=settings)
    graph_manager = GraphIndexManager(settings=settings)

    class EmptyRetriever(BaseRetriever):
        def _retrieve(self, query_bundle):
            return []

    fallback = EmptyRetriever()

    query_engine = build_query_engine(
        settings=settings,
        vector_retriever=fallback,
        event_retriever=CurrentStateEventRetrieverWrapper(fallback),
        graph_retriever=fallback,
    )

    service = IQMeetGraphRAGService(
        settings=settings,
        query_engine=query_engine,
        allowed_workspaces=allowed_workspaces,
    )

    return RuntimeComponents(
        service=service,
        ingestion=ingestion,
        vector_manager=vector_manager,
        graph_manager=graph_manager,
    )


def ingest_and_index_meeting(
    runtime: RuntimeComponents,
    settings: AppSettings,
    transcript_text: str,
    workspace_id: str,
    meeting_id: str,
) -> dict[str, int]:
    result = runtime.ingestion.run(
        transcript_text=transcript_text,
        workspace_id=workspace_id,
        meeting_id=meeting_id,
    )

    nodes = result.nodes
    if nodes:
        runtime.vector_manager.build_index(nodes=nodes)

    graph_docs = [
        Document(
            text=node.get_content(),
            metadata={
                **node.metadata,
                "workspace_id": workspace_id,
                "meeting_id": meeting_id,
            },
        )
        for node in nodes
    ]
    if graph_docs:
        runtime.graph_manager.build_index(documents=graph_docs)

    if (
        runtime.vector_manager.index is not None
        and runtime.graph_manager.index is not None
    ):
        vector_retriever = runtime.vector_manager.index.as_retriever(
            similarity_top_k=settings.retrieval_top_k_vector
        )
        graph_retriever = runtime.graph_manager.index.as_retriever(
            similarity_top_k=settings.retrieval_top_k_graph
        )
        event_retriever = CurrentStateEventRetrieverWrapper(
            base_retriever=vector_retriever,
        )

        query_engine = build_query_engine(
            settings=settings,
            vector_retriever=vector_retriever,
            event_retriever=event_retriever,
            graph_retriever=graph_retriever,
        )
        runtime.service.set_query_engine(query_engine)

    snapshot = MeetingSnapshot(
        workspace_id=workspace_id,
        meeting_id=meeting_id,
        transcript_text=transcript_text,
        ingested_at=datetime.now(timezone.utc),
        accepted_events=result.accepted_events,
        validation_issues=[issue.reason for issue in result.validation_issues],
        extraction_failures=result.extraction_failures,
        indexed_nodes=len(nodes),
    )
    runtime.meeting_store[(workspace_id, meeting_id)] = snapshot
    for event in result.accepted_events:
        runtime.event_store[event.event_id] = event

    return {
        "accepted_events": len(result.accepted_events),
        "validation_issues": len(result.validation_issues),
        "extraction_failures": len(result.extraction_failures),
        "indexed_nodes": len(nodes),
    }
