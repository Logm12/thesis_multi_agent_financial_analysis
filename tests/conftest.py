import pytest
import os
import sys

# Thêm thư mục src vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

@pytest.fixture
def mock_agent_state():
    """Fixture cung cấp AgentState mẫu cho testing."""
    return {
        "messages": [],
        "question": "",
        "intent": "retrieve",
        "error_count": 0,
        "current_code": None,
        "execution_result": None,
        "steps": [],
        "final_answer": None
    }
