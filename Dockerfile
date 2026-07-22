# Imagen base liviana con Python 3.12
FROM python:3.12-slim

# Evita que Python genere .pyc y fuerza salida sin buffer (logs en tiempo real)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias primero (aprovecha el cache de Docker: si solo cambia
# el código, esta capa no se vuelve a reconstruir)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# El índice vectorial (data/vector_store/) se copia junto con el resto del
# código si ya corriste scripts/ingest_documents.py antes de construir la
# imagen. Si preferís generarlo dentro del contenedor en vez de incluirlo
# en la imagen, descomentá la siguiente línea (requiere COHERE_API_KEY
# disponible en tiempo de build):
# RUN python scripts/ingest_documents.py

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]