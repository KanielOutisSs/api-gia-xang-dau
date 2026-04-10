from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz

def get_petrolimex_prices():
    url = 'https://www.petrolimex.com.vn/'
    
    # Khởi chạy Playwright
    with sync_playwright() as p:
        # Mở trình duyệt Chromium ẩn (headless=True)
        browser = p.chromium.launch(headless=True)
        
        # Giả lập User-Agent của người dùng thật
        page = browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            print("Đang truy cập Petrolimex...")
            page.goto(url, timeout=30000)
            
            # QUAN TRỌNG: Đợi tối đa 15 giây cho đến khi thẻ chứa bảng giá xuất hiện
            # Điều này giúp vượt qua các màn hình loading hoặc check Cloudflare ban đầu
            page.wait_for_selector('.header__pricePetrol1', timeout=15000)
            print("Đã tải xong bảng giá, tiến hành bóc tách...")
            
            # Lấy toàn bộ mã HTML sau khi JavaScript đã chạy xong
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            target_items = ["DO 0,05S-II", "Xăng RON 95-V", "Xăng RON 95-III", "DO 0,001S-V"]
            results = {}

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
                
            print("✅ Bóc tách dữ liệu thành công!")
            print(json.dumps(data, ensure_ascii=False, indent=2))

        except Exception as e:
            print(f"❌ Có lỗi xảy ra hoặc bị block: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    get_petrolimex_prices()
