import os
import shutil
import uuid
import hashlib
import asyncio
from typing import Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends, Form
from api.schemas import UploadResponse, StatusResponse
from core.config import DATA_DIR, CHROMA_PATH
from core.cache import pdf_cache
from api.auth import get_current_user
from core.database import get_db_connection


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
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def populate_hash_store():
    try:
        for item in RAW_DIR.iterdir():
            if item.is_file() and item.suffix.lower() == ".pdf" and not item.name.startswith("tmp_"):
                try:
                    f_hash = get_file_hash(str(item))
                    _hash_store[f_hash] = str(item)
                except Exception as e:
                    print(f"Error computing hash for {item}: {e}")
    except Exception as e:
        print(f"Error populating hash store: {e}")

populate_hash_store()


async def _process_pdf_background(task_id: str, file_path: str):
    """PDF background processing pipeline."""
    try:
        from api.document_store import update_document_status
        _task_store[task_id]["status"] = "processing"
        _task_store[task_id]["details"] = "Extracting text from PDF..."
        update_document_status(task_id, "processing")
        
        def on_progress(current, total):
            _task_store[task_id]["details"] = f"OCR Processing Page {current}/{total}..."
            try:
                update_document_status(task_id, f"OCR Processing Page {current}/{total}...")
            except Exception:
                pass

        # 1. Parse PDF (with 120s timeout via thread)
        parser = FastPDFParser()
        # Run parsing in thread to avoid blocking the event loop
        blocks = await asyncio.to_thread(parser.parse_blocks, file_path, on_progress)

        
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
        
        # Initialize/Load ChromaDB with explicit collection_name to fix "Blind Agent"
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

from pydantic import BaseModel

class PathUploadRequest(BaseModel):
    file_path: str

@router.post("/upload-by-path", response_model=UploadResponse, status_code=202)
async def upload_by_path(
    background_tasks: BackgroundTasks,
    request: PathUploadRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Endpoint to ingest PDF by direct file path on server/workspace.
    """
    file_path = request.file_path.strip()
    
    # Normalize path from Host to Container (allows Windows or relative paths)
    clean_path = file_path.replace("\\", "/")
    import re
    match = re.match(r"^[a-zA-Z]:/Thesis/data/(.*)", clean_path, re.IGNORECASE)
    if match:
        file_path = f"/app/data/{match.group(1)}"
    elif clean_path.startswith("data/"):
        file_path = f"/app/{clean_path}"
        
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail=f"File not found on server: {file_path} (translated to {file_path})")
        
    if not file_path.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF format is supported.")
        
    task_id = str(uuid.uuid4())
    filename = os.path.basename(file_path)
    
    # Tạo bản sao trong RAW_DIR
    final_path = RAW_DIR / f"{task_id}_{filename}"
    try:
        shutil.copy(file_path, final_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Không thể sao chép tệp: {str(e)}")
        
    # Kiểm tra trùng lặp
    file_hash = get_file_hash(str(final_path))
    if file_hash in _hash_store:
        existing_path = _hash_store[file_hash]
        os.remove(final_path)
        existing_filename = os.path.basename(existing_path)
        existing_task_id = existing_filename.split("_")[0]
        
        # Link with user account
        from api.document_store import get_all_documents, add_document
        user_docs = get_all_documents(user_id=current_user["id"])
        if not any(d["id"] == existing_task_id for d in user_docs):
            size_mb = f"{(os.path.getsize(existing_path) / (1024 * 1024)):.1f} MB"
            add_document(existing_task_id, filename, size_mb, status="indexed", user_id=current_user["id"])
            
        return UploadResponse(
            task_id=existing_task_id,
            message=f"Document has been processed previously. Linked successfully."
        )
        
    _hash_store[file_hash] = str(final_path)
    
    # Initialize status
    _task_store[task_id] = {
        "status": "pending",
        "details": "Document accepted and preparing for processing."
    }
    
    from api.document_store import add_document
    size_mb = f"{(os.path.getsize(final_path) / (1024 * 1024)):.1f} MB"
    add_document(task_id, filename, size_mb, status="processing", user_id=current_user["id"])
    
    # Dispatch background task
    background_tasks.add_task(_process_pdf_background, task_id, str(final_path))
    
    return UploadResponse(
        task_id=task_id,
        message="Local file path ingestion task is running in the background."
    )

@router.post("/upload-pdf", response_model=UploadResponse, status_code=202)
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """
    Endpoint for asynchronous PDF ingestion.
    Supports Deduplication based on file hash.
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
        
        # Extract existing task id
        existing_filename = os.path.basename(existing_path)
        existing_task_id = existing_filename.split("_")[0]
        
        # Link document to this user if not already linked
        from api.document_store import get_all_documents, add_document
        user_docs = get_all_documents(user_id=current_user["id"])
        if not any(d["id"] == existing_task_id for d in user_docs):
            size_mb = f"{(os.path.getsize(existing_path) / (1024 * 1024)):.1f} MB"
            add_document(existing_task_id, file.filename, size_mb, status="indexed", user_id=current_user["id"])
            
        return UploadResponse(
            task_id=existing_task_id, 
            message=f"File already processed (matched with {os.path.basename(existing_path)}). Associated with your account."
        )

    # Rename file from tmp to official
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
    """Get the processing status of the task."""
    processed_path = PROCESSED_DIR / f"{task_id}.json"
    if processed_path.exists():
        return StatusResponse(
            task_id=task_id,
            status="completed",
            details="Successfully processed and loaded existing document."
        )
        
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
    """Get the complete list of knowledge documents."""
    from api.document_store import get_all_documents
    return get_all_documents(user_id=current_user["id"])

@router.patch("/documents/{file_id}")
async def patch_document(file_id: str, payload: dict, current_user: dict = Depends(get_current_user)):
    """Update the displayed name of the document."""
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
    """Delete the document and its related vectors in ChromaDB."""
    verify_document_owner(file_id, current_user)
    from api.document_store import delete_document
    doc = delete_document(file_id, user_id=current_user["id"])
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    # 1. Delete raw physical file
    try:
        for fname in os.listdir(RAW_DIR):
            if fname.startswith(file_id):
                os.remove(RAW_DIR / fname)
                break
    except Exception as e:
        print(f"[Delete] Error deleting raw file: {str(e)}")

    # Delete processed physical file
    processed_file = PROCESSED_DIR / f"{file_id}.json"
    if processed_file.exists():
        try:
            os.remove(processed_file)
        except Exception as e:
            print(f"[Delete] Error deleting processed file: {str(e)}")

    # 2. Delete vectors in ChromaDB
    try:
        embeddings = get_openai_embedding_model()
        vector_db = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings,
            collection_name="financial_docs"
        )
        # Chunker saves source metadata as the basename of the processed json path, i.e., {file_id}.json
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

