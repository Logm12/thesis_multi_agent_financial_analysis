from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.messages import AIMessage
from .state import AgentState
from core.config import CHROMA_PATH, EMBEDDING_MODEL, EMBEDDING_DIM
from dotenv import load_dotenv

load_dotenv()

def retrieve_node(state: AgentState) -> dict:
    """Node truy xuất dữ liệu từ ChromaDB với cơ chế Auto-Fallback."""
    question = state["question"]
    
    # Khởi tạo VectorDB với OpenAI Embeddings từ config
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, dimensions=EMBEDDING_DIM)
    vector_db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name="financial_docs"
    )
    
    # Filter logic if source_filter exists
    search_filter = None
    if "source_filter" in state and state["source_filter"]:
        search_filter = {"source": state["source_filter"]}
        
    # Truy xuất Top 3 chunks để đảm bảo đủ dữ liệu tài chính cho so sánh
    results = vector_db.similarity_search(question, k=3, filter=search_filter)
    
    # Định dạng context kèm theo [Trang X, Nguồn Y] để phục vụ trích dẫn
    context_parts = []
    
    # Build a lookup map: {file_id: friendly_name} from document store
    import os
    source_name_map: dict = {}
    try:
        from api.document_store import get_all_documents
        for doc_meta in get_all_documents():
            # processed source key is "{file_id}.json"
            source_name_map[f"{doc_meta['id']}.json"] = doc_meta["name"]
    except Exception:
        pass
    
    for doc in results:
        page = doc.metadata.get("page", "N/A")
        source = doc.metadata.get("source", "N/A")
        source_basename = os.path.basename(str(source))
        # Map UUID-based source to friendly file name
        source_clean = source_name_map.get(source_basename, source_basename)
        context_parts.append(f"**[Trang {page}, Nguồn {source_clean}]**\n{doc.page_content}")
        
    context = "\n\n".join(context_parts)
    
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
