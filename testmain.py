from time import sleep
import time
import logging
from logging.config import fileConfig
from enum import Enum
from datetime import datetime
import signal
import sys
import json
import math
from scheduler import ChargeControl
from datetime import timedelta


#UART = '/dev/ttyUSB0'
UART = 'simulate'

fileConfig('logging_config.ini')
logger = logging.getLogger()

"""
btn off
Power is on.
between 17-20 is powered off 1-2 min after connection.
Power is kept on after charge until disconnection
Every minute the file is read. Power can be limited to 0-8 hours. Default behaviour is used after disconnect

btn on
always power on

Add comments.
Add CO2 data to status
"""

config = {
    'power_off': [16, 17, 18, 19, 20, 21, 22, 23],
    'charged_hour': 6,
    }

now = datetime.now()
now = datetime(2018,5,1, 23, 59,0)
secCount = time.time()

schedule = ChargeControl(logger, now, secCount, UART)

def gracefull_shutdown(sig, frame):
        if(0 == sig):
                logger.info('This is the end my friend, the end')
        elif (signal.SIGINT == sig):
                logger.info('SIGINT received')
        elif (signal.SIGTERM == sig):
                logger.info('SIGTERM received')
        else:
                logger.info('Something happened. Shutting down')
        schedule._charger.chargeEnabled = True
        sys.exit(0)

signal.signal(signal.SIGINT, gracefull_shutdown)
signal.signal(signal.SIGTERM, gracefull_shutdown)

#try:
#run forever, but while debugging it can be nice to limit loop
i = 8    #20 hours
schedule._powerCountDown = 5;
while (i > 0):
    print(now.hour, ":", now.minute)
    print("seccount ", secCount)
    
    schedule._step(now, secCount, config)
    now = now + timedelta(0,0,0,0,1)
    secCount = secCount + 60
    i = i - 1

gracefull_shutdown(0, 0)
#except:
    #ensure that charging is enabled if something goes wrong
#    gracefull_shutdown(0, 0)
