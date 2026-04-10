import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta
import pytz
import re
import time

def fetch_and_convert():
    # 1. 사이트 접속 및 기본 세팅
    url = "https://plavecalendar.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    max_retries = 3

    for attempt in range(max_retries):
        try:
            print(f"[{attempt + 1}/{max_retries}] 사이트 접속 중...")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            c = Calendar()
            
            # 한국 시간 기준 '이번 달 1일' 계산
            kst = pytz.timezone('Asia/Seoul')
            now = datetime.now(kst)
            first_day_of_this_month = kst.localize(datetime(now.year, now.month, 1))

            # 2. 스케줄 블록(하루 단위) 모두 찾기
            day_blocks = soup.select('div.mb-3.border.border-gray-100')

            for block in day_blocks:
                # 날짜 데이터 추출 (예: 2026-04-02T15:00:00.000Z)
                time_tag = block.select_one('time')
                if not time_tag: continue
                
                raw_date_str = time_tag.get('datetime')
                
                # UTC 시간을 한국 시간(KST)으로 변환
                base_date_utc = datetime.strptime(raw_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                base_date_utc = base_date_utc.replace(tzinfo=pytz.utc)
                base_date_kst = base_date_utc.astimezone(kst)

                # "이번 달 1일"보다 과거인 일정은 패스!
                if base_date_kst < first_day_of_this_month:
                    continue

                # 3. 해당 날짜 안의 개별 스케줄(버튼)들 추출
                events = block.select('button[aria-label="Event details"]')
                for ev in events:
                    title_attr = ev.get('title', '').strip() # 예: PLAVE LIVE 20:00
                    
                    # 카테고리 (Live, Special, Media 등)
                    category_tag = ev.select_one('p.font-semibold')
                    category = category_tag.text if category_tag else ""
                    
                    # 깔끔한 제목 (h4 태그 안의 텍스트)
                    title_tag = ev.select_one('h4')
                    clean_title = title_tag.text if title_tag else title_attr

                    e = Event()
                    e.name = f"[{category}] {clean_title}" # [Live] PLAVE LIVE 형태로 저장

                    # 정규식을 사용해 title 속성 맨 뒤의 'HH:MM' 시간 추출
                    time_match = re.search(r'(\d{2}):(\d{2})$', title_attr)
                    
                    if time_match:
                        # 시간이 적혀있다면 (예: 20:00)
                        hour = int(time_match.group(1))
                        minute = int(time_match.group(2))
                        event_start_kst = base_date_kst.replace(hour=hour, minute=minute)
                        
                        e.begin = event_start_kst
                        e.end = event_start_kst + timedelta(hours=1) # 종료 시간은 임의로 1시간 뒤로 설정
                    else:
                        # 시간이 안 적힌 스케줄(팝업스토어, 앨범 발매 등)은 '종일 일정'으로 설정
                        e.make_all_day()
                        e.begin = base_date_kst.date()

                    c.events.add(e)

            # 4. 파일 저장
            with open('plave_schedule.ics', 'w', encoding='utf-8') as f:
                f.writelines(c.serialize_iter())
                
            print("🎉 캘린더 파일 업데이트 성공!")
            break

        except Exception as e:
            print(f"오류 발생: {e}")
            if attempt < max_retries - 1:
                print("5분 뒤에 다시 시도합니다...")
                time.sleep(300)
            else:
                print("최대 재시도 횟수를 초과했습니다.")

if __name__ == "__main__":
    fetch_and_convert()
