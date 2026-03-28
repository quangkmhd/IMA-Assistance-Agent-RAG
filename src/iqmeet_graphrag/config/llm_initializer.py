import os
import logging
from llama_index.core import Settings
from llama_index.llms.litellm import LiteLLM
from llama_index.embeddings.litellm import LiteLLMEmbedding

from .settings import AppSettings

logger = logging.getLogger(__name__)

def setup_llm_and_embedding(settings: AppSettings):
    """
    Initialize global Settings.llm and Settings.embed_model for LlamaIndex 
    using LiteLLM multi-provider strategy.
    """
    
    # 1. Update environment variables for Litellm/Google based on AppSettings
    if settings.vertexai_project:
        os.environ["VERTEXAI_PROJECT"] = settings.vertexai_project
    if settings.vertexai_location:
        os.environ["VERTEXAI_LOCATION"] = settings.vertexai_location
    if settings.google_application_credentials:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials
    if settings.gemini_api_key:
        os.environ["GEMINI_API_KEY"] = settings.gemini_api_key
        os.environ["GOOGLE_API_KEY"] = settings.gemini_api_key

    # 2. Configure LLM
    llm_kwargs = {}
    if settings.llm_provider == "ollama":
        llm_kwargs["api_base"] = settings.ollama_api_base
        
    Settings.llm = LiteLLM(
        model=settings.llm_model,
        **llm_kwargs
    )
    logger.info(f"Initialized Global LLM via LiteLLM. Provider: {settings.llm_provider}, Model: {settings.llm_model}")
    
    # 3. Configure Embeddings
    embed_kwargs = {}
    if settings.embedding_provider == "ollama":
        embed_kwargs["api_base"] = settings.ollama_api_base
    
    # In LlamaIndex, litellm embedding class needs model_name
    Settings.embed_model = LiteLLMEmbedding(
        model_name=settings.embedding_model,
        **embed_kwargs
    )
    logger.info(f"Initialized Global Embedding via LiteLLM. Provider: {settings.embedding_provider}, Model: {settings.embedding_model}")

