import json
from pathlib import Path

def add_programmatic():
    dataset_path = Path("evaluation/test_dataset.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        cases = json.load(f)
        
    print(f"Current cases: {len(cases)}")
    
    # Check current Vietnamese cases (not ending in _EN)
    vi_ids = [x['id'] for x in cases if not x['id'].endswith('_EN')]
    print(f"Vietnamese cases count: {len(vi_ids)}")
    
    # We will generate TC_081 to TC_100
    missing_vi_cases = [
        {
            "id": "TC_081",
            "category": "Multi_Step_Reasoning",
            "question": "Tính tỷ số thanh toán nhanh (Quick Ratio) cuối năm 2023 của Vinamilk, biết hàng tồn kho là 5.500 tỷ đồng, tài sản ngắn hạn là 35.800 tỷ đồng và nợ ngắn hạn là 18.200 tỷ đồng?",
            "ground_truth": "Tỷ số thanh toán nhanh là 1.66 ((35.800 - 5.500) / 18.200)."
        },
        {
            "id": "TC_082",
            "category": "Multi_Step_Reasoning",
            "question": "Tính tốc độ tăng trưởng doanh thu thuần của FPT năm 2023 so với năm 2022 (biết doanh thu thuần năm 2023 là 52.618 tỷ đồng và năm 2022 là 44.005 tỷ đồng)?",
            "ground_truth": "Tốc độ tăng trưởng doanh thu thuần của FPT năm 2023 là 19.57% ((52.618 - 44.005) / 44.005 * 100)."
        },
        {
            "id": "TC_083",
            "category": "Multi_Step_Reasoning",
            "question": "Tính tỷ suất sinh lời trên vốn chủ sở hữu (ROE) năm 2023 của Vinamilk, biết LNST là 9.019 tỷ đồng và vốn chủ sở hữu bình quân là 32.500 tỷ đồng?",
            "ground_truth": "ROE của Vinamilk năm 2023 là 27.75% (9.019 / 32.500 * 100)."
        },
        {
            "id": "TC_084",
            "category": "Multi_Step_Reasoning",
            "question": "Tính biên lợi nhuận ròng (Net Profit Margin) năm 2023 của Vinamilk, biết lợi nhuận sau thuế là 9.019 tỷ đồng và doanh thu thuần là 60.369 tỷ đồng?",
            "ground_truth": "Biên lợi nhuận ròng của Vinamilk năm 2023 là 14.94% (9.019 / 60.369 * 100)."
        },
        {
            "id": "TC_085",
            "category": "Multi_Step_Reasoning",
            "question": "Tính số vòng quay hàng tồn kho (Inventory Turnover) của Vinamilk năm 2023, biết giá vốn hàng bán là 35.798 tỷ đồng và hàng tồn kho bình quân là 5.600 tỷ đồng?",
            "ground_truth": "Số vòng quay hàng tồn kho năm 2023 là 6.39 vòng (35.798 / 5.600)."
        },
        {
            "id": "TC_086",
            "category": "Multi_Step_Reasoning",
            "question": "Tính hệ số nợ trên vốn chủ sở hữu (Debt-to-Equity Ratio) cuối năm 2023 của Vinamilk, biết tổng nợ phải trả là 18.200 tỷ đồng và vốn chủ sở hữu là 32.500 tỷ đồng?",
            "ground_truth": "Hệ số nợ trên vốn chủ sở hữu cuối năm 2023 là 0.56 (18.200 / 32.500)."
        },
        {
            "id": "TC_087",
            "category": "Multi_Step_Reasoning",
            "question": "So sánh biên lợi nhuận gộp giữa FPT và Vinamilk trong năm 2023, biết doanh thu và lợi nhuận gộp của FPT lần lượt là 52.618 tỷ và 20.100 tỷ đồng; của Vinamilk là 60.369 tỷ và 24.571 tỷ đồng?",
            "ground_truth": "Biên lợi nhuận gộp FPT là 38.20%, Vinamilk là 40.70%. Vinamilk có biên lợi nhuận gộp cao hơn FPT 2.50%."
        },
        {
            "id": "TC_088",
            "category": "Multi_Step_Reasoning",
            "question": "Tính tốc độ tăng trưởng LNST của Vinamilk năm 2023 so với năm 2022, biết LNST năm 2023 là 9.019 tỷ đồng và năm 2022 là 8.578 tỷ đồng?",
            "ground_truth": "Tốc độ tăng trưởng LNST năm 2023 là 5.14% ((9.019 - 8.578) / 8.578 * 100)."
        },
        {
            "id": "TC_089",
            "category": "Multi_Step_Reasoning",
            "question": "Vẽ biểu đồ đường thể hiện doanh thu thuần của FPT trong 2 năm 2022 (44.005 tỷ) và 2023 (52.618 tỷ đồng).",
            "ground_truth": "Hệ thống phải sinh ra mã Python vẽ biểu đồ đường doanh thu thuần FPT tăng trưởng từ 44.005 tỷ lên 52.618 tỷ đồng."
        },
        {
            "id": "TC_090",
            "category": "Multi_Step_Reasoning",
            "question": "Tính tốc độ tăng trưởng kép hàng năm (CAGR) về doanh thu của FPT trong giai đoạn 2021-2023, biết doanh thu năm 2021 là 35.657 tỷ đồng và năm 2023 là 52.618 tỷ đồng?",
            "ground_truth": "CAGR doanh thu FPT giai đoạn 2021-2023 là 21.48% ((52.618 / 35.657)**(1/2) - 1)."
        },
        {
            "id": "TC_091",
            "category": "Multi_Step_Reasoning",
            "question": "Tính hệ số tự tài trợ (Equity Ratio) của Vinamilk cuối năm 2023, biết vốn chủ sở hữu là 32.500 tỷ đồng và tổng tài sản là 50.700 tỷ đồng?",
            "ground_truth": "Hệ số tự tài trợ của Vinamilk là 0.64 (32.500 / 50.700)."
        },
        {
            "id": "TC_092",
            "category": "Multi_Step_Reasoning",
            "question": "Tính tỷ suất vòng quay tài sản (Asset Turnover Ratio) năm 2023 của FPT, biết doanh thu thuần là 52.618 tỷ đồng và tổng tài sản bình quân là 45.000 tỷ đồng?",
            "ground_truth": "Tỷ suất vòng quay tài sản của FPT năm 2023 là 1.17 vòng (52.618 / 45.000)."
        },
        {
            "id": "TC_093",
            "category": "Multi_Step_Reasoning",
            "question": "Tính số ngày vòng quay hàng tồn kho (Days Inventory Outstanding) năm 2023 của Vinamilk, biết giá vốn hàng bán là 35.798 tỷ đồng và hàng tồn kho bình quân là 5.600 tỷ đồng (dùng 365 ngày)?",
            "ground_truth": "Số ngày vòng quay hàng tồn kho là 57.08 ngày (5.600 / 35.798 * 365)."
        },
        {
            "id": "TC_094",
            "category": "Multi_Step_Reasoning",
            "question": "Tính thu nhập trên mỗi cổ phiếu (EPS) của FPT năm 2023, biết lợi nhuận sau thuế của cổ đông công ty mẹ là 6.476 tỷ đồng và số lượng cổ phiếu bình quân gia quyền đang lưu hành là 1.270 triệu cổ phiếu?",
            "ground_truth": "EPS của FPT năm 2023 là 5.099 đồng/cổ phiếu (6.476 tỷ đồng / 1.270 triệu cổ phiếu)."
        },
        {
            "id": "TC_095",
            "category": "Multi_Step_Reasoning",
            "question": "Tính tỷ suất cổ tức (Dividend Yield) năm 2023 của Vinamilk, biết cổ tức bằng tiền mặt trên mỗi cổ phiếu là 3.850 đồng và giá cổ phiếu hiện tại là 68.000 đồng?",
            "ground_truth": "Tỷ suất cổ tức của Vinamilk là 5.66% (3.850 / 68.000 * 100)."
        },
        {
            "id": "TC_096",
            "category": "Multi_Step_Reasoning",
            "question": "Tính hệ số thanh toán lãi vay (Interest Coverage Ratio) năm 2023 của FPT, biết lợi nhuận trước thuế và lãi vay (EBIT) là 9.500 tỷ đồng và chi phí lãi vay là 850 tỷ đồng?",
            "ground_truth": "Hệ số thanh toán lãi vay năm 2023 của FPT là 11.18 lần (9.500 / 850)."
        },
        {
            "id": "TC_097",
            "category": "Multi_Step_Reasoning",
            "question": "Tính tốc độ tăng trưởng vốn chủ sở hữu của Vinamilk trong năm 2023 so với năm 2022, biết vốn chủ sở hữu năm 2023 là 32.500 tỷ đồng và năm 2022 là 31.800 tỷ đồng?",
            "ground_truth": "Tốc độ tăng trưởng vốn chủ sở hữu năm 2023 là 2.20% ((32.500 - 31.800) / 31.800 * 100)."
        },
        {
            "id": "TC_098",
            "category": "Multi_Step_Reasoning",
            "question": "Tính tỷ lệ đòn bẩy tài chính (Financial Leverage Multiplier) cuối năm 2023 của FPT, biết tổng tài sản là 60.000 tỷ đồng và vốn chủ sở hữu là 25.000 tỷ đồng?",
            "ground_truth": "Tỷ lệ đòn bẩy tài chính là 2.40 (60.000 / 25.000)."
        },
        {
            "id": "TC_099",
            "category": "Multi_Step_Reasoning",
            "question": "Tính số ngày phải thu khách hàng (Days Sales Outstanding) năm 2023 của Vinamilk, biết khoản phải thu bình quân là 4.200 tỷ đồng và doanh thu thuần là 60.369 tỷ đồng (dùng 365 ngày)?",
            "ground_truth": "Số ngày phải thu khách hàng năm 2023 là 25.39 ngày (4.200 / 60.369 * 365)."
        },
        {
            "id": "TC_100",
            "category": "Multi_Step_Reasoning",
            "question": "Vẽ biểu đồ cột chồng so sánh nợ ngắn hạn và nợ dài hạn năm 2023 của FPT (Nợ ngắn hạn: 22.000 tỷ, Nợ dài hạn: 3.500 tỷ) và Vinamilk (Nợ ngắn hạn: 17.600 tỷ, Nợ dài hạn: 600 tỷ).",
            "ground_truth": "Hệ thống phải sinh ra mã Python vẽ biểu đồ cột chồng so sánh nợ ngắn hạn và dài hạn của FPT và Vinamilk năm 2023."
        }
    ]
    
    # Filter out any pre-existing duplicates of these IDs
    cases = [x for x in cases if x['id'] not in [y['id'] for y in missing_vi_cases]]
    
    cases.extend(missing_vi_cases)
    print(f"Total cases after adding: {len(cases)}")
    
    # Sort
    def sort_key(x):
        idx = x['id']
        is_en = idx.endswith('_EN')
        base_num = int(idx.split('_')[1].split('_')[0]) if is_en else int(idx.split('_')[1])
        return (is_en, base_num)
        
    cases.sort(key=sort_key)
    
    with open(dataset_path, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully reached exactly {len(cases)} test cases!")

if __name__ == "__main__":
    add_programmatic()