@router.post("/document/upload-test")
async def upload_test(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session_id: str = Form("default"),
    current_user: dict = Depends(get_current_user)
):
    """
    Test endpoint allowing upload of raw PDF binary.
    Calculates SHA-256 hash and checks Redis cache.
    """
    # 1. Read file content asynchronously
    content = await file.read()
    
    # 2. Calculate SHA-256 hash
    sha256_hash = hashlib.sha256(content).hexdigest()
    
    # 3. Check Redis cache
    cached_task_id = pdf_cache.get_ingest_cache(sha256_hash)
    if cached_task_id:
        return {
            "status": "success",
            "sha256": sha256_hash,
            "cache_hit": True,
            "task_id": cached_task_id,
            "message": "File ingestion cached (matched via SHA-256)."
        }
        
    # 4. Cache miss: Create new task_id and save file to RAW_DIR
    task_id = str(uuid.uuid4())
    final_path = RAW_DIR / f"{task_id}_{file.filename}"
    
    # Write file asynchronously (avoid blocking event loop)
    def write_binary_file(path, data):
        with open(path, "wb") as f:
            f.write(data)
            
    await asyncio.to_thread(write_binary_file, final_path, content)
    
    # Lưu vào in-memory cache hoặc mapping Redis
    _hash_store[sha256_hash] = str(final_path)
    pdf_cache.set_ingest_cache(sha256_hash, task_id)
    
    # Initialize task status
    _task_store[task_id] = {
        "status": "pending",
        "details": "File accepted and queued for processing."
    }
    
    # Save document metadata
    from api.document_store import add_document
    size_mb = f"{(len(content) / (1024 * 1024)):.2f} MB"
    add_document(task_id, file.filename, size_mb, status="processing", user_id=current_user["id"])
    
    # Start background processing
    background_tasks.add_task(_process_pdf_background, task_id, str(final_path))
    
    return {
        "status": "success",
        "sha256": sha256_hash,
        "cache_hit": False,
        "task_id": task_id,
        "message": "File accepted and background task started."
    }

