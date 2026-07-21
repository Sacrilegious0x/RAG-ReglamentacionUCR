"""
schemas.py
----------
Modelos Pydantic para la API. Definen la forma exacta del request y
response de /chat, que deben coincidir con lo que espera chat_service.js:

  Request:  { "query": "...", "history": [{"role": "user", "content": "..."}, ...] }
  Response: { "answer": "...", "sources": [{"articulo": "...", "documento": "..."}] }
"""
from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Pregunta del usuario")
    history: list[Message] = Field(default_factory=list, description="Turnos previos de la conversación")


class Source(BaseModel):
    articulo: str
    documento: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str = "ok"