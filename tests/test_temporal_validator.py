from __future__ import annotations

from datetime import datetime, timezone
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from iqmeet_graphrag.contracts.events import EventRecord, SourceSpan
from iqmeet_graphrag.ingestion.validator import EventValidatorChain


class TemporalValidatorTests(unittest.TestCase):
    def test_rejects_active_range_overlap(self) -> None:
        validator = EventValidatorChain()
        now = datetime.now(timezone.utc)

        event_a = EventRecord(
            event_id="evt_a",
            workspace_id="ws_1",
            meeting_id="mtg_1",
            block_id="blk_1",
            event_type="status_update",
            entity_id="ent_1",
            attribute="deployment_strategy",
            value="phase_1",
            occurred_at=now,
            valid_from=now,
            valid_to=None,
            source_span=SourceSpan(utterance_id="utt_1", char_start=0, char_end=10),
            extraction_version="v1.3.0",
            created_at=now,
        )
        event_b = EventRecord(
            event_id="evt_b",
            workspace_id="ws_1",
            meeting_id="mtg_1",
            block_id="blk_2",
            event_type="status_update",
            entity_id="ent_1",
            attribute="deployment_strategy",
            value="phase_2",
            occurred_at=now,
            valid_from=now,
            valid_to=None,
            source_span=SourceSpan(utterance_id="utt_2", char_start=0, char_end=10),
            extraction_version="v1.3.0",
            created_at=now,
        )

        accepted, issues = validator.validate([event_a, event_b])

        self.assertEqual(len(accepted), 1)
        self.assertEqual(accepted[0].event_id, "evt_a")
        self.assertTrue(any(issue.reason == "active_range_overlap" for issue in issues))


if __name__ == "__main__":
    unittest.main()
