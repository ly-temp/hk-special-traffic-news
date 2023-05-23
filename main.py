import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

#cofig
API_URL = 'https://api.data.gov.hk/v1/historical-archive/get-file?url=https%3A%2F%2Fwww.td.gov.hk%2Ftc%2Fspecial_news%2Ftrafficnews.xml&time='
BACK_TRACK_TIME=timedelta(hours=10)

os.makedirs('./json', exist_ok=True)

now = datetime.now(tz=ZoneInfo("Asia/Hong_Kong"))
t = now-BACK_TRACK_TIME

while t <= now:
    print(t.date)
    t += timedelta(minutes=1)
