# IQMeet Agentic Temporal GraphRAG

Product-grade local implementation scaffold for **Agentic Temporal GraphRAG for Meeting Intelligence**.

This repository follows a **LlamaIndex-first** approach:

- Prefer built-in LlamaIndex modules for ingestion, routing, retrieval, fusion, workflows, and synthesis.
- Add custom logic only for temporal/business rules that are domain-specific.

## What is included

- Production-oriented code skeleton under `src/iqmeet_graphrag/`
- Pydantic contracts for events, query plans, answers, and errors
- Ingestion pipeline with structured extraction interfaces + validator chain
- Qdrant vector index and Neo4j property graph index wrappers (via LlamaIndex integrations)
- Router + fusion retrieval orchestration
- Temporal postprocessors (`rerank`, `labeling`, `dedup`)
- Agentic query workflow with bounded reflection loop
- ACL boundary, semantic cache, observability scaffolding
- Sprint-by-sprint implementation plan in `IMPLEMENTATION_PLAN_SPRINTS.md`

## Quick start

1. Create virtual environment and install dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

2. Provide runtime configuration by environment variables (see `src/iqmeet_graphrag/config/settings.py`).

3. Start coding from these entry points:

- Contracts: `src/iqmeet_graphrag/contracts/`
- Ingestion: `src/iqmeet_graphrag/ingestion/pipeline.py`
- Retrieval orchestration: `src/iqmeet_graphrag/retrieval/router.py`
- Workflow: `src/iqmeet_graphrag/workflows/query_workflow.py`

## Notes

- This scaffold is designed for iterative hardening with tests and evaluation suites.
- Temporal correctness is intentionally implemented as custom postprocessors and validators.
- No production secrets are committed in code.

## API server (FastAPI)

This repository now includes an HTTP API layer under `src/iqmeet_graphrag/api/`.

Run locally:

```bash
uvicorn iqmeet_graphrag.api.main:app --reload
```

Default API prefix: `/api/v1`

Required headers for protected endpoints:

- `X-API-Key` (default from settings: `dev-key`)
- `X-Workspace-Id`

Key endpoints:

- `GET /api/v1/health/live`
- `GET /api/v1/health/ready`
- `POST /api/v1/query/answer`
- `POST /api/v1/query/plan`
- `POST /api/v1/ingestion/meetings`
- `GET /api/v1/meetings/{meeting_id}`
- `GET /api/v1/meetings/{meeting_id}/events`
- `GET /api/v1/events/{event_id}`
- `POST /api/v1/events/search`
- `POST /api/v1/cache/invalidate-workspace`
- `GET /api/v1/admin/runtime`
- `GET /api/v1/admin/metrics`
