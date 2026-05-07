import os
import sys
import pandas as pd
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Fix console encoding for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm src vào path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from config import SYNTHESIZER_MODEL, EMBEDDING_MODEL

# Khởi tạo LLM cho RAGAS
eval_llm = ChatOpenAI(model=SYNTHESIZER_MODEL)
eval_embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

def run_ragas_evaluation():
    print("[*] Đang khởi chạy đánh giá RAGAS...")
    
    # Dataset mẫu (3 câu hỏi)
    data = {
        "question": [
            "Doanh thu thuần năm 2024 của công ty là bao nhiêu?",
            "Tầm nhìn chiến lược của công ty là gì?",
            "So sánh lợi nhuận gộp giữa năm 2024 và 2023."
        ],
        "answer": [
            "Doanh thu thuần năm 2024 đạt 500 tỷ VNĐ.",
            "Trở thành tập đoàn công nghệ tài chính hàng đầu khu vực.",
            "Lợi nhuận gộp năm 2024 tăng 15% so với năm 2023 nhờ tối ưu chi phí."
        ],
        "contexts": [
            ["Báo cáo tài chính 2024: Doanh thu thuần đạt mốc 500 tỷ VNĐ, tăng trưởng 20%."],
            ["Về tầm nhìn: Chúng tôi định hướng trở thành tập đoàn công nghệ tài chính hàng đầu khu vực vào năm 2030."],
            ["Kết quả kinh doanh: Lợi nhuận gộp năm 2024 cao hơn năm 2023 khoảng 15%."]
        ],
        "ground_truth": [
            "500 tỷ VNĐ",
            "Tập đoàn công nghệ tài chính hàng đầu khu vực",
            "Tăng 15%"
        ]
    }
    
    dataset = Dataset.from_dict(data)
    
    # Thực hiện đánh giá
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy],
        llm=eval_llm,
        embeddings=eval_embeddings
    )
    
    print("\n" + "="*30)
    print("KẾT QUẢ ĐÁNH GIÁ RAGAS")
    print("="*30)
    print(result)
    
    return result

def check_code_executability():
    """Custom metric: Kiểm tra khả năng thực thi của code mẫu."""
    print("\n[*] Đang kiểm tra Code Executability...")
    from langchain_experimental.utilities import PythonREPL
    
    test_code = """
import pandas as pd
data = {'Year': [2023, 2024], 'Revenue': [100, 120]}
df = pd.DataFrame(data)
print(df['Revenue'].mean())
"""
    repl = PythonREPL()
    output = repl.run(test_code)
    
    is_success = "110.0" in output
    print(f"  > Kết quả thực thi: {'THÀNH CÔNG' if is_success else 'THẤT BẠI'}")
    return is_success

if __name__ == "__main__":
    run_ragas_evaluation()
    check_code_executability()
