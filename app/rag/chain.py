"""
chain.py
--------
Une el retriever (búsqueda de contexto) con el LLM de Cohere para generar
respuestas ancladas en los reglamentos, devolviendo también las fuentes
citadas en el formato que espera el frontend (chat_service.js):
    { "answer": "...", "sources": [{"articulo": "...", "documento": "..."}] }
"""
import logging

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_cohere import ChatCohere

from app.config.settings import settings
from app.rag.prompt import SYSTEM_PROMPT
from app.rag.retriever import get_retriever

logger = logging.getLogger(__name__)

# Frases que indican que el modelo no encontró información relevante en el
# contexto. Si la respuesta contiene alguna de estas, no tiene sentido citar
# fuentes (evita citar artículos "de relleno" que el retriever trajo pero
# que el modelo terminó descartando).
_MARCADORES_SIN_RESPUESTA = [
    "no encontré esa información",
    "no encontré información",
    "no encontré datos",
    "no cuento con esa información",
]


def _respuesta_indica_sin_info(respuesta: str) -> bool:
    respuesta_lower = respuesta.lower()
    return any(marcador in respuesta_lower for marcador in _MARCADORES_SIN_RESPUESTA)


def _format_docs(docs: list[Document]) -> str:
    """Concatena los chunks recuperados en un solo bloque de texto para el prompt."""
    partes = []
    for doc in docs:
        articulo = doc.metadata.get("articulo", "—")
        documento = doc.metadata.get("documento", "Documento no identificado")
        partes.append(f"[{documento} | {articulo}]\n{doc.page_content}")
    return "\n\n---\n\n".join(partes)


def _extraer_fuentes(docs: list[Document]) -> list[dict]:
    """Deduplica y da formato a las fuentes para el campo 'sources' de la respuesta."""
    vistos = set()
    fuentes = []
    for doc in docs:
        articulo = doc.metadata.get("articulo", "—")
        documento = doc.metadata.get("documento", "Documento no identificado")
        clave = (articulo, documento)
        if clave in vistos:
            continue
        vistos.add(clave)
        fuentes.append({"articulo": articulo, "documento": documento})
    return fuentes


def _formatear_historial(history: list[dict] | None) -> str:
    """Convierte el historial de chat (lista de {role, content}) en texto legible."""
    if not history:
        return "(sin conversación previa)"
    lineas = []
    for turno in history[-6:]:  # solo los últimos 3 intercambios, para no inflar el prompt
        rol = "Estudiante" if turno.get("role") == "user" else "Asistente"
        lineas.append(f"{rol}: {turno.get('content', '')}")
    return "\n".join(lineas)


def _build_llm() -> ChatCohere:
    if not settings.cohere_api_key:
        raise ValueError("No se encontró COHERE_API_KEY en .env")
    return ChatCohere(
        model=settings.cohere_llm_model,
        temperature=settings.llm_temperature,
        cohere_api_key=settings.cohere_api_key,
    )


def answer_question(query: str, history: list[dict] | None = None) -> dict:
    """
    Punto de entrada principal: recibe una pregunta (y opcionalmente el
    historial de la conversación) y devuelve {"answer": str, "sources": list[dict]}.
    """
    retriever = get_retriever()
    docs = retriever.invoke(query)

    if not docs:
        logger.warning("No se encontraron chunks relevantes para: %s", query)
        return {
            "answer": "No encontré información relacionada en los reglamentos consultados.",
            "sources": [],
        }

    contexto = _format_docs(docs)
    historial = _formatear_historial(history)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Historial de la conversación:\n{historial}\n\nPregunta actual: {question}"),
    ])

    llm = _build_llm()
    chain = prompt | llm | StrOutputParser()

    logger.info("Generando respuesta con %s...", settings.cohere_llm_model)
    respuesta = chain.invoke({
        "context": contexto,
        "historial": historial,
        "question": query,
    })

    return {
        "answer": respuesta,
        "sources": [] if _respuesta_indica_sin_info(respuesta) else _extraer_fuentes(docs),
    }
