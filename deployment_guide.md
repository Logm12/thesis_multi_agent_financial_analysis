# Hướng Dẫn Deploy Hệ Thống Multi-Agent Financial Analysis Lên Web (Demo Hội Đồng)

Tài liệu này cung cấp hướng dẫn từng bước để deploy toàn bộ hệ thống Multi-Agent phân tích báo cáo tài chính lên các nền tảng đám mây miễn phí/tiết kiệm phục vụ cho việc demo trước hội đồng bảo vệ.

---

## 📐 Kiến Trúc Deploy Tổng Quan

Hệ thống của chúng ta gồm 3 phần độc lập, được phân chia deploy như sau để tối ưu hiệu năng và chi phí:

```mermaid
graph TD
    User([Người dùng / Hội đồng]) -->|Truy cập| FE[Frontend: React Vite]
    User -->|Xem luồng Agent| CL[Developer UI: Chainlit]
    FE -->|API requests| BE[Backend: FastAPI]
    CL -->|API/Graph requests| BE
    
    subgraph Cloud Platforms
        FE ::: vercel
        CL ::: render
        BE ::: render
    end
    
    subgraph Cloud Databases
        BE --> DB[(PostgreSQL: Neon)]
        BE --> RD[(Redis: Upstash)]
    end
    
    classDef vercel fill:#000,stroke:#333,stroke-width:2px,color:#fff;
    classDef render fill:#46a39f,stroke:#2b6f6c,stroke-width:2px,color:#fff;
```

