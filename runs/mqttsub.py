#!/usr/bin/python3
import configparser
import fileinput
import re
import subprocess
# import sys
import threading
import time
from datetime import datetime
from json import loads as json_loads
from json.decoder import JSONDecodeError
import paho.mqtt.client as mqtt
# import os
# from pathlib import Path
# from subprocess import run

inaction = 0
openwbconffile = "/var/www/html/openWB/openwb.conf"
config = configparser.ConfigParser()
shconfigfile = '/var/www/html/openWB/smarthome.conf'
numberOfSupportedDevices = 9   # limit number of smarthome devices
numberOfSupportedLP = 3     # limit number of LP devices, lite=3 openWB=8
debug = 0
OPENWB = "openWB/"
RequestYearGraphv1 = 0
ipallowed = '^[0-9.]+$'
nameallowed = '^[0-9a-zA-Z- \_\.]+$'
namenumballowed = '^[0-9a-zA-Z ]+$'
emailallowed = '^([\w\.]+)([\w]+)@(\w{2,})\.(\w{2,})$'


lock = threading.Lock()


def dolog(msg):
    timestamp = datetime.now().strftime(format="%Y-%m-%d %H:%M:%S")
    file = open('/var/www/html/openWB/ramdisk/mqtt.log', 'a')
    file.write("%s %s \n" % (timestamp, msg))
    file.close()


dolog(" -------------------")

config.read(shconfigfile)
dolog("configfile [%s] read, for check." % (shconfigfile))

for i in range(1, (numberOfSupportedDevices + 1)):
    try:
        confvar = config.get('smarthomedevices', 'device_configured_' + str(i))
    except Exception:
        try:
            config.set('smarthomedevices', 'device_configured_' + str(i), str(0))
            dolog("configfile SET device_configured_%s = 0" % (str(i)))
        except Exception:
            config.add_section('smarthomedevices')
            config.set('smarthomedevices', 'device_configured_' + str(i), str(0))
            dolog("configfile ADD device_configured_%s = 0" % (str(i)))
with open(shconfigfile, 'w') as f:
    config.write(f)
    dolog("configfile [%s] rewritten" % (shconfigfile))


def writetoSHconfig(section, key, value):
    global ramdisk
    global shconfigfile
    config.read(shconfigfile)
    dolog("  writeShConfig [%s] = [%s]" % (key, value))
    try:
        config.set(section, key, value)
    except Exception:
        config.add_section(section)
        config.set(section, key, value)
    with open(shconfigfile, 'w') as f:
        config.write(f)
    ramdisk.write('reread' + str(section), "1")
#    try:
#        f = open('/var/www/html/openWB/ramdisk/reread' + str(section), 'w+')
#        f.write(str(1))
#        f.close()
#    except Exception as e:
#        print(str(e))


def publish0r(topic, payload):
    global client
    dolog("  publish: [%s%s] = [%s] " % (OPENWB, topic, payload))
    client.publish(OPENWB + topic, payload, qos=0, retain=True)

#
# mit einsetzen der devoceid
#    publish0rd("config/get/SmartHome/Devices/%d/device_configured", devnr, payload)
def publish0rd(topic, nr, payload):
    global client
    topic = topic % (nr)
    dolog("  publish: [%s%s] = [%s] " % (OPENWB, topic, payload))
    client.publish(OPENWB + topic, payload, qos=0, retain=True)


def replaceinconfig(changeval, newval):
    sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", changeval, newval]
    subprocess.run(sendcommand)
    dolog("  replaceinconfig.sh %s [%s]" % (changeval, newval))


def xsubprocess(xcommand):
    subprocess.run(xcommand)
    dolog("  subprocess run [%s]" % (xcommand))


#  "sofortsocstatlp1=", msg.payload.decode("utf-8"))
def replaceAll(changeval, newval):
    global inaction
    if (inaction == 0):
        inaction = 1
        for line in fileinput.input(openwbconffile, inplace=1):
            if line.startswith(changeval):
                line = changeval + newval + "\n"
                dolog("  replaceAll line [%s]" % (line))
            # sys.stdout.write(line)
        time.sleep(0.1)
        inaction = 0

#
# def getConfigValue(key):
#    for line in fileinput.input(openwbconffile):
#        if line.startswith(str(key + "=")):
#            return line.split("=", 1)[1]
#    return
#


def getserial():
    # Extract serial from cpuinfo file
    with open('/proc/cpuinfo', 'r') as f:
        for line in f:
            if line[0:6] == 'Serial':
                return line[10:26]
        return "0000000000000000"


#
# ############################################
class Ramdisk:
    def __init__(self, rambase):
        self.rambase = rambase
        dolog("Ramdisk is [%s]" % (rambase))

    def write(self, name, val):
        global debug
        fn = self.rambase + '/' + name
        try:
            with open(fn, 'r') as f:
                oldval = f.read().rstrip("\n")
        except Exception:
            oldval = ""
        if val != oldval:
            with open(fn, 'w') as f:
                f.write(str(val))
            if debug > 0:
                dolog("  write ramdisk %s = [%s] old[%s] " % (fn, val, oldval))
        else:
            if debug > 0:
                dolog("  Not write ramdisk %s = [%s] Same value" % (fn, val))
        return True

    def readint(self, name, defval='0'):
        global debug
        fn = self.rambase + '/' + name
        try:
            with open(fn, 'r') as f:
                val = f.read().rstrip("\n")
        except Exception:
            val = defval
            dolog("ramdisk.readint %s  not found used default [%s]" % (fn, val))
            return int(val)
        if debug > 0:
            dolog("read ramdiskI %s = [%s]" % (fn, val))
        return int(val)

    def readfloat(self, name, defval='0.0'):
        global debug
        fn = self.rambase + '/' + name
        try:
            with open(fn, 'r') as f:
                val = f.read().rstrip("\n")
        except Exception:
            val = defval
            dolog("ramdisk.readfloat %s  not found used default [%s]" % (fn, val))
        else:
            if debug > 0:
                dolog("read ramdiskF %s = [%s]" % (fn, val))
        return float(val)

    def readstr(self, name, defval=''):
        global debug
        fn = self.rambase + '/' + name
        try:
            with open(fn, 'r') as f:
                val = f.read().rstrip("\n")
        except Exception:
            val = defval
            dolog("ramdisk.readstr %s  not found used default [%s]" % (fn, val))
        else:
            if debug > 0:
                dolog("read ramdiskS %s = [%s]" % (fn, val))
        return str(val)


#############################################


mqtt_broker_ip = "localhost"
client = mqtt.Client("openWB-mqttsub-" + getserial())

ramdisk = Ramdisk('/var/www/html/openWB/ramdisk')

debug = ramdisk.readint('debug')
dolog("mqttsub starting, debug=%d " % (debug))

# dolog("int [%s] " %  ramdisk.readint('int'))
# dolog("int [%s] nf" %  ramdisk.readint('intx'))
# dolog("int [%s] nf" %  ramdisk.readint('intx',0))
# dolog("float [%s] " %  ramdisk.readfloat('float'))
# dolog("float [%s] " %  ramdisk.readfloat('float2'))
# dolog("float [%s] nf" %  ramdisk.readfloat('float3',0.0))
# dolog("str [%s] " %  ramdisk.readstr('str'))
# dolog("str [%s] " %  ramdisk.readstr('str', 'a'))
# dolog("str [%s] nf" %  ramdisk.readstr('str3', 'none'))


# connect to broker and subscribe to set topics
def on_connect(client, userdata, flags, rc):
    client.subscribe("openWB/set/#", 2)
    client.subscribe("openWB/config/set/#", 2)

# toks=[]
# tok=""
# allt=[]
#
# def gett():
#    global tok
#    if( tok):
#        allt.append(tok)
#    tok=toks.pop(0)
#    # dolog("token:[%s] rest %s "%(tok,toks))
#    return tok
#


