import sys
import io
from pathlib import Path
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Config console to display Vietnamese
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Add root and backend to sys.path
project_root = str(Path(__file__).parent.parent.absolute())
backend_path = str(Path(__file__).parent.parent.absolute() / "backend")
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from backend.agents.graph import get_graph_app

def verify_calculation():
    load_dotenv()
    app = get_graph_app()
    
    query = "Doanh thu năm 2023 là 100 tỷ, 2022 là 80 tỷ, tính tốc độ tăng trưởng %."
    print(f"\n=== VERIFYING TIP-002 ===")
    print(f"Query: {query}")
    print("-" * 40)
    
    initial_state = {
        "messages": [HumanMessage(content=query)]
    }
    
    try:
        result = app.invoke(initial_state, config={"configurable": {"thread_id": "verify_tip_002"}})
        print("\n--- EXECUTION RESULTS ---")
        print(f"Intent identified: {result.get('intent')}")
        print(f"Generated Python Code:\n{result.get('current_code')}")
        print("-" * 40)
        print(f"REPL Output:\n{result.get('execution_result')}")
        print("-" * 40)
        print(f"Final Synthesized Answer:\n{result.get('final_answer')}")
        print("\n✅ SUCCESS: Execution completed without Syntax or Key errors.")
    except Exception as e:
        print(f"\n❌ FAILED with Exception: {e}")

if __name__ == "__main__":
    verify_calculation()
