#!/bin/bash
# called by MQTT RequestLiveGraph=1
# 50 mal 10 sekunden sind rund 8 Minuten 
mosquitto_pub -t openWB/system/LiveGraphData -r -m "$(cat /var/www/html/openWB/ramdisk/all-live.graph.csv | tail -n 50)" &
(sleep 3 && mosquitto_pub -t openWB/set/graph/RequestLiveGraph -r -m "0")& 
