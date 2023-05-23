import os
import pickle
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json
import xmltodict
import requests

#cofig
API_URL = 'https://api.data.gov.hk/v1/historical-archive/get-file?url=https%3A%2F%2Fwww.td.gov.hk%2Ftc%2Fspecial_news%2Ftrafficnews.xml&time='
DEFAULT_BACK_TRACK_TIME=timedelta(minutes=10)
PROGRAM_DATA_DIR = './temp/program_data.pickle'

class ProgramData(object):
    def __init__(self, last_update_t):
        self.last_update_t = last_update_t

def get_json(t_strg):
    res = requests.get(API_URL+t_strg)
    if res.ok:
        xml = res.content
        data_dict = xmltodict.parse(xml)
        message = data_dict.get('list').get('message')
        incident_id = message.pop('INCIDENT_NUMBER')
        message = {incident_id: message}
        print(json.dumps(message, ensure_ascii=False))
    
get_json('20230522-1248')
exit()

os.makedirs('./temp', exist_ok=True)
os.makedirs('./json', exist_ok=True)

now = datetime.now(tz=ZoneInfo("Asia/Hong_Kong"))

if os.path.exists(PROGRAM_DATA_DIR):
    with open(PROGRAM_DATA_DIR, 'rb') as f:
        data = pickle.load(f)
else:
    data = ProgramData(now-DEFAULT_BACK_TRACK_TIME)

t = data.last_update_t
while t <= now:
    t_strg = f'{t.year}{t.month:02d}{t.day:02d}-{t.hour:02d}{t.minute:02d}'
    print(t_strg)
    t += timedelta(minutes=1)
data.last_update_t = t

with open(PROGRAM_DATA_DIR, 'wb') as f:
    pickle.dump(data, f)