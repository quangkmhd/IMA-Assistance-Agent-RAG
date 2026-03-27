# Agentic Temporal GraphRAG for Meeting Intelligence (Production Blueprint)

Tài liệu này là bản chi tiết và logic hơn, tổng hợp từ `ARCHITECTURE.md` và `architecture_review.md`, tập trung vào khả năng triển khai production.

---

## 1. Mục tiêu và phạm vi

### 1.1 Mục tiêu

Hệ thống cần:
- Trả lời câu hỏi meeting theo ngữ cảnh đa phiên (multi-meeting).
- Đúng theo thời gian (temporal correctness), phân biệt thông tin mới và cũ.
- Hỗ trợ Q&A, summary, timeline và relationship reasoning.
- Có cơ chế fallback rõ ràng khi thành phần retrieval/extraction gặp sự cố.

### 1.2 Non-goals (v1)

- Không hướng đến full autonomous action execution (chỉ recommendation/answer).
- Không bắt buộc graph retrieval cho tất cả query (chỉ bật khi cần multi-hop).
- Không thay thế quy trình human review cho event confidence thấp.

### 1.3 Nguyên tắc thiết kế

- Accuracy first: event extraction quality là trọng tâm.
- Temporal-first reasoning: thông tin mới được ưu tiên đúng cách, không xóa ngữ cảnh lịch sử.
- Graceful degradation: thành phần lỗi thì hệ thống vẫn trả lời với confidence và citation rõ ràng.
- Explicit contracts: mọi boundary giữa component đều có Input/Output/Error contract.

### 1.4 Nguyên tắc triển khai: LlamaIndex-first

- Mặc định ưu tiên dùng module sẵn có của LlamaIndex cho toàn bộ pipeline (ingestion, retrieval, fusion, generation, observability hooks).
- Chỉ viết custom khi LlamaIndex chưa có khả năng tương đương hoặc không đáp ứng constraint nghiệp vụ (đặc biệt temporal business rules).
- Mọi custom component phải bọc theo interface của LlamaIndex (Retriever, Postprocessor, QueryEngine, Workflow step) để tránh lock-in vào code riêng.
- Khi có thể, cấu hình qua LlamaIndex trước (metadata filters, reranker, router, response synthesizer) rồi mới cân nhắc custom logic.

Các phần dự kiến cần custom (v1):
- Temporal conflict validator cho `valid_from`/`valid_to` và non-overlap active range theo (`workspace_id`,`entity_id`,`attribute`).
- Temporal scoring feature engineering cho `current_state` (validity + recency + superseded semantics).
- Workspace ACL enforcement tại gateway/data access boundary (bọc ngoài LlamaIndex).
- Semantic cache invalidation policy theo ingestion events ở mức workspace/entity.

---

## 2. Kiến trúc tổng thể

## 2.1 End-to-end query flow

```text
User Query
  -> Query Gateway (auth, workspace ACL)
  -> LlamaIndex Query Transform (intent/time/entity normalization)
  -> Semantic Cache Check
      -> cache hit: return answer + citations
      -> cache miss:
          -> LlamaIndex Router/Workflow Planner (route strategy)
          -> Multi-Retrieval via LlamaIndex Retrievers (Vector/Event/Graph)
          -> Fusion (QueryFusionRetriever) + Temporal Rerank (custom postprocessor)
          -> Context Builder via Node Postprocessors (dedup + annotate + compact)
          -> LlamaIndex Response Synthesizer
          -> Reflection loop (max 2 iterations, bằng workflow step)
          -> Answer Composer (confidence + citations + audit metadata)
```

## 2.2 Retrieval routing policy

- `summary`: dùng `VectorIndexRetriever` là chủ đạo.
- `current_state`: Event retrieval là chủ đạo (LlamaIndex retriever + custom temporal filter bắt buộc).
- `timeline`: Event retrieval + temporal expansion postprocessing.
- `relationship` hoặc `why` phức tạp: kết hợp Event + Graph retriever (`PropertyGraphIndex`/`KnowledgeGraphIndex`).
- Routing do `RouterRetriever` hoặc workflow router đảm nhiệm; mặc định không gọi cả 3 retriever cùng lúc nếu không cần.

---

## 3. Data model và schema

## 3.1 Canonical entities

Sử dụng 4 document core: `meeting`, `block`, `event`, `entity` (giữ tương thích bản gốc).

