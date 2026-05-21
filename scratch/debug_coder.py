import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import AIMessage

project_root = str(Path(__file__).parent.parent.absolute())
backend_path = str(Path(__file__).parent.parent.absolute() / "backend")
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

load_dotenv()

from backend.agents.coder import coder_node
from backend.agents.state import AgentState

state = {
    "question": "Doanh thu năm 2023 là 100 tỷ, 2022 là 80 tỷ, tính tốc độ tăng trưởng %.",
    "messages": [AIMessage(content="Doanh thu năm 2023 là 100 tỷ, 2022 là 80 tỷ.")],
    "error_count": 0,
    "steps": []
}

class Config:
    pass

config = {"configurable": {"session_tmp_dir": "tmp"}}

try:
    print("Calling coder_node...")
    res = coder_node(state, config)
    print("--- RESULT ---")
    print("Code:")
    print(res.get("current_code"))
    print("Execution Result:")
    print(res.get("execution_result"))
    print("Error count:", res.get("error_count"))
except Exception as e:
    print("Exception occurred:", e)
