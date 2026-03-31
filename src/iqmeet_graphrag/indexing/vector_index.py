from __future__ import annotations

from typing import Any

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from iqmeet_graphrag.config.settings import AppSettings


class VectorIndexManager:
    def __init__(self, settings: AppSettings, embeddings: Any) -> None:
        client = QdrantClient(url=settings.qdrant_url)
        self._vector_store = QdrantVectorStore(
            client=client,
            collection_name=settings.qdrant_collection,
            embedding=embeddings,
        )

    def add_documents(self, documents: list[Document]) -> None:
        """Add documents to the Qdrant vector store."""
        self._vector_store.add_documents(documents)

    def as_retriever(self, top_k: int = 20) -> Any:
        """Return a LangChain retriever backed by this vector store."""
        return self._vector_store.as_retriever(search_kwargs={"k": top_k})

    @property
    def vector_store(self) -> QdrantVectorStore:
        return self._vector_store
