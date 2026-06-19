# OCR Quality Evaluation Report

This report benchmarks the accuracy of EasyOCR with PyMuPDF table parsers on Vietnamese scanned reports.

## Metrics Summary

| Metric | Average Error Rate | Average Accuracy | Target Threshold | Status |
|---|---|---|---|---|
| **Character Error Rate (CER)** | 0.0280 | 97.20% | < 5.00% (Accuracy > 95%) | ✅ PASS |
| **Word Error Rate (WER)** | 0.0764 | 92.36% | < 10.00% (Accuracy > 90%) | ✅ PASS |

## Detailed Page Breakdown

| Page ID | Document Type | CER | WER | CER Accuracy | WER Accuracy |
|---|---|---|---|---|---|
| Page_01 | scanned_table | 0.0000 | 0.0000 | 100.00% | 100.00% |
| Page_02 | scanned_text | 0.0112 | 0.0625 | 98.88% | 93.75% |
| Page_03 | noisy_scanned_table | 0.0727 | 0.1667 | 92.73% | 83.33% |
