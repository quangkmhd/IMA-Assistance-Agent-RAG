from __future__ import annotations

from llama_index.core import Document, PropertyGraphIndex
from llama_index.core.indices.property_graph import SimpleLLMPathExtractor
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.llms.ollama import Ollama

from iqmeet_graphrag.config.settings import AppSettings


class GraphIndexManager:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._graph_store = Neo4jPropertyGraphStore(
            username=settings.neo4j_username,
            password=settings.neo4j_password,
            url=settings.neo4j_url,
            database=settings.neo4j_database,
        )
        self._llm = Ollama(model=settings.llm_model, request_timeout=120.0)
        self._embed_model = HuggingFaceEmbedding(model_name=settings.embedding_model)
        self._index: PropertyGraphIndex | None = None

    def build_index(self, documents: list[Document]) -> PropertyGraphIndex:
        kg_extractor = SimpleLLMPathExtractor(llm=self._llm, num_workers=4)
        self._index = PropertyGraphIndex.from_documents(
            documents,
            property_graph_store=self._graph_store,
            kg_extractors=[kg_extractor],
            embed_model=self._embed_model,
            show_progress=True,
        )
        return self._index

    @property
    def index(self) -> PropertyGraphIndex | None:
        return self._index
