from __future__ import annotations

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.schema import BaseNode
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from iqmeet_graphrag.config.settings import AppSettings


class VectorIndexManager:
    def __init__(self, settings: AppSettings) -> None:
        client = QdrantClient(url=settings.qdrant_url)
        self._vector_store = QdrantVectorStore(
            client=client,
            collection_name=settings.qdrant_collection,
        )
        self._embed_model = Settings.embed_model
        self._index: VectorStoreIndex | None = None

    def build_index(self, nodes: list[BaseNode]) -> VectorStoreIndex:
        self._index = VectorStoreIndex(
            nodes=nodes, vector_store=self._vector_store, embed_model=self._embed_model
        )
        return self._index

    @property
    def index(self) -> VectorStoreIndex | None:
        return self._index
