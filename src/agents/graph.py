from langgraph.graph import StateGraph, START, END
from agents.state import AgentState
from agents.router import router_node
from agents.retriever import retrieve_node
from agents.coder import coder_node
from agents.synthesizer import synthesizer_node
from data_processing.pdf_parser import FastPDFParser
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from config import CHROMA_PATH, EMBEDDING_MODEL, EMBEDDING_DIM, POSTGRES_URL
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter

def route_intent(state: AgentState):
    """Điều hướng dựa trên intent."""
    return state["intent"]

def check_retry(state: AgentState):
    """Kiểm tra xem có cần retry code hay không."""
    # Nếu có kết quả thực thi và không chứa lỗi thì đi tiếp tới synthesizer
    res = state.get("execution_result", "")
    if res and not any(x in res for x in ["Traceback", "Error:", "Exception:"]):
        return "synthesize"
    
    # Nếu lỗi quá 3 lần thì dừng lại đi tới synthesizer để báo lỗi
    if state.get("error_count", 0) >= 3:
        return "synthesize"
    
    return "retry"

def build_graph():
    """Dựng luồng LangGraph Workflow hoàn chỉnh (TIP-004)."""
    workflow = StateGraph(AgentState)

    # 1. Thêm các Node
    workflow.add_node("router", router_node)
    workflow.add_node("retriever", retrieve_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("synthesizer", synthesizer_node)

    # 2. Thiết lập Edges
    workflow.add_edge(START, "router")

    # 3. Router -> Retriever (cả hai luồng đều cần context)
    workflow.add_conditional_edges(
        "router",
        route_intent,
        {
            "retrieve": "retriever",
            "code": "retriever",
        }
    )
    
    # 4. Retriever -> Coder hoặc Synthesizer
    def after_retrieve(state: AgentState):
        if state["intent"] == "code":
            return "go_to_coder"
        return "synthesize"

    workflow.add_conditional_edges(
        "retriever",
        after_retrieve,
        {
            "go_to_coder": "coder",
            "synthesize": "synthesizer"
        }
    )

    # 5. Coder -> Synthesizer hoặc Retry
    workflow.add_conditional_edges(
        "coder",
        check_retry,
        {
            "retry": "coder",
            "synthesize": "synthesizer"
        }
    )

    # 6. Synthesizer -> END
    workflow.add_edge("synthesizer", END)

    # 7. Persistence: Sử dụng MemorySaver cho TIP-001 (Postgres refactor in TIP-004)
    from langgraph.checkpoint.memory import MemorySaver
    checkpointer = MemorySaver()
    print("[Graph] Using MemorySaver for current session.")
    
    # Biên dịch với checkpointer
    app = workflow.compile(checkpointer=checkpointer)
    return app

def ingest_pdf(file_path: str):
    """Utility function để nạp PDF mới vào VectorDB."""
    print(f"[*] Đang nạp file: {file_path}")
    parser = FastPDFParser()
    content = parser.parse(file_path)
    
    # Chuyển đổi content thành chunks (Markdown split)
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    chunks = markdown_splitter.split_text(content)
    
    # Lưu vào ChromaDB
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, dimensions=EMBEDDING_DIM)
    vector_db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
    vector_db.add_documents(chunks)
    print(f"[+] Đã nạp thành công {len(chunks)} chunks vào VectorDB.")

# Lazy initialization for the LangGraph app
_graph_app = None

def get_graph_app():
    """Getter cho LangGraph app với cơ chế lazy-init."""
    global _graph_app
    if _graph_app is None:
        print("[Graph] Initializing LangGraph application...")
        _graph_app = build_graph()
    return _graph_app
