#!/usr/bin/python3
import sys
import os
import time
import json
import paho.mqtt.client as mqtt
import re
from datetime import datetime, timezone

numberOfSupportedDevices = 9  # limit number of smarthome devices
doneread=0	# bitmap 

def initlog(devicenummer):
	global logfx
	file_string = '/var/www/html/openWB/ramdisk/sm/device_' + str(devicenumber) + '_mqtt.log'
	if os.path.isfile(file_string):
		logfx = open(file_string, 'a')
	else:
		logfx = open(file_string, 'w')


def log(message):
	local_time = datetime.now(timezone.utc).astimezone()
	my_pid = str(os.getpid())
	print(local_time.strftime(format="%Y-%m-%d %H:%M:%S") + " " + my_pid + ": " + message , file=logfx )

# erscheint als ERROR in mainlog
def mlog(message):
	my_pid = str(os.getpid())
	print(my_pid + ": " + message , file=sys.stderr )

def	subscribeOne(topic):
    log('subs %s ' % (topic))
    client.subscribe(topic, 2)

def on_connect(client, userdata, flags, rc):
    global devicenumber, doneread
    subscribeOne("openWB/SmartHome/set/Devices/"+devicenumber+"/Aktpower")
    subscribeOne("openWB/SmartHome/set/Devices/"+devicenumber+"/Powerc")
    doneread=0


def on_message(client, userdata, msg):
    global numberOfSupportedDevices, doneread
    global aktpower
    global powerc
    if (("openWB/SmartHome/set/Device" in msg.topic) and ("Aktpower" in msg.topic)):
        devicenumb = re.sub(r'\D', '', msg.topic)
        if (1 <= int(devicenumb) <= numberOfSupportedDevices):
            aktpower = int(msg.payload)
            log ('RESC get Aktpower=[%d] ' % (aktpower))
            doneread |= 1	# bitmap
    elif (("openWB/SmartHome/set/Device" in msg.topic) and ("Powerc" in msg.topic)):
        devicenumb = re.sub(r'\D', '', msg.topic)
        if (1 <= int(devicenumb) <= numberOfSupportedDevices):
            powerc = int(msg.payload)
            log ('RESC get Powerc=[%d] ' % (powerc))
            doneread |= 2	# bitmap
    else:
        log ('RESC ignore [%s] = [%s]' % (msg.topic, msg.payload.decode("utf-8") ))
        mlog ('mqtt.py RESC ignore [%s] = [%s]' % (msg.topic, msg.payload.decode("utf-8") ))

aktpower = 0
powerc = 0
devicenumber = str(sys.argv[1])
ipadr = str(sys.argv[2])
uberschuss = int(sys.argv[3])

initlog(devicenumber)
log('mqtt/watt.py Device:%d ip:%s neuer ueberschuss:%d' % (int(devicenumber), ipadr, uberschuss ))

client = mqtt.Client("openWB-mqttsmarthomecust" + devicenumber)
client.on_connect = on_connect
client.on_message = on_message
startTime = time.time()
waitTime = 2
client.connect("localhost")
while True:
	client.loop()
	elapsedTime = time.time() - startTime
	if elapsedTime > waitTime:
		break
	if doneread==3:	# bitmap
		break
topic="openWB/SmartHome/set/Devices/"+str(devicenumber) +"/Ueberschuss"
log('publish [%s] = [%s]' % (topic, str(uberschuss)) ) 
client.publish(topic, str(uberschuss), qos=0, retain=True)
client.loop(timeout=2.0)
client.disconnect()
file_stringpv = '/var/www/html/openWB/ramdisk/sm/device_' + str(devicenumber) + '_pv'
pvmodus = 0
if os.path.isfile(file_stringpv):
	f = open(file_stringpv, 'r')
	pvmodus = int(f.read())	# 1 = Shut be switch on, pv ist genug da
	log('read %s [%d]' % (file_stringpv, pvmodus) )
	f.close()
answer = '{"power":' + str(aktpower) + ',"powerc":' + str(powerc) + ',"on":' + str(pvmodus) + '} '

f1 = open('/var/www/html/openWB/ramdisk/sm/device_ret' + str(devicenumber), 'w')
json.dump(answer, f1)
f1.close()

log('Answer is %s' % (answer))
logfx.close()
