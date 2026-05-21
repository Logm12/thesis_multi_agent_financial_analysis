import os
import shutil
import uuid
import hashlib
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
from api.schemas import UploadResponse, StatusResponse
from core.config import DATA_DIR, CHROMA_PATH
from api.auth import get_current_user

def verify_document_owner(file_id: str, user: dict):
    if user["role"] == "ADMIN":
        return
    from api.document_store import get_all_documents
    docs = get_all_documents(user_id=user["id"])
    if not any(d["id"] == file_id for d in docs):
        raise HTTPException(status_code=403, detail="Access denied. You do not own this document.")
from services.ocr.pdf_parser import FastPDFParser
from services.rag.cleaner import clean_vietnamese_text
from services.rag.chunker import process_blocks
from services.rag.embedder import get_openai_embedding_model
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
        from api.document_store import update_document_status
        _task_store[task_id]["status"] = "processing"
        _task_store[task_id]["details"] = "Extracting text from PDF..."
        update_document_status(task_id, "processing")
        
        # 1. Parse PDF (với timeout 120s qua thread)
        parser = FastPDFParser()
        # Chạy parse trong thread để không block event loop
        blocks = await asyncio.to_thread(parser.parse_blocks, file_path)
        
        # 2. Clean Vietnamese Text
        _task_store[task_id]["details"] = "Cleaning extracted text..."
        for block in blocks:
            block["text"] = clean_vietnamese_text(block["text"])
        
        # 3. Save to processed folder
        import json
        processed_path = PROCESSED_DIR / f"{task_id}.json"
        with open(processed_path, "w", encoding="utf-8") as f:
            json.dump(blocks, f, ensure_ascii=False, indent=2)
            
        # 4. Chunking
        _task_store[task_id]["details"] = "Chunking document..."
        chunks = await asyncio.to_thread(process_blocks, blocks, f"{task_id}.json")
        
        if not chunks:
            _task_store[task_id]["status"] = "failed"
            _task_store[task_id]["details"] = "No content extracted from PDF."
            update_document_status(task_id, "failed")
            return

        # 5. Vectorize & Store (OpenAI Embeddings)
        _task_store[task_id]["details"] = f"Vectorizing {len(chunks)} chunks..."
        embeddings = get_openai_embedding_model()
        
        # Initialize/Load ChromaDB with explicit collection_name to fix "Agent mù"
        vector_db = await asyncio.to_thread(
            Chroma,
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings,
            collection_name="financial_docs"
        )
        
        # Add documents
        await asyncio.to_thread(vector_db.add_documents, chunks)
        
        # Finalize
        _task_store[task_id]["status"] = "completed"
        _task_store[task_id]["details"] = f"Successfully processed {len(chunks)} chunks."
        update_document_status(task_id, "indexed")
        print(f"[Async Pipeline] Task {task_id} completed.")
        
    except Exception as e:
        error_msg = str(e)
        print(f"[Async Pipeline] Task {task_id} failed: {error_msg}")
        _task_store[task_id]["status"] = "failed"
        _task_store[task_id]["details"] = f"Error: {error_msg}"
        try:
            from api.document_store import update_document_status
            update_document_status(task_id, "failed")
        except Exception:
            pass

@router.post("/upload-pdf", response_model=UploadResponse, status_code=202)
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
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
    
    # Save metadata to persistent store
    from api.document_store import add_document
    size_mb = f"{(os.path.getsize(final_path) / (1024 * 1024)):.1f} MB"
    add_document(task_id, file.filename, size_mb, status="processing", user_id=current_user["id"])
    
    # Queue background task
    background_tasks.add_task(_process_pdf_background, task_id, str(final_path))
    
    return UploadResponse(
        task_id=task_id,
        message="File accepted for processing in background"
    )

@router.get("/status/{task_id}", response_model=StatusResponse)
async def get_task_status(task_id: str, current_user: dict = Depends(get_current_user)):
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

@router.get("/documents")
async def get_documents(current_user: dict = Depends(get_current_user)):
    """Lấy toàn bộ danh sách tài liệu tri thức."""
    from api.document_store import get_all_documents
    return get_all_documents(user_id=current_user["id"])

@router.patch("/documents/{file_id}")
async def patch_document(file_id: str, payload: dict, current_user: dict = Depends(get_current_user)):
    """Cập nhật tên tài liệu hiển thị."""
    new_name = payload.get("name")
    if not new_name:
        raise HTTPException(status_code=400, detail="Missing 'name' in payload.")
    
    from api.document_store import rename_document
    success = rename_document(file_id, new_name, user_id=current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"status": "success", "message": "Document renamed successfully."}

