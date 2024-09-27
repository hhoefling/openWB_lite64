#!/usr/bin/python3
import pprint
import asyncio
import logging
import inspect
import json
import time
import sys
import os
import paho.mqtt.client as mqtt
from   aiohttp import ClientSession
from   datetime import datetime
import getopt
   

try:
    from skodaconnect import Connection
    from skodaconnect.__version__ import __version__ as lib_version    
except ModuleNotFoundError:
    print("callskoda.py Unable to import library")
    sys.exit(1)

## Defaults
username="hh45475@gmx.de"
password="MHHN15Ehugo01"
debug=1
lp=2
carinfo=0
mqttskoda=0
        
				
try:
	opts, args = getopt.getopt(sys.argv[1:], 'd:p:u:l:CQcq', ['username=', 'password=', 'lp=', 'debug=', 'car', 'MQTT'])
except getopt.error as msg:
	sys.stdout = sys.stderr
	print(msg)
	print("""usage: %s [-u|-p|-l|-d|-c|-q]
	-u[sername], -p[assword]: username and passwort
	-c|--car  carinfo schreiben
	-q|--MQTT 
	-l[p]: Ladepunkt (1 oder 2)
	-d: debug level 0,1,2""" % sys.argv[0])
	sys.exit(2)
for opt, arg in opts:
	#print(f"{opt} = [{arg}] ")
	if opt in ('-u', '--username'):
		username=arg
		password=''      # must follow username
	elif opt in ('-p', '--password'):
		password=arg
	elif opt in ('-l', '--lp'):
		lp=int(arg)
	elif opt in ('-c', '--car'):
		carinfo=1
	elif opt in ('-q', '--MQTT'):
		mqttskoda=1
	elif opt in ('-d', '--debug'):
		debug=int(arg)
    

#print f"debug: {debug}"
if debug < 2:
    logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

#_LOGGER.info(f"{str(sys.argv)}")



#if debug>0: print( f"callskoda.py for LP{lp} debug:{debug} car:{carinfo} mqtt:{mqttskoda}") 
   

RESOURCES = [
#    "adblue_level",
#    "auxiliary_climatisation",
    "battery_level",
    "charge_max_ampere",
#    "charger_action_status",
    "charging",
    "charging_cable_connected",
    "charging_cable_locked",
    "charging_time_left",
#    "climater_action_status",
    "climatisation_target_temperature",
    "climatisation_without_external_power",
#    "combined_range",
    "combustion_range",
#    "departure1",           # wird einzel extra gemacht
#    "departure2",           # wird einzel extra gemacht
#    "departure3",           # wird einzel extra gemacht
    "distance",
    "door_closed_left_back",
    "door_closed_left_front",
    "door_closed_right_back",
    "door_closed_right_front",
    "door_locked",
    "electric_climatisation",
#   "electric_range",
    "energy_flow",
    "external_power",
#   "fuel_level",
    "hood_closed",
    "last_connected",
#    "lock_action_status",
#   "oil_inspection",
#   "oil_inspection_distance",
    "outside_temperature",
    "parking_light",
    "parking_time",
#   "pheater_heating",
#   "pheater_status",
#    "pheater_ventilation",
#    "position",  # wird einzeln extar gemacht
#    "refresh_action_status",
#   "refresh_data",
#   "request_in_progress",
#    "request_results",
#    "requests_remaining",
    "service_inspection",
    "service_inspection_distance",
#    "sunroof_closed",
#    "trip_last_average_auxillary_consumption",
    "trip_last_average_electric_consumption",
#   "trip_last_average_fuel_consumption",
    "trip_last_average_speed",
    "trip_last_duration",
#    "trip_last_entry"       # wird einzel extra gemacht
    "trip_last_length",
    "trip_last_recuperation",
    "trip_last_average_recuperation",
    "trip_last_total_electric_consumption",
    "trunk_closed",
    "trunk_locked",
    "vehicle_moving",
#    "window_closed_left_back",
#    "window_closed_left_front",
#    "window_closed_right_back",
#    "window_closed_right_front",
#    "window_heater",
#    "windows_closed",
    "model",
    "nickname",
    "vin",
#    "json"
]

ToMQtt = [
    "battery_level",
    "charge_max_ampere",
    "charging",
    "charging_cable_connected",
    "charging_cable_locked",
    "charging_time_left",
    "combustion_range",
    "outside_temperature",
    "trip_last_average_electric_consumption",
    "ledColor",
    "ledState",
]

