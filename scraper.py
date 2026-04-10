import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz

def get_petrolimex_prices():
    url = 'https://www.petrolimex.com.vn/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        target_items = [
            "DO 0,05S-II", 
            "Xăng RON 95-V", 
            "Xăng RON 95-III", 
            "DO 0,001S-V"
        ]
        
        results = {}

        rows = soup.find_all('tr')
        
        for row in rows:
            cols = row.find_all('td')
            
            if len(cols) >= 3: 
                name = cols[0].text.strip()
                
                if name in target_items:
                    results[name] = {
                        "vung_1": cols[1].text.strip(),
                        "vung_2": cols[2].text.strip()
                    }

        tz_VN = pytz.timezone('Asia/Ho_Chi_Minh')
        datetime_VN = datetime.now(tz_VN)

        data = {
            "nguon": "Petrolimex",
            "cap_nhat_luc": datetime_VN.strftime('%Y-%m-%d %H:%M:%S'),
            "gia_ban": results
        }

        with open('gia_xang.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(json.dumps(data, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_petrolimex_prices()
