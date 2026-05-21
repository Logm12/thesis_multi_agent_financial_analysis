import os
import fitz  # PyMuPDF
import numpy as np
import sys
from dotenv import load_dotenv
from core.cache import pdf_cache

# Load environment variables
load_dotenv()

class FastPDFParser:
    """
    Parser Node sử dụng PyMuPDF kết hợp OCR Fallback (EasyOCR CPU).
    Tối ưu cho máy cấu hình yếu, chạy ổn định trên Windows.
    """
    
    def __init__(self):
        self.reader = None  # Khởi tạo lazy loading để tiết kiệm RAM

    def _init_ocr(self):
        """Khởi tạo EasyOCR chỉ khi gặp trang scan."""
        if self.reader is None:
            print("[Parser] Đang khởi tạo bộ máy EasyOCR (CPU Mode)...")
            import easyocr
            # lang=['vi'] cho tiếng Việt, gpu=False để không lag máy
            self.reader = easyocr.Reader(['vi'], gpu=False)

    def parse_blocks(self, file_path: str) -> list:
        """
        Đọc PDF, trích xuất text trực tiếp (Digital) hoặc OCR (Scan).
        Kết quả trả về danh sách các blocks: {"text": str, "page": int, "bbox": str, "type": str}
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

        # 0. Check Cache using Content Hashing
        import hashlib
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            file_hash = hasher.hexdigest()
        except Exception as e:
            file_hash = hashlib.md5(file_path.encode()).hexdigest()

        cache_key = f"pdf_content_hash_{file_hash}"
        cached_content = pdf_cache.get_pdf_cache(cache_key)
        
        if cached_content:
            import json
            print(f"[Parser] Cache Hit for {file_path} (Key: {cache_key})")
            try:
                return json.loads(cached_content)
            except:
                pass

        doc = fitz.open(file_path)
        blocks = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # 1. Hybrid extraction: Tìm tables trước
            tables = page.find_tables()
            table_bboxes = []
            if tables and tables.tables:
                import pandas as pd
                for table in tables.tables:
                    bbox = table.bbox
                    table_bboxes.append(bbox)
                    df = table.to_pandas()
                    md_table = df.to_markdown(index=False)
                    if md_table:
                        blocks.append({
                            "text": md_table,
                            "page": page_num + 1,
                            "bbox": f"[{bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f}, {bbox[3]:.1f}]",
                            "type": "table"
                        })

            # 2. Phân tích text block
            page_text = page.get_text("text").strip()
            
            # 3. Logic Fallback: Nếu text quá ngắn (< 50 ký tự) và không có table, coi là bản Scan
            if len(page_text) < 50 and not table_bboxes:
                print(f"[Parser] Phát hiện bản Scan tại trang {page_num + 1}. Đang chạy OCR...")
                try:
                    self._init_ocr()
                    
                    # Chuyển trang sang ảnh (Dùng Matrix 2x để đảm bảo độ nét cho OCR)
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.h, pix.w, pix.n))
                    
                    # Chạy OCR
                    results = self.reader.readtext(img, detail=1)
                    for res in results:
                        bbox_ocr, text_ocr, prob = res
                        if text_ocr.strip():
                            # Thu nhỏ tọa độ do scale 2x
                            x0 = min(p[0] for p in bbox_ocr) / 2
                            y0 = min(p[1] for p in bbox_ocr) / 2
                            x1 = max(p[0] for p in bbox_ocr) / 2
                            y1 = max(p[1] for p in bbox_ocr) / 2
                            blocks.append({
                                "text": text_ocr.strip(),
                                "page": page_num + 1,
                                "bbox": f"[{x0:.1f}, {y0:.1f}, {x1:.1f}, {y1:.1f}]",
                                "type": "text"
                            })
                except Exception as ocr_err:
                    print(f"[Parser] Bỏ qua lỗi OCR trên trang {page_num + 1}: {str(ocr_err)}")
                    if page_text:
                        blocks.append({
                            "text": page_text,
                            "page": page_num + 1,
                            "bbox": "[0.0, 0.0, 0.0, 0.0]",
                            "type": "text"
                        })
            else:
                # Text extraction với tọa độ chuẩn
                page_dict = page.get_text("dict")
                if "blocks" in page_dict:
                    for b in page_dict["blocks"]:
                        if b.get("type") == 0:  # text block
                            bbox = b["bbox"]
                            # Bỏ qua nếu block nằm trong bảng đã parse
                            is_in_table = False
                            for tb in table_bboxes:
                                if fitz.Rect(bbox).intersects(fitz.Rect(tb)):
                                    is_in_table = True
                                    break
                            
                            if not is_in_table:
                                text = ""
                                for l in b["lines"]:
                                    for s in l["spans"]:
                                        text += s["text"] + " "
                                    text += "\n"
                                text = text.strip()
                                if text:
                                    blocks.append({
                                        "text": text,
                                        "page": page_num + 1,
                                        "bbox": f"[{bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f}, {bbox[3]:.1f}]",
                                        "type": "text"
                                    })

        doc.close()
        
        import json
        pdf_cache.set_pdf_cache(cache_key, json.dumps(blocks, ensure_ascii=False))
        
        return blocks

if __name__ == "__main__":
    import time
    if sys.stdout.encoding != 'utf-8':
        try: sys.stdout.reconfigure(encoding='utf-8')
        except: pass

    parser = FastPDFParser()
    
    # Test cases
    test_files = [
        {"name": "Digital (2008)", "path": "data/test_pdfs-VNM_CN-2008_7.pdf"},
        {"name": "Scanned (2025)", "path": "data/test_pdfs_scanned/VNM_Q3-2025_4.pdf"}
    ]

    print("=== BẮT ĐẦU BENCHMARK OCR (EASYOCR) ===")
    for test in test_files:
        path = test["path"]
        if os.path.exists(path):
            print(f"\n[Bench] Đang xử lý {test['name']}: {path}")
            start_time = time.time()
            blocks = parser.parse_blocks(path)
            end_time = time.time()
            
            # Tính toán kết quả
            process_time = end_time - start_time
            if blocks:
                preview = blocks[0]["text"][:200].replace("\n", " ")
            else:
                preview = "No text extracted."
            
            print(f"--- Kết quả {test['name']} ---")
            print(f"Thời gian: {process_time:.2f} giây")
            print(f"Tổng số blocks: {len(blocks)}")
            print(f"Preview block 1: {preview}...")
            print("-" * 30)
        else:
            print(f"[Lỗi] Không tìm thấy file test: {path}")
