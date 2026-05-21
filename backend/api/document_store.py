import json
import os
import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from core.config import DATA_DIR
from core.database import get_db_connection

DOCS_JSON_PATH = Path(DATA_DIR) / "documents.json"

def _sync_to_json():
    """Reads all documents from DB and saves them to documents.json for backward compatibility."""
    try:
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
        
        DOCS_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DOCS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[DocumentStore Warning] Failed to sync to documents.json: {str(e)}")

def get_all_documents(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all documents. If user_id is provided, filters documents by owner (tenant isolation)."""
    try:
        docs = []
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if user_id:
                    cur.execute(
                        "SELECT id, name, size, uploaded_at, status, user_id FROM documents WHERE user_id = %s ORDER BY created_at DESC",
                        (user_id,)
                    )
                else:
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
        return docs
    except Exception as e:
        print(f"[DocumentStore] DB error in get_all_documents, falling back to JSON: {str(e)}")
        # Fallback to JSON
        if not DOCS_JSON_PATH.exists():
            return []
        try:
            with open(DOCS_JSON_PATH, "r", encoding="utf-8") as f:
                docs = json.load(f)
            if user_id:
                docs = [d for d in docs if d.get("user_id") == user_id]
            return docs
        except Exception:
            return []

def add_document(doc_id: str, name: str, size: str, status: str = "processing", user_id: Optional[str] = None) -> Dict[str, Any]:
    """Adds a new document to the database and syncs with the JSON file."""
    uploaded_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Delete existing if same ID
                cur.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
                cur.execute(
                    "INSERT INTO documents (id, name, size, uploaded_at, status, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
                    (doc_id, name, size, uploaded_at, status, user_id)
                )
        # Sync to JSON
        _sync_to_json()
    except Exception as e:
        print(f"[DocumentStore] DB error in add_document: {str(e)}")
        # Fallback in-memory/JSON write
        docs = []
        if DOCS_JSON_PATH.exists():
            try:
                with open(DOCS_JSON_PATH, "r", encoding="utf-8") as f:
                    docs = json.load(f)
            except Exception:
                pass
        docs = [d for d in docs if d["id"] != doc_id]
        new_doc = {
            "id": doc_id,
            "name": name,
            "size": size,
            "uploadedAt": uploaded_at,
            "status": status,
            "user_id": user_id
        }
        docs.insert(0, new_doc)
        try:
            with open(DOCS_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(docs, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
            
    return {
        "id": doc_id,
        "name": name,
        "size": size,
        "uploadedAt": uploaded_at,
        "status": status,
        "user_id": user_id
    }

def update_document_status(doc_id: str, status: str) -> bool:
    """Updates the status of a document."""
    found = False
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE documents SET status = %s WHERE id = %s RETURNING id", (status, doc_id))
                if cur.fetchone():
                    found = True
        if found:
            _sync_to_json()
        return found
    except Exception as e:
        print(f"[DocumentStore] DB error in update_document_status: {str(e)}")
        # Fallback JSON write
        if not DOCS_JSON_PATH.exists():
            return False
        try:
            with open(DOCS_JSON_PATH, "r", encoding="utf-8") as f:
                docs = json.load(f)
            for d in docs:
                if d["id"] == doc_id:
                    d["status"] = status
                    found = True
                    break
            if found:
                with open(DOCS_JSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(docs, f, ensure_ascii=False, indent=2)
            return found
        except Exception:
            return False

def rename_document(doc_id: str, new_name: str, user_id: Optional[str] = None) -> bool:
    """Renames a document, ensuring user ownership if user_id is provided."""
    found = False
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if user_id:
                    cur.execute(
                        "UPDATE documents SET name = %s WHERE id = %s AND user_id = %s RETURNING id",
                        (new_name, doc_id, user_id)
                    )
                else:
                    cur.execute(
                        "UPDATE documents SET name = %s WHERE id = %s RETURNING id",
                        (new_name, doc_id)
                    )
                if cur.fetchone():
                    found = True
        if found:
            _sync_to_json()
        return found
    except Exception as e:
        print(f"[DocumentStore] DB error in rename_document: {str(e)}")
        # Fallback JSON
        if not DOCS_JSON_PATH.exists():
            return False
        try:
            with open(DOCS_JSON_PATH, "r", encoding="utf-8") as f:
                docs = json.load(f)
            for d in docs:
                if d["id"] == doc_id:
                    if not user_id or d.get("user_id") == user_id:
                        d["name"] = new_name
                        found = True
                        break
            if found:
                with open(DOCS_JSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(docs, f, ensure_ascii=False, indent=2)
            return found
        except Exception:
            return False

def delete_document(doc_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Deletes a document, ensuring user ownership if user_id is provided. Returns deleted doc metadata."""
    deleted_doc = None
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Select first
                if user_id:
                    cur.execute(
                        "SELECT id, name, size, uploaded_at, status, user_id FROM documents WHERE id = %s AND user_id = %s",
                        (doc_id, user_id)
                    )
                else:
                    cur.execute(
                        "SELECT id, name, size, uploaded_at, status, user_id FROM documents WHERE id = %s",
                        (doc_id,)
                    )
                r = cur.fetchone()
                if r:
                    deleted_doc = {
                        "id": r[0],
                        "name": r[1],
                        "size": r[2],
                        "uploadedAt": r[3],
                        "status": r[4],
                        "user_id": str(r[5]) if r[5] else None
                    }
                    cur.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
        if deleted_doc:
            _sync_to_json()
        return deleted_doc
    except Exception as e:
        print(f"[DocumentStore] DB error in delete_document: {str(e)}")
        # Fallback JSON
        if not DOCS_JSON_PATH.exists():
            return None
        try:
            with open(DOCS_JSON_PATH, "r", encoding="utf-8") as f:
                docs = json.load(f)
            for d in docs:
                if d["id"] == doc_id:
                    if not user_id or d.get("user_id") == user_id:
                        deleted_doc = d
                        break
            if deleted_doc:
                docs = [d for d in docs if d["id"] != doc_id]
                with open(DOCS_JSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(docs, f, ensure_ascii=False, indent=2)
            return deleted_doc
        except Exception:
            return None
