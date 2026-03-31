# IQMeet GraphRAG: Architecture Blueprint

## 1. Executive Summary
IQMeet GraphRAG is a production-grade system designed for temporal reasoning and relationship extraction from meeting transcripts. The system is built using LangChain and LCEL (LangChain Expression Language) for transparency, debugging, and native support for multi-provider LLMs via LiteLLM.

## 2. Core Framework Stack
- **Orchestration**: LangChain (LCEL) + Custom Agentic Loop
- **Vector Database**: Qdrant (via `langchain-qdrant`)
- **Graph Database**: Neo4j (via `langchain-community`)
- **LLM/Embeddings**: LiteLLM (supporting Gemini, VertexAI, Ollama)
- **Schema/Validation**: Pydantic v2

## 3. Data Ingestion & Indexing
### Ingestion Pipeline
- **Splitter**: `RecursiveCharacterTextSplitter` (LangChain)
- **Extraction**: `with_structured_output` for high-fidelity event extraction.
- **Validation**: Custom `EventValidatorChain` (Temporal overlap & Schema check).

### Hybrid Indexing
- **Vector**: Chunk-level semantic indexing in Qdrant.
- **Graph**: `LLMGraphTransformer` extracts entities and relationships into Neo4j.

## 4. Retrieval & Reasoning
The system uses a **Router-Fusion-Rerank** architecture:

1. **Routing**: LLM decides between Vector, Event (Temporal), or Graph retrievers.
2. **Fusion**: `EnsembleRetriever` uses Reciprocal Rank Fusion (RRF) to merge results.
3. **Temporal Reranking**: Custom `TemporalRerankPostprocessor` applies hybrid scoring:
   `Score = Semantic*0.25 + Recency*0.25 + Validity*0.35 + Importance*0.10 + Diversity*0.05`

## 5. Agentic Query Workflow
The `AgenticQueryWorkflow` implements a reflection loop:
- Iteratively refines the answer if confidence is low.
- Tracks source documents (`source_documents`) for automatic citation generation.
