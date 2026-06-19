# Project Directory Scan & Structural Analysis Report

**Date of Scan:** June 18, 2026  
**Root Directory:** `E:\Thesis`  
**System Type:** Multi-Agent Financial Analysis Platform  
**Design Theme:** Deep-Space Command Terminal Aesthetics  

---

## 1. Executive Summary

This report provides a detailed structural mapping and functional analysis of the **Multi-Agent Financial Analysis Platform** codebase. The repository is organized as a decoupled, full-stack application consisting of a **FastAPI Python Backend** (utilizing **LangGraph** for multi-agent orchestration) and a **Vite/React TypeScript Frontend**. It also includes extensive scripts for automated evaluation, data ingestion, OCR parsing, and infrastructure deployment (Docker Compose).

---

## 2. Directory Structure Tree

Below is the directory structure layout, filtered to exclude environment virtual folders and build artifacts:

```text
Thesis/
├── .chainlit/                       # UI configuration files for the legacy Chainlit prototype
│   ├── config.toml                  # Appearance, theme, and server settings
│   └── translations/                # Multi-language localization JSON files
├── backend/                         # Main Backend Codebase
│   ├── agents/                      # LangGraph agents definition
│   │   ├── coder.py                 # Coder agent generating chart code & visual grounding
│   │   ├── graph.py                 # Multi-agent state transition graph
│   │   ├── retriever.py             # Financial context retrieval agent
│   │   ├── router.py                # User intent routing agent
│   │   ├── state.py                 # Shared agent state definition
│   │   └── synthesizer.py           # Answer synthesis and final compiling agent
│   ├── api/                         # FastAPI web server and routing
│   │   ├── document.py              # Document ingestion, status checking & deduplication APIs
│   │   ├── document_store.py        # Database integration for document metadata
│   │   ├── routes.py                # Global API route aggregator
│   │   ├── schemas.py               # Request/Response Pydantic validation schemas
│   │   └── server.py                # FastAPI lifecycle, CORS, and middleware settings
│   ├── core/                        # Central configurations and core layers
│   │   ├── cache.py                 # Redis connection manager and caching layer
│   │   └── config.py                # Environment variable reader and global settings
│   ├── legacy_chainlit/             # Deprecated Chainlit app entry points
│   │   └── app.py                   # Initial implementation file
│   ├── main.py                      # Global entrypoint for running backend manually
│   ├── services/                    # Document processing and information extraction
│   │   ├── ocr/
│   │   │   └── pdf_parser.py        # Intelligent PDF parser with EasyOCR fallback mechanism
│   │   └── rag/
│   │       ├── chunker.py           # Document chunking module (MarkdownHeaderTextSplitter)
│   │       ├── cleaner.py           # Text cleaning, normalization, and formatting
│   │       └── embedder.py          # Vector embedding pipeline targeting ChromaDB
│   └── tools/                       # Utilities and sandboxed execution runtimes
│       ├── finance_dict.json        # Dictionary map for financial domain terminologies
│       └── sandbox.py               # Secure Python environment for Coder agent output evaluation
├── data/                            # File storage and Vector DB
│   ├── chroma_db/                   # ChromaDB native vector store database files
│   ├── persistence/                 # Persistent volumes for state/chat storage
│   ├── processed/                   # Parsed document chunks and intermediate MD representations
│   └── test_pdfs/                   # Sample financial files and PDF documents
├── evaluation/                      # Automated evaluation suite
│   ├── benchmark_report.csv         # Computed quantitative results of models
│   ├── run_batch_eval.py            # Automated runner for batch metrics evaluation
│   └── test_dataset.json            # Curated ground-truth QA financial test dataset
├── frontend/                        # Main Frontend Codebase (Vite + React + TS)
│   ├── landing-page/                # Landing page component
│   │   ├── src/                     # Visual design pages (Hero, Security, Visualizer)
│   │   └── package.json             # Configuration for landing UI
│   ├── src/                         # Core Application UI source
│   │   ├── api/                     # API client utilities (Axios client)
│   │   ├── components/              # Reusable React components
│   │   │   ├── Dashboard.tsx        # Financial analytics and graphs dashboard
│   │   │   ├── KnowledgeManagement.tsx # PDF management/upload interface
│   │   │   ├── MessageBubble.tsx    # Chat message with interactive citations
│   │   │   └── Sidebar.tsx          # System-wide navigation controls
│   │   ├── store/                   # Global state management
│   │   │   └── useChatStore.ts      # Zustand chat history and system parameter stores
│   │   └── main.tsx                 # Frontend main entry point
│   └── tests/                       # Playwright E2E browser tests
│       ├── chat_features.spec.ts    # Chat interactive flow E2E test suite
│       └── tip_004_visual_grounding.spec.ts # Bounding box & citation scrolling test suite
├── models/                          # GGUF models & configuration manifests
│   ├── Modelfile                    # Ollama model build configuration
│   └── Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf # Local LLM weight file
├── reports/                         # Architectural & verification documents
│   └── TECH_STACK_REPORT.md         # Technology breakdown report
├── scripts/                         # Maintenance and diagnostic scripts
│   ├── build_chromadb.py            # Pre-population of the vector database
│   ├── scan_dir.py                  # Self-scanning utility to update directories
│   └── verify_tip_002.py            # Integration test checker for PDF-RAG pipeline
└── tests/                           # Backend unit tests
    ├── test_chromadb.py             # ChromaDB connection & search test suite
    └── test_router.py               # LangGraph Routing logic tests
```

