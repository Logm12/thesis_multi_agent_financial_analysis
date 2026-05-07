from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.messages import AIMessage
from agents.state import AgentState
from config import CHROMA_PATH, EMBEDDING_MODEL, EMBEDDING_DIM
from dotenv import load_dotenv

load_dotenv()

def retrieve_node(state: AgentState) -> dict:
    """Node truy xuất dữ liệu từ ChromaDB với cơ chế Auto-Fallback."""
    question = state["question"]
    
    # Khởi tạo VectorDB với OpenAI Embeddings từ config
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, dimensions=EMBEDDING_DIM)
    vector_db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
    
    # Truy xuất Top 4 chunks
    results = vector_db.similarity_search(question, k=4)
    
    context = "\n\n".join([doc.page_content for doc in results])
    
    # Logic Auto-Fallback: Cảnh báo nếu dữ liệu có vẻ thiếu
    # Ví dụ: Nếu người dùng hỏi "3 năm" nhưng chỉ tìm thấy dữ liệu năm 2023
    fallback_msg = ""
    years_found = set()
    import re
    years_found.update(re.findall(r"202[0-9]", context))
    
    # Giả lập kiểm tra: Nếu context quá ngắn hoặc không thấy nhiều năm
    if len(results) < 2:
        fallback_msg = "\n\n(Cảnh báo: Hệ thống chỉ tìm thấy rất ít dữ liệu liên quan đến yêu cầu này.)"
    elif "so sánh" in question.lower() and len(years_found) < 2:
        fallback_msg = f"\n\n(Cảnh báo: Chỉ tìm thấy dữ liệu liên quan đến năm {', '.join(years_found)}. Không đủ dữ liệu để so sánh đối chiếu đầy đủ.)"

    final_content = context + fallback_msg
    
    return {
        "messages": [AIMessage(content=final_content)],
        "steps": ["📚 Retriever đã tìm kiếm dữ liệu trong VectorDB."]
    }
