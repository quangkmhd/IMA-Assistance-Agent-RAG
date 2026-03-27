from pydantic import BaseModel, Field


class Citation(BaseModel):
    event_id: str | None = None
    block_id: str | None = None
    reason: str = "evidence"


class AnswerPayload(BaseModel):
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    citations: list[Citation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    trace_id: str
