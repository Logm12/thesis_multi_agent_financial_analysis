import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_upload_invalid_file():
    response = client.post("/upload", files={"file": ("test.txt", b"hello", "text/plain")})
    assert response.status_code == 400
    assert "Chỉ hỗ trợ file PDF" in response.json()["detail"]

@pytest.mark.parametrize("query,expected_intent", [
    ("Lợi nhuận của HPG năm 2023 là bao nhiêu?", "retrieve"),
    ("Vẽ biểu đồ doanh thu FPT 3 năm qua", "code"),
    ("So sánh nợ vay của Vingroup và Masan", "retrieve"),
    ("Tính tỷ suất lợi nhuận trên vốn chủ sở hữu ROE của Vinamilk", "code"),
    ("Ai là chủ tịch của Vietcombank?", "retrieve"),
    ("Dự báo tăng trưởng doanh thu của MWG", "code"),
    ("Tải file báo cáo tài chính của REE", "retrieve"),
    ("Phân tích cơ cấu tài sản của GAS", "code"),
    ("Cổ tức của ACB năm vừa rồi là bao nhiêu?", "retrieve"),
    ("Tính biên lợi nhuận gộp của PNJ", "code"),
])
def test_router_classification(query, expected_intent):
    # Test logic classification qua agent (mocked or real)
    from agents.router import router_node
    from agents.state import AgentState
    state = {"messages": [{"content": query}], "question": query}
    result = router_node(state)
    assert result["intent"] == expected_intent

def test_chat_stream_status():
    # Kiểm tra xem endpoint có trả về đúng header SSE không
    response = client.get("/chat-stream?message=hello&thread_id=test_thread")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

def test_error_handling_invalid_thread():
    # Sẽ test xem hệ thống có tạo folder tmp cho thread_id không
    import os
    from config import TEMP_DIR
    thread_id = "test_cleanup_thread"
    client.get(f"/chat-stream?message=test&thread_id={thread_id}")
    assert os.path.exists(TEMP_DIR / thread_id)
