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
    và chia nhỏ văn bản theo trang, giữ nguyên bảng biểu nguyên khối.
    """
    import json
    chunk_size = 1000
    chunk_overlap = 150
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""] 
    )
    
    final_splits = []
    
    # Nhóm các block văn bản theo trang
    page_text_map = {}
    table_blocks = []
    
    for block in blocks:
        if block.get("type") == "table":
            table_blocks.append(block)
        else:
            page = block.get("page", 1)
            if page not in page_text_map:
                page_text_map[page] = []
            page_text_map[page].append(block)
            
    # Thêm các bảng biểu nguyên khối
    for block in table_blocks:
        doc = Document(
            page_content=block["text"],
            metadata={
                "page": block["page"],
                "bbox": block["bbox"],
                "source": source_name,
                "type": "table"
            }
        )
        doc.metadata = sanitize_metadata(doc.metadata)
        final_splits.append(doc)
        
    # Xử lý văn bản theo từng trang
    for page, page_blocks in sorted(page_text_map.items()):
        # Sắp xếp các block trên trang theo thứ tự từ trên xuống dưới
        def get_y_coord(b):
            try:
                bbox_str = b.get("bbox", "[0, 0, 0, 0]")
                coords = json.loads(bbox_str)
                return coords[1]
            except:
                return 0
                
        page_blocks.sort(key=get_y_coord)
        
        # Ghép các block văn bản trên trang
        combined_text = "\n\n".join([b["text"] for b in page_blocks if b.get("text", "").strip()])
        if not combined_text.strip():
            continue
            
        # Chia nhỏ đoạn văn bản đã ghép của trang
        splits = text_splitter.split_text(combined_text)
        for split_text in splits:
            doc = Document(
                page_content=split_text,
                metadata={
                    "page": page,
                    "bbox": page_blocks[0].get("bbox", "[0.0, 0.0, 0.0, 0.0]"),
                    "source": source_name,
                    "type": "text"
                }
            )
            doc.metadata = sanitize_metadata(doc.metadata)
            final_splits.append(doc)
            
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
