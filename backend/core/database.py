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
