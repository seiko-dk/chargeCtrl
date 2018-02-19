from EasyModbus import ModbusClient
from time import sleep

def send (data):
    print (data)
    
def getIO():
    res = modbusClient.ReadHoldingRegisters(24004, 2)
    print(res)
    return res


    
    
send("hej")
uart = '/dev/ttyUSB0'

modbusClient = ModbusClient.ModbusClient(uart)
modbusClient.UnitIdentifier = 16                    #Set slave ID
modbusClient.Parity = ModbusClient.Parity.none
modbusClient.Connect()
modbusClient.ser.setDTR(False)                      #Enable autogating (half-duplex)

getIO()
modbusClient.close()
