import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz

def get_petrolimex_prices():
    # URL trang chủ Petrolimex
    url = 'https://www.petrolimex.com.vn/'
    
    # Headers giả lập trình duyệt để tránh bị chặn
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Phân tích HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Danh sách các mặt hàng bạn muốn lấy
        target_items = [
            "DO 0,05S-II", 
            "Xăng RON 95-V", 
            "Xăng RON 95-III", 
            "DO 0,001S-V"
        ]
        
        results = {}

        # Tìm thẻ div chứa bảng giá theo đúng cấu trúc trong ảnh F12 của bạn
        price_container = soup.find('div', class_='header__pricePetrol')
        
        if price_container:
            # Lấy tất cả các hàng (tr) trong bảng
            rows = price_container.find_all('tr')
            
            for row in rows:
                cols = row.find_all('td')
                
                # Bỏ qua các hàng không có đủ dữ liệu (ví dụ hàng tiêu đề)
                if len(cols) >= 3: 
                    name = cols[0].text.strip()
                    
                    # Nếu tên nhiên liệu nằm trong danh sách yêu cầu thì lấy giá
                    if name in target_items:
                        # cols[1] là giá Vùng 1, cols[2] là giá Vùng 2
                        price_vung1 = cols[1].text.strip()
                        price_vung2 = cols[2].text.strip()
                        
                        results[name] = {
                            "vung_1": price_vung1,
                            "vung_2": price_vung2
                        }
        
        if not results:
            print("Cảnh báo: Không bóc tách được dữ liệu. Có thể web đã đổi cấu trúc!")

        # Lấy thời gian hiện tại theo múi giờ Việt Nam
        tz_VN = pytz.timezone('Asia/Ho_Chi_Minh')
        datetime_VN = datetime.now(tz_VN)

        # Đóng gói thành chuẩn JSON
        data = {
            "nguon": "Petrolimex",
            "cap_nhat_luc": datetime_VN.strftime('%Y-%m-%d %H:%M:%S'),
            "gia_ban": results
        }

        # Lưu ra file json
        with open('gia_xang.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print("✅ Bóc tách dữ liệu thành công!")
        print(json.dumps(data, ensure_ascii=False, indent=2)) # In ra log để dễ kiểm tra

    except Exception as e:
        print(f"❌ Có lỗi xảy ra trong quá trình cào dữ liệu: {e}")

if __name__ == "__main__":
    get_petrolimex_prices()
