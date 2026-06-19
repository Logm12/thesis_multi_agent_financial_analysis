import os
import io
import sys
import pytest
import uuid
import hashlib
from pathlib import Path
from fastapi.testclient import TestClient

# Add project root and backend path to sys.path
project_root = str(Path(__file__).parent.parent.absolute())
backend_path = os.path.join(project_root, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
if project_root not in sys.path:
    sys.path.insert(1, project_root)

from backend.api.server import app
from backend.core.database import get_db_connection
from backend.core.config import REDIS_URL
import redis

client = TestClient(app)

def clean_test_user(email: str):
    """Utility to remove test users from the database."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE email = %s", (email,))

@pytest.fixture
def unique_email():
    email = f"test_doc_{uuid.uuid4().hex}@lumo.ai"
    yield email
    clean_test_user(email)

@pytest.fixture(autouse=True)
def clean_redis():
    try:
        r = redis.from_url(REDIS_URL, socket_timeout=1)
        # Flush keys related to ingestion cache
        keys = r.keys("ingest_cache:*")
        if keys:
            r.delete(*keys)
        pdf_keys = r.keys("pdf_cache:*")
        if pdf_keys:
            r.delete(*pdf_keys)
    except Exception:
        pass

def test_upload_test_unauthenticated():
    # Calling the endpoint without login should return 401 Unauthorized
    dummy_file = io.BytesIO(b"%PDF-1.4 dummy content")
    response = client.post(
        "/api/v1/document/upload-test",
        files={"file": ("dummy.pdf", dummy_file, "application/pdf")},
        data={"session_id": "session-qa-test-101"}
    )
    assert response.status_code == 401

def test_upload_test_success_and_cache(unique_email):
    # 1. Register test user
    reg_payload = {
        "email": unique_email,
        "password": "SecurePassword123",
        "full_name": "Doc Test User"
    }
    response = client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201

    # 2. Login
    login_payload = {
        "email": unique_email,
        "password": "SecurePassword123"
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200

    # 3. Prepare PDF content and calculate expected hash
    pdf_content = b"%PDF-1.4 actual binary test content " + uuid.uuid4().bytes
    expected_hash = hashlib.sha256(pdf_content).hexdigest()
    dummy_file = io.BytesIO(pdf_content)

    # 4. First upload (Cache Miss)
    response = client.post(
        "/api/v1/document/upload-test",
        files={"file": ("test.pdf", dummy_file, "application/pdf")},
        data={"session_id": "session-qa-test-101"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["sha256"] == expected_hash
    assert data["cache_hit"] is False
    assert "task_id" in data
    task_id = data["task_id"]

    # 5. Second upload of the SAME file content (Cache Hit)
    dummy_file_dup = io.BytesIO(pdf_content)
    response_dup = client.post(
        "/api/v1/document/upload-test",
        files={"file": ("test.pdf", dummy_file_dup, "application/pdf")},
        data={"session_id": "session-qa-test-101"}
    )
    assert response_dup.status_code == 200
    data_dup = response_dup.json()
    assert data_dup["status"] == "success"
    assert data_dup["sha256"] == expected_hash
    assert data_dup["cache_hit"] is True
    assert data_dup["task_id"] == task_id

def test_pdf_parser_dual_mode_table_and_sse_progress(unique_email):
    # Test 1: Verify Dual-mode table structure in PDF parser mock/unit test
    from backend.services.ocr.pdf_parser import FastPDFParser
    import pandas as pd
    
    # Mocking a fitz table
    class MockTable:
        def __init__(self):
            self.bbox = [10.0, 20.0, 110.0, 120.0]
            self.row_count = 2
            self.col_count = 2
            
        def extract(self):
            return [["Header1", "Header2"], ["Cell1", "Cell2"]]
            
        def to_pandas(self):
            return pd.DataFrame([["Cell1", "Cell2"]], columns=["Header1", "Header2"])
            
    class MockTables:
        def __init__(self):
            self.tables = [MockTable()]
            
    class MockPage:
        def find_tables(self):
            return MockTables()
            
        def get_text(self, option):
            if option == "text":
                return "Table page text"
            return {"blocks": []}
            
        def load_page(self, num):
            return self
            
    class MockDoc:
        def __len__(self):
            return 1
        def load_page(self, num):
            return MockPage()
        def close(self):
            pass
            
    import fitz
    # Temporarily monkeypatch fitz.open to return MockDoc
    original_open = fitz.open
    fitz.open = lambda *args, **kwargs: MockDoc()
    
    try:
        parser = FastPDFParser()
        # Mock file path
        mock_file = "dummy_path.pdf"
        # We need to mock os.path.exists
        import os
        original_exists = os.path.exists
        os.path.exists = lambda path: path.endswith(".pdf")
        
        # Mock open for content hashing
        import builtins
        original_builtin_open = builtins.open
        
        class MockFileIO:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, *args): return b""
            
        builtins.open = lambda *args, **kwargs: MockFileIO()
        
        try:
            blocks = parser.parse_blocks(mock_file)
            table_blocks = [b for b in blocks if b["type"] == "table"]
            assert len(table_blocks) > 0
            tb = table_blocks[0]
            assert "table_layout" in tb
            assert "markdown" in tb["table_layout"]
            assert "json_data" in tb["table_layout"]
            assert len(tb["table_layout"]["json_data"]) == 4 # 2x2 table cells
            cell = tb["table_layout"]["json_data"][0]
            assert cell["row"] == 0
            assert cell["col"] == 0
            assert cell["text"] == "Header1"
            assert "bbox" in cell
        finally:
            os.path.exists = original_exists
            builtins.open = original_builtin_open
    finally:
        fitz.open = original_open

    # Test 2: SSE progress stream endpoint test
    # Register/Login
    reg_payload = {
        "email": unique_email,
        "password": "SecurePassword123",
        "full_name": "Doc Test User"
    }
    reg_resp = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201, f"Reg failed: {reg_resp.text}"
    
    login_payload = {
        "email": unique_email,
        "password": "SecurePassword123"
    }
    login_resp = client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    
    # We can upload a file, get task_id, and hit progress stream
    pdf_content = b"%PDF-1.4 sse test content " + uuid.uuid4().bytes
    dummy_file = io.BytesIO(pdf_content)
    
    response = client.post(
        "/api/v1/document/upload-test",
        files={"file": ("test_sse.pdf", dummy_file, "application/pdf")},
        data={"session_id": "session-sse-101"}
    )
    assert response.status_code == 200
    task_id = response.json()["task_id"]
    
    # Get progress stream
    progress_response = client.get(f"/api/v1/document/progress/{task_id}")
    assert progress_response.status_code == 200
    # Check if SSE EventSourceResponse returns progress content
    # Note: TestClient supports streaming content via iter_lines()
    lines = list(progress_response.iter_lines())
    assert len(lines) > 0
    # At least one line should contain 'event: progress' or 'event: done'
    has_event = any("event:" in line for line in lines)
    assert has_event is True



