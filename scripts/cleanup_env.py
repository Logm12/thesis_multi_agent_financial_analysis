import os
import shutil
import sys
from pathlib import Path

def cleanup():
    # Fix console encoding
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        
    print("[*] Đang bắt đầu dọn dẹp hệ thống...")
    
    base_dir = Path(__file__).parent.parent
    
    # 1. Danh sách các thư mục cache cần xóa
    cache_dirs = [
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "__pycache__",
        "src/agents/__pycache__",
        "src/data_processing/__pycache__",
        "tests/__pycache__",
        "evaluation/__pycache__",
    ]
    
    # 2. Danh sách các file rác/temp cần xóa
    temp_files = [
        "chart.png",
        "tess_log.txt",
        "test_output.md",
        "test_router_output.txt",
        "test_router_output.txt"
    ]
    
    # Xóa thư mục cache
    for d in cache_dirs:
        dir_path = base_dir / d
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  - Đã xóa thư mục: {d}")
            
    # Xóa file temp
    for f in temp_files:
        file_path = base_dir / f
        if file_path.exists():
            file_path.unlink()
            print(f"  - Đã xóa file: {f}")
            
    # 3. Dọn dẹp thư mục tmp/ (session data)
    tmp_dir = base_dir / "tmp"
    if tmp_dir.exists():
        for item in tmp_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        print("  - Đã dọn dẹp thư mục tmp/")

    print("[+] Hoàn tất dọn dẹp môi trường.")

if __name__ == "__main__":
    cleanup()
