import os
import sys
from pathlib import Path

# Thêm đường dẫn dự án vào sys.path để import modules
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data_processing.chunker import process_markdown_file
try:
    from falkordb import FalkorDB
except ImportError:
    print("Vui lòng cài đặt falkordb bằng lệnh: pip install falkordb")
    sys.exit(1)

PROCESSED_DATA_DIR = os.path.join(project_root, "data", "processed")

def build_graph_db():
    print("[1] Bắt đầu khởi tạo kết nối FalkorDB (Graph DB)")
    try:
        # FalkorDB default host is localhost, port 6379 (giống Redis)
        db = FalkorDB(host='localhost', port=6379)
        graph = db.select_graph("financial_report_graph")
        print("✅ Đã kết nối thành công tới FalkorDB Docker container!")
    except Exception as e:
        print(f"❌ Lỗi kết nối FalkorDB: {e}")
        print("Vui lòng đảm bảo container Docker FalkorDB đang chạy: docker run -p 6379:6379 -it --rm falkordb/falkordb:latest")
        return

    print("[2] Đang đọc và chia Chunk các file Markdown...")
    if not os.path.exists(PROCESSED_DATA_DIR):
        print(f"Không tìm thấy thư mục: {PROCESSED_DATA_DIR}")
        return
        
    for filename in os.listdir(PROCESSED_DATA_DIR):
        if filename.endswith(".md"):
            file_path = os.path.join(PROCESSED_DATA_DIR, filename)
            chunks = process_markdown_file(file_path)
            
            # Tạo node tài liệu gốc
            doc_query = f"MERGE (d:Document {{name: '{filename}'}}) RETURN d"
            graph.query(doc_query)
            
            print(f" - Đang map {len(chunks)} chunks của {filename} vào hệ Graph...")
            for i, chunk in enumerate(chunks):
                # An toàn hóa chuỗi JSON - tránh string break trong Cypher
                safe_text = chunk.page_content.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'")
                header_context = " | ".join(chunk.metadata.values()) if chunk.metadata else ""
                
                # Tạo Chunk Node với Header Meta và quan hệ HAS_CHUNK
                chunk_query = f"""
                MATCH (d:Document {{name: '{filename}'}})
                CREATE (c:Chunk {{index: {i}, headers: "{header_context}", text: "{safe_text[:100]}..." }})
                CREATE (d)-[:HAS_CHUNK]->(c)
                """
                graph.query(chunk_query)
            
    print("✅ Đã lưu trữ Graph nodes vào FalkorDB thành công!")
    
    # Test truy xuất: Đếm số node và đọc 1 quan hệ Document -> Chunk
    res = graph.query("MATCH (n) RETURN COUNT(n) as node_count")
    for row in res.result_set:
        print(f"🔍 Test truy xuất đồ thị: Tổng cộng có {row[0]} nodes trên FalkorDB.")
        
    print("🔍 Ví dụ truy xuất GraphRAG:")
    sample = graph.query("MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk) RETURN d.name, c.headers, c.text LIMIT 1")
    for row in sample.result_set:
        print(f"   Document: {row[0]} | Headers: {row[1]} | Text Snippet: {row[2]}")

if __name__ == "__main__":
    build_graph_db()
