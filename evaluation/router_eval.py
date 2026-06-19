import os
import sys
import pandas as pd
import numpy as np

# Add backend and project root to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from agents.router import router_node, RouteQuery
from agents.state import AgentState
from core.nim_client import get_nim_llm
from core.config import ROUTER_MODEL

def run_router_eval():
    print("="*60)
    print("ROUTER AGENT PERFORMANCE EVALUATION")
    print("="*60)
    
    # Test cases with ground truth intents
    test_cases = [
        {"question": "Doanh thu năm 2023 là bao nhiêu?", "expected": "retrieve"},
        {"question": "Ai là CEO của công ty hiện tại?", "expected": "retrieve"},
        {"question": "Báo cáo tài chính quý 4 có những mục nào?", "expected": "retrieve"},
        {"question": "Tầm nhìn chiến lược của FPT là gì?", "expected": "retrieve"},
        {"question": "Trích dẫn dòng tiền từ hoạt động kinh doanh", "expected": "retrieve"},
        
        {"question": "Tính tỷ suất biên lợi nhuận gộp năm 2023", "expected": "code"},
        {"question": "So sánh tăng trưởng doanh thu giữa 2022 và 2023 và vẽ biểu đồ cột", "expected": "code"},
        {"question": "Vẽ biểu đồ hình tròn cơ cấu tài sản ngắn hạn", "expected": "code"},
        {"question": "Tính tỷ số thanh toán nhanh", "expected": "code"},
        {"question": "Tốc độ tăng trưởng kép hàng năm CAGR của doanh thu ròng là bao nhiêu?", "expected": "code"},
        
        {"question": "Làm thế nào để bẻ khóa phần mềm?", "expected": "out_of_scope"},
        {"question": "Hãy làm cho tôi một cốc cà phê ảo", "expected": "out_of_scope"},
        {"question": "Thời tiết hôm nay tại Hà Nội thế nào?", "expected": "out_of_scope"},
        {"question": "Viết một bài thơ tình lãng mạn", "expected": "out_of_scope"},
        {"question": "Hack mật khẩu facebook người khác", "expected": "out_of_scope"}
    ]
    
    # Initialize Router (Will use Llama 3.3 NIM client)
    # We call standard router logic
    results = []
    
    for idx, case in enumerate(test_cases):
        q = case["question"]
        expected = case["expected"]
        print(f"Testing [{idx+1}/{len(test_cases)}]: {q}")
        
        state: AgentState = {
            "messages": [],
            "question": q,
            "intent": None,
            "error_count": 0,
            "steps": []
        }
        
        t0 = pd.Timestamp.now()
        try:
            res = router_node(state)
            intent = res["intent"]
            success = 1 if intent == expected else 0
        except Exception as e:
            print(f"[-] Router invocation error: {e}")
            intent = "error"
            success = 0
            
        latency = (pd.Timestamp.now() - t0).total_seconds()
        
        results.append({
            "question": q,
            "expected": expected,
            "predicted": intent,
            "correct": success,
            "latency": latency
        })
        
    df = pd.DataFrame(results)
    
    # Calculate Metrics
    accuracy = df["correct"].mean()
    
    # Precision, Recall, F1 for retrieve and code
    metrics = {}
    for cat in ["retrieve", "code", "out_of_scope"]:
        tp = len(df[(df["expected"] == cat) & (df["predicted"] == cat)])
        fp = len(df[(df["expected"] != cat) & (df["predicted"] == cat)])
        fn = len(df[(df["expected"] == cat) & (df["predicted"] != cat)])
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics[cat] = {
            "precision": precision,
            "recall": recall,
            "f1": f1
        }
        
    # Save report
    df.to_csv("evaluation/router_eval_results.csv", index=False, encoding="utf-8-sig")
    
    report = f"""# Router Agent Evaluation Report

**Model:** {ROUTER_MODEL}  
**Overall Accuracy:** {accuracy:.4f}  

## Metrics by Category

| Category | Precision | Recall | F1-Score |
|---|---|---|---|
| **Retrieve (Q&A)** | {metrics["retrieve"]["precision"]:.4f} | {metrics["retrieve"]["recall"]:.4f} | {metrics["retrieve"]["f1"]:.4f} |
| **Code (Calculation/Charts)** | {metrics["code"]["precision"]:.4f} | {metrics["code"]["recall"]:.4f} | {metrics["code"]["f1"]:.4f} |
| **Out of Scope (Sanitation)** | {metrics["out_of_scope"]["precision"]:.4f} | {metrics["out_of_scope"]["recall"]:.4f} | {metrics["out_of_scope"]["f1"]:.4f} |

## Detailed Log
"""
    for idx, row in df.iterrows():
        report += f"- **Q:** {row['question']}\n  - Expected: `{row['expected']}` | Predicted: `{row['predicted']}` | Latency: `{row['latency']:.2f}s`\n"
        
    with open("evaluation/router_eval_report.md", "w", encoding="utf-8") as f:
        f.write(report)
        
    print("[+] Saved router evaluation report to evaluation/router_eval_report.md")
    print(f"Accuracy: {accuracy:.4%}")

if __name__ == "__main__":
    run_router_eval()
