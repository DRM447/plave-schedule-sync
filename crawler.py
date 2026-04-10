import requests
from ics import Calendar, Event
from datetime import datetime, timedelta
import pytz
import time

def fetch_and_convert():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    first_day_of_this_month = kst.localize(datetime(now.year, now.month, 1))

    api_url = f"https://plavecalendar.com/api/events?year={now.year}&month={now.month}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://plavecalendar.com/',
        'Origin': 'https://plavecalendar.com'
    }
    max_retries = 3

    category_map = {
        "aa3be5ab-8895-456c-a39b-dece94875531": "Live",
        "6b6cc049-b062-480a-aab1-fe5c3ae8925b": "Special",
        "708da38d-5422-4868-8898-378900f93ff9": "Release",
        "ce09b4b4-98f5-4e21-ba0a-08f2ee17048a": "Media"
    }

    for attempt in range(max_retries):
        try:
            print(f"[{attempt + 1}/{max_retries}] 스케줄 데이터 가져오는 중...")
            response = requests.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()

            schedules = response.json()
            c = Calendar()

            for item in schedules:
                utc_start_str = item.get("utcStart")
                if not utc_start_str: continue

                start_date_utc = datetime.strptime(utc_start_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                start_date_utc = start_date_utc.replace(tzinfo=pytz.utc)
                start_date_kst = start_date_utc.astimezone(kst)

                if start_date_kst < first_day_of_this_month:
                    continue

                e = Event()
                e.uid = item.get("id")

                raw_title = item.get("title", "스케줄")
                cat_id = item.get("category", "")
                cat_name = category_map.get(cat_id, "Schedule")
                e.name = f"[{cat_name}] {raw_title}"

                if item.get("isAllDay"):
                    e.make_all_day()
                    e.begin = start_date_kst.date()
                    utc_end_str = item.get("utcEnd")
                    if utc_end_str:
                        end_date_utc = datetime.strptime(utc_end_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                        e.end = end_date_utc.replace(tzinfo=pytz.utc).astimezone(kst).date()
                else:
                    e.begin = start_date_kst
                    e.end = start_date_kst + timedelta(hours=1)

                links = item.get("links", [])
                if links and len(links) > 0:
                    url = links[0].get("url")
                    e.url = url
                    e.description = f"상세 링크: {url}"

                c.events.add(e)

            # --- 파일 저장 핵심 로직 ---
            calendar_content = str(c.serialize())
            with open('plave_schedule.ics', 'w', encoding='utf-8') as f:
                f.write(calendar_content)
                f.flush()

            print("🎉 진짜 캘린더 파일 업데이트 성공!")
            break

        except Exception as e:
            print(f"오류 발생: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                print("최대 재시도 횟수를 초과했습니다.")

if __name__ == "__main__":
    fetch_and_convert()
