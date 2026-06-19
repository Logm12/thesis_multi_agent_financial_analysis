# LangGraph State and Control Flow Orchestration

This document defines the execution flow and state transitions managed by LangGraph within the Multi-Agent Financial Analysis System.

---

## 1. Flowchart Diagram

This diagram separates individual processing tasks (such as validation, compilation, and execution) into distinct single-purpose nodes for improved readability.

```mermaid
flowchart TD
    %% Styling Definitions
    classDef startEnd fill:#f1f5f9,stroke:#475569,stroke-width:2px,color:#0f172a;
    classDef nodeStyle fill:#f8fafc,stroke:#3b82f6,stroke-width:1.5px,color:#1e293b;
    classDef conditionStyle fill:#fffbeb,stroke:#d97706,stroke-width:1.5px,color:#78350f;

    %% Nodes
    START([Start User Query]):::startEnd
    
    intent_classify[Intent Classifier]:::nodeStyle
    route_check{Intent Path}:::conditionStyle
    
    vector_search[ChromaDB Vector Search]:::nodeStyle
    context_isolate[Context Isolation]:::nodeStyle
    after_retrieve_check{Execute Code?}:::conditionStyle
    
    code_gen[Code Generator]:::nodeStyle
    ast_check[AST Validator]:::nodeStyle
    repl_exec[REPL Sandbox]:::nodeStyle
    retry_check{Execution Check}:::conditionStyle
    
    synthesizer[Response Synthesizer]:::nodeStyle
    END([End Stream Response]):::startEnd

    %% Control Flow Links
    START --> intent_classify
    intent_classify --> route_check
    
    route_check -->|out_of_scope| synthesizer
    route_check -->|retrieve or code| vector_search
    
    vector_search --> context_isolate
    context_isolate --> after_retrieve_check
    
    after_retrieve_check -->|no| synthesizer
    after_retrieve_check -->|yes| code_gen
    
    code_gen --> ast_check
    ast_check --> repl_exec
    repl_exec --> retry_check
    
    retry_check -->|Error and retries < 5| code_gen
    retry_check -->|Success or retries >= 5| synthesizer
    
    synthesizer --> END
```

---

## 2. Orchestration Logic Details

*   **State Store (`AgentState`)**: A typed dictionary passed between all nodes. It maintains query history (`messages`), current source filtering parameters (`source_filter`), error retry count (`error_count`), and temporary code generation data.
*   **Routing (`route_intent`)**: Evaluates the `intent` field updated by the router node to decide whether to bypass code execution.
*   **Self-Correction Loop (`check_retry`)**: Inspects the sandbox execution output (`execution_result`). If a traceback or exception is present, it returns control to the code generation node and increments `error_count` up to 5 times.
