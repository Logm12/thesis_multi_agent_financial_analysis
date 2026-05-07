FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY pyproject.toml .
RUN pip install --no-cache-dir .
RUN pip install --no-cache-dir fastapi uvicorn sse-starlette python-multipart redis psycopg[binary] \
    langgraph langsmith langchain-core langchain-chroma langchain-openai langchain-text-splitters \
    langchain-experimental openai langgraph-checkpoint-postgres

# Copy project source
COPY src/ /app/src/
COPY .env /app/.env

ENV PYTHONPATH=/app/src
EXPOSE 8001

CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8001"]
