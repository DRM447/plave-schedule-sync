import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import pytz

def fetch_and_convert():
    url = "https://plavecalendar.com/"
    # 브라우저 접속처럼 보이게 설정
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    c = Calendar()
    
    # 한국 시간(KST) 기준으로 이번 달 1일 설정
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    first_day_of_this_month = datetime(now.year, now.month, 1, tzinfo=kst)
    
    # ⚠️ 중요: 아래는 예시 뼈대입니다. 실제 웹사이트의 HTML 구조를 파악해 채워넣어야 합니다.
    schedules = soup.select('.schedule-item-class-name') 
    
    for item in schedules:
        e = Event()
        e.name = "스케줄 제목" # 실제 사이트의 제목 요소
        # e.url = "링크 주소" # 팝업의 링크 주소
        
        # 임시 날짜 비교 로직 (실제로는 사이트의 날짜 텍스트를 변환해야 함)
        # if parsed_date >= first_day_of_this_month:
        #     e.begin = parsed_date
        #     c.events.add(e)
            
    with open('plave_schedule.ics', 'w', encoding='utf-8') as f:
        f.writelines(c.serialize_iter())

if __name__ == "__main__":
    fetch_and_convert()
