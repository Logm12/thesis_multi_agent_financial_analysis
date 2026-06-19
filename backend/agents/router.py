import os
from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from .state import AgentState
from core.config import ROUTER_MODEL
from dotenv import load_dotenv

load_dotenv()


class RouteQuery(BaseModel):
    """Phân loại ý định người dùng."""

    intent: Literal["retrieve", "code", "out_of_scope"] = Field(
        ...,
        description="Ý định: retrieve (tra cứu thông tin), code (tính toán/so sánh/vẽ biểu đồ) hoặc out_of_scope (câu hỏi phá hoại, ngoài lề, không liên quan tài chính)",
    )
    reasoning: str = Field(..., description="Lý do phân loại ý định.")


from core.nim_client import get_nim_llm

# Khởi tạo model từ config
llm = get_nim_llm(
    model_name=ROUTER_MODEL,
    temperature=0,
)

# Ràng buộc output theo Pydantic schema
structured_llm = llm.with_structured_output(RouteQuery)

ROUTER_PROMPT = """You are a specialized router agent for a financial statement analysis system.
Your task is to classify the user's query into one of the following categories:

1. 'retrieve': Questions that are informational, querying facts, definitions, or standard textual details present in the document.
   - Examples: "What is the revenue for 2024?", "What is the corporate vision statement?", "Who is the CEO?"
2. 'code': Questions requiring mathematical computations, multi-year comparisons, or chart generation.
   - Examples: "Compare the revenue growth rate over the last 3 years", "Calculate the net profit margin", "Draw a chart showing liabilities."
3. 'out_of_scope': Out-of-scope, off-topic, or malicious queries that are not related to corporate financial statement analysis.
   - Examples: "What is the weather today?", "How do I hack a Facebook account?", "Write a poem for me."

Analyze the question carefully and return the most appropriate classification."""


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

    print(f"[Router] Intent: {result.intent} | Reason: {result.reasoning}")

    # Telemetry Logging Guard: Save query, predicted intent, and ground truth to PostgreSQL
    from core.database import get_db_connection
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO intent_logs (query, predicted_intent, ground_truth) VALUES (%s, %s, %s)",
                    (user_question, result.intent, state.get("ground_truth"))
                )
    except Exception as e:
        print(f"[Telemetry Logging Guard] Error inserting intent log: {str(e)}")

    # Poka-Yoke firewall: enforce strict Literal type checks
    allowed_intents = {"retrieve", "code", "out_of_scope"}
    validated_intent = result.intent if result.intent in allowed_intents else "out_of_scope"

    return {
        "intent": validated_intent, 
        "question": user_question, 
        "error_count": 0,
        "steps": [f"Router determined query intent: {validated_intent} ({result.reasoning})"]
    }

