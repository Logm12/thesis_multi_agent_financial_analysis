import os
import json
import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from api.auth import get_current_user, verify_token
from core.database import get_db_connection
from core.logger import TRACE_FILE_PATH

router = APIRouter(prefix="/api/traces", tags=["traces"])

# Simple dependency to ensure user is logged in as an ADMIN
async def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Administrator privileges required."
        )
    return current_user

class NodeTraceDetail(BaseModel):
    node_name: str
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    cost: float
    created_at: str

class StepDetail(BaseModel):
    node: str
    output: str

class SessionTraceResponse(BaseModel):
    thread_id: str
    message: str
    final_answer: str
    timestamp: str
    chart_url: Optional[str]
    total_cost: float
    steps: List[StepDetail]
    token_usage: List[NodeTraceDetail]

@router.get("/sessions", response_model=List[SessionTraceResponse])
async def list_sessions(admin: dict = Depends(get_admin_user)):
    """Returns all traces recorded in agent_trace.json."""
    if not TRACE_FILE_PATH.exists():
        return []
        
    try:
        with open(TRACE_FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            traces = json.loads(content)
            if not isinstance(traces, list):
                return []
            
            # Map steps and token usage keys to fit Pydantic schema
            response = []
            for t in traces:
                steps = []
                for s in t.get("steps", []):
                    steps.append(StepDetail(node=s.get("node", "unknown"), output=s.get("output", "")))
                
                tokens = []
                for tu in t.get("token_usage", []):
                    tokens.append(NodeTraceDetail(
                        node_name=tu.get("node_name", "unknown"),
                        model_name=tu.get("model_name", "unknown"),
                        prompt_tokens=tu.get("prompt_tokens", 0),
                        completion_tokens=tu.get("completion_tokens", 0),
                        cost=tu.get("cost", 0.0),
                        created_at=tu.get("created_at", "")
                    ))
                    
                response.append(SessionTraceResponse(
                    thread_id=t.get("thread_id", ""),
                    message=t.get("message", ""),
                    final_answer=t.get("final_answer", ""),
                    timestamp=t.get("timestamp", ""),
                    chart_url=t.get("chart_url"),
                    total_cost=t.get("total_cost", 0.0),
                    steps=steps,
                    token_usage=tokens
                ))
            # Sort by timestamp descending
            response.sort(key=lambda x: x.timestamp, reverse=True)
            return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read agent trace file: {str(e)}")

@router.get("/stats")
async def get_token_stats(admin: dict = Depends(get_admin_user)):
    """Returns aggregated stats of tokens and cost per node and model."""
    stats = {
        "total_cost": 0.0,
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "by_node": {},
        "by_model": {}
    }
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT node_name, model_name, SUM(prompt_tokens), SUM(completion_tokens), SUM(cost) "
                    "FROM token_usage GROUP BY node_name, model_name"
                )
                rows = cur.fetchall()
                for r in rows:
                    node, model, prompt, completion, cost = r
                    prompt = int(prompt)
                    completion = int(completion)
                    cost = float(cost)
                    
                    stats["total_cost"] += cost
                    stats["total_prompt_tokens"] += prompt
                    stats["total_completion_tokens"] += completion
                    
                    # Group by node
                    if node not in stats["by_node"]:
                        stats["by_node"][node] = {"prompt": 0, "completion": 0, "cost": 0.0}
                    stats["by_node"][node]["prompt"] += prompt
                    stats["by_node"][node]["completion"] += completion
                    stats["by_node"][node]["cost"] += cost
                    
                    # Group by model
                    if model not in stats["by_model"]:
                        stats["by_model"][model] = {"prompt": 0, "completion": 0, "cost": 0.0}
                    stats["by_model"][model]["prompt"] += prompt
                    stats["by_model"][model]["completion"] += completion
                    stats["by_model"][model]["cost"] += cost
        return stats
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Database error during stats query: {str(e)}")

@router.get("/logs/raw")
async def get_raw_trace_logs(admin: dict = Depends(get_admin_user)):
    """Downloads or shows the raw content of the trace JSON file."""
    if not TRACE_FILE_PATH.exists():
        return []
    try:
        with open(TRACE_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading log file: {str(e)}")

@router.get("/logs/stream")
async def stream_trace_logs(token: str):
    """
    SSE stream of trace log updates.
    Validates token via query parameter since SSE doesn't easily support Authorization headers.
    """
    payload = verify_token(token)
    if not payload or payload.get("role") != "ADMIN":
        raise HTTPException(status_code=401, detail="Unauthorized log stream access.")
        
    async def log_generator():
        last_mtime = 0.0
        while True:
            if TRACE_FILE_PATH.exists():
                mtime = os.path.getmtime(TRACE_FILE_PATH)
                if mtime > last_mtime:
                    last_mtime = mtime
                    try:
                        with open(TRACE_FILE_PATH, "r", encoding="utf-8") as f:
                            content = f.read().strip()
                            if content:
                                data = json.loads(content)
                                # Send only the latest recorded trace
                                if isinstance(data, list) and len(data) > 0:
                                    yield f"event: log_update\ndata: {json.dumps(data[-1])}\n\n"
                    except Exception:
                        pass
            await asyncio.sleep(1.0)
            
    return StreamingResponse(log_generator(), media_type="text/event-stream")