| Thành phần | Nền tảng deploy đề xuất | Lý do & Chi phí |
| :--- | :--- | :--- |
| **Frontend** ([React Vite](file:///e:/Thesis/frontend)) | **Vercel** | Free, tự động tối ưu hóa tốc độ tải trang, cấu hình rewrite sẵn sàng. |
| **Backend** ([FastAPI](file:///e:/Thesis/backend)) | **Render** hoặc **Railway** | Hỗ trợ Python tốt. Sử dụng file [render.yaml](file:///e:/Thesis/render.yaml) có sẵn. |
| **Developer UI** ([Chainlit](file:///e:/Thesis/backend/legacy_chainlit)) | **Render** | Chạy như một Web Service độc lập kết nối đến Backend chung. |
| **PostgreSQL** | **Neon.tech** | Cơ sở dữ liệu serverless Postgres miễn phí, khởi tạo trong 10 giây. |
| **Redis** | **Upstash** hoặc **Render Redis** | Redis cloud miễn phí, lý tưởng làm message queue cho LangGraph. |

---

## 🛠️ Bước 1: Khởi Tạo Cơ Sở Dữ Liệu Cloud (Postgres & Redis)

### 1. Khởi tạo PostgreSQL trên Neon.tech
1. Đăng ký/đăng nhập vào [Neon.tech](https://neon.tech/).
2. Tạo project mới và chọn khu vực gần nhất (e.g., Singapore hoặc Asia Pacific) để giảm độ trễ (latency).
3. Sau khi tạo xong, copy **Connection String** dạng:
   `postgresql://neondb_owner:password@ep-host.ap-southeast-1.aws.neon.tech/neondb?sslmode=require`
4. Lưu chuỗi này lại để đặt làm biến môi trường `POSTGRES_URL` cho Backend.

### 2. Khởi tạo Redis trên Upstash
1. Đăng nhập vào [Upstash Console](https://console.upstash.com/).
2. Chọn **Create Database**, đặt tên và chọn vùng gần nhất.
3. Sau khi tạo, sao chép URL kết nối có dạng:
   `redis://default:your_password@your_endpoint.upstash.io:6379/0`
4. Lưu URL này lại để đặt làm biến môi trường `REDIS_URL`.

---

## 🚀 Bước 2: Deploy Backend (FastAPI) Lên Render

Chúng ta sẽ điều chỉnh file [render.yaml](file:///e:/Thesis/render.yaml) để trỏ chính xác vào module `backend` (chứ không phải `src`).

### 1. Cấu hình file `render.yaml` chuẩn hóa
Dưới đây là cấu hình đã sửa đổi để chạy trực tiếp trên Render:

```yaml
services:
  - type: web
    name: financial-analyzer-backend
    env: python
    buildCommand: pip install . && pip install fastapi uvicorn gunicorn sse-starlette python-multipart redis psycopg[binary] langgraph langsmith langchain-core langchain-chroma langchain-openai langchain-text-splitters langchain-experimental openai langgraph-checkpoint-postgres
    startCommand: gunicorn backend.api.server:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHONPATH
        value: .
      - key: OPENAI_API_KEY
        sync: false
      - key: POSTGRES_URL
        sync: false
      - key: REDIS_URL
        sync: false
      - key: LANGCHAIN_TRACING_V2
        value: "true"
      - key: LANGCHAIN_API_KEY
        sync: false
```

### 2. Các bước Deploy trên Dashboard của Render:
1. Đăng nhập vào [Render.com](https://render.com/).
2. Kết nối tài khoản GitHub của bạn và chọn Repository chứa đồ án này.
3. Chọn **New** -> **Blueprint Application**. Render sẽ tự động đọc cấu hình từ file [render.yaml](file:///e:/Thesis/render.yaml).
4. Điền các giá trị thực tế cho các biến môi trường (`OPENAI_API_KEY`, `POSTGRES_URL`, `REDIS_URL`, `LANGCHAIN_API_KEY`).
5. Bấm **Apply**. Quá trình build sẽ mất khoảng 2-4 phút. Sau khi hoàn thành, Render sẽ cấp cho bạn một URL của Backend dạng:
   `https://financial-analyzer-backend.onrender.com`

---

## 🎨 Bước 3: Deploy Frontend (Vite) Lên Vercel

Sử dụng các kỹ năng tối ưu hóa Vercel, chúng ta sẽ deploy phần Client nhanh chóng.

### 1. Cấu hình môi trường trên Vercel
Khi deploy lên Vercel, bạn cần liên kết dự án vào thư mục [frontend](file:///e:/Thesis/frontend).

Sử dụng Vercel CLI từ máy cục bộ:
```bash
cd frontend
vercel login
vercel link
```

### 2. Cài đặt các biến môi trường (Environment Variables)
Đặt các biến môi trường sau trên Vercel Dashboard của dự án:
- `VITE_API_URL`: Điền URL Backend vừa tạo ở bước trước (e.g. `https://financial-analyzer-backend.onrender.com`).
- `VITE_API_BASE_URL`: Điền URL API chính (e.g. `https://financial-analyzer-backend.onrender.com/api/v1`).

### 3. Thực hiện Deploy
Chạy lệnh sau tại thư mục `frontend/` để deploy lên production:
```bash
vercel deploy --prod
```
Vercel sẽ trả về URL cho Frontend của bạn, ví dụ: `https://thesis-financial-analyzer.vercel.app`.

---

## 📊 Bước 4: Deploy Chainlit UI (Tùy Chọn Độc Lập)

Nếu bạn muốn hội đồng xem trực tiếp luồng suy nghĩ chi tiết của các Agent (Chainlit Cockpit), bạn có thể chạy thêm 1 Web Service trên Render:

1. Trên Render Dashboard, chọn **New** -> **Web Service**.
2. Liên kết đến repo GitHub hiện tại.
3. Cấu hình các thông số sau:
   - **Environment**: `Python`
   - **Build Command**: `pip install . && pip install chainlit`
   - **Start Command**: `python -m chainlit run backend/legacy_chainlit/app.py --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `POSTGRES_URL`, `REDIS_URL`, `OPENAI_API_KEY` (tương tự như Backend).
     - `PYTHONPATH`: `.`
4. Chọn gói Free hoặc Starter và bấm **Deploy**.

---

## 🧪 Quy Trình Kiểm Thử & Xác Minh (Pre-Deployment Checklist)

Trước khi thuyết trình trước hội đồng, hãy hoàn thành check-list sau để đảm bảo ứng dụng chạy mượt mà 100%:

- [ ] **Kiểm tra cơ sở dữ liệu**: Đảm bảo các bảng dữ liệu đã được migrate đầy đủ lên Neon.
- [ ] **CORS Settings**: Đảm bảo Backend FastAPI đã cho phép CORS từ tên miền Vercel của Frontend (kiểm tra cấu hình CORS trong `backend/api/server.py` hoặc thêm `*` làm Allow-Origins).
- [ ] **LLM Gateway**: Tránh sử dụng Ollama cho môi trường Cloud miễn phí trừ khi bạn chạy Ngrok từ máy cá nhân. Khuyên dùng **OpenAI API** hoặc **NVIDIA NIM API** (đã cấu hình sẵn trong `.env` của dự án).
- [ ] **Smoke Test**: Mở trình duyệt ẩn danh, truy cập trang web Vercel, thử upload một file PDF báo cáo tài chính mẫu và gửi câu hỏi tính toán để xác nhận Coder Agent hoạt động chính xác.
- [ ] **Phương án Rollback khẩn cấp**: Nếu server cloud bị quá tải (Cold Start của Render free tier có thể mất 50 giây), hãy chuẩn bị sẵn một bản demo chạy dưới Local (Docker Compose) như một phương án backup dự phòng số 1.

Chúc bạn bảo vệ luận văn thành công đạt kết quả xuất sắc!