---

## 3. Core Component Walkthrough

### 3.1 Backend Architecture
The backend is structured to separate concern areas cleanly:
* **`backend/agents/` (The Multi-Agent Brain)**: Uses **LangGraph** to build a state machine workflow. The `router.py` decides the intent, `retriever.py` fetches semantic context, `coder.py` executes sandboxed code (`sandbox.py`) for custom chart creation, and `synthesizer.py` merges these inputs to format the final user response.
* **`backend/api/` (API Server)**: Fast, asynchronous API server powered by **FastAPI**. Exposes endpoints for asynchronous file uploads, status polling, and streaming LLM responses.
* **`backend/services/` (Data Pipeline)**: Extracts information from PDFs (`pdf_parser.py`), cleans it (`cleaner.py`), splits it (`chunker.py`), and embeds it (`embedder.py`) into a local **ChromaDB** store. It falls back to OCR via **EasyOCR** for scanned images.

### 3.2 Frontend Architecture
The user interface is designed around a premium "Deep Space Terminal" visual theme.
* **Vite & React (TypeScript)**: Employs React Hooks and functional components for highly interactive modular states.
* **Zustand (`frontend/src/store/`)**: Provides lightweight, atomic state management for chat streams, visual bounding boxes, and workspace settings.
* **Recharts (`DynamicChart.tsx`)**: Renders data charts dynamically generated by the backend `coder.py` agent.
* **E2E Tests (`frontend/tests/`)**: Automated **Playwright** tests verifying the interactive resizing layout and visual citations.

---

## 4. Technology Stack & Directory Mapping

| Technology Layer | Tool / Library Used | File / Folder Target |
| :--- | :--- | :--- |
| **Orchestration** | LangGraph, LangChain | `backend/agents/` |
| **Web API** | FastAPI, Uvicorn | `backend/api/` |
| **Local LLM** | Ollama, Qwen 2.5 Coder (3B) | `models/` |
| **Vector DB** | ChromaDB | `data/chroma_db/` |
| **Caching** | Redis (via redis-py) | `backend/core/cache.py` |
| **Frontend** | React, Zustand, Vite, Recharts | `frontend/src/` |
| **E2E Testing** | Playwright | `frontend/tests/` |
| **Containerization**| Docker, Docker Compose | `Dockerfile`, `docker-compose.yml` |

---

## 5. AI-Friendly Reference Guide (llms.txt Format)

For AI agents indexing this directory structure:

### Core Files
- [`backend/main.py`](file:///e:/Thesis/backend/main.py): Entrypoint for API execution.
- [`backend/agents/graph.py`](file:///e:/Thesis/backend/agents/graph.py): Core LangGraph state flow.
- [`backend/services/rag/embedder.py`](file:///e:/Thesis/backend/services/rag/embedder.py): Vector processing.
- [`frontend/src/App.tsx`](file:///e:/Thesis/frontend/src/App.tsx): Frontend mounting point.

### Architectural Rules
1. **Sandboxed Code Execution**: Any code generated by `coder.py` MUST be evaluated via the execution context in `backend/tools/sandbox.py`.
2. **State Sharing**: Do not bypass `backend/agents/state.py` when passing context between agent nodes.
3. **Responsive Citations**: Citations in Markdown are structured as `[Page X, DocName.pdf](#citation-page_X_doc_DocName.pdf)`. The frontend intercepts clicks on these anchors to visually highlights the PDF container.

---

## 6. Maintenance and Report Updates

To regenerate this directory tree or perform automated cleanups, refer to the following maintenance scripts:
- **Directory Scanner:** [`scripts/scan_dir.py`](file:///e:/Thesis/scripts/scan_dir.py)
- **Environment Cleanups:** [`scripts/cleanup_env.py`](file:///e:/Thesis/scripts/cleanup_env.py)
