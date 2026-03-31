# IQMeet GraphRAG Roadmap

## Current Capabilities

### Infrastructure
- Multi-provider LLM support via LiteLLM.
- Qdrant-backed vector storage.
- Neo4j-backed graph relationship storage.

### Ingestion & Indexing
- High-fidelity event extraction using structured LLM outputs.
- Temporal overlap and schema validation for meeting events.
- Automated graph entity/relationship extraction.

### Retrieval & Reasoning
- LLM-based intelligent routing between data stores.
- Hybrid retrieval with Reciprocal Rank Fusion.
- Temporal hybrid reranking with multi-factor scoring.
- Agentic reflection loop for iterative answer refinement.

## Future Sprints
- [ ] LangGraph Integration: Advanced state management for agentic loops.
- [ ] Cypher Generation: Direct graph querying via `GraphCypherQAChain`.
- [ ] Evaluation: Integrated Ragas/LangSmith performance benchmarking.
