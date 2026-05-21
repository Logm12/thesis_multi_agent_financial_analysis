import requests
import os
import sys
import re

# Reconfigure stdout for Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def download_cafef_pdfs(symbol, limit=10):
    # CafeF Internal API
    api_url = f"https://cafef.vn/du-lieu/Ajax/PageNew/FileBCTC.ashx?Symbol={symbol.lower()}&Type=1&Year=0"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    print(f"--- Fetching reports for symbol: {symbol} (2020-2025) ---")
    
    try:
        response = requests.get(api_url, headers=headers)
        data = response.json()
        
        if not data.get("Success"): return

        if not os.path.exists("test_pdfs_scanned"):
            os.makedirs("test_pdfs_scanned")

        count = 0
        for report in data["Data"]:
            if count >= limit: break
            
            time_str = report.get("Time", "")
            # Filter for 2020-2025
            if not re.search(r"202[0-5]", time_str):
                continue
            
            link = report.get("Link")
            name = report.get("Name")
            
            file_name = os.path.join("test_pdfs_scanned", f"{symbol}_{time_str}_{count}.pdf".replace("/", "-"))
            
            print(f"Downloading: {name} ({time_str})...", end=" ", flush=True)
            
            pdf_res = requests.get(link)
            with open(file_name, "wb") as f:
                f.write(pdf_res.content)
            print("OK")
            count += 1

    except Exception as e:
        print(f"Error: {e}")

download_cafef_pdfs("VNM", limit=5)
