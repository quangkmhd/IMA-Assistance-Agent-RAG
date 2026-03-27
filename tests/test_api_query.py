from __future__ import annotations

import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from iqmeet_graphrag.api.main import create_app
from iqmeet_graphrag.config import AppSettings
from iqmeet_graphrag.contracts.answer import AnswerPayload, Citation


class _DummyService:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    @property
    def settings(self) -> AppSettings:
        return self._settings

    def answer(
        self,
        workspace_id: str,
        normalized_query: str,
        intent: str,
        acl_signature: str,
    ) -> AnswerPayload:
        _ = workspace_id
        _ = normalized_query
        _ = intent
        _ = acl_signature
        return AnswerPayload(
            answer="ok",
            confidence=0.8,
            citations=[Citation(event_id="evt_1", block_id="blk_1")],
            warnings=[],
            trace_id="trc_dummy",
        )

    def invalidate_workspace_cache(self, workspace_id: str) -> None:
        _ = workspace_id

    def is_workspace_allowed(self, workspace_id: str) -> bool:
        _ = workspace_id
        return True


class _DummyRuntime:
    def __init__(self, settings: AppSettings) -> None:
        self.service = _DummyService(settings=settings)
        self.meeting_store = {}
        self.event_store = {}


class APIQueryTests(unittest.TestCase):
    def test_query_answer_requires_api_key_and_workspace(self) -> None:
        settings = AppSettings(api_key="test-key", allowed_workspaces={"ws_1"})
        app = create_app(settings=settings, runtime=_DummyRuntime(settings=settings))
        client = TestClient(app)

        unauthorized = client.post(
            "/api/v1/query/answer",
            json={"query": "What changed?", "intent": "current_state"},
            headers={"X-Workspace-Id": "ws_1"},
        )
        self.assertEqual(unauthorized.status_code, 401)

        ok = client.post(
            "/api/v1/query/answer",
            json={"query": "What changed?", "intent": "current_state"},
            headers={"X-Workspace-Id": "ws_1", "X-API-Key": "test-key"},
        )
        self.assertEqual(ok.status_code, 200)
        self.assertEqual(ok.json()["data"]["answer"], "ok")


if __name__ == "__main__":
    unittest.main()
