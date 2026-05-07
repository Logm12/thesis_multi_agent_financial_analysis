import os
import sys
from pathlib import Path
from langchain_community.vectorstores import Chroma

# Thêm đường dẫn dự án vào sys.path để import modules
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data_processing.chunker import process_markdown_file
from src.data_processing.embedder import get_vietnamese_embedding_model

CHROMA_DB_DIR = os.path.join(project_root, "data", "chroma_db")
PROCESSED_DATA_DIR = os.path.join(project_root, "data", "processed")

def build_vector_db():
    print("[1] Bắt đầu khởi tạo hệ thống Vector Database (Chroma)")
    
    # 1. Khởi tạo Embedding Model
    embeddings = get_vietnamese_embedding_model()
    
    # 2. Xử lý Chunking (Semantic)
    all_chunks = []
    print("[2] Đang đọc và Semantic Chunking các file Markdown...")
    if not os.path.exists(PROCESSED_DATA_DIR):
        print(f"Không tìm thấy thư mục: {PROCESSED_DATA_DIR}")
        return
        
    for filename in os.listdir(PROCESSED_DATA_DIR):
        if filename.endswith(".md"):
            file_path = os.path.join(PROCESSED_DATA_DIR, filename)
            chunks = process_markdown_file(file_path)
            all_chunks.extend(chunks)
            print(f" - {filename}: {len(chunks)} chunks")
            
    if not all_chunks:
        print("Không có chunk nào được tạo ra.")
        return
        
    print(f"[3] Đang tiến hành Vector hóa (Embedding) và lưu vào ChromaDB ({len(all_chunks)} chunks).")
    print(f"Lưu ý: Thư mục CSDL sẽ lưu tại {CHROMA_DB_DIR}")
    
    # Sử dụng Chroma via langchain-community
    vectorstore = Chroma.from_documents(
        documents=all_chunks, 
        embedding=embeddings, 
        persist_directory=CHROMA_DB_DIR
    )
    
    # Lưu xuống ổ đĩa (Chroma phiên bản mới tự persist, nhưng gọi persist() để an tâm trên bản cũ)
    print("✅ Đã tạo VectorDB thành công!")
    return vectorstore

if __name__ == "__main__":
    build_vector_db()
