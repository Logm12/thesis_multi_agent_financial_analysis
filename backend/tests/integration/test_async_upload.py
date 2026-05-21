import os
import io
import pytest
import sys
import asyncio
from unittest.mock import MagicMock, patch
from fastapi import BackgroundTasks

# Create a clean mock easyocr package structure
mock_easyocr = MagicMock()
mock_reader = MagicMock()
mock_reader.readtext.return_value = [
    ([[10.0, 10.0], [100.0, 10.0], [100.0, 50.0], [10.0, 50.0]], "BCTC Cong Ty Co Phan Sua Viet Nam", 0.99)
]
mock_easyocr.Reader.return_value = mock_reader

# Inject mock easyocr before import to prevent downloading weights
sys.modules["easyocr"] = mock_easyocr

from backend.main import app
from backend.services.ocr.pdf_parser import FastPDFParser
from backend.api.document import _task_store, _hash_store

def setup_mocks(monkeypatch):
    """
    Mock all heavy operations (parsing, chunking, database, embeddings)
    to ensure instant, reliable test execution.
    Can be called directly from runner scripts without using pytest fixtures.
    """
    # 1. Mock Chroma
    mock_chroma_instance = MagicMock()
    monkeypatch.setattr("backend.api.document.Chroma", lambda *args, **kwargs: mock_chroma_instance)
    
    # 2. Mock OpenAIEmbeddings
    monkeypatch.setattr("backend.api.document.get_openai_embedding_model", lambda *args, **kwargs: MagicMock())
    
    # 3. Mock process_blocks chunker
    monkeypatch.setattr("backend.api.document.process_blocks", lambda *args, **kwargs: [MagicMock()])
    
    # 4. Mock FastPDFParser.parse_blocks across all possible import namespaces to prevent sys.path module identity issues
    mocked_blocks = [{"text": "Mocked digital content", "page": 1, "bbox": "[10.0, 10.0, 100.0, 50.0]", "type": "text"}]
    
    # Patch FastPDFParser directly in backend.api.document namespace
    import backend.api.document
    monkeypatch.setattr(backend.api.document.FastPDFParser, "parse_blocks", lambda self, file_path: mocked_blocks)
    
    # Patch FastPDFParser in services.ocr.pdf_parser namespace
    try:
        import services.ocr.pdf_parser
        monkeypatch.setattr(services.ocr.pdf_parser.FastPDFParser, "parse_blocks", lambda self, file_path: mocked_blocks)
    except ImportError:
        pass
        
    # Patch FastPDFParser in backend.services.ocr.pdf_parser namespace
    try:
        import backend.services.ocr.pdf_parser
        monkeypatch.setattr(backend.services.ocr.pdf_parser.FastPDFParser, "parse_blocks", lambda self, file_path: mocked_blocks)
    except ImportError:
        pass
        
    # Patch the class itself in this module's scope
    monkeypatch.setattr(FastPDFParser, "parse_blocks", lambda self, file_path: mocked_blocks)
    
    # 5. Mock BackgroundTasks.add_task to schedule cleanly in the active running event loop
    def mock_add_task(self, func, *args, **kwargs):
        asyncio.create_task(func(*args, **kwargs))
    monkeypatch.setattr(BackgroundTasks, "add_task", mock_add_task)
    
    # 6. Mock asyncio.to_thread to run synchronously and immediately in the same thread
    async def mock_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)
    monkeypatch.setattr(asyncio, "to_thread", mock_to_thread)
    
    # Clear task store and hash store for each test case
    _task_store.clear()
    _hash_store.clear()

@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    """Fixture that delegates to setup_mocks."""
    setup_mocks(monkeypatch)

def test_async_upload_digital_pdf(client):
    """
    Test uploading a digital (unscanned) PDF.
    Verifies full async pipeline status transitions (pending -> processing -> completed).
    """
    pdf_content = b"%PDF-1.4 mock digital content"

    # Upload file
    response = client.post(
        "/api/v1/upload-pdf",
        files={"file": ("VNM_BCTC.pdf", io.BytesIO(pdf_content), "application/pdf")}
    )
    
    assert response.status_code == 202
    res_data = response.json()
    assert "task_id" in res_data
    task_id = res_data["task_id"]
    assert task_id != "existing"

    # Poll status synchronously since the task was scheduled in the event loop
    import time
    for _ in range(30):
        status_response = client.get(f"/api/v1/status/{task_id}")
        assert status_response.status_code == 200
        status_data = status_response.json()
        if status_data["status"] == "completed":
            break
        elif status_data["status"] == "failed":
            pytest.fail(f"Processing failed: {status_data['details']}")
        time.sleep(0.1)
    else:
        pytest.fail("Polling timed out before completing")

    assert status_data["status"] == "completed"
    assert "Successfully processed" in status_data["details"]

def test_async_upload_scanned_pdf_ocr_fallback(client, monkeypatch):
    """
    Test uploading a scanned PDF that triggers the OCR fallback.
    Verifies that the EasyOCR fallback is executed and returns mock text successfully.
    """
    # Force FastPDFParser to run OCR path
    def mock_parse_blocks_scanned(self, file_path):
        self._init_ocr()
        img = sys.modules["numpy"].zeros((100, 100, 3), dtype=sys.modules["numpy"].uint8)
        results = self.reader.readtext(img, detail=1)
        
        blocks = []
        for res in results:
            bbox_ocr, text_ocr, prob = res
            blocks.append({
                "text": text_ocr,
                "page": 1,
                "bbox": "[10.0, 10.0, 100.0, 50.0]",
                "type": "text"
            })
        return blocks

    import backend.api.document
    monkeypatch.setattr(backend.api.document.FastPDFParser, "parse_blocks", mock_parse_blocks_scanned)

    pdf_content = b"%PDF-1.4 mock scanned"
    response = client.post(
        "/api/v1/upload-pdf",
        files={"file": ("Scanned_BCTC.pdf", io.BytesIO(pdf_content), "application/pdf")}
    )
    
    assert response.status_code == 202
    task_id = response.json()["task_id"]

    import time
    for _ in range(30):
        status_response = client.get(f"/api/v1/status/{task_id}")
        assert status_response.status_code == 200
        status_data = status_response.json()
        if status_data["status"] == "completed":
            break
        elif status_data["status"] == "failed":
            pytest.fail(f"Processing failed: {status_data['details']}")
        time.sleep(0.1)
    else:
        pytest.fail("Polling timed out")

    assert status_data["status"] == "completed"
    assert "Successfully processed" in status_data["details"]

def test_upload_deduplication(client):
    """
    Test deduplication flow by uploading the same PDF file twice.
    The second upload should instantly return 'existing' status.
    """
    pdf_content = b"%PDF-1.4 deduplication test content"
    
    # First Upload
    resp1 = client.post(
        "/api/v1/upload-pdf",
        files={"file": ("Duplicate_Test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    )
    assert resp1.status_code == 202
    task_id1 = resp1.json()["task_id"]
    assert task_id1 != "existing"

    # Second Upload (Same Content)
    resp2 = client.post(
        "/api/v1/upload-pdf",
        files={"file": ("Duplicate_Test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    )
    assert resp2.status_code == 202
    res_data2 = resp2.json()
    assert res_data2["task_id"] == "existing"
    assert "File already processed" in res_data2["message"]

    # Status checking for 'existing' task
    status_resp = client.get("/api/v1/status/existing")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["status"] == "completed"
    assert "File already existed" in status_data["details"]
