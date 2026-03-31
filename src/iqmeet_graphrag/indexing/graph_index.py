from __future__ import annotations

from typing import Any

from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document

from iqmeet_graphrag.config.settings import AppSettings


class GraphIndexManager:
    def __init__(self, settings: AppSettings, llm: Any) -> None:
        self._settings = settings
        self._graph = Neo4jGraph(
            url=settings.neo4j_url,
            username=settings.neo4j_username,
            password=settings.neo4j_password,
            database=settings.neo4j_database,
        )
        self._transformer = LLMGraphTransformer(llm=llm)
        self._initialized = False

    def build_index(self, documents: list[Document]) -> None:
        """Extract graph entities/relationships from documents and store in Neo4j."""
        graph_documents = self._transformer.convert_to_graph_documents(documents)
        self._graph.add_graph_documents(graph_documents)
        self._initialized = True

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def graph(self) -> Neo4jGraph:
        return self._graph