## 3.2 Event type taxonomy (rút gọn)

Để giảm ambiguity extraction, event type v1 được rút gọn:
- `decision`
- `action_item`
- `deadline`
- `status_update`
- `risk_blocker`
- `approval_rejection`
- `question`
- `claim_fact`
- `discussion_note`
- `information`

Chi tiết bổ sung thông qua `tags` thay vì phình event_type:
- Ví dụ: `tags=["agreement","policy_change","concern"]`

## 3.3 Event schema (v1.3)

```json
{
  "event_id": "evt_...",
  "workspace_id": "ws_...",
  "meeting_id": "mtg_...",
  "block_id": "blk_...",

  "event_type": "decision",
  "tags": ["policy_change"],

  "entity_id": "ent_...",
  "attribute": "deployment_strategy",
  "value": "rollout in 2 phases",

  "arguments": [
    {"role": "owner", "entity_id": "ent_pm"}
  ],

  "occurred_at": "2026-03-25T09:30:00Z",
  "valid_from": "2026-03-25T09:30:00Z",
  "valid_to": null,

  "status": "open",
  "priority": "high",

  "confidence": 0.86,
  "importance": 0.72,

  "source_span": {
    "utterance_id": "utt_...",
    "char_start": 14,
    "char_end": 120
  },

  "extraction_version": "v1.3.0",
  "updated_by_event_id": null,
  "created_at": "2026-03-25T09:31:20Z"
}
```

## 3.4 Định nghĩa rõ `confidence` vs `importance`

- `confidence`: độ tin cậy của extractor rằng event này đúng (model certainty + validation consistency).
- `importance`: mức ưu tiên nghiệp vụ của event cho retrieval/context compaction.
- Trong ranking:
  - `confidence` dùng như guardrail, có thể filter.
  - `importance` là tín hiệu scoring bổ sung.

## 3.5 Validation constraints

- Temporal integrity:
  - `meeting.start_time <= meeting.end_time`
  - `event.valid_to == null` hoặc `valid_to >= valid_from`
- Non-overlap active range:
  - với cùng (`workspace_id`,`entity_id`,`attribute`), không cho 2 event active overlap.
- Event-specific rules:
  - `action_item` phải có `arguments.role=owner`
  - `deadline` phải parse được datetime trong `value`
- Confidence guardrail:
  - `confidence < 0.55` -> `low_confidence_queue`

## 3.6 Meeting summary template contract (Core/Optional)

Mục tiêu: chuẩn hoá summary để dùng trực tiếp cho retrieval, reasoning và graph linking,
thay vì chỉ tạo "biên bản đọc cho người".

### Core fields (bắt buộc cho mọi meeting)

- `objective`: mục tiêu cuộc họp.
- `topics`: các chủ đề chính đã thảo luận (group theo ý).
- `key_points`: insight/ý chính quan trọng (problem, approach, trade-off).
- `entities`: thực thể liên quan (person/team/project/system).
- `timeline`: các mốc diễn tiến theo thời gian.

Lưu ý: timeline được tạo bởi pipeline/command riêng nhưng vẫn lưu trong summary contract.

### Optional fields (cho phép rỗng)

- `decisions`: quyết định cuối cùng (nếu có).
- `actions`: action items theo cấu trúc `owner`, `task`, `due_date` (optional).
- `issues`: vấn đề/risk/blocker chưa giải quyết.
- `open_questions`: câu hỏi còn mở.

### Canonical JSON contract

```json
{
  "objective": "...",
  "topics": ["...", "..."],
  "key_points": ["...", "..."],
  "entities": ["...", "..."],
  "timeline": [
    {"time": "...", "event": "..."}
  ],
  "decisions": [],
  "actions": [],
  "issues": [],
  "open_questions": []
}
```

### Storage + retrieval notes

- Lưu dạng structured JSONB trong `meeting_summaries` để filter/index dễ hơn so với blob text.
- Không ép `decisions/actions/issues/open_questions` phải có dữ liệu; empty là hợp lệ.
- Retrieval mapping:
  - `topics + key_points` -> semantic retrieval.
  - `entities` -> graph/entity linking.
  - `timeline` -> temporal reasoning.
  - `actions/decisions` -> task-tracking và current-state follow-up.

---

## 4. Temporal model

