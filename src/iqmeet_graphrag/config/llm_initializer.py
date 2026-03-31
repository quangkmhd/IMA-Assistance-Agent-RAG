import os
import logging
from typing import Any

from langchain_community.chat_models.litellm import ChatLiteLLM
import litellm

from .settings import AppSettings

logger = logging.getLogger(__name__)


class LiteLLMEmbeddings:
    """Minimal embedding adapter compatible with LangChain vector stores."""

    def __init__(self, model: str, **kwargs: Any) -> None:
        self.model = model
        self.kwargs = kwargs

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = litellm.embedding(model=self.model, input=texts, **self.kwargs)
        return [item["embedding"] for item in response["data"]]

    def embed_query(self, text: str) -> list[float]:
        vectors = self.embed_documents([text])
        return vectors[0] if vectors else []


def setup_llm_and_embedding(
    settings: AppSettings,
) -> tuple[ChatLiteLLM, LiteLLMEmbeddings]:
    """
    Initialize LLM and Embedding instances for the system
    using a multi-provider strategy.
    """

    # 1. Update environment variables for LiteLLM/Google based on AppSettings
    if settings.vertexai_project:
        os.environ["VERTEXAI_PROJECT"] = settings.vertexai_project
    if settings.vertexai_location:
        os.environ["VERTEXAI_LOCATION"] = settings.vertexai_location
    if settings.google_application_credentials:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
            settings.google_application_credentials
        )
    if settings.gemini_api_key:
        os.environ["GEMINI_API_KEY"] = settings.gemini_api_key
        os.environ["GOOGLE_API_KEY"] = settings.gemini_api_key

    # 2. Configure LLM
    llm_kwargs: dict = {}
    if settings.llm_provider == "ollama":
        llm_kwargs["api_base"] = settings.ollama_api_base

    llm = ChatLiteLLM(model=settings.llm_model, **llm_kwargs)
    logger.info(
        "Initialized LLM via ChatLiteLLM. Provider: %s, Model: %s",
        settings.llm_provider,
        settings.llm_model,
    )

    # 3. Configure Embeddings
    embed_kwargs: dict = {}
    if settings.embedding_provider == "ollama":
        embed_kwargs["api_base"] = settings.ollama_api_base

    embeddings = LiteLLMEmbeddings(model=settings.embedding_model, **embed_kwargs)
    logger.info(
        "Initialized Embeddings via LiteLLMEmbeddings. Provider: %s, Model: %s",
        settings.embedding_provider,
        settings.embedding_model,
    )

    return llm, embeddings
