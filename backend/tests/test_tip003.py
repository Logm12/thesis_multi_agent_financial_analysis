import pytest
from backend.tools.sandbox import SafePythonREPL, SecurityError

def test_safe_repl_ast_blocks_malicious_code():
    repl = SafePythonREPL()
    # Blocks imports not in whitelist
    with pytest.raises(SecurityError) as exc1:
        repl.validate_code("import os\nos.system('echo Hello')")
    assert "Import of module 'os' is blocked" in str(exc1.value)

    # Blocks blocked builtins
    with pytest.raises(SecurityError) as exc2:
        repl.validate_code("open('test.txt', 'w')")
    assert "Call to built-in function 'open' is blocked" in str(exc2.value)

def test_safe_repl_execution():
    repl = SafePythonREPL()
    code = "import pandas as pd\ndf = pd.DataFrame({'A': [1, 2]})\nprint(df['A'].sum())"
    res = repl.execute(code)
    assert res["success"] is True
    assert "3" in res["stdout"]

def test_safe_repl_timeout():
    repl = SafePythonREPL()
    # Execute an infinite math calculation loop
    code = "import math\nwhile True:\n    math.sqrt(9.0)"
    res = repl.execute(code, timeout=1.0)
    assert res["success"] is False
    assert "timed out" in res["stderr"]
