"""
embeddings.py
-------------
Devuelve el modelo de embeddings a usar, según settings.embeddings_provider.
Soporta:
  - "cohere": requiere COHERE_API_KEY en .env (recomendado, buen soporte multilingue/espanol)
  - "openai": requiere OPENAI_API_KEY en .env
  - "huggingface": corre local, no requiere API key (mas lento, sin costo)
"""
import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)


def get_embeddings():
    provider = settings.embeddings_provider.lower()

    if provider == "cohere":
        from langchain_cohere import CohereEmbeddings

        if not settings.cohere_api_key:
            raise ValueError(
                "embeddings_provider='cohere' pero no se encontro COHERE_API_KEY en .env"
            )
        logger.info("Usando embeddings de Cohere: %s", settings.cohere_embeddings_model)
        return CohereEmbeddings(
            model=settings.cohere_embeddings_model,
            cohere_api_key=settings.cohere_api_key,
        )

    else:
        raise ValueError(
            f"embeddings_provider desconocido: '{provider}'. Usa 'cohere' o agrega soporte para otros modelos."
        )