## 4.1 Temporal semantics

- `occurred_at`: lúc sự kiện được phát ngôn/ghi nhận.
- `valid_from`/`valid_to`: khoảng hiệu lực nghiệp vụ.
- Query type ảnh hưởng cách xử lý:
  - `current_state`: ưu tiên event còn hiệu lực.
  - `timeline/history`: giữ cả event đã superseded.

## 4.2 Conflict resolution

Khi event mới cập nhật cùng (`entity_id`,`attribute`):
1. Đóng event cũ: set `valid_to = new_event.valid_from`.
2. Tạo cạnh graph `old_event -updates-> new_event`.
3. Đánh dấu cũ là `status=superseded` nếu phù hợp.

## 4.3 Hybrid temporal scoring

```python
final_score = (
  semantic_score   * w_semantic
  + recency_score  * w_recency
  + validity_score * w_validity
  + importance     * w_importance
  + diversity      * w_diversity
)
```

Recommended defaults:
- `current_state`: `w_validity=0.35`, `w_recency=0.25`, `w_semantic=0.25`, `w_importance=0.10`, `w_diversity=0.05`
- `timeline`: `w_semantic=0.35`, `w_recency=0.25`, `w_validity=0.10`, `w_importance=0.20`, `w_diversity=0.10`

---

## 5. Ingestion pipeline (chi tiết)

## 5.1 Pipeline

```text
Transcript + diarization + pause metadata
  -> LlamaIndex IngestionPipeline + NodeParser (audio-aware semantic chunking)
  -> LlamaIndex LLM extraction / structured program (event candidates)
  -> Schema validation (Pydantic) + temporal validation (custom)
  -> Entity linking + canonicalization (metadata extractor + custom resolver)
  -> Confidence calibration (custom scorer/postprocessor)
  -> Indexing qua LlamaIndex indices (vector/event/graph/metadata)
  -> Audit log + quality metrics
```

## 5.2 Extraction strategy (P0)

### Step A - Candidate extraction
- Prompt bắt buộc trả JSON đúng schema.
- Bắt buộc citation span (`utterance_id`, `char_start`, `char_end`).
- Yêu cầu model phân biệt `fact` và `speculation`.

### Step B - Deterministic validation
- Validate schema, enum, datetime parse.
- Validate role constraints (`owner`, `target`, ...).
- Validate `source_span` nằm trong block gốc.

### Step C - Temporal/business validation
- Kiểm tra overlap active range.
- Kiểm tra conflict update chain có hợp lệ.

### Step D - Confidence calibration
- Raw LLM score + rule penalties.
- Ví dụ penalty:
  - thiếu source span: `-0.25`
  - value mơ hồ: `-0.15`
  - entity linking fail: `-0.20`

### Step E - Retry/fallback
- 1 lần retry với prompt stricter nếu fail schema.
- Nếu vẫn fail: ghi `extraction_failed` + đưa block vào reprocess queue.

## 5.3 Extraction output contract

```json
{
  "block_id": "blk_...",
  "events": [{"event_id": "evt_..."}],
  "rejected_candidates": [{"reason": "invalid_datetime"}],
  "quality": {
    "accepted": 3,
    "rejected": 1,
    "avg_confidence": 0.79
  }
}
```

---

## 6. Retrieval, fusion, rerank

## 6.1 Retriever interfaces

### Vector retriever
- Ưu tiên: `VectorIndexRetriever` (LlamaIndex).
- Input: `rewritten_query`, `workspace_id`, `top_k`.
- Output: block candidates + semantic scores.

### Event retriever
- Ưu tiên: retriever của LlamaIndex + `MetadataFilters` cho `workspace_id`, `meeting_id`, `entity_id`, `event_type`.
- Custom tối thiểu: `TemporalEventRetriever` wrapper để xử lý `valid_from`/`valid_to`, superseded chain và current-state semantics.
- Output: event candidates + metadata filters + temporal features.

### Graph retriever
- Ưu tiên: `PropertyGraphIndex` hoặc `KnowledgeGraphIndex` retriever trong LlamaIndex.
- Input: seed entities + hop limit.
- Output: paths/subgraphs + path confidence.

## 6.2 Fusion strategy (không vague)

