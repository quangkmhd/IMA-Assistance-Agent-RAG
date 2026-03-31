from __future__ import annotations

from langchain_core.documents import Document


class EventDedupPostprocessor:
    """Postprocessor to remove duplicate documents based on event_id or block_id."""

    def postprocess(self, docs: list[Document]) -> list[Document]:
        seen: set[str] = set()
        result: list[Document] = []
        for doc in docs:
            event_id = (
                doc.metadata.get("event_id")
                or doc.metadata.get("block_id")
                or str(id(doc))
            )
            if event_id in seen:
                continue
            seen.add(event_id)
            result.append(doc)
        return result
