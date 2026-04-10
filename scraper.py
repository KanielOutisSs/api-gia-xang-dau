import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz

def get_petrolimex_prices():
    url = 'https://www.petrolimex.com.vn/'
    
    # Sử dụng cloudscraper để bypass các hệ thống WAF (Cloudflare/Anti-bot)
    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })

    try:
        response = scraper.get(url, timeout=15)
        response.raise_for_status()
        
        # Kiểm tra nhanh xem có bị block không (in ra Action Logs)
        if "header__pricePetrol" not in response.text:
            print("⚠️ CẢNH BÁO: Không tìm thấy class chứa giá. Có thể WAF đã chặn truy cập.")
            print("Mã HTML trả về (500 ký tự đầu):", response.text[:500])
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        target_items = [
            "DO 0,05S-II", 
            "Xăng RON 95-V", 
            "Xăng RON 95-III", 
            "DO 0,001S-V"
        ]
        
        results = {}

        # Trỏ chính xác vào class chứa bảng giá như trong ảnh F12
        price_container = soup.find('div', class_='header__pricePetrol1')
        
        if price_container:
            rows = price_container.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3: 
                    name = cols[0].text.strip()
                    if name in target_items:
                        results[name] = {
                            "vung_1": cols[1].text.strip(),
                            "vung_2": cols[2].text.strip()
                        }

        # Lưu dữ liệu
        tz_VN = pytz.timezone('Asia/Ho_Chi_Minh')
        datetime_VN = datetime.now(tz_VN)

        data = {
            "nguon": "Petrolimex",
            "cap_nhat_luc": datetime_VN.strftime('%Y-%m-%d %H:%M:%S'),
            "gia_ban": results
        }

        with open('gia_xang.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print("✅ Dữ liệu bóc tách:")
        print(json.dumps(data, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"❌ Lỗi thực thi: {e}")

if __name__ == "__main__":
    get_petrolimex_prices()
