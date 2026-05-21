import sys
from pathlib import Path

project_root = str(Path(__file__).parent.parent.absolute())
backend_path = str(Path(__file__).parent.parent.absolute() / "backend")
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from backend.tools.sandbox import SafePythonREPL

print("Initializing SafePythonREPL...")
repl = SafePythonREPL()

code = """
import pandas as pd
df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
print(df['a'].sum())
"""

print("Executing test code...")
res = repl.execute(code)
print("Execution completed.")
print("Success:", res["success"])
print("Stdout:", res["stdout"])
print("Stderr:", res["stderr"])
print("Error:", res["error"])
