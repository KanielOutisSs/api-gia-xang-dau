import json
import re
import sys
from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup


URL = "https://giaxanghomnay.com/"
# Match product names exactly after normalizing spaces/dashes.
# Include the E10 RON 95 products currently shown by the website.
PRODUCT_PATTERNS = (
    r"^Xăng E5 RON 92(?:-II)?$",
    r"^Xăng E10 RON 95-(?:III|V)$",
    r"^Xăng RON 95-(?:III|V)$",
    r"^(?:Dầu )?DO 0,05S-II$",
    r"^(?:Dầu )?DO 0,001S-V$",
)


def clean(value):
    return re.sub(r"\s+", " ", value.replace("\xa0", " ").replace("–", "-").replace("—", "-")).strip()


def is_target(name):
    return any(re.fullmatch(pattern, name, flags=re.IGNORECASE) for pattern in PRODUCT_PATTERNS)


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
            if not is_target(name):
                continue

            region1 = clean(cols[-2].get_text(" ", strip=True))
            region2 = clean(cols[-1].get_text(" ", strip=True))
            if not re.fullmatch(r"[\d.,]+", region1) or not re.fullmatch(r"[\d.,]+", region2):
                print(f"Bỏ qua giá không hợp lệ: {name}: {region1} / {region2}")
                continue
            results[name] = {"vung_1": region1, "vung_2": region2}

        print("Các mặt hàng trong bảng Petrolimex:", observed)
        if results:
            return results

    # Help diagnose layout changes without writing an empty JSON file.
    raise ValueError(
        "Không đọc được bảng giá Petrolimex với cột Giá vùng 1 và Giá vùng 2. "
        "Có thể website thay đổi cấu trúc hoặc trả về HTML khác trên GitHub Actions."
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
