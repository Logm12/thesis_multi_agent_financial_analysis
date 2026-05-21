import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from .state import AgentState
from core.config import SYNTHESIZER_MODEL
from dotenv import load_dotenv

load_dotenv()

# Khởi tạo model từ config
llm = ChatOpenAI(
    model=SYNTHESIZER_MODEL,
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
)

SYNTHESIZER_PROMPT = """Bạn là một chuyên gia phân tích tài chính cao cấp. Hãy tổng hợp dữ liệu dưới đây để trả lời câu hỏi của người dùng.

Dữ liệu đầu vào:
{data}

Yêu cầu câu trả lời:
1. TRỰC DIỆN, NGẮN GỌN, dùng văn phong chuyên nghiệp, lịch sự.
2. TUYỆT ĐỐI không bịa đặt số liệu (Zero Hallucination). Nếu phát hiện thiếu thông tin cần thiết, hãy ghi chú rõ.
3. BẮT BUỘC: Mọi câu trả lời liên quan tới số liệu hoặc thông tin từ văn bản đều phải có TRÍCH DẪN IN ĐẬM nguồn trang ngay sau câu/mệnh đề đó.
   - Định dạng bắt buộc: **[Trang X, Tên-File.pdf]** (Ví dụ: **[Trang 15, BCTC_FPT.pdf]**).
   - Hãy tìm thông tin này từ các phần "**[Trang X, Nguồn Y]**" trong dữ liệu đầu vào — dùng phần "Nguồn Y" làm tên file.
4. ĐỊNH DẠNG MARKDOWN BẮT BUỘC:
   - Nếu người dùng yêu cầu "bảng", "so sánh", hoặc "trình bày dạng bảng": BẮT BUỘC dùng Markdown table với cú pháp đầy đủ:
     | Chỉ tiêu | Kỳ 1 | Kỳ 2 | Chênh lệch | % Thay đổi |
     |---|---:|---:|---:|---:|
     KHÔNG viết dạng văn xuôi thuần túy khi dữ liệu là dạng bảng số.
   - Sử dụng ## heading cho mỗi mục chính (## Tổng quan, ## Phân tích, ## Kết luận).
   - Sử dụng **bold** cho các chỉ tiêu tài chính và số liệu quan trọng.
   - Sử dụng bullet list (- item) cho các nhận xét/kết luận ngắn gọn.
5. Nếu kết quả thực thi mã có vẽ biểu đồ, hãy thông báo cho người dùng xem biểu đồ đính kèm phía dưới.
6. Nếu đây là trường hợp lỗi kỹ thuật (error_count >= 3), hãy đưa ra lời xin lỗi thân thiện và tóm tắt thông tin thô thu thập được kèm trích dẫn nguồn trang rõ ràng.
7. QUY TẮC ĐẶC BIỆT VỀ XUNG ĐỘT SỐ LIỆU (Data Conflict Resolution): Nếu phát hiện mâu thuẫn hay lệch số liệu giữa thông tin dạng Văn bản (Text) và Bảng biểu (Table/OCR Table) trong dữ liệu đầu vào, bạn PHẢI ưu tiên sử dụng số liệu từ Bảng biểu (Table) đồng thời ghi chú rõ hoặc giải trình rõ ràng sự chênh lệch này trong câu trả lời.

Hãy viết câu trả lời cuối cùng:"""

def synthesizer_node(state: AgentState) -> dict:
    """Node tổng hợp câu trả lời cuối cùng."""
    question = state["question"]
    error_count = state.get("error_count", 0)
    intent = state.get("intent")

    # Xử lý trường hợp câu hỏi ngoài phạm vi (out_of_scope)
    if intent == "out_of_scope":
        return {
            "final_answer": "Xin lỗi, tôi chỉ có thể hỗ trợ các câu hỏi liên quan đến phân tích báo cáo tài chính của các doanh nghiệp. Vui lòng đặt câu hỏi phù hợp.",
            "steps": ["✍️ Synthesizer đã phát hiện câu hỏi ngoài phạm vi và từ chối xử lý."]
        }
    
    # Tìm context của retriever chứa thông tin trích dẫn để chuyển cho synthesizer
    context = ""
    if state.get("messages"):
        for msg in reversed(state["messages"]):
            if "**[Trang" in msg.content:
                context = msg.content
                break
                
    # Lấy dữ liệu từ execution_result (nếu có) hoặc từ context
    if state.get("execution_result"):
        data = f"Kết quả thực thi mã tính toán:\n{state['execution_result']}\n\nDữ liệu thô tham chiếu:\n{context}"
    else:
        data = state["messages"][-1].content if state["messages"] else "Không tìm thấy dữ liệu."

    prompt = ChatPromptTemplate.from_messages([("system", SYNTHESIZER_PROMPT)])
    chain = prompt | llm
    
    response = chain.invoke({
        "query": question,
        "data": data,
        "error_count": error_count
    })
    
    final_answer = response.content
    
    # Nếu có biểu đồ base64 trong state, nhúng thẳng vào cuối câu trả lời dạng Markdown
    if state.get("chart_path") and state["chart_path"].startswith("data:image"):
        final_answer += f"\n\n![Biểu đồ tài chính]({state['chart_path']})"
    elif state.get("chart_path") and os.path.exists(state["chart_path"]):
        # Fallback nếu chart_path là đường dẫn tệp thực tế
        import base64
        try:
            with open(state["chart_path"], "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                final_answer += f"\n\n![Biểu đồ tài chính](data:image/png;base64,{encoded_string})"
        except Exception as e:
            print(f"[Synthesizer] Failed to read chart file: {e}")
    
    return {
        "final_answer": final_answer,
        "steps": ["✍️ Synthesizer đã tổng hợp câu trả lời cuối cùng."]
    }
