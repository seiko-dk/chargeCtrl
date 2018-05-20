from datetime import datetime
from co2fetch import CO2Fetcher
import json

fetch = CO2Fetcher()
now = datetime.now()
co2 = fetch.getCO2Prognosis(720, now)
#print(co2)
with open('/home/tajs/sw/chargeCtrl/co2future.txt', 'w') as outfile:  
    json.dump(co2, outfile)
