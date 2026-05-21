from pathlib import Path
from core.cache import pdf_cache

def test_fastapi_health(client):
    """Kiểm thử hoạt động của mock FastAPI Client thông qua api /health."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert "Financial Analyzer" in data["service"]

def test_mock_redis():
    """Kiểm thử mock Redis cache hoạt động đúng."""
    # Set một giá trị cache giả lập
    pdf_cache.set_pdf_cache("dummy_path.pdf", "cached_content_123")
    
    # Lấy giá trị ra và kiểm tra tính nhất quang
    cached = pdf_cache.get_pdf_cache("dummy_path.pdf")
    assert cached == "cached_content_123"

def test_temporary_file_creation():
    """Kiểm thử việc tạo file tạm trong tmp/ để kiểm tra cơ chế dọn dẹp tự động."""
    project_root = Path(__file__).parent.parent.parent.parent.absolute()
    tmp_dir = project_root / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = tmp_dir / "test_smoke_temp.tmp"
    test_file.write_text("Dữ liệu tạm thời phát sinh trong quá trình chạy test.", encoding="utf-8")
    
    assert test_file.exists()
    assert test_file.read_text(encoding="utf-8") == "Dữ liệu tạm thời phát sinh trong quá trình chạy test."
