import os
import datetime

def scan_directory(root_dir):
    ignore_dirs = {
        '.git', '__pycache__', 'node_modules', 'dist', '.gemini', 
        '.idea', '.vscode', 'venv', '.env_venv', 'antigravity-awesome-skills',
        'chroma_db', 'models', 'tmp', 'persistence'
    }
    ignore_files = {
        '.DS_Store', 'Thumbs.db', 'out.txt'
    }
    
    tree_lines = []
    
    def walk_tree(current_dir, prefix=""):
        try:
            items = sorted(os.listdir(current_dir))
        except Exception as e:
            return
            
        filtered_items = []
        for item in items:
            path = os.path.join(current_dir, item)
            if os.path.isdir(path):
                if item not in ignore_dirs:
                    filtered_items.append((item, True))
            else:
                if item not in ignore_files:
                    filtered_items.append((item, False))
                    
        count = len(filtered_items)
        for i, (name, is_dir) in enumerate(filtered_items):
            is_last = (i == count - 1)
            connector = "└── " if is_last else "├── "
            
            if is_dir:
                tree_lines.append(f"{prefix}{connector}📂 {name}/")
                new_prefix = prefix + ("    " if is_last else "│   ")
                walk_tree(os.path.join(current_dir, name), new_prefix)
            else:
                size = os.path.getsize(os.path.join(current_dir, name))
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size/1024:.1f} KB"
                else:
                    size_str = f"{size/(1024*1024):.1f} MB"
                tree_lines.append(f"{prefix}{connector}📄 {name} ({size_str})")

    tree_lines.append(f"📂 {os.path.basename(os.path.abspath(root_dir))}/")
    walk_tree(root_dir)
    return "\n".join(tree_lines)

def compile_all_documents():
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"[Compiler] Scanning root directory: {root_path}...")
    dir_tree = scan_directory(root_path)
    
    # Header of compilation
    compiled_content = []
    compiled_content.append("# TỔNG HỢP TOÀN BỘ TÀI LIỆU VÀ CẤU TRÚC DỰ ÁN")
    compiled_content.append(f"**Ngày cập nhật:** {current_time}")
    compiled_content.append(f"**Thư mục gốc:** `{root_path}`\n")
    compiled_content.append("---")
    
    # Section 1: Directory Tree
    compiled_content.append("## I. SƠ ĐỒ THƯ MỤC & TẬP TIN DỰ ÁN\n")
    compiled_content.append("```text")
    compiled_content.append(dir_tree)
    compiled_content.append("```\n")
    compiled_content.append("---")
    
    # Section 2: File List and description
    compiled_content.append("## II. DANH SÁCH CÁC TÀI LIỆU HƯỚNG DẪN CỐT LÕI (.MD)\n")
    compiled_content.append("Dưới đây là nội dung chi tiết của tất cả các tài liệu tài liệu định dạng Markdown (`.md`) nằm trong thư mục gốc của dự án:\n")
    
    # Find all .md files in the root folder, sorted
    md_files = [f for f in os.listdir(root_path) if f.endswith('.md') and f != 'compiled_docs.md']
    md_files.sort()
    
    for md_file in md_files:
        file_path = os.path.join(root_path, md_file)
        print(f"[Compiler] Compiling file: {md_file}...")
        
        compiled_content.append(f"### 📄 {md_file}\n")
        compiled_content.append(f"> **Đường dẫn vật lý:** `{file_path}`")
        compiled_content.append(f"> **Kích thước:** {os.path.getsize(file_path) / 1024:.2f} KB\n")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Format content properly so it stays clear
            compiled_content.append("#### NỘI DUNG TÀI LIỆU:")
            compiled_content.append("\n```markdown")
            compiled_content.append(content)
            compiled_content.append("```\n")
        except Exception as e:
            compiled_content.append(f"⚠️ *Không thể đọc nội dung file: {e}*\n")
        
        compiled_content.append("---\n")
        
    # Write everything to compiled_docs.md
    output_path = os.path.join(root_path, "compiled_docs.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(compiled_content))
        
    print(f"[Compiler] Compilation successfully written to: {output_path}")

if __name__ == "__main__":
    compile_all_documents()
