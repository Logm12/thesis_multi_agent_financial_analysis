import os
import sys
import io
from pathlib import Path
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# 1. Cấu hình encoding cho console Windows (Fix UnicodeEncodeError)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 2. Thêm đường dẫn project vào sys.path để import được src
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 3. Import app từ LangGraph (Fix NameError)
from src.agents.graph import app

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
            result = app.invoke(initial_state)
            
            # Kiểm tra kết quả
            q_type = result.get("question_type")
            print(f"Kết quả phân loại: {q_type}")
        except Exception as e:
            print(f"Lỗi: {e}")
            
        print("=" * 60 + "\n")

if __name__ == "__main__":
    test_router_cases()