@router.delete("/documents/{file_id}")
async def delete_document_endpoint(file_id: str, current_user: dict = Depends(get_current_user)):
    """Xóa tài liệu và các vector liên quan trong ChromaDB."""
    verify_document_owner(file_id, current_user)
    from api.document_store import delete_document
    doc = delete_document(file_id, user_id=current_user["id"])
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    # 1. Xóa file vật lý raw
    try:
        for fname in os.listdir(RAW_DIR):
            if fname.startswith(file_id):
                os.remove(RAW_DIR / fname)
                break
    except Exception as e:
        print(f"[Delete] Error deleting raw file: {str(e)}")

    # Xóa file vật lý processed
    processed_file = PROCESSED_DIR / f"{file_id}.json"
    if processed_file.exists():
        try:
            os.remove(processed_file)
        except Exception as e:
            print(f"[Delete] Error deleting processed file: {str(e)}")

    # 2. Xóa vector trong ChromaDB
    try:
        embeddings = get_openai_embedding_model()
        vector_db = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings,
            collection_name="financial_docs"
        )
        # Chunker lưu source metadata là basename của processed json path, tức {file_id}.json
        vector_db.delete(where={"source": f"{file_id}.json"})
        print(f"[Delete] Successfully deleted vectors for source {file_id}.json from ChromaDB")
    except Exception as e:
        print(f"[Delete] Error deleting vectors: {str(e)}")
    return {"status": "success", "message": "Document and its vectors deleted successfully."}

from fastapi.responses import FileResponse
from fastapi import Response

@router.get("/documents/{file_id}/pdf")
async def get_document_pdf(file_id: str, current_user: dict = Depends(get_current_user)):
    verify_document_owner(file_id, current_user)
    """Download or stream the raw PDF file directly."""
    pdf_path = None
    for fname in os.listdir(RAW_DIR):
        if fname.startswith(file_id):
            pdf_path = RAW_DIR / fname
            break
            
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF document not found")
        
    return FileResponse(str(pdf_path), media_type="application/pdf")

@router.get("/documents/{file_id}/info")
async def get_document_info(file_id: str, current_user: dict = Depends(get_current_user)):
    verify_document_owner(file_id, current_user)
    """Retrieve structural information of the document (total pages, dimensions of each page)."""
    pdf_path = None
    for fname in os.listdir(RAW_DIR):
        if fname.startswith(file_id):
            pdf_path = RAW_DIR / fname
            break
            
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF document not found")
        
    try:
        import fitz
        doc = fitz.open(pdf_path)
        pages_info = []
        for i in range(len(doc)):
            page = doc.load_page(i)
            pages_info.append({
                "page": i + 1,
                "width": page.rect.width,
                "height": page.rect.height
            })
        total_pages = len(doc)
        doc.close()
        
        # Look up friendly name from documents.json
        from api.document_store import get_all_documents
        doc_meta = None
        for d in get_all_documents():
            if d["id"] == file_id:
                doc_meta = d
                break
                
        return {
            "id": file_id,
            "name": doc_meta["name"] if doc_meta else os.path.basename(pdf_path),
            "totalPages": total_pages,
            "pages": pages_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing PDF document structure: {str(e)}")

@router.get("/documents/{file_id}/blocks")
async def get_document_blocks(file_id: str, current_user: dict = Depends(get_current_user)):
    verify_document_owner(file_id, current_user)
    """Get all extracted document blocks with structural text, pages, and bounding box coordinates."""
    processed_path = PROCESSED_DIR / f"{file_id}.json"
    if not processed_path.exists():
        raise HTTPException(status_code=404, detail="Processed document metadata not found")
        
    import json
    try:
        with open(processed_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading document blocks: {str(e)}")

@router.get("/documents/{file_id}/page/{page_num}/image")
async def get_document_page_image(file_id: str, page_num: int, current_user: dict = Depends(get_current_user)):
    verify_document_owner(file_id, current_user)
    """Render a specific page of a PDF as a PNG image using PyMuPDF."""
    pdf_path = None
    for fname in os.listdir(RAW_DIR):
        if fname.startswith(file_id):
            pdf_path = RAW_DIR / fname
            break
            
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF document not found")
        
    try:
        import fitz
        doc = fitz.open(pdf_path)
        if page_num < 1 or page_num > len(doc):
            doc.close()
            raise HTTPException(status_code=400, detail=f"Page number {page_num} out of range (1-{len(doc)})")
            
        page = doc.load_page(page_num - 1)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # 2x zoom for high quality image
        img_data = pix.tobytes("png")
        doc.close()
        
        return Response(content=img_data, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering PDF page: {str(e)}")
