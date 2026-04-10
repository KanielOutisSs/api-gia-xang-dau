from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz
import sys # Import thêm thư viện này để ép Action báo lỗi đỏ nếu thất bại

def get_petrolimex_prices():
    url = 'https://www.petrolimex.com.vn/'
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Thêm Viewport và User-Agent để ngụy trang giống người dùng thật hơn
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            print("Đang truy cập Petrolimex...")
            page.goto(url, timeout=60000)
            
            # ĐÃ SỬA LỖI: Xóa số 1 ở cuối tên class
            page.wait_for_selector('.header__pricePetrol', timeout=20000)
            print("Đã tải xong bảng giá, tiến hành bóc tách...")
            
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            target_items = ["DO 0,05S-II", "Xăng RON 95-V", "Xăng RON 95-III", "DO 0,001S-V"]
            results = {}

            # ĐÃ SỬA LỖI: Xóa số 1 ở cuối tên class
            price_container = soup.find('div', class_='header__pricePetrol')
            
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

            # Nếu mảng rỗng (cào xịt), ném ra lỗi để dừng chương trình
            if not results:
                raise ValueError("Không bóc tách được dữ liệu. Có thể web đã đổi cấu trúc!")

            # Lưu dữ liệu nếu cào thành công
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
            sys.exit(1)  # Kích hoạt báo lỗi đỏ trên GitHub Actions
        finally:
            browser.close()

if __name__ == "__main__":
    get_petrolimex_prices()
