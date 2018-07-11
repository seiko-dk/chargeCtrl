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
import os
from scheduler import ChargeControl
from datetime import timedelta
from scheduler import STATUS_FILENAME


UART = '/dev/ttyUSB0'
#UART = 'simulate'

"""Before we do anything, check that we are not already running
"""


fil = datetime.fromtimestamp(int(os.path.getmtime(STATUS_FILENAME)))
#print(fil)
current = datetime.fromtimestamp(int(time.time()))
#print(current)
diff = current - fil
#print (diff)
if (timedelta(seconds = 5*60) > diff):
    print("We are running")
    print (diff)
    quit()
#else:
#    print("We are NOT running")

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
"""

config = {
    'power_off': [16, 17, 18, 19, 20, 21, 22, 22, 23],
    'charged_hour': 6,
    }

now = datetime.now()
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

try:
    while (1):
        schedule.run(config)

    gracefull_shutdown(0, 0)
finally:
    #ensure that charging is enabled if something goes wrong
    gracefull_shutdown(0, 0)
