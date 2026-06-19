import os
import psycopg
from contextlib import contextmanager
from core.config import POSTGRES_URL

@contextmanager
def get_db_connection():
    """Context manager for obtaining a database connection."""
    conn = psycopg.connect(POSTGRES_URL)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initializes the database schema using core/schema.sql."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    if not os.path.exists(schema_path):
        print(f"[Database] Error: schema.sql not found at {schema_path}")
        return

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    print("[Database] Initializing schema...")
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
        print("[Database] Schema initialized successfully.")
    except Exception as e:
        print(f"[Database] Error initializing schema: {str(e)}")
        raise e

def log_session_audit(session_id: str, question: str, answer: str, steps: list, chart_b64: str = None, warnings: list = None):
    """Writes session audit details to PostgreSQL database."""
    import json
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO session_audit (session_id, question, answer, steps, chart_b64, warnings) VALUES (%s, %s, %s, %s, %s, %s)",
                    (session_id, question, answer, json.dumps(steps), chart_b64, json.dumps(warnings or []))
                )
    except Exception as e:
        print(f"[Database Error] log_session_audit failed: {str(e)}")

def cleanup_session(session_id: str, temp_dir_path: str):
    """Deletes the temporary directory of a session using shutil.rmtree."""
    import shutil
    if temp_dir_path and os.path.exists(temp_dir_path):
        try:
            shutil.rmtree(temp_dir_path, ignore_errors=True)
            print(f"[Cleanup] Cleaned up temporary directory: {temp_dir_path}")
        except Exception as e:
            print(f"[Cleanup Warning] Failed to delete temp directory {temp_dir_path}: {str(e)}")
