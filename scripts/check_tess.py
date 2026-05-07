from docling.datamodel.pipeline_options import PdfPipelineOptions
import traceback
import sys

with open("tess_log.txt", "w", encoding="utf-8") as f:
    f.write("Trying to import docling tesseract models...\n")
    f.write(f"Python path: {sys.executable}\n")
    try:
        from docling.models.tesseract_ocr_cli_model import TesseractCliOcrOptions
        f.write("Found TesseractCliOcrOptions\n")
    except Exception as e:
        f.write("Error TesseractCliOcrOptions:\n")
        traceback.print_exc(file=f)

    try:
        from docling.models.tesseract_ocr_model import TesseractOcrOptions
        f.write("Found TesseractOcrOptions\n")
    except Exception as e:
        f.write("Error TesseractOcrOptions:\n")
        traceback.print_exc(file=f)
