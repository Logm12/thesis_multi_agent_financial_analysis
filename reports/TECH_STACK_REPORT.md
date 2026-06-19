# Báo cáo Quét Thư mục & Chi tiết Tech Stack — Financial Analyzer

## 1. Cấu trúc Thư mục Thực tế (Directory Scan Report)

Dưới đây là cấu trúc thư mục và tệp tin thực tế của dự án:

```text
e:/Thesis
├── backend/                    # Backend API và hệ thống Multi-Agent (Python)
│   ├── agents/                 # Tác tử thông minh (LangGraph)
│   │   ├── graph.py            # Định nghĩa luồng StateGraph và điều phối Agents
│   │   ├── state.py            # Quản lý trạng thái AgentState
│   │   ├── router.py           # Phân loại câu hỏi từ người dùng
│   │   ├── retriever.py        # Tìm kiếm dữ liệu ngữ cảnh (Semantic Search)
│   │   ├── coder.py            # Thực thi code Python và vẽ biểu đồ phân tích
│   │   └── synthesizer.py      # Tổng hợp báo cáo phân tích tài chính cuối cùng
│   ├── api/                    # Tầng FastAPI web framework
│   │   ├── server.py           # Khởi chạy server API chính & Static files serving
│   │   ├── auth.py             # Quản lý Đăng ký, Đăng nhập và Xác thực (JWT, bcrypt)
│   │   ├── document.py         # Quản lý tải lên PDF, lập chỉ mục và truy xuất chunk
│   │   ├── document_store.py   # Quản lý lưu trữ văn bản
│   │   ├── routes.py           # Quản lý và đăng ký các APIRouter
│   │   └── schemas.py          # Xác thực dữ liệu đầu vào/đầu ra (Pydantic models)
│   ├── core/                   # Cấu hình cốt lõi và kết nối CSDL
│   │   ├── config.py           # Quản lý biến môi trường và settings hệ thống
│   │   ├── database.py         # Kết nối PostgreSQL (Cơ sở dữ liệu chính)
│   │   ├── cache.py            # Kết nối Redis (Cache cho PDF parsing & OCR)
│   │   ├── rate_limit.py       # Giới hạn tần suất yêu cầu API để tránh spam
│   │   └── schema.sql          # Thiết lập cấu trúc các bảng CSDL PostgreSQL
│   ├── services/               # Các dịch vụ nghiệp vụ chính
│   │   ├── ocr/                # Bộ phân tích PDF & OCR hybrid
│   │   │   └── pdf_parser.py   # Trích xuất dữ liệu sử dụng PyMuPDF & EasyOCR
│   │   └── rag/                # Hệ thống RAG (Retrieval-Augmented Generation)
│   │       ├── chunker.py      # Chia nhỏ tài liệu thành các block Markdown
│   │       ├── cleaner.py      # Làm sạch và chuẩn hóa văn bản Tiếng Việt
│   │       └── embedder.py     # Tạo vector nhúng cho dữ liệu tài liệu
│   ├── tools/                  # Các công cụ hỗ trợ cho Agents
│   │   ├── sandbox.py          # Python Sandbox REPL an toàn để Coder Agent chạy code
│   │   └── finance_dict.json   # Từ điển thuật ngữ tài chính mẫu
│   └── main.py                 # Điểm chạy backend chính
├── frontend/                   # Frontend SPA (React + TypeScript + Vite)
│   ├── src/                    # Mã nguồn React (components, hooks, stores, styles)
│   ├── tests/                  # Kiểm thử E2E giao diện sử dụng Playwright
│   ├── tailwind.config.js      # Cấu hình Tailwind CSS cho giao diện
│   ├── vite.config.ts          # Cấu hình đóng gói Vite
│   ├── package.json            # Thư viện và kịch bản frontend
│   └── vercel.json             # Cấu hình deploy ứng dụng lên Vercel
├── evaluation/                 # Tập dữ liệu kiểm thử và đo lường (Ragas)
├── data/                       # Chứa các tài liệu PDF báo cáo tài chính mẫu
├── reports/                    # Lưu trữ các báo cáo tài liệu kỹ thuật
├── scripts/                    # Scripts tiện ích hệ thống (migration, eval runner)
├── tests/                      # Kiểm thử tích hợp và đơn vị (Backend)
├── Dockerfile                  # Cấu hình container Docker cho Backend
├── docker-compose.yml          # Triển khai các container (App, Redis, PostgreSQL)
├── pyproject.toml              # Quản lý các dependencies backend (Poetry/Setuptools)
└── .env                        # Biến môi trường hệ thống
```

