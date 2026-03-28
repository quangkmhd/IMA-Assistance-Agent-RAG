from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    app_name: str = "iqmeet-agentic-temporal-graphrag"
    environment: str = "local"

    llm_provider: str = Field(default="ollama", description="Lựa chọn: vertex_ai, gemini_ai_studio, ollama")
    llm_model: str = Field(default="ollama/llama3.1")
    
    embedding_provider: str = Field(default="ollama")
    embedding_model: str = Field(default="ollama/nomic-embed-text")

    # Vertex AI settings
    vertexai_project: str | None = Field(default=None)
    vertexai_location: str | None = Field(default=None)
    google_application_credentials: str | None = Field(default=None)
    
    # Gemini API Studio
    gemini_api_key: str | None = Field(default=None)
    
    # Ollama settings
    ollama_api_base: str = Field(default="http://localhost:11434")
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
