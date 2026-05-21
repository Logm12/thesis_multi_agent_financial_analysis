# SƠ ĐỒ THƯ MỤC DỰ ÁN (PROJECT DIRECTORY SCAN)

**Ngày quét:** 2026-05-18 11:21:56  
**Thư mục gốc:** `E:\Thesis`

---

## 1. Cấu trúc cây thư mục (Directory Tree)
Dưới đây là sơ đồ cấu trúc tệp tin và thư mục thực tế của dự án (đã bỏ qua các thư mục môi trường ảo và file rác hệ thống):

```text
📂 Thesis/
├── 📂 .chainlit/
│   ├── 📄 config.toml (6.0 KB)
│   └── 📂 translations/
│       ├── 📄 ar-SA.json (18.4 KB)
│       ├── 📄 bn.json (20.8 KB)
│       ├── 📄 da-DK.json (9.3 KB)
│       ├── 📄 de-DE.json (9.6 KB)
│       ├── 📄 el-GR.json (24.2 KB)
│       ├── 📄 en-US.json (8.9 KB)
│       ├── 📄 es.json (9.7 KB)
│       ├── 📄 fr-FR.json (10.2 KB)
│       ├── 📄 gu.json (18.5 KB)
│       ├── 📄 he-IL.json (15.9 KB)
│       ├── 📄 hi.json (19.5 KB)
│       ├── 📄 it.json (9.2 KB)
│       ├── 📄 ja.json (13.8 KB)
│       ├── 📄 kn.json (22.0 KB)
│       ├── 📄 ko.json (12.3 KB)
│       ├── 📄 ml.json (23.0 KB)
│       ├── 📄 mr.json (18.8 KB)
│       ├── 📄 nl.json (9.3 KB)
│       ├── 📄 pt-PT.json (9.9 KB)
│       ├── 📄 ta.json (22.3 KB)
│       ├── 📄 te.json (21.5 KB)
│       ├── 📄 zh-CN.json (10.9 KB)
│       └── 📄 zh-TW.json (11.0 KB)
├── 📄 .dockerignore (105 B)
├── 📄 .env (425 B)
├── 📄 .gitignore (911 B)
├── 📄 Dockerfile (793 B)
├── 📄 Final_QA_Checklist_Thesis_Financial_Analyzer.md (3.1 KB)
├── 📄 README.md (4.6 KB)
├── 📄 TIP-001_ Refactor Architecture & Environment Cleanup.md (4.7 KB)
├── 📄 TIP-002_ Data Pipeline Enhancement & Lazy OCR System.md (3.5 KB)
├── 📄 TIP-003_ Core Agentic System & Financial Brain.md (2.7 KB)
├── 📄 TIP-004_ Frontend Integration & Interactive Visual Grounding.md (3.1 KB)
├── 📄 VIBECODE BLUEPRINT_ Hệ thống Multi-Agent Phân tích Báo cáo Tài chính v1.0.md (5.4 KB)
├── 📂 backend/
│   ├── 📄 __init__.py (36 B)
│   ├── 📂 agents/
│   │   ├── 📄 coder.py (7.2 KB)
│   │   ├── 📄 graph.py (4.0 KB)
│   │   ├── 📄 retriever.py (2.6 KB)
│   │   ├── 📄 router.py (2.4 KB)
│   │   ├── 📄 state.py (1.1 KB)
│   │   └── 📄 synthesizer.py (3.6 KB)
│   ├── 📂 api/
│   │   ├── 📄 document.py (12.3 KB)
│   │   ├── 📄 document_store.py (2.9 KB)
│   │   ├── 📄 routes.py (1.9 KB)
│   │   ├── 📄 schemas.py (1.2 KB)
│   │   └── 📄 server.py (8.0 KB)
│   ├── 📂 core/
│   │   ├── 📄 __init__.py (0 B)
│   │   ├── 📄 cache.py (1.4 KB)
│   │   └── 📄 config.py (1.1 KB)
│   ├── 📂 legacy_chainlit/
│   │   └── 📄 app.py (6.0 KB)
│   ├── 📄 main.py (1.1 KB)
│   ├── 📂 services/
│   │   ├── 📄 __init__.py (0 B)
│   │   ├── 📂 ocr/
│   │   │   ├── 📄 __init__.py (0 B)
│   │   │   └── 📄 pdf_parser.py (6.8 KB)
│   │   └── 📂 rag/
│   │       ├── 📄 __init__.py (3 B)
│   │       ├── 📄 chunker.py (3.3 KB)
│   │       ├── 📄 cleaner.py (3.7 KB)
│   │       └── 📄 embedder.py (2.1 KB)
│   └── 📂 tools/
│       ├── 📄 __init__.py (0 B)
│       ├── 📄 finance_dict.json (6.4 KB)
│       └── 📄 sandbox.py (6.3 KB)
├── 📄 completion_report.md (7.1 KB)
├── 📄 crawl_data.py (1.6 KB)
├── 📂 data/
│   ├── 📄 Baocao_fpt_english.pdf (2.3 MB)
│   ├── 📄 FPT_BCTC.pdf (1.8 MB)
│   ├── 📄 VNM_BCTC.pdf (150.8 KB)
│   ├── 📂 chroma_db/
│   │   ├── 📂 8c241c78-3091-44d8-a66c-b9edc66bcf52/
│   │   │   ├── 📄 data_level0.bin (313.7 KB)
│   │   │   ├── 📄 header.bin (100 B)
│   │   │   ├── 📄 length.bin (400 B)
│   │   │   └── 📄 link_lists.bin (0 B)
│   │   └── 📄 chroma.sqlite3 (684.0 KB)
│   ├── 📂 persistence/
│   ├── 📂 processed/
│   │   ├── 📄 15767250-129f-4839-ba16-167472976d62.md (10.8 KB)
│   │   └── 📄 37d37c93_1769052195.md (16.5 KB)
│   ├── 📂 raw/
│   ├── 📂 test_pdfs/
│   ├── 📄 test_pdfs-VNM_CN-2008_7.pdf (653.5 KB)
│   ├── 📄 test_pdfs-VNM_CN-2008_8.pdf (1.5 MB)
│   ├── 📄 test_pdfs-VNM_CN-2008_9.pdf (671.4 KB)
│   ├── 📄 test_pdfs-VNM_CN-2009_0.pdf (600.7 KB)
│   ├── 📄 test_pdfs-VNM_CN-2009_1.pdf (509.3 KB)
│   ├── 📄 test_pdfs-VNM_Q1-2009_5.pdf (462.7 KB)
│   ├── 📄 test_pdfs-VNM_Q1-2009_6.pdf (476.6 KB)
│   ├── 📄 test_pdfs-VNM_Q2-2009_4.pdf (716.2 KB)
│   ├── 📄 test_pdfs-VNM_Q3-2009_2.pdf (514.5 KB)
│   ├── 📄 test_pdfs-VNM_Q3-2009_3.pdf (518.2 KB)
│   └── 📂 test_pdfs_scanned/
│       ├── 📄 VNM_CN-2025_0.pdf (46 B)
│       ├── 📄 VNM_CN-2025_1.pdf (46 B)
│       ├── 📄 VNM_Q3-2025_4.pdf (3.1 MB)
│       ├── 📄 VNM_Q4-2025_2.pdf (2.9 MB)
│       └── 📄 VNM_Q4-2025_3.pdf (4.0 MB)
├── 📄 directory_scan.md (14.0 KB)
├── 📄 docker-compose.yml (1.1 KB)
├── 📂 evaluation/
│   ├── 📄 benchmark_report.csv (21.6 KB)
│   ├── 📄 evaluation_results.csv (21.6 KB)
│   ├── 📄 run_batch_eval.py (7.4 KB)
│   ├── 📄 run_evaluation.py (2.9 KB)
│   └── 📄 test_dataset.json (5.5 KB)
├── 📂 frontend/
│   ├── 📄 .dockerignore (145 B)
│   ├── 📄 .gitignore (253 B)
│   ├── 📄 Dockerfile (145 B)
│   ├── 📄 Dockerfile.dev (118 B)
│   ├── 📄 README.md (2.4 KB)
│   ├── 📄 eslint.config.js (591 B)
│   ├── 📄 index.html (360 B)
│   ├── 📂 landing-page/
│   │   ├── 📄 .gitignore (253 B)
│   │   ├── 📄 README.md (2.4 KB)
│   │   ├── 📄 components.json (533 B)
│   │   ├── 📄 eslint.config.js (591 B)
│   │   ├── 📄 index.html (552 B)
│   │   ├── 📄 package-lock.json (252.5 KB)
│   │   ├── 📄 package.json (1.2 KB)
│   │   ├── 📄 postcss.config.js (80 B)
│   │   ├── 📂 public/
│   │   │   ├── 📄 favicon.svg (9.3 KB)
│   │   │   ├── 📄 icons.svg (4.9 KB)
│   │   │   └── 📂 locales/
│   │   │       ├── 📄 en.json (3.9 KB)
│   │   │       └── 📄 vi.json (4.7 KB)
│   │   ├── 📂 src/
│   │   │   ├── 📄 App.css (2.8 KB)
│   │   │   ├── 📄 App.tsx (5.8 KB)
│   │   │   ├── 📂 assets/
│   │   │   │   ├── 📄 hero.png (12.8 KB)
│   │   │   │   ├── 📄 react.svg (4.0 KB)
│   │   │   │   └── 📄 vite.svg (8.5 KB)
│   │   │   ├── 📂 components/
│   │   │   │   ├── 📂 sections/
│   │   │   │   │   ├── 📄 FooterSection.tsx (946 B)
│   │   │   │   │   ├── 📄 HeroSection.tsx (2.6 KB)
│   │   │   │   │   ├── 📄 LoginSection.tsx (6.2 KB)
│   │   │   │   │   ├── 📄 MethodologySection.tsx (9.9 KB)
│   │   │   │   │   ├── 📄 SecuritySection.tsx (3.2 KB)
│   │   │   │   │   └── 📄 VisualizerSection.tsx (16.0 KB)
│   │   │   │   └── 📂 ui/
│   │   │   │       ├── 📄 accordion.tsx (2.5 KB)
│   │   │   │       ├── 📄 button.tsx (3.1 KB)
│   │   │   │       ├── 📄 card.tsx (2.6 KB)
│   │   │   │       ├── 📄 progress.tsx (1.7 KB)
│   │   │   │       ├── 📄 switch.tsx (1.7 KB)
│   │   │   │       └── 📄 tabs.tsx (3.4 KB)
│   │   │   ├── 📄 i18n.ts (603 B)
│   │   │   ├── 📄 index.css (2.7 KB)
│   │   │   ├── 📂 lib/
│   │   │   │   ├── 📄 auth-context.tsx (1.8 KB)
│   │   │   │   └── 📄 utils.ts (166 B)
│   │   │   └── 📄 main.tsx (555 B)
│   │   ├── 📄 tailwind.config.js (1.7 KB)
│   │   ├── 📄 tsconfig.app.json (766 B)
│   │   ├── 📄 tsconfig.json (246 B)
│   │   ├── 📄 tsconfig.node.json (591 B)
│   │   └── 📄 vite.config.ts (323 B)
│   ├── 📄 package-lock.json (210.6 KB)
│   ├── 📄 package.json (1.1 KB)
│   ├── 📄 postcss.config.js (80 B)
│   ├── 📂 public/
│   │   ├── 📄 favicon.svg (9.3 KB)
│   │   └── 📄 icons.svg (4.9 KB)
│   ├── 📄 screenshot.png (76.2 KB)
│   ├── 📄 screenshot_after_upload.png (59.3 KB)
│   ├── 📂 src/
│   │   ├── 📄 App.css (2.8 KB)
│   │   ├── 📄 App.tsx (1.2 KB)
│   │   ├── 📂 api/
│   │   │   └── 📄 client.ts (538 B)
│   │   ├── 📂 assets/
│   │   │   ├── 📄 hero.png (12.8 KB)
│   │   │   ├── 📄 react.svg (4.0 KB)
│   │   │   └── 📄 vite.svg (8.5 KB)
│   │   ├── 📂 components/
│   │   │   ├── 📄 Dashboard.tsx (6.9 KB)
│   │   │   ├── 📄 DynamicChart.tsx (2.9 KB)
│   │   │   ├── 📄 Home.tsx (2.1 KB)
│   │   │   ├── 📄 KnowledgeManagement.tsx (13.5 KB)
│   │   │   ├── 📄 MainContent.tsx (13.5 KB)
│   │   │   ├── 📄 MessageBubble.tsx (10.7 KB)
│   │   │   ├── 📄 RightPanel.tsx (12.0 KB)
│   │   │   ├── 📄 Settings.tsx (6.4 KB)
│   │   │   └── 📄 Sidebar.tsx (4.0 KB)
│   │   ├── 📄 index.css (219 B)
│   │   ├── 📄 main.tsx (230 B)
│   │   ├── 📂 store/
│   │   │   └── 📄 useChatStore.ts (1.5 KB)
│   │   └── 📂 types/
│   │       └── 📄 chat.ts (328 B)
│   ├── 📄 tailwind.config.js (551 B)
│   ├── 📂 test-results/
│   │   └── 📄 .last-run.json (45 B)
│   ├── 📂 tests/
│   │   ├── 📄 chat_features.spec.ts (2.5 KB)
│   │   ├── 📄 chat_flow.spec.ts (2.4 KB)
│   │   ├── 📄 tip_003_scenarios.spec.ts (3.1 KB)
│   │   ├── 📄 tip_004_visual_grounding.spec.ts (8.4 KB)
│   │   └── 📄 upload_validation.spec.ts (4.1 KB)
│   ├── 📄 tsconfig.app.json (617 B)
│   ├── 📄 tsconfig.json (119 B)
│   ├── 📄 tsconfig.node.json (591 B)
│   ├── 📄 vercel.json (96 B)
│   └── 📄 vite.config.ts (281 B)
├── 📂 models/
│   ├── 📄 Modelfile (386 B)
│   ├── 📄 Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf (1840.5 MB)
│   └── 📂 ollama/
│       ├── 📂 blobs/
│       │   ├── 📄 sha256-32f0014400ca1c1f81e7fb5befa9b9af476ba967dcbf92bad27409228c57c5b4 (1840.5 MB)
│       │   ├── 📄 sha256-760c50ea61ea15ac88ba7dbf251cd77f2fe2b2ec8f35ecce02a16bca012ea058 (161 B)
│       │   ├── 📄 sha256-f02dd72bb2423204352eabc5637b44d79d17f109fdb510a7c51455892aa2d216 (59 B)
│       │   └── 📄 sha256-f35597882842dee1179ec0644352b38d2e114b099b135f557b4f10d022ceccf1 (413 B)
│       └── 📂 manifests/
│           └── 📂 registry.ollama.ai/
│               └── 📂 library/
│                   └── 📂 qwen2.5-coder-thesis/
│                       └── 📄 latest (825 B)
├── 📂 public/
│   └── 📄 custom.css (2.8 KB)
├── 📄 pyproject.toml (1.4 KB)
├── 📄 render.yaml (640 B)
├── 📂 reports/
│   └── 📄 TECH_STACK_REPORT.md (4.5 KB)
├── 📂 scratch/
│   ├── 📄 debug_coder.py (1.1 KB)
│   └── 📄 test_sandbox.py (749 B)
├── 📂 scripts/
│   ├── 📄 build_chromadb.py (2.1 KB)
│   ├── 📄 build_graphdb.py (3.3 KB)
│   ├── 📄 check_tess.py (778 B)
│   ├── 📄 cleanup_env.py (1.6 KB)
│   ├── 📄 extract_pdf.py (4.2 KB)
│   ├── 📄 list_available_models.py (405 B)
│   ├── 📄 reorganize_and_clean.py (6.3 KB)
│   ├── 📄 scan_dir.py (5.5 KB)
│   └── 📄 verify_tip_002.py (1.6 KB)
├── 📄 task_graph.md (753 B)
├── 📄 tech_stack.md (9.6 KB)
├── 📂 tests/
│   ├── 📄 test_chromadb.py (2.1 KB)
│   ├── 📄 test_langsmith.py (1.4 KB)
│   ├── 📄 test_ocr_27.py (2.9 KB)
│   ├── 📄 test_qwen.py (1.3 KB)
│   └── 📄 test_router.py (2.2 KB)
├── 📂 tmp/
│   ├── 📄 chart.png (47.9 KB)
│   └── 📂 demo_sess_r7p0nz2yu2c/
└── 📄 walkthrough.md (5.3 KB)
```

