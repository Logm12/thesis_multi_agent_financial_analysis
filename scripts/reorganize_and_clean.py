import os
import shutil
from pathlib import Path

def main():
    project_root = Path(__file__).parent.parent.resolve()
    print(f"[*] Project root identified as: {project_root}")

    # ==========================================
    # Phase 1: Environment Cleanup
    # ==========================================
    print("\n--- Phase 1: Environment Cleanup ---")
    
    # 1. Clean pycache and test caches recursively
    deleted_counts = {"dirs": 0, "files": 0}
    for item in project_root.rglob("*"):
        # Skip node_modules or .git directory
        if "node_modules" in item.parts or ".git" in item.parts:
            continue
            
        if item.is_dir() and item.name in ("__pycache__", ".pytest_cache", ".coverage", ".mypy_cache", ".ruff_cache"):
            try:
                shutil.rmtree(item)
                print(f"  - Deleted cache directory: {item.relative_to(project_root)}")
                deleted_counts["dirs"] += 1
            except Exception as e:
                print(f"  [!] Failed to delete cache dir {item}: {e}")
        elif item.is_file() and item.suffix in (".pyc", ".pyo", ".bak", ".log", ".tmp"):
            try:
                item.unlink()
                print(f"  - Deleted cache file: {item.relative_to(project_root)}")
                deleted_counts["files"] += 1
            except Exception as e:
                print(f"  [!] Failed to delete cache file {item}: {e}")
                
    print(f"  [+] Cleaned {deleted_counts['dirs']} cache directories and {deleted_counts['files']} cache/temp files.")

    # 2. Move root PDFs and test directories to data/
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Move root pdfs: test_pdfs-VNM_*
    for item in project_root.glob("test_pdfs-VNM_*.pdf"):
        dest = data_dir / item.name
        try:
            shutil.move(str(item), str(dest))
            print(f"  - Moved PDF: {item.name} -> data/{item.name}")
        except Exception as e:
            print(f"  [!] Failed to move {item.name}: {e}")

    # Move root pdf folders
    for folder_name in ("test_pdfs", "test_pdfs_scanned"):
        folder_path = project_root / folder_name
        if folder_path.exists() and folder_path.is_dir():
            dest = data_dir / folder_name
            if dest.exists():
                print(f"  - data/{folder_name} already exists. Merging contents...")
                for sub_item in folder_path.iterdir():
                    shutil.move(str(sub_item), str(dest / sub_item.name))
                shutil.rmtree(folder_path)
            else:
                shutil.move(str(folder_path), str(dest))
            print(f"  - Moved folder: {folder_name} -> data/{folder_name}")

    # ==========================================
    # Phase 2: Folders Setup & Reorganization
    # ==========================================
    print("\n--- Phase 2: Setup & Reorganization ---")

    # 1. Move landing-page inside frontend
    landing_page_src = project_root / "landing-page"
    frontend_dir = project_root / "frontend"
    landing_page_dest = frontend_dir / "landing-page"

    if landing_page_src.exists() and landing_page_src.is_dir():
        if landing_page_dest.exists():
            print(f"  [!] Warning: {landing_page_dest} already exists! Skipping move.")
        else:
            try:
                shutil.move(str(landing_page_src), str(landing_page_dest))
                print(f"  - Moved landing-page -> frontend/landing-page")
            except Exception as e:
                print(f"  [!] Failed to move landing-page: {e}")

    # 2. Create modular directories in backend
    backend_dir = project_root / "backend"
    core_dir = backend_dir / "core"
    services_dir = backend_dir / "services"
    rag_dir = services_dir / "rag"
    ocr_dir = services_dir / "ocr"
    tools_dir = backend_dir / "tools"
    tests_dir = project_root / "tests"

    for d in (core_dir, services_dir, rag_dir, ocr_dir, tools_dir, tests_dir):
        d.mkdir(parents=True, exist_ok=True)
        # Create __init__.py if missing to make it a package
        init_file = d / "__init__.py"
        if not init_file.exists() and d != tests_dir:
            init_file.write_text("")

    # 3. Move config.py and cache.py to core
    config_src = backend_dir / "config.py"
    config_dest = core_dir / "config.py"
    if config_src.exists():
        shutil.move(str(config_src), str(config_dest))
        print("  - Moved config.py -> backend/core/config.py")

    cache_src = backend_dir / "utils" / "cache.py"
    cache_dest = core_dir / "cache.py"
    if cache_src.exists():
        shutil.move(str(cache_src), str(cache_dest))
        print("  - Moved cache.py -> backend/core/cache.py")

    # 4. Move RAG & OCR files
    dp_dir = backend_dir / "data_processing"
    if dp_dir.exists():
        # Move RAG files
        for f_name in ("chunker.py", "cleaner.py", "embedder.py", "__init__.py"):
            f_src = dp_dir / f_name
            if f_src.exists():
                shutil.move(str(f_src), str(rag_dir / f_name))
                print(f"  - Moved RAG file: {f_name} -> backend/services/rag/{f_name}")

        # Move OCR files
        ocr_src = dp_dir / "pdf_parser.py"
        if ocr_src.exists():
            shutil.move(str(ocr_src), str(ocr_dir / "pdf_parser.py"))
            print("  - Moved OCR file: pdf_parser.py -> backend/services/ocr/pdf_parser.py")

        # Cleanup empty backend/data_processing
        try:
            shutil.rmtree(dp_dir)
            print("  - Deleted empty data_processing folder.")
        except Exception as e:
            print(f"  [!] Failed to delete data_processing: {e}")

    # Cleanup empty backend/utils
    utils_dir = backend_dir / "utils"
    if utils_dir.exists():
        try:
            shutil.rmtree(utils_dir)
            print("  - Deleted empty utils folder.")
        except Exception as e:
            print(f"  [!] Failed to delete utils: {e}")

    # 5. Move test files from scripts/ to tests/
    scripts_dir = project_root / "scripts"
    if scripts_dir.exists():
        for test_file in scripts_dir.glob("test_*.py"):
            shutil.move(str(test_file), str(tests_dir / test_file.name))
            print(f"  - Moved test file: {test_file.name} -> tests/{test_file.name}")

    print("\n[+] Folder setup & reorganization complete.")

if __name__ == "__main__":
    main()
