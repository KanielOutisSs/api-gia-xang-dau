import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz
import sys

def get_giaxanghomnay_prices():
    url = 'https://giaxanghomnay.com/'
    
    # Sử dụng User-Agent chuẩn để tránh bị chặn bởi các filter cơ bản
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        print(f"Đang truy cập {url}...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Tìm tất cả các bảng trên trang. Bảng đầu tiên [0] là của Petrolimex
        tables = soup.find_all('table')
        if not tables:
            raise ValueError("Không tìm thấy thẻ <table> nào trên trang!")

        petrolimex_table = tables[0]
        
        # Tìm phần thân bảng (tbody) và lấy tất cả các hàng (tr)
        tbody = petrolimex_table.find('tbody')
        rows = tbody.find_all('tr') if tbody else petrolimex_table.find_all('tr')

        target_items = [
            "DO 0,05S-II", 
            "Xăng RON 95-V", 
            "Xăng RON 95-III", 
            "DO 0,001S-V",
            "Xăng E5 RON 92-II" # Bổ sung thêm mặt hàng này vì khá phổ biến
        ]
        
        results = {}

        for row in rows:
            cols = row.find_all('td')
            
            # Đảm bảo hàng có đủ 5 cột như cấu trúc đã phân tích
            if len(cols) >= 5: 
                name = cols[0].text.strip()
                
                if name in target_items:
                    results[name] = {
                        "vung_1": cols[3].text.strip(),
                        "vung_2": cols[4].text.strip()
                    }

        if not results:
            raise ValueError("Không bóc tách được dữ liệu. Website có thể đã thay đổi cấu trúc!")

        # Chuẩn hóa thời gian theo múi giờ Việt Nam
        tz_VN = pytz.timezone('Asia/Ho_Chi_Minh')
        datetime_VN = datetime.now(tz_VN)

        data = {
            "nguon": "giaxanghomnay.com",
            "cap_nhat_luc": datetime_VN.strftime('%Y-%m-%d %H:%M:%S'),
            "gia_ban": results
        }

        # Lưu xuất dữ liệu ra tệp JSON
        with open('gia_xang.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print("✅ Bóc tách dữ liệu thành công!")
        print(json.dumps(data, ensure_ascii=False, indent=2))

    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi kết nối HTTP: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi thực thi logic: {e}")
        sys.exit(1)

if __name__ == "__main__":
    get_giaxanghomnay_prices()
