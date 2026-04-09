# IQMeetRAGv2 Configuration Guide

## 1. Overview
IQMeetRAGv2 uses Pydantic `BaseSettings` for robust, type-checked configuration management. All configurations are defined in `src/iqmeet_graphrag/config/settings.py` and can be overridden using a `.env` file or direct environment variables.

## 2. Environment Variables

The system expects an `.env` file in the root directory. Below is an exhaustive list of all supported configuration parameters.

### 2.1 General Application Settings
*   `APP_NAME` (string): The application identifier. Default: `iqmeet-agentic-temporal-graphrag`
*   `ENVIRONMENT` (string): Execution environment (e.g., `local`, `dev`, `prod`). Default: `local`
*   `API_PREFIX` (string): Base path for all FastAPI routes. Default: `/api/v1`
*   `API_KEY` (string): Static API key for basic authentication. Default: `dev-key`
*   `ALLOWED_WORKSPACES` (JSON array/set): Workspaces authorized to use the API. Default: `["ws_default"]`

### 2.2 LLM and Embedding Providers
Controls which models are used for generation and embedding via LiteLLM.

*   `LLM_PROVIDER` (string): The primary LLM provider. Options: `ollama`, `vertex_ai`, `gemini_api_studio`. Default: `ollama`
*   `LLM_MODEL` (string): The specific model identifier. Default: `ollama/llama3.1`
*   `EMBEDDING_PROVIDER` (string): The provider for text embeddings. Default: `ollama`
*   `EMBEDDING_MODEL` (string): The specific embedding model. Default: `ollama/nomic-embed-text`

#### Provider-Specific Credentials
*   **Google Gemini:**
    *   `GEMINI_API_KEY` (string): Your Google Gemini API Studio key.
*   **Google Vertex AI:**
    *   `VERTEXAI_PROJECT` (string): Google Cloud Project ID.
    *   `VERTEXAI_LOCATION` (string): GCP Region (e.g., `us-central1`).
    *   `GOOGLE_APPLICATION_CREDENTIALS` (string): Path to the GCP service account JSON file.
*   **Ollama (Local):**
    *   `OLLAMA_API_BASE` (string): The URL where the Ollama service is running. Default: `http://localhost:11434`

### 2.3 Database Connections
#### Qdrant (Vector DB)
*   `QDRANT_URL` (string): Endpoint for the Qdrant instance. Default: `http://localhost:6333`
*   `QDRANT_COLLECTION` (string): Collection name for meeting chunks. Default: `iqmeet_meeting_nodes`

#### Neo4j (Graph DB)
*   `NEO4J_URL` (string): Bolt protocol endpoint. Default: `bolt://localhost:7687`
*   `NEO4J_USERNAME` (string): Database user. Default: `neo4j`
*   `NEO4J_PASSWORD` (string): Database password. Default: `neo4j_password`
*   `NEO4J_DATABASE` (string): Specific database name. Default: `neo4j`

### 2.4 Agentic Workflow Hyperparameters
Fine-tune the behavior of the retrieval and reflection loops.

*   `INPUT_CONTEXT_BUDGET` (int): Maximum number of tokens allowed in the prompt context. Default: `10000`
*   `REFLECTION_MAX_ITERATIONS` (int): Maximum number of times the agent can auto-correct its answer if confidence is low. Default: `2`
*   `LOW_CONFIDENCE_THRESHOLD` (float): The minimum confidence score (0.0 to 1.0) required to return an answer without entering reflection. Default: `0.55`
*   `EXTRACTION_VERSION` (string): Version tag for the prompt/schema used in graph extraction. Default: `v1.3.0`
*   `EXTRACTION_MAX_RETRIES` (int): Number of retries if entity extraction fails validation. Default: `1`

### 2.5 Retrieval Tuning
Controls the number of candidate documents retrieved before fusion and reranking.

*   `RETRIEVAL_TOP_K_VECTOR` (int): Number of semantic chunks retrieved from Qdrant. Default: `20`
*   `RETRIEVAL_TOP_K_EVENT` (int): Number of temporal event nodes retrieved. Default: `30`
*   `RETRIEVAL_TOP_K_GRAPH` (int): Number of related entity nodes retrieved from Neo4j. Default: `10`

## 3. Example `.env` Configurations

### Example: Fully Local Deployment (Ollama)
```ini
LLM_PROVIDER=ollama
LLM_MODEL=ollama/llama3.1
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=ollama/nomic-embed-text
OLLAMA_API_BASE=http://localhost:11434
QDRANT_URL=http://localhost:6333
NEO4J_URL=bolt://localhost:7687
```

### Example: Production Deployment (Google Gemini)
```ini
ENVIRONMENT=prod
API_KEY=your_secure_production_key
LLM_PROVIDER=gemini_api_studio
LLM_MODEL=gemini/gemini-1.5-pro-latest
EMBEDDING_PROVIDER=vertex_ai
EMBEDDING_MODEL=text-embedding-004
GEMINI_API_KEY=AIzaSy...
QDRANT_URL=https://your-qdrant-cluster.com
NEO4J_URL=bolt+s://your-neo4j-aura.com
NEO4J_PASSWORD=super_secret
LOW_CONFIDENCE_THRESHOLD=0.75
REFLECTION_MAX_ITERATIONS=3
```
