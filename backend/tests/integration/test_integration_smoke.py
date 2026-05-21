from agents.graph import get_graph_app

def test_langgraph_initialization():
    """Kiểm thử việc khởi tạo luồng LangGraph Workflow hoàn chỉnh."""
    app = get_graph_app()
    assert app is not None
    
    # Kiểm tra xem có cấu hình checkpointer không
    assert hasattr(app, "get_state") or hasattr(app, "nodes")
    
    # In ra danh sách các nodes trong graph để kiểm chứng
    nodes = app.nodes if hasattr(app, "nodes") else {}
    print(f"\n[Integration Test] LangGraph Nodes: {list(nodes.keys())}")
    
    # Kiểm chứng các nodes lõi hiện diện đúng
    assert "router" in nodes
    assert "retriever" in nodes
    assert "coder" in nodes
    assert "synthesizer" in nodes
