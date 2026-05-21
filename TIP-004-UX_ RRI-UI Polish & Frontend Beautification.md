# **TIP-004-UX: RRI-UI POLISH & FRONTEND BEAUTIFICATION**

**DỰ ÁN:** Hệ thống Multi-Agent Phân tích Báo cáo Tài chính  
**MÃ TÁC VỤ:** TIP-004-UX (Giao diện chuẩn Chuyên gia)  
**MỨC ĐỘ ƯU TIÊN:** P0 (Critical for Presentation)  
**PHỤ THUỘC:** TIP-004 (Core Frontend Logic)  
**TRẠNG THÁI:** Sẵn sàng thi công

## ---

**1\. PHÂN BIỆN UX/UI THEO KHUNG RRI-UI (CRITIQUE)**

Để giao diện thuyết phục được các Giáo sư, Tiến sĩ và Chuyên gia đầu ngành, hệ thống không thể sử dụng giao diện Chatbot mặc định (thô sơ, thiếu chuyên nghiệp). Chúng ta cần chuyển đổi sang phong cách **Institutional Financial Terminal** (Trạm phân tích tài chính cao cấp giống Bloomberg/Refinitiv) dựa trên các nguyên tắc:

* **Eye Travel (Hướng mắt):** Giảm thiểu khoảng trống thừa, gom cụm thông tin số liệu và biểu đồ vào các thẻ (Cards) có viền sắc nét.  
* **Cognitive Load (Tải nhận thức):** BCTC có mật độ chữ và số cực dày. Giao diện phải tăng khoảng cách dòng (leading-relaxed) để không bị dính chữ tiếng Việt có dấu.  
* **Vietnamese Specific Patterns:** Các cột số tài chính phải căn phải (text-right), font chữ hệ thống phải hiển thị mượt mà không lỗi font hiển thị dấu (Khuyến nghị dùng *Inter* hoặc *SF Pro*).

## ---

**2\. CHI TIẾT TÁC VỤ CẢI TIẾN (REFURBISHMENT TASKS)**

### **2.1. Tái cấu trúc Palette màu & Typography (Enterprise Theme)**

* **Màu chủ đạo (Primary):** Deep Slate/Navy (\#0f172a) tạo cảm giác học thuật, tin cậy.  
* **Màu bổ trợ (Accent):** Emerald Green (\#10b981) cho các chỉ số tài chính dương/tăng trưởng và Rose Red (\#f43f5e) cho các chỉ số âm/rủi ro.  
* **Background:** Sử dụng màu nền xám nhẹ siêu sạch (\#f8fafc) để làm nổi bật khung PDF và khung Chat.

### **2.2. Nâng cấp Panel Chat & Markdown Renderer**

* Thay thế bong bóng chat tròn xòe mặc định bằng các khối Card vuông vắn, có shadow mờ (shadow-sm) và border mỏng (border-slate-200).  
* **Custom Table Renderer:** Bảng số liệu do Agent sinh ra hoặc trích xuất từ HTML phải có hiệu ứng Zebra-striping (dòng chẵn xám nhẹ, dòng lẻ trắng), có border rõ ràng, tiêu đề bảng (Th) viết hoa, nền xám đậm chữ trắng.  
* **Chart Container:** Biểu đồ sinh ra phải nằm trong một khung bo góc tròn, có nút "Export Data" và nút "Full Screen View".

### **2.3. Cải tiến PDF Viewer & Khung Overlay Bounding Box**

* Bọc PDF Viewer bằng một container có nền tối nhẹ để làm nổi bật trang giấy trắng.  
* **Khung đỏ Bounding Box (REQ-UI-01):** Sử dụng position: absolute với thuộc tính mix-blend-mode: multiply và màu nền đỏ nhạt trong suốt (rgba(244, 63, 94, 0.15)), viền đỏ sắc nét (border-2 border-rose-500) đè chính xác lên đoạn text/bảng.  
* Thêm hiệu ứng hoạt họa mượt mà (Fade-in) khi khung đỏ xuất hiện để thu hút sự chú ý của chuyên gia.

## ---

**3\. TIÊU CHÍ NGHIỆM THU KIỂM THỬ (QA/TESTING CRITERIA)**

| AC-ID | Kịch bản kiểm thử RRI-T (Gherkin format) | Trạng thái kỳ vọng |
| :---- | :---- | :---- |
| **AC-UX-01** | **Given** giao diện hiển thị bảng tài chính dài **When** xem trên màn hình lớn **Then** chữ tiếng Việt không bị chồng dấu, các cột số phải thẳng hàng và căn phải tuyệt đối. | Mượt mà (No wrap vỡ số) |
| **AC-UX-02** | **Given** hành động click vào Link trích dẫn **When** PDF nhảy trang và hiển thị Bounding Box **Then** vị trí khung đỏ phải bao bọc chuẩn xác 100% phần dữ liệu, không bị lệch kể cả khi zoom-in/zoom-out. | Chính xác tọa độ pixel |
| **AC-UX-03** | **Given** Agent đang trong quá trình sinh code vẽ biểu đồ nặng **When** hệ thống đang xử lý ngầm **Then** Frontend phải hiển thị một Shimmer Skeleton chuyên nghiệp thay vì icon loading xoay tròn gây cảm giác đơ lag. | Trải nghiệm liền mạch |

## ---

**4\. BIỆN LUẬN HỌC THUẬT (DÀNH CHO BUỔI BẢO VỆ)**

*Mẹo ăn điểm: Khi các GS/TS hỏi về mặt giao diện, bạn có thể biện luận: "Hệ thống áp dụng chuẩn phân phối mật độ thông tin cao (High Information Density) của các hệ thống tài chính chuyên nghiệp, giúp chuyên gia quét nhanh dữ liệu trong 3 giây (Data Scanner Persona) thay vì trải nghiệm giải trí thông thường."*