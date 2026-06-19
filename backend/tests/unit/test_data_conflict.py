from unittest.mock import patch
from langchain_core.messages import AIMessage, HumanMessage
from backend.agents.synthesizer import synthesizer_node

def test_synthesizer_data_conflict_prompt_and_flow():
    """
    Scenario: Verify that the Synthesizer node successfully incorporates the Data Conflict 
    resolution rules in its prompt and handles the data flow correctly.
    """
    # 1. Create mock AgentState with conflicted messages
    state = {
        "question": "Doanh thu của VNM năm nay là bao nhiêu?",
        "error_count": 0,
        "messages": [
            HumanMessage(content="Doanh thu của VNM năm nay là bao nhiêu?"),
            AIMessage(content=(
                "**[Trang 3, BCTC_VNM.pdf]**\n"
                "Thông tin dạng văn bản (Text): Doanh thu là 100\n"
                "Thông tin dạng bảng biểu (Table): \n"
                "| Chỉ tiêu | Giá trị |\n"
                "| Doanh thu | 100.5 |"
            ))
        ],
        "execution_result": "",
        "chart_path": ""
    }

    # 2. Mock ChatOpenAI's invoke method to return a standard resolved message
    mock_ai_message = AIMessage(
        content="Doanh thu thực tế là 100.5 tỷ (được trích xuất từ bảng biểu, ưu tiên hơn so với 100 tỷ trong phần văn bản báo cáo)."
    )
    
    # Patch the invoke method of ChatOpenAI
    with patch("backend.agents.synthesizer.ChatOpenAI.invoke") as mock_invoke:
        mock_invoke.return_value = mock_ai_message
        
        # 3. Invoke synthesizer_node
        result = synthesizer_node(state)
        
        # Assertions on return value
        assert "final_answer" in result
        assert "100.5" in result["final_answer"]
        assert "steps" in result
        
        # Assertions on prompt construction and parameters
        assert mock_invoke.called
        call_args = mock_invoke.call_args[0][0]
        
        # Ensure the prompt contains system instructions and the conflict rules
        prompt_text = str(call_args)
        assert "DATA CONFLICT RESOLUTION" in prompt_text
        assert "tabular structure" in prompt_text
        assert "100.5" in prompt_text
