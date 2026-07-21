"""
retriever.py
------------
Carga el índice FAISS ya construido y expone un retriever de LangChain
listo para usar en chain.py.
"""
import logging

from app.config.settings import settings
from app.rag.vector_store import load_vector_store

logger = logging.getLogger(__name__)


def get_retriever(k: int | None = None):
    """
    Devuelve un retriever de LangChain sobre el índice FAISS persistido.

    k: cuántos chunks devolver por consulta (por defecto settings.retriever_k).

    Nota: search_type="similarity" es el default (más rápido). Si más
    adelante se obtienen resultados muy repetitivos entre sí, se puede cambiar a
    search_type="mmr" (Maximal Marginal Relevance) para diversificar,
    ej: vector_store.as_retriever(search_type="mmr", search_kwargs={"k": k, "fetch_k": 20}).
    """
    vector_store = load_vector_store()
    k = k or settings.retriever_k
    logger.info("Creando retriever con k=%d", k)
    return vector_store.as_retriever(search_kwargs={"k": k})
