#!/usr/bin/python3
import sys
import urllib.request
from urllib.parse import urlparse
import logging
from smarthome.smartlog import initlog, initMainlog
from smarthome.smartret import writeret


devicenumber = int(sys.argv[1])
uberschuss = int(sys.argv[3])
url = str(sys.argv[4])
try:
    urlc = str(sys.argv[5])
except Exception:
    urlc = "none"
try:
    urlstate = str(sys.argv[8])
except Exception:
    urlstate = "none"



#initMainlog()
#mlog = logging.getLogger('smarthome.http.watt')

initlog("http", devicenumber)
log = logging.getLogger("http.watt")


if not urlparse(url).scheme:
    url = 'http://' + url
if not urlparse(urlstate).scheme and not urlstate.startswith("none"):
    urlstate = 'http://' + urlstate
if uberschuss < 0:
    uberschuss = 0
urlrep = url.replace("<openwb-ueberschuss>", str(uberschuss))
#mlog.info('watt devicenr %d orig url %s replaced url %s urlc %s urlstate %s' %
#         (devicenumber, url, urlrep, urlc, urlstate))
#log.info('watt devicenr %d orig url %s replaced url %s urlc %s urlstate %s' %
#         (devicenumber, url, urlrep, urlc, urlstate))
if not urlstate.startswith("none"):
    stateurl_response = 0
    log.info('state devicenr %d url %s ' % (devicenumber, urlstate))
    try:
        stateurl_response = urllib.request.urlopen(urlstate, timeout=5).read().decode("utf-8")
    except urllib.error.HTTPError as e:
        log.info('watt StateURL HTTP Error: %d' % (e.code))
    except urllib.error.URLError as e:
        log.info('watt StateURL URL Error: %s' % (e.reason))
    try:
        state = int(stateurl_response)
    except ValueError:
        log.info('watt StateURL delivered no integer but: %s' % (stateurl_response))
        state = 0
else:
    state = 0

# log.info('huhu')

try:
    log.info('state devicenr %d url %s ' % (devicenumber, urlrep))
    aktpowerfl = float(urllib.request.urlopen(urlrep, timeout=5).read().decode("utf-8"))
except urllib.error.HTTPError as e:
    raise ValueError("Keine Daten von %s" % (urlrep) ) from e
aktpower = int(aktpowerfl)
if state == 1 or aktpower > 50:
    relais = 1
else:
    relais = 0
if len(urlc) < 6:
    powerc = 0
else:
    if not urlparse(urlc).scheme:
        urlc = 'http://' + urlc
    log.info('counter devicenr %d url %s ' % (devicenumber, urlc))
    try:
    powercfl = float(urllib.request.urlopen(urlc, timeout=5).read().decode("utf-8"))
    powerc = int(powercfl)
    except urllib.error.HTTPError as e:
       log.erroror("Keine Daten von %s" % (urlc) )
       powerc = 0

answer = '{"power":' + str(aktpower) + ',"powerc":' + str(powerc) + ',"on":' + str(relais) + '}'
writeret(answer, devicenumber)
log.info(answer + ' saved')
