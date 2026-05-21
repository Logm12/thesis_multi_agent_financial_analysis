import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest

# 1. Thêm đường dẫn project và backend vào sys.path để tránh shadow import
backend_dir = Path(__file__).parent.parent.absolute()
project_root = backend_dir.parent.absolute()

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(1, str(project_root))

# Fix console encoding globally for Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')  # type: ignore[union-attr]
    except AttributeError:
        pass

# 2. Mock Redis & Postgres at import time to prevent any connection attempts during module loading
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

# Now safe to import app without any side-effects
try:
    from main import app  # noqa: E402
except ImportError:
    from backend.main import app  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402

@pytest.fixture
def client():
    """Fixture trả về FastAPI test client."""
    return TestClient(app)

@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """Fixture to expose the mock redis client if needed."""
    try:
        from core.cache import pdf_cache
        if pdf_cache:
            pdf_cache.client = mock_redis_client
    except ImportError:
        pass
    return mock_redis_client

@pytest.fixture(autouse=True)
def mock_postgres(monkeypatch):
    """Fixture to expose mock postgres pool."""
    mock_pool = MagicMock()
    return mock_pool


# 5. Strict System Cleanup Mechanism
def cleanup_temp_files():
    """
    Hàm dọn rác hệ thống tự động:
    Tìm kiếm và xóa bỏ hoàn toàn __pycache__, .pytest_cache, tmp/* và *.tmp
    An toàn và bọc trong khối try-except để không làm treo luồng kiểm thử trên Windows.
    """
    import shutil

    # Các mẫu file/thư mục rác cần quét dọn
    targets = [
        "**/__pycache__",
        "**/.pytest_cache",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
    ]

    print("\n[Strict System Cleanup Hook] Starting system cleanup...")

    # Dọn dẹp cache
    for pattern in targets:
        for p in list(backend_dir.glob(pattern)):
            # Bỏ qua thư mục .git và các thư mục ngoài workspace
            if ".git" in p.parts:
                continue
            try:
                if p.is_dir():
                    shutil.rmtree(p, ignore_errors=True)
                    print(f"[Cleanup Hook] Removed cache directory: {p.relative_to(project_root)}")
                elif p.is_file():
                    p.unlink(missing_ok=True)
                    print(f"[Cleanup Hook] Removed cache file: {p.relative_to(project_root)}")
            except Exception as e:
                print(f"[Cleanup Hook] Warning - could not remove {p.name}: {e}")

    # Dọn dẹp thư mục tmp/
    tmp_dir = project_root / "tmp"
    if tmp_dir.exists() and tmp_dir.is_dir():
        print(f"[Strict System Cleanup Hook] Cleaning temp directory: {tmp_dir}")
        for item in tmp_dir.iterdir():
            try:
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                    print(f"[Cleanup Hook] Removed temp directory: {item.relative_to(project_root)}")
                elif item.is_file():
                    item.unlink(missing_ok=True)
                    print(f"[Cleanup Hook] Removed temp file: {item.relative_to(project_root)}")
            except Exception as e:
                print(f"[Cleanup Hook] Warning - could not remove temp item {item.name}: {e}")

def pytest_sessionstart(session):
    """Chạy dọn rác trước khi phiên test bắt đầu để đảm bảo vệ sinh môi trường."""
    cleanup_temp_files()

def pytest_sessionfinish(session, exitstatus):
    """Chạy dọn rác ngay khi phiên test hoàn thành để giải phóng tài nguyên."""
    cleanup_temp_files()
