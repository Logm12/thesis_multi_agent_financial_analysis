# Coder Agent Evaluation Report

**Model:** qwen2.5-coder-thesis:latest (Ollama)  
**Total Samples:** 4  

## Metrics Summary

| Metric | Result | Target Threshold | Status |
|---|---|---|---|
| **Compilation Success Rate** | 0.00% | > 90% | ⚠️ WARNING |
| **Avg Error Retries** | 1.0 | < 1.0 | ⚠️ WARNING |
| **Avg Execution Time** | 0.10s | < 5.0s | ✅ PASS |

## Detailed Results
### Run 1: Tính tỷ suất biên lợi nhuận gộp
- **Success:** `False` | **Retries:** `1` | **Execution Latency:** `0.36s`
- **REPL Output preview:**
```
'Input to ChatPromptTemplate is missing variables {\'"name"\', "\\n        \'Year\'"}.  Expected: ["\\n        \'Year\'", \'"name"\', \'chart_path\', \'context\', \'finance_dict\', \'last_error\', \'question\'] Received: [\'question\', \'context\', \'finance_dict\', \'last_error\', \'chart_path\']\n
```

### Run 2: Tính tỷ lệ ROE
- **Success:** `False` | **Retries:** `1` | **Execution Latency:** `0.01s`
- **REPL Output preview:**
```
'Input to ChatPromptTemplate is missing variables {\'"name"\', "\\n        \'Year\'"}.  Expected: ["\\n        \'Year\'", \'"name"\', \'chart_path\', \'context\', \'finance_dict\', \'last_error\', \'question\'] Received: [\'question\', \'context\', \'finance_dict\', \'last_error\', \'chart_path\']\n
```

### Run 3: So sánh tăng trưởng doanh thu
- **Success:** `False` | **Retries:** `1` | **Execution Latency:** `0.01s`
- **REPL Output preview:**
```
'Input to ChatPromptTemplate is missing variables {\'"name"\', "\\n        \'Year\'"}.  Expected: ["\\n        \'Year\'", \'"name"\', \'chart_path\', \'context\', \'finance_dict\', \'last_error\', \'question\'] Received: [\'question\', \'context\', \'finance_dict\', \'last_error\', \'chart_path\']\n
```

### Run 4: Vẽ biểu đồ cột doanh thu 3 năm
- **Success:** `False` | **Retries:** `1` | **Execution Latency:** `0.01s`
- **REPL Output preview:**
```
'Input to ChatPromptTemplate is missing variables {\'"name"\', "\\n        \'Year\'"}.  Expected: ["\\n        \'Year\'", \'"name"\', \'chart_path\', \'context\', \'finance_dict\', \'last_error\', \'question\'] Received: [\'question\', \'context\', \'finance_dict\', \'last_error\', \'chart_path\']\n
```

