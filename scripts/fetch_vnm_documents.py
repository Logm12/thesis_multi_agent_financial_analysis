import os
import requests

os.makedirs("data/raw", exist_ok=True)

urls = {
    "VNM_BCTC_2023.pdf": "https://cafefnew.mediacdn.vn/Images/Uploaded/DuLieuDownload/BCTC/000691699604743083cng-ty-c-phn-sa-vit-nam27022024-180124.pdf",
    "VNM_BCTN_2023.pdf": "https://cafefnew.mediacdn.vn/Images/Uploaded/DuLieuDownload/BCTC/VNM_23CN_BCTN.pdf",
    "VNM_Q4_2023.pdf": "https://cafefnew.mediacdn.vn/Images/Uploaded/DuLieuDownload/BCTC/0014822134387351778cng-ty-c-phn-sa-vit-nam30012024-161854.pdf",
    "FPT_BCTN_2023.pdf": "https://cafefnew.mediacdn.vn/Images/Uploaded/DuLieuDownload/BCTC/FPT_23CN_BCTN.pdf"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

for name, url in urls.items():
    dest = os.path.join("data", "raw", name)
    print(f"Downloading {name} from {url}...")
    try:
        r = requests.get(url, headers=headers, stream=True)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Successfully downloaded {name} to {dest} ({os.path.getsize(dest)} bytes)")
    except Exception as e:
        print(f"Error downloading {name}: {e}")
