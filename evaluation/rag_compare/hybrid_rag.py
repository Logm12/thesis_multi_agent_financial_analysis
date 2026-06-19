import os
import sys
from pathlib import Path
import re

# Add backend to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from core.config import CHROMA_PATH, EMBEDDING_MODEL, SYNTHESIZER_MODEL
from core.nim_client import get_nim_llm

class HybridRAG:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        self.db = Chroma(persist_directory=CHROMA_PATH, embedding_function=self.embeddings)
        self.llm = get_nim_llm(model_name=SYNTHESIZER_MODEL, temperature=0.0)

    def keyword_search(self, question: str, all_docs, k: int = 3):
        # Basic keyword scoring using word match frequency
        words = re.findall(r'\w+', question.lower())
        scored_docs = []
        for doc in all_docs:
            score = 0
            content = doc.page_content.lower()
            for word in words:
                if len(word) > 2:  # Ignore small stop words
                    score += content.count(word)
            scored_docs.append((doc, score))
        # Sort by score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, score in scored_docs[:k] if score > 0]

    def retrieve(self, question: str, k: int = 3):
        try:
            # Vector Search
            vector_docs = self.db.similarity_search(question, k=k)
            
            # Simple keyword search fallback/combination
            # Get a sample pool of docs to search over for keyword matching
            all_docs = self.db.similarity_search(question, k=k*3)
            keyword_docs = self.keyword_search(question, all_docs, k=k)
            
            # Merge vector and keyword docs (deduplicate)
            merged = []
            seen = set()
            for doc in vector_docs + keyword_docs:
                if doc.page_content not in seen:
                    seen.add(doc.page_content)
                    merged.append(doc)
            return [doc.page_content for doc in merged[:k]]
        except Exception as e:
            print(f"[Hybrid RAG] Retrieval error: {e}")
            return []

    def answer(self, question: str) -> str:
        contexts = self.retrieve(question)
        context_str = "\n---\n".join(contexts)
        
        prompt = (
            f"You are a financial analyst. Answer the user question based on the provided context.\n\n"
            f"Context:\n{context_str}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Error executing hybrid RAG: {e}"

if __name__ == "__main__":
    rag = HybridRAG()
    ans = rag.answer("Mã chứng khoán của Vinamilk là gì?")
    print(ans)
