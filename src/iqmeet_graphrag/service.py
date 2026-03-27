from __future__ import annotations

from uuid import uuid4

from iqmeet_graphrag.cache import SemanticCache
from iqmeet_graphrag.config import AppSettings
from iqmeet_graphrag.contracts.answer import AnswerPayload
from iqmeet_graphrag.observability import TraceContext, TraceLogger
from iqmeet_graphrag.security import ACLGuard, ACLViolation
from iqmeet_graphrag.workflows import AgenticQueryWorkflow


class IQMeetGraphRAGService:
    def __init__(
        self,
        settings: AppSettings,
        query_engine,
        allowed_workspaces: set[str],
    ) -> None:
        self._settings = settings
        self._workflow = AgenticQueryWorkflow(
            settings=settings, query_engine=query_engine
        )
        self._cache = SemanticCache(ttl_hours=6)
        self._acl = ACLGuard(allowed_workspaces=allowed_workspaces)
        self._trace_logger = TraceLogger()

    def set_query_engine(self, query_engine) -> None:
        self._workflow.set_query_engine(query_engine)

    @property
    def settings(self) -> AppSettings:
        return self._settings

    def is_workspace_allowed(self, workspace_id: str) -> bool:
        try:
            self._acl.enforce(workspace_id)
        except ACLViolation:
            return False
        return True

    def invalidate_workspace_cache(self, workspace_id: str) -> None:
        self._acl.enforce(workspace_id)
        self._cache.invalidate_workspace(workspace_id)

    def answer(
        self, workspace_id: str, normalized_query: str, intent: str, acl_signature: str
    ) -> AnswerPayload:
        self._acl.enforce(workspace_id)

        trace_id = f"trc_{uuid4().hex}"
        cache_key = self._cache.build_key(
            workspace_id=workspace_id,
            normalized_query=normalized_query,
            intent=intent,
            time_bucket="current",
            acl_signature=acl_signature,
        )
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        response = self._workflow.run(query=normalized_query, trace_id=trace_id)

        self._trace_logger.emit(
            TraceContext(
                trace_id=trace_id, component="query_service", stage="finalize"
            ),
            {
                "workspace_id": workspace_id,
                "intent": intent,
                "confidence": response.confidence,
                "citation_count": len(response.citations),
            },
        )

        self._cache.put(key=cache_key, workspace_id=workspace_id, payload=response)
        return response
