import pytest
from agents.router import router_node
from langchain_core.messages import HumanMessage

def test_router_retrieve_classification(mock_agent_state):
    """Kiểm tra Router phân loại đúng câu hỏi tra cứu."""
    state = mock_agent_state.copy()
    state["question"] = "Doanh thu năm 2023 của công ty là bao nhiêu?"
    state["messages"] = [HumanMessage(content=state["question"])]
    
    result = router_node(state)
    
    assert result["intent"] == "retrieve"
    assert "steps" in result
    assert "🔍 Router đã xác định ý định: retrieve" in result["steps"][0]

def test_router_code_classification(mock_agent_state):
    """Kiểm tra Router phân loại đúng câu hỏi cần tính toán/vẽ biểu đồ."""
    state = mock_agent_state.copy()
    state["question"] = "Hãy vẽ biểu đồ so sánh lợi nhuận ròng 3 năm qua."
    state["messages"] = [HumanMessage(content=state["question"])]
    
    result = router_node(state)
    
    assert result["intent"] == "code"
    assert "steps" in result
    assert "🔍 Router đã xác định ý định: code" in result["steps"][0]

def test_router_empty_message(mock_agent_state):
    """Kiểm tra Router khi không có tin nhắn (fallback về question field)."""
    state = mock_agent_state.copy()
    state["question"] = "Tổng tài sản là bao nhiêu?"
    state["messages"] = []
    
    result = router_node(state)
    assert result["intent"] == "retrieve"
