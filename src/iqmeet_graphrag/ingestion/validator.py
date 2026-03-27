from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from iqmeet_graphrag.contracts.events import EventRecord, EventType


@dataclass
class ValidationIssue:
    event_id: str
    reason: str


class EventValidatorChain:
    def validate(
        self, events: list[EventRecord]
    ) -> tuple[list[EventRecord], list[ValidationIssue]]:
        accepted: list[EventRecord] = []
        issues: list[ValidationIssue] = []

        for event in events:
            issue = self._validate_single(event)
            if issue is None:
                accepted.append(event)
            else:
                issues.append(issue)

        overlap_issues = self._validate_temporal_overlap(accepted)
        if overlap_issues:
            rejected_ids = {issue.event_id for issue in overlap_issues}
            accepted = [
                event for event in accepted if event.event_id not in rejected_ids
            ]
            issues.extend(overlap_issues)

        return accepted, issues

    def _validate_single(self, event: EventRecord) -> ValidationIssue | None:
        if event.valid_to is not None and event.valid_to < event.valid_from:
            return ValidationIssue(
                event_id=event.event_id, reason="invalid_valid_range"
            )

        if event.event_type == EventType.action_item and not any(
            arg.role == "owner" for arg in event.arguments
        ):
            return ValidationIssue(
                event_id=event.event_id, reason="action_item_missing_owner"
            )

        if event.event_type == EventType.deadline:
            if event.value is None:
                return ValidationIssue(
                    event_id=event.event_id, reason="deadline_missing_value"
                )
            try:
                datetime.fromisoformat(event.value.replace("Z", "+00:00"))
            except ValueError:
                return ValidationIssue(
                    event_id=event.event_id, reason="invalid_deadline_datetime"
                )

        return None

    def _validate_temporal_overlap(
        self, events: list[EventRecord]
    ) -> list[ValidationIssue]:
        grouped: dict[tuple[str, str, str], list[EventRecord]] = {}
        for event in events:
            if not event.entity_id or not event.attribute:
                continue
            key = (event.workspace_id, event.entity_id, event.attribute)
            grouped.setdefault(key, []).append(event)

        issues: list[ValidationIssue] = []
        for grouped_events in grouped.values():
            sorted_events = sorted(grouped_events, key=lambda evt: evt.valid_from)
            for i in range(len(sorted_events) - 1):
                current = sorted_events[i]
                following = sorted_events[i + 1]
                current_valid_to = current.valid_to or datetime.max.replace(
                    tzinfo=following.valid_from.tzinfo
                )
                if current_valid_to > following.valid_from:
                    issues.append(
                        ValidationIssue(
                            event_id=following.event_id,
                            reason="active_range_overlap",
                        )
                    )
        return issues
