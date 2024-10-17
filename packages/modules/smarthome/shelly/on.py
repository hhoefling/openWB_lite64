#!/usr/bin/python3
import sys
import urllib.request
import os
import json
import logging
from smarthome.smartlog import initlog,initMainlog 


devicenumber = str(sys.argv[1])
ipadr = str(sys.argv[2])
uberschuss = int(sys.argv[3])
gen = '1'
model = '???'


initMainlog()
mlog = logging.getLogger('smarthome.shelly.on')

initlog("shelly", devicenumber)
log = logging.getLogger("shelly.on")


try:
    chan = int(sys.argv[4])
except Exception:
    chan = 0
shaut = int(sys.argv[5])
user = str(sys.argv[6])
pw = str(sys.argv[7])
fbase = '/var/www/html/openWB/ramdisk/sm/device_ret.'
fnameg = fbase + str(ipadr) + '_shelly_infogv1'
if os.path.isfile(fnameg):
    with open(fnameg, 'r') as f:
        jsonin = json.loads(f.read())
        gen = str(jsonin['gen'])
        model = str(jsonin['model'])
        log.debug(['use shelly_infogv1', gen, model])
else:
    gen = "1"
if (gen == "1"):
    if (chan == 0):
        url = "http://" + str(ipadr) + "/relay/0?turn=on"
    else:
        chan = chan - 1
        url = "http://" + str(ipadr) + "/relay/" + str(chan) + "?turn=on"
else:
    if (chan > 0):
        chan = chan - 1
    # shelly pro 3em mit add on hat fix id 100 als switch Kanal, das Device muss auf jeden fall mit separater
    # Leistunsmessung erfasst werden, da die Leistung auf drei verschiedenenen Kanälen angeliefert werden kann
    if ("SPEM-003CE" in model):
        chan = 100
    # gen 2 will das als on cmd /rpc/Switch.Set?id=100&on=true
    url = "http://" + str(ipadr) + "/rpc/Switch.Set?id=" + str(chan) + "&on=true"
if (shaut == 1):
    log.debug("Shelly on" + str(shaut) + user + pw)
    passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, user, pw)
    authhandler = urllib.request.HTTPBasicAuthHandler(passman)
    opener = urllib.request.build_opener(authhandler)
    urllib.request.install_opener(opener)
log.info('url:' + str(url) )
with urllib.request.urlopen(url) as response:
    response.read().decode("utf-8")
