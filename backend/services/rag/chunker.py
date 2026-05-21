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

def process_blocks(blocks: list, source_name: str) -> List[Document]:
    """
    Kỹ thuật Semantic Chunking: Đọc danh sách block từ PDF (text, table) 
    và chia nhỏ văn bản, giữ nguyên bảng biểu nguyên khối.
    """
    # Bước 1: Cấu hình splitter
    chunk_size = 1000
    chunk_overlap = 150
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""] 
    )
    
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    final_splits = []
    
    for block in blocks:
        text = block.get("text", "")
        if not text.strip():
            continue
            
        if block.get("type") == "table":
            # Bảng biểu: Giữ nguyên khối không ngắt
            doc = Document(
                page_content=text,
                metadata={
                    "page": block["page"],
                    "bbox": block["bbox"],
                    "source": source_name,
                    "type": "table"
                }
            )
            doc.metadata = sanitize_metadata(doc.metadata)
            final_splits.append(doc)
        else:
            # Text thông thường: Phân tích header và chunk
            md_header_splits = markdown_splitter.split_text(text)
            splits = text_splitter.split_documents(md_header_splits)
            
            for s in splits:
                s.metadata["page"] = block["page"]
                s.metadata["bbox"] = block["bbox"]
                s.metadata["source"] = source_name
                s.metadata["type"] = "text"
                s.metadata = sanitize_metadata(s.metadata)
                final_splits.append(s)
                
    return final_splits

if __name__ == "__main__":
    # Test script cục bộ
    import json
    sample_file = r"e:\Thesis\data\processed\test.json"
    if os.path.exists(sample_file):
        with open(sample_file, "r", encoding="utf-8") as f:
            blocks = json.load(f)
        chunks = process_blocks(blocks, "test.json")
        print(f"Tổng số chunk sau khi Semantic Split: {len(chunks)}")
        if chunks:
             print("Sample Chunk 1:")
             print(f"Metadata: {chunks[0].metadata}")
             print(f"Content:\n{chunks[0].page_content[:200]}...")
