from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from iqmeet_graphrag.contracts.errors import ErrorContract
from iqmeet_graphrag.security import ACLViolation


def _error_response(
    *,
    status_code: int,
    error_code: str,
    component: str,
    retryable: bool,
    fallback: str,
) -> JSONResponse:
    payload = ErrorContract(
        error_code=error_code,
        component=component,
        retryable=retryable,
        fallback=fallback,
        trace_id=f"trc_{uuid4().hex}",
    )
    return JSONResponse(
        status_code=status_code, content={"error": payload.model_dump()}
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ACLViolation)
    async def _acl_violation_handler(
        request: Request, exc: ACLViolation
    ) -> JSONResponse:
        _ = request
        _ = exc
        return _error_response(
            status_code=403,
            error_code="ACL_WORKSPACE_DENIED",
            component="acl",
            retryable=False,
            fallback="verify_workspace_access",
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        _ = request
        _ = exc
        return _error_response(
            status_code=422,
            error_code="REQUEST_VALIDATION_ERROR",
            component="api",
            retryable=False,
            fallback="fix_request_payload",
        )

    @app.exception_handler(Exception)
    async def _unhandled_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        _ = request
        _ = exc
        return _error_response(
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR",
            component="api",
            retryable=True,
            fallback="retry_request",
        )
