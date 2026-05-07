import pytest
from unittest.mock import MagicMock, patch
from agents.coder import coder_node
from langchain_core.messages import AIMessage, HumanMessage

@patch("agents.coder.llm")
@patch("agents.coder.PythonREPL")
def test_coder_node_success(mock_repl_class, mock_llm, mock_agent_state):
    """Kiểm tra Coder node khi LLM sinh mã thành công."""
    # Giả lập LLM
    mock_response = MagicMock()
    mock_response.content = "```python\nprint('Hello World')\n```"
    mock_llm.invoke.return_value = mock_response
    
    # Giả lập REPL
    mock_repl = MagicMock()
    mock_repl.run.return_value = "Hello World"
    mock_repl_class.return_value = mock_repl
    
    state = mock_agent_state.copy()
    state["question"] = "In ra Hello World"
    state["intent"] = "code"
    state["messages"] = [HumanMessage(content="Dữ liệu mẫu")]
    
    config = {"configurable": {"session_tmp_dir": "tmp"}}
    
    result = coder_node(state, config)
    
    assert "Hello World" in result["execution_result"]
    assert result["error_count"] == 0
    assert "🖥️ Coder đã viết và thực thi mã thành công." in result["steps"][0]

@patch("agents.coder.llm")
@patch("agents.coder.PythonREPL")
def test_coder_node_retry_on_error(mock_repl_class, mock_llm, mock_agent_state):
    """Kiểm tra Coder node khi mã thực thi lỗi (tăng error_count)."""
    # Giả lập LLM
    mock_response = MagicMock()
    mock_response.content = "```python\nprint(undefined_variable)\n```"
    mock_llm.invoke.return_value = mock_response
    
    # Giả lập REPL trả về lỗi
    mock_repl = MagicMock()
    mock_repl.run.return_value = "Traceback (most recent call last):\nNameError: name 'undefined_variable' is not defined"
    mock_repl_class.return_value = mock_repl
    
    state = mock_agent_state.copy()
    state["error_count"] = 0
    
    config = {"configurable": {"session_tmp_dir": "tmp"}}
    
    result = coder_node(state, config)
    
    assert result["error_count"] == 1
    assert "🔄 Coder đã thử chạy mã lần 1 nhưng gặp lỗi" in result["steps"][0]
