import os
import datetime

url = 'https://api.data.gov.hk/v1/historical-archive/get-file?url=https%3A%2F%2Fwww.td.gov.hk%2Ftc%2Fspecial_news%2Ftrafficnews.xml&time='

os.makedirs('./json', exist_ok=True)
print(datetime.datetime.now())