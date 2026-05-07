# Directory Scan: Thesis - Financial Analyzer

**Date:** 2026-05-01
**Project Root:** `e:\Thesis`

## Project Overview
This project appears to be a Financial Analyzer leveraging LLMs (Large Language Models), RAG (Retrieval-Augmented Generation), and Graph-based agent orchestration. It supports both cloud APIs (Gemini) and local models (Qwen via Ollama).

---

## Directory Structure

### 📂 `src/` (Source Code)
The core logic of the application.
- **📂 `agents/`**: Contains agentic logic.
  - `graph.py`: Likely defines the LangGraph workflow/topology.
  - `router.py`: Handles routing between different nodes or agents.
  - `state.py`: Defines the shared state object for the agent graph.
- **📂 `data_processing/`**: Pipeline for preparing financial data.
  - `chunker.py`: Splits large documents into manageable segments.
  - `cleaner.py`: Sanitizes and formats raw text extracted from PDFs.
  - `embedder.py`: Handles vectorization for RAG.

### 📂 `scripts/` (Utilities & Maintenance)
Support scripts for setup and testing.
- `build_chromadb.py`: Initializes the Chroma vector database.
- `build_graphdb.py`: Sets up the graph database (e.g., Neo4j or similar).
- `extract_pdf.py`: Extracts text from raw financial PDF documents.
- `test_gemini_api.py` / `test_qwen.py`: Verification scripts for LLM providers.
- `test_router.py`: Tests the agent routing logic.
- `test_langsmith.py`: Integration script for LangSmith observability.

### 📂 `models/` (Local LLM Storage)
- `Modelfile`: Configuration for Ollama.
- `Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf`: Local model file.
- **📂 `ollama/`**: Ollama-specific configuration or data.

### 📂 `data/` (Data Persistence)
- **📂 `raw/`**: Original PDF files.
- **📂 `processed/`**: Extracted and cleaned text files.
- **📂 `chroma_db/`**: Persistent storage for the vector database.

### 📂 `.agent/`
- Workspace-specific agent configurations and skills.

---

## Configuration Files
- `.env`: Contains sensitive API keys and environment variables.
- `pyproject.toml`: Defines Python dependencies and project metadata.
- `tess_log.txt`: Log file likely related to Tesseract OCR or system testing.
- `test_router_output.txt`: Captured output from routing tests.

---

## Key Technologies Observed
- **Frameworks:** LangGraph, LangChain.
- **Database:** ChromaDB (Vector), GraphDB.
- **Models:** Gemini (Google), Qwen (Alibaba/Ollama).
- **Tooling:** Ruff (Linting), PDF Extraction tools.
