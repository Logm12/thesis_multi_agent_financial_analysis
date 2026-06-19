import os
import sys
import shutil
import uuid
import json
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from core.config import DATA_DIR, CHROMA_PATH
from core.database import get_db_connection
from services.ocr.pdf_parser import FastPDFParser
from services.rag.cleaner import clean_vietnamese_text
from services.rag.chunker import process_blocks
from services.rag.embedder import get_openai_embedding_model
from langchain_chroma import Chroma

# Paths
RAW_DIR = Path(DATA_DIR) / "raw"
PROCESSED_DIR = Path(DATA_DIR) / "processed"
DOCS_JSON_PATH = Path(DATA_DIR) / "documents.json"

# Targets (these are the clean files we just downloaded)
# Targets (configured from user's FPT and Vinamilk subdirectories)
TARGETS = [
    {
        "relative_path": "FPT/20260319 - FPT - BCTC hop nhat nam 2025 da kiem toan.pdf",
        "display_name": "FPT_BCTC_2025_Audited.pdf"
    },
    {
        "relative_path": "FPT/20260424 - FPT - BCTC hop nhat Quy 1 nam 2026.pdf",
        "display_name": "FPT_BCTC_Q1_2026.pdf"
    },
    {
        "relative_path": "Vinamilk/20260227_BCTC_KIEM_TOAN_2025_HOP_NHAT_VN_94f1e76e45.pdf",
        "display_name": "VNM_BCTC_2025_Audited.pdf"
    },
    {
        "relative_path": "Vinamilk/20260319_VNM_Bao_cao_thuong_nien_2025_6e6aa72069.pdf",
        "display_name": "VNM_BCTN_2025.pdf"
    },
    {
        "relative_path": "Vinamilk/20260429_VNM_BCTC_DA_SOAT_XET_Q1_2026_HOP_NHAT_VN_d44326741a.pdf",
        "display_name": "VNM_BCTC_Q1_2026.pdf"
    }
]

def clear_existing_data():
    print("--- Clearing ChromaDB ---")
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print(f"Deleted {CHROMA_PATH}")
    else:
        print("ChromaDB path does not exist, nothing to delete.")

    print("--- Clearing documents table in PostgreSQL ---")
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM documents")
            print("Deleted all records from documents table.")

    # Remove documents.json
    if DOCS_JSON_PATH.exists():
        os.remove(DOCS_JSON_PATH)
        print("Deleted documents.json")

    # Clean RAW_DIR and PROCESSED_DIR entirely since source files are safe in data subdirectories
    print("--- Cleaning raw and processed directories ---")
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    for file in os.listdir(PROCESSED_DIR):
        file_path = PROCESSED_DIR / file
        if os.path.isfile(file_path):
            os.remove(file_path)
            
    for file in os.listdir(RAW_DIR):
        file_path = RAW_DIR / file
        if os.path.isfile(file_path):
            os.remove(file_path)

def get_jury_user_id():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email = 'giamkhao@lumo.ai'")
            row = cur.fetchone()
            if row:
                return str(row[0])
            else:
                cur.execute("SELECT id FROM users LIMIT 1")
                row = cur.fetchone()
                if row:
                    return str(row[0])
    return None

async def ingest_file(target, user_id):
    relative_path = target["relative_path"]
    display_name = target["display_name"]
    source_path = Path(DATA_DIR) / relative_path
    
    if not source_path.exists():
        print(f"Target file {relative_path} does not exist at {source_path}, skipping.")
        return
        
    doc_id = str(uuid.uuid4())
    dest_path = RAW_DIR / f"{doc_id}_{display_name}"
    
    # Copy file to have the correct prefix name in RAW_DIR
    shutil.copy(source_path, dest_path)
    size_mb = f"{(os.path.getsize(dest_path) / (1024 * 1024)):.2f} MB"
    
    print(f"Ingesting {display_name} (ID: {doc_id}, Size: {size_mb})...")
    
    # 1. Parse PDF
    parser = FastPDFParser()
    blocks = parser.parse_blocks(str(dest_path))
    
    # 2. Clean Vietnamese Text
    for block in blocks:
        block["text"] = clean_vietnamese_text(block["text"])
        
    # 3. Save to processed folder
    processed_path = PROCESSED_DIR / f"{doc_id}.json"
    with open(processed_path, "w", encoding="utf-8") as f:
        json.dump(blocks, f, ensure_ascii=False, indent=2)
        
    # 4. Chunking
    chunks = process_blocks(blocks, f"{doc_id}.json")
    
    if not chunks:
        print(f"Warning: No chunks extracted from {display_name}")
        return
        
    # 5. Vectorize & Store (OpenAI Embeddings)
    embeddings = get_openai_embedding_model()
    vector_db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name="financial_docs"
    )
    
    batch_size = 2000
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        print(f"Adding batch {i//batch_size + 1} of {len(chunks)//batch_size + 1 or 1} ({len(batch)} chunks)...")
        vector_db.add_documents(batch)
    
    # 6. Add to Database
    uploaded_at = os.path.getmtime(dest_path)
    import datetime
    uploaded_at_str = datetime.datetime.fromtimestamp(uploaded_at).strftime("%Y-%m-%d %H:%M")
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO documents (id, name, size, uploaded_at, status, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
                (doc_id, display_name, size_mb, uploaded_at_str, "indexed", user_id)
            )
            
    print(f"Successfully ingested {display_name} into ChromaDB with {len(chunks)} chunks.")

def sync_to_json():
    """Sync database documents to documents.json."""
    docs = []
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, size, uploaded_at, status, user_id FROM documents ORDER BY created_at DESC"
            )
            rows = cur.fetchall()
            for r in rows:
                docs.append({
                    "id": r[0],
                    "name": r[1],
                    "size": r[2],
                    "uploadedAt": r[3],
                    "status": r[4],
                    "user_id": str(r[5]) if r[5] else None
                })
    
    with open(DOCS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    print("Synchronized DB documents to documents.json")

async def main():
    clear_existing_data()
    user_id = get_jury_user_id()
    if not user_id:
        print("Error: No user found in database. Run seed.py first.")
        return
    print(f"Using User ID: {user_id} for document owner.")
    
    for target in TARGETS:
        await ingest_file(target, user_id)
        
    sync_to_json()
    print("--- REBUILD COMPLETED SUCCESSFULLY ---")

if __name__ == "__main__":
    asyncio.run(main())
