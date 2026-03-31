# IQMeet RAG v2

Agentic Temporal GraphRAG for Meeting Intelligence.

## Key Features
- **LangChain Native**: Built using LCEL for maximum flexibility and observability.
- **Temporal Reasoning**: Built-in understanding of event validity, lifecycles, and superseding events.
- **GraphRAG**: Combines vector semantic search with Neo4j relationship traversal.
- **Local-First**: Optimized for Ollama/LiteLLM usage.

## Quick Start
```bash
# 1. Install dependencies
pip install .

# 2. Configure environment
export GEMINI_API_KEY=your_key
export QDRANT_URL=http://localhost:6333
export NEO4J_URL=bolt://localhost:7687

# 3. Run application
python -m iqmeet_graphrag.app
```

## Architecture
See [ARCHITECTURE_PRODUCTION.md](ARCHITECTURE_PRODUCTION.md) for a detailed technical breakdown.
