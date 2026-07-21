"""
document_loader.py
-------------------
Carga los reglamentos en PDF y los convierte en objetos
Document de LangChain, agregando metadata útil (nombre del archivo,
número de página) que luego se usará para citar artículos/reglamentos
en la respuesta del chat.
"""
import logging
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

from app.config.settings import settings

logger = logging.getLogger(__name__)


def _nombre_reglamento(path: Path) -> str:
    """
    Convierte el nombre de archivo en un nombre legible de reglamento.
    Ej: 'Reglamento_Estudiantil.pdf' -> 'Reglamento Estudiantil'
    """
    return path.stem.replace("_", " ").strip()


def load_documents(raw_dir: Path | None = None) -> list[Document]:
    """
    Recorre todos los PDFs en raw_dir (por defecto settings.raw_data_dir)
    y devuelve una lista de Document, uno por página, con metadata:
      - source: nombre del archivo
      - documento: nombre legible del reglamento
      - page: número de página (0-indexed, tal como lo entrega PyPDFLoader)
    """
    raw_dir = raw_dir or settings.raw_data_dir
    raw_dir = Path(raw_dir)

    if not raw_dir.exists():
        raise FileNotFoundError(f"No existe el directorio de datos crudos: {raw_dir}")

    pdf_files = sorted(raw_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning("No se encontraron archivos PDF en %s", raw_dir)
        return []

    all_docs: list[Document] = []
    for pdf_path in pdf_files:
        logger.info("Cargando %s", pdf_path.name)
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()

        documento_legible = _nombre_reglamento(pdf_path)
        for doc in docs:
            doc.metadata["source"] = pdf_path.name
            doc.metadata["documento"] = documento_legible
            # PyPDFLoader ya agrega 'page', la dejamos tal cual

        all_docs.extend(docs)

    logger.info("Total de páginas cargadas: %d (de %d archivos)", len(all_docs), len(pdf_files))
    return all_docs


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    documentos = load_documents()
    print(f"Se cargaron {len(documentos)} páginas.")
    if documentos:
        print("Ejemplo de metadata:", documentos[0].metadata)