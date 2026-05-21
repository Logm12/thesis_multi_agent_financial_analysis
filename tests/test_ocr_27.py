import sys
import os
import time

# Set PYTHONPATH to include backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from services.ocr.pdf_parser import FastPDFParser

def benchmark_first_27_pages():
    if sys.stdout.encoding != 'utf-8':
        try: sys.stdout.reconfigure(encoding='utf-8')
        except: pass

    parser = FastPDFParser()
    pdf_path = "data/test_pdfs_scanned/VNM_Q3-2025_4.pdf"

    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return

    print(f"=== BENCHMARKING FIRST 27 PAGES ===")
    print(f"File: {pdf_path}")
    
    # We will modify parser behavior dynamically or implement a 27-page limit
    # Let's inspect the first 27 pages. Since we already ran the full 63 pages, 
    # the results might be cached in Redis. If cached, it will be instantaneous.
    # To demonstrate a fresh OCR run of 27 pages without cache (or with cache if available),
    # let's run it.
    
    start_time = time.time()
    
    # Let's write a custom parse method for 27 pages to be absolutely safe and fast
    import fitz
    import numpy as np
    
    doc = fitz.open(pdf_path)
    full_text = []
    
    # Process only the first 27 pages
    pages_to_process = min(27, len(doc))
    print(f"Total pages in PDF: {len(doc)}. Processing first {pages_to_process} pages...")
    
    for page_num in range(pages_to_process):
        page = doc.load_page(page_num)
        page_text = page.get_text("text").strip()
        
        if len(page_text) < 50:
            print(f"[OCR] Page {page_num + 1}/{pages_to_process}: Scanned page detected. Running EasyOCR...")
            parser._init_ocr()
            
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.h, pix.w, pix.n))
            
            results = parser.reader.readtext(img, detail=0)
            page_text = "\n".join(results)
        else:
            print(f"[Text] Page {page_num + 1}/{pages_to_process}: Digital text detected.")
            
        full_text.append(f"## Trang {page_num + 1}\n{page_text}\n")
        
    doc.close()
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    final_output = "\n".join(full_text)
    
    # Save the output to a file for user inspection
    output_file = "first_27_pages_ocr.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_output)
        
    print(f"\n=== BENCHMARK COMPLETED ===")
    print(f"Time elapsed for {pages_to_process} pages: {elapsed:.2f} seconds")
    print(f"Average time per page: {elapsed/pages_to_process:.2f} seconds")
    print(f"Results successfully saved to: {os.path.abspath(output_file)}")
    print(f"Preview of Trang 1:\n")
    print(final_text_preview := final_output[:500])

if __name__ == "__main__":
    benchmark_first_27_pages()
