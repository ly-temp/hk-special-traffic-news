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
JSON_DIR = './json/api.json'

class ProgramData(object):
    def __init__(self, last_update_t):
        self.last_update_t = last_update_t

def get_as_obj(t_strg):
    res = requests.get(API_URL+t_strg)
    if res.ok:
        xml = res.content
        data_dict = xmltodict.parse(xml)
        message = data_dict['list']['message']
        return message
        #print(json.dumps(message, ensure_ascii=False))

def push_msg(history, message):
    incident_id = message.pop('INCIDENT_NUMBER')

    update_msg = {}
    for e in ['ANNOUNCEMENT_DATE','INCIDENT_STATUS_EN','INCIDENT_STATUS_CN','ID','CONTENT_EN','CONTENT_CN']:
        update_msg[e] = message.pop(e)
    message_t = update_msg.pop('ANNOUNCEMENT_DATE')

    if incident_id in history:
        history[incident_id]['message'].update({
            message_t: update_msg
        })
    else:
        history.update({incident_id:{
            'description': message,
            'message': {
                message_t: update_msg
            }
        }})

history = {}
if(os.path.exists(JSON_DIR)):
    with open(JSON_DIR, 'wb') as f:
        history = json.load(f)

msg = get_as_obj('20230522-1248')
push_msg(history, msg)
msg = get_as_obj('20230522-1255')
push_msg(history, msg)
msg = get_as_obj('20230522-1341')
push_msg(history, msg)

print(json.dumps(history, ensure_ascii=False))
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