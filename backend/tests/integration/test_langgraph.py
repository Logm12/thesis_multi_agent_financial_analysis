import os
from unittest.mock import patch

# Ensure OPENAI_API_KEY is present so langchain doesn't complain
os.environ["OPENAI_API_KEY"] = "mock-key"

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.documents import Document
from langchain_core.runnables import RunnableBinding
from langchain_openai import ChatOpenAI

from backend.agents.graph import get_graph_app
from backend.agents.router import RouteQuery

def test_router_out_of_scope_interception():
    """
    REQ-006: Router Agent nhận diện prompt hack/hỏi ngoài lề và chặn ngay từ đầu,
    không gọi các Agent khác (Retriever, Coder).
    """
    app = get_graph_app()
    
    # Mock Router LLM to classify as out_of_scope
    mock_route = RouteQuery(
        intent="out_of_scope",
        reasoning="Yêu cầu hỏi cách hack Facebook, không liên quan đến tài chính doanh nghiệp."
    )
    
    # Trace the execution path using class-level patch of RunnableBinding.invoke
    with patch.object(RunnableBinding, "invoke", return_value=mock_route) as mock_router_invoke:
        config = {"configurable": {"thread_id": "test_thread_out_of_scope"}}
        initial_state = {
            "messages": [HumanMessage(content="Làm sao để hack facebook?")]
        }
        
        result = app.invoke(initial_state, config=config)
        
        # Verify Router LLM was called
        assert mock_router_invoke.called
        
        # Verify final answer is a polite refusal
        assert "final_answer" in result
        assert "Xin lỗi" in result["final_answer"]
        assert "phân tích báo cáo tài chính" in result["final_answer"]
        
        # Verify executed steps in the state
        steps = result.get("steps", [])
        print("Executed steps:", steps)
        
        # Verify retriever or coder node steps are NOT in steps
        assert any("Router" in s for s in steps)
        assert any("Synthesizer" in s for s in steps)
        assert not any("Retriever" in s for s in steps)
        assert not any("Coder" in s for s in steps)

def test_recursive_loop_termination_at_5():
    """
    REQ-003: Dừng vòng lặp đệ quy quá giới hạn max_retries = 5 của LangGraph
    khi Coder Agent liên tục sinh mã lỗi.
    """
    app = get_graph_app()
    
    # 1. Mock Router to return "code" intent
    mock_route = RouteQuery(
        intent="code",
        reasoning="Yêu cầu tính toán tăng trưởng doanh thu."
    )
    
    # 2. Mock Retriever search to return some context documents
    mock_docs = [
        Document(
            page_content="Doanh thu 2023: 100 tỷ\nDoanh thu 2024: 120 tỷ",
            metadata={"page": "5", "source": "BCTC_VNM.pdf"}
        )
    ]
    
    # 3. Mock Coder LLM call to return a python block
    mock_coder_response = AIMessage(
        content="```python\n# This code will fail execution\nprint(1/0)\n```"
    )
    
    # 4. Mock SafePythonREPL.execute to return a failed run with an error
    mock_repl_result = {
        "success": False,
        "error": "ZeroDivisionError: division by zero",
        "stderr": "ZeroDivisionError: division by zero",
        "stdout": "",
        "plot": None
    }
    
    # 5. Mock Synthesizer response
    mock_synth_response = AIMessage(
        content="Xin lỗi, tôi đã cố gắng thực thi mã phân tích tài chính 5 lần nhưng đều gặp lỗi. Dữ liệu thô cho thấy doanh thu tăng từ 100 tỷ lên 120 tỷ."
    )
    
    # Side-effect function to route the ChatOpenAI.invoke to Coder or Synthesizer mock
    def mock_llm_invoke(input_data, *args, **kwargs):
        prompt_str = str(input_data)
        if "chuyên gia lập trình" in prompt_str:
            return mock_coder_response
        elif "chuyên gia phân tích tài chính" in prompt_str:
            return mock_synth_response
        return AIMessage(content="Mock response")
    
    # Patch all required calls using safe class-level patching
    with patch.object(RunnableBinding, "invoke", return_value=mock_route), \
         patch.object(ChatOpenAI, "invoke", side_effect=mock_llm_invoke) as mock_openai_invoke, \
         patch("backend.agents.retriever.Chroma.similarity_search", return_value=mock_docs), \
         patch("backend.agents.retriever.OpenAIEmbeddings.__init__", return_value=None), \
         patch("backend.agents.coder.SafePythonREPL.execute", return_value=mock_repl_result) as mock_repl_execute:
         
        config = {"configurable": {"thread_id": "test_thread_recursion", "session_tmp_dir": "tmp"}}
        initial_state = {
            "messages": [HumanMessage(content="Tính tăng trưởng doanh thu VNM 2023-2024")]
        }
        
        result = app.invoke(initial_state, config=config)
        
        # Verify the coder node was called exactly 5 times
        assert mock_repl_execute.call_count == 5
        
        # Verify ChatOpenAI.invoke was called for both Coder and Synthesizer
        # Coder is called 5 times, Synthesizer called 1 time -> total 6 times
        assert mock_openai_invoke.call_count == 6
        
        # Verify the final state error_count is 5
        assert result.get("error_count", 0) == 5
        
        # Verify the final answer contains the warning/failure summary
        assert "final_answer" in result
        assert "Xin lỗi" in result["final_answer"]
        assert "5 lần" in result["final_answer"]
