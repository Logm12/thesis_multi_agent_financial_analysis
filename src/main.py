import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_v1_router

# Khởi tạo FastAPI app
app = FastAPI(
    title="Financial Analyzer Thesis - API",
    description="Hệ thống Backend cho đồ án tốt nghiệp - Phân tích tài chính Multi-Agent",
    version="1.0.0"
)

# Cấu hình CORS (AC1)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Linh hoạt cho môi trường dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký routes
app.include_router(api_v1_router)
from api.document import router as api_document_router
app.include_router(api_document_router)

@app.get("/health")
async def root_health():
    """Health check endpoint tại root."""
    return {"status": "alive", "service": "Financial Analyzer Backend"}

# TODO: Implement Async PDF Pipeline in TIP-002 (AC8)

if __name__ == "__main__":
    import uvicorn
    # Chạy trên port 8001 để tránh xung đột
    print("[Main] Starting server on http://0.0.0.0:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
