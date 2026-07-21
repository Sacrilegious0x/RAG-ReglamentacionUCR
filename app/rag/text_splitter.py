"""
text_splitter.py
-----------------
Divide los documentos cargados en chunks aptos para embeddings.
Además, intenta detectar a qué "Artículo N" pertenece cada chunk
(buscando el último encabezado de artículo visto antes o dentro del
fragmento) para poder mostrarlo como cita en el frontend
(campo 'articulo' que espera chat_service.js).
"""
import re
import logging

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Detecta encabezados tipo "Artículo 15", "ARTÍCULO 3.", "Artículo 7º", etc.
ARTICULO_RE = re.compile(r"art[íi]culo\s+(\d+)", re.IGNORECASE)


def _detectar_articulos(texto: str) -> list[str]:
    """Devuelve la lista de números de artículo encontrados en el texto, en orden."""
    return ARTICULO_RE.findall(texto)


def split_documents(documents: list[Document]) -> list[Document]:
    """
    Divide los documentos en chunks usando RecursiveCharacterTextSplitter.
    Propaga la metadata original (source, documento, page) y agrega:
      - articulo: "Art. N" del último artículo detectado antes/dentro del chunk,
                  o "—" si no se detectó ninguno todavía en ese documento.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[Document] = []
    ultimo_articulo_por_fuente: dict[str, str] = {}

    for doc in documents:
        fuente = doc.metadata.get("source", "desconocido")
        sub_docs = splitter.split_documents([doc])

        for sub in sub_docs:
            articulos_en_chunk = _detectar_articulos(sub.page_content)
            if articulos_en_chunk:
                # Nos quedamos con el primer artículo mencionado en el chunk
                articulo_actual = f"Art. {articulos_en_chunk[0]}"
                ultimo_articulo_por_fuente[fuente] = articulo_actual
            else:
                articulo_actual = ultimo_articulo_por_fuente.get(fuente, "—")

            sub.metadata["articulo"] = articulo_actual
            chunks.append(sub)

    logger.info("Se generaron %d chunks a partir de %d documentos", len(chunks), len(documents))
    return chunks


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from app.rag.document_loader import load_documents

    docs = load_documents()
    trozos = split_documents(docs)
    print(f"Se generaron {len(trozos)} chunks.")
    if trozos:
        print("Ejemplo:", trozos[0].metadata, trozos[0].page_content[:120])