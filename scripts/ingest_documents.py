"""
scripts/ingest_documents.py
----------------------------
Corre el pipeline completo de ingesta:
  1. Carga los PDFs de data/reglamentos/becas/
  2. Los divide en chunks
  3. Genera embeddings y construye el índice FAISS
  4. Guarda el índice en data/vector_store/

Uso:
    python scripts/ingest_documents.py
"""
import logging
import sys
from pathlib import Path

# Permite correr el script directamente sin instalar el paquete
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.rag.document_loader import load_documents
from app.rag.text_splitter import split_documents
from app.rag.vector_store import build_vector_store

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ingest")


def main():
    logger.info("Paso 1/3: cargando documentos PDF...")
    documentos = load_documents()
    if not documentos:
        logger.error("No se cargó ningún documento. Verificá que data/reglamentos/becas/ tenga archivos .pdf")
        return

    logger.info("Paso 2/3: dividiendo en chunks...")
    chunks = split_documents(documentos)

    logger.info("Paso 3/3: generando embeddings y construyendo índice FAISS...")
    build_vector_store(chunks, persist=True)

    logger.info("¡Listo! Índice generado con %d chunks.", len(chunks))


if __name__ == "__main__":
    main()