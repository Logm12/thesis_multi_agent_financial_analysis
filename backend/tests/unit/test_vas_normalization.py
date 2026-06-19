import pandas as pd
import numpy as np

def clean_vas_column(series: pd.Series) -> pd.Series:
    # Stage 1: Strip currency, spaces, and other noise except digits, dots, commas, and minus signs
    s_stage1 = series.astype(str).str.replace(r'[^\d\.,-]', '', regex=True)
    # Stage 2: Remove dot thousands separators
    s_stage2 = s_stage1.str.replace('.', '', regex=False)
    # Stage 3: Replace decimal comma with dot and cast to float
    return pd.to_numeric(s_stage2.str.replace(',', '.', regex=False), errors='coerce')

def test_vas_normalization_pipeline():
    """Verify the 3-stage normalization process handles VAS formatted numbers correctly."""
    inputs = pd.Series([
        "1.234.567,89 VND",
        " -500.000,00 USD ",
        "N/A",
        "100",
        "1.234,56",
        "0,05",
        "1.000.000"
    ])
    
    expected = [
        1234567.89,
        -500000.0,
        np.nan,
        100.0,
        1234.56,
        0.05,
        1000000.0
    ]
    
    outputs = clean_vas_column(inputs)
    
    for out, exp in zip(outputs, expected):
        if np.isnan(exp):
            assert np.isnan(out)
        else:
            assert abs(out - exp) < 1e-9
