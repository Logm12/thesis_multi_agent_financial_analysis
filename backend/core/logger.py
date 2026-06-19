import os
import json
import datetime
from pathlib import Path
from typing import List, Optional

# Base logs path
LOGS_DIR = Path(__file__).parent.parent.absolute() / "logs"
TRACE_FILE_PATH = LOGS_DIR / "agent_trace.json"

def write_agent_trace(
    thread_id: str,
    message: str,
    steps: List[dict],
    final_answer: str,
    chart_url: Optional[str] = None
):
    """
    Appends a new trace record to e:\Thesis\backend\logs\agent_trace.json.
    Creates parent directories and the file if they do not exist.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    new_trace = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "thread_id": thread_id,
        "message": message,
        "steps": steps,
        "final_answer": final_answer,
        "chart_url": chart_url
    }
    
    traces = []
    if TRACE_FILE_PATH.exists():
        try:
            with open(TRACE_FILE_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    traces = json.loads(content)
                    if not isinstance(traces, list):
                        traces = []
        except Exception as e:
            # Fallback if corrupt
            traces = []
            
    traces.append(new_trace)
    
    try:
        with open(TRACE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(traces, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Logger Error] Failed to write agent trace: {str(e)}")
