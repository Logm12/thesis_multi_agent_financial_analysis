# Báo cáo Quét Thư mục & Chi tiết Tech Stack — Financial Analyzer

## 1. Cấu trúc Thư mục (Directory Scan Report)

Dưới đây là cấu trúc tệp tin chính của dự án sau quá trình hiện đại hóa:

```text
e:/Thesis
├── evaluation/              # Chứa dữ liệu test và kết quả đánh giá (RAGAS)
│   ├── test_dataset.json    # 20 test cases mẫu
│   └── run_batch_eval.py    # Script chạy benchmark tự động
├── src/                     # Mã nguồn chính
│   ├── agents/              # Logic AI Agents (LangGraph)
│   │   ├── graph.py         # Định nghĩa luồng StateGraph
│   │   ├── coder.py         # Agent xử lý code/vẽ biểu đồ
│   │   └── reporter.py      # Agent tổng hợp báo cáo
│   ├── api/                 # Backend FastAPI
│   │   ├── server.py        # API server & Static file serving
│   │   └── static/          # Chứa bundle React sau khi build
│   ├── ui/                  # Frontend React (Vite)
│   │   ├── src/             # Mã nguồn React (App.tsx, hooks, styles)
│   │   └── dist/            # Sản phẩm build
│   ├── utils/               # Công cụ hỗ trợ (Cache, PDF Parser)
│   └── config.py            # Cấu hình hệ thống (Paths, Env)
├── data/                    # Chứa dữ liệu PDF mẫu
├── Dockerfile               # Cấu hình Multi-stage Docker build
├── docker-compose.yml       # Orchestration (App, DB, Redis)
└── .env                     # Biến môi trường (API Keys, DB URLs)
```

---

## 2. Chi tiết Tech Stack

Hệ thống được xây dựng trên mô hình **SaaS-inspired AI Agent**, sử dụng các công nghệ hiện đại nhất:

### Backend & AI Framework
| Công nghệ | Chức năng |
| :--- | :--- |
| **Python 3.11** | Ngôn ngữ lập trình chính cho Backend và AI logic. |
| **FastAPI** | Framework hiệu năng cao để xây dựng API, hỗ trợ SSE (Server-Sent Events) cho streaming. |
| **LangGraph** | Framework quản lý trạng thái AI Agent, cho phép xây dựng luồng tư duy phức tạp (Cycle/Loop). |
| **LangChain** | Thư viện kết nối LLM, công cụ xử lý văn bản và công cụ RAG. |
| **Google GenAI (Gemini)** | Mô hình ngôn ngữ lớn (LLM) chính dùng để phân tích tài chính và tư duy. |
| **PyMuPDF** | Thư viện phân tích file PDF tốc độ cao, trích xuất text và bảng biểu. |

### Frontend (Giao diện)
| Công nghệ | Chức năng |
| :--- | :--- |
| **React (Vite)** | Thư viện UI hiện đại, đảm bảo tốc độ tải nhanh và trải nghiệm người dùng mượt mà. |
| **TypeScript** | Đảm bảo an toàn kiểu dữ liệu, giảm thiểu lỗi runtime trong quá trình phát triển. |
| **Lucide React** | Bộ icon hiện đại, tối giản theo phong cách SaaS. |
| **Vanilla CSS** | Tùy chỉnh giao diện theo phong cách Gemini (Chat A.I+) một cách linh hoạt. |
| **React Markdown** | Hiển thị câu trả lời của AI dưới dạng format Markdown, hỗ trợ bảng và code block. |

### Cơ sở hạ tầng & Lưu trữ
| Công nghệ | Chức năng |
| :--- | :--- |
| **PostgreSQL** | Cơ sở dữ liệu quan hệ, lưu trữ bền vững (Persistence) trạng thái chat và lịch sử. |
| **Redis** | In-memory database, dùng để cache kết quả parse PDF (MD5 hashing) nhằm tối ưu tốc độ. |
| **Docker & Compose** | Container hóa toàn bộ stack, đảm bảo tính nhất quán giữa môi trường dev và production. |

### Đánh giá & Kiểm thử (Testing)
| Công nghệ | Chức năng |
| :--- | :--- |
| **RAGAS** | Framework đánh giá chất lượng RAG (Faithfulness, Relevancy) dựa trên LLM. |
| **Playwright/Browser** | Tự động hóa kiểm thử trên trình duyệt (E2E Testing). |

---

## 3. Vai trò của từng thành phần
- **Frontend**: Cung cấp giao diện Gemini-style, quản lý trạng thái đăng nhập và nạp file.
- **API Server**: Cầu nối giữa UI và AI, phục vụ static files và quản lý luồng Streaming.
- **AI Agent (Graph)**: "Bộ não" của hệ thống, quyết định khi nào cần đọc PDF, khi nào cần vẽ biểu đồ hay tính toán tài chính.
- **Infrastructure**: Đảm bảo dữ liệu không bị mất sau khi restart và tăng tốc độ xử lý các file đã từng nạp.
