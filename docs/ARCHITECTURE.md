# IQMeetRAGv2 Architecture

## 1. Executive Summary

IQMeetRAGv2 is a sophisticated, production-grade Agentic Temporal GraphRAG (Graph-based Retrieval-Augmented Generation) system. It is specifically designed to handle complex meeting intelligence tasks, such as extracting entities, understanding temporal relationships (timelines), and generating highly contextualized insights from meeting transcripts. The system achieves sub-second latency leveraging hybrid search mechanisms, Reciprocal Rank Fusion (RRF), and multi-provider Large Language Model (LLM) orchestration.

## 2. High-Level System Architecture

The architecture of IQMeetRAGv2 is heavily centered around the LangChain ecosystem, utilizing LangChain Expression Language (LCEL) for workflow orchestration. It combines semantic vector search with graph-based relational retrieval to provide deep, accurate answers.

### 2.1 Core Components

- **Orchestration Engine:** LangChain (LCEL) acts as the backbone, defining data pipelines and agentic reflection loops.
- **API Layer:** FastAPI provides a robust, asynchronous RESTful interface.
- **Semantic Storage (Vector DB):** Qdrant is utilized for chunk-level semantic indexing of meeting transcripts.
- **Relational Storage (Graph DB):** Neo4j stores extracted entities (e.g., people, projects, action items) and their temporal/causal relationships.
- **LLM Abstraction:** LiteLLM is used to standardize interactions across multiple providers, including local deployments via Ollama, Google Gemini, and VertexAI.
- **Data Validation:** Pydantic v2 ensures strict schema adherence and temporal logic validation throughout the pipeline.

## 3. Detailed Data Flow

### 3.1 Ingestion and Indexing Pipeline
The ingestion pipeline transforms raw transcripts into a highly queryable format.

1.  **Text Splitting:** Raw meeting transcripts are divided into manageable chunks using LangChain's `RecursiveCharacterTextSplitter`. This ensures that context is preserved within token limits.
2.  **Entity & Graph Extraction:** The `LLMGraphTransformer` analyzes the chunks and extracts structural data (nodes and edges) representing entities and their relationships.
3.  **Temporal Validation:** The custom `EventValidatorChain` intercepts the extracted graph data. It enforces temporal logic (e.g., ensuring "Yesterday" logically precedes "Today") and validates the schema using Pydantic.
4.  **Storage:**
    *   *Semantic Context:* The raw text chunks and their embeddings (generated via `nomic-embed-text` or similar) are stored in Qdrant.
    *   *Relational Context:* The validated nodes and edges are persisted in Neo4j.

### 3.2 Retrieval and Reasoning Pipeline
When a user submits a query, the system employs an Agentic Router-Fusion-Rerank architecture.

1.  **Query Routing:** An LLM-based router analyzes the user's query intent. It dynamically decides whether the query requires purely semantic retrieval (Vector DB), temporal event tracking (Event Retriever), or complex relationship traversal (Graph DB).
2.  **Hybrid Retrieval & Fusion:** The `EnsembleRetriever` executes parallel searches across the selected data stores. It uses Reciprocal Rank Fusion (RRF) to seamlessly merge and rank results from Qdrant and Neo4j into a unified context pool.
3.  **Temporal Reranking:** The merged results are passed through a custom `TemporalRerankPostprocessor`. This component applies a sophisticated scoring algorithm to ensure the most relevant and temporally accurate data is prioritized:
    *   `Final Score = (Semantic * 0.25) + (Recency * 0.25) + (Validity * 0.35) + (Importance * 0.10) + (Diversity * 0.05)`
4.  **Agentic Reflection Loop:** The `AgenticQueryWorkflow` orchestrates the final answer generation. If the initial LLM answer falls below the `low_confidence_threshold` (e.g., 0.55), the agent enters a reflection loop, automatically re-querying or correcting itself up to `reflection_max_iterations`.

## 4. System Design Decisions

- **Local-First Capabilities:** By integrating Ollama, the system can run entirely on local hardware, ensuring data privacy for sensitive meeting transcripts.
- **Hybrid Approach:** Relying solely on Vector DBs fails for questions like "What happened after X?". Adding Neo4j enables structural and temporal reasoning, bridging the gap between context and causality.
- **Strict Validation:** Using Pydantic v2 and custom validators prevents "hallucinated timelines", a common failure mode in LLM-driven event extraction.
