from EasyModbus import ModbusClient
from time import sleep

def send (data):
    print (data)
    
    
    
send("hej")
uart = '/dev/ttyUSB0'

modbusClient = ModbusClient.ModbusClient(uart)
modbusClient._unitIdentifier = 16
modbusClient._parity =  2
modbusClient.Connect()
modbusClient.ser.setDTR(False)

res = modbusClient.ReadHoldingRegisters(24004, 2)
print(res)
modbusClient.close()
