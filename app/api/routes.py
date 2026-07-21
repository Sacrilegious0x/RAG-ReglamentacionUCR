"""
routes.py
---------
Endpoints de la API:
  POST /chat   -> recibe una pregunta + historial, devuelve respuesta y fuentes
  GET  /health -> chequeo de salud, usado por chat_service.js para el statusLabel
"""
import logging

from fastapi import APIRouter, HTTPException

from app.api.schemas import ChatRequest, ChatResponse, HealthResponse
from app.rag.chain import answer_question

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """
    Recibe la pregunta del usuario y el historial de la conversación,
    ejecuta el pipeline RAG (retriever + LLM) y devuelve la respuesta
    junto con las fuentes (artículo + reglamento) citadas.
    """
    try:
        historial = [mensaje.model_dump() for mensaje in request.history]
        resultado = answer_question(request.query, historial)
        return ChatResponse(**resultado)
    except ValueError as e:
        # Ej: falta la API key de Cohere en .env
        logger.error("Error de configuración: %s", e)
        raise HTTPException(status_code=500, detail=f"Error de configuración del servidor: {e}")
    except Exception as e:
        logger.exception("Error inesperado procesando la consulta: %s", request.query)
        raise HTTPException(status_code=500, detail="Ocurrió un error procesando la consulta.")


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")