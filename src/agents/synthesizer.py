import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from agents.state import AgentState
from config import SYNTHESIZER_MODEL
from dotenv import load_dotenv

load_dotenv()

# Khởi tạo model từ config
llm = ChatOpenAI(
    model=SYNTHESIZER_MODEL,
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
)

SYNTHESIZER_PROMPT = """Là một chuyên gia tư vấn tài chính, hãy tổng hợp dữ liệu sau: {data} để trả lời câu hỏi: {query}. 
Yêu cầu: TRỰC DIỆN, NGẮN GỌN, dùng văn phong lịch sự. Nếu phát hiện dữ liệu thiếu, hãy ghi chú rõ. Tuyệt đối không bịa đặt số liệu (Zero Hallucination).

Nếu có biểu đồ (chart.png) được nhắc tới trong kết quả, hãy dặn người dùng xem biểu đồ đính kèm phía dưới.
Nếu đây là trường hợp lỗi (error_count >= 3), hãy đưa ra thông báo lỗi thân thiện: "Tôi đã cố gắng tính toán nhưng gặp sự cố kỹ thuật, dưới đây là dữ liệu thô tôi tìm thấy..." kèm theo dữ liệu hiện có.

Hãy viết câu trả lời cuối cùng:"""

def synthesizer_node(state: AgentState) -> dict:
    """Node tổng hợp câu trả lời cuối cùng."""
    question = state["question"]
    error_count = state.get("error_count", 0)
    
    # Lấy dữ liệu từ execution_result (nếu có) hoặc từ context trong messages
    if state.get("execution_result"):
        data = f"Kết quả thực thi mã: {state['execution_result']}"
    else:
        # Lấy tin nhắn cuối cùng (thường là từ retriever)
        data = state["messages"][-1].content if state["messages"] else "Không tìm thấy dữ liệu."

    prompt = ChatPromptTemplate.from_messages([("system", SYNTHESIZER_PROMPT)])
    chain = prompt | llm
    
    response = chain.invoke({
        "query": question,
        "data": data,
        "error_count": error_count
    })
    
    final_answer = response.content
    
    return {
        "final_answer": final_answer,
        "steps": ["✍️ Synthesizer đã tổng hợp câu trả lời cuối cùng."]
    }
