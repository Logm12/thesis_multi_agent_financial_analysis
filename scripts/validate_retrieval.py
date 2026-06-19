import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from core.config import CHROMA_PATH
from services.rag.embedder import get_openai_embedding_model
from langchain_chroma import Chroma

# Force stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def validate():
    print("--- Validating ChromaDB Retrieval ---")
    embeddings = get_openai_embedding_model()
    vector_db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name="financial_docs"
    )

    queries = [
        "Doanh thu thuần hợp nhất năm 2023 của Vinamilk",
        "Lợi nhuận gộp năm 2023 của Vinamilk",
        "Chi phí bán hàng quý 4 năm 2023 của Vinamilk",
        "Chủ tịch Hội đồng Quản trị của VNM trong năm 2023 là ai",
        "Tầm nhìn của công ty FPT đến năm 2030 là gì"
    ]

    for q in queries:
        print(f"\nQuery: '{q}'")
        docs = vector_db.similarity_search(q, k=3)
        for idx, doc in enumerate(docs):
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page", "unknown")
            print(f"  Result {idx+1} [Source: {source}, Page: {page}]:")
            text_snippet = doc.page_content.strip().replace("\n", " ")[:200]
            print(f"    {text_snippet}...")

if __name__ == "__main__":
    validate()