---

## 2. Chi tiết Tech Stack Thực tế

Hệ thống được phát triển trên kiến trúc **Multi-Agent & RAG** chuyên sâu phục vụ phân tích tài chính doanh nghiệp:

### 2.1. Backend & AI Framework
| Công nghệ | Vai trò trong hệ thống | Vị trí áp dụng |
| :--- | :--- | :--- |
| **Python >= 3.10** | Ngôn ngữ lập trình cốt lõi phía máy chủ. | Toàn bộ thư mục `backend/` |
| **FastAPI** | Framework API bất đồng bộ hiệu năng cao, tự động hóa tài liệu OpenAPI/Swagger. | `backend/api/` |
| **LangGraph** | Điều phối luồng làm việc tuần hoàn (Stateful Cyclic Graph) giữa các AI Agents. | `backend/agents/` |
| **LangChain Core** | Các lớp trừu tượng kết nối LLM, embeddings, và vector store. | `backend/agents/`, `backend/services/rag/` |
| **Google GenAI / OpenAI** | Cung cấp LLM cao cấp (Gemini 1.5 Flash/Pro, GPT-4o) để phân tích tài chính sâu rộng. | `backend/agents/coder.py`, `backend/agents/synthesizer.py` |
| **Python Sandbox REPL** | Môi trường sandbox Python bảo mật để thực thi code tính toán chỉ số tài chính động. | `backend/tools/sandbox.py` |

### 2.2. Xử lý Dữ liệu & OCR Pipeline (Tối ưu cho Máy cấu hình thấp)
| Công nghệ | Vai trò trong hệ thống | Vị trí áp dụng |
| :--- | :--- | :--- |
| **PyMuPDF (fitz)** | Đọc tệp PDF tốc độ cao, trích xuất text trực tiếp, phát hiện bảng dữ liệu thông minh. | `backend/services/ocr/pdf_parser.py` |
| **EasyOCR** | Thư viện OCR hỗ trợ Tiếng Việt (CPU Mode), tự động kích hoạt khi phát hiện tài liệu scan. | `backend/services/ocr/pdf_parser.py` |
| **Vietnamese Text Cleaner & Chunker** | Chuẩn hóa, loại bỏ nhiễu ký tự OCR Tiếng Việt và phân mảnh tài liệu thành cấu trúc Markdown theo trang. | `backend/services/rag/cleaner.py`, `backend/services/rag/chunker.py` |
| **Pandas & Matplotlib** | Hỗ trợ Coder Agent tính toán số liệu tài chính thô, vẽ đồ thị phân tích doanh nghiệp. | `backend/agents/coder.py`, `backend/tools/sandbox.py` |

### 2.3. Frontend (Giao diện Người dùng)
| Công nghệ | Vai trò trong hệ thống | Vị trí áp dụng |
| :--- | :--- | :--- |
| **React 19 (Vite 8)** | Giao diện Single Page App tải cực nhanh và tối ưu hóa tài nguyên. | `frontend/` |
| **TypeScript** | Đảm bảo an toàn kiểu dữ liệu chặt chẽ cho giao diện chatbot và báo cáo tài chính. | `frontend/src/` |
| **Tailwind CSS 3** | Xây dựng giao diện responsive phong cách Gemini Chat chuyên nghiệp, hiện đại. | `frontend/tailwind.config.js` |
| **Zustand 5** | Quản lý trạng thái toàn cục phía client (lịch sử chat, danh sách file, thông tin session). | `frontend/src/` |
| **Recharts 3** | Thư viện biểu đồ tương tác để trực quan hóa số liệu tài chính được sinh từ Coder Agent. | `frontend/src/` |
| **React Markdown** | Hiển thị nội dung định dạng phong phú của AI (gồm bảng số liệu và khối mã). | `frontend/src/` |

