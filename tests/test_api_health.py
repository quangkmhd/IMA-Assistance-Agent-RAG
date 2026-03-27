from __future__ import annotations

import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from iqmeet_graphrag.api.main import create_app
from iqmeet_graphrag.config import AppSettings


class _DummyService:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    @property
    def settings(self) -> AppSettings:
        return self._settings

    def answer(
        self, workspace_id: str, normalized_query: str, intent: str, acl_signature: str
    ):
        _ = workspace_id
        _ = normalized_query
        _ = intent
        _ = acl_signature
        raise NotImplementedError

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


class APIHealthTests(unittest.TestCase):
    def test_live_and_ready(self) -> None:
        settings = AppSettings(api_key="test-key", allowed_workspaces={"ws_1"})
        app = create_app(settings=settings, runtime=_DummyRuntime(settings=settings))
        client = TestClient(app)

        live = client.get("/api/v1/health/live")
        self.assertEqual(live.status_code, 200)
        self.assertEqual(live.json()["data"]["status"], "ok")

        ready = client.get("/api/v1/health/ready")
        self.assertEqual(ready.status_code, 200)
        self.assertEqual(ready.json()["data"]["status"], "ready")


if __name__ == "__main__":
    unittest.main()
