#!/usr/bin/python3
import sys
import os
import time
import json
named_tuple = time.localtime()  # getstruct_time
time_string = time.strftime("%m/%d/%Y, %H:%M:%S viessmann watty.py", named_tuple)
devicenumber = str(sys.argv[1])
ipadr = str(sys.argv[2])
uberschuss = int(sys.argv[3])
file_stringpv = '/var/www/html/openWB/ramdisk/sm/device_' + str(devicenumber) + '_pv'
# PV-Modus
pvmodus = 0
if os.path.isfile(file_stringpv):
    f = open(file_stringpv, 'r')
    pvmodus = int(f.read())
    f.close()
aktpower = 0
powerc = 0
answer = '{"power":' + str(aktpower) + ',"powerc":' + str(powerc) + ',"on":' + str(pvmodus) + '} '
f1 = open('/var/www/html/openWB/ramdisk/sm/device_ret' + str(devicenumber), 'w')
json.dump(answer, f1)
f1.close()
