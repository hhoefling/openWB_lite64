#!/usr/bin/python3
# used for Satellit (ohne PI, ipevse)
import sys
from pymodbus.client.sync import ModbusTcpClient

ipadd = str(sys.argv[1])
modbusid = int(sys.argv[2])
readreg = int(sys.argv[3])
reganzahl = int(sys.argv[4])

client = ModbusTcpClient(ipadd, port=8899)
rq = client.read_holding_registers(readreg, reganzahl, unit=modbusid)

client.close()
print(rq.registers[0])
