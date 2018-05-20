from datetime import datetime
from datetime import timedelta
import urllib3
import json

class CO2Fetcher(object):

    def __init__(self):
        self._http = urllib3.PoolManager()
        self._url = 'http://api.energidataservice.dk/datastore_search?resource_id=b5a8e0bc-44af-49d7-bb57-8f968f96932d&limit=5&filters='
        self._future_url = 'http://api.energidataservice.dk/datastore_search?resource_id=d856694b-5e0e-463b-acc4-d9d7d895128a&limit=5&filters='

    def _calcLookuptime(self, timestamp):
        timestamp = timestamp - timedelta(0,0,0,0,timestamp.minute % 5)
        timestamp = timestamp - timedelta(0,0,0,0,10)
        return timestamp

    def _formatLookuptime(self, timestamp):
        timestring = "%i-%02i-%02iT%02i:%02i" % (timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute)
        return timestring

    def _GetCO2Data(self, timestring):
        filter= '{"PriceArea":"DK2","Minutes5DK":"' + timestring +'"}'
        #print(filter)
        completeUrl = self._url + filter
        #print (completeUrl)
        r = self._http.request('GET', completeUrl)
        #print (r.data)
        d=json.loads(r.data.decode('utf-8'))
        d=d['result']
        d=d['records']
        d=d[0]
        d=d['CO2Emission']
        #print(d)
        return d

    def _GetCO2FutureData(self, timestring):
        filter= '{"PriceArea":"DK2","Minutes5DK":"' + timestring +'"}'
        #print(filter)
        completeUrl = self._future_url + filter
        #print (completeUrl)
        r = self._http.request('GET', completeUrl)
        #print (r.data)
        d=json.loads(r.data.decode('utf-8'))
        d=d['result']
        d=d['records']
        d=d[0]
        key=d['_id']
        d=d['CO2Emission']
        #print(d)
        return d

    def getCO2Prognosis(self, minutes, timestamp):
        loopCount = 0;
        co2 = [];
        try:
            timestamp = timestamp + timedelta(0, 0, 0, 0, 10)   #compensate for the _calcLookuptime 10 subtraction
            timestamp = self._calcLookuptime(timestamp)
            while (0<minutes):
                timestr = self._formatLookuptime(timestamp)
                value = self._GetCO2FutureData(timestr)
                entry = [timestamp.hour, value]
                co2.append(entry)
                minutes = minutes - 60
                timestamp = timestamp + timedelta(0, 0, 0, 0, 60)
                loopCount = loopCount +1
                #print(entry)
        except:
            co2 = [];
        #print(co2avg)
        return co2

    def getCO2Avgr(self, minutes, timestamp):
        loopCount = 0;
        co2 = 0;
        try:
            timestamp = self._calcLookuptime(timestamp)
            while (0<=minutes):
                timestr = self._formatLookuptime(timestamp)
                co2 = co2 + self._GetCO2Data(timestr)
                minutes = minutes - 15
                timestamp = timestamp - timedelta(0, 0, 0, 0, 15)
                loopCount = loopCount +1 
                #print(timestr)
                #print(co2)
            co2avg = round(co2/loopCount)
        except:
            co2avg = ' '
        #print(co2avg)
        return co2avg
"""
#test code
fetch = CO2Fetcher()
now = datetime.now()
fetch.getCO2Prognosis(120, now)
"""