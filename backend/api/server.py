import os
import json
import asyncio
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from sse_starlette.sse import EventSourceResponse

from agents.graph import get_graph_app, ingest_pdf
from core.config import DATA_DIR, TEMP_DIR, REDIS_URL
from core.database import init_db
from api.auth import router as auth_router, get_current_user
import redis

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse

from api.routes import router as routes_router
from api.document import router as document_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema on startup
    init_db()
    yield

app = FastAPI(title="Financial Analyzer API", lifespan=lifespan)

# Port resolution for Docker vs Local
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5433")

# CORS mapping
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(routes_router)
app.include_router(document_router)

RAW_DATA_DIR = DATA_DIR / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

class ChatRequest(BaseModel):
    message: str
    thread_id: str
    session_id: Optional[str] = "default"

@app.get("/chart/{thread_id}")
async def get_chart(thread_id: str, current_user: dict = Depends(get_current_user)):
    """
    Endpoint phục vụ file chart.png sinh ra cho thread cụ thể.
    """
    if current_user["role"] != "ADMIN" and not thread_id.startswith(f"{current_user['id']}_"):
        raise HTTPException(status_code=403, detail="Access denied. You do not own this session.")
        
    chart_path = TEMP_DIR / thread_id / "chart.png"
    if not os.path.exists(chart_path):
        raise HTTPException(status_code=404, detail="Chart not found for this session")
    return FileResponse(str(chart_path), media_type="image/png")

@app.get("/chat-stream")
async def chat_stream(message: str, thread_id: str, current_user: dict = Depends(get_current_user)):
    """
    Endpoint SSE để stream kết quả từ LangGraph.
    """
    scoped_thread_id = f"{current_user['id']}_{thread_id}"
    
    async def event_generator():
        inputs = {"messages": [HumanMessage(content=message)], "steps": []}
        config = {"configurable": {"thread_id": scoped_thread_id, "session_tmp_dir": str(TEMP_DIR / scoped_thread_id)}}
        
        # Ensure thread tmp dir exists
        (TEMP_DIR / scoped_thread_id).mkdir(parents=True, exist_ok=True)

        try:
            graph_app = get_graph_app()
            active_chart_path = None # Track accumulated chart path in this session
            async for output in graph_app.astream(inputs, config=config):
                for node, values in output.items():
                    # Accumulate chart path if any node produced it (e.g., coder)
                    if "chart_path" in values and values["chart_path"]:
                        active_chart_path = values["chart_path"]
                    
                    # Gửi trạng thái node (Thought Process)
                    step_msg = values["steps"][-1] if values.get("steps") else f"Executing {node}..."
                    yield {
                        "event": "step",
                        "data": json.dumps({"node": node, "output": step_msg})
                    }
                    
                    # Nếu là node cuối hoặc có final_answer
                    if "final_answer" in values:
                        chart_url = f"/chart/{scoped_thread_id}" if active_chart_path and os.path.exists(active_chart_path) else None
                        yield {
                            "event": "final_answer",
                            "data": json.dumps({
                                "content": values["final_answer"],
                                "chart_url": chart_url
                            })
                        }
            
            # Gửi tín hiệu kết thúc
            yield {"event": "done", "data": "end"}
            
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"detail": str(e)})
            }

    return EventSourceResponse(event_generator())

# Global Fallback InMemory store if Redis is unavailable
_in_memory_rates = {}

@app.get("/api/v1/demo")
async def demo_stream(message: str, session_id: str):
    """
    Endpoint Demo API không cần JWT, Rate limited 3 lần / Session.
    Cố định truy vấn dữ liệu BCTC FPT 2025.
    """
    async def demo_event_generator():
        try:
            # 1. Check Rate Limit
            limit_exceeded = False
            try:
                r = redis.from_url(REDIS_URL, socket_timeout=2)
                key = f"demo_rate:{session_id}"
                count = r.incr(key)
                if count == 1:
                    r.expire(key, 86400) # Expire in 24h
                if count > 3:
                    limit_exceeded = True
            except Exception as redis_err:
                print(f"[Redis Warning] Fallback to In-Memory due to: {str(redis_err)}")
                # Fallback to in-memory storage
                current_count = _in_memory_rates.get(session_id, 0) + 1
                _in_memory_rates[session_id] = current_count
                if current_count > 3:
                    limit_exceeded = True

            if limit_exceeded:
                yield {
                    "event": "error",
                    "data": json.dumps({"detail": "Rate limit exceeded. You have reached the maximum of 3 questions allowed for the Guest demo."})
                }
                return

            # 2. Trực tiếp gọi LangGraph workflow với `source_filter` nhúng cố định
            inputs = {
                "messages": [HumanMessage(content=message)], 
                "steps": [],
                "source_filter": "15767250-129f-4839-ba16-167472976d62.md" # Cố định tài liệu FPT 2025
            }
            
            config = {
                "configurable": {
                    "thread_id": f"demo_{session_id}", 
                    "session_tmp_dir": str(TEMP_DIR / f"demo_{session_id}")
                }
            }
            
            (TEMP_DIR / f"demo_{session_id}").mkdir(parents=True, exist_ok=True)

            graph_app = get_graph_app()
            active_chart_path = None
            
            async for output in graph_app.astream(inputs, config=config):
                for node, values in output.items():
                    if "chart_path" in values and values["chart_path"]:
                        active_chart_path = values["chart_path"]
                    
                    # Mapping các Thought steps (Thinking UI cho frontend)
                    step_msg = values["steps"][-1] if values.get("steps") else f"Executing {node}..."
                    yield {
                        "event": "step",
                        "data": json.dumps({"node": node, "output": step_msg})
                    }
                    
                    if "final_answer" in values:
                        chart_url = f"/chart/demo_{session_id}" if active_chart_path and os.path.exists(active_chart_path) else None
                        yield {
                            "event": "final_answer",
                            "data": json.dumps({
                                "content": values["final_answer"],
                                "chart_url": chart_url
                            })
                        }
            
            yield {"event": "done", "data": "end"}

        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"detail": str(e)})
            }

    return EventSourceResponse(demo_event_generator())

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Serve React Static Files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_path, "assets")), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        if full_path.startswith("api/") or full_path in ["chat-stream", "upload", "health"]:
            return # Let FastAPI handle it
        return HTMLResponse(content=open(os.path.join(static_path, "index.html")).read())

if __name__ == "__main__":
    import uvicorn
    # Port 8001 to avoid conflict with existing Chainlit on 8000
    uvicorn.run(app, host="0.0.0.0", port=8001)
