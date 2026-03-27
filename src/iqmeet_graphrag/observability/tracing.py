from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass
class TraceContext:
    trace_id: str
    component: str
    stage: str


class TraceLogger:
    def emit(self, context: TraceContext, payload: dict[str, object]) -> str:
        log_line = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **asdict(context),
            "payload": payload,
        }
        return json.dumps(log_line)