def processSmartHomeDevice(topic, payload):
    global numberOfSupportedDevices, client, ramdisk
    di = int(re.sub(r'\D', '', topic))
    ds = str(di)
    if (di < 1 or di > numberOfSupportedDevices):
        dolog("SMartHomeTopic: " + topic + " illegal Device Nr")
        return

    if ("device_configured" in topic):
        if (0 <= int(payload) <= 1):
            writetoSHconfig('smarthomedevices', 'device_configured_' + ds, payload)
            publish0rd("config/get/SmartHome/Devices/%s/device_configured",di, payload)
    elif ("device_canSwitch" in topic):
        if (0 <= int(payload) <= 1):
            writetoSHconfig('smarthomedevices', 'device_canSwitch_' + ds, payload)
            publish0rd("config/get/SmartHome/Devices/%d/device_canSwitch", di, payload)
    elif ("device_differentMeasurement" in topic):
        if (0 <= int(payload) <= 1):
            writetoSHconfig('smarthomedevices', 'device_differentMeasurement_' + ds, payload)
            publish0rd("config/get/SmartHome/Devices/%d/device_differentMeasurement", di, payload)
    elif ("device_chan" in topic):
        if (0 <= int(payload) <= 6):
            writetoSHconfig('smarthomedevices', 'device_chan_' + ds, payload)
            publish0rd("config/get/SmartHome/Devices/%d/device_chan", di, payload)
    elif ("device_measchan" in topic):
        if (0 <= int(payload) <= 6):
            writetoSHconfig('smarthomedevices', 'device_measchan_' + ds, payload)
            publish0rd("config/get/SmartHome/Devices/%d/dWevice_measchan", di, payload)
    elif ("device_ip" in topic):
        if (len(str(payload)) > 6 and bool(re.match(ipallowed, payload))):
            writetoSHconfig('smarthomedevices', 'device_ip_' + ds, payload)
            publish0rd("config/get/SmartHome/Devices/%d/device_ip", di, payload)
    elif ("device_pbip" in topic):
        if (len(str(payload)) > 6 and bool(re.match(ipallowed, payload))):
            writetoSHconfig('smarthomedevices', 'device_pbip_' + ds, payload)
            publish0rd("config/get/SmartHome/Devices/%d/device_pbip", di, payload)
    elif ("device_pbtype" in topic):
        validDeviceTypespb = ['none', 'shellypb']
        if (len(str(payload)) > 2):
            try:
                # just check vor payload in list, deviceTypeIndex is not used
                deviceTypeIndex = validDeviceTypespb.index(payload)
            except ValueError:
                pass
            else:
                writetoSHconfig('smarthomedevices', 'device_pbtype_' + ds, payload)
                publish0rd("config/get/SmartHome/Devices/%d/device_pbtype", di, payload)
    elif ("device_measureip" in topic):
        if (len(str(payload)) > 6 and bool(re.match(ipallowed, payload))):
            writetoSHconfig('smarthomedevices', 'device_measureip_' + ds, payload)
            publish0rd("config/get/SmartHome/Devices/%d/device_measureip", di, payload)
    elif ("device_name" in topic):
        if (3 <= len(str(payload)) <= 12 and bool(re.match(nameallowed, payload))):
            writetoSHconfig('smarthomedevices', 'device_name_' + ds, payload)
            publish0rd("config/get/SmartHome/Devices/%d/device_name", di, payload)
        else:
            dolog("Illegal Name  [%s]" % (msg.payload))
    elif ("device_type" in topic):
        validDeviceTypes = ['none', 'shelly', 'tasmota', 'acthor', 'elwa', 'idm', 'vampair', 'stiebel', 'http', 'avm', 'mystrom', 'viessmann', 'mqtt']
        if (len(str(payload)) > 2):
            try:
                # just check vor payload in list, deviceTypeIndex is not used
                deviceTypeIndex = validDeviceTypes.index(payload)
            except ValueError:
                pass
            else:
                writetoSHconfig('smarthomedevices', 'device_type_' + ds, payload)
                publish0rd("config/get/SmartHome/Devices/%d/device_type", di, payload)
    elif ("device_measureType" in topic):
        validDeviceMeasureTypes = ['shelly', 'tasmota', 'http', 'mystrom', 'sdm630', 'we514', 'fronius', 'json', 'avm', 'mqtt', 'sdm120', 'smaem'] 
        if (len(str(payload)) > 2):
            try:
                #  just check vor payload in list, deviceMeasureTypeIndex is not used
                deviceMeasureTypeIndex = validDeviceMeasureTypes.index(payload)
            except ValueError:
                pass
            else:
                writetoSHconfig('smarthomedevices', 'device_measuretype_' + ds, payload)
                publish0rd("config/get/SmartHome/Devices/%d/device_measureType", di, payload)
    elif ("device_temperatur_configured" in topic):
        if (0 <= int(payload) <= 3):
            writetoSHconfig('smarthomedevices', 'device_temperatur_configured_' + ds, payload)
            publish0rd("config/get/SmartHome/Devices/%d/device_temperatur_configured", di, payload)
    elif ("device_einschaltschwelle" in topic):
        if (-100000 <= int(payload) <= 100000):
            writetoSHconfig('smarthomedevices', 'device_einschaltschwelle_' + ds, payload)
            publish0rd("config/get/SmartHome/Devices/%d/device_einschaltschwelle", di, payload)
    elif ("device_deactivateper" in topic):
        if (0 <= int(payload) <= 100):
            writetoSHconfig('smarthomedevices', 'device_deactivateper_' + ds, payload)
            publish0rd("config/get/SmartHome/Devices/%d/device_deactivateper", di, payload)

    else:
        dolog("SmartHomeTopic: [%s] Message: [%s] [%d] [%s] NOT ASSIGNED" % (topic, payload, di, ds))


