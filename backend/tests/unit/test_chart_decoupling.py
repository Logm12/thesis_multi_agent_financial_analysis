"""Unit tests for Synthesizer Agent Chart Decoupling Protocol.

Verifies that the Synthesizer does NOT embed Base64 PNG data directly into the
`final_answer` string (which would pollute the LLM context window). Instead, it
should append a semantic reference label [CHART_01_RENDERED] when a chart is present.
The actual chart data is transmitted separately via the SSE `chart_url` payload field.
"""
import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage, HumanMessage


def _make_state(chart_path=None, execution_result=None):
    """Helper to build a minimal AgentState dict for the synthesizer."""
    return {
        "messages": [AIMessage(content="Revenue in 2023 was 500 billion VND.")],
        "question": "What is the revenue trend?",
        "intent": "code",
        "error_count": 0,
        "execution_result": execution_result or "Revenue 2023: 500B",
        "chart_path": chart_path,
        "ground_truth": None,
        "tracebacks": [],
        "steps": [],
    }


def _run_synthesizer(state, llm_response_content="Revenue grew significantly in 2023."):
    """Run synthesizer_node with a mocked LLM and a patched benchmark override."""
    from backend.agents.synthesizer import synthesizer_node

    mock_response = MagicMock()
    mock_response.content = llm_response_content

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_response

    with patch("backend.agents.synthesizer.llm") as mock_llm, \
         patch("core.benchmark_override.get_override_answer", return_value=None):
        # Build a chain that the prompt | llm pipe returns
        mock_prompt_obj = MagicMock()
        mock_prompt_obj.__or__ = MagicMock(return_value=mock_chain)
        with patch("langchain_core.prompts.ChatPromptTemplate.from_messages",
                   return_value=mock_prompt_obj):
            return synthesizer_node(state)


def test_synthesizer_does_not_embed_base64_chart():
    """Verify that final_answer does NOT contain a data:image/png Base64 URI."""
    fake_base64 = (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    state = _make_state(chart_path=fake_base64)
    result = _run_synthesizer(state)
    final_answer = result["final_answer"]

    # CRITICAL: Base64 image data must NOT be embedded in final_answer
    assert "data:image/png;base64," not in final_answer, (
        "Synthesizer must NOT embed Base64 chart data into final_answer. "
        "The chart is transmitted via the SSE chart_url payload field."
    )


def test_synthesizer_appends_chart_reference_label_when_chart_present():
    """Verify final_answer contains [CHART_01_RENDERED] label when chart_path is set."""
    state = _make_state(chart_path="data:image/png;base64,FAKEPNG==")
    result = _run_synthesizer(state, llm_response_content="Here is the revenue analysis.")
    final_answer = result["final_answer"]

    assert "[CHART_01_RENDERED]" in final_answer, (
        "When chart_path is set, Synthesizer should append [CHART_01_RENDERED] reference label."
    )


def test_synthesizer_no_chart_label_when_no_chart():
    """Verify [CHART_01_RENDERED] is NOT appended when chart_path is absent."""
    state = _make_state(chart_path=None, execution_result=None)
    result = _run_synthesizer(state, llm_response_content="Total revenue in 2023 was 500 billion VND.")
    final_answer = result["final_answer"]

    assert "[CHART_01_RENDERED]" not in final_answer, (
        "[CHART_01_RENDERED] should only appear when chart_path is set."
    )
    assert "data:image/png;base64," not in final_answer
