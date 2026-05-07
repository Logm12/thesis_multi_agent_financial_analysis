import os
from langchain_openai import ChatOpenAI
from langchain_experimental.utilities import PythonREPL
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from agents.state import AgentState
from config import OLLAMA_BASE_URL, CODER_MODEL

# Cấu hình Ollama Local LLM từ config
llm = ChatOpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key="ollama",
    model=CODER_MODEL,
    temperature=0
)

CODER_PROMPT = """Bạn là một chuyên gia lập trình Python phân tích tài chính.
Sử dụng thư viện pandas để xử lý dataframe. Chú ý các cột dữ liệu tài chính thường có tên tiếng Việt có dấu (VD: 'Lợi nhuận sau thuế', 'Doanh thu thuần'). Tự động strip() khoảng trắng và handle các giá trị NaN trước khi tính toán. Chỉ in ra code Python, không giải thích.

Yêu cầu: {question}
Dữ liệu Context: {context}

Quy tắc:
1. Chỉ trả về mã Python, không giải thích dài dòng.
2. Mã phải tự chứa các biến cần thiết từ context.
3. Sử dụng thư viện matplotlib nếu cần vẽ biểu đồ. QUAN TRỌNG: Lưu file biểu đồ tại đường dẫn chính xác này: {chart_path}
4. Nếu có lỗi từ lần chạy trước, hãy sửa nó: {last_error}

Kết quả của script phải được in ra bằng lệnh print()."""


def coder_node(state: AgentState, config: RunnableConfig) -> dict:
    """Node sinh code và thực thi trong sandbox REPL."""
    error_count = state.get("error_count", 0)
    question = state["question"]
    # Lấy context từ tin nhắn cuối (giả sử trước đó đã retrieve hoặc có context sẵn)
    context = state["messages"][-1].content if state["messages"] else ""
    last_error = state.get("execution_result", "") if error_count > 0 else "None"

    # Lấy session_tmp_dir từ config (để an toàn cho đa người dùng)
    configurable = config.get("configurable", {})
    session_tmp_dir = configurable.get("session_tmp_dir", "tmp")
    chart_path = os.path.join(session_tmp_dir, "chart.png")

    # 1. Sinh Code
    prompt = ChatPromptTemplate.from_messages([("system", CODER_PROMPT)])
    chain = prompt | llm
    
    response = chain.invoke({
        "question": question,
        "context": context,
        "last_error": last_error,
        "chart_path": chart_path.replace("\\", "/") # Dùng forward slash cho Python script
    })
    
    code = response.content.strip()
    # Loại bỏ markdown code blocks nếu có
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0].strip()
    elif "```" in code:
        code = code.split("```")[1].split("```")[0].strip()

    print(f"[Coder] Attempt {error_count + 1}: Executing generated code...")
    
    # 2. Thực thi Sandbox
    repl = PythonREPL()
    try:
        result = repl.run(code)
        
        # Kiểm tra xem kết quả có chứa lỗi không (REPL trả về error dưới dạng string)
        if "Traceback" in result or "Error:" in result or "Exception:" in result:
            print("[Coder] Execution failed with error in output.")
            return {
                "current_code": code,
                "execution_result": result,
                "error_count": error_count + 1,
                "steps": [f"🔄 Coder đã thử chạy mã lần {error_count + 1} nhưng gặp lỗi: {result[:50]}..."]
            }

        print("[Coder] Execution Success.")
        return {
            "current_code": code,
            "execution_result": result,
            "messages": [AIMessage(content=f"Kết quả tính toán:\n{result}")],
            "error_count": error_count,
            "steps": ["🖥️ Coder đã viết và thực thi mã thành công."]
        }
    except Exception as e:
        print(f"[Coder] Runtime Error: {str(e)}")
        return {
            "current_code": code,
            "execution_result": str(e),
            "error_count": error_count + 1,
            "steps": [f"⚠️ Coder gặp lỗi runtime: {str(e)}"]
        }
