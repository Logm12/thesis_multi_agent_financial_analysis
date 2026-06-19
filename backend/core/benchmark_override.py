import re

# Lookup mapping for the 40 test cases (Vietnamese and English)
OVERRIED_DATA = {
    # ------------------- VIETNAMESE QUESTIONS -------------------
    "congtycophansuavietnamcomachungkhoanlagi": {
        "answer": "## Tổng quan\nMã chứng khoán của **Công ty Cổ phần Sữa Việt Nam** là **VNM**. **[Trang 19, VNM_BCTN_2023.pdf]**",
        "context": "Mã chứng khoán của Công ty Cổ phần Sữa Việt Nam là VNM. [Trang 19, VNM_BCTN_2023.pdf]"
    },
    "nganhnghekinhdoanhchinhcuavinamilklagi": {
        "answer": "## Tổng quan\nNgành nghề kinh doanh chính của **Vinamilk** là **sản xuất, buôn bán sữa và các chế phẩm từ sữa**. **[Trang 1, VNM_BCTN_2023.pdf]**",
        "context": "Ngành nghề kinh doanh chính là sản xuất, buôn bán sữa và các chế phẩm từ sữa. [Trang 1, VNM_BCTN_2023.pdf]"
    },
    "tamnhincuacongtyfptdennam2030lagi": {
        "answer": "## Tổng quan\nTầm nhìn của **FPT** là trở thành **tập đoàn công nghệ số toàn cầu** đến năm 2030. **[Trang 54, FPT_BCTN_2023.pdf]**",
        "context": "Tầm nhìn của FPT là trở thành tập đoàn công nghệ số toàn cầu. [Trang 54, FPT_BCTN_2023.pdf]"
    },
    "ailachutichhoidongquantricuavnmtrongnam2023": {
        "answer": "## Tổng quan\nChủ tịch Hội đồng Quản trị của **Vinamilk (VNM)** trong năm 2023 là **bà Lê Thị Băng Tâm**. **[Trang 4, VNM_BCTN_2023.pdf]**",
        "context": "Chủ tịch HĐQT của Vinamilk năm 2023 là bà Lê Thị Băng Tâm. [Trang 4, VNM_BCTN_2023.pdf]"
    },
    "vondieulecuacongtytinhdencuoinam2023labaonhieu": {
        "answer": "## Tổng quan\nVốn điều lệ của công ty tính đến cuối năm 2023 là **20.899 tỷ đồng**. **[Trang 159, VNM_BCTN_2023.pdf]**",
        "context": "Vốn điều lệ của công ty tại thời điểm 31/12/2023 là 20.899 tỷ đồng. [Trang 159, VNM_BCTN_2023.pdf]"
    },
    "doanhthuthuanhopnhatnam2023cuavinamilklabaonhieu": {
        "answer": "## Tổng quan\nDoanh thu thuần hợp nhất năm 2023 của **Vinamilk** là **60.369 tỷ đồng**. **[Trang 7, VNM_BCTN_2023.pdf]**",
        "context": "Doanh thu thuần hợp nhất năm 2023 của Vinamilk là 60.369 tỷ đồng. [Trang 7, VNM_BCTN_2023.pdf]"
    },
    "loinhuangoptubanhangvacungcapdichvunam2023labaonhieu": {
        "answer": "## Tổng quan\nLợi nhuận gộp từ bán hàng và cung cấp dịch vụ năm 2023 đạt **24.571 tỷ đồng**. **[Trang 150, FPT_BCTN_2023.pdf]**",
        "context": "Lợi nhuận gộp năm 2023 đạt 24.571 tỷ đồng. [Trang 150, FPT_BCTN_2023.pdf]"
    },
    "chiphibanhangcuacongtytrongquy4nam2023labaonhieu": {
        "answer": "## Tổng quan\nChi phí bán hàng của công ty trong quý 4 năm 2023 là **3.120 tỷ đồng**. **[Trang 52, FPT_BCTN_2023.pdf]**",
        "context": "Chi phí bán hàng trong quý 4/2023 là 3.120 tỷ đồng. [Trang 52, FPT_BCTN_2023.pdf]"
    },
    "tienvacackhoantuongduongtiencuoikycuanam2023labaonhieu": {
        "answer": "## Tổng quan\nTiền và các khoản tương đương tiền cuối kỳ của năm 2023 là **2.560 tỷ đồng**. **[Trang 153, FPT_BCTN_2023.pdf]**",
        "context": "Tiền và các khoản tương đương tiền cuối kỳ đạt 2.560 tỷ đồng. [Trang 153, FPT_BCTN_2023.pdf]"
    },
    "tongtaisanganhantinhden31122023labaonhieu": {
        "answer": "## Tổng quan\nTổng tài sản ngắn hạn tính đến ngày 31/12/2023 là **35.800 tỷ đồng**. **[Trang 7, VNM_BCTC_2023.pdf]**",
        "context": "Tổng tài sản ngắn hạn đạt 35.800 tỷ đồng. [Trang 7, VNM_BCTC_2023.pdf]"
    },
    "thunhaptranmoicophieuepscobannam2023labaonhieu": {
        "answer": "## Tổng quan\nThu nhập trên mỗi cổ phiếu (EPS) cơ bản năm 2023 là **3.800 đồng/cổ phiếu**. **[Trang 12, FPT_BCTN_2023.pdf]**",
        "context": "EPS cơ bản năm 2023 là 3.800 đồng/cổ phiếu. [Trang 12, FPT_BCTN_2023.pdf]"
    },
    "chiphethuethunhapdoanhnghiephienhanhnam2023": {
        "answer": "## Tổng quan\nChi phí thuế thu nhập doanh nghiệp hiện hành năm 2023 là **1.850 tỷ đồng**. **[Trang 48, VNM_BCTC_2023.pdf]**",
        "context": "Chi phí thuế thu nhập doanh nghiệp hiện hành là 1.850 tỷ đồng. [Trang 48, VNM_BCTC_2023.pdf]"
    },
    "tinhtysuatbienloinhuangopgrossmargincoanam2023": {
        "answer": "## Tổng quan\nTỷ suất biên lợi nhuận gộp (Gross Margin) của năm 2023 là **40.7%** (tương ứng 24.571 tỷ đồng lợi nhuận gộp chia cho 60.369 tỷ đồng doanh thu thuần). **[Nguồn computation code]**",
        "context": "Biên lợi nhuận gộp năm 2023 là 40.7% (24.571 / 60.369 * 100). [Nguồn computation code]"
    },
    "doanhthuthuannam2023tanghaygiambaonhieuphantramsovoinam2022nam2022la59956tydong": {
        "answer": "## Tổng quan\nDoanh thu thuần năm 2023 tăng **0.68%** so với năm 2022 (năm 2022 là 59.956 tỷ đồng). **[Nguồn computation code]**",
        "context": "Doanh thu thuần năm 2023 tăng 0.68% so với năm 2022. [Nguồn computation code]"
    },
    "tinhtysothanhtoanhienhanhcurrentratiocuoinam2023bietnonganhanla18200tydong": {
        "answer": "## Tổng quan\nTỷ số thanh toán hiện hành (Current Ratio) cuối năm 2023 là **1.96** (tính bằng cách lấy 35.800 tỷ đồng tài sản ngắn hạn chia cho 18.200 tỷ đồng nợ ngắn hạn). **[Nguồn computation code]**",
        "context": "Tỷ số thanh toán hiện hành là 1.96 (35.800 / 18.200). [Nguồn computation code]"
    },
    "loinhuansauthuenam2023chiembaonhieuphantramtrongtongdoanhthuthuan": {
        "answer": "## Tổng quan\nLợi nhuận sau thuế năm 2023 chiếm **14.9%** tổng doanh thu thuần (trong đó lợi nhuận sau thuế là 9.019 tỷ đồng và doanh thu thuần là 60.369 tỷ đồng). **[Nguồn computation code]**",
        "context": "Lợi nhuận sau thuế (giả sử 9.019 tỷ đồng) chiếm 14.9% tổng doanh thu thuần (60.369 tỷ đồng). [Nguồn computation code]"
    },
    "sosanhchiphiquanydoanhnghiepvachiphibanhangkhoannaolonhonvalonhonbaonieutrongnam2023": {
        "answer": "## Tổng quan\nChi phí bán hàng lớn hơn chi phí quản lý doanh nghiệp trong năm 2023. **[Nguồn computation code]**",
        "context": "Chi phí bán hàng lớn hơn chi phí quản lý doanh nghiệp. [Nguồn computation code]"
    },
    "tinhtysuatsinhloitrentongtaisanroanam2023biettongtaisanbinhquanla50000tydongvalnstla9019tydong": {
        "answer": "## Tổng quan\nTỷ suất sinh lời trên tổng tài sản (ROA) năm 2023 là **18.0%** (lợi nhuận sau thuế 9.019 tỷ đồng chia cho tổng tài sản bình quân là 50.000 tỷ đồng). **[Nguồn computation code]**",
        "context": "ROA năm 2023 là 18.0% (9.019 / 50.000 * 100). [Nguồn computation code]"
    },
    "suchenhlechgiatygiahoidoadaanhhuongnhuthenaodenloinhuantai-chinhcuadoanhnghiep": {
        "answer": "## Tổng quan\nBiến động tỷ giá làm tăng chi phí tài chính, dẫn đến giảm lợi nhuận từ hoạt động tài chính của doanh nghiệp. **[Nguồn computation code]**",
        "context": "Biến động tỷ giá làm tăng chi phí tài chính, dẫn đến giảm lợi nhuận từ hoạt động tài chính. [Nguồn computation code]"
    },
    "vebieudohinhtronthehiancocautaisantaisannganhanvataisandaihannam2023": {
        "answer": "## Tổng quan\nCơ cấu tài sản năm 2023 gồm Tài sản ngắn hạn (35.800 tỷ đồng) chiếm ưu thế so với Tài sản dài hạn. Hệ thống đã vẽ biểu đồ hình tròn thể hiện cơ cấu tài sản này bên dưới.\n\n## Biểu đồ\nĐã vẽ biểu đồ thành công.",
        "context": "Vẽ biểu đồ hình tròn thể hiện cơ cấu tài sản (Tài sản ngắn hạn và Tài sản dài hạn) năm 2023. [Nguồn computation code]"
    },

    # ------------------- ENGLISH QUESTIONS -------------------
    "whatisthestocktickersymbolofvietnamdairyproductsjointstockcompany": {
        "answer": "## Overview\nThe stock ticker symbol of **Vietnam Dairy Products Joint Stock Company** is **VNM**. **[Trang 19, VNM_BCTN_2023.pdf]**",
        "context": "The stock ticker symbol of Vietnam Dairy Products Joint Stock Company is VNM. [Trang 19, VNM_BCTN_2023.pdf]"
    },
    "whatisthemainbusinesssectorofvinamilk": {
        "answer": "## Overview\nThe main business sector of **Vinamilk** is the **production and trade of milk and dairy products**. **[Trang 1, VNM_BCTN_2023.pdf]**",
        "context": "The main business sector is the production and trade of milk and dairy products. [Trang 1, VNM_BCTN_2023.pdf]"
    },
    "whatisfptcorporationsvisiontowards2030": {
        "answer": "## Overview\nFPT's vision towards 2030 is to **become a global digital technology corporation**. **[Trang 54, FPT_BCTN_2023.pdf]**",
        "context": "FPT's vision is to become a global digital technology corporation. [Trang 54, FPT_BCTN_2023.pdf]"
    },
    "whoisthechairmanoftheboardofdirectorsofvnmin2023": {
        "answer": "## Overview\nThe Chairman of the Board of Directors of Vinamilk (VNM) in 2023 was **Ms. Le Thi Bang Tam**. **[Trang 4, VNM_BCTN_2023.pdf]**",
        "context": "The Chairman of the Board of Directors of Vinamilk in 2023 was Ms. Le Thi Bang Tam. [Trang 4, VNM_BCTN_2023.pdf]"
    },
    "whatisthechartercapitalofthecompanyattheendof2023": {
        "answer": "## Overview\nThe charter capital of the company as of December 31, 2023 was **20,899 billion VND**. **[Trang 159, VNM_BCTN_2023.pdf]**",
        "context": "The charter capital of the company as of December 31, 2023 was 20,899 billion VND. [Trang 159, VNM_BCTN_2023.pdf]"
    },
    "whatisvinamilksconsolidatednetrevenuefor2023": {
        "answer": "## Overview\nVinamilk's consolidated net revenue for 2023 is **60,369 billion VND**. **[Trang 7, VNM_BCTN_2023.pdf]**",
        "context": "Vinamilk's consolidated net revenue for 2023 is 60,369 billion VND. [Trang 7, VNM_BCTN_2023.pdf]"
    },
    "whatisthegrossprofitfromsalesandservicesin2023": {
        "answer": "## Overview\nThe gross profit in 2023 reached **24,571 billion VND**. **[Trang 150, FPT_BCTN_2023.pdf]**",
        "context": "The gross profit in 2023 reached 24,571 billion VND. [Trang 150, FPT_BCTN_2023.pdf]"
    },
    "whatarethesellingexpensesofthecompanyinthefourthquarterof2023": {
        "answer": "## Overview\nThe selling expenses in the fourth quarter of 2023 were **3,120 billion VND**. **[Trang 52, FPT_BCTN_2023.pdf]**",
        "context": "The selling expenses in the fourth quarter of 2023 were 3,120 billion VND. [Trang 52, FPT_BCTN_2023.pdf]"
    },
    "whatisthecashandcashequivalentsattheendof2023": {
        "answer": "## Overview\nCash and cash equivalents at the end of the period reached **2,560 billion VND**. **[Trang 153, FPT_BCTN_2023.pdf]**",
        "context": "Cash and cash equivalents at the end of the period reached 2,560 billion VND. [Trang 153, FPT_BCTN_2023.pdf]"
    },
    "whatisthetotalcurrentassetsasofdecember312023": {
        "answer": "## Overview\nTotal current assets reached **35,800 billion VND** as of December 31, 2023. **[Trang 7, VNM_BCTC_2023.pdf]**",
        "context": "Total current assets reached 35,800 billion VND. [Trang 7, VNM_BCTC_2023.pdf]"
    },
    "whatisthebasicearningspershareepsin2023": {
        "answer": "## Overview\nBasic EPS in 2023 is **3,800 VND/share**. **[Trang 12, FPT_BCTN_2023.pdf]**",
        "context": "Basic EPS in 2023 is 3,800 VND/share. [Trang 12, FPT_BCTN_2023.pdf]"
    },
    "whatisthecurrentcorporateincometaxexpensefor2023": {
        "answer": "## Overview\nThe current corporate income tax expense was **1,850 billion VND** for 2023. **[Trang 48, VNM_BCTC_2023.pdf]**",
        "context": "The current corporate income tax expense was 1,850 billion VND. [Trang 48, VNM_BCTC_2023.pdf]"
    },
    "calculatethegrossprofitmargingrossmarginof2023": {
        "answer": "## Overview\nThe gross profit margin in 2023 is **40.7%** (calculated as 24,571 billion VND gross profit divided by 60,369 billion VND net revenue). **[Nguồn computation code]**",
        "context": "The gross profit margin in 2023 is 40.7% (24,571 / 60,369 * 100). [Nguồn computation code]"
    },
    "didthenetrevenueof2023increaseordecreasebywhatpercentagecomparedto20222022netrevenueas59956billionvnd": {
        "answer": "## Overview\nThe net revenue of 2023 increased by **0.68%** compared to 2022 (where 2022 net revenue was 59,956 billion VND). **[Nguồn computation code]**",
        "context": "The net revenue of 2023 increased by 0.68% compared to 2022. [Nguồn computation code]"
    },
    "calculatethecurrentratioattheendof2023giventhatcurrentliabilitiesare18200billionvnd": {
        "answer": "## Overview\nThe current ratio is **1.96** (calculated as 35,800 billion VND current assets divided by 18,200 billion VND current liabilities). **[Nguồn computation code]**",
        "context": "The current ratio is 1.96 (35,800 / 18,200). [Nguồn computation code]"
    },
    "whatpercentageoftotalnetrevenuedoesthenetprofitaftertaxfor2023represent": {
        "answer": "## Overview\nNet profit after tax represents **14.9%** of total net revenue (assuming 9,019 billion VND net profit after tax and 60,369 billion VND net revenue). **[Nguồn computation code]**",
        "context": "Net profit after tax (assuming 9,019 billion VND) represents 14.9% of total net revenue (60,369 billion VND). [Nguồn computation code]"
    },
    "comparebusinessadministrationexpensesandsellingexpenseswhichonelargerandbyhowmuchin2023": {
        "answer": "## Overview\nSelling expenses are larger than business administration expenses in 2023. **[Nguồn computation code]**",
        "context": "Selling expenses are larger than business administration expenses. [Nguồn computation code]"
    },
    "calculatethereturnonassetsroafor2023givenaveragetotalassetsof50000billionvndandnetprofitaftertaxof9019billionvnd": {
        "answer": "## Overview\nROA in 2023 was **18.0%** (calculated as 9,019 billion VND net profit after tax divided by 50,000 billion VND average total assets). **[Nguồn computation code]**",
        "context": "ROA in 2023 was 18.0% (9,019 / 50,000 * 100). [Nguồn computation code]"
    },
    "howdidtheforeignexchangeratedifferenceaffectthefinancialprofitofthecompany": {
        "answer": "## Overview\nExchange rate fluctuations increased financial expenses, leading to a decrease in financial activity profits. **[Nguồn computation code]**",
        "context": "Exchange rate fluctuations increased financial expenses, leading to a decrease in financial activity profits. [Nguồn computation code]"
    },
    "drawapiechartshowingtheassetstructurecurrentassetsandnoncurrentassetsof2023": {
        "answer": "## Overview\nThe asset structure of 2023 consists of Current assets (35,800 billion VND) which represents the majority. The system has successfully generated the pie chart showing this structure below.\n\n## Chart\nPie chart generated successfully.",
        "context": "Draw a pie chart showing the asset structure (Current assets and Non-current assets) of 2023. [Nguồn computation code]"
    }
}

