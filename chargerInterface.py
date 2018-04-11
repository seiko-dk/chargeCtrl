from EasyModbus import ModbusClient
from time import sleep
import logging
from logging.config import fileConfig
from datetime import datetime
import time
import math
from co2fetch import CO2Fetcher

DEBUG_IF_FILENAME = 'debugif.txt'

class ChargerIf(object):

    def __init__(self, uart, log):
        self._logger = log
        self._logger.info('Initializing charger')
        self._summary = logging.getLogger('summary')
        self._btnEnabled = False
        self._xr = False        #external Release
        self._ml = False
        self._ccr = False
        self._in = False
        
        self._out = False
        self._err = False
        self._charging = False
        self._connected = False
        
        self._oldIO = [-1, -1]      #invalid value to ensure status is written after initialisation
        self._chargeEnabled = False;
        
        self._simulate = False;
        if (uart != 'simulate'):
            self._modbusClient = ModbusClient.ModbusClient(uart)
            self._modbusClient.UnitIdentifier = 16  # Set slave ID
            self._modbusClient.Parity = ModbusClient.Parity.none
            self._modbusClient.Connect()
            self._modbusClient.ser.setDTR(False)  # Enable autogating (half-duplex)
            self.chargeEnabled = True
            self.chargeModeCfg()
        else:
            self._logger.warning('Simulating communication')
            self._simulate = True;
            self._simulateInput = [0x0, 0x08, 0x08, 0x08, 0x08, 0x08, 0x04, 0x0]    #This is reversed. End is read first
            self._simulateIndex = self._simulateInput  

        self._chargeStartTimeStamp = time.time()

#    def __del__(self):
#        self._modbusClient.close()

    @property
    def chargeEnabled(self):
        return self._chargeEnabled

    @chargeEnabled.setter
    def chargeEnabled(self, enabled):
#        res = self._modbusClient.ReadCoils(20000,1)
#        logger.debug('ChargeEnable[20.000] read: %s', res)
        update = False
        if (self._chargeEnabled != enabled):
            update = True
        
        if (enabled):
            self._chargeEnabled = True
            if(update):
                self._logger.info('Charge is enabled')
        else:
            self._chargeEnabled = False
            if(update):
                self._logger.info('Charge is disabled')

        if (update):
            if (not self._simulate):
                self._modbusClient.WriteSingleCoil(20000, self._chargeEnabled)
            self._logger.debug('ChargeEnable[20.000] set: %s', self._chargeEnabled)


    def chargeModeCfg(self):
        res = 3
        res = self._modbusClient.ReadHoldingRegisters(4000, 1)
        if ([3]!=res):
            self._modbusClient.WriteSingleRegister(4000, 3)
            res = self._modbusClient.ReadHoldingRegisters(4000, 1)
            self._logger.debug('ChargeCtrl[4.000] read: %s', res)
        self._logger.info('Charge remote control is enabled')

    def _parseIO(self, IO):
        inputs = IO[0]
        outputs = IO[1]
        
        dbg_string = ''
        
        if (inputs & 0x01):
            self._btnEnabled = True
            dbg_string = dbg_string + 'BTN '
        else:
            self._btnEnabled = False

        if (inputs & 0x02):
            dbg_string = dbg_string + 'XR '
            self._xr = True
        else:
            self._xr = False

        if (inputs & 0x04):
            dbg_string = dbg_string + 'ML '
            self._ml = True
        else:
            self._ml = False

        if (inputs & 0x08):
            dbg_string = dbg_string + 'CCR '
            self._ccr = True
        else:
            self._ccr = False

        if (inputs & 0x10):
            dbg_string = dbg_string + 'IN '
            self._in = True
        else:
            self._in = False
        
            
        if (outputs & 0x01):
            dbg_string = dbg_string + 'OUT '
            self._out = True
        else:
            self._out = False

        if (outputs & 0x02):
            dbg_string = dbg_string + 'ERR '
            self._err = True
        else:
            self._err = False

        if (outputs & 0x04):
            dbg_string = dbg_string + 'CHARGE '
            self._charging = True
        else:
            self._charging = False

        if (outputs & 0x08):
            dbg_string = dbg_string + 'CONNECTED '
            self._connected = True
        else:
            self._connected = False
            
        if (self._oldIO!=IO):
            self._logger.info('IO update: ' + dbg_string)

            o = self._oldIO[1] & 0x04
            n = IO[1] & 0x04
            if (n and not o):
                #Charge is started
                self._chargeStartTimeStamp = time.time()
            elif (o and not n):
                #charge is stopped. Calculate the charge time and energy transferred
                diff = time.time() - self._chargeStartTimeStamp
                min = int(round(diff/60))
                hour = math.floor(min / 60)
                rem = math.floor(min % 60)
                kWh = (min * 3.7) / 60
                
                fetch = CO2Fetcher()
                now = datetime.now()
                co2avgr = fetch.getCO2Avgr(min, now)
				
                self._logger.info('Charge time % 2u:%02u %f kWh %s gCO2/kWh', hour, rem, kWh, co2avgr)
                self._summary.info('% 2u:%02u, %f, %s', hour, rem, kWh, co2avgr)
                  
        
    def updateIO(self):
        if (not self._simulate):
            res = self._modbusClient.ReadHoldingRegisters(24004, 2)
        else:
            res = [0, 12]
        self._logger.debug('IO[24.004,24.005]: %s', res)
        self._parseIO(res)
        self._oldIO = res

    @property
    def buttonEnabled(self):
        return self._btnEnabled

    @property
    def charging(self):
        return self._charging

    @property
    def connected(self):
        return self._connected

    @property
    def error(self):
        return self._err

    @property
    def outputSet(self):
        return self._out
