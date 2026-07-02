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
RUN pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install --default-timeout=1000 --retries 30 --no-cache-dir . -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install --default-timeout=1000 --retries 30 --no-cache-dir fastapi uvicorn sse-starlette python-multipart redis psycopg[binary] \
    langgraph langsmith langchain-core langchain-chroma langchain-openai langchain-text-splitters \
    langchain-experimental openai langgraph-checkpoint-postgres langchain-huggingface \
    pandas matplotlib tabulate -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install --default-timeout=1000 --retries 30 --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install --default-timeout=1000 --retries 30 --no-cache-dir easyocr -i https://mirrors.aliyun.com/pypi/simple/
RUN python -c "import easyocr; easyocr.Reader(['vi'], gpu=False)"

# Copy project source
COPY backend/ /app/backend/
COPY .env /app/.env

ENV PYTHONPATH=/app/backend
EXPOSE 8001

CMD ["python", "-c", "import os; import sys; sys.path.append('/app'); import uvicorn; uvicorn.run('api.server:app', host='0.0.0.0', port=int(os.getenv('PORT', 8001)))"]
