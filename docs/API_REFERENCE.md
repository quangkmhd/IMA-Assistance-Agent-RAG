# IQMeetRAGv2 API Reference

## 1. Overview
The IQMeetRAGv2 API is built on FastAPI and organized into modular routers. It provides endpoints for querying the RAG system, managing meeting data, triggering ingestion pipelines, and monitoring system health. All API endpoints are prefixed with `/api/v1` by default.

## 2. Core API Routers

### 2.1 Query API (`/api/v1/query`)
Handles all natural language questions directed at the meeting intelligence system.

*   **POST** `/api/v1/query`
    *   **Description:** Submits a query to the Agentic Temporal GraphRAG workflow.
    *   **Request Body (JSON):**
        *   `query` (str): The natural language question (e.g., "What were the key action items from the Q3 planning meeting?").
        *   `filters` (dict, optional): Metadata filters (e.g., `{"meeting_id": "123"}`).
    *   **Response (JSON):**
        *   `answer` (str): The generated response.
        *   `confidence` (float): The confidence score of the answer.
        *   `sources` (List[str]): List of document chunk IDs or graph node IDs used to formulate the answer.
    *   **Usage Example:**
        ```json
        // Request
        {
          "query": "Who is responsible for the new UI?",
        }
        // Response
        {
          "answer": "John Doe is responsible for the new UI design, expected by next Friday.",
          "confidence": 0.92,
          "sources": ["doc_ui_sync_chunk_4", "node_person_johndoe"]
        }
        ```

### 2.2 Ingestion API (`/api/v1/ingestion`)
Manages the process of parsing, embedding, and indexing new meeting transcripts.

*   **POST** `/api/v1/ingestion/upload`
    *   **Description:** Uploads a raw meeting transcript file and triggers the indexing pipeline (Text Splitting -> Graph Extraction -> Vector/Graph DB storage).
    *   **Form Data:**
        *   `file` (UploadFile): The transcript file (.txt, .vtt, .json).
        *   `meeting_metadata` (JSON string): Additional context (date, participants).
    *   **Response (JSON):**
        *   `status` (str): "processing" or "completed".
        *   `job_id` (str): ID to track ingestion status.

### 2.3 Meetings & Events API (`/api/v1/meetings`, `/api/v1/events`)
CRUD operations for managed meeting entities.

*   **GET** `/api/v1/meetings`
    *   **Description:** Lists all indexed meetings.
*   **GET** `/api/v1/meetings/{meeting_id}`
    *   **Description:** Retrieves metadata and summary for a specific meeting.
*   **GET** `/api/v1/events`
    *   **Description:** Retrieves a timeline of extracted events across all or filtered meetings.

### 2.4 System API (`/api/v1/health`, `/api/v1/admin`)
*   **GET** `/api/v1/health`
    *   **Description:** Returns the operational status of the API, Qdrant connection, and Neo4j connection.

## 3. Core Python Classes & Methods

If integrating directly via Python, the following classes in `iqmeet_graphrag` are essential:

### `iqmeet_graphrag.workflows.query_workflow.AgenticQueryWorkflow`
The main orchestrator for answering queries.
*   `query(question: str) -> dict`: Executes the router-fusion-rerank loop and returns the answer, confidence, and sources.

### `iqmeet_graphrag.retrieval.fusion.HybridRetriever`
Handles multi-store data retrieval.
*   `get_context(query: str, top_k: int = 5) -> List[Document]`: Bypasses the agentic loop for fast, semantic-only lookups from Qdrant.

### `iqmeet_graphrag.ingestion.extractor.LLMGraphTransformer`
Converts raw text into structured graph data.
*   `extract(text: str) -> GraphData`: Analyzes text and returns a structured representation of nodes and edges ready for Neo4j insertion.
