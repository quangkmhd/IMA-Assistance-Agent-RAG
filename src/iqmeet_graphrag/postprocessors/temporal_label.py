from __future__ import annotations

from datetime import datetime, timezone

from langchain_core.documents import Document


class TemporalLabelPostprocessor:
    """Postprocessor to assign temporal labels (LATEST, SUPERSEDED, HISTORICAL) to documents."""

    def postprocess(self, docs: list[Document]) -> list[Document]:
        now = datetime.now(timezone.utc)
        for doc in docs:
            status = doc.metadata.get("status", "open")
            valid_to = doc.metadata.get("valid_to")

            if status == "superseded":
                doc.metadata["temporal_label"] = "SUPERSEDED"
                continue

            if valid_to:
                try:
                    valid_to_dt = datetime.fromisoformat(
                        str(valid_to).replace("Z", "+00:00")
                    )
                    if valid_to_dt < now:
                        doc.metadata["temporal_label"] = "HISTORICAL"
                        continue
                except ValueError:
                    doc.metadata["temporal_label"] = "HISTORICAL"
                    continue

            doc.metadata["temporal_label"] = "LATEST"

        return docs
