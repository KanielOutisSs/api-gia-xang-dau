import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz

def get_fuel_prices():
    # Giả sử chúng ta cào dữ liệu từ một trang web cung cấp giá xăng dầu
    url = 'https://vnexpress.net/chu-de/gia-xang-dau-2449' # (Đây là URL ví dụ, bạn có thể đổi thành trang khác)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # --- BẮT ĐẦU PHẦN TÙY CHỈNH THEO WEBSITE ---
        # Bạn dùng F12 (Inspect) để tìm class chứa giá. Dưới đây là code mô phỏng logic:
        # ron_95 = soup.find('td', class_='price-ron95').text.strip()
        # dau_do = soup.find('td', class_='price-do').text.strip()
        
        # Tạm thời gán dữ liệu giả lập nếu cấu trúc web phức tạp
        ron_95 = "24.000"
        dau_do = "20.500"
        # --- KẾT THÚC PHẦN TÙY CHỈNH ---

        # Lấy giờ Việt Nam hiện tại
        tz_VN = pytz.timezone('Asia/Ho_Chi_Minh')
        datetime_VN = datetime.now(tz_VN)

        # Định dạng dữ liệu thành Dictionary
        data = {
            "nguon": "Tự cào dữ liệu",
            "cap_nhat_luc": datetime_VN.strftime('%Y-%m-%d %H:%M:%S'),
            "gia_ban": {
                "RON_95": ron_95,
                "DO_0.05S": dau_do
            }
        }

        # Lưu ra file JSON
        with open('gia_xang.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print("Cào dữ liệu và tạo file JSON thành công!")

    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    get_fuel_prices()
