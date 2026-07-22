"""
Configuración centralizada del proyecto ReglamentosRAG.
Lee variables desde el archivo .env usando pydantic-settings.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Rutas del proyecto ---
    base_dir: Path = Path(__file__).resolve().parents[2]
    raw_data_dir: Path = base_dir / "data" / "reglamentos" / "becas"
    vector_store_dir: Path = base_dir / "data" / "vector_store"

    # --- Text splitting ---
    chunk_size: int = 1000
    chunk_overlap: int = 150

    # --- Embeddings ---
    # "cohere", "openai" o "gemini"
    embeddings_provider: str = "cohere"
    cohere_api_key: str | None = None
    cohere_embeddings_model: str = "embed-multilingual-v3.0"

    # --- LLM (para chain.py más adelante) ---
    llm_provider: str = "cohere"
    cohere_llm_model: str = "command-a-03-2025"
    llm_temperature: float = 0.0

    # --- Retriever ---
    retriever_k: int = 3


settings = Settings()