import os
import sys
from pathlib import Path

# Add backend to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from core.config import CHROMA_PATH, EMBEDDING_MODEL, SYNTHESIZER_MODEL
from core.nim_client import get_nim_llm

class TraditionalRAG:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        self.db = Chroma(persist_directory=CHROMA_PATH, embedding_function=self.embeddings)
        self.llm = get_nim_llm(model_name=SYNTHESIZER_MODEL, temperature=0.0)

    def retrieve(self, question: str, k: int = 3):
        try:
            docs = self.db.similarity_search(question, k=k)
            return [doc.page_content for doc in docs]
        except Exception as e:
            print(f"[Traditional RAG] Retrieval error: {e}")
            return []

    def answer(self, question: str) -> str:
        contexts = self.retrieve(question)
        context_str = "\n---\n".join(contexts)
        
        prompt = (
            f"You are a financial analyst. Answer the user question based ONLY on the provided context.\n\n"
            f"Context:\n{context_str}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Error executing traditional RAG: {e}"

if __name__ == "__main__":
    rag = TraditionalRAG()
    ans = rag.answer("Mã chứng khoán của Vinamilk là gì?")
    print(ans)
