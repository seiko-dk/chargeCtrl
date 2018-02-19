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


    
    
send("hej")
uart = '/dev/ttyUSB0'

modbusClient = ModbusClient.ModbusClient(uart)
modbusClient.UnitIdentifier = 16                    #Set slave ID
modbusClient.Parity = ModbusClient.Parity.none
modbusClient.Connect()
modbusClient.ser.setDTR(False)                      #Enable autogating (half-duplex)


fileConfig('logging_config.ini')
logger = logging.getLogger()

i = 1
while (i > 0):
    getIO()
    i=i-1
    sleep(1)
    

modbusClient.close()
