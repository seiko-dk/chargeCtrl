from datetime import datetime
from co2fetch import CO2Fetcher
import json

OUT_FILE = '/home/tajs/sw/chargeCtrl/co2future.txt'
#OUT_FILE = 'co2future.txt'


fetch = CO2Fetcher()
now = datetime.now()
co2 = fetch.getCO2Prognosis(720, now)
#print(co2)
with open(OUT_FILE, 'w') as outfile:  
    json.dump(co2, outfile)
