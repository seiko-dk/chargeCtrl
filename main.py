import logging
from logging.config import fileConfig
from chargerInterface import ChargerIf

uart = '/dev/ttyUSB0'
fileConfig('logging_config.ini')
logger = logging.getLogger()

charger = ChargerIf(uart, logger)

"""
btn off
Power on charging at 20:00
Power off at 17:00

btn on
always power on
"""

i = 19 * 60    #20 hours
while (i > 0):
    charger.updateIO();
    i = i - 1
    sleep(60)

