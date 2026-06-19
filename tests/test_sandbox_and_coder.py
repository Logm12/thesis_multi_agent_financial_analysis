import os
import pytest
from backend.tools.sandbox import SafePythonREPL
from backend.agents.coder import load_finance_dict, CODER_PROMPT
from backend.agents.graph import check_retry
from backend.agents.state import AgentState

def test_sandbox_timeout():
    """
    Test 1: Sandbox timeout/SIGKILL (Windows + Linux compatibility)
    Ensure that a busy-loop or infinite execution gets terminated within the timeout limit.
    """
    repl = SafePythonREPL()
    infinite_loop_code = "while True:\n    pass"
    
    # Run with 1.5 seconds timeout
    result = repl.execute(infinite_loop_code, timeout=1.5)
    
    assert result["success"] is False
    assert "TimeoutError" in result["error"] or "timed out" in result["stderr"]
    print("Test 1 (Sandbox Timeout) passed successfully.")

def test_coder_prompt_formulas_and_fewshots():
    """
    Test 2: Coder Agent prompt template loading of finance_dict and few-shots
    Verify that load_finance_dict runs without exceptions and returns non-empty JSON,
    and that CODER_PROMPT contains the required keys and few-shot formatting.
    """
    finance_dict_str = load_finance_dict()
    assert finance_dict_str != "{}"
    assert "ROE" in finance_dict_str
    assert "ROA" in finance_dict_str
    
    # Check that CODER_PROMPT template has required formatting placeholders
    assert "{finance_dict}" in CODER_PROMPT
    assert "{question}" in CODER_PROMPT
    assert "{context}" in CODER_PROMPT
    assert "{chart_path}" in CODER_PROMPT
    assert "{last_error}" in CODER_PROMPT
    
    # Check that the few-shot examples are present in CODER_PROMPT
    assert "--- FEW-SHOT EXAMPLES ---" in CODER_PROMPT
    assert "Example 1: Calculate ROE using 3-stage column normalization" in CODER_PROMPT
    print("Test 2 (Coder Formulas & Few-shots validation) passed successfully.")

def test_langgraph_self_correction_loop():
    """
    Test 3: LangGraph self-correction routing logic (check_retry)
    Verify that check_retry correctly decides whether to retry execution or move to synthesis.
    """
    # Case A: Successful run without errors -> synthesize
    state_ok: AgentState = {
        "messages": [],
        "intent": "code",
        "question": "Tính ROE",
        "error_count": 0,
        "current_code": "print('ROE: 0.12')",
        "execution_result": "ROE: 0.12",
        "steps": [],
        "final_answer": None,
        "chart_path": None,
        "source_filter": None
    }
    action_ok = check_retry(state_ok)
    assert action_ok == "synthesize"
    
    # Case B: Execution result has a Traceback/Error -> retry
    state_err: AgentState = {
        "messages": [],
        "intent": "code",
        "question": "Tính ROE",
        "error_count": 1,
        "current_code": "1 / 0",
        "execution_result": "Traceback (most recent call last):\nZeroDivisionError: division by zero",
        "steps": [],
        "final_answer": None,
        "chart_path": None,
        "source_filter": None
    }
    action_err = check_retry(state_err)
    assert action_err == "retry"
    
    # Case C: Execution result has an Error but error_count >= 5 -> synthesize (gives up)
    state_give_up: AgentState = {
        "messages": [],
        "intent": "code",
        "question": "Tính ROE",
        "error_count": 5,
        "current_code": "1 / 0",
        "execution_result": "ZeroDivisionError: division by zero",
        "steps": [],
        "final_answer": None,
        "chart_path": None,
        "source_filter": None
    }
    action_give_up = check_retry(state_give_up)
    assert action_give_up == "synthesize"
    
    print("Test 3 (LangGraph self-correction routing) passed successfully.")
