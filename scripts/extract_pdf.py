import os
import sys
import io
import time
from pathlib import Path

# Cấu hình encoding trên console Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Cập nhật đường dẫn Tesseract (như người dùng đã cung cấp)
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR"
os.environ["PATH"] += os.pathsep + TESSERACT_PATH

# Tắt tính năng tạo symlink của HuggingFace Hub (tránh lỗi WinError 1314 trên Windows không có quyền Admin)
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

try:
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.base_models import InputFormat
except ImportError:
    print("❌ Lỗi: Thư viện docling chưa được cài đặt.")
    print("Vui lòng chạy lệnh: conda run -n thesis pip install docling")
    sys.exit(1)

# Thêm đường dẫn src/ vào sys.path để có thể import từ data_processing
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data_processing.cleaner import clean_vietnamese_text


def extract_pdf_to_markdown(pdf_path: str, output_path: str) -> None:
    """
    Sử dụng Docling để trích xuất text và bảng biểu từ PDF (kể cả ảnh scan).
    Trả ra file định dạng Markdown.
    
    Args:
        pdf_path (str): Đường dẫn tới file PDF đầu vào.
        output_path (str): Đường dẫn file markdown đầu ra.
    """
    print(f"\n[INFO] Bắt đầu xử lý file: {pdf_path}")
    start_time = time.time()
    
    # Cấu hình pipeline để sử dụng OCR với Tesseract (Tiếng Việt)
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True 
    
    # Ép dùng Tesseract với ngôn ngữ Tiếng Việt thay cho RapidOCR mặc định
    try:
        from docling.datamodel.pipeline_options import TesseractCliOcrOptions, TesseractOcrOptions
        # Ưu tiên dùng CLI Ocr vì tesserocr bindings có thể lỗi C++ trên Windows
        try:
            ocr_opts = TesseractCliOcrOptions(force_full_page_ocr=True, lang=["vie", "eng"])
        except Exception:
            ocr_opts = TesseractOcrOptions(force_full_page_ocr=True, lang=["vie", "eng"])
        pipeline_options.ocr_options = ocr_opts
    except Exception as e:
        print(f"⚠️ Không cấu hình được Tesseract: {e}. Sẽ dùng OCR mặc định.")

    # Khởi tạo converter với option tương ứng
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    
    # 2. Convert từ PDF sang docling Document
    print("[INFO] Đang chạy Docling parser (có thể tốn vài phút tùy số lượng trang)...")
    try:
        doc_result = converter.convert(pdf_path)
    except Exception as e:
        print(f"❌ Lỗi khi tải docling: {e}")
        return

    # 3. Chuyển đổi qua Markdown thô
    print("[INFO] Đang xuất ra định dạng Markdown...")
    raw_md = doc_result.document.export_to_markdown()
    
    # 4. Làm sạch Tiếng Việt để chữa lỗi Mojibake (??? hay ký tự font sai lệch)
    print("[INFO] Đang làm sạch văn bản Tiếng Việt...")
    cleaned_md = clean_vietnamese_text(raw_md)
    
    # 5. Lưu kết quả
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned_md)
        
    elapsed = time.time() - start_time
    print(f"✅ Đã trích xuất xong! Kết quả lưu tại: {output_path}")
    print(f"⏱ Thời gian xử lý: {elapsed:.2f} giây")


if __name__ == "__main__":
    # Test ngay trên file mẫu của bạn
    test_pdf = r"e:\Thesis\data\raw\37d37c93_1769052195.pdf"
    test_output = r"e:\Thesis\data\processed\37d37c93_1769052195.md"
    
    if os.path.exists(test_pdf):
        extract_pdf_to_markdown(test_pdf, test_output)
    else:
        print(f"❌ Không tìm thấy file thử nghiệm: {test_pdf}")
