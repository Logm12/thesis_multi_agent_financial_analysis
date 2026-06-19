import pytest
from backend.agents.state import append_messages
from backend.agents.graph import check_retry
from backend.agents.router import router_node, RouteQuery
from langchain_core.messages import HumanMessage
from unittest.mock import MagicMock

def test_sliding_window_reducer():
    tracebacks = ["tb1", "tb2", "tb3"]
    # Appending a new one should discard the first one and keep max 3
    res = append_messages(tracebacks, "tb4")
    assert len(res) == 3
    assert res == ["tb2", "tb3", "tb4"]
    
    # Appending when empty
    res2 = append_messages([], "tb_only")
    assert res2 == ["tb_only"]

def test_check_retry_logic():
    # If no traceback or error and execution_result exists -> synthesize
    state1 = {
        "execution_result": "Success!",
        "error_count": 0
    }
    assert check_retry(state1) == "synthesize"

    # If error in execution and error_count < 5 -> retry
    state2 = {
        "execution_result": "Traceback (most recent call last): ...",
        "error_count": 3
    }
    assert check_retry(state2) == "retry"

    # If error in execution and error_count >= 5 -> synthesize
    state3 = {
        "execution_result": "Traceback (most recent call last): ...",
        "error_count": 5
    }
    assert check_retry(state3) == "synthesize"
