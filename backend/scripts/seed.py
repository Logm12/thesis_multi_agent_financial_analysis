import os
import sys
import json
import bcrypt
import uuid

# Add backend_dir to sys.path to resolve imports correctly
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from core.database import init_db, get_db_connection
from core.config import DATA_DIR

def seed_data():
    # 1. Initialize DB Schema
    init_db()

    # Default Jury Credentials
    jury_email = "giamkhao@lumo.ai"
    jury_password = "LumoAI@2026"
    jury_name = "Giám Khảo"
    jury_role = "USER"

    print(f"[Seed] Seeding jury account: {jury_email}...")

    # Hash Password
    password_hash = bcrypt.hashpw(jury_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user_id = None
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Check if user already exists
            cur.execute("SELECT id FROM users WHERE email = %s", (jury_email,))
            row = cur.fetchone()
            if row:
                user_id = row[0]
                print(f"[Seed] Jury account already exists (ID: {user_id}). Updating password...")
                cur.execute(
                    "UPDATE users SET password_hash = %s, full_name = %s, role = %s WHERE id = %s",
                    (password_hash, jury_name, jury_role, user_id)
                )
            else:
                user_id = str(uuid.uuid4())
                cur.execute(
                    "INSERT INTO users (id, email, full_name, password_hash, role) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, jury_email, jury_name, password_hash, jury_role)
                )
                print(f"[Seed] Jury account created successfully (ID: {user_id}).")

            # 2. Seed existing documents from data/documents.json
            docs_json_path = os.path.join(DATA_DIR, "documents.json")
            if os.path.exists(docs_json_path):
                print(f"[Seed] Reading documents from {docs_json_path}...")
                try:
                    with open(docs_json_path, "r", encoding="utf-8") as f:
                        docs_list = json.load(f)
                    
                    for doc in docs_list:
                        doc_id = doc.get("id")
                        doc_name = doc.get("name")
                        doc_size = doc.get("size", "0.0 MB")
                        uploaded_at = doc.get("uploadedAt", "")
                        status = doc.get("status", "indexed")

                        if not doc_id or not doc_name:
                            continue

                        # Check if document exists in db
                        cur.execute("SELECT id FROM documents WHERE id = %s", (doc_id,))
                        if cur.fetchone():
                            # Update existing document user_id
                            cur.execute(
                                "UPDATE documents SET name = %s, size = %s, uploaded_at = %s, status = %s, user_id = %s WHERE id = %s",
                                (doc_name, doc_size, uploaded_at, status, user_id, doc_id)
                            )
                        else:
                            # Insert new document linked to jury
                            cur.execute(
                                "INSERT INTO documents (id, name, size, uploaded_at, status, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
                                (doc_id, doc_name, doc_size, uploaded_at, status, user_id)
                            )
                    print(f"[Seed] Linked {len(docs_list)} documents to jury account.")
                except Exception as e:
                    print(f"[Seed] Error reading/seeding documents.json: {str(e)}")
            else:
                print(f"[Seed] Warning: {docs_json_path} not found. Skipping document links.")

    print("[Seed] Seeding completed successfully.")

if __name__ == "__main__":
    seed_data()
