import os
from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from agents.state import AgentState
from config import ROUTER_MODEL
from dotenv import load_dotenv

load_dotenv()


class RouteQuery(BaseModel):
    """Phân loại ý định người dùng."""

    intent: Literal["retrieve", "code"] = Field(
        ...,
        description="Ý định: retrieve (tra cứu thông tin) hoặc code (tính toán/so sánh/vẽ biểu đồ)",
    )
    reasoning: str = Field(..., description="Lý do phân loại ý định.")


# Khởi tạo model từ config
llm = ChatOpenAI(
    model=ROUTER_MODEL,
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Ràng buộc output theo Pydantic schema
structured_llm = llm.with_structured_output(RouteQuery)

ROUTER_PROMPT = """Bạn là một chuyên gia điều phối (Router Agent) cho hệ thống phân tích báo cáo tài chính.
Nhiệm vụ của bạn là phân loại câu hỏi của người dùng vào một trong hai loại sau:

1. 'retrieve': Câu hỏi mang tính tra cứu, tìm kiếm định nghĩa hoặc thông tin có sẵn trong văn bản.
   - VD: "Doanh thu năm 2024 là bao nhiêu?", "Tầm nhìn của công ty là gì?", "Ai là chủ tịch?"
2. 'code': Câu hỏi mang tính tính toán phức tạp, so sánh dữ liệu nhiều năm, hoặc yêu cầu vẽ biểu đồ.
   - VD: "So sánh tăng trưởng doanh thu 3 năm qua", "Tính tỷ lệ biên lợi nhuận ròng", "Vẽ biểu đồ nợ phải trả."

Hãy phân tích kỹ nội dung câu hỏi và trả về kết quả phân loại phù hợp nhất."""


def router_node(state: AgentState) -> dict:
    """Node phân loại ý định sử dụng OpenAI GPT-4o-mini."""
    user_question = (
        state["messages"][-1].content
        if state["messages"]
        else state.get("question", "")
    )

    prompt = ChatPromptTemplate.from_messages(
        [("system", ROUTER_PROMPT), ("human", "{question}")]
    )

    chain = prompt | structured_llm
    result: RouteQuery = chain.invoke({"question": user_question})

    print(f"[Router] Intent: {result.intent} | Lý do: {result.reasoning}")

    return {
        "intent": result.intent, 
        "question": user_question, 
        "error_count": 0,
        "steps": [f"🔍 Router đã xác định ý định: {result.intent} ({result.reasoning})"]
    }
