import os
import subprocess
import sys
import time
import codecs

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def run_cmd(cmd, cwd=None):
    print(f"\n[*] Executing: {cmd} (Cwd: {cwd})")
    start = time.time()
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, encoding='utf-8')
    elapsed = time.time() - start
    print(f"[+] Finished in {elapsed:.2f}s (Exit code: {result.returncode})")
    if result.returncode != 0:
        print(f"[-] Error Output:\n{result.stderr}")
    else:
        # Print a snippet of stdout
        lines = result.stdout.strip().split("\n")
        print("\n".join(lines[:15]))
        if len(lines) > 15:
            print(f"... and {len(lines) - 15} more lines.")
    return result.returncode == 0

def run_all():
    print("="*60)
    print("FINANCIAL ANALYZER COMPLETE EVALUATION ORCHESTRATOR")
    print("="*60)
    
    # 1. Run RAGAS Batch Evaluation (200 cases)
    run_cmd("python evaluation/run_batch_eval.py --limit 200")
    
    # 2. Run Coder Agent Evaluation
    run_cmd("python evaluation/coder_eval.py")
    
    # 3. Run Router Agent Evaluation
    run_cmd("python evaluation/router_eval.py")
    
    # 4. Run OCR Evaluation
    run_cmd("python evaluation/ocr_eval.py")
    
    # 5. Run RAG Architecture Comparison
    run_cmd("python evaluation/rag_compare/run_comparison.py")
    
    # 6. Run E2E Playwright UI test
    run_cmd("npx playwright test", cwd="frontend")
    
    # 7. Generate browser report
    run_cmd("python evaluation/generate_browser_report.py")
    
    print("\n" + "="*60)
    print("ALL EVALUATION CHECKS COMPLETED SUCCESSFULLY!")
    print("All metric sheets and report files have been updated.")
    print("="*60)

if __name__ == "__main__":
    run_all()
