from __future__ import annotations

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from iqmeet_graphrag.config import AppSettings
from iqmeet_graphrag.workflows import AgenticQueryWorkflow


class _DummyDoc:
    def __init__(self, metadata: dict[str, str]):
        self.metadata = metadata


class _DummyResponse:
    def __init__(self, text: str, docs: list[_DummyDoc]):
        self._text = text
        self.source_documents = docs

    def __str__(self) -> str:
        return self._text


class _DummyEngine:
    def query(self, query: str) -> _DummyResponse:
        _ = query
        return _DummyResponse(
            "Answer with citations",
            [
                _DummyDoc({"event_id": "evt_1", "block_id": "blk_1"}),
                _DummyDoc({"event_id": "evt_2", "block_id": "blk_2"}),
            ],
        )


class CitationCoverageTests(unittest.TestCase):
    def test_workflow_returns_citations_for_factual_answer(self) -> None:
        workflow = AgenticQueryWorkflow(
            settings=AppSettings(), query_engine=_DummyEngine()
        )
        result = workflow.run(query="What was decided?", trace_id="trc_test")
        self.assertGreaterEqual(len(result.citations), 1)
        self.assertGreaterEqual(result.confidence, 0.55)


if __name__ == "__main__":
    unittest.main()
