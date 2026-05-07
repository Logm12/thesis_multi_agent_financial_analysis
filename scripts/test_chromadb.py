import os
import sys
import time
from pathlib import Path
from langchain_community.vectorstores import Chroma

project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data_processing.embedder import get_vietnamese_embedding_model

CHROMA_DB_DIR = os.path.join(project_root, "data", "chroma_db")

def test_vector_retrieval():
    print("--- KIỂM THỬ TRUY XUẤT CHROMA DB ---")
    
    start_time = time.time()
    embeddings = get_vietnamese_embedding_model()
    
    if not os.path.exists(CHROMA_DB_DIR):
        print("❌ Lỗi: Chưa tìm thấy Chroma DB. Xin hãy chạy script build_vector_db.py trước.")
        return
        
    vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)
    
    # Một truy vấn mẫu bám sát ngôn ngữ báo cáo (Tiếng Việt)
    query = "Lợi nhuận gộp về bán hàng và cung cấp dịch vụ trong năm 2025 là bao nhiêu?"
    print(f"\n🔍 Truy vấn (Query): '{query}'\n")
    
    # Thực hiện search top 2 kết quả sát nhất
    results = vectorstore.similarity_search(query, k=2)
    end_time = time.time()
    
    print(f"✅ Truy xuất thành công {len(results)} kết quả trong vòng {end_time - start_time:.2f} giây:")
    for i, res in enumerate(results):
         print(f"--- [Kết quả {i+1}] ---")
         print(f"📄 Nguồn: {res.metadata.get('source', 'Unknown')} | Header Liên quan: {res.metadata}")
         print(f"📝 Trích dẫn nội dung:\n{res.page_content.strip()[:400]}...")
         print("-" * 60)

if __name__ == "__main__":
    test_vector_retrieval()
