import operator
from typing import TypedDict, Annotated, Literal, Optional, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Trạng thái (State) chung cho LangGraph workflow.

    Attributes:
        messages: Danh sách lịch sử tin nhắn.
        intent: Ý định người dùng (retrieve hoặc code).
        question: Câu hỏi hiện tại.
        error_count: Số lần thử lại nếu code fail.
        current_code: Đoạn code Python đang thực thi.
        execution_result: Kết quả thực thi từ sandbox.
        steps: Nhật ký các bước thực hiện (Thought Process).
        final_answer: Câu trả lời cuối cùng đã được biên tập.
    """

    messages: Annotated[list[BaseMessage], add_messages]
    intent: Literal["retrieve", "code"]
    question: str
    error_count: int
    current_code: Optional[str]
    execution_result: Optional[str]
    steps: Annotated[List[str], operator.add]
    final_answer: Optional[str]
