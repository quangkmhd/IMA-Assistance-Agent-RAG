from pydantic import BaseModel


class ErrorContract(BaseModel):
    error_code: str
    component: str
    retryable: bool
    fallback: str
    trace_id: str
