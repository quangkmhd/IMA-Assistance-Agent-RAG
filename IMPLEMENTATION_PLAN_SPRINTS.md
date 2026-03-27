# Implementation Plan (Product-Grade)

This plan executes the architecture in `ARCHITECTURE_PRODUCTION.md` with a **LlamaIndex-first** strategy.

## Sprint 1 - Contracts, ingestion, and indexing foundation

Goal: ship deterministic contracts and data plane that can ingest meetings and index into Qdrant + Neo4j.

- Define all Pydantic contracts (`Event`, `MeetingSummary`, `QueryRewritePayload`, `AnswerPayload`, `ErrorContract`).
- Build transcript ingestion pipeline using `IngestionPipeline` + `SentenceSplitter`.
- Implement structured extraction interface with strict JSON schema output.
- Implement validator chain:
  - schema and enum checks,
  - deterministic business rules (`action_item` owner, `deadline` parse),
  - temporal non-overlap validator for active range.
- Implement confidence calibration and retry/fallback mechanics.
- Implement index sinks:
  - vector indexing to Qdrant through LlamaIndex vector store,
  - property graph indexing to Neo4j via `PropertyGraphIndex`.

Acceptance criteria:

- Ingestion run creates nodes, events, and indexing artifacts for one workspace.
- Temporal overlap conflicts are rejected with explicit error payload.
- Extraction failures are queued/reported without crashing ingestion job.

## Sprint 2 - Query plane, routing, fusion, and temporal reasoning

Goal: answer `summary/current_state/timeline/relationship` queries with citations and bounded reflection.

- Build query rewrite payload and intent classification contract.
- Implement retrievers and routing:
  - vector retriever (summary-heavy),
  - event retriever wrapper with current-state semantics,
  - graph retriever via property graph index.
- Implement `RouterRetriever` policy and `QueryFusionRetriever` (RRF default).
- Implement custom temporal postprocessors:
  - temporal rerank hybrid scoring,
  - temporal labels (`LATEST`, `SUPERSEDED`, `HISTORICAL`),
  - dedup and compact.
- Implement context builder + synthesizer prompt contract with mandatory citations.
- Implement bounded reflection loop (`max_iterations=2`).

Acceptance criteria:

- Query path never fails silently; degraded answers include warnings + confidence.
- `current_state` queries prioritize valid and recent events.
- Citations include `event_id`/`block_id` for factual answers.

## Sprint 3 - Product hardening (security, cache, observability, quality gates)

Goal: make local deployment production-like with safety and measurable quality.

- Enforce ACL at gateway and retrieval boundaries.
- Add semantic cache with keying and invalidation policies.
- Add tracing and metrics across rewrite/retrieve/rerank/generate.
- Add failure-mode handlers per architecture matrix.
- Build test suites:
  - unit tests for validators/scoring,
  - integration tests for end-to-end ingestion/query,
  - temporal correctness and cross-workspace ACL tests.
- Add offline eval harness for retrieval and temporal metrics.

Acceptance criteria:

- SLO dashboards available locally (latency + quality + safety).
- Temporal accuracy and citation coverage are measurable and tracked by run.
- Release checklist from architecture doc is executable as CI gates.

## PR slicing recommendation

- PR1: contracts + settings + ingestion skeleton
- PR2: validators + confidence + event store
- PR3: qdrant + neo4j indexing
- PR4: routing + fusion + temporal postprocessors
- PR5: workflow + synthesis + reflection
- PR6: ACL + cache + observability
- PR7: tests + eval + docs