async def main():
    """Main method."""

    all={}  # fields of interest
    if debug>0: print('Init Skoda Connect library, version {}".format(lib_version)')
    async with ClientSession(headers={'Connection': 'keep-alive'}) as session:
        if debug>0: print("Initiating new session to Skoda Connect with {} as username".format(username))
        if debug>0:
            connection = Connection(session, username, password, True)
        else:
            connection = Connection(session, username, password, False)
        
        if debug>0: print("Attempting to login to the Skoda Connect service")
        if debug>0: print(datetime.now())
        if await connection.doLogin():
            if debug>0: print('Login success! ----------------------------')
            if debug>0: print(datetime.now())
            
            if debug>0: print('Fetching vehicles associated with account.')
            await connection.get_vehicles()
            timername='departuretimer'

            
            
            for vehicle in connection.vehicles:
                if( carinfo>0):
                    if debug>0: print(" Writing /var/www/html/openWB/ramdisk/carinfo_{}.json".format(lp)) 
                    file=open("/var/www/html/openWB/ramdisk/carinfo_{}.json".format(lp),"w")
                    file.write( vehicle.json)
                    file.close()
                for prop in dir(vehicle):
                    func = "vehicle.{}".format(prop)
                    name = str(prop)
                    typ = type(eval(func))
                    try:
                        val = eval(func)
                        if( name in RESOURCES):     
                            all[name]=val
                        else:
                            if debug>1: print("Skip Field {} ".format(name))
                    except:
                        pass
                # add sub-fields of interest         
                all['ledColor']=vehicle.attrs.get('charger', {}).get('status',{}).get('ledStatusData',{}).get('ledColor',{}).get('content','')
                all['ledState']=vehicle.attrs.get('charger', {}).get('status',{}).get('ledStatusData',{}).get('ledState',{}).get('content','')
                all['position_lat']=vehicle.position.get('lat','')
                all['position_lng']=vehicle.position.get('lng','')
 
                #all['chargeMinLimit']     = vehicle.attrs.get(timername, {}).get('timersAndProfiles', {}).get('timerBasicSetting', {}).get('chargeMinLimit', 0)
                #all['targetTemperature']  = vehicle.attrs.get(timername, {}).get('timersAndProfiles', {}).get('timerBasicSetting', {}).get('targetTemperature', 0)

                ts = vehicle.attrs.get(timername, {}).get('timersAndProfiles', {}).get('timerList', {}).get('timer', False)
                tps=  vehicle.attrs.get(timername, {}).get('timersAndProfiles', {}).get('timerProfileList', {}).get('timerProfile', False)
                for x in [0,1,2]:
                    xx=x+1
                    timer = ts[x]
                    timer.update(tps[x])
                    timer.pop('timestamp', None)
                    timer.pop('timerID', None)
                    timer.pop('profileID', None)
                    for field in timer:
                        all["timer/{}/{}".format(xx,field)]=timer[field]
                if debug>0: 
                    for x in sorted(all):
                        print("{} = {}".format(x,all[x]) )
                   
                
    # Export to MQTT for Skoda 
    mclient = mqtt.Client("openWB-skoda_broker-" + str(os.getpid()))
    mclient.connect("localhost")
    _LOGGER.debug("MQTTT connect to localhost")
    mclient.loop(timeout=2.0)
    if( mqttskoda > 0):
        if debug>0: print("Write to MQTT /Skoda/")
        for x in all:
            val = all[x]
            field="Skoda/{}".format(x)
            mclient.publish(str(field), payload=str(val), qos=0, retain=True)
            _LOGGER.debug("MQTTT publish %s %s", field, val) 
        mclient.loop(timeout=2.0)

    # Export to MQTT for openWB      
    for x in all:
        val = all[x]
        if x == 'battery_level' :
            field='openWB/set/lp/{}/%Soc'.format(x)
            mclient.publish(str(field), payload=str(val), qos=0, retain=True)
            _LOGGER.debug("MQTTT publish %s %s", field, val) 
        if x in ToMQtt :
            field='openWB/lp/{}/Skoda_{}'.format(lp,x)
            mclient.publish(str(field), payload=str(val), qos=0, retain=True)
            field='openWB/set/lp/{}/Skoda_{}'.format(lp,x)
            mclient.publish(str(field), payload=str(val), qos=0, retain=True)
            _LOGGER.debug("MQTTT publish %s  %s", field, val) 
    mclient.loop(timeout=2.0)
    mclient.disconnect()
    _LOGGER.debug("MQTTT disconnect")
    return True
            

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
