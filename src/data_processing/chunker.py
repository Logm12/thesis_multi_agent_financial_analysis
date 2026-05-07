import os
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

def sanitize_metadata(metadata: dict) -> dict:
    """
    Sanitize metadata for ChromaDB compatibility.
    ChromaDB strictly accepts only str, int, float, or bool.
    This function flattens any nested dictionaries or lists into strings.
    """
    sanitized = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)):
            sanitized[key] = value
        elif value is None:
            sanitized[key] = ""
        else:
            # Flatten everything else to string
            sanitized[key] = str(value)
    return sanitized

def process_markdown_file(file_path: str) -> List[Document]:
    """
    Kỹ thuật Semantic Chunking: Đọc file Markdown BCTC và chia nhỏ văn bản
    dựa trên cấu trúc Header (#) để giữ ngữ nghĩa trọn vẹn của từng phần 
    (ví dụ: Bảng Cân Đối Kế Toán, Báo cáo LCTT không bị gãy đoạn).
    """
    if not os.path.exists(file_path):
        print(f"File không tồn tại: {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Bước 1: Chia theo ngữ nghĩa của Header Markdown Báo cáo tài chính
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(md_text)

    # Bước 2: Với các đoạn quá dài (ví dụ bảng dài ngầm), chặt tiếp sao cho vừa window của LLM
    # Phù hợp với tiếng Việt, giữ cụm từ liền lề, ngăn ngắt ở giữa bảng.
    chunk_size = 1000
    chunk_overlap = 150
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""] 
    )
    
    # Chia lại các document
    final_splits = text_splitter.split_documents(md_header_splits)
    
    # Thêm Metadata Source file và Sanitize cho ChromaDB
    for doc in final_splits:
        doc.metadata["source"] = os.path.basename(file_path)
        doc.metadata = sanitize_metadata(doc.metadata)
        
    return final_splits

if __name__ == "__main__":
    # Test script cục bộ
    sample_file = r"e:\Thesis\data\processed\37d37c93_1769052195.md"
    chunks = process_markdown_file(sample_file)
    print(f"Tổng số chunk sau khi Semantic Split: {len(chunks)}")
    if chunks:
         print("Sample Chunk 1:")
         print(f"Metadata: {chunks[0].metadata}")
         print(f"Content:\n{chunks[0].page_content[:200]}...")
