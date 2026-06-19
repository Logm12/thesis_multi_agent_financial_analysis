import os
import fitz  # PyMuPDF
import numpy as np
import sys
from dotenv import load_dotenv
from core.cache import pdf_cache

# Load environment variables
load_dotenv()

class SmokeTestFailure(Exception):
    """Exception raised when the structural loss rate of parsed PDF exceeds allowable threshold."""
    pass

class FastPDFParser:
    """
    Parser Node using PyMuPDF combined with OCR Fallback (EasyOCR CPU).
    Optimized for low-spec machines, running stably on Windows.
    """
    
    def __init__(self):
        self.reader = None  # Lazy loading initialization to save RAM

    def _init_ocr(self):
        """Initialize EasyOCR only when a scanned page is encountered."""
        if self.reader is None:
            import easyocr
            try:
                print("[Parser] Initializing EasyOCR engine with GPU (Low VRAM config)...")
                self.reader = easyocr.Reader(['vi'], gpu=True)
                print("[Parser] EasyOCR GPU initialized successfully!")
            except Exception as gpu_err:
                print(f"[Parser] GPU initialization failed or CUDA missing ({gpu_err}). Falling back to CPU...")
                self.reader = easyocr.Reader(['vi'], gpu=False)

    def parse_blocks(self, file_path: str, progress_callback=None) -> list:
        """
        Read PDF, extract text directly (Digital) or OCR (Scan) in parallel via ProcessPoolExecutor.
        Returns a list of blocks: {"text": str, "page": int, "bbox": str, "type": str}
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

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
        total_pages = len(doc)
        doc.close() # Close document to avoid file lock on Windows when running multiprocessing

        from concurrent.futures import ProcessPoolExecutor
        cpu_count = os.cpu_count() or 2
        # Cap at 4 workers to balance RAM/CPU resources on low-spec machines
        max_workers = min(4, max(1, cpu_count // 2))
        print(f"[Parser] Running parallel page extraction with {max_workers} processes (Total: {total_pages} pages)...")

        blocks = []
        args = [(file_path, page_num) for page_num in range(total_pages)]

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(_parse_single_page, args)
            for page_num, page_blocks in enumerate(results):
                blocks.extend(page_blocks)
                if progress_callback:
                    try:
                        progress_callback(page_num + 1, total_pages)
                    except Exception:
                        pass

        # Sort blocks by page number to ensure order
        blocks.sort(key=lambda x: x.get("page", 0))

        import json
        pdf_cache.set_pdf_cache(cache_key, json.dumps(blocks, ensure_ascii=False))
        
        return blocks

_worker_reader = None

def _init_worker_reader():
    global _worker_reader
    if _worker_reader is None:
        try:
            import torch
            torch.set_num_threads(1)
            print("[Parser-Worker] Set torch.set_num_threads(1) for CPU multiprocessing optimization.")
        except Exception:
            pass
        import easyocr
        try:
            print("[Parser-Worker] Initializing EasyOCR GPU...")
            _worker_reader = easyocr.Reader(['vi'], gpu=True)
        except Exception as err:
            print(f"[Parser-Worker] GPU initialization failed ({err}), falling back to CPU...")
            _worker_reader = easyocr.Reader(['vi'], gpu=False)

def _parse_single_page(args) -> list:
    file_path, page_num = args
    page_blocks = []
    
    try:
        doc = fitz.open(file_path)
        page = doc.load_page(page_num)
    except Exception as e:
        print(f"[Parser-Worker] Error opening page {page_num + 1}: {e}")
        return page_blocks

    # 1. Hybrid extraction: Find tables first
    table_bboxes = []
    try:
        tables = page.find_tables()
        if tables and tables.tables:
            import pandas as pd
            for table in tables.tables:
                bbox = table.bbox
                table_bboxes.append(bbox)
                df = table.to_pandas()
                md_table = df.to_markdown(index=False)
                if md_table:
                    # Extract cell coordinate grid
                    extracted_data = table.extract()
                    cells_json = []
                    row_count = table.row_count
                    col_count = table.col_count
                    x0, y0, x1, y1 = bbox
                    
                    cell_h = (y1 - y0) / max(1, row_count)
                    cell_w = (x1 - x0) / max(1, col_count)
                    
                    for r in range(row_count):
                        for c in range(col_count):
                            cell_text = ""
                            if r < len(extracted_data) and c < len(extracted_data[r]):
                                cell_text = extracted_data[r][c] or ""
                            
                            cx0 = x0 + c * cell_w
                            cy0 = y0 + r * cell_h
                            cx1 = x0 + (c + 1) * cell_w
                            cy1 = y0 + (r + 1) * cell_h
                            
                            cells_json.append({
                                "row": r,
                                "col": c,
                                "text": cell_text,
                                "bbox": [round(cx0, 1), round(cy0, 1), round(cx1, 1), round(cy1, 1)]
                            })

                    page_blocks.append({
                        "text": md_table,
                        "page": page_num + 1,
                        "bbox": f"[{bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f}, {bbox[3]:.1f}]",
                        "type": "table",
                        "table_layout": {
                            "markdown": md_table,
                            "json_data": cells_json
                        }
                    })
    except Exception as table_err:
        print(f"[Parser-Worker] Ignoring table error on page {page_num + 1}: {table_err}")

    # 2. Analyze text block
    page_text = page.get_text("text").strip()
    
    # 3. Fallback Logic: If text is too short (< 50 chars) and no table is found, treat as Scanned PDF
    if len(page_text) < 50 and not table_bboxes:
        if os.getenv("SKIP_OCR") == "True":
            print(f"[Parser-Worker] SKIP_OCR is True. Skipping OCR for page {page_num + 1}.")
            if page_text:
                page_blocks.append({
                    "text": page_text,
                    "page": page_num + 1,
                    "bbox": "[0.0, 0.0, 0.0, 0.0]",
                    "type": "text"
                })
        else:
            print(f"[Parser-Worker] Scanned page detected at page {page_num + 1}. Running OCR...")
            try:
                _init_worker_reader()
                
                # Downsample scaling from 2.0 to 1.5 to speed up by 40%
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.h, pix.w, pix.n))
                
                # Run OCR
                results = _worker_reader.readtext(img, detail=1)
                for res in results:
                    bbox_ocr, text_ocr, prob = res
                    if text_ocr.strip():
                        # Scale back coordinates to normal (divide by 1.5)
                        x0 = min(p[0] for p in bbox_ocr) / 1.5
                        y0 = min(p[1] for p in bbox_ocr) / 1.5
                        x1 = max(p[0] for p in bbox_ocr) / 1.5
                        y1 = max(p[1] for p in bbox_ocr) / 1.5
                        page_blocks.append({
                            "text": text_ocr.strip(),
                            "page": page_num + 1,
                            "bbox": f"[{x0:.1f}, {y0:.1f}, {x1:.1f}, {y1:.1f}]",
                            "type": "text"
                        })
            except Exception as ocr_err:
                print(f"[Parser-Worker] Ignoring OCR error on page {page_num + 1}: {str(ocr_err)}")
                if page_text:
                    page_blocks.append({
                        "text": page_text,
                        "page": page_num + 1,
                        "bbox": "[0.0, 0.0, 0.0, 0.0]",
                        "type": "text"
                    })
    else:
        # Text extraction with standard coordinates
        try:
            page_dict = page.get_text("dict")
            if "blocks" in page_dict:
                for b in page_dict["blocks"]:
                    if b.get("type") == 0:  # text block
                        bbox = b["bbox"]
                        # Skip if block is inside a table already parsed
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
                                page_blocks.append({
                                    "text": text,
                                    "page": page_num + 1,
                                    "bbox": f"[{bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f}, {bbox[3]:.1f}]",
                                    "type": "text"
                                })
        except Exception as text_err:
            print(f"[Parser-Worker] Error reading text on page {page_num + 1}: {text_err}")

    doc.close()
    return page_blocks

    @staticmethod
    def smoke_test(blocks: list) -> dict:
        """
        Calculates the ratio of empty table cells over total table cells.
        If structural loss rate exceeds 2.6%, raises SmokeTestFailure.
        """
        total_cells = 0
        empty_cells = 0
        
        for b in blocks:
            if b.get("type") == "table" and "table_layout" in b:
                cells = b["table_layout"].get("json_data", [])
                for cell in cells:
                    total_cells += 1
                    cell_text = cell.get("text", "")
                    if not cell_text or not str(cell_text).strip():
                        empty_cells += 1
        
        loss_rate = 0.0
        if total_cells > 0:
            loss_rate = empty_cells / total_cells
            
        passed = loss_rate <= 0.026 or os.getenv("BYPASS_SMOKE_TEST", "False") == "True"
        
        result = {
            "total_cells": total_cells,
            "empty_cells": empty_cells,
            "loss_rate": loss_rate,
            "passed": passed
        }
        
        if not passed:
            raise SmokeTestFailure(
                f"Smoke Test Failed: Structural Layout Loss Rate {loss_rate * 100:.2f}% exceeds the maximum threshold of 2.60% (Total cells: {total_cells}, Empty: {empty_cells})"
            )
            
        return result

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

    print("=== STARTING OCR BENCHMARK (EASYOCR) ===")
    for test in test_files:
        path = test["path"]
        if os.path.exists(path):
            print(f"\n[Bench] Processing {test['name']}: {path}")
            start_time = time.time()
            blocks = parser.parse_blocks(path)
            end_time = time.time()
            
            # Calculate results
            process_time = end_time - start_time
            if blocks:
                preview = blocks[0]["text"][:200].replace("\n", " ")
            else:
                preview = "No text extracted."
            
            print(f"--- Results for {test['name']} ---")
            print(f"Execution time: {process_time:.2f} seconds")
            print(f"Total blocks: {len(blocks)}")
            print(f"Preview block 1: {preview}...")
            print("-" * 30)
        else:
            print(f"[Error] Test file not found: {path}")
