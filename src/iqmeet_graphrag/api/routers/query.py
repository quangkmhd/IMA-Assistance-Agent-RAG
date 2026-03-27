from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends
from starlette.concurrency import run_in_threadpool

from iqmeet_graphrag.api.dependencies import (
    WorkspaceContext,
    get_runtime,
    get_workspace_context,
    require_api_key,
)
from iqmeet_graphrag.api.models import (
    QueryAnswerEnvelope,
    QueryAnswerRequest,
    QueryPlanEnvelope,
    QueryPlanRequest,
)
from iqmeet_graphrag.contracts.query import (
    PlannerPayload,
    QueryRewritePayload,
    RetrievalPlan,
    TimeRange,
)

router = APIRouter(
    prefix="/query",
    tags=["query"],
    dependencies=[Depends(require_api_key)],
)


@router.post("/answer", response_model=QueryAnswerEnvelope)
async def query_answer(
    payload: QueryAnswerRequest,
    runtime=Depends(get_runtime),
    workspace: WorkspaceContext = Depends(get_workspace_context),
) -> QueryAnswerEnvelope:
    answer = await run_in_threadpool(
        runtime.service.answer,
        workspace.workspace_id,
        payload.query,
        payload.intent.value,
        payload.acl_signature,
    )
    return QueryAnswerEnvelope(data=answer, trace_id=answer.trace_id)


@router.post("/plan", response_model=QueryPlanEnvelope)
async def query_plan(
    payload: QueryPlanRequest,
    workspace: WorkspaceContext = Depends(get_workspace_context),
) -> QueryPlanEnvelope:
    rewrite = QueryRewritePayload(
        original_query=payload.query,
        rewritten_query=payload.query,
        intent=payload.intent,
        time_range=TimeRange(from_=datetime.now(timezone.utc), to=None),
        entities=[],
        workspace_id=workspace.workspace_id,
    )
    retrieval_tools = ["event", "vector"]
    if payload.intent.value == "relationship":
        retrieval_tools = ["event", "vector", "graph"]
    plan = RetrievalPlan(
        plan_id=f"pln_{uuid4().hex}",
        tools=retrieval_tools,
        top_k={"event": 30, "vector": 20, "graph": 10},
        query_payload={"query": payload.query, "workspace_id": workspace.workspace_id},
    )
    response = PlannerPayload(rewrite=rewrite, retrieval_plan=plan)
    return QueryPlanEnvelope(data=response, trace_id=f"trc_{uuid4().hex}")
