#!/usr/bin/python3
import sys
import os
import time
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

numberOfSupportedDevices = 9  # limit number of smarthome devices

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

def publishOne(topic,value):
	log('publish [%s] = [%s]' % (topic, str(value) ) )
	client.publish(topic, str(value), qos=0, retain=True)


def on_connect(client, userdata, flags, rc):
    global devicenumber, doneread
#    subscribeOne("openWB/SmartHome/set/Devices/"+devicenumber+"/#")
    doneread=0


def on_message(client, userdata, msg):
    global numberOfSupportedDevices


devicenumber = str(sys.argv[1])
ipadr = str(sys.argv[2])
uberschuss = int(sys.argv[3])

initlog(devicenumber)
log('mqtt/on.py Device:%d ip:%s neuer ueberschuss:%d' % (int(devicenumber), ipadr, uberschuss ))


client = mqtt.Client("openWB-mqttsmarthomecust")
client.on_connect = on_connect
client.on_message = on_message
startTime = time.time()
waitTime = 2
client.connect("localhost")
# while True:
#    client.loop()
#    elapsedTime = time.time() - startTime
#    if elapsedTime > waitTime:
#        break
log('ueberschuss %6d /ReqRelay = 1' % (uberschuss))

publishOne("openWB/SmartHome/set/Devices/"+str(devicenumber) + "/ReqRelay", "1" )
client.loop(timeout=0.2)
publishOne("openWB/SmartHome/set/Devices/"+str(devicenumber) + "/Ueberschuss", str(uberschuss) )
client.loop(timeout=0.2)
client.disconnect()

file_stringpv = '/var/www/html/openWB/ramdisk/sm/device_' + str(devicenumber) + '_pv'
log('write 1 to %s' % (file_stringpv) )
f = open(file_stringpv, 'w')
f.write(str(1))
f.close()
