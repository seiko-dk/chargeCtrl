from datetime import datetime
from datetime import timedelta
from co2fetch import CO2Fetcher
import json
from locale import currency

OUT_FILE = '/home/tajs/sw/chargeCtrl/co2future.txt'
#OUT_FILE = 'co2future.txt'


fetch = CO2Fetcher()
now = datetime.now()
current = [[now.hour, fetch.getCO2Avgr(0, now)]]
co2future = fetch.getCO2Prognosis(720, now)
combined = current + co2future
#print(combined)
with open(OUT_FILE, 'w') as outfile:  
    json.dump(combined, outfile)
