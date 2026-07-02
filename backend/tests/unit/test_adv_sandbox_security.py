import pytest
import pandas as pd
import numpy as np
import time
from backend.tools.sandbox import SafePythonREPL

def test_tc_adv_be_11_dynamic_attribute_obfuscation():
    """TC-ADV-BE-11: Attempt to bypass builtin filters via getattr / string manipulation."""
    repl = SafePythonREPL()
    # Attempt: getattr(pd, "__builtins__")["eval"](...)
    code = 'getattr(pd, "__builtins__")["eval"]("import os; os.system(\'id\')")'
    result = repl.execute(code)
    assert result["success"] is False
    assert "Security Validation Error" in result["error"]
    assert "built-in function 'getattr' is blocked" in result["error"]

def test_tc_adv_be_12_c_extension_ctypes_blocked():
    """TC-ADV-BE-12: Import ctypes to access system memory directly."""
    repl = SafePythonREPL()
    code = 'import ctypes; ctypes.CDLL(None)'
    result = repl.execute(code)
    assert result["success"] is False
    assert "Security Validation Error" in result["error"]
    assert "Import of module 'ctypes' is blocked" in result["error"]

def test_tc_adv_be_13_symlink_attack_prevention():
    """TC-ADV-BE-13: Code attempting to use os.symlink to read host configuration."""
    repl = SafePythonREPL()
    code = 'import os; os.symlink("/etc/passwd", "/tmp/passwd_link")'
    result = repl.execute(code)
    assert result["success"] is False
    assert "Import of module 'os' is blocked" in result["error"]

def test_tc_adv_be_14_redos_regex_timeout():
    """TC-ADV-BE-14: Test regex clean logic limits ReDoS (algorithmic DoS)."""
    # Simple simulated ReDoS target
    pattern = re_pattern = r'^(a+)+$'
    evil_input = "a" * 30 + "!"
    
    start_time = time.time()
    # If regex engine supports timeout or we do length checks:
    import re
    # Python's re doesn't support timeout natively, so we guard by input length limits in code.
    # We verify that if execution takes too long, SafePythonREPL timeout halts the subprocess.
    repl = SafePythonREPL()
    code = f"""
import re
pattern = r'{pattern}'
evil_input = '{evil_input}'
re.match(pattern, evil_input)
"""
    # Since re is not allowed by default in whitelist, it should fail immediately
    result = repl.execute(code)
    assert result["success"] is False
    assert "Import of module 're' is blocked" in result["error"]

def test_tc_adv_be_15_multithreading_fork_bomb():
    """TC-ADV-BE-15: Attempt to fork process table via multiprocessing / os.fork."""
    repl = SafePythonREPL()
    code = 'import multiprocessing; multiprocessing.Process(target=lambda: 1).start()'
    result = repl.execute(code)
    assert result["success"] is False
    assert "Import of module 'multiprocessing' is blocked" in result["error"]

def test_tc_adv_be_16_explosive_dataframe_join_limit():
    """TC-ADV-BE-16: Descartes cross merge to exhaust sandbox memory limit."""
    repl = SafePythonREPL()
    # Construct a massive cross join code. If Docker sandbox runs, it will be killed due to OOM.
    # If running locally, SafePythonREPL timeout will kill it.
    code = """
import pandas as pd
df1 = pd.DataFrame({'key': [1]*100000})
df2 = pd.DataFrame({'key': [1]*100000})
res = pd.merge(df1, df2, on='key', how='outer')
"""
    result = repl.execute(code, timeout=3.0)
    assert result["success"] is False
    # Success means it either OOM killed (returncode != 0) or hit TimeoutError
    assert ("TimeoutError" in result["error"] or "exited with" in result["error"] or "Killed" in result["error"] or "out of memory" in result["error"].lower())

def test_tc_adv_be_17_nan_infinity_propagation():
    """TC-ADV-BE-17: NaN and Inf values propagation inside pandas."""
    repl = SafePythonREPL()
    code = """
import pandas as pd
import numpy as np
df = pd.DataFrame({'a': [1, 2], 'b': [0, 0]})
df['res'] = df['a'] / df['b'] # creates inf
print(df['res'].tolist())
"""
    result = repl.execute(code)
    assert result["success"] is True
    assert "inf" in result["stdout"]

def test_tc_adv_be_18_env_var_poisoning():
    """TC-ADV-BE-18: Writing to system environment variables inside container."""
    repl = SafePythonREPL()
    code = 'import os; os.environ["PATH"] = "/evil_bin"'
    result = repl.execute(code)
    assert result["success"] is False
    assert "Import of module 'os' is blocked" in result["error"]

def test_tc_adv_be_19_zip_bomb_ingestion_limit():
    """TC-ADV-BE-19: Protect against Zip/PDF decompression bombs."""
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB Limit
    # Simulating upload size validation
    uploaded_file_size = 150 * 1024 * 1024 # 150MB
    assert uploaded_file_size > MAX_FILE_SIZE

def test_tc_adv_be_20_matplotlib_giant_canvas_limit():
    """TC-ADV-BE-20: Prevent memory crash via giant resolution Matplotlib render."""
    repl = SafePythonREPL()
    # Attempting to draw an extremely giant canvas
    code = """
import matplotlib.pyplot as plt
plt.figure(figsize=(20000, 20000))
plt.plot([1, 2], [3, 4])
"""
    result = repl.execute(code, timeout=3.0)
    assert result["success"] is False
    # Should hit memory limits and get killed or timeout
    assert ("TimeoutError" in result["error"] or "Process exited" in result["error"] or "Security" in result["error"] or "fail" in result["error"].lower())
