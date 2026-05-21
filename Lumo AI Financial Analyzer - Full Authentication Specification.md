# **LUMO AI FINANCIAL ANALYZER**

ĐẶC TẢ KỸ THUẬT MODULE AUTHENTICATION & SYNC PROFILE

---

**Giai đoạn:** Đồ án tốt nghiệp cao cấp (Hội đồng GS, TS, Chuyên gia AI & Tài chính)  
**Phương pháp áp dụng:** Vibecode Kit v6.0 (RRI, RRI-T, RRI-UX)

## **CHƯƠNG I: MA TRẬN ĐÁP ỨNG YÊU CẦU CHỐT (FINAL RRI MATRIX)**

Dưới đây là ma trận yêu cầu cốt lõi (REQ-IDs) đã được Chủ nhà phê duyệt, thiết kế riêng để đáp ứng các tiêu chuẩn khắt khe từ hội đồng chuyên gia tài chính và công nghệ:

| REQ-ID | Loại ưu tiên | Mô tả yêu cầu chi tiết | Giải pháp Kỹ thuật / UI-UX   |
| :---- | :---- | :---- | :---- |
| **REQ-AUTH-001** | **P0** | Đăng ký tài khoản mới bằng Email thường (không bắt buộc email trường/viện). Trạng thái mặc định sau khi ký là Unverified. | Cho phép đăng nhập thẳng vào Dashboard sau khi bấm Đăng ký thành công để tối ưu thời gian demo trước Hội đồng, không bị nghẽn ở bước chờ OTP. |
| **REQ-AUTH-002** | **P1** | Đồng bộ hóa tên người dùng đăng nhập thay thế cho placeholder "John Doe" ở Sidebar bên trái. Hướng đến đối tượng doanh nghiệp. | Hiển thị dưới dạng tên rút gọn (Ví dụ: "Học Nguyễn"). Sử dụng CSS truncate chống vỡ khung. Hover chuột sẽ hiện Tooltip chứa đầy đủ Tên \+ Chức danh doanh nghiệp. |
| **REQ-AUTH-003** | **P1** | Khi người dùng nhấn Đăng xuất (Logout), hệ thống giữ nguyên vẹn lịch sử để phục vụ tra cứu sau này. | Dữ liệu file BCTC đã bóc tách, vector embeddings của file và lịch sử chat không bị xóa mà lưu an toàn trong Database gắn với User ID. |
| **REQ-AUTH-004** | **P0** | Đảm bảo tính tối mật của dữ liệu tài chính. Cách ly hoàn toàn dữ liệu giữa các tài khoản (Tenant Isolation). | Sử dụng định dạng khóa chính UUIDv4 cho các bảng dữ liệu. Áp dụng Row-Level Security (RLS) cứng ở tầng API để chặn triệt để lỗ hổng quét IDOR. |
| **REQ-AUTH-005** | **P0** | Landing Page chỉ đóng vai trò giới thiệu tính năng, không cho phép Guest dùng thử Local LLM dở dang. | Khóa cứng luồng. Click vào bất kỳ nút trải nghiệm phân tích nào trên Landing Page đều kích hoạt chuyển hướng về Form Đăng ký/Đăng nhập. |
| **REQ-AUTH-006** | **P0** | Xử lý lỗi nhập liệu tiếng Việt có dấu, khoảng trắng hoặc ký tự đặc biệt phá vỡ logic hệ thống. | Backend thực hiện ép lowercase và trim() chuỗi Email. Trường Full Name được xử lý qua bộ lọc Sanitize nghiêm ngặt để triệt tiêu mã độc XSS. |
| **REQ-AUTH-007** | **P1** | Chặn lỗi Race Condition khi Hội đồng bấm click liên tục vào nút Submit form, và chặn tấn công dò mật khẩu. | Frontend kích hoạt trạng thái Disabled \+ hiển thị Spinner ngay sau click đầu tiên. Cấu hình Middleware chặn IP nếu vượt quá 5 lượt gửi form/phút (Rate Limiting). |
| **REQ-AUTH-008** | **P0** | Xử lý đồng bộ trạng thái an toàn trên nhiều Tab trình duyệt cùng lúc (Multi-tab Scenario). | Nếu Tab 1 bấm Đăng xuất, Tab 2 đang sinh dữ liệu phân tích từ Local LLM vẫn được phép hoàn thành và lưu vào DB của User đó, sau đó lập tức hiển thị Modal cảnh báo đăng xuất và đẩy về màn đăng nhập. |
| **REQ-AUTH-009** | **P0** | Luồng xác thực gọn nhẹ, không gây xung đột tài nguyên RAM/VRAM của máy chủ vận hành Local LLM. | Sử dụng token mã hóa mã nguồn mở JWT lưu trữ hoàn toàn trong HttpOnly Cookie để trình duyệt tự động gửi kèm, tối ưu hóa triệt để tài nguyên Client-side. |
| **REQ-AUTH-010** | **P1** | Đồng bộ hóa giao diện đổi tên real-time, không gây gián đoạn hoặc load lại mô hình AI trên trang chính. | Sử dụng thư viện quản lý trạng thái siêu nhẹ Zustand. Khi trạng thái Auth thay đổi, Sidebar lập tức cập nhật tên mà không reload ứng dụng. |
| **REQ-AUTH-011** | **P1** | Tạo sẵn tài khoản và nạp sẵn dữ liệu mẫu để rút gọn quy trình, phục vụ cho buổi chấm điểm của các Thầy trong Hội đồng. | Tạo sẵn tài khoản seed mặc định: giamkhao@lumo.ai / Pass: LumoAI@2026. Logic seed tự động quét và import toàn bộ tài liệu BCTC có trong thư mục test case. |
| **REQ-AUTH-012** | **P2** | Quản lý vòng đời tài khoản và giám sát tài nguyên tiêu hao của Local LLM trong phiên Demo. | Xây dựng thêm 1 trang Admin Dashboard riêng biệt tại đường dẫn /admin hiển thị tổng số User, danh sách file, và biểu đồ Token tiêu hao thực tế. |

