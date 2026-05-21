import fitz
from backend.services.ocr.pdf_parser import FastPDFParser

def create_minimal_pdf(path: str, text: str):
    """Utility function to create a valid minimal PDF file using fitz."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    doc.save(path)
    doc.close()

def test_redis_content_based_caching(tmp_path, mock_redis):
    """
    Scenario: Verify that FastPDFParser successfully caches PDF parsed blocks using
    SHA-256 content hashing rather than filename. Two files with identical byte content
    but different names must trigger a Cache Hit on the second run.
    """
    # 1. Create a dummy PDF file
    pdf_path_1 = tmp_path / "BCTC_VNM.pdf"
    create_minimal_pdf(str(pdf_path_1), "VNM Finance Report 2026 - Revenue is 5000 billion VND")
    
    # 2. Create another PDF file with a completely different name but identical bytes
    pdf_path_2 = tmp_path / "VNM_Report_Copy.pdf"
    with open(pdf_path_1, "rb") as f:
        pdf_bytes = f.read()
    with open(pdf_path_2, "wb") as f:
        f.write(pdf_bytes)
        
    # Ensure they have identical bytes but different paths
    assert pdf_path_1 != pdf_path_2
    assert pdf_path_1.name != pdf_path_2.name
    assert open(pdf_path_1, "rb").read() == open(pdf_path_2, "rb").read()
    
    # Initialize parser
    parser = FastPDFParser()
    
    # 3. Parse the first file (Cache Miss)
    blocks_1 = parser.parse_blocks(str(pdf_path_1))
    assert len(blocks_1) > 0
    assert any("5000" in b["text"] for b in blocks_1)
    
    # Verify that mock_redis was called to set the cache
    assert mock_redis.set.called
    
    # Reset mock call history to check the next call cleanly
    mock_redis.set.reset_mock()
    mock_redis.get.reset_mock()
    
    # 4. Parse the second file (Must trigger Cache Hit!)
    blocks_2 = parser.parse_blocks(str(pdf_path_2))
    
    # Assertions
    assert blocks_1 == blocks_2
    assert mock_redis.get.called
    # Since it is a Cache Hit, it should NOT trigger a set cache again
    assert not mock_redis.set.called
