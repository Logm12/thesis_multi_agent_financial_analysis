import pytest
from unittest.mock import MagicMock, patch
from backend.agents.state import append_messages
from backend.api.server import extract_chart_data
from backend.agents.router import router_node
from langchain_core.messages import HumanMessage

def test_sliding_window_reducer():
    """Verify that append_messages keeps at most the last 3 traceback errors."""
    # Test case 1: Initial empty or None
    assert append_messages(None, ["error1"]) == ["error1"]
    assert append_messages([], ["error1"]) == ["error1"]

    # Test case 2: Less than 3 items
    state = ["error1", "error2"]
    assert append_messages(state, ["error3"]) == ["error1", "error2", "error3"]

    # Test case 3: Reaches limit (should keep last 3)
    state = ["error1", "error2", "error3"]
    assert append_messages(state, ["error4"]) == ["error2", "error3", "error4"]

    # Test case 4: Exceeds limit by multiple items (should keep last 3)
    state = ["error1", "error2"]
    assert append_messages(state, ["error3", "error4", "error5"]) == ["error3", "error4", "error5"]

def test_extract_chart_data_tagged():
    """Verify extract_chart_data successfully parses JSON from <json_data> tags."""
    raw_stdout = "Calculations complete.\n<json_data>[{\"name\": \"2023\", \"Revenue\": 120.0}, {\"name\": \"2024\", \"Revenue\": 150.0}]</json_data>\nOutput text."
    data = extract_chart_data(raw_stdout)
    assert data is not None
    assert len(data) == 2
    assert data[0]["name"] == "2023"
    assert data[1]["Revenue"] == 150.0

def test_extract_chart_data_raw_fallback():
    """Verify extract_chart_data falls back to raw JSON list structure in stdout."""
    raw_stdout = "Logs:\n[{\"name\": \"2023\", \"Val\": 10}, {\"name\": \"2024\", \"Val\": 20}]\nDone."
    data = extract_chart_data(raw_stdout)
    assert data is not None
    assert len(data) == 2
    assert data[0]["name"] == "2023"
    assert data[1]["Val"] == 20

def test_extract_chart_data_invalid():
    """Verify extract_chart_data returns None for invalid or missing JSON."""
    assert extract_chart_data("No JSON here") is None
    assert extract_chart_data("<json_data>invalid json</json_data>") is None

@patch("backend.agents.router.structured_llm")
@patch("core.database.get_db_connection")
def test_router_node_telemetry_logging(mock_get_db, mock_llm):
    """Verify router_node classifies intent and invokes database logging."""
    # Mock LLM route intent classification result
    mock_route = MagicMock()
    mock_route.intent = "code"
    mock_route.reasoning = "Quantitative analytical query."
    mock_llm.invoke.return_value = mock_route
    mock_llm.return_value = mock_route


    # Mock DB Connection and Cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    # Setup initial state
    state = {
        "messages": [HumanMessage(content="Calculate growth rate of FPT")],
        "ground_truth": "code"
    }

    # Execute router node
    res = router_node(state)

    assert res["intent"] == "code"
    
    # Assert DB insert command executed
    mock_cursor.execute.assert_called_once()
    args, kwargs = mock_cursor.execute.call_args
    sql_str = args[0]
    params = args[1]
    assert "INSERT INTO intent_logs" in sql_str
    assert params[0] == "Calculate growth rate of FPT"
    assert params[1] == "code"
    assert params[2] == "code"
