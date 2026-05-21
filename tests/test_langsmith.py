import os
import sys
import io
from dotenv import load_dotenv
from langsmith import Client

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    load_dotenv()
    
    api_key = os.getenv("LANGCHAIN_API_KEY")
    project = os.getenv("LANGCHAIN_PROJECT")
    
    if not api_key or api_key == "your_langsmith_api_key_here":
        print("❌ Lỗi: Chưa cấu hình LANGCHAIN_API_KEY trong file .env")
        return
        
    try:
        # Khởi tạo client
        client = Client()
        
        print(f"✅ Đã kết nối thành công tới LangSmith!")
        print(f"Project name: {project}")
        
        # Thử tạo một project để xem quyền
        print("Đang kiểm tra quyền tạo/đọc project...")
        if not client.has_project(project):
            client.create_project(project_name=project, description="Project for Thesis Financial Analyzer")
            print(f"✅ Đã tạo project '{project}' trên LangSmith.")
        else:
            print(f"✅ Project '{project}' đã tồn tại trên LangSmith.")
            
        print("-" * 50)
        print("Bạn có thể đăng nhập vào https://smith.langchain.com/ để theo dõi các traces sau này.")
        
    except Exception as e:
        print(f"❌ Có lỗi xảy ra khi kết nối LangSmith: {e}")

if __name__ == "__main__":
    main()
