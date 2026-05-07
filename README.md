# Multi-Agent Financial Analysis Platform 

> A state-of-the-art financial document parser and intelligent multi-agent Q&A platform built on top of LangGraph, FastAPI, ChromaDB, and React. Inspired by deep-space command terminal aesthetics.

---

## System Architecture

### Multi-Agent LangGraph Orchestration
The core of the system is an autonomous multi-agent graph powered by **LangGraph**. It routes user requests, retrieves context, writes python visualization code, and synthesizes final answers.

```mermaid
graph TD
    User([User Prompt]) --> Router{Router Agent}
    Router -- "Financial Q&A" --> Retriever[Retriever Agent]
    Router -- "Data Visualization" --> Coder[Coder Agent]
    
    Retriever --> Synthesizer[Synthesizer Agent]
    Coder --> Synthesizer
    
    Synthesizer --> Output([Final Response + Charts])
```

### Full-Stack System Topology
```mermaid
graph TB
    subgraph "Frontend"
        UI[React App + Zustand + Recharts]
    end

    subgraph "Backend Services"
        FastAPI[FastAPI Server]
        LangGraph[LangGraph Engine]
    end

    subgraph "Data & Cache Layer"
        Chroma[(ChromaDB Vector Store)]
        Postgres[(PostgreSQL State Store)]
        Redis[(Redis Cache)]
    end

    UI -->|Async PDF Upload / Chat| FastAPI
    FastAPI --> LangGraph
    LangGraph --> Chroma
    LangGraph --> Postgres
    FastAPI --> Redis
```

---

## ✨ Features

- **Non-blocking Async PDF Upload**: Drag & Drop financial reports; parsed asynchronously using background tasks.
- **LangGraph Multi-Agent Router**: Dynamically routes requests based on user intent (e.g., plain Q&A vs. data visualization).
- **Dynamic Data Visualization**: Coder agent generates code to extract JSON data blocks which React parses and renders into beautiful, interactive **Recharts** (Bar/Line charts) on the fly.
- **High Performance Caching**: Redis-backed cache layer for fast response times.
- **State Persistence**: PostgreSQL-backed postgres checkpointer for LangGraph agent session persistence.

---

## 🚀 Quick Start

### 1. Run Everything with Docker Compose (<3 minutes)

Make sure you have Docker and Docker Compose installed, then run:

```bash
docker compose up -d --build
```

This starts all 4 services:
* **Frontend**: `http://localhost:5173`
* **FastAPI Backend**: `http://localhost:8001`
* **PostgreSQL Database**: `localhost:5433`
* **Redis Cache**: `localhost:6380`

### 2. Manual Source Installation

#### Backend Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```
2. Configure your `.env` file (see [Configuration](#-configuration)).
3. Start the FastAPI server:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
   ```

#### Frontend Setup

1. Install Node dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Run the Vite development server:
   ```bash
   npm run dev
   ```

---

## 🛠️ Configuration

The application is configured using environment variables in the root [.env](file:///.env) file.

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API Key for embeddings and agent LLMs | - | **Yes** |
| `POSTGRES_URL` | PostgreSQL connection string for LangGraph states | `postgresql://langgraph:langgraph_pass@postgres:5432/financial_analyzer` | Yes |
| `REDIS_URL` | Redis cache connection string | `redis://redis:6379/0` | Yes |
| `LANGCHAIN_TRACING_V2` | Enable LangSmith tracing | `true` | No |
| `LANGCHAIN_API_KEY` | LangSmith API Key | - | No |

---

## 🔌 API Reference

### Document Management
* **`POST /api/v1/document/upload`**: Async PDF upload. Returns `task_id` for tracking.
* **`GET /api/v1/document/status/{task_id}`**: Polling status of PDF ingestion and vectorization.

### Agentic Chat
* **`POST /api/v1/chat/message`**: Send a message to the Multi-Agent system. Returns response with optional `chart_data` block.

---

## 🤖 llms.txt (AI-Friendly Reference)

For AI agents and crawlers indexing this repository:

### Core Files
- `src/main.py`: Application entry point.
- `src/api/server.py`: FastAPI server configuration.
- `src/agents/graph.py`: Main LangGraph multi-agent definition.
- `src/data_processing/embedder.py`: ChromaDB embedding pipeline.

### Key Concepts
- **State Store**: PostgreSQL checkpointer persists chat sessions.
- **Chunking Strategy**: MarkdownHeaderTextSplitter with flattening metadata to avoid nested dictionary errors in ChromaDB.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
