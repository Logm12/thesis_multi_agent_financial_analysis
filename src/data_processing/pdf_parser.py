import os
import fitz  # PyMuPDF
from dotenv import load_dotenv
from utils.cache import pdf_cache

# Load environment variables
load_dotenv()

class FastPDFParser:
    """
    Parser Node sử dụng PyMuPDF để trích xuất văn bản nhanh.
    (Đã loại bỏ Gemini theo yêu cầu của Chủ nhà)
    """
    
    def __init__(self):
        # Không còn yêu cầu API Key cho Gemini
        pass

    def parse(self, file_path: str) -> str:
        """
        Đọc PDF, trích xuất text trực tiếp.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

        # 0. Check Cache
        cached_content = pdf_cache.get_pdf_cache(file_path)
        if cached_content:
            print(f"[Parser] Cache Hit for {file_path}")
            return cached_content

        doc = fitz.open(file_path)
        full_text = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # 1. Lấy text thông thường
            page_text = page.get_text("text")
            full_text.append(f"## Trang {page_num + 1}\n")
            full_text.append(page_text)

            # Ghi chú: Xử lý hình ảnh và bảng biểu bằng AI (Gemini) đã bị gỡ bỏ.
            # Trong tương lai có thể thay thế bằng OCR engine khác nếu cần.

        doc.close()
        final_text = "\n".join(full_text)
        
        # Cache result
        pdf_cache.set_pdf_cache(file_path, final_text)
        
        return final_text

if __name__ == "__main__":
    # Fix console encoding
    import sys
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass

    parser = FastPDFParser()
    sample_pdf = r"e:\Thesis\data\raw\37d37c93_1769052195.pdf"
    if os.path.exists(sample_pdf):
        print(f"Đang xử lý: {sample_pdf}")
        result = parser.parse(sample_pdf)
        with open("parsed_result.md", "w", encoding="utf-8") as f:
            f.write(result)
        print("Xử lý hoàn tất. Kết quả lưu tại parsed_result.md")
