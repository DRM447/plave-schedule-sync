import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
import datetime

def fetch_and_convert():
    url = "https://plavecalendar.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    c = Calendar()
    
    # 1. 사이트에서 일정 데이터를 찾는 로직 (예시)
    # 실제 사이트의 HTML 구조(class name 등)에 맞춰 수정이 필요합니다.
    schedules = soup.select('.schedule-item') 
    
    for item in schedules:
        e = Event()
        e.name = item.select_one('.title').text
        e.begin = item.select_one('.date').text # YYYY-MM-DD HH:mm:ss 형식으로 변환 필요
        c.events.add(e)
    
    # 2. .ics 파일로 저장
    with open('plave_schedule.ics', 'w', encoding='utf-8') as f:
        f.writelines(c.serialize_iter())

if __name__ == "__main__":
    fetch_and_convert()