### 2.4. Lưu trữ & Bảo mật
| Công nghệ | Vai trò trong hệ thống | Vị trí áp dụng |
| :--- | :--- | :--- |
| **PostgreSQL** | Lưu trữ người dùng, hội thoại và lịch sử tương tác. | `backend/core/database.py` |
| **LangGraph Checkpointer** | Sử dụng `langgraph-checkpoint-postgres` để duy trì bền vững bộ nhớ hội thoại giữa các agent. | `backend/pyproject.toml` |
| **Redis** | Lưu trữ kết quả phân tích PDF và OCR thông qua mã băm SHA-256 của file, bỏ qua tính toán trùng lặp. | `backend/core/cache.py` |
| **ChromaDB** | Vector Database lưu trữ các đoạn văn bản nhúng phục vụ cho cơ chế tìm kiếm ngữ nghĩa RAG. | `backend/api/document_store.py` |
| **PyJWT & Bcrypt** | Mã hóa mật khẩu người dùng và quản lý phiên đăng nhập an toàn qua JSON Web Tokens. | `backend/api/auth.py` |

### 2.5. Kiểm thử & Đánh giá (QA & Evaluation)
| Công nghệ | Vai trò trong hệ thống | Vị trí áp dụng |
| :--- | :--- | :--- |
| **Ragas** | Đánh giá độ tin cậy (Faithfulness) và mức độ liên quan (Answer Relevancy) của RAG. | `evaluation/` |
| **Playwright** | Viết các kịch bản kiểm thử tự động E2E luồng đăng nhập, upload file và chat. | `frontend/tests/` |
| **Pytest** | Chạy kiểm thử tích hợp API và đơn vị cho các hàm nghiệp vụ backend. | `tests/` |

---

## 3. Luồng Hoạt động Cốt lõi & Vai trò Thành phần
- **Frontend SPA**: Cung cấp giao diện phân tích tài chính chuyên sâu, quản lý luồng hội thoại trực quan, vẽ đồ thị tương tác từ kết quả JSON nhận về qua API FastAPI.
- **FastAPI Backend Server**: Cổng API bảo mật (JWT + Rate Limiter), tiếp nhận file PDF, kiểm tra trùng lặp qua cache, đưa việc lập chỉ mục vào BackgroundTasks.
- **Hybrid PDF Parser Service**: Kiểm tra cấu trúc trang PDF. Nếu là digital, parse text/table trực tiếp bằng PyMuPDF. Nếu là bản scan, tự động kích hoạt EasyOCR. Dữ liệu sau đó được chuẩn hóa tiếng Việt, chunk và nạp vào ChromaDB.
- **Multi-Agent Orchestrator (LangGraph)**:
  - **Router Agent**: Điều hướng câu hỏi vào luồng RAG hoặc tính toán tài chính.
  - **Retriever Agent**: Truy xuất ngữ cảnh chính xác từ ChromaDB.
  - **Coder Agent**: Viết script tính toán các chỉ số tài chính (ROA, ROE, Leverage,...) và thực thi trong một Sandbox REPL an toàn để trả về kết quả số học/ảnh đồ thị.
  - **Synthesizer Agent**: Kết hợp toàn bộ dữ liệu thô, phân tích số liệu và văn bản ngữ cảnh để tổng hợp nên câu trả lời hoàn chỉnh, mạch lạc nhất gửi người dùng.
- **Database & Cache Infrastructure**: Đảm bảo các phiên chat và cấu trúc AgentState được lưu lại đầy đủ (PostgreSQL checkpointer), đồng thời giảm tải 99.9% thời gian xử lý file trùng lặp thông qua Redis Cache.
