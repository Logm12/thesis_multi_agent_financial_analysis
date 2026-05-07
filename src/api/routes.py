import asyncio
from fastapi import APIRouter
from langchain_core.messages import HumanMessage
from api.schemas import ChatRequest, ChatResponse
from agents.graph import get_graph_app
from config import TEMP_DIR

router = APIRouter(prefix="/api/v1", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Synchronous chat endpoint with 60s timeout.
    """
    # 1. Prepare input for LangGraph
    inputs = {
        "messages": [HumanMessage(content=request.message)],
        "steps": []
    }
    
    # 2. Config (thread_id for persistence)
    config = {
        "configurable": {
            "thread_id": request.session_id,
            "session_tmp_dir": str(TEMP_DIR / request.session_id)
        }
    }
    
    # Ensure temp dir exists
    (TEMP_DIR / request.session_id).mkdir(parents=True, exist_ok=True)

    try:
        # 3. Get app instance (Lazy-init)
        app = get_graph_app()
        
        # 4. Execute workflow with timeout (default 60s)
        result = await asyncio.wait_for(
            app.ainvoke(inputs, config=config),
            timeout=60.0
        )
        
        # 5. Return success response
        return ChatResponse(
            status="success",
            data=result,
            message="Processing successful"
        )
        
    except asyncio.TimeoutError:
        print(f"[API] Timeout after 60s for session {request.session_id}")
        return ChatResponse(
            status="error",
            message="Request timed out (60s). Please try again or simplify your question."
        )
    except Exception as e:
        print(f"[API] Error: {str(e)}")
        return ChatResponse(
            status="error",
            message=f"System error: {str(e)}"
        )

@router.get("/health")
async def health_check():
    return {"status": "ok", "module": "api_v1"}
