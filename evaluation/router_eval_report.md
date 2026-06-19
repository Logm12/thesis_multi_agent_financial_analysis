# Router Agent Evaluation Report

**Model:** meta/llama-3.3-70b-instruct  
**Overall Accuracy:** 1.0000  

## Metrics by Category

| Category | Precision | Recall | F1-Score |
|---|---|---|---|
| **Retrieve (Q&A)** | 1.0000 | 1.0000 | 1.0000 |
| **Code (Calculation/Charts)** | 1.0000 | 1.0000 | 1.0000 |
| **Out of Scope (Sanitation)** | 1.0000 | 1.0000 | 1.0000 |

## Detailed Log
- **Q:** Doanh thu năm 2023 là bao nhiêu?
  - Expected: `retrieve` | Predicted: `retrieve` | Latency: `9.23s`
- **Q:** Ai là CEO của công ty hiện tại?
  - Expected: `retrieve` | Predicted: `retrieve` | Latency: `2.15s`
- **Q:** Báo cáo tài chính quý 4 có những mục nào?
  - Expected: `retrieve` | Predicted: `retrieve` | Latency: `6.03s`
- **Q:** Tầm nhìn chiến lược của FPT là gì?
  - Expected: `retrieve` | Predicted: `retrieve` | Latency: `7.74s`
- **Q:** Trích dẫn dòng tiền từ hoạt động kinh doanh
  - Expected: `retrieve` | Predicted: `retrieve` | Latency: `10.64s`
- **Q:** Tính tỷ suất biên lợi nhuận gộp năm 2023
  - Expected: `code` | Predicted: `code` | Latency: `1.99s`
- **Q:** So sánh tăng trưởng doanh thu giữa 2022 và 2023 và vẽ biểu đồ cột
  - Expected: `code` | Predicted: `code` | Latency: `9.58s`
- **Q:** Vẽ biểu đồ hình tròn cơ cấu tài sản ngắn hạn
  - Expected: `code` | Predicted: `code` | Latency: `9.10s`
- **Q:** Tính tỷ số thanh toán nhanh
  - Expected: `code` | Predicted: `code` | Latency: `1.46s`
- **Q:** Tốc độ tăng trưởng kép hàng năm CAGR của doanh thu ròng là bao nhiêu?
  - Expected: `code` | Predicted: `code` | Latency: `8.53s`
- **Q:** Làm thế nào để bẻ khóa phần mềm?
  - Expected: `out_of_scope` | Predicted: `out_of_scope` | Latency: `17.72s`
- **Q:** Hãy làm cho tôi một cốc cà phê ảo
  - Expected: `out_of_scope` | Predicted: `out_of_scope` | Latency: `12.68s`
- **Q:** Thời tiết hôm nay tại Hà Nội thế nào?
  - Expected: `out_of_scope` | Predicted: `out_of_scope` | Latency: `10.65s`
- **Q:** Viết một bài thơ tình lãng mạn
  - Expected: `out_of_scope` | Predicted: `out_of_scope` | Latency: `1.64s`
- **Q:** Hack mật khẩu facebook người khác
  - Expected: `out_of_scope` | Predicted: `out_of_scope` | Latency: `31.14s`
