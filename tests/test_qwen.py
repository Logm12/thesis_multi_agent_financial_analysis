import sys
import io
from langchain_ollama import OllamaLLM

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    print("Đang khởi tạo kết nối với Ollama local model...")
    # Khởi tạo model Qwen2.5-Coder. Đảm bảo bạn đã pull model này trong ollama.
    # Cập nhật model name thành model vừa tạo từ file GGUF
    model_name = "qwen2.5-coder-thesis"
    
    try:
        llm = OllamaLLM(model=model_name)
        
        prompt = "Viết một hàm Python tính tổng hai số a và b."
        print(f"Prompt: {prompt}\n")
        print("-" * 50)
        print(f"Đang đợi phản hồi từ {model_name}...")
        
        response = llm.invoke(prompt)
        
        print("-" * 50)
        print("✅ Phản hồi từ mô hình:")
        print(response)
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Có lỗi xảy ra khi gọi Ollama: {e}")
        print("\nGợi ý khắc phục:")
        print("1. Đảm bảo Ollama đã được bật (chạy icon Ollama hoặc gõ `ollama serve` trong terminal).")
        print(f"2. Đảm bảo bạn đã pull model bằng lệnh: `ollama pull {model_name}`")

if __name__ == "__main__":
    main()
