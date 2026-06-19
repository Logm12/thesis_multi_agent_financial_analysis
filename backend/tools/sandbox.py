import ast
import io
import sys
import matplotlib
matplotlib.use('Agg')  # Ensure matplotlib doesn't try to open a GUI window
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import base64

class SecurityError(Exception):
    pass

class SafePythonREPL:
    """
    Safe Python REPL Sandbox using AST analysis to prevent dangerous code execution.
    Only allows pandas, numpy, and matplotlib.
    Blocks os, sys, subprocess, builtins open, eval, exec, etc.
    """
    def __init__(self):
        # Whitelist of allowed modules
        self.allowed_modules = {"pandas", "numpy", "matplotlib", "matplotlib.pyplot", "plt", "pd", "np", "json", "math"}
        # Blacklist of built-in functions
        self.blocked_builtins = {"open", "eval", "exec", "globals", "locals", "compile", "dir", "help", "input", "getattr", "setattr", "delattr"}

    def validate_code(self, code_str: str) -> bool:
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            raise ValueError(f"Syntax Error: {e}")

        for node in ast.walk(tree):
            # Block Import and ImportFrom
            if isinstance(node, ast.Import):
                for alias in node.names:
                    base_module = alias.name.split('.')[0]
                    if base_module not in self.allowed_modules:
                        raise SecurityError(f"Import of module '{alias.name}' is blocked.")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    base_module = node.module.split('.')[0]
                    if base_module not in self.allowed_modules:
                        raise SecurityError(f"Import from module '{node.module}' is blocked.")
            
            # Block function calls to blocked builtins
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.blocked_builtins:
                        raise SecurityError(f"Call to built-in function '{node.func.id}' is blocked.")
                elif isinstance(node.func, ast.Attribute):
                    # Catch e.g. __builtins__.open
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "__builtins__":
                        if node.func.attr in self.blocked_builtins:
                            raise SecurityError(f"Call to built-in function '{node.func.attr}' is blocked.")
            
            # Block double underscores (dunder attributes)
            elif isinstance(node, ast.Attribute):
                if node.attr.startswith("__"):
                    raise SecurityError("Access to dunder attributes is blocked.")
            elif isinstance(node, ast.Name):
                if node.id.startswith("__"):
                    raise SecurityError("Access to dunder names is blocked.")

        return True

    def execute(self, code_str: str, timeout: float = 10.0) -> dict:
        """
        Executes code safely and captures stdout, stderr, and generated matplotlib plots.
        Uses a separate subprocess for security and cross-platform timeout/SIGKILL capabilities.
        """
        try:
            self.validate_code(code_str)
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "plot": "",
                "success": False,
                "error": f"Security Validation Error: {e}"
            }

        runner_script = """
import sys
import json
import base64
import io
import traceback

def run_code(code_str):
    import pandas as pd
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        'figure.facecolor': '#FFFFFF',
        'axes.facecolor': '#F8FAFC',
        'axes.edgecolor': '#CBD5E1',
        'axes.grid': True,
        'grid.color': '#E2E8F0',
        'grid.alpha': 0.6,
        'font.family': 'sans-serif',
        'font.size': 10,
        'text.color': '#1E293B',
        'axes.labelcolor': '#1E293B',
        'xtick.color': '#475569',
        'ytick.color': '#475569',
        'figure.figsize': (10, 6),
        'savefig.facecolor': '#FFFFFF',
        'savefig.bbox': 'tight',
    })

    class NumpyJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (pd.Timestamp, pd.Period)):
                return str(obj)
            return super().default(obj)

    class CustomJSON:
        def dumps(self, *args, **kwargs):
            if 'cls' not in kwargs:
                kwargs['cls'] = NumpyJSONEncoder
            return json.dumps(*args, **kwargs)
        def dump(self, *args, **kwargs):
            if 'cls' not in kwargs:
                kwargs['cls'] = NumpyJSONEncoder
            return json.dump(*args, **kwargs)
        def __getattr__(self, name):
            return getattr(json, name)

    custom_json = CustomJSON()

    captured_stdout = io.StringIO()
    captured_stderr = io.StringIO()
    
    sys.stdout = captured_stdout
    sys.stderr = captured_stderr

    blocked_builtins = {"open", "eval", "exec", "globals", "locals", "compile", "dir", "help", "input", "getattr", "setattr", "delattr"}
    if hasattr(__builtins__, "__dict__"):
        builtins_dict = __builtins__.__dict__
    elif isinstance(__builtins__, dict):
        builtins_dict = __builtins__
    else:
        builtins_dict = {}
    safe_builtins = {k: v for k, v in builtins_dict.items() if k not in blocked_builtins}

    safe_globals = {
        "__builtins__": safe_builtins,
        "pd": pd,
        "pandas": pd,
        "np": np,
        "numpy": np,
        "plt": plt,
        "matplotlib": matplotlib,
        "json": custom_json
    }


    success = True
    error_msg = ""
    try:
        exec(code_str, safe_globals)
    except Exception as e:
        success = False
        error_msg = str(e)
        traceback.print_exc(file=sys.stderr)
        
    plot_base64 = ""
    try:
        fig = plt.gcf()
        if fig.get_axes():
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
    except Exception as e:
        captured_stderr.write(f"Matplotlib capture failed: {e}\\n")
    finally:
        plt.clf()
        plt.close('all')

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    result = {
        "stdout": captured_stdout.getvalue(),
        "stderr": captured_stderr.getvalue(),
        "plot": plot_base64,
        "success": success,
        "error": error_msg
    }
    print(json.dumps(result))

if __name__ == "__main__":
    user_code = sys.stdin.read()
    run_code(user_code)
"""

        import subprocess
        import sys
        import json
        import shutil
        
        # Check if docker is available and running
        use_docker = False
        if shutil.which("docker"):
            try:
                # Quick check if docker daemon is reachable
                res = subprocess.run(["docker", "info"], capture_output=True, timeout=2)
                if res.returncode == 0:
                    use_docker = True
            except Exception:
                pass

        try:
            if use_docker:
                # Run containerized using thesis-backend:latest
                proc = subprocess.Popen(
                    [
                        "docker", "run", "--rm", "-i",
                        "--network", "none",
                        "--memory", "256m",
                        "--cpus", "0.5",
                        "thesis-backend:latest",
                        "python", "-u", "-c", runner_script
                    ],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8"
                )
            else:
                proc = subprocess.Popen(
                    [sys.executable, "-c", runner_script],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8"
                )
            
            try:
                stdout, stderr = proc.communicate(input=code_str, timeout=timeout)
            except subprocess.TimeoutExpired:
                # Force kill the process/container
                if use_docker:
                    # Docker containers ran with --rm are killed, but let's terminate the parent process immediately
                    proc.kill()
                    proc.communicate()
                else:
                    proc.kill()
                    proc.communicate()
                return {
                    "stdout": "",
                    "stderr": f"Execution timed out after {timeout} seconds. Process was terminated.",
                    "plot": "",
                    "success": False,
                    "error": f"TimeoutError: Execution exceeded time limit of {timeout}s."
                }
                
            if proc.returncode != 0:
                return {
                    "stdout": stdout,
                    "stderr": stderr or f"Process exited with code {proc.returncode}",
                    "plot": "",
                    "success": False,
                    "error": f"Process exited with non-zero code {proc.returncode}"
                }
                
            # Parse result from stdout JSON
            try:
                result = json.loads(stdout.strip())
                return result
            except Exception as parse_err:
                return {
                    "stdout": stdout,
                    "stderr": stderr + f"\nParse Error: {parse_err}",
                    "plot": "",
                    "success": False,
                    "error": f"Failed to parse runner output: {parse_err}"
                }
                
        except Exception as setup_err:
            return {
                "stdout": "",
                "stderr": str(setup_err),
                "plot": "",
                "success": False,
                "error": f"Sandbox execution setup error: {setup_err}"
            }

if __name__ == "__main__":
    repl = SafePythonREPL()
    
    # Test valid code
    valid_code = "import pandas as pd\ndf = pd.DataFrame({'A': [1, 2, 3]})\nprint(df.sum())"
    print("Valid Code execution test:")
    print(repl.execute(valid_code))
    
    # Test invalid code
    invalid_code = "import os\nos.system('echo Hello')"
    print("\nInvalid Code execution test (os block):")
    print(repl.execute(invalid_code))
    
    # Test built-in open block
    blocked_code = "open('test.txt', 'w')"
    print("\nInvalid Code execution test (open block):")
    print(repl.execute(blocked_code))

