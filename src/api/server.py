import os
import json
import asyncio
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from sse_starlette.sse import EventSourceResponse

from agents.graph import get_graph_app, ingest_pdf
from config import DATA_DIR, TEMP_DIR

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI(title="Financial Analyzer API")

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

RAW_DATA_DIR = DATA_DIR / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

class ChatRequest(BaseModel):
    message: str
    thread_id: str
    session_id: Optional[str] = "default"

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Xử lý nạp file PDF."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file PDF")
    
    save_path = RAW_DATA_DIR / file.filename
    try:
        with open(save_path, "wb") as buffer:
            shutil_copy = await file.read()
            buffer.write(shutil_copy)
        
        # Ingest into VectorDB
        await asyncio.to_thread(ingest_pdf, str(save_path))
        return {"status": "success", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat-stream")
async def chat_stream(message: str, thread_id: str):
    """
    Endpoint SSE để stream kết quả từ LangGraph.
    """
    async def event_generator():
        inputs = {"messages": [HumanMessage(content=message)], "steps": []}
        config = {"configurable": {"thread_id": thread_id, "session_tmp_dir": str(TEMP_DIR / thread_id)}}
        
        # Ensure thread tmp dir exists
        (TEMP_DIR / thread_id).mkdir(parents=True, exist_ok=True)

        try:
            graph_app = get_graph_app()
            async for output in graph_app.astream(inputs, config=config):
                for node, values in output.items():
                    # Gửi trạng thái node (Thought Process)
                    step_msg = values["steps"][-1] if values.get("steps") else f"Executing {node}..."
                    yield {
                        "event": "step",
                        "data": json.dumps({"node": node, "output": step_msg})
                    }
                    
                    # Nếu là node cuối hoặc có final_answer
                    if "final_answer" in values:
                        yield {
                            "event": "final_answer",
                            "data": json.dumps({"content": values["final_answer"]})
                        }
            
            # Gửi tín hiệu kết thúc
            yield {"event": "done", "data": "end"}
            
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"detail": str(e)})
            }

    return EventSourceResponse(event_generator())

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
