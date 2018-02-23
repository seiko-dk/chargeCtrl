from EasyModbus import ModbusClient
from time import sleep
import logging
from logging.config import fileConfig

def send (data):
    print (data)

def getIO():
    res = modbusClient.ReadHoldingRegisters(24004, 2)
    logger.debug('IO: %s', res)
    return res


#send("hej")
uart = '/dev/ttyUSB0'

class ChargerIf(object):
	def __init__(self, *params):
		self._charging = 0
		self._connected = 0
		self._btnEnabled = 0

	def update(self, inputs, outputs):
		self._btnEnabled = 1

modbusClient = ModbusClient.ModbusClient(uart)
modbusClient.UnitIdentifier = 16                    #Set slave ID
modbusClient.Parity = ModbusClient.Parity.none
modbusClient.Connect()
modbusClient.ser.setDTR(False)                      #Enable autogating (half-duplex)

charger = ChargerIf()
charger.update(0,1)


fileConfig('logging_config.ini')
logger = logging.getLogger()

i = 1 #24 * 60	#20 hours
while (i > 0):
    getIO()
    i=i-1
#    sleep(60)


modbusClient.close()
