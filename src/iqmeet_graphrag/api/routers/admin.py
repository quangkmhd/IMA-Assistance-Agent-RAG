from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends
from starlette.concurrency import run_in_threadpool

from iqmeet_graphrag.api.dependencies import get_runtime, get_settings, require_api_key
from iqmeet_graphrag.api.models import RuntimeInfo, SuccessEnvelope

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_api_key)],
)


@router.get("/runtime", response_model=SuccessEnvelope)
async def get_runtime_info(
    runtime=Depends(get_runtime), settings=Depends(get_settings)
) -> SuccessEnvelope:
    _ = runtime
    info = RuntimeInfo(
        app_name=settings.app_name,
        environment=settings.environment,
        llm_model=settings.llm_model,
        embedding_model=settings.embedding_model,
        qdrant_url=settings.qdrant_url,
        neo4j_url=settings.neo4j_url,
        input_context_budget=settings.input_context_budget,
        reflection_max_iterations=settings.reflection_max_iterations,
        retrieval_top_k_vector=settings.retrieval_top_k_vector,
        retrieval_top_k_event=settings.retrieval_top_k_event,
        retrieval_top_k_graph=settings.retrieval_top_k_graph,
        configured_workspaces=sorted(settings.allowed_workspaces),
    )
    return SuccessEnvelope(data=info.model_dump(), trace_id=f"trc_{uuid4().hex}")


@router.get("/metrics", response_model=SuccessEnvelope)
async def get_metrics(runtime=Depends(get_runtime)) -> SuccessEnvelope:
    counts = await run_in_threadpool(
        lambda: {
            "meeting_count": len(runtime.meeting_store),
            "event_count": len(runtime.event_store),
        }
    )
    return SuccessEnvelope(
        data=counts,
        trace_id=f"trc_{uuid4().hex}",
    )
