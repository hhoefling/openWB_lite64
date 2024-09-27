#!/usr/bin/python3
import sys
import os
import os.path
# import time
# import getopt
# import socket
# import ConfigParser
import struct
# import binascii
from pymodbus.client.sync import ModbusSerialClient


seradd = str(sys.argv[1])
sdmid = int(sys.argv[2])
# on 64 /dev/ttyUSB0 105
seradd = "/dev/ttyUSB0"
sdmid = 105

client = ModbusSerialClient(method="rtu", port=seradd, baudrate=9600, stopbits=1, bytesize=8, timeout=1)

def writeramdisk(fn,val):
	print("%s = [%s]" % (fn,val) )


if (sdmid < 100):
    f.close()
else:
    resp = client.read_input_registers(0x00, 2+2+2, unit=sdmid)
    v1 = struct.unpack('>f', struct.pack('>HH', *resp.registers[0:2]))[0]  # item 0,1
    v2 = struct.unpack('>f', struct.pack('>HH', *resp.registers[2:4]))[0]  # item 2,3
    v3 = struct.unpack('>f', struct.pack('>HH', *resp.registers[4:6]))[0]  # item 4,5
    writeramdisk('llv1', "{:.1f}".format(v1) )
    writeramdisk('llv2', "{:.1f}".format(v2))
    writeramdisk('llv3', "{:.1f}".format(v3))



    resp = client.read_input_registers(0x06, 2+2+2, unit=sdmid)
    a1 = float(struct.unpack('>f', struct.pack('>HH', *resp.registers[0:2]))[0])
    a2 = float(struct.unpack('>f', struct.pack('>HH', *resp.registers[2:4]))[0])
    a3 = float(struct.unpack('>f', struct.pack('>HH', *resp.registers[4:6]))[0])
    writeramdisk('lla1', "{:.1f}".format(a1) )
    writeramdisk('lla2', "{:.1f}".format(a2))
    writeramdisk('lla3', "{:.1f}".format(a3))


    resp = client.read_input_registers(0x0C, 2+2+2, unit=sdmid)
    w1 = int(float(struct.unpack('>f', struct.pack('>HH', *resp.registers[0:2]))[0]))
    w2 = int(float(struct.unpack('>f', struct.pack('>HH', *resp.registers[2:4]))[0]))
    w3 = int(float(struct.unpack('>f', struct.pack('>HH', *resp.registers[4:6]))[0]))
    llg = w1 + w2 + w3
    if llg < 10:
        llg = 0
    writeramdisk('llaktuell', str(llg) )
    
    resp = client.read_input_registers(0x46, 2, unit=sdmid)
    hz = struct.unpack('>f', struct.pack('>HH', *resp.registers))[0]
    writeramdisk('llhz', "{:.2f}".format(hz) )
    

    resp = client.read_input_registers(0x1E, 2+2+2, unit=sdmid)
    pf1 = struct.unpack('>f', struct.pack('>HH', *resp.registers[0:2]))[0]
    pf2 = struct.unpack('>f', struct.pack('>HH', *resp.registers[2:4]))[0]
    pf3 = struct.unpack('>f', struct.pack('>HH', *resp.registers[4:6]))[0]
    writeramdisk('llpf1', "{:.3f}".format(pf1))
    writeramdisk('llpf2', "{:.3f}".format(pf2))
    writeramdisk('llpf3', "{:.3f}".format(pf3))


    if not os.path.isfile("/var/www/html/openWB/ramdisk/lp1Serial"):
        print("Trying to read meter serial number once from meter at address " + str(seradd) + ", ID " + str(sdmid))
        try:
            resp = client.read_holding_registers(0xFC00, 2, unit=sdmid)
            sn = struct.unpack('>I', struct.pack('>HH', *resp.registers))[0]
            writeramdisk('lp1Serial', str(sn) )
        except:
            print("Meter serial number of meter at address " + str(seradd) + ", ID " + str(sdmid) + " is not available")
            writeramdisk('lp1Serial', '0')
