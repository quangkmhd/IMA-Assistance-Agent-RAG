# 🧠 IQMeet RAG v2

> Agentic Temporal GraphRAG for Meeting Intelligence

---

## 🚀 Overview

IQMeet RAG v2 is a **GraphRAG-based system** designed for intelligent meeting understanding.

It combines:
- Semantic retrieval (vector search)
- Graph-based reasoning (Neo4j)
- Temporal-aware logic
- Agentic LLM workflows

---

## ✨ Key Features

- **LangChain Native**  
  Built using LCEL for maximum flexibility and observability.

- **Temporal Reasoning**  
  Handles event validity, lifecycle, and superseding events.

- **GraphRAG**  
  Combines vector semantic search (Qdrant) with graph traversal (Neo4j).

- **Local-First**  
  Optimized for Ollama / LiteLLM deployment.

---

## ⚙️ Quick Start

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

---

## 🏗 Architecture

See detailed system design:

👉 [Architecture Documentation](./docs/ARCHITECTURE.md)

---

## 📂 Project Structure

```
IQMeetRAGv2/
├── CONTRIBUTING.md
├── README.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
│
├── data/
│   └── raw/                     # Raw input data for testing & development
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT_WORKFLOW.md
│   └── roadmap/
│       └── GRAPHRAG_IMPLEMENTATION_ROADMAP.md
│
├── src/
│   └── iqmeet_graphrag/
│       ├── __init__.py
│       │
│       ├── api/                # API layer (FastAPI / endpoints)
│       ├── config/             # Configuration management
│       ├── contracts/          # Data schemas / interfaces
│       ├── ingestion/          # Data ingestion pipeline
│       ├── indexing/           # Embedding & indexing logic
│       ├── retrieval/          # Hybrid retrieval (vector + graph)
│       ├── postprocessors/     # Reranking / refinement
│       ├── observability/      # Logging / tracing
│       ├── security/           # Access control / validation
│       ├── workflows/          # Agentic workflows / pipelines
│       │
│       ├── runtime.py          # Runtime orchestration
│       └── service.py          # Core service logic
│
├── tests/
│
└── .github/
    ├── pull_request_template.md
    └── workflows/              # CI/CD (to be added later)
```

---

## 🧩 Core Modules Explained

### 🔹 ingestion/
Handles raw data processing:
- Parsing meeting transcripts
- Extracting structured events
- Preparing data for indexing

---

### 🔹 indexing/
- Generate embeddings
- Store vectors in Qdrant
- Build graph entities & relationships in Neo4j

---

### 🔹 retrieval/
- Hybrid search (vector + graph)
- Uses Reciprocal Rank Fusion (RRF)
- Intelligent routing via LLM

---

### 🔹 workflows/
- Agentic pipelines
- Multi-step reasoning loops
- Reflection & refinement

---

### 🔹 postprocessors/
- Reranking results
- Temporal filtering
- Final answer polishing

---

## 🧪 Testing

```bash
pytest
```

Includes:
- API validation
- Temporal logic checks
- Citation coverage
- Access control

---

## 🤝 Contributing

See:

👉 [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 🗺 Roadmap

👉 [GraphRAG Implementation Roadmap](./docs/roadmap/GRAPHRAG_IMPLEMENTATION_ROADMAP.md)

---

## ⚡ Notes

- `.github/workflows/` is prepared for CI/CD integration
- Supports multi-LLM providers via LiteLLM
- Designed for extensibility and production scaling

---
