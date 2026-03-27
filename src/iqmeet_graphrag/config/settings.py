from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    app_name: str = "iqmeet-agentic-temporal-graphrag"
    environment: str = "local"

    llm_model: str = Field(default="llama3.1")
    embedding_model: str = Field(default="BAAI/bge-small-en-v1.5")

    qdrant_url: str = Field(default="http://localhost:6333")
    qdrant_collection: str = Field(default="iqmeet_meeting_nodes")

    neo4j_url: str = Field(default="bolt://localhost:7687")
    neo4j_username: str = Field(default="neo4j")
    neo4j_password: str = Field(default="neo4j_password")
    neo4j_database: str = Field(default="neo4j")

    input_context_budget: int = 10_000
    reflection_max_iterations: int = 2
    extraction_version: str = "v1.3.0"
    extraction_max_retries: int = 1
    low_confidence_threshold: float = 0.55

    retrieval_top_k_vector: int = 20
    retrieval_top_k_event: int = 30
    retrieval_top_k_graph: int = 10

    api_prefix: str = "/api/v1"
    api_key: str = "dev-key"
    allowed_workspaces: set[str] = Field(default_factory=lambda: {"ws_default"})
