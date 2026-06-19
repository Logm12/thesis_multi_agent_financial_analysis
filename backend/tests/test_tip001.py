import pytest
from backend.services.rag.cleaner import clean_vietnamese_text
from backend.services.ocr.pdf_parser import FastPDFParser, SmokeTestFailure

def test_cleaner_conversions():
    # Test typical VAS numbers with thousand dots and decimal commas
    assert clean_vietnamese_text("1.250.000,50") == "1250000.50"
    assert clean_vietnamese_text("1.250.000") == "1250000.0"
    assert clean_vietnamese_text("340,75") == "340.75"
    assert clean_vietnamese_text("No modification 100") == "No modification 100"

def test_smoke_test_passing():
    blocks = [
        {
            "type": "table",
            "table_layout": {
                "json_data": [
                    {"text": "100"}, {"text": "200"}, {"text": "300"},
                    {"text": "400"}, {"text": "500"}, {"text": "600"}
                ]
            }
        }
    ]
    res = FastPDFParser.smoke_test(blocks)
    assert res["passed"] is True
    assert res["loss_rate"] == 0.0

def test_smoke_test_failing():
    blocks = [
        {
            "type": "table",
            "table_layout": {
                "json_data": [
                    {"text": "100"}, {"text": ""}, {"text": ""},
                    {"text": "400"}, {"text": "500"}, {"text": "600"}
                ]
            }
        }
    ]
    # loss rate: 2/6 = 33.3% > 2.6% -> should fail
    with pytest.raises(SmokeTestFailure) as exc:
        FastPDFParser.smoke_test(blocks)
    assert "exceeds the maximum threshold of 2.60%" in str(exc.value)
