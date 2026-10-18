import json
import re
import sys
from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup


URL = "https://giaxanghomnay.com/"
# Exactly two products requested; keep stable JSON keys across name variants.
PRODUCT_PATTERNS = {
    "Xăng E10 RON 95 Mức 5": r"^Xăng\s+E10\s+RON\s*95\s*(?:-?V|Mức\s*5)$",
    "DO 0,05S Mức 2": r"^(?:Dầu\s+)?DO\s+0[,.]05S\s*(?:-?II|Mức\s*2)$",
}


def clean(value):
    return re.sub(r"\s+", " ", value.replace("\xa0", " ").replace("–", "-").replace("—", "-")).strip()


def match_product(name):
    for label, pattern in PRODUCT_PATTERNS.items():
        if re.fullmatch(pattern, name, flags=re.IGNORECASE):
            return label
    return None


def extract_prices(html):
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    print(f"Đã tìm thấy {len(tables)} bảng HTML.")

    for table in tables:
        rows = table.find_all("tr")
        # Identify Petrolimex table by the two regional price headers,
        # rather than assuming the first table is Petrolimex.
        header = clean(" ".join(cell.get_text(" ", strip=True) for row in rows[:3]
                                for cell in row.find_all(["th", "td"]))).lower()
        if not ("vùng 1" in header and "vùng 2" in header):
            continue

        results = {}
        observed = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue
            name = clean(cols[0].get_text(" ", strip=True))
            observed.append(name)
            product = match_product(name)
            if product is None:
                continue

            region1 = clean(cols[-2].get_text(" ", strip=True))
            region2 = clean(cols[-1].get_text(" ", strip=True))
            if not re.fullmatch(r"[\d.,]+", region1) or not re.fullmatch(r"[\d.,]+", region2):
                print(f"Bỏ qua giá không hợp lệ: {name}: {region1} / {region2}")
                continue
            results[product] = {"vung_1": region1, "vung_2": region2}

        print("Các mặt hàng trong bảng Petrolimex:", observed)
        missing = set(PRODUCT_PATTERNS) - set(results)
        if not missing:
            return results
        print(f"Chưa tìm thấy đủ mặt hàng: {sorted(missing)}")

    # Help diagnose layout changes without writing an empty JSON file.
    raise ValueError(
        "Không lấy đủ 2 mặt hàng E10 RON 95 Mức 5 và DO 0,05S Mức 2 "
        "trong bảng giá Petrolimex (Vùng 1/Vùng 2); giữ nguyên JSON cũ."
    )


def get_giaxanghomnay_prices():
    try:
        print(f"Đang truy cập {URL}...")
        response = requests.get(
            URL,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.7",
            },
            timeout=25,
        )
        response.raise_for_status()
        results = extract_prices(response.text)
        vn_now = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
        data = {
            "nguon": "giaxanghomnay.com",
            "cap_nhat_luc": vn_now.strftime("%Y-%m-%d %H:%M:%S"),
            "gia_ban": results,
        }
        with open("gia_xang.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print("✅ Bóc tách dữ liệu thành công!")
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except (requests.RequestException, ValueError) as exc:
        print(f"❌ Lỗi scraper: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    get_giaxanghomnay_prices()
