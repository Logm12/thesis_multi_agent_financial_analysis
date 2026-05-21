import pytest
import base64
from backend.tools.sandbox import SafePythonREPL

def test_sandbox_matplotlib_chart_generation():
    """
    Verify that executing code using matplotlib inside SafePythonREPL
    generates a valid, non-empty base64-encoded PNG chart.
    """
    repl = SafePythonREPL()
    
    # Python script using matplotlib to draw a simple line chart
    chart_code = (
        "import matplotlib.pyplot as plt\n"
        "import numpy as np\n"
        "x = np.linspace(0, 10, 100)\n"
        "y = np.sin(x)\n"
        "plt.figure(figsize=(6, 4))\n"
        "plt.plot(x, y, label='Sine Wave', color='blue')\n"
        "plt.title('Integration Test Sine Plot')\n"
        "plt.xlabel('X axis')\n"
        "plt.ylabel('Y axis')\n"
        "plt.legend()\n"
        "plt.grid(True)\n"
        "print('Chart generated successfully')"
    )
    
    result = repl.execute(chart_code)
    
    # Assert successful execution in sandbox
    assert result["success"] is True
    assert "Chart generated successfully" in result["stdout"]
    assert not result["error"]
    
    # Assert that a base64 plot was captured
    plot_b64 = result["plot"]
    assert plot_b64 != ""
    assert isinstance(plot_b64, str)
    
    # Verify that the base64 string can be successfully decoded into a valid PNG
    try:
        decoded_bytes = base64.b64decode(plot_b64)
        # Check PNG header signature: \x89PNG\r\n\x1a\n
        assert decoded_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    except Exception as e:
        pytest.fail(f"Failed to decode base64 plot into a valid PNG: {e}")

def test_sandbox_multiple_plots_isolation():
    """
    Verify that the sandbox isolates state and clears previous plots on each execution.
    """
    repl = SafePythonREPL()
    
    # 1. First run generates a plot
    plot_code_1 = (
        "import matplotlib.pyplot as plt\n"
        "plt.plot([1, 2], [3, 4])\n"
        "print('Plot 1')"
    )
    res1 = repl.execute(plot_code_1)
    assert res1["success"] is True
    assert res1["plot"] != ""
    
    # 2. Second run executes code with NO plot, verifying previous plot is cleared and not returned
    plot_code_2 = (
        "print('No Plot Here')"
    )
    res2 = repl.execute(plot_code_2)
    assert res2["success"] is True
    assert res2["plot"] == ""
