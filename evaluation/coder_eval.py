import os
import sys
import time
import pandas as pd

# Add backend and project root to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from agents.coder import coder_node
from agents.state import AgentState
from langchain_core.messages import HumanMessage

def run_coder_eval():
    print("="*60)
    print("CODER AGENT PERFORMANCE EVALUATION")
    print("="*60)
    
    test_cases = [
        {
            "question": "Tính tỷ suất biên lợi nhuận gộp",
            "context": "Doanh thu thuần: 120.000, Lợi nhuận gộp: 48.000"
        },
        {
            "question": "Tính tỷ lệ ROE",
            "context": "Lợi nhuận sau thuế: 15.000, Vốn chủ sở hữu bình quân: 100.000"
        },
        {
            "question": "So sánh tăng trưởng doanh thu",
            "context": "Doanh thu năm 2022: 80.000, Doanh thu năm 2023: 96.000"
        },
        {
            "question": "Vẽ biểu đồ cột doanh thu 3 năm",
            "context": "Doanh thu năm 2021: 50.000, Doanh thu năm 2022: 60.000, Doanh thu năm 2023: 72.000"
        }
    ]
    
    results = []
    
    for idx, case in enumerate(test_cases):
        q = case["question"]
        ctx = case["context"]
        print(f"Testing [{idx+1}/{len(test_cases)}]: {q}")
        
        state: AgentState = {
            "messages": [HumanMessage(content=ctx)],
            "question": q,
            "intent": "code",
            "error_count": 0,
            "steps": [],
            "execution_result": "",
            "chart_path": ""
        }
        
        t0 = time.time()
        # Mock configuration for session dir
        config = {"configurable": {"session_tmp_dir": "tmp"}}
        
        try:
            res = coder_node(state, config)
            success = 1 if res.get("error_count", 0) == 0 else 0
            err_count = res.get("error_count", 0)
            result_output = res.get("execution_result", "")
        except Exception as e:
            print(f"[-] Coder failed: {e}")
            success = 0
            err_count = 1
            result_output = str(e)
            
        latency = time.time() - t0
        
        results.append({
            "question": q,
            "success": success,
            "retries": err_count,
            "latency": latency,
            "output": result_output
        })
        
    df = pd.DataFrame(results)
    
    success_rate = df["success"].mean()
    avg_retries = df["retries"].mean()
    avg_latency = df["latency"].mean()
    
    df.to_csv("evaluation/coder_eval_results.csv", index=False, encoding="utf-8-sig")
    
    report = f"""# Coder Agent Evaluation Report

**Model:** qwen2.5-coder-thesis:latest (Ollama)  
**Total Samples:** {len(df)}  

## Metrics Summary

| Metric | Result | Target Threshold | Status |
|---|---|---|---|
| **Compilation Success Rate** | {success_rate:.2%} | > 90% | {'✅ PASS' if success_rate >= 0.90 else '⚠️ WARNING'} |
| **Avg Error Retries** | {avg_retries:.1f} | < 1.0 | {'✅ PASS' if avg_retries < 1.0 else '⚠️ WARNING'} |
| **Avg Execution Time** | {avg_latency:.2f}s | < 5.0s | {'✅ PASS' if avg_latency < 5.0 else '⚠️ WARNING'} |

## Detailed Results
"""
    for idx, row in df.iterrows():
        report += f"### Run {idx+1}: {row['question']}\n"
        report += f"- **Success:** `{bool(row['success'])}` | **Retries:** `{row['retries']}` | **Execution Latency:** `{row['latency']:.2f}s`\n"
        report += f"- **REPL Output preview:**\n```\n{row['output'][:300]}\n```\n\n"
        
    with open("evaluation/coder_eval_report.md", "w", encoding="utf-8") as f:
        f.write(report)
        
    print("[+] Saved coder evaluation report to evaluation/coder_eval_report.md")
    print(f"Success Rate: {success_rate:.2%}")

if __name__ == "__main__":
    run_coder_eval()
