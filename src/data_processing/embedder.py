from langchain_huggingface import HuggingFaceEmbeddings
import torch

def get_vietnamese_embedding_model():
    """
    Khởi tạo mô hình Embedding Tiếng Việt tiên tiến và gọn nhẹ.
    Dựa trên yêu cầu: SOTA < 2026, tối ưu hóa đọc hiểu Báo cáo tài chính tiếng Việt.
    Mô hình đề xuất: 'keepitreal/vietnamese-sbert' hoặc 'bkai-foundation-models/vietnamese-bi-encoder'
    Cả hai đều cực nhẹ (chỉ tốn vài trăm MB VRAM/RAM), chạy Fast và chính xác.
    """
    
    # Chọn bkai-foundation-models/vietnamese-bi-encoder cực tốt cho tiếng Việt
    # Hoặc keepitreal/vietnamese-sbert. Tính đến ~2024-2025 thì keepitreal/vietnamese-sbert
    # và dangvantuan/vietnamese-embedding là best local models. 
    # Ở đây chọn 'keepitreal/vietnamese-sbert' làm default do nó nhỏ gọn và semantic tốt.
    model_name = "keepitreal/vietnamese-sbert"
    
    # Tự động chọn GPU nếu có, ngược lại dùng CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[Embedding] Khởi tạo model: {model_name} trên thiết bị: {device.upper()}")
    
    model_kwargs = {'device': device}
    encode_kwargs = {'normalize_embeddings': True} # Tối ưu cho Cosine Similarity

    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    
    return embeddings

def get_openai_embedding_model():
    """
    Khởi tạo OpenAI Embeddings model (text-embedding-3-small).
    Sử dụng API key từ environment.
    """
    from langchain_openai import OpenAIEmbeddings
    from config import EMBEDDING_MODEL, EMBEDDING_DIM
    
    print(f"[Embedding] Khởi tạo OpenAI model: {EMBEDDING_MODEL}")
    return OpenAIEmbeddings(model=EMBEDDING_MODEL, dimensions=EMBEDDING_DIM)

if __name__ == "__main__":
    emb = get_vietnamese_embedding_model()
    test_vec = emb.embed_query("Báo cáo tài chính FPT")
    print(f"Kích thước vector Output: {len(test_vec)}")