- Mặc định dùng `QueryFusionRetriever` (RRF mode) khi có từ 2 retriever trả kết quả khác thang điểm.
- Dùng weighted merge (LlamaIndex fusion + custom scorer) khi tất cả score đã normalize [0..1].
- Nếu 1 retriever rỗng:
  - không fail pipeline;
  - ghi telemetry `retriever_empty_result`;
  - tiếp tục fusion với retriever còn lại.

RRF formula:

```python
rrf_score(d) = sum(1 / (k + rank_i(d)))
```

Weighted merge formula:

```python
fused_score = a*vector + b*event + c*graph
```

Recommended defaults:
- `current_state`: `a=0.20, b=0.65, c=0.15`
- `relationship`: `a=0.15, b=0.35, c=0.50`

---

## 7. Context builder

## 7.1 Processing pipeline

1. Deduplicate bằng LlamaIndex postprocessors (ID-based) theo `event_id`/`block_id`.
2. Sắp xếp timeline (custom temporal sorter nếu cần).
3. Gắn nhãn temporal: `[LATEST]`, `[SUPERSEDED]`, `[HISTORICAL]` (custom metadata enricher).
4. Nhóm theo entity/attribute để giảm token.
5. Context compaction theo token budget qua node postprocessing + response synthesizer.

## 7.2 Token budget policy

- Mặc định v1: `input_context_budget = 10_000 tokens` (quản lý trong workflow/synthesizer của LlamaIndex).
- Compaction order:
  1. Latest valid state
  2. Root-cause historical event
  3. Supporting evidence (top score)

## 7.3 Prompt contract tới LLM

Bắt buộc có:
- `question`
- `context_blocks` (có labels temporal)
- `required_output_format`
- `citation_rules` (event_id/block_id bắt buộc)
- `failure_instruction` (nếu thiếu evidence thì trả low_confidence)

Khuyến nghị triển khai:
- Dùng structured output (`Pydantic` program/output parser) trong LlamaIndex thay vì parse tay.
- Dùng citation support sẵn có của query engine; chỉ custom khi cần format citation đặc thù.

---

## 8. Agentic loop và reflection

## 8.1 Reflection checklist

- Có citation hợp lệ chưa?
- Có xung đột temporal chưa giải quyết?
- Có cần retrieve bổ sung entity/time range?

## 8.2 Hard stop

- `max_iterations=2`
- Dừng ngay nếu tập evidence mới trùng hoàn toàn tập cũ.
- Nếu sau lần 2 vẫn thiếu evidence: trả kết quả `low_confidence`.

---

## 9. Interface contracts giữa components

## 9.1 Query Rewrite -> Planner

```json
{
  "original_query": "...",
  "rewritten_query": "...",
  "intent": "summary|current_state|timeline|relationship",
  "time_range": {"from": "...", "to": "..."},
  "entities": ["ent_1", "ent_2"],
  "workspace_id": "ws_..."
}
```

## 9.2 Planner -> Retrieval Orchestrator

```json
{
  "plan_id": "pln_...",
  "tools": ["event", "vector"],
  "top_k": {"event": 30, "vector": 20},
  "query_payload": {"...": "..."}
}
```

## 9.3 Retrieval -> Reranker

```json
{
  "candidates": [
    {
      "id": "evt_...",
      "source": "event",
      "semantic_score": 0.81,
      "recency_score": 0.72,
      "validity_score": 1.0
    }
  ]
}
```

## 9.4 Error contract (chung)

```json
{
  "error_code": "RETRIEVER_TIMEOUT",
  "component": "graph_retriever",
  "retryable": true,
  "fallback": "continue_without_graph",
  "trace_id": "trc_..."
}
```

---

## 10. Failure modes và degradation strategy

| Failure | Impact | Strategy |
|---|---|---|
| Vector DB timeout | Mất semantic context | Dùng event retrieval + lower confidence |
| Event retriever fail | Mất factual state | Dùng vector + graph nếu có, gắn warning |
| Graph DB timeout | Mất multi-hop | Continue với vector+event |
| Extraction empty | Không tạo event mới | Retry 1 lần, sau đó queue reprocess |
| Embedding service fail | Không index đủ vector | Lưu raw block + async retry queue |
| Metadata DB lag | Citation không đầy đủ | Read replica fallback, nếu fail trả low_confidence |

Nguyên tắc:
- Không trả lời "silent failure".
- Luôn ghi rõ confidence và nguồn evidence trong response.

