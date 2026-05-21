import os
import re
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from .state import AgentState
from core.config import ROUTER_MODEL
from backend.tools.sandbox import SafePythonREPL

# Cấu hình OpenAI LLM cho Coder (sử dụng ROUTER_MODEL = gpt-5.4-mini)
llm = ChatOpenAI(
    model=ROUTER_MODEL,
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

def load_finance_dict() -> str:
    """Đọc từ điển công thức tài chính để đưa vào prompt của Coder."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Đường dẫn tương thích: backend/tools/finance_dict.json
    dict_path = os.path.join(os.path.dirname(current_dir), "tools", "finance_dict.json")
    try:
        with open(dict_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Coder] Không thể tải từ điển công thức tài chính: {e}")
        return "{}"

CODER_PROMPT = """Bạn là một chuyên gia lập trình Python phân tích tài chính.
Sử dụng thư viện pandas để xử lý dữ liệu. Chú ý các cột dữ liệu tài chính thường có tên tiếng Việt có dấu. 

QUAN TRỌNG: Bạn BẮT BUỘC phải tuân thủ chính xác các công thức tài chính từ từ điển sau, TUYỆT ĐỐI không được tự ý chế công thức:
{finance_dict}

QUAN TRỌNG ĐẶC BIỆT VỀ LÀM SẠCH DỮ LIỆU:
1. Dữ liệu Việt Nam thường dùng dấu chấm làm phân cách hàng ngàn (VD: 1.234.567). Khi viết vào code Python, bạn PHẢI chuyển chúng thành số chuẩn (VD: 1234567).
2. BẮT BUỘC ép kiểu dữ liệu về dạng số (int/float) TRƯỚC KHI tính toán.
3. Khi đọc chuỗi số chứa ký tự không xác định, bạn PHẢI dùng: `pd.to_numeric(df['cột'].astype(str).str.replace(r'[^\\d]', '', regex=True), errors='coerce')`
4. Toàn bộ logic tính toán của bạn PHẢI bọc trong khối `try...except Exception as e:` để nếu fail sẽ `print(f"[Execution Error] {{e}}")` thay vì crash engine.

BẮT BUỘC: Bọc mã Python duy nhất của bạn bên trong một block markdown dạng ```python ... ```.
Không giải thích ngoài mã nguồn, không có lời nói mở đầu hoặc kết thúc.

Yêu cầu: {question}
Dữ liệu Context: {context}

Quy tắc:
1. CHỈ trả về một block mã Python ```python ... ```, TUYỆT ĐỐI không giải thích dài dòng hay bình luận tiếng Việt ngoài block code.
2. Mã phải tự chứa các biến cần thiết từ context.
3. Sử dụng thư viện matplotlib nếu cần vẽ biểu đồ. QUAN TRỌNG: Lưu file biểu đồ tại đường dẫn chính xác này: {chart_path}
4. Nếu có lỗi từ lần chạy trước, hãy sửa nó: {last_error}

Kết quả tính toán cuối cùng của script phải được in ra màn hình bằng câu lệnh print()."""

def pre_sanitize_context(text: str) -> str:
    """
    Làm sạch các số dạng Việt Nam (VD: 1.234.567 -> 1234567) trong context 
    để giảm thiểu lỗi cú pháp cho LLM.
    """
    if not text:
        return text
    # 1. Khớp nhóm 3 chữ số cách nhau bởi dấu chấm (Hàng triệu): X.XXX.XXX
    text = re.sub(r'(\d{1,3})\.(\d{3})\.(\d{3})', lambda m: m.group().replace('.', ''), text)
    # 2. Khớp dấu chấm hàng nghìn đơn giản: X.XXX
    text = re.sub(r'\b(\d{1,3})\.(\d{3})\b', lambda m: m.group().replace('.', ''), text)
    return text

def coder_node(state: AgentState, config: RunnableConfig) -> dict:
    """Node sinh code và thực thi trong sandbox REPL bảo mật."""
    error_count = state.get("error_count", 0)
    question = state["question"]
    raw_context = state["messages"][-1].content if state["messages"] else ""
    context = pre_sanitize_context(raw_context)
    last_error = state.get("execution_result", "") if error_count > 0 else "None"

    # Lấy session_tmp_dir từ config (đảm bảo an toàn đa người dùng)
    configurable = config.get("configurable", {})
    session_tmp_dir = configurable.get("session_tmp_dir", "tmp")
    chart_path = os.path.join(session_tmp_dir, "chart.png")

    # Load từ điển công thức tài chính
    finance_dict_str = load_finance_dict()

    # 1. Sinh Code
    prompt = ChatPromptTemplate.from_messages([("system", CODER_PROMPT)])
    chain = prompt | llm
    
    response = chain.invoke({
        "question": question,
        "context": context,
        "finance_dict": finance_dict_str,
        "last_error": last_error,
        "chart_path": chart_path.replace("\\", "/") # Dùng forward slash cho script Python
    })
    
    code = response.content.strip()
    code_match = re.search(r'```python\s*(.*?)\s*```', code, re.DOTALL)
    if not code_match:
        code_match = re.search(r'```\s*(.*?)\s*```', code, re.DOTALL)
    
    if code_match:
        code = code_match.group(1).strip()
    else:
        # Hậu xử lý nếu không có block markdown
        lines = code.split('\n')
        cleaned_lines = []
        in_code = False
        for line in lines:
            if any(kw in line for kw in ['import ', 'print(', 'df =', 'def ', '= ']):
                in_code = True
            if in_code:
                cleaned_lines.append(line)
        if cleaned_lines:
            code = '\n'.join(cleaned_lines).strip()

    print(f"[Coder] Attempt {error_count + 1}: Executing generated code...")
    
    # 2. Thực thi qua Sandbox bảo mật
    repl = SafePythonREPL()
    try:
        exec_res = repl.execute(code)
        
        if not exec_res["success"]:
            print(f"[Coder] Execution failed with error: {exec_res['error']}")
            return {
                "current_code": code,
                "execution_result": exec_res["error"] or exec_res["stderr"],
                "error_count": error_count + 1,
                "steps": [f"🔄 Coder đã thử chạy mã lần {error_count + 1} nhưng gặp lỗi: {exec_res['error'][:50]}..."]
            }

        print("[Coder] Execution Success.")
        
        # Lấy kết quả in ra màn hình
        result = exec_res["stdout"]
        # Lấy ảnh biểu đồ dạng base64 nếu có sinh ra
        plot_b64 = exec_res["plot"]
        
        chart_val = None
        if plot_b64:
            chart_val = f"data:image/png;base64,{plot_b64}"
        elif os.path.exists(chart_path):
            chart_val = chart_path

        return {
            "current_code": code,
            "execution_result": result,
            "messages": [AIMessage(content=f"Kết quả tính toán:\n{result}")],
            "error_count": error_count,
            "chart_path": chart_val,
            "steps": ["🖥️ Coder đã viết và thực thi mã thành công."]
        }
    except Exception as e:
        print(f"[Coder] Runtime Exception: {str(e)}")
        return {
            "current_code": code,
            "execution_result": str(e),
            "error_count": error_count + 1,
            "steps": [f"⚠️ Coder gặp lỗi runtime: {str(e)}"]
        }
