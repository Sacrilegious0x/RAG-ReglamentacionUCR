"""
vector_store.py
----------------
Maneja la creación, persistencia y carga del índice vectorial FAISS
que contiene los chunks de los reglamentos ya embebidos.
"""
import logging
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from app.config.settings import settings
from app.rag.embeddings import get_embeddings

logger = logging.getLogger(__name__)


def build_vector_store(chunks: list[Document], persist: bool = True) -> FAISS:
    """
    Crea un índice FAISS a partir de los chunks dados.
    Si persist=True, lo guarda en settings.vector_store_dir
    (genera index.faiss e index.pkl).
    """
    if not chunks:
        raise ValueError("No hay chunks para indexar. Corré el loader/splitter primero.")

    embeddings = get_embeddings()
    logger.info("Generando embeddings para %d chunks...", len(chunks))
    vector_store = FAISS.from_documents(chunks, embeddings)

    if persist:
        settings.vector_store_dir.mkdir(parents=True, exist_ok=True)
        vector_store.save_local(str(settings.vector_store_dir))
        logger.info("Índice FAISS guardado en %s", settings.vector_store_dir)

    return vector_store


def load_vector_store() -> FAISS:
    """
    Carga el índice FAISS previamente guardado en settings.vector_store_dir.
    Lanza FileNotFoundError si todavía no fue generado
    (correr scripts/ingest_documents.py primero).
    """
    index_path = Path(settings.vector_store_dir) / "index.faiss"
    if not index_path.exists():
        raise FileNotFoundError(
            f"No se encontró el índice en {settings.vector_store_dir}. "
            "Corré 'python scripts/ingest_documents.py' primero."
        )

    embeddings = get_embeddings()
    vector_store = FAISS.load_local(
        str(settings.vector_store_dir),
        embeddings,
        allow_dangerous_deserialization=True,  # seguro acá porque el índice lo generamos nosotros
    )
    logger.info("Índice FAISS cargado desde %s", settings.vector_store_dir)
    return vector_store