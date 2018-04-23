from datetime import datetime
from co2fetch import CO2Fetcher
import json

fetch = CO2Fetcher()
now = datetime.now()
co2 = fetch.getCO2Prognosis(120, now)
#print(co2)
with open('co2future.txt', 'w') as outfile:  
    json.dump(co2, outfile)