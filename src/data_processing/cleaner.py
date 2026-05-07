import ftfy
import regex as re

def clean_vietnamese_text(text: str) -> str:
    """
    Chuẩn hóa và làm sạch văn bản Tiếng Việt, sử dụng Type Hints đầy đủ.
    Khắc phục các lỗi ký tự mojibake và loại bỏ khoảng trắng dư thừa.
    
    Args:
        text (str): Chuỗi văn bản thô trích xuất từ PDF.
        
    Returns:
        str: Chuỗi văn bản đã được làm sạch.
    """
    if not text:
        return ""
    
    # 1. Dùng ftfy để sửa các lỗi font/encoding (ví dụ â€œ -> ")
    text = ftfy.fix_text(text)
    
    # 2. Xóa khoảng trắng và tab dư thừa trên một dòng
    text = re.sub(r'[ \t]+', ' ', text)
    
    # 3. Chuẩn hóa số lượng ký tự xuống dòng (Không quá 2 dòng trống liên tiếp)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 4. Heuristics cho lỗi "dính chữ" do OCR (ví dụ "Tai san" bị sát vào cột Markdown)
    # Tách các chữ dính liền vào số đầu dòng nếu có (ví dụ "1Tai san" -> "1 Tai san")
    text = re.sub(r'(?<=\d)(?=[A-Z][a-z])', ' ', text)
    
    # 5. Sửa một số lỗi nhận diện sai dấu nháy của OCR (VD: duo'ng -> đương)
    text = text.replace("o'ng", "ơng").replace("u'ng", "ưng")
    
    # 6. Chuẩn hóa bảng biểu Markdown (bỏ khoảng trắng sát dấu pipe |)
    text = re.sub(r'\|\s+', '| ', text)
    text = re.sub(r'\s+\|', ' |', text)
    
    # 7. Kaizen/Poka-Yoke: Từ điển chuẩn hóa các thuật ngữ Kế toán/Tài chính hay bị RapidOCR làm mất dấu
    TERM_MAPPINGS = {
        "BAO CAO TAI CHINH": "BÁO CÁO TÀI CHÍNH",
        "BANGCAN DOI KE TOAN": "BẢNG CÂN ĐỐI KẾ TOÁN",
        "BAO CAO LUU CHUYENTIEN TE": "BÁO CÁO LƯU CHUYỂN TIỀN TỆ",
        "BAO CAO KET QUA HOAT DONG SAN XUAT KINH DOANH": "BÁO CÁO KẾT QUẢ HOẠT ĐỘNG KINH DOANH",
        "TAISANNGANHAN": "TÀI SẢN NGẮN HẠN",
        "TAISANDAIHAN": "TÀI SẢN DÀI HẠN",
        "TONGCONGTAISAN": "TỔNG CỘNG TÀI SẢN",
        "NGUON VON": "NGUỒN VỐN",
        "NOPHAITRA": "NỢ PHẢI TRẢ",
        "VONCHUSOHU'U": "VỐN CHỦ SỞ HỮU",
        "TONGCONGNGUONVON": "TỔNG CỘNG NGUỒN VỐN",
        "Lgi nhuan": "Lợi nhuận",
        "Lqi nhuan": "Lợi nhuận",
        "Lpi nhuan": "Lợi nhuận",
        "Tien va cac khoan tuong duong tien": "Tiền và các khoản tương đương tiền",
        "Tai sanco dinh": "Tài sản cố định",
        "Tai san co dinh": "Tài sản cố định",
        "Hang ton kho": "Hàng tồn kho",
        "Doanh thu": "Doanh thu",
        "Chi phi": "Chi phí",
        "So cubi quy": "Số cuối kỳ",
        "So dau nam": "Số đầu năm",
        "Thuyet minh": "Thuyết minh",
        "Luy ke tir dau nam": "Lũy kế từ đầu năm"
    }
    
    for wrong, right in TERM_MAPPINGS.items():
        # Dùng regex ignore case nhưng giữ nguyên cáse của từ gốc thì hơi phức tạp, 
        # Tạm thời replace text trực tiếp để đảm bảo Poka-Yoke chạy nhanh nhất.
        text = text.replace(wrong, right)
        # Thay thế cả version in hoa toàn bộ của RapidOCR
        text = text.replace(wrong.upper(), right.upper())
    
    return text.strip()
