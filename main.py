import os
import pickle
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

#cofig
API_URL = 'https://api.data.gov.hk/v1/historical-archive/get-file?url=https%3A%2F%2Fwww.td.gov.hk%2Ftc%2Fspecial_news%2Ftrafficnews.xml&time='
DEFAULT_BACK_TRACK_TIME=timedelta(hours=10)

class ProgramData(object):
    def __init__(self, last_update_t):
        self.last_update_t = last_update_t

os.makedirs('./json', exist_ok=True)

now = datetime.now(tz=ZoneInfo("Asia/Hong_Kong"))
t = now-DEFAULT_BACK_TRACK_TIME

while t <= now:
    t_strg = f'{t.year}{t.month:02d}{t.day:02d}-{t.hour:02d}{t.minute:02d}'
    print(t_strg)
    t += timedelta(minutes=1)
