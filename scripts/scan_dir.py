import os
import datetime

def scan_directory(root_dir):
    ignore_dirs = {
        '.git', '__pycache__', 'node_modules', 'dist', '.gemini', 
        '.idea', '.vscode', 'venv', '.env_venv', 'antigravity-awesome-skills'
    }
    ignore_files = {
        '.DS_Store', 'Thumbs.db', 'first_27_pages_ocr.md', 'out.txt'
    }
    
    tree_lines = []
    
    def walk_tree(current_dir, prefix=""):
        try:
            items = sorted(os.listdir(current_dir))
        except Exception as e:
            return
            
        # Filter out ignored directories and files
        filtered_items = []
        for item in items:
            path = os.path.join(current_dir, item)
            if os.path.isdir(path):
                if item not in ignore_dirs:
                    filtered_items.append((item, True))
            else:
                if item not in ignore_files:
                    filtered_items.append((item, False))
                    
        count = len(filtered_items)
        for i, (name, is_dir) in enumerate(filtered_items):
            is_last = (i == count - 1)
            connector = "└── " if is_last else "├── "
            
            if is_dir:
                tree_lines.append(f"{prefix}{connector}📂 {name}/")
                new_prefix = prefix + ("    " if is_last else "│   ")
                walk_tree(os.path.join(current_dir, name), new_prefix)
            else:
                size = os.path.getsize(os.path.join(current_dir, name))
                # Human readable size
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size/1024:.1f} KB"
                else:
                    size_str = f"{size/(1024*1024):.1f} MB"
                tree_lines.append(f"{prefix}{connector}📄 {name} ({size_str})")

    tree_lines.append(f"📂 {os.path.basename(os.path.abspath(root_dir))}/")
    walk_tree(root_dir)
    return "\n".join(tree_lines)

def generate_report():
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"[Scan] Scanning root directory: {root_path}...")
    dir_tree = scan_directory(root_path)
    
    md_content = f"""# SƠ ĐỒ THƯ MỤC DỰ ÁN (PROJECT DIRECTORY SCAN)

**Ngày quét:** {current_time}  
**Thư mục gốc:** `{root_path}`

---

## 1. Cấu trúc cây thư mục (Directory Tree)
Dưới đây là sơ đồ cấu trúc tệp tin và thư mục thực tế của dự án (đã bỏ qua các thư mục môi trường ảo và file rác hệ thống):

```text
{dir_tree}
```

---

## 2. Mô tả các thành phần cốt lõi

### 📂 `backend/` (Ứng dụng Máy chủ API & AI Agents)
Thành phần trung tâm của hệ thống xử lý logic nghiệp vụ và chạy các tác tử thông minh:
*   **📂 `api/`**: Nơi chứa cấu trúc định tuyến (routes) và các endpoint API của FastAPI:
    *   📄 `server.py`: Điểm khởi chạy của máy chủ FastAPI, thiết lập cấu hình CORS và các middleware.
    *   📄 `document.py`: Quản lý các endpoint nạp PDF, kiểm tra deduplication, kiểm tra trạng thái và xóa tài liệu.
    *   📄 `document_store.py`: Tương tác lưu trữ siêu dữ liệu (metadata) của tài liệu trên hệ thống.
*   **📂 `agents/`**: Hệ thống các Agent xử lý tài chính được xây dựng trên **LangGraph**:
    *   📄 `graph.py`: Định nghĩa cấu trúc đồ thị trạng thái luồng làm việc của Multi-Agent.
    *   📄 `state.py`: Định nghĩa mô hình dữ liệu dùng chung (State) xuyên suốt đồ thị tác tử.
    *   📄 `router.py`, `retriever.py`, `coder.py`, `synthesizer.py`: Các nút tác tử chuyên biệt.
*   **📂 `data_processing/`**: Pipeline tiền xử lý văn bản báo cáo tài chính:
    *   📄 `pdf_parser.py`: Bộ máy trích xuất PDF thông minh kết hợp cơ chế OCR Fallback qua EasyOCR.
    *   📄 `cleaner.py`: Làm sạch văn bản tiếng Việt thô, chuẩn hóa khoảng trắng và ký tự lỗi.
    *   📄 `chunker.py`: Cắt văn bản thành các đoạn nhỏ dựa trên cấu trúc Markdown.
*   **📂 `utils/`**: Các công cụ tiện ích bổ trợ:
    *   📄 `cache.py`: Quản lý bộ nhớ đệm Redis cho PDF Parsing giúp tránh chạy lại OCR nhiều lần.

### 📂 `frontend/` (Giao diện Người dùng)
Ứng dụng Web trực quan cho phép người dùng giao tiếp với các Chatbot Agent và quản lý tài liệu:
*   **Vận hành bởi:** Vite + React + TypeScript + Tailwind CSS.
*   **📂 `src/`**: Chứa toàn bộ các components giao diện, trang tổng quan và hook xử lý REST API.

### 📂 `scripts/` (Công cụ Bảo trì & Thử nghiệm)
*   📄 `scan_dir.py`: Script tự động tạo sơ đồ thư mục này.
*   📄 `test_ocr_27.py`: Script benchmark thử nghiệm 27 trang của BCTC quét sử dụng EasyOCR.
*   📄 `crawl_data.py`: Crawler tự động tải báo cáo tài chính giai đoạn 2020-2025 từ nguồn CafeF.

### 📄 `tech_stack.md`
Tài liệu chỉ rõ cấu trúc công nghệ sử dụng, vị trí áp dụng và vai trò của từng thư viện trong hệ thống.
"""
    
    output_path = os.path.join(root_path, "directory_scan.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"[Scan] Directory scan successfully written to: {output_path}")

if __name__ == "__main__":
    generate_report()