# handle each set topic
def on_message(client, userdata, msg):
    global numberOfSupportedDevices, RequestYearGraphv1
    # log all messages before any error forces this process to die
    if (len(msg.payload.decode("utf-8")) >= 1):
        lock.acquire()
        try:
            setTopicCleared = False
            payload = msg.payload.decode("utf-8")
            dolog("Topic: [%s] Message: [%s]" % (msg.topic, payload))
            if (("openWB/set/lp" in msg.topic) and ("ChargePointEnabled" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedLP and 0 <= int(payload) <= 1):  # 8
                    ramdisk.write('lp%senabled' % devicenumb, payload)
                    publish0rd('lp/%d/ChargePointEnabled',int(devicenumb), payload)
            if (("openWB/set/lp" in msg.topic) and ("ForceSoCUpdate" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= 2 and int(payload) == 1):
                    if (int(devicenumb) == 1):
                        ramdisk.write('soctimer', "20005")
                    elif (int(devicenumb) == 2):
                        ramdisk.write('soctimer1', "20005")
            #
            #  ###########################################
            #
            if ("openWB/config/set/SmartHome/Device" in msg.topic):
                processSmartHomeDevice(msg.topic, payload)
            if (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_deactivateWhileEvCharging" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 2):
                    writetoSHconfig('smarthomedevices', 'device_deactivateWhileEvCharging_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_deactivateWhileEvCharging", payload, qos=0, retain=True)
            if (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_ausschaltschwelle" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and -100000 <= int(payload) <= 100000):
                    writetoSHconfig('smarthomedevices', 'device_ausschaltschwelle_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_ausschaltschwelle", payload, qos=0, retain=True)
            if (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_ausschaltverzoegerung" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 10000):
                    writetoSHconfig('smarthomedevices', 'device_ausschaltverzoegerung_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_ausschaltverzoegerung", payload, qos=0, retain=True)
            if (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_einschaltverzoegerung" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 100000):
                    writetoSHconfig('smarthomedevices', 'device_einschaltverzoegerung_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_einschaltverzoegerung", payload, qos=0, retain=True)
            if (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_measureid" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 1 <= int(payload) <= 255):
                    writetoSHconfig('smarthomedevices', 'device_measureid_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_measureid", payload, qos=0, retain=True)
            if (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_speichersocbeforestart" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 100):
                    writetoSHconfig('smarthomedevices', 'device_speichersocbeforestart_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_speichersocbeforestart", payload, qos=0, retain=True)
            if (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_speichersocbeforestop" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 100):
                    writetoSHconfig('smarthomedevices', 'device_speichersocbeforestop_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_speichersocbeforestop", payload, qos=0, retain=True)
            if (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_maxeinschaltdauer" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 100000):
                    writetoSHconfig('smarthomedevices', 'device_maxeinschaltdauer_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_maxeinschaltdauer", payload, qos=0, retain=True)
            if (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_mineinschaltdauer" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 100000):
                    writetoSHconfig('smarthomedevices', 'device_mineinschaltdauer_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_mineinschaltdauer", payload, qos=0, retain=True)
            if (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_manual_control" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 1):
                    publish0rd("config/get/SmartHome/Devices/%d/device_manual_control", int(devicenumb), payload)
                    ramdisk.write('smarthome_device_manual_control_' + str(devicenumb), payload)
            if (("openWB/config/set/SmartHome/Device" in msg.topic) and ("mode" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 1):
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/mode", payload, qos=0, retain=True)
                    ramdisk.write('smarthome_device_manual_' + str(devicenumb), payload)
            if (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_einschalturl" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices):
                    writetoSHconfig('smarthomedevices', 'device_einschalturl_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_einschalturl", payload, qos=0, retain=True)
            if (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_ausschalturl" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices):
                    writetoSHconfig('smarthomedevices', 'device_ausschalturl_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_ausschalturl", payload, qos=0, retain=True)
            if (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_leistungurl" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices):
                    writetoSHconfig('smarthomedevices', 'device_leistungurl_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_leistungurl", payload, qos=0, retain=True)
            if (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_stateurl" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices):
                    writetoSHconfig('smarthomedevices', 'device_stateurl_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_stateurl", payload, qos=0, retain=True)
            if (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_measureurlc" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices):
                    if (payload == "none"):
                        # print("received message 'none'")
                        client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_measureurlc", "", qos=0, retain=True)
                    else:
                        client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_measureurlc", payload, qos=0, retain=True)
                    writetoSHconfig('smarthomedevices', 'device_measureurlc_' + str(devicenumb), payload)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_measureurl" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices):
                    writetoSHconfig('smarthomedevices', 'device_measureurl_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_measureurl", payload, qos=0, retain=True)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_measurejsonurl" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices):
                    writetoSHconfig('smarthomedevices', 'device_measurejsonurl_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_measurejsonurl", payload, qos=0, retain=True)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_measurejsonpower" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices):
                    writetoSHconfig('smarthomedevices', 'device_measurejsonpower_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_measurejsonpower", payload, qos=0, retain=True)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_measurejsoncounter" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices):
                    writetoSHconfig('smarthomedevices', 'device_measurejsoncounter_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_measurejsoncounter", payload, qos=0, retain=True)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_username" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices):
                    writetoSHconfig('smarthomedevices', 'device_username_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_username", payload, qos=0, retain=True)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_password" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices):
                    writetoSHconfig('smarthomedevices', 'device_password_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_password", payload, qos=0, retain=True)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_actor" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices):
                    writetoSHconfig('smarthomedevices', 'device_actor_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_actor", payload, qos=0, retain=True)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_measureavmusername" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices):
                    writetoSHconfig('smarthomedevices', 'device_measureavmusername_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_measureavmusername", payload, qos=0, retain=True)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_measureavmpassword" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices):
                    writetoSHconfig('smarthomedevices', 'device_measureavmpassword_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_measureavmpassword", payload, qos=0, retain=True)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_measureavmactor" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices):
                    writetoSHconfig('smarthomedevices', 'device_measureavmactor_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_measureavmactor", payload, qos=0, retain=True)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_acthortype" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                validDeviceTypes = ['M1', 'M3', '9s', '9s18']
                if (1 <= int(devicenumb) <= numberOfSupportedDevices):
                    try:
                        # just check vor payload in list, deviceTypeIndex is not used
                        deviceTypeIndex = validDeviceTypes.index(payload)
                    except ValueError:
                        pass
                    else:
                        writetoSHconfig('smarthomedevices', 'device_acthortype_' + str(devicenumb), payload)
                        client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_acthortype", payload, qos=0, retain=True)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_acthorpower" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 18000):
                    writetoSHconfig('smarthomedevices', 'device_acthorpower_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_acthorpower", payload, qos=0, retain=True)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_finishTime" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and re.search(r'^([01]{0,1}\d|2[0-3]):[0-5]\d$', payload)):
                    writetoSHconfig('smarthomedevices', 'device_finishtime_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_finishTime", payload, qos=0, retain=True)
                else:
                    print("invalid payload for topic '" + msg.topic + "': " + payload)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_onTime" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and re.search(r'^([01]{0,1}\d|2[0-3]):[0-5]\d$', payload)):
                    writetoSHconfig('smarthomedevices', 'device_ontime_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_onTime", payload, qos=0, retain=True)
                else:
                    print("invalid payload for topic '" + msg.topic + "': " + payload)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_offTime" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and re.search(r'^([01]{0,1}\d|2[0-3]):[0-5]\d$', payload)):
                    writetoSHconfig('smarthomedevices', 'device_offtime_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_offTime", payload, qos=0, retain=True)
                else:
                    print("invalid payload for topic '" + msg.topic + "': " + payload)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_onuntilTime" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and re.search(r'^([01]{0,1}\d|2[0-3]):[0-5]\d$', payload)):
                    writetoSHconfig('smarthomedevices', 'device_onuntilTime_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_onuntilTime", payload, qos=0, retain=True)
                else:
                    print("invalid payload for topic '" + msg.topic + "': " + payload)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_startTime" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and re.search(r'^([01]{0,1}\d|2[0-3]):[0-5]\d$', payload)):
                    writetoSHconfig('smarthomedevices', 'device_startTime_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_startTime", payload, qos=0, retain=True)
                else:
                    print("invalid payload for topic '" + msg.topic + "': " + payload)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_endTime" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and re.search(r'^([01]{0,1}\d|2[0-3]):[0-5]\d$', payload)):
                    writetoSHconfig('smarthomedevices', 'device_endTime_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_endTime", payload, qos=0, retain=True)
                else:
                    print("invalid payload for topic '" + msg.topic + "': " + payload)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_homeConsumtion" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 1):
                    writetoSHconfig('smarthomedevices', 'device_homeConsumtion_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_homeConsumtion", payload, qos=0, retain=True)
                else:
                    print("invalid payload for topic '" + msg.topic + "': " + payload)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_measurePortSdm" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 9999):
                    writetoSHconfig('smarthomedevices', 'device_measurePortSdm_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_measurePortSdm", payload, qos=0, retain=True)
                else:
                    print("invalid payload for topic '" + msg.topic + "': " + payload)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_startupDetection" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 1):
                    writetoSHconfig('smarthomedevices', 'device_startupdetection_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_startupDetection", payload, qos=0, retain=True)
                else:
                    print("invalid payload for topic '" + msg.topic + "': " + payload)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_standbyPower" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 1000):
                    writetoSHconfig('smarthomedevices', 'device_standbypower_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_standbyPower", payload, qos=0, retain=True)
                else:
                    print("invalid payload for topic '" + msg.topic + "': " + payload)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_nonewatt" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 10000):
                    writetoSHconfig('smarthomedevices', 'device_nonewatt_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_nonewatt", payload, qos=0, retain=True)
                else:
                    print("invalid payload for topic '" + msg.topic + "': " + payload)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_idmnav" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 1 <= int(payload) <= 2):
                    writetoSHconfig('smarthomedevices', 'device_idmnav_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_idmnav", payload, qos=0, retain=True)
                else:
                    print("invalid payload for topic '" + msg.topic + "': " + payload)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_standbyDuration" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 86400):
                    writetoSHconfig('smarthomedevices', 'device_standbyduration_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_standbyDuration", payload, qos=0, retain=True)
                else:
                    print("invalid payload for topic '" + msg.topic + "': " + payload)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_startupMulDetection" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 1):
                    writetoSHconfig('smarthomedevices', 'device_startupMulDetection_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_startupMulDetection", payload, qos=0, retain=True)
                else:
                    print("invalid payload for topic '" + msg.topic + "': " + payload)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_measuresmaage" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices and 0 <= int(payload) <= 1000):
                    writetoSHconfig('smarthomedevices', 'device_measuresmaage_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_measuresmaage", payload, qos=0, retain=True)
                else:
                    print("invalid payload for topic '" + msg.topic + "': " + payload)
            elif (("openWB/config/set/SmartHome/Device" in msg.topic) and ("device_measuresmaser" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedDevices):
                    writetoSHconfig('smarthomedevices', 'device_measuresmaser_' + str(devicenumb), payload)
                    client.publish("openWB/config/get/SmartHome/Devices/" + str(devicenumb) + "/device_measuresmaser", payload, qos=0, retain=True)
                else:
                    print("invalid payload for topic '" + msg.topic + "': " + payload)
            elif (msg.topic == "openWB/config/set/SmartHome/maxBatteryPower"):
                if (0 <= int(payload) <= 30000):
                    ramdisk.write('sm/maxbatterypower', payload)
                    client.publish("openWB/config/get/SmartHome/maxBatteryPower", payload, qos=0, retain=True)
            elif (msg.topic == "openWB/config/set/SmartHome/smartmq"):
                if (0 <= int(payload) <= 1):
                    ramdisk.write('smartmq', payload)
                    client.publish("openWB/config/get/SmartHome/smartmq", payload, qos=0, retain=True)
            elif (msg.topic == "openWB/config/set/SmartHome/logLevel"):
                if (int(payload) >= 0 and int(payload) <= 2):
                    ramdisk.write('sm/loglevel', payload)
                    client.publish("openWB/config/get/SmartHome/logLevel", payload, qos=0, retain=True)
            #
            # ##############################################################################
            #
            if (("openWB/config/set/lp" in msg.topic) and ("stopchargeafterdisc" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedLP and 0 <= int(payload) <= 1):
                    replaceinconfig("stopchargeafterdisclp" + str(devicenumb) + "=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "stopchargeafterdisclp" + str(devicenumb) + "=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/lp/" + str(devicenumb) + "/stopchargeafterdisc", payload, qos=0, retain=True)
            if (("openWB/config/set/sofort/lp" in msg.topic) and ("current" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedLP and 6 <= int(payload) <= 32):    # 8
                    client.publish('openWB/config/get/sofort/lp/%s/current' % devicenumb, payload, qos=0, retain=True)
                    ramdisk.write('lp%ssofortll' % devicenumb, payload)
            if (("openWB/set/lp" in msg.topic) and ("manualSoc" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= 2 and 0 <= int(payload) <= 100):
                    client.publish("openWB/lp/" + str(devicenumb) + "/manualSoc", payload, qos=0, retain=True)
                    ramdisk.write('manual_soc_lp' + str(devicenumb), payload)
                    client.publish("openWB/lp/" + str(devicenumb) + "/%Soc", payload, qos=0, retain=True)
                    if (int(devicenumb) == 1):
                        ramdisk.write('soc', payload)
                        # socFile = '/var/www/html/openWB/ramdisk/soc'
                    elif (int(devicenumb) == 2):
                        ramdisk.write('soc1', payload)
                        # socFile = '/var/www/html/openWB/ramdisk/soc1'
            if (("openWB/config/set/sofort/lp" in msg.topic) and ("energyToCharge" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedLP and 0 <= int(payload) <= 100):   # 8
                    if (int(devicenumb) == 1):
                        replaceinconfig("lademkwh=", payload)
                        # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "lademkwh=", payload]
                        # subprocess.run(sendcommand)
                    if (int(devicenumb) == 2):
                        replaceinconfig("lademkwhs1=", payload)
                        # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "lademkwhs1=", payload]
                        # subprocess.run(sendcommand)
                    if (int(devicenumb) == 3):
                        replaceinconfig("lademkwhs2=", payload)
                        # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "lademkwhs2=", payload]
                        # subprocess.run(sendcommand)
#                    if (int(devicenumb) >= 4):
#                        sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "lademkwhlp" + str(devicenumb) + "=", payload]
#                        subprocess.run(sendcommand)
                    client.publish("openWB/config/get/sofort/lp/" + str(devicenumb) + "/energyToCharge", payload, qos=0, retain=True)
            if (("openWB/config/set/sofort/lp" in msg.topic) and ("resetEnergyToCharge" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= numberOfSupportedLP and int(payload) == 1):  # 8
                    if (int(devicenumb) == 1):
                        ramdisk.write('aktgeladen', "0")
                        ramdisk.write('gelrlp1', "0")
                    if (int(devicenumb) == 2):
                        ramdisk.write('aktgeladens1', "0")
                        ramdisk.write('gelrlp2', "0")
                    if (int(devicenumb) == 3):
                        ramdisk.write('aktgeladens2', "0")
                        ramdisk.write('gelrlp3', "0")
            if (("openWB/config/set/sofort/lp" in msg.topic) and ("socToChargeTo" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (1 <= int(devicenumb) <= 2 and 0 <= int(payload) <= 100):
                    client.publish("openWB/config/get/sofort/lp/" + str(devicenumb) + "/socToChargeTo", payload, qos=0, retain=True)
                    replaceinconfig("sofortsoclp" + str(devicenumb) + "=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "sofortsoclp" + str(devicenumb) + "=", payload]
                    # subprocess.run(sendcommand)
            if (("openWB/config/set/sofort/lp" in msg.topic) and ("chargeLimitation" in msg.topic)):
                devicenumb = re.sub(r'\D', '', msg.topic)
                if (3 <= int(devicenumb) <= numberOfSupportedLP and 0 <= int(payload) <= 1):
                    replaceinconfig("msmoduslp" + str(devicenumb) + "=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "msmoduslp" + str(devicenumb) + "=", payload]
                    # subprocess.run(sendcommand)
                    time.sleep(0.4)
                    if (int(payload) == 1):
                        replaceinconfig("lademstatlp" + str(devicenumb) + "=", "1")
                        # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "lademstatlp" + str(devicenumb) + "=", "1"]
                        # subprocess.run(sendcommand)
                        client.publish("openWB/lp/" + str(devicenumb) + "/boolDirectModeChargekWh", payload, qos=0, retain=True)
                    else:
                        replaceinconfig("lademstatlp" + str(devicenumb) + "=", "0")
                        # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "lademstatlp" + str(devicenumb) + "=", "0"]
                        # subprocess.run(sendcommand)
                        client.publish("openWB/lp/" + str(devicenumb) + "/boolDirectModeChargekWh", "0", qos=0, retain=True)
                    client.publish("openWB/config/get/sofort/lp/" + str(devicenumb) + "/chargeLimitation", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/minFeedinPowerBeforeStart"):
                if (int(payload) >= -100000 and int(payload) <= 100000):
                    replaceinconfig("mindestuberschuss=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "mindestuberschuss=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/minFeedinPowerBeforeStart", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/maxPowerConsumptionBeforeStop"):
                if (int(payload) >= -100000 and int(payload) <= 100000):
                    replaceinconfig("abschaltuberschuss=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "abschaltuberschuss=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/maxPowerConsumptionBeforeStop", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/stopDelay"):
                if (int(payload) >= 0 and int(payload) <= 10000):
                    replaceinconfig("abschaltverzoegerung=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "abschaltverzoegerung=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/stopDelay", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/startDelay"):
                if (int(payload) >= 0 and int(payload) <= 100000):
                    replaceinconfig("einschaltverzoegerung=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "einschaltverzoegerung=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/startDelay", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/minCurrentMinPv"):
                if (int(payload) >= 6 and int(payload) <= 16):
                    replaceinconfig("minimalampv=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "minimalampv=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/minCurrentMinPv", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/lp/1/maxSoc"):
                if (int(payload) >= 0 and int(payload) <= 100):
                    replaceinconfig("stopchargepvpercentagelp1=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "stopchargepvpercentagelp1=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/lp/1/maxSoc", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/lp/2/maxSoc"):
                if (int(payload) >= 0 and int(payload) <= 100):
                    replaceinconfig("stopchargepvpercentagelp2=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "stopchargepvpercentagelp2=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/lp/2/maxSoc", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/lp/1/socLimitation"):
                if (int(payload) >= 0 and int(payload) <= 1):
                    replaceinconfig("stopchargepvatpercentlp1=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "stopchargepvatpercentlp1=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/lp/1/socLimitation", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/lp/2/socLimitation"):
                if (int(payload) >= 0 and int(payload) <= 1):
                    replaceinconfig("stopchargepvatpercentlp2=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "stopchargepvatpercentlp2=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/lp/2/socLimitation", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/lp/1/minCurrent"):
                if (int(payload) >= 6 and int(payload) <= 16):
                    replaceinconfig("minimalapv=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "minimalapv=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/lp/1/minCurrent", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/lp/2/minCurrent"):
                if (int(payload) >= 6 and int(payload) <= 16):
                    replaceinconfig("minimalalp2pv=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "minimalalp2pv=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/lp/2/minCurrent", payload, qos=0, retain=True)
            if (("openWB/set/pv" in msg.topic) and ("faultState" in msg.topic)):
                devicenumb = int(re.sub(r'\D', '', msg.topic))
                if ((1 <= devicenumb <= 2) and (0 <= int(payload) <= 2)):
                    client.publish("openWB/pv/" + str(devicenumb) + "/faultState", payload, qos=0, retain=True)
            if (("openWB/set/pv" in msg.topic) and ("faultStr" in msg.topic)):
                devicenumb = int(re.sub(r'\D', '', msg.topic))
                if (1 <= devicenumb <= 2):
                    client.publish("openWB/pv/" + str(devicenumb) + "/faultStr", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/u1p3p/standbyPhases"):
                if (int(payload) >= 1 and int(payload) <= 3):
                    replaceinconfig("u1p3pstandby=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "u1p3pstandby=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/u1p3p/standbyPhases", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/u1p3p/sofortPhases"):
                if (int(payload) >= 1 and int(payload) <= 3):
                    replaceinconfig("u1p3psofort=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "u1p3psofort=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/u1p3p/sofortPhases", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/u1p3p/nachtPhases"):
                if (int(payload) >= 1 and int(payload) <= 3):
                    replaceinconfig("u1p3pnl=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "u1p3pnl=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/u1p3p/nachtPhases", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/u1p3p/minundpvPhases"):
                if (int(payload) >= 1 and int(payload) <= 4):
                    replaceinconfig("u1p3pminundpv=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "u1p3pminundpv=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/u1p3p/minundpvPhases", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/u1p3p/nurpvPhases"):
                if (int(payload) >= 1 and int(payload) <= 4):
                    replaceinconfig("u1p3pnurpv=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "u1p3pnurpv=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/u1p3p/nurpvPhases", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/u1p3p/isConfigured"):
                if (int(payload) >= 0 and int(payload) <= 1):
                    replaceinconfig("u1p3paktiv=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "u1p3paktiv=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/u1p3p/isConfigured", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/global/minEVSECurrentAllowed"):
                if (int(payload) >= 6 and int(payload) <= 32):
                    replaceinconfig("minimalstromstaerke=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "minimalstromstaerke=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/global/minEVSECurrentAllowed", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/global/maxEVSECurrentAllowed"):
                if (int(payload) >= 6 and int(payload) <= 32):
                    replaceinconfig("maximalstromstaerke=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "maximalstromstaerke=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/global/maxEVSECurrentAllowed", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/global/dataProtectionAcknoledged"):
                if (int(payload) >= 0 and int(payload) <= 2):
                    replaceinconfig("datenschutzack=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "datenschutzack=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/global/dataProtectionAcknoledged", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/lp/1/minSocAlwaysToChargeTo"):
                if (int(payload) >= 0 and int(payload) <= 80):
                    replaceinconfig("minnurpvsoclp1=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "minnurpvsoclp1=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/lp/1/minSocAlwaysToChargeTo", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/lp/1/maxSocToChargeTo"):
                if (int(payload) >= 0 and int(payload) <= 101):
                    replaceinconfig("maxnurpvsoclp1=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "maxnurpvsoclp1=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/lp/1/maxSocToChargeTo", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/lp/1/minSocAlwaysToChargeToCurrent"):
                if (int(payload) >= 6 and int(payload) <= 32):
                    replaceinconfig("minnurpvsocll=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "minnurpvsocll=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/lp/1/minSocAlwaysToChargeToCurrent", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/chargeSubmode"):
                if (int(payload) >= 0 and int(payload) <= 2):
                    replaceinconfig("pvbezugeinspeisung=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "pvbezugeinspeisung=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/chargeSubmode", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/regulationPoint"):
                if (int(payload) >= -300000 and int(payload) <= 300000):
                    replaceinconfig("offsetpv=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "offsetpv=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/regulationPoint", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/boolShowPriorityIconInTheme"):   # NC
                if (int(payload) >= 0 and int(payload) <= 1):               # NC
                    replaceinconfig("speicherpvui=", payload)   # NC
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "speicherpvui=", payload] # NC
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/boolShowPriorityIconInTheme", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/minBatteryChargePowerAtEvPriority"):
                if (int(payload) >= 0 and int(payload) <= 90000):
                    replaceinconfig("speichermaxwatt=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "speichermaxwatt=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/minBatteryChargePowerAtEvPriority", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/minBatteryDischargeSocAtBattPriority"):
                if (int(payload) >= 0 and int(payload) <= 101):
                    replaceinconfig("speichersocnurpv=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "speichersocnurpv=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/minBatteryDischargeSocAtBattPriority", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/batteryDischargePowerAtBattPriority"):
                if (int(payload) >= 0 and int(payload) <= 90000):
                    replaceinconfig("speicherwattnurpv=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "speicherwattnurpv=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/batteryDischargePowerAtBattPriority", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/batteryDischargePowerAtBattPriorityHybrid"):
                if (int(payload) >= 0 and int(payload) <= 100000):
                    replaceinconfig("speicherwattnurpvhybrid=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "speicherwattnurpvhybrid=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/batteryDischargePowerAtBattPriorityHybrid", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/socStartChargeAtMinPv"):
                if (int(payload) >= 0 and int(payload) <= 101):
                    replaceinconfig("speichersocminpv=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "speichersocminpv=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/socStartChargeAtMinPv", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/socStopChargeAtMinPv"):
                if (int(payload) >= 0 and int(payload) <= 101):
                    replaceinconfig("speichersochystminpv=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "speichersochystminpv=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/socStopChargeAtMinPv", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/boolAdaptiveCharging"):
                if (int(payload) >= 0 and int(payload) <= 1):
                    replaceinconfig("adaptpv=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "adaptpv=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/boolAdaptiveCharging", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/adaptiveChargingFactor"):
                if (int(payload) >= 0 and int(payload) <= 100):
                    replaceinconfig("adaptfaktor=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "adaptfaktor=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/adaptiveChargingFactor", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/nurpv70dynact"):
                if (int(payload) >= 0 and int(payload) <= 1):
                    replaceinconfig("nurpv70dynact=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "nurpv70dynact=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/nurpv70dynact", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/nurpv70dynw"):
                if (int(payload) >= 2000 and int(payload) <= 50000):
                    replaceinconfig("nurpv70dynw=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "nurpv70dynw=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/nurpv70dynw", payload, qos=0, retain=True)
            if (msg.topic == "openWB/set/system/GetRemoteSupport"):
                if (5 <= len(payload) <= 50):
                    ramdisk.write('remotetoken', payload)
                    # getsupport = ["/var/www/html/openWB/runs/initremote.sh"]
                    xsubprocess(["/var/www/html/openWB/runs/initremote.sh"])
            if (msg.topic == "openWB/set/hook/HookControl"):
                if (int(payload) >= 0 and int(payload) <= 30):
                    hookmsg = payload
                    sendhook = ["/var/www/html/openWB/runs/hookcontrol.sh", hookmsg]
                    hooknmb = hookmsg[1:2]
                    hookact = hookmsg[0:1]
                    subprocess.run(sendhook)
                    client.publish("openWB/hook/" + hooknmb + "/boolHookStatus", hookact, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/display/displayLight"):
                if (int(payload) >= 10 and int(payload) <= 250):
                    replaceinconfig("displayLight=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "displayLight=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/display/displayLight", payload, qos=0, retain=True)
                    # sendcommand2 = ["/var/www/html/openWB/runs/displaybacklight.sh", payload]
                    xsubprocess(["/var/www/html/openWB/runs/displaybacklight.sh", payload])
            if (msg.topic == "openWB/config/set/display/displaysleep"):
                if (int(payload) >= 10 and int(payload) <= 1800):
                    replaceinconfig("displaysleep=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "displaysleep=", payload]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/display/displaysleep", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/display/displaypincode"):
                if (int(payload) >= 1000 and int(payload) <= 99999999):
                    replaceinconfig("displaypincode=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "displaypincode=", payload]
                    # subprocess.run(sendcommand)
                    # ! intentionally not publishing PIN code via MQTT !
            if (msg.topic == "openWB/config/set/global/rfidConfigured"):
                if (int(payload) >= 0 and int(payload) <= 1):
                    rfidMode = payload
                    replaceinconfig("rfidakt=", rfidMode)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "rfidakt=", rfidMode]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/global/rfidConfigured", rfidMode, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/global/lp/1/cpInterrupt"):
                if (int(payload) >= 0 and int(payload) <= 1):
                    einbeziehen = payload
                    replaceinconfig("cpunterbrechunglp1=", einbeziehen)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "cpunterbrechunglp1=", einbeziehen]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/global/lp/1/cpInterrupt", einbeziehen, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/global/lp/2/cpInterrupt"):
                if (int(payload) >= 0 and int(payload) <= 1):
                    einbeziehen = payload
                    replaceinconfig("cpunterbrechunglp2=", einbeziehen)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "cpunterbrechunglp2=", einbeziehen]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/global/lp/2/cpInterrupt", einbeziehen, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/pv/priorityModeEVBattery"):
                if (int(payload) >= 0 and int(payload) <= 1):
                    einbeziehen = payload
                    replaceinconfig("speicherpveinbeziehen=", einbeziehen)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "speicherpveinbeziehen=", einbeziehen]
                    # subprocess.run(sendcommand)
                    client.publish("openWB/config/get/pv/priorityModeEVBattery", einbeziehen, qos=0, retain=True)
            if (msg.topic == "openWB/set/graph/LiveGraphDuration"):
                if (int(payload) >= 20 and int(payload) <= 120):
                    replaceinconfig("livegraph=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "livegraph=", payload]
                    # subprocess.run(sendcommand)
            if (msg.topic == "openWB/set/system/SimulateRFID"):
                if len(str(payload)) >= 1 and bool(re.match(namenumballowed, payload)):
                    ramdisk.write('readtag', payload)
            if (msg.topic == "openWB/set/system/PerformUpdate"):
                if (int(payload) == 1):
                    client.publish("openWB/set/system/PerformUpdate", "0", qos=0, retain=True)
                    setTopicCleared = True
                    subprocess.run("/var/www/html/openWB/runs/update.sh")
            if (msg.topic == "openWB/set/system/SendDebug"):
                payload = payload
                if (20 <= len(payload) <= 1000):
                    try:
                        json_payload = json_loads(str(payload))
                    except JSONDecodeError:
                        file = open('/var/www/html/openWB/ramdisk/mqtt.log', 'a')
                        file.write("payload is not valid JSON, fallback to simple text\n")
                        file.close()
                        payload = payload.rpartition('email: ')
                        json_payload = {"message": payload[0], "email": payload[2]}
                    finally:
                        if (re.match(emailallowed, json_payload["email"])):
                            ramdisk.write('debuguser', "%s\n%s\n" % (json_payload["message"], json_payload["email"]))
                            # f = open('/var/www/html/openWB/ramdisk/debuguser', 'w')
                            # f.write("%s\n%s\n" % (json_payload["message"], json_payload["email"]))
                            # f.close()
                            ramdisk.write('debugmail', json_payload["email"] + "\n")
                            # f = open('/var/www/html/openWB/ramdisk/debugemail', 'w')
                            # f.write(json_payload["email"] + "\n")
                            # f.close()
                        else:
                            file = open('/var/www/html/openWB/ramdisk/mqtt.log', 'a')
                            file.write("payload does not contain a valid email: '%s'\n" % (str(json_payload["email"])))
                            file.close()
                        client.publish("openWB/set/system/SendDebug", "0", qos=0, retain=True)
                        setTopicCleared = True
                        subprocess.run("/var/www/html/openWB/runs/senddebuginit.sh")
            if (msg.topic == "openWB/set/system/reloadDisplay"):
                if (int(payload) >= 0 and int(payload) <= 1):
                    client.publish("openWB/system/reloadDisplay", payload, qos=0, retain=True)
                    xsubprocess(["/var/www/html/openWB/runs/reloadDisplay.sh", payload])
                    # script = "/var/www/html/openWB/runs/reloadDisplay.sh"
                    # ps = Path(script)
                    # if ps.is_file():
                    #   # sendcommand = [script, payload)]
                    # ps = None
            # if (msg.topic == "openWB/config/set/releaseTrain"):
            if (msg.topic == "openWB/set/system/releaseTrain"):
                if (payload == "stable17" or payload == "master" or payload == "beta" or payload.startswith("yc/")):
                    sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "releasetrain=", payload]
                    subprocess.run(sendcommand)
                    client.publish("openWB/system/releaseTrain", payload, qos=0, retain=True)

            if (msg.topic == "openWB/set/graph/RequestLiveGraph"):		# NC, maybe from cloud?
                if (int(payload) == 1):
                    subprocess.run("/var/www/html/openWB/runs/sendlivegraphdata.sh")
                else:
                    client.publish("openWB/system/LiveGraphData", "empty", qos=0, retain=True)
                setTopicCleared = True
# Live wird immer erzeugt und nicht angfordert
# (nur die letzen 50) daher nach mqtt neustart erst nur wenige daten
#

            if (msg.topic == "openWB/set/graph/RequestLLiveGraph"):
                if (int(payload) == 1):
                    # subprocess.run("/var/www/html/openWB/runs/sendllivegraphdata.sh")
                    xsubprocess(["/var/www/html/openWB/runs/sendllivegraphdata.sh"])
                else:
                    client.publish("openWB/system/1alllivevalues", "empty", qos=0, retain=True)
                    client.publish("openWB/system/2alllivevalues", "empty", qos=0, retain=True)
                    client.publish("openWB/system/3alllivevalues", "empty", qos=0, retain=True)
                    client.publish("openWB/system/4alllivevalues", "empty", qos=0, retain=True)
                    client.publish("openWB/system/5alllivevalues", "empty", qos=0, retain=True)
                    client.publish("openWB/system/6alllivevalues", "empty", qos=0, retain=True)
                    client.publish("openWB/system/7alllivevalues", "empty", qos=0, retain=True)
                    client.publish("openWB/system/8alllivevalues", "empty", qos=0, retain=True)
                    client.publish("openWB/system/9alllivevalues", "empty", qos=0, retain=True)
                    client.publish("openWB/system/10alllivevalues", "empty", qos=0, retain=True)
                    client.publish("openWB/system/11alllivevalues", "empty", qos=0, retain=True)
                    client.publish("openWB/system/12alllivevalues", "empty", qos=0, retain=True)
                    client.publish("openWB/system/13alllivevalues", "empty", qos=0, retain=True)
                    client.publish("openWB/system/14alllivevalues", "empty", qos=0, retain=True)
                    client.publish("openWB/system/15alllivevalues", "empty", qos=0, retain=True)
                    client.publish("openWB/system/16alllivevalues", "empty", qos=0, retain=True)
                setTopicCleared = True
            if (msg.topic == "openWB/set/graph/RequestDayGraph"):
                if (int(payload) >= 1 and int(payload) <= 20501231):
                    # sendcommand = ["/var/www/html/openWB/runs/senddaygraphdata.sh", msg.payload]
                    # subprocess.run(sendcommand)
                    xsubprocess(["/var/www/html/openWB/runs/senddaygraphdata.sh", payload])
                else:
                    client.publish("openWB/system/DayGraphData1", "empty", qos=0, retain=True)
                    client.publish("openWB/system/DayGraphData2", "empty", qos=0, retain=True)
                    client.publish("openWB/system/DayGraphData3", "empty", qos=0, retain=True)
                    client.publish("openWB/system/DayGraphData4", "empty", qos=0, retain=True)
                    client.publish("openWB/system/DayGraphData5", "empty", qos=0, retain=True)
                    client.publish("openWB/system/DayGraphData6", "empty", qos=0, retain=True)
                    client.publish("openWB/system/DayGraphData7", "empty", qos=0, retain=True)
                    client.publish("openWB/system/DayGraphData8", "empty", qos=0, retain=True)
                    client.publish("openWB/system/DayGraphData9", "empty", qos=0, retain=True)
                    client.publish("openWB/system/DayGraphData10", "empty", qos=0, retain=True)
                    client.publish("openWB/system/DayGraphData11", "empty", qos=0, retain=True)
                    client.publish("openWB/system/DayGraphData12", "empty", qos=0, retain=True)
                setTopicCleared = True
            if (msg.topic == "openWB/set/graph/RequestMonthGraph"):
                if (int(payload) >= 1 and int(payload) <= 205012):
                    # sendcommand = ["/var/www/html/openWB/runs/sendmonthgraphdata.sh", msg.payload]
                    # subprocess.run(sendcommand)
                    xsubprocess(["/var/www/html/openWB/runs/sendmonthgraphdata.sh", payload])
                else:
                    client.publish("openWB/system/MonthGraphData1", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphData2", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphData3", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphData4", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphData5", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphData6", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphData7", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphData8", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphData9", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphData10", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphData11", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphData12", "empty", qos=0, retain=True)
                setTopicCleared = True
            if (msg.topic == "openWB/set/graph/RequestMonthGraphv1"):
                if (int(payload) >= 1 and int(payload) <= 205012):
                    # sendcommand = ["/var/www/html/openWB/runs/sendmonthgraphdatav1.sh", msg.payload]
                    # subprocess.run(sendcommand)
                    xsubprocess(["/var/www/html/openWB/runs/sendmonthgraphdatav1.sh", payload])
                else:
                    client.publish("openWB/system/MonthGraphDatan1", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphDatan2", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphDatan3", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphDatan4", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphDatan5", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphDatan6", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphDatan7", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphDatan8", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphDatan9", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphDatan10", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphDatan11", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthGraphDatan12", "empty", qos=0, retain=True)
                setTopicCleared = True
            if (msg.topic == "openWB/set/graph/RequestYearGraph"):
                if (int(payload) >= 1 and int(payload) <= 2050):
                    # sendcommand = ["/var/www/html/openWB/runs/sendyeargraphdata.sh", msg.payload]
                    # subprocess.run(sendcommand)
                    xsubprocess(["/var/www/html/openWB/runs/sendyeargraphdata.sh", payload])
                else:
                    client.publish("openWB/system/YearGraphData1", "empty", qos=0, retain=True)
                    client.publish("openWB/system/YearGraphData2", "empty", qos=0, retain=True)
                    client.publish("openWB/system/YearGraphData3", "empty", qos=0, retain=True)
                    client.publish("openWB/system/YearGraphData4", "empty", qos=0, retain=True)
                    client.publish("openWB/system/YearGraphData5", "empty", qos=0, retain=True)
                    client.publish("openWB/system/YearGraphData6", "empty", qos=0, retain=True)
                    client.publish("openWB/system/YearGraphData7", "empty", qos=0, retain=True)
                    client.publish("openWB/system/YearGraphData8", "empty", qos=0, retain=True)
                    client.publish("openWB/system/YearGraphData9", "empty", qos=0, retain=True)
                    client.publish("openWB/system/YearGraphData10", "empty", qos=0, retain=True)
                    client.publish("openWB/system/YearGraphData11", "empty", qos=0, retain=True)
                    client.publish("openWB/system/YearGraphData12", "empty", qos=0, retain=True)
                setTopicCleared = True
            if (msg.topic == "openWB/set/graph/RequestYearGraphv1"):
                if (int(payload) >= 1 and int(payload) <= 2050):
                    # sendcommand = ["/var/www/html/openWB/runs/sendyeargraphdatav1.sh", msg.payload]
                    # subprocess.run(sendcommand)
                    xsubprocess(["/var/www/html/openWB/runs/sendyeargraphdatav1.sh", payload])
                    RequestYearGraphv1 = int(payload)
                    dolog("set RequestYearGraphv1 to :%d" % (RequestYearGraphv1))
                else:
                    if (RequestYearGraphv1 > 0):
                        RequestYearGraphv1 = 0
                        dolog("RequestYearGraphv1 clear :%d" % (RequestYearGraphv1))
                        client.publish("openWB/system/YearGraphDatan1", "empty", qos=0, retain=True)
                        client.publish("openWB/system/YearGraphDatan2", "empty", qos=0, retain=True)
                        client.publish("openWB/system/YearGraphDatan3", "empty", qos=0, retain=True)
                        client.publish("openWB/system/YearGraphDatan4", "empty", qos=0, retain=True)
                        client.publish("openWB/system/YearGraphDatan5", "empty", qos=0, retain=True)
                        client.publish("openWB/system/YearGraphDatan6", "empty", qos=0, retain=True)
                        client.publish("openWB/system/YearGraphDatan7", "empty", qos=0, retain=True)
                        client.publish("openWB/system/YearGraphDatan8", "empty", qos=0, retain=True)
                        client.publish("openWB/system/YearGraphDatan9", "empty", qos=0, retain=True)
                        client.publish("openWB/system/YearGraphDatan10", "empty", qos=0, retain=True)
                        client.publish("openWB/system/YearGraphDatan11", "empty", qos=0, retain=True)
                        client.publish("openWB/system/YearGraphDatan12", "empty", qos=0, retain=True)
                    else:
                        dolog("RequestYearGraphv1 skip :%d" % (RequestYearGraphv1))
                setTopicCleared = True
            if (msg.topic == "openWB/set/system/debug/RequestDebugInfo"):
                if (int(payload) == 1):
                    xsubprocess(["/var/www/html/openWB/runs/sendmdebug.sh"])
                else:
                    xsubprocess(["runs/sendinfo.sh", payload])
                setTopicCleared = True
            if (msg.topic == "openWB/set/graph/RequestMonthLadelog"):
                if (int(payload) >= 1 and int(payload) <= 205012):
                    # sendcommand = ["/var/www/html/openWB/runs/sendladelog.sh", msg.payload]
                    # subprocess.run(sendcommand)
                    xsubprocess(["/var/www/html/openWB/runs/sendladelog.sh", payload])
                else:
                    client.publish("openWB/system/MonthLadelogData1", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthLadelogData2", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthLadelogData3", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthLadelogData4", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthLadelogData5", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthLadelogData6", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthLadelogData7", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthLadelogData8", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthLadelogData9", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthLadelogData10", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthLadelogData11", "empty", qos=0, retain=True)
                    client.publish("openWB/system/MonthLadelogData12", "empty", qos=0, retain=True)
                setTopicCleared = True
            if (msg.topic == "openWB/set/pv/NurPV70Status"):
                if (int(payload) >= 0 and int(payload) <= 1):
                    client.publish("openWB/pv/bool70PVDynStatus", payload, qos=0, retain=True)
                    ramdisk.write('nurpv70dynstatus', payload)
            if (msg.topic == "openWB/set/RenewMQTT"):
                if (int(payload) == 1):
                    client.publish("openWB/set/RenewMQTT", "0", qos=0, retain=True)
                    setTopicCleared = True
                    ramdisk.write('renewmqtt', "1")
            if (msg.topic == "openWB/set/ChargeMode"):
                if (int(payload) >= 0 and int(payload) <= 4):
                    ramdisk.write('lademodus', payload)
                    publish0r("global/ChargeMode", payload)
            if (msg.topic == "openWB/config/set/sofort/lp/1/chargeLimitation"):
                if (int(payload) >= 0 and int(payload) <= 2):
                    replaceinconfig("msmoduslp1=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "msmoduslp1=", payload]
                    # subprocess.run(sendcommand)
                    if (int(payload) == 1):
                        client.publish("openWB/lp/1/boolDirectModeChargekWh", payload, qos=0, retain=True)
                    else:
                        client.publish("openWB/lp/1/boolDirectModeChargekWh", "0", qos=0, retain=True)
                    if (int(payload) == 2):
                        client.publish("openWB/lp/1/boolDirectChargeModeSoc", "1", qos=0, retain=True)
                    else:
                        client.publish("openWB/lp/1/boolDirectChargeModeSoc", "0", qos=0, retain=True)
                    client.publish("openWB/config/get/sofort/lp/1/chargeLimitation", payload, qos=0, retain=True)
            if (msg.topic == "openWB/config/set/sofort/lp/2/chargeLimitation"):
                if (int(payload) >= 0 and int(payload) <= 2):
                    replaceinconfig("msmoduslp2=", payload)
                    # sendcommand = ["/var/www/html/openWB/runs/replaceinconfig.sh", "msmoduslp2=", payload]
                    # subprocess.run(sendcommand)
                    if (int(payload) == 1):
                        client.publish("openWB/lp/2/boolDirectModeChargekWh", payload, qos=0, retain=True)
                    else:
                        client.publish("openWB/lp/2/boolDirectModeChargekWh", "0", qos=0, retain=True)
                    if (int(payload) == 2):
                        client.publish("openWB/lp/2/boolDirectChargeModeSoc", "1", qos=0, retain=True)
                    else:
                        client.publish("openWB/lp/2/boolDirectChargeModeSoc", "0", qos=0, retain=True)
                    client.publish("openWB/config/get/sofort/lp/2/chargeLimitation", payload, qos=0, retain=True)
            if (msg.topic == "openWB/set/lp/1/DirectChargeSubMode"):
                if (int(payload) == 0):
                    replaceAll("lademstat=", payload)
                    replaceAll("sofortsocstatlp1=", payload)
                if (int(payload) == 1):
                    replaceAll("lademstat=", payload)
                    replaceAll("sofortsocstatlp1=", "0")
                if (int(payload) == 2):
                    replaceAll("lademstat=", "0")
                    replaceAll("sofortsocstatlp1=", "1")
            if (msg.topic == "openWB/set/lp/2/DirectChargeSubMode"):
                if (int(payload) == 0):
                    replaceAll("lademstats1=", payload)
                    replaceAll("sofortsocstatlp2=", payload)
                if (int(payload) == 1):
                    replaceAll("lademstats1=", payload)
                    replaceAll("sofortsocstatlp2=", "0")
                if (int(payload) == 2):
                    replaceAll("lademstats1=", "0")
                    replaceAll("sofortsocstatlp2=", "1")
            if (msg.topic == "openWB/set/lp/3/DirectChargeSubMode"):
                if (int(payload) == 0):
                    replaceAll("lademstats2=", payload)
                    # replaceAll("sofortsocstatlp3=", payload)
                if (int(payload) == 1):
                    replaceAll("lademstats2=", payload)
                    # replaceAll("sofortsocstatlp3=", "0")
                # if (int(payload) == 2):
                #    replaceAll("lademstats2=", "0")
                #    replaceAll("sofortsocstatlp3=", "1")
#            if (msg.topic == "openWB/set/lp/4/DirectChargeSubMode"):
#                if (int(payload) == 0):
#                    replaceAll("lademstatlp4=", payload)
#                if (int(payload) == 1):
#                    replaceAll("lademstatlp4=", payload)
#            if (msg.topic == "openWB/set/lp/5/DirectChargeSubMode"):
#                if (int(payload) == 0):
#                    replaceAll("lademstatlp5=", payload)
#                if (int(payload) == 1):
#                    replaceAll("lademstatlp5=", payload)
#            if (msg.topic == "openWB/set/lp/6/DirectChargeSubMode"):
#                if (int(payload) == 0):
#                    replaceAll("lademstatlp6=", payload)
#                if (int(payload) == 1):
#                    replaceAll("lademstatlp6=", payload)
#            if (msg.topic == "openWB/set/lp/7/DirectChargeSubMode"):
#                if (int(payload) == 0):
#                    replaceAll("lademstatlp7=", payload)
#                if (int(payload) == 1):
#                    replaceAll("lademstatlp7=", payload)
#            if (msg.topic == "openWB/set/lp/8/DirectChargeSubMode"):
#                if (int(payload) == 0):
#                    replaceAll("lademstatlp8=", payload)
#                if (int(payload) == 1):
#                    replaceAll("lademstatlp8=", payload)
            if (msg.topic == "openWB/set/isss/ClearRfid"):
                if (int(payload) > 0 and int(payload) <= 1):
                    ramdisk.write('readtag', "0")
            if (msg.topic == "openWB/set/isss/Current"):
                if (float(msg.payload) >= 0 and float(msg.payload) <= 32):
                    ramdisk.write('llsoll', payload)
            if (msg.topic == "openWB/set/isss/Lp2Current"):
                if (float(msg.payload) >= 0 and float(msg.payload) <= 32):
                    ramdisk.write('llsolls1', payload)
            if (msg.topic == "openWB/set/isss/U1p3p"):
                if (int(payload) >= 0 and int(payload) <= 5):
                    ramdisk.write('u1p3pstat', payload)
            if (msg.topic == "openWB/set/isss/U1p3pLp2"):
                if (int(payload) >= 0 and int(payload) <= 5):
                    ramdisk.write('u1p3plp2stat', payload)
            if (msg.topic == "openWB/set/isss/Cpulp1"):
                if (int(payload) >= 0 and int(payload) <= 5):
                    ramdisk.write('extcpulp1', payload)
            if (msg.topic == "openWB/set/isss/heartbeat"):
                if (int(payload) >= -1 and int(payload) <= 5):
                    ramdisk.write('heartbeat', payload)
            if (msg.topic == "openWB/set/isss/parentWB"):
                ramdisk.write('parentWB', payload)
                client.publish("openWB/system/parentWB", payload, qos=0, retain=True)
            if (msg.topic == "openWB/set/isss/parentCPlp1"):
                client.publish("openWB/system/parentCPlp1", payload, qos=0, retain=True)
                ramdisk.write('parentCPlp1', payload)
            if (msg.topic == "openWB/set/isss/parentCPlp2"):
                client.publish("openWB/system/parentCPlp2", payload, qos=0, retain=True)
                ramdisk.write('parentCPlp2', payload)
            if (msg.topic == "openWB/set/awattar/MaxPriceForCharging"):
                if (float(msg.payload) >= -50.0 and float(msg.payload) <= 95.0):
                    ramdisk.write('etprovidermaxprice', payload)
# <<<< RCT Detailsteuerung start
            # Automatik von regel.sh
            if (msg.topic == "openWB/set/houseBattery/priceload"):
                if(int(payload) == 0):
                    sendcommand = ["/var/www/html/openWB/modules/tibber_rct/rct_setter.sh", "resetwatt"]
                    xsubprocess(sendcommand)
                else:
                    sendcommand = ["/var/www/html/openWB/modules/tibber_rct/rct_setter.sh", "loadbat", "180"]
                    xsubprocess(sendcommand)

            # Aktiviere Endladeschutz manuell (z.b. beim Duschen im Akkubetrieb)
            if (msg.topic == "openWB/set/houseBattery/aktivateDrainmode"):
                sendcommand = ["/var/www/html/openWB/modules/tibber_rct/rct_setter.sh", "aktivateDrainmode", str(payload)]
                xsubprocess(sendcommand)

            # reset from Menu oder timeouts (at)
            if (msg.topic == "openWB/set/houseBattery/reset_rct"):      # Manuell from GUI  watt oder current
                sendcommand = ["/var/www/html/openWB/modules/tibber_rct/rct_setter.sh", payload]
                xsubprocess(sendcommand)

            # aktiviere , stoppe akku drainageschutz
            if (msg.topic == "openWB/set/houseBattery/hooker"):
                sendcommand = ["/var/www/html/openWB/modules/tibber_rct/rct_setter.sh", payload]
                xsubprocess(sendcommand)

            # Manelles laden
            if (msg.topic == "openWB/set/houseBattery/loadbat"):
                if (int(payload) >= 1 and int(payload) <= 180):
                    sendcommand = ["/var/www/html/openWB/modules/tibber_rct/rct_setter.sh", "loadbat", str(payload)]
                    xsubprocess(sendcommand)

            # toogle buttons
            if (msg.topic == "openWB/set/houseBattery/enable_discharge_max"):
                if (int(payload) >= 0 and int(payload) <= 1):
                    ramdisk.write('HB_enable_discharge_max', payload)
                    client.publish("openWB/housebattery/enable_discharge_max", payload, qos=0, retain=True)
            if (msg.topic == "openWB/set/houseBattery/enable_priceloading"):
                if (int(payload) >= 0 and int(payload) <= 1):
                    ramdisk.write('HB_enable_priceloading', payload)
                    client.publish("openWB/housebattery/enable_priceloading", payload, qos=0, retain=True)

# >>>>> RCT Detailsteuerung end

            if (msg.topic == "openWB/set/houseBattery/W"):
                if (float(msg.payload) >= -30000 and float(msg.payload) <= 30000):
                    ramdisk.write('speicherleistung', payload)
            if (msg.topic == "openWB/set/houseBattery/WhImported"):
                if (float(msg.payload) >= 0 and float(msg.payload) <= 9000000):
                    ramdisk.write('speicherikwh', payload)
            if (msg.topic == "openWB/set/houseBattery/WhExported"):
                if (float(msg.payload) >= 0 and float(msg.payload) <= 9000000):
                    ramdisk.write('speicherekwh', payload)
            if (msg.topic == "openWB/set/houseBattery/%Soc"):
                if (float(msg.payload) >= 0 and float(msg.payload) <= 100):
                    ramdisk.write('speichersoc', payload)
            if (msg.topic == "openWB/set/houseBattery/faultState"):
                if (int(payload) >= 0 and int(payload) <= 2):
                    client.publish("openWB/housebattery/faultState", payload, qos=0, retain=True)
            if (msg.topic == "openWB/set/houseBattery/faultStr"):
                client.publish("openWB/housebattery/faultStr", payload, qos=0, retain=True)
            if (msg.topic == "openWB/set/evu/W"):
                if (float(msg.payload) >= -100000 and float(msg.payload) <= 100000):
                    ramdisk.write('wattbezug', payload)
            if (msg.topic == "openWB/set/evu/APhase1"):
                if (float(msg.payload) >= -1000 and float(msg.payload) <= 1000):
                    ramdisk.write('bezuga1', payload)
            if (msg.topic == "openWB/set/evu/APhase2"):
                if (float(msg.payload) >= -1000 and float(msg.payload) <= 1000):
                    ramdisk.write('bezuga2', payload)
            if (msg.topic == "openWB/set/evu/APhase3"):
                if (float(msg.payload) >= -1000 and float(msg.payload) <= 1000):
                    ramdisk.write('bezuga3', payload)
            if (msg.topic == "openWB/set/evu/VPhase1"):
                if (float(msg.payload) >= -1000 and float(msg.payload) <= 1000):
                    ramdisk.write('evuv1', payload)
            if (msg.topic == "openWB/set/evu/VPhase2"):
                if (float(msg.payload) >= -1000 and float(msg.payload) <= 1000):
                    ramdisk.write('evuv2', payload)
            if (msg.topic == "openWB/set/evu/VPhase3"):
                if (float(msg.payload) >= -1000 and float(msg.payload) <= 1000):
                    ramdisk.write('evuv3', payload)
            if (msg.topic == "openWB/set/evu/HzFrequenz"):
                if (float(msg.payload) >= 0 and float(msg.payload) <= 80):
                    ramdisk.write('evuhz', payload)
            if (msg.topic == "openWB/set/evu/WhImported"):
                if (float(msg.payload) >= 0 and float(msg.payload) <= 10000000000):
                    ramdisk.write('bezugkwh', payload)
            if (msg.topic == "openWB/set/evu/WhExported"):
                if (float(msg.payload) >= 0 and float(msg.payload) <= 10000000000):
                    ramdisk.write('einspeisungkwh', payload)
            if (msg.topic == "openWB/set/evu/faultState"):
                if (int(payload) >= 0 and int(payload) <= 9):
                    client.publish("openWB/evu/faultState", payload, qos=0, retain=True)
            if (msg.topic == "openWB/set/evu/faultStr"):
                client.publish("openWB/evu/faultStr", payload, qos=0, retain=True)
            if (msg.topic == "openWB/set/lp/1/%Soc"):
                if (float(msg.payload) >= 0 and float(msg.payload) <= 100):
                    ramdisk.write('soc', payload)
            if (msg.topic == "openWB/set/lp/2/%Soc"):
                if (float(msg.payload) >= 0 and float(msg.payload) <= 100):
                    ramdisk.write('soc1', payload)
            if (msg.topic == "openWB/set/pv/1/kWhCounter"):
                if (float(msg.payload) >= 0 and float(msg.payload) <= 10000000000):
                    pvkwhcounter = float(payload) * 1000
                    ramdisk.write('pvkwh', str(pvkwhcounter))
            if (msg.topic == "openWB/set/pv/1/WhCounter"):
                if (float(msg.payload) >= 0 and float(msg.payload) <= 10000000000):
                    ramdisk.write('pvkwh', payload)
            if (msg.topic == "openWB/set/pv/1/W"):
                if (float(msg.payload) >= -10000000 and float(msg.payload) <= 100000000):
                    if (float(msg.payload) > 1):
                        pvwatt = int(float(payload)) * -1
                    else:
                        pvwatt = int(float(payload))
                    ramdisk.write('pvwatt', str(pvwatt))
            if (msg.topic == "openWB/set/pv/2/kWhCounter"):
                if (float(msg.payload) >= 0 and float(msg.payload) <= 10000000000):
                    pvkwhcounter = float(payload) * 1000
                    ramdisk.write('pvkwh', str(pvkwhcounter))
            if (msg.topic == "openWB/set/pv/2/WhCounter"):
                if (float(msg.payload) >= 0 and float(msg.payload) <= 10000000000):
                    ramdisk.write('pv2kwh', payload)
            if (msg.topic == "openWB/set/pv/2/W"):
                if (float(msg.payload) >= -10000000 and float(msg.payload) <= 100000000):
                    if (float(msg.payload) > 1):
                        pvwatt = int(float(payload)) * -1
                    else:
                        pvwatt = int(float(payload))
                    ramdisk.write('pv2watt', str(pvwatt))

#            if (msg.topic == "openWB/set/lp/1/AutolockStatus"):
#                if (int(payload) >= 0 and int(payload) <= 3):
#                    ramdisk.write('autolockstatuslp1', payload)
#                    #  values used for AutolockStatus flag:
#                    #  0 = standby
#                    #  1 = waiting for autolock
#                    #  2 = autolock performed
#                    #  3 = auto-unlock performed
#                    # warum im mqtt nur bei lp1 und nicht bei lp2,3++
#                    client.publish("openWB/lp/1/AutolockStatus", payload, qos=0, retain=True)
#            if (msg.topic == "openWB/set/lp/2/AutolockStatus"):
#                if (int(payload) >= 0 and int(payload) <= 3):
#                    ramdisk.write('autolockstatuslp2', payload)
#            if (msg.topic == "openWB/set/lp/3/AutolockStatus"):
#                if (int(payload) >= 0 and int(payload) <= 3):
#                    ramdisk.write('autolockstatuslp3', payload)
#            if (msg.topic == "openWB/set/lp/4/AutolockStatus"):
#                if (int(payload) >= 0 and int(payload) <= 3):
#                    f = open('/var/www/html/openWB/ramdisk/autolockstatuslp4', 'w')
#                    f.write(payload)
#                    f.close()
#            if (msg.topic == "openWB/set/lp/5/AutolockStatus"):
#                if (int(payload) >= 0 and int(payload) <= 3):
#                    f = open('/var/www/html/openWB/ramdisk/autolockstatuslp5', 'w')
#                    f.write(payload)
#                    f.close()
#            if (msg.topic == "openWB/set/lp/6/AutolockStatus"):
#                if (int(payload) >= 0 and int(payload) <= 3):
#                    f = open('/var/www/html/openWB/ramdisk/autolockstatuslp6', 'w')
#                    f.write(payload)
#                    f.close()
#            if (msg.topic == "openWB/set/lp/7/AutolockStatus"):
#                if (int(payload) >= 0 and int(payload) <= 3):
#                    f = open('/var/www/html/openWB/ramdisk/autolockstatuslp7', 'w')
#                    f.write(payload)
#                    f.close()
#            if (msg.topic == "openWB/set/lp/8/AutolockStatus"):
#                if (int(payload) >= 0 and int(payload) <= 3):
#                    f = open('/var/www/html/openWB/ramdisk/autolockstatuslp8', 'w')
#                    f.write(payload)
#                    f.close()
            if (("openWB/set/lp" in msg.topic) and ("faultState" in msg.topic)):
                devicenumb = int(re.sub(r'\D', '', msg.topic))
                if ((1 <= devicenumb <= numberOfSupportedLP) and (0 <= int(payload) <= 2)):
                    client.publish("openWB/lp/" + str(devicenumb) + "/faultState", payload, qos=0, retain=True)
            if (("openWB/set/lp" in msg.topic) and ("faultStr" in msg.topic)):
                devicenumb = int(re.sub(r'\D', '', msg.topic))
                if (1 <= devicenumb <= numberOfSupportedLP):
                    client.publish("openWB/lp/" + str(devicenumb) + "/faultStr", payload, qos=0, retain=True)
            if (("openWB/set/lp" in msg.topic) and ("socFaultState" in msg.topic)):
                devicenumb = int(re.sub(r'\D', '', msg.topic))
                if ((1 <= devicenumb <= 2) and (0 <= int(payload) <= 2)):
                    client.publish("openWB/lp/" + str(devicenumb) + "/socFaultState", payload, qos=0, retain=True)
            if (("openWB/set/lp" in msg.topic) and ("socFaultStr" in msg.topic)):
                devicenumb = int(re.sub(r'\D', '', msg.topic))
                if (1 <= devicenumb <= 2):
                    client.publish("openWB/lp/" + str(devicenumb) + "/socFaultStr", payload, qos=0, retain=True)
            if (("openWB/set/lp" in msg.topic) and ("socKM" in msg.topic)):
                devicenumb = int(re.sub(r'\D', '', msg.topic))
                if (1 <= devicenumb <= numberOfSupportedLP):
                    client.publish("openWB/lp/" + str(devicenumb) + "/socKM", payload, qos=0, retain=True)
                    ramdisk.write('soc' + str(devicenumb) + 'KM', payload)
            if (("openWB/set/lp" in msg.topic) and ("socRange" in msg.topic)):
                devicenumb = int(re.sub(r'\D', '', msg.topic))
                if (1 <= devicenumb <= numberOfSupportedLP):
                    client.publish("openWB/lp/" + str(devicenumb) + "/socRange", payload, qos=0, retain=True)
                    ramdisk.write('soc' + str(devicenumb) + 'Range', payload)
            # Topics for Mqtt-EVSE module
            # ToDo: check if Mqtt-EVSE module is selected!
            # llmodule = getConfigValue("evsecon")
            if (("openWB/set/lp" in msg.topic) and ("plugStat" in msg.topic)):
                devicenumb = int(re.sub(r'\D', '', msg.topic))
                if ((1 <= devicenumb <= numberOfSupportedLP) and (0 <= int(payload) <= 1)):
                    plugstat = int(payload)
                    if (devicenumb == 1):
                        filename = "plugstat"
                    elif (devicenumb == 2):
                        filename = "plugstats1"
                    elif (devicenumb == 3):
                        filename = "plugstatlp3"
                    ramdisk.write(str(filename), str(plugstat))
            if (("openWB/set/lp" in msg.topic) and ("chargeStat" in msg.topic)):
                devicenumb = int(re.sub(r'\D', '', msg.topic))
                if ((1 <= devicenumb <= numberOfSupportedLP) and (0 <= int(payload) <= 1)):
                    chargestat = int(payload)
                    if (devicenumb == 1):
                        filename = "chargestat"
                    elif (devicenumb == 2):
                        filename = "chargestats1"
                    elif (devicenumb == 3):
                        filename = "chargestatlp3"
                    ramdisk.write(str(filename), str(chargestat))
            # Topics for Mqtt-LL module
            # ToDo: check if Mqtt-LL module is selected!
            # llmodule = getConfigValue("ladeleistungsmodul")
            if (("openWB/set/lp" in msg.topic) and ("/W" in msg.topic)):
                devicenumb = int(re.sub(r'\D', '', msg.topic))
                if ((1 <= devicenumb <= numberOfSupportedLP) and (0 <= int(payload) <= 100000)):
                    llaktuell = int(payload)
                    if (devicenumb == 1):
                        filename = "llaktuell"
                    elif (devicenumb == 2):
                        filename = "llaktuells1"
                    elif (devicenumb == 3):
                        filename = "llaktuells2"
                    ramdisk.write(str(filename), str(llaktuell))
            if (("openWB/set/lp" in msg.topic) and ("kWhCounter" in msg.topic)):
                devicenumb = int(re.sub(r'\D', '', msg.topic))
                if ((1 <= devicenumb <= numberOfSupportedLP) and (0 <= float(msg.payload) <= 10000000000)):
                    if (devicenumb == 1):
                        filename = "llkwh"
                    elif (devicenumb == 2):
                        filename = "llkwhs1"
                    elif (devicenumb == 3):
                        filename = "llkwhs2"
                    ramdisk.write(str(filename), payload)
            if (("openWB/set/lp" in msg.topic) and ("VPhase1" in msg.topic)):
                devicenumb = int(re.sub(r'\D.', '', msg.topic))
                if ((1 <= devicenumb <= numberOfSupportedLP) and (0 <= float(msg.payload) <= 300)):
                    if (devicenumb == 1):
                        filename = "llv1"
                    elif (devicenumb == 2):
                        filename = "llvs11"
                    elif (devicenumb == 3):
                        filename = "llvs21"
                    ramdisk.write(str(filename), payload)
            if (("openWB/set/lp" in msg.topic) and ("VPhase2" in msg.topic)):
                devicenumb = int(re.sub(r'\D.', '', msg.topic))
                if ((1 <= devicenumb <= numberOfSupportedLP) and (0 <= float(msg.payload) <= 300)):
                    if (devicenumb == 1):
                        filename = "llv2"
                    elif (devicenumb == 2):
                        filename = "llvs12"
                    elif (devicenumb == 3):
                        filename = "llvs22"
                    ramdisk.write(str(filename), payload)
            if (("openWB/set/lp" in msg.topic) and ("VPhase3" in msg.topic)):
                devicenumb = int(re.sub(r'\D.', '', msg.topic))
                if ((1 <= devicenumb <= numberOfSupportedLP) and (0 <= float(msg.payload) <= 300)):
                    if (devicenumb == 1):
                        filename = "llv3"
                    elif (devicenumb == 2):
                        filename = "llvs13"
                    elif (devicenumb == 3):
                        filename = "llvs23"
                    ramdisk.write(str(filename), payload)
            if (("openWB/set/lp" in msg.topic) and ("APhase1" in msg.topic)):
                devicenumb = int(re.sub(r'\D.', '', msg.topic))
                if ((1 <= devicenumb <= numberOfSupportedLP) and (0 <= float(msg.payload) <= 3000)):
                    if (devicenumb == 1):
                        filename = "lla1"
                    elif (devicenumb == 2):
                        filename = "llas11"
                    elif (devicenumb == 3):
                        filename = "llas21"
                    ramdisk.write(str(filename), payload)
            if (("openWB/set/lp" in msg.topic) and ("APhase2" in msg.topic)):
                devicenumb = int(re.sub(r'\D.', '', msg.topic))
                if ((1 <= devicenumb <= numberOfSupportedLP) and (0 <= float(msg.payload) <= 3000)):
                    if (devicenumb == 1):
                        filename = "lla2"
                    elif (devicenumb == 2):
                        filename = "llas12"
                    elif (devicenumb == 3):
                        filename = "llas22"
                    ramdisk.write(str(filename), payload)
            if (("openWB/set/lp" in msg.topic) and ("APhase3" in msg.topic)):
                devicenumb = int(re.sub(r'\D.', '', msg.topic))
                if ((1 <= devicenumb <= numberOfSupportedLP) and (0 <= float(msg.payload) <= 3000)):
                    if (devicenumb == 1):
                        filename = "lla3"
                    elif (devicenumb == 2):
                        filename = "llas13"
                    elif (devicenumb == 3):
                        filename = "llas23"
                    ramdisk.write(str(filename), payload)
            if (("openWB/set/lp" in msg.topic) and ("HzFrequenz" in msg.topic)):
                devicenumb = int(re.sub(r'\D', '', msg.topic))
                if ((1 <= devicenumb <= numberOfSupportedLP) and (0 <= float(msg.payload) <= 80)):
                    if (devicenumb == 1):
                        filename = "llhz"
                    elif (devicenumb == 2):
                        filename = "llhzs1"
                    elif (devicenumb == 3):
                        filename = "llhzs2"
                    ramdisk.write(str(filename), payload)

            # clear all set topics if not already done, ohne logging
            if (not(setTopicCleared)):
                client.publish(msg.topic, "", qos=0, retain=True)

        finally:
            lock.release()


client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker_ip, 1883)
dolog("enter mqtt loop")
client.loop_forever()
client.disconnect()
