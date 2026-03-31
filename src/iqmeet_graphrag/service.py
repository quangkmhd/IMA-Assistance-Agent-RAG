from __future__ import annotations

import logging
from typing import Any
from uuid import uuid4

from iqmeet_graphrag.config import AppSettings
from iqmeet_graphrag.contracts.answer import AnswerPayload
from iqmeet_graphrag.workflows.query_workflow import AgenticQueryWorkflow

logger = logging.getLogger(__name__)


class IQMeetGraphRAGService:
    """Service layer for IQMeet GraphRAG.

    Coordinates query execution, semantic caching, and ACLs.
    """

    def __init__(
        self,
        settings: AppSettings,
        query_engine: Any,
        allowed_workspaces: set[str],
    ) -> None:
        self._settings = settings
        self._workflow = AgenticQueryWorkflow(
            settings=settings, query_engine=query_engine
        )
        self._allowed_workspaces = allowed_workspaces
        self._semantic_cache: dict[str, AnswerPayload] = {}

    def query(
        self,
        query_text: str,
        workspace_id: str,
        trace_id: str = "default",
    ) -> AnswerPayload:
        """Execute a query against the RAG system."""

        # 1. ACL Check
        if workspace_id not in self._allowed_workspaces:
            logger.warning(
                "Access denied for workspace %s. Allowed: %s",
                workspace_id,
                self._allowed_workspaces,
            )
            return AnswerPayload(
                answer="Access denied to this workspace.",
                confidence=0.0,
                citations=[],
                warnings=["access_denied"],
                trace_id=trace_id,
            )

        # 2. Semantic Cache Check (Simple for now)
        cache_key = f"{workspace_id}:{query_text}"
        if cache_key in self._semantic_cache:
            logger.info("Semantic cache hit for query: %s", query_text)
            return self._semantic_cache[cache_key]

        # 3. Execute Agentic Workflow
        logger.info("Executing agentic workflow for query: %s", query_text)
        response = self._workflow.run(query=query_text, trace_id=trace_id)

        # 4. Cache Result
        if response.confidence > 0.8:
            self._semantic_cache[cache_key] = response

        return response

    def answer(
        self,
        workspace_id: str,
        normalized_query: str,
        intent: str,
        acl_signature: str,
    ) -> AnswerPayload:
        """Backward-compatible answer API used by existing routers."""
        _ = intent
        _ = acl_signature
        return self.query(
            query_text=normalized_query,
            workspace_id=workspace_id,
            trace_id=f"trc_{uuid4().hex}",
        )

    @property
    def settings(self) -> AppSettings:
        return self._settings

    def is_workspace_allowed(self, workspace_id: str) -> bool:
        return workspace_id in self._allowed_workspaces

    def invalidate_workspace_cache(self, workspace_id: str) -> None:
        prefix = f"{workspace_id}:"
        keys_to_delete = [k for k in self._semantic_cache if k.startswith(prefix)]
        for key in keys_to_delete:
            del self._semantic_cache[key]

    def set_query_engine(self, query_engine: Any) -> None:
        """Update the underlying query engine during runtime (e.g. after indexing)."""
        self._workflow.set_query_engine(query_engine)

    def clear_cache(self) -> None:
        """Clear the semantic cache."""
        self._semantic_cache.clear()
