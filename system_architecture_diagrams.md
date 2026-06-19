# System Architecture Diagrams — Multi-Agent Financial Analysis System

---

## Diagram 1 — System Overview

```mermaid
graph TD
    subgraph FE ["Frontend (Vite · React · TypeScript)"]
        UI["User Interface\nChat · Upload · Auth"]
    end

    subgraph BE ["Backend Services (FastAPI)"]
        API["REST API Gateway\nJWT Auth · SSE"]
        QUEUE["Distributed Task Queue\n(Celery / ARQ Broker)"]
    end

    subgraph WORKER ["Background Worker Tier (Python GIL Isolation)"]
        PARSER["PDF Ingestion Worker\n(PyMuPDF + EasyOCR)"]
        CHUNKER["Text Cleaner & Chunker"]
        EMBEDDER["Embedding Generator\n(OpenAI text-embedding-3-small)"]
        
        PARSER --> CHUNKER --> EMBEDDER
    end

    subgraph AGENT ["Multi-Agent Orchestration (LangGraph)"]
        ROUTER["Router Agent\nIntent Classifier"]
        RETRIEVER["Retriever Agent\nRAG Search"]
        CODER["Coder Agent\nPython Code Generator"]
        SANDBOX["Security Sandbox\nAST Validator + Safe REPL"]
        SYNTH["Synthesizer Agent\nReport Composer"]
        XAI["XAI Translation Layer\n(CoT & Audit Trail Explainer)"]

        ROUTER -->|retrieve| RETRIEVER
        ROUTER -->|code| RETRIEVER
        ROUTER -->|out of scope| SYNTH
        RETRIEVER -->|retrieve path| SYNTH
        RETRIEVER -->|code path| CODER
        CODER --> SANDBOX
        SANDBOX -->|success| SYNTH
        SANDBOX -->|error, retry up to 5x| CODER
        SYNTH -->|raw report & trace| XAI
    end

    subgraph STORE ["Storage & Cache"]
        REDIS[("Redis\nPDF Cache & Task Queue Broker")]
        CHROMA[("ChromaDB\nVector Database (Financial Chunks)")]
        PG[("PostgreSQL\nPersistent State Store (LangGraph Checkpoints & Session Hydration)")]
    end

    subgraph EVAL ["Automated Evaluation Pipeline"]
        RAGAS["RAGAS Evaluator\n(Comparative Experiments)"]
    end

    UI -->|REST / SSE| API
    API -->|asynchronous PDF upload| QUEUE
    QUEUE -->|enqueue tasks via Redis| REDIS
    REDIS -->|consume tasks| WORKER
    EMBEDDER -->|write document vectors| CHROMA
    
    API -->|user query| AGENT
    AGENT -->|retrieve vectors| CHROMA
    AGENT -->|read/write checkpoints| PG
    API -->|auth & metadata| PG
    
    XAI -->|explainable report & audit trail| API
    API -->|stream response| UI
    
    CHROMA -->|ground truth vectors| RAGAS
    PG -->|session state trace| RAGAS
    RAGAS -->|evaluation scores| EXP["Ch. 4 Experimental Results"]

    classDef fe      fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f
    classDef api     fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d
    classDef worker  fill:#fef9c3,stroke:#ca8a04,stroke-width:2px,color:#713f12
    classDef agent   fill:#ede9fe,stroke:#7c3aed,stroke-width:2px,color:#3b0764
    classDef sandbox fill:#fce7f3,stroke:#db2777,stroke-width:2px,color:#831843
    classDef store   fill:#f1f5f9,stroke:#475569,stroke-width:2px,color:#1e293b
    classDef eval    fill:#ffe4e6,stroke:#f43f5e,stroke-width:2px,color:#881337

    class UI fe
    class API,QUEUE api
    class PARSER,CHUNKER,EMBEDDER worker
    class ROUTER,RETRIEVER,CODER,SYNTH,XAI agent
    class SANDBOX sandbox
    class REDIS,CHROMA,PG store
    class RAGAS,EXP eval

    style FE    fill:#eff6ff,stroke:#3b82f6,stroke-width:1.5px
    style BE    fill:#f0fdf4,stroke:#22c55e,stroke-width:1.5px
    style WORKER fill:#fefce8,stroke:#eab308,stroke-width:1.5px
    style AGENT fill:#f5f3ff,stroke:#8b5cf6,stroke-width:1.5px
    style STORE fill:#f8fafc,stroke:#64748b,stroke-width:1.5px
    style EVAL  fill:#fff1f2,stroke:#fda4af,stroke-width:1.5px
```

---

## Diagram 2 — LangGraph Agent Pipeline

```mermaid
flowchart LR
    START([User Query]) --> ROUTER

    subgraph GRAPH ["LangGraph Stateful Workflow"]
        direction LR

        ROUTER["Router\nClassify intent"]
        RETRIEVER["Retriever\nVector search"]
        
        subgraph CODE_PATH ["Code Execution Path"]
            direction TB
            CODER["Coder\nGenerate Python"]
            SANDBOX["Security Sandbox\nAST check + Safe REPL"]
            RETRY{{"Error?\nretry < 5"}}

            CODER --> SANDBOX --> RETRY
            RETRY -->|yes, inject last error| CODER
        end

        SYNTH["Synthesizer\nCompose report"]
        XAI["XAI Translation Layer\nGenerate CoT & Audit Trail"]

        ROUTER -->|retrieve| RETRIEVER
        ROUTER -->|code| RETRIEVER
        ROUTER -->|out of scope| SYNTH
        RETRIEVER -->|retrieve path| SYNTH
        RETRIEVER -->|code path| CODER
        RETRY -->|no error| SYNTH
        SYNTH --> XAI
    end

    subgraph STATE_PERSIST ["State Store Tier"]
        PG[("PostgreSQL State Store\nSession Hydration & Checkpoints")]
    end
    
    subgraph EVAL ["Evaluation Tier"]
        RAGAS["RAGAS Evaluator\n(Chapter 4 Comparative Tests)"]
    end

    GRAPH <-->|persist state / load checkpoints| PG
    RETRIEVER <-->|retrieve from| CHROMA[("ChromaDB Vector Store")]
    
    PG -->|read session states| RAGAS
    CHROMA -->|read context chunks| RAGAS

    XAI --> END([Streamed Response\nMarkdown · Table · Charts + Explanations])

    classDef router   fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f
    classDef rag      fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d
    classDef coder    fill:#fef9c3,stroke:#ca8a04,stroke-width:2px,color:#713f12
    classDef sandbox  fill:#fce7f3,stroke:#db2777,stroke-width:2px,color:#831843
    classDef synth    fill:#ede9fe,stroke:#7c3aed,stroke-width:2px,color:#3b0764
    classDef endpoint fill:#f1f5f9,stroke:#475569,stroke-width:2px,color:#1e293b
    classDef store    fill:#f8fafc,stroke:#64748b,stroke-width:2px,color:#1e293b
    classDef eval     fill:#ffe4e6,stroke:#f43f5e,stroke-width:2px,color:#881337

    class ROUTER router
    class RETRIEVER rag
    class CODER coder
    class SANDBOX sandbox
    class RETRY sandbox
    class SYNTH,XAI synth
    class START,END endpoint
    class PG store
    class RAGAS eval

    style GRAPH     fill:#fafafa,stroke:#cbd5e1,stroke-width:1.5px
    style CODE_PATH fill:#fff7ed,stroke:#f97316,stroke-width:1.5px
```
