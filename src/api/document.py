import os
import shutil
import uuid
import hashlib
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from api.schemas import UploadResponse, StatusResponse
from config import DATA_DIR, CHROMA_PATH
from data_processing.pdf_parser import FastPDFParser
from data_processing.cleaner import clean_vietnamese_text
from data_processing.chunker import process_markdown_file
from data_processing.embedder import get_openai_embedding_model
from langchain_chroma import Chroma

router = APIRouter(prefix="/api/v1", tags=["document"])

# Directories
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# In-memory task store
_task_store: Dict[str, Dict[str, Any]] = {}
# Hash store for deduplication: {hash: file_path}
_hash_store: Dict[str, str] = {}

def get_file_hash(file_path: str) -> str:
    """Tính SHA-256 hash của file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

async def _process_pdf_background(task_id: str, file_path: str):
    """Pipeline xử lý PDF chạy ngầm."""
    try:
        _task_store[task_id]["status"] = "processing"
        _task_store[task_id]["details"] = "Extracting text from PDF..."
        
        # 1. Parse PDF (với timeout 120s qua thread)
        parser = FastPDFParser()
        # Chạy parse trong thread để không block event loop
        content = await asyncio.to_thread(parser.parse, file_path)
        
        # 2. Clean Vietnamese Text
        _task_store[task_id]["details"] = "Cleaning extracted text..."
        cleaned_content = clean_vietnamese_text(content)
        
        # 3. Save to processed folder
        processed_path = PROCESSED_DIR / f"{task_id}.md"
        with open(processed_path, "w", encoding="utf-8") as f:
            f.write(cleaned_content)
            
        # 4. Chunking
        _task_store[task_id]["details"] = "Chunking document..."
        chunks = await asyncio.to_thread(process_markdown_file, str(processed_path))
        
        if not chunks:
            _task_store[task_id]["status"] = "failed"
            _task_store[task_id]["details"] = "No content extracted from PDF."
            return

        # 5. Vectorize & Store (OpenAI Embeddings)
        _task_store[task_id]["details"] = f"Vectorizing {len(chunks)} chunks..."
        embeddings = get_openai_embedding_model()
        
        # Initialize/Load ChromaDB
        vector_db = await asyncio.to_thread(
            Chroma,
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings
        )
        
        # Add documents
        await asyncio.to_thread(vector_db.add_documents, chunks)
        
        # Finalize
        _task_store[task_id]["status"] = "completed"
        _task_store[task_id]["details"] = f"Successfully processed {len(chunks)} chunks."
        print(f"[Async Pipeline] Task {task_id} completed.")
        
    except Exception as e:
        error_msg = str(e)
        print(f"[Async Pipeline] Task {task_id} failed: {error_msg}")
        _task_store[task_id]["status"] = "failed"
        _task_store[task_id]["details"] = f"Error: {error_msg}"

@router.post("/upload-pdf", response_model=UploadResponse, status_code=202)
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Endpoint nạp PDF xử lý bất đồng bộ.
    Hỗ trợ Deduplication dựa trên file hash.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    task_id = str(uuid.uuid4())
    temp_path = RAW_DIR / f"tmp_{task_id}_{file.filename}"
    
    # Save temporary file
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
    
    # Deduplication check
    file_hash = get_file_hash(str(temp_path))
    if file_hash in _hash_store:
        # File đã tồn tại, xóa file tạm và trả về task_id cũ hoặc báo thành công ngay
        existing_path = _hash_store[file_hash]
        os.remove(temp_path)
        return UploadResponse(
            task_id="existing", 
            message=f"File already processed (matched with {os.path.basename(existing_path)}). Skip embedding."
        )

    # Đổi tên file từ tmp thành chính thức
    final_path = RAW_DIR / f"{task_id}_{file.filename}"
    os.rename(temp_path, final_path)
    _hash_store[file_hash] = str(final_path)

    # Initialize state
    _task_store[task_id] = {
        "status": "pending",
        "details": "File accepted and queued for processing."
    }
    
    # Queue background task
    background_tasks.add_task(_process_pdf_background, task_id, str(final_path))
    
    return UploadResponse(
        task_id=task_id,
        message="File accepted for processing in background"
    )

@router.get("/status/{task_id}", response_model=StatusResponse)
async def get_task_status(task_id: str):
    """Lấy trạng thái xử lý của task."""
    if task_id == "existing":
        return StatusResponse(task_id=task_id, status="completed", details="File already existed in system.")
        
    if task_id not in _task_store:
        raise HTTPException(status_code=404, detail="Task ID not found.")
    
    task = _task_store[task_id]
    return StatusResponse(
        task_id=task_id,
        status=task["status"],
        details=task["details"]
    )