---

## 11. Concurrency và consistency model

## 11.1 Read/write model

- Ingestion và query độc lập, dùng eventual consistency cho vector/graph.
- Metadata/event store cần read-after-write trong cùng workspace cho truy vấn current state.

## 11.2 Versioning strategy

- Mỗi event update tạo bản ghi mới, không overwrite destructive.
- Dùng `updated_by_event_id` + `valid_to` để tạo update chain.
- Query current state đọc snapshot mới nhất theo `created_at <= query_time`.

## 11.3 Idempotency

- Ingestion key: (`workspace_id`, `meeting_id`, `block_id`, `extraction_version`).
- Nếu retry ingestion trùng key thì bỏ qua hoặc merge an toàn.

---

## 12. Security và ACL

- ACL check bắt buộc tại Query Gateway và Retrieval layer.
- Query rewrite không được mở rộng scope ngoài `workspace_id` được cấp quyền.
- Audit log:
  - ai query,
  - query nào,
  - truy cập meeting nào,
  - retriever nào được dùng.

---

## 13. Semantic cache

## 13.1 Cache key

`hash(workspace_id + normalized_query + intent + time_bucket + acl_signature)`

## 13.2 Hit policy

- Similarity >= 0.92 cho normalized query embedding.
- Chỉ cache answer có confidence >= 0.75 và citation đầy đủ.

## 13.3 Invalidation

- TTL mặc định: 6 giờ.
- Invalidate theo workspace khi có meeting mới ingestion xong.
- Invalidate selective nếu event liên quan entity trong query bị update.

---

## 14. Observability, evaluation, SLO

## 14.1 Metrics bắt buộc

- Extraction quality: precision/recall theo event_type.
- Retrieval quality: precision@k, MRR, citation coverage.
- Temporal accuracy: độ đúng current-state và timeline.
- Runtime: p50/p95 latency theo từng stage.
- Safety: tỷ lệ `low_confidence` và unanswered.

## 14.2 Tracing

- OpenTelemetry trace id xuyên suốt: rewrite -> retrieve -> rerank -> generate.
- Log structured JSON cho mỗi component boundary.
- Ưu tiên tích hợp callback/observability hooks của LlamaIndex trước, sau đó mới bổ sung custom span nếu thiếu.

## 14.3 Initial SLO (v1)

- p95 end-to-end latency <= 6s (query không cần graph).
- p95 latency <= 9s (query có graph).
- Citation coverage >= 95% cho answer factual.
- Temporal accuracy >= 90% trên bộ test current_state.

---

## 15. Schema evolution và data lifecycle

## 15.1 Schema evolution

- Mỗi thay đổi schema event tăng `extraction_version`.
- Có migration adapter để đọc dữ liệu cũ (`v1.2` -> `v1.3`).
- Không phá backward compatibility cho retriever.

## 15.2 Retention policy

- Transcript raw: 12 tháng (có thể config theo workspace).
- Event và metadata: 24 tháng.
- Vector compaction chạy định kỳ (weekly) cho dữ liệu superseded low-importance.

---

## 16. Delivery roadmap (thực dụng)

### Phase 1 - Production v1
- Vector + Event retrieval (LlamaIndex-first)
- Temporal rerank + context builder (custom tối thiểu trên postprocessor)
- Query transform/rewrite + semantic cache
- Reflection bounded loop trong workflow
- ACL + tracing cơ bản

### Phase 2 - Reasoning scale
- Graph retrieval cho relationship/multi-hop (LlamaIndex graph index)
- Dynamic retrieval planner nâng cao (router/workflow)
- Better calibration cho confidence

### Phase 3 - Quality automation
- Drift detection extraction
- Auto eval pipeline + canary benchmark
- Policy-based cache invalidation nâng cao

---

## 17. Checklist sẵn sàng production

- [ ] Extraction prompt + validator + retry/fallback đã được implement.
- [ ] Interface contracts đã được enforce bằng schema validation.
- [ ] Failure matrix đã được test fault-injection.
- [ ] Temporal test suite (current_state, timeline conflict) pass.
- [ ] ACL test pass cho cross-workspace isolation.
- [ ] Observability dashboard và alerts đã bật.

Tài liệu này có thể dùng làm baseline implementation cho team engineering và MLOps, giảm ambiguity khi đi từ architecture vision sang production execution.
