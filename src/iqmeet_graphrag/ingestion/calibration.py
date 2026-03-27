from __future__ import annotations

from iqmeet_graphrag.contracts.events import EventRecord


class ConfidenceCalibrator:
    def calibrate(self, event: EventRecord) -> EventRecord:
        penalty = 0.0

        if not event.source_span.utterance_id:
            penalty += 0.25

        if not event.value:
            penalty += 0.15

        if not event.entity_id:
            penalty += 0.20

        event.confidence = max(0.0, min(1.0, event.confidence - penalty))
        return event