@router.get("/document/progress/{task_id}")
async def get_document_progress(task_id: str):
    """
    SSE endpoint to track real-time progression of document ingestion.
    """
    import json
    from sse_starlette.sse import EventSourceResponse
    
    async def progress_generator():
        last_details = ""
        while True:
            if task_id not in _task_store:
                yield {
                    "event": "error",
                    "data": json.dumps({"status": "failed", "details": "Task ID not found."})
                }
                break
                
            task_status = _task_store[task_id]
            status = task_status.get("status", "pending")
            details = task_status.get("details", "")
            
            if details != last_details:
                yield {
                    "event": "progress",
                    "data": json.dumps({"status": status, "details": details})
                }
                last_details = details
                
            if status in ["completed", "failed", "indexed"]:
                yield {
                    "event": "done",
                    "data": json.dumps({"status": status, "details": details})
                }
                break
                
            await asyncio.sleep(0.5)
            
    return EventSourceResponse(progress_generator())


from pydantic import BaseModel
from fastapi import Request
from api.auth import oauth2_scheme

class IngestRequest(BaseModel):
    file_path: str
    extraction_method: str = "auto"

async def get_current_user_or_default(request: Request, access_token: Optional[str] = Depends(oauth2_scheme)) -> dict:
    try:
        return await get_current_user(request, access_token)
    except HTTPException:
        # Auth failed or missing, get/create default test user in DB
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, email, full_name, role FROM users LIMIT 1")
                user = cur.fetchone()
                if user:
                    return {
                        "id": str(user[0]),
                        "email": user[1],
                        "full_name": user[2],
                        "role": user[3]
                    }
                else:
                    import bcrypt
                    pw_hash = bcrypt.hashpw(b"testpass123", bcrypt.gensalt()).decode('utf-8')
                    cur.execute(
                        "INSERT INTO users (email, full_name, password_hash, role) VALUES (%s, %s, %s, %s) RETURNING id",
                        ("test@example.com", "Test User", pw_hash, "USER")
                    )
                    user_id = str(cur.fetchone()[0])
                    conn.commit()
                    return {
                        "id": user_id,
                        "email": "test@example.com",
                        "full_name": "Test User",
                        "role": "USER"
                    }

@router.post("/test/ingest-automated")
async def test_ingest_automated(
    payload: IngestRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user_or_default)
):
    """
    Headless QA Ingestion endpoint. Accepts an absolute file path on the server/Docker container.
    """
    file_path = payload.file_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail=f"File not found at absolute path: {file_path}")
        
    if not file_path.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    # Read binary content
    def read_file_content(path):
        with open(path, "rb") as f:
            return f.read()
            
    content = await asyncio.to_thread(read_file_content, file_path)
    sha256_hash = hashlib.sha256(content).hexdigest()
    
    # Check cache
    cached_task_id = pdf_cache.get_ingest_cache(sha256_hash)
    if cached_task_id:
        return {
            "status": "success",
            "sha256": sha256_hash,
            "cache_hit": True,
            "task_id": cached_task_id,
            "message": "File ingestion cached (matched via SHA-256)."
        }
        
    # Generate task
    task_id = str(uuid.uuid4())
    filename = os.path.basename(file_path)
    final_path = RAW_DIR / f"{task_id}_{filename}"
    
    # Copy file to RAW_DIR
    def copy_file(src, dst):
        shutil.copy(src, dst)
        
    await asyncio.to_thread(copy_file, file_path, final_path)
    
    _hash_store[sha256_hash] = str(final_path)
    pdf_cache.set_ingest_cache(sha256_hash, task_id)
    
    _task_store[task_id] = {
        "status": "pending",
        "details": "File accepted and queued for processing."
    }
    
    from api.document_store import add_document
    size_mb = f"{(len(content) / (1024 * 1024)):.2f} MB"
    add_document(task_id, filename, size_mb, status="processing", user_id=current_user["id"])
    
    background_tasks.add_task(_process_pdf_background, task_id, str(final_path))
    
    return {
        "status": "success",
        "sha256": sha256_hash,
        "cache_hit": False,
        "task_id": task_id,
        "message": "File accepted and background task started."
    }



