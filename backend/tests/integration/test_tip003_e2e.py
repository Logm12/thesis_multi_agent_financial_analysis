import sys
from unittest.mock import MagicMock

# Mock easyocr to avoid Torch/CUDA download/initialization
mock_easyocr = MagicMock()
mock_reader = MagicMock()
mock_reader.readtext.return_value = [([[10, 10], [100, 10], [100, 50], [10, 50]], "Mocked easyocr output text", 0.99)]
mock_easyocr.Reader.return_value = mock_reader
sys.modules["easyocr"] = mock_easyocr

import os
import pytest
import asyncio
from fastapi import BackgroundTasks
from backend.main import app
from backend.api.document import _task_store, _hash_store

@pytest.fixture(autouse=True)
def mock_dependencies_qa(monkeypatch):
    # Mock Chroma
    mock_chroma_instance = MagicMock()
    monkeypatch.setattr("backend.api.document.Chroma", lambda *args, **kwargs: mock_chroma_instance)
    
    # Mock OpenAIEmbeddings
    monkeypatch.setattr("backend.api.document.get_openai_embedding_model", lambda *args, **kwargs: MagicMock())
    
    # Mock process_blocks chunker
    monkeypatch.setattr("backend.api.document.process_blocks", lambda *args, **kwargs: [MagicMock()])
    
    # Mock FastPDFParser
    mocked_blocks = [{"text": "Mocked QA digital content for financial analysis", "page": 1, "bbox": "[10.0, 10.0, 100.0, 50.0]", "type": "text"}]
    monkeypatch.setattr("backend.api.document.FastPDFParser.parse_blocks", lambda self, file_path, *args, **kwargs: mocked_blocks)
    
    # Mock BackgroundTasks.add_task
    def mock_add_task(self, func, *args, **kwargs):
        asyncio.create_task(func(*args, **kwargs))
    monkeypatch.setattr(BackgroundTasks, "add_task", mock_add_task)
    
    # Mock asyncio.to_thread
    async def mock_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)
    monkeypatch.setattr(asyncio, "to_thread", mock_to_thread)
    
    _task_store.clear()
    _hash_store.clear()

def test_headless_qa_ingest_digital(client, tmp_path):
    # Create a dummy PDF file
    dummy_pdf = tmp_path / "test_digital.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4 mock content")
    
    payload = {
        "file_path": str(dummy_pdf),
        "extraction_method": "digital"
    }
    
    # Trigger headless ingest
    response = client.post("/api/v1/test/ingest-automated", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert "task_id" in res_data
    assert res_data["cache_hit"] is False
    
    task_id = res_data["task_id"]
    
    # Check status
    status_response = client.get(f"/api/v1/status/{task_id}")
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "completed"
