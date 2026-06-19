# Thesis Multi-Agent Financial Analysis System

This repository contains the source code for a Multi-Agent Financial Report Analysis System. The application consists of a FastAPI backend, a React frontend, and a Developer/Testing interface powered by Chainlit.

## Architecture Overview

The system uses three primary LLM models specialized for different agent roles:
*   **Router**: Decides the routing logic based on user queries (e.g., retrieving facts vs. running custom code calculations).
*   **Retriever**: Extracts text and tables from vectorized PDF financial reports.
*   **Coder**: Generates and executes Python code locally inside a sandbox to perform calculations on retrieved financial metrics, with automatic compiler feedback for self-healing.

## Prerequisites

Ensure you have the following installed on your machine:
*   **Docker** and **Docker Compose**
*   **Python 3.10** or higher
*   **Node.js** (v18 or higher) and npm/yarn
*   **Ollama** (for local model hosting, e.g., Qwen 2.5 Coder)

---

## Configuration

Before starting, prepare the environment variables. Create a `.env` file in the root directory based on the following template:

```env
# Open AI API
OPENAI_API_KEY=your_openai_api_key_here

# Local Ollama URL
OLLAMA_BASE_URL=http://localhost:11434/v1

# Databases (Defaults for local development outside docker network)
POSTGRES_URL=postgresql://langgraph:langgraph_pass@localhost:5433/financial_analyzer
REDIS_URL=redis://localhost:6380/0
```

---

## Deployment Steps

### 1. Launch Databases via Docker

Start the PostgreSQL and Redis containers configured in `docker-compose.yml`:

```bash
docker compose up -d postgres redis
```

This maps PostgreSQL to port `5433` and Redis to port `6380` on localhost.

### 2. Set Up the Backend Server

1. Navigate to the project root directory.
2. Initialize and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
3. Install the Python dependencies:
   ```bash
   pip install --upgrade pip
   pip install -e .
   ```
4. Run the database migration script to set up tables:
   ```bash
   python backend/core/database.py
   ```
5. Start the FastAPI backend server:
   ```bash
   python -m uvicorn backend.api.server:app --host 0.0.0.0 --port 8001 --reload
   ```

### 3. Set Up the Frontend Client

1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Start the Vite React development server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your browser to access the client interface.

### 4. Run the Chainlit Developer UI

The Chainlit cockpit provides a direct developer/testing interface to view detailed agent thoughts, execution logs, and compiler tracebacks.

1. Keep your virtual environment active in the project root folder.
2. Start Chainlit:
   ```bash
   python -m chainlit run backend/legacy_chainlit/app.py -h --port 8002
   ```
3. Open `http://localhost:8002` in your browser.

---

## Running Evaluations and Tests

To run the unit and integration tests:
```bash
pytest
```
