import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Setup sys.path
backend_dir = Path(__file__).parent.parent.absolute()
project_root = backend_dir.parent.absolute()
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(1, str(project_root))

# Mock conftest dependencies before importing main app
import redis
mock_redis_client = MagicMock()
mock_db = {}
mock_redis_client.get.side_effect = lambda key: mock_db.get(key)
mock_redis_client.set.side_effect = lambda key, val, ex=None: mock_db.__setitem__(key, val) or True
mock_redis_client.ping.side_effect = lambda: True
redis.from_url = lambda *args, **kwargs: mock_redis_client

try:
    import psycopg_pool
    psycopg_pool.ConnectionPool = lambda *args, **kwargs: MagicMock()
except ImportError:
    pass

try:
    import psycopg
    psycopg.connect = lambda *args, **kwargs: MagicMock()
except ImportError:
    pass

from fastapi.testclient import TestClient
from backend.main import app

class MonkeyPatch:
    def setattr(self, target, name, value=None, raising=True):
        import importlib
        if value is None:
            # e.g. monkeypatch.setattr("module.submodule.ClassName", value)
            value = name
            parts = target.split('.')
            module_path = '.'.join(parts[:-1])
            attr_name = parts[-1]
            module = importlib.import_module(module_path)
            setattr(module, attr_name, value)
        else:
            # e.g. monkeypatch.setattr(obj, "attr", value)
            if isinstance(target, str):
                module = importlib.import_module(target)
                setattr(module, name, value)
            else:
                setattr(target, name, value)

def run():
    print("======================================================================")
    print("STARTING BACKEND INTEGRATION TESTS RUNNER")
    print("======================================================================")
    
    # 1. Run Coder Chart Tests
    print("\n[Coder Chart Tests] Running...")
    from backend.tests.integration.test_coder_chart import (
        test_sandbox_matplotlib_chart_generation,
        test_sandbox_multiple_plots_isolation
    )
    test_sandbox_matplotlib_chart_generation()
    print("  - test_sandbox_matplotlib_chart_generation: PASSED")
    test_sandbox_multiple_plots_isolation()
    print("  - test_sandbox_multiple_plots_isolation: PASSED")
    print("[Coder Chart Tests] ALL PASSED")

    # 2. Run Async Upload Tests
    print("\n[Async Upload Tests] Running...")
    from backend.tests.integration import test_async_upload
    
    client = TestClient(app)
    mp = MonkeyPatch()
    
    # Setup dependencies
    test_async_upload.setup_mocks(mp)
    
    # Run test cases
    print("  - Running test_async_upload_digital_pdf...")
    test_async_upload.test_async_upload_digital_pdf(client)
    print("  - test_async_upload_digital_pdf: PASSED")
    
    # Reset stores and re-mock
    test_async_upload.setup_mocks(mp)
    print("  - Running test_async_upload_scanned_pdf_ocr_fallback...")
    test_async_upload.test_async_upload_scanned_pdf_ocr_fallback(client, mp)
    print("  - test_async_upload_scanned_pdf_ocr_fallback: PASSED")
    
    # Reset stores and re-mock
    test_async_upload.setup_mocks(mp)
    print("  - Running test_upload_deduplication...")
    test_async_upload.test_upload_deduplication(client)
    print("  - test_upload_deduplication: PASSED")
    
    print("[Async Upload Tests] ALL PASSED")
    
    print("\n======================================================================")
    print("SUCCESS: ALL BACKEND INTEGRATION TESTS PASSED")
    print("======================================================================")

if __name__ == "__main__":
    run()
