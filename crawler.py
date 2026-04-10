import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import pytz
import time  # 시간을 지연시키기 위해 새로 추가된 모듈

def fetch_and_convert():
    url = "https://plavecalendar.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    max_retries = 3  # 최대 재시도 횟수
    
    for attempt in range(max_retries):
        try:
            print(f"[{attempt + 1}/{max_retries}] 사이트 접속 시도 중...")
            
            # timeout=10: 10초 동안 응답이 없으면 에러로 처리하라는 뜻
            response = requests.get(url, headers=headers, timeout=10)
            
            # 사이트에서 200(정상)이 아닌 404, 500(서버 에러) 등을 보내면 강제로 에러를 발생시킴
            response.raise_for_status() 
            
            # --- 접속 성공 시 아래 크롤링 로직 실행 ---
            soup = BeautifulSoup(response.text, 'html.parser')
            c = Calendar()
            
            kst = pytz.timezone('Asia/Seoul')
            now = datetime.now(kst)
            first_day_of_this_month = datetime(now.year, now.month, 1, tzinfo=kst)
            
            # (여기에 앞서 논의한 실제 스케줄 데이터 파싱 로직이 들어갑니다)
            # schedules = soup.select('...') 
            # for item in schedules:
            #     ...
            
            with open('plave_schedule.ics', 'w', encoding='utf-8') as f:
                f.writelines(c.serialize_iter())
                
            print("성공적으로 캘린더 파일을 업데이트했습니다!")
            break  # 완료되었으므로 재시도 루프(for문)를 탈출함

        except Exception as e:
            # 에러가 발생하면 이쪽으로 넘어옵니다.
            print(f"오류 발생: {e}")
            
            if attempt < max_retries - 1:
                print("5분(300초) 뒤에 다시 시도합니다...\n")
                time.sleep(300)  # 300초 동안 코드를 일시 정지
            else:
                print("최대 재시도 횟수를 초과했습니다. 이번 크롤링 작업을 취소합니다.")
                # 여기서 실패했다는 사실을 텔레그램이나 디스코드로 내 폰에 알림 오게 짤 수도 있습니다!

if __name__ == "__main__":
    fetch_and_convert()
