from backend.tools.sandbox import SafePythonREPL

def test_sandbox_valid_code():
    """Verify that safe mathematical and data operations are allowed to execute."""
    repl = SafePythonREPL()
    code = (
        "import pandas as pd\n"
        "import numpy as np\n"
        "df = pd.DataFrame({'A': [1, 2, 3]})\n"
        "res = df['A'].sum() + np.sqrt(4)\n"
        "print(res)"
    )
    result = repl.execute(code)
    assert result["success"] is True
    assert "8.0" in result["stdout"]
    assert not result["error"]

def test_sandbox_blocks_import_os():
    """Verify that importing 'os' module raises a SecurityError."""
    repl = SafePythonREPL()
    code = "import os; os.system('echo Hacked')"
    result = repl.execute(code)
    assert result["success"] is False
    assert "Security Validation Error" in result["error"]
    assert "module 'os' is blocked" in result["error"]

def test_sandbox_blocks_import_sys():
    """Verify that importing 'sys' module raises a SecurityError."""
    repl = SafePythonREPL()
    code = "import sys; sys.exit(0)"
    result = repl.execute(code)
    assert result["success"] is False
    assert "Security Validation Error" in result["error"]
    assert "module 'sys' is blocked" in result["error"]

def test_sandbox_blocks_import_subprocess():
    """Verify that importing 'subprocess' module raises a SecurityError."""
    repl = SafePythonREPL()
    code = "import subprocess; subprocess.run(['echo', 'Hacked'])"
    result = repl.execute(code)
    assert result["success"] is False
    assert "Security Validation Error" in result["error"]
    assert "module 'subprocess' is blocked" in result["error"]

def test_sandbox_blocks_open():
    """Verify that the built-in 'open' function is blocked."""
    repl = SafePythonREPL()
    code = "f = open('malicious.txt', 'w'); f.write('hacked')"
    result = repl.execute(code)
    assert result["success"] is False
    assert "Security Validation Error" in result["error"]
    assert "built-in function 'open' is blocked" in result["error"]

def test_sandbox_blocks_eval_exec():
    """Verify that 'eval' and 'exec' functions are blocked."""
    repl = SafePythonREPL()
    # Test eval
    result_eval = repl.execute("eval('1+1')")
    assert result_eval["success"] is False
    assert "built-in function 'eval' is blocked" in result_eval["error"]
    
    # Test exec
    result_exec = repl.execute("exec('print(1)')")
    assert result_exec["success"] is False
    assert "built-in function 'exec' is blocked" in result_exec["error"]

def test_sandbox_blocks_getattr_setattr():
    """Verify that 'getattr' and 'setattr' are blocked to prevent dynamic access."""
    repl = SafePythonREPL()
    # Test getattr
    result_getattr = repl.execute("getattr(pd, 'DataFrame')")
    assert result_getattr["success"] is False
    assert "built-in function 'getattr' is blocked" in result_getattr["error"]

def test_sandbox_blocks_dunders():
    """Verify that accessing double-underscore (dunder) methods/properties is blocked."""
    repl = SafePythonREPL()
    code = "df = pd.DataFrame({'A': [1]}); df.__class__.__bases__"
    result = repl.execute(code)
    assert result["success"] is False
    assert "Security Validation Error" in result["error"]
    assert "dunder attributes" in result["error"]