---

## 2. Mô tả các thành phần cốt lõi

### 📂 `backend/` (Ứng dụng Máy chủ API & AI Agents)
Thành phần trung tâm của hệ thống xử lý logic nghiệp vụ và chạy các tác tử thông minh:
*   **📂 `api/`**: Nơi chứa cấu trúc định tuyến (routes) và các endpoint API của FastAPI:
    *   📄 `server.py`: Điểm khởi chạy của máy chủ FastAPI, thiết lập cấu hình CORS và các middleware.
    *   📄 `document.py`: Quản lý các endpoint nạp PDF, kiểm tra deduplication, kiểm tra trạng thái và xóa tài liệu.
    *   📄 `document_store.py`: Tương tác lưu trữ siêu dữ liệu (metadata) của tài liệu trên hệ thống.
*   **📂 `agents/`**: Hệ thống các Agent xử lý tài chính được xây dựng trên **LangGraph**:
    *   📄 `graph.py`: Định nghĩa cấu trúc đồ thị trạng thái luồng làm việc của Multi-Agent.
    *   📄 `state.py`: Định nghĩa mô hình dữ liệu dùng chung (State) xuyên suốt đồ thị tác tử.
    *   📄 `router.py`, `retriever.py`, `coder.py`, `synthesizer.py`: Các nút tác tử chuyên biệt.