## **CHƯƠNG II: BẢN VẼ KỸ THUẬT & CẤU TRÚC FILE MODULAR (TECHNICAL BLUEPRINT)**

Thợ thi công (Antigravity) bắt buộc phải tuân thủ việc phân tách module cô lập theo thiết kế dưới đây, đảm bảo tính dễ bảo trì và không làm xáo trộn các file logic,  các folder cốt lõi có sẵn của dự án:

`src/`  
`├── store/`  
`│   └── authStore.ts          # Zustand store quản lý global state (user profile, login status)`  
`├── middleware.ts             # Next.js Edge Middleware xử lý Route Guard & Rate Limiter theo IP`  
`├── app/`  
`│   ├── (auth)/               # Route Group cô lập giao diện Auth`  
`│   │   ├── login/page.tsx    # Trang Đăng nhập (Giao diện Single-Column, Center-aligned Card Layout)`  
`│   │   └── register/page.tsx # Trang Đăng ký tài khoản (Email, Full Name, Password)`  
`│   ├── admin/                # Route Quản trị hệ thống`  
`│   │   └── page.tsx          # Giao diện Admin Dashboard giám sát số lượng tài khoản & token tiêu hao`  
`│   └── api/`  
`│       ├── auth/`  
`│       │   ├── register/route.ts # API Đăng ký tài khoản: Validate đầu vào, mã hóa mật khẩu bằng bcrypt`  
`│       │   ├── login/route.ts    # API Đăng nhập: Cấp token mã hóa JWT và gán vào HttpOnly Cookie`  
`│       │   ├── logout/route.ts   # API Đăng xuất: Xóa cookie xác thực ra khỏi trình duyệt`  
`│       │   └── me/route.ts       # API Lấy thông tin phiên hiện hành dựa trên token gửi lên`  
`│       └── admin/stats/route.ts  # API Thống kê tổng hợp số liệu (User, File count, Token usage) cho Admin`  
`prisma/`  
`└── seed.ts                   # Script chạy seed dữ liệu: Tạo user giamkhao@lumo.ai và nạp dữ liệu từ thư mục 'test case'`

## **CHƯƠNG III: GÓI CHỈ THỊ CÔNG VIỆC CHUYỂN GIAO THỢ (TASK GRAPH & TIPS PACK)**

### **TIP-AUTH-001: Khởi tạo Database Schema & Giám khảo Data Seeding**

