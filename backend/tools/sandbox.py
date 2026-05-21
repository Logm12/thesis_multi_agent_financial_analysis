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

    def execute(self, code_str: str) -> dict:
        """
        Executes code safely and captures stdout, stderr, and generated matplotlib plots.
        Returns:
            {"stdout": str, "stderr": str, "plot": str (base64 image or empty), "success": bool, "error": str}
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

        # Clear any existing matplotlib plots
        plt.clf()
        plt.close('all')

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        captured_stdout = io.StringIO()
        captured_stderr = io.StringIO()
        
        success = True
        error_msg = ""

        try:
            sys.stdout = captured_stdout
            sys.stderr = captured_stderr

            # Define safe builtins dynamically
            if hasattr(__builtins__, "__dict__"):
                builtins_dict = __builtins__.__dict__
            elif isinstance(__builtins__, dict):
                builtins_dict = __builtins__
            else:
                builtins_dict = {}
                
            safe_builtins = {k: v for k, v in builtins_dict.items() if k not in self.blocked_builtins}

            # Define safe globals
            safe_globals = {
                "__builtins__": safe_builtins,
                "pd": pd,
                "pandas": pd,
                "np": np,
                "numpy": np,
                "plt": plt,
                "matplotlib": matplotlib
            }
            
            try:
                exec(code_str, safe_globals)
            except Exception as e:
                success = False
                error_msg = str(e)
                print(f"Runtime Error: {e}", file=sys.stderr)
        except Exception as e:
            success = False
            error_msg = f"Sandbox Setup Error: {e}"
            captured_stderr.write(f"Sandbox Setup Error: {e}\n")
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        # Capture plot if generated
        plot_base64 = ""
        try:
            fig = plt.gcf()
            if fig.get_axes():  # Check if there is an active plot
                buf = io.BytesIO()
                fig.savefig(buf, format='png', bbox_inches='tight')
                buf.seek(0)
                plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
        except Exception as e:
            captured_stderr.write(f"Matplotlib capture failed: {e}\n")
        finally:
            plt.clf()
            plt.close('all')

        return {
            "stdout": captured_stdout.getvalue(),
            "stderr": captured_stderr.getvalue(),
            "plot": plot_base64,
            "success": success,
            "error": error_msg
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
