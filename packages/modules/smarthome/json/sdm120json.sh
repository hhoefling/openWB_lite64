#!/bin/bash

dev=${1:-"ttyUSB0"}
idnr=${3:-"9"}

echo "python3 /var/www/html/openWB/packages/modules/smarthome/json/sdm120json.py $dev $idnr" 
python3 /var/www/html/openWB/packages/modules/smarthome/json/sdm120json.py $dev $idnr 

exit 0