**Working Dir:** prisma/  
**Nhiệm vụ cốt lõi:** Cập nhật file schema.prisma thêm model User (id dạng UUID, email, fullName, passwordHash, role mặc định 'USER'). Map khóa ngoại từ các bảng lưu trữ báo cáo tài chính sang bảng User. Viết mã nguồn cho file seed.ts để tự động quét thư mục test case, khởi tạo tài khoản Giám khảo kèm theo toàn bộ dữ liệu phân tích mẫu đã bóc tách sẵn.  
**Kịch bản kiểm thử (Gherkin):**

`Scenario: Chạy nạp dữ liệu mẫu cho Hội đồng thành công`  
  `Given thư mục "test case" tồn tại trong mã nguồn và chứa các file phân tích BCTC mẫu`  
  `When Thợ thực thi lệnh Terminal "npx prisma db seed"`  
  `Then Tài khoản giamkhao@lumo.ai được tạo thành công với mật khẩu mã hóa an toàn`  
  `And Toàn bộ tệp phân tích mẫu được liên kết chính xác với User ID của tài khoản Giám khảo trong cơ sở dữ liệu`

### **TIP-AUTH-002: Backend API Layer, Xác thực JWT HttpOnly & Rate Limiter Middleware**

**Working Dir:** src/app/api/auth/\*, src/middleware.ts  
**Nhiệm vụ cốt lõi:** Viết logic cho API Đăng ký và Đăng nhập. Khi đăng nhập thành công, sinh token bảo mật JWT, thiết lập Header Set-Cookie với các cấu hình bắt buộc: HttpOnly, Secure, SameSite=Strict, Path=/. Cấu hình file middleware.ts bảo vệ toàn bộ các route bên trong Dashboard, đồng thời đếm số lượng request từ IP để áp dụng Rate Limiting chặn brute-force.  
**Kịch bản kiểm thử (Gherkin):**

`Scenario: Cấp phát token bảo mật HttpOnly an toàn tuyệt đối`  
  `Given người dùng gửi thông tin đăng nhập chính xác đến endpoint "/api/auth/login"`  
  `When API xử lý thông tin thành công và xác thực mật khẩu trùng khớp`  
  `Then Phản hồi trả về chứa Header Set-Cookie mang giá trị JWT mã hóa`  
  `And Cờ HttpOnly được bật (JavaScript phía client không thể đọc token - Chống tấn công XSS thành công)`

### **TIP-AUTH-003: Frontend Form UI, Zustand State Sync, Multi-tab Guard & Admin UI**

**Working Dir:** src/app/(auth)/\*, src/store/authStore.ts, Sidebar Component, src/app/admin/\*  
**Nhiệm vụ cốt lõi:** Xây dựng giao diện thẻ đăng nhập một cột tối giản, tinh tế ở chính giữa màn hình. Thiết lập Zustand store xử lý cập nhật trạng thái đăng nhập. Đồng bộ hóa Sidebar: Đọc thông tin từ store, tách lấy tên rút gọn của người dùng (Ví dụ: "Nguyễn Đại Học" thành "Học Nguyễn"), tích hợp CSS truncate và tooltip. Viết Event Listener lắng nghe biến động cookie/storage: Khi tab 1 logout, tab 2 nếu đang sinh câu trả lời AI dở dang thì đợi sinh xong, lưu vào DB, sau đó chặn hiển thị bằng Modal cảnh báo đăng xuất và đẩy về màn đăng nhập. Thiết kế trang quản trị /admin hiển thị trực quan các thông số hệ thống.  
**Kịch bản kiểm thử (Gherkin):**

`Scenario: Thay đổi nickname John Doe ở Sidebar real-time không reload trang`  
  `Given một chuyên gia doanh nghiệp vừa hoàn tất đăng nhập thành công vào hệ thống`  
  `When Zustand store ghi nhận thông tin Profile mới có tên "Nguyễn Đại Học"`  
  `Then Placeholder "John Doe" ở Sidebar lập tức chuyển thành "Học Nguyễn" mà không reload lại UI ứng dụng`  
  `And Khi rê chuột vào tên rút gọn sẽ hiển thị Tooltip đầy đủ "Nguyễn Đại Học - Chuyên gia doanh nghiệp"`  
