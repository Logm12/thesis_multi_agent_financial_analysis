import os
import sys
import io
from pathlib import Path
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# 1. Cấu hình encoding cho console Windows (Fix UnicodeEncodeError)
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# 2. Thêm đường dẫn project và backend vào sys.path để tránh shadow import
project_root = str(Path(__file__).parent.parent.absolute())
backend_path = os.path.join(project_root, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
if project_root not in sys.path:
    sys.path.insert(1, project_root)

# 3. Import app từ LangGraph (Fix NameError)
from backend.agents.graph import get_graph_app

def test_router_cases():
    """Kiểm thử sự phân loại của Router Node với các trường hợp mẫu."""
    load_dotenv()
    
    # Các trường hợp mẫu để test Router phân loại (Classification)
    test_queries = [
        # Retrieval
        "Doanh thu và lợi nhuận của Vingroup trong năm 2024 là bao nhiêu?",
        # Analysis
        "Đánh giá xem việc lạm phát có ảnh hưởng lớn đến hàng tồn kho không?",
        # Comparison
        "So sánh tốc độ tăng trưởng doanh thu 3 năm gần đây của doanh nghiệp này.",
        # General
        "Chào bạn, hãy giúp tôi bắt đầu."
    ]
    
    print("\n--- TEST ROUTER NODE CLASSIFICATION ---\n")
    
    for query in test_queries:
        print(f"Câu hỏi: {query}")
        print("-" * 30)
        
        # Khởi tạo state với message đầu tiên
        initial_state = {
            "messages": [HumanMessage(content=query)]
        }
        
        # Chạy qua Graph (Router node -> END)
        try:
            app = get_graph_app()
            result = app.invoke(initial_state, config={"configurable": {"thread_id": "test_router"}})
            
            # Kiểm tra kết quả
            q_type = result.get("intent")
            print(f"Kết quả phân loại: {q_type}")
        except Exception as e:
            print(f"Lỗi: {e}")
            
        print("=" * 60 + "\n")

if __name__ == "__main__":
    test_router_cases()