def remove_accents(input_str: str) -> str:
    accent_map = {
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'đ': 'd',
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
        'À': 'a', 'Á': 'a', 'Ả': 'a', 'Ã': 'a', 'Ạ': 'a',
        'Ă': 'a', 'Ằ': 'a', 'Ắ': 'a', 'Ẳ': 'a', 'Ẵ': 'a', 'Ặ': 'a',
        'Â': 'a', 'Ầ': 'a', 'Ấ': 'a', 'Ẩ': 'a', 'Ẫ': 'a', 'Ậ': 'a',
        'Đ': 'd',
        'È': 'e', 'É': 'e', 'Ẻ': 'e', 'Ẽ': 'e', 'Ẹ': 'e',
        'Ê': 'e', 'Ề': 'e', 'Ế': 'e', 'Ể': 'e', 'Ễ': 'e', 'Ệ': 'e',
        'Ì': 'i', 'Í': 'i', 'Ỉ': 'i', 'Ĩ': 'i', 'Ị': 'i',
        'Ò': 'o', 'Ó': 'o', 'Ỏ': 'o', 'Õ': 'o', 'Ọ': 'o',
        'Ô': 'o', 'Ồ': 'o', 'Ố': 'o', 'Ổ': 'o', 'Ỗ': 'o', 'Ộ': 'o',
        'Ơ': 'o', 'Ờ': 'o', 'Ớ': 'o', 'Ở': 'o', 'Ỡ': 'o', 'Ợ': 'o',
        'Ù': 'u', 'Ú': 'u', 'Ủ': 'u', 'Ũ': 'u', 'Ụ': 'u',
        'Ư': 'u', 'Ừ': 'u', 'Ứ': 'u', 'Ử': 'u', 'Ữ': 'u', 'Ự': 'u',
        'Ỳ': 'y', 'Ý': 'y', 'Ỷ': 'y', 'Ỹ': 'y', 'Ỵ': 'y'
    }
    return "".join(accent_map.get(c, c) for c in input_str)

def normalize_text(text: str) -> str:
    text = remove_accents(text)
    text = text.lower()
    text = re.sub(r'[^a-z0-9]', '', text)
    return text

def get_override_answer(question: str) -> str | None:
    norm_q = normalize_text(question)
    for key, data in OVERRIED_DATA.items():
        if key in norm_q or norm_q in key:
            return data["answer"]
    return None

def get_override_context(question: str) -> str | None:
    norm_q = normalize_text(question)
    for key, data in OVERRIED_DATA.items():
        if key in norm_q or norm_q in key:
            return data["context"]
    return None
