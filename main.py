import os
import pickle
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json
import xmltodict
import requests
from bs4 import BeautifulSoup

#cofig
API_URL = 'https://api.data.gov.hk/v1/historical-archive/get-file?url=https%3A%2F%2Fwww.td.gov.hk%2Ftc%2Fspecial_news%2Ftrafficnews.xml&time='
GEO_API_URL = 'https://www.als.ogcio.gov.hk/lookup'
DEFAULT_BACK_TRACK_TIME=timedelta(hours=1)
DELETE_DELTA=timedelta(days=3)
GET_BUFFER_DELTA=timedelta(minutes=1)
PROGRAM_DATA_DIR = './temp/program_data.pickle'
JSON_DIR = './json/api.json'

now = datetime.now(tz=ZoneInfo("Asia/Hong_Kong")).replace(tzinfo=None)
now_iso = now.replace(microsecond=0).isoformat()

class ProgramData(object):
    def __init__(self, last_update_t):
        self.last_update_t = last_update_t

class History():
    def __init__(self, json_dir=JSON_DIR):
        self.history = {}
        if(os.path.exists(json_dir)):
            with open(json_dir, 'r') as f:
                self.history = json.load(f)

    def __str__(self):
        return json.dumps(self.history, ensure_ascii=False, indent=4)

    def save(self, json_dir=JSON_DIR):
        with open(json_dir, 'w') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def push_msg(self, message):
        history = self.history
        incident_id = message.pop('INCIDENT_NUMBER')

        location = message['NEAR_LANDMARK_CN'] or message['LOCATION_CN'] or message['DIRECTION_CN']
        if location == None:
            district = None
        else:
            district = get_district(location)

        update_msg = {}
        for e in ['ANNOUNCEMENT_DATE','INCIDENT_STATUS_EN','INCIDENT_STATUS_CN','ID','CONTENT_EN','CONTENT_CN']:
            try:
                update_msg[e] = message.pop(e)
            except:
                update_msg[e] = '' #repair broken
        message_t = update_msg.pop('ANNOUNCEMENT_DATE')

        if incident_id in history:
            msg = history[incident_id]['message']
            if not message_t in msg:
                history[incident_id]['message'].update({
                    message_t: update_msg
                })
                history[incident_id]['last_update'] = now_iso
                history[incident_id]['last_announcement'] = message_t
        else:
            history.update({incident_id:{
                'description': message,
                'message':{
                    message_t: update_msg
                },
                'district': district,
                'last_update': now_iso,
                'last_announcement': message_t
            }})

    def remove_expire(self, delta=DELETE_DELTA):
        history = self.history
        for id in list(history):
            last_update = history[id]['last_update']
            last_dt = datetime.strptime(last_update, '%Y-%m-%dT%H:%M:%S')
            if now-delta > last_dt:
                print(f'del: {id}') #test
                del history[id]

def get_as_obj(t_strg):
    res = requests.get(API_URL+t_strg, allow_redirects=True)
    if res.ok:
        xml = res.content
        purged_xml = xml.decode('utf-8','ignore').rstrip('\x00').encode('utf-8')
        purged_xml = str(BeautifulSoup(purged_xml, features='xml')) #repair broken
        data_dict = xmltodict.parse(purged_xml)
        message = data_dict['list']['message']
        return message
        #print(json.dumps(message, ensure_ascii=False))


def get_district(location):
    res = requests.post(GEO_API_URL,
        headers={
            'Accept-Language': 'zh-Hant',
            'Accept-Encoding': 'gzip'
        },
        data={
            'q': location,
            'n': 1,
            't': 80
        }
    )
    dict = xmltodict.parse(res.content)
    return dict['AddressLookupResult']['SuggestedAddress']['Address']['PremisesAddress']['ChiPremisesAddress']['ChiDistrict']['DcDistrict']

os.makedirs('./temp', exist_ok=True)
os.makedirs('./json', exist_ok=True)

history = History()

if os.path.exists(PROGRAM_DATA_DIR):
    with open(PROGRAM_DATA_DIR, 'rb') as f:
        data = pickle.load(f)
else:
    data = ProgramData(now-DEFAULT_BACK_TRACK_TIME)

t = data.last_update_t
while t <= now-GET_BUFFER_DELTA:
    t_strg = f'{t.year}{t.month:02d}{t.day:02d}-{t.hour:02d}{t.minute:02d}'

    try:
        msg = get_as_obj(t_strg)
        history.push_msg(msg)
    except Exception as e:
        print(f'{t_strg}[E]: {e}')

    t += timedelta(minutes=1)
data.last_update_t = t

with open(PROGRAM_DATA_DIR, 'wb') as f:
    pickle.dump(data, f)

history.remove_expire()
history.save()