*   **📂 `data_processing/`**: Pipeline tiền xử lý văn bản báo cáo tài chính:
    *   📄 `pdf_parser.py`: Bộ máy trích xuất PDF thông minh kết hợp cơ chế OCR Fallback qua EasyOCR.
    *   📄 `cleaner.py`: Làm sạch văn bản tiếng Việt thô, chuẩn hóa khoảng trắng và ký tự lỗi.
    *   📄 `chunker.py`: Cắt văn bản thành các đoạn nhỏ dựa trên cấu trúc Markdown.
*   **📂 `utils/`**: Các công cụ tiện ích bổ trợ:
    *   📄 `cache.py`: Quản lý bộ nhớ đệm Redis cho PDF Parsing giúp tránh chạy lại OCR nhiều lần.

### 📂 `frontend/` (Giao diện Người dùng)
Ứng dụng Web trực quan cho phép người dùng giao tiếp với các Chatbot Agent và quản lý tài liệu:
*   **Vận hành bởi:** Vite + React + TypeScript + Tailwind CSS.
*   **📂 `src/`**: Chứa toàn bộ các components giao diện, trang tổng quan và hook xử lý REST API.

### 📂 `scripts/` (Công cụ Bảo trì & Thử nghiệm)
*   📄 `scan_dir.py`: Script tự động tạo sơ đồ thư mục này.
*   📄 `test_ocr_27.py`: Script benchmark thử nghiệm 27 trang của BCTC quét sử dụng EasyOCR.
*   📄 `crawl_data.py`: Crawler tự động tải báo cáo tài chính giai đoạn 2020-2025 từ nguồn CafeF.

### 📄 `tech_stack.md`
Tài liệu chỉ rõ cấu trúc công nghệ sử dụng, vị trí áp dụng và vai trò của từng thư viện trong hệ thống.
