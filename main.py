from time import sleep
import time
import logging
from logging.config import fileConfig
from chargerInterface import ChargerIf
from enum import Enum
from datetime import datetime
import signal
import sys
import json
import math
from co2fetch import CO2Fetcher

UART = '/dev/ttyUSB0'
#UART = 'simulate'

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
POWER_OFF_START = 16
POWER_OFF_END   = 22
POWER_LIMIT_FILENAME = 'pwr.txt'
POWER_LIMIT_DEFAULT = 1000000000

STATUS_FILENAME = 'status.txt'

class chargeStates(Enum):
    init = 0
    powerOnForced = 1
    powerOnPeriodWaitForConnection = 2
    powerOnPeriodConnected = 3
    powerOffPeriodWaitForConnection = 4
    powerOffPeriodConnected = 5
    chargeComplete = 6
    
    

class ChargeControl(object):

    def __init__(self, log):
        self._logger = log
        self._summary = logging.getLogger('summary')

        self._currentState = chargeStates.init
        self._nextState = chargeStates.init
        self._charger = ChargerIf(UART, log)
        
        timeT = datetime.now()
        self._lastRunMin = timeT.minute - 1
        self._lastRunHour = timeT.hour -1
        
        self._powerCountDown = POWER_LIMIT_DEFAULT
        
        self._chargeStartTimeStamp = time.time()

    def _statePowerOnForced(self):
         self._charger.chargeEnabled = True
         self._powerCountDown = POWER_LIMIT_DEFAULT
            
    def _statePowerOn(self):
         self._charger.chargeEnabled = True

    def _statePowerOff(self):
         self._charger.chargeEnabled = False

    def _statePowerOffWaitForConnection(self):
         self._charger.chargeEnabled = True

    def _powerOffPeriodConnected(self):
        #ensure power is on, then wait one minute, then disconnect power
         self._charger.chargeEnabled = True
         self._chargeStartTimeStamp = time.time()
         sleep(30)
         self._charger.updateIO()
         if (not self._charger.buttonEnabled):  
             self._charger.chargeEnabled = False

    def _stateChargeComplete(self):
         if (not self._charger.buttonEnabled):  
             self._charger.chargeEnabled = False

    def run(self):
        now = datetime.now()
        #Poll button status and command file every minute
        if (self._lastRunMin == now.minute):
            diffSec = 60 - now.second
#            diffSec = 1
            sleep(diffSec)
        wasCharging = self._charger.charging
        self._charger.updateIO()
        isCharging = self._charger.charging
        now = datetime.now()
        self._lastRunMin = now.minute

        #Detect button state
        if (self._charger.buttonEnabled):
            self._nextState = chargeStates.powerOnForced
        else:
            #The button is not pressed, so lets have a look at the time
            if (POWER_OFF_START > now.hour or POWER_OFF_END <= now.hour):
                # We are not in the poweroff period 
                if (self._charger.connected):
                    self._nextState = chargeStates.powerOnPeriodConnected
                else:
                    self._nextState = chargeStates.powerOnPeriodWaitForConnection
                    self._powerCountDown = POWER_LIMIT_DEFAULT
            elif (POWER_OFF_START <= now.hour and POWER_OFF_END > now.hour):
                # We are now in the poweroff period
                if (self._charger.connected):
                    self._nextState = chargeStates.powerOffPeriodConnected
                else:
                    self._nextState = chargeStates.powerOffPeriodWaitForConnection
                    self._powerCountDown = POWER_LIMIT_DEFAULT

            #Perform file IO
            try:
                with open(POWER_LIMIT_FILENAME, 'r') as f:
                    pwrlimit = int(f.read())
                    f.closed
            except:
                pwrlimit = 0
                with open(POWER_LIMIT_FILENAME, 'w') as f:
                    f.write('0')
                f.closed
                
                
            
            if (0<pwrlimit):
                with open(POWER_LIMIT_FILENAME, 'w') as f:
                    f.write('0')
                f.closed
                self._powerCountDown = pwrlimit
                logger.info('Limited charge to %u minutes', self._powerCountDown)
                
                
            if (0 < self._powerCountDown and POWER_LIMIT_DEFAULT != self._powerCountDown):
                if (self._charger.charging):
                    self._powerCountDown = self._powerCountDown -1
    
            if (0 == self._powerCountDown):
                self._nextState = chargeStates.chargeComplete
                self._powerCountDown = POWER_LIMIT_DEFAULT
                logger.info('Charge time limit reached. Stopping charge')

        #Act on the new states
        if(self._nextState != self._currentState):
            if (chargeStates.powerOnForced == self._nextState):
                self._statePowerOnForced()
            elif (chargeStates.chargeComplete == self._currentState):
                if (chargeStates.powerOffPeriodConnected == self._nextState or chargeStates.powerOnPeriodConnected == self._nextState):
                    self._stateChargeComplete()
                    self._nextState = self._currentState #prevent statechange
                else:
                    self._powerCountDown = POWER_LIMIT_DEFAULT
                    self._statePowerOn()
            elif (chargeStates.powerOnPeriodConnected == self._nextState or chargeStates.powerOnPeriodWaitForConnection == self._nextState):
                self._statePowerOn()
            elif (chargeStates.powerOffPeriodWaitForConnection == self._nextState):
                self._statePowerOffWaitForConnection()
            elif (chargeStates.powerOffPeriodConnected == self._nextState):
                if (chargeStates.powerOnPeriodConnected == self._currentState):
                    self._statePowerOff()
                else:
                    self._powerOffPeriodConnected()

        #Write consumption data
        if (isCharging and not wasCharging):
            #Charge is started
            self._chargeStartTimeStamp = time.time()
        elif (wasCharging and not isCharging):
            #charge is stopped. Calculate the charge time and energy transferred
            diff = time.time() - self._chargeStartTimeStamp
            min = int(round(diff/60))
            hour = math.floor(min / 60)
            rem = math.floor(min % 60)
            kWh = (min * 3.7) / 60

            fetch = CO2Fetcher()
            now = datetime.now()
            co2avgr = fetch.getCO2Avgr(min, now)

            logger.info('Charge time % 2u:%02u %.02f kWh %s gCO2/kWh', hour, rem, kWh, co2avgr)
            self._summary.info('% 2u:%02u, %.02f, %s', hour, rem, kWh, co2avgr)


        if(self._nextState != self._currentState):
            self._logger.info('%s -> %s', self._currentState, self._nextState)
            self._currentState = self._nextState

        #now = datetime.now()
        stateinfo = {'time': now.ctime(),
                     'currentState': self._currentState.name,
                     'button': self._charger.buttonEnabled, 
                     'connected': self._charger.connected, 
                     'charging': self._charger.charging, 
                     'chargeEnabled': self._charger.chargeEnabled,
                     'limitRemaining': self._powerCountDown,
                     }

#        print(stateinfo)

        try:
            with open(STATUS_FILENAME, 'w') as f:
                json.dump(stateinfo, f)
            f.closed
        except Exception:
            pass

schedule = ChargeControl(logger)

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
i = 20    #20 hours
while (i > 0):
    schedule.run()
    i = i - 1

gracefull_shutdown(0, 0)
#except:
    #ensure that charging is enabled if something goes wrong
#    gracefull_shutdown(0, 0)
